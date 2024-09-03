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
import bmesh
from BlenderAddon_ShapeKeysUtil.scripts.funcs.utils import func_object_utils, func_mesh_utils


# 指定座標を基準にSide of Active
def select_axis_from_point(point=(0, 0, 0), mode='POSITIVE', axis='X', threshold=0.0001):
    obj = func_object_utils.get_active_object()
    if obj.type != 'MESH':
        return

    bpy.ops.object.mode_set(mode='EDIT')
    temp_mesh_select_mode = bpy.context.tool_settings.mesh_select_mode 
    bpy.context.tool_settings.mesh_select_mode  = (True, False, False)
    bm = bmesh.from_edit_mesh(obj.data)

    axis_index = 0
    if axis == 'X':
        axis_index = 0
    elif axis == 'Y':
        axis_index = 1
    elif axis == 'Z':
        axis_index = 2
    else:
        raise ValueError('axis must be [X, Y, Z]')

    point = [point[0], point[1], point[2]]
    if mode == 'POSITIVE':
        point[axis_index] += -threshold
        for v in bm.verts:
            if v.co[axis_index] >= point[axis_index]:
                v.select = True
            else:
                v.select = False
    elif mode == 'NEGATIVE':
        point[axis_index] += threshold
        for v in bm.verts:
            if v.co[axis_index] <= point[axis_index]:
                v.select = True
            else:
                v.select = False
    elif mode == 'ALIGNED':
        for v in bm.verts:
            if (
                point[axis_index] - threshold <= v.co[axis_index] 
                and
                v.co[axis_index] <= point[axis_index] + threshold
            ):
                v.select = True
            else:
                v.select = False
    else:
        raise ValueError('mode must be [POSITIVE, NEGATIVE, ALIGNED]')
    bm.select_flush_mode()
    # bmesh.update_edit_mesh(obj.data)
    obj.update_from_editmode()
    bpy.context.tool_settings.mesh_select_mode  = temp_mesh_select_mode
    bm.free()
    del bm


