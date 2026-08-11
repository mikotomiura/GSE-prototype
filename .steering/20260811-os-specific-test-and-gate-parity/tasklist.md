# タスクリスト

## 準備
- [x] 関連 docs / requirement.md / design.md を読む
- [x] file-finder / impact-analyzer で影響範囲を調査
- [x] 現状 cargo test --workspace が全 green (330 tests) であることを確認

## 実装 (各項目 = 1 コミット。実装 → cargo build/test → 緑を確認 → commit の交互サイクル)

- [ ] 1. `ime_macos.rs`: `select_ime_source` を抽出 + テスト追加 (ローカル macOS で検証可能)
- [ ] 2. `ime_windows.rs`: `is_stale_winevent_active` / `is_ime_candidate_class_name` を抽出 + テスト追加
      (macOS ローカルは構文チェックのみ、実行確認は Windows CI)
- [ ] 3. `hook_windows.rs`: `ime_open_after_press` / `ime_open_after_release` /
      `classify_ime_nav_key` / `is_ime_mode_key` を抽出 + `is_typing_key` にテスト追加
      (同上、Windows CI 依存)
- [ ] 4. `.github/workflows/ci.yml`: `build-windows` job に pubkey.txt プレースホルダ検査ステップを追加

## テスト
- [ ] cargo build --workspace (macOS ローカル、ime_macos.rs のみ実効検証)
- [ ] cargo test --workspace (macOS ローカル、既存 330 テスト + 新規 ime_macos テストの green 確認)
- [ ] git push → Windows CI (windows-latest, check job) が緑になることを確認
      (ime_windows.rs / hook_windows.rs の新規テストがここで初めて実行される)
- [ ] macOS CI (gse-mac-selfhosted) が緑のままであることを確認 (regression なし)

## レビュー
- [ ] code-reviewer + security-checker を並列起動
- [ ] HIGH 指摘への対応 (MEDIUM はユーザーに判断を仰ぐ)

## ドキュメント
- [ ] docs 更新は不要 (内部実装のテスト容易化のみ、公開 API・アーキテクチャ変更なし)

## 完了処理
- [ ] design.md の最終化 (実装後に差分があれば追記)
- [ ] decisions.md に「抽出方針」「Windows 確認体制」「Windows gate 対象」の3判断を記録
- [ ] git commit (4項目 = 4コミット、git-workflow Skill に従う)
- [ ] /finish-task (cross-review 含む)
