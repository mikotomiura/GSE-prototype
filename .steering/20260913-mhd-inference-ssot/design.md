# 設計 v2（★ `/reimagine` 再生成案）

## 実装アプローチ

**新規 ADR-030 を書く。コードは 1 行も変えない。**

### ★★★ v2 の出発点 —— 「新設しない」を**既存コードのレベルまで降ろす**

⚠️ `stall onset` を宙に浮いた新しい検出器として設計しない。
★ **repo には既にエピソード分割器がある**（★ 2026-09-13 実測）:

| 既存物 | 場所 | 中身 |
|---|---|---|
| `StuckTrigger`（3 値） | `metrics.rs:122-129` | `PStuckThreshold`（既定）/ `UserLabel` / `InterventionFired` |
| `segment_stuck_episodes` | `metrics.rs:319` 周辺 | 連続 Stuck を `merge_gap_ms` で 1 エピソードに統合 |
| `OutcomeConfig` | `metrics.rs:135-158` | 閾値を外出し。⚠️ 逐語「研究設計フォークをコードに焼き込まない」 |

→ ★ **`stall onset` は「4 つ目の `StuckTrigger`」として定義する。**

### ⚠️★★★ 既存 3 トリガは **どれも予測トラックの原点に使えない**（★ これが本 ADR の核心）

| トリガ | ⚠️ なぜ使えないか |
|---|---|
| `PStuckThreshold`（**既定**） | ★★★ **循環している。** `p_stuck` は推定器の出力であり、それで criterion の原点を定義すると「入力した pause を別名の score として返しているだけ」になる（`.idea/criterion §1.1` 逐語「`p_stuck` が高いこと自体は妥当性の証拠ではない」） |
| `UserLabel` | ⚠️ **較正セッションにしか無い。** O1 は自然作業で GT ラベルが無い |
| `InterventionFired` | ⚠️★★★ **介入が原点になる。** ADR-029 D1 が禁じた「介入を駆動する量と介入を評価する量の同一化」と**同型** |

> ★ **これは「新しい判定量」ではない。** ADR-014 D4c の禁止対象は **判定量（= G2 の上下界の幅）**であり、
> 本 ADR が足すのは **ADR-029 D2 が既に確定した `t0` の検出器**である。判定量は 1 つも増えない。

## Decision（ADR-030 に書く内容）

### D1. 検出器は **オフライン側**に置く（★ `HMM_VERSION` 不変）

- `engine.rs:27-58` が bump 対象に挙げるのは `features.rs` の
  `phi` / `make_silence_observation` / `calculate_features` の**数値挙動**。★ そこに触らない。
- 先例: `metrics.rs:4-5` 逐語「派生値はログ記録時ではなく本モジュールで計算する設計のため、
  閾値変更時に過去セッションを再処理するだけで再計算できる」。
- ADR-014 D4b「記録のみ。推論には 1 バイトも流さない」と整合。

### D2. `t0` = **検出時点**に置く（⚠️ 停滞が始まった時点ではない）

★ **理由は 2 本ある。v1 は 1 本しか持っていなかった。**

1. **不死時間バイアス（immortal time bias）** ★★★ ——
   `t0` を「継続の開始時点」に置くと、区間 `[t0, t0+θ]` では
   **回復が起きていないことが定義上保証される**（起きていれば onset が宣言されない）。
   ⚠️ **リスク集合に「イベントが起こりえない時間」が入る** ＝ 初期の期のハザードが下向きに歪む。
2. **窓の重なり** —— `criterion:66` 逐語「stall onset の検出窓と転帰判定窓を重ねない」。
   検出窓 `[t0−θ, t0]` と転帰窓 `[t0, ∞)` が接するだけになる。

★ 副次的利点: **オンラインで観測可能な時点**なので、Layer 5 が読み出す時点と一致する
（左側切断が起きない）。

### D3. 検出条件 —— **既存パラメータを再利用し、新しい定数を作らない**

入力は **`key` 行の `(t, category, press)` 列だけ**（★ `schema_dto.rs:132-136`・新計器ゼロ）。

```text
条件 A（産出）: 因果窓 W（右端 = 評価時刻・★ look-ahead ゼロ）内の
                net = Σ(挿入系 press) − Σ(削除系 press)  が  net < net_diff_min
                ★ net_diff_min は既存 OutcomeConfig の値（既定 1）を再利用する
                  （`metrics.rs:147-149` 逐語「純増 1 文字以上で前進」。★ 回復側と対称）
条件 B（持続）: 条件 A が θ_person を超えて連続した
t0            : 条件 B が成立した時点
```

⚠️★★★ **`progress_proxy` を onset に使わない。** `progress_proxy` は
「**T 秒以内に取り消されない**」という **look-ahead** を持つ（`personalization:341`）。
使えば検出窓が `t0+T` まで伸びて転帰窓と重なる。
→ ★ **onset は look-ahead-free。`recovery`（転帰）側だけが `progress_proxy` を使う。**

