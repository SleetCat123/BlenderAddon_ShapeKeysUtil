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

from .. import consts
from ..funcs import func_apply_modifiers_with_shapekeys


# シェイプキーをもつオブジェクトのモディファイアを適用
# AutoMerge連携用
class OBJECT_OT_apply_modifiers_with_shapekeys_for_automerge_addon(bpy.types.Operator):
    bl_idname = "object.shapekeys_util_apply_mod_with_shapekeys_automerge"
    bl_label = "[Internal] Apply Modifiers With Shapekeys For AutoMerge Addon"
    bl_options = {'REGISTER', 'UNDO'}

    use_update_mesh_deform_addon: bpy.props.BoolProperty(
        name="Use Update Mesh Deform Addon",
        default=False,
        description="Use MeshDeformUtils Addon"
    )

    skip_modifier_types_str: bpy.props.StringProperty(
        name="Skip Modifier Types"
    )

    def execute(self, context):
        # カンマ区切りの文字列からスキップ対象モディファイアタイプのセットをパース
        skip_types = consts.parse_skip_modifier_types_str(self.skip_modifier_types_str)
        print(f"ShapekeysUtil - link_with_AutoMerge (skip_types={skip_types})")
        func_apply_modifiers_with_shapekeys.apply_modifiers_with_shapekeys(
            remove_nonrender=True,
            use_update_mesh_deform_addon=self.use_update_mesh_deform_addon,
            skip_modifier_types=skip_types)
        return {'FINISHED'}


classes = [
    OBJECT_OT_apply_modifiers_with_shapekeys_for_automerge_addon,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

