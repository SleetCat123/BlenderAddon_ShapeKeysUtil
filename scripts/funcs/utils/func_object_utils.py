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


def get_active_object():
    return bpy.context.view_layer.objects.active


def set_active_object(obj):
    # try:
    bpy.context.view_layer.objects.active = obj
    # except ReferenceError:
    #    print("removed")


def get_children_objects(obj, only_current_view_layer: bool = True):
    all_objects = bpy.data.objects
    if only_current_view_layer:
        current_layer_objects_name = bpy.context.window.view_layer.objects.keys()
        return [child for child in all_objects if
                child.parent == obj and child.name in current_layer_objects_name]
    else:
        return [child for child in all_objects if child.parent == obj]


def get_children_recursive(targets, only_current_view_layer: bool = True):
    result = []

    def recursive(t):
        result.append(t)
        children = get_children_objects(t, only_current_view_layer)
        for child in children:
            recursive(child)

    if targets is bpy.types.Object:
        targets = [targets]
    for obj in targets:
        recursive(obj)
    return result


def select_children_recursive(targets=None, only_current_view_layer: bool = True):
    def recursive(t):
        select_object(t, True)
        children = get_children_objects(obj=t, only_current_view_layer=only_current_view_layer)
        for child in children:
            recursive(child)

    if targets is None:
        targets = bpy.context.selected_objects
    elif targets is bpy.types.Object:
        targets = [targets]
    for obj in targets:
        recursive(obj)


def select_all_objects():
    targets = bpy.context.scene.collection.all_objects
    for obj in targets:
        select_object(obj, True)


def deselect_all_objects():
    print("deselect_all_objects")
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


def get_selected_root_objects():
    selected_objects = bpy.context.selected_objects
    not_root = []
    root_objects = []
    for obj in selected_objects:
        if obj in not_root:
            continue
        parent = obj
        while True:
            parent = parent.parent
            print(parent)
            if parent is None:
                # 親以上のオブジェクトに選択中オブジェクトが存在しなければ、そのオブジェクトはrootとなる
                root_objects.append(obj)
                break
            if parent in selected_objects:
                not_root.append(parent)
                break
    return root_objects


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
        bpy.ops.object.duplicate(linked=linked)
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
