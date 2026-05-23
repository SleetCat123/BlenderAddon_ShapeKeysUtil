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

"""
ベースシェイプキー変更機能

指定シェイプキーをBasis形状に適用し、元のBasis形状を逆シェイプキーとして保持する。
Blenderのシェイプキーは絶対座標で格納されているため、
BasisとソースのVertex座標を入れ替えることで実現する。
"""

import bpy

from .. import consts
from .func_shapekey_utils import get_shape_key_index
from .func_shapekey_integrity import ensure_shape_key_integrity, validate_shape_key_lengths
from . import func_separate_lr_shapekey
from .progress_info import ProgressInfo
from .utils import func_object_utils

CHANGE_BASE_MODE_WITH_REVERSE = "WITH_REVERSE"
CHANGE_BASE_MODE_STANDALONE = "STANDALONE"
DEFAULT_CHANGE_BASE_MODE = CHANGE_BASE_MODE_WITH_REVERSE


def _sync_mesh_vertices_to_basis(obj):
    """Basis shape key coordinates to the mesh's base vertices.

    Some export paths read ``obj.data.vertices`` instead of ``Basis.data``.
    Keep them aligned after swapping the base shape key so exported geometry
    uses the new Basis shape.
    """
    basis = obj.data.shape_keys.key_blocks[0]
    for index, vertex in enumerate(obj.data.vertices):
        basis_co = basis.data[index].co
        vertex.co = (basis_co.x, basis_co.y, basis_co.z)
    obj.data.update()


def _calc_basis_delta(source_co, basis_co):
    delta = []
    for source_value, basis_value in zip(source_co, basis_co):
        delta.append((
            source_value[0] - basis_value[0],
            source_value[1] - basis_value[1],
            source_value[2] - basis_value[2],
        ))
    return delta


def _offset_shape_key(shape_key, delta_co):
    result = []
    for index, point in enumerate(shape_key.data):
        result.append((
            point.co.x + delta_co[index][0],
            point.co.y + delta_co[index][1],
            point.co.z + delta_co[index][2],
        ))
    return result


def _write_shape_key_coords(shape_key, coords):
    if len(shape_key.data) != len(coords):
        raise ValueError(
            f"Shape key vertex count mismatch: {shape_key.name} "
            f"{len(shape_key.data)} vs {len(coords)}"
        )
    for index, point in enumerate(shape_key.data):
        point.co = coords[index]


def _normalize_target_name_list(target_names):
    if isinstance(target_names, str):
        iterable = target_names.splitlines()
    elif isinstance(target_names, (list, tuple, set)):
        iterable = target_names
    else:
        return []

    result = []
    seen = set()
    for value in iterable:
        name = str(value or "").strip()
        if not name or name in seen:
            continue
        result.append(name)
        seen.add(name)
    return result


def _normalize_assign_tag_entries(assign_tag_entries):
    if not isinstance(assign_tag_entries, (list, tuple, set)):
        return []

    result = []
    seen = set()
    for entry in assign_tag_entries:
        if not isinstance(entry, dict):
            continue
        shapekey_name = str(entry.get("shapekey_name", "") or "").strip()
        if (
            not shapekey_name
            or shapekey_name == "Basis"
            or shapekey_name.endswith("_left")
            or shapekey_name.endswith("_right")
            or shapekey_name in seen
        ):
            continue
        result.append(
            {
                "shapekey_name": shapekey_name,
                "keep_original": bool(entry.get("keep_original", False)),
                "enable_sort": bool(entry.get("enable_sort", False)),
                "invert_lr_names": bool(entry.get("invert_lr_names", False)),
            }
        )
        seen.add(shapekey_name)
    return result


def _normalize_source_assign_tag(source_assign_tag):
    if not isinstance(source_assign_tag, dict) or not source_assign_tag:
        return None
    return {
        "keep_original": bool(
            source_assign_tag.get("keep_original", source_assign_tag.get("duplicate", True))
        ),
        "enable_sort": bool(source_assign_tag.get("enable_sort", source_assign_tag.get("sort", False))),
        "invert_lr_names": bool(source_assign_tag.get("invert_lr_names", False)),
    }


