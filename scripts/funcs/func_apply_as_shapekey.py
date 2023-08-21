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
from BlenderAddon_ShapeKeysUtil.scripts import consts


def apply_as_shapekey(modifier):
    try:
        # 名前の文字列から%AS%を削除する
        modifier.name = modifier.name[len(consts.APPLY_AS_SHAPEKEY_PREFIX):len(modifier.name)]
        # Apply As Shape
        bpy.ops.object.modifier_apply_as_shapekey(keep_modifier=False, modifier=modifier.name)
    except RuntimeError:
        # 無効なModifier（対象オブジェクトが指定されていないなどの状態）は適用しない
        print("!!! Apply as shapekey failed !!!: [{0}]".format(modifier.name))
        bpy.ops.object.modifier_remove(modifier=modifier.name)
    else:
        try:
            print("Apply as shapekey: [{0}]".format(modifier.name))
        except UnicodeDecodeError:
            print("Apply as shapekey")
