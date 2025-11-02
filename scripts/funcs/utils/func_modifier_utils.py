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


def get_target_object(modifier: bpy.types.Modifier):
    if hasattr(modifier, 'object'):
        return modifier.object
    if hasattr(modifier, 'mirror_object'):
        return modifier.mirror_object
    if hasattr(modifier, 'target'):
        return modifier.target


def set_target_object(modifier: bpy.types.Modifier, obj: bpy.types.Object):
    if hasattr(modifier, 'object'):
        modifier.object = obj
        return
    if hasattr(modifier, 'mirror_object'):
        modifier.mirror_object = obj
        return
    if hasattr(modifier, 'target'):
        modifier.target = obj
        return


def get_modifier_name_safe(modifier):
    """モディファイア名を安全に取得する"""
    # hasattr自体がUnicodeDecodeErrorを引き起こす可能性があるため、try-exceptで囲む
    try:
        has_name = hasattr(modifier, 'name')
    except UnicodeDecodeError as e:
        # Blenderの内部データが一時的に不正な状態になっている
        print("WARNING: UnicodeDecodeError in hasattr(modifier, 'name')")
        print(f"Error: {e}")
        print("This is likely a temporary Blender internal issue. Retrying...")
        
        # 少し待機してから再試行
        import time
        time.sleep(0.1)
        
        try:
            # 再試行
            has_name = hasattr(modifier, 'name')
        except UnicodeDecodeError:
            # それでもダメなら、このモディファイアは無効と判断
            error_msg = (
                "Modifier object is in an invalid state (UnicodeDecodeError in hasattr).\n"
                "This may be caused by:\n"
                "- Corrupted modifier data\n"
                "- Recent Undo/Redo operations\n"
                "- Temporary Blender internal issue\n"
                "Please try: Save the file, reopen Blender, and load the file again."
            )
            raise RuntimeError(error_msg) from e
    
    # モディファイアが無効な状態の可能性をチェック
    if not has_name:
        raise AttributeError(f"Modifier has no 'name' attribute. Type: {type(modifier)}")
    
    try:
        # 名前を取得（UnicodeDecodeErrorが発生する可能性がある）
        return modifier.name
    except UnicodeDecodeError as e:
        # より詳細なエラー情報を提供
        error_msg = (
            f"Invalid character in modifier name (UnicodeDecodeError).\n"
            f"Modifier type: {getattr(modifier, 'type', 'unknown')}\n"
            f"Error details: {e}\n"
            f"This may be caused by:\n"
            f"- Corrupted modifier data\n"
            f"- Undo/Redo operations\n"
            f"- Invalid characters in modifier name\n"
            f"Please try: Save the file, reopen Blender, and load the file again."
        )
        raise UnicodeDecodeError(e.encoding, e.object, e.start, e.end, error_msg) from e
