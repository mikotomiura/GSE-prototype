# ml-workflow: HMM → ONNX 移行ガイド

## 移行の前提条件

- 十分なセッションログデータの蓄積（目安: 100 セッション以上）
- `ort` crate (ONNX Runtime) を Cargo.toml に追加済み
- `export_onnx.py` で PyTorch モデルを `.onnx` に変換済み

## 移行手順

### Step 1: Cargo.toml に ort を追加

```toml
[dependencies]
ort = { version = "2.0", features = ["cuda"] }  # CUDA は任意
```

### Step 2: engine.rs に ONNX セッションフィールドを追加

```rust
use ort::{Environment, Session, SessionBuilder, Value};

pub struct Engine {
    // 既存フィールド...
    forward_probs: [f64; 3],
    display_probs: [f64; 3],

    // ONNX 移行後に追加
    onnx_session: Option<Session>,
}
```

### Step 3: update() を差し替え（FeatureExtractor は変更しない）

```rust
pub fn update(&mut self, features: &Features) {
    if let Some(session) = &self.onnx_session {
        // ONNX 推論パス
        let input = Array2::from_shape_vec((1, 5), features.to_vec()).unwrap();
        let outputs = session.run(inputs![input]).unwrap();
        let probs: &[f32] = outputs[0].try_extract_tensor().unwrap().as_slice().unwrap();
        self.display_probs = [probs[0] as f64, probs[1] as f64, probs[2] as f64];
    } else {
        // フォールバック: 既存 HMM パス
        let obs = self.quantize(features);
        self.forward_hmm(obs);
    }
}
```

### Step 4: フォールバック戦略

ONNX セッション初期化失敗時（モデルファイル不在等）は HMM にフォールバック。
ユーザーへの通知は不要（graceful degradation）。

```rust
fn init_onnx(model_path: &Path) -> anyhow::Result<Session> {
    let env = Environment::builder().build()?;
    SessionBuilder::new(&env)?.with_model_from_file(model_path)
        .context("ONNX model load failed")
}
// 失敗時は onnx_session = None のまま HMM で動作継続
```

## A/B テスト戦略（推奨）

移行直後は HMM と ONNX の両方を並列実行し、セッションログに両方の確率を記録する。
十分な検証後に HMM コードを削除する。
