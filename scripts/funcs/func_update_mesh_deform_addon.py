import bpy


def update_mesh_deform_addon(obj, modifier, use_update_mesh_deform_addon):
    if use_update_mesh_deform_addon and(modifier.type == 'MESH_DEFORM' or modifier.type == 'SURFACE_DEFORM'):
        temp_active_modifier = obj.modifiers.active
        try:
            obj.modifiers.active = modifier
            bpy.ops.object.mizore_update_mesh_deform(mode_target = "ACTIVE", until_active_modifier = True)
        except AttributeError:
            obj.modifiers.clear()
            t = "!!! Failed to load MeshDeformUtils !!! - on apply modifier"
            print(t)
            operator.report({ 'ERROR'}, t)
        finally:
            obj.modifiers.active = temp_active_modifier