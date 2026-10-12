#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
校验词条表格式。

    python tools/check_dict.py dict/rd_zh.tsv

检查项：
  · 每行必须是三列 TAB 分隔
  · 原文与译文都不能为空
  · 译文里的 %1 / %2 / %n 占位符必须是原文的子集（多出来的必然写错了）
  · 原文里带 & 快捷助记符时，译文里要保留
  · 转义是否合法（\\n \\t \\r \\\\）
"""
import re
import sys

PH = re.compile(r'%(\d+|n)')


def unescape(s):
    out = []
    i = 0
    while i < len(s):
        if s[i] == '\\' and i + 1 < len(s):
            e = s[i + 1]
            out.append({'n': '\n', 't': '\t', 'r': '\r', '\\': '\\'}.get(e, e))
            i += 2
        else:
            out.append(s[i])
            i += 1
    return ''.join(out)


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else 'dict/rd_zh.tsv'
    rows = 0
    bad_cols, empty, bad_ph, bad_amp = [], [], [], []
    for ln, line in enumerate(open(path, encoding='utf-8'), 1):
        if line.startswith('#') or not line.strip():
            continue
        p = line.rstrip('\n').split('\t')
        if len(p) != 3:
            bad_cols.append((ln, line[:60]))
            continue
        rows += 1
        src, tr = unescape(p[1]), unescape(p[2])
        if not src.strip() or not tr.strip():
            empty.append((ln, src[:40]))
            continue
        if not set(PH.findall(tr)) <= set(PH.findall(src)):
            bad_ph.append((ln, src[:50], tr[:50]))
        for m in re.finditer(r'&(?![&])', src):
            nxt = src[m.end():m.end() + 1]
            if nxt and nxt.isalnum() and ('&' + nxt) not in tr \
               and ('&' + nxt.upper()) not in tr and ('&' + nxt.lower()) not in tr:
                bad_amp.append((ln, src[:50], tr[:50]))
                break

    print('词条行数: %d' % rows)
    print('列数不对: %d' % len(bad_cols))
    for b in bad_cols[:10]:
        print('   第 %d 行: %r' % b)
    print('空原文/空译文: %d' % len(empty))
    for b in empty[:10]:
        print('   第 %d 行: %r' % b)
    print('占位符对不上: %d' % len(bad_ph))
    for b in bad_ph[:10]:
        print('   第 %d 行: %r -> %r' % b)
    print('快捷助记符 & 丢失: %d' % len(bad_amp))
    for b in bad_amp[:10]:
        print('   第 %d 行: %r -> %r' % b)

    return 1 if (bad_cols or empty or bad_ph) else 0


if __name__ == '__main__':
    sys.exit(main())
