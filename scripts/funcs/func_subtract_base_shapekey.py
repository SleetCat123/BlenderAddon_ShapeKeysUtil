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
from . import func_composite_shapekey
from .utils import func_object_utils


def subtract_base_shapekey_all():
    """@BASE:xxx形式のシェイプキーをベース減算処理"""
    obj = func_object_utils.get_active_object()
    print(f"Subtract Base Shapekey All: [{obj.name}]")
    
    if not obj.data.shape_keys or len(obj.data.shape_keys.key_blocks) <= 1:
        print("No shape keys to process")
        return
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    processed_count = 0
    shape_keys = obj.data.shape_keys.key_blocks
    
    # 処理対象のシェイプキーを収集
    target_shapekeys = []
    for sk in shape_keys:
        clean_name, base_name = consts.parse_shapekey_name_for_base(sk.name)
        if base_name is not None:
            target_shapekeys.append((sk, clean_name, base_name))
    
    if not target_shapekeys:
        print("No shape keys with @BASE: tag found")
        return
    
    # 処理実行
    for sk, clean_name, base_name in target_shapekeys:
        print(f"Processing: [{sk.name}] -> [{clean_name}] (Base: [{base_name}])")
        
        # ベースシェイプキーの存在確認
        if base_name not in shape_keys:
            print(f"WARNING: Base shape key [{base_name}] not found, skipping [{sk.name}]")
            continue
        
        # ベースシェイプキーを減算
        func_composite_shapekey.apply_composite_subtraction(obj, sk, base_name)
        
        # シェイプキー名をリネーム
        sk.name = clean_name
        processed_count += 1
    
    print(f"Subtract Base Shapekey All: Processed {processed_count} shape keys")

