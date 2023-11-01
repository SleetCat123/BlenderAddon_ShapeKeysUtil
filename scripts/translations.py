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
from . import consts
from .funcs.utils import func_package_utils
from .consts import DESC
from .ops.op_separate_lr_shapekey import OBJECT_OT_specials_shapekeys_util_separate_lr_shapekey as separate_lr_shapekey
from .ops.op_assign_lr_shapekey_tag import OBJECT_OT_specials_shapekeys_util_assign_lr_shapekey_tag as assign_lr_shapekey_tag
from .ops.op_separate_lr_shapekey_all import OBJECT_OT_specials_shapekeys_util_separate_lr_shapekey_all as separate_lr_shapekey_all
from .ops.op_separate_lr_shapekey_all_tag_detect import (
    OBJECT_OT_specials_shapekeys_util_separate_lr_shapekey_all_tag_detect as separate_lr_shapekey_all_tag_detect
)
from .ops.op_apply_modifiers import OBJECT_OT_specials_shapekeys_util_apply_modifiers as apply_modifiers
from .ops.op_separate_shapekeys import OBJECT_OT_specials_shapekeys_util_shapekeys_to_objects as shapekeys_to_objects
from .ops.op_sideofactive_point import MESH_OT_specials_shapekeys_util_sideofactive_point as sideofactive_point


translations_dict = {
    "en_US": {
        ("*", separate_lr_shapekey_all_tag_detect.bl_idname + DESC):
            "See \"Read-me.txt\"\nCan't use if a shape key name ends with \"_left\" or \"_right\"",

        # apply_modifiers
        ("*", apply_modifiers.bl_idname + consts.DESC):
            "Apply all modifiers except for Armature.\nCan use even if has a shape key.\nWarning: It may take a while",
        ("*", apply_modifiers.bl_idname + "duplicate"): "Execute the function on the copied object",
        ("*", apply_modifiers.bl_idname + "remove_nonrender"): "A non-render modifier will be removed.",

        # separate_lr_shapekey
        ("*", separate_lr_shapekey.bl_idname + DESC):
            "A selected shape key separate left and right based on object origin.",
        ("*", separate_lr_shapekey.bl_idname + "duplicate"): "Execute the function on the copied shape key",
        ("*", separate_lr_shapekey.bl_idname + "enable_sort"): "Result shape keys move to below target shape key",

        # separate_lr_shapekey_all
        ("*", separate_lr_shapekey_all.bl_idname + DESC):
            "All shape key separate left and right based on object origin.\n"
            "Separation is skipping if a shape key name ends with \"_left\" or \"_right\"",
        ("*", separate_lr_shapekey_all.bl_idname + "duplicate"):
            "Keep the shape key before the left-right split.\n"
            "Note: Using the shape keys before and after the left-right split at the same time,\n"
            " may result in an unintended appearance of the model."
            " (because the shape key is doubly applied)",
        ("*", separate_lr_shapekey_all.bl_idname + "enable_sort"):
            "Result shape keys move to below target shape key.\nWarning: It may take a while",

        # shapekeys_to_objects
        ("*", shapekeys_to_objects.bl_idname + DESC):
            "Separate objects for each shape keys.\nWarning: It may take a while",
        ("*", shapekeys_to_objects.bl_idname + "duplicate"): "Execute the function on the copied object",
        ("*", shapekeys_to_objects.bl_idname + "apply_modifiers"): "Apply modifiers after separation",
        ("*", shapekeys_to_objects.bl_idname + "remove_nonrender"): "A non-render modifier will be removed.",

        # assign_lr_shapekey_tag
        ("*", assign_lr_shapekey_tag.bl_idname + DESC): "See \"Read-me.txt\"",
        ("*", assign_lr_shapekey_tag.bl_idname + "enable"): "Assign this shape key to separation target",

        ("*", "verts_count_difference"): "Warn: vertices count are different:\n[{0}]({2}), [{1}]({3})",

        # sideofactive_point
        ("*", sideofactive_point.bl_idname + DESC):
            "Performs a select Side of Active based on the specified coordinates",
    },

    "ja_JP": {
        ("*", separate_lr_shapekey_all_tag_detect.bl_idname + DESC):
            "詳細はRead-me.txtを参照。\n名前の最後が_leftまたは_rightのシェイプキーには使えません",

        # apply_modifiers
        ("*", apply_modifiers.bl_idname + consts.DESC):
            "Armature以外の全モディファイアを適用します。\nシェイプキーがあっても使用できます。\n注意：少し時間がかかります",
        ("*", apply_modifiers.bl_idname + "duplicate"): "対象オブジェクトのコピーに対して処理を行います",
        ("*", apply_modifiers.bl_idname + "remove_nonrender"):
            "レンダリング無効化状態のモディファイア\n（モディファイア一覧でカメラアイコンが押されていない）\nを削除します。",

        # separate_lr_shapekey
        ("*", separate_lr_shapekey.bl_idname + DESC): "現在のシェイプキーを\nオブジェクト原点基準で左右別々のシェイプキーにします",
        ("*", separate_lr_shapekey.bl_idname + "duplicate"): "左右分割前のシェイプキーを残します",
        ("*", separate_lr_shapekey.bl_idname + "enable_sort"): "左右分割後のシェイプキーを分割前シェイプキーのすぐ下に移動します",

        # separate_lr_shapekey_all
        ("*", separate_lr_shapekey_all.bl_idname + DESC):
            "全てのシェイプキーをオブジェクト原点基準で左右別々にします。\n"
            "名前の最後が_leftまたは_rightのシェイプキーは分割済みと見なし処理をスキップします",
        ("*", separate_lr_shapekey_all.bl_idname + "duplicate"):
            "左右分割前のシェイプキーを残します。\n"
            "注意：左右分割する前とした後のシェイプキーを同時に使うとモデルが意図しない見た目になる可能性があります。\n"
            "（シェイプキーが二重にかかるため）",
        ("*", separate_lr_shapekey_all.bl_idname + "enable_sort"):
            "左右分割後のシェイプキーを分割前シェイプキーのすぐ下に移動します。\n注意：時間がかかります",

        # shapekeys_to_objects
        ("*", shapekeys_to_objects.bl_idname + DESC): "シェイプキーをそれぞれ別オブジェクトにします。\n注意：少し時間がかかります",
        ("*", shapekeys_to_objects.bl_idname + "duplicate"): "対象オブジェクトのコピーに対して処理を行います",
        ("*", shapekeys_to_objects.bl_idname + "apply_modifiers"): "分割後にオブジェクトのモディファイアを適用します",
        ("*", shapekeys_to_objects.bl_idname + "remove_nonrender"):
            "レンダリング無効化状態のモディファイア\n（モディファイア一覧でカメラアイコンが押されていない）\nを削除します。",

        # assign_lr_shapekey_tag
        ("*", assign_lr_shapekey_tag.bl_idname + DESC): "詳細はRead-me.txtを参照",
        ("*", assign_lr_shapekey_tag.bl_idname + "enable"): "シェイプキーを左右分割処理の対象とします",

        ("*", "verts_count_difference"):
            "シェイプキーの頂点数が異なっているため処理を実行できませんでした。\n"
            "ミラーモディファイアの\"結合\"で他より多くの頂点が結合されてしまっているなどの原因が考えられます。\n[{0}]({2}), [{1}]({3})",

        ("*", sideofactive_point.bl_idname + DESC): "指定した座標を基準にSelect Side of activeを実行します",
    },
}


def register():
    bpy.app.translations.register(func_package_utils.get_package_root(), translations_dict)


def unregister():
    bpy.app.translations.unregister(func_package_utils.get_package_root())
