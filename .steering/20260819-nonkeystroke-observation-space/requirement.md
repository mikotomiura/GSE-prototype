# 非打鍵タスクの観測空間を「実測で」決める（設計のみ・コード変更ゼロ）

> ⚠️★★★ **本タスクは設計だけを確定する。`src-tauri/` のコードは 1 バイトも変えない。**
> 理由: **G1 は実施中**（確証標本 1/3 名・`experiments/20260801-controlled-friction-task/data.md:4`）。
> 実施中に記録仕様を変えるとブロック間の比較可能性が壊れ、
> `preregistration.md §3.6` がブロックの事後除外を禁じているため**回復不能**になる。

## 背景

### 発意（2026-08-19・研究者本人・⚠️ 逐語。誤字も直さない）

```
以前の私のユーザー検証でのPhase1以降で書くタスクでの適用などをさせたい都市、現在それに関して
の各タスクでの適用の方を作成しているが、打鍵での推論のみではまた同じ形になるため、打鍵以外
(各タスクでは具体的に主に行う操作)の内容などを推論の素材として入力させるとよいのでは？また
その入力させる内容などを決定させるためにその顕著としてでるないようの平均などを求めるためにそ
のタスク(普段の作業)を抽出させるためのそのタスクに適した作業を普段行っているユーザーのデータ
抽出検証を行うべきではないか
```

要旨は 3 つ:

1. ⚠️ **打鍵だけで推論すると、タスクを変えても「また同じ形」になる。**
2. ★ 各タスクで **実際に主に行われている操作** を推論の素材にすべきではないか。
3. ★★★ **「何を入れるか」は dev の推測ではなく、そのタスクを普段行っているユーザーから
   データを抽出して *実測で* 決めるべきではないか。**

### なぜ今か（★ 2026-08-19 に実証された 2 つの失敗が動機）

| # | 実測された失敗 | 出所 |
|---|---|---|
| 1 | ⚠️★★★ **計器がコホートを跨げなかった** —— Phase1（P010–P014・63 ファイル）に `hook_health` 行が **1 行も無い**。記録期間 2026-07-04〜07-24 に対し `liveness.rs` の追加は **2026-08-09**（＝収集の 16 日後） | `experiments/20260819-silence-presence-decomposition/notes.md §1` |
| 2 | ⚠️ **同型が既に 2 件目**（1 件目は Tier 0 の `keys`/`bs_keys`・配線 2026-08-16） | 同 `§1.1` |
| 3 | ★ それでも model-free の層は答えを出した: **適格性ゲートが落とす 235 窓は時間の 84.3% が ≥30 秒の沈黙**（`1–99` 打鍵帯が **87.0%** で最大） | 同 `§2.2` |

→ ★★★ **「打鍵が薄い窓を測る」とは「長い沈黙の中身を割る」ことに他ならない**が、**中身は不明のまま**。
⚠️★★★ **打鍵中心のタスク（論述）ですらこうである。動画編集・スライド・CAD では打鍵がさらに薄い。
★ 同じ設計のまま進めば同じ結果になる。**

### 収集仕様に見つかった 3 つの穴（★ 統合した下流課題・すべて本タスクで実測確認済み）

| # | 穴 | 実測の根拠（`file:line`） |
|---|---|---|
| **A** | ⚠️ **30 秒未満の非打鍵は 1 行も残らない** | `src-tauri/src/lib.rs:2924`（`if health == prev_health && !rehook { continue; }`）＋ `src-tauri/src/input/liveness.rs:64`（`log_after_ms: 30_000`） |
| **B** | ⚠️ **`dropped` は累積カウンタ**なのに解析側は「この区間で落ちた」と読む | `src-tauri/src/input/hook.rs:140`（`EVENTS_DROPPED: AtomicU64`）を `src-tauri/src/lib.rs:2883` が読み `:2965` でそのまま搬送 |
| **C** | ⚠️★★★ **計器の有無を「その計器が出す行の有無」で判定できない** | `lib.rs:2924` は状態変化時にしか出さないので、**計器が動いていて 30 秒未満しか starve しなかったセッションも 0 行**になる |

