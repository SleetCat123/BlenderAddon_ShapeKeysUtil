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
import mathutils

from .. import consts
from ..funcs import func_composite_shapekey, func_shapekey_utils
from ..funcs.utils import func_object_utils


def _apply_override_delta(obj, modifier, already_exists_index):
    """
    デルタ加算モード: Basisからの差分を既存シェイプキーに加算
    """
    modifier_name = modifier.name
    base_shapekey_name = consts.get_base_shapekey_name(modifier)

    # モディファイア変形を新規シェイプキーとして取得（Basisとの差分）
    bpy.ops.object.modifier_apply_as_shapekey(keep_modifier=False, modifier=modifier_name)
    new_shapekey = obj.data.shape_keys.key_blocks[-1]

    # ベースシェイプキーがあれば減算処理
    if base_shapekey_name:
        func_composite_shapekey.apply_composite_subtraction(obj, new_shapekey, base_shapekey_name)

    # 既存シェイプキーを取得
    exists_shapekey = obj.data.shape_keys.key_blocks[already_exists_index]
    basis = obj.data.shape_keys.key_blocks[0]

    # 既存シェイプキーの座標に、新規シェイプキーの差分（Basisからの変位）を加算
    for i in range(len(exists_shapekey.data)):
        delta_x = new_shapekey.data[i].co.x - basis.data[i].co.x
        delta_y = new_shapekey.data[i].co.y - basis.data[i].co.y
        delta_z = new_shapekey.data[i].co.z - basis.data[i].co.z
        exists_shapekey.data[i].co.x += delta_x
        exists_shapekey.data[i].co.y += delta_y
        exists_shapekey.data[i].co.z += delta_z

    # 新規シェイプキーを削除
    obj.shape_key_remove(new_shapekey)


def _apply_override_direct(obj, modifier, already_exists_index):
    """
    直接適用モード: 既存シェイプキーの座標に直接変形を適用
    """
    modifier_name = modifier.name
    base_shapekey_name = consts.get_base_shapekey_name(modifier)

    temp_selected_objects = bpy.context.selected_objects

    func_object_utils.deselect_all_objects()
    func_object_utils.select_object(obj, True)
    func_object_utils.set_active_object(obj)

    # オブジェクトをコピーしてモディファイアを適用
    dup_obj = func_object_utils.duplicate_object(obj)

    # 同名シェイプキーの形状がベースになるようにして他シェイプを消す
    func_shapekey_utils.bake_shape_key(already_exists_index)

    # AS用モディファイアを普通に適用
    bpy.ops.object.modifier_apply(modifier=modifier_name)

    # 元オブジェクトにJoin as Shape
    func_object_utils.select_object(dup_obj, True)
    func_object_utils.select_object(obj, True)
    func_object_utils.set_active_object(obj)
    bpy.ops.object.join_shapes()

    # AS用モディファイアは削除
    bpy.ops.object.modifier_remove(modifier=modifier_name)

    # 既存のシェイプキーを新規シェイプキーで上書き
    new_shapekey = obj.data.shape_keys.key_blocks[-1]

    # ベースシェイプキーがあれば減算処理
    if base_shapekey_name:
        func_composite_shapekey.apply_composite_subtraction(obj, new_shapekey, base_shapekey_name)

    exists_shapekey = obj.data.shape_keys.key_blocks[already_exists_index]
    for i, v in enumerate(new_shapekey.data):
        exists_shapekey.data[i].co = v.co
    obj.shape_key_remove(new_shapekey)

    # コピーしたオブジェクトを削除
    func_object_utils.remove_object(dup_obj)

    func_object_utils.select_objects(temp_selected_objects)


