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
from ..funcs import func_separate_shapekeys
from ..funcs.utils import func_object_utils


def apply_selected_modifier(operator, original_obj):
    func_object_utils.set_active_object(original_obj)
    func_object_utils.deselect_all_objects()
    active_mod_name = original_obj.modifiers.active.name
    print(f"Active Mod: {active_mod_name}")
    # シェイプキーをもつオブジェクトのモディファイアを適用
    if original_obj.data.shape_keys and original_obj.data.shape_keys.key_blocks:
        basis_obj = func_object_utils.duplicate_object(original_obj, False)
        separated_objects = func_separate_shapekeys.separate_shapekeys(
            duplicate=False,
            enable_apply_modifiers=False,
            remove_nonrender=False,
            keep_original_shapekeys=False
        )
        print(f"Basis: {basis_obj.name}")
        try:
            func_object_utils.set_active_object(basis_obj)
            bpy.ops.object.modifier_apply(modifier=active_mod_name)
            for separated_obj in separated_objects:
                print(separated_obj.name)
                func_object_utils.set_active_object(separated_obj)
                bpy.ops.object.modifier_apply(modifier=active_mod_name)
        except Exception as e:
            print(e)
            operator.report({'ERROR'}, str(e))
            # 処理中オブジェクトを削除
            func_object_utils.remove_object(basis_obj)
            func_object_utils.remove_objects(separated_objects)
            func_object_utils.set_active_object(original_obj)
            return {'CANCELLED'}

        prev_obj_name = basis_obj.name
        prev_vert_count = len(basis_obj.data.vertices)
        func_object_utils.select_object(basis_obj, True)
        func_object_utils.set_active_object(basis_obj)
        for obj in separated_objects:
            vert_count = len(obj.data.vertices)
            print("current: [{1}]({3})   prev: [{0}]({2})".format(
                prev_obj_name,
                obj.name, 
                str(prev_vert_count),
                str(vert_count))
                )
            if vert_count != prev_vert_count:
                # 前回のシェイプキーと頂点数が違ったら警告して処理を取り消し
                warn = bpy.app.translations.pgettext("mizore_error_apply_mod_with_shapekey_verts_count_difference").format(
                    obj_1 = prev_obj_name, 
                    obj_verts_1 = prev_vert_count,
                    obj_2 = obj.name,
                    obj_verts_2 = vert_count
                    )
                operator.report({'ERROR'}, warn)
                print("!!!!! " + warn + "!!!!!")
                # 処理中オブジェクトを削除
                func_object_utils.remove_object(basis_obj)
                func_object_utils.remove_objects(separated_objects)
                func_object_utils.set_active_object(original_obj)
                return False

            prev_vert_count = vert_count
            prev_obj_name = obj.name

            # 一気にjoin_shapesするとシェイプキーの順番がおかしくなるので1つずつ
            # Armatureによる変形を無効化
            for modifier in obj.modifiers:
                if modifier.type == 'ARMATURE':
                    modifier.show_viewport = False
                    modifier.show_render = False
            func_object_utils.select_object(obj, True)
            print("Join: [{2}]({3}) -> [{0}]({1})".format(
                basis_obj.name, 
                str(len(basis_obj.data.vertices)), 
                obj.name,
                str(vert_count))
                )
            # オブジェクトを1つにまとめなおす
            bpy.ops.object.join_shapes()
            func_object_utils.select_object(obj, False)
        # シェイプキーの名前と数値を復元
        basis_obj.active_shape_key_index = original_obj.active_shape_key_index
        for i, shapekey in enumerate(basis_obj.data.shape_keys.key_blocks):
            shapekey.name = original_obj.data.shape_keys.key_blocks[i].name
            shapekey.value = original_obj.data.shape_keys.key_blocks[i].value

        # オリジナルオブジェクトに反映
        original_obj.data = basis_obj.data
        original_obj.modifiers.remove(original_obj.modifiers[active_mod_name])
        func_object_utils.remove_object(basis_obj)
        func_object_utils.remove_objects(separated_objects)
        func_object_utils.select_object(original_obj, True)
        func_object_utils.set_active_object(original_obj)
    else:
        # シェイプキーを持たないオブジェクトのモディファイアを適用
        bpy.ops.object.modifier_apply(modifier=active_mod_name)
    return True
