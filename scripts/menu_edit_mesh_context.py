import bpy
from . import ShapeKeysUtil

# エディットモード　Special → ShapeKeys Util を登録する
def INFO_MT_edit_mesh_specials_shapekeys_util_menu(self, context):
    self.layout.menu(VIEW3D_MT_edit_mesh_specials_shapekeys_util.bl_idname)


# エディットモード　Special → ShapeKeys Util にコマンドを登録するクラス
class VIEW3D_MT_edit_mesh_specials_shapekeys_util(bpy.types.Menu):
    bl_label = "ShapeKeys Util"
    bl_idname = "INFO_MT_edit_mesh_specials_shapekeys_util_menu"

    def draw(self, context):
        self.layout.operator(ShapeKeysUtil.MESH_OT_specials_shapekeys_util_sideofactive_point.bl_idname)


def register():
    bpy.utils.register_class(VIEW3D_MT_edit_mesh_specials_shapekeys_util)
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.append(INFO_MT_edit_mesh_specials_shapekeys_util_menu)


def unregister():
    bpy.utils.unregister_class(VIEW3D_MT_edit_mesh_specials_shapekeys_util)
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.remove(INFO_MT_edit_mesh_specials_shapekeys_util_menu)
