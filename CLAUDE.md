# GSE (Generative Struggle Engine) プロトタイプ開発ガイド
## Claude Code による段階的実装マニュアル

---

## 📋 プロジェクト概要

**プロジェクト名**: GSE (Generative Struggle Engine) Prototype  
**目的**: キー入力を監視し、ユーザーの認知状態（FLOW/INCUBATION/STUCK）を推定し、視覚的フィードバックを提供するWindows向けプロトタイプ  
**技術スタック**: Rust, Windows API, Direct2D/DirectX  
**開発期間**: 7〜10日間（MVPスコープ）

---

## 🎯 Claude Codeを使う理由

Claude Codeは以下の点でこのプロジェクトに最適です：

1. **複雑なWindowsシステムプログラミング**の実装を自然言語で指示できる
2. **マルチファイル編集**を一度に実行可能
3. **段階的な開発**をサポート（各Phaseで独立したコミットが可能）
4. **Gitワークフロー**を自動化できる
5. **エラー修正とデバッグ**を対話的に実行

---

## 🚀 前提条件

### 1. システム要件
- **OS**: Windows 10/11 (64bit)
- **Node.js**: 18.x以上
- **Git**: 最新版
- **Visual Studio Build Tools**: C++開発ツールチェーン

### 2. Claude Code のセットアップ

#### インストール（ネイティブインストーラー推奨）

**Windows (WinGet):**
```bash
winget install Anthropic.ClaudeCode
```

**または npm:**
```bash
npm install -g @anthropic-ai/claude-code
```

#### 認証

```bash
claude auth
```

ブラウザが開き、Claude.aiアカウントでログインします。

#### 動作確認

```bash
claude doctor
```

すべての項目に ✓ が表示されればOKです。

### 3. Rust環境のセットアップ

#### Rustのインストール
```bash
# Windowsの場合、rustup-init.exeをダウンロード
# https://rustup.rs/
```

#### Visual Studio Build Toolsのインストール
Visual Studio Installerから「C++によるデスクトップ開発」ワークロードをインストール

#### 確認
```bash
rustc --version
cargo --version
```

---

## 📂 プロジェクト構造

Claude Codeで自動生成される最終的な構造：

```
gse-prototype/
├── Cargo.toml                 # Rustプロジェクト設定
├── CLAUDE.md                  # このファイル（開発ガイド）
├── README.md                  # プロジェクト説明
├── .gitignore                 # Git除外設定
└── src/
    ├── main.rs                # エントリーポイント
    ├── input/
    │   ├── mod.rs             # 入力モジュール
    │   ├── keyboard.rs        # キーボードフック
    │   └── tsf.rs             # TSF統合（Phase 6）
    ├── inference/
    │   ├── mod.rs             # 推論モジュール
    │   ├── rules.rs           # ルールベース推論
    │   └── hmm.rs             # HMM実装（Phase 4）
    └── ui/
        ├── mod.rs             # UIモジュール
        └── overlay.rs         # オーバーレイ描画
```

---

## 🎬 開発フロー：Claude Codeでの実装

### 事前準備：プロジェクトの初期化

```bash
# 作業ディレクトリに移動
cd ~/projects

# Claude Codeを起動
claude
```

Claude Code内で以下のコマンドを実行：

```
/generate Create a new Rust project named gse-prototype with the following structure:
- src/main.rs (with basic logging setup using tracing)
- src/input/mod.rs and src/input/keyboard.rs (empty modules)
- src/inference/mod.rs and src/inference/rules.rs (empty modules)
- src/ui/mod.rs and src/ui/overlay.rs (empty modules)
- Cargo.toml with dependencies: windows, tracing, tracing-subscriber, chrono, serde, serde_json
- .gitignore for Rust projects
- README.md with project overview
```

---

## 📝 Phase別開発ガイド

### Phase 0: プロジェクト初期化 ✅

**所要時間**: 30分〜1時間

**Claude Codeでの実行手順:**

1. プロジェクト作成（上記の `/generate` コマンド）
2. ビルド確認

```
/ask Can you build the project and verify everything compiles?
```

**期待される出力:**
```
✓ Project structure created
✓ Cargo.toml configured
✓ cargo build succeeded
```

**確認コマンド（ターミナル）:**
```bash
cd gse-prototype
cargo build
cargo run
```

---

### Phase 1: Global Key Hook実装 🎯

**所要時間**: 4〜6時間

**目標**: キー入力をキャプチャし、FlightTimeをコンソールに表示

#### ステップ 1-1: Cargo.tomlの更新

```
/generate Update Cargo.toml to add the following Windows API features:
- Win32_Foundation
- Win32_UI_WindowsAndMessaging
- Win32_System_LibraryLoader

The windows dependency should be version 0.58
```

