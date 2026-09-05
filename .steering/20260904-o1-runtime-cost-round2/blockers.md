# blockers / 計測中の申し送り

## ★ 計測が走っている（⚠️ 2026-09-05 06:27 JST まで）

| 項目 | 値 |
|---|---|
| サンプラ | `results/with-gse/`（★ 開始 09-04 22:27 JST・8 時間・間隔 30 s） |
| GSE | ★ `~/Desktop/O1_計測用_macOS/.../gse-next` を**バイナリ直叩き**で起動（pid は都度変わる） |
| セッションログ | `~/Documents/GSE-sessions/gse_o1_20260904_132816.ndjson` |
| 電源 | ★ **AC**（⚠️ 抜くと sleep 1 分で死ぬ） |

### ⚠️ 終わるまでやらないこと
- ⚠️ **`git push` しない**（★ この Mac は self-hosted CI ランナーでもあり、CI が CPU を奪う）。
- ⚠️ GSE を落とさない / サンプラの端末を殺さない（★ `nohup` + `disown` 済みだが念のため）。
- ⚠️ AC を抜かない。

### ★ 終わったらやること
```bash
cd /Users/johnd/GSE-prototype
D=experiments/20260903-o1-runtime-cost
cat $D/results/with-gse/finished_utc            # ★ 完走したか
python3 $D/scripts/summarize.py                 # ★ 2 回目
python3 $D/scripts/summarize.py with-gse-20260904-steady   # ★ 1 回目（比較用）
grep -F "O1 orphan sweep" ~/Documents/GSE-sessions/gse-app.log | tail -4
```
→ ★ 結果を `experiments/20260903-o1-runtime-cost/notes.md` の「実測の経過」に追記する。
⚠️ **未検証を「問題なし」と書かない**（★ Windows は 1 秒も測っていない）。

## ⚠️★★★ 研究者判断が要る（★ 本セッションでは触っていない）

| # | 何 | ⚠️ 効き方 |
|---|---|---|
| 1 | ★ `gse_o1_20260903_120435.ndjson`（**11.6 MB・研究者のテストセッション**）を消すか | ⚠️ 2026-09-04 22:23 に回収されたので、**48 時間の猶予の起点が今**。★ `o1_consent_ack` を戻すと P009 名義で送信対象になる |
| 2 | ★ 今回できた 2 本 —— `gse_o1_20260904_132328.ndjson`（スモーク・5 KB・回収済み）と `..._132816.ndjson`（計測中・8 時間ぶん） | ⚠️ 同上。★ **計測のために作ったもの**であり、研究データではない |
| 3 | ★ `~/.gse/o1_consent_ack.bak` を戻すか | ⚠️ 戻すと自動提出が再武装する。★ **1・2 を片付けてから** |
| 4 | ⚠️ 画面に「登録」を求められても**押さない** | ★ 押すと `acknowledge_o1_enrollment` が走り、3 を勝手に再武装する |

## ⚠️ 計測中に観測された既存の欠陥（★ 本実験の欠陥ではない）

★ 1 回目と同じく `keyboard hook may be dead ... starved_ms≈30000` の CGEventTap 失効が
`gse-app.log` に出ている（memory `macos-tap-idle-away-probe-bug`）。⚠️ 2 回目でも出るなら記録する。
