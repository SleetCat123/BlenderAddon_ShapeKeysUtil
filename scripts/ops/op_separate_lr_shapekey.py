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
from ..funcs import func_separate_lr_shapekey
from ..funcs.utils import func_object_utils


class OBJECT_OT_specials_shapekeys_util_separate_lr_shapekey(bpy.types.Operator):
    bl_idname = "object.shapekeys_util_separate_lr_shapekey"
    bl_label = "Separate Shape Key Left and Right"
    bl_description = "A selected shape key separate left and right based on object origin."
    bl_options = {'REGISTER', 'UNDO'}

    keep_original: BoolProperty(
        name="Keep Original",
        default=False,
        description="Keep the shape key before the left-right split"
    )
    enable_sort: BoolProperty(
        name="Enable Sort",
        default=True,
        description="Result shape keys move to below target shape key"
    )

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj.type == 'MESH' and obj.data.shape_keys and len(obj.data.shape_keys.key_blocks) != 0

    def execute(self, context):
        try:
            obj = context.object
            func_object_utils.set_active_object(obj)

            # 頂点を全て表示
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.reveal()
            bpy.ops.object.mode_set(mode='OBJECT')

            func_separate_lr_shapekey.separate_lr_shapekey(
                source_shape_key_index=obj.active_shape_key_index,
                duplicate=self.keep_original, 
                enable_sort=self.enable_sort
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
        ( "*", "A selected shape key separate left and right based on object origin." ): "現在のシェイプキーを\nオブジェクト原点基準で左右別々のシェイプキーにします",
        ( "*", "Keep Original" ): "元のシェイプキーを残す",
        ( "*", "Keep the shape key before the left-right split" ): "左右分割前のシェイプキーを残します。\n"
        "注意：左右分割する前とした後のシェイプキーを同時に有効化するとモデルが意図しない見た目になる可能性があります。\n"
        "（シェイプキーが二重にかかるため）",
        ( "*", "Enable Sort" ): "分割後の並び替え",
        ( "*", "Result shape keys move to below target shape key" ): "左右分割後のシェイプキーを分割前シェイプキーのすぐ下に移動します",
    },
}


def register():
    bpy.utils.register_class(OBJECT_OT_specials_shapekeys_util_separate_lr_shapekey)
    bpy.app.translations.register(__name__, translations_dict)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_specials_shapekeys_util_separate_lr_shapekey)
    bpy.app.translations.unregister(__name__)