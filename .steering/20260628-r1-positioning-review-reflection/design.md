# 設計

## 実装アプローチ

**docs のみの編集**。研究主張の言い回しは ground-truth（functional-design / v0.4 / WBS / glossary）に突合して直す。
指摘 A は「取った後の測り方・解釈」の問題で **Phase 1 収集は不変**。コード根拠:

- `src-tauri/src/schema_dto.rs:82` — feat（FeatSnapshot）は **p_stuck を既にログ**している。
- `src-tauri/src/analysis/calibration_eval.rs` — 較正は現状 `x_friction`/`y_engagement` のみ集約し
  `x↔q1`/`y↔q2` で C-index を出す（p_stuck は集約していない）。
  → よって p_stuck↔criterion の検証は**後段オフライン分析の追加**で可能（収集変更不要）。本タスクは docs 反映が主、
  較正 CLI への p_stuck 分析追加は「任意・別タスク」に切り出してよい。

## 変更対象（修正するファイル）

- `docs/research-positioning.md` — 指摘 A/B/D/E/G/H/I/J/K/L の文言修正（§1 headline・§4 差分・§5 仮説・§8）
- `docs/references.md` — 指摘 I/J に伴う使用箇所の調整（番号は append-only、renumber 禁止）
- `docs/experiment-tracking.md` — 必要なら H-Y 交絡・追加アウトカムの追記（指摘 D）
- `docs/glossary.md` — 指摘 F（MhD 登録）/ L（GATE1-3 ↔ PreReg マッピング登録）

## 指摘の反映内容（C 除外）

| ID | 重大度 | 反映 |
|---|---|---|
| A-1 | CRIT | §1/§5: 「GATE3 の C-index が検証するのは MhD の X/Y 二軸（X↔Q1・Y↔Q2）であって p_stuck そのものではない」を明示。p_stuck は X/Y から導く Need 信号で妥当性は別問題、と橋渡し（line33 の "→ p_stuck" 矢印を定義）。★正当化方針はユーザー確認後に確定。 |
| A-2 | CRIT | criterion label(Q1/Q2) の限界（プローブ反応性・観察者効果）を §8 か新設「方法論的限界」節へ。軽減策（遅延プローブ/事後リコール一致/プローブ頻度感度）併記。 |
| B | HIGH | H-X2 を確認的→探索的(heterogeneity 推定)へ格下げ。cutoff・近接アウトカムの向きは事前登録・凍結と明記。 |
| D | HIGH | H-Y(§5)/§8 に交絡（諦め/別デバイス/検索移行/新規性/実験者効果）＋追加アウトカム（完了率/放棄率/時間超過/外部支援自己申告）＋軽減（washout/実験者盲検/カウンターバランス）。 |
| E | HIGH | §4 差分に「本文非保存制約下で検出→Need/Opportunity 分離→不便介入まで閉じた統合プロトタイプ＋前向き較正」を新規性の核として明示。headline B 維持＋「本文非保存の制約下で」修飾。 |
| F | HIGH | glossary に MhD 登録（略語展開＋Stage1 HMM/Stage2 ロジ）。 |
| G | MED | GATE1（尺度理解ビネット）は現スモークで「延期」（functional-design §7）。「X1 鎖は現状 GATE2 起点」と整合。 |
| H | MED | C-index 0.65/0.55 を「事前登録の慣習値」or preregistration 参照と明記。 |
| I | MED | §1 の依存主張から [P11] を外し [P4] のみ。P11/V6 は keystroke 検出文脈のみ。 |
| J | LOW | [P15] は測定点(§5 副指標)のみで引用。 |
| K | LOW | 「X1 Kill でも貢献」に真の null/abandon 条件を併記。 |
| L | LOW | [v0.4§0/§9]→§0 訂正。GATE1-3↔PreReg を glossary 登録。 |
| **C** | — | **除外（Physical Anchor は実装予定。§9 等の PA 記述はいじらない）** |

## 既存パターンとの整合性

- 引用は `citation-ssot` skill（P/V 名前空間・append-only・恒久 ID・tombstone・renumber 禁止）。
- 用語追加は `glossary.md` を SSOT として登録（CLAUDE.md の規約）。

## テスト戦略

- 引用整合: `grep -oE '\[[PV][0-9]+\]'` で本文 vs references.md を集合比較（過去ターンと同手順）。
- overclaim 検出: 「分類」「認知状態を読む」「順序弁別」等の grep。
- 独立レビュー: code-reviewer + `/cross-review`（Codex）。wrapper は `bash scripts/run-codex-*.sh`（+x 欠落のため）。
  必要なら先に `chmod +x scripts/*.sh`（verify-setup L-1 と同根）。

## ロールバック計画

R1 成果物は全て未コミット。問題時は `git checkout -- docs/...` で破棄、または編集前にブランチを切る
（`docs/r1-review-reflection` 等）。glossary は既存ファイルなので diff を最小に保つ。

## 補足: 別件（本タスク外）

- **Windows overlay 透過バグ**（`index.html` の不透明 `<body background:#0f172a>` が overlay 窓の透過を潰し、
  ダッシュボード起動時・プローブ時に白い残存箱が出る）は **別タスク**。修正案: body の背景を外し、`.start-screen` /
  VignetteTest コンテナに `background-color: var(--color-bg)` を付与。Windows 実機確認要。