#### ステップ 1-2: キーボードフックの実装

```
/generate Implement a Windows global keyboard hook in src/input/keyboard.rs that:
1. Uses SetWindowsHookExW with WH_KEYBOARD_LL
2. Captures all key events (WM_KEYDOWN)
3. Calculates flight time (time between consecutive key presses)
4. Logs flight time to console using tracing::info!
5. Stores the last key press time in a static variable
6. Calls CallNextHookEx properly

Use the windows crate and follow Rust best practices for unsafe code.
```

#### ステップ 1-3: main.rsの更新

```
/generate Update src/main.rs to:
1. Initialize tracing with INFO level
2. Install the keyboard hook from src/input/keyboard
3. Enter a Windows message loop
4. Properly cleanup the hook on exit
5. Handle errors gracefully

Print "GSE Core Initialized" on startup.
```

#### ステップ 1-4: テストと検証

```
/ask Build the project and run it. Test if it captures keyboard input from Notepad.
```

**成功基準:**
- ✅ メモ帳でタイプすると、コンソールに `FlightTime: 125ms` のようなログが表示される
- ✅ Ctrl+Cで正常に終了する

**デバッグが必要な場合:**
```
/ask The hook is not capturing keys. Can you check if:
1. We're using the correct hook type (WH_KEYBOARD_LL)
2. The message loop is running properly
3. We have the right permissions (may need to run as administrator)
```

---

### Phase 2: ルールベース状態推論 🧠

**所要時間**: 3〜4時間

**目標**: FLOW/INCUBATION/STUCKの3状態を判定し、色分けしてログ出力

#### ステップ 2-1: 状態定義

```
/generate Create src/inference/rules.rs with:
1. An enum FlowState with three variants: Flow, Incubation, Stuck
2. A function classify_state(flight_time_ms: u64, backspace_count: u32) -> FlowState
3. Classification rules:
   - Flow: flight_time < 100ms AND backspace_count < 2
   - Stuck: flight_time > 500ms OR backspace_count > 5
   - Incubation: everything else
4. Add Debug and Clone derives to FlowState
```

#### ステップ 2-2: 統合とログ出力

```
/generate Update src/input/keyboard.rs to:
1. Import the classify_state function from inference::rules
2. Call classify_state with the flight_time
3. Log the state with different log levels:
   - Flow: info! with green color indicator
   - Incubation: warn! with yellow color indicator  
   - Stuck: error! with red color indicator
4. Format the log as: "[STATE: FLOW] FlightTime: 85ms"
```

#### ステップ 2-3: Backspaceカウントの追加

```
/generate Enhance the keyboard hook to:
1. Track Backspace key presses separately
2. Count backspaces in a 5-second sliding window
3. Pass this count to classify_state
4. Reset the count after 5 seconds of no backspace activity

Use a VecDeque or similar data structure to track timestamps.
```

**成功基準:**
- ✅ 高速タイピング → 緑の `[STATE: FLOW]`
- ✅ 迷って削除 → 黄色の `[STATE: INCUBATION]`
- ✅ 完全に止まる → 赤の `[STATE: STUCK]`

---

### Phase 3: HMM統合（オプション） 📊

**所要時間**: 6〜10時間

**目標**: Hidden Markov Modelによる確率的状態推定

⚠️ **注意**: このフェーズは高度です。Phase 2のルールベースで十分なデモが可能です。

#### ステップ 3-1: HMM構造の実装

```
/generate Create src/inference/hmm.rs with:
1. A struct HMM containing:
   - transition: [[f64; 3]; 3] (transition probability matrix)
   - state_probs: [f64; 3] (current state probabilities)
2. Implement HMM::new() with these initial transition probabilities:
   From FLOW:       [0.85, 0.10, 0.05]
   From INCUBATION: [0.40, 0.45, 0.15]
   From STUCK:      [0.30, 0.20, 0.50]
3. Initial state: [1.0, 0.0, 0.0] (start in FLOW)
```

#### ステップ 3-2: Forward Algorithm

```
/generate Add an update method to HMM that:
1. Takes an observation (flight_time_ms)
2. Calculates observation probabilities for each state using Gaussian distributions:
   - FLOW: mean=50ms, std=30ms
   - INCUBATION: mean=250ms, std=100ms
   - STUCK: mean=1000ms, std=500ms
3. Performs Bayesian update using the forward algorithm
4. Returns the most likely current state
```

#### ステップ 3-3: 統合

```
/generate Update main.rs or keyboard.rs to:
1. Create a global HMM instance
2. Call hmm.update() on each key press
3. Log the state probabilities: "[STATE: FLOW] Prob: 0.87 | INCUBATION: 0.10 | STUCK: 0.03"
```

