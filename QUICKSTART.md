# GSE Prototype - Claude Code クイックスタートガイド

## 🚀 5分で始める開発

### ステップ1: Claude Codeの起動

```bash
# プロジェクトディレクトリに移動
cd ~/projects

# Claude Code起動
claude
```

### ステップ2: プロジェクト初期化（コピペ用プロンプト）

以下をClaude Codeにコピペしてください：

```
I'm building a Windows prototype called GSE (Generative Struggle Engine) that monitors keyboard input and provides visual feedback based on user cognitive state.

Phase 1 Goal: Create the project structure and implement global keyboard hook.

Please create a Rust project with this structure:

Project: gse-prototype
Language: Rust (edition 2021)

Dependencies in Cargo.toml:
- windows = { version = "0.58", features = ["Win32_Foundation", "Win32_UI_WindowsAndMessaging", "Win32_System_LibraryLoader"] }
- tracing = "0.1"
- tracing-subscriber = "0.3"
- chrono = "0.4"
- serde = { version = "1.0", features = ["derive"] }
- serde_json = "1.0"

Directory structure:
src/
  main.rs          (with tracing initialization and "GSE Core Initialized" message)
  input/
    mod.rs         (declare keyboard module)
    keyboard.rs    (empty for now)
  inference/
    mod.rs         (declare rules module)
    rules.rs       (empty for now)
  ui/
    mod.rs         (empty for now)
    overlay.rs     (empty for now)

Also create:
- .gitignore (standard Rust gitignore)
- README.md (brief project description)

After creating the structure, build the project to verify everything compiles.
```

---

## 📝 Phase別プロンプト集

### Phase 1: Global Key Hook (4-6時間)

#### プロンプト 1-1: キーボードフックの実装

```
Now let's implement the keyboard hook in src/input/keyboard.rs.

Requirements:
1. Use Windows API SetWindowsHookExW with WH_KEYBOARD_LL (low-level keyboard hook)
2. Create an unsafe extern "system" function keyboard_proc that:
   - Captures WM_KEYDOWN events
   - Calculates flight time (time between consecutive key presses)
   - Logs flight time using tracing::info!
   - Uses a static Option<Instant> to store last key press time
   - Properly calls CallNextHookEx
3. Export a public function to install the hook

Safety requirements:
- Use proper Windows types (WPARAM, LPARAM, LRESULT)
- Handle the static variable safely with unsafe blocks
- Add comments explaining the unsafe code

Please implement this following Rust best practices.
```

#### プロンプト 1-2: main.rsの更新

```
Update src/main.rs to:
1. Initialize tracing with INFO level logging
2. Import and install the keyboard hook from input::keyboard
3. Enter a Windows message loop using GetMessageW
4. Call TranslateMessage and DispatchMessageW in the loop
5. Properly unhook on exit
6. Add error handling for hook installation

The program should print "GSE Core Initialized" and then "Keyboard hook installed" on startup.
```

#### テスト用プロンプト

```
Build and test the keyboard hook:
1. cargo build
2. Run the program (may need administrator privileges)
3. Open Notepad and type some text
4. Verify that flight times are logged to console

If there are any compilation errors or runtime issues, help me debug them.
```

---

### Phase 2: ルールベース状態推論 (3-4時間)

#### プロンプト 2-1: 状態定義

```
Create the state classification logic in src/inference/rules.rs:

1. Define an enum FlowState with three variants:
   - Flow (user is in flow state, typing smoothly)
   - Incubation (user is thinking, moderate delays)
   - Stuck (user is stuck, long delays or many corrections)

2. Implement a function classify_state(flight_time_ms: u64, backspace_count: u32) -> FlowState with these rules:
   - Flow: flight_time < 100ms AND backspace_count < 2
   - Stuck: flight_time > 500ms OR backspace_count > 5
   - Incubation: everything else

3. Add appropriate derives (Debug, Clone, Copy, PartialEq)

Make it public and well-documented.
```

