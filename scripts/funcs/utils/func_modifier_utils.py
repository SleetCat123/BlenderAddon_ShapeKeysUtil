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


def get_target_object(modifier: bpy.types.Modifier):
    if hasattr(modifier, 'object'):
        return modifier.object
    if hasattr(modifier, 'mirror_object'):
        return modifier.mirror_object
    if hasattr(modifier, 'target'):
        return modifier.target


def set_target_object(modifier: bpy.types.Modifier, obj: bpy.types.Object):
    if hasattr(modifier, 'object'):
        modifier.object = obj
        return
    if hasattr(modifier, 'mirror_object'):
        modifier.mirror_object = obj
        return
    if hasattr(modifier, 'target'):
        modifier.target = obj
        return
