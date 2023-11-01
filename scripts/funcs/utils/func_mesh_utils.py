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
from . import func_object_utils


def select_axis(mode='POSITIVE', axis='X', threshold=0.0001):
    if mode == 'POSITIVE':
        mode = 'POS'
    elif mode == 'NEGATIVE':
        mode = 'NEG'
    elif mode == 'ALIGNED':
        mode = 'ALIGN'
    bpy.ops.mesh.select_axis(sign=mode, axis=axis, threshold=threshold)


def update_mesh():
    obj = func_object_utils.get_active_object()
    if obj and obj.data:
        obj.data.update()
