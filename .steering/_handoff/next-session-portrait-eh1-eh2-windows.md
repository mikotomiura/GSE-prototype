# 引き継ぎ — 肖像の EH1（合成の記録の検査）と EH2（壁紙 API の機械の検証）・Windows 機

> 作成: 2026-10-09。研究者の指示「EH-1 は windows に回す感じにして、windows のみ EH-1, 2 両方回す感じで引継ぎに書くか」（`.steering/20261009-portrait-eh1-eh2/decisions.md` 判断 5）。
> ⚠️ **このメモを一次資料にしない。** EH1 の作りと合否の基準は `.steering/20261009-portrait-eh1-eh2/design.md` §1・§3・§8、EH2 は同 §4 と `experiments/20261009-portrait-eh2/README.md`。
> macOS の引き継ぎは `next-session-portrait-eh2-macos.md`（EH2 だけ・別の機器で並行に回す）。

## §0 次のセッションの最初に貼るプロンプト

```
.steering/_handoff/next-session-portrait-eh1-eh2-windows.md を読んで、肖像の EH1 と EH2（Windows 版）を回してください。
ブランチは docs/portrait-eh1-eh2 です。worktree を切って作業し、§4 に書いたファイルだけをコミットして push してください（PR は出さない）。
EH1 と EH2 は同時に回さないでください（EH2 は CPU を測ります）。
```

## §1 前提（この機械で回してよいか）

1. **計測の run がこの機械で走っていないこと**を研究者に確かめる（G-GEAR は CI の self-hosted runner でもある）。走っていたら回さない。
2. EH1 に要るもの: GSE をビルドできる Rust（`cargo`・MSVC。`gse-replay` は `src-tauri` のライブラリごとビルドするので、初回は 7〜10 分ほど）・Python 3.11 以上（計器を作った機械は 3.11.9。違う版なら `provenance.json` に刻まれるので、notes にも書く）・git-bash（`run.sh` は bash）。
3. EH2 に要るもの: 背景が「画像」であること（設定 → 個人用設定 → 背景）。スライドショー・単色・Windows スポットライト・元の画像のファイルが消えている・元の画像が Themes フォルダの写し、のどれかだとスクリプトは断って止まる（元に戻せないため）。⚠️ `-Force` は使わない。一時的に「画像」へ替えたなら、終わったあとに研究者が自分で元に戻す。

## §2 EH1（合成の記録・参加者なし・機械を触らなくてよい）

合成した打鍵 → `gse-replay`（GSE の F 系列の計算そのもの）→ 仮の形の生成器 → 検査、で「形に停滞の情報が残らないか（E1-3）」などを、**結果の前に固定した基準**（design §3）で判定する。world は 2 つ回す: **v1**（固定した設計どおり・主の記録）と **v2**（逸脱・design §8: 休止の分布を揃えて、停滞が修正・打鍵の間隔・まとまりの打鍵数にだけ出る世界）。

```
git fetch origin docs/portrait-eh1-eh2
git worktree add -b docs/portrait-eh1-eh2-win-run C:/wt/portrait-eh1-eh2-win origin/docs/portrait-eh1-eh2
cd C:/wt/portrait-eh1-eh2-win/experiments/20261009-portrait-eh1
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
bash run.sh --smoke --world v1      # 最初に gse-replay をビルドする（target は worktree の外 ../../../_target-portrait-eh1）。その後 1 分ほど
bash run.sh --world v1              # 本番
bash run.sh --world v2              # 本番（逸脱）
```

- 所要の見込み: 作った機械（16 論理コア）で、本番 1 本あたり 20〜40 分（E1-3 の分類器の学習と帰無の並べ替え 20 回が大半）。⚠️ 通しで計った値ではない（作った機械の本番は途中で止めた）。コアが少ないと延びる。
- **確かめること**:
  - 各回の `selftest.py` の出力が `0 failed` で、本番では `PASS  mutation: random levels keep the E1-3 gain below the margin` が出る（スモークでは `SKIP` になるのが正しい）。
  - `results/v1/` と `results/v2/` に `summary.json`・`e13.json`・`e16.json`・`e14.json`・`e17.json`・`order.json`・`e12.json`・`describe.json`・`exploratory_recent.json`・`provenance.json`・`capabilities.json`・`samples/`・`e18/` ができる。
  - `provenance.json` の `experiment_dir_dirty` が `false`（計器を変えずに回した証拠）。
- ⚠️ **基準を動かさない・計器を変えない**: 結果が赤や判定不能でも、そのまま記録する。緑にするために設定やコードを変えて回し直さない。エラーで止まった・selftest が落ちたときは、直す前に研究者に報告する。どうしても直したときは `notes.md` の「逸脱・気づいたこと」に、日時・何を・なぜを書く（design §8 への反映は本体のセッションが行う）。
- `results/<world>/` の値を `experiments/20261009-portrait-eh1/notes.md` の「結果」に写す（組ごとに緑・赤・判定不能。陽性対照 PC1・PC2 の判定と、帰無の 95 パーセンタイルも）。書き方は、緑なら「検査した範囲で見つからなかった」、判定不能なら「判定不能（理由）」。

## §3 EH2（壁紙の機械の検証・約 15 分・本番の間は機械を触らない）

**EH1 の本番が走っていないときに回す**（EH2 は CPU を測る）。下のコマンドは PowerShell でも git-bash でも打てる（パスはスラッシュで書く）。

