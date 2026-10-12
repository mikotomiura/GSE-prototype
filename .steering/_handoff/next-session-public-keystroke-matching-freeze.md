# 次のセッション: 公開データでの照合の論文 —— KLiCKe の返事の後の凍結

作成 2026-10-12、更新 2026-10-12（判断 41〜49・合成の記録の検査と `/cross-review` 2 巡の後）。作業は worktree `C:\GSE-wt-matching-prereg`（ブランチ `docs/public-keystroke-matching-prereg`）。この版は main にマージ済みの見込み（PR の番号は `git log` の merge コミットで確かめる）。

## 今の状態

- 事前登録は**下書き 8**（`experiments/20261012-public-keystroke-matching/preregistration.md`・`config.json`・`SEED`）。合成の記録の検査は済み（`notes.md`・`results/synthetic_check.json`・`scripts/`）。検査の結果と 2 巡のレビューで形と規則を直した（判断 41〜48）。
- 英語の版 `preregistration.en.md`（学術的な英語・GSE への言及なし）と OSF の各欄の文面 `osf-registration-fields.md` は用意した。
- **凍結は KLiCKe の著者の返事を見てから**（判断 49）。返事しだいで判断 1・4（この論文をやるか・KLiCKe を使うか）に戻る。
- PoPETs: CFP [V271] で、対面は掲載の条件でなく費用もないことを確かめた。録画の要否は CFP に無い → **研究者が PC chairs に問い合わせる**（本計算には関わらない）。

## 背景（これだけ読めば始められる）

- 研究者の判断: `.steering/20261012-public-keystroke-matching-judgement/decisions.md`（判断 1〜5）と `.steering/20261012-public-keystroke-matching-prereg/decisions.md`（判断 6〜49）。
- 合成の記録の検査の経緯と数値: `experiments/20261012-public-keystroke-matching/notes.md`。
- attack-me は round 4 で閉じた。接地の本文は `attack-me/prereg-public-matching/round-1/tmp/sources/`（git が無視する）。凍結を終えたら `tmp/` を消す（`panel.md` の URL と SHA-256 から取り直せる）。

## やること（KLiCKe の返事が来たら）

1. 返事を研究者と読み、判断 1・4 に戻るかを研究者が決める。返事で条件が変われば、日本語の版・英語の版・`osf-registration-fields.md` を直す（凍結の前なので逸脱ではない）。
2. 凍結の前に閉じる残り:
   - [V281] Menlo Report と [V282] Kerckhoffs は provisional。一次（原本）を取得して書誌を確かめ、`docs/references.md` の状態を active にし、英語の版の References も直す。
   - 英語の版と日本語の版の食い違いを確かめる（下書き 8 から変えたところを両方に入れる）。
3. 論文用の git リポジトリを作る（private・最初の push は研究者に `!` で頼む・判断 24）。中身は英語の版（ファイル名は `preregistration.md` にする）・`config.json`・`SEED`・`scripts/align.py`（型の写し・SHA-256 `6c03dc66…`）・`scripts/align_ext.py`・合成の記録の検査の `scripts/`・ENJA15 の換算表 `romaji_table.py`（SHA-256 は config）。
   - ⚠️ `config.json` には GSE の中の参照が残っている（`_note` の `.steering/` の文・`romaji_table.py` の `experiments/...` のパス・`alignment.implementation` の `experiments/20261011-g1-copy-self-trial/scripts`）。論文用のリポジトリの版ではリポジトリの中のパスに直し、GSE に言及しない。
   - 英語の版の本文は `scripts/align.py`・`scripts/align_ext.py` を参照している（写しで合わせる）。
4. 各ファイルの SHA-256 を計算して `osf-registration-fields.md` の「Other」に入れ、研究者が OSF に登録する（Claude はログインしない）。
5. 日本語の版と英語の版の状態の行を「凍結: <日時>・コミット <sha>・OSF の DOI <doi>」に書き換えてコミットする。
6. 完了処理: commit → push → PR → CI → merge → main の CI（`/cross-review` は文書の差分なら 1 巡で足りるかを判断する）。

## 守ること

- 応答は日本語（AskUserQuestion の問い・選択肢も日本語）。★・⚠️ を多用しない。
- docs を先に読む。必須 Skill（`reproducibility-discipline`・`citation-ssot`・`verify-before-claiming`・`subagent-delegation`）を参照してから手を動かす。
- データ（KLiCKe・ENJA15・KeyTAR）を取得しない（開始条件を満たし、研究者が決めるまで）。
- 打鍵の記録・本文を外部 LLM（Codex を含む）に送らない。Codex に渡すのはコードと文書の差分だけ。
- 有料の DB と有料の本文は使わない。
- `git add -A` や `git add <dir>` を使わず、ファイルを明示してステージする。並行セッションがあるので worktree で作業する。
- Codex の予算は、回す前に origin/main の台帳も見る。
- 公開する英語の成果物は学術的な英語・GSE への言及なし・記号や口語なし。
- 置換のスクリプトは Write で作る（heredoc のバックスラッシュが壊れる）。config を書き換えたら、重複キーを検出する形で JSON を読む。