⚠️ `feat` 行から復元してはならない —— `schema_dto.rs:174-176` 逐語
「累積カウンタではなく…沈黙中は同じ値が毎秒くり返される」。★ **`key` 行の生の `t` 列を使う。**

### D4. `θ_person` = **個人内分布の分位点**（★ 絶対秒数を固定しない）

```text
θ_person = max( W , quantile_q( その個人の隣接 key 行の t 差分の分布 ) )
```

- ★ **床は `W`**（＝検出器自身の分解能。⚠️ 絶対秒数の床ではない）。
- ⚠️ **天井は置かない** —— 絶対秒数の天井は「絶対秒数で固定しない」と衝突する。
- ★ `q` の**値**は P1 開始前に事前宣言する。★★★ **本 ADR が凍結するのは「決め方」だけ。**
  ★ 先例: ADR-009 §Accepted 条件 B 逐語「**決め方は 2026-08-16 に凍結済み**」（Δ と同じ形）。
- **推定の会計は ADR-008 D4 に従う**: `cold_start` / `past_session_adapted` は可、
  ⚠️ `within_session_adaptive` は**探索的結果としてのみ**。
- ⚠️★★★ **根拠の格を正確に書く**: 「個人間 66 倍」は **F5（= `2 秒以上の無入力回数`・
  `features.rs:28`）の中央値**の話であって、**pause 長そのものの分布ではない**。
  ★ 「固定閾値が個人を大きく違う形に切る」ことの**間接証拠**として引く（⚠️ 直接測定と書かない）。

### D5. `phase` は O1 では `unspecified` に collapse する

★ `task-adaptation-and-scope-gating.md §3.6` の**暫定案（研究者判断待ち）を本 ADR で確定**する。
→ 鍵は `user × task_kind` の 2 つに落ちる。⚠️ 意味的 `phase` を検証する正解ラベルが無いため。

### D6. `task_kind` —— ⚠️★★★ **引き継ぎと ADR-014 D4d の推論を訂正する**

★ **一次確認（2026-09-13）**:

| # | 実測 | 場所 |
|---|---|---|
| 1 | `App.tsx` の `TASK_KINDS` は `argumentative` 1 値のまま | `App.tsx:15-21` |
| 2 | ★★★ **O1 はその画面を経由しない** —— 逐語「**O1 では最初からダッシュボードを出す。宣言は `RecordingControls` から行う**」／ `if (o1Mode) setIsStarted(true);` | `App.tsx:192` / `:339` |
| 3 | ★ O1 の宣言 UI は **4 値** | `RecordingControls.tsx:61-71` |
| 4 | backend の入口は `declare_task_kind` **1 本**（★ `record_session_meta` は O1 で拒否される） | `lib.rs:1345` / `lib.rs:2404-2410` |

→ ★★★ **ADR-014 D4d の本文「lock は残っている」は `App.tsx` については正しいが、
そこから引いた「解除しない限り R3 は `task_kind` 分散ゼロ」は *実装で解消済み*** である
（★ ADR-014 判断 5「R3 の範囲でのみ解除する」が **別経路として**実装された）。
⚠️ **ADR-014 本文は書き換えない。** 本 ADR 側に訂正を書く（ADR-021→022→026→027 の先例）。

⚠️ ただし **`task_kind = null`（未宣言）はありうる**（ADR-016 判断 4b-1「強制しない」）。
→ ★ **`null` を 5 値目にしない。鍵を作らず個人全体の基準へ back-off する。**

### D7. `Decision Episode` は**新設しない**

| 何 | ★ 使う既決 |
|---|---|
| 作る部品 | **ADR-008 D2** の `ContextBuilder`（⚠️ 実装は未着手 —— `PersonalizationStore` を grep して **0 件**） |
| 読み出し単位 | **ADR-010 D4** 逐語「推定は streaming 窓、読み出しは Decision Episode」 |
| 意味的境界 | **ADR-014 D6**（★ 境界イベント列は `personalization §3.1` のまま） |

★ **1 `stall onset` = 1 `Decision Episode` の開始**。★ 標本単位はこれ（`criterion:68` の leakage 防止 4 番目）。
⚠️ `.idea` の第三語彙（`departure` / `externalization`）は**名前を採らない**（ADR-029 D5）。

### D8. 除外区間では検出器を走らせない（★ ADR-016 D4 ＋ ADR-029 D3 のまま）

`recording_pause{paused=true}` / `secure_input{on}` / `hook_health{alive=false}` /
`dropped_delta > 0` / セッション境界。
⚠️★★★ **除外区間の沈黙を「産出なし」として数えると偽 onset が出る。**
⚠️ `hook_health` / `starve_window` は `threshold_gated`（`capabilities.rs:107`）なので
**0 行は「健全」ではなく「判定不能」**。★ 行がある区間だけで回す（ADR-029 D2 と同じ規律）。