#### プロンプト 2-2: 状態ログの統合

```
Update src/input/keyboard.rs to integrate state classification:

1. Import classify_state from crate::inference::rules
2. After calculating flight_time, call classify_state(flight_time_ms, 0) 
   (we'll add backspace tracking later)
3. Log the state with different log levels:
   - FlowState::Flow → use tracing::info! with prefix "[STATE: FLOW]"
   - FlowState::Incubation → use tracing::warn! with prefix "[STATE: INCUBATION]"
   - FlowState::Stuck → use tracing::error! with prefix "[STATE: STUCK]"

Format: "[STATE: FLOW] FlightTime: 85ms"
```

#### プロンプト 2-3: Backspace追跡の追加

```
Enhance the keyboard hook to track Backspace key presses:

1. Add a static VecDeque<Instant> to track backspace timestamps
2. When Backspace (VK_BACK) is pressed, add current time to the deque
3. Remove timestamps older than 5 seconds from the deque
4. Pass the deque length as backspace_count to classify_state

Use std::collections::VecDeque and proper unsafe handling for the static variable.
```

---

### Phase 3: HMM統合（オプション、6-10時間）

#### プロンプト 3-1: HMM構造

```
Create src/inference/hmm.rs with a Hidden Markov Model implementation:

1. Define a struct HMM with:
   - transition: [[f64; 3]; 3] (transition probability matrix)
   - state_probs: [f64; 3] (current state probabilities)

2. Implement HMM::new() with these transition probabilities:
   From FLOW (index 0):       [0.85, 0.10, 0.05] → [FLOW, INCUBATION, STUCK]
   From INCUBATION (index 1): [0.40, 0.45, 0.15]
   From STUCK (index 2):      [0.30, 0.20, 0.50]

3. Initialize state_probs to [1.0, 0.0, 0.0] (start in FLOW)

Add comprehensive documentation explaining the model.
```

#### プロンプト 3-2: Forward Algorithm

```
Add the Forward Algorithm to HMM:

1. Implement fn update(&mut self, observation: f64) where observation is flight_time_ms
2. Calculate observation probabilities using Gaussian distributions:
   - FLOW: mean=50ms, std=30ms
   - INCUBATION: mean=250ms, std=100ms
   - STUCK: mean=1000ms, std=500ms
3. Multiply current state_probs by transition matrix
4. Multiply by observation probabilities
5. Normalize so probabilities sum to 1.0
6. Return the most likely state (argmax of state_probs)

Use the statrs crate for Gaussian calculations if needed.
```

---

### Phase 4: オーバーレイUI (6-8時間)

#### プロンプト 4-1: Windows Graphics依存関係

```
Add Windows graphics features to Cargo.toml:

Update the windows dependency to include:
- Win32_Graphics_Direct2D
- Win32_Graphics_Direct3D11
- Win32_Graphics_Dxgi
- Win32_Graphics_Gdi

Keep all existing features.
```

#### プロンプト 4-2: オーバーレイウィンドウ作成

```
Implement in src/ui/overlay.rs:

1. Create function create_overlay_window() -> HWND that:
   - Creates a layered window covering the entire screen
   - Uses window styles: WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_TOPMOST
   - Makes it click-through (doesn't capture mouse/keyboard)
   - Returns the window handle

2. Create function set_overlay_alpha(hwnd: HWND, alpha: u8, color: u32):
   - Uses SetLayeredWindowAttributes to set window opacity and color
   - alpha: 0 = transparent, 255 = opaque
   - color: RGB format (e.g., 0xFFFFFF for white)

Include proper error handling and documentation.
```

#### プロンプト 4-3: 状態ベースの視覚効果

