#!/usr/bin/env python3
"""
结构质检 + 合并总册脚本。
- 质检:每个卡片 md 检查七段标题是否齐全 + 元数据(frontmatter)是否完整
- 合并:按主题顺序拼接,卡片 h1 降为 h2,加文档头
"""
import re
import sys
from pathlib import Path
from datetime import date

ROOT = Path("/Users/divh/Downloads/llm-serving-ops-study/interview-cards")
CARDS = ROOT / "cards"
ASSEMBLY = ROOT / "assembly"

# 主题顺序(按面试场景由浅入深)
TOPIC_ORDER = [
    ("T01", "推理框架 / vLLM / SGLang / PagedAttention"),
    ("T02", "KV Cache / 显存管理"),
    ("T03", "TTFT / 首 token 延迟"),
    ("T04", "TPOT / Decode / 流式输出"),
    ("T05", "量化 / FP8 / AWQ / GPTQ / INT8"),
    ("T06", "GPU / CUDA / 显存硬件"),
    ("T07", "压测 / Bench / 容量规划 / QPS"),
    ("T08", "监控 / Prometheus / Grafana / 指标"),
    ("T09", "Prefill / Decode / Continuous Batching / PD 分离"),
    ("T10", "前缀缓存"),
    ("T11", "推理优化综合题 / 推理服务 / 模型部署"),
]

REQUIRED_SECTIONS = [
    "一句话核心",
    "30 秒电梯回答",
    "2 分钟展开版",
    "项目证据锚点",
    "常见追问与应对",
    "缺口提示",
]

def check_card(path: Path) -> list[str]:
    """检查单张卡片是否结构合规"""
    text = path.read_text(encoding="utf-8")
    errors = []
    # frontmatter 必有 qid
    if not re.search(r"^---\s*\n.*qid:\s*\S+", text, re.M):
        errors.append("frontmatter 缺 qid")
    # 七段标题
    for sec in REQUIRED_SECTIONS:
        if sec not in text:
            errors.append(f"缺段:{sec}")
    return errors

def main():
    ASSEMBLY.mkdir(parents=True, exist_ok=True)

    # === 步4:结构质检 ===
    all_errors = {}
    total_cards = 0
    total_size = 0
    per_topic = {}

    for slug, label in TOPIC_ORDER:
        d = CARDS / slug
        if not d.exists():
            print(f"[WARN] {slug} 目录不存在(可能 batch 未完成)")
            per_topic[slug] = {"count": 0, "size": 0, "errors": 0}
            continue
        qs = sorted([p for p in d.iterdir() if p.suffix == ".md" and p.stem.startswith("q")])
        per_topic[slug] = {"count": len(qs), "size": 0, "errors": 0}
        for q in qs:
            errs = check_card(q)
            if errs:
                all_errors[q.name] = errs
                per_topic[slug]["errors"] += 1
            per_topic[slug]["size"] += q.stat().st_size
            total_cards += 1
            total_size += q.stat().st_size

    print("=" * 60)
    print(f"结构质检报告")
    print(f"  总卡数:{total_cards}")
    print(f"  总大小:{total_size / 1024:.1f} KB")
    print(f"  有错卡片:{len(all_errors)}")
    print()
    print("按主题统计:")
    for slug, label in TOPIC_ORDER:
        info = per_topic[slug]
        flag = "✓" if info["errors"] == 0 and info["count"] > 0 else ("⚠" if info["errors"] > 0 else "—")
        print(f"  {flag} {slug}({label[:24]}):{info['count']} 卡 / {info['size']/1024:.1f} KB / 错 {info['errors']}")

    if all_errors:
        print(f"\n=== 错误明细({len(all_errors)})===")
        for fname, errs in list(all_errors.items())[:20]:
            print(f"  {fname}: {'; '.join(errs)}")
        if len(all_errors) > 20:
            print(f"  ... 还有 {len(all_errors) - 20} 个")
        # 质检不过就不出 PDF
        print("\n[FAIL] 质检有错,中止合并")
        sys.exit(1)

    # === 步5:合并总册 ===
    out_md = ASSEMBLY / "面试答题卡·总册.md"
    out_pdf = ASSEMBLY / "面试答题卡·总册.pdf"

    parts = []
    parts.append(f"""# 面试答题卡 · 总册

> 项目:LLM 推理层部署运维实战(llm-serving-ops-study)
> 题库:小红书 Agent 面试题 · 关键词命中 106 题
> 模板:七段式主题卡(覆盖题目表 / 一句话核心 / 30s 电梯 / 2 分钟展开 / 项目证据锚点 / 常见追问 / 缺口提示)
> 生成日期:{date.today().isoformat()}

## 目录与统计

| 主题 | 题数 | 大小 |
|---|---|---|
""")
    for slug, label in TOPIC_ORDER:
        info = per_topic[slug]
        parts.append(f"| {slug} {label} | {info['count']} | {info['size']/1024:.1f} KB |\n")

    parts.append(f"\n**总计:{total_cards} 张卡 · {total_size/1024:.1f} KB**\n\n---\n\n")

    # 拼接各主题卡片
    for i, (slug, label) in enumerate(TOPIC_ORDER):
        d = CARDS / slug
        if not d.exists():
            continue
        # 主题封面页
        parts.append(f"# 主题 {i+1} · {label}({slug})\n\n")
        info = per_topic[slug]
        parts.append(f"> 共 {info['count']} 张卡 · {info['size']/1024:.1f} KB\n\n---\n\n")

        # 该主题下所有卡片(按 qid 排序)
        qs = sorted([p for p in d.iterdir() if p.suffix == ".md" and p.stem.startswith("q")])
        for q in qs:
            text = q.read_text(encoding="utf-8")
            # 卡片 h1 降为 h2(总册已经有 h1 了)
            text = re.sub(r"^# ", "## ", text, flags=re.M, count=1)
            parts.append(text)
            parts.append("\n\n---\n\n")

    out_md.write_text("".join(parts), encoding="utf-8")
    print(f"\n[OK] 总册已写出:{out_md}({out_md.stat().st_size/1024:.1f} KB)")
    print(f"[下一步] 转 PDF:{out_pdf}")

if __name__ == "__main__":
    main()
