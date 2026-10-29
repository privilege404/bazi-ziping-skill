# 多端接入说明

各类智能体共用根目录的 `SKILL.md` 和同一计算入口。接入需要助手能够读取技能文件并运行本地命令：

```bash
uv run python -m bazi_ziping --datetime 1991-03-15T18:00:00 --gender female --target-year 2026 --topic overview --format json
```

在仓库根目录运行，返回的 JSON 包含 `chart`、`core`、`topic` 和 `interpretation_limits`。助手读取计算结果后，按照 `SKILL.md` 结合用户的问题生成解读。

## 支持 Agent Skills 的宿主

| 宿主 | 本地 skill 目录 | 说明 |
| --- | --- | --- |
| Codex | `~/.codex/skills/` | 安装后新开对话，提及“子平八字”或 skill 名称。 |
| Claude Code | `~/.claude/skills/` | 官方文档支持个人技能目录；需要本地命令权限。 |
| OpenClaw | `~/.agents/skills/` | 官方文档将其列为个人 agent skills；也支持 `~/.openclaw/skills/`。 |
| Hermes Agent | `~/.hermes/skills/` | 官方文档列为技能目录；需允许执行本地命令。 |

将**整个仓库**克隆到对应目录，即可保留技能说明、排盘引擎和依赖配置。安装后新开一次对话，告诉助手“请用子平八字帮我排盘”，并提供出生年月日时、性别和出生地。使用自定义配置或多个 profile 时，以当前助手配置的 skills 目录为准。

参考：[Agent Skills 规范](https://agentskills.io/specification)、[Claude Code 技能](https://code.claude.com/docs/en/skills)、[OpenClaw 技能](https://docs.openclaw.ai/tools/skills)、[Hermes 技能](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills)。

## 其他个人助手与 harness

WorkBuddy、DeepSeek 模型所在的 agent harness，以及其他提供工具调用的个人助手，可把上面的 JSON 命令注册为本地工具。将 `datetime`、`gender`、`target_year`、`topic` 作为独立参数传给进程，返回 JSON，再交给模型解读。

接入步骤：

1. 在助手运行环境中克隆仓库并安装 `uv`。
2. 将工作目录设为仓库目录，用参数数组调用上面的命令。
3. 将根目录 `SKILL.md` 作为技能说明，让助手读取 JSON 结果并回答。

使用 HTTP 工具的助手可以通过自行部署的 API 封装同一计算入口。

计算在本机进行，但把 JSON 或问题发送给云模型时，出生信息可能离开本机。请按具体平台的隐私政策决定是否使用。
