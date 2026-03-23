"""
倒计时模块

提供灵活的倒计时功能，支持进度回调和自定义格式。
"""

import time
from typing import Callable, Optional

from .display import format_duration


def countdown(
    seconds: int,
    interval: float = 1.0,
    callback: Optional[Callable[[int, int], None]] = None,
    silent: bool = False,
    message: Optional[str] = None,
) -> None:
    """
    执行倒计时。

    参数:
        seconds: 倒计时总秒数
        interval: 每次更新的间隔时间（秒），默认 1.0
        callback: 每次更新时的回调函数，接收 (remaining, total) 参数
        silent: 是否静默模式（不打印进度）
        message: 倒计时开始前的提示消息

    返回:
        None

    示例:
        >>> from chronos import countdown
        >>>
        >>> countdown(5)
        倒计时: 5s
        倒计时: 4s
        倒计时: 3s
        倒计时: 2s
        倒计时: 1s
        时间到！

        >>> # 使用回调函数
        >>> def on_tick(remaining, total):
        ...     print(f"进度: {100 * (total - remaining) / total:.0f}%")
        >>> countdown(3, callback=on_tick)

        >>> # 自定义消息
        >>> countdown(10, message="休息时间")
    """
    if seconds <= 0:
        raise ValueError("倒计时秒数必须大于 0")
    if interval <= 0:
        raise ValueError("间隔时间必须大于 0")

    if message and not silent:
        print(message)

    if callback:
        callback(seconds, seconds)

    remaining = seconds
    while remaining > 0:
        if not silent:
            print(f"倒计时: {remaining}s")
        remaining -= 1
        if remaining > 0:
            time.sleep(interval)
            if callback:
                callback(remaining, seconds)
        else:
            # 最后一步也需要 sleep 完整的一秒
            time.sleep(interval)

    if not silent:
        print("时间到！")


def countdown_precise(
    seconds: float,
    callback: Optional[Callable[[float, float], None]] = None,
    silent: bool = False,
) -> None:
    """
    精确倒计时，使用 time.perf_counter() 获得更精确的计时。

    参数:
        seconds: 倒计时总秒数（支持浮点数，如 0.5 秒）
        callback: 每次更新时的回调函数，接收 (remaining, total) 参数
        silent: 是否静默模式

    返回:
        None

    示例:
        >>> from chronos.countdown import countdown_precise
        >>> countdown_precise(2.5)
    """
    if seconds <= 0:
        raise ValueError("倒计时秒数必须大于 0")

    start = time.perf_counter()
    total = seconds

    while True:
        elapsed = time.perf_counter() - start
        remaining = total - elapsed

        if remaining <= 0:
            break

        if callback:
            callback(remaining, total)

        time.sleep(0.01)  # 10ms 精度刷新

    if callback:
        callback(0, total)

    if not silent:
        print("时间到！")
