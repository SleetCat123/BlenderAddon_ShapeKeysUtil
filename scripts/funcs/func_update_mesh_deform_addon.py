import bpy


def update_mesh_deform_addon(obj, modifier, use_update_mesh_deform_addon):
    if not use_update_mesh_deform_addon:
        return False
    if modifier.type not in {'MESH_DEFORM', 'SURFACE_DEFORM'}:
        return False

    temp_active_modifier = obj.modifiers.active
    try:
        current_modifier = obj.modifiers.get(modifier.name)
        if current_modifier is None:
            return False
        obj.modifiers.active = current_modifier
        bpy.ops.object.mizore_update_mesh_deform(mode_target="ACTIVE", until_active_modifier=True)
        return True
    except AttributeError:
        print("!!! Failed to load MeshDeformUtils !!! - on apply modifier")
        return False
    except RuntimeError as e:
        print(f"!!! MeshDeformUtils update failed !!! [{obj.name}:{modifier.name}] {e}")
        return False
    finally:
        if temp_active_modifier and obj.modifiers.get(temp_active_modifier.name):
            obj.modifiers.active = obj.modifiers[temp_active_modifier.name]
