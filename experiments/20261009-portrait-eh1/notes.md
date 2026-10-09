# notes — EH1 of the portrait

> ⚠️ EH0 の実験である。結果は「検査した範囲で見つからなかった」までで、「状態の情報が無い」の証明ではない（親タスク判断 8 E1-3）。合成した「停滞」は打鍵の統計の型であり、認知の状態ではない。「GSE が示した」と書かない。

## 接続

- **検証する仮説**: `docs/research-positioning.md` §5 の仮説には対応しない（肖像は EH0・RP の主張ではない）。問いは `.idea/20261005-motivation-fatigue-reentry-surface.md` §8.5 の EH1 と、親タスク `.steering/20261005-portrait-invitation-constraints/decisions.md` 判断 5・8（E1-1〜E1-8）。
- **X/Y**: MhD の X/Y も検証の X/Y も扱わない。`p_stuck` は陽性対照 PC2 の材料と、合成の記録の妥当性の確認にだけ使う（L0 の検証対象ではない）。
- **事前登録に当たるもの**: `.steering/20261009-portrait-eh1-eh2/design.md` §3（合否の基準・結果の前に `abfb2c45` で固定）。固定の後の逸脱は同 §8。
- **借用した手法**: 攻撃者の最大を取る漏れの検査の組み立て（`papers/ime-observation/experiment/preregistration.md` §6.8）。セッション単位の交差検証とブートストラップは標準の手法。

## 実行の記録

| 日時 | 機械 | world | 計器のコミット | 所要 | selftest |
|---|---|---|---|---|---|
| （Windows の機器で記入） | | v1 | | | |
| | | v2 | | | |

## 結果（基準は design §3・値は `results/<world>/*.json`）

### world v1（主の記録・固定した設計どおり）

（`summary.json`・`e13.json`・`e16.json`・`e14.json`・`e17.json`・`order.json` から、組ごとに緑・赤・判定不能を写す。陽性対照（PC1・PC2）と帰無の 95 パーセンタイルも書く）

### world v2（逸脱・design §8）

（同じ形で）

### 探索（固定の外）: scheduler `recent`

（`exploratory_recent.json`。合否を付けない）

### 記述: E1-2・戻ったときの変化と不在の長さの順位相関・D の組の距離

（`e12.json`・`describe.json`）

### E1-8 の候補

`results/<world>/e18/synth-*.png`（基準なし）。見本の画像は `results/<world>/samples/synth-*.png`。

## 逸脱・気づいたこと

（引き継ぎ先のセッションが気づいたことはここに書く。design §8 への反映は本体のセッションが行う）

## 限界

- E1-3 はセッションをまたいで学ぶ攻撃者を想定している。本人が 1 セッションの中で自分の写像を覚えることは検査しない（`keyed` の守りはこの想定に頼る）→ EH3 の M-4。
- 結果は合成の記録の仮定（区間の型・遷移・打鍵の分布）に条件づけられる。world v1 では打鍵の有無だけで停滞がほぼ決まり、v2 では停滞が修正・打鍵の間隔・まとまりの打鍵数にだけ出る。実際の打鍵はその間のどこかにある（未確認）。
- 生成器は仮の文法で、製品の候補ではない。見た目の美しさは測っていない。
- EH1 は Windows の機器の解析で回した。`analysis/` で OS により違うのはキーリピートの判定だけで（Windows は同じキーを離す前の再度の押下を除く・macOS は hook で autorepeat を捨てる）、合成の記録ではその重なりは押下の 0.069%。EH1 は入力層を通らないので、OS ごとの入力の違い（IME・観測するキー）は検査していない（decisions 判断 5 の補記）。
