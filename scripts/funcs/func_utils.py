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
from BlenderAddon_ShapeKeysUtil.scripts.funcs import func_package_utils


def select_object(obj, value=True):
    obj.select_set(value)


def select_objects(objects, value=True):
    for obj in objects:
        select_object(obj, value)


def get_active_object():
    return bpy.context.view_layer.objects.active


def set_active_object(obj):
    bpy.context.view_layer.objects.active = obj


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
    return bpy.context.preferences.addons[func_package_utils.get_package_root()].preferences


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


def update_mesh():
    obj = get_active_object()
    if obj.mode == 'OBJECT':
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.object.mode_set(mode='OBJECT')
    else:
        mode_cache = obj.mode
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode=mode_cache)


def duplicate_object(obj: bpy.types.Object):
    temp_objects = bpy.context.selected_objects
    temp_active = get_active_object()
    deselect_all_objects()
    select_object(obj, True)
    bpy.ops.object.duplicate()
    result = get_active_object()
    set_active_object(temp_active)
    select_objects(temp_objects, True)
    return result

