#!/usr/bin/env python3
"""
把 05-生成.md 里的 @图名 按每段「参考图清单」换成 @图片N，并校验。

用法：
    python3 refnum.py 05-生成.md               # 只检查
    python3 refnum.py 05-生成.md --write       # 检查并改写（Seedance：@图片N）
    python3 refnum.py 05-生成.md --write --wan # 检查并改写（Wan：图N）

文档格式（每段）：

    ### G05 · 刀架上脖子

    **参考图（顺序即编号，只列这次真传的）**
    | # | 图名 | 用来锁什么 |
    |---|---|---|
    | 1 | 沈九脸锁 | 脸型、灰衫、缺指 |
    | 2 | 雷震脸锁 | 方脸短须、左眉疤 |

    **提示词**
    ……参考 @沈九脸锁 的身份，对面是 @雷震脸锁 ……

规则：
  · 正文只准写 @图名，不准手写 @图片N
  · 清单的 # 必须 1..N 连续，从 1 开始
  · 正文出现的图名，必须在该段清单里
"""
import re, sys

SEG = re.compile(r'(?m)^###\s+(.+)$')
ROW = re.compile(r'^\s*\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*(.*?)\s*\|\s*$')
NAME = re.compile(r'@([^\s@，。、；：""''（）()\[\]{}]+)')
MANUAL = re.compile(r'@图片\s*\d+|(?<![@\w])图\s*\d+')

H2 = re.compile(r'(?m)^##\s')

def parse(path):
    lines = open(path, encoding="utf-8").read().split("\n")
    segs = []           # [(title, start, end)]
    cur = None
    for i, ln in enumerate(lines):
        m = SEG.match(ln)
        if m:
            if cur: cur[2] = i
            cur = [m.group(1).strip(), i, len(lines)]
            segs.append(cur)
        elif cur and ln.startswith("## "):
            # 遇到二级标题，本段结束
            cur[2] = i
            cur = None
    return lines, segs

def check(path, write=False):
    lines, segs = parse(path)
    problems, warns, reports = [], [], []
    for title, a, b in segs:
        block = lines[a:b]
        refs, order = {}, []
        for ln in block:
            m = ROW.match(ln)
            if m:
                idx, name = int(m.group(1)), m.group(2).strip()
                if name in ("图名", "---"): continue
                refs[name] = idx
                order.append((idx, name))
        # 清单连续性
        nums = sorted(n for n, _ in order)
        if nums and nums != list(range(1, len(nums)+1)):
            problems.append(f"[{title}] 清单编号不连续：{nums}")
        body = "\n".join(block)
        used = [n for n in NAME.findall(body) if not n.startswith("图片")]
        for u in sorted(set(used)):
            if u not in refs:
                problems.append(f"[{title}] 正文用了 @{u}，但清单里没有")
        if MANUAL.search(body):
            problems.append(f"[{title}] 正文出现手写编号（@图片N 或 图N）—— 必须写 @图名")
        # 未使用的
        unused = [n for n in refs if n not in used]
        if unused:
            warns.append(f"[{title}] 清单里有 {unused}，正文没提到（可能白传）")
        reports.append(f"  {title}: 传 {len(order)} 张 → " +
                       " ".join(f"{n}={refs[n]}" for _, n in order))
        if write:
            for i in range(a, b):
                wan = "--wan" in sys.argv
                def sub(m):
                    nm = m.group(1)
                    if nm not in refs: return m.group(0)
                    return f"图{refs[nm]}" if wan else f"@图片{refs[nm]}"
                lines[i] = NAME.sub(sub, lines[i])
    print("每段参考图：")
    print("\n".join(reports) if reports else "  （没找到 ### 段）")
    if warns:
        print("\n⚠️ 提醒（不影响通过）：")
        for w in warns: print("  ·", w)
    if problems:
        print("\n❌ 问题：")
        for p in problems: print("  ·", p)
    else:
        print("\n✅ 编号全部对得上")
    if write and not problems:
        open(path, "w", encoding="utf-8").write("\n".join(lines))
        print("已改写：@图名 → " + ("图N（Wan）" if "--wan" in sys.argv else "@图片N（Seedance）"))
    return 1 if problems else 0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(2)
    sys.exit(check(sys.argv[1], "--write" in sys.argv))
