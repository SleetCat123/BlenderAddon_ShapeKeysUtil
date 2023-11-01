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
import time
from BlenderAddon_ShapeKeysUtil.scripts.funcs import func_apply_modifiers
from BlenderAddon_ShapeKeysUtil.scripts.funcs.utils import func_object_utils, func_mesh_utils, func_package_utils


# シェイプキーをそれぞれ別のオブジェクトにする
def separate_shapekeys(
        duplicate: bool,
        enable_apply_modifiers: bool,
        remove_nonrender: bool = True,
        remove_original_shapekeys: bool = True
):
    source_obj = func_object_utils.get_active_object()
    source_obj_name = source_obj.name

    func_object_utils.deselect_all_objects()

    if duplicate:
        func_object_utils.select_object(source_obj, True)
        func_object_utils.set_active_object(source_obj)
        func_object_utils.duplicate_object()
        source_obj = func_object_utils.get_active_object()

    source_obj_matrix_world_inverted = source_obj.matrix_world.inverted()

    print("Separate ShapeKeys: [" + source_obj.name + "]")
    wait_counter = 0
    separated_objects = []
    shape_keys_length = len(source_obj.data.shape_keys.key_blocks)

    addon_prefs = func_package_utils.get_addon_prefs()
    wait_interval = addon_prefs.wait_interval
    wait_sleep = addon_prefs.wait_sleep

    func_object_utils.select_object(source_obj, True)
    for i, shapekey in enumerate(source_obj.data.shape_keys.key_blocks):
        print("Shape key [" + shapekey.name + "] [" + str(i) + " / " + str(shape_keys_length) + "]")

        # CPU負荷が高いっぽいので何回かに一回ウェイトをかける
        wait_counter += 1
        if wait_counter % wait_interval == 0:
            print("wait")
            time.sleep(wait_sleep)

        new_name = source_obj_name + "." + shapekey.name
        # Basisは無視
        if i == 0:
            if duplicate:
                func_object_utils.set_object_name(source_obj, new_name)
            continue

        # オブジェクトを複製し、元オブジェクトの子にする
        # bpy.ops.object.parent_setだと更新処理が走って重くなるのでLowLevelな方法を採用
        dup_obj = func_object_utils.duplicate_object(source_obj)
        dup_obj.parent = source_obj
        dup_obj.matrix_parent_inverse = source_obj_matrix_world_inverted
        # シェイプキーの名前を設定
        func_object_utils.set_object_name(dup_obj, new_name)

        # シェイプキーをsource_objからdup_objにコピー
        func_object_utils.select_object(source_obj, True)
        source_obj.active_shape_key_index = i
        # shapekey = source_obj.data.shape_keys.key_blocks[i]
        shapekey.value = 1
        dup_obj.shape_key_clear()
        bpy.ops.object.shape_key_transfer()

        # シェイプキーを削除し形状を固定
        dup_obj.shape_key_remove(dup_obj.data.shape_keys.key_blocks[0])  # Basisを消す
        dup_obj.shape_key_remove(dup_obj.data.shape_keys.key_blocks[0])  # 固定するシェイプキーを消す

        separated_objects.append(dup_obj)

        func_object_utils.select_object(dup_obj, False)

    if remove_original_shapekeys:
        # 元オブジェクトのシェイプキーを全削除
        source_obj.shape_key_clear()

    func_object_utils.deselect_all_objects()

    if enable_apply_modifiers:
        if not remove_original_shapekeys:
            func_object_utils.set_active_object(source_obj)
            func_apply_modifiers.apply_modifiers(remove_nonrender=remove_nonrender)
        for obj in separated_objects:
            func_object_utils.set_active_object(obj)
            func_apply_modifiers.apply_modifiers(remove_nonrender=remove_nonrender)
        func_object_utils.set_active_object(source_obj)

    # 表示を更新
    func_mesh_utils.update_mesh()

    print("Finish Separate ShapeKeys: [" + source_obj.name + "]")
    return separated_objects