### D9. ⚠️ 壁時計の非単調性を**未決として明示する**

★ `t` は `SystemTime::now()` 由来（`hook_windows.rs:563-579`）＝ **単調ではない**。
`saturating_sub` は逆行を 0 に潰す（`metrics.rs` 各所）。
- **逆行**（負ギャップ）→ 0 に潰れるので onset は**出にくくなる**（安全側）。
- ⚠️★★★ **前方跳躍**（時計補正・スリープ復帰）→ **巨大な偽ギャップ ＝ 偽 onset**。
→ ★ **本 ADR では閾値を決めない**（決めると恣意的な絶対秒数になる）。
  ⚠️ **未決として起票し、P1 の実データで跳躍の頻度を見てから決める。**

### D10. 特徴量再設計の **accept 対象**（⚠️ 特徴リストではない）

1. **Tier の枠**: T0 / T1a / T1b / T1c / T1d / T2 / T3 / **Q**（`survey §6.1` ＋ `criterion §2.1`）
2. **投資順序** T0 → T1 → T2 → T3、★ **上位 Tier は必ず下位への held-out block ablation で評価**
3. **leakage 防止 6 項**（`criterion §1.3`。★ 4 番目は ADR-010 D4 で既決）
4. ⚠️★★★ **`Q` を状態特徴にしない** —— `survey:194` 逐語
   「欠測を 0 として入力せず、**推論の抑制・abstention に使う**」

### D11. **計器を変えない範囲 / 変える範囲**の仕切り

| 範囲 | 計器 | ★ 根拠（一次） |
|---|---|---|
| **T0 / T1a / T1b / T1d / Q** | ✅ **不要** | `key` 行が **1 打鍵ごとに `t`**（`logger.rs:1634-1638`）／`KeyCategory` **14 種**で `sentence_punctuation` 分離済み（`anonymize.rs:93-110`）／`capabilities` ＋ `hook_health` 在り |
| ⚠️ **T1c** | **要** | `undo/redo` 不可 —— `KeyCategory` 量子化で `Ctrl+Z` と `Ctrl+A` が同じ `modifier`+`alphabetic` |
| ⚠️ **T2** | **要** | `focus_transition` は `{ t }` **のみ**（`schema_dto.rs:211` 逐語「HWND / PID / アプリ識別子…は 1 バイトも含まない」）→ **「元 app へ戻った」が作れない** |
| ⚠️ **T3** | **要** | `criterion:95` 自認「O1 の現行観測空間外」 |

★ **変える範囲は本 ADR で決めない** —— §8 タスク 4（起票 11 の ESM と束ねて一括裁定）へ送る。

## 変更対象

### 新規作成
- `docs/adr/ADR-030-stall-onset-and-decision-episode.md`

### 修正
- `docs/adr/README.md` — 行を 1 本足す（⚠️ `git add` はファイル指定で行う）

### 触らない
- ⚠️ `features.rs` / `engine.rs` / `metrics.rs` / `schema_dto.rs`（★ コード変更ゼロ）
- ⚠️ `ADR-009` / `ADR-014` / `ADR-016` / `preregistration-v0.3.md` の本文

## 既存パターンとの整合性

- ADR ヘッダは `昇格元: .idea/...`（ADR-008 / 009 / 014 / 029 と同形式）
- 改訂は**番号の大きい新 ADR 側**に書き、`README.md` の重ね書き注記で追跡する

## テスト戦略

⚠️★★★ **この裁定の正しさは機械検証できない。** 機械 AC は衛生条件:
`check_doc_lexicon.py`（⚠️ **ADR は検査対象外**・緑を「検査された」と読まない）／
`check_citations.py`（⚠️ 1 回で全件出ない → 反復）／ README 行の grep。
★ 実質の検証は `/cross-review` ＋ `code-reviewer` ＋ `security-checker` の **3 本**。

## ロールバック計画

ADR は append-only。誤りは番号の大きい新 ADR で上書きする。

## 設計判断の履歴
- 実行回数: 1 回目（`/reimagine`）
- 採用: **v2（再生成案）**
- 根拠: v1 は `metrics.rs` の既存 `StuckTrigger` / `segment_stuck_episodes` を見落としており、
  そのまま実装へ渡すと**契約の二重定義**が生まれる。また既定 `PStuckThreshold` が
  **推定器の出力で criterion の原点を作る（＝循環）**ことを明示的に却下できない。
  `t0` の根拠も v2 で 1 本 → 2 本（不死時間バイアスが主）になった。
- 研究者判断（2026-09-13）: **v2 採用** / **ADR-029 ブランチから分岐** / **`phase` は §3.6 暫定案を確定**
