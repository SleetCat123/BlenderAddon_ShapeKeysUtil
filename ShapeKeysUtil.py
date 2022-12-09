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
import bmesh
import time
from bpy.props import *

bl_info = {
    "name": "ShapeKeys Util",
    "author": "@sleetcat123(Twitter)",
    "version": (1,1,6),
    "blender": (2, 80, 0),
    "location": "",
    "description": "",
    "category": "Object"
}

# Create Left and Right Shape Keys の自動判定で使うやつ
ENABLE_LR_TAG = "%LR%"
ENABLE_DUPLICATE_TAG = "%D%"
ENABLE_SORT_TAG = "%S%"

# Apply Modifier用
APPLY_AS_SHAPEKEY_PREFIX = "%AS%"  # モディファイア名が%AS%で始まっているならApply as shapekey
FORCE_APPLY_MODIFIER_PREFIX = "%A%"  # モディファイア名が"%A%"で始まっているならArmatureなどの対象外モディファイアでも強制的に適用

# Func - Version Compatible #


def select_object(obj, value=True):
    obj.select_set(value)


def select_objects(objects, value=True):
    for obj in objects:
        select_object(obj, value)


def get_active_object():
    return bpy.context.view_layer.objects.active


def set_active_object(obj):
    bpy.context.view_layer.objects.active=obj


def deselect_all_objects():
    print("deselect_all_objects")
    targets = bpy.context.selected_objects
    for obj in targets:
        select_object(obj, False)
    # bpy.context.view_layer.objects.active = None


def set_object_name(obj, name):
    obj.name = name
    if obj.data:
        obj.data.name = name


def select_axis(mode='POSITIVE', axis='X', threshold=0.0001):
    if mode == 'POSITIVE':
        mode = 'POS'
    elif mode == 'NEGATIVE':
        mode = 'NEG'
    elif mode == 'ALIGNED':
        mode = 'ALIGN'
    bpy.ops.mesh.select_axis(sign=mode, axis=axis, threshold=threshold)


def get_addon_prefs():
    return bpy.context.preferences.addons[__name__].preferences

# region Translation #


translations_dict = {
    "en_US": {
        ("*",
          "object.shapekeys_util_apply_modifiers_desc"): "Apply all modifiers except for Armature.\nCan use even if has a shape key.\nWarning: It may take a while",
        ("*",
          "object.shapekeys_util_separateobj_desc"): "Separate objects for each shape keys.\nWarning: It may take a while",
        ("*",
          "object.shapekeys_util_separate_lr_shapekey_desc"): "A selected shape key separate left and right based on object origin.",
        ("*",
          "object.shapekeys_util_separate_lr_shapekey_all_desc"): "All shape key separate left and right based on object origin.\nSeparation is skipping if a shape key name ends with \"_left\" or \"_right\"",
        ("*",
          "object.shapekeys_util_separate_lr_shapekey_all_tagdetect_desc"): "See \"Read-me.txt\"\nCan't use if a shape key name ends with \"_left\" or \"_right\"",
        ("*", "object.shapekeys_util_assign_lr_shapekey_tag_desc"): "See \"Read-me.txt\"",

        ("*", "object.shapekeys_util_apply_modifiers_duplicate"): "Execute the function on the copied object",
        ("*", "object.shapekeys_util_separateobj_duplicate"): "Execute the function on the copied object",
        ("*", "object.shapekeys_util_separateobj_apply_modifiers"): "Apply modifiers after separation",
        ("*",
          "object.shapekeys_util_separate_lr_shapekey_enable_sort"): "Result shape keys move to below target shape key",
        ("*", "object.shapekeys_util_assign_lr_shapekey_tag_enable"): "Assign this shape key to separation target",

        ("*",
          "separate_lr_shapekey_all_enable_sort"): "Result shape keys move to below target shape key.\nWarning: It may take a while",
        ("*", "separate_lr_shapekey_duplicate"): "Execute the function on the copied shape key",

        ("*", "remove_nonrender"): "A non-render modifier will be removed.",
        ("*", "verts_count_difference"): "Warn: vertices count has different:\n[{0}]({2}), [{1}]({3})",
    },
    "ja_JP": {
        ("*",
          "object.shapekeys_util_apply_modifiers_desc"): "Armature以外の全モディファイアを適用します。\nシェイプキーがあっても使用できます。\n注意：少し時間がかかります",
        ("*", "object.shapekeys_util_separateobj_desc"): "シェイプキーをそれぞれ別オブジェクトにします。\n注意：少し時間がかかります",
        ("*", "object.shapekeys_util_separate_lr_shapekey_desc"): "現在のシェイプキーを\nオブジェクト原点基準で左右別々のシェイプキーにします",
        ("*",
          "object.shapekeys_util_separate_lr_shapekey_all_desc"): "全てのシェイプキーをオブジェクト原点基準で左右別々にします。\n名前の最後が_leftまたは_rightのシェイプキーは分割済みと見なし処理をスキップします",
        ("*",
          "object.shapekeys_util_separate_lr_shapekey_all_tagdetect_desc"): "詳細はRead-me.txtを参照。\n名前の最後が_leftまたは_rightのシェイプキーには使えません",
        ("*", "object.shapekeys_util_assign_lr_shapekey_tag_desc"): "詳細はRead-me.txtを参照",

        ("*", "object.shapekeys_util_apply_modifiers_duplicate"): "対象オブジェクトのコピーに対して処理を行います",
        ("*", "object.shapekeys_util_separateobj_duplicate"): "分割前のオブジェクトを残します",
        ("*", "object.shapekeys_util_separateobj_apply_modifiers"): "分割後にオブジェクトのモディファイアを適用します",
        ("*", "object.shapekeys_util_separate_lr_shapekey_enable_sort"): "左右分割後のシェイプキーを分割前シェイプキーのすぐ下に移動します",
        ("*", "object.shapekeys_util_assign_lr_shapekey_tag_enable"): "シェイプキーを左右分割処理の対象とします",

        ("*", "separate_lr_shapekey_all_enable_sort"): "左右分割後のシェイプキーを分割前シェイプキーのすぐ下に移動します。\n注意：時間がかかります",
        ("*", "separate_lr_shapekey_duplicate"): "左右分割前のシェイプキーを残します",

        ("*", "remove_nonrender"): "レンダリング無効化状態のモディファイア\n（モディファイア一覧でカメラアイコンが押されていない）\nを削除します。",
        ("*",
          "verts_count_difference"): "シェイプキーの頂点数が異なっているため処理を実行できませんでした。\nミラーモディファイアの\"結合\"で他より多くの頂点が結合されてしまっている、などの原因が考えられます。\n[{0}]({2}), [{1}]({3})",
    },
}
# endregion #

