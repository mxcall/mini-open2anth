# 构建错误修复指南

## 问题描述

在 GitHub Actions 中运行构建时遇到以下错误：
```
error: Multiple top-level modules discovered in a flat-layout: ['main', 'test_client'].
```

## 原因分析

错误发生在执行 `pip install -e .` 时，setuptools 检测到项目根目录有多个 Python 文件（main.py 和 test_client.py），无法自动确定模块结构。

## 解决方案

### 1. 移除 `pip install -e .`

已经从工作流中移除这个步骤，因为：
- PyInstaller 打包不需要以开发模式安装项目
- 项目根目录有多个 Python 文件，不符合标准 Python 包结构
- 直接使用 `pip install -r requirements.txt` 就足够了

### 2. 修复的文件

#### `.github/workflows/build-release.yml`

**修改前：**
```yaml
- name: Install project
  run: pip install -e .
```

**修改后：**
```yaml
# 已删除此步骤
```

#### `.github/workflows/build-release.yml` (版本获取)

**修改前：**
```yaml
- name: Upload artifacts
  with:
    name: mini-open2anth-windows-${{ env.VERSION }}
```

**修改后：**
```yaml
- name: Get version
  id: version
  run: |
    # 从 pyproject.toml 提取版本号
    $version = (Select-String -Path pyproject.toml -Pattern 'version = "([^"]+)"').Matches[1].Groups[1].Value
    echo "VERSION=$version" >> $env:GITHUB_OUTPUT

- name: Upload artifacts
  with:
    name: mini-open2anth-windows-${{ steps.version.outputs.VERSION }}
```

#### `build.ps1`

**修改：**
- 添加了 `$ErrorActionPreference = "Stop"` 确保严格错误处理
- 在 CI 环境下自动跳过依赖安装

#### `build.bat`

**修改：**
- 简化了错误检查逻辑
- 添加了 CI 环境支持
- 移除了虚拟环境依赖
- 优化了输出信息

## 工作流触发条件

### 自动触发（推送标签）
```bash
git tag v1.0.0
git push origin v1.0.0
```

### 手动触发
1. 访问 GitHub 仓库的 **Actions** 页面
2. 选择 **"Build and Release"** 工作流
3. 点击 **"Run workflow"** 按钮

## 构建流程

1. **安装依赖** - 安装 requirements.txt 中的所有依赖
2. **安装 PyInstaller** - 用于创建 exe 文件
3. **构建可执行文件** - 运行 `build.ps1` 或 `build.bat`
4. **提取版本号** - 从 `pyproject.toml` 读取
5. **上传制品** - 保存到 GitHub Actions
6. **创建 Release** - 仅在推送标签时触发

## 测试

推送更改后：
```bash
git add .github/ build.ps1 build.bat BUGFIX.md
git commit -m "fix: remove pip install -e . to resolve module discovery error"
git push
```

然后手动触发工作流或在 GitHub 上推送标签测试。

## Token 配置

**默认不需要额外配置！**

GitHub Actions 自动提供 `GITHUB_TOKEN`，足以用于：
- ✅ 构建 Windows 可执行文件
- ✅ 创建 GitHub Release
- ✅ 上传构建制品

**仅在以下情况需要 Personal Access Token：**
- 发布到其他 GitHub 仓库
- 发布到 GitHub Packages
- 需要访问私有依赖

## 验证构建成功

构建成功后，您将在以下位置找到文件：
- **GitHub Actions** → Artifacts
- **Release** 页面（如果推送了标签）

输出文件：
- `mini-open2anth.exe` - 可执行文件
- `.env.example` - 配置示例（如果存在）

---

**状态：** ✅ 已修复并优化