```
Add function update_overlay(hwnd: HWND, state: FlowState) in overlay.rs:

Visual feedback based on state:
- FLOW: alpha=0 (completely transparent)
- INCUBATION: alpha=25, color=0xFFFF99 (light yellow)
- STUCK: alpha=76, color=0xFFFFFF (white fog)

This should be called whenever the state changes.
```

#### プロンプト 4-4: メインループへの統合

```
Update main.rs to:
1. Create the overlay window on startup (after hook installation)
2. Store the HWND in a static or pass it to the keyboard hook somehow
3. Call update_overlay when state changes in keyboard_proc
4. Destroy the overlay window on program exit

Handle thread safety properly since the overlay is accessed from the hook callback.
```

---

## 🐛 デバッグ用プロンプト集

### ビルドエラー

```
I'm getting this compilation error:
[paste error here]

Can you:
1. Identify the root cause
2. Provide a fix
3. Explain why the error occurred
```

### 実行時エラー

```
The program compiles but crashes/hangs with this error:
[paste error or behavior]

Can you:
1. Add debug logging to track down the issue
2. Check for common Windows API pitfalls
3. Suggest fixes
```

### 機能が動作しない

```
The [keyboard hook/overlay/state detection] is not working as expected:
[describe behavior]

Can you:
1. Review the relevant code
2. Add diagnostic logging
3. Suggest what might be wrong
```

---

## 📋 チェックリスト用プロンプト

### Phase完了確認

```
I've completed Phase [N]. Can you:
1. Review all the code in this phase for correctness
2. Check if there are any potential bugs or issues
3. Verify that it meets the phase requirements
4. Suggest any improvements
```

### コードレビュー

```
Please review the entire codebase and check for:
1. Rust best practices and idiomatic code
2. Memory safety and proper unsafe usage
3. Error handling completeness
4. Performance considerations
5. Documentation quality
```

---

## 🎬 デモ準備用プロンプト

```
I'm ready to create a demo. Can you:
1. Ensure the code is production-ready
2. Add any missing error handling
3. Optimize performance if needed
4. Create a release build command
5. Suggest a demo script showing all features
```

---

## 💡 困ったときのプロンプト

### 完全に行き詰まったとき

```
I'm stuck on [specific issue]. Can you:
1. Explain the problem in simpler terms
2. Break it down into smaller steps
3. Provide a minimal working example
4. Suggest alternative approaches
```

### 方向性がわからないとき

```
I'm not sure how to proceed with [feature/phase]. Can you:
1. Explain the high-level architecture
2. Suggest a step-by-step implementation plan
3. Point out potential challenges
4. Recommend resources or documentation
```

---

## 🚀 時短テクニック

### バッチ実装

```
Let's implement multiple small features at once:
1. [Feature A]
2. [Feature B]
3. [Feature C]

Create them all in one go, ensuring they work together.
```

### コード生成と説明

```
Generate the code for [feature] AND explain:
1. How it works
2. Why you made specific design choices
3. What edge cases to watch for
4. How to test it
```

---

## ✅ 最終チェックリスト

コピペして最終確認に使用：

```
Final code review checklist:

Functionality:
- [ ] Keyboard hook captures all key events
- [ ] Flight time calculation is accurate
- [ ] State classification works correctly (FLOW/INCUBATION/STUCK)
- [ ] Overlay shows and changes opacity based on state
- [ ] No crashes or memory leaks

Code Quality:
- [ ] All unsafe code is properly documented
- [ ] Error handling is comprehensive
- [ ] Logging provides useful debugging info
- [ ] Code follows Rust best practices
- [ ] Performance meets 60fps requirement (< 16ms per frame)

Documentation:
- [ ] All public functions have doc comments
- [ ] README explains how to build and run
- [ ] CLAUDE.md is up to date
- [ ] Code comments explain complex logic

Testing:
- [ ] Works in Notepad
- [ ] Works in other applications
- [ ] Runs without administrator privileges if possible
- [ ] Clean startup and shutdown

Please review each item and let me know if anything needs improvement.
```

