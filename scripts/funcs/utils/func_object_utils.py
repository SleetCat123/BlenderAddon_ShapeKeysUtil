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

_MODIFIER_COPY_SKIP_PROPERTIES = {
    "bl_rna",
    "name",
    "rna_type",
    "type",
}


def _snapshot_property_value(value):
    if isinstance(value, (str, int, float, bool, type(None))):
        return value
    if isinstance(value, set):
        return set(value)
    if isinstance(value, tuple):
        return tuple(value)
    if isinstance(value, list):
        return list(value)
    if isinstance(value, bpy.types.ID):
        return value

    copy_method = getattr(value, "copy", None)
    if callable(copy_method):
        try:
            return copy_method()
        except Exception:
            pass

    if hasattr(value, "__iter__"):
        try:
            return tuple(value)
        except Exception:
            pass

    return value


def select_object(obj, value=True):
    try:
        obj.select_set(value)
    except RuntimeError as e:
        print(e)


def select_objects(objects, value=True):
    for obj in objects:
        try:
            obj.select_set(value)
        except RuntimeError as e:
            print(e)


def select_objects_by_name(names, value=True):
    for name in names:
        obj = bpy.data.objects.get(name)
        obj.select_set(value)


def get_active_object():
    return bpy.context.view_layer.objects.active


def set_active_object(obj):
    # try:
    bpy.context.view_layer.objects.active = obj
    # except ReferenceError:
    #    print("removed")


def get_current_view_layer_objects():
    current_layer_objects_name = bpy.context.window.view_layer.objects.keys()
    all_objects = bpy.data.objects
    return [obj for obj in all_objects if obj.name in current_layer_objects_name]


def get_children_objects(obj, only_current_view_layer: bool = True):
    all_objects = bpy.data.objects
    if only_current_view_layer:
        current_layer_objects_name = bpy.context.window.view_layer.objects.keys()
        return [child for child in all_objects if
                child.parent == obj and child.name in current_layer_objects_name]
    else:
        return [child for child in all_objects if child.parent == obj]


def get_children_recursive(targets, only_current_view_layer: bool = True, contains_self: bool = True):
    result = []

    def recursive(t):
        result.append(t)
        children = get_children_objects(t, only_current_view_layer)
        for child in children:
            recursive(child)

    if not hasattr(targets, '__iter__'):
        targets = [targets]
    # print("get_children_recursive  targets: " + str(targets))
    for obj in targets:
        recursive(obj)
    if not contains_self:
        for obj in targets:
            if obj in result:
                result.remove(obj)
    return result


# key: parent, value: children nameなdictを返す
def get_children_name_table(only_current_view_layer: bool = True):
    current_layer_objects_name = bpy.context.window.view_layer.objects.keys()
    all_objects = bpy.data.objects
    result = {}
    for obj in all_objects:
        if only_current_view_layer and obj.name not in current_layer_objects_name:
            continue
        if obj.name not in result:
            result[obj.name] = []
        parent = obj.parent
        if parent:
            if parent.name not in result:
                result[parent.name] = []
            result[parent.name].append(obj.name)
    return result


def select_children_recursive(targets=None, only_current_view_layer: bool = True):
    def recursive(t):
        select_object(t, True)
        children = get_children_objects(obj=t, only_current_view_layer=only_current_view_layer)
        for child in children:
            recursive(child)

    if targets is None:
        targets = bpy.context.selected_objects
    elif not hasattr(targets, '__iter__'):
        targets = [targets]
    for obj in targets:
        recursive(obj)


def select_all_objects():
    targets = bpy.context.scene.collection.all_objects
    for obj in targets:
        select_object(obj, True)


def deselect_all_objects():
    # print("deselect_all_objects")
    targets = bpy.context.scene.collection.all_objects
    for obj in targets:
        select_object(obj, False)
    # bpy.context.view_layer.objects.active = None


def ensure_single_user_object_data(targets=None):
    if targets is None:
        targets = bpy.context.selected_objects
    elif isinstance(targets, bpy.types.Object):
        targets = [targets]
    else:
        targets = list(targets)

    copied_count = 0
    for obj in targets:
        if obj is None:
            continue
        data = getattr(obj, "data", None)
        if data is None:
            continue
        if getattr(data, "users", 0) <= 1:
            continue

        original_name = data.name
        original_users = data.users
        obj.data = data.copy()
        copied_count += 1
        print(
            "[func_object_utils] duplicated shared object data: "
            f"{obj.name} ({original_name} users={original_users})"
        )
    return copied_count


def copy_modifier_settings(source_modifier, target_modifier):
    failed = []
    for prop in source_modifier.bl_rna.properties:
        if prop.identifier in _MODIFIER_COPY_SKIP_PROPERTIES:
            continue
        if prop.is_readonly or prop.type == 'COLLECTION':
            continue
        try:
            setattr(target_modifier, prop.identifier, getattr(source_modifier, prop.identifier))
        except Exception as exc:
            failed.append(f"{prop.identifier}({exc})")
    return failed


def serialize_modifier_settings(source_modifier):
    settings = {}
    failed = []
    for prop in source_modifier.bl_rna.properties:
        if prop.identifier in _MODIFIER_COPY_SKIP_PROPERTIES:
            continue
        if prop.is_readonly or prop.type == 'COLLECTION':
            continue
        try:
            settings[prop.identifier] = _snapshot_property_value(
                getattr(source_modifier, prop.identifier)
            )
        except Exception as exc:
            failed.append(f"{prop.identifier}({exc})")
    return settings, failed


