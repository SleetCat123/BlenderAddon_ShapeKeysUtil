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
from ..funcs import func_shapekey_utils


def apply_composite_subtraction(obj, shapekey, base_shapekey_name):
    """シェイプキーからベースシェイプキーを減算"""
    try:
        # ベースシェイプキーが存在するかチェック
        base_index = func_shapekey_utils.get_shape_key_index(obj, base_shapekey_name)
        if base_index == -1:
            print(f"Warning: base shapekey '{base_shapekey_name}' not found")
            return
        
        # シェイプキーの座標を取得
        applied_co = [(v.co.x, v.co.y, v.co.z) for v in shapekey.data]
        
        # ベースシェイプキーを減算
        diff_co = func_shapekey_utils.calculate_shapekey_difference(obj, base_shapekey_name, applied_co)
        
        # 差分を適用
        for i, v in enumerate(shapekey.data):
            v.co = diff_co[i]
    except Exception as e:
        print(f"Error applying composite subtraction: {e}")


def apply_single_composite_shapekey(obj, modifier):
    """単一複合シェイプキーを適用"""
    modifier_name = modifier.name
    base_shapekey_name = consts.get_base_shapekey_name(modifier)
    shape_name = consts.REGEX_APPLY_AS_SHAPEKEY_PREFIX.sub("", modifier_name)
    shape_name = shape_name.split("$")[0]

    print(f"add composite shapekey: {shape_name} with base: {base_shapekey_name}")

    # 複合シェイプキーを作成
    try:
        new_shapekey = func_shapekey_utils.create_composite_shapekey(obj, modifier, base_shapekey_name, shape_name)
        # モディファイアを削除
        bpy.ops.object.modifier_remove(modifier=modifier_name)
        return new_shapekey
    except ValueError as e:
        print(f"Error creating composite shapekey: {e}")
        # エラーの場合は通常のシェイプキー適用に戻す
        bpy.ops.object.modifier_apply_as_shapekey(keep_modifier=False, modifier=modifier_name)
        new_shapekey = obj.data.shape_keys.key_blocks[-1]
        new_shapekey.name = shape_name
        return new_shapekey


def apply_multiple_composite_shapekeys(obj, modifier):
    """複数複合シェイプキーを適用"""
    print("Add composite shapekeys from SurfaceDeform/MeshDeform")

    modifier_name = modifier.name
    global_base_shapekey_name = consts.get_base_shapekey_name(modifier)

    mod_target = modifier.target if hasattr(modifier, 'target') else modifier.object
    temp_show_only_shape_key = mod_target.show_only_shape_key
    temp_active_shape_key_index = mod_target.active_shape_key_index

    mod_target.show_only_shape_key = True
    key_blocks = mod_target.data.shape_keys.key_blocks
    len_key_blocks = len(key_blocks)

    for i in range(1, len_key_blocks):
        key = key_blocks[i]

        # シェイプキー名から個別のベース指定をチェック
        clean_name, individual_base = consts.parse_shapekey_name_for_base(key.name)

        # 個別ベースがあればそれを使用、なければグローバルベースを使用
        if individual_base:
            base_shapekey_name = individual_base
        else:
            base_shapekey_name = global_base_shapekey_name

        print(f"add composite shapekey: {clean_name} with base: {base_shapekey_name}")

        mod_target.active_shape_key_index = i

        if i == len_key_blocks - 1:
            keep_modifier = False
        else:
            keep_modifier = True

        if base_shapekey_name:
            # 複合シェイプキーとして処理
            try:
                _apply_composite_shapekey_for_multiple(obj, modifier_name, base_shapekey_name, clean_name, keep_modifier)
            except ValueError as e:
                print(f"Error creating composite shapekey '{clean_name}': {e}")
                # エラーの場合は通常のシェイプキー適用に戻す
                bpy.ops.object.modifier_apply_as_shapekey(keep_modifier=keep_modifier, modifier=modifier_name)
                new_shapekey = obj.data.shape_keys.key_blocks[-1]
                new_shapekey.name = clean_name
        else:
            # 通常のシェイプキー適用
            bpy.ops.object.modifier_apply_as_shapekey(keep_modifier=keep_modifier, modifier=modifier_name)
            new_shapekey = obj.data.shape_keys.key_blocks[-1]
            new_shapekey.name = clean_name

    mod_target.show_only_shape_key = temp_show_only_shape_key
    mod_target.active_shape_key_index = temp_active_shape_key_index


def _apply_composite_shapekey_for_multiple(obj, modifier_name, base_shapekey_name, target_shapekey_name, keep_modifier):
    """複数シェイプキー適用時の複合シェイプキー処理"""
    # ベースシェイプキーが存在するかチェック
    base_index = func_shapekey_utils.get_shape_key_index(obj, base_shapekey_name)
    if base_index == -1:
        raise ValueError(f"Base shapekey '{base_shapekey_name}' not found")

    # 1. モディファイアをApply As Shapekeyで通常通り適用
    bpy.ops.object.modifier_apply_as_shapekey(keep_modifier=keep_modifier, modifier=modifier_name)
    
    # 2. 適用されたシェイプキーを取得
    new_shapekey = obj.data.shape_keys.key_blocks[-1]
    applied_co = [(v.co.x, v.co.y, v.co.z) for v in new_shapekey.data]
    
    # 3. ベースシェイプキーを減算
    diff_co = func_shapekey_utils.calculate_shapekey_difference(obj, base_shapekey_name, applied_co)
    
    # 4. 差分を適用
    for i, v in enumerate(new_shapekey.data):
        v.co = diff_co[i]
    
    # 5. シェイプキー名を設定
    new_shapekey.name = target_shapekey_name