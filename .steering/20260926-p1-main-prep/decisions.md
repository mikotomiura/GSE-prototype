# 重要な設計判断 —— D. P1 本体の準備

> grill（2026-09-26・Opus）で研究者と閉じた分岐の記録。書式は「決定 / 理由 / 却下案」。
> ★ 研究者の回答は AskUserQuestion の選択そのまま。⚠️ 理由のうち「一次で確かめた」ものは出典を付ける。

## 判断 1: 収集状況 —— G1・O1 とも未開始

- **決定**: 実データは無い前提で D を組む（研究者回答）。
- **理由**: `experiments/20260801-controlled-friction-task/collection-readiness-record.md` の A〜C がすべて「（未記入）」（2026-09-26 実測）と整合する。
- **却下案**: 「G1 収集中・O1 未配布」「O1 も収集中」—— どちらでもない。

## 判断 2: D の終点は「器とテスト」まで

- **決定**: 実データに触れない。合成 fixture で緑になる経路・テスト・再現の雛形までを作る。PG-1 を通すかは研究者判断のまま。
- **理由**: 判断 1。加えて、事前宣言 §2.3 は PG-1 の手前でも中身を見ることを許していない（見てよいのは「分布だけ」・通すのは WP1 の yield 直後）。
- **却下案**: 実データで 3 極を回すところまで（データが無い）。

## 判断 3: v1.1 の規則 (a)〜(c) は「汎用の結合器」として今つくる

- **決定**: 任意のスカラー量を極ごとに受け取り、**軸ごと**（ポインタ軸 = `baseline`/`pointer_b`、修飾キー軸 = `baseline`/`modifier_m_plus`）に
  min / max / 幅と状態（`ok` / `not_computable` / `not_applicable`）を返す関数を作り、テストで固定する。G2 は後でこの関数に差し込む。
- **理由**: G2 は recovery 推定器と介入判断を要し、どちらも未実装（`personalization-and-online-learning.md:1174`・ADR-009:353）。
  規則そのものは量に依らないので、今テストで固定できる。
- **却下案**: G2 ができるまで保留（v1.1 の規則が検査ゼロのまま残る）。

## 判断 4: 解析コードは Python・`scripts/`

- **決定**: `scripts/p1_*.py` ＋ `scripts/tests/test_p1_*.py`（unittest）。依存は **stdlib ＋ 既存の dev 依存 duckdb** に限る。
- **理由**: `build_analysis_db.py` / `check_prereg_parity.py` と同じ置き場で、`analysis/` のレイヤー規則に触れない。
  ⚠️ `sklearn` は入っていない（2026-09-26 実測）ので、grouped k-fold は stdlib で書く（新規依存は Loop の Stop Condition）。
- **却下案**: Rust `src/bin/`（nested CV を Rust で書くのは重い）／ `experiments/` 内（テストの配線が弱い）。

## 判断 5: セッションと参加者の対応は「パスの構成要素」

- **決定**: レイアウト `<root>/<P-ID>/<session>/{baseline,pointer_b,modifier_m_plus}.json`（`<session>` は `run-features-all-poles.sh` の outdir）。
  P-ID はパスから取り、封筒の中身には手を入れない。
- **理由**: 封筒には参加者 ID が無い（`replay.rs` 実測）。`gen_sessions_manifest.py` / `build_analysis_db.py` と同じ流儀（パスの content-free な構成要素だけを読む）。
- **却下案**: 明示の対応表 CSV（手作業が増える）。

## 判断 6: 探索の実行器を入れる。PG-1 の値が無ければ拒否する

- **決定**: 格子（27 ＋ OFAT 4）を回す器と、grouped nested CV の選択器を作る。
  - 一人あたり episode 数の下限は、**凍結 JSON の新版が宣言した値**（キー名は判断 19）だけを読む。無ければ**非 0 で拒否**し、値を推測で埋めない。
  - `q` と `warmup_count` は対応表（`0.99→100`／`0.995→200`／`0.999→1000`）から**対で**渡す。
- **理由**: 事前宣言 §2.3（値は PG-1 で宣言する）・v1.1 (5)。
- **却下案**: 入れない（PG-1 の後の別タスク）／ 格子を回すところまで（CV は後）。
- ⚠️ 選択器の範囲は判断 18 が「metric 表まで」に狭めた。

## 判断 7: 起票 P1-F —— CLI は変えない

