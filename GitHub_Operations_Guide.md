
# GitHub 团队协作完整指南

---

## 一、基础概念

| 术语 | 什么意思 | 类比 |
|------|----------|------|
| **Repository** | 仓库，放代码的地方 | 就像一个共享文件夹 |
| **Clone** | 把远程仓库下载到本地 | 把共享文件夹复制到自己电脑 |
| **Commit** | 提交，保存当前修改 | 点击“保存”并写一句说明 |
| **Push** | 推送到远程仓库 | 把自己电脑的修改上传到共享文件夹 |
| **Pull** | 拉取远程更新 | 从共享文件夹下载别人的修改 |
| **Branch** | 分支，独立开发线 | 像每个人有自己的草稿本 |
| **Merge** | 合并分支 | 把草稿本的内容抄到正式本上 |

---

## 二、组员第一次使用：克隆仓库

### 2.1 克隆到本地（每人只做一次）

打开终端/Git Bash，执行：

```bash
# 进入你想放项目的文件夹
cd D:\code

# 克隆仓库（用你的仓库地址）
git clone https://github.com/wan719/Gesture-Based-Manipulation.git

# 进入项目文件夹
cd Gesture-Based-Manipulation
```

### 2.2 配置自己的身份（每人只做一次）
```bash
git config user.name "你的名字"        # 比如 git config user.name "张三"

git config user.email "你的邮箱@xx.com"  # 用真实邮箱
```
## 三日常工作流程
