# 示例配置 —— 使用前复制为 config.py 并填入自己的数据源凭证
# config.py 已在 .gitignore 中，不会提交到仓库

# ── 数据源配置 ──
# 只需配置一个，框架自动适配

DATA_SOURCE = {
    # --- iFinD 同花顺 ---
    # "type": "ifind",
    # "refresh_token": "你的refresh_token",

    # --- 灵启数据 ---
    # "type": "lingqi",
    # "api_key": "你的灵启API密钥",

    # --- 腾讯行情（免费，无需凭证） ---
    # "type": "tencent",
}

# ── ETF 监控池 ──
# 格式：代码: 名称
ETF_WATCHLIST = {
    "510300.SH": "300ETF",
    "510500.SH": "500ETF",
    "159845.SZ": "1000ETF",
    "159995.SZ": "芯片ETF",
    "511520.SH": "国债ETF",
    "518880.SH": "黄金ETF",
    "588000.SH": "科创50ETF",
    "159915.SZ": "创业板ETF",
}

# ── 指数监控 ──
INDEX_WATCHLIST = {
    "000001.SH": "上证",
    "000688.SH": "科创50",
    "000300.SH": "沪深300",
    "399006.SZ": "创业板指",
}
