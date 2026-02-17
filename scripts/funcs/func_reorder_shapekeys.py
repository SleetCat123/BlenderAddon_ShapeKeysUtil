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
シェイプキー並び替え機能

名前ソート、入れ替え、インデックス指定移動、指定シェイプキーの前に移動の4種類の操作を提供する。
全操作で relative_key を名前ベースで正しく解決する。
"""

from .func_shapekey_utils import (
    get_shape_key_index,
    shape_key_props_to_dict,
)
from .progress_info import ProgressInfo


def _serialize_shapekeys(key_blocks, start_index=0):
    """シェイプキーをシリアライズ（relative_keyは名前で保持）

    Args:
        key_blocks: obj.data.shape_keys.key_blocks
        start_index: シリアライズ開始インデックス

    Returns:
        list[dict]: シリアライズされたプロパティのリスト
    """
    props_list = []
    for i in range(start_index, len(key_blocks)):
        props = shape_key_props_to_dict(key_blocks[i])
        props['_relative_key_name'] = (
            props['relative_key'].name if props['relative_key'] else key_blocks[0].name
        )
        props_list.append(props)
    return props_list


def _write_shapekeys(key_blocks, props_list, start_index=0):
    """シリアライズされたプロパティをシェイプキーに書き戻す

    名前衝突を避けるため一時名を設定してから書き戻し、
    relative_keyは名前で解決する。

    Args:
        key_blocks: obj.data.shape_keys.key_blocks
        props_list: _serialize_shapekeysで取得したプロパティリスト
        start_index: 書き戻し開始インデックス
    """
    # 名前衝突を避ける
    for i in range(start_index, len(key_blocks)):
        key_blocks[i].name = f"__reorder_temp_{i}__"

    # プロパティを書き戻し（relative_key以外）
    for i, props in enumerate(props_list):
        kb = key_blocks[start_index + i]
        kb.interpolation = props['interpolation']
        kb.mute = props['mute']
        kb.name = props['name']
        kb.slider_max = props['slider_max']
        kb.slider_min = props['slider_min']
        kb.value = props['value']
        kb.vertex_group = props['vertex_group']
        co = props['co']
        for j, v in enumerate(kb.data):
            v.co = co[j]

    # relative_keyを名前で解決
    for i, props in enumerate(props_list):
        rel_name = props.get('_relative_key_name')
        if rel_name:
            for candidate in key_blocks:
                if candidate.name == rel_name:
                    key_blocks[start_index + i].relative_key = candidate
                    break


def sort_shapekeys_by_name(obj):
    """Basis以外のシェイプキーを名前のアルファベット順にソート

    Args:
        obj: 対象メッシュオブジェクト
    """
    if not obj.data.shape_keys:
        print(f"[sort_shapekeys_by_name] No shape keys on '{obj.name}'")
        return

    key_blocks = obj.data.shape_keys.key_blocks
    if len(key_blocks) <= 2:
        return

    # Basis以外をシリアライズ
    props_list = _serialize_shapekeys(key_blocks, start_index=1)

    # 名前でソート（大文字小文字を無視）
    props_list.sort(key=lambda p: p['name'].lower())

    # 書き戻し
    _write_shapekeys(key_blocks, props_list, start_index=1)

    print(f"[sort_shapekeys_by_name] Sorted {len(props_list)} shape keys on '{obj.name}'")


def swap_shapekeys(obj, name_a, name_b):
    """2つのシェイプキーの位置（データ）を入れ替える

    Args:
        obj: 対象メッシュオブジェクト
        name_a: シェイプキーA名
        name_b: シェイプキーB名

    Returns:
        bool: 成功したらTrue
    """
    if not obj.data.shape_keys:
        print(f"[swap_shapekeys] No shape keys on '{obj.name}'")
        return False

    key_blocks = obj.data.shape_keys.key_blocks

    index_a = get_shape_key_index(obj, name_a)
    index_b = get_shape_key_index(obj, name_b)

    if index_a == -1:
        print(f"[swap_shapekeys] Shape key '{name_a}' not found on '{obj.name}'")
        return False
    if index_b == -1:
        print(f"[swap_shapekeys] Shape key '{name_b}' not found on '{obj.name}'")
        return False

    if index_a == index_b:
        return True

    # プロパティをシリアライズ（relative_keyの名前も保持）
    props_a = shape_key_props_to_dict(key_blocks[index_a])
    props_a['_relative_key_name'] = (
        props_a['relative_key'].name if props_a['relative_key'] else key_blocks[0].name
    )
    props_b = shape_key_props_to_dict(key_blocks[index_b])
    props_b['_relative_key_name'] = (
        props_b['relative_key'].name if props_b['relative_key'] else key_blocks[0].name
    )

    # 名前衝突を避ける
    key_blocks[index_a].name = "__swap_temp_a__"
    key_blocks[index_b].name = "__swap_temp_b__"

    # 入れ替え（relative_key以外のプロパティ）
    for idx, props in [(index_a, props_b), (index_b, props_a)]:
        kb = key_blocks[idx]
        kb.interpolation = props['interpolation']
        kb.mute = props['mute']
        kb.name = props['name']
        kb.slider_max = props['slider_max']
        kb.slider_min = props['slider_min']
        kb.value = props['value']
        kb.vertex_group = props['vertex_group']
        co = props['co']
        for j, v in enumerate(kb.data):
            v.co = co[j]

    # relative_keyを名前で解決
    for idx, props in [(index_a, props_b), (index_b, props_a)]:
        rel_name = props.get('_relative_key_name')
        if rel_name:
            for candidate in key_blocks:
                if candidate.name == rel_name:
                    key_blocks[idx].relative_key = candidate
                    break

    # 他のシェイプキーがAまたはBをrelative_keyとして参照していた場合の修正
    old_name_a = props_a['name']
    old_name_b = props_b['name']
    for i in range(len(key_blocks)):
        if i in (index_a, index_b):
            continue
        kb = key_blocks[i]
        if kb.relative_key:
            # 元々Aを参照していた場合 → 新しい位置（index_b）に変更
            if kb.relative_key.name == old_name_a and get_shape_key_index(obj, old_name_a) == index_b:
                kb.relative_key = key_blocks[index_b]
            # 元々Bを参照していた場合 → 新しい位置（index_a）に変更
            elif kb.relative_key.name == old_name_b and get_shape_key_index(obj, old_name_b) == index_a:
                kb.relative_key = key_blocks[index_a]

    print(f"[swap_shapekeys] Swapped '{name_a}' and '{name_b}' on '{obj.name}'")
    return True


def move_shapekey_to_index(obj, shapekey_name, dest_index):
    """シェイプキーを指定インデックスに移動

    Args:
        obj: 対象メッシュオブジェクト
        shapekey_name: 移動するシェイプキー名
        dest_index: 移動先インデックス（0はBasisのため1以上推奨）

    Returns:
        bool: 成功したらTrue
    """
    if not obj.data.shape_keys:
        print(f"[move_shapekey_to_index] No shape keys on '{obj.name}'")
        return False

    key_blocks = obj.data.shape_keys.key_blocks
    source_index = get_shape_key_index(obj, shapekey_name)

    if source_index == -1:
        print(f"[move_shapekey_to_index] Shape key '{shapekey_name}' not found on '{obj.name}'")
        return False

    if dest_index < 0 or dest_index >= len(key_blocks):
        print(f"[move_shapekey_to_index] dest_index {dest_index} out of range (0-{len(key_blocks) - 1})")
        return False

    if source_index == dest_index:
        return True

    # 全シェイプキーをシリアライズ
    props_list = _serialize_shapekeys(key_blocks, start_index=0)

    # リスト操作で移動
    moved = props_list.pop(source_index)
    props_list.insert(dest_index, moved)

    # 書き戻し
    _write_shapekeys(key_blocks, props_list, start_index=0)

    print(f"[move_shapekey_to_index] Moved '{shapekey_name}' to index {dest_index} on '{obj.name}'")
    return True


def move_shapekey_before(obj, target_name, before_name):
    """指定シェイプキーを別のシェイプキーの直前に移動

    Args:
        obj: 対象メッシュオブジェクト
        target_name: 移動するシェイプキー名
        before_name: この直前に移動する

    Returns:
        bool: 成功したらTrue
    """
    if not obj.data.shape_keys:
        print(f"[move_shapekey_before] No shape keys on '{obj.name}'")
        return False

    key_blocks = obj.data.shape_keys.key_blocks
    target_index = get_shape_key_index(obj, target_name)
    before_index = get_shape_key_index(obj, before_name)

    if target_index == -1:
        print(f"[move_shapekey_before] Target '{target_name}' not found on '{obj.name}'")
        return False
    if before_index == -1:
        print(f"[move_shapekey_before] Before '{before_name}' not found on '{obj.name}'")
        return False

    if target_index == before_index:
        return True

    # 全シェイプキーをシリアライズ
    props_list = _serialize_shapekeys(key_blocks, start_index=0)

    # リスト操作: targetを抜き出してbeforeの直前に挿入
    moved = props_list.pop(target_index)
    # pop後のbefore位置を再計算（targetがbeforeより前にあった場合は1つ前にずれる）
    new_before_index = None
    for i, props in enumerate(props_list):
        if props['name'] == before_name:
            new_before_index = i
            break

    if new_before_index is None:
        print(f"[move_shapekey_before] Failed to locate '{before_name}' after pop")
        return False

    props_list.insert(new_before_index, moved)

    # 書き戻し
    _write_shapekeys(key_blocks, props_list, start_index=0)

    print(f"[move_shapekey_before] Moved '{target_name}' before '{before_name}' on '{obj.name}'")
    return True


def reorder_shapekeys_for_object(obj, operations_list):
    """オブジェクトに対して複数の並び替え操作を順次適用

    Args:
        obj: 対象メッシュオブジェクト
        operations_list: 操作辞書のリスト。各辞書は以下のキーを含む:
            - 'type': 'MOVE_TO_INDEX' | 'SORT_BY_NAME' | 'SWAP' | 'MOVE_BEFORE'
            - 'target': 対象シェイプキー名（SORT_BY_NAME以外で必要）
            - 'index': 移動先インデックス（MOVE_TO_INDEX用）
            - 'second': 2つ目のシェイプキー名（SWAP, MOVE_BEFORE用）

    Returns:
        int: 成功した操作数
    """
    if not obj.data.shape_keys:
        print(f"[reorder_shapekeys_for_object] No shape keys on '{obj.name}'")
        return 0

    count = 0
    for op in operations_list:
        op_type = op.get('type', '')
        target = op.get('target', '')
        second = op.get('second', '')
        index = op.get('index', 0)

        if op_type == 'SORT_BY_NAME':
            sort_shapekeys_by_name(obj)
            count += 1
        elif op_type == 'SWAP':
            if swap_shapekeys(obj, target, second):
                count += 1
        elif op_type == 'MOVE_TO_INDEX':
            if move_shapekey_to_index(obj, target, index):
                count += 1
        elif op_type == 'MOVE_BEFORE':
            if move_shapekey_before(obj, target, second):
                count += 1
        else:
            print(f"[reorder_shapekeys_for_object] Unknown operation type: '{op_type}'")

    return count


def reorder_shapekeys_iter(objects_with_settings):
    """複数オブジェクトに対する並び替え処理（ジェネレータ版）

    MizoresCustomExporter連携時のModal処理で使用する。

    Args:
        objects_with_settings: [(obj, operations_list), ...] のリスト
            operations_listの形式はreorder_shapekeys_for_objectを参照

    Yields:
        ProgressInfo: 進捗情報
    """
    total = len(objects_with_settings)
    if total == 0:
        return

    yield ProgressInfo(
        phase="reorder",
        progress=0.0,
        message="Reordering shape keys...",
        total_objects=total,
    )

    for idx, (obj, operations_list) in enumerate(objects_with_settings):
        progress = idx / total
        yield ProgressInfo(
            phase="reorder",
            progress=progress,
            message=f"Reordering shape keys: {obj.name}",
            object_name=obj.name,
            sub_progress=progress,
            total_objects=total,
            current_object_index=idx,
        )

        count = reorder_shapekeys_for_object(obj, operations_list)
        print(f"[reorder_shapekeys_iter] '{obj.name}': {count} reorder operations applied")

    yield ProgressInfo(
        phase="reorder",
        progress=1.0,
        message="Shape key reordering complete",
        total_objects=total,
        current_object_index=total,
    )
