# ADR-013: 収集仕様の自己記述性 — 「信号が無い」と「計器が無い」をログだけで区別する

- **ステータス**: **Accepted**（2026-08-19・研究者決定）。
  ★ **実装済み（2026-08-19・同日）** —— ⚠️★★★ **G1 リブートによりゲートが「G1 完了後」から
  「*リブート前の停止期間*」へ変わった**ため（下記 D5 の追記）。
  作業記録: `.steering/20260819-g1-reboot-and-instrument-fix/`
- **日付**: 2026-08-19
- **関連**: **ADR-012**（本 ADR が支える形成的トラック・一体で読む）/ ADR-005（additive schema versioning）/
  ADR-011（`hook_health` / `starved_ms` に依存する探索トラック）/
  `docs/architecture/personalization-and-online-learning.md §5.2` / `docs/development-guidelines.md §10`
- **作業記録**: `.steering/20260819-nonkeystroke-observation-space/`（決定 D-10 / D-12）

---

## Context

### 1. ⚠️★★★ 「計器がコホートを跨げなかった」が **2 件目**である

| # | 信号 | 何が起きたか |
|---|---|---|
| 1 | `keys` / `bs_keys`（Tier 0） | 配線は **2026-08-16**。⚠️ Phase1 ログはそれ以前なので存在しない。`§5.2` 逐語「⚠️ **旧 NDJSON には本フィールドが無い**ので、`--metrics` 経路では欠測が `0` に倒れる（「実測 0 打」と区別できない）」 |
| 2 | `hook_health` / `starved_ms` | ⚠️ **Phase1 コホート（P010–P014・63 ファイル）に 1 行も無い**。記録期間 **2026-07-04〜07-24** に対し `liveness.rs` の追加は **2026-08-09** ＝ **収集の 16 日後**（`experiments/20260819-silence-presence-decomposition/notes.md §1`） |

→ ★★★ **教訓の逐語**（同 `§1.1`）:
**「既存ログにある」は *現行コードが出す* の意味であって、*対象コホートにある* の意味ではない。**

⚠️★★★ **決定的な事実**: これは「**規約が無かった**」失敗ではない。
★ **`§5.2` に警告が書いてあったのに、`hook_health` には適用しなかった**のである。
→ ⚠️ **人が適用し忘れられる形のままでは、同じことが 3 件目として起きる。**

### 2. ★ さらに、収集仕様そのものに 3 つの穴が実測で見つかった

| # | 穴 | 実測の根拠（`file:line`） |
|---|---|---|
| **A** | ⚠️ **30 秒未満の非打鍵は 1 行も残らない** | `src-tauri/src/lib.rs` の間引き（`if health == prev_health && !rehook { continue; }`）＋ `src-tauri/src/input/liveness.rs` の `log_after_ms: 30_000`（`log_after_ms: 30_000`）→ **[P121] が「局所思考」と位置づけた micro 帯（2–15 秒）について永久に何も言えない** |
| **B** | ⚠️ **`dropped` は累積カウンタ**なのに解析側は「この区間で落ちた」と読む | `src-tauri/src/input/hook.rs:140`（`EVENTS_DROPPED: AtomicU64`）を `lib.rs:2883` が読み `:2965` で**そのまま**搬送。★ **前タスクの除外規則が実際に誤読していた**（code-reviewer HIGH で修正） |
| **C** | ⚠️★★★ **計器の有無を「その計器が出す行の有無」で判定できない** | `lib.rs` の間引き（`if health == prev_health && !rehook { continue; }`） は状態変化時にしか出さないので、**計器が動いていて 30 秒未満しか starve しなかったセッションも 0 行**になる。★ 前タスクはこれを「入力皆無だった」と報告しかけた |

★ **C の一般形が本 ADR の核心**である。

### 2b. ★★★ `app_version` は **G1 の実施記録が既に要求していた**（★ 本 ADR の発案ではない）

`experiments/20260801-controlled-friction-task/notes.md:1865-1869` 逐語:

> `hook_health` 行の存在は **v0.1.25 以降**を意味するだけで、v0.1.25 と v0.1.26 を分けない
> （`liveness.rs` の導入コミット 207170f は**両方のタグに含まれる**）。…
> → ★ **`meta` 行が持つのは `hmm_version` だけで、アプリの版を持っていない。**
> **アプリ版を `meta` に刻んでいれば機械的に答えが出た。次の版で入れる価値がある。**

→ ★★★ **同じ穴が、別の実験で、独立に踏まれている。**
⚠️ G1 では「**版の特定はできなかった**（★ 出せないものは出せないと書く）」という
**回復不能な情報損失**として現れた。★ 本 ADR D1 の `app_version` はその起票への回答である。

### 3. ⚠️ G1 は実施中であり、いま記録仕様を変えられない（★ **2026-08-19 に解消した**）

> ⚠️★★★ **本節の制約は同日中に外れた。** 研究者が **G1 のリブート**を決定したため
> （`preregistration.md` 第 17 版）、★ **実施中ではなくなり、停止期間がそのまま実装窓になった**。
> → ★ D1 / D2 / D4 は **2026-08-19 に実装済み**である。
> ★ 以下は**決定当時の状況**として残す（消さない）。

~~**確証標本 1/3 名**（`experiments/20260801-controlled-friction-task/data.md:4`）。~~
★ 現在は **確証標本 0/3 名**（P010 はパイロットへ移動・削除はしていない）。
⚠️ 実施中に記録仕様を変えるとブロック間の比較可能性が壊れ、
`preregistration.md §3.6` が**ブロックの事後除外を禁じている**ため**回復不能**になる。

### 4. ⚠️★★★ **`capabilities` を writer 側（`LogEntry` variant）から導出すると壊れる**（★ 本 ADR で実測）

`logger.rs` が出す行種は **16 種**、`LogEntry` enum の variant は **18 個**（うち行を出すのは 15 個。
`BlockEnd` / `Rotate` / `End` は制御用で行を出さない）。
★ 16 − 15 = **`meta` の 1 種だけ**が variant を持たず、`write_meta_start` / `write_meta_end` から出る。

> ⚠️★ **本 ADR の初版はここを「variant は 12 個・5 種が漏れる」と誤って書いていた**
> （`session_meta` / `probe_assignment` / `realtime_label` / `vignette_response` は
> **variant が実在する**（`logger.rs:780/803/812/829`）——行の整形が
> `format_*_line`（`:534/558/576/626`）に分かれているだけである）。★ code-reviewer の指摘で訂正した。
> ⚠️ **ただし下記の `#[cfg]` の問題は独立に成立しており、D2 の結論は変わらない。**

⚠️★★★ **決定的な事実（★ こちらが D2 の主たる根拠である）**:
**`LogEntry::ImeShadow` は両 OS でコンパイルされるが、送出元は `lib.rs:2257,2270` の
`#[cfg(target_os = "windows")] fn emit_ime_shadow`（`:2242`）だけ**である
（実測。macOS の `input/ime_macos.rs:114` は `ImeState` しか送らない）。

→ ★★★ **`capabilities` を `LogEntry` の variant から導出すると、macOS で `ime_shadow` を
「出せる」と *過大申告* する。** ⚠️ **これは「計器が無い」を「信号が無い」に化けさせる** ——
**本 ADR が防ごうとしている取り違えの、ちょうど裏返し**である。
★ 併せて **`meta` が漏れる**（variant を持たないため）。

★ 実際 `§5.2` は逐語で「`ime_nav` / `ime_abandon` の復旧 … **macOS で常時ゼロ。
実装バグか仕様か未確定**」という**未解決の問い**を抱えている。
→ ★ **送出元ベースの `capabilities` は、この問いを構造的に決着させる。**

---

## Decision

### D1. `meta`(session_start) 行に **`capabilities` と `app_version`** を additive に刻む

```json
{"type":"meta","session_start":1720000000000,"hmm_version":"0.4.0",
 "app_version":"0.x.y",
 "capabilities":{
   "unconditional":["feat","ime_shadow","ime_state","key","paste","review_marker",
                    "session_meta","session_start","user_label","vignette_response"],
   "threshold_gated":["hook_health","starve_window"],
   "config_gated":["probe_assignment","realtime_label",
                   "intervention_decision","intervention_response"]}}
```