def _normalize_assign_tag_config(assign_tag):
    if not isinstance(assign_tag, dict) or not assign_tag:
        return None
    return {
        "keep_original": bool(assign_tag.get("keep_original", assign_tag.get("duplicate", False))),
        "enable_sort": bool(assign_tag.get("enable_sort", assign_tag.get("sort", False))),
        "invert_lr_names": bool(assign_tag.get("invert_lr_names", False)),
    }


def _shape_key_coords(shape_key):
    return [(point.co.x, point.co.y, point.co.z) for point in shape_key.data]


def _make_unique_shape_key_name(obj, base_name):
    key_blocks = getattr(getattr(getattr(obj, "data", None), "shape_keys", None), "key_blocks", None)
    if not key_blocks:
        return base_name
    if key_blocks.get(base_name) is None:
        return base_name

    index = 1
    while True:
        candidate = f"{base_name}.{index:03d}"
        if key_blocks.get(candidate) is None:
            return candidate
        index += 1


def _duplicate_shape_key(obj, source_shape_key, new_name):
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.shape_key_add(from_mix=False)
    duplicated_shape_key = obj.data.shape_keys.key_blocks[-1]
    duplicated_shape_key.name = new_name
    _write_shape_key_coords(duplicated_shape_key, _shape_key_coords(source_shape_key))
    duplicated_shape_key.value = source_shape_key.value
    return duplicated_shape_key


def _accumulate_shape_key_into_existing(obj, target_shape_key, source_shape_key):
    basis = obj.data.shape_keys.key_blocks[0]
    result = []
    for basis_point, target_point, source_point in zip(basis.data, target_shape_key.data, source_shape_key.data):
        result.append((
            target_point.co.x + source_point.co.x - basis_point.co.x,
            target_point.co.y + source_point.co.y - basis_point.co.y,
            target_point.co.z + source_point.co.z - basis_point.co.z,
        ))
    _write_shape_key_coords(target_shape_key, result)


def _remove_fcurves_by_data_path(fcurves, data_path):
    if fcurves is None or not data_path:
        return 0

    removed_count = 0
    for fcurve in list(fcurves):
        if getattr(fcurve, "data_path", "") != data_path:
            continue
        fcurves.remove(fcurve)
        removed_count += 1
    return removed_count


def _shape_key_value_data_path(shape_key):
    try:
        return shape_key.path_from_id("value")
    except (ReferenceError, TypeError, ValueError):
        escaped_name = bpy.utils.escape_identifier(str(getattr(shape_key, "name", "") or ""))
        return f'key_blocks["{escaped_name}"].value'


def _clear_shape_key_value_animation(obj, shape_key):
    shape_keys = getattr(getattr(obj, "data", None), "shape_keys", None)
    animation_data = getattr(shape_keys, "animation_data", None)
    if animation_data is None:
        return 0

    data_path = _shape_key_value_data_path(shape_key)
    removed_count = _remove_fcurves_by_data_path(
        getattr(animation_data, "drivers", None),
        data_path,
    )
    action = getattr(animation_data, "action", None)
    removed_count += _remove_fcurves_by_data_path(
        getattr(action, "fcurves", None),
        data_path,
    )
    return removed_count


def _apply_generated_shape_key_settings(obj, target_shape_key, source_shape_key):
    basis = obj.data.shape_keys.key_blocks[0]
    _clear_shape_key_value_animation(obj, target_shape_key)
    target_shape_key.relative_key = basis
    target_shape_key.interpolation = source_shape_key.interpolation
    target_shape_key.mute = source_shape_key.mute
    target_shape_key.slider_min = source_shape_key.slider_min
    target_shape_key.slider_max = source_shape_key.slider_max
    target_shape_key.value = source_shape_key.value
    target_shape_key.vertex_group = source_shape_key.vertex_group


def _normalize_logical_shape_key_name(name):
    return consts.normalize_shapekey_name(str(name or "").split("@BASE:")[0])


