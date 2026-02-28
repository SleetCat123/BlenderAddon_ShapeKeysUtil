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
Separate Shapekeys Modal版オペレーター

ジェネレータベースのModal処理を使用して、進捗表示とキャンセル機能を
サポートするSeparate Shapekeysオペレーターを実装します。
"""

from collections.abc import Generator
from typing import Optional

import bpy
from bpy.props import BoolProperty

from ..funcs.func_separate_shapekeys import separate_shapekeys_iter
from ..funcs.modal_base import GeneratorModalOperator
from ..funcs.progress_info import ProgressInfo
from ..funcs.utils import func_object_utils
from ..link import func_link_with_MeshDeformUtils


class OBJECT_OT_shapekeys_util_separate_shapekeys_modal(GeneratorModalOperator):
    """Separate Shapekeys Modal版オペレーター

    シェイプキーをそれぞれ別のオブジェクトに分割します。
    Modal処理により進捗表示とキャンセル機能をサポートします。
    """

    bl_idname = "object.shapekeys_util_shapekeys_to_objects_modal"
    bl_label = "Separate Shapekeys (Modal)"
    bl_description = "Separate objects for each shape keys with progress display"
    bl_options = {'REGISTER', 'UNDO'}

    keep_original: BoolProperty(
        name="Keep Original",
        default=False,
        description="Execute the function on the copied object"
    )
    apply_modifiers: BoolProperty(
        name="Apply Modifiers",
        default=False,
        description="Apply modifiers after separation"
    )
    remove_nonrender: BoolProperty(
        name="Remove Non-Render Modifiers",
        default=True,
        description="A non-render modifier will be removed."
    )
    keep_original_shapekeys: BoolProperty(
        name="Keep Original Shapekeys",
        default=False,
        description="Keep the original shape keys"
    )
    use_update_mesh_deform_addon: BoolProperty(
        name="Use Update Mesh Deform Addon",
        default=False,
        description="Use MeshDeformUtils Addon"
    )

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj is not None and obj.type == 'MESH'

    def draw(self, context):
        """UIの描画"""
        layout = self.layout
        layout.prop(self, "keep_original")
        layout.prop(self, "apply_modifiers")
        layout.prop(self, "remove_nonrender")
        layout.prop(self, "keep_original_shapekeys")

        row = layout.row()
        row.prop(self, "use_update_mesh_deform_addon")
        row.enabled = func_link_with_MeshDeformUtils.update_mesh_deform_addon_is_found()

    def create_generator(self, context: bpy.types.Context) -> Optional[Generator[ProgressInfo, None, None]]:
        """処理ジェネレータを作成"""
        source_obj = context.object

        # 実行する必要がなければキャンセル
        if source_obj.data.shape_keys is None or len(source_obj.data.shape_keys.key_blocks) == 0:
            self.report({'WARNING'}, "No shape keys to separate")
            return None

        func_object_utils.deselect_all_objects()
        func_object_utils.select_object(source_obj, True)
        func_object_utils.set_active_object(source_obj)

        return separate_shapekeys_iter(
            duplicate=self.keep_original,
            enable_apply_modifiers=self.apply_modifiers,
            skip_modifier_types=set(),
            remove_nonrender=self.remove_nonrender,
            keep_original_shapekeys=self.keep_original_shapekeys,
            use_update_mesh_deform_addon=self.use_update_mesh_deform_addon
        )

    def on_complete(self, context: bpy.types.Context):
        """処理完了時のコールバック"""
        self.report({'INFO'}, "Separate Shapekeys complete")

    def execute(self, context: bpy.types.Context):
        """同期実行（invokeではなくexecuteが呼ばれた場合）"""
        # 同期版オペレーターにフォールバック
        return bpy.ops.object.shapekeys_util_shapekeys_to_objects(
            keep_original=self.keep_original,
            apply_modifiers=self.apply_modifiers,
            remove_nonrender=self.remove_nonrender,
            keep_original_shapekeys=self.keep_original_shapekeys
        )


# 翻訳辞書
translations_dict = {
    "ja_JP": {
        ("*", "Separate objects for each shape keys with progress display"):
            "シェイプキーをそれぞれ別オブジェクトにします（進捗表示付き）",
        ("*", "Keep Original"): "元のオブジェクトを残す",
        ("*", "Execute the function on the copied object"): "分割前のオブジェクトを残します",
        ("*", "Apply Modifiers"): "モディファイア適用",
        ("*", "Apply modifiers after separation"): "分割後にオブジェクトのモディファイアを適用します",
        ("*", "Remove Non-Render Modifiers"): "レンダリング無効は削除",
        ("*", "A non-render modifier will be removed."):
            "レンダリング無効化状態のモディファイアを削除します。",
        ("*", "Keep Original Shapekeys"): "元のシェイプキーを残す",
        ("*", "Keep the original shape keys"): "分割前のシェイプキーを残します",
    },
}


def register():
    """クラス登録"""
    bpy.utils.register_class(OBJECT_OT_shapekeys_util_separate_shapekeys_modal)
    bpy.app.translations.register(__name__, translations_dict)


def unregister():
    """クラス登録解除"""
    bpy.utils.unregister_class(OBJECT_OT_shapekeys_util_separate_shapekeys_modal)
    bpy.app.translations.unregister(__name__)
