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
from bpy.props import FloatProperty, IntProperty
from . import func_package_utils


class addon_preferences(bpy.types.AddonPreferences):
    bl_idname = func_package_utils.get_package_root()
    
    wait_interval: IntProperty(name="Wait Interval", default=5, min=1, soft_min=1)
    wait_sleep: FloatProperty(name="Wait Sleep", default=0.5, min=0, soft_min=0, max=2, soft_max=2)
    
    def draw(self, context):
        layout = self.layout
        
        layout.prop(self, "wait_interval")
        layout.prop(self, "wait_sleep")


def register():
    bpy.utils.register_class(addon_preferences)


def unregister():
    bpy.utils.unregister_class(addon_preferences)
