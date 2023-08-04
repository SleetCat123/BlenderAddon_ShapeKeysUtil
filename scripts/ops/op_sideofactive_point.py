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
from bpy.props import FloatVectorProperty, EnumProperty, FloatProperty
from .. import consts, func_select_axis_from_point


class MESH_OT_specials_shapekeys_util_sideofactive_point(bpy.types.Operator):
    bl_idname = "edit_mesh.shapekeys_util_sideofactive_point"
    bl_label = "Select Side of Active from Point"
    bl_description = bpy.app.translations.pgettext(bl_idname + consts.DESC)
    bl_options = {'REGISTER', 'UNDO'}

    point: FloatVectorProperty(name="Point")

    mode: EnumProperty(
        name="Axis Mode",
        default='NEGATIVE',
        items=(
            ('POSITIVE', "Positive Axis", ""),
            ('NEGATIVE', "Negative Axis", ""),
            ('ALIGNED', "Aligned Axis", ""),
        )
    )

    axis: EnumProperty(
        name="Axis",
        default='X',
        items=(
            ('X', "X", ""),
            ('Y', "Y", ""),
            ('Z', "Z", ""),
        )
    )

    threshold: FloatProperty(
        name="Threshold",
        min=0.000001, max=50.0,
        soft_min=0.00001, soft_max=10.0,
        default=0.0001,
    )

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj.type == 'MESH'

    def execute(self, context):
        func_select_axis_from_point.select_axis_from_point(self.point, self.mode, self.axis, self.threshold)

        return {'FINISHED'}


def register():
    bpy.utils.register_class(MESH_OT_specials_shapekeys_util_sideofactive_point)


def unregister():
    bpy.utils.unregister_class(MESH_OT_specials_shapekeys_util_sideofactive_point)