⚠️★★★ **列挙する要素は「行種名」であり、`meta` 行のフィールド名ではない。**
★ `"session_start"` は **`{"type":"session_start"}` という *行種*** を指す
（⚠️ **同名の `meta.session_start` *フィールド* とは別物である**。★ Codex 指摘で明記）。
★ 列挙は現行 **16 行種**の実測に合わせ、`"meta"` 自身は**この行がその `meta` なので載せない**。
★ `ime_shadow` は **Windows ビルドでのみ**入る（D2）。

> ### ⚠️★★★ 2026-08-19 改訂 — **第 3 群 `config_gated` を足した**（実装時に発見）
>
> ★ 本 ADR は当初 **2 群**（`unconditional` / `threshold_gated`）で凍結したが、
> ⚠️ **実装レビューで穴が見つかった**（code-reviewer HIGH）:
>
> | 行種 | ⚠️ 設定で丸ごと止まる条件 | 実測 |
> |---|---|---|
> | `probe_assignment` / `realtime_label` | ⚠️★★★ **G1 実施中は常に止まる** | `lib.rs`: `probes_disabled = disabled_by_env \|\| disabled_by_g1.is_some()` |
> | `intervention_decision` / `intervention_response` | ⚠️ **盲検較正では常に止まる** | `lib.rs`: `if !INTERVENTION_ENABLED { return safe_default(); }` |
>
> → ⚠️★★★ **これらを `unconditional` に置くと、G1 ログを下の判定表に掛けたときに
> `probe_assignment` 0 行が「信号が無かった（測れて、無かった）」という *偽の結論* になる。**
> ★ **本 ADR が潰そうとした取り違えそのもの**であり、しかも
> **「計器が無い」より質が悪い**（★ *測ったふりをする*）。
>
> ★ `threshold_gated` を分けた理屈（「0 行は判定不能」）は **設定ゲートにもそのまま当てはまる**。
> → ★ **第 3 群として分ける**。`config_gated` の 0 行は **判定不能**として扱う。
> ⚠️ 旧ログには本キーが無いので `Option`（`required` に入れない・additive）。

★★★ **`unconditional` と `threshold_gated`（★ および `config_gated`）を分ける理由（⚠️ 分けないと本 ADR は自己矛盾する）**:

⚠️ §Context-2 の**穴 C 自身**が「**計器が動いていて 30 秒未満しか starve しなかったセッションも 0 行になる**」
と書いている。→ ★ **閾値ゲート付きの行種では「0 行」は「信号が無かった」を意味しない。**
⚠️ **単一の集合にすると、本 ADR が防ごうとした取り違えを判定表が再導入する**（code-reviewer HIGH）。

★★★ **解析側の機械判定**（★ これが §Context-2 の穴 C の一般形への答え）:

| `capabilities` | 該当行の数 | ★ 結論 |
|---|---|---|
| `unconditional` に有 | 0 行 | ★ **信号が無かった**（測れて、無かった） |
| `unconditional` に有 | ≥1 行 | ★ 通常 |
| **`threshold_gated` に有** | **0 行** | ⚠️★★★ **判定不能**（`signal_absent` と **閾値未達**を区別できない）。★ **「信号が無かった」と書いてはならない** |
| **`config_gated` に有** | **0 行** | ⚠️★★★ **判定不能**（★ **設定で送出元ごと止まっていた**可能性がある。例: G1 では probe 系が常に 0 行） |
| `threshold_gated` に有 | ≥1 行 | ★ 通常（★ 閾値を越えた分のみ） |
| 無 | 0 行 | ⚠️ **計器が無かった**（測っていない）← ★ **2 件の失敗はここ** |
| 無 | ≥1 行 | ⚠️ **宣言のバグ** → `app_version` で追跡する |

⚠️ **`hmm_version` では代用できない**（実測: **HMM の版**であって「何を記録できるか」ではない）。

