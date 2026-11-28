import json
from pathlib import Path

r = json.loads(Path("studies/smallcap_investability/task-registry.json").read_text())
labels = {
    "en": {
        "done": "Done (bounded deliverable)",
        "partial": "Partial",
        "ready": "Ready to start",
        "waiting": "Waiting for evidence",
    },
    "zh": {
        "done": "已完成限定交付",
        "partial": "部分完成",
        "ready": "可启动",
        "waiting": "等待证据",
    },
}
for lang, name in [("en", "README.md"), ("zh", "README.zh-CN.md")]:
    en = lang == "en"
    lines = [
        "# Small-cap research checklist" if en else "# 小微盘研究完整待办清单",
        "",
        ("[Chinese (Simplified)](README.zh-CN.md)" if en else "[English](README.md)"),
        "",
        r["statusMeaning"][lang],
        "",
        ("Reviewed: " if en else "复核日期：") + r["reviewedOn"],
        "",
        (
            "The machine-readable source is [task-registry.json](task-registry.json). Waiting means the stated gate is unmet, not that every relevant dataset is absent. No recurring job or prospective registration is created by this checklist."
            if en
            else "机器可读来源为[task-registry.json](task-registry.json)。“等待证据”表示所列门槛尚未满足，不表示所有相关数据都不存在。本清单不创建定时任务或前瞻注册。"
        ),
        "",
        (
            "| ID | Priority | Status | Task | Depends on |"
            if en
            else "| 编号 | 优先级 | 状态 | 任务 | 依赖 |"
        ),
        "| --- | --- | --- | --- | --- |",
    ]
    for t in r["tasks"]:
        lines.append(
            f"| [{t['id']}](#{t['id'].lower()}) | {t['priority']} | {labels[lang][t['status']]} | {t['title'][lang]} | {', '.join(t['dependsOn']) or '—'} |"
        )
    for t in r["tasks"]:
        lines += [
            "",
            f'<a id="{t["id"].lower()}"></a>',
            f"## {t['id']} · {t['title'][lang]}",
            "",
            f"{t['priority']} · {labels[lang][t['status']]} · {t['owner']}",
            "",
            ("Acceptance: " if en else "验收：") + t["acceptance"][lang],
            "",
            ("Next action: " if en else "下一步：") + t["nextAction"][lang],
        ]
        if t["gap"]:
            lines += ["", ("Unmet gate: " if en else "未满足门槛：") + t["gap"][lang]]
        if t["evidence"]:
            lines += [
                "",
                ("Evidence: " if en else "已有证据：")
                + " · ".join(f"[source {i + 1}]({url})" for i, url in enumerate(t["evidence"])),
            ]
    Path("studies/smallcap_investability", name).write_text("\n".join(lines) + "\n")
