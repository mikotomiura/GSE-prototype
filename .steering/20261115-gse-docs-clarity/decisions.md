# 重要な設計判断

すべて 2026-11-15 に研究者が AskUserQuestion で決めた（推奨はどれも Claude）。

## 判断 1: research-positioning の直し方

- **選択肢**: A 現行版を新しく書き旧版は履歴へ / B 冒頭に要約を足すだけ / C 改訂ブロックを本文へ溶かし込む
- **採用**: A
- **理由**: 改訂ブロック 3 層の上書きの鎖で、読み手が古い契約を掴む。旧全文を逐語で残せば失うものは無い。
- **トレードオフ**: ADR-047 Migration 1（本文は書き直さない）を改める。→ 判断 3。

## 判断 2: §3 先行研究・§4 差分（約 900 行）の扱い

- **採用**: 要点だけ新しい本文に置き（新規性として書ける範囲・数えないもの）、詳細は履歴の旧全文と docs/literature/ のカードへ参照でつなぐ。
- **却下**: 別の現行文書 related-work.md に切り出す（再編が重い）／逐語で残す（短くならない）。

## 判断 3: Migration 1 を改める決定の記録先

- **採用**: 小さな ADR-053 を起こす（文書の現行版と履歴を分ける作法）。
- **却下**: このタスクの decisions.md だけ（ADR-047 を読んだ人が古い決定を掴む）。

## 判断 4: 未踏の不採択コメントへの対応表

- **採用**: 内部の追跡表として docs/mitou_submission/ に置く（論点・今の対応・状態・根拠）。未対応も書く。応募書類の改訂はしない。

## 判断 5: 範囲と区切り

- **採用**: 広く全部、3 つの PR に分ける（PR1 research-positioning＋履歴＋ADR-053 / PR2 agent-shared・glossary・design-map・対応表・削除 / PR3 functional-design・architecture）。各 PR で /cross-review。push と PR はその都度研究者に確かめる。

## 判断 6: 不要な docs

- **背景**: 研究者の指示「WBS は不要だろうから消そう。他にも docs の中で不要だと思われるものは消そう」。
- **採用**（推奨案）:
  - 削除: `docs/wbs-verification-halfyear.md`・`docs/eh3-distribution-tag.md`（ADR-049 で EH3 は実施しない）・`docs/design-history.ja.md`（英語版と同じ内容）。
  - 履歴へ移す: research-positioning の旧全文・`docs/design-history.md`・`docs/calibration-smoke-runbook.md`（Phase1 は終了）・`docs/architecture/gse-v2-overview.md`・`intervention-decision-engine.md`・`domain-adapter-boundary.md`（7 月の Epic 期の設計。現行は gse-design-map と ADR）。
  - 残す: 削除保証の台帳 2 本・凍結した事前登録 3 本・O1 の運用文書・被験者向け文書・pilot-runbook（.age の復号手順を今も使う）・references・literature・theory・mitou_submission。
- **条件**: ADR の本文は書き換えないので、ADR からの参照は `docs/history/README.md` の旧パスの表で辿る。ADR 以外の参照元は付け替える。各削除の前に参照元を grep で確かめ、今も手順として使われているものが見つかったら止めて研究者に聞く。

## 判断 7: /cross-review 1 巡目（PR1）の扱い

- **判断日時**: 2026-11-15
- **結果**: Codex は成功（diff は旧全文の削除を除いて 638 行で送った）。code-reviewer は起動できず、cross-reviewer が直接照合した。ADR-047 Context の数値はすべて一致。
- **採用**:
  1. 両者一致: §9.1 の H3 の行が ADR にも事前登録にも無い帰結（「外なら先回りが成り立つ側へ戻る」）を足していた → 同等性の判定であることと、外・広すぎの読みは凍結で決めることに改めた。
  2. 節番号の付け替え漏れ（experiments/README.md・experiments/_template/README.md・`.agents/` のミラー）→ PR1 で直した。docs の残りは PR2/PR3 のタスクに載せた。
  3. §7 の「論文として別に出している・計算中」（一次なし）→ 削った。
  4. ADR-053 D1 の射程に glossary を含めていた → 主張を担う文書に限り、glossary は例外とした。D3 に節番号の grep を足した。
  5. §0 に ADR-053 が Proposed であることを添えた。
  6. adr/README の ADR-047 の行に「Migration 1 は ADR-053 D4 で改めた」を足した（ADR 本文は触らない）。
  7. H1 の行に、事前登録の草案 S1-C1 が「判定」のままであることを添えた。
  8. Codex: §4.3 の「記録しない」を手跡の表現用の入力に限り、既存のポインタの観測（`pointer_bin`）と区別した。
- **却下**: Codex P3（旧全文の保存が差分に無い）は送り方の副作用による誤検知。
- **2 巡目**: 直しは指摘どおりの局所の修正なので回していない。研究者が望めば回す。

## 判断 8: PR1 の出し方と ADR-053 の Accepted

- **判断日時**: 2026-11-15（研究者・AskUserQuestion）
- **採用**: 2 巡目の /cross-review は回さず、push して docs だけの PR を [skip ci] で出し、PR2 へ進む。マージは研究者が本文を読んでから。ADR-053 は今 Accepted にする（推奨の「本文を読んでから」ではなく、研究者が今を選んだ）。

## 判断 9: PR2 の削除・移動で見つけた運用中の手順と、付け替えない参照

