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
from .func_shapekey_integrity import ensure_shape_key_integrity, normalize_relative_keys, validate_shape_key_lengths
from .utils import func_object_utils


def _resolve_base_name(key_blocks, base_name):
    if base_name in key_blocks:
        return base_name

    matches = []
    for key_block in key_blocks:
        clean_name, _ = consts.parse_shapekey_name_for_base(key_block.name)
        if clean_name == base_name:
            matches.append(key_block.name)

    if len(matches) == 1:
        return matches[0]
    return None


def subtract_base_shapekey_all(obj=None):
    """@BASE:xxx形式のシェイプキーをベース減算処理"""
    if obj is None:
        obj = func_object_utils.get_active_object()

    if obj is None:
        print("Subtract Base Shapekey All: active object is None")
        return 0

    if obj.type != 'MESH' or obj.data is None:
        print(f"Subtract Base Shapekey All: skip non-mesh object [{obj.name}]")
        return 0

    print(f"Subtract Base Shapekey All: [{obj.name}]")

    if not obj.data.shape_keys or len(obj.data.shape_keys.key_blocks) <= 1:
        print("No shape keys to process")
        return 0

    func_object_utils.set_active_object(obj)
    if obj.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    if not validate_shape_key_lengths(obj, log_prefix="subtract_base_shapekey"):
        return 0

    fixed_before = normalize_relative_keys(obj, log_prefix="subtract_base_shapekey")
    if fixed_before:
        print(f"Subtract Base Shapekey All: normalized {fixed_before} relative keys before processing")

    processed_count = 0
    shape_keys = obj.data.shape_keys.key_blocks
    basis = shape_keys[0]

    # 処理対象は名前だけ先に収集して、途中のリネームの影響を避ける
    target_shapekeys = []
    for key_block in shape_keys:
        clean_name, base_name = consts.parse_shapekey_name_for_base(key_block.name)
        if base_name is not None:
            target_shapekeys.append(
                {
                    "source_name": key_block.name,
                    "clean_name": clean_name,
                    "base_name": base_name,
                }
            )

    if not target_shapekeys:
        print("No shape keys with @BASE: tag found")
        return 0

    for target in target_shapekeys:
        shape_keys = obj.data.shape_keys.key_blocks
        source_name = target["source_name"]
        clean_name = target["clean_name"]
        base_name = target["base_name"]

        if source_name not in shape_keys:
            print(f"WARNING: Source shape key [{source_name}] not found, skipping")
            continue

        resolved_base_name = _resolve_base_name(shape_keys, base_name)
        if resolved_base_name is None:
            print(f"WARNING: Base shape key [{base_name}] not found, skipping [{source_name}]")
            continue

        shape_key = shape_keys[source_name]
        print(
            f"Processing: [{shape_key.name}] -> [{clean_name}] "
            f"(Base: [{base_name}] resolved=[{resolved_base_name}])"
        )

        func_composite_shapekey.apply_composite_subtraction(obj, shape_key, resolved_base_name)
        # 減算後はBasis基準のシェイプキーになるので、relative_keyもBasisへ戻す。
        shape_key.relative_key = basis
        shape_key.name = clean_name
        processed_count += 1

    if not validate_shape_key_lengths(obj, log_prefix="subtract_base_shapekey"):
        print("Subtract Base Shapekey All: aborting after processing due to invalid shape key lengths")
        return processed_count

    fixed_after = normalize_relative_keys(obj, log_prefix="subtract_base_shapekey")
    if fixed_after:
        print(f"Subtract Base Shapekey All: normalized {fixed_after} relative keys after processing")

    if not ensure_shape_key_integrity(obj, log_prefix="subtract_base_shapekey"):
        raise RuntimeError(f"Shape key integrity check failed after subtract-base: {obj.name}")

    obj.data.update()
    print(f"Subtract Base Shapekey All: Processed {processed_count} shape keys")
    return processed_count

