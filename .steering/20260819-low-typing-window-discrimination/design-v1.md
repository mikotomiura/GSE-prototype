# 設計

## 0. ⚠️★★★ grill の言い回しからの訂正（着手前に潰した設計欠陥）

grill の合格基準は「**T0 = 沈黙長のみ**」と書かれていたが、**この定式化は循環する**。

- アウトカムは「沈黙ギャップが H までに**終わる**か」＝ **ギャップ長そのもの**である。
- ギャップ開始時点では、全ギャップの経過沈黙長は同一（分散ゼロ）で予測子にならない。
- 途中時点の経過長を使うと、**アウトカムを特徴量に入れている**ことになる。

→ ★ `docs/research-positioning.md:539` の T0 定義（逐語「**打鍵動態 F1/F3/F4/F5/F6 ＋
`keys` / `bs_keys` / `paste`（記録のみ）**」）に戻し、**沈黙ギャップ直前の窓**で計算する。
これなら循環せず、`§8` が [V83] 由来で義務化した 2 基線要求もそのまま満たせる。

| 記号 | 中身 | 由来 |
|---|---|---|
| **基線 (a)** | 多数派分類器 | `§8` 逐語 [V83] `We cannot replicate models that significantly improve over the baseline of a majority classifier.` |
| **基線 (b) = T0** | 直前窓の `f1` / `f3` / `f4` / `f5` / `f6` / `keys` / `bs_keys` | `§8` T0 行 `:539` |
| **提案 = T0 + presence** | 上記 ＋ `suspect_by_L`（在席×非打鍵の指標） | 本タスクが作る ablation |

## 1. 実装アプローチ

### 1.1 なぜオフライン再解析か

`decisions.md` D-2 のとおり、**本番推論経路に触れない**ことが G1 ゲートを回避する唯一の道である
（`personalization-and-online-learning.md:786` 逐語「読む実装へ進む前に G1 の判定を通すこと」／
G1 は `data.md:4` のとおり 1/3 名）。`experiments/` での再解析は `cv-gate-null` /
`expression-power` が確立済みの経路であり、`src-tauri/` は 1 バイトも変えない。

### 1.2 `presence_ratio` をどう再構成するか（★ 本設計の核）

`input/liveness.rs:86-103` の `step()` は純関数で、次の 3 分岐しか持たない:

| 条件 | 挙動 |
|---|---|
| `!session_active \|\| hook_event_seen`（＝打鍵が来た） | `starved_ms = 0` に**リセット** |
| `!system_input_seen`（＝OS の最終入力時刻が動かない） | `prev` をそのまま返す＝**凍結** |
| それ以外（OS は入力を見たが打鍵は無い） | `starved_ms += tick_ms`（**加算**） |

→ ★★★ **`starved_ms` は「沈黙ギャップ内で入力デバイスに触れていた累積時間」そのものである。**
打鍵でリセットされるので、**各ギャップは 0 から始まる**（＝ギャップ間で汚染しない）。

`lib.rs:2951-2956` の復帰行は `peak_starved_ms`（そのエピソードの最大値）を載せる:

```text
let reported_starved_ms = if health == Ok { peak_starved_ms } else { starv.starved_ms };
```

→ **ギャップを閉じる `alive:true` 行の `starved_ms` = そのギャップの「在席×非打鍵」累積時間。**

### 1.3 ⚠️ 観測できる範囲（`lib.rs:2923` の間引きが決める）

```text
if health == prev_health && !rehook { continue; }   // 状態変化時のみ出力
```

`Thresholds::default()` は `log_after_ms: 30_000` / `down_after_ms: 120_000`（`liveness.rs:63-66`）。
→ ★ **出る行は 3 種類だけ**:

| 行 | 意味 |
|---|---|
| `alive:true, starved_ms≈30000` | 在席×非打鍵が累積 **30 秒**に達した（Suspect） |
| `alive:false, starved_ms≈120000` | 同 **120 秒**に達した（Down）＋ `rehook:true` |
| `alive:true, starved_ms = peak` | ギャップが**打鍵で閉じた**（復帰・peak を搬送） |

⚠️ **30 秒未満の在席×非打鍵は 1 行も残らない**（`decisions.md` D-7）。

### 1.4 ランドマーク設計（★ 循環と検閲を同時に避ける形）

- **コホート**: 沈黙ギャップの長さ **≥ 60 秒**
- **ランドマーク L = 60 秒**（ギャップ開始からの経過時間）
- **予測子は L 時点までに観測可能なものだけ**
- **アウトカム**: `gap_end ≤ H`（主 H = 3 分 / 副 H = 10 分・`decisions.md` D-6）