- **判断日時**: 2026-11-15（Claude。判断 6 の条件の範囲で行った）
- **研究者デバッグ起動の手順**: `docs/calibration-smoke-runbook.md` §1.1–1.2（二重 gate）は今も使う手順で、README・agent-shared が指していた。手順書全体を履歴へ移す前に、この節だけを現行の `docs/verification-runbook.md` §2.0 へ移した（削除された Wall の強制ボタンの記述は持ち込まない）。README の参照は §2.0 へ向けた。
- **design-history.ja.md の削除**: README.ja.md の「設計の変遷」は英語版の履歴の写しへ向け、「（英語）」と添えた。
- **付け替えない参照**: ADR の本文・`.steering/`・文献カード・実験の notes・凍結した事前登録（v0.3）・`references.md` の用途の欄・コードのコメント（`src/components/InvitationGlyph.tsx`・`src-tauri/src/analysis/heads/*.rs`）は過去の記録として残し、`docs/history/README.md` の旧パスの表で辿る。コードのコメントを触ると docs だけの PR でなくなるので、このタスクでは触らない。
- **移した文書を参照し続ける現行の文書**: `docs/architecture/personalization-and-online-learning.md`・`task-adaptation-and-scope-gating.md` は gse-v2-overview などを「上位」として参照している。パスは履歴へ付け替えた。中身を今の設計に合わせるかは PR3 で見る。

## 判断 10: /cross-review 1 巡目（PR2）の扱い

- **判断日時**: 2026-11-15
- **結果**: Codex は完走（削除 3 本の中身を除いた 841 行）。HIGH 0・MEDIUM 5・LOW 4。ADR との照合は Claude 側の結果に拠る（Codex は固定 prompt で diff だけを見た）。
- **採用（すべて）**:
  1. 両者一致: personalization・task-adaptation が履歴の文書を上位として引いている → 2 文書の冒頭と agent-shared の表に「引用先は履歴・現行は gse-design-map と ADR」の注を足した。中身の見直しは PR3。
  2. verification-runbook §2.0 で dev 起動のコマンドが抜けていた → コードブロックで戻した（直接実行の例も）。
  3. 未踏の表の「段階的な縮退」の行が Wall の削除にすり替わっていた → 評価されたのは下位のモデルを残す昇格の設計なので、固定 baseline と昇格ゲートと保留に引き継いだ形で書き直した。
  4. agent-shared の散歩の行の出典 → ADR-024 D5・018 D3 と研究者の言を足し、ADR-017 D10 はセンシングの除外に限った。
  5. task-adaptation の行番号での参照 → 節名で引いた。
  6. gse-design-map の同意の承認 → `38e37ce1` の承認し直しと PR #411 を足した。
  7. コードのコメントの旧パスは判断 9 のまま残す。
  8. Codex: agent-shared の「推定は契機を作らず」が無条件だった → 「段 1・段 2 の主の比べで」に限り、既存の招待の例外を書いた。
  9. Codex: 未踏の表の 1 行目が先行予測の否定を識別の否定に広げていた → 先行予測に限り、小さい効果を否定できないこと・識別は未確定を書いた。
- 未踏の表の「面白い」は原本の語の可能性があるので言い換えた（逐語を repo に置かない）。

## 判断 11: PR3 の直し方

- **判断日時**: 2026-11-15（Claude。判断 5 と ADR-053 の範囲で行った）
- **functional-design**: 旧全文を `docs/history/functional-design-2026-11-15.md` に写し、構成から書き直した（概要・モードの表・機能 3.1〜3.12・ユースケース・非機能要件、320 行）。打鍵・IME・段 1・手跡・フック生存監視・非機能要件の節は、正確だった旧文を訂正の注を外して引き継いだ。Phase1 期の経路（ホットキーのラベル・較正・コホート判定）は 3.12 と 3.10 の表に要約し、詳細は履歴へ。
- **architecture**: 旧全文を `docs/history/architecture-2026-11-15.md` に写したうえで、全面の書き直しはせず古い箇所だけを直した。実装の記述の大半（スレッド・ロガー・G1・O1・提出・招待・段 1）は今も正確で、書き直すと誤りを持ち込む危険のほうが大きいと判断した。直したのは、図の Overlay・Wall の注記・スレッドの表（段 1 の駆動・手跡の読み）・IME_ACTIVE の注・Nudge の既定・O1 の表の「既定は true」・フロー 2・TSF の理由（UIPI ではない）・外部連携の表（Wall の行・macOS の失敗回数 10 → 3・O1 の提出）・拡張ポイント（推定の段・招待）。手跡の層の節を足した。
- **残したもの**: `docs/architecture/personalization-and-online-learning.md`（1401 行）と `task-adaptation-and-scope-gating.md` は Epic 期の Proposed の設計（ADR-008〜010）で、冒頭の注（PR2）だけにした。中身を今の設計に合わせるか履歴へ移すかは研究者に聞く。expression-channel などに残る旧節番号の参照は、research-positioning §0 の規則で受ける。

## 判断 12: /cross-review 1 巡目（PR3）の扱い

- **判断日時**: 2026-11-15
- **結果**: Codex は完走（履歴の写しを除いて送った）。HIGH 0。コードと ADR の照合は Claude 側で、数値・名前・ADR の引用はほぼすべて一致した。
- **採用**:
  1. 両者一致: §3.3 の貼り付け「本文は読まない」は不正確（`clipboard.rs` は文字数を数えるために本文をメモリへ取り込み、すぐ破棄する）→ 実装どおりに直した。
  2. Codex: 「ポインタの値は記録しない」が `pointer_bin` の記録と矛盾して読める → §2 の表と UC-1 で「手跡のためのポインタの値（座標・押下・場）」に限り、`pointer_bin` は記録すると書いた。
  3. §3.7 の PR の並びを番号順に。
  4. LOW の要確認: `review_marker` は `logger.rs`・`lib.rs` に、第 2 週の宣言 `invitationEnabled` は `src/App.tsx` にあることを確かめた（直しは不要）。
- **却下**: Codex「履歴の写しが diff に無い」は、除外して送った副作用による誤検知。
