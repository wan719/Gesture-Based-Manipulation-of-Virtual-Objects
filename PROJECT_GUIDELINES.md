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