# Data #
# Func #


def remove_objects(targets=None):
    print("remove_objects")
    if targets is None:
        targets = bpy.context.selected_objects

    data_list = []
    # オブジェクトを削除
    for obj in targets:
        try:
            if obj.data:
                data_list.append(obj.data)
            print("remove: " + str(obj))
            bpy.data.objects.remove(obj)
        except ReferenceError:
            continue

    # オブジェクトのデータを削除
    for data in data_list:
        blocks = None
        data_type = type(data)
        if data_type == bpy.types.Mesh: blocks = bpy.data.meshes
        elif data_type == bpy.types.Armature: blocks = bpy.data.armatures
        elif data_type == bpy.types.Curve: blocks = bpy.data.curves
        elif data_type == bpy.types.Lattice: blocks = bpy.data.lattices
        elif data_type == bpy.types.Light: blocks = bpy.data.lights
        elif data_type == bpy.types.Camera: blocks = bpy.data.cameras
        elif data_type == bpy.types.MetaBall: blocks = bpy.data.metaballs
        elif data_type == bpy.types.GreasePencil: blocks = bpy.data.grease_pencils

        if blocks and data.users == 0:
            print("remove: " + str(data))
            blocks.remove(data)


# オブジェクトのモディファイアを適用
def apply_modifiers(remove_nonrender=True):
    print("apply_modifiers")
    obj = get_active_object()

    if obj.users != 1 or (obj.data and obj.data.users != 1):
        # リンクされたオブジェクトのモディファイアは適用できないので予めリンクを解除しておく
        bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=True, obdata=True, material=False, animation=False)
    
    print("Apply Modifiers: ["+obj.name+"]")
    for modifier in obj.modifiers:
        if not modifier.show_render:
            # モディファイアがレンダリング対象ではない（モディファイア一覧のカメラアイコンが押されていない）なら無視
            if remove_nonrender:
                bpy.ops.object.modifier_remove(modifier=modifier.name)
            continue
        
        if modifier.name.startswith(APPLY_AS_SHAPEKEY_PREFIX):
            # ここではApply as shapekeyさせたくない
            print("ERROR: apply_as_shapekey")
            bpy.ops.object.modifier_remove(modifier=modifier.name)
        elif modifier.name.startswith(FORCE_APPLY_MODIFIER_PREFIX) or modifier.type != 'ARMATURE':
            # 対象モディファイアが処理対象外モディファイアでないなら
            # または、モディファイアの名前欄が%A%で始まっているなら
            try:
                bpy.ops.object.modifier_apply(modifier=modifier.name)
            except RuntimeError:
                # 無効なModifier（対象オブジェクトが指定されていないなどの状態）は適用しない
                print("!!! Apply failed !!!: [{0}]".format(modifier.name))
                bpy.ops.object.modifier_remove(modifier=modifier.name)
            else:
                try:
                    # なんかここだけUnicodeEncodeErrorが出たり出なかったりする。なんで……？
                    print("Apply: [{0}]".format(modifier.name))
                except UnicodeDecodeError:
                    print("Apply")
    print("Finish Apply Modifiers: [{0}]".format(obj.name))


def apply_as_shapekey(modifier):
    try:
        # 名前の文字列から%AS%を削除する
        modifier.name = modifier.name[len(APPLY_AS_SHAPEKEY_PREFIX):len(modifier.name)]
        # Apply As Shape
        bpy.ops.object.modifier_apply_as_shapekey(keep_modifier=False, modifier=modifier.name)
    except RuntimeError:
        # 無効なModifier（対象オブジェクトが指定されていないなどの状態）は適用しない
        print("!!! Apply as shapekey failed !!!: [{0}]".format(modifier.name))
        bpy.ops.object.modifier_remove(modifier=modifier.name)
    else:
        try:
            print("Apply as shapekey: [{0}]".format(modifier.name))
        except UnicodeDecodeError:
            print("Apply as shapekey")


# シェイプキーをもつオブジェクトのモディファイアを適用
# AutoMerge連携用
def apply_modifiers_with_shapekeys_for_automerge_addon(self, source_obj):
    return apply_modifiers_with_shapekeys(self=self, source_obj=source_obj, duplicate=False, remove_nonrender=True)


