import bpy
from . import OT_separate_shapekeys, OT_apply_modifiers
from . import ShapeKeysUtil


# オブジェクトモード　Special → ShapeKeys Util を登録する
def INFO_MT_object_specials_shapekeys_util_menu(self, context):
    self.layout.menu(VIEW3D_MT_object_specials_shapekeys_util.bl_idname)


# オブジェクトモード　Special → ShapeKeys Util にコマンドを登録するクラス
class VIEW3D_MT_object_specials_shapekeys_util(bpy.types.Menu):
    bl_label = "ShapeKeys Util"
    bl_idname = "VIEW3D_MT_object_specials_shapekeys_util"

    def draw(self, context):
        layout = self.layout
        layout.operator(OT_apply_modifiers.OBJECT_OT_specials_shapekeys_util_apply_modifiers.bl_idname)
        layout.operator(OT_separate_shapekeys.OBJECT_OT_specials_shapekeys_util_separateobj.bl_idname)
        layout.separator()
        layout.operator(ShapeKeysUtil.OBJECT_OT_specials_shapekeys_util_separate_lr_shapekey.bl_idname)
        layout.operator(ShapeKeysUtil.OBJECT_OT_specials_shapekeys_util_separate_lr_shapekey_all.bl_idname)
        layout.operator(ShapeKeysUtil.OBJECT_OT_specials_shapekeys_util_separate_lr_shapekey_all_tagdetect.bl_idname)
        layout.operator(ShapeKeysUtil.OBJECT_OT_specials_shapekeys_util_assign_lr_shapekey_tag.bl_idname)


def register():
    bpy.utils.register_class(VIEW3D_MT_object_specials_shapekeys_util)
    bpy.types.VIEW3D_MT_object_context_menu.append(INFO_MT_object_specials_shapekeys_util_menu)


def unregister():
    bpy.utils.unregister_class(VIEW3D_MT_object_specials_shapekeys_util)
    bpy.types.VIEW3D_MT_object_context_menu.remove(INFO_MT_object_specials_shapekeys_util_menu)
