# 再開アウトカムの裁定 —— 主要アウトカムから推定器を外す (ADR-023 M3 の決着)

- **作成日**: 2026-09-07
- **前段**: `.steering/20260906-resumption-baseline/` (B1 完了 / M1 設計完了)
- **入口**: `.steering/_handoff/next-session-after-b1.md` §B-0 (⚠️★★★ 三次資料。★ 一次で裏を取った)

## 背景

★ **ADR-023 D7 が「機会保存の 2 指標が、プロジェクトが降ろした主張 (`p_flow` = 3 クラス分類) に
依存している」ことを記録に固定した。**⚠️ ただし **ADR-023 はコード変更ゼロの規約**だったため、
是正案の選択 (§Alternatives A3 の (i)/(ii)/(iii)) は **§Migration M3 として別タスクへ送られた**。

★ さらに 2026-09-06 に研究者が逐語で
「**立ち直ったなどではなく、身体的回帰をしたという意味付けにはならない？**」と提起し、
`experiments/20260906-interruption-resumption-arm1/notes.md` §10 に **未決 1 件**として記録された。
→ ★ **本タスクはこの 2 つを同時に決着させる。**

### ⚠️★★★ 本タスクで一次から新たに分かったこと (★ ADR-023 に無い)

| # | 発見 | 一次 |
|---|---|---|
| **1** | ⚠️★★★ **「外部の事実」であるはずの paste も、推定器が決めた窓で測られている** | `metrics.rs:370-378` —— `rec_ts` は「最初に `p_flow > 0.5` になった時刻」であり、`has_paste_in(pastes, ep.end_ms, rec_ts)` の **窓の右端がそれ**。→ ★ **p_flow が速く上がるほど窓が短くなり、paste を拾う機会が減る。**⚠️ 分母は `episode_count` 固定 (`metrics.rs:390`) なので、**① 回復判定を通る episode が増える / ② 窓が縮む の 2 経路とも同じ向きに押し上げる。**→ ⚠️★★★ **A3-(iii) の「併記義務」では防げない機械的バイアスである** |
| **2** | ⚠️ **回復窓の既定値が 2 系統ある** | `OutcomeConfig::default().recovery_window_ms = 5 * 60 * 1000` (`metrics.rs:157`) ⇄ 定数 `DEFAULT_RECOVERY_WINDOW_MS = 15 * 60 * 1000` (`metrics.rs:12`)。★ 後者を使うのは `compute_session_metrics` (`metrics.rs:497`) と `intervention_eval.rs:39` だけ。→ ★ **アウトカム系は 5 分である** |
| **3** | ⚠️★★★ **(b) 案 (トリガーも時計にする) は処置後変数で条件付ける** | ★ Physical Anchor は **離席を誘う介入**なので、離席候補の発生自体が処置の結果である。→ ⚠️ 分母を「離席候補の個数」に置くと、H-Y の効果推定で**選択バイアス**になる。★ `arm1/notes.md` §10 の「代償」欄に**この項目は無い** |
| **4** | ⚠️ **ADR-023 の内部に名前と形の不整合が 1 件ある** | `ADR-023:542-543` は **`receipt_free_resumption` = 生存時間 / 競合リスク**、**`stuck_exit_without_receipt` = 二値率**と割り当てている。⚠️ ところが **M2 と `adr/README.md:51` は「`self_recovery_without_paste` → `receipt_free_resumption`」**と書く。★ `self_recovery_without_paste` は **二値率** (`metrics.rs:390`) なので、そのまま改名すると**生存時間用の名前が二値率に付く** |

## ゴール

★ **主要アウトカムから推定器 (`p_flow`) を外し、ADR-023 が D6 で既に決めていた形
(`receipt_free_resumption` = 競合リスク) を「時計の事実」で実装しきる。**

★ **Done は exit code で言える**:

| # | Done 条件 | 検証コマンド (★ `src-tauri/` から実行) |
|---|---|---|
| **D-1** | 新指標と改名がコンパイルを通り、既存テストが緑 | `cargo test --workspace` が **exit 0** |
| **D-2** | 新指標の単体テストが緑 | `cargo test --workspace receipt_free_resumption` が **exit 0**・★ 追加する test 名は design.md §テスト戦略 |
| **D-3** | ⚠️ **回帰が byte-equal で保たれる** | `cargo run --bin gse-replay -- tests/fixtures/minimal.ndjson --snapshot tests/snapshots/minimal.json` が **exit 0** |
| **D-4** | ⚠️ **schema drift 無し** | `cargo run --bin emit_schema` の出力が `src-tauri/schema/current.json` と byte-equal |
| **D-5** | ★ 引用規約違反ゼロ | `PYTHONUTF8=1 python scripts/check_citations.py` が「違反なし」まで (⚠️ **1 回で全件出ない** —— 是正 → 再実行を繰り返す) |

★ **Stop 条件** (★ 進めずに研究者へ戻す):
- ⚠️ D-3 が赤になり、差分が **意図した変更で説明できない**とき
  (★ 本タスクは `HMM_VERSION` を **bump しない**ので、`FeatSnapshot` 列は 1 byte も変わらないはずである)