---

TSFは非常に複雑なため、段階的に実装します。以下のプロンプトを順番にClaude Codeに入力してください。

⚠️ 重要な前提知識
TSF統合は以下の理由で困難です：

COMインターフェースの複雑さ
ドキュメントの不足
Rustでの実装例がほぼ皆無
デバッグが難しい

推奨： 各ステップで動作確認し、問題があれば次に進まないこと。

Phase 5-0: TSF調査と設計（必須）
まず、Claude Codeに現状確認と設計をさせます：
I want to add TSF (Text Services Framework) integration to capture IME composition strings (Japanese input method).

Before we start coding, please:

1. Research the TSF architecture and explain:
   - What COM interfaces we need (ITfThreadMgr, ITfContext, ITfCompositionSink, etc.)
   - How TSF differs from the current keyboard hook approach
   - What limitations and challenges we should expect

2. Design a high-level architecture:
   - How TSF module fits into the existing code
   - Whether we need a separate thread for COM
   - How to pass composition string data to the main inference loop

3. Identify the Windows API features we need to add to Cargo.toml:
   - COM initialization (CoInitialize)
   - TSF-specific features
   
4. Suggest a minimal viable implementation:
   - What's the simplest TSF integration that just logs composition strings?
   - Can we start with read-only monitoring before full integration?

Please provide a detailed explanation and implementation plan BEFORE we write any code.
このプロンプトの後、Claude Codeの回答を読んで理解してから次に進んでください。

Phase 5-1: Cargo.toml更新
Based on your TSF architecture design, update Cargo.toml to add the necessary Windows features for TSF integration.

We need at minimum:
- Win32_System_Com (COM initialization)
- Win32_UI_TextServices (TSF interfaces)
- Any other features required for ITfThreadMgr, ITfContext, ITfDocumentMgr

Also add any new Rust crates if needed (like windows-implement for COM interface implementation).

Show me the updated [dependencies] section.

Phase 5-2: TSFモジュールの基本構造
Create src/input/tsf.rs with the basic TSF module structure:

