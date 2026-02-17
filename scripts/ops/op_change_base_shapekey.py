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

from ..funcs.func_change_base_shapekey import change_base_shapekey
from ..funcs.utils import func_object_utils


class OBJECT_OT_shapekeys_util_change_base_shapekey(bpy.types.Operator):
    bl_idname = "object.shapekeys_util_change_base_shapekey"
    bl_label = "Change Base Shape Key"
    bl_description = "Apply specified shape key as basis and create reverse shape key"
    bl_options = {'REGISTER', 'UNDO'}

    source_shapekey_name: StringProperty(
        name="Source Shape Key",
        description="Shape key to apply as the new Basis",
        default="",
    )
    reverse_shapekey_name: StringProperty(
        name="Reverse Shape Key Name",
        description="Name for the reverse shape key (stores original Basis shape)",
        default="",
    )

    @classmethod
    def poll(cls, context):
        obj = context.object
        return (
            obj is not None
            and obj.type == 'MESH'
            and obj.data.shape_keys is not None
            and len(obj.data.shape_keys.key_blocks) > 1
        )

    def invoke(self, context, event):
        obj = context.object
        key_blocks = obj.data.shape_keys.key_blocks
        # アクティブシェイプキーをデフォルトに設定
        active_index = obj.active_shape_key_index
        if active_index > 0 and not self.source_shapekey_name:
            self.source_shapekey_name = key_blocks[active_index].name
        if not self.reverse_shapekey_name and self.source_shapekey_name:
            self.reverse_shapekey_name = f"Reverse_{self.source_shapekey_name}"
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop_search(
            self, "source_shapekey_name",
            context.object.data.shape_keys, "key_blocks",
            text="Source",
        )
        layout.prop(self, "reverse_shapekey_name", text="Reverse Name")

    def execute(self, context):
        if not self.source_shapekey_name:
            self.report({'ERROR'}, "Source shape key name is empty")
            return {'CANCELLED'}
        if not self.reverse_shapekey_name:
            self.report({'ERROR'}, "Reverse shape key name is empty")
            return {'CANCELLED'}

        try:
            obj = context.object
            func_object_utils.set_active_object(obj)
            result = change_base_shapekey(obj, self.source_shapekey_name, self.reverse_shapekey_name)
            if result:
                self.report({'INFO'}, f"Changed base: '{self.source_shapekey_name}' -> Basis")
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, f"Failed to change base shape key '{self.source_shapekey_name}'")
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
        ("*", "Apply specified shape key as basis and create reverse shape key"):
            "指定シェイプキーをBasis形状に適用し、逆シェイプキーを作成します",
        ("*", "Source Shape Key"): "ソースシェイプキー",
        ("*", "Shape key to apply as the new Basis"):
            "新しいBasisとして適用するシェイプキー",
        ("*", "Reverse Shape Key Name"): "逆シェイプキー名",
        ("*", "Name for the reverse shape key (stores original Basis shape)"):
            "逆シェイプキーの名前（元のBasis形状を保存）",
    },
}


def register():
    bpy.utils.register_class(OBJECT_OT_shapekeys_util_change_base_shapekey)
    bpy.app.translations.register(__name__, translations_dict)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_shapekeys_util_change_base_shapekey)
    bpy.app.translations.unregister(__name__)