★ **`threshold_gated` の「判定不能」を減らすのが D4 の `starve_window`** である
（★ 30 秒未満の帯を窓集計で別に残すため）。⚠️ **完全には消えない**（窓集計にも閾値がある）。

### D2. ★★★ `capabilities` は **「送出元があるか」で決め、`#[cfg]` を反映する**

⚠️★★★ **本 ADR で最も重要な決定**。§Context-4 のとおり、
**writer 側（`LogEntry` variant / `write_*` 関数）から導出してはならない。**

| 誤った導出元 | ⚠️ 何が壊れるか |
|---|---|
| `LogEntry` の variant 列挙 | ⚠️★★★ **macOS で `ime_shadow` を過大申告する**（variant は両 OS でコンパイルされるが送出元は `#[cfg(target_os="windows")]`）。★ 併せて **`meta` が漏れる**（variant を持たない）／`BlockEnd`・`Rotate`・`End` を**過大申告する**（行を出さない制御 variant） |
| `logger.rs` が書ける行種の全列挙 | ⚠️ 同じく **macOS で `ime_shadow` を過大申告する**（★ writer 側は `#[cfg]` を持たない） |
| 手書きの定数リスト | ⚠️ **必ず腐る**（新しい行種を足したときの更新漏れ ＝ **今回と同じ失敗の別形**） |

★ **採用する形**: **このビルドで送出元が実在する行種**を、`#[cfg]` を効かせた形で 1 箇所に集約し、
`meta` 行の生成時にそこから読む。

### D3. ⚠️★ **acceptance にテストを含める**（★ 人の規律に頼らない）

実装タスク（★ **2026-08-19・リブート前の停止期間に実施**）の acceptance に、次を**必須**で含める:

1. ★ **網羅テスト**: `logger.rs` のソース中の `"type":"<x>"` リテラルを走査し、
   **`capabilities` の候補集合に現れない行種があれば落ちる**
   （`include_str!("logger.rs")` で自ソースを取り込めば外部ツール無しで書ける）。
   ⚠️ **既知の限界**: テスト用フィクスチャ内のリテラルも拾うため**過大側に振れる**。
   ★ それは「落ちすぎる」方向であり、**見落とす方向ではない**ので受け入れる。
2. ★ **OS 対のテスト**: `ime_shadow` が **Windows では capabilities に入り、macOS では入らない**
   ことを両 OS で固定する。
   ⚠️ 根拠は `docs/agent-shared.md` 逐語「**OS ごとに規則が違うロジックは両 OS に対のテストを置く**」
   （★ 2026-08-10 に macOS 前提のテストが Windows CI で赤になった実績がある）。
3a. ⚠️★ **仕様の回帰テスト（★ 将来実装で抜けやすい・Codex 指摘）**:
   ① **`starve_window` は `n_lt30 == 0` の窓を出力しない**、
   ② **`dropped_delta` が「前回行からの差分」であることを合成入力で固定**、
   ③ ⚠️★★★ **`hook_health` の出力条件と意味論が不変であること**
   （★ **旧ログ（G1 を含む）と新ログを混ぜられる**という D4 の前提そのものなので、
   ここが壊れると **ADR-011 の探索トラックが再計算になる**）。
3b. ⚠️★★★ **逆方向のアサート（過大申告の検出）**: **`capabilities` の各要素に、
   このビルドで到達可能な送出元が存在する**ことを固定する。
   ★ **1. は「漏れ」しか見ておらず、D6 が名指しで警告する「送出元が無いのに載る」を一般には検出できない**
   （★ `ime_shadow` は 2. が偶然カバーするだけである・code-reviewer MEDIUM）。
   ⚠️ **過大申告は「計器が無い」を「信号が無い」に化けさせる**ので、漏れより危険である。
4. ★ **schema parity**: `emit_schema` の diff が **additive-only**（`required` 追加なし・型変更なし）で、
   `scripts/check_schema_parity.py` が exit 0。

⚠️★★★ **テストが無ければ本 ADR は §Context-1 の失敗を防げない。**
★ 「規約は書いてあったが適用しなかった」が今回の失敗の正体だからである。

