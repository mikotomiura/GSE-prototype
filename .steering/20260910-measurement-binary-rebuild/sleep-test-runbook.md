# ★ スリープ跨ぎ検証 —— **研究者が単独で回す手順**

⚠️★★★ **Claude Code を終了しないと成立しない。** ★ 2026-09-10 に実測:
`caffeinate`（親 = `claude`）は **`pkill` しても新しい pid で復活する**。
★ よってこの手順は **Claude Code を閉じた状態で人が叩く**前提で書いてある。

---

## ⚠️★★★ 0-0. **真因は `SleepDisabled = 1` だった**（★ 2026-09-10 15:07 に特定）

★ 2 回のスリープ検証が失敗した理由は、⚠️ **assertion ではなく system 設定**だった:

```
$ pmset -g | grep SleepDisabled
 SleepDisabled		1
```

★ これは `sudo pmset disablesleep 1`（★ clamshell 運用でよく使う）の設定で、
⚠️★★★ **assertion と無関係に、蓋を閉じても含めてスリープを全面的に無効化する**。

★ 裏づけ（★ すべて実測）:

| ★ 証拠 | 値 |
|---|---|
| `kern.waketime` | ★ **0** ＝ ⚠️ **2026-07-26 の起動以来 46 日間 1 度も寝ていない** |
| 1 回目 閉蓋 16 分（13:16:31→13:32:31） | ⚠️ NDJSON の穴は最大 **1 秒** |
| 2 回目 閉蓋 5 分（14:59:34→15:04:38） | ⚠️ 同じく最大 **1 秒** |
| `pmset -g log` の Sleep/Wake 行 | ★ **0 件**（09-03 以降） |

### ⚠️★★ 私の誤り（★ 記録に残す）

★ 私は 2 回とも「**音声が直接の障害**」と書いた。⚠️ **それは誤りだった。**
★ 妨害している assertion は正しく列挙できていたのに、
⚠️ **その上位にある system 設定を 1 度も見なかった**。
→ ★ 教訓: **潰しても潰しても効かないときは、1 段上の層を疑う**。
  ⚠️ 個別の妨害者を消し込む作業に入る前に、**全体を無効化している設定が無いか**を見る。

## ★ 0-1. 解除の手順（⚠️ sudo が要る ＝ **私からは実行できない**）

```bash
sudo pmset -a disablesleep 0
pmset -g | grep SleepDisabled     # ★ 0 になっていること
```

⚠️ **検証が終わったら元に戻すか**は研究者判断（★ 元は 1 だった）。

---

## ★ 0. 妨害者の一覧（⚠️ 上の 0-0 を解除した**後**に効いてくる）

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