def _iter_matching_shape_key_names(obj, target_name):
    key_blocks = getattr(getattr(getattr(obj, "data", None), "shape_keys", None), "key_blocks", None)
    if not key_blocks:
        return []

    target_name = str(target_name or "").strip()
    if not target_name:
        return []

    normalized_target = _normalize_logical_shape_key_name(target_name)
    matches = []
    for key_block in key_blocks:
        key_name = str(key_block.name or "")
        if key_name == target_name or _normalize_logical_shape_key_name(key_name) == normalized_target:
            matches.append(key_name)
    return matches


def _resolve_shape_key_name(obj, target_name, *, exclude_names=None):
    exclude_names = {str(name or "").strip() for name in (exclude_names or []) if str(name or "").strip()}
    matches = [
        name for name in _iter_matching_shape_key_names(obj, target_name)
        if name not in exclude_names
    ]
    if not matches:
        return ""
    return matches[-1]


def _resolve_preferred_shape_key_name(obj, target_name, *, exclude_names=None):
    exclude_names = {str(name or "").strip() for name in (exclude_names or []) if str(name or "").strip()}
    key_name = str(target_name or "").strip()
    key_blocks = getattr(getattr(getattr(obj, "data", None), "shape_keys", None), "key_blocks", None)
    if key_blocks and key_name and key_name not in exclude_names and key_blocks.get(key_name) is not None:
        return key_name
    return _resolve_shape_key_name(obj, key_name, exclude_names=exclude_names)


def _move_shape_key_to_index(obj, shape_key_name, target_index):
    shape_key_index = get_shape_key_index(obj, shape_key_name)
    if shape_key_index <= 0:
        return

    obj.active_shape_key_index = shape_key_index
    while obj.active_shape_key_index > target_index:
        bpy.ops.object.shape_key_move(type='UP')
    while obj.active_shape_key_index < target_index:
        bpy.ops.object.shape_key_move(type='DOWN')


def _move_shape_key_pair_below(obj, anchor_shape_key_name, shape_key_names):
    anchor_index = get_shape_key_index(obj, anchor_shape_key_name)
    if anchor_index <= 0:
        return

    for offset, shape_key_name in enumerate(shape_key_names, start=1):
        _move_shape_key_to_index(obj, shape_key_name, anchor_index + offset)


def _remove_shape_key_by_name(obj, shape_key_name):
    resolved_name = _resolve_shape_key_name(obj, shape_key_name)
    if not resolved_name:
        return False

    shape_key_index = get_shape_key_index(obj, resolved_name)
    if shape_key_index <= 0:
        return False

    obj.active_shape_key_index = shape_key_index
    bpy.ops.object.shape_key_remove()
    return True


def _remove_shape_key_by_exact_name(obj, shape_key_name):
    key_name = str(shape_key_name or "").strip()
    if not key_name:
        return False

    shape_key_index = get_shape_key_index(obj, key_name)
    if shape_key_index <= 0:
        return False

    obj.active_shape_key_index = shape_key_index
    bpy.ops.object.shape_key_remove()
    return True


def _rename_or_merge_shape_key(obj, source_shape_key, target_name):
    resolved_target_name = _resolve_preferred_shape_key_name(
        obj,
        target_name,
        exclude_names={source_shape_key.name},
    )
    if not resolved_target_name:
        source_shape_key.name = target_name
        return target_name

    target_shape_key = obj.data.shape_keys.key_blocks[resolved_target_name]
    _accumulate_shape_key_into_existing(obj, target_shape_key, source_shape_key)
    _apply_generated_shape_key_settings(obj, target_shape_key, source_shape_key)
    _remove_shape_key_by_exact_name(obj, source_shape_key.name)

    if resolved_target_name != target_name and obj.data.shape_keys.key_blocks.get(target_name) is None:
        obj.data.shape_keys.key_blocks[resolved_target_name].name = target_name
        return target_name

    return resolved_target_name


