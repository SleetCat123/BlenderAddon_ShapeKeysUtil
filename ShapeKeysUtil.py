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
import bmesh
from bpy.props import BoolProperty, EnumProperty, FloatProperty, IntProperty, FloatVectorProperty
from . import func_utils, consts


def separate_lr_shapekey(soruce_shape_key_index, duplicate, enable_sort):
    obj = func_utils.get_active_object()
    source_shape_key = obj.data.shape_keys.key_blocks[soruce_shape_key_index]
    
    # print("before: "+source_shape_key.name)
    source_shape_key.name = source_shape_key.name.replace(consts.ENABLE_LR_TAG, '')
    source_shape_key.name = source_shape_key.name.replace(consts.ENABLE_DUPLICATE_TAG, '')
    source_shape_key.name = source_shape_key.name.replace(consts.ENABLE_SORT_TAG, '')
    result_shape_key_name = source_shape_key.name
    # print("after: "+source_shape_key.name)
    
    point = (0,0,0)
    
    # この後で行う選択範囲反転を正常に処理するため、頂点選択だけが有効になるようにしておく
    # temp_mesh_select_mode = bpy.context.tool_settings.mesh_select_mode
    bpy.context.tool_settings.mesh_select_mode = (True, False, False)
    
    # 左
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.shape_key_add(from_mix=False)
    left_shape_index = obj.active_shape_key_index
    left_shape = obj.data.shape_keys.key_blocks[left_shape_index]
    left_shape.name = result_shape_key_name + "_left"
    select_axis_from_point(point=point, mode='NEGATIVE', axis='X')
    # 中心位置を含ませないために選択範囲を反転する
    bpy.ops.mesh.select_all(action='INVERT')
    func_utils.update_mesh()
    if any([v.select for v in obj.data.vertices]):
        bpy.ops.mesh.blend_from_shape(shape=source_shape_key.name, blend=1, add=False)
    select_axis_from_point(point=point, mode='ALIGNED', axis='X')
    func_utils.update_mesh()
    if any([v.select for v in obj.data.vertices]):
        # 中心位置はシェイプを0.5でブレンド。
        # これをしないと、leftとright両方を同時に使ったときに中心位置の頂点が二倍動いてしまう
        bpy.ops.mesh.blend_from_shape(shape=source_shape_key.name, blend=0.5, add=False)
    
    # 右
    # 参照する座標の正負が逆なの以外、やってることは左と同じ
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.shape_key_add(from_mix=False)
    right_shape_index = obj.active_shape_key_index
    right_shape = obj.data.shape_keys.key_blocks[right_shape_index]
    right_shape.name = result_shape_key_name + "_right"
    select_axis_from_point(point=point, mode='POSITIVE', axis='X')
    bpy.ops.mesh.select_all(action='INVERT')
    func_utils.update_mesh()
    if any([v.select for v in obj.data.vertices]):
        print(any([v.select for v in obj.data.vertices]))
        bpy.ops.mesh.blend_from_shape(shape=source_shape_key.name, blend=1, add=False)
    select_axis_from_point(point=point, mode='ALIGNED', axis='X')
    func_utils.update_mesh()
    if any([v.select for v in obj.data.vertices]):
        bpy.ops.mesh.blend_from_shape(shape=source_shape_key.name, blend=0.5, add=False)
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    if enable_sort:
        # 分割したシェイプキーが分割元シェイプキーのすぐ下に来るように移動
        length=len(obj.data.shape_keys.key_blocks)
        if length*0.5 <= soruce_shape_key_index:
            # print("Bottom to Top")
            obj.active_shape_key_index = left_shape_index
            while soruce_shape_key_index + 1 != obj.active_shape_key_index:
                bpy.ops.object.shape_key_move(type='UP')
            obj.active_shape_key_index = right_shape_index
            while soruce_shape_key_index + 2 != obj.active_shape_key_index:
                bpy.ops.object.shape_key_move(type='UP')
        else:
            # 移動先の位置が上から数えたほうが早いとき
            # print("Top to Bottom")
            obj.active_shape_key_index = left_shape_index
            bpy.ops.object.shape_key_move(type='TOP')
            while soruce_shape_key_index + 1 != obj.active_shape_key_index:
                bpy.ops.object.shape_key_move(type='DOWN')
            obj.active_shape_key_index = right_shape_index
            bpy.ops.object.shape_key_move(type='TOP')
            while soruce_shape_key_index + 2 != obj.active_shape_key_index:
                bpy.ops.object.shape_key_move(type='DOWN')
    
    # 左右分割後のシェイプキーに分割元シェイプキーのvalueをコピー
    left_shape.value = source_shape_key.value
    right_shape.value = source_shape_key.value
    source_shape_key.value = 0
    
    if not duplicate:
        obj.active_shape_key_index = soruce_shape_key_index
        bpy.ops.object.shape_key_remove()
    obj.active_shape_key_index = soruce_shape_key_index