1. Add necessary imports from the windows crate for TSF
2. Create a struct TsfManager that will manage TSF state
3. Implement TsfManager::new() that:
   - Initializes COM with CoInitializeEx (COINIT_APARTMENTTHREADED)
   - Creates ITfThreadMgr instance
   - Does NOT install any sinks yet (we'll do that incrementally)
   - Returns Result<Self, Error> with proper error handling

4. Implement Drop for TsfManager to cleanup COM

5. Add a simple public function test_tsf_initialization() that:
   - Creates a TsfManager
   - Logs success or failure
   - Drops it cleanly

This is JUST the foundation - no composition tracking yet.

Requirements:
- Comprehensive error handling
- Detailed comments explaining COM/TSF concepts
- Safety documentation for all unsafe blocks

Phase 5-3: 初期動作テスト
Update src/main.rs to test TSF initialization:

1. Import tsf module
2. After "GSE Core Initialized", call tsf::test_tsf_initialization()
3. Log whether TSF initialized successfully
4. Continue with normal keyboard hook operation

Build and test to ensure:
- Program still compiles
- TSF initialization doesn't crash
- We can proceed to actual composition tracking

If there are any COM-related errors, help me debug them.
⚠️ ここで必ずテストしてください。COM初期化で問題があれば、次に進まないこと。

Phase 5-4: Composition Sink実装の準備
This is the most complex part. Before implementing the composition sink, explain:

1. How ITfContextOwnerCompositionSink works:
   - What methods we need to implement
   - When these methods are called by TSF
   - How to safely access the composition string

2. The threading model:
   - Does TSF callback happen on the same thread?
   - Do we need synchronization with the main keyboard hook?
   - How to pass composition data to the inference engine?

3. Implementation strategy:
   - Should we use windows-implement crate for COM interfaces?
   - Or use raw unsafe COM vtable manipulation?
   - What's the simplest approach that will work?

Provide a detailed plan before we implement the actual sink.

Phase 5-5: Composition Sink実装（最難関）
Implement ITfContextOwnerCompositionSink in src/input/tsf.rs:

1. Create a CompositionSink struct that implements the COM interface
2. Implement required methods:
   - OnStartComposition: Log when IME composition begins
   - OnUpdateComposition: Extract and log the current composition string
   - OnEndComposition: Log when composition is finalized

3. In OnUpdateComposition:
   - Get the ITfRange for the composition
   - Extract the text using ITfRange::GetText
   - Log the composition string to console
   - Store it for later use by the inference engine

4. Update TsfManager to:
   - Create and register the CompositionSink
   - Connect it to the active ITfContext
   - Provide a way to retrieve the latest composition string

This will be complex. Please:
- Add extensive comments explaining each step
- Handle all COM errors properly
- Use proper reference counting for COM objects
- Test incrementally if possible
⚠️ このステップは最も困難です。エラーが出たら一緒にデバッグします。

Phase 5-6: フォールバック実装
TSFが動作しない場合に備えて：
TSF integration is proving difficult. Let's implement a graceful fallback:

1. Make TSF initialization return Result
2. If TSF fails to initialize:
   - Log a warning "TSF unavailable, using keyboard hook only"
   - Continue with existing keyboard hook
   - Add a note to console: "Japanese IME input may not be accurately tracked"

3. Update README.md to document:
   - TSF is experimental
   - Known limitations with IME input
   - Fallback behavior

This ensures the demo still works even if TSF doesn't.

🐛 デバッグ用プロンプト
TSFでエラーが出たら以下を使用：
COM初期化エラー
I'm getting COM initialization errors:
[paste error]

Can you:
1. Check if CoInitializeEx is called correctly
2. Verify the apartment model (APARTMENTTHREADED vs MULTITHREADED)
3. Check if we're calling CoUninitialize properly
4. Add more detailed error logging
インターフェース取得失敗
ITfThreadMgr creation is failing with error:
[paste error]

Can you:
1. Verify we're using the correct CLSID
2. Check if TSF is available on this Windows version
3. Try alternative initialization methods
4. Add fallback to keyboard-only mode
Composition Stringが取得できない
The composition sink methods are being called, but I can't extract the text.

Can you:
1. Review the ITfRange::GetText usage
2. Check if we're accessing the correct context
3. Add detailed logging at each step of text extraction
4. Verify the text encoding/conversion
クラッシュ・メモリエラー
The program crashes when TSF is active:
[paste error or behavior]

Can you:
1. Review all unsafe blocks in tsf.rs
2. Check COM reference counting (AddRef/Release)
3. Verify we're not accessing freed memory
4. Add defensive checks and better error handling

📋 TSF実装チェックリスト
各ステップ完了後にチェック：
Phase 5 Progress:

[ ] 5-0: TSF architecture understood and designed
[ ] 5-1: Cargo.toml updated with TSF features
[ ] 5-2: TsfManager struct created and compiles
[ ] 5-3: COM initialization succeeds without crashes
[ ] 5-4: Composition sink strategy decided
[ ] 5-5: Composition sink implemented
[ ] 5-6: Can extract composition strings from Notepad/Chrome
[ ] 5-7: Integrated with inference engine
[ ] 5-8: Fallback works if TSF fails

Current status: [ ] Working / [ ] Partially working / [ ] Not working




## 🎯 成功の鍵

1. **小さく始める**: Phase 1から順番に
2. **頻繁にテスト**: 各変更後にビルド&実行
3. **エラーは即座に解決**: 積み重ねない
4. **Claude Codeを信頼**: でも結果は必ず確認
5. **楽しむ**: 複雑なプロジェクトも段階的なら達成可能！

Happy coding! 🚀