def _materialize_shape_key_output(obj, temp_shape_key_name, target_name):
    temp_shape_key = obj.data.shape_keys.key_blocks.get(temp_shape_key_name)
    if temp_shape_key is None:
        return ""

    resolved_target_name = _resolve_preferred_shape_key_name(
        obj,
        target_name,
        exclude_names={temp_shape_key_name},
    )
    if not resolved_target_name:
        temp_shape_key.name = target_name
        return target_name

    target_shape_key = obj.data.shape_keys.key_blocks[resolved_target_name]
    _accumulate_shape_key_into_existing(obj, target_shape_key, temp_shape_key)
    _apply_generated_shape_key_settings(obj, target_shape_key, temp_shape_key)
    _remove_shape_key_by_exact_name(obj, temp_shape_key_name)

    if resolved_target_name != target_name and obj.data.shape_keys.key_blocks.get(target_name) is None:
        obj.data.shape_keys.key_blocks[resolved_target_name].name = target_name
        return target_name

    return resolved_target_name


def _split_shape_key_from_temporary_duplicate(
    obj,
    source_shape_key_name,
    result_base_name,
    *,
    swap_lr_names=False,
    enable_sort=False,
    anchor_shape_key_name="",
):
    resolved_source_name = _resolve_shape_key_name(obj, source_shape_key_name)
    source_index = get_shape_key_index(obj, resolved_source_name) if resolved_source_name else -1
    if source_index <= 0:
        print(f"[change_base_shapekey] Split source not found: '{source_shape_key_name}' on '{obj.name}'")
        return []

    source_shape_key = obj.data.shape_keys.key_blocks[source_index]
    temp_name = _make_unique_shape_key_name(obj, f"__tmp_change_base_split__{result_base_name}")
    temp_shape_key = _duplicate_shape_key(obj, source_shape_key, temp_name)
    temp_index = get_shape_key_index(obj, temp_shape_key.name)
    if temp_index <= 0:
        print(f"[change_base_shapekey] Failed to duplicate split source: '{source_shape_key_name}' on '{obj.name}'")
        return []

    func_object_utils.select_object(obj, True)
    func_object_utils.set_active_object(obj)
    func_separate_lr_shapekey.separate_lr_shapekey(
        source_shape_key_index=temp_index,
        duplicate=False,
        enable_sort=False,
    )

    temp_left = obj.data.shape_keys.key_blocks.get(f"{temp_name}_left")
    temp_right = obj.data.shape_keys.key_blocks.get(f"{temp_name}_right")
    if temp_left is None or temp_right is None:
        print(f"[change_base_shapekey] Split result not found: '{source_shape_key_name}' on '{obj.name}'")
        return []

    result_left_name = f"{result_base_name}_left"
    result_right_name = f"{result_base_name}_right"
    if swap_lr_names:
        created_right_name = _materialize_shape_key_output(obj, temp_left.name, result_right_name)
        created_left_name = _materialize_shape_key_output(obj, temp_right.name, result_left_name)
    else:
        created_left_name = _materialize_shape_key_output(obj, temp_left.name, result_left_name)
        created_right_name = _materialize_shape_key_output(obj, temp_right.name, result_right_name)

    if enable_sort:
        _move_shape_key_pair_below(
            obj,
            _resolve_shape_key_name(obj, anchor_shape_key_name or source_shape_key_name) or resolved_source_name,
            [created_left_name, created_right_name],
        )

    return [created_left_name, created_right_name]


def _should_keep_reverse_shape_key(source_assign_tag=None, reverse_assign_tag=None):
    source_assign_tag = _normalize_source_assign_tag(source_assign_tag)
    source_keep_original = bool(
        source_assign_tag is not None
        and source_assign_tag.get("keep_original", True)
    )
    reverse_keep_original = bool(
        isinstance(reverse_assign_tag, dict)
        and reverse_assign_tag.get("keep_original", False)
    )
    return source_keep_original or reverse_keep_original


def _should_invert_lr_names(assign_tag, *, default=False):
    normalized_assign_tag = _normalize_assign_tag_config(assign_tag)
    if normalized_assign_tag is None:
        return bool(default)
    return bool(normalized_assign_tag.get("invert_lr_names", False))


