"""
投资组合追踪器 — 跟踪ETF持仓市值、盈亏、权重
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import date


@dataclass
class Position:
    code: str
    name: str
    shares: int       # 持仓股数
    cost: float       # 成本单价


@dataclass
class PortfolioSnapshot:
    date: str
    total_value: float
    total_cost: float
    total_pnl: float
    total_pnl_pct: float
    positions: List[dict]


class PortfolioTracker:
    """投资组合追踪器"""

    def __init__(self, positions: List[Position]):
        self.positions = {p.code: p for p in positions}

    def snapshot(self, prices: Dict[str, float]) -> PortfolioSnapshot:
        """生成组合快照"""
        total_value = 0.0
        total_cost = 0.0
        pos_list = []

        for code, pos in self.positions.items():
            price = prices.get(code, 0)
            value = price * pos.shares
            cost_total = pos.cost * pos.shares
            pnl = value - cost_total
            pnl_pct = ((price / pos.cost) - 1) * 100 if pos.cost else 0

            total_value += value
            total_cost += cost_total

            pos_list.append({
                "code": code,
                "name": pos.name,
                "price": price,
                "shares": pos.shares,
                "cost": pos.cost,
                "value": value,
                "pnl": pnl,
                "pnl_pct": round(pnl_pct, 2),
                "weight": 0,  # 稍后计算
            })

        total_pnl = total_value - total_cost
        total_pnl_pct = ((total_value / total_cost) - 1) * 100 if total_cost else 0

        # 计算权重
        for p in pos_list:
            p["weight"] = round(p["value"] / total_value * 100, 1) if total_value else 0

        return PortfolioSnapshot(
            date=date.today().strftime("%Y-%m-%d"),
            total_value=round(total_value, 2),
            total_cost=round(total_cost, 2),
            total_pnl=round(total_pnl, 2),
            total_pnl_pct=round(total_pnl_pct, 2),
            positions=pos_list,
        )

    @staticmethod
    def format_snapshot(snap: PortfolioSnapshot) -> str:
        """格式化输出"""
        lines = []
        lines.append(f"📊 **组合日报** — {snap.date}")
        lines.append("")
        lines.append(f"总市值: {snap.total_value:,.0f}  总成本: {snap.total_cost:,.0f}")
        arrow = "🟢" if snap.total_pnl >= 0 else "🔴"
        lines.append(f"总盈亏: {arrow} {snap.total_pnl:+,.0f} ({snap.total_pnl_pct:+.2f}%)")
        lines.append("")
        lines.append("| 标的 | 现价 | 持仓 | 成本 | 盈亏 | 权重 |")
        lines.append("|------|------|------|------|------|------|")
        for p in snap.positions:
            arrow = "🟢" if p["pnl"] >= 0 else "🔴"
            lines.append(
                f"| {p['name']} | {p['price']} | {p['shares']}股 | {p['cost']} | "
                f"{arrow}{p['pnl']:+,.0f}({p['pnl_pct']:+.1f}%) | {p['weight']}% |"
            )
        return "\n".join(lines)