- **決定**: `gse-replay` の `--set q=…` に `warmup_count` の連動を持たせない。解析側が対応表から対で渡し、封筒 `config` で規則 (d) の除外を掛ける。
- **理由**: CLI と封筒の契約（`overrides` の意味）を変えずに済む。v1.1 (5) が既に判定式を決めている。
- **却下案**: CLI に連動を持たせる（Rust と封筒の契約変更が要る）。
- **記録先**: ADR-030 補訂 3（issue 010）。

## 判断 8: 小物は 4 件とも D に入れる

- **決定**: P1-G・P1-A・#8（非対称の裁定）・#9（DuckDB 結合）を入れる。

## 判断 9: #8 —— `feat` 行 0 本の入力では `T1a` を `null` にする（onset に揃える）

- **決定**: 穴を検出できない（観測区間が確定しない）入力では、`pause_p50_ms` / `pause_p90_ms` / `pause_max_ms` を全行 `null` にする。ADR-030 に**補訂 3**として記録する（本文は書き換えない・issue 010）。
- **理由**: 「観測できないものは値で埋めない」原則（補訂 1 項目 2・事前宣言 §1「推測で埋めない」）に揃える。
- **トレードオフ**: `feat` 行を持たない入力（古いログ・一部の fixture）は `T1a` を全部失う。⚠️ O1 の実データが `feat` 行を必ず持つかは**未確認**（確かめるのは issue 008 の中で、コードからだけ）。
- **却下案**: 現状（値を返す）を規範化する。
- ⚠️ **凍結との関係**: 事前宣言は `t1a_window_ms` の**値**を凍結しており、この場合の扱いは書いていない → 値は変えないので新版は切らない。実データを見る前の変更である。
- ⚠️★★ **再確認（2026-09-26・分解中に研究者へ再提示して「進める・旧検査を張り直す」）**: 裁定時に「効くのは古いログと fixture だけのはず」と伝えたが、実測で影響が大きかった ——
  `src-tauri/tests/fixtures/` 19 本中 **11 本が `feat` 行 0 本**、過去 acceptance 2 本（`20260914-mhd-feature-offline-tiers/issues/003-acceptance.sh` の `deep_silence` / `instrument_rich`、
  `20260921-p1-prereg-cli-poles/issues/003-acceptance.sh` AC6 の「穴なし版」）が 0 本の入力で `T1a` の**値**を検査している。
  → ★ 旧検査は **fixture の一時コピーに 1Hz の `feat` 行を足して**値の検査を残す形に張り直す（fixture 本体・ゴールデンは変えない）。0 本の入力で全行 `null` になることを新しい検査にする。
  ⚠️ O1 の実ログが `feat` 行を必ず持つかは issue 008 の中でコード（logger の書き出し経路）から確かめ、持たない経路があれば止める。

## 判断 10: #9 —— episode 表だけを DuckDB に載せる

- **決定**: 3 極の出力から極ごとの episode（onset）表を作り、`sessions.csv`（参加者・OS・phase）と結合する。metrics・probe・survey とは結合しない。DB は repo の外に置き、共有しない。
- **理由**: 転帰の定義が無いうちに転帰と結合すると、PG-1 の規律（転帰を見ない）とぶつかりやすい。
- **却下案**: metrics・probe まで全部。

## 判断 11: 探索の副 metric の転帰は外から渡す。無ければ拒否する

- **決定**: 選択器は転帰ラベル表（episode → 転帰カテゴリ）を**必須入力**にする。無ければ非 0 で拒否する。テストは合成ラベルで行う。
- **理由**: `restart`（`T1d`）は「転帰側の量」だが、転帰の定義ではない（ADR-030 補訂 1 項目 7）。ここで決めると転帰の定義を裏口で決めることになる。
- **却下案**: `restart` を代理にする（ADR の裁定が要る）。

## 判断 12: PG-1 の分布集計と探索は 3 極それぞれ独立に

- **決定**: 極ごとに分布を出し、探索も極ごとに回して、極を混ぜずに報告する（§3 規律 4）。`pole_applicable=false` の単位は「算出不可」として別に数える。
- **却下案**: baseline だけ。

## 判断 13: Loop に分解する

- **決定**: to-prd（本 grill の結果をそのまま要件にする）→ to-issues（Opus）→ `/clear` → 別セッションで実行。
- **理由**: issue は 9 本前後で、Python と Rust の Allowed Files が交わらず、並列に向く。

## 判断 14: `experiments/` は雛形と 1 コマンド再現だけ

- **決定**: `scripts/templates/` に P1 の事前登録の雛形（PG-1 の欄・seed `20260921`・gse-dataset commit・`HMM_VERSION`・lockfile の刻印欄）と、再現スクリプトを置く。
  実体の `experiments/<日付>-…/` は P1 を始める日に作る。