def _apply_source_assign_tag_splits(
    obj,
    source_shapekey_name,
    reverse_shapekey_name,
    source_assign_tag=None,
):
    source_assign_tag = _normalize_source_assign_tag(source_assign_tag)
    if source_assign_tag is None:
        return []

    return _split_shape_key_from_temporary_duplicate(
        obj,
        reverse_shapekey_name,
        source_shapekey_name,
        swap_lr_names=not _should_invert_lr_names(source_assign_tag, default=False),
        enable_sort=bool(source_assign_tag.get("enable_sort", False)),
        anchor_shape_key_name=reverse_shapekey_name,
    )


def _apply_reverse_assign_tag_split(obj, reverse_shapekey_name, reverse_assign_tag=None):
    reverse_assign_tag = _normalize_assign_tag_config(reverse_assign_tag)
    if reverse_assign_tag is None:
        return []

    normalized_reverse_name = str(reverse_shapekey_name or "").strip()
    if (
        not normalized_reverse_name
        or normalized_reverse_name == "Basis"
        or normalized_reverse_name.endswith("_left")
        or normalized_reverse_name.endswith("_right")
    ):
        return []

    return _split_shape_key_from_temporary_duplicate(
        obj,
        reverse_shapekey_name,
        reverse_shapekey_name,
        swap_lr_names=_should_invert_lr_names(reverse_assign_tag, default=False),
        enable_sort=bool(reverse_assign_tag.get("enable_sort", False)),
        anchor_shape_key_name=reverse_shapekey_name,
    )


def _apply_assign_tag_splits(obj, assign_tag_entries=None):
    split_targets = _normalize_assign_tag_entries(assign_tag_entries)

    if not split_targets:
        return []

    func_object_utils.select_object(obj, True)
    func_object_utils.set_active_object(obj)

    applied_names = []
    for split_target in split_targets:
        shapekey_name = split_target["shapekey_name"]
        source_index = get_shape_key_index(obj, shapekey_name)
        if source_index <= 0:
            print(f"[change_base_shapekey] AssignTag target not found: '{shapekey_name}' on '{obj.name}'")
            continue
        _split_shape_key_from_temporary_duplicate(
            obj,
            shapekey_name,
            shapekey_name,
            swap_lr_names=bool(split_target.get("invert_lr_names", False)),
            enable_sort=bool(split_target.get("enable_sort", False)),
            anchor_shape_key_name=shapekey_name,
        )
        if not bool(split_target.get("keep_original", False)):
            _remove_shape_key_by_name(obj, shapekey_name)
        applied_names.append(shapekey_name)
    return applied_names


def _apply_change_base_split_operations(
    obj,
    source_shapekey_name,
    reverse_shapekey_name,
    *,
    source_assign_tag=None,
    reverse_assign_tag=None,
    assign_tag_entries=None,
):
    source_split_names = _apply_source_assign_tag_splits(
        obj,
        source_shapekey_name,
        reverse_shapekey_name,
        source_assign_tag=source_assign_tag,
    )
    reverse_split_names = _apply_reverse_assign_tag_split(
        obj,
        reverse_shapekey_name,
        reverse_assign_tag=reverse_assign_tag,
    )
    applied_split_names = []
    if reverse_split_names:
        applied_split_names.append(reverse_shapekey_name)
    applied_split_names.extend(
        _apply_assign_tag_splits(
            obj,
            assign_tag_entries=assign_tag_entries,
        )
    )

    if (
        (source_split_names or reverse_split_names)
        and not _should_keep_reverse_shape_key(
            source_assign_tag=source_assign_tag,
            reverse_assign_tag=reverse_assign_tag,
        )
    ):
        _remove_shape_key_by_name(obj, reverse_shapekey_name)

    return {
        "source_split_names": source_split_names,
        "reverse_split_names": reverse_split_names,
        "applied_split_names": applied_split_names,
    }


