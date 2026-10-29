# BaZi Ziping Skill | 子平八字

**排盘可核对，解读有温度。** 这是一个可供 AI 助手调用的本地子平八字 skill：先用 Python 计算四柱和命盘线索，再用自然语言回答你真正关心的问题。不把命理象意说成已经发生的事实，也不把它包装成确定性预测。

## 快速开始

先安装 [Git](https://git-scm.com/) 和 [uv](https://docs.astral.sh/uv/getting-started/installation/)，并确保你的助手有**本地文件读取和命令执行能力**。选你的宿主，在终端运行一行命令：

| 宿主 | 一行安装（PowerShell、macOS/Linux 终端均可） |
| --- | --- |
| Codex | `git clone https://github.com/privilege404/bazi-ziping-skill.git "$HOME/.codex/skills/bazi-ziping-skill"` |
| Claude Code | `git clone https://github.com/privilege404/bazi-ziping-skill.git "$HOME/.claude/skills/bazi-ziping-skill"` |
| OpenClaw | `git clone https://github.com/privilege404/bazi-ziping-skill.git "$HOME/.agents/skills/bazi-ziping-skill"` |
| Hermes Agent | `git clone https://github.com/privilege404/bazi-ziping-skill.git "$HOME/.hermes/skills/bazi-ziping-skill"` |

首次运行需要下载 Python 依赖。安装后新开对话，试着说：

> 请用子平八字帮我看看最近的工作状态。我是 1991 年 3 月 15 日 18:00 出生，女，出生地在东八区。先排盘，再根据证据讲，不要给确定性预言。

也可以不通过 AI，直接在仓库目录核对计算入口：

```bash
uv run python -m bazi_ziping --datetime 1991-03-15T18:00:00 --gender female --topic career
```

它会给出简短排盘线索。加 `--format json` 可得到结构化结果，供其他 agent 的工具层调用。自然语言解读由助手依据 [SKILL.md](SKILL.md) 生成，CLI 本身不冒充真人咨询。

## 能做与不能做

- 计算四柱、十神、大运和指定流年，保留时区、换日和真太阳时选项。
- 为事业、关系、学习、健康、家庭等问题提供少量可回溯的命理线索；回答时区分计算事实、解释和未知。
- 不从八字确认真实学历、疾病、收入、婚姻状态或未来事件；不替代医疗、法律、投资等专业判断。
- 出生时辰不明确时，不用虚构的中午或其他时间补时柱。生辰默认在本地计算；交给云端助手时仍需遵守该平台的隐私规则。

## 接入其他助手

本项目遵循 [Agent Skills](https://agentskills.io/specification) 的 `SKILL.md` 形式，但**支持某个模型**与**宿主能执行本地排盘**是两回事。Claude、DeepSeek 或其他模型只有在其 agent/harness 提供本地命令工具时，才能调用同一 Python 入口。普通聊天窗口不能靠粘贴提示词执行本地程序。

OpenClaw、Hermes、Claude Code 的安装路径及未验证事项见 [多端接入说明](docs/hosts.md)。WorkBuddy、DeepSeek harness 和其他个人助手也可以把 JSON CLI 注册为工具；尚无统一的一键安装方式，不在此宣称已端到端适配。

## 输入与排错

出生时间采用当地公历时间 `YYYY-MM-DDTHH:MM:SS`。`--gender` 用 `male` / `female`，用于大运顺逆。默认 `UTC+8` 与 `23:00` 换日；其他情况可传 `--timezone-offset`、`--day-boundary midnight`。需要平均真太阳时修正时，传 `--solar-time-mode mean_solar --longitude <经度>`。

```bash
uv run python -m bazi_ziping --datetime 1991-03-15T18:00:00 --gender female --target-year 2026 --topic relationship --format json
```

`--topic` 可选 `overview`、`career`、`wealth`、`relationship`、`education`、`health`、`family`。命令报找不到 `git`/`uv` 时先安装对应工具并重开终端；23:00 附近的出生时间请核对换日法。更完整的结构事实和规则卡见 [引擎说明](docs/engine.md)。

## 开源与隐私

MIT License。项目源自 [bazi-shaoweihua](https://github.com/privilege404/bazi-shaoweihua) 的确定性计算引擎，V2 重新组织了入口和回答方式。评测实验和私有案例不随 skill 分发；请勿把真实姓名、生辰和私人经历提交到公开 issue。
