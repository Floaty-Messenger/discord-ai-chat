# Discord-Based AI Chat

**Put Claude, GPT (Codex) and DeepSeek in one Discord server and let them work together — from your PC or your phone.**

[中文说明](#中文说明) · [Detailed guide (Chinese)](docs/使用说明.md)

Each AI is its own Discord bot. You talk to them like a group chat; they @ each other, review each other's plans, and only change files after the others agree. It runs on your own Windows PC using the subscriptions you already have (Claude Code + Codex CLI) plus the cheap DeepSeek API.

## Features

- **Three AIs, three bots** – @ one, several, or none (it guesses who you mean). One Discord channel = one project folder with its own git repo.
- **Long-running sessions** – each AI keeps one conversation per project and only reads new messages, so it costs far fewer tokens than starting over every time.
- **Three-way approval before acting** – GPT proposes a `[方案]` (plan); the other AIs approve before it gets write access, full-PC access or Computer Use for that one turn. Hard-gated, not just a prompt rule.
- **Safety buttons** – AIs can't delete files themselves; they request it and you get an Approve/Deny button in Discord. Deleted files go to a recycle folder.
- **Delegate to DeepSeek** – Claude or GPT can hand bulky, simple work (translations, boilerplate pages, basic code) to DeepSeek with `[交给大肥鱼]`. It works in a copy of the project and sends back a diff; changes reach the real files only through GPT's approved plan.
- **Independent answers → cross-review → final summary** for multi-AI questions, so later AIs aren't anchored by the first answer.
- **Budget mode** – DeepSeek does the cheap first drafts, GPT applies them (medium reasoning effort, extra-high when all three agree a task is hard), Claude only reviews big changes.
- **Memory & auto-summary** – per-project memory files for each AI; old chat is compressed by DeepSeek in the background.
- **Web search for all three** (DeepSeek via the official Search & Fetch APIs, same as local DSH).
- **Results to your phone** – files the AIs produce are uploaded to Discord; detailed notifications with jump links.
- **Runs in the background**, auto-restarts, optional autostart, `!下线` to stop from your phone.

## Requirements

- Windows 10/11 (install.bat installs Python if it is missing)
- [Claude Code](https://code.claude.com/docs/en/setup) logged in with a Claude Pro/Max account (`claude auth login`)
- [Codex CLI](https://github.com/openai/codex) logged in with ChatGPT (`codex login`)
- A DeepSeek API key ([platform.deepseek.com](https://platform.deepseek.com))
- Three Discord bot tokens (one per AI)

> Uses each vendor's **official** command-line tools with your own account, for your own use. Don't share your bots with other people — that would be sharing your subscriptions, which the vendors' terms don't allow.

## Quick start

1. Download this repo and unzip it.
2. Double-click `install.bat` (installs Claude Code, Codex, Git and Python packages, then opens the logins).
3. Copy `config.example.json` → `config.json`, fill in the three bot tokens, your Discord user ID and the DeepSeek key.
4. Test locally: `start.bat --local` (set `"mock": true` first to test without using any quota).
5. Double-click `创建桌面快捷方式.bat`, then start **AI群聊 - Discord** from your desktop.

Full step-by-step guide (creating the bots, permissions, every command): [docs/使用说明.md](docs/使用说明.md)

## Status

Personal project, built for one user's own setup and shared as-is. The interface and bot messages are in Chinese. Issues and ideas are welcome.

License: MIT

---

## 中文说明

**把 Claude、GPT（Codex）、DeepSeek 拉进同一个 Discord 服务器，让它们像群聊一样协作。电脑、手机都能用。**

每个 AI 是一个独立的 Discord 机器人。你在频道里说话，它们之间互相 @、互相审查方案；改文件之前必须经过其他 AI 同意。程序跑在你自己的 Windows 电脑上，用的是你已有的订阅（Claude Code、Codex 命令行），加上按量付费、很便宜的 DeepSeek API。

### 主要功能

- **三个 AI，三个机器人**：@ 一个、几个，或者不 @（程序会猜你在跟谁说话）。一个 Discord 频道 = 一个项目文件夹（自带 git）
- **长期会话**：每个 AI 在每个项目里有一个持续的对话，之后只读新消息，大幅省 token
- **三方同意才动手**：GPT 先发 `[方案]`，其他 AI 同意后，才在那一轮获得写文件、完全访问、Computer Use 的权限（硬性限制，不只是提示词）
- **安全按钮**：AI 不能自己删文件，只能申请；你在 Discord 点按钮同意后，程序把文件移到回收站
- **派活给大肥鱼**：大小姐或 GPT 可以用 `[交给大肥鱼]` 把量大但简单的活（翻译、照模板写页面、基础代码）交给 DeepSeek。它在项目副本里做，做完把改动发回来检查；改动要进正式文件，仍然要走 GPT 的审核方案
- **独立作答 → 交叉讨论 → 最终汇总**：多人讨论时后发言的 AI 不会被前面的答案带偏
- **省额度模式**：DeepSeek 先起草，GPT 用中等强度落地（三方都同意任务很难时用极高），大小姐（Claude）只审大改动
- **记忆和自动摘要**、**三个 AI 都能联网**、**成果文件自动发到 Discord**、**后台运行、自动重启、开机自启**

### 需要准备

- Windows 10/11（没有 Python 的话 install.bat 会自动装）
- Claude Pro/Max 账号（命令行登录 `claude auth login`）
- ChatGPT 账号（`codex login`）
- DeepSeek API key
- 三个 Discord 机器人

> 用的是各家**官方**命令行工具和你自己的账号，仅供你自己使用。不要把机器人开放给别人用——那等于共享订阅，违反服务条款。

### 快速开始

1. 下载并解压本仓库
2. 双击 `install.bat`（自动安装 Claude Code、Codex、Git 和依赖，并打开登录）
3. 把 `config.example.json` 复制为 `config.json`，填三个机器人令牌、你的 Discord 用户 ID、DeepSeek key
4. 先本地测试：`start.bat --local`（先把 `"mock"` 设为 `true`，可以不消耗任何额度跑通流程）
5. 双击 `创建桌面快捷方式.bat`，之后从桌面打开「AI群聊 - Discord」

详细步骤（怎么建机器人、勾哪些权限、所有命令）：[docs/使用说明.md](docs/使用说明.md)

### 说明

这是个人项目，按作者自己的使用环境开发，原样分享。欢迎提 issue 和想法。

开源协议：MIT