def apply_deferred_change_base_splits_for_object(obj, settings_list):
    if obj is None or obj.type != 'MESH' or obj.data is None or obj.data.shape_keys is None:
        return 0

    count = 0
    for setting in settings_list:
        if not isinstance(setting, dict):
            continue

        source_name = str(setting.get("source_shapekey_name", "") or "").strip()
        reverse_name = str(setting.get("reverse_shapekey_name", "") or "").strip()
        source_assign_tag = setting.get("source_assign_tag")
        reverse_assign_tag = setting.get("reverse_assign_tag")
        assign_tag_entries = setting.get("assign_tag_entries", [])

        if not reverse_name:
            continue
        if source_assign_tag is None and reverse_assign_tag is None and not assign_tag_entries:
            continue

        split_result = _apply_change_base_split_operations(
            obj,
            source_name,
            reverse_name,
            source_assign_tag=source_assign_tag,
            reverse_assign_tag=reverse_assign_tag,
            assign_tag_entries=assign_tag_entries,
        )
        if (
            split_result["source_split_names"]
            or split_result["reverse_split_names"]
            or split_result["applied_split_names"]
        ):
            count += 1

    if count > 0 and not ensure_shape_key_integrity(obj, log_prefix="apply_deferred_change_base_splits"):
        raise RuntimeError(f"Shape key integrity check failed after deferred change-base splits: {obj.name}")
    return count


def change_base_shapekey(
    obj,
    source_shapekey_name,
    reverse_shapekey_name,
    standalone_target_shapekey_names=None,
    source_assign_tag=None,
    reverse_assign_tag=None,
    assign_tag_entries=None,
    defer_split_until_after_merge=False,
):
    """指定シェイプキーをBasis形状に適用し、元のBasisを逆シェイプキーとして残す

    BasisとSourceの頂点座標を入れ替え、Sourceをreverse_shapekey_nameにリネームする。
    Sourceがあった位置にそのまま逆シェイプキーが残る。

    Args:
        obj: 対象メッシュオブジェクト
        source_shapekey_name: Basisに適用するシェイプキー名
        reverse_shapekey_name: 元のBasis形状を保存する逆シェイプキーの名前

    Returns:
        bool: 成功したらTrue
    """
    if not obj.data.shape_keys:
        print(f"[change_base_shapekey] No shape keys on '{obj.name}'")
        return False

    key_blocks = obj.data.shape_keys.key_blocks
    if len(key_blocks) < 2:
        print(f"[change_base_shapekey] '{obj.name}' has less than 2 shape keys")
        return False

    if not validate_shape_key_lengths(obj, log_prefix="change_base_shapekey"):
        return False

    source_index = get_shape_key_index(obj, source_shapekey_name)
    if source_index == -1:
        print(f"[change_base_shapekey] Source '{source_shapekey_name}' not found on '{obj.name}'")
        return False

    if source_index == 0:
        print("[change_base_shapekey] Cannot use Basis as source")
        return False

    basis = key_blocks[0]
    source = key_blocks[source_index]
    other_shape_keys = [
        key_blocks[index]
        for index in range(1, len(key_blocks))
        if index != source_index
    ]

    # Basisの頂点座標を保存
    basis_co = [(v.co.x, v.co.y, v.co.z) for v in basis.data]

    # Sourceの頂点座標をBasisにコピー
    source_co = [(v.co.x, v.co.y, v.co.z) for v in source.data]
    basis_delta = _calc_basis_delta(source_co, basis_co)

    standalone_target_names = set(_normalize_target_name_list(standalone_target_shapekey_names))

    _write_shape_key_coords(basis, source_co)
    shifted_coords = {
        key_block.name: _offset_shape_key(key_block, basis_delta)
        for key_block in other_shape_keys
        if key_block.name not in standalone_target_names
    }
    for key_block in other_shape_keys:
        if key_block.name in shifted_coords:
            _write_shape_key_coords(key_block, shifted_coords[key_block.name])

    # 保存したBasis座標をSourceに書き込み（逆シェイプキー化）
    _write_shape_key_coords(source, basis_co)

    # Sourceをreverse名にリネーム
    reverse_shapekey_name = _rename_or_merge_shape_key(obj, source, reverse_shapekey_name)

    source_split_names = []
    reverse_split_names = []
    applied_split_names = []
    if not defer_split_until_after_merge:
        split_result = _apply_change_base_split_operations(
            obj,
            source_shapekey_name,
            reverse_shapekey_name,
            source_assign_tag=source_assign_tag,
            reverse_assign_tag=reverse_assign_tag,
            assign_tag_entries=assign_tag_entries,
        )
        source_split_names = split_result["source_split_names"]
        reverse_split_names = split_result["reverse_split_names"]
        applied_split_names = split_result["applied_split_names"]

    if not ensure_shape_key_integrity(obj, log_prefix="change_base_shapekey"):
        raise RuntimeError(f"Shape key integrity check failed after change-base: {obj.name}")
    _sync_mesh_vertices_to_basis(obj)

    print(
        f"[change_base_shapekey] '{source_shapekey_name}' -> Basis, "
        f"reverse: '{reverse_shapekey_name}', "
        f"standalone_targets={sorted(standalone_target_names)}, "
        f"source_split_targets={source_split_names}, "
        f"assign_tag_targets={applied_split_names} on '{obj.name}'"
    )
    return True


