# BaZi Ziping Skill | 子平八字

**排盘可核对，解读有温度。** 为你的 AI 助手装上子平八字：从四柱、十神到大运流年，结合你关心的事业、感情与生活问题，给出有依据、听得懂的解读。

## 快速开始

先安装 [Git](https://git-scm.com/) 和 [uv](https://docs.astral.sh/uv/getting-started/installation/)。选择你使用的智能体，在终端运行对应的一行命令：

| 宿主 | 一行安装（PowerShell、macOS/Linux 终端均可） |
| --- | --- |
| Codex | `git clone https://github.com/privilege404/bazi-ziping-skill.git "$HOME/.codex/skills/bazi-ziping-skill"` |
| Claude Code | `git clone https://github.com/privilege404/bazi-ziping-skill.git "$HOME/.claude/skills/bazi-ziping-skill"` |
| OpenClaw | `git clone https://github.com/privilege404/bazi-ziping-skill.git "$HOME/.agents/skills/bazi-ziping-skill"` |
| Hermes Agent | `git clone https://github.com/privilege404/bazi-ziping-skill.git "$HOME/.hermes/skills/bazi-ziping-skill"` |

首次运行需要下载 Python 依赖。安装后新开对话，试着说：

> 我是 1991 年 3 月 15 日 18:00 出生，女，出生地上海。请用子平八字帮我看看最近的工作状态，有哪些值得把握的机会？

喜欢命令行？在仓库目录直接排盘：

```bash
uv run python -m bazi_ziping --datetime 1991-03-15T18:00:00 --gender female --topic career
```

命令行输出简短排盘结果；在助手中使用时，会结合你的问题展开解读。加 `--format json` 可获取结构化结果，方便接入自己的工具。

## 你可以问什么

- **认识自己**：我的性格、长处和做事节奏有什么特点？
- **事业与学习**：什么样的工作方式更适合我？如何发挥学习优势？
- **感情与家庭**：怎样理解自己的相处模式与关系需求？
- **大运与流年**：最近处于怎样的阶段，有哪些值得留意的变化？

底层引擎计算四柱、十神和岁运，助手结合命盘依据与你交流。需要深入核对时，可以查看结构化结果与规则出处。

## 接入其他助手

采用通用 [Agent Skills](https://agentskills.io/specification) 格式，一份 skill 共用同一套排盘引擎。Codex、Claude Code、OpenClaw、Hermes 的安装命令见上表。

WorkBuddy、DeepSeek harness 等支持本地工具的个人助手，也可以通过 JSON 接口接入。具体方法见 [多端接入说明](docs/hosts.md)。

## 输入与排错

出生时间采用当地公历时间 `YYYY-MM-DDTHH:MM:SS`。`--gender` 用 `male` / `female`，用于大运顺逆。默认 `UTC+8` 与 `23:00` 换日；其他情况可传 `--timezone-offset`、`--day-boundary midnight`。需要平均真太阳时修正时，传 `--solar-time-mode mean_solar --longitude <经度>`。

```bash
uv run python -m bazi_ziping --datetime 1991-03-15T18:00:00 --gender female --target-year 2026 --topic relationship --format json
```

`--topic` 可选 `overview`、`career`、`wealth`、`relationship`、`education`、`health`、`family`。命令报找不到 `git`/`uv` 时先安装对应工具并重开终端；23:00 附近的出生时间请核对换日法。更完整的结构事实和规则卡见 [引擎说明](docs/engine.md)。

## 开源与隐私

MIT License。项目源自 [bazi-shaoweihua](https://github.com/privilege404/bazi-shaoweihua) 的计算引擎，V2 重新组织了入口和回答方式。排盘在本地运行；使用云端助手时，数据处理遵循对应平台的隐私设置。命理内容供文化探索与自我反思。
