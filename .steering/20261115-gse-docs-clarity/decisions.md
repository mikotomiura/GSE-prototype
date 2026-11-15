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
