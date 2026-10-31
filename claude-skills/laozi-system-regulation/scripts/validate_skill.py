#!/usr/bin/env python3
"""Run deterministic static validation for Laozi System Regulation Skill v2.0."""

from __future__ import annotations

import re
import sys
from pathlib import Path


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    checks: list[tuple[str, bool]] = []

    def check(label: str, condition: bool) -> None:
        checks.append((label, bool(condition)))

    required = [
        "SKILL.md", "README.md", "QUICK_START.md", "VERSION.md",
        "CHANGELOG.md", "BOOK_INFO.md", "SOURCE_MAP.md",
        "SKILL_REGISTRY.md", "SKILL_STANDARD_BASELINE.md", "examples.md",
        "tests.md", "VALIDATION_REPORT.md",
    ]
    for rel in required:
        path = root / rel
        check(f"required:{rel}", path.is_file() and path.stat().st_size > 0)

    children = [
        "01-wuwei-action", "02-know-when-to-stop", "03-soft-over-hard",
        "04-less-is-more", "05-reversal-thinking", "06-systemic-leadership",
        "07-stillness-clarity", "08-comprehensive-regulation",
        "09-momentum-timing",
    ]
    for child in children:
        for filename in ("SKILL.md", "examples.md", "tests.md"):
            path = root / "skills" / child / filename
            check(f"child-file:{child}/{filename}", path.is_file() and path.stat().st_size > 0)

    skill_texts: list[str] = []
    for child in children:
        text = (root / "skills" / child / "SKILL.md").read_text(encoding="utf-8")
        skill_texts.append(text)
        check(f"frontmatter-name:{child}", bool(re.search(r"(?m)^name: [a-z0-9-]+$", text)))
        check(f"frontmatter-description:{child}", bool(re.search(r"(?m)^description: .{40,}$", text)))

    source = (root / "SOURCE_MAP.md").read_text(encoding="utf-8")
    map_labels = [
        "01 过度干预诊断助手", "02 知止边界助手", "03 柔性策略助手",
        "04 减法决策助手", "05 反作用检查助手", "06 系统自运行助手",
        "07 守静澄清助手", "08 老子综合调节助手", "09 顺势时机助手",
    ]
    chapters = ["第60章", "第44章", "第36章", "第48章", "第40章", "第17章", "第16章", "第2章", "第8章"]
    for label, chapter in zip(map_labels, chapters):
        check(f"source-skill:{label}", label in source)
        check(f"source-chapter:{chapter}", chapter in source)

    root_skill = (root / "SKILL.md").read_text(encoding="utf-8")
    root_terms = [
        "【调用】", "【作用】", "【经典依据】", "【判断】", "【为什么】",
        "【最大风险】", "【解决方案】", "【推荐方案】", "【下一步】", "【反问】",
        "【已确认事实】", "【用户判断】", "【Skill 假设】", "【待验证】", "【已排除】", "【本轮新增】",
        "无为不是不行动", "减法不是永远少做", "柔弱不是软弱", "不争不是不竞争",
        "顺势不是随波逐流", "反作用不是万能解释", "系统自运行不是无人负责",
        "只推荐一个", "可观察切换条件", "先更新判断", "信息足够就停止追问",
        "默认 1 主", "最多 1 主 + 2 辅", "经典提供观察方法，现实事实决定结论",
    ]
    for term in root_terms:
        check(f"root-term:{term}", term in root_skill)

    all_files = [p for p in root.rglob("*") if p.is_file()]
    all_text = "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in all_files if p.suffix in {".md", ".yaml"})
    names = re.findall(r"(?m)^name: ([a-z0-9-]+)$", "\n".join([root_skill, *skill_texts]))
    test_text = (root / "tests.md").read_text(encoding="utf-8")
    test_ids = re.findall(r"(?m)^- (T\d{3}) ", test_text)
    version = (root / "VERSION.md").read_text(encoding="utf-8")
    readme = (root / "README.md").read_text(encoding="utf-8")
    report_path = root / "VALIDATION_REPORT.md"
    baseline = (root / "SKILL_STANDARD_BASELINE.md").read_text(encoding="utf-8")
    agent = (root / "agents" / "openai.yaml").read_text(encoding="utf-8") if (root / "agents" / "openai.yaml").is_file() else ""
    examples = (root / "examples.md").read_text(encoding="utf-8")
    misc = [
        ("all-files-nonempty", all(p.stat().st_size > 0 for p in all_files)),
        ("no-todo-placeholders", "TODO" not in all_text and "[TODO" not in all_text),
        ("machine-names-unique", len(names) == 10 and len(names) == len(set(names))),
        ("root-tests-at-least-120", len(test_ids) >= 120),
        ("root-test-ids-unique", len(test_ids) == len(set(test_ids))),
        ("version-is-v2.0", "当前版本：v2.0" in version),
        ("status-pending-human-review", "状态：待人工验收" in version),
        ("source-map-required-columns", all(x in source for x in ["经典名称", "章节", "主题", "原文短句", "白话解释", "核心方法", "对应子 Skill", "适用问题", "不适用问题", "可信状态"])),
        ("readme-version", "v2.0" in readme),
        ("baseline-version", "v1.5 Final" in baseline),
        ("agent-default-prompt", "$laozi-system-regulation" in agent),
        ("child-count-nine", len([p for p in (root / "skills").iterdir() if p.is_dir()]) == 9),
        ("output-order", root_skill.index("【调用】") < root_skill.index("【作用】") < root_skill.index("【经典依据】") < root_skill.index("【判断】")),
        ("source-map-data-rows", len([line for line in source.splitlines() if line.startswith("| 《道德经》")]) >= 11),
        ("three-manual-prompts", examples.count("## 示例 ") >= 5 and "推荐人工验收的 3 道题" in examples),
    ]
    for label, condition in misc:
        check(label, condition)

    # The suite intentionally contains exactly 120 discrete automatic checks.
    if len(checks) != 120:
        print(f"INTERNAL ERROR: expected 120 checks, built {len(checks)}")
        return 2
    failures = [label for label, ok in checks if not ok]
    for label in failures:
        print(f"FAIL: {label}")
    passed = len(checks) - len(failures)
    print(f"Automatic checks: {passed}/{len(checks)} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