### D4. 穴 A / 穴 B の閉じ方

#### 穴 A — micro 帯は **`hook_health` の意味論を 1 文字も変えずに** 足す

```json
{"type":"starve_window","t":1720000060000,"win_ms":60000,"n_lt30":7,"sum_lt30_ms":4200}
```

⚠️★ **`n_lt30 == 0` の窓は出力しない。**
★ 理由は 2 つ: ① ログ量が減る、② ⚠️★★★ **毎分必ず 1 行出すと「分単位の在席/中断の連続タイムライン」
という新しい粒度が生まれ、労務監視的な二次利用に転用されうる**（security-checker MEDIUM）。
→ ★ 本 ADR は **micro 帯の量を測る**ためのものであって、**在席を連続記録するためのものではない。**

★★★ **決定的な利点**: `lib.rs` の間引き（`if health == prev_health && !rehook { continue; }`） の出力条件を変えないので、
**≥30 秒トラックの旧ログ（G1 を含む）と新ログが同一意味論のまま比較できる。**
→ ⚠️ **ADR-011 の探索トラックが再計算にならず**、
`experiments/20260819-silence-presence-decomposition/env.md` の「依存している実装」表を壊さない。

★ ログ量は 1Hz 案の **1/60**。⚠️ **失うのは micro 沈黙の *位置***（本数と合計は残る）。
→ ★ 「micro 帯が何割あるか」＝**投資判断の材料としては足りる**
（ADR-011 §Consequences 逐語「投資判断は『≥30 秒で情報がある』と分かってからでよい」と整合）。

⚠️ **閾値を下げる案（`log_after_ms` を 5 秒等）は採らない** —— `hook_health` の意味論が変わり、
**旧ログと混ぜられなくなる**。

#### 穴 B — `dropped_delta` を additive に併記する

```json
{"type":"hook_health","t":...,"alive":true,"starved_ms":0,"rehook":false,
 "dropped":42,"dropped_delta":3}
```

★ `dropped`（累積）は**そのまま残す**（非破壊）。
★ **実装は搬送 1 行で済む**: `lib.rs:2883-2891` に**既に `prev_dropped` があり**、
差分は `dropped_now` として `tracing` に出ている（実測）。
⚠️ **改名（`dropped_total`）は採らない** —— breaking であり、
`validate_blocks.py` 等の解析側を同時に直す必要がある。★ 併記で誤読は消える。

### D5. 実装時期 — ~~G1 完了後~~ ★ **リブート前の停止期間**に始め、次コホートの *収集開始* 前に終える

> ### ⚠️★★★ 2026-08-19 追記 — **ゲートが「G1 完了後」から「リブート前の停止期間」へ変わった**
>
> ★ 研究者が同日 **G1 のリブート**を決定した（`preregistration.md` 第 17 版）。
> → ⚠️ 本 ADR が待っていたのは **G1 が *実施中* であること**であって **G1 の *判定*** ではない。
> ★ したがって **リブートによる停止がそのままゲートを開ける**。
>
> ⚠️★★★ **口頭で済ませず、ここに記録する**（本追記がその記録である）。
>
> ★ **さらに、この順序でなければ得られない利得がある**:
> **ADR-013 実装 → リブート**の順にすると、**新 G1 ログに `starve_window` が載る**。
> → ★ **ADR-012 Stage 0 の左打ち切り問題が緩和される**（`C_write` を下界だけでなく幅で出せる）。
> ⚠️ **逆順（リブート → 実装）にするとこの利得を失う。**
>
> ★ **実施**: D1 / D2 / D4 を 2026-08-19 に実装。⚠️ **収集開始前の残ゲートは下の 2b（同意文書）である。**

⚠️★★★ **締切は募集開始ではなく収集開始である。**
★ 本 ADR の動機がまさに「**計器がコホートより後に作られた**」だからである。

⚠️★★★ **ゲートに「同意文書の更新」を含める（★ 実装だけでは足りない）**:

本 ADR は**被験者に見せている「記録するもの」表に無い項目を増やす**。
→ ★ **`experiments/20260801-controlled-friction-task/consent.md:38-53` の記録項目表と
participant-guide に `starve_window`（＝「毎分の短い中断の回数と合計」）と `app_version`
（＝「アプリの版」）を追記し、配布済みの電子同意フォームと突合するまで収集を始めない。**

⚠️ **repo には同型の事故の実績がある** —— 「`.gs` を直しただけでは実フォームは変わらない／
3 文書を同時に直す」（`consent.md:153-191`）。★ **同じ轍を踏まない。**

~~⚠️ **G1 実施中は着手しない**（§Context-3）。~~
★ **2026-08-19 のリブートで実施中ではなくなったので着手した**（上の追記）。
★ ADR-012 の **Stage 0（既存計器・募集ゼロ）と Stage 1 の別計測器は本 gate に縛られない**
（別プロセス・`src-tauri/` に触れないため）。

### D6. ⚠️★★★ **入れないと決めるもの**（★ 明示的に record する）

| 入れないもの | ⚠️ 理由 |
|---|---|
| **非打鍵モダリティの信号本体**（ポインタ動態 / アプリ切替回数 / 編集イベント）を **GSE 本体へ** | ★ **ADR-012 の実測待ち**。⚠️ いま入れると **ADR-008 D1 が禁じた「dev の推測で superset を決める」**そのものになる |
| **1Hz の全 tick 記録** | ⚠️ ログ量とバッテリの検討が要り、★ **値の大半が 0** になる。窓集計（D4）で目的は足りる |
| **`dropped` の改名**（`dropped_total`） | ⚠️ breaking change。★ 併記で誤読は消える |
| **アプリ識別子 / ウィンドウタイトル / URL / full path / プロジェクト名** | ⚠️ `data-privacy` の禁止事項。★ **[P117] が落ちた穴**（ADR-012 D3） |
| **`capabilities` に「将来出す予定の行種」を先に載せる** | ⚠️ **過大申告は「計器が無い」を「信号が無い」に化けさせる**（§Context-4 と同じ壊れ方） |
| **`app_version` に git SHA / ビルドホスト名 / ビルド時刻 / マシン GUID / OS ビルド番号を入れる** | ⚠️ **フィンガープリントになる**。★ 刻むのは**粗い semver のみ**（security-checker LOW） |
| **`capabilities` / `app_version` を共有アーティファクト（`metrics.json`）に載せる** | ★ 既定は**載せない**（現状 `metrics.json` は `hmm_version` すら載せていない）。⚠️ 載せる必要が出たら別途裁く |
| **毎分の `starve_window` を無条件に出す** | ⚠️ 在席の連続タイムラインになる（D4） |

---

## Alternatives

- **`app_version` / `schema_version` だけを刻み、版→能力の対応表を解析側が持つ**:
  ⚠️ **対応表が repo の外で腐る**。★ 今回の失敗はまさに「**どの版から入ったかを後から `git log` で探す**」
  ことになった事例である。却下（ただし `app_version` は D1 で**併せて**刻む —— 宣言自体のバグを追える）。
- **解析側の規約だけで対処する（「対象ログの行種を数える」を手順の先頭に置く）**:
  ⚠️★★★ **今回の失敗の正体がこれである** —— `§5.2` に警告が書いてあったのに `hook_health` には
  適用しなかった。★ **人が適用し忘れられる形は解決になっていない。** 却下（ただし規約は**併せて**残す）。
- **`capabilities` を手書きの定数リストにする**: ⚠️ 新しい行種を足したときに更新を忘れる。
  ★ **今回と同じ失敗の別形**である。却下（D2 / D3）。
- **`capabilities` を `LogEntry` variant から自動導出する**: ⚠️ §Context-4 のとおり
  **5 種が漏れ、macOS で `ime_shadow` を過大申告する**。却下（D2）。
- **`log_after_ms` を下げて micro 帯を見る**: ⚠️ `hook_health` の意味論が変わり、
  **G1 を含む旧ログと混ぜられなくなる**。★ ADR-011 の探索トラックが再計算になる。却下（D4）。
