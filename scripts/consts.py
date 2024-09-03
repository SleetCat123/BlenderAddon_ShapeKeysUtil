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

# Create Left and Right Shape Keys の自動判定で使うやつ
ENABLE_LR_TAG = "%LR%"
ENABLE_DUPLICATE_TAG = "%D%"
ENABLE_SORT_TAG = "%S%"

# Apply Modifier用
APPLY_AS_SHAPEKEY_PREFIX = "%AS%"  # モディファイア名が%AS%で始まっているならApply as shapekey
FORCE_APPLY_MODIFIER_PREFIX = "%A%"  # モディファイア名が"%A%"で始まっているならArmatureなどの対象外モディファイアでも強制的に適用
FORCE_KEEP_MODIFIER_PREFIX = "%KEEP%"  # モディファイア名が"%KEEP%"で始まっているならモディファイアを適用せずに処理を続行する
