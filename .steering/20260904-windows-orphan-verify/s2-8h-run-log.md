# §2 8時間本番測定 — 実行ログ

> ★ このファイルは実行中の作業メモ（三次資料）。最終結果は `evidence-s2-*.md` /
> `decisions.md` 判断4 / `experiments/20260903-o1-runtime-cost/env.md` に転記する。

## ビルド確認 (B-0)

- 対象コミット (build-relevant path 最終変更): `1301a340430ef66249d1dbad80fc4b039e696f91` (2026-09-08 16:44:42)
- 既存バイナリ mtime: 2026-09-09 15:06（上記コミットより新しい → 再ビルド不要と判断）
- 出所: 前セッション `decisions.md` 判断3 で `npm run build && npm run tauri build -- --no-bundle`
  によりコミット `22538ccb5654c6e55a6ac0327cf7ece3b2f9dfd9` から作成されたもの
  （`22538cc` は `1301a34` より新しく、`1301a34`〜現HEAD間に build-relevant path の変更なし
  → バイナリは現HEADの内容と等価）
- 現在の作業ツリー HEAD: `8146f08c529b7d7ec6ccc4a11784ca8107552088` (2026-09-09 16:08:36, docs のみ)
- 起動目視確認: ユーザーに確認済み「正常表示（問題なし）」— devUrl エラーなし

## B-1 スモーク

- 1回目（GSE 未起動のまま実行）: 全列 0 → 手順の誤り（引き継ぎメモ B-1 に「GSE を起動した状態で」の
  記述が抜けていた。一次資料 `README.md` の「★ 0. まず 1 分のスモーク」に従い GSE を起動して再実行）
- 2回目（GSE 起動済みで実行）: 列数 8、`cpu_pct`(1.5〜3.1%) / `rss_kb`(37220〜37252) / `threads`(43〜45)
  すべて非ゼロ → 測定器 正常。結果は破棄済み（`results/with-gse` を rm -rf 済み）

## B-2 本番 8時間

1. GSE 未起動を確認（`tasklist` に無し）— 16:15 頃
2. サンプラ先行起動: `nohup bash experiments/20260903-o1-runtime-cost/run.sh with-gse` を
   background 起動（stdout/stderr は `experiments/20260903-o1-runtime-cost/results/sampler.log`）
3. 基線サンプル 3 行確認（全列 0、間隔 約30s）— 16:15:14 / 16:15:45 / 16:16:15
4. GSE 起動（バイナリ直叩き `src-tauri/target/release/gse-next.exe`）: **2026-09-09 16:16:41**
   （PID 27160）

- **測定終了予定時刻の目安**: 2026-09-10 00:16 頃（起動から約8時間）
- 8時間経過後、B-3（`summarize.py` で集計）→ B-4（env.md 記入）→ B-5（完了処理）へ進む
- ★ この間、研究者は通常どおりこの機を使用してよい（実験の目的が「ふだんの作業のあいだ」の負荷測定）
