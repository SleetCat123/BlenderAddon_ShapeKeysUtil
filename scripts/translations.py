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


def register():
    bpy.app.translations.register(__package__, translations_dict)


def unregister():
    bpy.app.translations.unregister(__package__)
