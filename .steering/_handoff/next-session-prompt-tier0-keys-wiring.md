# 次セッション開始プロンプト — Tier 0 配線の実装

このファイルの「===」以下をコピペして開始する。

**前提**: 2026-08-15 に **MhD 改善と主張範囲のセッション**が走り、
**文献サーヴェイ 2 ラウンド ＋ docs 改訂 2 件 ＋ 本タスクの準備**まで終わっている。
⚠️★★★ **コードは 1 行も変更していない。次セッションは実装から始まる。**

---

===

## §0 ★ このセッションでやること

★ **`.steering/20260815-tier0-keys-wiring/` の tasklist を上から実行する。**

⚠️★★★ **ただし「実装」から始めてはいけない。★ 先に潰すブロッカーが 1 件ある（§2）。**

★ 研究者の判断は**既に 4 件下りている**（`decisions.md`）。★ **問い直さない。**

| # | 判断 | 内容 |
|---|---|---|
| **D1** | ★ 順序 | ★★★ **Tier 0 配線を「記録のみ」として G1 完了前に先行させる**（⚠️ §10 の記述改訂が要る） |
| **D2** | ★ 範囲 | ★ **gse-dataset 側も同時に更新する** |
| **D3** | ★ 設計 | ★ **案 B**（`keys` ＋ `bs_keys` を**ともに `u64`**） |
| **D4** | ★ 未決の決着 | ★ **`FeatSnapshot` に含める**（→ **golden 4 本の再生成が要る**） |

## §1 ★★★ 最初に読むもの（この順で）

1. `.steering/20260815-tier0-keys-wiring/requirement.md` — ★ ゴール・受け入れ条件・**ブロッカー B-1/B-2**
2. `.steering/20260815-tier0-keys-wiring/design.md` — ★ **実測した行番号つきの変更対象表**・作業順序
3. `.steering/20260815-tier0-keys-wiring/decisions.md` — ★ **研究者判断 4 件 ＋ 実測 2 件**
4. `.steering/20260801-recovery-axis-grounding/tier0-wiring-design.md` — ★ **設計の原本**（181 行・受け入れ条件つき）
   ⚠️ **行番号が古い**（`logger.rs:974` → 実測 `:1214`）
5. `docs/architecture/personalization-and-online-learning.md` §5.2 / §10
6. `docs/adr/ADR-009-...md` Migration P1 ／ `ADR-008` D5（pinning）／ `ADR-005`（additive）

## §2 ⚠️★★★ 実装より先に潰すブロッカー（★ 実測済み・原本 memo に無い）

### B-1: **既存の schema parity drift がある**

```
$ python scripts/check_schema_parity.py --dataset C:/gse-dataset
[check_schema_parity] DRIFT detected
Missing variants in B: hook_health
（＋ meta variant の g1_mode プロパティが B 側に無い）
REAL EXIT=1
```

- ★ `C:\gse-dataset` の HEAD は `f3e8566`。★ その後に本 repo へ入った `hook_health` / `g1_mode` が**未追随**。
- ⚠️★★★ **`check_schema_parity.py` は意味的比較（改行・キー順を無視）なので、CRLF 起因ではない。本物の drift。**

→ ★★★ **手順**:
1. ★ **先に drift だけを解消して `exit 0` に戻し、単独でコミットする**
2. ★ **その後で**本タスクの additive 変更を足す

⚠️ **順序を守らないと「今回の変更で壊れたのか、元から壊れていたのか」が分離できない。**

## §3 ★ 本セッション（2026-08-15）で実測して確定したこと（★ 測り直さない）

| 項目 | ★ 実測値 |
|---|---|
| `f3` の定義 | ★ **`correction_keys / total_keys`**（`features.rs:151-152`）。⚠️ **1 経路しか読んでいない** |
| `total_keys` / `correction_keys` | ★ **`features.rs:146` / `:149` にローカル変数として既存＝新規計算ゼロ** |
| `feat` 行の書き出し | ★ **`logger.rs:1214` の手書き `writeln!` フォーマット文字列**（★ `f3` は `{:.4}` で丸め） |
| `FeatSnapshot` | ★ **`analysis/loop_step.rs:134`**。★ doc コメント逐語「**ゴールデンスナップショット (P0-10) の byte-equal 比較対象**」 |
| golden | ★ **4 本**（`minimal` / `phase1_ime_heavy` / `category_coverage` / **`deep_silence`**）。⚠️ **notes.md の「3 本」は古い** |
| `gse-dataset` | ★ **`C:\gse-dataset` に実在**（HTTPS clone・SSH 未設定）・HEAD `f3e8566` |

## §4 ⚠️★★★ 破ってはいけない契約（★ これが本タスクの本体）

> **Tier 0 配線は `feat` 行に値を書くだけであり、HMM にも X/Y 合成式にも 1 バイトも流さない。**

- ★ `engine.rs` の遷移行列 / 放出行列 / 量子化 → **触らない**
- ★ `X` / `Y` の合成式 → **触らない**
- ★ `p_flow` / `p_inc` / `p_stuck` / `intervention.rs` の発火 → **変わらない**
- ★ **`HMM_VERSION` を bump しない**

★★★ **検査方法**: **golden 再生成の差分が「新フィールドの追加のみ」であること。**
⚠️★★★ **`p_*` / `raw_*` / `ewma_*` / `obs` が動いていたら、その場で止めて原因を突き止める。**

## §5 ⚠️ 使う道具

