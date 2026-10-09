# notes — EH1 round 3 of the portrait

> EH0 の実験である。結果は「検査した範囲で見つからなかった」までで、「状態の情報が無い」の証明ではない（親タスク判断 8 E1-3）。合成した「停滞」は打鍵の統計の型であり、認知の状態ではない。「GSE が示した」と書かない。

## 接続

- **検証する仮説**: `docs/research-positioning.md` §5 の仮説には対応しない（肖像は EH0・RP の主張ではない）。問いは親タスク `.steering/20261005-portrait-invitation-constraints/decisions.md` 判断 5・8 の E1-3 と、第 2 回の判断 9（`.steering/20261009-portrait-eh1-round2/decisions.md`）。
- **事前登録に当たるもの**: `.steering/20261010-portrait-eh1-round3/design.md` §3（合否の基準・どの結果よりも前に `58634d65` で固定）。固定の後の逸脱は同 §8。
- **第 2 回との関係**: 合成の記録と `gse-replay` のビルドは第 2 回と同じ。変えたのは E1-3 の検査器の確かめ方（PC-cal）・神託・ラベル（L1800）・判定する組（8 組）。第 2 回の判定（判定不能）は書き換えない。
- **借用した手法**: 攻撃者の最大を取る漏れの検査の組み立て（`papers/ime-observation/experiment/preregistration.md` §6.8）。セッション単位の交差検証とブートストラップ、等度回帰（pool-adjacent-violators）は標準の手法。

## 実行の記録

| 日時 | 機械 | 何を | 計器のコミット | 所要 | selftest |
|---|---|---|---|---|---|

## 結果

（本番の後に書く）

## 逸脱・気づいたこと

（design §8 と対応させて書く）
