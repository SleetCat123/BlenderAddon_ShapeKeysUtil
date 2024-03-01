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
from ..funcs.utils import func_object_utils


# 指定されたシェイプキーの形状を適用する。他のシェイプキーは削除される
def bake_shape_key(shape_name: str):
    obj = func_object_utils.get_active_object()
    key_blocks = obj.data.shape_keys.key_blocks
    target_shapekey = None
    # シェイプキーを検索
    for shapekey in key_blocks:
        if shapekey.name == shape_name:
            shapekey.value = 1
            target_shapekey = shapekey
            break
    if target_shapekey is None:
        raise ValueError(f"shape_name not found: {shape_name}")
    
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


def move_shape_key(source_index: int, dest_index: int):
    if source_index == dest_index:
        return
    obj = func_object_utils.get_active_object()
    key_blocks = obj.data.shape_keys.key_blocks
    source_shapekey = key_blocks[source_index]
    source_shapekey_props = shape_key_props_to_dict(source_shapekey)
    print(f"source_shapekey_props: {source_shapekey_props}")
    if source_index < dest_index:
        # source+1～destのシェイプキーを一つ前にずらす
        for i in range(source_index + 1, dest_index):
            this_shapekey = key_blocks[i]
            this_shapekey_props = shape_key_props_to_dict(this_shapekey)
            prev_shapekey = key_blocks[i - 1]
            set_shape_key_props_from_dict(prev_shapekey, this_shapekey_props)
    else:
        # dest+1～sourceのシェイプキーを一つ後ろにずらす
        for i in reversed(range(dest_index, source_index)):
            this_shapekey = key_blocks[i]
            this_shapekey_props = shape_key_props_to_dict(this_shapekey)
            next_shapekey = key_blocks[i + 1]
            set_shape_key_props_from_dict(next_shapekey, this_shapekey_props)
    # sourceのシェイプキーをdestに移動
    dest_shapekey = key_blocks[dest_index]
    set_shape_key_props_from_dict(dest_shapekey, source_shapekey_props)
    return dest_shapekey



    