- **1Hz で全 starvation を残す**: ⚠️ ログ量・バッテリ。★ 値の大半が 0。却下（D6）。
- **G1 実施中に実装する**: ⚠️ ブロック間の比較可能性が壊れ、`preregistration.md §3.6` により
  **回復不能**。却下（D5）。
  ★ **2026-08-19 注**: この却下は**いまも有効**である。⚠️ リブートで変わったのは
  「**いま実施中かどうか**」であって、この規則そのものではない。
  → ★ **収集を再開したら、また触れなくなる**（だから収集開始前に終える・D5）。

---

## Consequences

- ★ **本 ADR ではコード変更ゼロ。** `HMM_VERSION` は `0.4.0` のまま、
  ゴールデン・`schema/current.json`・gse-dataset に差分ゼロ。
- ★ **実装時の変更はすべて additive**（ADR-005）。`required` を増やさないので**旧ログは読めるまま**。
- ★★★ **ADR-011 の探索トラックは再計算にならない**（D4 で `hook_health` の意味論を変えないため）。
- ⚠️ **`schema_dto.rs` / `schema/current.json` を触るので、実装時に gse-dataset との parity check が要る**
  （`docs/development-guidelines.md` §10 / `/finish-task` Step 3）。
- ⚠️ **`capabilities` は「送出元がある」ことしか意味しない。** ★ 送出元が実在しても
  **バグで一度も呼ばれない**可能性は残る。→ **`app_version` を併記して事後追跡できるようにしてある**。
- ★ **副産物**: D2 の送出元ベース判定は、`§5.2` が抱えていた未解決の問い
  「`ime_nav` / `ime_abandon` は **macOS で常時ゼロ。実装バグか仕様か未確定**」を
  **構造的に決着させる**（capabilities に無ければ仕様、あってゼロならバグ）。
- ⚠️ **本 ADR が無いまま ADR-012 の次コホートを収集すると、§Context-1 の失敗が 3 件目として再生産される。**
  ★ **2 本の ADR は一体で読むこと。**

---

## Migration

1. ★ **実施済み（2026-08-19）**: 本 ADR を Accepted で凍結した。**コード変更ゼロ。**
2. ★ **実施済み（2026-08-19・リブート前の停止期間）**: D1 / D2 / D4 を additive に実装した。
   - `src-tauri/src/capabilities.rs`（**新規**・`#[cfg]` を反映した送出元ベースの宣言表）
   - `logger.rs`: `meta` に `app_version` / `capabilities` を**末尾に**追記、
     `LogEntry::StarveWindow` 新設、`HookHealth` に `dropped_delta` を併記
   - `input/liveness.rs`: `MicroStarveWindow`（**純関数**・`n_lt30 == 0` の窓は出さない）
   - `lib.rs`: 窓集計を **`continue` より前**に配線（⚠️ 後ろだと窓がまるごと消える）、
     `dropped_at_last_line` を `prev_dropped` と**分けて**保持（⚠️ 流用すると「前回行からの差分」にならない）
   - ⚠️★★★ **`emit_schema` の diff で `dropped_delta` が `required` に入ったのを検出し、
     DTO を `Option` に直した** —— そのままだと**旧ログが schema 検証に落ち**、
     本 ADR の「`required` を増やさないので旧ログは読めるまま」に反していた。
   - ★ 検証: `cargo test --workspace` 緑（407）/ ゴールデン **6 本 byte-equal** /
     `HMM_VERSION` は **`0.4.0` 据え置き**（additive の裏付け）/ schema parity 緑 /
     `validate_blocks.py --selftest` 緑。
   ~~⚠️ **未了（G1 完了後）**~~
   ★ acceptance は **D3 の 5 テスト**（網羅 / OS 対 / **仕様の回帰**（`n_lt30==0` 非出力・`dropped_delta` の差分・**`hook_health` 意味論の不変**）/ **過大申告の逆アサート** / schema parity）を必須とする。