# シェイプキーをもつオブジェクトのモディファイアを適用
def apply_modifiers_with_shapekeys(self, source_obj, duplicate, remove_nonrender=True):
    print("apply_modifiers_with_shapekeys: [{0}] [{1}]".format(source_obj.name, source_obj.type))
    # Apply as shapekey用モディファイアのインデックスを検索
    apply_as_shape_index = -1
    apply_as_shape_modifier = None
    for i, modifier in enumerate(source_obj.modifiers):
        if modifier.name.startswith(APPLY_AS_SHAPEKEY_PREFIX):
            apply_as_shape_index = i
            apply_as_shape_modifier = modifier
            print(f"apply as shape: {modifier.name}[{str(apply_as_shape_index)}]")
            break
    if apply_as_shape_index == 0:
        # Apply as shapekey用のモディファイアが一番上にあったらApply as shapekeyを実行
        print("apply_as_shapekey__B1")
        apply_as_shapekey(apply_as_shape_modifier)
        print("apply_as_shapekey__B2")
        # 関数を再実行して終了
        return apply_modifiers_with_shapekeys(self, source_obj, duplicate, remove_nonrender)
    elif apply_as_shape_index != -1:
        # 2番目以降にApply as shape用のモディファイアがあったら
        # 一時オブジェクトを作成
        bpy.ops.object.duplicate()
        tempobj = get_active_object()
        select_object(tempobj, True)
        print("duplicate: "+tempobj.name)
        set_active_object(source_obj)
        # モディファイアを一時オブジェクトにコピー
        print("copyto temp: make_links_data(type='MODIFIERS')")
        bpy.ops.object.make_links_data(type='MODIFIERS')

        # Apply as shapekeyとそれよりあとのモディファイアを削除
        for modifier in source_obj.modifiers[apply_as_shape_index:]:
            bpy.ops.object.modifier_remove(modifier=modifier.name)

        # 関数を再実行
        success=apply_modifiers_with_shapekeys(self, source_obj, duplicate, remove_nonrender)
        if not success:
            # 処理に失敗したら処理前のデータを復元して終了
            select_object(source_obj, True)
            set_active_object(tempobj)
            bpy.ops.object.make_links_data(type='OBDATA')
            bpy.ops.object.make_links_data(type='MODIFIERS')
            return False

        # 削除していたモディファイアを一時オブジェクトから復元
        select_object(source_obj, True)
        set_active_object(tempobj)
        print("restore: make_links_data(type='MODIFIERS')")
        bpy.ops.object.make_links_data(type='MODIFIERS')
        print("a")
        set_active_object(source_obj)
        # 適用済みのモディファイアを削除
        for modifier in source_obj.modifiers[:apply_as_shape_index]:
            bpy.ops.object.modifier_remove(modifier=modifier.name)

        # 一時オブジェクトを削除
        select_object(source_obj, False)
        select_object(tempobj, True)
        remove_objects()
        select_object(source_obj, True)
        set_active_object(source_obj)

        # 関数を再実行して終了
        return apply_modifiers_with_shapekeys(self, source_obj, duplicate, remove_nonrender)

    if source_obj.data.shape_keys and len(source_obj.data.shape_keys.key_blocks) == 1:
        # Basisしかなければシェイプキー削除
        print("remove basis: " + source_obj.name)
        bpy.ops.object.shape_key_remove(all=True)

    if source_obj.data.shape_keys is None or len(source_obj.data.shape_keys.key_blocks) == 0:
        # シェイプキーがなければモディファイア適用処理だけ実行
        print("only apply_modifiers: " + source_obj.name)
        apply_modifiers(remove_nonrender=remove_nonrender)
        if duplicate:
            bpy.ops.object.duplicate()
        return True

    # 対象オブジェクトだけを選択
    deselect_all_objects()
    select_object(source_obj, True)
    set_active_object(source_obj)

    # applymodifierの対象となるモディファイアがあるかどうか確認
    need_apply_modifier=False
    for modifier in source_obj.modifiers:
        if modifier.show_render or remove_nonrender:
            if modifier.name.startswith(APPLY_AS_SHAPEKEY_PREFIX) or (modifier.name.startswith(FORCE_APPLY_MODIFIER_PREFIX) or modifier.type != 'ARMATURE'):
                need_apply_modifier=True
                break
    print("{0}: Need Apply Modifiers: {1}".format(source_obj.name, str(need_apply_modifier)))
    if need_apply_modifier:
        # オブジェクトを複製
        bpy.ops.object.duplicate()
        source_obj_dup = get_active_object()
        select_object(source_obj_dup, False)
        select_object(source_obj, True)
        set_active_object(source_obj)

        # シェイプキーの名前と数値を記憶
        active_shape_key_index = source_obj.active_shape_key_index
        shapekey_name_and_values = []
        for shapekey in source_obj.data.shape_keys.key_blocks:
            shapekey_name_and_values.append((shapekey.name, shapekey.value))

        # シェイプキーをそれぞれ別オブジェクトにしてモディファイア適用
        separated_objects = separate_shapekeys(duplicate=False, enable_apply_modifiers=True, remove_nonrender=remove_nonrender)

        print("Source: " + source_obj.name)
        print("------ Merge Separated Objects ------\n" + '\n'.join([obj.name for obj in separated_objects]) + "\n----------------------------------")
    
        prev_obj_name = source_obj.name
        prev_vert_count = len(source_obj.data.vertices)
    
        shape_objects = []
        # オブジェクトを1つにまとめなおす
        select_object(source_obj, True)
        set_active_object(source_obj)
        for obj in separated_objects:
            # 前回のシェイプキーと頂点数が違ったら警告して処理を取り消し
            vert_count = len(obj.data.vertices)
            print("current: [{1}]({3})   prev: [{0}]({2})".format(prev_obj_name, obj.name, str(prev_vert_count), str(vert_count)))
            if vert_count != prev_vert_count:
                warn = bpy.app.translations.pgettext("verts_count_difference").format(prev_obj_name, obj.name, prev_vert_count, vert_count)
                if self: self.report({'ERROR'}, warn)
                print("!!!!! " + warn + "!!!!!")
                # 処理中オブジェクトを削除
                select_object(source_obj, True)
                for child in source_obj.children:
                    select_object(child, True)
                remove_objects()
                select_object(source_obj_dup, True)
                set_active_object(source_obj_dup)
                return False

            prev_vert_count = vert_count
            prev_obj_name = obj.name

            # 一気にjoin_shapesするとシェイプキーの順番がおかしくなるので1つずつ
            select_object(obj, True)
            print("Join: [{2}]({3}) -> [{0}]({1})".format(source_obj.name, str(len(source_obj.data.vertices)), obj.name, str(vert_count)))
            bpy.ops.object.join_shapes()
            select_object(obj, False)

            shape_objects.append(obj)
        select_object(source_obj, False)
        # 使い終わったオブジェクトを削除
        select_objects(shape_objects, True)
        remove_objects()

        # シェイプキーの名前と数値を復元
        source_obj.active_shape_key_index = active_shape_key_index
        for i, shapekey in enumerate(source_obj.data.shape_keys.key_blocks):
            shapekey.name = shapekey_name_and_values[i][0]
            shapekey.value = shapekey_name_and_values[i][1]
    
        if not duplicate:
            # 処理が正常に終了したら複製オブジェクトを削除する
            select_object(source_obj_dup, True)
            remove_objects()

    print("Shapekey Count (Include Basis Shapekey): " + str(len(source_obj.data.shape_keys.key_blocks)))

    select_object(source_obj, True)
    set_active_object(source_obj)
    return True