★ **C の一般形が下流課題の核心**: **「信号が無い」と「計器が無い」をログだけから区別できる形で残す。**

## ⚠️★★★ 最初に固定した切り分け（★ これを外すと既決違反に見える）

| 既決 | ★ なぜ当たらないか |
|---|---|
| `research-positioning.md §9` **A-Q3 解除条件①**（T2 以上について *利得があった* と書くには検出力の算術が要る） | ★ **形成的研究は「利得があった」と主張しない。** 測定法の開発（measurement development）であって効果推定ではない。⚠️ **ただし「効果が出た/精度が上がる」と一言でも書いた瞬間に発動する**（→ 受け入れ条件で禁止語に指定） |
| `§8` **文献の帯**（[P118] +0.9pt / [P120] 切替単独 ≈ 全部入り / [P117] 偶然 +0.07 / [V84] +15%） | ★ これらはすべて **「精度が上がるか」** の文献。本タスクの問いは **「そもそも測れるか」**（T3 は現行 sensing 層で**測定不能**と決まっている）。★ **同じ土俵ではない** |

⚠️★★★ **逆に、以下は本当に当たるので回避しない（設計に組み込む）**:

| 既決 | ⚠️ 何が問題か |
|---|---|
| **[P117] が否決された理由** | ⚠️ **アプリ識別子→カテゴリ写像に依存**していた（GSE が `data-privacy` で自ら禁じた情報）。★★★ 「そのタスクで主に行う操作」を識別する設計は**ここに正面からぶつかる** → **D-2 で裁いた** |
| `domain-adapter-boundary.md §Adapter C` 逐語 | 「長い無打鍵が正常・試行錯誤とデッドループの境界が**作品文脈依存**・**OS レベルイベントだけでは意味不足**・**プラグイン方式が必要になりうる**」「**まず一アプリに限定した feasibility study**」 |
| **ADR-008 D1** 逐語 | 「**何を集めるか（superset）は dev / 研究者が決める。ML に委譲できない**」 ← ★ **repo は「どう決めるか」を書いていない。本タスクがその空白を埋める** |
| 前 handoff §1-B | 「⚠️ superset を決めずに『全部集めてから学習器に選ばせる』も**やらない**」 ← ★ 形成的研究はこの禁止と**整合する**（先に実測で絞るため） |

## ゴール

**次の 3 つがすべて揃った状態で、`src-tauri/` に 1 バイトの変更も無いこと。**

1. **ADR-012（形成的研究トラック）** —— 「打鍵以外の何を推論の素材にするか」を
   **dev の推測ではなく実測で決める**手続きを Accepted で凍結する。`§8` 段別表の **T3 行の降格先列**を改める。
2. **ADR-013（収集仕様の自己記述性）** —— 穴 A/B/C を additive に閉じる仕様を Accepted で凍結する。
   ⚠️ **入れない判断も明示的に record する。**
3. **形成的研究の事前登録（`experiments/…/preregistration.md`）** ——
   実データを見る前に、合格基準・除外規則・Stop 条件を凍結する。

## スコープ

### 含むもの

- 形成的研究（上流）の設計: 顕著性の定義 / content-free の保ち方 / 参照チャネル / モダリティ選定規則 /
  取得手段 / 募集・同意・privacy 境界 / n と期間の下限 / 合格基準
- 収集仕様（下流）の設計: `capabilities` の刻印 / micro 帯 / 累積カウンタ / 入れない判断 / 実装時期
- `docs/research-positioning.md §8` 段別表の **T3 行・降格先列のみ**の改訂
- `docs/glossary.md` への新規用語の追記

### 含まないもの（Out）

