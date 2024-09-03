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
        result.remove(targets)
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
    for obj in bpy.context.selected_objects:
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
    if type(source) == bpy.types.Object:
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
