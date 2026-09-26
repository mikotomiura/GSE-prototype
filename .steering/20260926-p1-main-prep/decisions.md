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

## 判断 21: 参加者が 3 人未満なら nested CV を組まずに拒否する（TASK-PRE・Codex 指摘 4）

- **決定**: 選択器（005）は `N < 3` で exit 3。
- **理由**: 事前宣言 §2.2 の `k = min(5, 参加者数 − 1)` は N = 2 で k = 1 になり、grouped k-fold が組めない。事前宣言はこの場合を定めていないので、実装者が手続きを発明しない（判断 18 と同じ理由）。
- **却下案**: N = 2 のときは inner を省いて outer だけで表を出す（手続きの発明になる）。
- **見直し**: v1.2 で研究者が N < 3 の扱いを宣言したとき。

## 判断 22: PG-1 の値の置き場は凍結 JSON の新版のまま（TASK-PRE・Codex 指摘 1 を一部却下）

- **決定**: 判断 19 のまま。別の宣言ファイルは作らない。
- **理由**: 事前宣言 §2.3 の表「どこに書くか」= **本書の新バージョン**。値の SSOT は凍結 JSON（parity 検査の対象）。「変更禁止」は D の範囲での話で、v1.2 は研究者が新版として切る。
- **採った部分**: 値の型と範囲の検証（int・bool でない・1 以上）を 004 / 005 に足した。

## 判断 23: `verify_level: recheck` の 7 本を `parse` に落とす（実行セッション・watchdog の故障）

- **決定**: 001〜005・007・008 の `verify_level` を `recheck` → `parse` にする。006・009・010 は元から `parse`。
- **理由**: `recheck` の効果は watchdog（Haiku）の起動だけで、その watchdog が `WD_TOOLS` の不備で acceptance を回せず、
  20 ターンを使い切って空応答になり `blocked` になる（詳細と実測は `blockers.md` B-1）。**AC 未充足の指摘ではなく、gate の故障**。
- **担保**: acceptance は (1) `loop-run.sh` の verify 内（worktree で `00X-acceptance.sh`）と (2) merge 前のメインによる clean な検証用 worktree での再実行、の 2 段で残る。
  ★ `issue-slicing` 基準 5 の選別（研究の契約をコードで固定する issue は再検証する）の**趣旨**は (2) が担う。
- **却下案**: `loop-run.sh` の `WD_TOOLS` とプロンプトをこの task の中で直す（共有基盤の変更・範囲外）。→ 起票候補 P1-L。
- **見直し**: P1-L を直したら、次の task の issue-slicing で `recheck` を再び選別する。

## 判断 24: 「`feat` 行 0 本の fixture」の数の訂正（実行セッション・メイン）

- **決定**: 19 本中 **7 本**が正（`argumentative_ime_mixed` / `category_coverage` / `deep_silence` / `instrument_rich` / `minimal` / `minimal.anon` / `vibe_coding_ime_mixed`）。判断 9 の再確認・`issues/008.md` の Background・`_handoff/next-session-p1-main-prep-loop-run.md` §2 の「11 本」は**誤り**（分解時の数え方は記録に無く、再現できない）。
- **数え方**: JSON として `type == "feat"` の行を数える（`jq -c 'select(.type=="feat")' <file> | wc -l`）。⚠️ 文字列 grep `"type":"feat"` だと 8 本になる —— `resumption_outcomes.ndjson` だけ JSON の区切りに空白が入っており（`"type": "feat"`）数え落とす。
- **影響**: なし（判断 9 の決定そのものは数に依らない・onset 側へ揃える）。訂正したのは ADR-030 補訂 3 項目 1・issue 008 の Execution Result・issue 010 の記録・過去 acceptance（mhd 003）のコメント。
- ⚠️ 判断 9 の本文と 008.md の Background は**当時の記録として書き換えない**（この判断が訂正の SSOT）。

## 判断 25: 004-acceptance.sh の基準ブランチを `main` から base へ（実行セッション・分解の欠陥の是正）