⚠️ **なぜ L = 30 秒でないか**: Suspect 行は「累積 30 秒」で出るが、途中に凍結（入力皆無）が
挟まると **経過 30 秒時点ではまだ出ていない**。L = 60 秒なら「最初の 60 秒のうち 30 秒以上を
入力デバイスに触れていたか」が二値として確定する。

→ **`suspect_by_L`** ∈ {0, 1} = ギャップ開始から 60 秒以内に Suspect 行が出たか。

★ 副次的に、ギャップを閉じる行の `peak_starved_ms / gap_duration_ms` を **`presence_ratio`** として
記述統計に出す（⚠️ **これは L 以降の情報を含むので予測子には使わない**）。

## 2. 変更対象

### 新規作成するファイル

```text
experiments/20260819-silence-presence-decomposition/
├── README.md                  # 1 行の目的と実行方法
├── preregistration.md         # ★ 実データを見る前に凍結する（AC-4）
├── data.md                    # 入力の来歴・manifest sha256・限界
├── env.md                     # 実行環境（OS / Python / HMM_VERSION）
├── SEED                       # 乱数 seed（LOSO は決定的だが bootstrap に使う）
├── config.json                # L / H / 閾値 / 除外規則（★ コードに埋めない）
├── run.sh                     # 1 コマンド再現（exit 0 が Done の一部）
├── scripts/
│   ├── extract_gaps.py        # NDJSON → 沈黙ギャップ表
│   ├── analyze.py             # LOSO ablation と 2 基線への勝ち幅
│   ├── selftest.py            # ★ H0 真/偽の合成データで挙動を固定（AC-6）
│   └── leakcheck.py           # ★ ファイル名/絶対パス/ユーザー名の漏洩検査（AC-8）
├── results/                   # 生成物（gaps.json / metrics.json / selftest.json）
└── notes.md                   # 結果と限界（★ 上回らなかった場合も書ける形）
```

### 修正するファイル

- `docs/research-positioning.md` — **§8 の段別表は変更しない**。表の直後に追記のみ:
  - 探索的実験トラックの存在と位置づけ（`decisions.md` D-3）
  - **38.09%（全セッション・617 窓）と 29%（論述限定・360 窓）の併記**（D-9・AC-10）
  - 「個人差か実タスク差かは Phase1 では切り分けられない」（D-10）
- `docs/architecture/personalization-and-online-learning.md` §5.2 — 探索トラックへの参照を追記
- `docs/adr/ADR-010-low-typing-window-track.md` — **新規**（低打鍵窓の扱いと G1 ゲートとの関係）
- `docs/adr/README.md` — ADR-010 を索引に追加（AC-3）
- `docs/glossary.md` — **実施済み**（沈黙ギャップ / 在席×非打鍵 / 入力皆無 / 在席割合 / 打鍵再開 / 探索トラック）

### 削除するファイル

- 無し

## 3. ⚠️ 事前登録で凍結する除外規則（★ 実データを見る前に決める）

| # | 除外 | 理由 |
|---|---|---|
| **E1** | セッション境界をまたぐギャップ | `step()` は `!session_active` で `starved_ms` を 0 に落とす（`liveness.rs:95`）ため、累積が汚染される |
| **E2** | ⚠️★★★ `rehook:true` を含むギャップ | **測定器が 120 秒で介入する**（`lib.rs:2914` `request_reinstall()`）。フックが本当に死んでいた場合、再設置で打鍵記録が**復活**するので、「ギャップが終わった」が**利用者の再開ではなく装置の復旧**でありうる。⚠️ 主 H = 3 分は 120 秒より後なので**直撃する** |
| **E3** | `probe_assignment` / `realtime_label` / `vignette_response` を含むギャップ | プローブ提示が打鍵を止めさせる＝**装置由来の沈黙**。`phase1-calibration-analysis/notes.md:213` が「`probe_assignment` に対応する `realtime_label` が無い」欠測 11 件を報告しており、提示と応答が沈黙に絡む |
| **E4** | `dropped > 0` の行を含むギャップ | ログキュー溢れ＝記録の欠落 |

★ **E2 は感度分析として「含めた版」も併記する**（除外が結論を作っていないことを示すため）。
⚠️ E2 の除外数が対象の 30% を超えたら、**主判定を出さずに「装置の介入と分離できない」を結論にする**。

## 4. 影響範囲

