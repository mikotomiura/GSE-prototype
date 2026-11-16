# 手跡の入った版 v0.1.42 を本人の段 1 の配布フォルダへ入れる

## 背景

本人の段 1（macOS）の後期は 2026-11-24（割付の表の `late_start_day` 20781）に始まる。配布のフォルダ
（`~/GSE-S1-self/S1_実施用_macOS/`）の gse-next は v0.1.41（2026-11-07）で、手跡のコードを持たない
（引き継ぎ `next-session-gse-stage1-self-late-period.md` §1）。このままでは後期に手跡が出ず、
ADR-052 D4 の関門 2 を満たせない。割付の表は作り直せない。

## ゴール

11-24 より前に、手跡を含む v0.1.42 の macOS の版が本人の配布フォルダで Measuring で動いている。

## スコープ

### 含むもの
- 版を 0.1.42 に上げる（4 箇所）→ PR → マージ → タグ `v0.1.42` → CI の release で macOS の配布物
- `check-s1-release-readiness.sh --audience self --os-only macos` を通す
- 手跡が入っていることと割付の表の SHA-256 を手で確かめる（判断 2）
- 入れ替え（`gse-next.app` だけ・表と印のファイルは残す）と起動し直しの確かめ

### 含まないもの
- 3 名に配る版（Windows の手跡が通るまで配らない・ADR-052 D5／判断 1）
- 配布の門に手跡の検査を足すこと（3 名の版の前に別タスク・判断 2）
- 回 1（前期の漏れの確かめ）

## 受け入れ条件

- [ ] タグ `v0.1.42` の macOS の配布物が CI で作られた
- [ ] 門が exit 0
- [ ] バイナリに手跡の文字列があり、表の SHA-256 が記録の値 `e19e51c9…20da` と合う
- [ ] 入れ替え後に `Measuring` と `input_monitoring=true`、今日が前期なので手跡は出ない

## 関連ドキュメント

- ADR-052 D4・D5、ADR-051、`.steering/_handoff/next-session-gse-stage1-self-late-period.md` §1
- memory build-ci-and-pilot-distribution（タグを打つ前の検算・concurrency）

## 運用メモ
- /reimagine 適用: No
- 理由: 版上げと配布の作業で、設計判断を伴わない
