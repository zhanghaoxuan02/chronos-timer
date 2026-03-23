"""
时间显示模块

提供格式化时间显示功能，支持多种时间格式输出。
"""

import time
from datetime import datetime, timedelta, timezone
from typing import Optional


def show_time(
    fmt: Optional[str] = None,
    timezone_offset: Optional[int] = None,
    unix: bool = False,
    friendly: bool = False,
) -> Optional[str]:
    """
    显示当前时间，支持多种输出格式。

    参数:
        fmt: 自定义时间格式字符串（strftime 格式），默认为 "%Y-%m-%d %H:%M:%S"
        timezone_offset: 时区偏移（小时），如 8 表示 UTC+8（北京时间），默认为本地时区
        unix: 是否返回 Unix 时间戳（秒）
        friendly: 是否返回友好格式，如 "2026年3月22日 星期日 19:43:00"

    返回:
        格式化的时间字符串，或 Unix 时间戳（当 unix=True 时）

    示例:
        >>> from chronos import show_time
        >>>
        >>> show_time()
        '2026-03-22 19:43:00'
        >>>
        >>> show_time(fmt="%H:%M:%S")
        '19:43:00'
        >>>
        >>> show_time(unix=True)
        1771774980
        >>>
        >>> show_time(friendly=True)
        '2026年3月22日 星期日 19:43:00'
        >>>
        >>> show_time(timezone_offset=0)
        '2026-03-22 11:43:00'
    """
    now = time.time()

    # 返回 Unix 时间戳
    if unix:
        return int(now)

    # 处理时区
    if timezone_offset is not None:
        tz = timezone(timedelta(hours=timezone_offset))
        dt = datetime.fromtimestamp(now, tz=tz)
    else:
        dt = datetime.now()

    # 友好格式（中文）
    if friendly:
        weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
        weekday = weekdays[dt.weekday()]
        return f"{dt.year}年{dt.month}月{dt.day}日 {weekday} {dt.hour:02d}:{dt.minute:02d}:{dt.second:02d}"

    # 自定义格式或默认格式
    if fmt is None:
        fmt = "%Y-%m-%d %H:%M:%S"

    return dt.strftime(fmt)


def format_duration(seconds: float) -> str:
    """
    将秒数格式化为人类可读的时长字符串。

    参数:
        seconds: 秒数（可以是浮点数）

    返回:
        格式化的时长字符串，如 "1h 23m 45s" 或 "123.45s"

    示例:
        >>> format_duration(65.5)
        '1m 5s'
        >>> format_duration(3661)
        '1h 1m 1s'
        >>> format_duration(0.5)
        '0.50s'
    """
    if seconds < 0:
        raise ValueError("秒数不能为负数")

    total = int(seconds)
    frac = seconds - total

    hours, remainder = divmod(total, 3600)
    minutes, secs = divmod(remainder, 60)

    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0 or not parts:
        if frac > 0 and not parts:
            parts.append(f"{seconds:.2f}s")
        else:
            parts.append(f"{secs}s")

    return " ".join(parts)
