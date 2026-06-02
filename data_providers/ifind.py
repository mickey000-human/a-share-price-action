"""
iFinD（同花顺）数据源适配器

注意：这是示例数据源，用户需要用自己的 iFinD 账号和 refresh_token。
同花顺 iFinD 是商业产品，使用需遵守其服务条款。
"""

import json
import urllib.request
import ssl
from typing import List, Optional, Dict
from datetime import datetime, date, timedelta

from analysis.engine import Bar, Context


class IFiniDataSource:
    """iFinD HTTP API 数据源"""

    API_BASE = "https://quantapi.51ifind.com/api/v1"

    def __init__(self, refresh_token: str):
        self.refresh_token = refresh_token
        self._access_token: Optional[str] = None
        self.ssl_ctx = ssl.create_default_context()
        self._last_token_fetch: datetime = datetime.min

    def _get_access_token(self) -> str:
        """获取 access_token（7天有效，自动缓存）"""
        now = datetime.now()
        if self._access_token and (now - self._last_token_fetch).days < 6:
            return self._access_token

        req = urllib.request.Request(
            f"{self.API_BASE}/get_access_token",
            data=b"{}",
            headers={
                "Content-Type": "application/json",
                "refresh_token": self.refresh_token,
            },
            method="POST",
        )
        with urllib.request.urlopen(req, context=self.ssl_ctx, timeout=15) as resp:
            data = json.loads(resp.read())

        self._access_token = data["data"]["access_token"]
        self._last_token_fetch = now
        return self._access_token

    def _api_post(self, endpoint: str, payload: dict) -> dict:
        """调用 iFinD API"""
        token = self._get_access_token()
        req = urllib.request.Request(
            f"{self.API_BASE}/{endpoint}",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "access_token": token,
            },
            method="POST",
        )
        with urllib.request.urlopen(req, context=self.ssl_ctx, timeout=30) as resp:
            return json.loads(resp.read())

    def fetch_daily_bars(self, code: str, days: int = 90) -> List[Bar]:
        """获取日线K线"""
        end = date.today()
        start = end - timedelta(days=days + 10)  # 多取几天确保数据完整

        result = self._api_post("cmd_history_quotation", {
            "codes": code,
            "indicators": "close,open,high,low,changeRatio,amount",
            "startdate": start.strftime("%Y-%m-%d"),
            "enddate": end.strftime("%Y-%m-%d"),
            "functionpara": {"CPS": "6", "Interval": "D"},
        })

        bars: List[Bar] = []
        for tbl in result.get("tables", []):
            times = tbl.get("time", [])
            table = tbl.get("table", {})
            for i in range(len(times)):
                bars.append(Bar(
                    date=times[i],
                    open=table["open"][i],
                    high=table["high"][i],
                    low=table["low"][i],
                    close=table["close"][i],
                    volume=table.get("amount", [0])[i],
                    change_pct=table.get("changeRatio", [0])[i],
                ))
        return bars

    def fetch_realtime(self, codes: List[str]) -> Dict[str, dict]:
        """获取实时行情"""
        result = self._api_post("real_time_quotation", {
            "codes": ",".join(codes),
            "indicators": "latest,changeRatio,amount,high,low,open",
        })
        rt: Dict[str, dict] = {}
        for tbl in result.get("tables", []):
            code = tbl["thscode"]
            table = tbl["table"]
            rt[code] = {
                "latest": table.get("latest", [None])[0],
                "changeRatio": table.get("changeRatio", [None])[0],
                "amount": table.get("amount", [None])[0],
            }
        return rt

    def build_context(self, code: str, name: str, days: int = 90) -> Context:
        """构建分析上下文"""
        bars = self.fetch_daily_bars(code, days)
        return Context(bars=bars, etf_code=code, etf_name=name)

    def build_context_with_realtime(self, code: str, name: str,
                                     rt_data: Optional[dict] = None,
                                     days: int = 90) -> Context:
        """构建分析上下文（含实时数据覆盖）"""
        bars = self.fetch_daily_bars(code, days)
        if rt_data and code in rt_data and rt_data[code]["latest"]:
            rt = rt_data[code]
            bars[-1] = Bar(
                date=date.today().strftime("%Y-%m-%d"),
                open=bars[-1].open,
                high=max(bars[-1].high, rt["latest"]),
                low=min(bars[-1].low, rt["latest"]),
                close=rt["latest"],
                volume=rt["amount"] or bars[-1].volume,
                change_pct=rt["changeRatio"] or bars[-1].change_pct,
            )
        return Context(bars=bars, etf_code=code, etf_name=name)
