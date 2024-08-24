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
from ..funcs import func_separate_shapekeys
from ..funcs.utils import func_object_utils


class OBJECT_OT_mizore_shapekeys_util_apply_selected_modifiers(bpy.types.Operator):
    bl_idname = "object.shapekeys_util_apply_selected_modifiers"
    bl_label = "Apply Selected Modifiers"
    bl_description = "Apply Selected Modifiers"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.object
        return (
            obj
            and not obj.hide_viewport 
            and not obj.hide_get() 
            and obj.type == 'MESH' 
            and obj.modifiers 
            and obj.modifiers.active
            )

    def execute(self, context):
        original_obj = context.object
        func_object_utils.set_active_object(original_obj)
        func_object_utils.deselect_all_objects()
        active_mod_name = original_obj.modifiers.active.name
        print(f"Active Mod: {active_mod_name}")
        # シェイプキーをもつオブジェクトのモディファイアを適用
        if original_obj.data.shape_keys and original_obj.data.shape_keys.key_blocks:
            basis_obj = func_object_utils.duplicate_object(original_obj, False)
            separated_objects = func_separate_shapekeys.separate_shapekeys(
                duplicate=False,
                enable_apply_modifiers=False,
                remove_nonrender=False,
                keep_original_shapekeys=False
            )
            print(f"Basis: {basis_obj.name}")
            try:
                func_object_utils.set_active_object(basis_obj)
                bpy.ops.object.modifier_apply(modifier=active_mod_name)
                for separated_obj in separated_objects:
                    print(separated_obj.name)
                    func_object_utils.set_active_object(separated_obj)
                    bpy.ops.object.modifier_apply(modifier=active_mod_name)
            except Exception as e:
                print(e)
                self.report({'ERROR'}, str(e))
                # 処理中オブジェクトを削除
                func_object_utils.remove_object(basis_obj)
                func_object_utils.remove_objects(separated_objects)
                func_object_utils.set_active_object(original_obj)
                return {'CANCELLED'}

            prev_obj_name = basis_obj.name
            prev_vert_count = len(basis_obj.data.vertices)
            func_object_utils.select_object(basis_obj, True)
            func_object_utils.set_active_object(basis_obj)
            for obj in separated_objects:
                vert_count = len(obj.data.vertices)
                print("current: [{1}]({3})   prev: [{0}]({2})".format(
                    prev_obj_name,
                    obj.name, 
                    str(prev_vert_count),
                    str(vert_count))
                    )
                if vert_count != prev_vert_count:
                    # 前回のシェイプキーと頂点数が違ったら警告して処理を取り消し
                    warn = bpy.app.translations.pgettext("verts_count_difference").format(
                        prev_obj_name, 
                        obj.name,
                        prev_vert_count, 
                        vert_count
                        )
                    self.report({'ERROR'}, warn)
                    print("!!!!! " + warn + "!!!!!")
                    # 処理中オブジェクトを削除
                    func_object_utils.remove_object(basis_obj)
                    func_object_utils.remove_objects(separated_objects)
                    func_object_utils.set_active_object(original_obj)
                    return {'CANCELLED'}

                prev_vert_count = vert_count
                prev_obj_name = obj.name

                # 一気にjoin_shapesするとシェイプキーの順番がおかしくなるので1つずつ
                # Armatureによる変形を無効化
                for modifier in obj.modifiers:
                    if modifier.type == 'ARMATURE':
                        modifier.show_viewport = False
                        modifier.show_render = False
                func_object_utils.select_object(obj, True)
                print("Join: [{2}]({3}) -> [{0}]({1})".format(
                    basis_obj.name, 
                    str(len(basis_obj.data.vertices)), 
                    obj.name,
                    str(vert_count))
                    )
                # オブジェクトを1つにまとめなおす
                bpy.ops.object.join_shapes()
                func_object_utils.select_object(obj, False)
            # シェイプキーの名前と数値を復元
            basis_obj.active_shape_key_index = original_obj.active_shape_key_index
            for i, shapekey in enumerate(basis_obj.data.shape_keys.key_blocks):
                shapekey.name = original_obj.data.shape_keys.key_blocks[i].name
                shapekey.value = original_obj.data.shape_keys.key_blocks[i].value

            # オリジナルオブジェクトに反映
            original_obj.data = basis_obj.data
            original_obj.modifiers.remove(original_obj.modifiers[active_mod_name])
            func_object_utils.remove_object(basis_obj)
            func_object_utils.remove_objects(separated_objects)
            func_object_utils.select_object(original_obj, True)
            func_object_utils.set_active_object(original_obj)
        else:
            # シェイプキーを持たないオブジェクトのモディファイアを適用
            bpy.ops.object.modifier_apply(modifier=active_mod_name)
        return {'FINISHED'}


translations_dict = {
    "en_US": {
        ("*", "verts_count_difference"): "Could not execute the process because the number of vertices of the shape key is different.\n"
        "It may be because the number of vertices is changed by Boolean or Merge of the Mirror modifier.\n[{0}]({2}), [{1}]({3})",
    },
    "ja_JP": {
        ("*", "verts_count_difference"):
            "シェイプキーの頂点数が異なっているため処理を実行できませんでした。\n"
            "ブーリアンやミラーモディファイアの\"結合\"で頂点数が変化しているなどの原因が考えられます。\n[{0}]({2}), [{1}]({3})",
            
        ("*", "Apply Selected Modifiers"):
            "詳細はRead-me.txtを参照。\n名前の最後が_leftまたは_rightのシェイプキーには使えません",
    },
}


def register():
    bpy.utils.register_class(OBJECT_OT_mizore_shapekeys_util_apply_selected_modifiers)
    bpy.app.translations.register(__name__, translations_dict)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_mizore_shapekeys_util_apply_selected_modifiers)
    bpy.app.translations.unregister(__name__)