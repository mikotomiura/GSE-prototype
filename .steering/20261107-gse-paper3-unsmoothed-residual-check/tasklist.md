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
- [ ] conditions.md と SEED をコードより前にコミットする

## 実装
- [ ] kit: `symbolizer.py` に `last_raw`、`variants.py`（u・n の規則）、README・selftest
- [ ] `build_variants.py`（Mac で新しい中間と P-U の門）
- [ ] `load.py`・`fit.py`（列を選ぶ読み込み・範囲を絞った当てはめ・npz）
- [ ] `residual.py`（擬似残差と自己相関）
- [ ] `report.py`・`repro_check.py`・`run.sh`・`mutate.sh`
- [ ] `selftest.py`（P-KIT〜P-PIN と変異 m41〜m51）

## テスト
- [ ] 合成の selftest がすべて通る
- [ ] 名指しの変異がすべて赤になる
- [ ] Mac の合成で時間を測り、見積もりを条件の末尾に足す
- [ ] Mac で中間を作り、P-U（全行）が通る

## レビュー
- [ ] code-reviewer と /cross-review（計算の前）
- [ ] 指摘への対応（実データの前なら条件の後の変更として記録）

## 本計算と記録
- [ ] HP Z2 の引き継ぎを書く（研究者が回す）
- [ ] P-REPRO が通る
- [ ] notes.md（読みの形のとおり・集計値だけ）

## 完了処理
- [ ] design.md・decisions.md の最終化
- [ ] git commit（push と PR は研究者が確かめてから）
