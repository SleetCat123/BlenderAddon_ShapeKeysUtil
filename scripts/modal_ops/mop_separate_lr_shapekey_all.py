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

"""
Separate LR Shapekey All Modal版オペレーター

ジェネレータベースのModal処理を使用して、進捗表示とキャンセル機能を
サポートするSeparate LR Shapekey Allオペレーターを実装します。
"""

from collections.abc import Generator
from typing import Optional

import bpy
from bpy.props import BoolProperty

from ..funcs.func_separate_lr_shapekey_all import separate_lr_shapekey_all_iter
from ..funcs.modal_base import GeneratorModalOperator
from ..funcs.progress_info import ProgressInfo
from ..funcs.utils import func_object_utils


class OBJECT_OT_shapekeys_util_separate_lr_all_modal(GeneratorModalOperator):
    """Separate LR Shapekey All Modal版オペレーター

    全シェイプキーを左右分割します。
    Modal処理により進捗表示とキャンセル機能をサポートします。
    """

    bl_idname = "object.shapekeys_util_separate_lr_shapekey_all_modal"
    bl_label = "Separate All Shape Key Left and Right (Modal)"
    bl_description = "All shape key separate left and right based on object origin with progress display"
    bl_options = {'REGISTER', 'UNDO'}

    keep_original: BoolProperty(
        name="Keep Original",
        default=False,
        description="Keep the shape key before the left-right split"
    )

    enable_sort: BoolProperty(
        name="Enable Sort",
        default=False,
        description="Result shape keys move to below target shape key"
    )

    @classmethod
    def poll(cls, context):
        obj = context.object
        return (obj is not None and
                obj.type == 'MESH' and
                obj.data.shape_keys is not None and
                len(obj.data.shape_keys.key_blocks) != 0)

    def draw(self, context):
        """UIの描画"""
        layout = self.layout
        layout.prop(self, "keep_original")
        layout.prop(self, "enable_sort")

    def create_generator(self, context: bpy.types.Context) -> Optional[Generator[ProgressInfo, None, None]]:
        """処理ジェネレータを作成"""
        obj = context.object

        if obj is None:
            self.report({'ERROR'}, "No active object")
            return None

        if obj.type != 'MESH':
            self.report({'ERROR'}, "Active object is not a mesh")
            return None

        if obj.data.shape_keys is None or len(obj.data.shape_keys.key_blocks) == 0:
            self.report({'ERROR'}, "No shape keys found")
            return None

        func_object_utils.set_active_object(obj)

        return separate_lr_shapekey_all_iter(
            duplicate=self.keep_original,
            enable_sort=self.enable_sort,
            auto_detect=False
        )

    def on_complete(self, context: bpy.types.Context):
        """処理完了時のコールバック"""
        self.report({'INFO'}, "Separate LR Shapekey All complete")

    def execute(self, context: bpy.types.Context):
        """同期実行（invokeではなくexecuteが呼ばれた場合）"""
        # 同期版オペレーターにフォールバック
        return bpy.ops.object.shapekeys_util_separate_lr_shapekey_all(
            keep_original=self.keep_original,
            enable_sort=self.enable_sort
        )


# 翻訳辞書
translations_dict = {
    "ja_JP": {
        ("*", "All shape key separate left and right based on object origin with progress display"):
            "全てのシェイプキーをオブジェクト原点基準で左右分割（進捗表示付き）",
        ("*", "Keep Original"): "元のシェイプキーを残す",
        ("*", "Keep the shape key before the left-right split"):
            "左右分割前のシェイプキーを残します",
        ("*", "Enable Sort"): "分割後の並び替え",
        ("*", "Result shape keys move to below target shape key"):
            "左右分割後のシェイプキーを分割前シェイプキーのすぐ下に移動します",
    },
}


def register():
    """クラス登録"""
    bpy.utils.register_class(OBJECT_OT_shapekeys_util_separate_lr_all_modal)
    bpy.app.translations.register(__name__, translations_dict)


def unregister():
    """クラス登録解除"""
    bpy.utils.unregister_class(OBJECT_OT_shapekeys_util_separate_lr_all_modal)
    bpy.app.translations.unregister(__name__)