# シェイプキーをそれぞれ別のオブジェクトにする
def separate_shapekeys(duplicate, enable_apply_modifiers, remove_nonrender=True):
    source_obj = get_active_object()
    source_obj_name = source_obj.name
    
    deselect_all_objects()
    
    if duplicate:
        select_object(source_obj, True)
        set_active_object(source_obj)
        bpy.ops.object.duplicate()
        source_obj = get_active_object()
    
    source_obj_matrix_world_inverted = source_obj.matrix_world.inverted()
    
    print("Separate ShapeKeys: ["+source_obj.name+"]")
    wait_counter = 0
    separated_objects = []
    shape_keys_length = len(source_obj.data.shape_keys.key_blocks)
    
    addon_prefs = get_addon_prefs()
    wait_interval = addon_prefs.wait_interval
    wait_sleep = addon_prefs.wait_sleep
    
    select_object(source_obj, True)
    for i, shapekey in enumerate(source_obj.data.shape_keys.key_blocks):
        print("Shape key ["+shapekey.name+"] ["+str(i)+" / "+str(shape_keys_length)+"]")
        
        # CPU負荷が高いっぽいので何回かに一回ウェイトをかける
        wait_counter += 1
        if wait_counter % wait_interval == 0:
            print("wait")
            time.sleep(wait_sleep)

        new_name=source_obj_name + "." + shapekey.name
        # Basisは無視
        if i == 0:
            if duplicate:
                set_object_name(source_obj,  new_name)
            continue
        
        # オブジェクトを複製
        set_active_object(source_obj)
        bpy.ops.object.duplicate()
        dup_obj = get_active_object()
        
        # 元オブジェクトの子にする
        # bpy.ops.object.parent_setだと更新処理が走って重くなるのでLowLevelな方法を採用
        dup_obj.parent = source_obj
        dup_obj.matrix_parent_inverse = source_obj_matrix_world_inverted
        
        # シェイプキーの名前を設定
        set_object_name(dup_obj, new_name)
        
        # シェイプキーをsource_objからdup_objにコピー
        select_object(source_obj, True)
        source_obj.active_shape_key_index = i
        # shapekey = source_obj.data.shape_keys.key_blocks[i]
        shapekey.value=1
        dup_obj.shape_key_clear()
        bpy.ops.object.shape_key_transfer()
        
        # シェイプキーを削除し形状を固定
        dup_obj.shape_key_remove(dup_obj.data.shape_keys.key_blocks[0]) # Basisを消す
        dup_obj.shape_key_remove(dup_obj.data.shape_keys.key_blocks[0]) # 固定するシェイプキーを消す
        
        separated_objects.append(dup_obj)
        
        select_object(dup_obj, False)
    
    # 元オブジェクトのシェイプキーを全削除
    deselect_all_objects()
    select_object(source_obj, True)
    set_active_object(source_obj)
    bpy.ops.object.shape_key_remove(all=True)
    
    if enable_apply_modifiers:
        apply_modifiers(remove_nonrender=remove_nonrender)
        for obj in separated_objects:
            set_active_object(obj)
            apply_modifiers(remove_nonrender=remove_nonrender)
        set_active_object(source_obj)
    
    # 表示を更新
    update_mesh()
    
    print("Finish Separate ShapeKeys: ["+source_obj.name+"]")
    return separated_objects


