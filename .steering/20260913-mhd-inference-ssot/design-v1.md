# 設計 v1（★ `/reimagine` 前の初回案）

> ⚠️ 本ファイルは `/reimagine` の比較材料として保存する。採用案は `design.md`。

## 実装アプローチ

**新規 ADR-030 を書く。コードは 1 行も変えない**（タスク 2 が実装する）。

### D1. `stall onset` 検出器は **オフライン側**に置く

- 根拠（一次）: `metrics.rs:4-5` 逐語「**派生値はログ記録時ではなく本モジュールで計算する設計**のため、
  閾値変更時に過去セッションを再処理するだけで再計算できる」
- `engine.rs:27-58` が bump 対象として列挙するのは `features.rs` の
  `phi` / `make_silence_observation` / `calculate_features` の**数値挙動**。
  → ★ **そこへ触らなければ `HMM_VERSION = "0.5.0"` は不変。**
- ADR-014 D4b「記録のみ。推論には 1 バイトも流さない」と整合。

### D2. `stall onset` の操作的定義（3 条件）

入力は **`key` 行の `(t, category, press)` 列だけ**（★ 新計器ゼロ）。

- 条件 1（**産出の低下**）: 因果窓 `W`（右端＝評価時刻・**look-ahead ゼロ**）内の
  純産出 `net = 挿入系 press 数 − 削除系 press 数` が個人基準を下回る
- 条件 2（**持続**）: 条件 1 が `θ_person` を超えて連続
- **`t0` = 条件 2 が成立した時点**（＝ **検出時点**。⚠️ 継続の開始時点ではない）

★ `t0` を検出時点に置くことで、検出窓 `[t0−θ, t0]` と転帰窓 `[t0, ∞)` が**重ならない**
（`criterion:66` 逐語「stall onset の検出窓と転帰判定窓を重ねない」を構造的に満たす）。

⚠️★★★ **onset 検出には `progress_proxy` を使わない。** `progress_proxy` は
「**T 秒以内に取り消されない**」という **look-ahead** を持つ（`personalization:341`）。
使うと検出窓が `t0+T` まで伸び、転帰窓と重なる。→ **onset は look-ahead-free な純産出**で判定する。

### D3. `θ_person` の算出規則

`θ_person = max(W, quantile_q(その個人の打鍵間ギャップ分布))`

- ★ **床は `W`**（＝検出器自身の分解能）。⚠️ 絶対秒数の天井は置かない。
- `q` の**値**は P1 開始前に事前宣言（既定 p90 案）。★ **決め方だけを先に凍結**する
  （先例: ADR-009 §Accepted B の Δ「決め方は 2026-08-16 に凍結済み」）。
- 分位点の推定は **ADR-008 D4 の会計**に従う:
  `cold_start` / `past_session_adapted` は可、`within_session_adaptive` は**探索的のみ**。

### D4. `phase` は O1 では `unspecified` に collapse

`task-adaptation-and-scope-gating.md §3.6` の暫定案を本 ADR で確定する。
→ 鍵は `user × task_kind` に落ちる。

### D5. `task_kind` — ⚠️ 引き継ぎの前提を訂正する

★ **一次確認**: `App.tsx:16` の lock は **G1 較正画面のみ**。
O1 は `RecordingControls.tsx:61-71` の `O1_TASK_KINDS`（**4 値**）＋ `declare_task_kind`
（`lib.rs:1345`）を通る。→ ★ **O1 で `task_kind` は分散を持つ。**
⚠️ ただし **未宣言（`null`）がありうる**（ADR-016 判断 4b-1「強制しない」）。
→ `null` は **5 値目にせず、個人全体の基準へ back-off** する。

### D6. `Decision Episode` は**新設しない**

ADR-008 D2 の `ContextBuilder` ／ ADR-010 D4 の読み出し単位 ／ ADR-014 D6 の意味的境界は**同一物**。
境界イベント列は `personalization §3.1` のまま。**1 stall onset = 1 Decision Episode の開始**。

### D7. 除外区間では onset 検出を走らせない

`recording_pause{paused=true}` / `secure_input{on}` / `hook_health{alive=false}` /
`dropped_delta > 0` / セッション境界（ADR-016 D4 ＋ ADR-029 D3）。
⚠️ **除外区間の沈黙を pause として数えると偽 onset が出る。**

### D8. 特徴量再設計の accept 対象

Tier 枠（T0/T1a/T1b/T1c/T1d/T2/T3/Q）＋ 投資順序 T0→T1→T2→T3 ＋ held-out block ablation 規律。
⚠️ **特徴リストは accept しない。**

### D9. 計器を変えない範囲 / 変える範囲の仕切り

| 範囲 | 計器 | 根拠 |
|---|---|---|
| T0 / T1a / T1b / T1d / Q | 不要 | `key` 行が 1 打鍵ごとに `t` を持つ |
| T1c | **要** | `undo/redo` は `KeyCategory` 量子化で不可 |
| T2 | **要** | `focus_transition{t}` に方向が無い |
| T3 | **要** | O1 の現行観測空間外 |

## 変更対象

### 新規作成
- `docs/adr/ADR-030-stall-onset-and-decision-episode.md`

### 修正
- `docs/adr/README.md` — 行を 1 本足す

## テスト戦略

⚠️ **機械 AC は衛生条件にすぎない**（`check_doc_lexicon.py` / `check_citations.py` / grep）。
裁定の正しさは `/cross-review` ＋ `code-reviewer` ＋ `security-checker` の 3 本で見る。

## ロールバック計画

ADR は append-only。誤りは**番号の大きい新 ADR** で上書きする（ADR-021→022→026→027 の先例）。
