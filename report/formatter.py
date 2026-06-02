"""
报告格式化器 — 将分析结果转为可读的文本报告
"""

from typing import List, Optional
from analysis.engine import AnalysisResult, Inference, TradeIdea


def format_report(
    index_results: List[tuple],
    etf_results: List[AnalysisResult],
    today_str: str,
) -> str:
    """生成完整日报"""
    lines = []
    lines.append(f"📊 **A股 ETF 价格行为信号日报**")
    lines.append(f"📅 {today_str}\n")

    # ── 大盘环境 ──
    lines.append("**【大盘环境】**")
    if index_results:
        for name, r in index_results:
            arrow = "🟢" if r.change_pct > 0 else "🔴"
            lines.append(f"{arrow} {name}: {r.close}  {r.change_pct:+.2f}%  |  周期:{r.cycle}")
    else:
        lines.append("（数据获取中）")
    lines.append("")

    # ── 信号池 ──
    signals = [r for r in etf_results if r.signal != "无信号"]
    watchers = [r for r in etf_results if r.signal == "无信号"]

    if signals:
        lines.append("**【信号池】**")
        for r in signals:
            arrow = "🟢" if r.change_pct > 0 else "🔴"
            idea = Inference.daily_outlook(r)
            lines.append(f"{arrow} **{r.etf_name}** ({r.etf_code})")
            lines.append(f"  收盘: {r.close}  {r.change_pct:+.2f}%  量比: {r.volume_ratio or 'N/A'}")
            lines.append(f"  信号: {r.signal} — {r.signal_reason}")
            lines.append(f"  周期: {r.cycle}  |  距20日高: {r.dist_from_high:.1f}%")
            lines.append(f"  支撑: {r.support}  阻力: {r.resistance}")
            lines.append(f"  均线: {r.ma_align}  (MA5:{r.ma5} MA20:{r.ma20})")
            lines.append(f"  💡 推演: {idea.action} — {idea.reason}")
            lines.append("")

    # ── 观察池 ──
    if watchers:
        lines.append("**【观察池】**")
        for r in watchers:
            arrow = "🟢" if r.change_pct > 0 else "🔴"
            lines.append(
                f"{arrow} {r.etf_name:8s}  {r.close:>7}  {r.change_pct:+.2f}%  "
                f"| vol:{r.volume_ratio or 'N/A'} 周期:{r.cycle}"
            )
        lines.append("")

    # ── 推演总结 ──
    lines.append("**【推演总结】**")
    if signals:
        primary = signals[0]
        idea = Inference.daily_outlook(primary)
        lines.append(f"关注: **{primary.etf_name}** ({primary.etf_code})")
        lines.append(f"信号: {primary.signal}")
        lines.append(f"建议: {idea.action}")
        lines.append(f"理由: {idea.reason}")
        if idea.entry_range:
            lines.append(f"入场: {idea.entry_range}")
        if idea.target:
            lines.append(f"目标: {idea.target}")
        if idea.stop_loss:
            lines.append(f"止损: {idea.stop_loss}")
    else:
        lines.append("池内无明确信号 — 市场处于平淡/等待状态")
        lines.append("最优策略：不交易，等待新信号出现")

    lines.append("")
    lines.append("---")
    lines.append("*本报告基于价格行为学框架，数据来源于第三方接口。*")
    lines.append("*内容仅供参考学习，不构成任何投资建议。*")

    return "\n".join(lines)
