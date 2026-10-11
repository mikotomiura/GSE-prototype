# design — portrait-eh3-prereg

## 1. アプローチ

研究者の決定（判断 1）を外枠として、事前登録の稿と実装の要件を書く。値の根拠は一次（親の判断 1〜15・台帳・ADR・コード・既存の事前登録）まで降ろす。凍結しない。

## 2. 成果物と置き場所

| 成果物 | 置き場所（案） | 備考 |
|---|---|---|
| 事前登録の稿 | `experiments/<日付>-portrait-eh3/preregistration-draft.md` | EH3 は実験なので `experiments/` に置く（`reproducibility-discipline`）。凍結のときに日付つきのディレクトリを確定する。⚠️ `docs/preregistration-*.md` には上げない（ADR・SSOT の書き換えをしない判断 1 #9 と、EH0 の格） |
| 実装の要件 | `.steering/20261011-portrait-eh3-prereg/implementation-requirements.md` | 別タスク（招待の PC 面・肖像の組み込み・記録・配布）の requirement の材料 |
| 研究者の決定 | `decisions.md` | |

## 3. 事前登録の稿の節（案）

1. 位置づけと主張の格（EH0・RP の主張ではない・「GSE が示した」と書かない）
2. 問い（M-1a〜M-6・E1-8 の none / seed・判断 7 の (a)〜(c)・`.idea` §8.6 の棄却線 (h)〜(k)・再査定の (a)〜(g)）
3. 条件と順序（肖像: 空 / D 日替わりの地模様 / A その回の形。招待の有無の組み方。E1-8 の none / seed の入れ方。日数・反順序化）
4. 参加者（6〜12 人・O1/G1 と分ける・募集と除外）
5. 手続き（初回の説明・I-1 の図像の意味・設定・日誌・経験サンプリング・終わりの面接。画面を録画しない M-1a）
6. 測るものと取り方（M-1a〜M-6 の項目・尺度の候補・記録の項目）
7. 閾値（判断 7 の「問題として観測された」・棄却線）を結果の前に固定する
8. 解析（記述が主・少人数なので個人に帰さない M-1b）
9. EH1 から持ち込む限界（親の判断 15・U-4 の閉じない点・判断 13 の代償）
10. 未決で凍結の前に埋めるもの（実装で決まる値・見本の選択・尺度）
11. 逸脱の扱い

## 4. 調べること（一次）

- ADR-026（PC-1〜PC-12）・ADR-033 D1〜D6・ADR-035 D1〜D6・ADR-030 補訂 1（再開の定義）・ADR-013（記録の自己記述）
- 既存の停滞の契機（`intervention.rs` の Nudge の判定・cooldown・cap）
- content-free の記録（`schema_dto.rs`・O1 の記録項目・同意文書の記録項目の一覧の場所）
- EH2 の壁紙の経路・EH1 の scheduler（recent60）と形の生成器の所在
- 既存の事前登録の書式（`docs/preregistration-p1-episode.md`・`docs/preregistration-v0.3.md`）
- 尺度: 反発 [V115] [V116]・罪悪感（S-PI のやり残し 5）

## 5. 検証

- 受け入れ条件（requirement.md）を節ごとに照合する。
- 凍結の前の段取り（attack-me・`/cross-review` 2 巡）は本タスクでは回さない。本タスクの完了時の `/cross-review` は文書の矛盾を見る 1 巡目・自分が足した規則の境界を見る 2 巡目を回す（memory: cross-review は 2 巡）。