def separate_lr_shapekey(soruce_shape_key_index, duplicate, enable_sort):
    obj = get_active_object()
    source_shape_key = obj.data.shape_keys.key_blocks[soruce_shape_key_index]
    
    # print("before: "+source_shape_key.name)
    source_shape_key.name = source_shape_key.name.replace(ENABLE_LR_TAG, '')
    source_shape_key.name = source_shape_key.name.replace(ENABLE_DUPLICATE_TAG, '')
    source_shape_key.name = source_shape_key.name.replace(ENABLE_SORT_TAG, '')
    result_shape_key_name = source_shape_key.name
    # print("after: "+source_shape_key.name)
    
    point = (0,0,0)
    
    # この後で行う選択範囲反転を正常に処理するため、頂点選択だけが有効になるようにしておく
    # temp_mesh_select_mode = bpy.context.tool_settings.mesh_select_mode
    bpy.context.tool_settings.mesh_select_mode = (True, False, False)
    
    # 左
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.shape_key_add(from_mix=False)
    left_shape_index = obj.active_shape_key_index
    left_shape = obj.data.shape_keys.key_blocks[left_shape_index]
    left_shape.name = result_shape_key_name + "_left"
    select_axis_from_point(point=point, mode='NEGATIVE', axis='X')
    # 中心位置を含ませないために選択範囲を反転する
    bpy.ops.mesh.select_all(action='INVERT')
    update_mesh()
    if any([v.select for v in obj.data.vertices]):
        bpy.ops.mesh.blend_from_shape(shape=source_shape_key.name, blend=1, add=False)
    select_axis_from_point(point=point, mode='ALIGNED', axis='X')
    update_mesh()
    if any([v.select for v in obj.data.vertices]):
        # 中心位置はシェイプを0.5でブレンド。
        # これをしないと、leftとright両方を同時に使ったときに中心位置の頂点が二倍動いてしまう
        bpy.ops.mesh.blend_from_shape(shape=source_shape_key.name, blend=0.5, add=False)
    
    # 右
    # 参照する座標の正負が逆なの以外、やってることは左と同じ
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.shape_key_add(from_mix=False)
    right_shape_index = obj.active_shape_key_index
    right_shape = obj.data.shape_keys.key_blocks[right_shape_index]
    right_shape.name = result_shape_key_name + "_right"
    select_axis_from_point(point=point, mode='POSITIVE', axis='X')
    bpy.ops.mesh.select_all(action='INVERT')
    update_mesh()
    if any([v.select for v in obj.data.vertices]):
        print(any([v.select for v in obj.data.vertices]))
        bpy.ops.mesh.blend_from_shape(shape=source_shape_key.name, blend=1, add=False)
    select_axis_from_point(point=point, mode='ALIGNED', axis='X')
    update_mesh()
    if any([v.select for v in obj.data.vertices]):
        bpy.ops.mesh.blend_from_shape(shape=source_shape_key.name, blend=0.5, add=False)
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    if enable_sort:
        # 分割したシェイプキーが分割元シェイプキーのすぐ下に来るように移動
        length=len(obj.data.shape_keys.key_blocks)
        if length*0.5 <= soruce_shape_key_index:
            # print("Bottom to Top")
            obj.active_shape_key_index = left_shape_index
            while soruce_shape_key_index + 1 != obj.active_shape_key_index:
                bpy.ops.object.shape_key_move(type='UP')
            obj.active_shape_key_index = right_shape_index
            while soruce_shape_key_index + 2 != obj.active_shape_key_index:
                bpy.ops.object.shape_key_move(type='UP')
        else:
            # 移動先の位置が上から数えたほうが早いとき
            # print("Top to Bottom")
            obj.active_shape_key_index = left_shape_index
            bpy.ops.object.shape_key_move(type='TOP')
            while soruce_shape_key_index + 1 != obj.active_shape_key_index:
                bpy.ops.object.shape_key_move(type='DOWN')
            obj.active_shape_key_index = right_shape_index
            bpy.ops.object.shape_key_move(type='TOP')
            while soruce_shape_key_index + 2 != obj.active_shape_key_index:
                bpy.ops.object.shape_key_move(type='DOWN')
    
    # 左右分割後のシェイプキーに分割元シェイプキーのvalueをコピー
    left_shape.value = source_shape_key.value
    right_shape.value = source_shape_key.value
    source_shape_key.value = 0
    
    if not duplicate:
        obj.active_shape_key_index = soruce_shape_key_index
        bpy.ops.object.shape_key_remove()
    obj.active_shape_key_index = soruce_shape_key_index


