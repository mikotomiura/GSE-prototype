# 設計 (v1) — 非打鍵タスクの観測空間を「実測で」決める

> ⚠️★★★ **破棄済み。現行の設計は `design.md`（v2）である。**
> ★ `/reimagine` で v2 と比較し **v2 を採用**した（比較は `design-comparison.md`）。
> ⚠️ **本ファイルには v2 が却下した案が含まれる**（例: **全セッションの画面録画**・
> θ を dev が事前登録で選ぶ・`capabilities` の手書き列挙）。**参照して実装しないこと。**

> ⚠️★★★ **本タスクは設計文書だけを作る。`src-tauri/` のコードは 1 バイトも変えない。**
> ★ 「実装」と書かれた箇所はすべて **別タスク**の対象であり、本タスクでは**着手しない**。

## 実装アプローチ

### 全体像 — 1 本の線（上流 → 下流）

```
  [上流] ADR-012  形成的研究トラック          [下流] ADR-013  収集仕様の自己記述性
  「何を載せるか」を実測で決める        →     「それを載せる仕様」を additive に決める
  gate: 募集（D-5）                            gate: G1 完了（D-12）
  計器: 専用の別計測器（D-4）                  計器: GSE 本体（実装は G1 後）
```

⚠️★★★ **2 本は独立に進む。** 片方の gate がもう片方を人質に取らない（D-8）。

### ★ 中核の論法（★ これが成果物の良し悪しを決める）

**ADR-008 D1** は「superset は dev / 研究者が決める。ML に委譲できない」と決めたが、
⚠️ **「どう決めるか」を 1 行も書いていない。** 本設計はその空白を次の 3 段で埋める:

| 段 | 誰が決めるか | ⚠️ 何を禁じるか |
|---|---|---|
| 1. **候補チャネルの列挙** | ★ **人（dev / 研究者）が、実データを見る前に凍結する** | ⚠️ 「あると便利そうだから全部」を禁じる。★ ゼロから起こさず既存表から起こす |
| 2. **候補の順位と採否** | ★ **実測（沈黙被覆率）が決める** | ⚠️ **dev の推測が決めることを禁じる**（＝発意の核心） |
| 3. **推論への配線** | ★ 人が決める（G1 判定後・ADR-011 D4） | ⚠️ 学習器に選ばせることを禁じる |

★ **段 1 と段 3 は人が持つので ADR-008 D1 を守っている。段 2 だけを実測に委ねる。**
⚠️ これは「全部集めてから学習器に選ばせる」（前 handoff §1-B の禁止）とは**別物**である
—— ★ **学習器を一切当てない**（記述統計のみ・D-9）。

---

## 上流: ADR-012 — 形成的研究トラック

### 1. 主要指標 = 沈黙被覆率（D-1）

**定義**（★ `docs/glossary.md` に登録する）:

```
沈黙区間     := 打鍵イベントが 1 つも無い連続時間区間で、長さ ≥ 30 秒のもの
             （★ 閾値 30 秒は liveness.rs:64 log_after_ms と揃える。
               ⚠️ 揃える理由は「既存トラックと同じ土俵で読めるようにする」ためであって、
               30 秒に理論的な意味があるからではない）

沈黙被覆率(C) := Σ (チャネル集合 C のイベントで覆われた沈黙時間) / Σ (沈黙時間)
             ★ 分母から打鍵の時間を定義上除いている ＝ 「頻度が高い操作」を選ぶと
               打鍵に戻るという退行が構造的に起きない（D-1）

限界寄与(c)   := 沈黙被覆率(C) − 沈黙被覆率(C \ {c})
             ★ そのチャネルを抜いたときの被覆率の低下
```

⚠️ **「覆われた」の定義を先に凍結する**: チャネル `c` のイベント時刻 `t` は、
`[t − w, t + w]` を覆うものとする（`w` は事前登録で固定。★ 実データを見て変えない）。

### 2. 候補チャネルの列挙（★ 段 1 = 人が凍結する）

⚠️★★★ **ゼロから起こさない**（handoff §4 逐語）。次の 2 つの既存表から起こす:

- `docs/architecture/domain-adapter-boundary.md` §Adapter A / §Adapter B / §Adapter C
- `docs/architecture/personalization-and-online-learning.md` §5.2 (a)

