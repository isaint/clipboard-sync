# Packaging / Deployment

## 目标

让目标机器不需要安装 Python，也不需要管理员权限。

## 结论

- Windows 无 Python / 无管理员权限：**可以**，使用打包后的 `clipboard-sync.exe`
- macOS：同理可打包为单文件可执行
- 但注意：**不能在 Linux 直接产出可运行的 Windows `.exe` 并保证稳定**
  - 最稳妥方式是在一台已有 Python 的 Windows 机器上执行 `build-windows-exe.ps1`
  - 或者在 CI（GitHub Actions / Azure Pipelines）里打包 Windows 工件

## Windows 打包

在任意一台可用的 Windows + Python 环境执行：

```powershell
powershell -ExecutionPolicy Bypass -File .\build-windows-exe.ps1
```

输出：

```text
.\dist\clipboard-sync.exe
```

然后把以下两个文件拷到目标 Windows 机器：

- `clipboard-sync.exe`
- `run-windows.bat`

## Windows 免管理员启动

方式 1：双击 `run-windows.bat`

方式 2：放入用户 Startup 文件夹：

```text
%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
```

也可以运行：

```bat
windows-startup-install.bat
```

## macOS 打包

在 macOS 上执行：

```bash
./build-macos.sh
```

输出：

```text
./dist/clipboard-sync
```

然后准备：

- `clipboard-sync`
- `run-macos.sh`

## 密钥处理建议

不要把带管理权限的完整连接字符串提交到 git 或发到群里。
建议：

- 单独创建用于此程序的 SAS policy
- 权限尽量最小化
- 至少把连接字符串只写到本机启动脚本里，不入库
