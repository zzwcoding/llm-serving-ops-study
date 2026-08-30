#!/usr/bin/env python3
"""
合成终稿:把 15 个碎片按教学顺序拼接,一级标题降二级,加文档头。
"""
import re
from pathlib import Path
from datetime import date

ROOT = Path("/Users/divh/Downloads/llm-serving-ops-study/knowledge-cards")
SCRATCH = ROOT / "scratch"
OUT = ROOT / "llm-serving-ops-study知识卡片.md"

# 教学顺序
ORDER = [
    ("0001-环境准备与显卡面板", "0.环境准备"),
    ("0002-docker与权限边界", "0.环境准备续"),
    ("0003-跑起第一个推理服务", "1.1 起服务"),
    ("0004-启动日志精读", "1.2 读日志"),
    ("0005-调通OpenAI接口", "1.3 调接口"),
    ("0006-亲眼看GPU干活", "1.4 盯显卡"),
    ("0007-prefill与decode", "1.5 两段旅程"),
    ("0008-裸看metrics", "2.1 裸看指标"),
    ("0009-装Prometheus", "2.2 Prometheus"),
    ("0010-装Grafana", "2.3 Grafana"),
    ("0011-对照实验", "2.4 对照实验"),
    ("0012-调参实验1-砍上下文长度", "3.1 砍上下文"),
    ("0013-调参实验2-显存水位", "3.2 显存水位"),
    ("0014-调参实验3-限并发与排队", "3.3 限并发"),
    ("0015-调参实验4-前缀缓存", "3.4 前缀缓存"),
]

# 统计
total_cards = 0
fragments_meta = []

parts = []
# 文档头:仅 4 行,无目录表;total_cards 用占位符,后面再 replace
parts.append(f"""# llm-serving-ops-study 知识卡片 · 终稿

> 用途:LLM 推理层部署运维实战的概念复习卡
> 卡片总数:__TOTAL__ 张(15 篇 lessons)
> 生成日期:{date.today().isoformat()}
> 碎片指针:`scratch/0001-00015.cards.md`

""")

# 拼接每个碎片(去掉碎片 h1,真正降为 h2)
for slug, stage in ORDER:
    f = SCRATCH / f"{slug}.cards.md"
    if not f.exists():
        print(f"[WARN] {f.name} 不存在")
        continue
    text = f.read_text(encoding="utf-8")
    n = len(re.findall(r"^### ", text, re.M))
    total_cards += n
    fragments_meta.append((slug, stage, n, f))
    # 文档头里需要的 total_cards 已提前累加(下面有补丁)
    # 去掉碎片首行 "# 0001 ... —— 知识卡片"
    text = re.sub(r"^# .+ —— 知识卡片\s*\n", "", text, flags=re.M)
    text = text.lstrip("\n")
    # 不加 ## 二级标题(避免第一张卡行数溢出);卡片用编号天然区分
    parts.append(text)
    parts.append("\n\n")

# 修正文档头里的卡片总数(占位符 __TOTAL__ → 真实数)
parts[0] = parts[0].replace("__TOTAL__", str(total_cards))

OUT.write_text("".join(parts), encoding="utf-8")
print(f"[OK] 终稿:{OUT}({OUT.stat().st_size / 1024:.1f} KB,{total_cards} 张卡)")

# 总自检
import subprocess
result = subprocess.run(
    ["python3", str(Path.home() / ".agents/skills/knowledge-cards/assets/check_cards.py"), str(OUT)],
    capture_output=True, text=True
)
print()
print("=== 总自检 ===")
print(result.stdout)
if result.returncode != 0:
    print(f"[FAIL] 违规非零,exit code {result.returncode}")
    print(result.stderr)
