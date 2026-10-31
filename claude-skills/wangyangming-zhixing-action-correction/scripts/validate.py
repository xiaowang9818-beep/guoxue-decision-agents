#!/usr/bin/env python3
"""Static validation for 王阳明知行合一与行动纠偏 Skill v2.0."""

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
failures: list[str] = []
passed = 0


def check(condition: bool, label: str) -> None:
    global passed
    if condition:
        passed += 1
    else:
        failures.append(label)


required_files = [
    "SKILL.md",
    "README.md",
    "QUICK_START.md",
    "VERSION.md",
    "CHANGELOG.md",
    "BOOK_INFO.md",
    "SOURCE_MAP.md",
    "SKILL_REGISTRY.md",
    "SKILL_STANDARD_BASELINE.md",
    "examples.md",
    "tests.md",
    "VALIDATION_REPORT.md",
]

for rel in required_files:
    path = ROOT / rel
    check(path.is_file(), f"缺少文件: {rel}")
    check(path.is_file() and path.stat().st_size > 20, f"空或过短: {rel}")

skill_dirs = sorted(p for p in (ROOT / "skills").iterdir() if p.is_dir())
check(len(skill_dirs) == 8, "子 Skill 数量必须为 8")
check(len({p.name for p in skill_dirs}) == 8, "子 Skill ID 重复")

child_required_terms = [
    "## 职责",
    "## 经典来源",
    "## 流程",
    "## 输出要求",
    "## 强制边界",
    "SOURCE_MAP.md",
    "统一结构",
    "推荐",
    "下一步",
]

frontmatter_names: list[str] = []
for directory in skill_dirs:
    path = directory / "SKILL.md"
    check(path.is_file(), f"缺少子 Skill: {directory.name}/SKILL.md")
    text = path.read_text(encoding="utf-8") if path.is_file() else ""
    check(len(text) > 300, f"子 Skill 内容过短: {directory.name}")
    match = re.search(r"\A---\s*\nname:\s*([^\n]+)\ndescription:\s*([^\n]+)\n---", text)
    check(bool(match), f"YAML frontmatter 无效: {directory.name}")
    if match:
        name = match.group(1).strip()
        frontmatter_names.append(name)
        check(name == directory.name, f"name 与目录不一致: {directory.name}")
        check(len(match.group(2).strip()) >= 40, f"description 触发信息不足: {directory.name}")
    else:
        check(False, f"无法检查 name: {directory.name}")
        check(False, f"无法检查 description: {directory.name}")
    for term in child_required_terms:
        check(term in text, f"{directory.name} 缺少: {term}")
    check("TODO" not in text, f"{directory.name} 存在 TODO")

check(len(frontmatter_names) == len(set(frontmatter_names)), "YAML name 重复")

top = (ROOT / "SKILL.md").read_text(encoding="utf-8")
for label in [
    "【调用】",
    "【作用】",
    "【经典依据】",
    "【判断】",
    "【为什么】",
    "【最大风险】",
    "【解决方案】",
    "【推荐方案】",
    "【下一步】",
    "【反问】",
]:
    check(label in top, f"总 Skill 缺少输出标签: {label}")

semantic_terms = [
    "默认简洁",
    "普通问题优先约 500～900 中文字",
    "当前只推荐一个方案",
    "可观察切换信号",
    "不机械切换",
    "已确认事实",
    "用户判断",
    "Skill 推测",
    "待验证",
    "已排除",
    "本轮新增",
    "不得跨轮自动升级",
    "新证据可推翻",
    "允许混合归因",
    "信息足够就停止追问",
    "鲁莽不是知行合一",
    "致良知”不等于凭感觉",
    "心即理”不等于主观万能",
    "反省不等于自责",
    "行动不代替思考",
    "判断 → 行动 → 反馈 → 修正",
    "不展示评分",
    "1 个主 Skill",
    "最多 1 主 + 2 辅",
    "经典只提供方法，现实证据决定结论",
]
for term in semantic_terms:
    check(term in top, f"总 Skill 缺少统一规则: {term}")

source = (ROOT / "SOURCE_MAP.md").read_text(encoding="utf-8")
entries = re.findall(r"^## Z\d{2} ", source, re.M)
check(len(entries) >= 10, "SOURCE_MAP 条目少于 10")
for zid in [f"Z{i:02d}" for i in range(1, 11)]:
    check(f"## {zid} " in source, f"SOURCE_MAP 缺少 {zid}")
for field in [
    "经典 / 文献",
    "主题",
    "具体出处",
    "可信状态",
    "短原文",
    "白话解释",
    "核心方法",
    "对应子 Skill",
    "适用问题",
    "不适用问题",
]:
    check(source.count(field) >= 10, f"SOURCE_MAP 字段不完整: {field}")
check(source.count("【已核验】") >= 9, "已核验来源不足")
check("【待核验】" in source, "缺少待核验状态")
check("待核验内容只能" in source, "缺少待核验引用禁令")
check(source.count("https://zh.wikisource.org/") >= 9, "已核验来源链接不足")

registry = (ROOT / "SKILL_REGISTRY.md").read_text(encoding="utf-8")
for name in [
    "知行合一执行",
    "致良知决策",
    "事上磨炼",
    "反求诸己复盘",
    "立志与长期行动",
    "自我觉察",
    "内在标准",
    "综合成长助手",
]:
    check(name in registry, f"旧版能力未记录: {name}")
for new_name in [
    "知行差距诊断助手",
    "自我欺骗检查助手",
    "行动启动助手",
    "事上磨炼助手",
    "反省纠偏助手",
    "责任边界助手",
    "行动反馈助手",
    "王阳明综合行动助手",
]:
    check(new_name in registry, f"新版能力未注册: {new_name}")

all_markdown = "\n".join(p.read_text(encoding="utf-8") for p in ROOT.rglob("*.md"))
for forbidden in [
    "你内心觉得对，就是对",
    "只要你相信就可以",
    "世界都是你内心创造的",
    "所有问题都是自己的错",
    "只管做，别想",
]:
    check(forbidden not in all_markdown, f"出现禁止表述: {forbidden}")
check("v2.0" in (ROOT / "VERSION.md").read_text(encoding="utf-8"), "VERSION 版本错误")
check("## v2.0" in (ROOT / "CHANGELOG.md").read_text(encoding="utf-8"), "CHANGELOG 版本错误")
check("待人工验收" in (ROOT / "README.md").read_text(encoding="utf-8"), "README 状态错误")
check("待人工验收" in (ROOT / "VERSION.md").read_text(encoding="utf-8"), "VERSION 状态错误")
check("TODO" not in all_markdown, "文档中仍有 TODO")

print(f"PASS={passed}")
print(f"FAIL={len(failures)}")
for failure in failures:
    print(f"- {failure}")
sys.exit(1 if failures else 0)

