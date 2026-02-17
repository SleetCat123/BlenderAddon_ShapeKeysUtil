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

from .func_shapekey_utils import get_shape_key_index
from .progress_info import ProgressInfo


def change_base_shapekey(obj, source_shapekey_name, reverse_shapekey_name):
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

    source_index = get_shape_key_index(obj, source_shapekey_name)
    if source_index == -1:
        print(f"[change_base_shapekey] Source '{source_shapekey_name}' not found on '{obj.name}'")
        return False

    if source_index == 0:
        print("[change_base_shapekey] Cannot use Basis as source")
        return False

    basis = key_blocks[0]
    source = key_blocks[source_index]

    # Basisの頂点座標を保存
    basis_co = [(v.co.x, v.co.y, v.co.z) for v in basis.data]

    # Sourceの頂点座標をBasisにコピー
    source_co = [(v.co.x, v.co.y, v.co.z) for v in source.data]
    for i, v in enumerate(basis.data):
        v.co = source_co[i]

    # 保存したBasis座標をSourceに書き込み（逆シェイプキー化）
    for i, v in enumerate(source.data):
        v.co = basis_co[i]

    # Sourceをreverse名にリネーム
    source.name = reverse_shapekey_name

    print(f"[change_base_shapekey] '{source_shapekey_name}' -> Basis, reverse: '{reverse_shapekey_name}' on '{obj.name}'")
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
    for source_name, reverse_name in settings_list:
        if change_base_shapekey(obj, source_name, reverse_name):
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
