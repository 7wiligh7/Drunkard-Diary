#!/usr/bin/env python3
"""从 data/beers.yml 生成 README.md 中的统计与酒单表格。

用法：
    python scripts/build.py          # 重新生成 README
    python scripts/build.py --check  # 仅检查 README 是否最新（CI 用）

只依赖 PyYAML。
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "beers.yml"
README_FILE = ROOT / "README.md"

# 风格 key -> 中文名。新增风格请同时更新 schema/beer.schema.json 与 CONTRIBUTING.md。
STYLES: dict[str, str] = {
    "draft": "鲜啤 / 原浆",
    "pale-lager": "淡色拉格",
    "dark-lager": "黑拉格",
    "pilsner": "皮尔森",
    "wheat": "小麦白啤",
    "witbier": "比利时白啤",
    "belgian-ale": "比利时艾尔",
    "trappist": "修道院啤酒",
    "ipa": "IPA",
    "stout": "世涛 / 黑啤",
    "sour": "酸啤 / 果啤",
    "ale": "艾尔（其他）",
    "non-alcoholic": "无醇啤酒",
}

STYLE_ORDER = {key: i for i, key in enumerate(STYLES)}

# 单瓶价格档位：1=<5 元，2=5-10 元，3=10-20 元，4=≥20 元
PRICE_LABELS = {1: "¥", 2: "¥¥", 3: "¥¥¥", 4: "¥¥¥¥"}

REQUIRED_FIELDS = ("id", "name", "style", "rating", "notes")

STATS_BEGIN = "<!-- STATS:BEGIN -->"
STATS_END = "<!-- STATS:END -->"
TABLE_BEGIN = "<!-- TABLE:BEGIN -->"
TABLE_END = "<!-- TABLE:END -->"


def load_data() -> list[dict]:
    if not DATA_FILE.exists():
        sys.exit(f"找不到数据文件：{DATA_FILE}")
    with DATA_FILE.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}

    beers = data.get("beers") or []
    if not isinstance(beers, list):
        sys.exit("data/beers.yml: `beers` 必须是一个列表")
    return beers


def validate(beers: list[dict]) -> list[str]:
    errors: list[str] = []
    seen_ids: set[str] = set()

    for i, beer in enumerate(beers, start=1):
        where = f"beers[{i}]"
        if not isinstance(beer, dict):
            errors.append(f"{where}: 条目必须是映射（key: value）")
            continue

        for field in REQUIRED_FIELDS:
            if beer.get(field) in (None, ""):
                errors.append(f"{where}: 缺少必填字段 `{field}`")

        beer_id = beer.get("id")
        if isinstance(beer_id, str):
            if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", beer_id):
                errors.append(f"{where}: id `{beer_id}` 只能包含小写字母、数字和连字符")
            if beer_id in seen_ids:
                errors.append(f"{where}: id `{beer_id}` 重复")
            seen_ids.add(beer_id)
            where = f"{where} ({beer_id})"

        style = beer.get("style")
        if style is not None and style not in STYLES:
            errors.append(f"{where}: 未知风格 `{style}`，可选值：{', '.join(STYLES)}")

        rating = beer.get("rating")
        if not isinstance(rating, int) or isinstance(rating, bool) or not 1 <= rating <= 5:
            errors.append(f"{where}: rating 必须是 1-5 的整数，当前为 {rating!r}")

        price = beer.get("price")
        if price is not None and price not in PRICE_LABELS:
            errors.append(
                f"{where}: price 只能是 1 / 2 / 3 / 4 或 null，当前为 {price!r}"
            )

        for field in ("abv", "plato"):
            value = beer.get(field)
            if value is not None and (not isinstance(value, (int, float)) or value < 0):
                errors.append(f"{where}: {field} 必须是非数字或 null，当前为 {value!r}")

        tags = beer.get("tags")
        if tags is not None and not isinstance(tags, list):
            errors.append(f"{where}: tags 必须是列表")

    return errors


def stars(rating: int) -> str:
    return "★" * rating + "☆" * (5 - rating)


def cell(value, empty: str = "—") -> str:
    if value is None or value == "":
        return empty
    text = str(value).replace("|", "\\|").replace("\n", " ")
    return text


def price_label(price: int | None) -> str:
    return PRICE_LABELS.get(price, "—")





def render_stats(beers: list[dict]) -> str:
    total = len(beers)
    avg = sum(b["rating"] for b in beers) / total if total else 0
    good = sum(1 for b in beers if b["rating"] >= 4)

    by_style: dict[str, list[int]] = defaultdict(list)
    for beer in beers:
        by_style[beer["style"]].append(beer["rating"])

    rows = [
        "| 风格 | 数量 | 平均分 |",
        "| --- | ---: | ---: |",
    ]
    for style in sorted(by_style, key=lambda s: (-len(by_style[s]), STYLE_ORDER[s])):
        ratings = by_style[style]
        rows.append(f"| {STYLES[style]} | {len(ratings)} | {sum(ratings) / len(ratings):.1f} |")

    return "\n".join(
        [
            f"共 **{total}** 款 · 平均 **{avg:.1f}** 星 · 好评（≥4★）**{good}** 款",
            "",
            *rows,
        ]
    )


def render_table(beers: list[dict]) -> str:
    ordered = sorted(
        beers,
        key=lambda b: (-b["rating"], STYLE_ORDER[b["style"]], b["name"]),
    )
    lines = [
        "| 名称 | 风格 | 产地 | 酒精度 | 麦汁浓度 | 价格档位 | 评分 | 风味关键词 | 品鉴笔记 |",
        "| --- | --- | --- | ---: | ---: | :---: | :---: | --- | --- |",
    ]
    for beer in ordered:
        origin = cell(beer.get("origin"))
        abv = "—" if beer.get("abv") is None else f"{beer['abv']}%"
        plato = "—" if beer.get("plato") is None else f"{beer['plato']}°P"
        price = price_label(beer.get("price"))
        tags = "、".join(beer.get("tags") or []) or "—"
        lines.append(
            "| {name} | {style} | {origin} | {abv} | {plato} | {price} | {stars} | {tags} | {notes} |".format(
                name=cell(beer["name"]),
                style=STYLES[beer["style"]],
                origin=origin,
                abv=abv,
                plato=plato,
                price=price,
                stars=stars(beer["rating"]),
                tags=cell(tags),
                notes=cell(beer["notes"]),
            )
        )
    return "\n".join(lines)


def replace_block(text: str, begin: str, end: str, body: str) -> str:
    pattern = re.compile(
        re.escape(begin) + r".*?" + re.escape(end),
        re.DOTALL,
    )
    if not pattern.search(text):
        sys.exit(f"README.md 中找不到标记块：{begin} ... {end}")
    return pattern.sub(f"{begin}\n{body}\n{end}", text, count=1)


def build() -> str:
    beers = load_data()
    errors = validate(beers)
    if errors:
        print("数据校验失败：", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        sys.exit(1)

    text = README_FILE.read_text(encoding="utf-8")
    text = replace_block(text, STATS_BEGIN, STATS_END, render_stats(beers))
    text = replace_block(text, TABLE_BEGIN, TABLE_END, render_table(beers))
    return text


def main() -> None:
    parser = argparse.ArgumentParser(description="生成 README 中的统计与酒单")
    parser.add_argument(
        "--check",
        action="store_true",
        help="只检查 README 是否与数据一致，不写入文件",
    )
    args = parser.parse_args()

    generated = build()

    if args.check:
        current = README_FILE.read_text(encoding="utf-8")
        if current != generated:
            print("README.md 与 data/beers.yml 不一致，请运行：python scripts/build.py", file=sys.stderr)
            sys.exit(1)
        print("README 已是最新。")
        return

    README_FILE.write_text(generated, encoding="utf-8", newline="\n")
    print(f"已更新 {README_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()