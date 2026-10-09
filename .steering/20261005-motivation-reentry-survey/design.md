# 設計

## アプローチ

`/literature-review` の Step 0〜9 をそのまま回す。Step 0・1 は研究者が AskUserQuestion で承認した（`decisions.md` 判断 1）。

### 下位問い（証拠の種類が変わる境界で割った）

| ID | 下位問い | angle |
|---|---|---|
| SQ1 | AI 疲労・テクノストレス・デジタル疲労の尺度は動機・関与の低下を含むか。個人間で強く相関するか。弁別できるか（共通の 1 因子か） | A1 心理測定 |
| SQ2 | 人の特性としての疲労・動機が、その人の中のエピソード（停滞・放棄・中断からの復帰）の頻度や終わり方を変える、という多層の証拠はあるか | A2 ESM・日誌の多層研究 |
| SQ3 | 非随伴の驚き・新奇性・好奇心・予期しない小さな肯定的出来事は、内発的動機・課題への再関与を上げるか（⚠️ 2026-10-05 用語の訂正: 「非随伴」は不正確。カードでは「予期しない驚き」「予期しない・評価を含まない驚き」と呼ぶ・判断 4） | A3 好奇心・驚き・予期しない報酬・肯定的感情 |
| SQ3 の反証 | 慣れ（新奇性効果の減衰）・ゲーム化の減衰・随伴の学習・予期しない刺激による注意の逸れで、驚きは消えるか、害になるか | A4 反証（必須） |
| SQ4 | 中断からの復帰や作業の切れ目に出会う周辺表示・壁紙・手がかりは、復帰のコストを増やすか減らすか | A5 再開の手がかり・周辺表示 |

### 回し方

- angle ごとに `general-purpose`（`model: sonnet`）を 1 本、計 5 本を 1 メッセージで並列に投げる。入れ子は禁止。締切 20 分。
- subagent は詳細を scratchpad のファイルに書き、最後の応答は短い要約にする（メインの文脈を守る）。
- 既出の文献（[P99] [P107] [P77] [P203] [P205] [P206] [P209] [P218] [P341]–[P343] [P351] [P355] [V144]、AI 疲労 DB の AF001・AF026）は重ねて取らない。
  - ⚠️ 2026-10-05 追記: ここでの「既出」は「探索で重ねて取らない」の意味である。AF001 は references.md に [P362] として既に登録されていた。AF026（ZEF）は未登録だったので、本ラウンドで [P437] として登録した（`decisions.md` 判断 2・4）。
- 断定に使う一次はメインが開く（WebFetch → 保存された PDF を pypdf）。
- 3 票の検証はメインが 3 つの視点（内的妥当性 / 外挿＝GSE の場面へ / 効果量の頑健性）で行い、カードに票を書く。

## 変更対象（worktree `C:/wt/motivation-reentry-survey`・ブランチ `docs/motivation-reentry-survey`）

- 新規: `docs/literature/20261005-motivation-fatigue-reentry-surface.md`
- 追記: `docs/references.md`（末尾の次番号から・append-only）、`docs/literature/_index.md`（1 行）
- 新規: `.steering/20261005-motivation-reentry-survey/`（本ディレクトリ）
- 版管理外: `C:/GSE-prototype/.idea/20261005-motivation-fatigue-reentry-surface.md` §7

## 影響範囲

- `references.md` の採番は並行セッションと衝突しうる → 登録の直前と merge の前に origin/main と他ブランチの末尾番号を測り直す。
- RP・ADR・コードには触らない。

## 検証戦略

- `python scripts/check_citations.py` を違反なしまで繰り返す。
- コミット後に `/cross-review` を 2 巡（1 巡目 = 自文書と他文書の矛盾 / 2 巡目 = 足した主張の境界条件）。パス限定・出力先は scratchpad。
