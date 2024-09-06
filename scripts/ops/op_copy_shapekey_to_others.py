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
from ..funcs.utils import func_object_utils


class OBJECT_OT_mizore_copy_shapekey_to_others(bpy.types.Operator):
    bl_idname = "object.mizore_copy_shapekey_to_others"
    bl_label = "Copy Shapekeys"
    bl_description = "Adds the shape of the active object to another object as a shape key"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        active_obj = func_object_utils.get_active_object()
        selected_objs = bpy.context.selected_objects
        return active_obj and active_obj.type == 'MESH' and len(selected_objs) > 1

    def execute(self, context):
        try:
            active_obj = func_object_utils.get_active_object()
            selected_objs = bpy.context.selected_objects
            # active_objの形状を他の選択オブジェクトにbpy.ops.object.join_shapes()でコピー
            for obj in selected_objs:
                if obj == active_obj:
                    continue
                func_object_utils.deselect_all_objects()
                func_object_utils.set_active_object(obj)
                func_object_utils.select_object(active_obj)
                print(f"Copy Shapekey: {active_obj} -> {obj}")
                bpy.ops.object.join_shapes()

            self.report({'INFO'}, "Finished")
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
        ("*", "Copy Shapekeys"): "シェイプキーをコピー",
        ("*", "Adds the shape of the active object to another object as a shape key"): "アクティブオブジェクトの形状をシェイプキーとして他のオブジェクトに追加します",
        ("*", "Finished"): "完了しました",
    },
}


def register():
    bpy.utils.register_class(OBJECT_OT_mizore_copy_shapekey_to_others)
    bpy.app.translations.register(__name__, translations_dict)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_mizore_copy_shapekey_to_others)
    bpy.app.translations.unregister(__name__)