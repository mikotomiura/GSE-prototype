# OS 固有コードの CI テスト・release gate 非対称の是正

## 背景

2026-08-11 のセッションで、Windows / macOS 各 OS 固有コードに対する CI 検査の実装状況を
一次資料 (`.github/workflows/ci.yml`, 各ソースファイル) で実測した結果、以下の非対称が判明した。

- `check` job (windows-latest + gse-mac-selfhosted の OS マトリクス) 自体は稼働しており、
  `#[cfg]` 分岐漏れは機械的に検知される (実例: `src/input/liveness.rs:397-430` の
  閉じ忘れ事故が「手元 macOS では緑・Windows CI で赤」として記録済み)。
- `src/input/liveness.rs` には `#[cfg(all(test, target_os = "windows"))]` /
  `#[cfg(all(test, target_os = "macos"))]` の対のテストが既にある。
- しかし `src/input/hook_windows.rs` (0 テスト) / `src/input/ime_windows.rs` (0 テスト) /
  `src/input/ime_macos.rs` (0 テスト) は無テスト。`hook_macos.rs` は 4 テストを持つが、
  対称な Windows 側テストが無い。
- `build-macos` job には pubkey.txt のプレースホルダ検査 (release gate) があるが、
  `build-windows` job には対応する検査が無い。

## ゴール

- `ime_windows.rs` / `ime_macos.rs` の判定ロジックにユニットテストを追加する。
- `hook_windows.rs` のコールバック内から判定/変換ロジック (純粋関数部分) を抽出し、
  `hook_macos.rs` の 4 テストと対称な水準のテストを追加する。
  ★ コールバック本体の構造は変えない (Atomic + channel のみという制約は維持)。
- `build-windows` job に、`build-macos` の `Verify researcher public key present` と
  同条件 (age1 行の有無) の pubkey.txt プレースホルダ検査を追加する。

## スコープ

### 含むもの
- `src/input/hook_windows.rs` からのロジック抽出 + テスト追加
- `src/input/ime_windows.rs` / `src/input/ime_macos.rs` へのユニットテスト追加
- `.github/workflows/ci.yml` の `build-windows` job への pubkey.txt 検査ステップ追加
- 上記変更が Windows CI (windows-latest) で実際に緑になることの確認

### 含まないもの
- フックコールバック自体の実装ロジックを作り替えること (挙動変更ゼロ)
- macOS の `--features package` バイナリ隔離実測 (`strings` grep) に相当する
  Windows 側の同等機能の新設 (今回は pubkey.txt 検査のみ)
- Windows ポータブル配布フォルダ (exe 隣に pubkey.txt を置く手動/半自動packaging手順) の
  CI 化そのもの — 今回はリポジトリ内 `src-tauri/resources/pubkey.txt` のプレースホルダ検査のみ
- Windows 実機での手動確認そのもの (CI 緑化までを本タスクのゴールとし、
  実機での追加確認は別途 Windows 実機セッションに依頼する)

## 受け入れ条件

- [ ] `cargo test --workspace --target x86_64-pc-windows-msvc` で `ime_windows.rs` /
      `hook_windows.rs` の新規テストが実行され、全て緑になる (Windows CI で確認)
- [ ] `cargo test --workspace --target aarch64-apple-darwin` で `ime_macos.rs` の
      新規テストが実行され、全て緑になる (macOS CI で確認)
- [ ] `hook_windows.rs` から抽出した関数が、macOS 側でもコンパイル可能な形
      (プラットフォーム非依存なロジックである) か、または Windows 専用のまま
      `#[cfg(all(test, target_os = "windows"))]` でテストされているかのいずれかを満たす
- [ ] `build-windows` job で `src-tauri/resources/pubkey.txt` にプレースホルダ (age1 行なし) が
      残っている場合に CI が fail する (macOS 側と同条件)
- [ ] 既存の `hook_macos.rs` 4 テスト・`liveness.rs` の対テストが regression なく通る
- [ ] `.steering/20260811-os-specific-test-and-gate-parity/decisions.md` に
      「抽出方針」「Windows 確認体制」「Windows gate 対象」の 3 判断を記録する

## 関連ドキュメント

- `docs/development-guidelines.md` §3 (両 OS に対のテストを置く方針)
- `.github/workflows/ci.yml` (`check` job のマトリクス構成、`build-macos` の pubkey gate)
- `src/input/liveness.rs:397-430` (対テストの実装例)
- memory `windows-only-code-needs-ci`

## 運用メモ
- /reimagine 適用: No
- 理由: 設計選択肢は grill で既に閉じている (抽出方針=純粋ロジックのみ / Windows確認体制=CI+実機依頼 /
  gate対象=pubkey.txtプレースホルダ検査)。アーキテクチャ変更や公開APIの新設を伴わない、
  既存コードへのテスト追加とCI設定の小規模拡張であり、複数案の比較検討は不要。
