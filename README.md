# Clipboard Sync

最精简的跨平台双机剪切板同步方案：

- 两台机器各自运行同一个 Python 脚本
- 本机剪切板变化后推送到 Azure Service Bus Queue
- 同时轮询 Queue，收到来自另一台机器的消息后写回本机剪切板
- 无需管理员权限
- 支持 macOS / Windows

## 为什么选 Service Bus Queue

相比 Event Hub：

- 更适合小消息、点对点消费
- 有显式 ack / complete 语义
- 实现简单
- 成本通常更适合这种低频个人同步场景

## 功能特性

- 文本剪切板同步
- 防回环（不会因为自己刚写入又立刻重新上报）
- 忽略自己发出的消息
- 纯用户态运行，无需管理员权限

## 目录

- `clipboard_sync.py` 主程序
- `requirements.txt` Python 依赖

## Azure 侧准备

1. 创建 Azure Service Bus namespace
2. 创建一个 queue，例如：`clipboard-sync`
3. 拿到连接字符串（推荐使用 queue 级别或最小权限 SAS）

## 本地运行方式

有两种方式：

### 方式 A：直接运行 Python

建议 Python 3.10+

```bash
python -m pip install -r requirements.txt
```

### 方式 B：运行已打包可执行文件（推荐给无 Python / 无管理员权限机器）

- Windows：可打包为单个 `clipboard-sync.exe`
- macOS：可打包为单个二进制或 `.app`
- 运行时不需要额外安装 Python

## 环境变量

需要设置：

- `SB_CONNECTION_STRING`：Service Bus 连接字符串
- `SB_QUEUE_NAME`：Queue 名称
- `DEVICE_ID`：当前设备唯一标识，例如 `macbook-sant` / `win-work`

可选：

- `POLL_INTERVAL`：本地剪切板轮询秒数，默认 `0.8`
- `RECV_WAIT_SECONDS`：接收端单次等待秒数，默认 `5`
- `SUPPRESS_SECONDS`：收到远端内容后，本地抑制再次上报的秒数，默认 `2.5`

## 运行

### Python 方式

```bash
export SB_CONNECTION_STRING='Endpoint=sb://...'
export SB_QUEUE_NAME='clipboard-sync'
export DEVICE_ID='macbook-sant'
python clipboard_sync.py
```

Windows PowerShell:

```powershell
$env:SB_CONNECTION_STRING = 'Endpoint=sb://...'
$env:SB_QUEUE_NAME = 'clipboard-sync'
$env:DEVICE_ID = 'win-sant'
python .\clipboard_sync.py
```

### 可执行文件方式

如果已经打包好：

macOS:

```bash
export SB_CONNECTION_STRING='Endpoint=sb://...'
export SB_QUEUE_NAME='clipboard-sync'
export DEVICE_ID='macbook-sant'
./dist/clipboard-sync
```

Windows CMD:

```bat
set SB_CONNECTION_STRING=Endpoint=sb://...
set SB_QUEUE_NAME=clipboard-sync
set DEVICE_ID=win-sant
clipboard-sync.exe
```

## 开机自启

### macOS

最省事：
- 先手动运行验证
- 之后可用 `LaunchAgent` 做用户级自启（不需要管理员权限）

### Windows

无管理员权限时：
- 放到当前用户的 Startup 文件夹
- 或用当前用户权限创建计划任务（若环境允许）

Startup 文件夹：

```text
shell:startup
```

把一个启动 `.bat` 放进去即可。

## 注意事项

- 当前版本只同步文本内容
- 图片/文件列表暂不处理，先保持最简
- 若两端同时频繁复制不同内容，后复制的内容会覆盖先前内容，这是符合剪切板同步预期的
- Queue 会保留消息直到被消费；本程序按“收到并处理后 complete”工作

## 安全建议

- 不要直接使用 RootManageSharedAccessKey 到处散发
- 最好单独建一个仅用于这个程序的 SAS policy
- 剪切板可能包含密码/令牌/隐私内容，请只在你信任的 Azure 资源里使用
