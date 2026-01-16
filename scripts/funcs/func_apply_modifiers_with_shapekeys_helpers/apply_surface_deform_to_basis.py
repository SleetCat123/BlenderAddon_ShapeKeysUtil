import time

import bpy

from ..utils import func_object_utils


def _apply_surface_deform_to_basis_core(source_obj, modifier, use_update_mesh_deform_addon):
    """
    SurfaceDeformモディファイアをBasisシェイプキーに適用するコア処理
    再帰呼び出しを行わない純粋な単一モディファイア処理
    """
    start_time = time.perf_counter()
    print("_apply_surface_deform_to_basis_core - core processing")
    if use_update_mesh_deform_addon:
        from .. import func_update_mesh_deform_addon
        func_update_mesh_deform_addon.update_mesh_deform_addon(
            obj=source_obj, 
            modifier=modifier, 
            use_update_mesh_deform_addon=use_update_mesh_deform_addon)

    # オブジェクトを複製
    temp_obj = func_object_utils.duplicate_object(source_obj)
    func_object_utils.deselect_all_objects()
    func_object_utils.select_object(temp_obj, True)
    func_object_utils.set_active_object(temp_obj)

    # 複製したオブジェクトのシェイプキーをすべて削除
    temp_obj.active_shape_key_index = 0
    bpy.ops.object.shape_key_remove(all=True, apply_mix=False)
    # 複製したオブジェクトのSurfaceDeformモディファイアを適用
    bpy.ops.object.modifier_apply(modifier=temp_obj.modifiers[0].name)

    temp_active_shape_key_index = source_obj.active_shape_key_index
    
    # 複製したオブジェクトから元オブジェクトにJoin as shape
    func_object_utils.select_object(source_obj, True)
    func_object_utils.set_active_object(source_obj)
    bpy.ops.object.join_shapes()
    # 複製したオブジェクトを削除
    func_object_utils.remove_object(temp_obj)

    # join as shapeしたシェイプキーをBasisに転送
    last_shapekey_index = len(source_obj.data.shape_keys.key_blocks) - 1
    temp_mode = source_obj.mode
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.reveal()
    bpy.ops.mesh.select_all(action='SELECT')
    last_shapekey_name = source_obj.data.shape_keys.key_blocks[last_shapekey_index].name
    # Basisをアクティブにする
    source_obj.active_shape_key_index = 0
    bpy.ops.mesh.blend_from_shape(shape=last_shapekey_name, blend=1)
    source_obj.active_shape_key_index = temp_active_shape_key_index

    # join as shapeしたシェイプキーを削除
    bpy.ops.object.mode_set(mode='OBJECT')
    source_obj.active_shape_key_index = last_shapekey_index
    bpy.ops.object.shape_key_remove()

    if temp_mode != 'OBJECT':
        # 元のモードに戻す
        bpy.ops.object.mode_set(mode=temp_mode)

    # 元オブジェクトのSurfaceDeformモディファイアを削除
    bpy.ops.object.modifier_remove(modifier=source_obj.modifiers[0].name)
    print(f"[_apply_surface_deform_to_basis_core] total: {time.perf_counter() - start_time:.3f}s")

def apply_surface_deform_to_basis(source_obj, modifier, use_update_mesh_deform_addon, remove_nonrender=True):
    """
    SurfaceDeformモディファイアをBasisシェイプキーに適用し、その後全モディファイアを再帰的に処理
    既存機能との互換性を維持
    """
    start_time = time.perf_counter()
    print("func_apply_modifiers_with_shapekeys - apply_surface_deform_to_basis")

    # コア処理を実行
    _apply_surface_deform_to_basis_core(source_obj, modifier, use_update_mesh_deform_addon)
    print(f"[apply_surface_deform_to_basis] core: {time.perf_counter() - start_time:.3f}s")

    # 関数を再実行して終了
    from ..func_apply_modifiers_with_shapekeys import apply_modifiers_with_shapekeys
    apply_modifiers_with_shapekeys(
        remove_nonrender=remove_nonrender,
        use_update_mesh_deform_addon=use_update_mesh_deform_addon)
    print(f"[apply_surface_deform_to_basis] total: {time.perf_counter() - start_time:.3f}s")

def apply_single_surface_deform_to_basis(source_obj, modifier, use_update_mesh_deform_addon, remove_nonrender=False):
    """
    SurfaceDeformモディファイアをBasisシェイプキーに適用（単一モディファイア用）
    再帰処理を行わず、指定されたモディファイアのみを処理
    """
    print("apply_single_surface_deform_to_basis - single modifier processing")
    
    # コア処理を実行（再帰呼び出しなし）
    _apply_surface_deform_to_basis_core(source_obj, modifier, use_update_mesh_deform_addon)
