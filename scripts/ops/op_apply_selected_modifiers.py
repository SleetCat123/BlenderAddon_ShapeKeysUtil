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
from ..funcs import func_separate_shapekeys
from ..funcs.utils import func_object_utils
from ..funcs import func_apply_selected_modifier


class OBJECT_OT_mizore_shapekeys_util_apply_selected_modifiers(bpy.types.Operator):
    bl_idname = "object.shapekeys_util_apply_selected_modifiers"
    bl_label = "Apply Selected Modifiers"
    bl_description = "Apply Selected Modifiers"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.object
        return (
            obj
            and not obj.hide_viewport 
            and not obj.hide_get() 
            and obj.type == 'MESH' 
            and obj.modifiers 
            and obj.modifiers.active
            )

    def execute(self, context):
        try:
            original_obj = context.object

            temp_selected_objects = bpy.context.selected_objects
            func_object_utils.deselect_all_objects()
            func_object_utils.select_object(original_obj, True)
            # リンクされたオブジェクトのモディファイアは適用できないので予めリンクを解除しておく
            bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=True, obdata=True, material=False, animation=False)

            func_apply_selected_modifier.apply_selected_modifier(original_obj)
            # 元の選択状態に戻す
            func_object_utils.select_objects(temp_selected_objects, True)
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
        ("*", "Apply Selected Modifiers"):
            "詳細はRead-me.txtを参照。\n名前の最後が_leftまたは_rightのシェイプキーには使えません",
    },
}


def register():
    bpy.utils.register_class(OBJECT_OT_mizore_shapekeys_util_apply_selected_modifiers)
    bpy.app.translations.register(__name__, translations_dict)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_mizore_shapekeys_util_apply_selected_modifiers)
    bpy.app.translations.unregister(__name__)