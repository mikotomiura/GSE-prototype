# タスクリスト

## 準備
- [x] 引き継ぎメモ・o1.rs doc・decisions.md・README.md を読む
- [x] `~/.gse/` 状態確認（o1_consent_ack 不在 = 自動提出は元々無効）
- [x] env 確認（Windows 11 Home / MSI MS-7E66 / デスクトップ機 = Win32_Battery null 想定）
- [x] `cargo test --features package --workspace` 緑確認（653 passed / 0 failed、再起動前に確認済み）
- [x] `target/release/gse-next.exe` を現 HEAD (`22538cc`) で再ビルド・コミットハッシュ記録
- [x] ⚠️ 副次発見: 素の `cargo build --release` は `custom-protocol` feature が付かず
      メインウィンドウが devUrl 依存になる欠陥に気づき、`npm run tauri build -- --no-bundle`
      で作り直して解消（`decisions.md` 判断3・本番配布ビルドへの影響なしを確認済み）

## §1 孤児回収の実機検証
- [x] O1 モード用フォルダに `o1.mode` を置く
- [x] A: 起動 → 数分打鍵 → CloseMainWindow() で正常終了 → session_end 即時確認（✅ 実測済み）
- [x] B: 起動 → 数分打鍵 → taskkill /F → 再起動 → orphan sweep ログ確認（✅ 実測済み）
- [x] 壊れ状態: 読み取り専用ファイルで起動 → cannot close ログ・closed に数えられないこと（✅ 実測済み）
- [x] べき等: 既に閉じたファイルで再起動 → session_end が 2 行にならないこと（✅ 実測済み）
- [x] C: 起動 → 数分打鍵 → **GSE を終了せず** OS 再起動 → 次セッションで session_end 有無を確認
      （⚠️ 試行1 は前提不成立で不採用・試行2 で確定。`decisions.md` 判断1/判断2・
      `evidence-s1-A-B.md` 参照。結論: 翻訳されず、次回起動の orphan sweep のみが回収 = §1-B と同じ経路）

## §2 稼働コスト実測
- [x] 1 分スモーク（8 列出るか・7/8 列目が空か）（✅ 列数8、cpu/rss/threads非ゼロ確認。
      引き継ぎメモのB-1にGSE起動の記述漏れがあり一次資料README優先で是正）
- [x] サンプラを先に起動 → 基線 1 分 → GSE 起動 → 8 時間本番（with-gse のみ）
      （✅ サンプラ16:15:14〜00:15:40完走・GSE起動16:16:30.569（gse-app.log一次資料）。
      906サンプル(=samples.tsv 907行−ヘッダ1行、うち判定対象903行)）
- [x] env.md の Windows 行を埋める（✅ Windows 11 Home / MSI MS-7E66 / バッテリーなし実測済み）
- [x] summarize.py で集計・判定表と照合（✅ CPU平均MARGINAL・他はPASS・NDJSONは一次資料で
      確定値化しPASS・エネルギー影響/バッテリーは原理的測定不能。`decisions.md`判断4）

## §3 overlay クリック透過
- [x] O1 起動・放置状態で四隅+中央の hit-test（WindowFromPoint）（✅ 5/5 箇所で奪っていない）
- [x] 窓の位置・サイズを記録（`debug_overlay_window_state` はビルド時ゲートで直接呼べず、
      `EnumWindows`+`GetWindowRect`+`GetWindowLong` で代替。`evidence-s3-overlay.md` 参照）
      ⚠️ 表示状態（Nudge/プローブ中）の hit-test は GUI 操作手段なしのため未検証

## 完了処理
- [x] `~/.gse/o1_consent_ack.bak` を戻す（→ N/A。`~/.gse/` に `o1_consent_ack` 自体が
      存在しない＝バックアップも作られていないことを実測確認済み）
- [x] 検証用 NDJSON の後始末を記録（§1-C 試行2 の対象 1 件 ＋ 診断中に発生した副産物 4 件、
      計 5 件を証跡転記後に削除。`evidence-s1-A-B.md` 参照）
- [x] decisions.md 作成（ブランチ判断・GUI 自動化判断・判断1〜4）
- [x] §2 で生成した実 O1 セッション NDJSON（`gse_o1_20260909_071630.ndjson` 他）の後始末を
      研究者に確認する（★ 研究者から「削除する」の回答を得て、証跡転記後に
      `gse_o1_20260909_071040.ndjson`（B-0診断）/ `..._071328.ndjson`（B-1スモーク）/
      `..._071630.ndjson`（本番8時間分）の3件を削除済み。バイト数・パス等は
      `evidence-s2-runtime-cost.md` に記録済み・内容は1文字も読んでいない）
- [x] 完了報告（未検証を隠さず明記）— §2 完了。タスク全体（§1/§2/§3）の完了報告を作成し
      `/finish-task` を実行した（`/cross-review` 2巡・HIGH2件/MEDIUM4件を修正済み。
      詳細は commit `c1e09d0`/`0963d07`/`764ea72`）
