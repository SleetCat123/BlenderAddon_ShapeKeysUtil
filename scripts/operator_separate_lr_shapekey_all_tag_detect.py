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
from . import func_utils, func_separate_lr_shapekey_all


class OBJECT_OT_specials_shapekeys_util_separate_lr_shapekey_all_tag_detect(bpy.types.Operator):
    bl_idname = "object.shapekeys_util_separate_lr_shapekey_all_tag_detect"
    bl_label = "(Tag) Separate All Shape Key Left and Right"
    bl_description = bpy.app.translations.pgettext(bl_idname + "_desc")
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj.type == 'MESH' and obj.data.shape_keys and len(obj.data.shape_keys.key_blocks) != 0

    def execute(self, context):
        obj = context.object
        func_utils.set_active_object(obj)
        func_separate_lr_shapekey_all.separate_lr_shapekey_all(duplicate=False, enable_sort=False, auto_detect=True)
        return {'FINISHED'}


def register():
    bpy.utils.register_class(OBJECT_OT_specials_shapekeys_util_separate_lr_shapekey_all_tag_detect)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_specials_shapekeys_util_separate_lr_shapekey_all_tag_detect)