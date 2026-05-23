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

"""
Apply Modifiers Modal版オペレーター

ジェネレータベースのModal処理を使用して、進捗表示とキャンセル機能を
サポートするApply Modifiersオペレーターを実装します。
"""

from collections.abc import Generator
from typing import Optional

import bpy
from bpy.props import BoolProperty

from .. import consts
from ..funcs.func_apply_modifiers_with_shapekeys import apply_modifiers_with_shapekeys_iter
from ..funcs.modal_base import GeneratorModalOperator
from ..funcs.progress_info import ProgressInfo
from ..funcs.utils import func_object_utils
from ..link import func_link_with_MeshDeformUtils


def apply_modifiers_all_iter(
    targets: list,
    remove_nonrender: bool,
    use_update_mesh_deform_addon: bool
) -> Generator[ProgressInfo, None, None]:
    """複数オブジェクトに対するモディファイア適用（ジェネレータ版）

    Args:
        targets: 処理対象オブジェクトのリスト
        remove_nonrender: レンダリング無効モディファイアを削除するか
        use_update_mesh_deform_addon: MeshDeformアドオン連携を使用するか

    Yields:
        ProgressInfo: 進捗情報
    """
    total = len(targets)

    for idx, obj in enumerate(targets):
        base_progress = idx / max(total, 1)

        yield ProgressInfo(
            phase="apply_modifiers",
            progress=base_progress,
            message=f"Processing object {idx + 1}/{total}: {obj.name}",
            object_name=obj.name
        )

        func_object_utils.set_active_object(obj)

        # 個別オブジェクトの処理をジェネレータで実行
        for sub_progress in apply_modifiers_with_shapekeys_iter(
            remove_nonrender=remove_nonrender,
            use_update_mesh_deform_addon=use_update_mesh_deform_addon,
            skip_modifier_types=consts.DEFAULT_SKIP_MODIFIER_TYPES
        ):
            # サブ進捗を全体進捗にマッピング
            combined_progress = base_progress + (sub_progress.progress / total)
            yield ProgressInfo(
                phase=sub_progress.phase,
                progress=combined_progress,
                message=sub_progress.message,
                object_name=sub_progress.object_name,
                sub_progress=sub_progress.progress
            )

    yield ProgressInfo(
        phase="complete",
        progress=1.0,
        message="Complete",
        object_name=""
    )


class OBJECT_OT_shapekeys_util_apply_modifiers_modal(GeneratorModalOperator):
    """Apply Modifiers Modal版オペレーター

    選択オブジェクトにモディファイアを適用します。
    Modal処理により進捗表示とキャンセル機能をサポートします。
    """

    bl_idname = "object.shapekeys_util_apply_modifiers_modal"
    bl_label = "Apply Modifiers (Modal)"
    bl_description = "Apply all modifiers except for Armature with progress display"
    bl_options = {'REGISTER', 'UNDO'}

    remove_nonrender: BoolProperty(
        name="Remove NonRender",
        default=True,
        description="A non-render modifier will be removed."
    )

    use_update_mesh_deform_addon: BoolProperty(
        name="Use Update Mesh Deform Addon",
        default=False,
        description="Use MeshDeformUtils Addon"
    )

    def draw(self, context):
        """UIの描画"""
        layout = self.layout
        layout.prop(self, "remove_nonrender")

        row = layout.row()
        row.prop(self, "use_update_mesh_deform_addon")
        row.enabled = func_link_with_MeshDeformUtils.update_mesh_deform_addon_is_found()

    def create_generator(self, context: bpy.types.Context) -> Optional[Generator[ProgressInfo, None, None]]:
        """処理ジェネレータを作成"""
        active = func_object_utils.get_active_object()
        selected_objects = bpy.context.selected_objects
        targets = [d for d in selected_objects if d.type == 'MESH']
        if active and active.type == 'MESH' and active not in targets:
            targets.append(active)

        if not targets:
            self.report({'ERROR'}, "No mesh objects selected")
            return None

        # 選択解除と再選択
        func_object_utils.deselect_all_objects()
        func_object_utils.select_objects(targets, True)

        func_object_utils.ensure_single_user_object_data(targets)

        # 状態保存（処理後の復元用）
        self._original_active = active
        self._original_selected = selected_objects

        return apply_modifiers_all_iter(
            targets=targets,
            remove_nonrender=self.remove_nonrender,
            use_update_mesh_deform_addon=self.use_update_mesh_deform_addon
        )

    def on_complete(self, context: bpy.types.Context):
        """処理完了時のコールバック"""
        # 選択状態を復元
        if hasattr(self, '_original_selected'):
            func_object_utils.select_objects(self._original_selected, True)
        if hasattr(self, '_original_active') and self._original_active:
            func_object_utils.set_active_object(self._original_active)

        self.report({'INFO'}, "Apply Modifiers complete")

    def execute(self, context: bpy.types.Context):
        """同期実行（invokeではなくexecuteが呼ばれた場合）"""
        # 同期版オペレーターにフォールバック
        return bpy.ops.object.shapekeys_util_apply_modifiers(
            remove_nonrender=self.remove_nonrender,
            use_update_mesh_deform_addon=self.use_update_mesh_deform_addon
        )


# 翻訳辞書
translations_dict = {
    "ja_JP": {
        ("*", "Apply all modifiers except for Armature with progress display"):
            "Armature以外の全モディファイアを適用（進捗表示付き）",
        ("*", "Remove NonRender"): "レンダリング無効は削除",
        ("*", "A non-render modifier will be removed."):
            "レンダリング無効化状態のモディファイアを削除します。",
    },
}


def register():
    """クラス登録"""
    bpy.utils.register_class(OBJECT_OT_shapekeys_util_apply_modifiers_modal)
    bpy.app.translations.register(__name__, translations_dict)


def unregister():
    """クラス登録解除"""
    bpy.utils.unregister_class(OBJECT_OT_shapekeys_util_apply_modifiers_modal)
    bpy.app.translations.unregister(__name__)
