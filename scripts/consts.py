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

import re

from .funcs.utils import func_modifier_utils

# Create Left and Right Shape Keys の自動判定で使うやつ
ENABLE_LR_TAG = "%LR%"
ENABLE_DUPLICATE_TAG = "%D%"
ENABLE_SORT_TAG = "%S%"

# Apply Modifier用
REGEX_APPLY_AS_SHAPEKEY_PREFIX = re.compile(r"^%AS(?::(.*))?%", re.IGNORECASE)  # モディファイア名が%AS%で始まっているならApply as shapekey
FORCE_APPLY_MODIFIER_PREFIX = "%A%"  # モディファイア名が"%A%"で始まっているならArmatureなどの対象外モディファイアでも強制的に適用
FORCE_KEEP_MODIFIER_PREFIX = "%KEEP%"  # モディファイア名が"%KEEP%"で始まっているならモディファイアを適用せずに処理を続行する

def get_tag(match):
    if match:
        groups = match.groups()
        if groups and groups[0]:
            return groups[0]
    return None

def get_base_shapekey_name(modifier):
    """モディファイア名からベースシェイプキー名を取得"""
    try:
        mod_name = func_modifier_utils.get_modifier_name_safe(modifier)
    except (RuntimeError, UnicodeDecodeError, AttributeError) as e:
        # モディファイアが無効な状態の場合はログを出してNoneを返す
        print(f"WARNING: Could not get modifier name in get_base_shapekey_name: {e}")
        return None
    
    match = REGEX_APPLY_AS_SHAPEKEY_PREFIX.match(mod_name)
    if not match:
        return None
    
    tag = get_tag(match)
    if not tag:
        return None
    
    # BASE:xxx形式のタグを解析
    if tag.startswith('BASE:'):
        return tag[5:]  # 'BASE:'以降を返す
    
    # ALL:BASE:xxx形式のタグを解析
    if tag.startswith('ALL:BASE:'):
        return tag[9:]  # 'ALL:BASE:'以降を返す
    
    return None

def is_composite_shapekey(modifier):
    """複合シェイプキーかどうかを判定"""
    return get_base_shapekey_name(modifier) is not None

def parse_shapekey_name_for_base(shapekey_name):
    """シェイプキー名から@BASE:xxx形式のベース指定を解析"""
    if '@BASE:' in shapekey_name:
        parts = shapekey_name.split('@BASE:')
        if len(parts) == 2:
            clean_name = parts[0]
            base_name = parts[1]
            return clean_name, base_name
    return shapekey_name, None

def use_inverted_bones_as_shapekey(modifier):
    if modifier.type != 'ARMATURE':
        return False
    # %AS:I%で始まっているならボーンの移動を反転した状態でApply as shapekey
    mod_name = func_modifier_utils.get_modifier_name_safe(modifier)
    match = REGEX_APPLY_AS_SHAPEKEY_PREFIX.match(mod_name)
    if get_tag(match) == 'I':
        return True
    return False

def use_apply_each_shapekeys(modifier):
    if modifier.type == 'MESH_DEFORM':
        target_object = modifier.object
    elif modifier.type == 'SURFACE_DEFORM':
        target_object = modifier.target
    else:
        return False
    
    if not target_object:
        return False
    
    if not modifier.is_bound:
        return False
    
    target_data = target_object.data
    if (target_data.shape_keys 
        and len(target_data.shape_keys.key_blocks) > 1 
        and target_data.shape_keys.key_blocks[0].name.lower() == "all"):
        # SurfaceDeformモディファイアのターゲットオブジェクトにシェイプキーが2つ以上存在していて、最初のシェイプキーの名前が"All"ならshow_only_shape_keyをTrueにしてシェイプキーを個別にシェイプキーとして適用
        return True

    # %AS:ALL%で始まっているならシェイプキーを個別にシェイプキーとして適用
    mod_name = func_modifier_utils.get_modifier_name_safe(modifier)
    
    match = REGEX_APPLY_AS_SHAPEKEY_PREFIX.match(mod_name)
    tag = get_tag(match)
    if tag and tag.lower() == "all":
        return True
    # %AS:ALL:BASE:xxx%で始まっているならシェイプキーを個別にシェイプキーとして適用
    if tag and tag.lower().startswith("all:base:"):
        return True
    return False

