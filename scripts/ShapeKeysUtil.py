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
from bpy.props import BoolProperty, EnumProperty, FloatProperty, IntProperty, FloatVectorProperty
from . import func_utils, consts, func_separate_lr_shapekey, func_select_axis_from_point


# AddonPreferences #
class addon_preferences(bpy.types.AddonPreferences):
    bl_idname = __package__
    
    wait_interval: IntProperty(name="Wait Interval", default=5, min=1, soft_min=1)
    wait_sleep: FloatProperty(name="Wait Sleep", default=0.5, min=0, soft_min=0, max=2, soft_max=2)
    
    def draw(self, context):
        layout = self.layout
        
        layout.prop(self, "wait_interval")
        layout.prop(self, "wait_sleep")


# region Object Operator


class OBJECT_OT_specials_shapekeys_util_separate_lr_shapekey(bpy.types.Operator):
    bl_idname = "object.shapekeys_util_separate_lr_shapekey"
    bl_label = "Separate Shape Key Left and Right"
    bl_description = bpy.app.translations.pgettext(bl_idname+"_desc")
    bl_options = {'REGISTER', 'UNDO'}
    
    duplicate: BoolProperty(name="Duplicate", default=False, description=bpy.app.translations.pgettext("separate_lr_shapekey_duplicate"))
    enable_sort: BoolProperty(name="Enable Sort", default=True, description=bpy.app.translations.pgettext(bl_idname+"_enable_sort"))
    
    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj.type == 'MESH' and obj.data.shape_keys and len(obj.data.shape_keys.key_blocks) != 0
    
    def execute(self, context):
        obj = context.object
        func_utils.set_active_object(obj)
        
        # 頂点を全て表示
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.reveal()
        bpy.ops.object.mode_set(mode='OBJECT')
        
        func_separate_lr_shapekey.separate_lr_shapekey(soruce_shape_key_index=obj.active_shape_key_index, duplicate=self.duplicate, enable_sort=self.enable_sort)
        return {'FINISHED'}


class OBJECT_OT_specials_shapekeys_util_assign_lr_shapekey_tag(bpy.types.Operator):
    bl_idname = "object.shapekeys_util_assign_lr_shapekey_tag"
    bl_label = "Assign Tag"
    bl_description = bpy.app.translations.pgettext(bl_idname+"_desc")
    bl_options = {'REGISTER', 'UNDO'}
    
    enable: BoolProperty(name="Enable", description=bpy.app.translations.pgettext(bl_idname+"_enable"))
    duplicate: BoolProperty(name="Duplicate", description=bpy.app.translations.pgettext("separate_lr_shapekey_duplicate"))
    enable_sort: BoolProperty(name="Enable Sort", description=bpy.app.translations.pgettext("separate_lr_shapekey_all_enable_sort"))
    
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
        self.duplicate = shapekey.name.find(consts.ENABLE_DUPLICATE_TAG) != -1
        self.enable_sort = shapekey.name.find(consts.ENABLE_SORT_TAG) != -1
        return self.execute(context)
    
    def draw(self, context):
        layout = self.layout
        layout.label(text="Target: "+self.target_name)
        layout.label(text="Shape: "+self.target_shape_name)
        layout.prop(self, "enable")
        col = layout.column()
        col.enabled = self.enable
        col.prop(self, "duplicate")
        col.prop(self, "enable_sort")
    
    def execute(self, context):
        obj = context.object
        shapekey = obj.data.shape_keys.key_blocks[obj.active_shape_key_index]
        
        if self.enable:
            if shapekey.name.find(consts.ENABLE_LR_TAG) == -1:
                shapekey.name += consts.ENABLE_LR_TAG
        else:
            shapekey.name=shapekey.name.replace(consts.ENABLE_LR_TAG, '')
        
        if self.enable and self.duplicate:
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
# endregion


# Mesh Operator #
class MESH_OT_specials_shapekeys_util_sideofactive_point(bpy.types.Operator):
    bl_idname = "edit_mesh.shapekeys_util_sideofactive_point"
    bl_label = "Side of Active from Point"
    bl_description = "指定座標を基準にSide of active"
    bl_options = {'REGISTER', 'UNDO'}
    
    point: FloatVectorProperty(name="Point")
    
    mode: EnumProperty(
        name="Axis Mode",
        default='NEGATIVE',
        items=(
            ('POSITIVE', "Positive Axis", ""),
            ('NEGATIVE', "Negative Axis", ""),
            ('ALIGNED', "Aligned Axis", ""),
        )
    )
    
    axis: EnumProperty(
        name="Axis",
        default='X',
        items=(
            ('X', "X", ""),
            ('Y', "Y", ""),
            ('Z', "Z", ""),
        )
    )
    
    threshold: FloatProperty(
        name="Threshold",
        min=0.000001, max=50.0,
        soft_min=0.00001, soft_max=10.0,
        default=0.0001,
    )
    
    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj.type == 'MESH'
    
    def execute(self, context):
        func_select_axis_from_point.select_axis_from_point(self.point, self.mode, self.axis, self.threshold)
        
        return {'FINISHED'}


# Init #
classes = [
    OBJECT_OT_specials_shapekeys_util_separate_lr_shapekey,
    OBJECT_OT_specials_shapekeys_util_assign_lr_shapekey_tag,
    
    MESH_OT_specials_shapekeys_util_sideofactive_point,
    
    addon_preferences,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
