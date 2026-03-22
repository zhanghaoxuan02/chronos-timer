"""
秒表模块

提供精确的秒表计时功能，支持分段计时（Lap）和多种统计输出。
"""

import time
from typing import List, Optional, Tuple

from .display import format_duration


class Stopwatch:
    """
    秒表类，用于精确计时。

    支持启动、暂停、继续、重置操作，以及分段计时（Lap）功能。

    示例:
        >>> from chronos import Stopwatch
        >>>
        >>> sw = Stopwatch()
        >>> sw.start()
        >>> time.sleep(1.5)
        >>> sw.lap()  # 记录第一个分段时间
        >>> time.sleep(2.0)
        >>> sw.lap()  # 记录第二个分段时间
        >>> sw.stop()
        >>> print(sw.summary())
        >>> print(sw.elapsed_seconds())  # 3.5
    """

    def __init__(self, name: Optional[str] = None, auto_start: bool = False):
        """
        初始化秒表。

        参数:
            name: 秒表名称（用于日志输出）
            auto_start: 是否在创建时自动开始计时
        """
        self._name = name
        self._start_time: Optional[float] = None
        self._stop_time: Optional[float] = None
        self._elapsed: float = 0.0  # 已累计的暂停前时间
        self._running = False
        self._laps: List[Tuple[float, float]] = []  # (lap_elapsed, total_elapsed)

        if auto_start:
            self.start()

    def start(self) -> "Stopwatch":
        """
        启动秒表。如果秒表已在运行，则不做任何操作。

        返回:
            self（支持链式调用）
        """
        if self._running:
            return self
        self._start_time = time.perf_counter()
        self._stop_time = None
        self._running = True
        return self

    def stop(self) -> "Stopwatch":
        """
        停止秒表并记录最终时间。

        返回:
            self（支持链式调用）
        """
        if not self._running:
            return self
        self._stop_time = time.perf_counter()
        self._elapsed += self._stop_time - self._start_time
        self._running = False
        return self

    def pause(self) -> "Stopwatch":
        """
        暂停秒表（与 stop 相同，但语义上表示"暂停"以支持后续 resume）。

        返回:
            self（支持链式调用）
        """
        return self.stop()

    def resume(self) -> "Stopwatch":
        """
        恢复暂停中的秒表。

        返回:
            self（支持链式调用）
        """
        if self._running:
            return self
        self._start_time = time.perf_counter()
        self._running = True
        return self

    def reset(self) -> "Stopwatch":
        """
        重置秒表，清零所有计时数据。

        返回:
            self（支持链式调用）
        """
        self._start_time = None
        self._stop_time = None
        self._elapsed = 0.0
        self._running = False
        self._laps.clear()
        return self

    def lap(self) -> Tuple[float, float]:
        """
        记录一个分段时间（不停止秒表）。

        返回:
            (lap_time, total_time) 元组，单位为秒
            lap_time: 自上次 lap 以来的时间
            total_time: 自开始以来的总时间
        """
        if not self._running:
            raise RuntimeError("秒表未在运行，无法记录 lap")

        now = time.perf_counter()
        current_total = self._elapsed + (now - self._start_time)

        if self._laps:
            last_total = self._laps[-1][1]
            lap_time = current_total - last_total
        else:
            lap_time = current_total

        self._laps.append((lap_time, current_total))
        return (lap_time, current_total)

    def elapsed_seconds(self) -> float:
        """
        获取已计时总秒数。

        返回:
            已计时的总秒数（浮点数）
        """
        if self._running:
            return self._elapsed + (time.perf_counter() - self._start_time)
        return self._elapsed

    def is_running(self) -> bool:
        """秒表是否正在运行。"""
        return self._running

    @property
    def laps(self) -> List[Tuple[float, float]]:
        """
        获取所有分段记录。

        返回:
            [(lap_time, total_time), ...] 列表
        """
        return list(self._laps)

    @property
    def lap_count(self) -> int:
        """获取分段数量。"""
        return len(self._laps)

    def fastest_lap(self) -> Optional[Tuple[int, float, float]]:
        """
        获取最快的分段。

        返回:
            (lap_index, lap_time, total_time) 元组，如果没有分段则返回 None
        """
        if not self._laps:
            return None
        fastest = min(self._laps, key=lambda x: x[0])
        idx = self._laps.index(fastest)
        return (idx + 1, fastest[0], fastest[1])

    def slowest_lap(self) -> Optional[Tuple[int, float, float]]:
        """
        获取最慢的分段。

        返回:
            (lap_index, lap_time, total_time) 元组，如果没有分段则返回 None
        """
        if not self._laps:
            return None
        slowest = max(self._laps, key=lambda x: x[0])
        idx = self._laps.index(slowest)
        return (idx + 1, slowest[0], slowest[1])

    def summary(self) -> str:
        """
        生成秒表的统计摘要。

        返回:
            格式化的统计字符串
        """
        total = self.elapsed_seconds()
        lines = []

        if self._name:
            lines.append(f"秒表: {self._name}")
        lines.append(f"总时间: {format_duration(total)} ({total:.4f}s)")
        lines.append(f"状态: {'运行中' if self._running else '已停止'}")

        if self._laps:
            lines.append(f"\n分段记录 ({self.lap_count} 段):")
            lines.append(f"  {'序号':<6}{'分段':<16}{'累计':<16}")
            lines.append(f"  {'-'*38}")
            for i, (lap_time, cum_time) in enumerate(self._laps):
                marker = ""
                fastest = self.fastest_lap()
                slowest = self.slowest_lap()
                if fastest and fastest[0] == i + 1:
                    marker = " [最快]"
                elif slowest and slowest[0] == i + 1:
                    marker = " [最慢]"
                lines.append(
                    f"  Lap {i+1:<3}{format_duration(lap_time):<16}"
                    f"{format_duration(cum_time):<16}{marker}"
                )

            if len(self._laps) > 1:
                avg = sum(lt for lt, _ in self._laps) / len(self._laps)
                lines.append(f"\n  平均分段: {format_duration(avg)} ({avg:.4f}s)")

        return "\n".join(lines)

    def __repr__(self) -> str:
        status = "running" if self._running else "stopped"
        name = f" '{self._name}'" if self._name else ""
        return f"<Stopwatch{name} {status} {self.elapsed_seconds():.4f}s>"

    def __enter__(self) -> "Stopwatch":
        """支持 with 语句上下文管理。"""
        self.start()
        return self

    def __exit__(self, *args) -> None:
        """退出 with 语句时自动停止。"""
        self.stop()


class Timer:
    """
    简单计时器，用于测量代码块执行时间。

    示例:
        >>> from chronos import Timer
        >>>
        >>> # 方式一：上下文管理器
        >>> with Timer() as t:
        ...     time.sleep(1)
        >>> print(t.elapsed_seconds())

        >>> # 方式二：手动控制
        >>> t = Timer()
        >>> t.start()
        >>> time.sleep(1)
        >>> t.stop()
        >>> print(t.elapsed_seconds())
    """

    def __init__(self):
        self._sw = Stopwatch()

    def start(self) -> "Timer":
        """开始计时。"""
        self._sw.start()
        return self

    def stop(self) -> float:
        """
        停止计时并返回耗时。

        返回:
            计时秒数
        """
        self._sw.stop()
        return self._sw.elapsed_seconds()

    def elapsed_seconds(self) -> float:
        """获取已计时秒数。"""
        return self._sw.elapsed_seconds()

    def __enter__(self) -> "Timer":
        self._sw.start()
        return self

    def __exit__(self, *args) -> None:
        self._sw.stop()

    def __repr__(self) -> str:
        return f"<Timer {self._sw.elapsed_seconds():.4f}s>"
