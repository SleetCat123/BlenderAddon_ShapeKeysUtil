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
from ..funcs import func_separate_lr_shapekey_all
from ..funcs.utils import func_object_utils


class OBJECT_OT_specials_shapekeys_util_separate_lr_shapekey_all(bpy.types.Operator):
    bl_idname = "object.shapekeys_util_separate_lr_shapekey_all"
    bl_label = "Separate All Shape Key Left and Right"
    bl_description = "All shape key separate left and right based on object origin.\nSeparation is skipping if a shape key name ends with \"_left\" or \"_right\""
    bl_options = {'REGISTER', 'UNDO'}

    keep_original: BoolProperty(
        name="Keep Original",
        default=False,
        description="Keep the shape key before the left-right split.\nNote: Using the shape keys before and after the left-right split at the same time,\n may result in an unintended appearance of the model.\n (because the shape key is doubly applied)"
    )
    enable_sort: BoolProperty(
        name="Enable Sort",
        default=False,
        description="Result shape keys move to below target shape key.\nWarning: It may take a while"
    )

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj.type == 'MESH' and obj.data.shape_keys and len(obj.data.shape_keys.key_blocks) != 0

    def execute(self, context):
        try:
            obj = context.object
            func_object_utils.set_active_object(obj)
            func_separate_lr_shapekey_all.separate_lr_shapekey_all(duplicate=self.keep_original, enable_sort=self.enable_sort, auto_detect=False)
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
        ( "*", "All shape key separate left and right based on object origin.\nSeparation is skipping if a shape key name ends with \"_left\" or \"_right\"" ):
            "全てのシェイプキーをオブジェクト原点基準で左右別々にします。\n"
            "名前の最後が_leftまたは_rightのシェイプキーは分割済みと見なし処理をスキップします",
        ( "*", "Keep Original" ): "元のシェイプキーを残す",
        ( "*", "Keep the shape key before the left-right split.\nNote: Using the shape keys before and after the left-right split at the same time,\n may result in an unintended appearance of the model.\n (because the shape key is doubly applied)" ):
            "左右分割前のシェイプキーを残します。\n"
            "注意：左右分割する前とした後のシェイプキーを同時に有効化するとモデルが意図しない見た目になる可能性があります。\n"
            "（シェイプキーが二重にかかるため）",
        ( "*", "Enable Sort" ): "分割後の並び替え",
        ( "*", "Result shape keys move to below target shape key.\nWarning: It may take a while" ):
            "左右分割後のシェイプキーを分割前シェイプキーのすぐ下に移動します。\n注意：時間がかかります",
    },
}


def register():
    bpy.utils.register_class(OBJECT_OT_specials_shapekeys_util_separate_lr_shapekey_all)
    bpy.app.translations.register(__name__, translations_dict)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_specials_shapekeys_util_separate_lr_shapekey_all)
    bpy.app.translations.unregister(__name__)