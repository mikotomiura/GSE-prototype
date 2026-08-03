# 設計

## 実装アプローチ

**凍結（`preregistration.md §3`）を一切動かさず、その周りを埋める。**
判定基準に触れる必要が出たら止まって記録する、という制約が最上位にある。

調査の結果、実装方針を決める事実が 4 つ確定した（いずれも本セッションで一次確認）:

| # | 事実 | 出所（一次確認） | 帰結 |
|---|---|---|---|
| 1 | NDJSON の `key` は**打鍵 1 打ごと**に出る | `logger.rs:939` `{"type":"key","t":..,"vk":..,"press":..}` | Tier 0/1 は**オフラインで全部計算できる**。凍結解除を待たない（引き継ぎ §0-1 の裏取り） |
| 2 | gse-dataset の `key` は `vk` ではなく **`category`** を持つ | `analysis/anonymize.rs:89`（`vk`→`category`）＋ `~/gse-dataset` 実データ | 解析は**匿名化後**の形式を入力にする。`bs_rate` は `category ∈ {backspace, delete}` から出す |
| 3 | 匿名化は `t` を **session_start 相対 ms** に変換する | `anonymize.rs:69-101` | ブロック境界の管理が「セッション内相対時刻」で完結する → T-B の (a) 案が有利 |
| 4 | `ime_shadow` は **Windows 限定** | `lib.rs:1486` `#[cfg(target_os = "windows")]` | macOS 実施では `ime_dwell_med` が**構造的に欠測**。FS-B は 14 特徴のまま、**分散ゼロ特徴の扱い規則**が要る |

## 変更対象

### 修正するファイル

- `experiments/20260801-controlled-friction-task/preregistration.md` — T-A の 9 項目（§2.1 書換 / §2.7 新設 /
  §2.8 新設 / §2.4 訂正 / §3.3 の分母を割合化 / §3.7 拡張 / §4 に適格性ゲート / §5 訂正 / 生態学的妥当性の明記）
- 同 `config.json` — 上記の機械可読同期
- 同 `README.md` — 凍結文書へのポインタ更新（設計本体の記述は変えない）
- 同 `env.md` — 「Tier 0/1 は凍結解除まで計算できない」を訂正・実施 OS の扱いを追記
- 同 `data.md` — 匿名化後スキーマ・ブロック分割・課題文セット ID を追記
- 同 `run.sh` — 停止スタブ → **実施前チェック**

### 新規作成するファイル

- 同 `protocol.md` — 実施プロトコル（T-B）
- 同 `consent.md` — 説明同意文書（T-F）
- 同 `assign.py` — SEED から被験者ごとの「題材↔条件↔ブロック順」割付表を生成（T-A-2 / T-B）
- 同 `validate_materials.py` — 課題文の制約を機械検証（T-C）
- 同 `analyze.py` — ブロック特徴量 ＋ 判定パイプライン（T-D / T-E）
- 同 `materials/README.md` / `materials/copy.md` / `materials/topic01_lo.md` / `materials/topic01_hi.md`
- `.steering/20260802-g1-implementation/*`

### 削除するファイル

なし。

## 残った設計自由度と、その埋め方

凍結文書が**沈黙している**箇所が 4 つある。いずれも「基準の変更」ではなく「未指定の埋め」なので、
**データを見る前に**宣言して埋める。詳細な却下理由は `decisions.md`。

### D-1: ブロックの切り方 → **(a) 1 ブロック = 1 セッション**（アプリを毎ブロック起動し直す）

- (b)（通しで録ってオフライン分割）を却下したのは、**分割時刻の取り違えが一発で全ブロックのラベルを
  ずらす**ため。(a) はファイルが物理的に分かれるので、ずれても 1 ブロック分で止まる。
- 匿名化が `t` をセッション開始相対にするため、(a) ならブロック内相対時刻がそのまま得られる。
- `FeatureExtractor` はセッション開始で `reset()` されるので、**30 秒ローリング窓が前ブロックを引きずらない**。
  (b) では各ブロック冒頭 30 秒が前ブロック＋休憩の沈黙で汚染される。
