"""
A股价格行为分析引擎 — 数据源无关的核心模块

输入标准化的OHLCV DataFrame，输出周期判断、信号检测、交易推演。
不关心数据从哪来（iFinD/灵启/腾讯/manual），只分析价格行为本身。
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum


# ─── 数据结构 ──────────────────────────────────────────

@dataclass
class Bar:
    """一根K线"""
    date: str          # YYYY-MM-DD
    open: float
    high: float
    low: float
    close: float
    volume: float = 0  # 成交额(元)或成交量
    change_pct: float = 0.0  # 涨跌幅%


@dataclass
class Context:
    """分析所需的全量历史数据"""
    bars: List[Bar]           # 日线（时间从旧到新）
    etf_code: str = ""
    etf_name: str = ""


class CyclePhase(Enum):
    TRADING_RANGE = "交易区间"
    BULL_NARROW = "多头窄通道"
    BULL_WIDE = "多头宽通道"
    BULL_WIDE_END = "多头宽通道(末端)"
    BEAR_BREAK = "空头突破"
    BEAR_CHANNEL = "空头通道"
    BEAR_NARROW = "空头窄通道"
    INSUFFICIENT = "数据不足"


class SignalType(Enum):
    NONE = "无信号"
    STRONG_BREAK = "强势突破"
    VOLUME_UP = "放量上攻"
    BREAK_DOWN = "⚠️破位下跌"
    VOLUME_DOWN = "放量下跌"
    VOLUME_STALL = "放量滞涨"
    SHRINK_RALLY = "缩量反弹"


@dataclass
class AnalysisResult:
    """分析结果"""
    # 当前K线
    close: float = 0.0
    change_pct: float = 0.0
    # 均线
    ma5: Optional[float] = None
    ma10: Optional[float] = None
    ma20: Optional[float] = None
    ma60: Optional[float] = None
    ma_align: str = "N/A"
    # 位置
    high_20d: float = 0.0
    low_20d: float = 0.0
    dist_from_high: float = 0.0  # % 距20日高
    pos_vs_ma5: float = 0.0      # % 距MA5
    # 量能
    amount: float = 0.0          # 亿
    volume_ratio: Optional[float] = None
    vol_percentile: int = 50     # 在历史中的分位数
    # 结构
    cycle: str = "数据不足"
    support: Optional[float] = None
    resistance: Optional[float] = None
    # 信号
    signal: str = "无信号"
    signal_reason: str = ""


# ─── 分析引擎 ─────────────────────────────────────────

class PriceActionEngine:
    """价格行为分析引擎"""

    @staticmethod
    def analyze(ctx: Context) -> AnalysisResult:
        bars = ctx.bars
        if len(bars) < 2:
            raise ValueError("至少需要2根K线")

        r = AnalysisResult()
        cur = bars[-1]
        r.close = cur.close
        r.change_pct = cur.change_pct

        closes = [b.close for b in bars]
        highs = [b.high for b in bars]
        lows = [b.low for b in bars]
        amounts = [b.volume for b in bars]
        changes = [b.change_pct for b in bars]

        # ── 均线 ──
        r.ma5 = _ma(closes, 5)
        r.ma10 = _ma(closes, 10)
        r.ma20 = _ma(closes, 20)
        r.ma60 = _ma(closes, 60)

        if r.ma5 and r.ma10 and r.ma20:
            if r.ma5 > r.ma10 > r.ma20: r.ma_align = "多头排列"
            elif r.ma5 < r.ma10 < r.ma20: r.ma_align = "空头排列"
            else: r.ma_align = "交叉缠绕"

        # ── 位置 ──
        high_20 = max(highs[-20:]) if len(highs) >= 20 else max(highs)
        low_20 = min(lows[-20:]) if len(lows) >= 20 else min(lows)
        r.high_20d = high_20
        r.low_20d = low_20
        r.dist_from_high = ((cur.close / high_20) - 1) * 100 if high_20 else 0
        r.pos_vs_ma5 = ((cur.close / r.ma5) - 1) * 100 if r.ma5 else 0

        # ── 支撑阻力 ──
        if len(highs) >= 10:
            r.resistance = max(highs[-20:]) if len(highs) >= 20 else max(highs[-10:])
            r.support = min(lows[-20:]) if len(lows) >= 20 else min(lows[-10:])

        # ── 量比（基于成交额） ──
        if len(amounts) >= 6:
            ma5_amt = sum(amounts[-6:-1]) / 5
            r.volume_ratio = round(cur.volume / ma5_amt, 2) if ma5_amt > 0 else None
        r.amount = round(cur.volume / 1e8, 1) if cur.volume else 0

        # ── 成交额分位数 ──
        if len(amounts) >= 20:
            sorted_vols = sorted(amounts)
            r.vol_percentile = int(
                sum(1 for v in sorted_vols if v < cur.volume) / len(sorted_vols) * 100
            ) if cur.volume else 50

        # ── 周期判断 ──
        r.cycle = PriceActionEngine._detect_cycle(changes, closes)

        # ── 信号判断 ──
        sig, reason = PriceActionEngine._detect_signal(
            cur.change_pct, r.volume_ratio, r.cycle
        )
        r.signal = sig
        r.signal_reason = reason

        return r

    @staticmethod
    def _detect_cycle(changes: List[float], closes: List[float]) -> str:
        """简易周期判断"""
        if len(changes) < 10:
            return "数据不足"

        recent_5 = changes[-5:]
        pos = sum(1 for c in recent_5 if c > 0)
        neg = sum(1 for c in recent_5 if c < 0)
        total_20 = sum(changes[-20:]) if len(changes) >= 20 else sum(changes)

        # 大阴线连续
        big_drops = sum(1 for c in recent_5 if c < -2)
        big_ups = sum(1 for c in recent_5 if c > 2)

        if total_20 > 8 and big_ups >= 2:
            return CyclePhase.BULL_WIDE_END.value
        elif total_20 > 5:
            return CyclePhase.BULL_WIDE.value
        elif total_20 < -8 and big_drops >= 2:
            return CyclePhase.BEAR_BREAK.value
        elif total_20 < -3:
            return CyclePhase.BEAR_CHANNEL.value
        elif abs(total_20) <= 3:
            return CyclePhase.TRADING_RANGE.value
        else:
            return CyclePhase.BULL_NARROW.value if total_20 > 0 else CyclePhase.BEAR_NARROW.value

    @staticmethod
    def _detect_signal(
        change_pct: float, vol_ratio: Optional[float], cycle: str
    ) -> tuple:
        """信号检测"""
        vr = vol_ratio if vol_ratio else 1.0

        if change_pct > 3:
            return SignalType.STRONG_BREAK.value, f"单日涨{change_pct:.1f}%"
        elif change_pct > 1.5 and vr > 1.3:
            return SignalType.VOLUME_UP.value, f"+{change_pct:.1f}% 量比{vr:.2f}"
        elif change_pct < -3:
            return SignalType.BREAK_DOWN.value, f"-{abs(change_pct):.1f}%"
        elif change_pct < -1.5 and vr > 1.3:
            return SignalType.VOLUME_DOWN.value, f"{change_pct:.1f}% 量比{vr:.2f}"
        elif abs(change_pct) < 0.5 and vr > 1.5:
            return SignalType.VOLUME_STALL.value, f"放量滞涨 量比{vr:.2f}"
        elif change_pct > 0 and vr < 0.7:
            return SignalType.SHRINK_RALLY.value, f"缩量反弹 量比{vr:.2f}"
        else:
            return SignalType.NONE.value, ""


# ─── 推演层 ──────────────────────────────────────────

@dataclass
class TradeIdea:
    action: str = "观望"
    symbol: str = ""
    entry_range: str = ""
    target: str = ""
    stop_loss: str = ""
    reason: str = ""
    confidence: str = "低"


class Inference:
    """基于分析结果的推演"""

    @staticmethod
    def daily_outlook(result: AnalysisResult) -> TradeIdea:
        idea = TradeIdea()

        if result.signal == "强势突破" or result.signal == "放量上攻":
            if result.dist_from_high > -3:
                # 接近前高
                idea.action = "观察，不追"
                idea.reason = f"接近20日高({result.high_20d})，追高风险大"
            else:
                idea.action = "等回调买入"
                idea.reason = f"放量上攻，等回调MA5({result.ma5})附近"
                idea.entry_range = f"~{result.ma5}" if result.ma5 else "观察"
                idea.target = f"{result.close * 1.03:.2f} (+3%)"
                idea.stop_loss = f"{result.close * 0.97:.2f} (-3%)"

        elif result.signal in ("⚠️破位下跌", "放量下跌"):
            if result.dist_from_high < -10:
                idea.action = "观察，可能超卖"
                idea.reason = f"距20日高-{abs(result.dist_from_high):.0f}%已超卖，等止跌信号"
            else:
                idea.action = "观望，不接刀"
                idea.reason = f"空头动能释放中，支撑{result.support}"

        elif result.signal == "缩量反弹":
            idea.action = "观望"
            idea.reason = "缩量反弹动能不足，等放量确认"

        else:
            idea.action = "观望"
            idea.reason = "无明确信号"

        return idea


# ─── 工具函数 ─────────────────────────────────────────

def _ma(values: List[float], period: int) -> Optional[float]:
    if len(values) < period:
        return None
    return sum(values[-period:]) / period