| # | 候補チャネル | 出所 | ⚠️ content-free か（D-2） |
|---|---|---|---|
| 1 | **ポインタ移動**（距離・速度のバケット。座標は保存しない） | §5.2 (a)「ポインタ動態」/ `§8` T2 | ★ 可（座標を捨てて量だけ持つ） |
| 2 | **ポインタボタン押下**（回数・種別なし） | §Adapter C | ★ 可 |
| 3 | **ホイール / スクロール** | §Adapter A「scroll」（保留扱い） | ★ 可 |
| 4 | **フォーカス遷移の回数**（★ **識別子を保存しない**） | §Adapter A「editor focus・return」/ §5.2 (a) | ★ 可（⚠️ 識別子を持てば [P117] の穴） |
| 5 | **打鍵**（比較基線・T0） | 現行 F1/F3/F4/F5/F6 | ★ 可（既存） |
| 6 | **入力皆無**（OS 最終入力時刻が動かない時間） | `liveness.rs:86-103` の `step()` | ★ 可（★ ADR-011 D1 の 2 分割をそのまま流用） |

⚠️ **列挙から意図的に外したもの**（★ 外した記録も残す）:

| 外したもの | ⚠️ 理由 |
|---|---|
| アプリ識別子 / ウィンドウタイトル / URL / プロジェクト名 | ★ `data-privacy` 禁止事項。**[P117] が落ちた穴そのもの**（D-2） |
| アプリ内の操作種別（タイムライン操作 / パラメータ調整 等） | ★ **プラグイン方式（D-2 案 B）が要る。次段**。⚠️ 1〜6 で被覆率が足りないと**実測で分かってから**進む |
| 画面の内容・スクリーンショット | ★ 参照チャネル（D-3）は**研究者限りで破棄**するため、**観測チャネルではない** |

### 3. content-free の保ち方（D-2）— 観測と宣言を融合しない

```
  観測チャネル（1〜6）  ──→  沈黙被覆率の計算に使う          ★ アプリ識別子ゼロ
  宣言（ブロック単位）  ──→  「どのタスクの被覆率か」のラベル  ★ routing のみ
  参照チャネル（録画）  ──→  顕著性の解釈・コード化           ⚠️ コード化直後に破棄
```

⚠️★★★ **3 つを融合して「真の操作種別」を作らない。**
★ 根拠は `ADR-010 D3` 逐語「**宣言は routing のみ、観測は `scope_fit` のみに使う。
融合して「真の task_kind」を作らない**」の写しである（**新しい原則を持ち込まない**）。

### 4. セッション設計（D-5 / D-7）

```text
[warm-up]  →  [A: 非打鍵タスク]  →  [B: 短い論述]  →  [A': 非打鍵タスク]
  破棄        （その人の普段の作業）   （★ タスク対比）    （復帰の確認）
```

- ★ **順序は被験者間で counterbalance**（B を常に中央に置かない）——`§2.3` と同型。
- ★ **warm-up は解析から破棄**する。
- ★ **境界をまたぐ窓は解析から除外**する。
- ⚠️ **要因を掛け合わせない**（`§2.8` 逐語）。論述ブロックは**セッションあたり 1 本**。
- ★ block 境界は既知の時刻として記録する（**新しいイベント種別を作らない**）。

### 5. 合格基準（D-9）★ 実データを見る前に `preregistration.md` で凍結する

| 判定 | 条件 |
|---|---|
| **主基準** | 候補チャネル集合の**合同**沈黙被覆率が **n 名全員**で閾値 `θ` を超える |
| **副基準（必須併記）** | 各チャネルの **null 被覆率**（そのチャネル自身のイベント率から期待される被覆率）を併記する |
| **採否** | チャネル `c` を superset に入れるのは **限界寄与(c) ≥ δ** かつ **null 超過**のとき |
| **Stop** | 合同被覆率が閾値未満 → ⚠️ **「情報が無かった」とは書かない。「この候補集合では覆えなかった」と書く**（→ D-2 案 B へ） |
| **除外** | warm-up / block 境界をまたぐ窓 / 沈黙区間 <20 本の被験者 |

⚠️★★★ **副基準を必須にする理由**: [V83] 逐語 **`We cannot replicate models that significantly
improve over the baseline of a majority classifier.`** ＋ `§8` の 2026-08-16 決定
「勝ち幅は 2 つの基線に対して報告する」。★ これが無いと **[P117] の「偶然 +0.07」を
「有望」と読む誤り**が形式を変えて再発する。

### 6. 計測器（D-4）— 専用の別計測器

