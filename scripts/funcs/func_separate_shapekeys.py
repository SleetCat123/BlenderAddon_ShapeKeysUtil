# ##### BEGIN GPL LICENSE BLOCK #####
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import time
from collections.abc import Generator

from . import func_apply_modifiers, func_shapekey_utils
from .func_shapekey_integrity import ensure_shape_key_integrity
from .progress_info import ProgressInfo, T
from .utils import func_mesh_utils, func_object_utils


def _duplicate_object_for_shapekey_split(source_obj):
    collection = source_obj.users_collection[0] if source_obj.users_collection else bpy.context.scene.collection
    dup_obj = source_obj.copy()
    if source_obj.data:
        dup_obj.data = source_obj.data.copy()
    collection.objects.link(dup_obj)
    func_object_utils.deselect_all_objects()
    func_object_utils.select_object(dup_obj, True)
    func_object_utils.set_active_object(dup_obj)
    return dup_obj


def separate_shapekeys_iter(
        duplicate: bool,
        enable_apply_modifiers: bool,
        skip_modifier_types: set,
        remove_nonrender: bool = True,
        keep_original_shapekeys: bool = False,
        use_update_mesh_deform_addon: bool = False,
) -> Generator[ProgressInfo, None, list]:
    """シェイプキーをそれぞれ別のオブジェクトにする（ジェネレータ版）

    Args:
        duplicate: 元オブジェクトを複製するか
        enable_apply_modifiers: 分割後にモディファイアを適用するか
        remove_nonrender: レンダリング無効モディファイアを削除するか
        keep_original_shapekeys: 元のシェイプキーを残すか
        use_update_mesh_deform_addon: MeshDeformアドオン連携を使用するか
        skip_modifier_types: スキップするモディファイアタイプのセット

    Yields:
        ProgressInfo: 進捗情報

    Returns:
        List: 分割されたオブジェクトのリスト
    """
    print(f"[separate_shapekeys_iter] skip_modifier_types={skip_modifier_types}")
    start_time = time.perf_counter()
    source_obj = func_object_utils.get_active_object()
    source_obj_name = source_obj.name

    print(f"[separate_shapekeys] start: {source_obj_name}")
    phase_start = start_time

    yield ProgressInfo(
        phase="init",
        progress=0.0,
        message=T("sku_progress_initializing").format(obj=source_obj.name),
        object_name=source_obj.name
    )

    func_object_utils.deselect_all_objects()

    if duplicate:
        func_object_utils.select_object(source_obj, True)
        func_object_utils.set_active_object(source_obj)
        func_object_utils.duplicate_object()
        source_obj = func_object_utils.get_active_object()

    source_obj_matrix_world_inverted = source_obj.matrix_world.inverted()

    print("Separate ShapeKeys: [" + source_obj.name + "]")
    separated_objects = []
    shape_keys_length = len(source_obj.data.shape_keys.key_blocks)

    func_object_utils.select_object(source_obj, True)
    print(f"[separate_shapekeys] init: {time.perf_counter() - phase_start:.3f}s")
    phase_start = time.perf_counter()

    # シェイプキー分割処理（0% - 60%）
    for i, shapekey in enumerate(source_obj.data.shape_keys.key_blocks):
        progress = 0.6 * (i / max(shape_keys_length, 1))
        print(f"Shape key [{shapekey.name}] [{i} / {shape_keys_length}]")

        yield ProgressInfo(
            phase="separate",
            progress=progress,
            message=T("sku_progress_separating").format(shapekey=shapekey.name, current=i, total=shape_keys_length),
            object_name=source_obj.name
        )

        new_name = source_obj_name + "." + shapekey.name
        # Basisは無視
        if i == 0:
            if duplicate:
                func_object_utils.set_object_name(source_obj, new_name)
            continue

        # オブジェクトを複製し、元オブジェクトの子にする
        # bpy.ops.object.parent_setだと更新処理が走って重くなるのでLowLevelな方法を採用
        dup_obj = _duplicate_object_for_shapekey_split(source_obj)
        dup_obj.parent = source_obj
        dup_obj.matrix_parent_inverse = source_obj_matrix_world_inverted
        # シェイプキーの名前をオブジェクト名として設定
        func_object_utils.set_object_name(dup_obj, new_name)
        # シェイプキーの形状を固定
        func_shapekey_utils.bake_shape_key(shapekey.name)
        if not ensure_shape_key_integrity(dup_obj, log_prefix="separate_shapekeys"):
            raise RuntimeError(f"Shape key integrity check failed after baking: {dup_obj.name}")

        separated_objects.append(dup_obj)

        func_object_utils.select_object(dup_obj, False)

    print(f"[separate_shapekeys] split_loop: {time.perf_counter() - phase_start:.3f}s")
    phase_start = time.perf_counter()

    yield ProgressInfo(
        phase="cleanup",
        progress=0.6,
        message=T("sku_progress_cleanup_shapekeys"),
        object_name=source_obj.name
    )

    if not keep_original_shapekeys:
        # 元オブジェクトのシェイプキーを全削除
        source_obj.shape_key_clear()
        if not ensure_shape_key_integrity(source_obj, log_prefix="separate_shapekeys"):
            raise RuntimeError(f"Shape key integrity check failed after clearing source keys: {source_obj.name}")

    func_object_utils.deselect_all_objects()
    print(f"[separate_shapekeys] cleanup: {time.perf_counter() - phase_start:.3f}s")
    phase_start = time.perf_counter()

    # モディファイア適用処理（60% - 95%）
    if enable_apply_modifiers:
        all_targets = []
        if not keep_original_shapekeys:
            all_targets.append(source_obj)
        all_targets.extend(separated_objects)
        total_targets = len(all_targets)

        for idx, obj in enumerate(all_targets):
            progress = 0.6 + 0.35 * (idx / max(total_targets, 1))

            yield ProgressInfo(
                phase="apply_modifiers",
                progress=progress,
                message=T("sku_progress_apply_modifiers").format(obj=obj.name, current=idx + 1, total=total_targets),
                object_name=obj.name
            )

            func_object_utils.set_active_object(obj)
            func_apply_modifiers.apply_modifiers(
                remove_nonrender=remove_nonrender,
                use_update_mesh_deform_addon=use_update_mesh_deform_addon,
                skip_modifier_types=skip_modifier_types)

        func_object_utils.set_active_object(source_obj)
        print(f"[separate_shapekeys] apply_modifiers_loop: {time.perf_counter() - phase_start:.3f}s")

    # 表示を更新
    func_mesh_utils.update_mesh()

    yield ProgressInfo(
        phase="complete",
        progress=1.0,
        message=T("sku_progress_complete").format(obj=source_obj.name),
        object_name=source_obj.name
    )

    print(f"[separate_shapekeys] {source_obj.name}: {time.perf_counter() - start_time:.3f}s")
    return separated_objects