| 対象 | 影響 |
|---|---|
| `src-tauri/` | ★ **無し**（コード変更ゼロ・D-2） |
| ゴールデン 6 本 | ★ **無し**（`HMM_VERSION` 不変・`0.4.0` のまま） |
| `schema_dto.rs` / `schema/current.json` | ★ **無し**（schema parity check は走らせるが差分ゼロが期待値） |
| G1 事前登録 | ★ **無し**（ゲート `keydown ≥ 100` を触らない・D-4） |
| `§8` 段別表 / `§9` A-Q3 | ★ **表と条件は不変**。追記のみ（D-3） |
| 確証核 L0 | ★ **不変**（`§9` A-Q2 と整合） |
| gse-dataset | ★ **無し**（schema 変更が無いので同期不要） |

## 5. 既存パターンとの整合性

| 規約 | 従い方 |
|---|---|
| `reproducibility-discipline` | `SEED` / `data.md`（manifest sha256）/ `env.md`（lockfile・HMM_VERSION）/ `run.sh` 1 コマンド再現 |
| `data-privacy` | ★ NDJSON のファイル名・絶対パス・OS ユーザー名を **repo に 1 つも書かない**。`leakcheck.py` で機械検査（`expression-power` の security-checker M1 と同じ轍を踏まない） |
| `citation-ssot` | [P117]〜[P121] / [V83]〜[V85] は**既登録**。新規の借用手法は無い（LOSO・ロジスティック回帰は標準手法）→ ★ `references.md` に新規登録しない |
| `experiment-tracking` | `experiments/<YYYYMMDD>-<exp-name>/` 命名。`config.json` に閾値を外出し |
| 上流との整合 | ⚠️ 窓の切り方は**再発明しない**。ただし本実験の単位は **5 分窓ではなくギャップ**。→ 参考として「各ギャップがどの 5 分窓に属するか」を併記し、`cv-gate-null` の 617 窓と突き合わせ可能にする |

## 6. テスト戦略

| 種別 | 内容 |
|---|---|
| **自己検査 1（H0 真）** | 在席割合と再開をランダムに独立生成 → **勝ち幅が 0 の近傍に入る**ことを確認。`selftest.py` が exit 非 0 で落とす |
| **自己検査 2（H0 偽）** | 在席割合が再開を強く駆動する合成データ → **勝ち幅が有意に正**になることを確認（検出器が動くことの確認） |
| **自己検査 3（再構成の正しさ）** | 合成 NDJSON（既知の `hook_health` 系列）を `extract_gaps.py` に通し、`peak_starved_ms` と `suspect_by_L` が**手計算値と一致**することを確認 |
| **自己検査 4（決定性）** | `run.sh` を 2 回走らせ `results/metrics.json` が **byte-equal** |
| **漏洩検査** | `leakcheck.py` が `results/` と repo 内の新規ファイルを走査。OS ユーザー名 / Windows 絶対パス / NDJSON のファイル名形式にヒットしたら exit 非 0 |
| **回帰** | `cd src-tauri && cargo test --workspace` が緑（コード変更ゼロの確認・AC-11） |
| **schema drift** | `cargo run --bin emit_schema` の出力が `schema/current.json` と byte-equal（差分ゼロが期待値） |

⚠️ **`input/` の OS フックは実機手動確認が要る領域だが、本タスクは `input/` を変更しないので不要。**

## 7. ロールバック計画

- `experiments/` は**追加のみ**。削除すれば元に戻る。
- `docs/` の変更は**追記のみ**（表・条件の書き換えゼロ）。`git revert` で戻せる。
- `src-tauri/` は無変更なので、ビルド・ゴールデン・schema にロールバック対象が無い。

## 8. 想定される結末と、それぞれの書き方（★ 先に決めておく）

| 結末 | `notes.md` の結論 | `§8` への波及 |
|---|---|---|
| T0+presence が **T0 を上回る** | 「低打鍵窓の弁別に在席情報が寄与する」＝ **文献に無い ablation の 1 本目** | ★ T1 昇格の**材料**になる。ただし昇格は別途裁く（D-3） |
| **上回らない** | 「在席情報は打鍵動態に対して増分を持たなかった」 | ★ **T1 は抑制側のまま**でよい根拠になる。[P118] の +0.9pt と整合 |
| 多数派分類器も超えない | 「本コホートでは打鍵再開は予測できない」 | ★ `§9` A-Q3 の解除条件①に**否定側の実数**が入る |
| 対象ギャップが 30 未満 | 「測れなかった」（Stop） | ★ 収集側の改善（D-7 の 1Hz 記録）が初めて費用対効果を持つ |

⚠️ **どの結末でも `notes.md` を書く。** `cv-gate-null` が「0.502 は統制下 CV の推定ではない」を
結論にしたのと同じく、**否定的な結果も成果である。**