def separate_lr_shapekey_all(duplicate, enable_sort, auto_detect):
    obj = func_utils.get_active_object()
    print("Create LR Shapekey All: ["+obj.name+"]")
    
    # 頂点を全て表示
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.reveal()
    bpy.ops.object.mode_set(mode='OBJECT')
    
    shape_keys_length=len(obj.data.shape_keys.key_blocks)
    for i in reversed(range(shape_keys_length)):
        if i == 0:
            break
        shapekey = obj.data.shape_keys.key_blocks[i]

        # 名前の最後が_leftまたは_rightのシェイプキーは既に左右分割済みと見なし処理スキップ
        if shapekey.name.endswith("_left") or shapekey.name.endswith("_right"):
            continue
        # auto_detectがTrueなら、名前に"%LR%"を含むときだけ左右分割処理を行う
        if not auto_detect or (auto_detect and shapekey.name.find(consts.ENABLE_LR_TAG) != -1):
            # print("Shapekey: ["+shapekey.name+"] ["+str(shape_keys_length-1-i)+" / "+str(shape_keys_length)+"]")
            print("Shapekey: ["+shapekey.name+"]")
            dup_temp = duplicate
            sort_temp = enable_sort
            if auto_detect:
                # 名前に"%DUP%"を含むなら強制的に複製ON
                if shapekey.name.find(consts.ENABLE_DUPLICATE_TAG) != -1:
                    dup_temp = True
                # 名前に"%SORT%"を含むなら強制的にソートON
                if shapekey.name.find(consts.ENABLE_SORT_TAG) != -1:
                    sort_temp = True
            separate_lr_shapekey(soruce_shape_key_index=i, duplicate=dup_temp, enable_sort=sort_temp)
    
    print("Finish Create LR Shapekey All: ["+obj.name+"]")


# 指定座標を基準にSide of Active
def select_axis_from_point(point=(0,0,0), mode='POSITIVE', axis='X', threshold=0.0001):
    obj = func_utils.get_active_object()
    if obj.type != 'MESH':
        return
    
    bpy.ops.object.mode_set(mode='EDIT')
    me = obj.data
    bm = bmesh.from_edit_mesh(me)
    
    # 頂点選択を有効化
    temp_select_mode = bm.select_mode
    bm.select_mode = {'VERT'}
    
    bpy.ops.mesh.select_all(action='DESELECT')
    # 一時的に頂点を追加し、それを基準にSide of Activeを使う
    v = bm.verts.new(point)
    func_utils.select_object(v, True)
    bm.select_history.add(v)
    func_utils.select_axis(mode=mode, axis=axis, threshold=threshold)
    # 追加した頂点を削除
    bmesh.ops.delete(bm, geom=[v], context='VERTS')
    
    bm.select_mode = temp_select_mode

    bmesh.update_edit_mesh(mesh=me, loop_triangles=False, destructive=True)
    # bpy.ops.object.mode_set(mode='OBJECT')


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
        
        separate_lr_shapekey(soruce_shape_key_index=obj.active_shape_key_index, duplicate=self.duplicate, enable_sort=self.enable_sort)
        return {'FINISHED'}


class OBJECT_OT_specials_shapekeys_util_separate_lr_shapekey_all(bpy.types.Operator):
    bl_idname = "object.shapekeys_util_separate_lr_shapekey_all"
    bl_label = "Separate All Shape Key Left and Right"
    bl_description = bpy.app.translations.pgettext(bl_idname+"_desc")
    bl_options = {'REGISTER', 'UNDO'}
    
    duplicate: BoolProperty(name="Duplicate", default=False, description=bpy.app.translations.pgettext("separate_lr_shapekey_duplicate"))
    enable_sort: BoolProperty(name="Enable Sort", default=False, description=bpy.app.translations.pgettext("separate_lr_shapekey_all_enable_sort"))
    
    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj.type == 'MESH' and obj.data.shape_keys and len(obj.data.shape_keys.key_blocks) != 0
    
    def execute(self, context):
        obj = context.object
        func_utils.set_active_object(obj)
        separate_lr_shapekey_all(duplicate=self.duplicate, enable_sort=self.enable_sort, auto_detect=False)
        return {'FINISHED'}


class OBJECT_OT_specials_shapekeys_util_separate_lr_shapekey_all_tagdetect(bpy.types.Operator):
    bl_idname = "object.shapekeys_util_separate_lr_shapekey_all_tagdetect"
    bl_label = "(Tag) Separate All Shape Key Left and Right"
    bl_description = bpy.app.translations.pgettext(bl_idname+"_desc")
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj.type == 'MESH' and obj.data.shape_keys and len(obj.data.shape_keys.key_blocks) != 0

    def execute(self, context):
        obj = context.object
        func_utils.set_active_object(obj)
        separate_lr_shapekey_all(duplicate=False, enable_sort=False, auto_detect=True)
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
        select_axis_from_point(self.point, self.mode, self.axis, self.threshold)
        
        return {'FINISHED'}


# Init #
classes = [
    OBJECT_OT_specials_shapekeys_util_separate_lr_shapekey,
    OBJECT_OT_specials_shapekeys_util_separate_lr_shapekey_all,
    OBJECT_OT_specials_shapekeys_util_separate_lr_shapekey_all_tagdetect,
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
