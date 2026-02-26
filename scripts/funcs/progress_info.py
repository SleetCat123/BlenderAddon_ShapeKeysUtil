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

"""
進捗情報の共通データ構造

ジェネレータベースの非同期処理で使用する進捗情報を定義します。
各処理関数はProgressInfoをyieldし、Modal版オペレーターで進捗表示に使用します。
"""

from dataclasses import dataclass

import bpy


def T(message: str) -> str:
    """ローカライズ対応のテキスト取得

    翻訳辞書で ("*", msgid) 形式で登録されたテキストを取得します。
    コンテキスト "*" は任意のコンテキストにマッチします。
    """
    return bpy.app.translations.pgettext(message, "*")


@dataclass
class ProgressInfo:
    """進捗情報データクラス

    Attributes:
        phase: 処理フェーズ名（例: "init", "convert", "modifiers", "merge"）
        progress: 全体進捗率（0.0〜1.0）
        message: 表示用メッセージ
        object_name: 処理中のオブジェクト名（オプション）
        sub_progress: フェーズ内の進捗率（0.0〜1.0、オプション）
        total_objects: 処理対象の総オブジェクト数（オプション）
        current_object_index: 現在のオブジェクトインデックス（オプション）
    """
    phase: str
    progress: float
    message: str
    object_name: str = ""
    sub_progress: float = 0.0
    total_objects: int = 0
    current_object_index: int = 0

    def __post_init__(self):
        # 進捗率を0.0〜1.0の範囲にクランプ
        self.progress = max(0.0, min(1.0, self.progress))
        self.sub_progress = max(0.0, min(1.0, self.sub_progress))


# フェーズの重み（進捗計算用）
# apply_modifier_and_merge_selections用
PHASE_WEIGHTS_MERGE_SELECTIONS = {
    "init": 0.05,
    "convert": 0.15,
    "instance": 0.10,
    "modifiers": 0.50,
    "empty": 0.05,
    "merge": 0.10,
    "join_shape": 0.05,
}

# merge_children_recursive用
PHASE_WEIGHTS_MERGE_CHILDREN = {
    "init": 0.05,
    "analyze": 0.10,
    "process_children": 0.80,
    "finalize": 0.05,
}


class ProgressCalculator:
    """進捗計算ヘルパークラス"""

    def __init__(self, phase_weights: dict):
        """
        Args:
            phase_weights: フェーズ名をキー、重みを値とする辞書
        """
        self.phase_weights = phase_weights
        self.phases = list(phase_weights.keys())

        # 累積重みを事前計算
        self._cumulative_weights = {}
        cumulative = 0.0
        for phase in self.phases:
            self._cumulative_weights[phase] = cumulative
            cumulative += phase_weights[phase]

    def calculate_progress(self, phase: str, sub_progress: float = 0.0) -> float:
        """全体進捗率を計算

        Args:
            phase: 現在のフェーズ名
            sub_progress: フェーズ内の進捗率（0.0〜1.0）

        Returns:
            全体進捗率（0.0〜1.0）
        """
        if phase not in self.phase_weights:
            return 0.0

        base = self._cumulative_weights[phase]
        phase_contribution = self.phase_weights[phase] * sub_progress
        return min(1.0, base + phase_contribution)

    def create_progress_info(
        self,
        phase: str,
        message: str,
        sub_progress: float = 0.0,
        object_name: str = "",
        total_objects: int = 0,
        current_object_index: int = 0
    ) -> ProgressInfo:
        """ProgressInfoを作成

        Args:
            phase: 処理フェーズ名
            message: 表示用メッセージ
            sub_progress: フェーズ内の進捗率
            object_name: 処理中のオブジェクト名
            total_objects: 処理対象の総オブジェクト数
            current_object_index: 現在のオブジェクトインデックス

        Returns:
            ProgressInfo
        """
        return ProgressInfo(
            phase=phase,
            progress=self.calculate_progress(phase, sub_progress),
            message=message,
            object_name=object_name,
            sub_progress=sub_progress,
            total_objects=total_objects,
            current_object_index=current_object_index
        )
