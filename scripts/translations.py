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

translations_dict = {
    "en_US": {
        ("*", "mizore_error_apply_mod_with_shapekey_verts_count_difference"): "Apply Modifier with Shapekey: Could not execute the process because the number of vertices of the shape key is different.\n"
        "It may be because the number of vertices is changed by Boolean or Merge of the Mirror modifier.\n{obj_1} (verts: {obj_verts_1}), {obj_2} (verts: {obj_verts_2})",

        ("*", "mizore_error_apply_as_shapekey_invalid_modifier"): "Apply As Shape: Could not execute the process because the modifier type is not supported or the settings are invalid.\nObject: {obj_name}\nModifier: {modifier_name}({modifier_type})",

        # Progress messages - separate_shapekeys
        ("*", "sku_progress_initializing"): "Initializing: {obj}",
        ("*", "sku_progress_separating"): "Separating: {shapekey} ({current}/{total})",
        ("*", "sku_progress_cleanup_shapekeys"): "Cleaning up shapekeys",
        ("*", "sku_progress_apply_modifiers"): "Apply Modifiers: {obj} ({current}/{total})",
        ("*", "sku_progress_complete"): "Complete: {obj}",

        # Progress messages - apply_modifiers_with_shapekeys
        ("*", "sku_progress_processing"): "Processing: {obj}",
        ("*", "sku_progress_apply_as_shape"): "Apply as shape: {modifier}",
        ("*", "sku_progress_partial_apply"): "Partial apply: {obj}",
        ("*", "sku_progress_removing_basis"): "Removing basis: {obj}",
        ("*", "sku_progress_apply_modifiers_no_shapekeys"): "Apply modifiers (no shapekeys): {obj}",
        ("*", "sku_progress_surface_deform"): "Surface deform: {obj}",
        ("*", "sku_progress_partial_apply_surface_deform"): "Partial apply (surface deform): {obj}",
        ("*", "sku_progress_apply_each_shapekey"): "Apply each shapekey modifiers: {obj}",
        ("*", "sku_progress_restoring_shapekeys"): "Restoring shapekey names: {obj}",
    },
    "ja_JP": {
        ("*", "mizore_error_apply_mod_with_shapekey_verts_count_difference"):
            "Apply Modifier with Shapekey: シェイプキーの頂点数が異なっているため処理を実行できませんでした。\n"
            "ブーリアンやミラーモディファイアの\"結合\"で頂点数が変化しているなどの原因が考えられます。\n{obj_1} (頂点数: {obj_verts_1}), {obj_2} (頂点数: {obj_verts_2})",

        ("*", "mizore_error_apply_as_shapekey_invalid_modifier"): "Apply As Shape: モディファイアの種類が非対応または設定内容が不適切なため、処理を実行できませんでした。\nオブジェクト: {obj_name}\nモディファイア: {modifier_name} ({modifier_type})",

        # Progress messages - separate_shapekeys
        ("*", "sku_progress_initializing"): "初期化中: {obj}",
        ("*", "sku_progress_separating"): "分割中: {shapekey} ({current}/{total})",
        ("*", "sku_progress_cleanup_shapekeys"): "シェイプキー整理中",
        ("*", "sku_progress_apply_modifiers"): "モディファイア適用中: {obj} ({current}/{total})",
        ("*", "sku_progress_complete"): "完了: {obj}",

        # Progress messages - apply_modifiers_with_shapekeys
        ("*", "sku_progress_processing"): "処理中: {obj}",
        ("*", "sku_progress_apply_as_shape"): "シェイプとして適用: {modifier}",
        ("*", "sku_progress_partial_apply"): "部分適用: {obj}",
        ("*", "sku_progress_removing_basis"): "Basis削除中: {obj}",
        ("*", "sku_progress_apply_modifiers_no_shapekeys"): "モディファイア適用 (シェイプキーなし): {obj}",
        ("*", "sku_progress_surface_deform"): "Surface Deform処理: {obj}",
        ("*", "sku_progress_partial_apply_surface_deform"): "部分適用 (Surface Deform): {obj}",
        ("*", "sku_progress_apply_each_shapekey"): "各シェイプキーにモディファイア適用中: {obj}",
        ("*", "sku_progress_restoring_shapekeys"): "シェイプキー名復元中: {obj}",
    },
}


def register():
    bpy.app.translations.register(__name__, translations_dict)


def unregister():
    bpy.app.translations.unregister(__name__)