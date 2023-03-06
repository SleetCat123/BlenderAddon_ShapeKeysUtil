import bpy


def select_object(obj, value=True):
    obj.select_set(value)


def select_objects(objects, value=True):
    for obj in objects:
        select_object(obj, value)


def get_active_object():
    return bpy.context.view_layer.objects.active


def set_active_object(obj):
    bpy.context.view_layer.objects.active=obj


def deselect_all_objects():
    print("deselect_all_objects")
    targets = bpy.context.selected_objects
    for obj in targets:
        select_object(obj, False)
    # bpy.context.view_layer.objects.active = None


def set_object_name(obj, name):
    obj.name = name
    if obj.data:
        obj.data.name = name


def select_axis(mode='POSITIVE', axis='X', threshold=0.0001):
    if mode == 'POSITIVE':
        mode = 'POS'
    elif mode == 'NEGATIVE':
        mode = 'NEG'
    elif mode == 'ALIGNED':
        mode = 'ALIGN'
    bpy.ops.mesh.select_axis(sign=mode, axis=axis, threshold=threshold)


def get_addon_prefs():
    return bpy.context.preferences.addons[__package__].preferences
