# A股价格行为信号日报

基于价格行为学（Price Action）的 A 股 ETF 分析工具。

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
