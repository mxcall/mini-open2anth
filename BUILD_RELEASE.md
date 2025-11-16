# GitHub Actions 自动构建和发布指南

本项目已配置 GitHub Actions 工作流，能够自动构建 Windows 可执行文件并创建 GitHub Release。

## 📋 工作流触发条件

工作流会在以下情况下自动运行：

1. **推送版本标签**（推荐）
   ```bash
   # 推送版本标签（例如：v1.0.0）
   git tag v1.0.0
   git push origin v1.0.0

   # 或者使用 annotated tag（包含更多信息）
   git tag -a v1.0.0 -m "Release version 1.0.0"
   git push origin v1.0.0
   ```

2. **手动触发**
   - 访问 GitHub 仓库的 Actions 页面
   - 选择 "Build and Release" 工作流
   - 点击 "Run workflow" 按钮

## 🎯 工作流功能

### 自动构建流程

1. **环境准备**
   - 使用最新的 Windows Runner（Windows Server 2022）
   - 安装 Python 3.11
   - 缓存 pip 依赖以加快构建速度

2. **依赖安装**
   - 安装所有 Python 依赖（requirements.txt）
   - 安装 PyInstaller
   - 以开发模式安装项目

3. **构建可执行文件**
   - 运行 `build.ps1` PowerShell 脚本
   - 清理之前的构建文件
   - 使用 PyInstaller 和 `build.spec` 配置构建
   - 准备发布文件

4. **创建发布**
   - 自动从 `pyproject.toml` 获取版本号
   - 创建 GitHub Release
   - 上传可执行文件和配置文件

### 输出文件

构建完成后，将在 release 目录中生成以下文件：

- `mini-open2anth.exe` - Windows 可执行文件
- `.env.example` - 配置示例文件（如果存在）
- `.env` - 环境配置文件（如果存在）

## 🏗️ 本地构建

如果您想在本地构建可执行文件，可以使用以下方法：

### 方法 1：使用批处理脚本（Windows）
```cmd
build.bat
```

### 方法 2：使用 PowerShell 脚本（Windows）
```powershell
pwsh build.ps1
```

### 方法 3：使用 Shell 脚本（Linux/macOS/WSL）
```bash
./build.sh
```

### 方法 4：手动构建
```bash
# 安装依赖
pip install -r requirements.txt
pip install pyinstaller

# 使用 PyInstaller 构建
pyinstaller build.spec --clean
```

## 📦 版本管理

版本号从 `pyproject.toml` 文件中读取。例如：
```toml
[project]
name = "mini-open2anth"
version = "0.1.0"
```

推荐使用语义化版本控制：
- **补丁版本**：`1.0.0` → `1.0.1`
- **次要版本**：`1.0.1` → `1.1.0`
- **主要版本**：`1.1.0` → `2.0.0`

## 🚀 发布流程

### 自动发布（推荐）

1. 更新 `pyproject.toml` 中的版本号
2. 推送版本标签：
   ```bash
   git add pyproject.toml
   git commit -m "Bump version to v1.0.0"
   git tag v1.0.0
   git push origin v1.0.0
   ```
3. GitHub Actions 将自动构建并创建 Release

### 手动发布

1. 访问 GitHub 仓库的 Actions 页面
2. 选择 "Build and Release" 工作流
3. 点击 "Run workflow"
4. 工作流完成后，将自动创建 Draft Release

## 📝 Release 说明

GitHub Release 的说明包括：
- 发布标题和版本号
- 构建内容的详细列表
- 使用说明
- 构建时间戳

## ⚙️ 工作流配置

工作流文件位于：`.github/workflows/build-release.yml`

### 主要配置

- **触发器**：`push` 标签和 `workflow_dispatch`（手动触发）
- **运行环境**：Windows Server 2022
- **Python 版本**：3.11
- **缓存**：pip 依赖缓存
- **制品保留**：30天

## 🔧 故障排除

### 构建失败

1. **检查 Python 版本**
   - 确保 `pyproject.toml` 中指定的 Python 版本 >= 3.8

2. **检查依赖**
   - 确保 `requirements.txt` 中列出了所有必要的依赖
   - 检查是否有缺失的隐藏导入（`hiddenimports`）

3. **检查 PyInstaller 配置**
   - 确保 `build.spec` 文件中的路径正确
   - 检查 `datas` 字段中的文件是否存在

4. **查看构建日志**
   - 在 GitHub Actions 页面查看详细的错误日志

### 可执行文件无法运行

1. **检查 .env 文件**
   - 确保可执行文件目录中有 `.env` 或 `.env.example` 文件
   - 检查环境变量配置

2. **检查依赖**
   - 运行 `build.ps1` 时查看是否有警告信息
   - 某些依赖可能需要添加到 `build.spec` 的 `hiddenimports` 中

3. **重新构建**
   - 清理 `build` 和 `dist` 目录
   - 重新运行构建脚本

## 📊 性能优化

### 加速构建

1. **缓存依赖**
   - 工作流自动缓存 pip 依赖
   - 在本地构建前可以运行 `pip cache purge` 清理缓存

2. **并行构建**
   - PyInstaller 支持并行构建
   - 确保 `build.spec` 中配置正确

### 减小文件大小

1. **排除不需要的模块**
   - 在 `build.spec` 的 `excludes` 字段中添加不必要的模块

2. **UPX 压缩**
   - `build.spec` 中已启用 UPX
   - 可以通过 `upx_exclude` 排除特定文件

## 🔒 安全注意事项

- 可执行文件包含所有依赖，可能较大（通常 10-100 MB）
- Release 页面上的文件公开可见
- 建议在发布前测试可执行文件
- 对于敏感配置，使用 `.env` 文件而不是硬编码

## 📚 相关资源

- [PyInstaller 文档](https://pyinstaller.org/en/stable/)
- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [GitHub Release 文档](https://docs.github.com/en/repositories/releasing-projects-on-github)

---

**需要帮助？** 如果遇到问题，请在 GitHub 仓库中创建 Issue。
