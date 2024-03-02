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
from ..funcs.utils import func_object_utils
from ..funcs import func_shapekey_utils


def apply_as_shapekey(modifier):
    try:
        obj = func_object_utils.get_active_object()
        # 名前の文字列から%AS%を削除する
        shape_name = modifier.name[len(consts.APPLY_AS_SHAPEKEY_PREFIX):len(modifier.name)]
        # 名前の文字列から$以降を削除する
        shape_name = shape_name.split("$")[0]

        # 同名のシェイプキーが存在するならインデックスを取得
        already_exists_index = func_shapekey_utils.get_shape_key_index(obj, shape_name)
        if already_exists_index == -1:
            if not obj.data.shape_keys and shape_name == 'Basis':
                # シェイプキーが存在せず、新規シェイプキー名がBasisの場合はBasisを上書きする
                print(f"override Basis shapekey: {shape_name}")
                # Apply As Shape
                bpy.ops.object.modifier_apply_as_shapekey(keep_modifier=False, modifier=modifier.name)
                obj.shape_key_remove(obj.data.shape_keys.key_blocks[0])
                obj.data.shape_keys.key_blocks[0].name = shape_name
            else:
                print(f"add shapekey: {shape_name}")
                # Apply As Shape
                bpy.ops.object.modifier_apply_as_shapekey(keep_modifier=False, modifier=modifier.name)
                # シェイプキー名を変更
                new_shapekey = obj.data.shape_keys.key_blocks[-1]
                new_shapekey.name = shape_name
        else:
            # 同名のシェイプキーが存在するなら、そのシェイプキーに対してモディファイアの変形を適用する
            print(f"override shapekey: {shape_name}")
            temp_selected_objects = bpy.context.selected_objects
            func_object_utils.deselect_all_objects()
            func_object_utils.select_object(obj, True)
            func_object_utils.set_active_object(obj)
            # オブジェクトをコピーしてモディファイアを適用
            dup_obj = func_object_utils.duplicate_object(obj)
            func_shapekey_utils.bake_shape_key(already_exists_index)
            bpy.ops.object.modifier_apply(modifier=modifier.name)

            func_object_utils.set_active_object(obj)
            # Apply As Shape
            bpy.ops.object.modifier_apply_as_shapekey(keep_modifier=False, modifier=modifier.name)
            # 既存のシェイプキーを新規シェイプキーで上書き
            new_shapekey = obj.data.shape_keys.key_blocks[-1]
            exists_shapekey = obj.data.shape_keys.key_blocks[already_exists_index]
            for i, v in enumerate(new_shapekey.data):
                exists_shapekey.data[i].co = v.co
            obj.shape_key_remove(new_shapekey)

            # コピーしたオブジェクトを削除
            func_object_utils.remove_object(dup_obj)

            func_object_utils.select_objects(temp_selected_objects)

    except RuntimeError as e:
        # 無効なModifier（対象オブジェクトが指定されていないなどの状態）は適用しない
        print("!!! Apply as shapekey failed !!!: [{0}]".format(modifier.name))
        print(e)
        bpy.ops.object.modifier_remove(modifier=modifier.name)
    else:
        try:
            print("Apply as shapekey: [{0}]".format(modifier.name))
        except UnicodeDecodeError:
            print("Apply as shapekey")
