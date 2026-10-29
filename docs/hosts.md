# 多端接入说明

各宿主共用根目录的 `SKILL.md` 和同一计算入口：

```bash
uv run python -m bazi_ziping --datetime 1991-03-15T18:00:00 --gender female --target-year 2026 --topic overview --format json
```

在仓库根目录运行，确认 JSON 包含 `chart`、`core`、`topic` 和 `interpretation_limits`。调用端应把 JSON 交给模型，并遵循 `SKILL.md` 的证据和表达边界。不要让模型从记忆重排四柱。

## 支持 Agent Skills 的宿主

| 宿主 | 本地 skill 目录 | 说明 |
| --- | --- | --- |
| Codex | `~/.codex/skills/` | 安装后新开对话，提及“子平八字”或 skill 名称。 |
| Claude Code | `~/.claude/skills/` | 官方文档支持个人技能目录；需要本地命令权限。 |
| OpenClaw | `~/.agents/skills/` | 官方文档将其列为个人 agent skills；也支持 `~/.openclaw/skills/`。 |
| Hermes Agent | `~/.hermes/skills/` | 官方文档列为技能目录；需允许执行本地命令。 |

上表是安装/发现路径，不代表本项目已在每个宿主的所有版本完成端到端测试。安装时请将**整个仓库**克隆进去，不要只复制 `SKILL.md`：本地计算还需要 `bazi_ziping`、`bazi_shaoweihua` 和依赖。若目标目录已存在，先检查内容，不要直接覆盖。

参考：[Agent Skills 规范](https://agentskills.io/specification)、[Claude Code 技能](https://code.claude.com/docs/en/skills)、[OpenClaw 技能](https://docs.openclaw.ai/tools/skills)、[Hermes 技能](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills)。

## 其他个人助手与 harness

WorkBuddy、DeepSeek 模型所在的 agent harness，以及其他提供工具调用的个人助手，可把上面的 JSON 命令注册为本地工具。建议将 `datetime`、`gender`、`target_year`、`topic` 作为独立参数传给进程，不要把未经校验的用户输入拼成 shell 字符串。不同宿主的工具配置不同，本项目没有声称提供通用的原生插件。

普通豆包、Claude、DeepSeek 等**纯聊天界面**不能执行这个本地入口。没有命令工具时，模型只能解释已计算好的结果，不能说“已排盘”。如果宿主只能调用远程 API，则需自行部署受控服务；本项目目前没有托管 API。

计算在本机进行，但把 JSON 或问题发送给云模型时，出生信息可能离开本机。请按具体平台的隐私政策决定是否使用。