- ⚠️★★★ **`src-tauri/` のコード変更**（G1 実施中・§5-1）。`schema_dto.rs` / `schema/current.json` も触らない
- ⚠️ **`§8` 段別表の T1/T2 行**（ADR-011 D2 で据え置きと決定済み・**別の段の話である**）
- ⚠️ **`§9` A-Q3 の解除条件**（不変）／**適格性ゲート `keydown ≥ 100`**（ADR-011 D3・G1 で凍結中）
- ⚠️ **確証核 L0**（1 ミリも動かさない）
- ⚠️ **モダリティを一括で始めること**（Adapter C 逐語「まず一アプリに限定」）
- ⚠️ **形成的研究の実施そのもの**（本タスクは設計まで。実施は募集後の別タスク）
- ⚠️ **別計測器の実装**（設計まで。実装は別タスク）
- ⚠️ **「効果があった / 精度が上がる」という主張**（★ 一言でも書けば A-Q3 が発動する）

## 受け入れ条件

- [ ] `git diff --stat` に `src-tauri/` のファイルが **1 つも現れない**
- [ ] `cd src-tauri && cargo test --workspace` が緑（★ 無変更なので当然だが、**変えていないことの証明**として回す）
- [ ] `cd src-tauri && cargo run --bin gse-replay -- tests/fixtures/minimal.ndjson --snapshot tests/snapshots/minimal.json` が exit 0（ゴールデン不変）
- [ ] `HMM_VERSION` が `0.4.0` のまま（`grep -n 'HMM_VERSION' src-tauri/src/analysis/engine.rs`）
- [ ] `python scripts/check_schema_parity.py` が exit 0（schema drift ゼロ）
- [ ] ADR-012 / ADR-013 が `docs/adr/README.md` の索引に載っている
- [ ] `docs/research-positioning.md §8` の **T1/T2 行が 1 文字も変わっていない**（`git diff` で確認）
- [ ] ★ **成果物の全文に「効果」「精度が上がる」「有効性」を利得の意味で使った箇所が無い**
      （`grep -nE '効果があ|精度が上が|有効性' docs/adr/ADR-012*.md docs/adr/ADR-013*.md experiments/*/preregistration.md`）
- [ ] 形成的研究の `preregistration.md` に **合格基準・除外規則・Stop 条件**が実データを見る前に書かれている
- [ ] `docs/glossary.md` に新規用語（沈黙被覆率 / 限界寄与 / 形成的研究 / 計器の自己記述）が定義されている
- [ ] `.steering/20260819-nonkeystroke-observation-space/decisions.md` に D-0〜D-12 が記録されている

## 関連ドキュメント

- `docs/architecture/domain-adapter-boundary.md` §Adapter B / §Adapter C（★ **取得候補イベントの既存列挙**・ゼロから起こさない）
- `experiments/20260819-silence-presence-decomposition/notes.md` §1 / §2 / §3
- `docs/research-positioning.md` §8 段別表（`:537-547` 付近）/ §9 A-Q3
- `docs/adr/ADR-011-low-typing-window-track.md` D2 / D5 / §Consequences
- `docs/adr/ADR-008-online-learning-boundary.md` D1 / D7 / §Consequences
- `docs/adr/ADR-010-task-scope-gating.md` D3（宣言と観測の役割分離）
- `docs/architecture/task-adaptation-and-scope-gating.md` §2.2–§2.6（block 設計・ラベルの 3 供給層）
- `docs/architecture/personalization-and-online-learning.md` §5.2 / §5.4 / §10
- `.claude/skills/data-privacy/SKILL.md` / `docs/development-guidelines.md` §10
- `experiments/20260819-silence-presence-decomposition/env.md`（★「依存している `src-tauri/` の実装」表）

## 運用メモ

- **/reimagine 適用**: Yes
- **理由**: 設計判断が中心であり、複数案が考えられて最良案が自明でない（handoff §9-2 の指示）。
  特に **content-free の保ち方**（D-2）と **合格基準の形**（D-9）は、初回案を破棄して
  再生成した案と比較する価値がある。
