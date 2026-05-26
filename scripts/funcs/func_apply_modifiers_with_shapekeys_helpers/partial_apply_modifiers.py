import time

import bpy

from ..utils import func_object_utils


def _get_shape_key_count(obj) -> int:
    shape_keys = getattr(getattr(obj, "data", None), "shape_keys", None)
    if not shape_keys:
        return 0
    return len(shape_keys.key_blocks)


def partial_apply_modifiers(source_obj, modifier_index, remove_nonrender: bool, use_update_mesh_deform_addon: bool, skip_modifier_types: set):
    start_time = time.perf_counter()
    phase_start = start_time
    target_modifier = source_obj.modifiers[modifier_index]
    print(
        f"[partial_apply_modifiers] start: "
        f"object={source_obj.name} "
        f"target_index={modifier_index} "
        f"target_modifier={target_modifier.name} "
        f"modifiers={len(source_obj.modifiers)} "
        f"shapekeys={_get_shape_key_count(source_obj)}"
    )
    # 2番目以降にmodifier_index用のモディファイアがあったら
    # 一時オブジェクトを作成
    print("create tempobj")
    tempobj = func_object_utils.duplicate_object(source_obj)
    func_object_utils.deselect_all_objects()
    func_object_utils.select_object(source_obj, True)
    func_object_utils.select_object(tempobj, True)
    func_object_utils.set_active_object(source_obj)
    print("duplicate: " + tempobj.name)
    print(f"[partial_apply_modifiers] create_tempobj: {time.perf_counter() - phase_start:.3f}s")
    phase_start = time.perf_counter()

    # modifier_indexとそれよりあとのモディファイアを削除
    for modifier in source_obj.modifiers[modifier_index:]:
        bpy.ops.object.modifier_remove(modifier=modifier.name)
    print(
        f"[partial_apply_modifiers] trimmed_stack: "
        f"object={source_obj.name} "
        f"remaining_modifiers={len(source_obj.modifiers)} "
        f"shapekeys={_get_shape_key_count(source_obj)}"
    )

    # 関数を再実行し、modifier_indexより前のモディファイアを適用
    print("re-execute apply_modifiers_with_shapekeys (1)")
    from ..func_apply_modifiers_with_shapekeys import apply_modifiers_with_shapekeys
    apply_modifiers_with_shapekeys(
        remove_nonrender=remove_nonrender,
        use_update_mesh_deform_addon=use_update_mesh_deform_addon,
        skip_modifier_types=skip_modifier_types)
    print(f"[partial_apply_modifiers] first_apply: {time.perf_counter() - phase_start:.3f}s")
    phase_start = time.perf_counter()

    # 削除していたモディファイアを一時オブジェクトから復元
    print("restore modifiers")
    func_object_utils.replace_modifiers(source_obj, tempobj)
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
    print(
        f"[partial_apply_modifiers] restored_stack: "
        f"object={source_obj.name} "
        f"modifiers={len(source_obj.modifiers)} "
        f"shapekeys={_get_shape_key_count(source_obj)}"
    )
    phase_start = time.perf_counter()

    # 関数を再実行して終了
    print("re-execute apply_modifiers_with_shapekeys (2)")
    from ..func_apply_modifiers_with_shapekeys import apply_modifiers_with_shapekeys
    apply_modifiers_with_shapekeys(
        remove_nonrender=remove_nonrender,
        use_update_mesh_deform_addon=use_update_mesh_deform_addon,
        skip_modifier_types=skip_modifier_types)
    print(f"[partial_apply_modifiers] second_apply: {time.perf_counter() - phase_start:.3f}s")
    print(f"[partial_apply_modifiers] total: {time.perf_counter() - start_time:.3f}s")