```
cd C:/wt/portrait-eh1-eh2-win
powershell -NoProfile -ExecutionPolicy Bypass -File experiments/20261009-portrait-eh2/windows/eh2_wallpaper.ps1 -DryRun
powershell -NoProfile -ExecutionPolicy Bypass -File experiments/20261009-portrait-eh2/windows/eh2_wallpaper.ps1 -Quick
powershell -NoProfile -ExecutionPolicy Bypass -File experiments/20261009-portrait-eh2/windows/eh2_wallpaper.ps1
```

1. `-DryRun` は壁紙を替えない。
2. `-Quick`（約 1 分・壁紙が縞と点に数回変わって元に戻る）の最後に `Restored: True ... position ok: True` が出ることを確かめる。⚠️ 出なければ止めて、README の「戻らなかったとき」で戻し、研究者に報告する（**壁紙を替えて戻す経路は、作った機械では回せていない** —— 作った機械の背景がスポットライトだったため）。
3. 本番（引数なし・約 12 分）。研究者がその場にいれば `-Manual` を付けて、仮想デスクトップ（Win+Ctrl+D）と画面共有か録画（Teams・Zoom・ゲームバー Win+Alt+R など）での見え方を y/n で答える。
4. 結果は `experiments/20261009-portrait-eh2/results/eh2-windows-<日時>.json`。`restored` がすべて `true`、`per_monitor.readback_ok` が `calls` と同じか、`error` が無いかを見る。
5. `experiments/20261009-portrait-eh2/notes-windows.md` を新しく作り、表に書く: 日時・機械の種類（例「G-GEAR・Windows 11・モニタ 2 台」。機械の名前やユーザー名は書かない）・モード・`per_monitor` の中央値と p95・`all_monitors`（中央値か skipped）・CPU（idle と busy の explorer と自分）・複数モニタで別々の画像が読み戻せたか・手の確認の答え・気づいたこと（ちらつき・反映の遅れなど）。

## §4 コミット（この機器が触るファイル）

- ⚠️ **macOS の機器も同じブランチへ並行に push する**。衝突を避けるため、この機器が触るのは次だけ:
  - `experiments/20261009-portrait-eh1/results/v1/`・`results/v2/` の中のファイル・`experiments/20261009-portrait-eh1/notes.md`
  - `experiments/20261009-portrait-eh2/results/eh2-windows-*.json`・`experiments/20261009-portrait-eh2/notes-windows.md`
  - `README.md`・`design.md`・`decisions.md`・`tasklist.md` は触らない（まとめは本体のセッションが行う）。判断を書く必要があれば notes の中に「判断 W1」として書く。
- `results/*-smoke/`・`work-*/`・`.venv/` は `.gitignore` で除外される。⚠️ **生成した NDJSON と秒ごとの特徴（`work-*/`）は合成でもコミットしない**。
- add はファイルを名指しする（`git add -A` とディレクトリ単位の add は使わない）。結果のファイルが多いので、一覧を出して目で確かめてから渡す:
  ```
  git status --short experiments/20261009-portrait-eh1 experiments/20261009-portrait-eh2
  git ls-files --others --exclude-standard experiments/20261009-portrait-eh1/results/v1 experiments/20261009-portrait-eh1/results/v2 > /tmp/eh1-files.txt
  # /tmp/eh1-files.txt を目で見て、JSON と PNG だけであることを確かめる
  git add $(cat /tmp/eh1-files.txt) experiments/20261009-portrait-eh1/notes.md
  git commit -m "docs(experiments): 肖像の EH1 を Windows で回した（v1・v2）" -m "Refs: .steering/20261009-portrait-eh1-eh2/"
  git add experiments/20261009-portrait-eh2/results/eh2-windows-<日時>.json experiments/20261009-portrait-eh2/notes-windows.md
  git commit -m "docs(experiments): 肖像の EH2 を Windows で回した（<機械の種類>）" -m "Refs: .steering/20261009-portrait-eh1-eh2/"
  git push origin HEAD:docs/portrait-eh1-eh2
  ```
  push が拒まれたら `git pull --rebase origin docs/portrait-eh1-eh2` してからもう一度。
- ⚠️ **ブランチ名は `docs/` のまま**にする。`feature/*` に push すると CI が self-hosted（G-GEAR・計測の Mac）で走る（2026-10-09 に一度起きた・判断 4）。**PR は出さない**（計測の run の後）。

## §5 守ること（CLAUDE.md・memory から）

- 応答は日本語。研究者に聞くときは AskUserQuestion に推奨と理由を添える。
- main checkout（`C:\GSE-prototype`）は別の作業が載っているので触らない。worktree で作業する。
- ⚠️ **標準出力を notes・コミットメッセージに貼らない**（一時フォルダのパスにユーザー名が出る）。コミットの前に次を回し、何も出ないことを確かめる:
  `grep -rInE 'Users|/var/folders|DISPLAY#' experiments/20261009-portrait-eh2/results/eh2-windows-*.json experiments/20261009-portrait-eh2/notes-windows.md experiments/20261009-portrait-eh1/notes.md experiments/20261009-portrait-eh1/results/v1 experiments/20261009-portrait-eh1/results/v2`
- 元の壁紙のパスは `%TEMP%\gse-eh2-restore-<日時>.json` にだけ置かれる。リポジトリに入れない。
- 数字は「この機械で測った値」「合成の記録での結果」として書く。一般化しない（「GSE が示した」と書かない）。
- 外部の LLM（Codex など）に結果を送るのは本体のセッションの `/cross-review` だけ。合成の記録でも NDJSON は送らない。
