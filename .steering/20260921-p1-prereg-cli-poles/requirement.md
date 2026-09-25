# P1 前: 事前宣言文書 ＋ CLI 注入 ＋ 両極（ポインタ・修飾キー）の出力

> ★ 一次: `.steering/20260914-mhd-feature-offline-tiers/decisions.md` **判断 25 #13**（`:1134`）／
> 同 `blockers.md` **起票 7 / 11 / 12 / 13 / 14 / 15 / 16 / 20 / 21**／
> `docs/adr/ADR-030-stall-onset-and-decision-episode.md` **D2 / D3 / D4 / D8 / D10 ＋ 補訂 1**／
> `docs/preregistration-v0.3.md`／`.idea/20260911-...roadmap` §3（WP0〜WP3）。
> ⚠️ `.steering/_handoff/next-session-step6-prereg-cli-poles.md` は**一次ではない**。

## 背景

ADR-030 は `stall onset` の検出器の**構造**を凍結したが、**定数は凍結していない**
（★ ADR-010 D5「検出器の構造を凍結し、定数は凍結しない」と同型）。その結果、次の 7 つが
未確定のまま実装の `Default` 値として残っている:

| 記号 | 役割 | 現行の `Default` | 一次の制約 |
|---|---|---|---|
| `W` | 条件 A の因果窓長 | 30,000 ms | ADR-030 D4「特徴量窓と同じ **30 秒系列**から選ぶ」 |
| `q` | `θ_person` の分位点 | 0.99 | ADR-030 D4「**p99 以上**から選ぶ」 |
| `B` | `t0` 直後の buffer | 30,000 ms | ADR-030 D2 / D4「`W` と同じ **30 秒系列**から選ぶ」 |
| `hole_gap_ms` | 観測区間を切る閾値 | 2,000 ms (2 tick) | ADR-030 補訂 1 項目 5「仮の値は `2 × ENGINE_TICK_MS`」 |
| `warmup_count` | θ の標本数の下限 | `None` | ADR-030 D4 点 1「下回ったら個人分位点を使わない」 |
| 分位点の推定法 | nearest-rank か線形補間か | nearest-rank | ADR-030 D4 点 3「**事前宣言する**」 |
| `T1a` の窓 | 分布特徴の集約窓 | 1 tick（＝ 未導入） | 起票 7 / 判断 25 #11 |

⚠️★★★ **このうち `T1a` は「未確定」ではなく *壊れている*。** 実測（`blockers.md` 起票 7）:
`features::PAUSE_THRESHOLD_MS`(2000) > `loop_step::ENGINE_TICK_MS`(1000) なので **1 tick に pause は
高々 1 本**であり、`pause_p50_ms` / `pause_p90_ms` / `pause_max_ms` は**常に同値**である
（★ `tests/fixtures/` 14 本すべてで `p50 != max` の行が 0 件）。
→ ⚠️ `issues/003.md` **AC3** の不変式 `p50 <= p90 <= max` は**等号でしか成立せず検出力がゼロ**である。

さらに、ADR-030 が「**片方に決めず両極で挟む**」と定めた 2 組の極が**どちらも未実装**である:

- **ポインタ**（D3 の囲み・補訂 1 項目 8）: 極 A（抑制しない ＝ 現行）／極 B（ポインタ活動区間を抑制）。
  ⚠️ `pointer_bin` は `analysis/pointer_bin.rs` に実装済みで NDJSON にも出ているが、
  **`--features` の collector に無い**。
- **修飾キー**（補訂 1 項目 3）: 極 M−（規則なし ＝ 現行）／極 M+（`modifier` 押下区間中の文字キーを
  挿入系に数えない）。

⚠️ 両極を出すには**出力の形を決める必要がある**（起票 13）—— 現行の `--features` は
**1 tick 1 行・`stall_onset` は 1 列**であり、極を足すとこの形に触る。

最後に、値を凍結しても**外から渡す経路が無い**（起票 16）——
`bin/replay.rs` の `--features` 経路は `StallOnsetConfig::default()` を渡している。

### ⚠️★★★ 一次の中に食い違いが 1 件ある（本タスクが閉じる）

- 起票 14 / 16（`blockers.md:517` / `:549`）: 「**P1 *前*** に 1 本の事前宣言文書で凍結する」
- 起票 15（`blockers.md:735`）: 「**P1 の実データ**で `feat` 行の隣接差の分布を見て … 事前宣言する」

★ `docs/architecture/personalization-and-online-learning.md:1225` で **P1 = 自然作業の episode 化
フェーズ（G1 の後・未実施）**なので、**両立しない**。→ ★ 本タスクは
「**P1 で使う運用値は今凍結し、探索は P1（discovery）の中で回して WP2 で freeze する**」（判断 A）で閉じる。

## ゴール

1. **P1 前の事前宣言文書 1 本**を作り、上の 7 項目の**運用値**と**探索空間・選択手続き**を凍結する。
2. **その値を `--features` に注入する経路**を作る（★ 値より先に作らない ＝ 研究者判断の順序制約）。
3. **両極（ポインタ 極 A/極 B・修飾キー 極 M−/極 M+）を出力できるようにする**。
4. ADR-030 に**補訂 2** を足し、補訂 1 の「補訂しないもの（範囲外）」をすべて閉じる。

