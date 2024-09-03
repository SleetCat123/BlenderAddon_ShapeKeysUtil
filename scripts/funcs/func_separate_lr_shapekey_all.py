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
from ..funcs import func_separate_lr_shapekey
from ..funcs.utils import func_object_utils


def separate_lr_shapekey_all(duplicate, enable_sort, auto_detect):
    obj = func_object_utils.get_active_object()
    print("Create LR Shapekey All: [" + obj.name + "]")

    # 頂点を全て表示
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.reveal()
    bpy.ops.object.mode_set(mode='OBJECT')

    shape_keys_length = len(obj.data.shape_keys.key_blocks)
    for i in reversed(range(shape_keys_length)):
        if i == 0:
            break
        shapekey = obj.data.shape_keys.key_blocks[i]

        # 名前の最後が_leftまたは_rightのシェイプキーは既に左右分割済みと見なし処理スキップ
        if shapekey.name.endswith("_left") or shapekey.name.endswith("_right"):
            continue
        # auto_detectがTrueなら、名前に"%LR%"を含むときだけ左右分割処理を行う
        if not auto_detect or (auto_detect and shapekey.name.find(consts.ENABLE_LR_TAG) != -1):
            # print("Shapekey: ["+shapekey.name+"] ["+str(shape_keys_length-1-i)+" / "+str(shape_keys_length)+"]")
            print("Shapekey: [" + shapekey.name + "]")
            dup_temp = duplicate
            sort_temp = enable_sort
            if auto_detect:
                # 名前に"%DUP%"を含むなら強制的に複製ON
                if shapekey.name.find(consts.ENABLE_DUPLICATE_TAG) != -1:
                    dup_temp = True
                # 名前に"%SORT%"を含むなら強制的にソートON
                if shapekey.name.find(consts.ENABLE_SORT_TAG) != -1:
                    sort_temp = True
            func_separate_lr_shapekey.separate_lr_shapekey(source_shape_key_index=i, duplicate=dup_temp,
                                                           enable_sort=sort_temp)

    print("Finish Create LR Shapekey All: [" + obj.name + "]")
