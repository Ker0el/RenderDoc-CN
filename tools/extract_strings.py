#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 RenderDoc 源码里抽出全部可翻译字符串（等价于 lupdate 的扫描规则）。

产出：
  dict/strings.tsv      三列 TSV：context <TAB> escaped_source <TAB> escaped_translation
                        （翻译列为空，等填）
  转义规则与 Qt .ts 一致：\\n \\t \\r \\\\ \\" 等。

用法：
  python tools/extract_strings.py <renderdoc源码根目录>
"""
import os
import re
import sys
import html
import json
from collections import OrderedDict

# ---------------------------------------------------------------- C++ 字面量
def parse_string_literals(text, pos):
    """从 pos 开始（应指向 '(' 或若干空白后）解析 C 字符串字面量串接。
    返回 (值, 结束位置) 或 (None, pos)。"""
    i = pos
    parts = []
    while True:
        while i < len(text) and text[i] in ' \t\r\n':
            i += 1
        if i >= len(text) or text[i] != '"':
            break
        i += 1
        buf = []
        while i < len(text) and text[i] != '"':
            c = text[i]
            if c == '\\':
                i += 1
                if i >= len(text):
                    return None, pos
                e = text[i]
                mapping = {'n': '\n', 't': '\t', 'r': '\r', '\\': '\\',
                           '"': '"', "'": "'", '0': '\0', '?': '?', 'a': '\a',
                           'b': '\b', 'f': '\f', 'v': '\v'}
                if e in mapping:
                    buf.append(mapping[e])
                    i += 1
                elif e == 'x':
                    i += 1
                    h = ''
                    while i < len(text) and text[i] in '0123456789abcdefABCDEF':
                        h += text[i]
                        i += 1
                    buf.append(chr(int(h, 16)) if h else 'x')
                elif e in '01234567':
                    o = ''
                    while i < len(text) and len(o) < 3 and text[i] in '01234567':
                        o += text[i]
                        i += 1
                    buf.append(chr(int(o, 8)))
                else:
                    buf.append(e)
                    i += 1
            else:
                buf.append(c)
                i += 1
        if i >= len(text):
            return None, pos
        i += 1  # closing quote
        parts.append(''.join(buf))
    if not parts:
        return None, pos
    return ''.join(parts), i


def skip_space(text, i):
    while i < len(text) and text[i] in ' \t\r\n':
        i += 1
    return i


CLASS_DEF_RE = re.compile(r'^\s*(?:class|struct)\s+([A-Za-z_]\w*)\b', re.M)
SCOPE_RE = re.compile(r'^[A-Za-z_][\w:<>,\.\*&\s]*?\b([A-Za-z_]\w*)::[~A-Za-z_]', re.M)


def build_context_map(lines):
    """返回 line_no -> 类名（尽力而为，够用即可）"""
    ctx = {}
    cur = 'Global'
    for idx, raw in enumerate(lines):
        m = SCOPE_RE.match(raw)
        if m:
            cur = m.group(1)
        m2 = CLASS_DEF_RE.match(raw)
        if m2:
            cur = m2.group(1)
        ctx[idx] = cur
    return ctx


def extract_cpp(path):
    """返回 [(context, source)]"""
    with open(path, 'r', encoding='utf-8-sig', errors='replace') as f:
        text = f.read()
    lines = text.split('\n')
    ctxmap = build_context_map(lines)

    def ctx_at(pos):
        ln = text.count('\n', 0, pos)
        return ctxmap.get(ln, 'Global')

    out = []

    # tr("...")  —— 前面不能是标识符字符（排除 setText( / lit( 里的 ...）
    for m in re.finditer(r'(?<![A-Za-z0-9_])tr\s*\(', text):
        i = m.end()
        s, e = parse_string_literals(text, i)
        if s is None or s == '':
            continue
        # 略过第二个参数（disambiguation），只取 source
        out.append((ctx_at(m.start()), s))

    # QCoreApplication::translate("ctx", "src")
    for m in re.finditer(r'\btranslate\s*\(', text):
        i = m.end()
        c, i2 = parse_string_literals(text, i)
        i2 = skip_space(text, i2)
        if i2 >= len(text) or text[i2] != ',':
            continue
        s, _ = parse_string_literals(text, i2 + 1)
        if s:
            out.append((c or 'Global', s))

    # QT_TRANSLATE_NOOP("ctx","src") / QT_TR_NOOP("src")
    for m in re.finditer(r'\bQT_TRANSLATE_NOOP\s*\(', text):
        i = m.end()
        c, i2 = parse_string_literals(text, i)
        i2 = skip_space(text, i2)
        if i2 < len(text) and text[i2] == ',':
            s, _ = parse_string_literals(text, i2 + 1)
            if s:
                out.append((c or 'Global', s))
    for m in re.finditer(r'\bQT_TR_NOOP\s*\(', text):
        i = m.end()
        s, _ = parse_string_literals(text, i)
        if s:
            out.append((ctx_at(m.start()), s))

    return out


def extract_ui(path):
    with open(path, 'r', encoding='utf-8-sig', errors='replace') as f:
        text = f.read()
    m = re.search(r'<class>([^<]+)</class>', text)
    ctx = m.group(1) if m else 'Global'
    out = []
    for mm in re.finditer(r'<(?:string|comment|title|toolTip|whatsThis|text|windowTitle|placeholderText|suffix|prefix)>([^<]*)</(?:string|comment|title|toolTip|whatsThis|text|windowTitle|placeholderText|suffix|prefix)>', text):
        # ★ uic 会把 XML 实体还原（&amp;Tools → &amp;Tools 到运行时是 "&Tools"），
        #   这里必须一起还原，否则词条跟运行期传进 translate() 的串对不上。
        s = html.unescape(mm.group(1))
        if s:
            out.append((ctx, s))
    return out


def unescape_cpp(s):
    """escape() 的逆运算，给别的脚本复用。"""
    out = []
    i = 0
    while i < len(s):
        if s[i] == chr(92) and i + 1 < len(s):
            e = s[i + 1]
            out.append({'n': chr(10), 't': chr(9), 'r': chr(13), chr(92): chr(92), '"': '"'}.get(e, e))
            i += 2
        else:
            out.append(s[i])
            i += 1
    return ''.join(out)


def escape(s):
    out = []
    for c in s:
        if c == '\\':
            out.append('\\\\')
        elif c == '\n':
            out.append('\\n')
        elif c == '\r':
            out.append('\\r')
        elif c == '\t':
            out.append('\\t')
        else:
            out.append(c)
    return ''.join(out)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    root = sys.argv[1]
    pairs = []
    nfiles = 0
    for dirpath, dirnames, filenames in os.walk(os.path.join(root, 'qrenderdoc')):
        dirnames[:] = [d for d in dirnames if d not in ('3rdparty', '.git', 'build')]
        for fn in filenames:
            p = os.path.join(dirpath, fn)
            if fn.endswith(('.cpp', '.h', '.hpp')):
                pairs += extract_cpp(p)
                nfiles += 1
            elif fn.endswith('.ui'):
                pairs += extract_ui(p)
                nfiles += 1

    # 去重：同一 (context, source) 只留一条；同时统计 source 出现次数
    seen = OrderedDict()
    for ctx, src in pairs:
        key = (ctx, src)
        if key not in seen:
            seen[key] = 0
        seen[key] += 1

    print(f'scanned {nfiles} files')
    print(f'raw occurrences: {len(pairs)}')
    print(f'unique (context, source): {len(seen)}')
    print(f'unique source strings  : {len(set(s for _, s in seen))}')

    out_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            'dict', 'strings.tsv')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write('# context\tsource\ttranslation\n')
        for (ctx, src), cnt in seen.items():
            f.write(f'{escape(ctx)}\t{escape(src)}\t\n')
    print('written:', out_path)

    # 统计：按 context 分布
    from collections import Counter
    c = Counter(ctx for ctx, _ in seen)
    print('\ntop contexts:')
    for k, v in c.most_common(25):
        print(f'  {v:5d}  {k}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
