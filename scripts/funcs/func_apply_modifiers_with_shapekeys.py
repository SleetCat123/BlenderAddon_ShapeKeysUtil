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

import bpy

from .. import consts
from ..funcs import (
    func_apply_as_shapekey,
    func_apply_modifiers,
    func_update_mesh_deform_addon,
)
from ..funcs.func_apply_modifiers_with_shapekeys_helpers.apply_each_shapekey_modifiers import (
    apply_each_shapekey_modifiers,
)
from ..funcs.func_apply_modifiers_with_shapekeys_helpers.apply_surface_deform_to_basis import (
    apply_surface_deform_to_basis,
)
from ..funcs.func_apply_modifiers_with_shapekeys_helpers.partial_apply_modifiers import (
    partial_apply_modifiers,
)
from ..funcs.func_shapekey_integrity import ensure_shape_key_integrity
from ..funcs.utils import func_object_utils
from .progress_info import ProgressInfo, T


def _get_shape_key_count(obj) -> int:
    shape_keys = getattr(getattr(obj, "data", None), "shape_keys", None)
    if not shape_keys:
        return 0
    return len(shape_keys.key_blocks)


def apply_modifiers_with_shapekeys_iter(
    skip_modifier_types: set,
    remove_nonrender: bool = True,
    use_update_mesh_deform_addon: bool = False,
    depth: int = 0
) -> Generator[ProgressInfo, None, None]:
    """シェイプキー付きモディファイア適用（ジェネレータ版）

    Args:
        remove_nonrender: レンダリング無効モディファイアを削除するか
        use_update_mesh_deform_addon: MeshDeformアドオン連携を使用するか
        skip_modifier_types: スキップするモディファイアタイプのセット
        depth: 再帰の深さ（進捗表示用）

    Yields:
        ProgressInfo: 進捗情報
    """
    print(f"[apply_modifiers_with_shapekeys_iter] skip_modifier_types={skip_modifier_types}")
    start_time = time.perf_counter()
    source_obj = func_object_utils.get_active_object()
    func_object_utils.ensure_single_user_object_data(source_obj)
    obj_name = source_obj.name

    yield ProgressInfo(
        phase="apply_modifiers",
        progress=0.0,
        message=T("sku_progress_processing").format(obj=obj_name),
        object_name=obj_name
    )

    print(
        f"[apply_modifiers_with_shapekeys] start: {obj_name} "
        f"modifiers={len(source_obj.modifiers)} "
        f"shapekeys={_get_shape_key_count(source_obj)} "
        f"depth={depth}"
    )

    # Apply as shapekey用モディファイアのインデックスを検索
    apply_as_shape_index = -1
    apply_as_shape_modifier = None
    for i, modifier in enumerate(source_obj.modifiers):
        if consts.REGEX_APPLY_AS_SHAPEKEY_PREFIX.match(modifier.name):
            apply_as_shape_index = i
            apply_as_shape_modifier = modifier
            print(
                f"[apply_modifiers_with_shapekeys] found_apply_as_shape: "
                f"object={obj_name} index={apply_as_shape_index} "
                f"modifier={modifier.name} shapekeys={_get_shape_key_count(source_obj)} "
                f"depth={depth}"
            )
            break

    if apply_as_shape_index == 0:
        yield ProgressInfo(
            phase="apply_as_shape",
            progress=0.2,
            message=T("sku_progress_apply_as_shape").format(modifier=apply_as_shape_modifier.name),
            object_name=obj_name
        )

        if use_update_mesh_deform_addon:
            func_update_mesh_deform_addon.update_mesh_deform_addon(
                obj=source_obj,
                modifier=apply_as_shape_modifier,
                use_update_mesh_deform_addon=use_update_mesh_deform_addon)

        print("%AS% modifier is top")
        func_apply_as_shapekey.apply_as_shapekey(apply_as_shape_modifier)

        # 再帰呼び出し
        print("re-execute apply_modifiers_with_shapekeys")
        yield from apply_modifiers_with_shapekeys_iter(
            remove_nonrender=remove_nonrender,
            use_update_mesh_deform_addon=use_update_mesh_deform_addon,
            skip_modifier_types=skip_modifier_types,
            depth=depth + 1
        )
        print(f"[apply_modifiers_with_shapekeys] {obj_name} (via %AS% top): {time.perf_counter() - start_time:.3f}s")
        return

    elif apply_as_shape_index >= 1:
        yield ProgressInfo(
            phase="partial_apply",
            progress=0.2,
            message=T("sku_progress_partial_apply").format(obj=obj_name),
            object_name=obj_name
        )
        print("%AS% modifier is not top")
        partial_apply_modifiers(
            source_obj=source_obj,
            modifier_index=apply_as_shape_index,
            remove_nonrender=remove_nonrender,
            use_update_mesh_deform_addon=use_update_mesh_deform_addon,
            skip_modifier_types=skip_modifier_types)
        print(f"[apply_modifiers_with_shapekeys] {obj_name} (via %AS% partial): {time.perf_counter() - start_time:.3f}s")
        return
    else:
        print("%AS% modifier is not found")

    if source_obj.data.shape_keys and len(source_obj.data.shape_keys.key_blocks) == 1:
        yield ProgressInfo(
            phase="remove_basis",
            progress=0.3,
            message=T("sku_progress_removing_basis").format(obj=obj_name),
            object_name=obj_name
        )
        print("remove basis: " + source_obj.name)
        source_obj.active_shape_key_index = 0
        bpy.ops.object.shape_key_remove(all=True)
        if not ensure_shape_key_integrity(source_obj, log_prefix="apply_modifiers_with_shapekeys"):
            raise RuntimeError(f"Shape key integrity check failed after removing Basis: {source_obj.name}")

    if source_obj.data.shape_keys is None or len(source_obj.data.shape_keys.key_blocks) == 0:
        yield ProgressInfo(
            phase="apply_modifiers",
            progress=0.5,
            message=T("sku_progress_apply_modifiers_no_shapekeys").format(obj=obj_name),
            object_name=obj_name
        )
        print("only apply_modifiers: " + source_obj.name)
        func_apply_modifiers.apply_modifiers(
            remove_nonrender=remove_nonrender,
            use_update_mesh_deform_addon=use_update_mesh_deform_addon,
            skip_modifier_types=skip_modifier_types)
        print(f"[apply_modifiers_with_shapekeys] {obj_name} (no shapekeys): {time.perf_counter() - start_time:.3f}s")
        return

    # SurfaceDeformモディファイア処理
    surface_deform_index = -1
    surface_deform_modifier = None
    for i, modifier in enumerate(source_obj.modifiers):
        if modifier.type == 'SURFACE_DEFORM':
            surface_deform_index = i
            surface_deform_modifier = modifier
            print(
                f"[apply_modifiers_with_shapekeys] found_surface_deform: "
                f"object={obj_name} index={surface_deform_index} "
                f"modifier={modifier.name} shapekeys={_get_shape_key_count(source_obj)} "
                f"depth={depth}"
            )
            break

    if surface_deform_index == 0:
        yield ProgressInfo(
            phase="surface_deform",
            progress=0.4,
            message=T("sku_progress_surface_deform").format(obj=obj_name),
            object_name=obj_name
        )
        print("SurfaceDeform modifier is top")
        apply_surface_deform_to_basis(
            source_obj=source_obj,
            modifier=surface_deform_modifier,
            use_update_mesh_deform_addon=use_update_mesh_deform_addon,
            remove_nonrender=remove_nonrender,
            skip_modifier_types=skip_modifier_types)
        print(f"[apply_modifiers_with_shapekeys] {obj_name} (via SurfaceDeform top): {time.perf_counter() - start_time:.3f}s")
        return

    if surface_deform_index >= 1:
        yield ProgressInfo(
            phase="partial_apply",
            progress=0.4,
            message=T("sku_progress_partial_apply_surface_deform").format(obj=obj_name),
            object_name=obj_name
        )
        print("SurfaceDeform modifier is not top")
        partial_apply_modifiers(
            source_obj=source_obj,
            modifier_index=surface_deform_index,
            remove_nonrender=remove_nonrender,
            use_update_mesh_deform_addon=use_update_mesh_deform_addon,
            skip_modifier_types=skip_modifier_types)
        print(f"[apply_modifiers_with_shapekeys] {obj_name} (via SurfaceDeform partial): {time.perf_counter() - start_time:.3f}s")
        return
    else:
        print("SurfaceDeform modifier is not found")

    func_object_utils.deselect_all_objects()
    func_object_utils.select_object(source_obj, True)
    func_object_utils.set_active_object(source_obj)

    # applymodifierの対象となるモディファイアがあるかどうか確認
    need_apply_modifier = False
    for modifier in source_obj.modifiers:
        if modifier.show_render or remove_nonrender:
            if modifier.name.startswith(consts.FORCE_APPLY_MODIFIER_PREFIX) or modifier.type not in skip_modifier_types:
                need_apply_modifier = True
                break

    print(
        f"[apply_modifiers_with_shapekeys] need_apply: "
        f"object={source_obj.name} result={need_apply_modifier} "
        f"modifiers={len(source_obj.modifiers)} "
        f"shapekeys={_get_shape_key_count(source_obj)} "
        f"depth={depth}"
    )

    if need_apply_modifier:
        yield ProgressInfo(
            phase="apply_each_shapekey",
            progress=0.6,
            message=T("sku_progress_apply_each_shapekey").format(obj=obj_name),
            object_name=obj_name
        )
        print(
            f"[apply_modifiers_with_shapekeys] apply_each_shapekey: "
            f"object={obj_name} modifiers={len(source_obj.modifiers)} "
            f"shapekeys={_get_shape_key_count(source_obj)} depth={depth}"
        )

        # シェイプキーの名前と数値を記憶
        active_shape_key_index = source_obj.active_shape_key_index
        shapekey_name_and_values = []
        for shapekey in source_obj.data.shape_keys.key_blocks:
            shapekey_name_and_values.append((shapekey.name, shapekey.value))

        # シェイプキーをそれぞれ別オブジェクトにしてモディファイア適用
        apply_each_shapekey_modifiers(source_obj, remove_nonrender, use_update_mesh_deform_addon, skip_modifier_types)

        yield ProgressInfo(
            phase="restore_shapekeys",
            progress=0.9,
            message=T("sku_progress_restoring_shapekeys").format(obj=obj_name),
            object_name=obj_name
        )

        print(shapekey_name_and_values)
        print([v.name for v in source_obj.data.shape_keys.key_blocks])
        # シェイプキーの名前と数値を復元
        source_obj.active_shape_key_index = active_shape_key_index
        for i, shapekey in enumerate(source_obj.data.shape_keys.key_blocks):
            shapekey.name = shapekey_name_and_values[i][0]
            shapekey.value = shapekey_name_and_values[i][1]
        if not ensure_shape_key_integrity(source_obj, log_prefix="apply_modifiers_with_shapekeys"):
            raise RuntimeError(
                f"Shape key integrity check failed after restoring shape keys: {source_obj.name}"
            )

    print("Shapekey Count (Include Basis Shapekey): " + str(len(source_obj.data.shape_keys.key_blocks)))

    func_object_utils.select_object(source_obj, True)
    func_object_utils.set_active_object(source_obj)

    yield ProgressInfo(
        phase="complete",
        progress=1.0,
        message=T("sku_progress_complete").format(obj=obj_name),
        object_name=obj_name
    )
    print(f"[apply_modifiers_with_shapekeys] {obj_name}: {time.perf_counter() - start_time:.3f}s")


def apply_modifiers_with_shapekeys(skip_modifier_types: set, remove_nonrender=True, use_update_mesh_deform_addon=False):
    """シェイプキー付きモディファイア適用（同期版ラッパー）

    ジェネレータ版を消費して実行します。
    """
    gen = apply_modifiers_with_shapekeys_iter(
        remove_nonrender=remove_nonrender,
        use_update_mesh_deform_addon=use_update_mesh_deform_addon,
        skip_modifier_types=skip_modifier_types
    )
    for _ in gen:
        pass
