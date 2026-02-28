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
from ..funcs.func_apply_modifiers_with_shapekeys_helpers.apply_surface_deform_to_basis import (
    apply_single_surface_deform_to_basis,
)
from ..funcs.utils import func_object_utils


def apply_selected_modifier(original_obj):
    func_object_utils.set_active_object(original_obj)
    func_object_utils.deselect_all_objects()
    active_modifier = original_obj.modifiers.active
    active_mod_name = active_modifier.name
    print(f"Active Mod: {active_mod_name}")
    if not original_obj.data.shape_keys or not original_obj.data.shape_keys.key_blocks:
        # シェイプキーを持たないオブジェクトのモディファイアを適用
        print("no shapekeys")
        bpy.ops.object.modifier_apply(modifier=active_mod_name)
        return True

    # SurfaceDeformモディファイアの場合は専用処理を実行
    if active_modifier.type == 'SURFACE_DEFORM':
        print(f"SurfaceDeform modifier detected: {active_mod_name}")
        apply_single_surface_deform_to_basis(
            source_obj=original_obj,
            modifier=active_modifier,
            use_update_mesh_deform_addon=False,
            remove_nonrender=False
        )
        return True

    # シェイプキーをもつオブジェクトのモディファイアを適用
    print("has shapekeys")
    basis_obj = func_object_utils.duplicate_object(original_obj, False)
    separated_objects = func_separate_shapekeys.separate_shapekeys(
        duplicate=False,
        enable_apply_modifiers=False,
        skip_modifier_types=set(),
        remove_nonrender=False,
        keep_original_shapekeys=False
    )
    print(f"Basis: {basis_obj.name}")
    func_object_utils.set_active_object(basis_obj)
    bpy.ops.object.modifier_apply(modifier=active_mod_name)
    for separated_obj in separated_objects:
        print(separated_obj.name)
        func_object_utils.set_active_object(separated_obj)
        bpy.ops.object.modifier_apply(modifier=active_mod_name)

    prev_obj_name = basis_obj.name
    prev_vert_count = len(basis_obj.data.vertices)
    func_object_utils.select_object(basis_obj, True)
    func_object_utils.set_active_object(basis_obj)
    for obj in separated_objects:
        vert_count = len(obj.data.vertices)
        print(f"current: [{obj.name}]({vert_count})   prev: [{prev_obj_name}]({prev_vert_count})")
        if vert_count != prev_vert_count:
            # 前回のシェイプキーと頂点数が違ったら警告して処理を取り消し
            warn = bpy.app.translations.pgettext("mizore_error_apply_mod_with_shapekey_verts_count_difference").format(
                obj_1 = prev_obj_name, 
                obj_verts_1 = prev_vert_count,
                obj_2 = obj.name,
                obj_verts_2 = vert_count
                )
            print("!!!!! " + warn + "!!!!!")
            raise Exception(warn)

        prev_vert_count = vert_count
        prev_obj_name = obj.name

        # 一気にjoin_shapesするとシェイプキーの順番がおかしくなるので1つずつ
        # Armatureによる変形を無効化
        for modifier in obj.modifiers:
            if modifier.type == 'ARMATURE':
                modifier.show_viewport = False
                modifier.show_render = False
        func_object_utils.select_object(obj, True)
        print(f"Join: [{obj.name}]({vert_count}) -> [{basis_obj.name}]({len(basis_obj.data.vertices)})")
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
    return True