def separate_lr_shapekey_all(duplicate, enable_sort, auto_detect):
    obj = get_active_object()
    print("Create LR Shapekey All: ["+obj.name+"]")
    
    # 頂点を全て表示
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.reveal()
    bpy.ops.object.mode_set(mode='OBJECT')
    
    shape_keys_length=len(obj.data.shape_keys.key_blocks)
    for i in reversed(range(shape_keys_length)):
        if i == 0:
            break
        shapekey = obj.data.shape_keys.key_blocks[i]

        # 名前の最後が_leftまたは_rightのシェイプキーは既に左右分割済みと見なし処理スキップ
        if shapekey.name.endswith("_left") or shapekey.name.endswith("_right"):
            continue
        # auto_detectがTrueなら、名前に"%LR%"を含むときだけ左右分割処理を行う
        if not auto_detect or (auto_detect and shapekey.name.find(ENABLE_LR_TAG) != -1):
            # print("Shapekey: ["+shapekey.name+"] ["+str(shape_keys_length-1-i)+" / "+str(shape_keys_length)+"]")
            print("Shapekey: ["+shapekey.name+"]")
            dup_temp = duplicate
            sort_temp = enable_sort
            if auto_detect:
                # 名前に"%DUP%"を含むなら強制的に複製ON
                if shapekey.name.find(ENABLE_DUPLICATE_TAG) != -1:
                    dup_temp = True
                # 名前に"%SORT%"を含むなら強制的にソートON
                if shapekey.name.find(ENABLE_SORT_TAG) != -1:
                    sort_temp = True
            separate_lr_shapekey(soruce_shape_key_index=i, duplicate=dup_temp, enable_sort=sort_temp)
    
    print("Finish Create LR Shapekey All: ["+obj.name+"]")


# 指定座標を基準にSide of Active
def select_axis_from_point(point=(0,0,0), mode='POSITIVE', axis='X', threshold=0.0001):
    obj = get_active_object()
    if obj.type != 'MESH':
        return
    
    bpy.ops.object.mode_set(mode='EDIT')
    me = obj.data
    bm = bmesh.from_edit_mesh(me)
    
    # 頂点選択を有効化
    temp_select_mode = bm.select_mode
    bm.select_mode = {'VERT'}
    
    bpy.ops.mesh.select_all(action='DESELECT')
    # 一時的に頂点を追加し、それを基準にSide of Activeを使う
    v = bm.verts.new(point)
    select_object(v, True)
    bm.select_history.add(v)
    select_axis(mode=mode, axis=axis, threshold=threshold)
    # 追加した頂点を削除
    bmesh.ops.delete(bm, geom=[v], context='VERTS')
    
    bm.select_mode = temp_select_mode

    bmesh.update_edit_mesh(mesh=me, loop_triangles=False, destructive=True)
    # bpy.ops.object.mode_set(mode='OBJECT')


def update_mesh():
    obj = get_active_object()
    if obj.mode == 'OBJECT':
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.object.mode_set(mode='OBJECT')
    else:
        mode_cache = obj.mode
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode=mode_cache)


# AddonPreferences #
class addon_preferences(bpy.types.AddonPreferences):
    bl_idname = __name__
    
    wait_interval: IntProperty(name="Wait Interval", default=5, min=1, soft_min=1)
    wait_sleep: FloatProperty(name="Wait Sleep", default=0.5, min=0, soft_min=0, max=2, soft_max=2)
    
    def draw(self, context):
        layout = self.layout
        
        layout.prop(self, "wait_interval")
        layout.prop(self, "wait_sleep")


# region Object Operator
class OBJECT_OT_specials_shapekeys_util_apply_modifiers(bpy.types.Operator):
    bl_idname = "object.shapekeys_util_apply_modifiers"
    bl_label = "Apply Modifiers"
    bl_description = bpy.app.translations.pgettext(bl_idname+"_desc")
    bl_options = {'REGISTER', 'UNDO'}
    
    duplicate : BoolProperty(name="Duplicate", default=False, description=bpy.app.translations.pgettext(bl_idname+"_duplicate"))
    remove_nonrender : BoolProperty(name="Remove NonRender", default=True, description=bpy.app.translations.pgettext("remove_nonrender"))
    
    @classmethod
    def poll(cls, context):
        return any(obj.type == 'MESH' for obj in bpy.context.selected_objects)
    
    def execute(self, context):
        active = get_active_object()
        selected_objects = bpy.context.selected_objects
        targets = [d for d in selected_objects if d.type == 'MESH']
        for obj in targets:
            set_active_object(obj)
            b = apply_modifiers_with_shapekeys(self, context.object, self.duplicate, self.remove_nonrender)
            if not b:
                return {'CANCELLED'}
        select_objects(selected_objects, True)
        set_active_object(active)
        return {'FINISHED'}


class OBJECT_OT_specials_shapekeys_util_separateobj(bpy.types.Operator):
    bl_idname = "object.shapekeys_util_separateobj"
    bl_label = "Separate Objects"
    bl_description = bpy.app.translations.pgettext(bl_idname+"_desc")
    bl_options = {'REGISTER', 'UNDO'}
    
    duplicate: BoolProperty(name="Duplicate", default=False, description=bpy.app.translations.pgettext(bl_idname+"_duplicate"))
    apply_modifiers: BoolProperty(name="Apply Modifiers", default=False, description=bpy.app.translations.pgettext(bl_idname+"_apply_modifiers"))
    remove_nonrender: BoolProperty(name="Remove NonRender", default=True, description=bpy.app.translations.pgettext("remove_nonrender"))
    
    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj.type == 'MESH'
    
    def execute(self, context):
        source_obj = context.object
        
        # 実行する必要がなければキャンセル
        if source_obj.data.shape_keys is None or len(source_obj.data.shape_keys.key_blocks)==0:
            return {'CANCELLED'}
        
        deselect_all_objects()
        select_object(source_obj, True)
        set_active_object(source_obj)
        
        # シェイプキーをそれぞれ別オブジェクトにする
        separate_shapekeys(self.duplicate, self.apply_modifiers, self.remove_nonrender)
        
        return {'FINISHED'}