- **決定**: `004-acceptance.sh` の「Rust 不変」検査の基準を `feat/p1-main-prep`（無ければ `main`）にする。検査の強さ（004 の変更が `src-tauri/src/` に及べば赤）は変えない。
- **理由**: `blockers.md` B-2。base は 007/008 の Rust の変更を含むので、`main` との差分は 004 と無関係に赤になる。worker が gate を書き換えずに止まったのは正しい判断だった。
- **担保**: 修正版を clean な検証用 worktree で worker のコミットに対して回し rc=0。他の acceptance を全数 grep して同型の欠陥が無いことを確かめた。
- **却下案**: 12 行目を削除する／特定ファイルだけに絞る（検査が弱くなる）。

## 判断 26: 完了レビュー（code-reviewer 2 本・security-checker・Codex 1 巡目）の仕分け（実行セッション）

- **結果**: CRITICAL / HIGH は 0 件。MEDIUM 4 件・LOW 多数。すべて一次（コード）で裏取りしてから反映した（偽陽性は無かった）。
- **直したもの**（本 task 内・`tech debt now`）:
  - `p1_run_grid.py`: 凍結 JSON 由来（`prereg_source: frozen`）の格子は、封筒の `prereg_sha256_prefix` と一致しなければ `RunError`（古い gse-replay の刻印で新しい格子を回さない）。`--prereg` 差し替え（`file`）は両方の hash を manifest に残すだけ。テスト `test_frozen_source_requires_envelope_hash_match`。
  - `p1_select.py`: `frozen` の格子を別 hash の事前宣言で評価するのは、**出力を書く前に** exit 3。manifest の `prereg_source` / `prereg_sha256_prefix` の形も検査（テスト追加）。
  - `p1-repro.sh`: `<workdir>` が `<ndjson-root>` の中かの判定を **`mkdir` の前**へ（2 段以上下のときに入力ディレクトリへ階層を残す欠陥。★ 旧コードで実測: 変異〔旧 `p1-repro.sh`〕で新テストが赤になる）。⚠️ 同時に指摘された「利用者の既存の空ディレクトリを `rmdir` する」は、旧コードでは入力ルートのレイアウト検査（『セッションが 1 つも無い』）が先に止めるため**その形では到達しなかった**（実測）。`rmdir` は防御として廃止し、既存の空ディレクトリを消さないテストは退行止めとして残した（旧コードでも緑＝判別力は無い）。未作成の `..` 入りは拒否。identity の Python は `KeyError` / `TypeError` も exit 3 に揃え、終了コードの契約（1〜3 は各段と重なる）を書いた。テスト 3 件追加。
  - `run-features-all-poles.sh`: git 判定から `GIT_DIR` / `GIT_WORK_TREE` / `GIT_CEILING_DIRECTORIES` を外した（他の 2 か所と同じ）。
  - `replay.rs`: `theta_estimator` の検証エラーも `echo_untrusted` を通す（端末へ ANSI が流れない）。
  - `p1_bounds.py`: 軸の値が dict でない単位も `ValueError`（docstring の契約）。
  - 009 の陰性対照: 「明示的な null」と「キーの欠落」を区別し、`theta_sample_n >= 100` も確認（Codex 指摘 2・reviewer LOW）。
  - ADR-030 補訂 3: 「(a)(b) は 0 本にならない」を**否定できない**へ訂正（Codex 指摘 1）／ 0 本と 1 本の不連続を明記（Codex 指摘 3・reviewer LOW）／ 「`p1_run_grid.py` は存在しない」を実装済みへ／ 「`gse-replay` に手を入れない」を連動に限定。`dispersion.rs` の doc・runbook (k) の `GSE_REPLAY_BIN`。
