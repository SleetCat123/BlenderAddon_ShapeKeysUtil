import time

import bpy

from ..utils import func_object_utils


def partial_apply_modifiers(source_obj, modifier_index, remove_nonrender: bool, use_update_mesh_deform_addon: bool):
    start_time = time.perf_counter()
    phase_start = start_time
    print("func_apply_modifiers_with_shapekeys - partial_apply_modifiers")
    # 2番目以降にmodifier_index用のモディファイアがあったら
    # 一時オブジェクトを作成
    print("create tempobj")
    tempobj = func_object_utils.duplicate_object(source_obj)
    func_object_utils.deselect_all_objects()
    func_object_utils.select_object(tempobj, True)
    print("duplicate: " + tempobj.name)
    func_object_utils.set_active_object(source_obj)
    # モディファイアを一時オブジェクトにコピー
    print("copyto temp: make_links_data(type='MODIFIERS')")
    bpy.ops.object.make_links_data(type='MODIFIERS')
    print(f"[partial_apply_modifiers] create_tempobj: {time.perf_counter() - phase_start:.3f}s")
    phase_start = time.perf_counter()

    # modifier_indexとそれよりあとのモディファイアを削除
    for modifier in source_obj.modifiers[modifier_index:]:
        bpy.ops.object.modifier_remove(modifier=modifier.name)

    # 関数を再実行し、modifier_indexより前のモディファイアを適用
    print("re-execute apply_modifiers_with_shapekeys (1)")
    from ..func_apply_modifiers_with_shapekeys import apply_modifiers_with_shapekeys
    apply_modifiers_with_shapekeys(
        remove_nonrender=remove_nonrender,
        use_update_mesh_deform_addon=use_update_mesh_deform_addon)
    print(f"[partial_apply_modifiers] first_apply: {time.perf_counter() - phase_start:.3f}s")
    phase_start = time.perf_counter()

    # 削除していたモディファイアを一時オブジェクトから復元
    print("restore modifiers")
    func_object_utils.deselect_all_objects()
    func_object_utils.select_object(source_obj, True)
    func_object_utils.set_active_object(tempobj)
    print("restore: make_links_data(type='MODIFIERS')")
    bpy.ops.object.make_links_data(type='MODIFIERS')
    print("temp: " + str(tempobj))
    print("source: " + str(source_obj))
    func_object_utils.set_active_object(source_obj)
    # 適用済みのモディファイアを削除。これでモディファイアの1番目がmodifier_index用のモディファイアになる
    for modifier in source_obj.modifiers[:modifier_index]:
        bpy.ops.object.modifier_remove(modifier=modifier.name)

    # 一時オブジェクトを削除
    print("remove tempobj")
    func_object_utils.remove_object(tempobj)
    func_object_utils.select_object(source_obj, True)
    func_object_utils.set_active_object(source_obj)
    print(f"[partial_apply_modifiers] restore_cleanup: {time.perf_counter() - phase_start:.3f}s")
    phase_start = time.perf_counter()

    # 関数を再実行して終了
    print("re-execute apply_modifiers_with_shapekeys (2)")
    from ..func_apply_modifiers_with_shapekeys import apply_modifiers_with_shapekeys
    apply_modifiers_with_shapekeys(
        remove_nonrender=remove_nonrender,
        use_update_mesh_deform_addon=use_update_mesh_deform_addon)
    print(f"[partial_apply_modifiers] second_apply: {time.perf_counter() - phase_start:.3f}s")
    print(f"[partial_apply_modifiers] total: {time.perf_counter() - start_time:.3f}s")