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

from .. import consts
from ..funcs import (
    func_apply_as_shapekey,
    func_apply_modifiers,
    func_update_mesh_deform_addon,
)
from ..funcs.func_apply_modifiers_with_shapekeys_helpers.apply_each_shapekey_modifiers import (
    apply_each_shapekey_modifiers,
)
from ..funcs.func_apply_modifiers_with_shapekeys_helpers.apply_surface_deform_to_basis import (
    apply_surface_deform_to_basis,
)
from ..funcs.func_apply_modifiers_with_shapekeys_helpers.partial_apply_modifiers import (
    partial_apply_modifiers,
)
from ..funcs.utils import func_object_utils


# シェイプキーをもつオブジェクトのモディファイアを適用
def apply_modifiers_with_shapekeys(remove_nonrender=True, use_update_mesh_deform_addon=False):
    source_obj = func_object_utils.get_active_object()
    print(f"apply_modifiers_with_shapekeys: [{source_obj.name}] [{source_obj.type}]  {len(source_obj.modifiers)} modifiers")
    # Apply as shapekey用モディファイアのインデックスを検索
    apply_as_shape_index = -1
    apply_as_shape_modifier = None
    for i, modifier in enumerate(source_obj.modifiers):
        if consts.REGEX_APPLY_AS_SHAPEKEY_PREFIX.match(modifier.name):
            apply_as_shape_index = i
            apply_as_shape_modifier = modifier
            print(f"%AS% modifier is found: {str(apply_as_shape_index)} - {modifier.name}")
            break
    if apply_as_shape_index == 0:
        # Apply as shapekey用のモディファイアが一番上にあったらモディファイアをシェイプキーとして適用

        if use_update_mesh_deform_addon:
            func_update_mesh_deform_addon.update_mesh_deform_addon(
                obj=source_obj, 
                modifier=apply_as_shape_modifier, 
                use_update_mesh_deform_addon=use_update_mesh_deform_addon)

        print("%AS% modifier is top")
        func_apply_as_shapekey.apply_as_shapekey(apply_as_shape_modifier)
        # 関数を再実行して終了
        print("re-execute apply_modifiers_with_shapekeys")
        apply_modifiers_with_shapekeys(
            remove_nonrender=remove_nonrender, 
            use_update_mesh_deform_addon=use_update_mesh_deform_addon)
        return
    elif apply_as_shape_index >= 1:
        # 2番目以降にApply as shape用のモディファイアがあったら
        print("%AS% modifier is not top")
        partial_apply_modifiers(
            source_obj=source_obj, 
            modifier_index=apply_as_shape_index, 
            remove_nonrender=remove_nonrender,
            use_update_mesh_deform_addon=use_update_mesh_deform_addon)
        return
    else:
        print("%AS% modifier is not found")

    if source_obj.data.shape_keys and len(source_obj.data.shape_keys.key_blocks) == 1:
        # Basisしかなければシェイプキー削除
        print("remove basis: " + source_obj.name)
        # 0番目のシェイプキーをアクティブにする（これが無いとエラーが出る場合がある）
        source_obj.active_shape_key_index = 0
        bpy.ops.object.shape_key_remove(all=True)

    if source_obj.data.shape_keys is None or len(source_obj.data.shape_keys.key_blocks) == 0:
        # シェイプキーがなければモディファイア適用処理だけ実行
        print("only apply_modifiers: " + source_obj.name)
        func_apply_modifiers.apply_modifiers(
            remove_nonrender=remove_nonrender, 
            use_update_mesh_deform_addon=use_update_mesh_deform_addon)
        return
    
    # シェイプキーがある場合、SurfaceDeformモディファイアはBasisシェイプに対して適用される
    surface_deform_index = -1
    surface_deform_modifier = None
    for i, modifier in enumerate(source_obj.modifiers):
        if modifier.type == 'SURFACE_DEFORM':
            surface_deform_index = i
            surface_deform_modifier = modifier
            print(f"SurfaceDeform modifier is found: {str(surface_deform_index)} - {modifier.name}")
            break
    if surface_deform_index == 0:
        # SurfaceDeformモディファイアが一番上にあったら
        print("SurfaceDeform modifier is top")
        apply_surface_deform_to_basis(
            source_obj=source_obj, 
            modifier=surface_deform_modifier, 
            use_update_mesh_deform_addon=use_update_mesh_deform_addon,
            remove_nonrender=remove_nonrender)
        return
    if surface_deform_index >= 1:
        # SurfaceDeformモディファイアが2番目以降にあったら
        print("SurfaceDeform modifier is not top")
        partial_apply_modifiers(
            source_obj=source_obj, 
            modifier_index=surface_deform_index, 
            remove_nonrender=remove_nonrender,
            use_update_mesh_deform_addon=use_update_mesh_deform_addon)
        return
    else:
        print("SurfaceDeform modifier is not found")

    # 対象オブジェクトだけを選択
    func_object_utils.deselect_all_objects()
    func_object_utils.select_object(source_obj, True)
    func_object_utils.set_active_object(source_obj)

    # applymodifierの対象となるモディファイアがあるかどうか確認
    need_apply_modifier = False
    for modifier in source_obj.modifiers:
        if modifier.show_render or remove_nonrender:
            if modifier.name.startswith(consts.FORCE_APPLY_MODIFIER_PREFIX) or modifier.type != 'ARMATURE':
                need_apply_modifier = True
                break
    print(f"{source_obj.name}: Need Apply Modifiers: {str(need_apply_modifier)}")
    if need_apply_modifier:
        # シェイプキーの名前と数値を記憶
        active_shape_key_index = source_obj.active_shape_key_index
        shapekey_name_and_values = []
        for shapekey in source_obj.data.shape_keys.key_blocks:
            shapekey_name_and_values.append((shapekey.name, shapekey.value))

        # シェイプキーをそれぞれ別オブジェクトにしてモディファイア適用してからオブジェクトを1つにまとめなおす
        apply_each_shapekey_modifiers(source_obj, remove_nonrender, use_update_mesh_deform_addon)

        print(shapekey_name_and_values)
        print([v.name for v in source_obj.data.shape_keys.key_blocks])
        # シェイプキーの名前と数値を復元
        source_obj.active_shape_key_index = active_shape_key_index
        for i, shapekey in enumerate(source_obj.data.shape_keys.key_blocks):
            shapekey.name = shapekey_name_and_values[i][0]
            shapekey.value = shapekey_name_and_values[i][1]

    print("Shapekey Count (Include Basis Shapekey): " + str(len(source_obj.data.shape_keys.key_blocks)))

    func_object_utils.select_object(source_obj, True)
    func_object_utils.set_active_object(source_obj)
