import bpy

from .. import func_separate_shapekeys
from ..utils import func_object_utils


def apply_each_shapekey_modifiers(source_obj, remove_nonrender, use_update_mesh_deform_addon):
    # シェイプキーをそれぞれ別オブジェクトにしてモディファイア適用
    separated_objects = func_separate_shapekeys.separate_shapekeys(
        duplicate=False,
        enable_apply_modifiers=True,
        remove_nonrender=remove_nonrender,
        keep_original_shapekeys=False,
        use_update_mesh_deform_addon=use_update_mesh_deform_addon
    )

    print("Source: " + source_obj.name)
    print("------ Merge Separated Objects ------\n" + '\n'.join(
        [obj.name for obj in separated_objects]) + "\n----------------------------------")

    prev_obj_name = source_obj.name
    prev_vert_count = len(source_obj.data.vertices)

    func_object_utils.select_object(source_obj, True)
    func_object_utils.set_active_object(source_obj)
    # 分けたオブジェクトを1つずつjoin_shapesしていく
    shape_objects = []
    for obj in separated_objects:
        # 前回のシェイプキーと頂点数が違ったら警告して処理を取り消し
        vert_count = len(obj.data.vertices)
        print(f"current: [{obj.name}]({vert_count})   prev: [{prev_obj_name}]({prev_vert_count})")
        if vert_count != prev_vert_count:
            warn = bpy.app.translations.pgettext("mizore_error_apply_mod_with_shapekey_verts_count_difference").format(
                obj_1 = prev_obj_name, 
                obj_verts_1 = prev_vert_count,
                obj_2 = obj.name, 
                obj_verts_2 = vert_count
                )
            print("!!!!! " + warn + "!!!!!")
            raise Exception(warn)

        prev_vert_count = vert_count
        prev_obj_name = obj.name

        # 一気にjoin_shapesするとシェイプキーの順番がおかしくなるので1つずつ
        # Armatureによる変形を無効化
        for modifier in obj.modifiers:
            if modifier.type == 'ARMATURE':
                modifier.show_viewport = False
                modifier.show_render = False
        func_object_utils.select_object(obj, True)
        print(f"Join: [{obj.name}]({vert_count}) -> [{source_obj.name}]({len(source_obj.data.vertices)})")
        bpy.ops.object.join_shapes()
        func_object_utils.select_object(obj, False)

        shape_objects.append(obj)

    # オブジェクト削除前にシェイプキーの参照を正規化（無効参照によるエラーを防止）
    if source_obj.data.shape_keys:
        for shapekey in source_obj.data.shape_keys.key_blocks:
            if shapekey.relative_key and shapekey.relative_key.name not in source_obj.data.shape_keys.key_blocks:
                # 削除予定オブジェクトへの参照がある場合はBasisに変更
                shapekey.relative_key = source_obj.data.shape_keys.key_blocks[0]

    # 使い終わったオブジェクトを削除
    func_object_utils.select_object(source_obj, False)
    func_object_utils.remove_objects(shape_objects)
