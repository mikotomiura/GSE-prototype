# 次のセッション: 公開データでの照合の論文 —— 2 度目の再起動の後、GPU の上げ止まりを下げて A4 を再開する

作成 2026-10-14（G-GEAR）。前の引き継ぎ `next-session-public-keystroke-matching-after-reboot.md` の続き。GPU がまた落ちたので、研究者が PC を再起動する。投稿の目標は PoPETs 2027 Issue 3（締切 2026-11-30 AoE）。

## 新しいセッションで最初に打ち込む文

```
.steering/_handoff/next-session-public-keystroke-matching-after-reboot-2.md を読んで、GPU のクロックと電力を下げてから A4 の生成を再開して。CPU の本計算は知らせるまで待って。
```

## 今の状態

- worktree `C:\GSE-wt-matching-prereg`・ブランチ `docs/public-keystroke-matching-freeze`。
- 逸脱 D2 を足した（`notes.md`）: `synthetic_logs.py` の `form_R1`・`form_R5`・`form_R6` が KLiCKe の行に無い `pause_time` を `del` して落ちた → `o.pop("pause_time", None)` に直した。KLiCKe の 5 人ですべての形が通ることを確かめた（行の数だけ）。照合と有用性の値は **まだ 1 つも計算していない**。ENJA15 も探索的な分析も回していない。
- A4: `raw/derived/a4/` に 5 人ぶん（直した後のコードの指紋）。2026-10-13 10:00:29 UTC に始めた試行で 5 人を終えた後、11:39 UTC に `CUDA error: unknown error` → 「GPU is lost」。1 人あたり約 17〜20 分（5 人で 5,688 秒。途中まで別セッションの `checks.py` と CPU を取り合っていた）。このままだと 500 人で約 6 日。1 回目の落ち方（10-13 の昼）は 3 人を終えた後。
- システムのイベント: 2026-10-13 18:58:29（現地）に `nvlddmkm` の 153（同じ時刻に 1 回目の試行が exit 127 で止まった）。18:48:28 に Kernel-Power 41（予期しない再起動）。2 回目（20:39 現地）の前後には `nvlddmkm` のイベントが残っていない。
- 落ちたときの消費電力は 65 W 前後（上限 180 W）・使用率 56% だった。電力より高いクロックで不安定になっている見込みを先に潰す（研究者の判断・2026-10-14）。

## やること（順に）

1. GPU が見えることを確かめる（`nvidia-smi`）。
2. クロックと電力を下げる（研究者の判断）。管理者の端末が要るので、研究者に打ってもらう。値は先に `nvidia-smi -q -d SUPPORTED_CLOCKS,POWER` で範囲を見て決め、研究者に示す。目安は、最大のグラフィックのクロックを 2,000 MHz 前後に固定（`nvidia-smi -lgc 210,2000`）し、電力の上限を 130 W 前後（`nvidia-smi -pl 130`・範囲の中で）。生成の中身は変わらない（指紋に入らない）。設定は再起動で戻るので、値と時刻を `notes.md` に書く。
3. A4 の生成を再開する（続きから・5 人ぶんはそのまま使う）:
   ```bash
   bash /c/GSE-wt-matching-prereg/experiments/20261012-public-keystroke-matching/scripts/a4_run_resumable.sh
   ```
   バックグラウンドで回す。注意: Claude Code の TaskStop ではこのループの bash が止まらなかった（2026-10-13）。止めるときは PowerShell で `a4_run_resumable` と `a4_keytar.py` を含むプロセスを `Stop-Process` する。
4. CPU の本計算・ENJA15・探索的な分析は、**研究者が知らせるまで始めない**（研究者の判断・2026-10-14。別セッションが CPU を使う）。知らせが来たら、前の引き継ぎの「やること」3〜5 の順に回す。先に試し実行（`--per-prompt-sample 2`・`results/.tmp/`・値は見ない）。試し実行は 12 並列で CPU を取り合った状態で 40 分を超えても終わらなかった。
5. 残りの見込みの見張りを置く（研究者の希望・2026-10-14: A4 の残りが 25 時間ほどになったら分かるように）。見込みは `scripts/a4_eta.py`（進み具合のログと `raw/derived/a4/` のファイルの数だけを読む。直近 10 人の 1 人あたりの時間の中央値 × 残りの人数。GPU が止まっている時間は入らない）。A4 を再開した後、バックグラウンドで 30 分ごとに `~/.venvs/pkm-main/Scripts/python -I scripts/a4_eta.py --within 25` を回し、終了コード 0 になったら研究者に PushNotification で知らせる（CPU の本計算はそこで研究者が始めるかを決める）。2026-10-14 の時点の見込み: 5/500・1 人 17.1 分・残り 140.8 時間。

## 守ること

- `synthetic_logs.py` ほか `FINGERPRINT_FILES` に入るコードは、A4 を回しているあいだ変えない（変えると生成済みのファイルが「別の生成」になる）。
- 記録・本文・A4 の復元の中身を Claude 自身も読まない（数・ハッシュ・分布だけ）。外部 LLM（Codex を含む）に送らない。
- 凍結の後の変更は `notes.md` の「逸脱」に。
- 応答は日本語。★・⚠️ を多用しない。`git add -A`・`git add <dir>` を使わない。
- 状態を変える操作（push・PR・merge）は出力をファイルに保存して 1 回だけ。
- Windows では、本計算を回している間はスクリプトを編集しない。
