# HandPilot 项目开发规范

## 一、项目基本信息

| 项目 | 内容 |
|------|------|
| 项目名称 | HandPilot：基于手势识别的虚拟机械狗交互控制系统 |
| 仓库地址 | [https://github.com/wan719/Gesture-Based-Manipulation](https://github.com/wan719/Gesture-Based-Manipulation-of-Virtual-Objects) |
| 技术栈 | Python + MediaPipe + OpenCV / Unity C# + UDP |
| 团队成员 | 组长：@wan719，组员：张思哲、秦爽一、梁博、谯金昕 |
| 项目周期 | 9周（2026年3月 - 5月） |

---

## 二、Git 使用规范

### 2.1 分支管理

| 分支 | 说明 | 谁可以用 |
|------|------|----------|
| `main` | 主分支，始终保持稳定可运行状态 | 只有组长可合并 |
| `dev` | 开发分支，用于集成各功能 | 所有人可合并到dev |
| `feature/手势识别` | 手势识别模块开发 | 组长/B |
| `feature/unity基础` | Unity场景和模型导入 | C/D |
| `feature/动画实现` | Unity动画开发 | C/D |
| `feature/通信联调` | UDP通信和联调 | E |
| `bugfix/xxx` | 修复特定bug | 谁发现谁建 |

### 2.2 提交信息规范

**格式**：


**类型说明**：

| 类型 | 适用场景 | 示例 |
|------|----------|------|
| `feat` | 新功能 | `feat(gesture): 实现握拳手势识别` |
| `fix` | 修复bug | `fix(unity): 修复动画切换卡顿问题` |
| `docs` | 文档更新 | `docs: 更新README中的分工说明` |
| `style` | 代码格式调整 | `style: 调整缩进和空格` |
| `refactor` | 代码重构 | `refactor: 将手势判断抽离为独立函数` |
| `test` | 测试相关 | `test: 增加握拳手势测试用例` |
| `chore` | 工具链调整 | `chore: 更新.gitignore` |

**示例**：eat(gesture): 实现握拳手势识别

基于21个关键点计算手指弯曲角度

添加规则判断逻辑

测试50次，准确率92%

### 2.3 提交频率要求
- **每天至少提交一次**（哪怕只是修改了一行）
- **每个功能点单独提交**（不要混在一起）
- 提交前先pull：`git pull --rebase origin dev`

### 2.4 常用Git命令速查

```bash
# 创建新分支
git checkout -b feature/xxx

# 切换分支
git checkout main

# 查看状态
git status

# 添加文件
git add 文件名    # 添加单个文件
git add .        # 添加所有修改

# 提交
git commit -m "type(module): 描述"

# 推送到远程
git push origin 分支名

# 拉取最新代码
git pull origin dev

# 合并分支（先切到目标分支）
git merge feature/xxx

三、代码规范
3.1 Python 规范（手势识别模块）
文件组织：
src/gesture/
├── __init__.py
├── hand_detector.py      # MediaPipe手部检测
├── feature_extractor.py  # 特征工程（距离、角度）
├── gesture_classifier.py # 规则分类器
├── ml_classifier.py      # 机器学习分类器
├── utils.py              # 工具函数
├── data/                 # 数据集
│   ├── fist/
│   ├── palm/
│   └── ...
└── tests/                # 测试脚本
