# gello_software

`gello_software` 是 GELLO 主手的独立软件项目。本仓库在上游 GELLO 的基础上增加了七自由度状态读取、AgileX PiPER-X 遥操作、JS 定位和原始数据记录，并使用 uv 统一管理 Python、依赖、虚拟环境、锁文件和命令行入口。

> [!WARNING]
> `read` 只读取 GELLO，但 `follow`、`follow-record`、`movejs` 以及部分官方工作流会向真实机械臂发送命令。运行前必须固定设备、清空工作空间并确保急停按钮触手可及。

## （1）项目能力

- 通过 FTDI/Dynamixel Protocol 2.0 读取 GELLO J1～J6 与夹爪位置
- 通过 ZMQ 连接 `agilexrobotics`，控制 PiPER-X 六轴与 AGX 夹爪
- 以指定 `--hz` 运行跟随和原始 JSONL 数据记录
- 支持上游 YAML、ZMQ、相机和 MuJoCo 工作流
- 统一使用 `uv run gello COMMAND [OPTIONS]`，不再直接维护每个实验脚本的 Python 启动方式

详细实现、参数含义和故障排查见[开发与调试手册](docs/DEVELOPMENT.md)，上游原始说明保存在[官方 README](docs/README_OFFICIAL.md)，该文件不随本地架构调整而修改。

## （2）环境要求

- Ubuntu 22.04 或更新版本
- Git、curl、USB 串口访问权限和基础编译工具
- pyenv 和 Python 3.11；`.python-version` 声明项目版本
- uv
- GELLO 主手及 FTDI/Dynamixel 串口适配器
- PiPER-X 功能额外需要独立的 `agilexrobotics` 服务与 USB-CAN
- 仿真功能额外需要 MuJoCo Menagerie 资产 submodule

## （3）快速开始

### 1. 安装系统工具、pyenv 与 uv

```bash
sudo apt update
sudo apt install -y git curl build-essential
curl -LsSf https://astral.sh/uv/install.sh | sh
source "$HOME/.local/bin/env"
uv --version
```

### 2. 获取项目

不使用仿真时，普通 clone 即可：

```bash
git clone git@github.com:right-or-not/gello_software.git
cd gello_software
```

需要 MuJoCo 仿真时，一并拉取 Menagerie：

```bash
git clone --recurse-submodules git@github.com:right-or-not/gello_software.git
cd gello_software
```

已经 clone 的仓库可在之后补充资产：

```bash
git submodule update --init --recursive
```

DynamixelSDK 已作为锁定的 uv/PyPI 依赖安装，不再需要手动 clone `third_party/DynamixelSDK`。

### 3. 创建环境

Python 由 pyenv 安装和选择，uv 负责 `.venv` 和依赖。基础 GELLO 与 PiPER-X 功能：

```bash
requested_version="$(<.python-version)"
resolved_version="$(pyenv latest -k "$requested_version")"
pyenv install -s "$resolved_version"
interpreter="$(PYENV_VERSION="$resolved_version" pyenv which python)"
UV_NO_MANAGED_PYTHON=1 uv sync --frozen --python "$interpreter"
```

按需安装可选功能：

```bash
uv sync --extra camera
uv sync --extra simulation
uv sync --extra robots
uv sync --extra full
```

显式传递 pyenv 解释器并设置 `UV_NO_MANAGED_PYTHON=1`，可以防止 uv 自行下载 Python。`uv sync` 会根据 `uv.lock` 创建或更新 `.venv`，无需手动执行 `uv venv`、`uv pip install -e .` 或激活环境。日常命令统一通过 `uv run` 执行。

### 4. 配置串口权限

```bash
sudo usermod -aG dialout "$USER"
```

注销并重新登录后，重新连接 GELLO，检查稳定设备路径和权限：

```bash
ls -l /dev/serial/by-id/
test -r /dev/ttyUSB0 && test -w /dev/ttyUSB0 && echo "GELLO 权限正常"
```

推荐使用 `/dev/serial/by-id/...`，避免 `/dev/ttyUSB0` 随插拔顺序变化。

### 5. 确认端口映射

串口路径必须存在于 `src/gello/agents/gello_agent.py` 的 `PORT_CONFIG_MAP` 中。若设备路径不同，需要为实际硬件配置舵机 ID、offset、方向系数和夹爪端点；不要只替换未知串口路径后直接启动机械臂。

### 6. 只读验证 GELLO

```bash
uv run gello read \
  --gello-port /dev/serial/by-id/usb-FTDI_USB__-__Serial_Converter_FTBM4Z46-if00-port0
```

机器可读输出：

```bash
uv run gello read \
  --gello-port /dev/serial/by-id/usb-FTDI_USB__-__Serial_Converter_FTBM4Z46-if00-port0 \
  --json
```

## （4）命令行入口

查看所有命令：

```bash
uv run gello --help
uv run gello follow --help
```

| 命令 | 功能 | 依赖范围 |
| --- | --- | --- |
| `read` | 读取 GELLO 关节和夹爪 | 基础 |
| `follow` | GELLO 控制 PiPER-X | 基础 |
| `follow-record` | 跟随并记录原始 episode | 基础 |
| `movejs` | 通过 PiPER-X ZMQ/JS 定位 | 基础 |
| `launch-yaml` | 从 YAML 启动工作流 | 基础或配置对应 extra |
| `launch-nodes` | 启动机器人 ZMQ 服务 | `robots` |
| `camera-server`、`camera-client` | RealSense 服务和显示 | `camera` |
| `quick-run`、`run-env` | 上游通用工作流 | `full` |

`experiments/*.py` 暂时保留为兼容包装器，现有外部脚本仍可运行；新增使用和开发统一面向 `gello` CLI。

## （5）PiPER-X 最小联调

终端 1 启动 `agilexrobotics` 服务：

```bash
cd /path/to/agilexrobotics
./scripts/config_can.sh
uv run ag status
uv run ag-gello-server --hz 50
```

终端 2 启动 GELLO 客户端：

```bash
cd /path/to/gello_software
uv run gello follow \
  --gello-port /dev/serial/by-id/usb-FTDI_USB__-__Serial_Converter_FTBM4Z46-if00-port0 \
  --start-joints 0 0 0 0 0 0 \
  --hz 50
```

示例中的零位不能直接用于未知姿态。必须先理解启动对齐和 `--start-joints`，具体步骤见[开发与调试手册](docs/DEVELOPMENT.md)。

## （6）开发检查

```bash
uv sync --dev
uv run pytest -q
uv run ruff check src/gello/cli.py src/gello/paths.py tests experiments
```

## （7）常见问题

### 1. `ModuleNotFoundError: dynamixel_sdk`

确保命令在项目根目录通过 uv 执行，并恢复锁定环境：

```bash
uv sync --frozen
uv run python -c "import dynamixel_sdk; print(dynamixel_sdk.__file__)"
```

### 2. 串口存在但没有权限

```bash
groups
ls -l /dev/serial/by-id/
```

加入 `dialout` 后必须注销并重新登录。

### 3. 串口被占用

同一时间只能有一个程序访问 GELLO 串口：

```bash
lsof /dev/serial/by-id/usb-FTDI_USB__-__Serial_Converter_FTBM4Z46-if00-port0
```

### 4. 找不到 MuJoCo Menagerie

```bash
git submodule update --init --recursive
```

也可以通过 `GELLO_MENAGERIE_ROOT=/absolute/path/to/mujoco_menagerie` 使用外部资产目录。
