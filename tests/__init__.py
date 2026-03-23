"""
chronos 单元测试
"""

import time
import unittest

from chronos import show_time, countdown, Stopwatch, Timer
from chronos.display import format_duration
from chronos.countdown import countdown_precise


class TestShowTime(unittest.TestCase):
    """测试时间显示功能。"""

    def test_default_format(self):
        """默认格式应返回 YYYY-MM-DD HH:MM:SS。"""
        result = show_time()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)
        parts = result.split(" ")
        self.assertEqual(len(parts), 2)
        self.assertIn("-", parts[0])
        self.assertIn(":", parts[1])

    def test_custom_format(self):
        """自定义格式应正常工作。"""
        result = show_time(fmt="%H:%M")
        self.assertIsNotNone(result)
        parts = result.split(":")
        self.assertEqual(len(parts), 2)
        self.assertTrue(0 <= int(parts[0]) <= 23)
        self.assertTrue(0 <= int(parts[1]) <= 59)

    def test_unix_timestamp(self):
        """Unix 时间戳应为整数。"""
        result = show_time(unix=True)
        self.assertIsInstance(result, int)
        self.assertGreater(result, 1700000000)

    def test_friendly_format(self):
        """友好格式应包含中文。"""
        result = show_time(friendly=True)
        self.assertIn("年", result)
        self.assertIn("月", result)
        self.assertIn("日", result)

    def test_timezone_offset(self):
        """时区偏移应正常工作。"""
        result = show_time(timezone_offset=0)
        self.assertIsNotNone(result)

    def test_timezone_offset_china(self):
        """UTC+8 时区偏移。"""
        result = show_time(timezone_offset=8)
        self.assertIsNotNone(result)


class TestFormatDuration(unittest.TestCase):
    """测试时长格式化。"""

    def test_seconds_only(self):
        self.assertEqual(format_duration(5), "5s")

    def test_minutes(self):
        self.assertEqual(format_duration(65), "1m 5s")

    def test_hours(self):
        self.assertEqual(format_duration(3661), "1h 1m 1s")

    def test_fractional(self):
        result = format_duration(0.5)
        self.assertIn("s", result)

    def test_negative_raises(self):
        with self.assertRaises(ValueError):
            format_duration(-1)


class TestStopwatch(unittest.TestCase):
    """测试秒表功能。"""

    def test_basic_timing(self):
        """基本计时精度测试。"""
        sw = Stopwatch()
        sw.start()
        time.sleep(0.1)
        sw.stop()
        elapsed = sw.elapsed_seconds()
        self.assertGreater(elapsed, 0.09)
        self.assertLess(elapsed, 0.3)

    def test_reset(self):
        """重置后时间应为 0。"""
        sw = Stopwatch()
        sw.start()
        time.sleep(0.1)
        sw.stop()
        sw.reset()
        self.assertEqual(sw.elapsed_seconds(), 0.0)

    def test_pause_resume(self):
        """暂停时间不应计入总时间。"""
        sw = Stopwatch()
        sw.start()
        time.sleep(0.1)
        sw.pause()
        time.sleep(0.2)
        sw.resume()
        time.sleep(0.1)
        sw.stop()
        elapsed = sw.elapsed_seconds()
        self.assertGreater(elapsed, 0.15)
        self.assertLess(elapsed, 0.35)

    def test_auto_start(self):
        """auto_start 应自动开始计时。"""
        sw = Stopwatch(auto_start=True)
        self.assertTrue(sw.is_running())
        sw.stop()

    def test_lap(self):
        """分段计时测试。"""
        sw = Stopwatch()
        sw.start()
        time.sleep(0.05)
        lap1 = sw.lap()
        time.sleep(0.05)
        lap2 = sw.lap()
        sw.stop()
        self.assertEqual(len(sw.laps), 2)
        self.assertGreater(lap2[1], lap1[1])

    def test_lap_when_not_running(self):
        """非运行状态下 lap 应抛出异常。"""
        sw = Stopwatch()
        with self.assertRaises(RuntimeError):
            sw.lap()

    def test_fastest_slowest_lap(self):
        """最快/最慢分段测试。"""
        sw = Stopwatch()
        sw.start()
        time.sleep(0.05)
        sw.lap()
        time.sleep(0.1)
        sw.lap()
        time.sleep(0.02)
        sw.lap()
        sw.stop()
        fastest = sw.fastest_lap()
        slowest = sw.slowest_lap()
        self.assertIsNotNone(fastest)
        self.assertIsNotNone(slowest)
        self.assertLess(fastest[1], slowest[1])

    def test_context_manager(self):
        """with 语句测试。"""
        with Stopwatch() as sw:
            time.sleep(0.1)
        elapsed = sw.elapsed_seconds()
        self.assertGreater(elapsed, 0.09)
        self.assertFalse(sw.is_running())

    def test_repr(self):
        """repr 测试。"""
        sw = Stopwatch(name="test")
        repr_str = repr(sw)
        self.assertIn("test", repr_str)
        self.assertIn("stopped", repr_str)

    def test_summary(self):
        """summary 输出测试。"""
        sw = Stopwatch(name="test")
        sw.start()
        sw.lap()
        sw.stop()
        summary = sw.summary()
        self.assertIn("test", summary)
        self.assertIn("分段记录", summary)


class TestTimer(unittest.TestCase):
    """测试简单计时器。"""

    def test_context_manager(self):
        """with 语句测试。"""
        with Timer() as t:
            time.sleep(0.1)
        self.assertGreater(t.elapsed_seconds(), 0.09)

    def test_manual(self):
        """手动控制测试。"""
        t = Timer()
        t.start()
        time.sleep(0.1)
        t.stop()
        self.assertGreater(t.elapsed_seconds(), 0.09)


class TestCountdown(unittest.TestCase):
    """测试倒计时功能。"""

    def test_basic_countdown(self):
        """基本倒计时测试。"""
        start = time.time()
        countdown(3, silent=True)
        elapsed = time.time() - start
        self.assertGreater(elapsed, 2.9)

    def test_countdown_with_callback(self):
        """带回调的倒计时测试。"""
        ticks = []

        def cb(remaining, total):
            ticks.append((remaining, total))

        countdown(3, callback=cb, silent=True)
        self.assertEqual(len(ticks), 3)
        self.assertEqual(ticks[0], (3, 3))
        self.assertEqual(ticks[1], (2, 3))

    def test_invalid_seconds(self):
        """非法秒数应抛出异常。"""
        with self.assertRaises(ValueError):
            countdown(0)
        with self.assertRaises(ValueError):
            countdown(-1)

    def test_precise_countdown(self):
        """精确倒计时测试。"""
        start = time.time()
        countdown_precise(0.2, silent=True)
        elapsed = time.time() - start
        self.assertGreater(elapsed, 0.15)


if __name__ == "__main__":
    unittest.main()