2b. ★ **実施済み（2026-08-20）**: **同意文書・participant-guide の記録項目表**に
   `starve_window`（「1 分ごとの**短い中断**の回数と合計時間」・⚠️ 0 回の分は記録しない）と
   `app_version`（「アプリの版」）を追記し、**配布済みの電子同意フォームと突合した**（D5）。
   - ★ **GAS の自己申告ではなく、被験者が見る公開 viewform を外から読んで確認した**
     （新文言 4 種が出て旧文言が消えたことを**対照つき**で実測）。
   - ★ 既存回答 6 件は不変。提出経路も生存確認済み（`onG1ConsentSubmit` がトリガー経由で完了）。
   - 一次記録: `.steering/20260820-consent-form-live-sync/`
2c. ★ **実施済み（2026-08-21）**: ⚠️★★★ **`starve_window` の実発火を初めて実測した**（陽性対照）。
   ★ 本 ADR の D1 が `starve_window` を `threshold_gated` に置いた以上、**0 行は「判定不能」としか読めない**
   —— つまり ⚠️ **計器が壊れていても気づけない**。→ ★ 配線の鎖（フック → `CALLBACK_COUNT` →
   `liveness::step` → `MicroStarveWindow::tick` → `LogEntry::StarveWindow` → `logger` → NDJSON）が
   **両端まで通っていること**を実機で確認した。
   - 条件: Windows 11 / `meta.g1_mode = "marker"`（**配布形と同じ経路**）/ `app_version = 0.1.27`
   - 実測: `starve_window` **1 行**（`win_ms = 60000` / `n_lt30 = 3` / `sum_lt30_ms = 21000`）、
     `hook_health` **0 行**（★ 30 秒に達していないので期待どおり ＝ **2 トラックが閾値で分割されている**実証）
   - 一次記録: `.steering/20260821-precollection-close-and-x-axis/t0-result.md`
     （⚠️ **生 NDJSON は repo に置かない**・値のみ転記）
   - ⚠️ `n_lt30 = 3` に対し操作は 5 回。★ **下側に偏るのは仕様**（1 Hz 分解能・所見 B）。
3. ★ **実施済み（2026-08-21）**: `docs/development-guidelines.md` **§10.5**（新設・判定表と使い方の SSOT）と
   `docs/architecture/personalization-and-online-learning.md §5.2`（表の冒頭に警告）に
   「**収集済み信号を使う解析は、最初に `capabilities` を機械判定する**」を追記した。
4. ★ **実施済み（2026-08-21）**: 判定を**コード**にした。
   - `scripts/capabilities_gate.py`（**新規**）—— 3 群 ＋「表に無い」＋ **旧ログ**（`capabilities` キー欠如）
     ＋ ⚠️★★★ **`MIXED`**（コホート内で宣言が食い違う＝過去 2 件の失敗様式）を判定する。
     `preflight()` で Python から、CLI で `run.sh` から呼べる。**exit code で止まる**。
   - `experiments/_template/`（**新規**）—— `run.sh` の **Step 0** がこのゲートである。
     `docs/experiment-tracking.md` のディレクトリ規約・再現性チェックリストにも反映した。
   - `scripts/tests/test_capabilities_gate.py`（**新規**・20 テスト）＋ `--self-test`（空振り検査）。
   - ⚠️★★ **CI に載せた**（`.github/workflows/ci.yml` の `frontend-check`）——
     ★ 本 ADR の診断が「規約は書いてあったのに適用しなかった」である以上、
     **検査が空振りしていないことまで機械が見る**必要がある。
   - ⚠️ **実ログで検算した**（2026-08-21）: 新ログ（v0.1.27）は `key=PRESENT` /
     `starve_window=PRESENT` / `probe_assignment=UNDECIDABLE`（exit 3）、
     旧ログ（2026-08-10）は `key=PRESENT` / `starve_window=INSTRUMENT_ABSENT`（exit 4）、
     新旧混在は `MIXED`（exit 6）。★ **空振りしていない。**
5. ★ **次コホートの収集開始前**に 2〜4 が終わっていることを確認する（D5）。
   ⚠️ **終わっていなければ収集を始めない。**
   → ★ **2026-08-21 時点で 2 / 2b / 2c / 3 / 4 はすべて完了**している。
