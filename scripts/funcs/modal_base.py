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
ジェネレータベースのModal処理基底クラス

ジェネレータを使用した非同期処理をBlenderのModal処理として実行するための
シンプルな基底クラスを提供します。
"""

import time
from collections.abc import Generator
from typing import Optional

import bpy

from .progress_info import ProgressInfo


def create_progress_bar(progress: float, width: int = 20) -> str:
    """プログレスバー文字列を生成

    Args:
        progress: 進捗率（0.0〜1.0）
        width: バーの幅（文字数）

    Returns:
        プログレスバー文字列（例: "████████░░░░"）
    """
    filled = int(width * progress)
    empty = width - filled
    return "█" * filled + "░" * empty


class GeneratorModalOperator(bpy.types.Operator):
    """ジェネレータベースのModal処理基底クラス

    サブクラスでcreate_generator()を実装し、処理ジェネレータを返すことで
    Modal処理として実行できます。
    """

    bl_options = {'REGISTER', 'UNDO'}

    # タイマー設定（クラス変数）
    _timer_interval: float = 0.001  # 1000Hz（高速化）

    # バッチ処理設定
    _batch_time_limit: float = 0.05  # 1フレームあたりの最大処理時間（50ms）

    # 復元設定（サブクラスでオーバーライド可能）
    _undo_on_cancel: bool = True  # キャンセル時に自動Undo
    _undo_on_error: bool = True   # エラー時に自動Undo

    # インスタンス変数はinvokeで初期化（Blenderオペレーターでは__init__使用不可）

    def create_generator(self, context: bpy.types.Context) -> Optional[Generator[ProgressInfo, None, None]]:
        """処理ジェネレータを作成（サブクラスで実装）

        Args:
            context: Blenderコンテキスト

        Returns:
            処理ジェネレータ、またはNone（処理不要の場合）
        """
        raise NotImplementedError("Subclass must implement create_generator()")

    def on_progress(self, context: bpy.types.Context, progress: ProgressInfo):
        """進捗更新時のコールバック（サブクラスでオーバーライド可能）

        Args:
            context: Blenderコンテキスト
            progress: 進捗情報
        """
        # プログレスバー付きの進捗表示
        percent = int(progress.progress * 100)
        bar = create_progress_bar(progress.progress, width=15)

        # メッセージ構築: プログレスバー + パーセント + メッセージ
        # messageフィールドを優先表示（処理内容がわかりやすい）
        parts = [f"{bar} {percent:3d}%"]

        if progress.message:
            # メッセージがある場合はそれを表示
            parts.append(progress.message)
        else:
            # メッセージがない場合はフェーズとオブジェクト名を表示
            if progress.phase:
                parts.append(f"[{progress.phase}]")
            if progress.object_name:
                parts.append(progress.object_name)

        display_message = " ".join(parts)
        context.workspace.status_text_set(display_message)

    def on_complete(self, context: bpy.types.Context):
        """処理完了時のコールバック（サブクラスでオーバーライド可能）

        Args:
            context: Blenderコンテキスト
        """
        self.report({'INFO'}, "Processing complete")

    def on_cancel(self, context: bpy.types.Context):
        """キャンセル時のコールバック（サブクラスでオーバーライド可能）

        Args:
            context: Blenderコンテキスト
        """
        # キャンセル時の自動Undo
        restored = False
        if self._undo_on_cancel:
            restored = self._restore_state()

        if restored:
            self.report({'WARNING'}, "Cancelled - state restored")
        else:
            self.report({'WARNING'}, "Cancelled")

    def on_error(self, context: bpy.types.Context, error: Exception):
        """エラー時のコールバック（サブクラスでオーバーライド可能）

        Args:
            context: Blenderコンテキスト
            error: 発生した例外
        """
        import traceback
        traceback.print_exc()

        # エラー時の自動Undo
        restored = False
        if self._undo_on_error:
            restored = self._restore_state()

        if restored:
            self.report({'ERROR'}, f"Error: {str(error)} - state restored")
        else:
            self.report({'ERROR'}, f"Error: {str(error)} - restore failed, use Ctrl+Z")

    def _log_timing_complete(self):
        """処理完了時のタイミングログ出力"""
        now = time.perf_counter()
        if self._last_phase is not None:
            phase_elapsed = now - self._phase_start_time
            print(f"[Modal] phase '{self._last_phase}' completed in {phase_elapsed:.3f}s")
        elapsed = now - self._start_time
        print(f"[Modal] {self.bl_idname} total: {elapsed:.3f}s (yields: {self._batch_total_count})")

    def _log_timing_cancel(self):
        """キャンセル時のタイミングログ出力"""
        elapsed = time.perf_counter() - self._start_time
        print(f"[Modal] {self.bl_idname} cancelled after {elapsed:.3f}s (yields: {self._batch_total_count})")

    def _log_timing_error(self, error: Exception):
        """エラー時のタイミングログ出力"""
        elapsed = time.perf_counter() - self._start_time
        print(f"[Modal] {self.bl_idname} error after {elapsed:.3f}s (yields: {self._batch_total_count}): {error}")

    def _restore_state(self) -> bool:
        """処理開始前の状態に復元

        Returns:
            bool: 復元に成功した場合True
        """
        try:
            if bpy.ops.ed.undo.poll():
                bpy.ops.ed.undo()
                print("Modal operator: State restored via undo")
                return True
            else:
                print("Modal operator: Undo not available")
                return False
        except Exception as e:
            print(f"Modal operator: Failed to restore state: {e}")
            return False

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event) -> set[str]:
        """Modal処理を開始"""
        # インスタンス変数の初期化（Blenderオペレーターでは__init__使用不可）
        self._timer = None
        self._generator = None
        self._is_cancelled = False
        self._last_progress = None
        self._start_time = time.perf_counter()  # 処理時間計測用
        self._batch_total_count = 0  # 総yield数
        self._last_phase = None  # 前回のフェーズ名
        self._phase_start_time = self._start_time  # フェーズ開始時刻

        print(f"[Modal] {self.bl_idname} started")

        try:
            # 復元ポイントを作成（キャンセル/エラー時のUndo用）
            if self._undo_on_cancel or self._undo_on_error:
                bpy.ops.ed.undo_push(message=f"Before {self.bl_label}")

            # ジェネレータを作成
            self._generator = self.create_generator(context)
            if self._generator is None:
                return {'CANCELLED'}

            # タイマーを開始
            self._timer = context.window_manager.event_timer_add(
                self._timer_interval,
                window=context.window
            )

            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}

        except Exception as e:
            self.on_error(context, e)
            return {'CANCELLED'}

    def modal(self, context: bpy.types.Context, event: bpy.types.Event) -> set[str]:
        """Modalイベント処理"""
        # キャンセル判定
        if event.type in {'ESC', 'RIGHTMOUSE'} and event.value == 'PRESS':
            self._is_cancelled = True
            self._cleanup(context)
            self._log_timing_cancel()
            self.on_cancel(context)
            return {'CANCELLED'}

        # タイマーイベント
        if event.type == 'TIMER':
            try:
                # バッチ処理：時間制限内で複数のyieldを処理
                start_time = time.perf_counter()
                batch_count = 0

                while True:
                    # ジェネレータから次の進捗を取得
                    progress = next(self._generator)
                    self._last_progress = progress
                    batch_count += 1
                    self._batch_total_count += 1

                    # フェーズが変わったら前フェーズの処理時間をログ出力
                    if progress.phase and progress.phase != self._last_phase:
                        now = time.perf_counter()
                        if self._last_phase is not None:
                            phase_elapsed = now - self._phase_start_time
                            print(f"[Modal] phase '{self._last_phase}' completed in {phase_elapsed:.3f}s")
                        self._last_phase = progress.phase
                        self._phase_start_time = now

                    # 時間制限チェック（UIの応答性を維持するため）
                    elapsed = time.perf_counter() - start_time
                    if elapsed >= self._batch_time_limit:
                        break

                # バッチ処理後に進捗を更新（最後の進捗のみ表示）
                if self._last_progress:
                    self.on_progress(context, self._last_progress)

                return {'RUNNING_MODAL'}

            except StopIteration:
                # 処理完了
                self._cleanup(context)
                self._log_timing_complete()
                self.on_complete(context)
                return {'FINISHED'}

            except Exception as e:
                # エラー発生
                self._cleanup(context)
                self._log_timing_error(e)
                self.on_error(context, e)
                return {'CANCELLED'}

        # 処理中は入力をブロック（オブジェクト操作による不具合を防止）
        # RUNNING_MODALを返すことで他のイベントがBlenderに渡されなくなる
        return {'RUNNING_MODAL'}

    def _cleanup(self, context: bpy.types.Context):
        """クリーンアップ処理"""
        # タイマー停止
        if self._timer is not None:
            context.window_manager.event_timer_remove(self._timer)
            self._timer = None

        # ステータステキストをクリア
        context.workspace.status_text_set(None)

        # ジェネレータをクリア
        self._generator = None
