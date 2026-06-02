#!/usr/bin/env python3
"""
A股价格行为信号日报 — 入口

用法：
  1. 复制 config.example.py 为 config.py，填入你的数据源凭证
  2. python3 main.py
"""

import sys
import os
from datetime import date

# 确保能找到同目录下的包
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from analysis.engine import PriceActionEngine, Inference, AnalysisResult
from report.formatter import format_report


def main():
    today = date.today().strftime("%Y-%m-%d")

    # ── 加载配置 ──
    try:
        import config as cfg
    except ImportError:
        print("⚠️ 未找到 config.py，请复制 config.example.py 为 config.py")
        print("   然后填入你的数据源凭证")
        sys.exit(1)

    # ── 初始化数据源 ──
    if not hasattr(cfg, "DATA_SOURCE") or not cfg.DATA_SOURCE:
        print("⚠️ 请在 config.py 中配置 DATA_SOURCE")
        sys.exit(1)

    ds_type = cfg.DATA_SOURCE.get("type", "")
    data_source = None

    if ds_type == "ifind":
        from data_providers.ifind import IFiniDataSource
        data_source = IFiniDataSource(cfg.DATA_SOURCE["refresh_token"])
    elif ds_type == "lingqi":
        from data_providers.lingqi import LingQiDataSource
        data_source = LingQiDataSource(cfg.DATA_SOURCE["api_key"])
    elif ds_type == "tencent":
        from data_providers.tencent import TencentDataSource
        data_source = TencentDataSource()
    else:
        print(f"⚠️ 不支持的数据源类型: {ds_type}")
        print("   支持: ifind, lingqi, tencent")
        sys.exit(1)

    print(f"📡 使用数据源: {ds_type}  |  {today}")

    # ── 获取指数数据 ──
    index_results = []
    for code, name in cfg.INDEX_WATCHLIST.items():
        try:
            ctx = data_source.build_context(code, name)
            r = PriceActionEngine.analyze(ctx)
            r.etf_code = code
            r.etf_name = name
            index_results.append((name, r))
        except Exception as e:
            print(f"  ⚠️ {name}({code}): {e}")

    # ── 获取 ETF 数据 ──
    etf_results = []
    for code, name in cfg.ETF_WATCHLIST.items():
        try:
            ctx = data_source.build_context(code, name)
            r = PriceActionEngine.analyze(ctx)
            r.etf_code = code
            r.etf_name = name
            etf_results.append(r)
        except Exception as e:
            print(f"  ⚠️ {name}({code}): {e}")

    # ── 生成报告 ──
    report = format_report(index_results, etf_results, today)
    print("\n" + "=" * 60)
    print(report)

    # ── 保存 ──
    out_dir = os.path.expanduser("~/.hermes/cron/output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"pa_signal_{today}.txt")
    with open(out_path, "w") as f:
        f.write(report)
    print(f"\n📁 已保存: {out_path}")


if __name__ == "__main__":
    main()
