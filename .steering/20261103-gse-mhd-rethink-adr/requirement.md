# gse-mhd-rethink-adr —— MhD の再考の ADR 案（A）

## 背景

- ADR-045（2026-11-03）で主の対象を行動上の停滞に置き、詰まりは停滞の中身の 1 つとして記述することにした。ADR-045 の「決めずに残すもの」に、MhD の criterion 直結の段のラベルの対応づけと、ADR-042 D5 の詰まりの件数の下限が残った。
- ADR-044 で HMM 0.5.0 は段 1 の終わりまで凍結し、`p_stuck` は固定 baseline の比べの床と H3 の手がかりの 1 つに狭めた。3 状態（Flow / Incubation / Stuck）の名前は、主張（research-positioning の headline・L1 Stuck）と画面（Dashboard.tsx）に残っている。
- ADR-019 D1 の段の順（固定 baseline → criterion 直結 → 個人・タスク適応 → 時系列）は、ADR-042 D1 が MhD の主張を人の中の推論に限ったことと、段 1 の確認が 2〜4 名であることに合っていない。
- 引き継ぎ: `.steering/_handoff/next-session-gse-mhd-rethink-abc.md` §2 の A。

## ゴール

ADR-046 を 1 本書き、研究者が grill で選んだ次の 5 点を記録する（判断 1〜5・decisions.md）。

1. 形: 今決められる名前とラベルは中身を決め、データ待ちの段の順の中身と ROCKET 系の値は候補・決める時期・条件だけを決める。ステータスは Accepted。
2. 3 状態の名前は主張・被験者が見る画面・新しい文書から外す。記録の列名・enum は内部の識別子として残す。
3. criterion 直結の段のラベルは二値の形と ADR-042 D5 の下限の形を残し、対象を「陽性の類」に一般化する。類は本人の探索の後・C4 を開く前に事前登録で選ぶ。詰まりは候補の 1 つ。
4. criterion 直結の段は初めから 1 人ごとに学ぶ。「個人・タスク適応」の段は人をまたぐ部分プーリングと読み、段 1 の人数では使わない。時系列の段の候補に HMM の構造を残した 1 人ごとの EM を足す。順は昇格ゲートが担うまま。
5. ROCKET 系を使い始める条件は 3 つ（その人の criterion 直結の段が昇格ゲートを通った後・独立な陽性の件数が公開データの空回しで過学習しなかった件数以上・核の数と罰と特徴の選び方を使う前にコミット）。値は決めない。

## スコープ

### 含むもの
- `docs/adr/ADR-046-*.md` の新規
- `docs/adr/README.md` の一覧への追加と、読み替える既存 ADR の行への注記
- `docs/architecture/gse-design-map.md` の推定（MhD）の行に ADR-046 を書き足す
- `docs/glossary.md` の Flow / Incubation / Stuck・MhD の項への注記（名前が状態の主張ではないこと）
- 引用が要る記述は `citation-ssot` に従う（新しく依拠する文献が無ければ「無い」と書く）

### 含まないもの
- 事前登録 `docs/preregistration-stage1.md` の改訂（S1-A3・S1-E4・S1-E8 の書き直しは別タスク。ADR の Migration に書く）
- `docs/research-positioning.md` の headline・L1 の言い方の改訂（ADR-041 Migration 4 の別タスク）
- `src/components/Dashboard.tsx` の文言の変更・コードの変更（被験者向けの文は契約なので別タスク）
- 記録の列名・schema の変更
- B（CoAuthor での個人ごとの学習の試験）・C（停滞の中身の割合の幅）
- H2・H3 の種別（事前登録の改訂で決める）

## 受け入れ条件

- [ ] ADR-046 が判断 1〜5 をすべて含み、既存 ADR のどこを残しどこを読み替えるかの表がある
- [ ] 既存 ADR の本文を書き換えていない（docs/adr/ADR-0[0-4]*.md に差分が無い）
- [ ] ADR-046 の主張の語を全文 grep で確かめた（verify-before-claiming ルール 7・8）
- [ ] 禁止の言い方を含まない（停滞の始まりで詰まりを検出した・Physical Anchor 未実装・「疲労」・作業中の認知状態）
- [ ] /reimagine で初回案と作り直し案を比べ、研究者が採る案を選んだ
- [ ] /cross-review（code-reviewer ＋ Codex）を回し、指摘の採否を decisions.md に記録した

## 関連ドキュメント

- docs/adr/ADR-019・ADR-021 D11・ADR-042・ADR-044・ADR-045
- docs/preregistration-stage1.md（S1-A3・S1-E4・S1-E8）
- docs/architecture/gse-design-map.md
- .steering/20261103-gse-design-consolidation/mhd-anatomy.md
- experiments/20261103-mhd-pipeline-dryrun/notes.md

## 運用メモ
- /reimagine 適用: Yes
- 理由: 研究者が「使う」を選んだ（Claude の推奨は「使わない」。分かれ道は grill で閉じており、残るのは読み替えの書き方だけという見立てだった）
