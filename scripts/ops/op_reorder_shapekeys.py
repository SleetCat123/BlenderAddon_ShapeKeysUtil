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

import traceback

import bpy
from bpy.props import StringProperty

from ..funcs.func_reorder_shapekeys import sort_shapekeys_by_name, swap_shapekeys
from ..funcs.utils import func_object_utils


class OBJECT_OT_shapekeys_util_sort_shapekeys_by_name(bpy.types.Operator):
    bl_idname = "object.shapekeys_util_sort_shapekeys_by_name"
    bl_label = "Sort Shape Keys by Name"
    bl_description = "Sort shape keys alphabetically (excluding Basis)"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.object
        return (
            obj is not None
            and obj.type == 'MESH'
            and obj.data.shape_keys is not None
            and len(obj.data.shape_keys.key_blocks) > 2
        )

    def execute(self, context):
        try:
            obj = context.object
            func_object_utils.set_active_object(obj)
            sort_shapekeys_by_name(obj)
            self.report({'INFO'}, "Shape keys sorted by name")
            return {'FINISHED'}
        except Exception as e:
            bpy.ops.ed.undo_push(message="Restore point")
            bpy.ops.ed.undo()
            bpy.ops.ed.undo_push(message="Restore point")
            traceback.print_exc()
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}


class OBJECT_OT_shapekeys_util_swap_shapekeys(bpy.types.Operator):
    bl_idname = "object.shapekeys_util_swap_shapekeys"
    bl_label = "Swap Shape Keys"
    bl_description = "Swap positions of two shape keys"
    bl_options = {'REGISTER', 'UNDO'}

    shapekey_a: StringProperty(
        name="Shape Key A",
        description="First shape key to swap",
        default="",
    )
    shapekey_b: StringProperty(
        name="Shape Key B",
        description="Second shape key to swap",
        default="",
    )

    @classmethod
    def poll(cls, context):
        obj = context.object
        return (
            obj is not None
            and obj.type == 'MESH'
            and obj.data.shape_keys is not None
            and len(obj.data.shape_keys.key_blocks) > 2
        )

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop_search(
            self, "shapekey_a",
            context.object.data.shape_keys, "key_blocks",
            text="A",
        )
        layout.prop_search(
            self, "shapekey_b",
            context.object.data.shape_keys, "key_blocks",
            text="B",
        )

    def execute(self, context):
        if not self.shapekey_a or not self.shapekey_b:
            self.report({'ERROR'}, "Both shape key names are required")
            return {'CANCELLED'}

        try:
            obj = context.object
            func_object_utils.set_active_object(obj)
            result = swap_shapekeys(obj, self.shapekey_a, self.shapekey_b)
            if result:
                self.report({'INFO'}, f"Swapped '{self.shapekey_a}' and '{self.shapekey_b}'")
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, "Failed to swap shape keys")
                return {'CANCELLED'}
        except Exception as e:
            bpy.ops.ed.undo_push(message="Restore point")
            bpy.ops.ed.undo()
            bpy.ops.ed.undo_push(message="Restore point")
            traceback.print_exc()
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}


translations_dict = {
    "ja_JP": {
        ("*", "Sort shape keys alphabetically (excluding Basis)"):
            "シェイプキーを名前のアルファベット順にソートします（Basisを除く）",
        ("*", "Swap positions of two shape keys"):
            "2つのシェイプキーの位置を入れ替えます",
        ("*", "Shape Key A"): "シェイプキーA",
        ("*", "First shape key to swap"): "入れ替えるシェイプキー（1つ目）",
        ("*", "Shape Key B"): "シェイプキーB",
        ("*", "Second shape key to swap"): "入れ替えるシェイプキー（2つ目）",
    },
}


def register():
    bpy.utils.register_class(OBJECT_OT_shapekeys_util_sort_shapekeys_by_name)
    bpy.utils.register_class(OBJECT_OT_shapekeys_util_swap_shapekeys)
    bpy.app.translations.register(__name__, translations_dict)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_shapekeys_util_sort_shapekeys_by_name)
    bpy.utils.unregister_class(OBJECT_OT_shapekeys_util_swap_shapekeys)
    bpy.app.translations.unregister(__name__)
