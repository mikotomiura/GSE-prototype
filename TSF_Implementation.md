現在、GSEプロトタイプの「Global Key Hook版」は `windows` crate v0.58.0 で正常に動作しています。
この状態を**絶対に壊さずに**、IMEの未確定文字列を取得するTSF (Text Services Framework) 機能を「安全なポーリング方式」で追加してください。

以下の厳密な手順と制約に従って実装してください。

## 1. Cargo.toml の機能追加
`[dependencies.windows]` の `features` に以下がなければ追加してください。
- `"Win32_UI_TextServices"`
- `"Win32_System_Com"`
- `"Win32_System_Ole"`

## 2. TSFマネージャーの実装 (`src/input/tsf.rs`)
複雑な「イベントリスナー (Sink)」の実装はビルドエラーの主原因となるため**禁止**します。
代わりに、**「必要な時に現在の状態を見に行く（ポーリング）」** 設計で `TsfManager` を実装してください。

### 実装要件: `src/input/tsf.rs`
- **構造体**: `pub struct TsfManager` (内部に `ITfThreadMgr` を保持)
- **初期化 (`new`)**:
  - `CoInitializeEx` (COINIT_APARTMENTTHREADED) を呼び出す。
  - `CoCreateInstance` で `ITfThreadMgr` を作成する。
  - 失敗してもパニックせず、`Result<Self, Error>` または `Option<Self>` を返す。
- **文字列取得メソッド (`get_current_composition`)**:
  - 引数なし、戻り値 `Option<String>`。
  - ロジック:
    1. `thread_mgr.GetFocus()` で現在の `ITfDocumentMgr` を取得。
    2. `doc_mgr.GetBase()` または `GetTop()` で `ITfContext` を取得。
    3. `context.GetProperty(GUID_PROP_COMPOSING)` を取得し、範囲（Range）を特定する。
    4. その範囲のテキスト (`GetText`) を取得して返す。
  - **重要**: 取得プロセスでエラーが発生してもパニックせず、静かに `None` を返してログ(`error!`)に残すのみとする。

## 3. 安全な統合 (`src/main.rs`)
既存のキーフックループの中に、TSFの呼び出しを「オプショナル」として組み込んでください。

- `main` 関数の冒頭で `TsfManager::new()` を呼ぶ。
  - 失敗した場合: "TSF initialize failed. Running in KeyHook-only mode." とログを出し、プログラムを続行する（**ここで終了させない**）。
- メインループ（`GetMessage` ループ内、またはキーフック検知時）で:
  - `tsf_manager` が有効な場合のみ `get_current_composition()` を呼ぶ。
  - 文字列が取得できた場合のみ、`info!("IME Composition: {}", text)` とログ出力する。

## 4. 禁則事項（絶対守ること）
- `#[implement]` マクロを使用した複雑な COM インターフェースの実装（Sinkなど）は行わないでください（コンパイルエラー回避のため）。
- `unsafe` ブロック内でのエラー（HRESULT）は、必ず `Result` 型でハンドリングし、`.unwrap()` を乱用しないでください。
- 既存の `src/input/keyboard.rs` や `src/ui/overlay.rs` のコードを削除・改変しないでください。

この変更を行い、`cargo build` が一発で通るようにしてください。

ベストを尽くし、最高なコーティングを楽しみましょう！Let's think step by step!