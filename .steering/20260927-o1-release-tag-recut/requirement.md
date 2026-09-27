# 要件 — o1-release-tag-recut

## 背景
`bash scripts/check-o1-release-readiness.sh` が未達 2 件。そのうち 1 件が
「リリースタグ v0.1.36 は古い。タグ以降にコードが 5 コミット動いている」（PR #233 の reconcile 修正
a819f0d / 016b5f2 / 914e88f / a94e0ac / 53e98b6）。実装は main に merge 済みで、配るバイナリに入っていないだけ。
v0.1.36 は G1 の配布タグとして凍結済み（ADR-034 D3・`experiments/20260801-controlled-friction-task/distribution-tag.md`）。

## ゴール（検証可能な形）
1. バージョンを 0.1.37 に上げ（4 ファイル）、merge コミットに `v0.1.37` を切る（push は研究者承認後）。
2. CI（build-macos / build-windows / release）が全 job success。
3. Release 資産の実体検証（版文字列・署名・対照つき）。
4. `make-common-app-zip.sh --mode o1 --tag v0.1.37 --config Form_O1/o1_submit.json` で O1 用 zip を作り、独立に再検算。
5. `docs/o1-distribution-tag.md` を新設して記録（append-only）。
6. **Done**: `bash scripts/check-o1-release-readiness.sh` の出力から「リリースタグ … は **古い**」が消え、
   「O1 実装を含むリリースタグがある（v0.1.37）」が ✅ になる。未達は同意文書の「未了」1 件だけになる。

## スコープ外
- 同意文書の「未了」（6 択 ESM 追補の採否）— 研究者判断待ち。
- G1 の記録票 A/B/C・G1 の配布タグ（v0.1.36 のまま凍結）。
- reconcile.rs などコードの変更。
- Drive 差し替え・被験者への送付（研究者）。
- 20260927-g1-o1-release-and-o1-resilience の T3。

## 運用メモ
- /reimagine 適用: No
- 理由: リリース手順の再実行で設計判断を伴わない（型は v0.1.36 の手順）。
