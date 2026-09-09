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
- [ ] 1 分スモーク（8 列出るか・7/8 列目が空か）
- [ ] サンプラを先に起動 → 基線 1 分 → GSE 起動 → 8 時間本番（with-gse のみ）
- [ ] env.md の Windows 行を埋める
- [ ] summarize.py で集計・判定表と照合

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
- [x] decisions.md 作成（ブランチ判断・GUI 自動化判断・判断1〜3）
- [ ] 完了報告（未検証を隠さず明記）— ⚠️ §2（8時間稼働コスト）は次セッションへ持ち越し