| 項目 | 決定 |
|---|---|
| 形態 | ★ **standalone**（GSE 本体と別プロセス・別バイナリ） |
| 出力 | ★ **Layer 2 `EventEnvelope` 互換**（`domain-adapter-boundary.md §Layer 2`）→ 後で本体へ additive に移植できる |
| 品質要求 | ★ **使い捨ての測定器**。本番品質を要求しない |
| ⚠️ 禁止 | `src-tauri/` に触れない・`HMM_VERSION` を動かさない・ゴールデン/schema に触れない |
| ★ 必須 | ⚠️ **自分自身に `capabilities` を刻む**（＝ ADR-013 と同じ規律を最初から満たす）。★ 今回の失敗を計測器自身が繰り返さないため |

⚠️ **実装は本タスクの Out。** 本タスクは仕様まで。

---

## 下流: ADR-013 — 収集仕様の自己記述性

### 7. 穴 C: `capabilities` の刻印（★ 最優先）

**現状**（実測・`src-tauri/src/logger.rs:1090-1104`）:

```json
{"type":"meta","session_start":1720000000000,"hmm_version":"0.4.0"}
{"type":"meta","session_start":1720000000000,"hmm_version":"0.4.0","g1_mode":"..."}
```

**案（additive）**:

```json
{"type":"meta","session_start":1720000000000,"hmm_version":"0.4.0",
 "app_version":"0.x.y",
 "capabilities":["key","feat","paste","ime","hook_health","starve_window","self_marker","probe"]}
```

★★★ **解析側の機械判定**（★ これが穴 C の一般形への答え）:

| `capabilities` に含まれる | 該当行の数 | ★ 結論 |
|---|---|---|
| ✅ | 0 行 | ★ **信号が無かった**（測れて、無かった） |
| ✅ | ≥1 行 | ★ 通常 |
| ❌ | 0 行 | ⚠️ **計器が無かった**（測っていない）← ★ 今回の失敗がここ |
| ❌ | ≥1 行 | ⚠️ **`capabilities` の宣言がバグっている** → `app_version` で追跡する |

⚠️ **`hmm_version` では代用できない**（★ 実測: HMM の版であって「何を記録できるか」ではない）。

### 8. 穴 A: micro 帯（★ `hook_health` の意味論を 1 文字も変えない）

**案（additive な別行種）**:

```json
{"type":"starve_window","t":1720000060000,"win_ms":60000,"n_lt30":7,"sum_lt30_ms":4200}
```

- ★ **`hook_health` の出力条件（`lib.rs:2924`）を変えない** →
  ⚠️★★★ **≥30 秒トラックの旧ログ（G1 を含む）と新ログが同一意味論のまま比較できる。**
  ★ **ADR-011 の探索トラックが再計算にならない**（`env.md` の依存表を壊さない）。
- ★ ログ量は 1Hz 案の **1/60**。
- ⚠️ **失うもの**: 個々の micro 沈黙の**位置**（本数と合計のみ残る）。
  ★ 「micro 帯が何割あるか」＝投資判断の材料としては足りる。

### 9. 穴 B: 累積カウンタ

```json
{"type":"hook_health","t":...,"alive":true,"starved_ms":0,"rehook":false,
 "dropped":42,"dropped_delta":3}
```

- ★ `dropped`（累積）は**そのまま残す**（非破壊・additive）。
- ★ **実装は搬送 1 行で済む**: `lib.rs:2883-2890` に**既に `prev_dropped` があり**、
  差分は `dropped_now` として `tracing` に出ている（実測）。それを `LogEntry::HookHealth` に載せるだけ。
- ⚠️ **改名（`dropped_total`）は採らない**（breaking・`validate_blocks.py` 等の同時修正が要る）。

### 10. 入れないと決めるもの（★ 明示的に record する — D-10）

| 入れないもの | ⚠️ 理由 |
|---|---|
| 非打鍵モダリティの信号本体を **GSE 本体へ** | ★ **形成的研究の結論待ち**。⚠️ 今入れると **ADR-008 D1 が禁じた「dev の推測で superset を決める」** |
| 1Hz の全 tick 記録 | ⚠️ ログ量・バッテリ。★ 値の大半が 0。窓集計で足りる |
| `dropped` の改名 | ⚠️ breaking change。★ 併記で誤読は消える |
| アプリ識別子・ウィンドウタイトル・URL | ⚠️ `data-privacy` 禁止事項・**[P117] の穴** |

