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
from bpy.props import BoolProperty
from .. import consts


class OBJECT_OT_specials_shapekeys_util_assign_lr_shapekey_tag(bpy.types.Operator):
    bl_idname = "object.shapekeys_util_assign_lr_shapekey_tag"
    bl_label = "Assign Tag"
    bl_description = "Assign or remove the tag for \"(Tag) Separate All Shape Key Left and Right\""
    bl_options = {'REGISTER', 'UNDO'}

    enable: BoolProperty(
        name="Enable",
        description="Assign this shape key to separation target"
    )
    keep_original: BoolProperty(
        name="Keep Orignal",
        description="Keep the shape key before the left-right split"
    )
    enable_sort: BoolProperty(
        name="Enable Sort",
        description="Move the result shape keys to below target shape key"
    )

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
                b = False

        return b

    def invoke(self, context, event):
        obj = context.object
        shapekey = obj.data.shape_keys.key_blocks[obj.active_shape_key_index]
        self.target_name = obj.name
        self.target_shape_name = shapekey.name

        self.enable = shapekey.name.find(consts.ENABLE_LR_TAG) != -1
        self.keep_original = shapekey.name.find(consts.ENABLE_DUPLICATE_TAG) != -1
        self.enable_sort = shapekey.name.find(consts.ENABLE_SORT_TAG) != -1
        return self.execute(context)

    def draw(self, context):
        layout = self.layout
        idname = OBJECT_OT_specials_shapekeys_util_assign_lr_shapekey_tag.bl_idname
        layout.label(text=bpy.app.translations.pgettext("target_object").format(self.target_name))
        layout.label(text=bpy.app.translations.pgettext("target_shape").format(self.target_shape_name))
        layout.prop(self, "enable")
        col = layout.column()
        col.enabled = self.enable
        col.prop(self, "keep_original")
        col.prop(self, "enable_sort")

    def execute(self, context):
        obj = context.object
        shapekey = obj.data.shape_keys.key_blocks[obj.active_shape_key_index]

        if self.enable:
            if shapekey.name.find(consts.ENABLE_LR_TAG) == -1:
                shapekey.name += consts.ENABLE_LR_TAG
        else:
            shapekey.name = shapekey.name.replace(consts.ENABLE_LR_TAG, '')

        if self.enable and self.keep_original:
            if shapekey.name.find(consts.ENABLE_DUPLICATE_TAG) == -1:
                shapekey.name += consts.ENABLE_DUPLICATE_TAG
        else:
            shapekey.name = shapekey.name.replace(consts.ENABLE_DUPLICATE_TAG, '')

        if self.enable and self.enable_sort:
            if shapekey.name.find(consts.ENABLE_SORT_TAG) == -1:
                shapekey.name += consts.ENABLE_SORT_TAG
        else:
            shapekey.name = shapekey.name.replace(consts.ENABLE_SORT_TAG, '')

        return {'FINISHED'}


translations_dict = {
    "en_US": {
        ("*", "target_object"): "Object: {}",
        ("*", "target_shape"): "Shape: {}",
    },

    "ja_JP": {
        ("*", "target_object"): "オブジェクト: {}",
        ("*", "target_shape"): "シェイプキー: {}",

        ("*", "Assign or remove the tag for \"(Tag) Separate All Shape Key Left and Right\""):
            "現在のシェイプキーに対し、\"(Tag) Separate All Shape Key Left and Right\" の処理用テキストを追加／削除します",
        ("*", "Enable"): "有効",
        ("*", "Assign this shape key to separation target"): "シェイプキーを左右分割処理の対象とします",
        ("*", "Keep Orignal"): "元のシェイプキーを残す",
        ("*", "Keep the shape key before the left-right split"): "左右分割前のシェイプキーを残します",
        ("*", "Enable Sort"): "分割後の並び替え",
        ("*", "Move the result shape keys to below target shape key"): "左右分割後のシェイプキーを分割前シェイプキーのすぐ下に移動します",
    },
}


def register():
    bpy.utils.register_class(OBJECT_OT_specials_shapekeys_util_assign_lr_shapekey_tag)
    bpy.app.translations.register(__name__, translations_dict)



def unregister():
    bpy.utils.unregister_class(OBJECT_OT_specials_shapekeys_util_assign_lr_shapekey_tag)
    bpy.app.translations.unregister(__name__)

