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

from ..funcs.utils import func_object_utils


def get_shape_key_index(shape_name:str):
    obj = func_object_utils.get_active_object()
    return get_shape_key_index(obj, shape_name)

def get_shape_key_index(obj: bpy.types.Object, shape_name:str):
    if not obj.data.shape_keys:
        return -1
    key_blocks = obj.data.shape_keys.key_blocks
    for i, shapekey in enumerate(key_blocks):
        if shapekey.name == shape_name:
            return i
    return -1


def bake_shape_key(shape_name: str):
    obj = func_object_utils.get_active_object()
    shape_index = get_shape_key_index(obj, shape_name)
    if shape_index == -1:
        raise ValueError(f"shape_name not found: {shape_name}")
    bake_shape_key(shape_index)

# 指定されたシェイプキーの形状を適用する。他のシェイプキーは削除される
def bake_shape_key(shape_index: int):
    obj = func_object_utils.get_active_object()
    key_blocks = obj.data.shape_keys.key_blocks
    target_shapekey = key_blocks[shape_index]
    
    # シェイプキーの頂点座標を適用
    shape_co = [v.co for v in target_shapekey.data]
    for i, v in enumerate(obj.data.vertices):
        v.co = shape_co[i]
    obj.data.update()

    obj.shape_key_clear()

    
def shape_key_props_to_dict(shapekey):
    result = {
        'interpolation': shapekey.interpolation,
        'mute': shapekey.mute,
        'name': shapekey.name,
        'relative_key': shapekey.relative_key,
        'slider_max': shapekey.slider_max,
        'slider_min': shapekey.slider_min,
        'value': shapekey.value,
        'vertex_group': shapekey.vertex_group,
        'co': [(v.co.x, v.co.y, v.co.z) for v in shapekey.data]
    }
    return result


def set_shape_key_props_from_dict(shapekey, props: dict):
    shapekey.interpolation = props['interpolation']
    shapekey.mute = props['mute']
    shapekey.name = props['name']
    shapekey.relative_key = props['relative_key']
    shapekey.slider_max = props['slider_max']
    shapekey.slider_min = props['slider_min']
    shapekey.value = props['value']
    shapekey.vertex_group = props['vertex_group']
    co = props['co']
    for i, v in enumerate(shapekey.data):
        v.co = co[i]


def move_shape_key(source_index: int, dest_index: int, length: int = 1):
    if source_index == dest_index:
        return None 
    if length < 1:
        raise ValueError("length must be 1 or more")
    obj = func_object_utils.get_active_object()
    key_blocks = obj.data.shape_keys.key_blocks
    source_shapekey_props_list = []
    for i in range(source_index, source_index + length):
        source_shapekey = key_blocks[i]
        source_shapekey_props = shape_key_props_to_dict(source_shapekey)
        source_shapekey.name += "%temp%"
        source_shapekey_props_list.append(source_shapekey_props)
    #print(f"source_shapekey_props: {source_shapekey_props}")
    if source_index < dest_index:
        #print("source_index < dest_index")
        #print([shape.name for shape in key_blocks])
        # source+1～destのシェイプキーをn個前にずらす
        for i in range(source_index + 1, dest_index):
            this_shapekey = key_blocks[i]
            this_shapekey_props = shape_key_props_to_dict(this_shapekey)
            this_shapekey.name += "%temp%"
            prev_shapekey = key_blocks[i - length]
            set_shape_key_props_from_dict(prev_shapekey, this_shapekey_props)
            #print([shape.name for shape in key_blocks])
    else:
        #print("source_index > dest_index")
        #print([shape.name for shape in key_blocks])
        # dest～sourceのシェイプキーをn個後ろにずらす
        for i in reversed(range(dest_index, source_index)):
            this_shapekey = key_blocks[i]
            this_shapekey_props = shape_key_props_to_dict(this_shapekey)
            this_shapekey.name += "%temp%"
            next_shapekey = key_blocks[i + length]
            set_shape_key_props_from_dict(next_shapekey, this_shapekey_props)
            #print([shape.name for shape in key_blocks])
    # sourceのシェイプキーをdestに移動
    dest_shapekeys = []
    for i, source_shapekey_props in enumerate(source_shapekey_props_list):
        dest_shapekey = key_blocks[dest_index + i]
        #print(f"dest_shapekey: {dest_shapekey.name}")
        set_shape_key_props_from_dict(dest_shapekey, source_shapekey_props)
        dest_shapekeys.append(dest_shapekey)
        #print([shape.name for shape in key_blocks])
    return dest_shapekeys


def clean_shapekey_name(name):
    """制御文字列を除去してクリーンなシェイプキー名を取得"""
    if '@BASE:' in name:
        return name.split('@BASE:')[0]
    return name


def calculate_shapekey_difference(obj, base_shapekey_name, shapekey_co):
    """シェイプキーからベースシェイプキーを減算"""
    if not obj.data.shape_keys:
        return shapekey_co
    
    # ベースシェイプキーが存在するかチェック
    base_index = get_shape_key_index(obj, base_shapekey_name)
    if base_index == -1:
        print(f"Warning: base shapekey '{base_shapekey_name}' not found")
        return shapekey_co
    
    # ベースシェイプキーの座標を取得
    base_shapekey = obj.data.shape_keys.key_blocks[base_index]
    base_co = [(v.co.x, v.co.y, v.co.z) for v in base_shapekey.data]
    
    # Basisからの差分を計算
    basis_co = [(v.co.x, v.co.y, v.co.z) for v in obj.data.shape_keys.key_blocks[0].data]
    
    # 差分を計算: shapekey_co - (base_co - basis_co)
    diff_co = []
    for i in range(len(shapekey_co)):
        # ベースシェイプキーのBasisからの変位
        base_delta_x = base_co[i][0] - basis_co[i][0]
        base_delta_y = base_co[i][1] - basis_co[i][1]
        base_delta_z = base_co[i][2] - basis_co[i][2]
        
        # 適用されたシェイプキーからベースの変位を減算
        diff_x = shapekey_co[i][0] - base_delta_x
        diff_y = shapekey_co[i][1] - base_delta_y
        diff_z = shapekey_co[i][2] - base_delta_z
        
        diff_co.append((diff_x, diff_y, diff_z))
    
    return diff_co


def create_composite_shapekey(obj, modifier, base_shapekey_name, target_shapekey_name):
    """複合シェイプキーを作成"""
    print(f"Creating composite shapekey: {target_shapekey_name} with base: {base_shapekey_name}")
    
    # ベースシェイプキーが存在するかチェック
    base_index = get_shape_key_index(obj, base_shapekey_name)
    if base_index == -1:
        raise ValueError(f"Base shapekey '{base_shapekey_name}' not found")
    
    # 1. モディファイアをApply As Shapekeyで通常通り適用
    bpy.ops.object.modifier_apply_as_shapekey(keep_modifier=False, modifier=modifier.name)
    
    # 2. 適用されたシェイプキーを取得
    new_shapekey = obj.data.shape_keys.key_blocks[-1]
    applied_co = [(v.co.x, v.co.y, v.co.z) for v in new_shapekey.data]
    
    # 3. ベースシェイプキーを減算
    diff_co = calculate_shapekey_difference(obj, base_shapekey_name, applied_co)
    
    # 4. 差分を適用
    for i, v in enumerate(new_shapekey.data):
        v.co = diff_co[i]
    
    # 5. シェイプキー名を設定
    new_shapekey.name = target_shapekey_name
    
    return new_shapekey



    