# 短片六工序

从一句话主题走到成片的六个工序。每一步一个 skill，产物落到固定文件，靠文件串起来。

```
① juben 剧本 → ② dingxi 定戏 → ③ jingtou 镜头表
→ ④ sucai 素材 → ⑤ shengcheng 生成 → ⑥ jianji 剪辑
```

## 装

```bash
cd 短片六工序
./install.sh          # 装到所有已存在的 skill 目录（自动备份旧版）
./install.sh --link   # 用软链接，改源文件立即生效
./install.sh --dry    # 先看会做什么
```

会往这些目录里装（存在才装）：`~/.agents/skills`、`~/.claude/skills`、`~/.codex/skills`、`~/.cursor/skills`。

**装完要开新会话**——技能清单是会话开始时读的。

## 没有 skill 机制怎么办

用 `短片六工序.md`：整个文件贴进系统提示，或放进项目根目录当规则文件
（`CLAUDE.md` / `AGENTS.md` / `.cursorrules`）。

**有 skill 就用 skill 版**——分步加载省上下文，单文件版 1700 多行，一次全进很贵。

## 依赖

| 工具 | 用在哪 | 必需吗 |
|---|---|---|
| `python3` | 三个脚本 | 是 |
| `ffmpeg` / `ffprobe` | `cutcheck.py` `voicecheck.py` | 剪辑阶段要 |
| `openai-whisper` | `cutcheck.py` | 剪辑阶段要 |
| `numpy` | `voicecheck.py` | 剪辑阶段要 |

前两个工序只要读写文件，**不装任何东西也能跑到 03**。

## 怎么用

开项目：

```
新建项目 <路径>。做一个关于 ▢▢ 的短片，▢ 分钟。
按短片流程走：剧本 → 定戏 → 镜头表 → 素材 → 生成 → 剪辑。
```

之后每步一句话：

| 说什么 | 进哪个 |
|---|---|
| 「S3 这场怎么拍」 | `dingxi` |
| 「把 S3 排成镜头表」 | `jingtou` |
| 「准备素材」 | `sucai` |
| 「开始生成」 | `shengcheng` |
| 「剪一下」 | `jianji` |

**每步的产物落到固定文件**，下一步读它。靠文件串，不靠对话记忆。

## 三条硬边界

1. **画面只由视频模型生成**（Wan / Seedance）。不做网页动效、不做代码合成、不截图拼接。
2. **闸可以跳过，但必须登记**：跳过了什么 / 代价是什么 / 谁决定的。
3. **模型只写提示词，不替你执行**。要生成会先问。

## 三个脚本

| 脚本 | 干什么 |
|---|---|
| `shengcheng/scripts/refnum.py` | 正文写 `@图名`，按每段清单换成 `@图片N`（Seedance）或 `图N`（Wan），并校验编号对不上 |
| `jianji/scripts/cutcheck.py` | whisper 转写，查每个剪辑点是不是切在话中间 |
| `jianji/scripts/voicecheck.py` | 量每段人声基频，看同一个人有没有换嗓子 |

## 更新

改 `skills/<名字>/SKILL.md`，重跑 `./install.sh`。
