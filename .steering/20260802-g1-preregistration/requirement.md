# G1 統制タスク実験の事前登録（凍結）

## 背景

Phase1 は **GATE2 = pass / GATE3 = DataInsufficient（判定保留）**である
（`experiments/20260731-phase1-calibration-analysis/` — GATE3 母数に乗ったのは 5 名中 1 名のみ。
PreReg-4 の「全員 > 0.55」を判定するには最低 3 名要る）。**Kill ではない。**
真因は HMM ではなく**ラベル供給側**（Q1 の straight-lining・プローブ収量）だった。

→ **同じ設計のまま被験者を増やしても同じ理由で落ちうる。**
`§8.2` の **G1（統制タスク実験）は criterion を主観プローブでなく実験者の条件ラベルにする**ため、
この律速を設計で回避できる唯一の実験である。設計は
`experiments/20260801-controlled-friction-task/` に既にあるが**未実施・未事前登録**だった。

## ゴール

**G1 を実施前に事前登録して凍結する。** `docs/preregistration-v0.3.md`（Phase1 の凍結契約）は
**変更しない**。G1 はそこに含まれない新規ゲートなので**別文書として登録する**。

## スコープ

### 含むもの
- `experiments/20260801-controlled-friction-task/preregistration.md`（凍結文書）
- `config.json` の機械可読化（凍結基準を本文書と一致させる）
- `notes.md` の未解決 5 件のうち **4 件を閉じる**
- 先行プロトコル調査（`notes.md` が「未調査」と自認していた項目）と文献登録

### 含まないもの
- **実験の実施**（Phase1 完了・凍結解除後）
- 課題文の作成 / 倫理・同意手続き / Tier 0/1 特徴量の実装 / 解析スクリプトの実装
- コード変更（凍結対象に触れない）

## 受け入れ条件

- [x] 判定基準を**データを 1 件も見る前に**凍結した
- [x] `preregistration-v0.3.md` を変更していない
- [x] 先行プロトコルの有無を調査し、結果を設計に反映した
- [x] 研究者判断（positive control の採否 / n）を確定して反映した
- [x] `notes.md` の未解決のうち閉じた項目と残した項目を明示した
- [x] 変更はすべて**判定を厳しくする方向**であり、合格しやすくする変更を含まない
- [x] コード変更ゼロ・PII なし・raw NDJSON なし

## 関連ドキュメント

- `experiments/20260801-controlled-friction-task/README.md`（設計本体）
- `docs/architecture/personalization-and-online-learning.md §8.2`（G1 の定義）/ `ADR-009 D7`
- `experiments/20260731-phase1-calibration-analysis/`（しきい値 0.70 の根拠・Phase1 の判定）
- `docs/architecture/task-adaptation-and-scope-gating.md §2.4 / §4.1`（copy task と scope 検出）
