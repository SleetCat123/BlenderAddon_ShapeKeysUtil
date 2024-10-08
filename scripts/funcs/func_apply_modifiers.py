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
from .. import consts
from ..funcs.utils import func_object_utils


# オブジェクトのモディファイアを適用
def apply_modifiers(remove_nonrender=True):
    print("apply_modifiers")
    obj = func_object_utils.get_active_object()

    if obj.users != 1 or (obj.data and obj.data.users != 1):
        # リンクされたオブジェクトのモディファイアは適用できないので予めリンクを解除しておく
        bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=True, obdata=True, material=False,
                                        animation=False)

    print("Apply Modifiers: [" + obj.name + "]")
    for modifier in obj.modifiers:
        if modifier.name.startswith(consts.FORCE_KEEP_MODIFIER_PREFIX):
            # モディファイア名がFORCE_KEEP_MODIFIER_PREFIXで始まっているなら無視
            print(f"FORCE_KEEP_MODIFIER_PREFIX: [{modifier.name}]")
            continue
        if not modifier.show_render:
            # モディファイアがレンダリング対象ではない（モディファイア一覧のカメラアイコンが押されていない）なら無視
            if remove_nonrender:
                print(f"remove_nonrender: [{modifier.name}]")
                bpy.ops.object.modifier_remove(modifier=modifier.name)
            continue

        if modifier.name.startswith(consts.APPLY_AS_SHAPEKEY_PREFIX):
            # ここではApply as shapekeyさせたくない
            print("ERROR: apply_as_shapekey")
            bpy.ops.object.modifier_remove(modifier=modifier.name)
        elif modifier.name.startswith(consts.FORCE_APPLY_MODIFIER_PREFIX) or modifier.type != 'ARMATURE':
            # 対象モディファイアが処理対象外モディファイアでないなら
            # または、モディファイアの名前欄が%A%で始まっているなら
            try:
                try:
                    # なんかここだけUnicodeEncodeErrorが出たり出なかったりする。なんで……？
                    print(f"Apply: [{modifier.name}]")
                except UnicodeDecodeError:
                    print("Apply")
                bpy.ops.object.modifier_apply(modifier=modifier.name)
            except RuntimeError:
                # 無効なModifier（対象オブジェクトが指定されていないなどの状態）は適用しない
                print(f"!!! Apply failed !!!: [{modifier.name}]")
                bpy.ops.object.modifier_remove(modifier=modifier.name)
    print(f"Finish Apply Modifiers: [{obj.name}]")
