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
from . import op_sideofactive_point


# エディットモード　Special → ShapeKeys Util を登録する
def INFO_MT_edit_mesh_specials_shapekeys_util_menu(self, context):
    self.layout.menu(VIEW3D_MT_edit_mesh_specials_shapekeys_util.bl_idname)


# エディットモード　Special → ShapeKeys Util にコマンドを登録するクラス
class VIEW3D_MT_edit_mesh_specials_shapekeys_util(bpy.types.Menu):
    bl_label = "ShapeKeys Util"
    bl_idname = "INFO_MT_edit_mesh_specials_shapekeys_util_menu"

    def draw(self, context):
        self.layout.operator(operator_sideofactive_point.MESH_OT_specials_shapekeys_util_sideofactive_point.bl_idname)


def register():
    bpy.utils.register_class(VIEW3D_MT_edit_mesh_specials_shapekeys_util)
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.append(INFO_MT_edit_mesh_specials_shapekeys_util_menu)


def unregister():
    bpy.utils.unregister_class(VIEW3D_MT_edit_mesh_specials_shapekeys_util)
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.remove(INFO_MT_edit_mesh_specials_shapekeys_util_menu)
