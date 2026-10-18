# 次のセッション: 公開データでの照合の論文 —— 3 度目の再起動の後、A4 を CPU の代替つきで再開する

作成 2026-10-18（G-GEAR）。前の引き継ぎ `next-session-public-keystroke-matching-after-reboot-2.md` の続き。投稿の目標は PoPETs 2027 Issue 3（締切 2026-11-30 AoE）。

## 新しいセッションで最初に打ち込む文

ターミナル（VS Code ではなく）で `cd C:\GSE-wt-matching-prereg` してから `claude` を起動し、次を打つ:

```
C:\GSE-wt-matching-prereg\.steering\_handoff\next-session-public-keystroke-matching-after-reboot-3.md を読んで、commit の上限と GPU の設定を確かめてから、A4 を CPU の代替つきで再開して
```

## 今の状態

- worktree `C:\GSE-wt-matching-prereg`・ブランチ `docs/public-keystroke-matching-freeze`。
- A4: `raw/derived/a4/` に 352/500 人（指紋は 10-13 から同じ）。353 人目で GPU のメモリが足りず落ち続けた（逸脱 D3・`notes.md`）。ループと見張りは止めてある。
- 逸脱 D3（研究者の判断 2026-10-18・案 1）: `scripts/a4_keytar_cpu_fallback.py` が、GPU に載りきらない塊だけを CPU で生成する（`a4_keytar.py` は変えない・指紋は同じ）。作った入力で GPU と CPU の出力が食い違うことがある（`notes.md` D3）。研究者はそれを承知で案 1 を選んだ。
- `scripts/a4_run_resumable.sh` は環境変数 `A4_SCRIPT` で呼ぶスクリプトを替えられる（既定は `a4_keytar.py`）。
- ページファイル: 初期 64 GB・最大 96 GB に設定済み（10-15）。この再起動で効く見込み。commit の上限が約 96 GB になっていることを確かめる。
- CPU の本計算・ENJA15・探索的な分析は、A4 が終わってから回す（研究者の判断 10-17）。
- A4 の 1 人あたりは平均 約 17.5 分。残り 148 人で約 43 時間 ＋ CPU の代替の時間（1 塊で数十分〜数時間の見込み・未計測）。

## やること（順に）

1. 確かめる: `nvidia-smi`（GPU が見える）。commit の上限（PowerShell: `(Get-CimInstance Win32_OperatingSystem).TotalVirtualMemorySize/1MB` が約 96 GB。62 GB のままなら研究者に知らせる）。
2. GPU の設定を研究者に打ってもらう（管理者の PowerShell・再起動で戻るため）:
   ```
   nvidia-smi -lgc 210,2000
   nvidia-smi -pl 150
   ```
   入ったことを `nvidia-smi -q -d POWER` で確かめ、値と時刻を `notes.md` の「A4 の実行の記録（GPU の設定）」に足す。
3. A4 を CPU の代替つきで再開する（バックグラウンド）:
   ```bash
   A4_SCRIPT=scripts/a4_keytar_cpu_fallback.py bash /c/GSE-wt-matching-prereg/experiments/20261012-public-keystroke-matching/scripts/a4_run_resumable.sh
   ```
   止めるときは PowerShell で `a4_run_resumable` と `a4_keytar` を含むプロセスを `Stop-Process`（TaskStop ではループが止まらない）。
4. 見張りを置く（バックグラウンド・git の外の台本）:
   ```bash
   bash /c/GSE-wt-matching-prereg/experiments/20261012-public-keystroke-matching/raw/a4_watch/a4_err_watch.sh --first-writer
   ```
   353 人目が通ったら終了コード 6、また落ちたら 5（Windows の通知も出る）。6 が来たら `--first-writer` なしで立て直す（終わり 0・止まり 3・同じ書き手で 2 回続けて落ちる 5・150 分変化なし 4）。CPU の代替の塊は `raw/derived_a4_cpu_fallback.jsonl` と進み具合のログの "cpu fallback" の行で見る。
   Claude Code はメモリ不足のときバックグラウンドのシェルを止めることがある（中の bash は生き残ることが多い）。止められたら、プロセスの有無を確かめて研究者に知らせる。
5. A4 が終わったら: 研究者に知らせる → CPU で生成した塊と書き手の数を `notes.md` D3 に書く → 前の引き継ぎ（`-2`）の流れで、試し実行（`--per-prompt-sample 2`・`--all` なし・`results/.tmp/`）→ 本計算（12 並列・`--all`）→ ENJA15 → 探索的な分析 → `main_a4.json`。A4 の正答率は、CPU の塊を含む全体と、その書き手を除いた場合の両方を出す（D3）。
6. 終わった作業は、コード・文書の差分を code-reviewer と security-checker（並列）と `/cross-review`（パス限定・`raw/` と結果の JSON を範囲に入れない）にかける。`a4_keytar_cpu_fallback.py` と `a4_run_resumable.sh` の変更（10-18）はまだレビューしていない。

## 守ること

- `FINGERPRINT_FILES` のコードは、A4 を回しているあいだ変えない。
- 記録・本文・A4 の復元の中身を Claude 自身も読まない（数・ハッシュ・分布だけ）。外部 LLM（Codex を含む）に送らない。
- 凍結の後の変更は `notes.md` の「逸脱」に。
- 応答は日本語。★・⚠️ を多用しない。`git add -A`・`git add <dir>` を使わない。
- 状態を変える操作（push・PR・merge）は出力をファイルに保存して 1 回だけ。