**デバッグヘルプ:**
```
/ask The HMM probabilities don't look right. Can you:
1. Add debug logging for observation probabilities
2. Verify the transition matrix multiplication
3. Check if probabilities sum to 1.0
```

---

### Phase 4: オーバーレイUI 🎨

**所要時間**: 6〜8時間

**目標**: 状態に応じた画面フェード効果

#### ステップ 4-1: Cargo.tomlの更新

```
/generate Add the following Windows graphics features to Cargo.toml:
- Win32_Graphics_Direct2D
- Win32_Graphics_Direct3D11
- Win32_Graphics_Dxgi
- Win32_Graphics_Gdi
```

#### ステップ 4-2: 透明ウィンドウの作成

```
/generate Create src/ui/overlay.rs with:
1. A function create_overlay_window() that:
   - Creates a layered, transparent, topmost window covering the entire screen
   - Uses WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_TOPMOST styles
   - Makes it click-through (no interaction)
   - Returns the HWND
2. A function set_overlay_alpha(hwnd: HWND, alpha: u8, color: u32) that:
   - Uses SetLayeredWindowAttributes to change opacity and color
```

#### ステップ 4-3: 状態に応じた描画

```
/generate Create a function update_overlay(hwnd: HWND, state: FlowState) that:
- FLOW: alpha=0 (completely transparent)
- INCUBATION: alpha=25, color=0xFFFF99 (light yellow)
- STUCK: alpha=76, color=0xFFFFFF (white fog)

Call this from the keyboard hook when state changes.
```

#### ステップ 4-4: 統合とテスト

```
/generate Update main.rs to:
1. Create the overlay window on startup
2. Pass the HWND to the keyboard hook
3. Update the overlay when state changes
4. Destroy the window on exit
```

**成功基準:**
- ✅ FLOW状態 → 画面は完全に透明
- ✅ INCUBATION状態 → 薄い黄色のフェード
- ✅ STUCK状態 → 白い霧が画面を覆う
- ✅ オーバーレイはクリックスルーで、他のアプリの操作を妨げない

**トラブルシューティング:**
```
/ask The overlay window is not showing. Can you check:
1. If we're using the correct window styles
2. If SetLayeredWindowAttributes is being called with the right parameters
3. If the window is actually created at the topmost Z-order
```

---

### Phase 5: TSF統合（高難度・オプション） ⚠️

**所要時間**: 8〜16時間

**目標**: IME未確定文字列の取得

⚠️ **警告**: TSFは最も困難なフェーズです。Phase 4までで十分なデモが完成しています。

#### フォールバック戦略
TSFが動作しない場合：
1. Global Key Hookのみを使用
2. 「日本語入力中は精度が低い」という制約を明記
3. 将来の課題として文書化

#### ステップ 5-1: TSF構造の調査

```
/ask Can you research how to implement a TSF (Text Services Framework) text input processor in Rust?
I need to:
1. Register as a text input processor
2. Receive composition string events
3. Access the current composition text
4. Work with ITfContext and ITfCompositionSink

Provide a high-level architecture first before we start coding.
```

#### ステップ 5-2: 段階的実装

```
/generate Create src/input/tsf.rs with:
1. COM initialization for TSF
2. ITfThreadMgr setup
3. Basic text sink implementation
4. Log when composition starts/ends

Start with the simplest possible implementation that just detects when IME is active.
```

**このフェーズは時間制約により省略可能です。**

---

## 🎬 デモ動画の撮影

### 準備

```bash
# 管理者権限で実行
cargo build --release
target/release/gse-prototype.exe
```

### 撮影シナリオ

1. **起動** (5秒)
   - コンソール表示: `GSE Core Initialized`
   
2. **FLOW状態** (20秒)
   - メモ帳で高速タイピング
   - コンソール: 緑の `[STATE: FLOW]`
   - 画面: 透明

3. **INCUBATION状態** (30秒)
   - 手を止め、バックスペースで削除
   - コンソール: 黄色の `[STATE: INCUBATION]`
   - 画面: 薄い黄色

4. **STUCK状態** (40秒)
   - 完全に手を止める
   - コンソール: 赤の `[STATE: STUCK] Prob: 0.92`
   - 画面: 白い霧

5. **復帰** (15秒)
   - 再びタイピング開始
   - FLOWに戻る

---

## 🐛 トラブルシューティング

### 一般的なエラーと解決策

#### 1. `link.exe not found`

```
/ask I'm getting "link.exe not found" error. Can you:
1. Verify that Visual Studio Build Tools are installed
2. Check if the MSVC toolchain is properly configured
3. Suggest steps to fix the PATH if needed
```

#### 2. `Hook installation failed`

```
/ask The keyboard hook installation is failing. Can you:
1. Check if we need administrator privileges
2. Verify the hook procedure signature is correct
3. Add better error handling and logging
```

