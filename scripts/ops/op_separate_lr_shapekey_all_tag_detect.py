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
from ..funcs import func_separate_lr_shapekey_all
from ..funcs.utils import func_object_utils


class OBJECT_OT_specials_shapekeys_util_separate_lr_shapekey_all_tag_detect(bpy.types.Operator):
    bl_idname = "object.shapekeys_util_separate_lr_shapekey_all_tag_detect"
    bl_label = "(Tag) Separate All Shape Key Left and Right"
    bl_description = "Separate shape keys with '%LR%' tag into left and right.\nApply Mirror modifier before use.\n\nAdditional tags:\n'%D%' to keep original\n'%S%' to sort below original.\nWarning: Sorting may take time for many shape keys.\n\nControl tags are removed from result shape key names"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj.type == 'MESH' and obj.data.shape_keys and len(obj.data.shape_keys.key_blocks) != 0

    def execute(self, context):
        obj = context.object
        func_object_utils.set_active_object(obj)
        func_separate_lr_shapekey_all.separate_lr_shapekey_all(duplicate=False, enable_sort=False, auto_detect=True)
        return {'FINISHED'}


translations_dict = {
    "ja_JP": {
        ( "*", "Separate shape keys with '%LR%' tag into left and right.\nApply Mirror modifier before use.\n\nAdditional tags:\n'%D%' to keep original\n'%S%' to sort below original.\nWarning: Sorting may take time for many shape keys.\n\nControl tags are removed from result shape key names" ):
            "'%LR%'タグの付いたシェイプキーを左右に分割します。\n使用前にミラーモディファイアを適用してください。\n\n追加タグ：\n'%D%'で元のキーを保持\n'%S%'で分割後のキーを元のキーの下に移動。\n注：シェイプキー数が多い場合、ソートに時間がかかる可能性があります。\n\n制御用タグは結果のシェイプキー名から削除されます",
    },
}


def register():
    bpy.utils.register_class(OBJECT_OT_specials_shapekeys_util_separate_lr_shapekey_all_tag_detect)
    bpy.app.translations.register(__name__, translations_dict)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_specials_shapekeys_util_separate_lr_shapekey_all_tag_detect)
    bpy.app.translations.unregister(__name__)
