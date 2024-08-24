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
from .ops import (
    op_apply_modifiers, 
    op_separate_lr_shapekey,
    op_separate_lr_shapekey_all_tag_detect, 
    op_assign_lr_shapekey_tag, 
    op_separate_lr_shapekey_all,
    op_separate_shapekeys,
    op_apply_selected_modifiers,
)


# オブジェクトモード　Special → ShapeKeys Util を登録する
def INFO_MT_object_specials_shapekeys_util_menu(self, context):
    self.layout.menu(VIEW3D_MT_object_specials_shapekeys_util.bl_idname)


# オブジェクトモード　Special → ShapeKeys Util にコマンドを登録するクラス
class VIEW3D_MT_object_specials_shapekeys_util(bpy.types.Menu):
    bl_label = "ShapeKeys Util"
    bl_idname = "VIEW3D_MT_object_specials_shapekeys_util"

    def draw(self, context):
        layout = self.layout
        layout.operator(op_apply_modifiers.OBJECT_OT_specials_shapekeys_util_apply_modifiers.bl_idname)
        layout.operator(op_apply_selected_modifiers.OBJECT_OT_mizore_shapekeys_util_apply_selected_modifiers.bl_idname)
        layout.operator(op_separate_shapekeys.OBJECT_OT_specials_shapekeys_util_shapekeys_to_objects.bl_idname)
        layout.separator()
        layout.operator(op_separate_lr_shapekey.OBJECT_OT_specials_shapekeys_util_separate_lr_shapekey.bl_idname)
        layout.operator(
            op_separate_lr_shapekey_all.OBJECT_OT_specials_shapekeys_util_separate_lr_shapekey_all.bl_idname)
        layout.operator(
            op_separate_lr_shapekey_all_tag_detect.OBJECT_OT_specials_shapekeys_util_separate_lr_shapekey_all_tag_detect.bl_idname)
        layout.operator(op_assign_lr_shapekey_tag.OBJECT_OT_specials_shapekeys_util_assign_lr_shapekey_tag.bl_idname)


def register():
    bpy.utils.register_class(VIEW3D_MT_object_specials_shapekeys_util)
    bpy.types.VIEW3D_MT_object_context_menu.append(INFO_MT_object_specials_shapekeys_util_menu)


def unregister():
    bpy.utils.unregister_class(VIEW3D_MT_object_specials_shapekeys_util)
    bpy.types.VIEW3D_MT_object_context_menu.remove(INFO_MT_object_specials_shapekeys_util_menu)