- **理由**: 日付は「作る日」の規約。結果が空の実験 dir を長く残さない。O1 の実験 dir は別タスク。
- **却下案**: 今 `experiments/` に作る ／ O1 の dir に相乗りする。

## 判断 15: タスク名 `p1-main-prep`（研究者選択）

---

## 分解時の判断（issue-slicing・Opus・研究者に聞かずに決めたもの）

## 判断 16: P1-G の検証は「形式」だけにする（一致は求めない）

- **決定**: `--feature-config` の `id` は `^[a-z0-9][a-z0-9-]{0,63}$`、`version` は `^[0-9]+\.[0-9]+\.[0-9]+$` に合わなければ非 0 で拒否する。凍結 JSON の `id` / `version` との**一致は求めない**。
- **理由**: 起票 P1-G は security LOW で、懸念は「検証せずに封筒へ写す」こと。別の config を使うこと自体は正当で、区別は `config_source` / sha / `overrides` が既に担う（起票表の注記）。
- **却下案**: 凍結 JSON と一致を要求する（`--feature-config` の用途を潰す）。

## 判断 17: Python の検証は `unittest discover -p "test_p1_*.py"`、skip 0 は acceptance で見る

- **決定**: Loop の verify は `cargo test` に加えて `python -m unittest discover -s scripts/tests -t . -p "test_p1_*.py"` を回す。各 issue の acceptance が「自分のテストが 1 件以上走り、skip 0」を確かめる。
- **理由**: Python 3.11 では 0 件でも exit 0 になる（空振り）。duckdb が無いと skip で緑になる（`ci.yml:856` の注記と同じ罠）。
- ⚠️ 新しいテストは `ci.yml` にモジュール名で配線する（`check-tests-are-wired.sh` は名前で見る）。→ `ci.yml` を触る Python issue は直列になる。

## 判断 18: nested CV の選択器は「fold × 一式 × 極の metric 表」まで（研究者裁定 2026-09-26）

- **決定**: 選択器は fold を組み（outer = leave-one-participant-out・inner = grouped k-fold・`k = min(5, 参加者数 − 1)`・seed `20260921`）、
  fold × 一式 × 極ごとに 3 metric（主・副・第 3）の**素の値**を計算した表を出すところまでにする。
  **fold をまたぐ集約・同点の崩し方・最終の 1 つの選び方は実装しない** —— PG-1 と同じ新版（v1.2）で宣言し、実装はその後の別タスク。
- **理由**: 事前宣言 §2.2 / §2.3 はこれらを決めていない（例: inner の検証側が 1 人だと変動係数は定義上 0）。
  実装者が決めると手続きを実装の中で決めることになる。
- **却下案**: Opus の草案（全 fold で主を満たす一式だけ残す → 副 → 第 3 の平均最小 → 同点は運用値に近い順／最終は outer の最頻値）で実装し、宣言前は鎖す。

## 判断 19: PG-1 の値を読むキーの名前（分解時・Opus）

- **決定**: 格子の実行器（004）と選択器（005）は、凍結 JSON の新版にあるキー `pg1.min_episodes_per_participant`（1 以上の整数）を読む。
  キーが無ければ **exit 6（PG-1 未宣言）**で拒否する。既定の読み先は `src-tauri/prereg/p1-episode.json`、テストは `--prereg <path>` で差し替える。
  どちらを使ったか（`frozen` / `file`）と sha256 の先頭 16 桁を出力に刻む。
- **理由**: 事前宣言 §2.3 は PG-1 の前に探索を「1 度も回さない」としているので、格子の実行器も PG-1 の値を持たない限り走らせない。
- ⚠️ **キーの名前は提案である**。v1.2 を書くときに変えるなら 004 / 005 を合わせて直す（値はここでは決めない）。
- ⚠️ 「下回った参加者の扱い」（§2.3）は表には関わらないので、キーを置かない（v1.2 で宣言する）。

## 判断 20: 修飾キー軸で極 M+ が `not_applicable` のときの出力（分解時・Opus）

- **決定**: 状態 `not_applicable`、`width = 0`、`min = max = baseline の値`。極 M+ の値のキーは**出さない**（「極 M+ を計算した」と書かない）。
  ポインタ軸の `not_computable` は `min = max = width = null`。
- **理由**: v1.1 (3)「`not_applicable` と報告し、極 M+ を計算したと書かない…上下界の幅への寄与はゼロ」／「幅 0 と報告しない（ポインタ軸）」。
  極 M+ は構造上 M− と恒等なので、min / max に baseline を置いても M+ を計算したことにはならない。
