# タスクリスト — O1 リリースと配布物の作り直し

## §0 事実確認（★ メモを一次資料にしない）

- [x] PR #130 の状態を確認 → `MERGED` (2026-08-30T04:29:43Z)
- [x] `git ls-tree v0.1.29 src-tauri/src/o1.rs` → 空（O1 を含まない）
- [x] `git tag --contains 7a062cc` → 空
- [x] `check-o1-release-readiness.sh` → 通過 17 / 未達 2
- [x] runner の online / repo の visibility を確認（両方 online・PRIVATE だが直近 run は全 success）
- [x] `0.1.29` の全出現箇所を走査し、直す／残すを分類

## §1-A タグを切る

- [x] `docs/handoff-timeout-scoping` を main へ入れる
- [x] `package.json` / `tauri.conf.json` / `Cargo.toml` を 0.1.30 へ
- [x] `cargo check` で `Cargo.lock` を追随させる（`schannel` は触らない）
- [x] コミット & main へ
- [x] `git tag v0.1.30 && git push origin v0.1.30`
- [x] CI 完走を待つ（`build-macos` / `build-windows` / `release`）
- [x] `gh release view v0.1.30 --json assets` に dmg / exe が揃うことを確認
- [x] `git tag --contains 7a062cc` が `v0.1.30` を返すことを確認

## §1-B secret ローテート（★ 研究者が「する」と決定）

- [x] `openssl rand -base64 32` で新しい値を作る
- [x] ローカル `Form_O1/o1_submit.json` の `secret` を差し替え
- [ ] ⚠️ **研究者**が Apps Script のスクリプトプロパティを差し替え（Claude からは不可）
- [ ] `checkSubmitConfig()` を回して緑を確認

## §1-C 配布物を作り直す

- [x] `./make-common-app-zip.sh --mode o1 --tag v0.1.30 --config ../../Form_O1/o1_submit.json`
- [x] 新ゲートが全部通ったことを実行ログで確認
- [x] G1 の zip が作り直されていないことをタイムスタンプで確認

## §1-D macOS 実機での通し確認（⚠️ 配布物そのものから）

- [x] zip を展開してデスクトップへ
- [x] 初回セットアップ → `OK: 準備できました（O1 モード）…`
- [x] `gse-next.app` をダブルクリック（TCC の再要求の有無を記録）
- [x] ファイル名が `gse_o1_*`
- [x] `gse-app.log` に `Probe scheduler thread started` が**無い**
- [x] 「記録中 · 作業の種類: …」の表示
- [x] 「開始する」を押していないのに `key` 行が出る
- [x] `intervention_enabled` が false
- [x] 宣言 4 択を選び直す → ローテートして新ファイルに `session_meta`
- [x] 「すぐ止める」→ `recording_pause` / 停止中 `feat` 行 0
- [ ] ⚠️★★★ 「この時間帯の記録を消す」（一時停止 → 削除の順・`redaction_ledger.jsonl`）
- [ ] 自動起動の登録 → 再起動して本当に自動で立ち上がるか

## §1-E 送信 timeout

- [x] `.idea/issue.md` を読む
- [x] 圧縮の不在を自分で確かめる（`flate2` / `zstd` / `gzip` / `brotli`）
- [x] `/reimagine` で「固定値 vs サイズ比例＋下限」を比較
- [ ] 実測（合成ペイロードで転送時間）
- [ ] 記録票を「実測済み」にし、コードを直す

## §1-F 配布フォルダ

- [ ] zip 2 本を Drive へ置く
- [ ] リンクを開いて 2 本見えることを確認

## §1-G README（⚠️ 承認が要る）

- [ ] Drive から実際に落として Gatekeeper のダイアログを踏む
- [ ] 【3】ログイン項目の表示を実機に合わせる
- [ ] 承認後: `【ドラフト・未承認】` を消す → 検査語も外す → `--selftest` が 1 件減る

## §2 完了処理

- [ ] `code-reviewer` + `security-checker` 並列
- [ ] `/cross-review`（ブロックされたら skip 理由を明記）
- [ ] `check-o1-release-readiness.sh` の最終結果を記録
