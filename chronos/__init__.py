"""
chronos - 优雅的 Python 时间工具包

以希腊时间之神 Chronos 命名，提供三大核心功能：
- show_time(): 显示当前时间，支持多种格式
- countdown(seconds): 倒计时，支持回调和静默模式
- Stopwatch: 秒表类，支持分段计时、暂停恢复、统计摘要
- Timer: 简洁的代码块计时器
"""

from .display import show_time
from .countdown import countdown
from .stopwatch import Stopwatch, Timer

__version__ = "1.0.0"
__all__ = ["show_time", "countdown", "Stopwatch", "Timer", "__version__"]
