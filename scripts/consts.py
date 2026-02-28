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

# Create Left and Right Shape Keys の自動判定で使うやつ
ENABLE_LR_TAG = "%LR%"
ENABLE_DUPLICATE_TAG = "%D%"
ENABLE_SORT_TAG = "%S%"

# Apply Modifier用
REGEX_APPLY_AS_SHAPEKEY_PREFIX = re.compile(r"^%AS(?::(.*))?%", re.IGNORECASE)  # モディファイア名が%AS%で始まっているならApply as shapekey
FORCE_APPLY_MODIFIER_PREFIX = "%A%"  # モディファイア名が"%A%"で始まっているならArmatureなどの対象外モディファイアでも強制的に適用
FORCE_KEEP_MODIFIER_PREFIX = "%KEEP%"  # モディファイア名が"%KEEP%"で始まっているならモディファイアを適用せずに処理を続行する

# モディファイア適用時にデフォルトでスキップするモディファイアタイプ
DEFAULT_SKIP_MODIFIER_TYPES = {'ARMATURE'}

# Blender自動付与サフィックスのパターン（.001, .002 など）
REGEX_BLENDER_SUFFIX = re.compile(r'\.\d{3}$')


def parse_skip_modifier_types_str(s: str) -> set:
    """カンマ区切り文字列からスキップ対象モディファイアタイプのセットをパース"""
    return set(filter(None, s.split(',')))


def normalize_shapekey_name(name: str) -> str:
    """
    シェイプキー名を正規化する

    1. $以降を削除
    2. .001などのBlender自動付与サフィックスを削除

    Args:
        name: 正規化前の名前

    Returns:
        正規化後の名前
    """
    # $以降を削除
    result = name.split("$")[0]
    # .001などのBlender自動付与サフィックスを削除
    result = REGEX_BLENDER_SUFFIX.sub("", result)
    return result

def get_tag(match):
    if match:
        groups = match.groups()
        if groups and groups[0]:
            return groups[0]
    return None


def parse_tag_options(tag):
    """
    タグ文字列からオプションを解析
    例: "ALL:DIRECT:BASE:MyBasis" -> {'all': True, 'direct': True, 'base': 'MyBasis'}
    """
    if not tag:
        return {}

    options = {}
    parts = tag.upper().split(':')

    i = 0
    while i < len(parts):
        part = parts[i]
        if part == 'ALL':
            options['all'] = True
        elif part == 'DIRECT':
            options['direct'] = True
        elif part == 'I':
            options['inverted'] = True
        elif part == 'BASE':
            # BASE:xxx形式 - 次の要素がベースシェイプキー名
            if i + 1 < len(parts):
                # 元のケースを保持するために元のタグから取得
                original_parts = tag.split(':')
                options['base'] = original_parts[i + 1]
                i += 1
        i += 1

    return options


def get_modifier_tag_options(modifier):
    """モディファイアからタグオプションを取得"""
    match = REGEX_APPLY_AS_SHAPEKEY_PREFIX.match(modifier.name)
    tag = get_tag(match)
    return parse_tag_options(tag)

def get_base_shapekey_name(modifier):
    """モディファイア名からベースシェイプキー名を取得"""
    options = get_modifier_tag_options(modifier)
    return options.get('base')

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
    """
    %AS:I%を含むならボーンの移動を反転した状態でApply as shapekey
    """
    if modifier.type != 'ARMATURE':
        return False
    options = get_modifier_tag_options(modifier)
    return options.get('inverted', False)


def use_direct_apply_mode(modifier):
    """
    %AS:DIRECT%を含むなら直接適用モード（既存シェイプキーの座標に直接変形を適用）
    デフォルト（%AS%のみ）はデルタ加算モード（Basisからの差分を加算）
    """
    options = get_modifier_tag_options(modifier)
    return options.get('direct', False)


def use_apply_each_shapekeys(modifier):
    """
    %AS:ALL%を含むならシェイプキーを個別にシェイプキーとして適用
    """
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
        # ターゲットオブジェクトの最初のシェイプキーが"All"なら個別適用
        return True

    options = get_modifier_tag_options(modifier)
    return options.get('all', False)

