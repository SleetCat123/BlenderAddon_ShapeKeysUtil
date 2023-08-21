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
from BlenderAddon_ShapeKeysUtil.scripts import consts
from BlenderAddon_ShapeKeysUtil.scripts.funcs import func_select_axis_from_point
from BlenderAddon_ShapeKeysUtil.scripts.funcs.utils import func_object_utils, func_mesh_utils


def separate_lr_shapekey(source_shape_key_index, duplicate, enable_sort):
    obj = func_object_utils.get_active_object()
    source_shape_key = obj.data.shape_keys.key_blocks[source_shape_key_index]

    # print("before: "+source_shape_key.name)
    source_shape_key.name = source_shape_key.name.replace(consts.ENABLE_LR_TAG, '')
    source_shape_key.name = source_shape_key.name.replace(consts.ENABLE_DUPLICATE_TAG, '')
    source_shape_key.name = source_shape_key.name.replace(consts.ENABLE_SORT_TAG, '')
    result_shape_key_name = source_shape_key.name
    # print("after: "+source_shape_key.name)

    point = (0, 0, 0)

    # この後で行う選択範囲反転を正常に処理するため、頂点選択だけが有効になるようにしておく
    # temp_mesh_select_mode = bpy.context.tool_settings.mesh_select_mode
    bpy.context.tool_settings.mesh_select_mode = (True, False, False)

    # 左
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.shape_key_add(from_mix=False)
    left_shape_index = obj.active_shape_key_index
    left_shape = obj.data.shape_keys.key_blocks[left_shape_index]
    left_shape.name = result_shape_key_name + "_left"
    func_select_axis_from_point.select_axis_from_point(point=point, mode='NEGATIVE', axis='X')
    # 中心位置を含ませないために選択範囲を反転する
    bpy.ops.mesh.select_all(action='INVERT')
    func_mesh_utils.update_mesh()
    if any([v.select for v in obj.data.vertices]):
        bpy.ops.mesh.blend_from_shape(shape=source_shape_key.name, blend=1, add=False)
    func_select_axis_from_point.select_axis_from_point(point=point, mode='ALIGNED', axis='X')
    func_mesh_utils.update_mesh()
    if any([v.select for v in obj.data.vertices]):
        # 中心位置はシェイプを0.5でブレンド。
        # これをしないと、leftとright両方を同時に使ったときに中心位置の頂点が二倍動いてしまう
        bpy.ops.mesh.blend_from_shape(shape=source_shape_key.name, blend=0.5, add=False)

    # 右
    # 参照する座標の正負が逆なの以外、やってることは左と同じ
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.shape_key_add(from_mix=False)
    right_shape_index = obj.active_shape_key_index
    right_shape = obj.data.shape_keys.key_blocks[right_shape_index]
    right_shape.name = result_shape_key_name + "_right"
    func_select_axis_from_point.select_axis_from_point(point=point, mode='POSITIVE', axis='X')
    bpy.ops.mesh.select_all(action='INVERT')
    func_mesh_utils.update_mesh()
    if any([v.select for v in obj.data.vertices]):
        print(any([v.select for v in obj.data.vertices]))
        bpy.ops.mesh.blend_from_shape(shape=source_shape_key.name, blend=1, add=False)
    func_select_axis_from_point.select_axis_from_point(point=point, mode='ALIGNED', axis='X')
    func_mesh_utils.update_mesh()
    if any([v.select for v in obj.data.vertices]):
        bpy.ops.mesh.blend_from_shape(shape=source_shape_key.name, blend=0.5, add=False)

    bpy.ops.object.mode_set(mode='OBJECT')

    if enable_sort:
        # 分割したシェイプキーが分割元シェイプキーのすぐ下に来るように移動
        length = len(obj.data.shape_keys.key_blocks)
        if length * 0.5 <= source_shape_key_index:
            # print("Bottom to Top")
            obj.active_shape_key_index = left_shape_index
            while source_shape_key_index + 1 != obj.active_shape_key_index:
                bpy.ops.object.shape_key_move(type='UP')
            obj.active_shape_key_index = right_shape_index
            while source_shape_key_index + 2 != obj.active_shape_key_index:
                bpy.ops.object.shape_key_move(type='UP')
        else:
            # 移動先の位置が上から数えたほうが早いとき
            # print("Top to Bottom")
            obj.active_shape_key_index = left_shape_index
            bpy.ops.object.shape_key_move(type='TOP')
            while source_shape_key_index + 1 != obj.active_shape_key_index:
                bpy.ops.object.shape_key_move(type='DOWN')
            obj.active_shape_key_index = right_shape_index
            bpy.ops.object.shape_key_move(type='TOP')
            while source_shape_key_index + 2 != obj.active_shape_key_index:
                bpy.ops.object.shape_key_move(type='DOWN')

    # 左右分割後のシェイプキーに分割元シェイプキーのvalueをコピー
    left_shape.value = source_shape_key.value
    right_shape.value = source_shape_key.value
    source_shape_key.value = 0

    if not duplicate:
        obj.active_shape_key_index = source_shape_key_index
        bpy.ops.object.shape_key_remove()
    obj.active_shape_key_index = source_shape_key_index