def apply_modifier_settings(target_modifier, settings):
    failed = []
    for prop_identifier, value in settings.items():
        try:
            setattr(target_modifier, prop_identifier, value)
        except Exception as exc:
            failed.append(f"{prop_identifier}({exc})")
    return failed


def serialize_modifiers(source_modifiers):
    snapshots = []
    failed = {}
    for source_modifier in source_modifiers:
        settings, serialize_failed = serialize_modifier_settings(source_modifier)
        snapshots.append({
            "name": source_modifier.name,
            "type": source_modifier.type,
            "settings": settings,
        })
        if serialize_failed:
            failed[source_modifier.name] = serialize_failed

    if failed:
        print(
            f"[func_object_utils] modifier serialize warnings: {failed}"
        )
    return snapshots, failed


def replace_modifiers_from_snapshots(target_obj, modifier_snapshots):
    while target_obj.modifiers:
        target_obj.modifiers.remove(target_obj.modifiers[-1])

    failed = {}
    for modifier_snapshot in modifier_snapshots:
        new_modifier = target_obj.modifiers.new(
            modifier_snapshot["name"],
            modifier_snapshot["type"],
        )
        copy_failed = apply_modifier_settings(
            new_modifier,
            modifier_snapshot["settings"],
        )
        if copy_failed:
            failed[new_modifier.name] = copy_failed

    if failed:
        print(
            f"[func_object_utils] modifier restore warnings on '{target_obj.name}': {failed}"
        )
    return failed


def replace_modifiers(target_obj, source_obj):
    while target_obj.modifiers:
        target_obj.modifiers.remove(target_obj.modifiers[-1])

    failed = {}
    for source_modifier in source_obj.modifiers:
        new_modifier = target_obj.modifiers.new(source_modifier.name, source_modifier.type)
        copy_failed = copy_modifier_settings(source_modifier, new_modifier)
        if copy_failed:
            failed[new_modifier.name] = copy_failed

    if failed:
        print(
            f"[func_object_utils] modifier copy warnings on '{target_obj.name}': {failed}"
        )
    return failed


def remove_object(target: bpy.types.Object = None):
    print("remove_object")
    if target is None:
        # target = get_active_object()
        raise Exception("Remove target is empty")

    data = None
    # オブジェクトを削除
    try:
        if target.data:
            data = target.data
        print("remove: " + str(target))
        bpy.data.objects.remove(target)
    except ReferenceError:
        pass

    # オブジェクトのデータを削除
    blocks = None
    data_type = type(data)
    if data_type == bpy.types.Mesh:
        blocks = bpy.data.meshes
    elif data_type == bpy.types.Armature:
        blocks = bpy.data.armatures
    elif data_type == bpy.types.Curve:
        blocks = bpy.data.curves
    elif data_type == bpy.types.Lattice:
        blocks = bpy.data.lattices
    elif data_type == bpy.types.Light:
        blocks = bpy.data.lights
    elif data_type == bpy.types.Camera:
        blocks = bpy.data.cameras
    elif data_type == bpy.types.MetaBall:
        blocks = bpy.data.metaballs
    elif data_type == bpy.types.GreasePencil:
        blocks = bpy.data.grease_pencils

    if blocks and data.users == 0:
        print("remove: " + str(data))
        blocks.remove(data)


def remove_objects(targets=None):
    print("remove_objects")
    if targets is None:
        # targets = bpy.context.selected_objects
        raise Exception("Remove target is empty")

    for obj in targets:
        remove_object(target=obj)


# targetsと子の中で最も上位階層にあるオブジェクト群を取得
def get_top_level_objects(targets):
    print("get_top_level_objects targets: " + str(targets))
    top_level_objects = []
    for obj in targets:
        parent = obj.parent
        is_root = True
        while parent:
            if parent in targets:
                is_root = False
                break
            parent = parent.parent
        if is_root:
            top_level_objects.append(obj)
    print("get_top_level_objects: " + str(top_level_objects))
    return top_level_objects


def duplicate_objects(
        source=None,
        linked: bool = False,
):
    if source is None:
        source = bpy.context.selected_objects
    else:
        deselect_all_objects()
        select_objects(source, True)
    print("Duplicate Source: " + str(source))
    bpy.ops.object.duplicate(linked=linked)
    result = bpy.context.selected_objects
    print("Duplicate Result: " + str(result))
    return result


def duplicate_object(
        source=None,
        linked: bool = False,
):
    if source is None:
        source = bpy.context.selected_objects
    print("Duplicate Source: " + str(source))
    if isinstance(source, bpy.types.Object):
        deselect_all_objects()
        select_object(source, True)
        set_active_object(source)
        mode_temp = source.mode
        if mode_temp != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.duplicate(linked=linked)
        if mode_temp != 'OBJECT':
            bpy.ops.object.mode_set(mode=mode_temp)
        result = bpy.context.selected_objects[0]
        print("Duplicate Result: " + str(result))
        return result
    else:
        deselect_all_objects()
        select_objects(source, True)
        bpy.ops.object.duplicate(linked=linked)
        result = bpy.context.selected_objects
        print("Duplicate Result: " + str(result))
        return result


def set_object_name(obj, name):
    obj.name = name
    if obj.data:
        obj.data.name = name

def set_parent(obj, parent):
    obj.parent = parent
    obj.matrix_parent_inverse = parent.matrix_world.inverted()

def hide_unselected_objects():
    for obj in bpy.context.scene.collection.all_objects:
        if not obj.select_get():
            obj.hide_set(True)

def is_hidden(obj: bpy.types.Object):
    return obj.hide_viewport or obj.hide_get()

def force_unhide(obj: bpy.types.Object):
    obj.hide_viewport = False
    obj.hide_set(False)
