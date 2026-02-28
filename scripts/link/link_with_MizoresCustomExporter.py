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

from .. import consts
from ..funcs.func_apply_modifiers_with_shapekeys import (
    apply_modifiers_with_shapekeys,
    apply_modifiers_with_shapekeys_iter,
)
from ..funcs.func_change_base_shapekey import change_base_shapekeys_iter
from ..funcs.func_reorder_shapekeys import reorder_shapekeys_iter
from ..funcs.func_separate_lr_shapekey_all import (
    separate_lr_shapekey_all,
    separate_lr_shapekey_all_iter,
)
from ..funcs.func_subtract_base_shapekey import subtract_base_shapekey_all


def get_apply_modifiers_iter_for_exporter(skip_modifier_types: set, remove_nonrender=False, use_update_mesh_deform_addon=False):
    """MizoresCustomExporter連携用のモディファイア適用ジェネレータを取得

    Args:
        remove_nonrender: レンダリング無効モディファイアを削除するか
        use_update_mesh_deform_addon: MeshDeformアドオン連携を使用するか
        skip_modifier_types: スキップするモディファイアタイプのセット

    Returns:
        Generator: モディファイア適用処理のジェネレータ
    """
    print(f"ShapekeysUtil - Apply Modifiers With Shapekeys (iter) skip_modifier_types={skip_modifier_types}")
    return apply_modifiers_with_shapekeys_iter(
        remove_nonrender=remove_nonrender,
        use_update_mesh_deform_addon=use_update_mesh_deform_addon,
        skip_modifier_types=skip_modifier_types
    )


def get_separate_lr_iter_for_exporter():
    """MizoresCustomExporter連携用の左右分割ジェネレータを取得

    Returns:
        Generator: 左右分割処理のジェネレータ
    """
    print("ShapekeysUtil - Separate LR Shapekeys (iter)")
    return separate_lr_shapekey_all_iter(
        duplicate=False,
        enable_sort=False,
        auto_detect=True
    )


def get_change_base_iter_for_exporter(objects_with_settings):
    """MizoresCustomExporter連携用のベース変更ジェネレータを取得

    Args:
        objects_with_settings: [(obj, [(source_name, reverse_name), ...]), ...]

    Returns:
        Generator: ベース変更処理のジェネレータ
    """
    print("ShapekeysUtil - Change Base Shapekeys (iter)")
    return change_base_shapekeys_iter(objects_with_settings)


def get_reorder_iter_for_exporter(objects_with_settings):
    """MizoresCustomExporter連携用の並び替えジェネレータを取得

    Args:
        objects_with_settings: [(obj, [{'type': ..., 'target': ..., ...}, ...]), ...]

    Returns:
        Generator: 並び替え処理のジェネレータ
    """
    print("ShapekeysUtil - Reorder Shapekeys (iter)")
    return reorder_shapekeys_iter(objects_with_settings)


# MizoresCustomExporter連携用（同期版エクスポートフローで使用中）
class OBJECT_OT_apply_modifiers_for_mizores_custom_exporter_addon(bpy.types.Operator):
    bl_idname = "object.shapekeys_util_apply_mod_for_exporter_addon"
    bl_label = "[Internal] Apply Modifiers With Shapekeys For MizoresCustomExporter Addon"
    bl_options = {'REGISTER', 'UNDO'}

    use_update_mesh_deform_addon: bpy.props.BoolProperty(
        name="Use Update Mesh Deform Addon",
        default=False,
        description="Use MeshDeformUtils Addon"
    )

    skip_modifier_types_str: bpy.props.StringProperty(
        name="Skip Modifier Types"
    )

    def execute(self, context):
        # カンマ区切りの文字列からスキップ対象モディファイアタイプのセットをパース
        skip_types = consts.parse_skip_modifier_types_str(self.skip_modifier_types_str)
        print(f"ShapekeysUtil - Apply Modifiers With Shapekeys (skip_types={skip_types})")
        apply_modifiers_with_shapekeys(
            remove_nonrender=False,
            use_update_mesh_deform_addon=self.use_update_mesh_deform_addon,
            skip_modifier_types=skip_types)
        return {'FINISHED'}


class OBJECT_OT_separate_lr_shapekey_for_mizores_custom_exporter_addon(bpy.types.Operator):
    bl_idname = "object.shapekeys_util_separate_lr_shapekey_for_exporter"
    bl_label = "[Internal] Separate All Shape Key Left and Right For MizoresCustomExporter Addon"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        print("ShapekeysUtil - Separate LR Shapekeys")
        separate_lr_shapekey_all(duplicate=False, enable_sort=False, auto_detect=True)
        return {'FINISHED'}


class OBJECT_OT_subtract_base_shapekey_for_mizores_custom_exporter_addon(bpy.types.Operator):
    bl_idname = "object.shapekeys_util_subtract_base_shapekey_for_exporter"
    bl_label = "[Internal] Subtract Base Shapekey For MizoresCustomExporter Addon"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        print("ShapekeysUtil - Subtract Base Shapekeys")
        subtract_base_shapekey_all()
        return {'FINISHED'}


classes = [
    OBJECT_OT_apply_modifiers_for_mizores_custom_exporter_addon,
    OBJECT_OT_separate_lr_shapekey_for_mizores_custom_exporter_addon,
    OBJECT_OT_subtract_base_shapekey_for_mizores_custom_exporter_addon,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    # ジェネレータ取得関数をWindowManagerに登録
    bpy.types.WindowManager.shapekeys_util_get_apply_modifiers_iter = get_apply_modifiers_iter_for_exporter
    bpy.types.WindowManager.shapekeys_util_get_separate_lr_iter = get_separate_lr_iter_for_exporter
    bpy.types.WindowManager.shapekeys_util_get_change_base_iter = get_change_base_iter_for_exporter
    bpy.types.WindowManager.shapekeys_util_get_reorder_iter = get_reorder_iter_for_exporter


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    if hasattr(bpy.types.WindowManager, 'shapekeys_util_get_apply_modifiers_iter'):
        del bpy.types.WindowManager.shapekeys_util_get_apply_modifiers_iter
    if hasattr(bpy.types.WindowManager, 'shapekeys_util_get_separate_lr_iter'):
        del bpy.types.WindowManager.shapekeys_util_get_separate_lr_iter
    if hasattr(bpy.types.WindowManager, 'shapekeys_util_get_change_base_iter'):
        del bpy.types.WindowManager.shapekeys_util_get_change_base_iter
    if hasattr(bpy.types.WindowManager, 'shapekeys_util_get_reorder_iter'):
        del bpy.types.WindowManager.shapekeys_util_get_reorder_iter

