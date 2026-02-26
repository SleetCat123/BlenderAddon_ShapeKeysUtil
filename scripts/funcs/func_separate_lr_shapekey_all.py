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

import time
from collections.abc import Generator

import bpy

from .. import consts
from ..funcs import func_separate_lr_shapekey
from ..funcs.utils import func_object_utils
from .progress_info import ProgressInfo


def separate_lr_shapekey_all_iter(
    duplicate: bool,
    enable_sort: bool,
    auto_detect: bool
) -> Generator[ProgressInfo, None, None]:
    """左右シェイプキー分割（ジェネレータ版）

    Args:
        duplicate: 元のシェイプキーを保持するか
        enable_sort: ソートを有効にするか
        auto_detect: タグ自動検出を使用するか

    Yields:
        ProgressInfo: 進捗情報
    """
    start_time = time.perf_counter()
    obj = func_object_utils.get_active_object()
    obj_name = obj.name
    print(f"[separate_lr_shapekey_all] start: {obj_name}")

    yield ProgressInfo(
        phase="init",
        progress=0.0,
        message=f"Starting LR separation: {obj_name}",
        object_name=obj_name
    )

    # 頂点を全て表示
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.reveal()
    bpy.ops.object.mode_set(mode='OBJECT')

    shape_keys_length = len(obj.data.shape_keys.key_blocks)

    # 処理対象のシェイプキーをカウント
    process_count = 0
    for i in reversed(range(shape_keys_length)):
        if i == 0:
            break
        shapekey = obj.data.shape_keys.key_blocks[i]
        if shapekey.name.endswith("_left") or shapekey.name.endswith("_right"):
            continue
        if not auto_detect or (auto_detect and shapekey.name.find(consts.ENABLE_LR_TAG) != -1):
            process_count += 1

    processed = 0
    for i in reversed(range(shape_keys_length)):
        if i == 0:
            break
        shapekey = obj.data.shape_keys.key_blocks[i]

        # 名前の最後が_leftまたは_rightのシェイプキーは既に左右分割済みと見なし処理スキップ
        if shapekey.name.endswith("_left") or shapekey.name.endswith("_right"):
            continue
        # auto_detectがTrueなら、名前に"%LR%"を含むときだけ左右分割処理を行う
        if not auto_detect or (auto_detect and shapekey.name.find(consts.ENABLE_LR_TAG) != -1):
            print("Shapekey: [" + shapekey.name + "]")

            progress = processed / max(process_count, 1)
            yield ProgressInfo(
                phase="separate_lr",
                progress=progress,
                message=f"LR separate: {shapekey.name}",
                object_name=obj_name
            )

            dup_temp = duplicate
            sort_temp = enable_sort
            if auto_detect:
                # 名前に"%DUP%"を含むなら強制的に複製ON
                if shapekey.name.find(consts.ENABLE_DUPLICATE_TAG) != -1:
                    dup_temp = True
                # 名前に"%SORT%"を含むなら強制的にソートON
                if shapekey.name.find(consts.ENABLE_SORT_TAG) != -1:
                    sort_temp = True
            func_separate_lr_shapekey.separate_lr_shapekey(
                source_shape_key_index=i,
                duplicate=dup_temp,
                enable_sort=sort_temp
            )
            processed += 1

    yield ProgressInfo(
        phase="complete",
        progress=1.0,
        message=f"Complete: {obj_name}",
        object_name=obj_name
    )

    print(f"[separate_lr_shapekey_all] {obj_name}: {time.perf_counter() - start_time:.3f}s")


def separate_lr_shapekey_all(duplicate, enable_sort, auto_detect):
    """左右シェイプキー分割（同期版ラッパー）

    既存コードとの互換性のため、ジェネレータ版を消費して実行します。
    """
    gen = separate_lr_shapekey_all_iter(
        duplicate=duplicate,
        enable_sort=enable_sort,
        auto_detect=auto_detect
    )
    for _ in gen:
        pass