class OBJECT_OT_specials_shapekeys_util_separate_lr_shapekey(bpy.types.Operator):
    bl_idname = "object.shapekeys_util_separate_lr_shapekey"
    bl_label = "Separate Shape Key Left and Right"
    bl_description = bpy.app.translations.pgettext(bl_idname+"_desc")
    bl_options = {'REGISTER', 'UNDO'}
    
    duplicate: BoolProperty(name="Duplicate", default=False, description=bpy.app.translations.pgettext("separate_lr_shapekey_duplicate"))
    enable_sort: BoolProperty(name="Enable Sort", default=True, description=bpy.app.translations.pgettext(bl_idname+"_enable_sort"))
    
    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj.type == 'MESH' and obj.data.shape_keys and len(obj.data.shape_keys.key_blocks) != 0
    
    def execute(self, context):
        obj = context.object
        set_active_object(obj)
        
        # 頂点を全て表示
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.reveal()
        bpy.ops.object.mode_set(mode='OBJECT')
        
        separate_lr_shapekey(soruce_shape_key_index=obj.active_shape_key_index, duplicate=self.duplicate, enable_sort=self.enable_sort)
        return {'FINISHED'}


class OBJECT_OT_specials_shapekeys_util_separate_lr_shapekey_all(bpy.types.Operator):
    bl_idname = "object.shapekeys_util_separate_lr_shapekey_all"
    bl_label = "Separate All Shape Key Left and Right"
    bl_description = bpy.app.translations.pgettext(bl_idname+"_desc")
    bl_options = {'REGISTER', 'UNDO'}
    
    duplicate: BoolProperty(name="Duplicate", default=False, description=bpy.app.translations.pgettext("separate_lr_shapekey_duplicate"))
    enable_sort: BoolProperty(name="Enable Sort", default=False, description=bpy.app.translations.pgettext("separate_lr_shapekey_all_enable_sort"))
    
    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj.type == 'MESH' and obj.data.shape_keys and len(obj.data.shape_keys.key_blocks) != 0
    
    def execute(self, context):
        obj = context.object
        set_active_object(obj)
        separate_lr_shapekey_all(duplicate=self.duplicate, enable_sort=self.enable_sort, auto_detect=False)
        return {'FINISHED'}


class OBJECT_OT_specials_shapekeys_util_separate_lr_shapekey_all_tagdetect(bpy.types.Operator):
    bl_idname = "object.shapekeys_util_separate_lr_shapekey_all_tagdetect"
    bl_label = "(Tag) Separate All Shape Key Left and Right"
    bl_description = bpy.app.translations.pgettext(bl_idname+"_desc")
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj.type == 'MESH' and obj.data.shape_keys and len(obj.data.shape_keys.key_blocks) != 0

    def execute(self, context):
        obj = context.object
        set_active_object(obj)
        separate_lr_shapekey_all(duplicate=False, enable_sort=False, auto_detect=True)
        return {'FINISHED'}


class OBJECT_OT_specials_shapekeys_util_assign_lr_shapekey_tag(bpy.types.Operator):
    bl_idname = "object.shapekeys_util_assign_lr_shapekey_tag"
    bl_label = "Assign Tag"
    bl_description = bpy.app.translations.pgettext(bl_idname+"_desc")
    bl_options = {'REGISTER', 'UNDO'}
    
    enable: BoolProperty(name="Enable", description=bpy.app.translations.pgettext(bl_idname+"_enable"))
    duplicate: BoolProperty(name="Duplicate", description=bpy.app.translations.pgettext("separate_lr_shapekey_duplicate"))
    enable_sort: BoolProperty(name="Enable Sort", description=bpy.app.translations.pgettext("separate_lr_shapekey_all_enable_sort"))
    
    target_name = ""
    target_shape_name = ""
    
    @classmethod
    def poll(cls, context):
        obj = context.object
        
        b = (obj.type == 'MESH' and obj.data.shape_keys and obj.active_shape_key_index != 0)
        if b:
            shapekey = obj.data.shape_keys.key_blocks[obj.active_shape_key_index]
            # 名前の最後が_leftまたは_rightのシェイプキーには使えないように
            if shapekey.name.endswith("_left") or shapekey.name.endswith("_right"):
                b=False
        
        return b
    
    def invoke(self, context, event):
        obj = context.object
        shapekey = obj.data.shape_keys.key_blocks[obj.active_shape_key_index]
        self.target_name = obj.name
        self.target_shape_name = shapekey.name
        
        self.enable = shapekey.name.find(ENABLE_LR_TAG) != -1
        self.duplicate = shapekey.name.find(ENABLE_DUPLICATE_TAG) != -1
        self.enable_sort = shapekey.name.find(ENABLE_SORT_TAG) != -1
        return self.execute(context)
    
    def draw(self, context):
        layout = self.layout
        layout.label(text="Target: "+self.target_name)
        layout.label(text="Shape: "+self.target_shape_name)
        layout.prop(self, "enable")
        col = layout.column()
        col.enabled = self.enable
        col.prop(self, "duplicate")
        col.prop(self, "enable_sort")
    
    def execute(self, context):
        obj = context.object
        shapekey = obj.data.shape_keys.key_blocks[obj.active_shape_key_index]
        
        if self.enable:
            if shapekey.name.find(ENABLE_LR_TAG) == -1:
                shapekey.name += ENABLE_LR_TAG
        else:
            shapekey.name=shapekey.name.replace(ENABLE_LR_TAG, '')
        
        if self.enable and self.duplicate:
            if shapekey.name.find(ENABLE_DUPLICATE_TAG) == -1:
                shapekey.name += ENABLE_DUPLICATE_TAG
        else:
            shapekey.name = shapekey.name.replace(ENABLE_DUPLICATE_TAG, '')
        
        if self.enable and self.enable_sort:
            if shapekey.name.find(ENABLE_SORT_TAG) == -1:
                shapekey.name += ENABLE_SORT_TAG
        else:
            shapekey.name=shapekey.name.replace(ENABLE_SORT_TAG, '')
        
        return {'FINISHED'}