def separate_shapekeys(
        duplicate: bool,
        enable_apply_modifiers: bool,
        skip_modifier_types: set,
        remove_nonrender: bool = True,
        keep_original_shapekeys: bool = False,
        use_update_mesh_deform_addon: bool = False,
):
    """シェイプキーをそれぞれ別のオブジェクトにする（同期版ラッパー）

    Args:
        duplicate: 元オブジェクトを複製するか
        enable_apply_modifiers: 分割後にモディファイアを適用するか
        remove_nonrender: レンダリング無効モディファイアを削除するか
        keep_original_shapekeys: 元のシェイプキーを残すか
        use_update_mesh_deform_addon: MeshDeformアドオン連携を使用するか
        skip_modifier_types: スキップするモディファイアタイプのセット

    Returns:
        List: 分割されたオブジェクトのリスト
    """
    gen = separate_shapekeys_iter(
        duplicate=duplicate,
        enable_apply_modifiers=enable_apply_modifiers,
        remove_nonrender=remove_nonrender,
        keep_original_shapekeys=keep_original_shapekeys,
        use_update_mesh_deform_addon=use_update_mesh_deform_addon,
        skip_modifier_types=skip_modifier_types
    )
    result = None
    try:
        while True:
            next(gen)
    except StopIteration as e:
        result = e.value
    return result if result is not None else []
