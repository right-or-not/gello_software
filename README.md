# gello_software

`gello_software` 是 GELLO 主手的软件项目。本仓库在上游 GELLO 的基础上增加了七自由度 GELLO 状态读取、AgileX PiPER-X 与 AGX 夹爪遥操作、JS 定位和原始数据记录功能。GELLO 通过 FTDI 串口与 Dynamixel 舵机通信，PiPER-X 扩展则通过 ZMQ 连接独立运行的 `agilexrobotics` 服务。

> [!WARNING]
> GELLO 状态读取本身不会移动从臂，但跟随、定位和记录脚本会向真实机械臂发送命令。运行硬件控制前必须固定机械臂、清空工作空间、确保急停按钮触手可及，并先完成本 README 中的只读 GELLO 验证。

## （1）文档导航

- [开发与调试手册](docs/DEVELOPMENT.md)：本仓库扩展、全部脚本参数、PiPER-X 联调、数据映射和故障排查
- [上游官方 README](docs/README_OFFICIAL.md)：原始 GELLO 项目的硬件、机器人和通用工作流说明

## （2）环境要求

- Ubuntu 或其他可访问 USB 串口的 Linux 系统
- Python 3.11（项目通过 `.python-version` 指定）
- Git、uv 和基础编译工具
- GELLO 主手、稳定供电和 FTDI/Dynamixel 串口适配器
- PiPER-X 跟随功能还需要同级的 `agilexrobotics` 项目及可用的 USB-CAN；只读取 GELLO 时不需要连接 PiPER-X

## （3）快速开始

### 1. 安装系统工具

在 Ubuntu 上执行：

```bash
sudo apt update
sudo apt install -y git curl build-essential
```

如果尚未安装 uv，可使用官方安装脚本：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source "$HOME/.local/bin/env"
uv --version
```

其他安装方式见 [uv 官方文档](https://docs.astral.sh/uv/getting-started/installation/)。

### 2. 获取项目

使用 SSH：

```bash
git clone git@github.com:right-or-not/gello_software.git
cd gello_software
```

未配置 GitHub SSH 密钥时可使用 HTTPS：

```bash
git clone https://github.com/right-or-not/gello_software.git
cd gello_software
```

### 3. 创建虚拟环境并安装依赖

本项目使用 `requirements.txt` 和 `setup.py`，没有 `pyproject.toml` 或 uv 锁文件。先创建 Python 3.11 虚拟环境，再安装依赖和当前项目：

```bash
uv python install 3.11
uv venv --python 3.11
uv pip install -r requirements.txt
uv pip install -e .
```

当前仓库的 GELLO 串口驱动还依赖 ROBOTIS DynamixelSDK。将其克隆到项目约定路径并以可编辑模式安装：

```bash
mkdir -p third_party
git clone https://github.com/ROBOTIS-GIT/DynamixelSDK.git third_party/DynamixelSDK
uv pip install -e third_party/DynamixelSDK/python
```

后续命令统一使用 `.venv/bin/python`，因此不要求激活虚拟环境。如需激活，可执行：

```bash
source .venv/bin/activate
```

### 4. 配置串口权限

将当前用户加入 Ubuntu 的 `dialout` 组：

```bash
sudo usermod -aG dialout "$USER"
```

随后注销并重新登录，使组权限生效。重新连接 GELLO 后查看稳定的设备路径：

```bash
ls -l /dev/serial/by-id/
```

检查当前终端是否已有读写权限：

```bash
test -r /dev/ttyUSB0 && test -w /dev/ttyUSB0 && echo "GELLO 权限正常"
```

推荐始终使用 `/dev/serial/by-id/...` 路径，而不是可能随插拔变化的 `/dev/ttyUSB0`。

### 5. 确认 GELLO 端口配置

串口路径必须存在于 `gello/agents/gello_agent.py` 的 `PORT_CONFIG_MAP` 中。当前 PiPER-X 工作区使用的配置键为：

```text
/dev/serial/by-id/usb-FTDI_USB__-__Serial_Converter_FTBM4Z46-if00-port0
```

如果你的 `by-id` 路径不同，需要先在 `PORT_CONFIG_MAP` 中新增对应配置，并根据实际 GELLO 确认舵机 ID、关节 offset、方向系数和夹爪端点；不要只把未知设备路径替换进去就直接控制机械臂。具体配置含义见[开发与调试手册](docs/DEVELOPMENT.md#5-关键数据映射)。

### 6. 进行只读 GELLO 验证

将下面的串口路径替换成 `ls -l /dev/serial/by-id/` 查到且已写入 `PORT_CONFIG_MAP` 的路径：

```bash
.venv/bin/python experiments/read_gello_joints.py \
  --gello-port /dev/serial/by-id/usb-FTDI_USB__-__Serial_Converter_FTBM4Z46-if00-port0
