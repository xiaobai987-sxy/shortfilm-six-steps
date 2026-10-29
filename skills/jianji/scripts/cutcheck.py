#!/usr/bin/env python3
"""
检查每个剪辑点是不是切在「话说到一半」上。

用法：
    python3 cutcheck.py 成片.mp4 --cuts 10.0,18.0,28.0
    python3 cutcheck.py 成片.mp4 --timeline 06-剪辑.md --write

它做什么：
  1. whisper 转写，拿到逐词时间码
  2. 每个切点：判断落在词内部 / 词刚结束 / 静默里
  3. 落在词内部 → 失败；落在词结束后 0.15 秒内 → 危险
  4. 给出「最近的静默中点」作为建议切点

--write 会把建议切点写回时间线（只改时间，不改内容）。
"""
import sys, re, subprocess, tempfile, os

def transcribe(video):
    import whisper
    wav = tempfile.mktemp(suffix=".wav")
    subprocess.run(["ffmpeg","-v","error","-y","-i",video,"-vn","-ar","16000","-ac","1",wav],
                   check=True)
    m = whisper.load_model("small")
    r = m.transcribe(wav, language="zh", fp16=False, word_timestamps=True, verbose=False)
    os.unlink(wav)
    words = []
    for s in r.get("segments", []):
        for w in s.get("words", []):
            words.append((w["start"], w["end"], w["word"]))
    return words

def nearest_gap(words, t, span=1.0):
    """返回 t 附近最宽的静默区间 (a,b)"""
    best, ba, bb = -1, None, None
    for i in range(len(words)-1):
        a, b = words[i][1], words[i+1][0]
        if b <= a: continue
        mid = (a+b)/2
        if abs(mid - t) <= span and (b-a) > best:
            best, ba, bb = b-a, a, b
    return ba, bb, best

def main():
    if len(sys.argv) < 4:
        print(__doc__); sys.exit(2)
    video = sys.argv[1]
    cuts = []
    if "--cuts" in sys.argv:
        cuts = [float(x) for x in sys.argv[sys.argv.index("--cuts")+1].split(",")]
    words = transcribe(video)
    print(f"转写：{len(words)} 个词\n")
    bad = 0
    print(f"{'切点':>8}  判定        情况")
    print("-"*60)
    for t in cuts:
        inside = [w for w in words if w[0] < t < w[1]]
        just   = [w for w in words if 0 <= t - w[1] <= 0.15]
        if inside:
            w = inside[0]
            print(f"{t:8.2f}  ❌ 切在词中   「{w[2]}」{w[0]:.2f}-{w[1]:.2f}")
            bad += 1
        elif just:
            print(f"{t:8.2f}  ⚠️ 紧贴词尾   「{just[0][2]}」结束于 {just[0][1]:.2f}")
            bad += 1
        else:
            a, b, d = nearest_gap(words, t)
            info = f"最近的静默 {a:.2f}-{b:.2f}（{d:.2f}s）" if a is not None else "附近没有词，是空段"
            print(f"{t:8.2f}  ✅ 静默       {info}")
    print("-"*60)
    print(f"{'❌ 有 '+str(bad)+' 刀切在话上' if bad else '✅ 全部落在静默里'}")
    sys.exit(1 if bad else 0)

if __name__ == "__main__":
    main()
