# タスクリスト

## 場面ごとの道具（完了前に照合する）

| 場面 | 使うもの |
|---|---|
| ADR・事前登録に出典を書く | citation-ssot（references.md を先に引く） |
| 事実を断定する・ADR を確定する | verify-before-claiming（全文 grep・1 節で代表させない） |
| experiments/ を作る | reproducibility-discipline（SEED・env・run.sh・provenance） |
| コードのレビュー | code-reviewer（条件のコミットの後・計算の前に一度） |
| 完了時 | /cross-review（Codex には O1 の記録を送らない・既知の未決の一覧を添える） |

## 準備
- [x] 引き継ぎ・next-study-design 判断 1〜13・ADR-042・空回しの v1・synthesis §5 を読む
- [x] grill（判断 1〜5）

## ADR-043
- [x] 引用する番号の中身を references.md で確かめる
- [x] ADR-043 を書く
- [x] README の一覧に足し、ADR-031・032 の行に注記
- [x] next-study-design 判断 2〜13 との突き合わせ（落ちがないか grep）

## 事前登録の草案
- [x] `docs/preregistration-stage1.md` を書く
- [x] 出典の対応表で全項目を照合
- [x] リンクハブ（agent-shared.md）への追加の要否

## 空回しの次の版
- [x] conditions.md・SEED・env.md・data.md・run.sh
- [x] daysim.py と dryrun_v2.py・--selftest
- [x] 条件とコードをコミット（計算の前・073e0580）
- [ ] code-reviewer（計算の前）と指摘の対応
- [ ] 計算・results・notes.md

## レビューと完了
- [ ] /cross-review と指摘の対応（decisions.md）
- [ ] 引き継ぎを書く（attack-me は凍結の前の版で Codex つき）
- [ ] コミット・push（PR は研究者に確かめてから）