def apply_as_shapekey(modifier):
    modifier_name = modifier.name
    modifier_type = modifier.type
    base_shapekey_name = consts.get_base_shapekey_name(modifier)

    try:
        obj = func_object_utils.get_active_object()
        print(f"ShapeKeysUtil - func_apply_as_shapekey: {modifier_name}")
        if consts.use_apply_each_shapekeys(modifier):
            # SurfaceDeformモディファイアのターゲットオブジェクトにシェイプキーが2つ以上存在していて、最初のシェイプキーの名前が"All"ならshow_only_shape_keyをTrueにしてシェイプキーを個別にシェイプキーとして適用
            print("Add shapekeys from SurfaceDeform")
            mod_target = modifier.target
            temp_show_only_shape_key = mod_target.show_only_shape_key
            temp_active_shape_key_index = mod_target.active_shape_key_index

            mod_target.show_only_shape_key = True
            key_blocks = mod_target.data.shape_keys.key_blocks
            len_key_blocks = len(key_blocks)
            for i in range(1, len_key_blocks):
                key = key_blocks[i]
                print(f"add shapekey: {key.name}")
                mod_target.active_shape_key_index = i

                if i == len_key_blocks - 1:
                    keep_modifier = False
                else:
                    keep_modifier = True
                bpy.ops.object.modifier_apply_as_shapekey(keep_modifier=keep_modifier, modifier=modifier_name)
                # シェイプキー名を変更
                new_shapekey = obj.data.shape_keys.key_blocks[-1]
                # シェイプキー名から個別のベース指定をチェック
                clean_name, individual_base = consts.parse_shapekey_name_for_base(key.name)
                # 個別ベースがなければモディファイアのベースを使用
                if not individual_base:
                    individual_base = base_shapekey_name
                # ベースシェイプキーがあれば減算処理
                if individual_base:
                    func_composite_shapekey.apply_composite_subtraction(obj, new_shapekey, individual_base)
                new_shapekey.name = clean_name
            mod_target.show_only_shape_key = temp_show_only_shape_key
            mod_target.active_shape_key_index = temp_active_shape_key_index
            # 特殊な処理なので以降の処理はスキップ
            return

        use_inverted_bones = consts.use_inverted_bones_as_shapekey(modifier)
        if use_inverted_bones:
            # %AS:I%で始まっているならボーンの移動を反転した状態でApply as shapekey
            print("Apply as shapekey with inverted bones")
            mod_target = modifier.object
            # ボーンの移動と回転とスケールを記憶
            bone_locations = {}
            bone_rotations = {}
            bone_scales = {}
            for pose_bone in mod_target.pose.bones:
                bone_locations[pose_bone.name] = pose_bone.location.copy()
                bone_rotations[pose_bone.name] = pose_bone.rotation_quaternion.copy()
                bone_scales[pose_bone.name] = pose_bone.scale.copy()
            # pose boneの移動と回転とスケールを反転
            for pose_bone in mod_target.pose.bones:
                pose_bone.location = mathutils.Vector((-pose_bone.location[0], -pose_bone.location[1], -pose_bone.location[2]))
                pose_bone.rotation_quaternion = pose_bone.rotation_quaternion.inverted()
                pose_bone.scale = mathutils.Vector((1 / pose_bone.scale[0], 1 / pose_bone.scale[1], 1 / pose_bone.scale[2]))

        # 名前の文字列から%AS%を削除し、$以降と.001などのサフィックスも削除する
        raw_name = consts.REGEX_APPLY_AS_SHAPEKEY_PREFIX.sub("", modifier_name)
        shape_name = consts.normalize_shapekey_name(raw_name)

        # 同名のシェイプキーが存在するならインデックスを取得
        already_exists_index = func_shapekey_utils.get_shape_key_index(obj, shape_name)
        if already_exists_index == -1:
            if not obj.data.shape_keys and shape_name == 'Basis':
                # シェイプキーが存在せず、新規シェイプキー名がBasisの場合は通常のモディファイア適用
                bpy.ops.object.modifier_apply(modifier=modifier_name)
            else:
                print(f"add shapekey: {shape_name}")
                bpy.ops.object.modifier_apply_as_shapekey(keep_modifier=False, modifier=modifier_name)
                new_shapekey = obj.data.shape_keys.key_blocks[-1]
                if base_shapekey_name:
                    func_composite_shapekey.apply_composite_subtraction(obj, new_shapekey, base_shapekey_name)
                new_shapekey.name = shape_name
        else:
            # 同名のシェイプキーが存在するなら、そのシェイプキーに対してモディファイアの変形を適用
            use_direct_mode = consts.use_direct_apply_mode(modifier)

            if use_direct_mode:
                # 直接適用モード: 既存シェイプキーの座標に直接変形を適用
                print(f"override shapekey (DIRECT mode): {shape_name}")
                _apply_override_direct(obj, modifier, already_exists_index)
            else:
                # デルタ加算モード（デフォルト）: Basisからの差分を既存シェイプキーに加算
                print(f"override shapekey (DELTA mode): {shape_name}")
                _apply_override_delta(obj, modifier, already_exists_index)

        if use_inverted_bones:
            # ボーンの移動と回転とスケールを元に戻す
            for pose_bone in mod_target.pose.bones:
                pose_bone.location = bone_locations[pose_bone.name]
                pose_bone.rotation_quaternion = bone_rotations[pose_bone.name]
                pose_bone.scale = bone_scales[pose_bone.name]
    except RuntimeError as e:
        # 無効なModifier（対象オブジェクトが指定されていないなどの状態）は適用しない
        warn = bpy.app.translations.pgettext("mizore_error_apply_as_shapekey_invalid_modifier").format(
            obj_name = obj.name,
            modifier_name = modifier_name,
            modifier_type = modifier_type
        )
        print(e)
        raise Exception(warn) from e
    else:
        print(f"func_apply_as_shapekey: [{modifier_name}]")
