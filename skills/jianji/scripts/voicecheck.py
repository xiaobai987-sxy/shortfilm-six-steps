#!/usr/bin/env python3
"""
量每段人声的基频中位数，看同一个人的嗓子有没有变。

用法：
    python3 voicecheck.py 素材目录/ --glob "*.mp4"
    python3 voicecheck.py 成片.mp4 --cuts 10,18,28,48.7

输出每段的 F0 中位数（Hz）。同一个人在同一部片里，
相邻段的偏差超过 12% 就基本听得出来换人了。

不判断「像不像」，只报「差多少」——判断权在人。
"""
import sys, os, glob, subprocess, tempfile, numpy as np

def load_sr16k(path, ss=None, t=None):
    cmd=["ffmpeg","-v","error"]
    if ss is not None: cmd+=["-ss",str(ss)]
    if t is not None: cmd+=["-t",str(t)]
    cmd+=["-i",path,"-vn","-ac","1","-ar","16000","-f","s16le","-"]
    raw=subprocess.run(cmd,capture_output=True).stdout
    return np.frombuffer(raw,dtype=np.int16).astype(np.float32)/32768.0

def median_f0(x, sr=16000, fmin=70, fmax=320, frame=0.04, hop=0.02):
    n=int(frame*sr); h=int(hop*sr)
    if len(x)<n: return None
    lo,hi=int(sr/fmax),int(sr/fmin)
    f0s=[]
    for i in range(0,len(x)-n,h):
        f=x[i:i+n]
        if np.sqrt((f**2).mean())<0.02: continue   # 静音
        f=f-f.mean()
        ac=np.correlate(f,f,mode="full")[n-1:]
        if ac[0]<=0: continue
        seg=ac[lo:hi]
        if len(seg)==0: continue
        k=int(np.argmax(seg))+lo
        if ac[k]/ac[0] < 0.3: continue             # 不清浊
        f0s.append(sr/k)
    return float(np.median(f0s)) if f0s else None

def main():
    p=sys.argv[1]
    if "--cuts" in sys.argv:
        cuts=[float(x) for x in sys.argv[sys.argv.index("--cuts")+1].split(",")]
        bounds=[0.0]+cuts
        spans=[(bounds[i],bounds[i+1]) for i in range(len(bounds)-1)]
        files=[p]*len(spans)
    else:
        g=sys.argv[sys.argv.index("--glob")+1] if "--glob" in sys.argv else "*.mp4"
        files=sorted(glob.glob(os.path.join(p,g)))
        spans=[(None,None)]*len(files)
    print(f"{'段':<3}{'文件/区间':<44}{'F0 中位':>9}")
    print("-"*60)
    vals=[]
    for i,(fp,(a,b)) in enumerate(zip(files,spans),1):
        x=load_sr16k(fp,a,(b-a) if b is not None else None)
        f0=median_f0(x)
        label=os.path.basename(fp)[:40] if a is None else f"{a:.1f}-{b:.1f}s"
        print(f"{i:<3}{label:<44}{(f'{f0:.0f} Hz' if f0 else '—'):>9}")
        if f0: vals.append((i,f0))
    if len(vals)>1:
        v=[x[1] for x in vals]
        med=float(np.median(v)); spread=(max(v)-min(v))/med*100
        print("-"*60)
        print(f"中位 {med:.0f} Hz · 最大偏差 {spread:.1f}%  " +
              ("⚠️ 超过 12%，可能换人了" if spread>12 else "✅ 在可接受范围"))
        for i,f0 in vals:
            if abs(f0-med)/med>0.12:
                print(f"   ⚠️ 第 {i} 段 {f0:.0f} Hz 偏离中位 {abs(f0-med)/med*100:.0f}%")

if __name__=="__main__":
    main()
