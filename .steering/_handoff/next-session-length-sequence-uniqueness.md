# 引き継ぎ: 公開テキストで「長さの並び」がどれだけ一意かを見積もる（ADR-039 D6 の関門の最初の実測）

作成 2026-10-09（Windows の機・`C:\GSE-prototype`）。新しいセッションで `/clear` の後に始める。
返答・記録では絵文字や記号（★・⚠️）を多用しない（研究者の指摘）。応答は日本語。

## 1. 何をするか

ADR-039 D6（公開前の関門）の攻撃のうち「照合」（公開した打鍵の記録を、候補の文章と突き合わせて、その文章を書いたときの記録かを当てる）について、
**長さの代理の並び**（Space の間の英字の打鍵の個数、変換の Space までの打鍵の個数、句読点や Enter の間の打鍵の個数）が、公開テキストの中でどれだけ一意になるかを見積もる。
人のデータは使わない。研究者が 2026-10-09 に「最初の一歩はこれ」と決めた（`.steering/20261009-release-deidentification-survey/decisions.md` 判断 7）。

分かるのは「長さだけを、正確に使える攻撃者」の場合の目安であって、照合の危険の上限ではない。時刻の癖や本人の過去の文章を使う照合は含まず、結果はコーパスと分け方に依存し、打鍵の個数は本文の長さと同じではない（判断 8・ADR-039 D6 の注）。結果を「上限」と書かない。

## 2. 先に読むもの

- `docs/adr/ADR-039-research-use-and-release.md` の D5・D6（2026-10-09 の注と裁定）
- `docs/literature/20261009-keystroke-release-reidentification.md` のカード 3（時刻と長さの並びから内容が漏れる）と「GSE への還元」
- issue #333 の本文と 2 件のコメント（`gh issue view 333 --comments`）
- 当方の記録に何が残るか: `src-tauri/src/analysis/anonymize.rs` の `KeyCategory`（Alphabetic / Numeric / Punctuation / SentencePunctuation / Space / Enter / Backspace ほか）と `src-tauri/src/logger.rs` の key 行、`src-tauri/src/packaging.rs` の `anonymize_ndjson`
- 日本語で境界が崩れる点: `docs/research-positioning.md` の [P272] の段落（語間に空白が無い・変換の確定が見えない境界を作る）
- 青空文庫の取り方: memory「青空文庫の取得元」（本家 aozora.gr.jp を使う・版は zip の SHA-256 で固定）

## 3. 始め方

1. `/start-task` から入る（CLAUDE.md）。作業記録は `.steering/<日付>-length-sequence-uniqueness/`、実験は `experiments/<日付>-length-sequence-uniqueness/`（`reproducibility-discipline` Skill: 乱数の種・依存の固定・コーパスの版の固定）。
2. 設計の論点は、次をそれぞれ推奨と理由を添えて AskUserQuestion で研究者に聞く（推測で決めない）:
   - コーパス: 青空文庫だけか、英語のテキストも入れるか（英字入力の単語長）。研究者や参加者の文章は使わない。
   - 観測の型（何を「長さ」とみなすか）: 英語は Space の間の英字の打鍵数。日本語のローマ字入力は変換の Space までの打鍵数で、かなからローマ字への打鍵数の換算が要る（「ん」の nn、拗音、促音などの揺れ）。文は SentencePunctuation の間、段落は Enter の間。文節の区切りには形態素解析器が要る（新しい依存になる → 研究者の承認が要る）。最初は句読点と改行の間の打鍵数だけで始める案もある。
   - 指標: 長さの並びを k 個並べたとき、コーパス中の位置が一意に決まる割合（k の関数として）。候補の数 N を変えたときの照合の正答率を、偶然の水準 1/N と並べる。
   - 条件: 理想の観測（推敲なし・長さが正確）だけか、雑音（打鍵数の ±1、変換の揺れ、BackSpace の混入）も入れるか。
3. 合格の基準の数値（ADR-039【決 6】）は研究者が決める。Claude は数値を出さない。この実測は合否の判定ではなく、照合攻撃の試作（次の一歩）を設計するための見積もり。

## 4. してはいけないこと

- O1・G1・Phase1 の記録（NDJSON）を読まない・使わない。打鍵の記録や参加者の情報を外部の LLM（Codex を含む）に送らない（`data-privacy` Skill）。
- 研究者や参加者の書いた文章をコーパスにしない。
- 新しい依存（形態素解析器など）を承認なしに入れない。
- 見積もりを「照合の危険の上限」「安全の証明」と書かない。

## 5. 終わり方

- 結果のノートを `experiments/` と作業記録に書き、ADR-039 D6 と issue #333 に要点を返す（ADR は本文を消さず、日付つきの注で足す）。
- `/finish-task`（code-reviewer と Codex の `/cross-review`）→ git-workflow ルール 6（commit → push → PR → CI が緑なら merge → main の CI 確認）。計測の run が走っているかは推測せず、分からなければ研究者に聞く。
- Codex の台帳（`.codex/budget.json`）は、回す前に origin/main の値も見る。2026-10-09 は 198,420 / 6 回だった。

## 6. 関連して未決のもの（このタスクでは決めない）

- ADR-039【決 5-b】（ライセンス・利用規約の文面）、【決 6】（合格の基準）、【決 6-a】（正解のある入力: IME 論文の合成入力か、決まった文章を打つ課題か）、【決 9】。
- 同意文 v2 の第 3 層の文面（最大の範囲で取る・照合と健康状態の推定のおそれを書く）: `.steering/20261007-research-use-and-release/consent-v2-draft.md`。同意文は契約なので、別のタスクで研究者と詰める。
- BRM への問い合わせ A の送付（送るのは研究者・`.steering/20261007-research-use-and-release/inquiry-drafts.md`）。
