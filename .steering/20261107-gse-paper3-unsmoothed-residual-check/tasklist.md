# タスクリスト

## 場面ごとの道具（完了前に照合する）
- 設計の比べ → /reimagine（済）
- コードのレビュー → code-reviewer と /cross-review（Codex）
- 決めること → AskUserQuestion（1 問ずつ・推奨と理由）
- 本計算 → HP Z2（研究者が回す・引き継ぎの文を渡す）
- push と PR → 研究者が確かめてから

## 準備
- [x] 引き継ぎ §3・verdict・判断 11・tau-extend の条件とコード・kit を読む
- [x] 判断 1〜5（列・残差・範囲・読みの形）を AskUserQuestion で決める
- [x] /reimagine で設計を比べ、v2 を採る（判断 6）
- [x] conditions.md と SEED を書く
- [x] conditions.md と SEED をコードより前にコミットする

## 実装
- [x] kit: `symbolizer.py` に `last_raw`、`variants.py`（u・n の規則）、README・selftest
- [x] `build_variants.py`（Mac で新しい中間と P-U の門）
- [x] `load.py`・`fit.py`（列を選ぶ読み込み・範囲を絞った当てはめ・npz）
- [x] `residual.py`（擬似残差と自己相関）
- [x] `report.py`・`repro_check.py`・`run.sh`・`mutate.sh`
- [x] `selftest.py`（P-KIT〜P-PIN と変異 m41〜m51）

## テスト
- [x] 合成の selftest がすべて通る
- [x] 名指しの変異がすべて赤になる
- [x] Mac の合成で時間を測り、見積もりを条件の末尾に足す
- [x] Mac で中間を作り、P-U（全行）が通る
- [x] 配管の合成の通し（`e2e_synth.py`・判断 8）が通る

## レビュー
- [x] code-reviewer と /cross-review（計算の前）
- [x] 指摘への対応（実データの前なら条件の後の変更として記録）

## 本計算と記録
- [x] HP Z2 の引き継ぎを書く（研究者が回す）
- [x] P-REPRO が通る（葉 5,751・外れ 0）
- [x] notes.md（読みの形のとおり・集計値だけ・判断 12・13）
- [ ] 論文 3 の外枠を直す（C1・C2 の Strength・限界・補足の表・4.2 の 1 文）
- [ ] code-reviewer と /cross-review（notes と外枠の diff・集計値だけ）

## 完了処理
- [ ] design.md・decisions.md の最終化
- [ ] git commit（push と PR は研究者が確かめてから）