# endregion


# Mesh Operator #
class MESH_OT_specials_shapekeys_util_sideofactive_point(bpy.types.Operator):
    bl_idname = "edit_mesh.shapekeys_util_sideofactive_point"
    bl_label = "Side of Active from Point"
    bl_description = "指定座標を基準にSide of active"
    bl_options = {'REGISTER', 'UNDO'}
    
    point: FloatVectorProperty(name="Point")
    
    mode: EnumProperty(
        name="Axis Mode",
        default='NEGATIVE',
        items=(
            ('POSITIVE', "Positive Axis", ""),
            ('NEGATIVE', "Negative Axis", ""),
            ('ALIGNED', "Aligned Axis", ""),
        )
    )
    
    axis: EnumProperty(
        name="Axis",
        default='X',
        items=(
            ('X', "X", ""),
            ('Y', "Y", ""),
            ('Z', "Z", ""),
        )
    )
    
    threshold: FloatProperty(
        name="Threshold",
        min=0.000001, max=50.0,
        soft_min=0.00001, soft_max=10.0,
        default=0.0001,
    )
    
    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj.type == 'MESH'
    
    def execute(self, context):
        select_axis_from_point(self.point, self.mode, self.axis, self.threshold)
        
        return {'FINISHED'}

# Init Menu #


# エディットモード　Special → ShapeKeys Util を登録する
def INFO_MT_edit_mesh_specials_shapekeys_util_menu(self, context):
    self.layout.menu(VIEW3D_MT_edit_mesh_specials_shapekeys_util.bl_idname)


# オブジェクトモード　Special → ShapeKeys Util を登録する
def INFO_MT_object_specials_shapekeys_util_menu(self, context):
    self.layout.menu(VIEW3D_MT_object_specials_shapekeys_util.bl_idname)


# エディットモード　Special → ShapeKeys Util にコマンドを登録するクラス
class VIEW3D_MT_edit_mesh_specials_shapekeys_util(bpy.types.Menu):
    bl_label = "ShapeKeys Util"
    bl_idname = "INFO_MT_edit_mesh_specials_shapekeys_util_menu"
    
    def draw(self, context):
        self.layout.operator(MESH_OT_specials_shapekeys_util_sideofactive_point.bl_idname)


# オブジェクトモード　Special → ShapeKeys Util にコマンドを登録するクラス
class VIEW3D_MT_object_specials_shapekeys_util(bpy.types.Menu):
    bl_label = "ShapeKeys Util"
    bl_idname = "VIEW3D_MT_object_specials_shapekeys_util"
    
    def draw(self, context):
        layout = self.layout
        layout.operator(OBJECT_OT_specials_shapekeys_util_apply_modifiers.bl_idname)
        layout.operator(OBJECT_OT_specials_shapekeys_util_separateobj.bl_idname)
        layout.separator()
        layout.operator(OBJECT_OT_specials_shapekeys_util_separate_lr_shapekey.bl_idname)
        layout.operator(OBJECT_OT_specials_shapekeys_util_separate_lr_shapekey_all.bl_idname)
        layout.operator(OBJECT_OT_specials_shapekeys_util_separate_lr_shapekey_all_tagdetect.bl_idname)
        layout.operator(OBJECT_OT_specials_shapekeys_util_assign_lr_shapekey_tag.bl_idname)

# Init #
classes = [
    VIEW3D_MT_object_specials_shapekeys_util,
    VIEW3D_MT_edit_mesh_specials_shapekeys_util,
    
    OBJECT_OT_specials_shapekeys_util_apply_modifiers,
    OBJECT_OT_specials_shapekeys_util_separateobj,
    OBJECT_OT_specials_shapekeys_util_separate_lr_shapekey,
    OBJECT_OT_specials_shapekeys_util_separate_lr_shapekey_all,
    OBJECT_OT_specials_shapekeys_util_separate_lr_shapekey_all_tagdetect,
    OBJECT_OT_specials_shapekeys_util_assign_lr_shapekey_tag,
    
    MESH_OT_specials_shapekeys_util_sideofactive_point,
    
    addon_preferences,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.app.translations.register(__name__, translations_dict)

    bpy.types.VIEW3D_MT_object_context_menu.append(INFO_MT_object_specials_shapekeys_util_menu)
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.append(INFO_MT_edit_mesh_specials_shapekeys_util_menu)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    bpy.app.translations.unregister(__name__)

    bpy.types.VIEW3D_MT_object_context_menu.remove(INFO_MT_object_specials_shapekeys_util_menu)
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.remove(INFO_MT_edit_mesh_specials_shapekeys_util_menu)

if __name__ == "__main__":
    register()