#### 3. `Overlay window not visible`

```
/ask The overlay window is not showing. Can you:
1. Verify the window creation code
2. Check if we're setting the correct window styles
3. Add debug logging to track window creation
```

#### 4. `Compilation errors with windows crate`

```
/ask I'm getting compilation errors with the windows crate. Can you:
1. Check if all required features are enabled in Cargo.toml
2. Verify the correct windows crate version (0.58)
3. Fix any API usage issues
```

### Claude Codeの使い方のコツ

#### 段階的な依頼
❌ 悪い例:
```
Implement the entire GSE prototype
```

✅ 良い例:
```
First, create the basic keyboard hook structure.
Then, we'll add flight time calculation.
After that, we'll integrate state classification.
```

#### 具体的なエラーメッセージを共有
```
/ask I'm getting this error:
[paste full error message]

Can you help me fix it?
```

#### コンテキストの提供
```
/ask I'm working on Phase 2 (state classification).
The keyboard hook is working, but the state is always FLOW.
Can you check the classify_state logic in rules.rs?
```

---

## 📊 成功基準チェックリスト

### Must Have ✅
- [ ] Global Key Hookが動作し、全てのキー入力をキャプチャ
- [ ] FlightTimeが正確に計算され、コンソールに表示
- [ ] 3状態（FLOW/INCUBATION/STUCK）が判定され、色分け表示
- [ ] 画面オーバーレイが状態に応じて変化（透明→黄色→白）
- [ ] 60fps（16ms以内）で動作し、入力遅延がない
- [ ] 管理者権限で実行可能

### Nice to Have 🌟
- [ ] HMMによる確率的推定が動作
- [ ] 状態確率がコンソールに表示される
- [ ] スムーズな状態遷移アニメーション

### Optional 🎯
- [ ] TSFでIME未確定文字列を取得
- [ ] Chrome、VS Codeでも動作
- [ ] 設定ファイルでパラメータ調整可能

---

## 🚀 次のステップ

### 1. プロジェクトの初期化
```bash
claude
# Then in Claude Code:
/generate [use the project initialization prompt from above]
```

### 2. Phase 1の実装
```bash
# Follow Phase 1 prompts in Claude Code
```

### 3. 継続的な開発
各Phaseで：
1. Claude Codeで実装
2. ビルドして動作確認
3. Gitでコミット
4. 次のPhaseへ

### 4. デバッグとテスト
```
/ask Run the project and test if [specific functionality] works.
If there are errors, help me debug them.
```

---

## 📚 参考資料

### Windows API
- [SetWindowsHookEx](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setwindowshookexw)
- [SetLayeredWindowAttributes](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setlayeredwindowattributes)

### Rust
- [windows-rs](https://github.com/microsoft/windows-rs)
- [tracing](https://docs.rs/tracing/)

### Claude Code
- [公式ドキュメント](https://docs.claude.com/en/docs/claude-code/overview)
- [GitHub](https://github.com/anthropics/claude-code)

---

## 🎯 最終目標

**7〜10日間でMVPを完成させ、デモ動画を撮影する**

- Day 1-2: Phase 0-1 (プロジェクト初期化、キーフック)
- Day 3: Phase 2 (ルールベース推論)
- Day 4-5: Phase 3 (HMM統合、オプション)
- Day 6-7: Phase 4 (オーバーレイUI)
- Day 8-10: デバッグ、最適化、デモ撮影

---

## 💡 Claude Codeのベストプラクティス

### 1. 小さな変更を頻繁に
```
/generate Small, focused changes
/ask Test this specific feature
```

### 2. エラーは即座に修正
```
/ask Fix this compilation error: [paste error]
```

### 3. コードレビューを依頼
```
/ask Review this keyboard hook implementation. 
Is it following Rust best practices?
Are there any potential memory leaks?
```

### 4. ドキュメント生成
```
/generate Add comprehensive comments to all public functions
```

### 5. リファクタリング
```
/refactor Extract the state classification logic into a separate module
```

---

## ✨ プロジェクト完了後

1. **README.mdの更新**
```
/generate Update README.md with:
- Project overview
- Installation instructions
- Usage guide
- Demo video link
- Known limitations
```

2. **技術文書の作成**
```
/generate Create TECHNICAL.md documenting:
- Architecture decisions
- Performance considerations
- Future improvements
- Lessons learned
```

3. **リリースの準備**
```bash
cargo build --release
# Test thoroughly
# Create demo video
# Package for distribution
```

---

## 🎉 成功への道

このガイドに従い、Claude Codeを活用すれば、複雑なWindowsシステムプログラミングも段階的に実装できます。

**各Phaseで動作するものを作り、小さな成功を積み重ねていきましょう！**

Good luck with your GSE prototype! 🚀
