import bpy
from bpy.props import BoolProperty
from . import func_utils, func_apply_modifiers_with_shapekeys


class OBJECT_OT_specials_shapekeys_util_apply_modifiers(bpy.types.Operator):
    bl_idname = "object.shapekeys_util_apply_modifiers"
    bl_label = "Apply Modifiers"
    bl_description = bpy.app.translations.pgettext(bl_idname + "_desc")
    bl_options = {'REGISTER', 'UNDO'}

    duplicate: BoolProperty(name="Duplicate", default=False,
                            description=bpy.app.translations.pgettext(bl_idname + "_duplicate"))
    remove_nonrender: BoolProperty(name="Remove NonRender", default=True,
                                   description=bpy.app.translations.pgettext("remove_nonrender"))

    @classmethod
    def poll(cls, context):
        return any(obj.type == 'MESH' for obj in bpy.context.selected_objects)

    def execute(self, context):
        active = func_utils.get_active_object()
        selected_objects = bpy.context.selected_objects
        targets = [d for d in selected_objects if d.type == 'MESH']
        for obj in targets:
            func_utils.set_active_object(obj)
            b = func_apply_modifiers_with_shapekeys.apply_modifiers_with_shapekeys(self, context.object, self.duplicate, self.remove_nonrender)
            if not b:
                return {'CANCELLED'}
        func_utils.select_objects(selected_objects, True)
        func_utils.set_active_object(active)
        return {'FINISHED'}


def register():
    bpy.utils.register_class(OBJECT_OT_specials_shapekeys_util_apply_modifiers)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_specials_shapekeys_util_apply_modifiers)