```

正常情况下会输出 J1～J6 的弧度、角度和归一化夹爪值。需要供脚本解析的输出时可添加 `--json`：

```bash
.venv/bin/python experiments/read_gello_joints.py \
  --gello-port /dev/serial/by-id/usb-FTDI_USB__-__Serial_Converter_FTBM4Z46-if00-port0 \
  --json
```

确认读取稳定后按 `Ctrl+C` 或等待单次读取结束。若出现 `-3001`，说明 Dynamixel 状态包接收超时，请先检查供电、串联线、公共 GND、波特率、舵机 ID 和串口占用；完整排查清单见[开发与调试手册](docs/DEVELOPMENT.md#6-dynamixel-通信与--3001)。

## （4）PiPER-X 跟随

PiPER-X 跟随需要同时准备本仓库和同级的 `agilexrobotics` 项目。先在终端 1 配置 CAN 并启动从臂服务：

```bash
cd /path/to/agilexrobotics
./scripts/config_can.sh
uv run ag status
uv run ag-gello-server --hz 50
```

确认服务端已经监听后，在终端 2 启动 GELLO 客户端：

```bash
cd /path/to/gello_software
.venv/bin/python experiments/piper_x_follow.py \
  --gello-port /dev/serial/by-id/usb-FTDI_USB__-__Serial_Converter_FTBM4Z46-if00-port0 \
  --start-joints 0 0 0 0 0 0 \
  --hz 50
```

`--start-joints` 必须与机械臂当前姿态和所选对齐方式匹配，不能在不了解其含义时照抄零值进行真实运动。推荐在完整 `robot/` 工作区使用父目录的 `start_gello_follow.sh`，由脚本执行设备检查、姿态对齐和退出回零。完整流程见[开发与调试手册](docs/DEVELOPMENT.md#1-一键启动-piper-x-跟随)。

## （5）开发检查

需要运行测试和静态检查时，先安装开发依赖：

```bash
uv pip install -r requirements_dev.txt
```

当前本地扩展的测试可执行：

```bash
.venv/bin/python -m pytest tests
```

更详细的文件职责、命令参数、数据记录、YAM 工作流和串口故障处理统一记录在[开发与调试手册](docs/DEVELOPMENT.md)中。

## （6）常见问题

### 1. `ModuleNotFoundError: dynamixel_sdk`

说明 DynamixelSDK 尚未安装到当前 `.venv`，或命令使用了系统 Python。回到项目目录执行：

```bash
uv pip install -e third_party/DynamixelSDK/python
.venv/bin/python -c "import dynamixel_sdk; print(dynamixel_sdk.__file__)"
```

### 2. 串口存在但没有权限

确认用户属于 `dialout` 组，并在加入组后完成注销和重新登录：

```bash
groups
ls -l /dev/serial/by-id/
```

### 3. 串口被占用

同一时间只能有一个程序访问 GELLO 串口。使用以下命令查看占用进程，不要在未确认进程用途时直接结束它：

```bash
lsof /dev/serial/by-id/usb-FTDI_USB__-__Serial_Converter_FTBM4Z46-if00-port0
```
