#!/usr/bin/env python3
"""单页导读 HTML 的结构自检。

用法:
    python3 check_page.py /abs/path/page.html
    python3 check_page.py /abs/path/page.html --sections acts,world,parent

检查项:
  1. 文件大小
  2. 常见容器标签是否闭合
  3. 是否引用了外部资源（单文件要求）
  4. 本地链接/图片目标是否存在
  5. <table> 是否包在 .tablewrap 里（否则整页横向溢出）
  6. <svg> 是否有 viewBox 与 aria-label
  7. 必填板块 id 是否齐全
  8. 折叠卡数量与默认展开数量

退出码: 有 ERROR 时返回 1，仅 WARN 时返回 0。
"""

import argparse
import os
import re
import sys

TAGS = ["div", "section", "details", "article", "svg", "table", "dl", "ul", "ol",
        "style", "script", "g", "text", "a"]

DEFAULT_SECTIONS = ["oneline", "people", "acts", "chapters", "world", "words", "parent"]


def check(path, sections):
    errors, warns, notes = [], [], []
    try:
        src = open(path, encoding="utf-8").read()
    except OSError as exc:
        print("ERROR 无法读取文件: %s" % exc)
        return 1

    size_kb = len(src.encode("utf-8")) / 1024
    notes.append("文件大小 %.1f KB" % size_kb)
    if size_kb > 400:
        warns.append("文件大于 400KB，考虑精简 SVG 或拆分（单页建议 < 150KB）")

    # 2. 标签闭合
    for tag in TAGS:
        opened = len(re.findall(r"<%s[\s>]" % tag, src))
        closed = len(re.findall(r"</%s>" % tag, src))
        if opened != closed:
            errors.append("<%s> 未闭合: 开 %d / 闭 %d" % (tag, opened, closed))

    # 3. 外部资源
    external = re.findall(r"""(?:src|href)\s*=\s*["'](https?://[^"']+)""", src)
    external += re.findall(r"""@import\s+url\(["']?(https?://[^"')]+)""", src)
    if external:
        for url in sorted(set(external)):
            errors.append("引用了外部资源（单文件要求）: %s" % url)

    # 4. 本地链接
    base = os.path.dirname(os.path.abspath(path))
    for attr, target in re.findall(r"""(href|src)\s*=\s*["']([^"']+)["']""", src):
        if target.startswith(("#", "http://", "https://", "data:", "mailto:", "javascript:")):
            continue
        if target.strip() == "":
            continue
        if not os.path.exists(os.path.join(base, target.split("#")[0])):
            errors.append("%s 指向的文件不存在: %s" % (attr, target))

    # 5. table 包裹
    for m in re.finditer(r"<table[\s>]", src):
        if "tablewrap" not in src[max(0, m.start() - 400):m.start()]:
            warns.append("<table> 可能没包在 .tablewrap 里，窄屏会撑破整页")

    # 6. svg 属性
    for m in re.finditer(r"<svg([^>]*)>", src):
        attrs = m.group(1)
        if "viewBox" not in attrs:
            errors.append("<svg> 缺少 viewBox（无法自适应缩放）")
        if "aria-label" not in attrs:
            warns.append("<svg> 缺少 aria-label（无障碍）")

    # 7. 板块
    ids = set(re.findall(r"""id\s*=\s*["']([^"']+)["']""", src))
    for need in sections:
        if need not in ids:
            warns.append("缺少板块 id=#%s" % need)

    # 8. 折叠卡
    beats = len(re.findall(r"<details[^>]*class=\"[^\"]*beat", src))
    opened = len(re.findall(r"<details[^>]*\bopen\b", src))
    if beats:
        notes.append("章节折叠卡 %d 张，HTML 内默认展开 %d 张" % (beats, opened))
        if opened == 0:
            if re.search(r"\.open\s*=\s*true", src):
                notes.append("首张折叠卡由脚本默认展开（ok）")
            else:
                warns.append("没有默认展开的折叠卡，读者可能不知道可以点开")
    if not re.search(r"<h1[\s>]", src):
        errors.append("缺少 <h1>")
    if not re.search(r"<title>[^<]+</title>", src):
        warns.append("缺少 <title>")

    # 9. 中英混排（正文里夹了没改掉的英文单词）
    whitelist = {"HTML", "CSS", "SVG", "PDF", "OK", "APP", "AI", "PPT", "USB", "ID"}
    body = src.split("</style>", 1)[-1]
    mixed = set()
    for m in re.finditer(r"[\u4e00-\u9fa5]\s*[A-Za-z]{2,}|[A-Za-z]{2,}\s*[\u4e00-\u9fa5]", body):
        token = m.group(0)
        letters = re.sub(r"[^A-Za-z]", "", token)
        if letters.upper() in whitelist:
            continue
        if len(set(letters.lower())) == 1:   # 形如 xx崽 的占位符
            continue
        mixed.add(token.strip())
    if mixed:
        warns.append("正文里疑似夹了英文：%s（检查是否漏改）" % "、".join(sorted(mixed)[:8]))

    # 输出
    print("=" * 56)
    print("检查: %s" % os.path.basename(path))
    print("=" * 56)
    for n in notes:
        print("  ·  %s" % n)
    for w in warns:
        print("  !  WARN  %s" % w)
    for e in errors:
        print("  x  ERROR %s" % e)
    if not errors and not warns:
        print("  ok 全部通过")
    print("")
    print("结果: %d 个错误, %d 个提醒" % (len(errors), len(warns)))
    return 1 if errors else 0


def main():
    ap = argparse.ArgumentParser(description="单页导读 HTML 结构自检")
    ap.add_argument("path", help="HTML 文件路径")
    ap.add_argument("--sections", default=",".join(DEFAULT_SECTIONS),
                    help="期望存在的板块 id，逗号分隔")
    args = ap.parse_args()
    sections = [s.strip() for s in args.sections.split(",") if s.strip()]
    sys.exit(check(args.path, sections))


if __name__ == "__main__":
    main()
