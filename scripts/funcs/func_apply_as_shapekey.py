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
from ..funcs.utils import func_object_utils
from ..funcs import func_shapekey_utils


def apply_as_shapekey(modifier):
    try:
        obj = func_object_utils.get_active_object()
        print(f"ShapeKeysUtil - func_apply_as_shapekey: {modifier.name}")
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
                bpy.ops.object.modifier_apply_as_shapekey(keep_modifier=keep_modifier, modifier=modifier.name)
                # シェイプキー名を変更
                new_shapekey = obj.data.shape_keys.key_blocks[-1]
                new_shapekey.name = key.name
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

        # 名前の文字列から%AS%を削除する
        shape_name = consts.REGEX_APPLY_AS_SHAPEKEY_PREFIX.sub("", modifier.name)
        # 名前の文字列から$以降を削除する
        shape_name = shape_name.split("$")[0]

        # 同名のシェイプキーが存在するならインデックスを取得
        already_exists_index = func_shapekey_utils.get_shape_key_index(obj, shape_name)
        if already_exists_index == -1:
            if not obj.data.shape_keys and shape_name == 'Basis':
                # シェイプキーが存在せず、新規シェイプキー名がBasisの場合は通常のモディファイア適用
                bpy.ops.object.modifier_apply(modifier=modifier.name)
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
            modifier_name = modifier.name,
            modifier_type = modifier.type
        )
        print(e)
        # bpy.ops.object.modifier_remove(modifier=modifier.name)
        raise Exception(warn)
    else:
        try:
            print("func_apply_as_shapekey: [{0}]".format(modifier.name))
        except UnicodeDecodeError:
            print("func_apply_as_shapekey")
