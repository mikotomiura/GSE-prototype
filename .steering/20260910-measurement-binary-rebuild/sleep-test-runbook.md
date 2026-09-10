# ★ スリープ跨ぎ検証 —— **研究者が単独で回す手順**

⚠️★★★ **Claude Code を終了しないと成立しない。** ★ 2026-09-10 に実測:
`caffeinate`（親 = `claude`）は **`pkill` しても新しい pid で復活する**。
★ よってこの手順は **Claude Code を閉じた状態で人が叩く**前提で書いてある。

---

## ★ 0. なぜ前回失敗したか（⚠️ 同じ穴に落ちないため）

★ 蓋を **16 分**閉じた（13:16:31 → 13:32:31）のに **Mac は寝なかった**。
★ 決定的な証拠は NDJSON: 閉蓋中の 960 秒にも `feat` が **1 Hz で 1,100 行**、
**最大の穴 1 秒**。→ ⚠️ **一瞬も止まっていない**。

★ 閉蓋中ずっとこれらが `PreventUserIdleSystemSleep` を握っていた:

| ★ 主体 | ⚠️ 対処 |
|---|---|
| ⚠️★★★ `Safari` "com.apple.WebCore: **HTMLMediaElement playback**" | ★ **動画 / 音声の再生を止める**（★ タブを閉じるのが確実） |
| ⚠️ `coreaudiod` / `AirPlayXPCHelper` | ★ 音声出力を止める・**AirPlay を切る** |
| ⚠️★★★ `caffeinate`（親 = `claude`） | ★ **Claude Code を終了する**（⚠️ pkill では復活する） |
| ⚠️ `Claude`（Electron `NoIdleSleepAssertion`） | ★ **Claude デスクトップを終了する** |
| ★ `sharingd` "Handoff" | ★ 短命。⚠️ 気にしなくてよい |

---

## ★ 1. 手順（⚠️ この順で）

```bash
cd /Users/johnd/GSE-prototype

# ── ① GSE が走っているか。★ 落ちていたら起こす（⚠️ D9 の SIGSEGV で落ちうる）
pgrep -x gse-next || nohup ~/Desktop/O1_計測用_macOS/gse-next.app/Contents/MacOS/gse-next \
  > /tmp/gse.log 2>&1 &

# ── ② 基線を採る（⚠️ 8h サンプラが走っていれば止まる。★ それでよい）
bash .steering/20260910-measurement-binary-rebuild/pre-sleep-snapshot.sh

# ── ③ ★★★ 寝られるかを機械で見る（⚠️ rc=0 でなければ閉じても寝ない）
bash .steering/20260910-measurement-binary-rebuild/check-can-sleep.sh
#    → ⚠️ Safari / caffeinate / Claude が挙がったら潰して**もう一度**叩く
#    → ★ caffeinate が消えないなら **Claude Code を終了してから**やり直す
```

★ **③ が rc=0 になってから**蓋を閉じる。⚠️ **5 分以上**待つ。

```bash
# ── ④ 起こしたら **まず何か打鍵してから**（★ 項目 6 は打鍵しないと判定できない）
bash .steering/20260910-intake-windows-and-cpu-convention/post-wake-check.sh
```

---

## ★ 2. 何が出れば「寝た」と言えるか（⚠️ 1 つでは足りない）

| ★ 経路 | ★ 寝た場合 | ⚠️ 前回（寝なかった） |
|---|---|---|
| ★★★ NDJSON の穴（項目 4） | ★ **スリープ時間とほぼ一致する穴**が開く | ⚠️ 最大 1 秒 |
| ★ `kern.waketime` | ★ 基線より**後**の時刻になる | ⚠️ `sec = 0` |
| ★ wake 理由（自己参照除去後） | ★ **1 件以上** | ⚠️ 0 件 |
| ★ `clamshelled` | ★ `YES` → `lidopen` | ★ YES は出た（＝閉じてはいた） |

⚠️★★★ **「寝ていない」を「異常なし」と読まない。** ★ 寝ていないなら**検証していない**。

---

## ★ 3. 復帰後にやること

```bash
# ★ 8h 再測を始め直す（★ 2 行を続けて）
LABEL=with-gse-$(date +%Y%m%d-%H%M)-macos-8h-v0133
cd experiments/20260903-o1-runtime-cost && \
  GSE_COST_LABEL=$LABEL nohup bash run.sh with-gse >/dev/null 2>&1 & disown
\
  nohup bash experiments/20260903-o1-runtime-cost/scripts/watch-and-summarize.sh $LABEL \
  >/dev/null 2>&1 & disown
```

⚠️★★★ **8h の途中で GSE が落ちていないか時々見ること**（★ D9）:

```bash
pgrep -x gse-next || echo "⚠️ 落ちている"
ls -lt ~/Library/Logs/DiagnosticReports/ | grep gse | head -3
```
