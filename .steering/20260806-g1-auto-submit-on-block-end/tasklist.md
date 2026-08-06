# タスクリスト

⚠️ ★ **`/reimagine` 適用 = Yes**。設計 (§2) を承認する前に一度破棄して作り直す。

## 0. 準備

- [ ] ★ `data-privacy` Skill を読む（**外部送信を足すので必須**）
- [ ] `architecture-rules` / `rust-standards` / `typescript-standards` を読む
- [ ] `.steering/20260805-g1-app-mode-and-log-rotation/decisions.md` R-7 / R-8 / **R-9** を読む
      （★ R-9 は「蒸し返さない」ことの確認）
- [ ] `experiments/.../consent.md` §3 と `participant-guide.md` を読む（★ 何を約束済みか）
- [ ] ⚠️ 環境: `~/.rustup/toolchains/stable-aarch64-apple-darwin/bin` を PATH に足す
      （`requirement.md` 環境メモ。★ 足さないと `run.sh` の cargo ゲートが飛ぶ）

## 1. 調査

- [ ] `packaging.rs` の匿名化がどこで `vk` → `category` に落としているかを読む
- [ ] `find_latest_session_ndjson` の呼び出し元をすべて洗う（`--input` 追加の影響範囲）
- [ ] ローテート後に「閉じたばかりのファイルのパス」を取れるか確認する
      （`logger.rs` / `lib.rs` の `g1-block-ended` 発火経路）
- [ ] Tauri 2.0 で HTTP を出す経路（`tauri-plugin-http` / `reqwest` 直）と CSP の要件を確認する
- [ ] ⚠️ GAS Web App の **POST サイズ上限・実行時間上限**を実測する（★ 推測で書かない）
      → `.age` の実サイズは P-1 の 4 本で見積もる

## 2. 設計

- [ ] design.md を書く（送信の実行主体・キューの形・ブロック番号の採り方）
- [ ] ★ **`/reimagine`**: requirement.md だけを見て v2 案を作り、2 案を比較して採用を決める
- [ ] decisions.md の「まだ決めていないこと」4 件を閉じる
- [ ] ★ `consent.md` の**文案**を出して研究者の承認を取る（★ 実装より先）

## 3. 実装

- [ ] **B**: `gse-submit` に `--input <path>` を追加（★ ゼロ引数の既定挙動は不変）
- [ ] **A**: G1 モード時のスタート画面に参加者 ID 欄。妥当な ID まで「開始する」を無効化
- [ ] **A**: ID の永続化と次回起動時の復元
- [ ] **C**: ブロック自動終了時に、閉じたばかりの NDJSON を指定して `.age` を生成
- [ ] **D**: 送信 + 失敗時のローカル保持 + 再送（起動時 / 次ブロック終了時）
- [ ] **E**: スタート画面の「未送信 N 件」（★ 0 件なら何も出さない）
- [ ] **G**: GAS Web App (`doPost`) の実装と配備

## 4. テスト（★ 足したら、その場でわざと壊して赤を実測する）

- [ ] `--input` の単体テスト（存在しないパス / 別ディレクトリ / 既定との共存）
- [ ] ★ **匿名化の実測**: 生成した `.age` を `gse-unpack` で開き、`vk` が無く `category` があること
- [ ] ★ ID 未入力で開始できないこと（**空にして赤を実測**）
- [ ] ★ 送信失敗 → ローカル保持 → 再送 の一巡（**エンドポイントを落として赤を実測**）
- [ ] ★ **通常運用（マーカー無し）で画面も挙動も変わらない**非回帰
- [ ] `cargo test --workspace` / `--features package`
- [ ] `gse-replay --snapshot` golden 4 本 / `emit_schema` byte-equal / `npx tsc --noEmit`
- [ ] `bash run.sh` GREEN（★ cargo ゲートが**実際に走った**ことを "N / N 本" で確認）

## 5. レビュー

- [ ] `code-reviewer` と **`security-checker`** を並列起動（★ 外部送信なので security 必須）
- [ ] HIGH 指摘への対応
- [ ] ★ `/cross-review`（★ 予算はその場で計算する。⚠️ **メモの数字を根拠にしない**）

## 6. ドキュメント

- [ ] `consent.md` §3（自動送信の明記）
- [ ] `participant-guide.md` / `protocol.md §4b.2`（手順から「提出する」の手作業を落とす）
- [ ] `docs/architecture.md`（送信層の位置づけ）
- [ ] `experiments/.../notes.md`（★ 実測したことだけ）

## 7. 完了処理

- [ ] design.md / decisions.md の最終化
- [ ] `/finish-task`
