# 计算引擎与证据边界

V2 保留了 V1 的 `bazi_shaoweihua` 计算包和 `references/` 规则卡。`bazi_ziping` 是面向 skill 用户的薄入口：计算命盘、选择一个主题、缩减证据，再交给宿主模型解释。

旧命令 `scripts/bazi_cli.py` 仍可用于 `chart`、`structure`、`report`、`reading`、`dossier` 和 `batch` 等深入核对场景。普通用户不需要依次运行这些命令。

证据层的强弱分数、格局、神煞和岁运触发属于启发式或候选信息。完整断事、最高学历、疾病诊断和确定性事件年份没有获得可靠验证；不能因为规则卡多就把这些内容说成事实。

本仓库不包含 `bazi-eval-lab` 的比赛题、私有出生资料、运行报告或选择题 scorer。V1 的详细设计与测试历史见原始仓库。

开发测试：

```bash
uv run --extra test pytest -q
```
