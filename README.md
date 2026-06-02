# A股价格行为信号日报

基于价格行为学（Price Action）的 A 股 ETF 分析工具。

## 输出示例

```
📊 A股 ETF 价格行为信号日报
📅 2026-06-02

【大盘环境】
🟢 上证: 4087 +0.46% | 周期:交易区间
🟢 科创50: 1691 +1.66% | 周期:多头宽通道
🟢 沪深300: 4916 +1.49% | 周期:多头宽通道
🟢 创业板指: 4058 +2.71% | 周期:多头宽通道(末端)

【信号池】
🔴 芯片ETF (159995)
  收盘: 2.399 +1.78%  量比:0.73
  信号: 缩量反弹 — 距20日高-12%
  推演: 观望，等放量确认

【观察池】
🟢 300ETF  4.938 +1.44% | vol:0.70 周期:交易区间
🟢 500ETF  8.419 +0.59% | vol:1.08 周期:交易区间
🟢 黄金ETF 9.411 +0.72% | vol:0.93 周期:交易区间
🔴 国债ETF 118.13 +0.10% | vol:0.62 周期:交易区间

【推演总结】
关注: 芯片ETF — 空头动能释放中
建议: 等收盘确认，不追
```

## 特点

- **数据源无关** — 支持 iFinD（同花顺）、灵启、腾讯行情等数据源，也可接入自定义数据
- **纯技术分析** — 只分析 K 线结构和量价关系，不含任何投资建议
- **A股本土化** — 内置 A 股滤镜（T+1、假突破识别、大盘环境压制等）
- **可组合** — 分析引擎、数据源、报告格式互相独立，可替换任意模块

## 快速开始

```bash
# 1. 克隆
git clone https://github.com/你的用户名/a-share-price-action.git
cd a-share-price-action

# 2. 配置数据源
cp config.example.py config.py
# 编辑 config.py 填入你的数据源凭证

# 3. 运行
python3 main.py
```

## 配置数据源

### iFinD（同花顺）

需要有同花顺 iFinD 数据接口账号。在 config.py 中：

```python
DATA_SOURCE = {
    "type": "ifind",
    "refresh_token": "你的refresh_token",
}
```

refresh_token 从 iFinD Windows 客户端的「超级命令 → 工具 → refresh_token 查询/更新」获取。

### 灵启数据

```python
DATA_SOURCE = {
    "type": "lingqi",
    "api_key": "你的灵启API密钥",
}
```

### 腾讯行情（免费）

无需凭证，直接使用：

```python
DATA_SOURCE = {
    "type": "tencent",
}
```

腾讯行情仅有日线 OHLCV，无前复权、无成交额分位数，分析精度受限。

## 项目结构

```
a-share-price-action/
├── main.py                    # 入口
├── config.example.py          # 配置示例
├── analysis/
│   └── engine.py              # 价格行为分析引擎（数据源无关）
├── data_providers/
│   ├── ifind.py               # iFinD 数据源
│   ├── lingqi.py              # 灵启数据源（TODO）
│   └── tencent.py             # 腾讯行情数据源（TODO）
└── report/
    └── formatter.py           # 报告格式化
```

## 分析框架

参考了 A 股指数价格行为学交易系统，输出六层结构：

1. **事实层** — 当前 K 线数据、量能
2. **结构层** — 市场周期、关键位
3. **信号层** — 信号类型与强度
4. **A股滤镜修正** — T+1 风险、假突破概率
5. **交易应对** — 动作、触发条件、失效条件
6. **置信度**

## 免责声明

本工具是个人学习项目，仅提供技术分析参考。
**不构成任何投资建议，不对任何交易行为负责。**
数据来源为第三方接口，使用请遵守相关服务条款。

## 支持项目

如果这个工具对你有帮助，可以请作者喝杯咖啡 ☕

<p align="center">
  <img src="assets/wechat_pay.jpg" width="200" alt="微信打赏">
</p>