---

## 変更対象

### 新規作成するファイル

- `docs/adr/ADR-012-nonkeystroke-observation-formative-track.md` — 上流の決定
- `docs/adr/ADR-013-collection-self-description.md` — 下流の決定
- `experiments/20260819-nonkeystroke-silence-coverage/preregistration.md` — 合格基準の事前凍結
- `experiments/20260819-nonkeystroke-silence-coverage/README.md` — 実験の目的と Stop 条件
- `.steering/_handoff/next-session-prompt-g1-cohort-silence-decomposition.md` — ★ **G1 収集完了後にすぐ実走するための引き継ぎ**（ADR-011 Migration 3b）
- `.steering/_handoff/next-session-prompt-nonkeystroke-instrument-build.md` — 別計測器の実装タスクへの引き継ぎ

### 修正するファイル

- `docs/research-positioning.md` — **§8 段別表の T3 行「降格先」列のみ**（D-11）
- `docs/adr/README.md` — ADR-012 / ADR-013 を索引に追加
- `docs/glossary.md` — 新規用語 4 件
- `docs/architecture/domain-adapter-boundary.md` — §Adapter C に ADR-012 へのリンクを追記
- `docs/architecture/personalization-and-online-learning.md` — §5.2 の末尾に ADR-013 へのリンクを追記

### ⚠️ 変更しないファイル（★ 受け入れ条件で機械確認する）

- `src-tauri/` **すべて**（G1 実施中）／`src-tauri/schema/current.json`／`schema_dto.rs`
- `docs/research-positioning.md` の **§8 T1/T2 行**・**§9 A-Q3**
- `docs/preregistration-v0.3.md`（Phase1 の契約）

## 影響範囲

| 影響先 | 内容 | 対処 |
|---|---|---|
| G1（実施中） | ★ **影響ゼロ**（コード変更なし） | 受け入れ条件で機械確認 |
| ADR-011 の探索トラック | ★ **影響ゼロ**（`hook_health` の意味論を変えないため） | ADR-013 の Consequences に明記 |
| `data-privacy` Skill | ⚠️ **拡張対象**（別計測器・画面録画・削除要求経路） | ADR-012 の Consequences に起票（★ Skill の改訂は別タスク） |
| 募集リソース | ⚠️ **G1 の残り 2 名と競合する** | D-5 の選定規則で「降りる」を許容 |

## 既存パターンとの整合性

| 本設計 | ならった既存パターン |
|---|---|
| 観測と宣言を融合しない | **ADR-010 D3**（宣言は routing のみ・観測は `scope_fit` のみ） |
| 同一セッション内に 2 タスク | `task-adaptation-and-scope-gating.md §2.2` **C-2** |
| 全員一致 ＋ 件数の床 | `§8` GATE3（全員 >0.55）／PreReg-5（≥20 件/人・[V28][V27]） |
| 2 基線に対して報告 | `§8` 2026-08-16 決定（多数派分類器 ＋ T0 baseline・[V83]） |
| コード変更ゼロで実験トラックを開く | **ADR-011 D4** |
| additive schema | **ADR-005** |
| 実データを見る前に凍結 | `reproducibility-discipline` ／ ADR-011 Migration 1 |

## テスト戦略

★ **コードを変えないので、テストは「変えていないことの証明」である。**

| 検査 | コマンド | 期待 |
|---|---|---|
| 単体 | `cd src-tauri && cargo test --workspace` | 緑 |
| 回帰（ゴールデン） | `cd src-tauri && cargo run --bin gse-replay -- tests/fixtures/minimal.ndjson --snapshot tests/snapshots/minimal.json` | exit 0 |
| schema drift | `python scripts/check_schema_parity.py` | exit 0 |
| コード無変更 | `git diff --stat -- src-tauri` | ★ **空** |
| T1/T2 不変 | `git diff docs/research-positioning.md` | ★ T3 行以外に差分なし |
| 禁止語 | `grep -nE '効果があ\|精度が上が\|有効性' docs/adr/ADR-012*.md docs/adr/ADR-013*.md experiments/*/preregistration.md` | ★ **ヒット 0** |

## ロールバック計画

★ ドキュメントのみなので `git revert` で完全に戻る。
⚠️ **ただし `§8` T3 行の改訂だけは研究者決定の記録**なので、
戻す場合は **ADR-012 を Superseded にしてから**戻すこと（★ 決定だけが宙に浮かないようにする）。
