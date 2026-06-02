"""
灵启数据（lingqi）数据源适配器

灵启是第三方财经数据平台，提供ETF/指数前复权日线。
使用前需注册账号获取API密钥。
"""

from typing import List, Dict, Optional
from datetime import datetime, date, timedelta
import json
import urllib.request
import ssl

from analysis.engine import Bar, Context


class LingQiDataSource:
    """灵启数据源"""

    def __init__(self, api_key: str, base_url: str = "https://api.lingqi.cn/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.ssl_ctx = ssl.create_default_context()

    def fetch_daily_bars(self, code: str, days: int = 90) -> List[Bar]:
        """获取日线K线（灵启API示例，需根据实际文档调整）"""
        end = date.today()
        start = end - timedelta(days=days + 10)

        # 这里填入灵启实际API调用
        # 以下是占位示例
        url = f"{self.base_url}/kline?code={code}&start={start}&end={end}&adjust=qfq"

        req = urllib.request.Request(
            url,
            headers={"Authorization": f"Bearer {self.api_key}"},
        )
        with urllib.request.urlopen(req, context=self.ssl_ctx, timeout=15) as resp:
            data = json.loads(resp.read())

        bars: List[Bar] = []
        for item in data.get("data", []):
            bars.append(Bar(
                date=item["date"],
                open=item["open"],
                high=item["high"],
                low=item["low"],
                close=item["close"],
                volume=item.get("amount", 0),
                change_pct=item.get("change_pct", 0.0),
            ))
        return bars

    def build_context(self, code: str, name: str, days: int = 90) -> Context:
        bars = self.fetch_daily_bars(code, days)
        return Context(bars=bars, etf_code=code, etf_name=name)
