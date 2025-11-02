import bpy


def update_mesh_deform_addon_is_found():
    try:
        return hasattr(bpy.types, bpy.ops.object.mizore_update_mesh_deform.idname())
    except AttributeError:
        return False