def change_base_shapekeys_for_object(obj, settings_list):
    """オブジェクトに対して複数のベース変更を順次適用

    Args:
        obj: 対象メッシュオブジェクト
        settings_list: (source_shapekey_name, reverse_shapekey_name) のタプルのリスト

    Returns:
        int: 成功した変更数
    """
    count = 0
    for setting in settings_list:
        if isinstance(setting, dict):
            source_name = setting.get("source_shapekey_name", "")
            reverse_name = setting.get("reverse_shapekey_name", "")
            standalone_target_names = setting.get("standalone_target_shapekey_names", [])
            source_assign_tag = setting.get("source_assign_tag")
            reverse_assign_tag = setting.get("reverse_assign_tag")
            assign_tag_entries = setting.get("assign_tag_entries", [])
            defer_split_until_after_merge = bool(setting.get("defer_split_until_after_merge", False))
        else:
            source_name = setting[0] if len(setting) > 0 else ""
            reverse_name = setting[1] if len(setting) > 1 else ""
            standalone_target_names = setting[2] if len(setting) > 2 else []
            if len(setting) > 5:
                source_assign_tag = setting[3]
                reverse_assign_tag = setting[4]
                assign_tag_entries = setting[5]
            else:
                source_assign_tag = None
                reverse_assign_tag = setting[3] if len(setting) > 3 else None
                assign_tag_entries = setting[4] if len(setting) > 4 else []
            defer_split_until_after_merge = False

        if change_base_shapekey(
            obj,
            source_name,
            reverse_name,
            standalone_target_shapekey_names=standalone_target_names,
            source_assign_tag=source_assign_tag,
            reverse_assign_tag=reverse_assign_tag,
            assign_tag_entries=assign_tag_entries,
            defer_split_until_after_merge=defer_split_until_after_merge,
        ):
            count += 1
    return count


def change_base_shapekeys_iter(objects_with_settings):
    """複数オブジェクトに対するベース変更処理（ジェネレータ版）

    MizoresCustomExporter連携時のModal処理で使用する。

    Args:
        objects_with_settings: [(obj, settings_list), ...] のリスト
            settings_listは (source_shapekey_name, reverse_shapekey_name) のタプルのリスト

    Yields:
        ProgressInfo: 進捗情報
    """
    total = len(objects_with_settings)
    if total == 0:
        return

    yield ProgressInfo(
        phase="change_base",
        progress=0.0,
        message="Changing base shape keys...",
        total_objects=total,
    )

    for idx, (obj, settings_list) in enumerate(objects_with_settings):
        progress = idx / total
        yield ProgressInfo(
            phase="change_base",
            progress=progress,
            message=f"Changing base shape keys: {obj.name}",
            object_name=obj.name,
            sub_progress=progress,
            total_objects=total,
            current_object_index=idx,
        )

        count = change_base_shapekeys_for_object(obj, settings_list)
        print(f"[change_base_shapekeys_iter] '{obj.name}': {count} base changes applied")

    yield ProgressInfo(
        phase="change_base",
        progress=1.0,
        message="Base shape key changes complete",
        total_objects=total,
        current_object_index=total,
    )
