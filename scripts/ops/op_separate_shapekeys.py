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

import bpy
import traceback
from bpy.props import BoolProperty
from ..funcs import func_separate_shapekeys
from ..funcs.utils import func_object_utils


class OBJECT_OT_specials_shapekeys_util_shapekeys_to_objects(bpy.types.Operator):
    bl_idname = "object.shapekeys_util_shapekeys_to_objects"
    bl_label = "Separate Objects"
    bl_description = "Separate objects for each shape keys.\nWarning: It may take a while"
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

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj.type == 'MESH'

    def execute(self, context):
        try:
            source_obj = context.object

            # 実行する必要がなければキャンセル
            if source_obj.data.shape_keys is None or len(source_obj.data.shape_keys.key_blocks) == 0:
                return {'CANCELLED'}

            func_object_utils.deselect_all_objects()
            func_object_utils.select_object(source_obj, True)
            func_object_utils.set_active_object(source_obj)
            
            # シェイプキーをそれぞれ別オブジェクトにする
            func_separate_shapekeys.separate_shapekeys(
                duplicate=self.keep_original,
                enable_apply_modifiers=self.apply_modifiers,
                remove_nonrender=self.remove_nonrender,
                keep_original_shapekeys=self.keep_original_shapekeys
            )

            return {'FINISHED'}
        except Exception as e:
            bpy.ops.ed.undo_push(message = "Restore point")
            bpy.ops.ed.undo()
            bpy.ops.ed.undo_push(message = "Restore point")
            traceback.print_exc()
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}


translations_dict = {
    "ja_JP": {
        ("*", "Separate objects for each shape keys.\nWarning: It may take a while"):
            "シェイプキーをそれぞれ別オブジェクトにします。\n注意：少し時間がかかります",
        ("*", "Keep Original"): "元のオブジェクトを残す",
        ("*", "Execute the function on the copied object"): "分割前のオブジェクトを残します",
        ("*", "Apply Modifiers"): "モディファイア適用",
        ("*", "Apply modifiers after separation"): "分割後にオブジェクトのモディファイアを適用します",
        ("*", "Remove Non-Render Modifiers"): "レンダリング無効は削除",
        ("*", "A non-render modifier will be removed."):
            "レンダリング無効化状態のモディファイア\n（モディファイア一覧でカメラアイコンが押されていない）\nを削除します。",
        ("*", "Keep Original Shapekeys"): "元のシェイプキーを残す",
        ("*", "Keep the original shape keys"): "分割前のシェイプキーを残します",
    },
}


def register():
    bpy.utils.register_class(OBJECT_OT_specials_shapekeys_util_shapekeys_to_objects)
    bpy.app.translations.register(__name__, translations_dict)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_specials_shapekeys_util_shapekeys_to_objects)
    bpy.app.translations.unregister(__name__)
