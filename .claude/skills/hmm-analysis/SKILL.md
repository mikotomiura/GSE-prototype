---
name: hmm-analysis
description: >
  GSE の HMM 認知状態推定エンジンの詳細仕様。analysis/features.rs と
  analysis/engine.rs を書く・修正する・デバッグするときに必須参照。
  以下の状況で必須参照:
  - F1/F3/F4/F5/F6 の特徴量計算ロジックを修正するとき
  - X軸 (Cognitive Friction) / Y軸 (Engagement) の合成式を変更するとき
  - 観測ビン (obs=0..25) の量子化ロジックを変更するとき
  - EWMA / ヒステリシス EMA の α 値を調整するとき
  - β ベースライン (β_writing / β_writing_latin・Coding head の β) を変更するとき
  - 摩擦フロア・サイレンス検出・バックスペースペナルティを修正するとき
  - 30秒ローリングウィンドウのバッファ管理を変更するとき
allowed-tools: Read, Grep, Glob, Edit
---

# HMM 分析エンジン仕様

## このスキルの目的

GSE のコアロジックである特徴量抽出・潜在軸計算・HMM 推論の仕様を
正確に把握し、変更時の意図せぬ破壊を防ぐ。

## 適用範囲

### 適用するもの
- `src-tauri/src/analysis/features.rs`
- `src-tauri/src/analysis/engine.rs`

### 適用しないもの
- `input/hook.rs`（InputEvent の生成）
- `logger.rs`（ログ出力）

---

## アーキテクチャ概要

```
InputEvent (vk_code, timestamp_ms, is_backspace, ...)
        │ push()
        ▼
FeatureExtractor (30s ローリングウィンドウ, VecDeque<600>)
        │ extract() → 5 特徴量
        ▼
[F1: Flight Time, F3: Correction Rate, F4: Burst Length,
 F5: Pause Count, F6: Pause-After-Delete Rate]
        │ 正規化 φ(x, β)
        ▼
X軸 (Cognitive Friction), Y軸 (Engagement)  ← EWMA で平滑化
        │ 量子化 → 5×5 グリッド (obs=0..24) or ペナルティ (obs=25)
        ▼
HMM Forward Algorithm (3 states × 26 bins)
        │
        ▼
{p_flow, p_incubation, p_stuck} ← ヒステリシス EMA で平滑化
        │
        ▼
display_probs → Frontend に返す
```

---

## 主要なルール

### ルール 1: 5 つの特徴量定義（変更時は必ずここを確認）

| ID | 名称 | 計算式 | 単位 |
|---|---|---|---|
| F1 | Flight Time | 連続キー押下間の中央値時間 | ms |
| F3 | Correction Rate | (Backspace + Delete) / 総キー数 | 比率 0..1 |
| F4 | Burst Length | 打鍵間隔 < 200ms の連続打鍵の平均文字数 | 文字数 |
| F5 | Pause Count | 2秒以上の沈黙の回数 (30s ウィンドウ内) | 回数 |
| F6 | Pause-After-Delete Rate | (削除後2秒以上の沈黙) / 総削除数 | 比率 0..1 |

※ F2 は欠番（設計過程で除外）

---

### ルール 2: 正規化関数 φ とベースライン β

```
φ(x, β) = clamp((x − β) / (κ · β), 0.0, 1.0)    κ = 2.0
```

β は **各 domain head の所有物**である（ADR-006 Alternative C・実装は `analysis/heads/`）。

- **Writing head**（論述・文章作成。Phase1 はこれのみ稼働）
  - `β_writing`: 日本語 IME 入力時のベースライン（IME_OPEN = true）
  - `β_writing_latin`: IME off のラテン直接入力（英字引用・数式・URL）のベースライン
    （IME_OPEN = false）。⚠️ **旧 `β_coding` を改名したもので、Coding の baseline ではない**
    （ADR-006 下位決定 #2 の再スコープ）
- IME_OPEN フラグが切り替わったとき、次の 1Hz サイクルから β が変わる。
  この切替は **Writing head 内部の within-writing 信号**であり、
  「どの head を走らせるか」を決める `task_kind` とは役割が直交する。

---

### ルール 3: 潜在軸の合成式

```
X (Cognitive Friction) = 加重合成(F3, F6, F1_inv, F5)  高いほど「つまずき」
Y (Engagement)         = 加重合成(F4, F1_inv, F5_inv)   高いほど「滑らかな出力」
```

EWMA で平滑化（α = 0.15 通常時、サイレンス時に段階的変化）。

---

### ルール 4: 観測ビン量子化（26 bins）

```
X軸: 0..1 → x_bin = 0..4 (5分割)
Y軸: 0..1 → y_bin = 0..4 (5分割)
obs = x_bin * 5 + y_bin   (0..24)   ★ 実装 (engine.rs) はこの順序

特例: バックスペース 14 連続以上 → obs = 25 (ペナルティビン)
      IME_ACTIVE = true 時はペナルティ抑制
```

---

### ルール 5: サイレンス検出と α 段階的調整

キー入力なし（2秒以上）のとき、合成特徴量を生成し HMM を更新。

```
サイレンス継続時間に応じた EWMA α:
  〜 10s: α = 0.15 (通常)
  10〜30s: α = 0.18
  30s 〜: α = 0.25

摩擦フロア: サイレンス時の X 軸最小値を保持し、
           長時間無入力でも Stuck への急激な侵食を防ぐ
```

---

### ルール 6: display_probs のヒステリシス EMA

```
display_probs[i] = α_h * raw_probs[i] + (1 - α_h) * display_probs[i]
α_h = 0.3 (forward_probs より遅い追従)
```

急激な状態変動を UI に表示しないためのバッファ。

---

### ルール 7: コールドスタート初期値

```rust
// Flow 寄りの安定した初期確率
forward_probs = [0.80, 0.15, 0.05];  // [Flow, Incubation, Stuck]
display_probs = [0.80, 0.15, 0.05];
```

---

## チェックリスト

- [ ] 特徴量の計算式が上記定義と一致しているか
- [ ] β ベースライン切替タイミングが IME_OPEN フラグと連動しているか
- [ ] obs=25 のペナルティが IME_ACTIVE 時に抑制されているか
- [ ] サイレンス時の α 調整が段階的になっているか
- [ ] パラメータ変更時に根拠コメントを書いたか
- [ ] 変更後にセッションログで事後検証したか

---

## 補足資料

- `parameter-reference.md` — 現行パラメータ値と変更履歴

## 関連する他の Skill

- `ml-workflow` — HMM チューニング手順・ONNX 移行パターン
- `hook-constraints` — InputEvent の生成制約
