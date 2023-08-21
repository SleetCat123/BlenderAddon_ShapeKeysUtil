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
from bpy.props import BoolProperty
from .. import consts
from ..funcs import func_apply_modifiers_with_shapekeys
from ..funcs.utils import func_object_utils


class OBJECT_OT_specials_shapekeys_util_apply_modifiers(bpy.types.Operator):
    bl_idname = "object.shapekeys_util_apply_modifiers"
    bl_label = "Apply Modifiers"
    bl_description = bpy.app.translations.pgettext(bl_idname + consts.DESC)
    bl_options = {'REGISTER', 'UNDO'}

    duplicate: BoolProperty(name="Duplicate", default=False,
                            description=bpy.app.translations.pgettext(bl_idname + "duplicate"))
    remove_nonrender: BoolProperty(name="Remove NonRender", default=True,
                                   description=bpy.app.translations.pgettext(bl_idname + "remove_nonrender"))

    @classmethod
    def poll(cls, context):
        return any(obj.type == 'MESH' for obj in bpy.context.selected_objects)

    def execute(self, context):
        active = func_object_utils.get_active_object()
        selected_objects = bpy.context.selected_objects
        targets = [d for d in selected_objects if d.type == 'MESH']
        for obj in targets:
            func_object_utils.set_active_object(obj)
            b = func_apply_modifiers_with_shapekeys.apply_modifiers_with_shapekeys(self, self.duplicate, self.remove_nonrender)
            if not b:
                return {'CANCELLED'}
        func_object_utils.select_objects(selected_objects, True)
        func_object_utils.set_active_object(active)
        return {'FINISHED'}


def register():
    bpy.utils.register_class(OBJECT_OT_specials_shapekeys_util_apply_modifiers)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_specials_shapekeys_util_apply_modifiers)
