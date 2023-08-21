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
from . import func_object_utils


def find_collection(name):
    return next((c for c in bpy.context.scene.collection.children if name in c.name), None)


def find_layer_collection(name):
    return next((c for c in bpy.context.view_layer.layer_collection.children if name in c.name), None)


def recursive_get_collections(collection):
    def recursive_get_collections_main(col, result):
        result.append(col)
        for child in col.children:
            result = recursive_get_collections_main(child, result)
        return result

    return recursive_get_collections_main(collection, [])


def get_all_collections():
    result = recursive_get_collections(bpy.context.scene.collection)
    return result


def get_collection_objects(collection, include_children_collections):
    if collection is None:
        return []
    result = set(collection.objects)
    if include_children_collections:
        cols = recursive_get_collections(collection)
        for c in cols[1:]:
            result = result | set(c.objects)
    return result


# 現在選択中のオブジェクトのうち指定コレクションに属するものだけを選択した状態にする
def select_collection_only(collection, include_children_objects, include_children_collections, set_visible):
    if collection is None:
        return
    targets = bpy.context.selected_objects
    if include_children_collections:
        # コレクションと子以下のコレクションにあるオブジェクトだけを選択する
        assigned_objs_set = set()
        cols = recursive_get_collections(collection)
        for c in cols:
            assigned_objs_set = assigned_objs_set | set(c.objects)
        # 対象コレクション（子階層以下のコレクションを含む）に属するオブジェクトと選択中オブジェクトの積集合
        assigned_objs_set = assigned_objs_set & set(targets)
    else:
        # 対象コレクションに属するオブジェクトと選択中オブジェクトの積集合
        assigned_objs_set = set(collection.objects) & set(targets)
    assigned_objs = list(assigned_objs_set)
    result = assigned_objs
    if include_children_objects:
        for obj in assigned_objs:
            func_object_utils.deselect_all_objects()
            if set_visible:
                obj.hide_set(False)
            func_object_utils.select_object(obj, True)
            func_object_utils.set_active_object(obj)
            if bpy.context.object.mode != 'OBJECT':
                # Armatureをアクティブにしたとき勝手にPoseモードになる場合があるためここで確実にObjectモードにする
                bpy.ops.object.mode_set(mode='OBJECT')
            # オブジェクトの子も対象に含める
            func_object_utils.select_children_recursive()
            children = bpy.context.selected_objects
            for child in children:
                if (obj != child) and (child in targets):
                    result.append(child)
    func_object_utils.deselect_all_objects()
    func_object_utils.select_objects(result, True)
    return result


def deselect_collection(collection):
    if collection is None:
        return
    print("Deselect Collection: " + collection.name)
    active = func_object_utils.get_active_object()
    targets = bpy.context.selected_objects
    # 処理targetsから除外するオブジェクトの選択を外す
    # 対象コレクションに属するオブジェクトと選択中オブジェクトの積集合
    assigned_objs = collection.objects
    for obj in assigned_objs:
        func_object_utils.deselect_all_objects()
        temp_hide = obj.hide_get()
        obj.hide_set(False)
        func_object_utils.select_object(obj, True)
        func_object_utils.set_active_object(obj)
        if bpy.context.object.mode != 'OBJECT':
            # Armatureをアクティブにしたとき勝手にPoseモードになる場合があるためここで確実にObjectモードにする
            bpy.ops.object.mode_set(mode='OBJECT')
        # オブジェクトの子も除外対象に含める
        func_object_utils.select_children_recursive()
        children = bpy.context.selected_objects
        for child in children:
            if child in targets:
                targets.remove(child)
            if child == active:
                active = None
            print("Deselect: " + child.name)
        obj.hide_set(temp_hide)
    func_object_utils.deselect_all_objects()
    func_object_utils.select_objects(targets, True)
    if active is not None:
        func_object_utils.set_active_object(active)


# 選択オブジェクトを指定名のグループに入れたり外したり
def assign_object_group(group_name, assign=True):
    collection = find_collection(group_name)
    if not collection:
        if assign:
            # コレクションが存在しなければ新規作成
            collection = bpy.data.collections.new(name=group_name)
            bpy.context.scene.collection.children.link(collection)
        else:
            # コレクションが存在せず、割り当てがfalseなら何もせず終了
            return

    active = func_object_utils.get_active_object()
    targets = bpy.context.selected_objects
    for obj in targets:
        if assign:
            func_object_utils.set_active_object(obj)
            if obj.name not in collection.objects:
                # コレクションに追加
                collection.objects.link(obj)
        else:
            if obj.name in collection.objects:
                # コレクションから外す
                collection.objects.unlink(obj)

    if not collection.objects:
        # コレクションが空なら削除する
        bpy.context.scene.collection.children.unlink(collection)
        bpy.data.collections.remove(collection)

    # アクティブオブジェクトを元に戻す
    func_object_utils.set_active_object(active)


def hide_collection(context, group_name, hide=True):
    layer_col = find_layer_collection(group_name)
    if layer_col:
        layer_col.hide_viewport = hide