- ⚠️ `gse-dataset` 側の `metrics/P*/<os>/metrics.json` に改名対象フィールドが実在し、
  後方互換の判断が研究者を要するとき

## スコープ

### 含むもの

1. ★ **裁定を ADR-024 として起票する** (⚠️ ADR-023 本文は書き換えない規約のため、新規 ADR が要る)
2. ★ **`receipt_free_resumption` を `metrics.rs` に実装する** (★ 競合リスク・時計基準)
3. ★ **`self_recovery_without_paste` → `pflow_exit_without_receipt` へ改名し、副次へ降格する**
4. ★ **M2 の残り `recovery` 系識別子を一括処理する**
   (`productive_manual_recovery_rate` / `recovered_episode_count` / `compute_recovered_at` / `recovery_window_ms`)
5. ★ **`docs/glossary.md:247-248` の例外条項を同じ版に揃える** (→ ADR-023 D6 冒頭の要求)
6. ★ **`experiments/20260906-interruption-resumption-arm1/notes.md` §10 の未決を閉じる**
   (★ §5 のアウトカムの表と定型文も新形へ更新する)

### 含まないもの (★ 明示的に Out)

- ⚠️ **`HMM_VERSION` の bump とゴールデン再生成** —— ★ (b′) を採ったので **不要になった** (→ decisions.md 判断 1)
- ⚠️★★★ **`receipt` の実装を広げること** —— ★ CGT 挿入 / suggestion accept は `data-privacy` ルール 7 に当たり
  **別 ADR の主題**である (ADR-023 §Migration 「守ること」逐語)
- ⚠️ **M1 の Step 2b (アウトカム本解析) を回すこと** —— ★ 本タスクは**計器を用意するところまで**。
  ⚠️ かつ **素の比率 (66/125) を既に見てしまっている**ので事前登録へ格上げできない (`arm1/notes.md` §7-1)
- ⚠️ **フォーカス遷移アーム** —— ★ `capabilities_gate.py` が `INSTRUMENT_ABSENT` (exit 4) で止める
- ⚠️ **ADR-017 / 018 / 020 / 021 / 022 / 023 の本文書き換え**
- ⚠️ **凍結済み `docs/preregistration-v0.3.md` の書き換え**
- ⚠️ **アート (表現の形) の議論** —— ★ ハンドオフ §B-1。**次セッションへ**
- ⚠️ **`capabilities_gate.py` の `file_id` 是正** —— ★ ハンドオフ §C-2-1。**別タスク**
- ⚠️ **`scripts/secrets-filter.sh` への `email=` 追加** —— ★ fail-closed で over-block (M10)

## 受け入れ条件

- [ ] **AC-1**: D-1 〜 D-5 がすべて exit 0 / 「違反なし」
- [ ] **AC-2**: `receipt_free_resumption` の算出に **`p_flow` が 1 度も現れない**
      (★ 検証: 新規関数の本体に `p_flow` の文字列が無いことを test で固定する)
- [ ] **AC-3**: 新指標が **離席候補 (≥180s) を要求する**こと、および閾値の SSOT が 1 つであること
      (★ `intervention.rs` の `AWAY_IDLE_MS` を再定義しない)
- [ ] **AC-4**: ⚠️ **系が「離席した」と宣言しない** —— ★ 新指標は**事後の層別解析**であり、
      `InterventionDecision` にも UI にも出ない (ADR-018 D1)
- [ ] **AC-5**: ADR-024 に **却下案 (i)/(ii)/(iii)/(b) とその理由**が書かれている
- [ ] **AC-6**: `docs/glossary.md` の例外条項が新しい名前と矛盾しない
- [ ] **AC-7**: ⚠️ **報告時の定型文が「窓長依存」を含む**ように更新されている
      (★ ADR-023 D7-2 の併記義務は、新発見 1 を知らずに書かれている)

## 関連ドキュメント

- `docs/adr/ADR-023-coupling-as-primary-outcome.md` **D6 / D7 / D8 / §Alternatives A3 / §Migration M2-M3**
- `docs/adr/ADR-018-physical-anchor-without-completion.md` **D1**（系は開始も完了も判定しない）
- `docs/adr/ADR-017-expression-channel-boundary.md` **D8 / D10**（入力の割り方 / 身体センサ恒久除外）
- `experiments/20260906-p321-resumption-baseline/notes.md`（B1 の結果と限界）
- `experiments/20260906-interruption-resumption-arm1/notes.md` **§5 / §7 / §10**
- `docs/glossary.md:247-248`（禁止用語の例外条項）

## 運用メモ

- **/reimagine 適用**: **No**
- **理由**: ★ 設計の選択肢 (A3 の 3 案 ＋ (b) ＋ (b′)) は **ADR-023 が既に列挙しており**、
  本セッションの grill で **一次の新発見 3 件を提示したうえで研究者が (b′) を選んだ**。
  ⚠️ 初回案を破棄して再生成する段階ではなく、**確定した裁定を実装する段階**である。