★ Done は exit code で言える（→ `design.md` §受け入れ条件・各 issue の Acceptance Criteria）。

## スコープ

### 含むもの

- **【1】事前宣言文書**（新設 `docs/preregistration-p1-episode.md`）＋ **凍結 JSON**（SSOT）
  ＋ **文書と JSON の一致検査**
- **【2】CLI 注入**: 凍結 JSON を既定として読み、`--feature-config <path>` と
  `--set <key>=<value>` で上書きできる経路。封筒に「既定から外れた値」を明示的に刻む
- **【3】両極**: `--pole <baseline|pointer_b|modifier_m_plus>`（**1 実行 1 極**）
- **`pointer_bin` collector**（極 B に必須。`--features` 経路へ追加）
- **`T1a` の 30 秒ローリング窓**（＋ `features.rs:129` の生リテラル `30_000` の `pub const` 化）
- **θ の標本数 `n` の出力**（退化の判定を解析側で可能にする）
- **削除 UI の最小幅 > `hole_gap_ms`** の固定（**(b) 入口で広げて消す ＋ (a) 定数比較の検査**）
- **IME 変換中の onset 頻度カウンタ**（補訂 1 項目 4 の暫定の数え方）
- **極 M+ の `not_applicable` 判定単位**の裁定と実装
- **起票 21**（`008-acceptance.sh` AC18 / AC18b が `R = 1` なので `R` に比例する経路を素通りさせる）
- **ADR-030 補訂 2**

### 含まないもの

- ⚠️ **`cold_start`（集団 prior）の新設** —— ★ P1 前に集団データが無く、prior の中身を推測で埋めることになる。
  → `warmup_count` を下回る間は **onset を立てない**（issue 005 Stop Condition「既定値で埋めない」のまま）
- ⚠️ **壁時計の非単調性（ADR-030 D9）** —— ★ ADR が「**P1 の実データで頻度と大きさを見てから決める**」と
  しており、今決めるとその判断を覆す
- ⚠️ **`key.mod`（ADR-032 D9）の実装** —— ★ schema / logger / `schema_dto.rs` に**存在しない**（実測）。
  → 極 M+ は `category:"modifier"` の押下区間でのみ計算する（★ Shift を含む側）
- ⚠️ **`meta` 行への `os` の追加** —— ★ 計器の変更（ADR-032 の領域・起票 1）
- ⚠️ **匿名化写像の変更（`modifier` の分割）** —— ★ ADR-014 判断 6 の再審・同意文書の再開封（補訂 1 項目 3）
- ⚠️ **E1（エピソード連結）の実装** —— ★ 補訂 1 項目 6 が issue 006 の V1 へ回しており、
  `recovery`（`progress_proxy`）が未実装のまま入れると検出列の挙動が変わる
- ⚠️ **`--features` 出力の `gse-dataset` への共有** —— ★ `docs/glossary.md`「特徴行」の禁止のまま

## 受け入れ条件

- [ ] `docs/preregistration-p1-episode.md` が存在し、7 項目の運用値と探索空間を持つ
- [ ] 凍結 JSON が repo にあり、**文書の値と JSON の値の一致**を検査するスクリプトが exit 0
- [ ] `gse-replay <in> --features` が凍結 JSON を既定として読み、封筒 `config` にその値が出る
- [ ] `--feature-config` / `--set` で上書きでき、封筒に「既定から外れた」事実が刻まれる
- [ ] `--pole baseline|pointer_b|modifier_m_plus` が 3 本とも**同一の行の形**で出力される
- [ ] 極 M+ が計算できない入力で `pole_applicable=false` と理由が封筒に出る（値で埋めない）
- [ ] `T1a` の 3 値が 30 秒窓で**同値でなくなる** fixture があり、旧検査（同値固定）が置き換わっている
- [ ] 削除幅の制約に**陽性対照**がある（違反する値で赤になる）
- [ ] `cargo test --workspace` / `check` / `clippy` / `fmt` / ゴールデン / schema parity がすべて exit 0
- [ ] `code-reviewer` ＋ `security-checker` 並列 → `/cross-review`（Codex・2 巡）

## 運用メモ

- **/reimagine 適用: No**
- 理由: 設計分岐 12 件は本セッションの grill で**研究者が直接裁定済み**（→ `decisions.md` 判断 1〜12）。
  初回案を破棄して再生成する余地は、裁定済みの分岐を無視することにしかならない。
- **実行の形**: **混合** —— 【1】は本セッションの対話で作り研究者の承認を経て凍結、
  【2】【3】ほかを issue に分解して**新セッションで Loop**（★ `docs/loop-engineering.md`）。

## 関連ドキュメント

- `docs/adr/ADR-030-stall-onset-and-decision-episode.md`（D2 / D3 / D4 / D8 / D10 ＋ **補訂 1**）
- `docs/preregistration-v0.3.md`（★ 凍結済みの合否契約。**本タスクは触らない**）
- `docs/architecture/personalization-and-online-learning.md` §10 / §11（P1 の位置づけ）
- `.idea/20260911-mhd-growth-personalization-and-gse-overview-roadmap.md` §3（WP0〜WP3）
- `.steering/20260914-mhd-feature-offline-tiers/`（`decisions.md` 判断 25 ／ `blockers.md` 起票 7〜21）
- `docs/loop-engineering.md`（Loop を回す段の SSOT）