| いつ | 何 |
|---|---|
| ★ **断定の前** | **`verify-before-claiming`**（★ 本セッションでも memo の行番号 3 件が実際にずれていた） |
| ★ Rust を書く | `rust-standards` ／ `architecture-rules`（★ `analysis/` に OS API を入れない） |
| ★ schema / logger | **`data-privacy`**（★ `keys`/`bs_keys` は**打鍵の数のみ**。文字内容・VK 生値を含まない） |
| ★ 実装の骨格 | `implementation-workflow` ／ `/add-feature` |
| ★ レビュー | ★★★ **`code-reviewer` + `security-checker` を並列起動**（⚠️ **前 2 セッションは動作条件で Agent が禁止され未実行**） |
| ★ 完了 | **`/finish-task`**（★ Step 3 で schema parity check が走る） |
| ★ コミット | `git-workflow` |

## §6 ⚠️ 落とし穴（★ この系列で実際に踏んだもの）

1. ⚠️★★★ **`Cargo.toml` は repo 直下に無い**（`src-tauri/`）。★ `cd src-tauri` するか `--manifest-path` を付ける。
2. ⚠️★★ **Windows コンソールは cp932** —— ★ Python は `PYTHONIOENCODING=utf-8 PYTHONUTF8=1` を必ず付ける。
3. ⚠️★★ **bash の heredoc は長い日本語 Markdown で壊れる** → ★ `Write` / `Edit` を使う。
4. ⚠️★★★ **`git rebase` / `git push` は deny** —— ★ 押すなら研究者に `! git push` を依頼する。
5. ⚠️★★★ **docs の行番号・状態記述を現況と思い込まない** —— ★ 本セッションだけで
   `logger.rs:974`（→ 1214）／ golden 3 本（→ 4 本）／ schema parity 清浄（→ drift あり）の **3 件が外れていた**。
6. ⚠️★★ **実セッション名 `Pnnn_gse_<日付>_<時刻>` は repo にも外部 LLM にも書かない。**

## §7 ★ 2026-08-15 セッションの成果（★ 本タスクの外・文脈として）

| コミット | 内容 |
|---|---|
| `d70a56a` | ★ 文献 R1: **デスク上行動からの停滞推定**（新規 [P117]–[P120] / [V83]–[V84]） |
| `15de344` | ★ `research-positioning.md §8` の「入力層の再設計を要する別課題」を**証拠状態の違う 3 段に分割** |
| `ff59807` | ★ 文献 R2: **沈黙の弁別**（新規 [P121]–[P123] / [V85]） |
| `2b0c58b` | ★ `§5.2` の **`boundary keys` を「採用候補」→「弁別の前提条件」へ格上げ** |

★ **本タスクを支える文献側の結論**:
- ★★★ **Tier 0 ＋ 個人正規化は 12 か国 449 名の実配備実績がある**（★ 識別子を 1 つも使わない）[P119]
- ⚠️ **Tier 1–2 の利得を測った ablation はゼロ（判定不能）** → ★ **Tier 1–2 の投資理由は「精度」ではない**
- ⚠️★★★ **「デスク上行動を足せば当たる」は precision 0.57（base rate 0.5）が否定する側** [P117]

## §8 ⚠️ 未決のまま次に渡すもの

| # | 未決 | 備考 |
|---|---|---|
| **T0-Q1** | ★ Tier 1（沈黙長・burst 長の**分布**）を `feat` に足すか別レコードか | ⚠️ **G1 の FS-B に必要**（原本 §8-3）→ ★ **G1 の残り 2 名を回す前に決める** |
| **T0-Q2** | ★ 期の幅 Δ（§11-7） | ★ **Δ が決まると Tier 1 の窓が決まる。順序としては Δ が先** |
| **T0-Q3** | ★ `notes.md §5③`「golden 3 本」を訂正するか | ⚠️ 別タスクの記録なので研究者判断 |
| **T0-Q4** | ★ `§5.2` Tier 0 表の `bs_rate`「未配線」表記の訂正 | ★ **誤り**（`f3` として既出・原本 §0 が指摘済み） |

## §9 ★ A–D のうち動かしていないもの（★ 研究者の 4 主題）

| # | 主題 | 状態 |
|---|---|---|
| **A** | 主張範囲を広げる | ★ **§8 は 3 段に分割済み**。⚠️ **§9 の非スコープ記述と §1 headline は据え置き（研究者判断）** |
| **B** | 対象タスクを増やす | ⚠️ **転移の文献はゼロのまま**。★ CV 算術（許せる CV = 0.502×√プール倍率）で判定可能 |
| **C** | 行動経済学 × オンライン ML | ⚠️ **既決は抑制方向のみ**（§6.2 / ADR-008 D7）。★ [V83] が「増やす前に多数派基線」を要求 |
| **D** | MhD 本体 | ★ **本タスクがその第一歩** |

⚠️★★★ **そして A–D のどれでもない未担当が 1 件残っている** ——
★ `experiments/20260731-phase1-calibration-analysis/notes.md §7` 逐語:
> **「次の一手は HMM 再チューニングでも task_kind 拡張でもなく、プローブ/介入レートの個人適応と尺度教示である」**

★ **[V83] の 3 脅威のうち「尺度の場当たり変換」がここに直撃する。★ 誰も担当していない。**

## §10 ★ リポジトリの状態（2026-08-15 セッション終了時点・実測）

| 項目 | 値 |
|---|---|
| ブランチ | **`docs/media-sound-modality-survey`**（⚠️ main ではない） |
| 本セッションのコミット | ★ **5 件**（`d70a56a` / `15de344` / `ff59807` / `2b0c58b` ＋ 本 steering） |
| ⚠️ 未コミット | ★ **他セッション由来が 27 件残っている**（★ 表現層トラック・EP-Q5 が未決） |
| ⚠️ 未実施 | **`/cross-review`** ／ **`/finish-task`** ／ **サブエージェント並列レビュー** |
