# 次のセッション: 公開データでの照合の論文 —— 凍結の前の合成の記録の検査と、凍結

作成 2026-10-12、更新 2026-10-12（判断 6〜40・attack-me round 1〜4 の後）。作業は worktree `C:\GSE-wt-matching-prereg`（ブランチ `docs/public-keystroke-matching-prereg`）。

## 今の状態

- 事前登録は下書き 5（`experiments/20261012-public-keystroke-matching/preregistration.md`・`config.json`・`SEED`）。attack-me は round 4 で minor（直してから凍結・再査読は要らない）になり、その直しは入れた（判断 37〜40）。
- 凍結の前に残っているのは、合成の記録の検査（下の やること 1）だけ。研究者の判断で、この検査は凍結の**前**に行い、結果と直した形を凍結する版に入れる（下書き 3 以降の冒頭・判断 31 の m8）。
- 公開の置き場: 事前登録は OSF の registration（判断 25・研究者のアカウントで登録・Claude は英語の文面を用意する）。コードと集計は論文用の git リポジトリのリリースを Zenodo に置く（判断 24・25）。論文用のリポジトリは凍結のときに作り、最初の中身は英語の事前登録（GSE への言及なし・private・最初の push は研究者に `!` で頼む）。

## 背景（これだけ読めば始められる）

- 研究者の判断: `.steering/20261012-public-keystroke-matching-judgement/decisions.md`（判断 1〜5）と `.steering/20261012-public-keystroke-matching-prereg/decisions.md`（判断 6〜40。判断 16 以降は attack-me の各 round への対応の表）。
- attack-me の記録: `.steering/20261012-public-keystroke-matching-prereg/attack-me/prereg-public-matching/round-1/`〜`round-4/`（各 `verdict.md`）。接地の本文は `round-1/tmp/sources/`（git が無視する）。attack-me を閉じたら `tmp/` を消す（`panel.md` の URL と SHA-256 から取り直せる）。
- `design.md` は古い案（冒頭に注）。現行の設計は事前登録と `decisions.md` が正。

## やること

1. **合成の記録の検査**（`experiments/20261012-public-keystroke-matching/scripts/synthetic_logs.py` と自己検査・人のデータを使わない）。事前登録の「公開の他の列から長さが戻らないかの検査（凍結の前・合成の記録）」の節に書いたものを全部行う:
   - 削除・選択の削除・置換・貼り付け・移動（矢印・Home・End・マウス）・取り消しを含む合成の記録で、各形の出す列だけから区間の長さが戻るか（経路: `position` の差分・`word_count` の差分・`activity`・イベントの数・時刻の間隔・A1' の再生）。
   - R7(p): 正解の揃えの道が切れる割合・真の群が上限を超えた割合・正解の費用と真の対応での費用の差（判断 33）。
   - `align.py` の包み: 全文の終点の固定・∞ の扱い（「全候補 ∞」と「正解だけ ∞」）・R7 の群の列の差し替えと `max_group` を上限で呼ぶこと。(1,4) 以上の群が実際に選ばれる記録を含める。
   - R3-u の A3: 再生の誤りが 1 つあるときに、正解の時刻の項がどれだけ落ちるか（判断 38）。
   - 結果は `notes.md`。形や規則を変えたら、事前登録の「固定の前に見たもの」に変えた箇所と理由を書く（無ければ「変更なし」）。
   - 検査スクリプトは、実の合成の記録と実装で通しで回し、変異（判定式が常に真・語の偶然の一致など）で潰してから「確かめた」と書く。config を書き換えたら、重複キーを検出する形で JSON を読む（2026-10-12 に `json.loads` が重複キーを黙って通した）。
2. 研究者に凍結を問う（推奨と理由を添える）。凍結を決めたら:
   - 英語の版（学術的な英語・GSE への言及なし）を作り、論文用の git リポジトリを作って置く（private・最初の push は研究者に `!` で頼む）。
   - OSF の registration の各欄の文面を用意し、研究者が登録する（Claude はログインしない）。
   - 事前登録の冒頭の状態の行を「凍結: <日時>・コミット <sha>・OSF の DOI <doi>」に書き換えてコミットする。
3. 凍結の前の残り（小さいもの）: 倫理の考察の「同意は目的と手順を示したとだけ書かれている」（preregistration.md の倫理の節）の言い方を、KLiCKe の論文の一次と照らす（round 3 の監査役の参考の指摘）。
4. PoPETs のオンライン発表や録画の提出の要否を、採録論文の案内か PC chairs への問い合わせで確かめる（問い合わせは研究者が送る）。
5. 完了処理: `/cross-review` を 2 巡（コミットの後・パス限定）→ commit → push → PR → CI → merge → main の CI。

## 守ること

- 応答は日本語（AskUserQuestion の問い・選択肢も日本語）。★・⚠️ を多用しない。
- docs を先に読む。必須 Skill（`reproducibility-discipline`・`citation-ssot`・`verify-before-claiming`・`subagent-delegation`・`attack-me`）を参照してから手を動かす。
- データ（KLiCKe・ENJA15・KeyTAR）を取得しない（開始条件を満たし、研究者が決めるまで。KLiCKe は著者の返事待ち）。
- 打鍵の記録・本文を外部 LLM（Codex を含む）に送らない。Codex に渡すのはコードと文書の差分だけ。
- 有料の DB と有料の本文は使わない。
- `git add -A` や `git add <dir>` を使わず、ファイルを明示してステージする。並行セッションがあるので worktree で作業する。
- Codex の予算は、回す前に origin/main の台帳も見る。
