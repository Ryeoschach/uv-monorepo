好的，各位 Python 开发者朋友们，前面有讲过uv的使用，今天我们来聊聊如何使用**uv**来管理我们的 Python 单体仓库（Monorepo）。

**什么是单体仓库？**

简单来说，单体仓库就是把多个相关的项目或库放在同一个代码仓库中进行管理。
在我们的这个例子中，我们有 `py-api`（一个 FastAPI 应用）、`py-commonlib`（一个共享的通用库）和 `py-core`（一个核心工具），它们都放在同一个 Git 仓库里。

**为什么在单体仓库中使用包管理器很重要？**

在一个单体仓库中，不同的项目或库之间往往存在依赖关系。例如，我们的 `py-api` 和 `py-core` 都依赖于 `py-commonlib`。包管理器可以帮助我们：

- **统一管理依赖:** 确保每个项目都使用正确且兼容的依赖版本。
- **隔离环境:** 为每个项目创建独立的虚拟环境，避免依赖冲突。
- **加速依赖安装:** 提高安装依赖的速度，尤其是在大型项目中。

**今天的主角：uv**

`uv` 是一个由 Rust 编写的 Python 包管理器。它的目标是提供一个**极快**且兼容 `pip` 和 `pip-tools` 的替代方案。与传统的 `pip` 相比，`uv` 在依赖解析和安装速度上通常有显著的提升。

**我们的项目结构概览**

使用uv创建三个嵌套项目
uv init py-commonlib --lib
uv init py-api
uv init py-core

值得注意的是，我在创建 **py-commonlib** 项目时使用了 `--lib` 选项标志。当使用该标志时，`src`目录用于存放 Python 模块。
如果不使用 `--lib` 标志，则默认使用 `--app` 选项，它会创建一个类似 **py-api** 和 **py-base** 的扁平结构。

看一下当前项目的结构

```
├── py-api
│   ├── README.md
│   ├── main.py
│   ├── pyproject.toml
├── py-commonlib
│   ├── README.md
│   ├── pyproject.toml
│   ├── src
│   │   └── py_commonlib
│   │       ├── __init__.py
│   │       ├── datetime_lib.py
│   │       └── py.typed
└── py-core
    ├── README.md
    ├── main.py
    ├── pyproject.toml
```

可以看到，每个子项目都有一个 `pyproject.toml` 文件，这是现代 Python 项目管理中用于声明项目依赖和构建配置的标准文件。

**关键文件内容**

- **`py-api/main.py`:** 一个简单的 FastAPI 应用，依赖于 `py-commonlib` 来获取 UTC 时间戳。
- **`py-commonlib/src/py_commonlib/datetime_lib.py`:** 包含一个 `get_utc_timestamp` 函数。
- **`py-core/main.py`:** 一个简单的 Python 脚本，也依赖于 `py-commonlib` 来获取 UTC 时间戳。


**如何使用 uv 管理我们的单体仓库**

虽然 `uv` 本身并没有像 `pdm` 或 `poetry` 那样内置的单体仓库管理命令，但我们可以结合 `uv` 的基本功能和一些简单的脚本来实现依赖管理。

**步骤 1: 确保安装了 uv**

如果你还没有安装 `uv`，可以使用 `pip` 来安装：

Bash

```
pipx install uv
```

**步骤 2: 在每个子项目中安装依赖**

导航到每个子项目（`py-api`、`py-commonlib`、`py-core`）的目录，并使用 `uv` 来安装该项目在 `pyproject.toml` 中声明的依赖。

例如，对于 `py-api`：

Bash

```
cd py-api
uv pip sync
cd ..
```

同样地，对 `py-commonlib` 和 `py-core` 执行相应的命令。

**注意:**

- `uv pip sync` 命令会根据 `pyproject.toml` 和 `uv.lock` 文件安装或更新依赖。如果 `uv.lock` 不存在，`uv` 会根据 `pyproject.toml` 解析依赖并生成 `uv.lock`。

**步骤 3: 处理项目间的依赖关系**

在我们的例子中，`py-api` 和 `py-core` 依赖于本地的 `py-commonlib`。有几种处理这种本地依赖关系的方法：

- **使用相对路径 (不推荐用于发布):** 你可以在 `py-api` 和 `py-core` 的 `pyproject.toml` 中使用相对路径来指定 `py-commonlib`。例如：

    ```
    [project]
    dependencies = [
        { path = "../py-commonlib", editable = true },
        "fastapi",
        "uvicorn",
    ]
    ```
    
    然后使用 `uv pip sync` 安装依赖。`uv` 会将 `py-commonlib` 以可编辑模式安装到 `py-api` 的虚拟环境中。
    
- **将 `py-commonlib` 发布到本地 PyPI 镜像或直接安装 (更适合构建和部署):**
    
    1. 在 `py-commonlib` 中构建 wheel 包。
    2. 将 wheel 包安装到 `py-api` 和 `py-core` 的虚拟环境中。

**步骤 4: 创建和激活虚拟环境**
直接使用uv run 命令，免去激活虚拟环境的步骤

cd py-commonlib/src/py_commonlib && uv run datetime_lib.py
cd py-core && uv run main.py
cd py-api && uv run uvicorn main:app --reload

**更进一步：使用脚本简化流程**

为了更方便地管理单体仓库的依赖，你可以编写一些简单的 shell 脚本来自动化安装所有子项目的依赖。例如，在仓库根目录下创建一个 `install_deps.sh` 文件：

Bash

```
#!/bin/bash

set -e

echo "Installing dependencies for py-commonlib..."
cd py-commonlib
uv pip sync
cd ..

echo "Installing dependencies for py-api..."
cd py-api
uv pip sync
cd ..

echo "Installing dependencies for py-core..."
cd py-core
uv pip sync
cd ..

echo "All dependencies installed."
```

然后运行 `chmod +x install_deps.sh` 使其可执行，并运行 `./install_deps.sh`。

**总结**

虽然 `uv` 专注于提供快速的依赖解析和安装，它本身并没有内置复杂的单体仓库管理功能。然而，通过结合 `uv` 的基本命令和 Python 的包管理标准（如 `pyproject.toml`）以及一些简单的脚本，我们仍然可以有效地管理 Python 单体仓库中的依赖关系。

在处理本地依赖时，使用可编辑的路径依赖对于开发阶段非常方便，而将共享库发布到本地镜像或直接安装则更适合构建和部署。

希望这个简单的讲解能够帮助你理解如何在你的 Python 单体仓库中使用 `uv` 进行依赖管理！`uv` 的速度优势在大型项目中会更加明显，不妨尝试一下，看看它是否能提升你的开发效率。
