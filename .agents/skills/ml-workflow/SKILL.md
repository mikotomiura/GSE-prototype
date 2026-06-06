---
name: ml-workflow
description: >
  GSE の HMM 手動チューニング規則・Python/PyTorch 学習スクリプト配置・
  ONNX Runtime への移行パターン。analysis/engine.rs を修正するとき・
  HMM パラメータを変更するとき・ONNX 移行を実装するとき・
  Python 学習スクリプトを analysis/ に追加するときに必須参照。
  以下の状況で必須参照:
  - engine.rs の emission_matrix / transition_matrix を変更するとき
  - HMM パラメータチューニングの根拠をコメントで書くとき
  - ONNX Runtime の依存を Cargo.toml に追加するとき
  - Python/PyTorch の学習スクリプト (*.py) を配置するとき
  - FeatureExtractor と ML モデルの境界を設計するとき
allowed-tools: Read, Grep, Glob, Edit
---

# ML ワークフロー規約

## このスキルの目的

現状の手動チューニング HMM を適切に保守し、
将来の ONNX Runtime 移行への道筋を明確にする。
Python 学習スクリプトと Rust 推論の境界を守る。

## 適用範囲

### 適用するもの
- `src-tauri/src/analysis/engine.rs`（HMM パラメータ・推論ロジック）
- `src-tauri/src/analysis/features.rs`（特徴量抽出）
- 将来の Python 学習スクリプト（`analysis/` 配下）

### 適用しないもの
- `input/` モジュール（OS 層）
- `logger.rs`（永続化層）

---

## 主要なルール

### ルール 1: HMM パラメータ変更時は根拠をコメントで明記

ハードコードされたパラメータを変更するとき、必ず理由をコメントに残す。

```rust
// ✅ 良い例
/// Emission matrix: 3 states × 26 observation bins
/// 各値はセッションログ (gse_*.ndjson) の事後分析で検証済み (2026-03-08)
/// - obs=17..20 (high friction + low engagement) → Stuck 寄りに補正
/// - obs=12 付近の Flow/Nudge ギャップを埋めるため y_bin=2 を調整
const EMISSION: [[f64; 26]; 3] = [...];

// ❌ 悪い例（なぜこの値か不明）
const EMISSION: [[f64; 26]; 3] = [[0.08, 0.10, ...], ...];
```

---

### ルール 2: パラメータ変更後はセッションログで事後検証

HMM パラメータ変更は必ずセッションログ (NDJSON) の事後分析で検証する。
検証スクリプトは `analysis/behavioral_gt.py`（Phase 2 以降）。

```
変更フロー:
1. engine.rs のパラメータを変更
2. 手動セッションで動作確認
3. ~/Documents/GSE-sessions/ のログを分析スクリプトで検証
4. 問題なければ .steering/ に変更根拠を記録してコミット
```

---

### ルール 3: ONNX 移行時の変更箇所は `engine.rs` の `update()` のみ

FeatureExtractor (`features.rs`) は ONNX 移行後も共通利用する。
`update()` メソッドの内部実装を差し替えるだけでよい。

```rust
// 現状 (HMM)
pub fn update(&mut self, obs: usize) {
    // Forward Algorithm
    self.forward_hmm(obs);
}

// ONNX 移行後（インターフェースは変えない）
pub fn update(&mut self, obs: usize) {
    // ONNX Runtime セッションで推論
    self.infer_onnx(obs);
}
```

**FeatureExtractor の `extract()` → obs 変換は変更しない。**

---

### ルール 4: Python 学習スクリプトは `analysis/` 配下に配置

Python スクリプトは OS API を呼ばない（Windows 依存なし）ため `analysis/` に置く。

```
src-tauri/src/analysis/
├── features.rs          # Rust 特徴量抽出
├── engine.rs            # Rust HMM 推論
└── (将来) scripts/
    ├── train.py         # PyTorch 学習スクリプト
    ├── export_onnx.py   # ONNX エクスポート
    └── behavioral_gt.py # セッションログ分析
```

**Python スクリプト内でも Windows API は使わない。**（OS 依存は `input/` に閉じ込める原則と同じ）

---

### ルール 5: ONNX モデルファイルの配置

学習済みモデル (`.onnx`) は `src-tauri/models/` に配置し、
Tauri のリソースとしてバンドルする。

```toml
# tauri.conf.json (将来)
[bundle]
resources = ["models/*.onnx"]
```

---

## チェックリスト

- [ ] HMM パラメータ変更時に根拠コメントを書いたか
- [ ] パラメータ変更後にセッションログで検証したか
- [ ] ONNX 移行時に features.rs のインターフェースを壊していないか
- [ ] Python スクリプトが Windows API を呼んでいないか
- [ ] 新しい crate (ort 等) 追加時に依存追加基準を確認したか

---

## 補足資料

- `migration-guide.md` — HMM → ONNX 移行の具体的な手順

## 関連する他の Skill

- `hmm-analysis` — HMM 特徴量・潜在軸・観測ビンの詳細仕様
- `data-privacy` — ML データ収集のプライバシー規約
- `architecture-rules` — analysis/ モジュールの OS 依存禁止