- コード変更ゼロで実現できる（アプリの通常の起動／停止だけ）。

### D-2: FS-A の算出元 → **`feat` 行（1Hz）の中央値**

- FS-A の問いは「**旧 X 軸の観測空間**で分離できるか」であり、観測空間とは**実行時の 5 特徴量**そのもの。
  `feat` 行はそれを 1Hz で記録している。
- 打鍵から再計算する案を却下: `InputEvent.is_repeat` は **NDJSON に載っていない**ため
  （`features.rs:110` が F1/F4 でリピートを除外している）、オフライン再計算は
  **オートリピートを混入させた別物**になる。
- 集約は**ブロック内 `feat` 行の中央値**（外れ値に強く、F1 自身が中央値である性格と整合）。

### D-3: out-of-fold AUC の定義 → **leave-one-pair-out の順位一致率**

- 「被験者内 leave-one-block-pair-out」は凍結済みだが、fold ごとに held-out が 1 対しかないので
  AUC の集計方法が未指定。**全 4×4=16 対を fold とし、held-out の HI が LO より高いスコアを得た
  fold の割合（同値は 0.5）**を out-of-fold AUC とする。これは held-out 対上の AUC の定義そのもの。
- positive control は copy(2)×writing(8) = 16 対で同じ統計量を使う。

### D-4: 分散ゼロ特徴の扱い → **標準化後 0（寄与なし）とし、必ず報告する**

- 事実 4 のとおり macOS では `ime_dwell_med` が構造的に欠測。
  課題文を紙で配る運用では `external_paste_chars` も全ブロック 0 になる。
- 学習 fold 内で標準偏差が 0 の特徴は **0 に潰す**（除去しない）。FS-B は 14 特徴のまま。
- **どの特徴が何 fold で潰れたかを出力に必ず出す**（黙って通さない）。

## 影響範囲

- `src-tauri/` / `src/` は**触らない**。凍結対象（`schema_dto.rs` / `engine.rs` / `loop_step.rs` /
  `intervention.rs` / `probe_scheduler.rs` / `App.tsx`）にも触らない。
- `docs/preregistration-v0.3.md` / `research-positioning.md §5` は**触らない**。
- `experiments/20260802-within-person-scope-detector/` は触らない（`analyze.py` は読むだけ）。

## 既存パターンとの整合性

- `experiments/20260802-within-person-scope-detector/analyze.py` に倣い、**Python 標準ライブラリのみ**。
  L2 ロジスティック回帰は Newton 法（14 特徴 × 6 標本）で自前実装する
  → `requirements.txt` を増やさない（`env.md` の方針・再現に lockfile を要さない）。
- `run.sh` は同実験と同じ「`cd $(dirname $0)` → SEED を読む → `python3 analyze.py`」の形。
- セッション日時を出力に出さない（同 `analyze.py:167` と同じ理由・本 repo は一時 public 化の運用がある）。

## テスト戦略

- **自己検証つき解析スクリプト**: `analyze.py --selftest` で合成データを生成して
  (i) 分離できる合成データで AUC=1.0・p=1/70、(ii) ラベルが無情報な合成データで p が大きい、
  (iii) 分散ゼロ特徴が潰れて例外にならない、を検査する。
- **課題文の機械検証**: `validate_materials.py` が資料本数・総文字数の一致・産出要求の記載を検査。
- **割付の機械検証**: `assign.py --selftest` が HI4/LO4・題材の重複なし・A/B で条件が反転を検査。
- **実施前チェック**: `run.sh` が上記 3 つを走らせ、資材が揃えば exit 0・欠ければ非 0。

## ロールバック計画

コード（`src-tauri/` / `src/`）には触らないため、製品側のロールバックは発生しない。
実験ディレクトリの変更は 1 コミット 1 論理単位で積むので `git revert` で戻せる。
`preregistration.md` の改訂は**追記と明示的な「★ 訂正」節**の形で行い、
元の記述を削除せず残すため、何が変わったかが文書内で追える。