- ⚠️ **研究者の裁定待ち（M3・実装は変えていない）**: `p1_select.py` の `metrics_for` は、**規則 (d) の除外で使えるセッションを 0 本にした参加者**を、適用不可だけの参加者と同じく最小値から外している（issue 005 の文言は「適用可のセッションが 1 本も無い参加者」で、実装判断〔005 Execution Result 146 行〕は「適用可かつ除外されていない」）。
  除外で 0 本になった参加者を**外す**か・**0 本として数える**か（後者なら主 metric の下限が悲観側に倒れる）は研究の意味に関わるので、実装者が決めない。→ 見えるように `n_participants_lost_to_rule_d` 列を**足しただけ**（最小値の計算は不変）。到達するのは参加者に固有の除外が起きたときだけ（格子は q と warmup を対で渡すので、通常は全参加者に同時に起きる）。v1.2 で宣言する（判断 18 と同じ扱い）。
- **記録だけにしたもの（LOW・直さない）**:
  - `build_p1_episode_db.py`: ガード後の TOCTOU（別プロセスが同じ `--out` を作ると `_remove_partial` が他人のファイルを消しうる）・失敗時に `mkdir` した親ディレクトリが残る。手元で 1 人が使う前提で確率は低い。
  - `p1_pg1_distribution.py` / `p1_select.py` の出力: 書きかけのファイルが残ると次の実行が「`--out` が既にある」で止まる（一時名 → rename にする案）。
  - `p1_run_grid.py` / `p1_select.py` が別モジュールの非公開名（`_inside_git_work_tree` / `_emit` / `_sha256_file`）を import している（worker が自己申告済み・共通モジュールへの切り出し案）。
  - `p1_select.py`: `param_mismatch` を自分で判定し直さず manifest の `excluded_rule_d` に頼る（規則 (d) 自体は独立に判定し直している）。
  - CI の P1 step は unittest の skip=0 を強制していない（acceptance 側にだけある・判断 17）。
  - `p1_run_grid.py`: Windows で `shutil.which("bash")` がカレントディレクトリを先に探す（cwd に置ける攻撃者が前提）。
  - `replay.rs`: `is_wellformed_prereg_version` は先頭ゼロを許す（`01.0.0` と `1.0.0` が別物として通る）。判断 16 の正規表現どおりなので仕様どおり。
- **却下**: なし（偽陽性 0 件）。

### 判断 26 の追記: Codex 2 巡目（修正コミット `2922675f` の差分・3 件）の仕分け

- **指摘 1（P2）`file` 由来の格子でも、選択時に同じ宣言を要求せよ → 採らない**。
  - 理由: `file` は `--prereg` で差し替えた実行（テスト・探索用）で、選択器は manifest の `configs` を使い格子を**組み直さない**ので、同じ格子を別の `L`・`seed` で評価し直すこと自体は成立する（provenance に両方の hash と `grid_prereg_*` が残り、食い違いは note で出る）。既存テストもこの使い方（1 つの格子を pg1 / seed を変えて評価）に依存している。
  - 研究の実行（既定＝repo の凍結 JSON。`p1-repro.sh` は `--prereg` を渡さない）では `frozen` なので、食い違いは出力前に拒否される（本判断の修正）。
  - 見直し: `--prereg` を研究の実行で認めるなら、`file` でも一致を要求する（その回に A→A 成功・A→B 拒否のテストを足す）。
- **指摘 2（P2）規則 (d) による脱落が最小 episode 数の判定を有利にしうる → 既知（裁定待ち）**。本 task は選択（集約・最終選択）を実装していないので現時点の影響は無い。⚠️ **選択を実装する回は、`n_participants_lost_to_rule_d > 0` の (一式, 極) の扱い（判定保留・悲観側で数える等）を先に裁定する**（★ 上の M3 と同じ論点）。
- **指摘 3（P3）`p1-repro.sh` の mkdir 前ガードの回帰テスト → 一部採用**。拒否の前後で入力ディレクトリの構成が同一であることを見る検査（`find . | sort` の比較）を足した。symlink 経由のケースは、Windows の git-bash で `ln -s` が信頼できない（コピーになりうる）ため入れていない（`pwd -P` で物理パスに解決しているので実装は対応済み・テストは未追加）。
