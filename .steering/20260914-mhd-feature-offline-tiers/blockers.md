# 詰まりと起票 — タスク 2（Mh-D 特徴量の Tier 別オフライン実装）

> ⚠️★★★ **このファイルは「本タスクでは閉じないが、閉じないまま黙らせてはいけないもの」の台帳**である。
> ★ 裁定済みのものは `decisions.md`、実行の記録は `issues/*.md` の Execution Result にある。

---

## 起票 1: ⚠️★★★ `meta` 行に `os` が無いので、`schema_dto.rs` が約束した判別ができない

- **起票日**: 2026-09-15（★ issue 002 の `security-checker` 指摘 M2 から派生）
- **何が食い違っているか**（★ 一次資料で確認・⚠️ 推測ではない）:
  - `src-tauri/src/schema_dto.rs:296` 逐語:
    「**由来は meta 行の os と capabilities 宣言で判別する。両 OS のデータを混ぜて学習・評価してはならない。**」
  - ⚠️ ところが **`"os"` は `logger.rs` / `capabilities.rs` / `schema_dto.rs` のどこにも無い**
    （★ 実測: 3 ファイルへの `grep '"os"'` が **0 件**）。
  - ⚠️ **機械生成の JSON Schema (`src-tauri/schema/current.json`) にも `os` キーが存在しない**
    （★ 実測: `grep -o '"os"'` が 0 件）。
  - ★ `meta` の実書式は `logger.rs:1628` / `:1640` の書式文字列がすべてで、
    `session_start` / `hmm_version` /（`g1_mode`）/ `app_version` / `capabilities` のみ。
- **なぜ効くか**: `capabilities.rs:216-233` が逐語で
  「**由来だけでなく「母数」も違う**」「⚠️ **`abandon` 率を OS 間で直接比べてはならない**」と述べ、
  その判別手段として **`meta` 行の OS** を指定している。
  → ★★★ **指定された手段が存在しないので、規約が履行不能である。**
  ⚠️ issue 002 で `ime_dwell_ms` / `ime_nav` / `ime_abandon` が `--features` の出力に載ったので、
  **下流が Win/mac を混ぜて平均できる状態**が実際に生まれた。
- **本タスクで閉じない理由**: ⚠️ `meta` へのフィールド追加は **計器変更**であり、
  issue 002 / 007 の Scope Out（`logger.rs` / `schema_dto.rs` / `capabilities.rs` を触らない）に直撃する。
  ★ 計器変更の裁定は **ADR-032 の領域**（→ `.steering/20260914-instrument-change-arbitration/`）。
- **★ 次に何をするか**（⚠️ 順序を飛ばさない）:
  1. ★ ADR-013 の Migration として「`meta` に `os` を足す」是非を裁定する
     （★ `os` は**端末環境の宣言**であって被験者由来データではないので、
     `data-privacy` ルール 1 / ルール 7 には抵触しない —— ⚠️ ただし
     **指紋性**は ADR-013 D6 逐語「粗い semver のみ」と同じ基準で検討すること）。
  2. ⚠️ 足すまでの間は、**`schema_dto.rs:296` の「meta 行の os」という記述が実体と食い違っている**
     ことを承知して読む。★ 直すなら「一次へ戻す」（= 記述を実体に合わせるか、実体を記述に合わせるか）を
     裁定してから（`feedback_stale_doc_revert_to_primary`）。
- **⚠️ 部分的に閉じるもの**: ★ `capabilities` 側の欠落は **issue 007（`Q`）が
  `quality.capabilities` / `quality.hook_health` を行に載せることで閉じる**。
  ⚠️ **`os` は閉じない**（★ `capabilities` 宣言は OS 名を含まない）。

---

## 起票 2: ⚠️ `--features` の出力に「由来の封筒」が無い —— ★★★ **2026-09-20 に閉じた**

> ★ **研究者判断 2026-09-18（判断 25 #14）**: 封筒を足す小 issue を切る（`{ provenance, config, rows }`・全 acceptance の前提を 1 度だけ書き換える）。Loop 基盤の修正の後。
>
> ### ★★★ 閉じた（2026-09-20・`.steering/20260920-envelope-issues/`）
>
> - ★ 出力は **`{ provenance, config, rows }`** になった（`bin/replay.rs::FeatureEnvelope`）。
> - ★ `provenance` が持つもの（★ grill で研究者が裁定・判断 2）:
>   `sharing` / `tool` / `tool_version` / `source_basename` / `source_sha256_prefix` /
>   `session_start` / `hmm_version` / `app_version` / `g1_mode` / `o1_mode` /
>   `keyboard_layout` / `capabilities`。
> - ⚠️★★★ **`os` は載っていない** —— `logger.rs::write_meta_start` が書いていないため
>   （2026-09-20 に一次で確認）。★ 足すのは**計器の変更** = 起票 1・ADR-032 の領域であり、
>   ⚠️ **推測で埋めなかった**。
> - ★ **二重化は解いた**（判断 3）: `capabilities` は `rows[].quality` から**外し**、封筒へ移した。
>   ⚠️ 「宣言が無い」という事実は tick 単位の欠測理由なので
>   `missing_reasons` の `capability_undeclared` は**そのまま残る**。
> - ⚠️★★★ **`provenance.hmm_version`（収集時）と `config.hmm_version`（解析時）は別物**である。
>   ★ `instrument_rich.ndjson` では前者 `0.2.0` / 後者 `0.5.0` で**実際に食い違う**
>   （2026-09-20 実測）。★ 食い違いが読めること自体が封筒の目的なので、
>   `envelope-acceptance.sh` AC8 が**同じ値になったら赤**にする。
> - ⚠️ **生成時刻は載せない**（判断 7）。★ 載せると「同じ入力から同じ出力」を検査できなくなる。
>   回帰は AC9（2 回実行してバイト単位で一致）。
> - ★ **acceptance 8 本すべて**を 1 度だけ書き換えた（判断 8・取得時に `jq '.rows'`）。
>   ★ merge 済み 6 本（001 / 002 / 003 / 005 / 007 / 008）が**実測で緑**。
>   ⚠️ 004 / 006 は blocked のままだが、**「配列が来ない」ではなく自分の Tier 未実装で赤**である
>   （2026-09-20 実測）。
> - ★ 検査: `.steering/20260920-envelope-issues/envelope-acceptance.sh`
>   （⚠️ 突然変異 6 種で赤になることを実測済み・同 `measurements.md`）。

- **起票日**: 2026-09-15（★ `security-checker` 指摘 M2 の後半）
- **中身**: `--features` の出力はトップレベルが **`FeatureRow` の配列**であり、
  セッション単位の事実（`capabilities` / `app_version` / OS / fixture 名）を持たない。
  → ⚠️ 複数セッションの出力を結合したとき、**どの行がどの計器条件で取れたか**が失われる。
- **本タスクで閉じない理由**: ★ 出力形状の変更は **002〜007 の全 `acceptance.sh` の前提**
  （`jq 'all(.[]; ...)'` が配列を仮定している）を壊す。
  ⚠️ 途中で変えると走り終えた issue の検査が全部無効になる。
- **★ 次に何をするか**: ★ **issue 007 が `quality` を行に載せ終えてから**、
  「行ごとに持つ」か「封筒に出す」かを 1 度だけ裁定する
  （⚠️ 007 の `quality.capabilities` は**行ごと**なので、封筒にすると二重になる）。

---

## 起票 3: ⚠️ `permission_denials` の中身が依然未検証 —— ★★★ **2026-09-20 に閉じた**

> ★ **研究者判断 2026-09-18（判断 25 #4）**: 次に Loop を回す前に直す。⚠️ worker の transcript は `~/.claude/projects/C--wt-GSE-prototype-<id>-issue/*.jsonl` に残る。
>
> ### ★★★ 閉じた（2026-09-20・`.steering/20260920-loop-foundation-fixes/`）
>
> - ★ **実スキーマを実測した**（`measurements.md` M1b）:
>   `{"tool_name":"Bash","tool_use_id":"...","tool_input":{"command":"...","description":"..."}}`
>   ⚠️★★★ **拒否はすべて `tool_name == "Bash"` になる**ので、
>   ★ **`.tool_name` だけ集計しても「何が拒否されたか」は分からない**（★ 本起票の核心はここだった）。
>   → ★ 集計キーを **`.tool_input.command` の先頭 2 語**にした。
> - ★ `loop-run.sh` が events の `detail` に `[Bash(git checkout)x1 Bash(git push)x1 WebFetch x1]` の形で内訳を書く。
> - ★ 生の `permission_denials` 配列を `$TASK_DIR/_loop-artifacts/<id>-attempt<N>-denials.json` に残す。
> - ⚠️★★★ **本起票が書いていた「`WORK_TMP` に保存する」は成立しない** ——
>   `loop-run.sh` の `trap cleanup_tmp EXIT` が run 終了時に `rm -rf` する（★ 2026-09-20 に一次で確認）。
> - ★ 検査: `scripts/loop-run-guard-test.sh` の D1（⚠️ 突然変異で赤になることを確認済み）。
> - ⚠️ **「非致命」の扱いは変えていない** —— ★ `events_path` が worktree の cwd 境界外にあるため
>   **必ず 1 件は拒否される**という理解は変わらない。★ ただし**今後は内訳で裏が取れる**。

- **起票日**: 2026-09-15（★ `decisions.md` 判断 8 の未決 3 を引き継ぐ）
- **中身**: Loop モードC は `permission_denials=N` を件数だけ events に残す。
  ★ issue 002 の 6 attempt では **1 / 2 / 5 / 10 件**が記録されたが、**何が拒否されたかは分からない**。
  ⚠️ events_path が worktree の cwd 境界外にあるため「必ず 1 件は出る」ことは分かっているが、
  ★ **10 件の内訳は説明できない**。
- **★ 次に何をするか**: `scripts/loop-run.sh:342` の `res` を `WORK_TMP` に保存する改修を先に入れる。
  ⚠️ それまでは「非致命」という扱いの妥当性を**確かめていないまま使っている**と承知する。

---

## 起票 4: ⚠️ `preflight_dag` の文言が誤診を誘う ＋ merge 済み依存を扱えない

- **起票日**: 2026-09-15（★ `decisions.md` **判断 15** から）
- **中身**:
  1. ⚠️ `scripts/loop-run.sh:435-448` は依存先が **`--issues` の選択に入っていない**とき、
     逐語「**issue NNN の依存 MMM が issues/ に存在しません**」と言う。
     ★ しかし **ファイルは存在する**。→ ⚠️ **誤診を誘う**（★ 実際に 1 度誤読しかけた）。
  2. ⚠️ `deps_met` は `issue_done` **イベント**でしか満たされないので、
     ★ **merge 済みでも events に行が無ければ依存が満たされない**（★ 002 がそれ）。
- **なぜ効くか**: ★ `loop-run.sh` は issue 間で merge しないため、
  **1 issue ずつ回して人が merge する**のが唯一正しい運用になる。
  → ⚠️ その運用では `--issues` が常に 1 件なので、**箇条書きの依存は必ず die する**。
  ★ 結果、`## Dependencies` の機械的な門を**全 issue で外さざるを得なかった**（判断 15）。
- **★ 次に何をするか**（⚠️ 本タスクの範囲外・Loop 基盤の改修）:
  - ★ 文言を「依存 MMM が今回の `--issues` 選択に入っていません」に直す。
  - ★ 「**merge 済みの依存を満たされたものとして扱う**」手段を足す
    （⚠️ ただし **events を手で書かせる形にしない** —— モードC の原則を壊す）。
  - ⚠️ あるいは `loop-run.sh` に **issue 間の merge ゲート**を持たせるかを裁定する
    （★ そうすれば DAG が本来の意味で機能する）。

---

## 起票 5: ⚠️★★★ 「`--features` 出力を共有しない」に**機械的な門が無い** —— ★★★ **2026-09-20 に閉じた**

> ★ **研究者判断 2026-09-18（判断 25 #14）**: 起票 2 の封筒 issue で「共有しない」を封筒に刻む。
>
> ### ★★★ 閉じた（2026-09-20・`.steering/20260920-envelope-issues/`）
>
> - ★ **封筒に刻んだ**（判断 5）: `provenance.sharing` =
>   `{ "gse_dataset": "prohibited", "anonymized": false, "absolute_epoch_ms": true, "rule": "docs/glossary.md 特徴行" }`。
>   ★ 「共有するな」だけでなく、⚠️ **なぜ共有できないか**（匿名化を通っていない・絶対 epoch）を
>   出力自身が持つ。⚠️ **真偽値 1 つにしなかった** —— `false` が書ける形は
>   「共有してよい `--features` 出力がありうる」と読まれるため。
> - ★ **門を置いた**: `scripts/check_no_feature_output.sh`。
>   判定は **(a) `sharing` マーカー** と **(b) 封筒を剥がした行の形**（`t_ms` ＋ `activity` ＋
>   `boundary` ＋ `dispersion` ＋ `stall_onset` の 5 キーを持つオブジェクトの配列）の
>   **2 本立て**で、どちらか 1 つでも当たれば赤（判断 6）。
>   ⚠️★★★ **ファイル名を 1 つも見ていない**（★ 起票 5 の逐語「名前依存なので代替にならない」）。
> - ★ CI に載せた: `ci.yml` の `frontend-check` に `--self-test` と本走査の 2 ステップ。
> - ⚠️★★★ **初版の検査器は陽性対照 P2 を通していた**（2026-09-20 実測）——
>   `[ .. | select(A) ] | length > 0 or (...)` と書くと jq が `|` を `or` より弱く結び、
>   ★ **2 本目が元の文書ではなく 1 本目の結果を入力に取っていた**。
>   → ★ `def` に包んで直し、**その穴を `--self-test` の P2 として恒久化**した
>   （⚠️ 壊した版を回すと P2 / P3 が赤になることを実測済み）。
> - ⚠️★★★ **本筋の一部は残っている** —— 起票 5 が書いた「`gse-dataset` 側に feature row 形の
>   JSON が無いことを **CI で** 見る」は**達成していない**。
>   ★ 理由（2026-09-20 に一次で確認）: **`gse-dataset` に `.github` が無く CI が存在しない**。
>   → ★ 同じ script を `--root <gse-dataset のクローン>` で**手で**回せるようにし、
>   手順を `docs/verification-runbook.md` に置いた。⚠️ **自動では走らない。**
>   → ★ 向こうに workflow を新設するかは**別リポの作業**として `next-session` に残す。

- **起票日**: 2026-09-15（★ issue 003 の `security-checker` 指摘 M1）
- **規約は在る**: `docs/glossary.md:223` 逐語
  「★ **中間成果物であり `gse-dataset` へは共有しない**」。
  ★ 実装も規約どおりで、`bin/replay.rs` の `--features` は **stdout に書くだけ**（ファイルを作らない）、
  `scripts/build_analysis_db.py` は `.metrics.json` しか読まない。
  → ★ **issue 003 の diff は規約に違反していない。**
- ⚠️ **問題は門が無いこと**（★ 実測で確認）:
  - `.gitignore` は **集計 JSON を意図的に対象外**にしている（逐語「集計 JSON (metrics/calib/cohort.json) は対象外」）。
  - ★ `git check-ignore` の実測: `feat.json` / `features.json` / `src-tauri/rows.json` /
    `experiments/x/feat.json` は **4 つとも NOT ignored**。
  - ⚠️★★★ **NDJSON の保護も名前依存である** —— ★ パターンは `gse_*.ndjson` /
    `P[0-9]*_*.ndjson` なので、**`out.ndjson` は NOT ignored**（★ 実測。
    ⚠️ 「NDJSON は守られている」と一般化して読まないこと）。
- ⚠️ **`T1a` で中身の機微度が上がった**: 002 までは件数・カテゴリ件数だったが、
  いま同じファイルに **ms 粒度の pause 長 ＋ セッション全体を横断する個人統計（`surprise`）**が載る。
  ★ かつ `t_ms` は**絶対 epoch のまま**で、**`anonymize.rs` を一度も通らない**。
- **★ 次に何をするか**:
  1. ✅ **実施済み（安価な側）**: `--features` の usage に
     「**手元の解析用中間成果物であり gse-dataset へ共有しない**」
     「**`t_ms` は絶対 epoch ms で匿名化を通っていない**」を明記した。
  2. ⚠️ **未実施（本筋）**: `glossary.md:223` の規約を**検査器にする**
     （★ `gse-dataset` 側に feature row 形の JSON が無いことを CI で見る）。
     ⚠️ `.gitignore` に慣用ファイル名を足すのは**名前依存なので代替にならない**。
- ⚠️ **起票 2（由来の封筒）と一緒に裁定するのが自然**（★ どちらも `--features` の出力契約の話）。

---

## 起票 6: ⚠️ 削除区間（redaction）の長さが `pause_max_ms` に現れる

- **起票日**: 2026-09-15（★ issue 003 の `security-checker` 指摘 L4）
- **中身**: `feat_offline/mod.rs` の共有ヘルパ doc は逐語
  「**`feat` 行の穴（削除区間・一時停止・計器欠損）を知らない**」
  「本関数を素通しで使うと**被験者が削除を求めた位置に必ず onset が立つ**」と警告しているが、
  ★ これは **issue 005 宛て**に書かれていた。
  ⚠️ ところが `T1a` も同じ `extract_pause_resumptions` を素通しで使うので、
  **削除後の NDJSON を入力にすると削除区間の前後が 1 本の巨大 pause として接続され、
  その長さが `pause_max_ms` に出る**。→ ★ **005 だけの課題ではなく、003 で既に顕在化している。**
- ★ **規約違反ではない**（⚠️ 情報は増えていない）: 削除後の NDJSON を読めば同じギャップが見えるし、
  **原因ラベルは付いていない**ので `data-privacy` ルール 6「何を消したかは書かない」に抵触しない。
- **★ 次に何をするか**: ⚠️ **issue 005 が「穴の有無で条件 B の連続を切る」を実装するとき、
  `T1a` にも同じ扱いが要るかを判断する**（★ 005 の設計が決まってから）。
  ⚠️ **原因ラベルを作る方向で直さない**（ADR-030 却下リスト 9）。

---

## 起票 7: ⚠️★★★ `T1a` の分位点が**構造的に退化している**（★ 集約窓は事前宣言事項なので裁定を上げる）

> ★ **研究者判断 2026-09-18（判断 25 #11）**: 集約窓は **P1 前の事前宣言文書で** `W` / `q` / `B` と一緒に決める。それまで現状の注記と検査を残す。

- **起票日**: 2026-09-15（★ issue 003 の `code-reviewer` **HIGH-1**）
- **何が起きているか**（★ 証明 ＋ 実測。⚠️ 推測ではない）:
  - `features::PAUSE_THRESHOLD_MS` = **2000ms** > `loop_step::ENGINE_TICK_MS` = **1000ms**。
  - pause は**再開側の press が属する tick** に帰属する（`feat_offline/mod.rs` のモジュール doc）。
  - ★ 同じ tick に終わる pause が 2 本あると仮定する。再開時刻を `t1 < t2` とすると
    同一 tick なので `t2 - t1 < 1000`。ところが `t2` で終わる pause の開始は `t1` 以降の press なので
    `gap(t2) <= t2 - t1 < 1000 < 2000` となり、**`gap(t2) >= PAUSE_THRESHOLD_MS` に矛盾する**。
  - → ★★★ **1 tick に pause は高々 1 本。** よって
    **`pause_p50_ms` / `pause_p90_ms` / `pause_max_ms` は常に同値**である。
  - ★ **実測（`tests/fixtures/` の 14 本すべて）**: `activity.pauses > 1` の tick は **0 件**、
    `p50 != max` の行も **0 件**。
- **なぜ効くか**:
  - ⚠️ **3 フィールドのうち 2 つが情報を持たない。**
  - ⚠️ `issues/003.md` **AC3** の不変式 `p50 <= p90 <= max` は
    **等号でしか成立せず、検出力がゼロ**である（★ 緑に見えて何も検査していない）。
  - ★ `ADR-030 D10` の `T1a` ＝「**分布**・個人相対（p50 / p90 / max・CV・個人基準からの逸脱）」が、
    **`decisions.md` 判断 2（出力単位 = 1 Hz tick）と噛み合っていない**。
    ⚠️ D10 は「`key` 行が 1 打鍵ごとに `t` を持つので **pause 長の分布を完全復元できる**」を
    `T1a` の前提に置いているが、★ **行の粒度がその分布を潰している**。
- ⚠️★★★ **本セッションでは値を決めなかった。理由を明記する**:
  - ★ 直し方は**集約窓を決める問題**である。⚠️ **窓長は事前宣言 (pre-registration) 事項**であり、
    `ADR-030 D4` が `W` / `q` / `B` を「**P1 前に事前宣言する**」と定め、
    `issues/005.md` は逐語で「**`W` / `q` / `B` の値を決めること**」を **Scope Out** にしている。
    → ★★★ **`T1a` の窓だけ裁定セッションが独断で決めるのは、同じ規律を片側だけ破ることになる。**
  - ⚠️ かつ `docs/preregistration-v0.3.md` が凍結された合否契約を持つので、
    ★ **研究者の承認なしに解析窓を足さない。**
- **★ 選択肢（⚠️ 研究者が選ぶ）**:
  - **(a) `T1a` だけ集約窓を広げる** —— ★ 例: 末尾 30 秒のローリング窓（`features.rs` の既存の窓と同じ長さ）。
    ★ 因果的（後ろ向きにしか見ない）で、**1 行 1 tick は保たれる**ので判断 2 も他の issue も壊れない。
    ⚠️ ただし `features.rs:129` の `30_000` は**名前の無い生リテラル**なので、
    採るなら**判断 7 と同じ型の命名リファクタ**（`pub const` 化）が先に要る。
  - **(b) `p50` / `p90` を落とす** —— ★ `T1a` を `pause_max_ms`（= その tick の唯一の pause 長）＋
    `iki_cv` ＋ `surprise` に絞る。⚠️ **D10 が名指しした項目を削ることになる。**
  - **(c) 判断 2 を見直す** —— ⚠️ **影響が全 issue に及ぶ**ので最後の手段。
- **★ いま入れてある暫定の扱い**（⚠️ 放置していない）:
  - ★ `dispersion.rs` の `Dispersion` の doc に**証明と実測を書き、「分布の要約として読むな」と明記**した。
  - ★ `003-acceptance.sh` に「**現状 3 値が同値であること**」を固定する検査を入れた。
    ⚠️ **(a) / (b) の裁定が入ったら、この検査を先に書き換えること。**
- **⚠️ 併記すべき関連指摘**（★ `code-reviewer` MEDIUM）:
  - `surprise` は pause を含む行で **`pause_max_ms` のアフィン変換にほぼ一致する**（共線性）。
    ★ 実測: `resumption_outcomes` の非 null 7 行中 6 行が `keys=1` ＝ tick 内 IKI が 1 件なので、
    `tick_mean` ≡ pause 長であり `surprise` はその線形写像そのもの。
    → ⚠️ `ADR-030` の block ablation で「`T1a` 一群」の増分を測ると、
    **実質 1 本の信号（pause 長）を重複計上する。**★ ablation 設計に明記が要る。
  - `surprise` は **tick 内 IKI 件数 n に依存して尺度が揃わない**（`keys=1` の行と `keys=20` の行を
    同じ尺度で読めない）。⚠️ ★ `code-reviewer` 自身が「手元 fixture が小さく**実証はできなかった**」と
    明記しているので、**断定しない**。★ (a) の裁定と併せて検討する。

---

## 起票 8: ★ pause の「対の突き合わせ」が 2 か所に複製されている → **issue 005 で一本化する**

- **起票日**: 2026-09-15（★ issue 003 の `code-reviewer` MEDIUM）
- **中身**:
  - `boundary::pause_boundary_pairs`（002）と `dispersion::pause_durations`（003）が、
    ★ **同一の 15 行の走査**（sorted press を左から歩き、`extract_pause_resumptions` の
    出力と値一致で対応づける）を**別々に持っている**。
  - ⚠️ さらに `feat_offline/mod.rs` は**同じ press 列に対して sort ＋ pause 抽出を 3 回**
    独立に行っている（`press_intervals` / `pause_boundary_pairs` / `pause_durations`）。
    → ★ **3 か所が drift しうる。**
- **⚠️ 今すぐ共通化しない理由**（★ `code-reviewer` の判断に同意した）:
  ★ **issue 003 の Allowed Files に `boundary.rs` が無い**ので、003 で抽出するのは Allowed Files 違反。
  → ★ **`boundary.rs` と `dispersion.rs` の両方を Allowed Files に持てる issue 005 で
  `pause_events()`（`resuming_ts` ＋ `gap_ms` ＋ prev/next カテゴリ）へ一本化する**のが正しい。
  ⚠️ 005 は `stall onset` で**同じ対の情報を要する**ので、そこが自然な集約点である。
- **★ 005 への申し送り（⚠️ 忘れると 3 か所目が増える）**:
  1. ★ **走査の正しさを支える不変式を明文化する** —— 現状どこにも書かれていない:
     「**`extract_pause_resumptions` が返す resumption は、同値 run の先頭であり、かつ昇順である**」。
     ⚠️ これが崩れると 3 か所すべてが黙って壊れる。
  2. ★ 一本化したら **002 / 003 の単体テストがそのまま通ること**を確認する
     （⚠️ 特に `dispersion::tests::pause_durations_pairs_gap_with_resuming_ts` の
     同時刻重複ケースと、`boundary::tests::duplicate_timestamps_do_not_misalign_pairs`）。
  3. ⚠️ **mutation で検出力を確かめてから**一本化する（★ 判断 16 の HIGH-2）。

---

## 起票 9: ⚠️★★★ issue 004 (`T1c` revision topology) の `rewrite` / `redelete` / `loop_depth` / `local_recurrence` — 演算的定義がリポジトリ内に無い（★ issue 自身の Stop Condition に該当・実装せず停止）

> ★ **研究者判断 2026-09-18（判断 25 #10）**: **理論レビュー（CORE-CS / 修正の理論）で扱い、004 は保留を続ける**。
>
> ★★★ **2026-09-19 追記（判断 26）**: 算出式と名前は理論レビューで**確定**し、issue 004 の Background へ転記した。⚠️ 走りの切れ目・重複率の式・tick への帰属・走りの最小の長さ（U1〜U4）は**実装フェーズで決める**。

- **起票日**: 2026-09-15（★ `/loop-issue 004` attempt 4、実装前の一次資料確認で発見）
- **経緯（★ 一次資料で確認）**:
  - `_loop-events.jsonl` の実測: `issue":"004"` は **attempt 1〜3 がすでに `acceptance_fail`**
    （fingerprint はそれぞれ別: `4aea54bf…` / `79592cf9…` / `9ddc17b2…`）。★ 原因ログは
    起票 3 の通り保存されない仕様なので、失敗理由そのものは特定できない。
  - ⚠️ しかし `issues/004.md` の `## Stop Conditions` は逐語で
    「**`rewrite` / `loop depth` の定義が本文なしでは一意に決まらないとき → 定義候補を 2〜3 出して止める
    （推測で 1 つ選ばない）**」と明記しており、attempt 4 の着手前にこの条件を検査したところ
    **該当することが判明した**。
- **確認した一次資料（★ 定義が「無い」ことの証拠）**:
  - `docs/adr/ADR-030-stall-onset-and-decision-episode.md` D11: `T1c` の 5 項目
    （`delete run` / `rewrite` / `再削除` / `loop depth` / `局所 recurrence`）を**「計器変更不要」と
    分類するのみ**で、演算的な定義は書かれていない。出典は `.idea/survey:189` とされるが、
    ★ `.idea/` は本 repo に存在しない（`Glob .idea/**` = 0 件）——研究者の私的資料であり
    **worker からは参照不可能**。
  - `requirement.md:18` / `design.md:33-34` も同様に**名前と JSON 形だけ**を示し、算出式を持たない。
  - `decisions.md` / `_issue-plan.md` / `_codex-preplan.md` の grep も**演算的定義 0 件**
    （fixture 差し替え（判断 13）は `delete_runs` の非退化検査の話であり、
    `rewrite` 等の定義そのものには触れていない）。
  - → ★★★ **`delete_run_max` / `delete_runs` の 2 項目だけは「連続する削除の走り」として
    一意に読める**（AC2 の「手計算と一致」・fixture コメントの「連続 2 打以上」とも整合）。
    ⚠️ **残る 4 項目（`rewrite_count` / `redelete_count` / `loop_depth_max` / `local_recurrence`）は
    一意に決まらない**。
- **なぜ「本文を参照せずに定義する」制約 (AC3) だけでは絞り込めないか**:
  AC3 は「引数が `KeyCategory` と時刻だけ」を要求するのみで、その 2 つから**どの集約規則**
  （burst の切り方・alternation か nesting か・window の取り方）を採るかは規定しない。
  以下のとおり、同じ入力に対して**異なる出力を返す複数の読みが両立する**
  （= 「唯一の妥当な読み」に収束しない。実測: 簡単な `D I D I D` 系列で試算すると
  alternation 数 = 4、push/pop 深さ = 1 と**候補間で値が食い違う**）。

  | 項目 | 候補 A | 候補 B | 候補 C |
  |---|---|---|---|
  | `rewrite_count` | **隣接再開**: 削除の走りの直後の 1 press（時間間隔を問わない、系列上の隣）が text-producing なら 1 カウント | **同一 burst 内再開**: `extract_pause_resumptions` が切る burst の中で、削除の走りの後に text-producing press が 1 件以上あれば 1 カウント（pause SSOT を再利用） | **net 回復**: 削除の走り後、次の削除の走り（または burst 終端）までの `net_production` が 0 以上に戻ったら 1 カウント（`net_production` ヘルパを再利用するが「区切り」を新規定義する必要がある） |
  | `redelete_count` | burst 内で 2 本目以降に現れる削除の走りをすべて計上（候補 B の burst 定義に依存） | 削除の走りの直後に text-producing が**ちょうど 1 件だけ**挟まって再び削除の走りが来た場合のみ計上（A よりきつい） | burst 境界を使わず session 全体で「直前の削除の走り後に net が正に回復しないまま次の削除の走りが来た」場合を計上（burst に依存しないぶん、tick 帰属規則が他 Tier と非対称になる） |
  | `loop_depth_max` | **alternation 数**: burst を `{D=delete run, I=insert run}` の 2 記号に圧縮した run-length 列の遷移回数 | **alternation 数 ÷ 2 (pair 数)**: 候補 A を D→I の完了ペア数として数え直したもの | **push/pop 深さ**: delete run で +1・text-producing の run で -1（0 未満に沈まない）とする累積カウンタの burst 内最大値。★ 候補 A/B とは**別の概念**であり、同じ入力で異なる数値になる（本文中の試算参照） |
  | `local_recurrence` | tick 内で KeyCategory bigram が重複する割合（window = 既存 tick grid、新規定数不要） | burst 内（pause SSOT の区切り）で同様の重複割合を出し、resuming tick に帰属 | `redelete_count > 0` を 0.0/1.0 にキャストしただけの縮退値（★ これは `redelete_count` と冗長になるため、3 候補の中では**採用に値しない**候補として明示的に却下する） |

- **なぜここで止めるのが正しいか（★ 推測で 1 つ選ばなかった理由）**:
  1. issue 自身の `## Stop Conditions` が該当ケースを名指ししている。
  2. 4 候補軸（burst 切り方 / alternation か nesting か / 隣接か net 回復か / window の単位）は
     互いに独立で、組み合わせ次第で `rewrite_count` 等の値が変わる——
     「唯一の自然な読み」に絞り込めない。
  3. **3 回の推測実装がすでに `acceptance_fail` で終わっている**（budget 6 attempt 中 3 消費済み）。
     ★ ここでさらに 4 回目の推測を重ねるのは `decisions.md` が記録した
     「issue 002 で実際に $5.7 を捨てた失敗様式」の再演になる。
- **★ 次に何をするか（研究者判断が必要）**:
  1. 上表 4 項目 × 各 2〜3 候補から、研究者が採用案を選ぶ（または別案を示す）。
  2. 選定結果を `decisions.md` に判断として記録し、`issues/004.md` の Background に
     算出式を明記してから `/loop-issue 004` を再実行する。
  3. ⚠️ **`.idea/survey:189` に算出式が実在するなら、その抜粋を issue に転記する**のが
     最短（★ worker はそのファイルを読めないため、転記なしでは同じ壁に当たる）。
- **本タスクで閉じない理由**: 定義確定は「本タスク（Tier 実装）」の外側にある研究者判断であり、
  `docs/loop-engineering.md` の Stop Condition「要件が曖昧 (AC を確定できない)」に直接該当する。

### ★★★ 裁定セッションによる追記（2026-09-15・⚠️ worker が読めなかった一次資料を確認した）

⚠️★★★ **worker の「`.idea/` は参照不可」は正しいが、理由は「存在しない」ではない。**

- ★ `.idea/` は **ローカルディスクに実在する**（`C:\GSE-prototype\.idea\`・20 ファイル）。
  ⚠️ **gitignore されている**ので、**worktree には 1 バイトも現れない**
  （★ `git worktree add` は追跡ファイルしか持って行かない）。
  → ★ **worker からは構造的に読めない**（★ 権限の問題ではない）。
- ★ 該当ファイルは `.idea/20260910-mhd-feature-work-behavior-literature-gap-survey.md`。
  `ADR-030` が引く `.idea/survey:189` は**その 189 行目**である。

★★★ **裁定セッションが実際に読んだ結果（⚠️ 推測ではない）** —— 189 行目の逐語:

```text
| T1c | revision topology | delete run、rewrite、再削除、loop depth、undo/redo 往復、局所 recurrence |
```

→ ⚠️★★★ **算出式は書かれていない。候補の *名前の一覧* である。**

- ★ 前後（§6.1 の Tier 表・§6.2 第一仮説）にも演算的定義は無い。
- ★ §17.3「追加するならこの形に限定する」に「**transition count と recurrence**」という
  記述はあるが、⚠️ これは**オンラインで作ってよい特徴の類型**を述べたもので、
  `loop_depth` / `local_recurrence` の**式ではない**。
- → ★★★ **worker の「次に何をするか 3」（`.idea/survey:189` の抜粋を転記するのが最短）は
  *実行できない*。** ⚠️ **転記すべき式が存在しない**ので、この経路は閉じた。

★ **したがって本起票は「資料を探せば解ける」ものではなく、研究者が定義を *作る* 案件である。**
⚠️ ★ `delete_run_max` / `delete_runs` の 2 項目だけが一意に読める、という worker の切り分けは
**追認する**（★ AC2 の「手計算と一致」と整合し、fixture も 3 連の走りを持つ）。

**★ 裁定（2026-09-15・`decisions.md` 判断 17）**: ⚠️ **issue 004 は保留し、実装しない。**
★ 005 / 006 / 007 は `revision` に依存しない（★ 005 は `net_production`、006 は `t0`、
007 は `capabilities` を要る）ので、**先に進める**。
⚠️ **部分実装（2 項目だけ）もしない** —— ★ AC1 が 6 フィールドを要求しており、
半分の Tier を出力に載せると**後から足すときにキー集合の検査を 2 度書き換える**ことになる。

---

## 起票 10: ⚠️★★★ worker が `git checkout main` で **worktree 隔離を自分で外せた**（★ 実測）—— ★★★ **2026-09-20 に閉じた**

> ★ **研究者判断 2026-09-18（判断 25 #4）**: 次に Loop を回す前に直す（ブランチ検査・worktree 内の `git checkout` / `git switch` の遮断）。
>
> ### ★★★ 閉じた（2026-09-20・`.steering/20260920-loop-foundation-fixes/`）
>
> **★ 境界はブランチ検査に置いた**（★ 研究者が grill で裁定・判断 1 / 2）:
>
> - ★ `loop-run.sh` に `ensure_branch` を足し、**attempt 開始時**と **`run_verify` の直前**の
>   2 か所で HEAD が `loop/<id>-*` であることを確かめる。外れていたら `blocked`（fail-closed）。
>   ⚠️ **自動で戻さない** —— 未コミットの変更を別ブランチへ持ち越さないため。
> - ★ 必須 deny を **7 → 9 件**にした（`Bash(git checkout:*)` / `Bash(git switch:*)`）。
>   ⚠️ ただし**これは多層防御であって境界ではない**（下記）。
> - ★ `/loop-issue` の契約に「**worker は commit してから終わる**」を明記した（判断 5・文章のみ）。
>
> **⚠️★★★ 本起票の「次に何をするか 1」の判断を一部 *訂正* した**:
>
> - ★ 本起票は「**`allow` の `Bash(git *)` を worktree 内では絞る**。★ 後者のほうが本筋」と書いていた。
> - ⚠️ **実行できない。** `<worktree>/.claude/settings.local.json` の `allow` は
>   追跡済み `.claude/settings.json` と **union** される（★ 2026-09-20 に一次で確認）ので、
>   **`allow` を worktree 限定で狭める手段が存在しない**。
>   → ★ 狭めるには追跡ファイルを変えるしかなく、**対話セッションの権限も同時に変わる**。
>   → ★ 代わりに **worktree 限定で効く `deny`** に置いた（★ 意図は達成している）。
>
> **⚠️★★★ 実測（`measurements.md`）**:
>
> | | 条件 | 結果 |
> |---|---|---|
> | M1 | deny **7** 件で `git checkout main` | ⚠️ **通った**（`main` へ移動・拒否 0 件）＝ 本起票の再現 |
> | M2 | deny **9** 件で `git checkout main` | ★ **拒否された**（ブランチ不変・`permission_denials` 1 件） |
> | M3 | deny **9** 件で `git -C . checkout main` | ⚠️★★★ **通った**（拒否 0 件・ブランチが動いた） |
>
> → ★ **M3 が「deny は境界ではない」の実測である。**
>   ⚠️ `docs/loop-engineering.md` が「2026-09-14 時点で**未検証**」と断っていた逐語が、これで検証された。
>   ★ ブランチ検査は**到達した綴りを問わず結果（HEAD）だけを見る**ので、M3 の形も拾う。
>
> ★ 検査: `scripts/loop-run-guard-test.sh` の B1 / B2（**陰性対照**）/ B3（detached HEAD）。
> ⚠️ 実装を殺すと赤になることを突然変異 3 種で確認済み。

- **起票日**: 2026-09-15（★ issue 004 の attempt で実際に発生）
- **何が起きたか**（★ reflog の実測）:
  ```text
  92fd22f HEAD@{0}: checkout: moving from loop/004-issue to main
  bd921b6 HEAD@{1}: commit: docs(engine): issue 004 … 実装せず停止し、定義未確定を起票する
  ```
  → ★ worker は停止記録をコミットした**後**、worktree を **`main` へ切り替えて終わった**。
  ⚠️ `git worktree list` が `C:/wt/GSE-prototype-004-issue 92fd22f [main]` を示す状態になった。
- **なぜ通ったか**（★ 一次資料で確認・⚠️ 推測ではない）:
  - ★ worktree に注入される必須 `deny` は **7 件**で、実測の内訳は
    `Bash(git push:*)` / `Bash(gh pr merge:*)` / `Bash(git reset --hard:*)` / `Bash(git rebase:*)` /
    `Bash(sudo:*)` / `Bash(rm -rf:*)` / `Bash(chmod -R:*)`。⚠️ **`git checkout` は入っていない。**
  - ★ 追跡済み `.claude/settings.json` の `permissions.allow` に
    **`Bash(git *)` と `Bash(gh *)`** が在る（★ 実測）。→ ⚠️ **`git checkout` は明示的に許可されている。**
  - ★ `_loop-config.json` の `allowed_tools` にも `git checkout` は無いが、
    ⚠️ **allow 側の `Bash(git *)` が広いので効かない。**
- ⚠️★★★ **これは `docs/loop-engineering.md` が理論として書いていたことの実測である**。逐語:
  > ⚠ **この 7 件は「多層防御」であって境界ではない** (2 点とも 2026-09-14 時点で未検証):
  > - **綴りを網羅できない**。… 追跡済み `.claude/settings.json` の
  >   `allow: ["Bash(git *)","Bash(gh *)"]` に拾われる。
  → ★ **「未検証」だった側が、2026-09-15 に検証された**（⚠️ 悪意ではなく通常動作として）。
- **今回の実害**: ★ **無い**。⚠️ ただしそれは**偶然である**:
  - ★ worker は commit **後**に checkout したので、作業は `loop/004-issue` に残った。
  - ⚠️ **未コミットの変更を抱えたまま checkout していたら失われていた**
    （★ 001 / 002 / 003 の worker は**いずれも未コミットのまま終わっている**）。
  - ⚠️ かつ main checkout が `main` に居たら checkout は失敗していた（★ 今回は別ブランチだったので通った）。
- **★ 次に何をするか**（⚠️ 本タスクの範囲外・Loop 基盤の改修）:
  1. ★ **deny に `Bash(git checkout:*)` / `Bash(git switch:*)` を足す**か、
     ⚠️ **`allow` の `Bash(git *)` を worktree 内では絞る**。
     ★ 後者のほうが本筋（★ 綴りの網羅を諦める側の設計にしない）。
  2. ⚠️★★★ **より重要**: `loop-run.sh` は attempt 終了時に
     **worktree が期待どおりのブランチに居るかを検査していない**。
     → ★ `run_verify` の前に `git -C "$wt" rev-parse --abbrev-ref HEAD` が
     `loop/<id>-issue` であることを確かめ、違えば `blocked` にする（fail-closed）。
     ⚠️ これが無いと、**別ブランチの内容を verify して緑/赤を出す**ことが起こりうる。
  3. ★ 併せて「**worker は commit してから終わる**」を `/loop-issue` の契約に書く
     （⚠️ 001 / 002 / 003 はいずれも未コミットで終わり、裁定セッションが拾っている）。

---

## 起票 11: ⚠️★★★ ADR-030 D3 の修飾キー規則は `Modifier` が **Shift を含む**ので、逐語どおりには実装できない（★ ADR の定義の穴）

> ★ **研究者判断 2026-09-18（判断 25 #5 / #12）**: ★★★ **規則あり・なしの両極で挟む**（ポインタと同じ ADR-030 の手法。独立に報告し、他の極と Cartesian に組まない）。★ 実装は **ポインタ極と同じ時期（P1 の解析設計）**。ADR-030 D3 の補訂は理論レビューの中で。

- **起票日**: 2026-09-18（★ issue 005 レビュー・判断 18）
- **ADR の逐語**（D3）: 「**修飾キーが押されている間の文字キーは挿入系に数えない**」「★ 復元できる: `key` 行は press と release の両方が出る
  → ★ 修飾キーの押下区間は `key` 行だけから復元できる（新計器ゼロ）」。
- **実測**（`anonymize.rs` の `KeyCategory::from_vk`）: `0x10 | 0x11 | 0x12 | 0x5B | 0x5C | 0xA0..=0xA5 => Self::Modifier`。
  → ⚠️★★★ **Shift（`0x10` / `0xA0` / `0xA1`）が Ctrl / Alt / Win と同じ `modifier` に入る。**
- **なぜ効くか**:
  - ⚠️ 逐語どおり実装すると、**大文字・Shift で打つ記号（`!` `?` `:` など）が産出から外れる**（★ 条件 A が偽に真へ倒れ、偽の onset が増える）。
  - ⚠️★★★ **提出されるのは匿名化 NDJSON**（`category` のみ）なので、研究者側では **Shift と Ctrl を区別できない**。
    ★ raw の `vk` を持つのは被験者端末だけである。
  - ⚠️ さらに **2026-08-23 より前のログには修飾キーの行がそもそも無い**（`anonymize.rs` 逐語「旧 `is_typing_key` はこれらを 1 つも通していない」）。
    → ★ 旧ログでは規則を適用できず、新旧でθ と onset の分布が変わる。
- **★ 選択肢（⚠️ 研究者が選ぶ）**:
  - (a) **規則を撤回**し、`Ctrl+Z` 等を「既知の系統誤差」として受ける（★ D3 の残差の扱いを広げる）
  - (b) **Shift を除いた修飾キー**だけで区間を作る —— ⚠️ 匿名化の写像を変える（`modifier` を分割）＝ **ADR-014 判断 6 の再審・同意文書の再開封**（★ ADR-030 D11 の囲み「禁止の再審」と同じ種類）
  - (c) 逐語どおり（Shift 込み）で実装し、偽 onset の増分を **P1 で実測**してから決める
- **本タスクでの扱い**: ⚠️ **実装しない**（issue 008 の Scope Out）。★ `stall_onset.rs` の module doc に未実装と明記する。

## 起票 12: ⚠️ ADR-030 D3 の「IME の変換中」の抑制は、区間の定義と「抑制」の意味が決まっていない

> ★ **研究者判断 2026-09-18（判断 25 #7）**: **P1 で頻度を見てから決める**（IME 変換中に立つ onset を数える）。それまで抑制しない。

- **起票日**: 2026-09-18（★ issue 005 レビュー・`code-reviewer` H2）
- **ADR の逐語**（D3 抑制表）: 「**IME の変換中** | `ime_shadow{dwell_ms, nav, abandon}` | 候補ナビゲーションは `navigation` なので `net` が動かず条件 A が成立し続ける ＝ 偽 onset」。
- **決まっていないこと**:
  1. ⚠️ 区間の形 —— `ime_shadow` の `t` は変換の**終端**か（`[t − dwell_ms, t]` が区間になるか）。
     ★ `schema_dto.rs:300-305` 逐語: macOS の `dwell_ms` は「**1 変換分とは限らない**」（次の変換と合算される）。
  2. ⚠️ 「抑制」の意味 —— 区間中は条件 A を**評価しない**のか、**産出ありとみなす**のか、D8 (b) と同じく**連続を切る**のか。
  3. ⚠️★★★ **実効性** —— `schema_dto.rs` 逐語「**20 秒を超えたセッションは打ち切られ行が出ない（両 OS 共通）**」。
     ★ 偽 onset には「産出なしが `W`（既定 30 秒）＋ θ 続く」ことが要るので、**問題になる長い変換ほど行が出ない**。
     → ★ `ime_shadow` による抑制は**最も効いてほしい場面を覆えない**可能性がある（★ 推論。⚠️ 実データで未確認）。
- **本タスクでの扱い**: ⚠️ **実装しない**（issue 008 の Scope Out）。

## 起票 13: ⚠️ ADR-030 D3 のポインタ活動の「両極」は出力の形が決まっていない

> ★ **研究者判断 2026-09-18（判断 25 #8）**: **P1 まで極 A のみ**。極 B と `pointer_bin` の collector は P1 の解析設計と一緒に。

- **起票日**: 2026-09-18（★ issue 005 レビュー・`code-reviewer` H2）
- **ADR の逐語**: 「極 A（抑制しない）と極 B（ポインタ活動区間を抑制する）の**両方で episode 集合を作り** … ★ 独立に報告する」。
- **決まっていないこと**: ⚠️ `--features` は 1 tick 1 行・`stall_onset` は 1 列である。★ 両極を出すには
  **列を 2 本にする**か **別モードにする**かを決める必要がある（★ どちらも出力形状の変更 ＝ 全 acceptance の前提に触る）。
  ⚠️ かつ `pointer_bin` は `--features` の collector にまだ無い。
- **本タスクでの扱い**: ⚠️ **実装しない**。★ 現行の onset は**極 A（抑制しない）に相当する**と module doc に書く。

## 起票 14: ⚠️ ADR-030 D4 の小標本対策（`warmup_count` の値・`cold_start` の集団 prior・版と時点の刻印）

> ★ **研究者判断 2026-09-18（判断 25 #13）**: **P1 前に 1 本の事前宣言文書**（`docs/preregistration-v0.3.md` の追補または新版）で `warmup_count` ほかを凍結する。

- **起票日**: 2026-09-18（★ issue 005 レビュー・`code-reviewer` H3 / `security-checker` MEDIUM）
- **何が起きているか**（★ 実測）: nearest-rank で `n <= 99` なら `ceil(0.99n) = n` なので **θ は常に最大値**。
  ★ `deep_silence` の θ = 2600 は 11 件中の max、`code-reviewer` の probe では gap 2 件で θ = max。
- **決まっていないこと**:
  1. ⚠️ `warmup_count` の**値**（★ 事前宣言事項。issue 008 は `Option<usize>`・既定 `None` の器だけ作る）
  2. ⚠️★★★ 下回ったときの fallback **`cold_start`（集団 prior）が存在しない** —— ★ ADR-008 D4 の語彙だが、集団 prior を作る部品は未実装。
     → ★ 008 では「`None` を返して onset を立てない」（issue 005 Stop Condition「既定値で埋めない」）。
  3. ⚠️ 刻印（D4 表 #4 `feature_schema_version` / `profile_cutoff_time` / `coverage`）—— ★ 出力フィールドを増やすので
     **起票 2（由来の封筒）と束ねて 007 完了後に 1 度だけ裁定する**。
     ⚠️ `.idea/survey §17.3:509` は `warmup_count` を「各時点の特徴値に**付ける**」値として書き、ADR-030 D4 は**閾値**として書いている（★ 語の役割が食い違う）。
- ★ 併記: 同じ理由で **θ は ADR-008 D4 の `within_session_adaptive`（探索的結果としてのみ報告）に当たる**。⚠️ 出力に出所が載っていない（→ 起票 2）。

## 起票 15: ⚠️ `hole_gap_ms`（`feat` 列の穴とみなす間隔）の値

> ★ **研究者判断 2026-09-18（判断 25 #6）**: **仮の値（2 tick）のまま、削除 UI の最小幅 > `hole_gap_ms` を redaction 側の制約として明記・テスト固定する**。値は事前宣言文書で。

- **起票日**: 2026-09-18（★ 判断 18）
- **中身**: ★ issue 008 は既定を **`2 * ENGINE_TICK_MS`**（「1Hz の予定行が少なくとも 1 本欠けた」の構造的な下限）に置いたが、
  ⚠️ **ADR-030 は値を決めていない**。⚠️ 実データの `feat` 行間隔（負荷・スリープ復帰での遅延）の分布は**未測定**である。
- **★ 次に何をするか**: ★ P1 の実データで `feat` 行の隣接差の分布を見て、`W` / `q` / `B` と一緒に**事前宣言**する。
  ⚠️ 大きくすると削除区間の短いものが穴と判定されず、小さくすると負荷による遅延で連続が切れる（★ どちらも onset の数を動かす）。
- ⚠️★★★ **2026-09-18 追記（issue 008 `security-checker` L1・実測）**: 比較は `隣接差 > hole_gap_ms` なので、
  **feat 行が 1 本だけ欠けた場合（差がちょうど 2000ms）は区間が切れない**。★ 1 秒おきの feat 行の中で `[30,900, 31,500]` を削除すると
  消える feat 行は 1 本で、**元に無い onset が丸ごと削除区間の内側に出た**。
  - ★ **現行 UI からは到達不能**: `RecordingControls.tsx` の削除入力は `datetime-local` の**分単位**（秒を 0 に固定）で、削除幅は 60,000ms の倍数。
  - ⚠️ ただし **`delete_time_range`（`lib.rs`）は任意の ms を受ける** —— ★ **秒単位の削除 UI を足した時点で実際に起きる**。
  - → ★ 値を事前宣言するときは「**削除 UI の最小幅 > `hole_gap_ms`**」を redaction 側の制約として同時に固定すること（★ 片側だけ決めない）。

## 起票 16: ⚠️ 事前宣言した値を `--features` へ外から渡す経路が無い

> ★ **研究者判断 2026-09-18（判断 25 #13）**: 事前宣言文書を作るときに CLI 注入を作る（★ 値より先に作らない）。

- **起票日**: 2026-09-18（★ issue 005 レビュー・`code-reviewer` M3）
- **中身**: ★ issue 008 で `StallOnsetConfig` は `build_feature_rows` の引数になるが、⚠️ **`gse-replay` の本番経路は `Default` を渡す**。
  → ★ P1 前に `W` / `q` / `B` / `hole_gap_ms` / `warmup_count` を宣言しても、**CLI から注入できない**。
- **★ 次に何をするか**: ★ 値の事前宣言（起票 14 / 15）が決まった時点で、CLI フラグか設定ファイルを足す（★ `bin/replay.rs` の `--features` 経路・小さな issue）。
  ⚠️ **値が決まる前に経路だけ作らない**（★ 使われない CLI は drift する）。

## 起票 17: ⚠️★★★ issue 006（`T1d` restart）の算出式が無い（★ しかも「再停止」は転帰側の語）

> ★ **研究者判断 2026-09-18（判断 25 #9）**: **理論レビューで EVAL-NCC の「再停止」と一体に決める**。006 は保留を続ける。
>
> ★★★ **2026-09-19 追記（判断 26）**: 算出式は理論レビューで**確定**し、issue 006 の Background へ転記した。候補 A（条件 A の次の立ち上がり）を採り、`stable_generation_ms` は `r_1` を起点にした。⚠️ 集計窓（E1）・条件 A の辺の取り出し方・fixture・打ち切りの指標（V1〜V4）は**実装フェーズで決める**。

- **起票日**: 2026-09-18（★ 判断 20）
- **無いもの**: ★ 一次資料（ADR-030 D10・`.idea/survey:190`・`issues/006.md`）はすべて**名前の一覧**である。
- **★ 決める必要がある 4 点と候補**（⚠️ 研究者が選ぶ）:

  | 論点 | 候補 A | 候補 B | 候補 C |
  |---|---|---|---|
  | **集計窓** | `[t0 + B, 次の onset の s)`（★ 同じ観測区間の中で打ち切る） | `[t0 + B, t0 + B + H)`（★ 新しいパラメータ `H` を事前宣言） | `[t0 + B, 転帰の時点)`（★ ADR-029 D2 の転帰が決まってから） |
  | **`restop_ms`（再停止）** | ★ **条件 A の次の立ち上がり**（`W` の再利用・新しい定数なし・onset と対称） | `PAUSE_THRESHOLD_MS` 以上の次の pause（★ 既存 SSOT だが語間ポーズで数秒に退化する） | EVAL-NCC 草案「主課題イベントが連続 30 秒以上途切れる」（★ 課題依存・閾値未固定） |
  | **`stable_generation_ms`（安定生成）** | 再開（最初の挿入系 press）から再停止までの長さ（⚠️ `restop_ms` とほぼ同じ量になる） | 窓内で pause（`PAUSE_THRESHOLD_MS`）を挟まない最長の生成 burst の長さ | net production が正のまま続いた最長区間 |
  | **`post_t0_*` の分類** | `navigation` / 挿入系 / 削除系（★ D3 の写像をそのまま使う） | ⚠️ 修飾キー規則（起票 11）を先に決める | — |

- ⚠️★★★ **SSOT の論点**: `ADR-031` は「再停止までの時間」を**主 criterion（転帰）**に置いている。
  → ★ **`T1d` を特徴量として持つなら、転帰と同じ定義を共有する**（二重定義にしない）か、
  **`T1d` を転帰の契約（EVAL-NCC）が決まるまで待つ**かを先に決める必要がある。
- ⚠️ `T1d` は **retrospective**（`t0` の後の未来を見る）であり、issue 006 AC7 のとおり **detection 側へ渡さない**。
- **★ 次に何をするか**: 研究者が 4 点を選ぶ → `issues/006.md` の Background に算出式を書く → `006-acceptance.sh` の fixture を
  `stall_onset_observed.ndjson` へ差し替え（★ `deep_silence` は 008 以後 onset が立たない）、正解値を参照実装で確定してから回す。

---

## 起票 18: ⚠️★★★ 逸脱した worktree は `loop-spawn.sh --cleanup` で撤去できず、**「完了」と嘘の報告をする**

- **起票日**: 2026-09-20（★ `.steering/20260920-loop-foundation-fixes/` の実測 M4 で発見）
- **何が起きたか**（★ 実測。⚠️ 推測ではない）:

  ```text
  $ bash scripts/loop-spawn.sh --cleanup zzz
  loop-spawn: worktree 見つからず (既に撤去?)
  Deleted branch loop/zzz-issue (was 1bdbb24).
  loop-spawn: cleanup 完了 issue zzz

  $ git worktree list
  C:/wt/GSE-prototype-zzz-issue    b7a1cae [main]      ← ★ 残っている
  ```

- **原因**（★ `scripts/loop-spawn.sh:57` 逐語）:

  ```bash
  wt="$(git worktree list --porcelain | awk -v id="$id" '/^worktree /{p=substr($0,10)} /^branch /&&$0 ~ ("loop/" id){print p}')"
  ```

  → ⚠️★★★ **worktree を「ブランチ名」で引いている**ので、
  ★ **起票 10 の形で `main` へ逸脱した worktree は 1 件もヒットしない**。
  ⚠️ しかも **branch だけは削除され**、★ **worktree は登録に残る**。

- **実害**:
  1. ⚠️ **同じ id の再実行が恒久的に死ぬ**（`loop-spawn.sh:90`「同名 worktree が既に存在」）。
  2. ⚠️ **main checkout が `main` をチェックアウトできなくなる**（git は同一ブランチの二重チェックアウトを拒む）。
  3. ⚠️★★★ **`--cleanup` が「完了」と報告する**ので、★ **失敗が誰にも見えない**（`verify-before-claiming` の型）。
- **★ 次に何をするか**（⚠️ 本タスクの範囲外）:
  1. ★ 引き方を **パス（`../wt/<repo>-<id>-<short>`）でも引く**ように足す。
     ⚠️ ブランチ名だけに依存させない。
  2. ★ **撤去できたことを確かめてから「完了」と書く**（★ `loop-spawn.sh` の `abort_worktree` は
     既にこの作法を持っている —— 逐語「⚠️ 撤去できたかを**確かめてから**「撤去しました」と書く」。
     ⚠️ `--cleanup` 側だけがこの作法から外れている）。
- ★ **緩和済み**: ブランチ検査（起票 10 の是正）が入ったので、⚠️ **逸脱した attempt はそもそも
  `blocked` で止まる**。★ この形に到達する確率は大きく下がったが、**経路は残っている**
  （★ M3 の迂回で逸脱し、その後 `--cleanup` する場合）。

### ✅ 是正済み（2026-09-21・`.steering/20260921-loop-spawn-cleanup-fix/`）

★ **直す前に再現させた**（⚠️ 再現しないまま直して「直った」と書かない）。実測:

```text
$ LOOP_FORCE=1 bash scripts/loop-spawn.sh --no-exec zzz
$ (cd ../wt/GSE-prototype-zzz-issue && git switch -c deviated-repro-zzz)
$ bash scripts/loop-spawn.sh --cleanup zzz
loop-spawn: worktree 見つからず (既に撤去?)
Deleted branch loop/zzz-issue (was ca7764f).
loop-spawn: cleanup 完了 issue zzz     ← ⚠️ 嘘 / exit=0
$ git worktree list
C:/wt/GSE-prototype-zzz-issue ca7764f [deviated-repro-zzz]   ← ★ 残っている
```

★ **やったこと**（`scripts/loop-spawn.sh` の `--cleanup` 分岐）:

1. ★ **パスでも引く**: 一致規則を **branch 系統 ∪ path 系統**にした
   （branch = `loop/<id>` / `loop/<id>-*`、path = basename が `<repo>-<id>` / `<repo>-<id>-*`）。
   ⚠️ 併せて**部分一致の穴も塞いだ** —— ★ 旧 `$0 ~ ("loop/" id)` は正規表現の部分一致なので
   `--cleanup 005` が `loop/0055-t` にも当たっていた（★ 実測で確認）。
2. ★ **撤去できたことを確かめてから書く**: `remove` の exit code を信じず、
   worktree は**登録とディレクトリを引き直して**、branch は `show-ref` で確認する。
   ⚠️ 1 つでも残れば `⚠️ cleanup 未完了` と書いて **非 0 で終了**する。
3. ★ 付随: **main checkout を撤去しない**明示ガード、**残存ディレクトリの報告**（⚠️ 自動削除はしない）、
   **対象 0 件は exit 0**（冪等）。

### ⚠️★★★ レビューで **同じ嘘が別経路で生きていた**ことが分かった（★ 同日・同タスクで是正）

★ `code-reviewer` HIGH →★ **メインが独立に再現**した実測:

```text
$ (cd $T/wt/repo-002-t && bash $T/repo/scripts/loop-spawn.sh --cleanup 002)
loop-spawn: cleanup 完了 issue 002 (worktree 0 件 / branch 1 件 を撤去)   ← ⚠️ rc=0
$ git -C $T/repo worktree list
.../wt/repo-002-t  [deviated]      ← ★ 残っている
```

⚠️ `git rev-parse --show-toplevel` は **linked worktree の中では worktree 自身**を返すため、
`repo_name` が化けて ★ **(1) path 系統 (2) main checkout ガード (3) 残存 dir の網 が同時に無効化**されていた。
→ ★ `git worktree list --porcelain` の**先頭 ＝ main worktree** から `repo_root` を取るよう直した。

★ 併せて `security-checker` MEDIUM 2 件も閉じた:
**(a)** `git branch --list` は **fnmatch パターン**なので `--cleanup '*'` が `loop/*` に化ける
→ ★ id を `[A-Za-z0-9._-]` に限定。
**(b)** `remove --force` を無条件に撃っていた → ★ **未コミット変更があれば撤去せず人へ渡す**
（⚠️ 逸脱 worktree は作業が載っている可能性が最も高い対象である）。

★ **回帰**: `scripts/loop-spawn-cleanup-test.sh`（新規・**7 群 25 件**・CI の ubuntu / Windows 両方に配線）。
⚠️ **変異テスト付き**（path 系統を潰すと赤くなる）。
★ **旧実装に当てると 17 件 NG / exit 1** になることを 2026-09-21 に実測した
（＝ この検査は空振りしていない）。

⚠️ `scripts/loop-run.sh:204` の `detail`（逐語「`--cleanup` はブランチ名で引くので逸脱した
worktree を撤去できない」）は**この是正で嘘になった**ので、同時に書き換えた。

---

## 起票 19: ⚠️ `RUSTSEC-2026-0285`（rustls 0.23.43）—— ★ `cargo update` では上がらない

- **起票日**: 2026-09-20（★ PR #214 の `audit` ジョブが赤になって表面化）
- **中身**: `cargo-audit` が逐語
  「**RUSTSEC-2026-0285  rustls 0.23.43  patched: >=0.23.45 /
  TLS 1.3 handshake messages incorrectly accepted across encryption level boundaries**」。
- ⚠️★★★ **PR #214 の変更が原因ではない**（★ 2026-09-20 に一次で確認）:
  - 本ブランチの `Cargo.lock` 差分は **1 行だけ**（`sha2` の辺の追加）。
  - `rustls 0.23.43` は **main と完全に同一**（`git show main:src-tauri/Cargo.lock` で照合）。
  - ★ main の最終 `supply-chain.yml` 実行は **2026-09-14 に success**。
    ⚠️ 助言 DB は **2026-09-19 更新**で、★ **この助言はその後に公開された新着**である。
- ⚠️ **単純な更新では解けない**: `cargo update -p rustls --dry-run` の実測が
  逐語「**Locking 0 packages to latest compatible versions**」。
  ★ `0.23.45` が現在の制約から到達できない理由（どの依存が上限を締めているか）は**未調査**。
- **★ 次に何をするか**:
  1. ★ `cargo tree -i rustls` 等で**誰が制約しているか**を特定する
     （★ 候補: `reqwest`（`--features package` で optional）/ `rustls-platform-verifier` / `tauri` 系）。
  2. ★ 上げられるなら lock を更新し、⚠️ **MSRV check と `--features package` の clippy を再走**する
     （★ `docs/verification-runbook.md` §1 の「依存を更新した回のみ」の行）。
  3. ⚠️ 上げられないなら `.cargo/audit.toml` に **理由 ＋ 依存パス ＋ `# review-by:`** を付けて waive する。
     ★ ただし **TLS のハンドシェイク検証**に関わる案件なので、**waive の可否は研究者判断**である。
- **★ 判断（2026-09-20・研究者裁定）**: **別タスクにして PR #214 はマージする。**
  ★ 根拠: `docs/agent-shared.md` 逐語「`supply-chain.yml` は **branch protection が無いので
  門ではなく信号**であり、赤でもマージは止まらない」。⚠️ **本 PR が赤くしたのではない。**

---

## 起票 20: ⚠️★★★ `T1d`（`restart`）の**打ち切りの追跡時間**が出力に無い／E2 の過剰分割が残る

- **起票日**: 2026-09-20（★ issue 006 の実装フェーズ・`.steering/20260920-issues-004-006/decisions.md` 判断 2 / 3）
- **研究者判断が要る理由**: どちらも **`issues/006.md` AC1 のフィールド集合（7 個）を変える**話であり、
  `definitions-restop-t1d-t1c.md` §5 が逐語「足すなら **AC の改訂 ＝ 研究者判断**」と書いている。

### (a) 打ち切りの**追跡時間**（★ V4 の裁定の残り）

- ★ **実装済みの事実**: onset のある行で `restop_ms` が `null` になる経路は
  **観測区間の右端 `b` までに `s'_1` を観測できなかった右側打ち切りだけ**である。
  → ★ 「打ち切りか否か」は `stall_onset.t0_ms != null && restart.restop_ms == null` で**完全に復元できる**
  （⚠️ だから `censored` の boolean は 1 ビットも情報を増やさない。V4 で足さないと裁定した）。
- ⚠️★★★ **足りないのは追跡時間である**。生存解析（`ADR-031:52` 逐語「主 criterion: … **再停止までの時間** …」）は
  `(時間, 事象)` の組を要し、打ち切り行には **`b − o`（原点から観測の切れ目までの長さ）** が要る。
  ★ いまの出力からは `b` が読めないので、**打ち切り行を生存解析に入れられない**。
- **★ 候補**:
  1. `restart` に `follow_up_ms`（= `min(次の onset の s, b) − o`）を足す（⚠️ AC1 を 8 フィールドへ）
  2. 封筒（`provenance`）に**観測区間の列**（`[(a, b), …]`）を 1 回だけ載せる（★ 行を太らせない）
  3. 足さない（★ 解析側が `stall_onset` の `feat` 穴から `b` を再構成する。⚠️ 出力に `feat_ts` は無いので**実際には不可**）
- ★ **推奨は 2**（⚠️ 行あたりのコストが 0 で、`T1d` 以外の打ち切り議論にも効く）。⚠️ 封筒の改訂なので研究者判断。

### (b) E2（分割）の過剰分割（★ V1 の裁定の代償・[V146]）

- ⚠️ 次の onset の `s` が原点 `o` より前にあると、**集計窓が消える**（`post_t0_*` / `resumption_count` が `null`）一方、
  `restop_ms` / `stable_generation_ms` は**次の停滞に属する時間帯**を測ることがある。
- ★ これは **E1（連結）を入れれば消える**。V1 の裁定どおり **`recovery`（`progress_proxy`）の実装と同時**に入れる。
  ⚠️ それまでは「E2 の値である」と明示して読む（★ `restart.rs` のモジュール doc に書いた）。
- ⚠️ **`B` の値への感度もここに効く**: `B` が大きいほど「窓が消える」行と
  「原点で既に生成している」行（★ V6）が増える。→ ★ **判断 25 #13 の事前宣言文書で `B` を決めるときの材料**にする。

---

## 起票 21: ⚠️★★★ `008-acceptance.sh` の AC18 / AC18b は **`R = 1`**（onset が 1 本）なので、転帰側の二乗を検出できない

> ⚠️★★★ **番号の衝突に注意（2026-09-21 に気づいた）。**
> ★ 本タスクの `decisions.md` **判断 4** と `tasklist.md:42`、および
> `.steering/_handoff/next-session-loop-run-task2.md` / `next-session-loop-foundation-and-task2-slicing.md`
> が言う「**起票 21**」は、⚠️ **本ファイルのこの起票ではない** ——
> ★ **`.steering/20260914-instrument-change-arbitration/blockers.md` の起票 21（単独キー用の門・ADR-032 M11）**である。
> ★ 本起票は 2026-09-21 に**別タスクで採番された同番号**であり、中身は無関係である。
> ⚠️ **改番しない**（★ 既に main へ merge 済みで、コミットと PR #215 が本番号を指している）。
> → ★ 「起票 21」を読んだら**どちらのファイルか**を先に確かめること。

- **起票日**: 2026-09-21（★ issue 004 / 006 のレビューで `code-reviewer` H1 と `security-checker` M1 が**独立に**指摘）
- **何が問題か**: `T1d`（`restart`）は **onset の立った tick ごと**に計算されるので、
  計算量は **onset 数 `R` × 観測区間の変化点数 `C`** に効く。
  ⚠️ ところが計算量の門である AC18 / AC18b は、**どちらも onset が 1 本しか立たない**:
  - AC18: 15 万打鍵 ＋ 末尾 60 秒の沈黙 → ★ 検査自体が「onset がちょうど 1 つ」を要求している。
  - AC18b: 立ち上がりが 75,000 回（`C ≈ 15 万`）だが、**70ms 周期の churn では θ_person を満たさず**、
    確定する onset は末尾の沈黙の 1 本だけ。
  → ⚠️★★★ **`R` に比例する経路は 20 秒の門を素通りする**（★ 本 issue の初版は実際に `O(R・C)` だった）。
- ★ **本 issue でやったこと**: 実装側は `ChangeIndex`（`true` の累積和 ＋ 二分探索）で `O(R log C)` に落とし、
  **多 onset の入力で素朴な走査と一致することを単体テスト**（`restart::tests::many_onsets_match_a_naive_scan`）で固定した。
  ⚠️ **門（acceptance）は直していない** —— ★ 計算量の門は issue 008 の持ち物であり、
  20 秒の timeout をもう 1 本足すと検査時間がさらに伸びるためである。
- **★ 次に何をするか（研究者判断）**:
  1. AC18c を足す（例: 60 秒 churn ＋ 60 秒沈黙を 300 周期 → `R ≈ 300` / `C ≈ 10 万`）。⚠️ 検査時間が +20 秒。
  2. 足さず、単体テスト（上記）だけで守る。⚠️ **配線を通した実測にはならない**。
  3. `--features` に経過時間を出させ、`008` の既存 AC の中で見る（★ 新しい出力が要る）。
- ★ **推奨は 1**。⚠️ ただし `docs/verification-runbook.md` の所要時間が伸びるので、採否は研究者が決める。

---

## 起票 22: ⚠️★★★ `.codex/budget.json` の **history を切り捨てるコードが実在した**（★ 2026-09-11 の注記は誤り）

- **起票日**: 2026-09-21（★ `/cross-review` 2 巡目の記帳で**実際に 1 件消えたのを実測**した）
- **何が起きたか**（★ 実測。⚠️ 推測ではない）:
  - 日付が 2026-09-20 → 2026-09-21 へ変わった後の**最初の記帳**で、
    `today`（2026-09-20・420545 / 10 回）が history へ移り、
    ⚠️ **歴代最古の `2026-08-12`（25290 / 1 回）が history から消えた**。
  - ★ 原因は `scripts/run-codex-review.sh:256`（当時）の
    `d['history'] = sorted(...)[-30:]` —— **30 件で切り捨てる**。
- ⚠️★★★ **`.codex/budget.json` 自身の注記が真逆のことを書いていた**（逐語）:
  > 「★ 実測: history を回転させるコードは repo 内に存在しない (手作業の削除だった)。→ ★ history は append-only とし、消さない。」
  → ⚠️ **2026-09-11 のこの「実測」は誤りである。** 回転させるコードは `run-codex-review.sh` に在った。
  ★ 当時 7 件が消えた事象も、**手作業ではなくこの切り捨てで説明がつく**（⚠️ ただし当時の消え方が
  本当にこれ 1 つで説明できるかは未検証 —— ★ 消えた 7 件には `1970-01-01` など日付順で先頭に来るものが含まれる）。
- **★ 本タスクでやったこと**:
  1. `run-codex-review.sh` の `[-30:]` を**外した**（★ 注記の規則「append-only」に実装を合わせた）。
  2. 消えた `2026-08-12`（25290 / 1 回）を **history へ戻した**（★ 値は消える直前に読んだ実測値であり、推定ではない）。
- **⚠️ 残っている論点（研究者判断）**:
  - ★ `_comment_history_2026_09_11` の**本文を訂正するか**（⚠️ 「実測」と書いてある結論が誤りだったので、
    そのまま残すと次に読む人がまた同じ誤診をする）。★ 本タスクでは**本文を書き換えていない**（注記は当時の記録なので）。
  - ★ history を**無制限に伸ばしてよいか**（⚠️ 1 年で 365 件。JSON が肥大する）。
    → ★ 切るなら「切ったことが分かる形」（件数と期間を注記に残す等）にすること。

---

## 起票 20 / 21 / 22 の裁定（★ 2026-09-21・研究者判断）

### ★ 起票 20 (a)「打ち切りの追跡時間」→ **候補 2 を採用（封筒に観測区間の列を載せる）— 実施済み**

- ★ `provenance.observed_intervals`（`[{a_ms, b_ms}, …]`・**両端を含む**）を足した。
  `feat` 行が 1 本も無い入力では**空配列**（⚠️ `null` にしない —— 「観測区間が無い」は観測できた事実である）。
- ★ これで打ち切り行の**追跡時間**が `b − o` で引ける（`o = t0 + config.b_ms`）。
- ⚠️ **新しい露出ではない**: 穴の位置と長さは `rows[].quality.observability_mask.feat` が
  既に tick ごとに出している（issue 007）。★ 封筒は**セッション不変の再表現**を 1 回だけ持つ。
- ★ `envelope-acceptance.sh` の AC2（キー集合の完全一致）に 1 語足し、**AC2b**（配列 / `{a_ms, b_ms}` /
  `a_ms <= b_ms`）を新設した。`scripts/check_no_feature_output.sh --self-test` も緑のまま。
- ⚠️ **(b)（E2 の過剰分割）は開いたまま** —— V1 の裁定どおり `recovery` の実装と同時に E1 を入れる。

### ⚠️★★★ 起票 21「AC18 の穴」→ **AC18c は足さない。★ 計時では分離できないことを実測した**

★ 研究者は当初「AC18c を足す」を選んだが、⚠️ **足す前に実測したところ前提が崩れた**。
→ ★ 再裁定（2026-09-21）: **足さない**。以下の実測を残す。

| 入力 | 是正版（`O(R log C)`） | 旧実装（`O(R・C)`） |
|---|---|---|
| churn 200 対 ＋ 60 秒沈黙 × 300 周期（142,203 行・onset **300** 本・`C ≈ 120,000`） | **3 秒** | **2 秒** |
| churn 400 対 ＋ 35 秒沈黙 × 600 周期（517,803 行・onset **600** 本・`C ≈ 480,000`） | **7 秒** | **9 秒** |

- ⚠️★★★ **差が 2 秒しか出ない。** ★ `R・C = 2.88 億`でも、1 反復が非常に安い（比較 ＋ `Vec::push`）ため、
  **解析の支配項は NDJSON の parse と JSON の書き出し**であり、二次の項が表に出てこない。
- ⚠️ 分離に足る規模にすると**是正版も 20 秒に近づく**ので、CI で flaky になる。
  → ★ **計時の門でこの回帰クラスを守るのは筋が悪い**。
- ★ 代わりに守るもの: 単体テスト `restart::tests::many_onsets_match_a_naive_scan`
  （onset 60 本で**素朴な走査と値が一致**）。⚠️ **正しさは守るが、計算量は守らない**。
- ★ 副産物（実測）: 517,803 行の入力で**是正版と旧実装の出力が byte-equal** だった
  （⚠️ 是正が振る舞いを変えていないことの、fixture より強い確認になっている）。
- ⚠️ **残る穴**: 配線を通した計算量の門は無い。★ 次に `T1d` 側で二乗を入れても、
  20 秒の門では気づけない（→ この起票は**開いたまま**にする）。

### ★ 起票 22「台帳の切り捨て」→ **(i) 訂正を追記・(ii) 上限は置かない — 実施済み**

- (i) `_comment_history_2026_09_11` の**本文は残し**、末尾に訂正を追記した
  （★ ADR と同じ流儀: 本文を書き換えず、番号の新しい記述を足す）。
- (ii) `run-codex-review.sh` の `[-30:]` は**外したまま**（★ 台帳の規約「append-only」に実装を合わせた）。
  ⚠️ 肥大が問題になったら、「切ったことが分かる形」（件数・期間・合計を注記に残す）で入れ直すこと。

---

## 起票 23: ⚠️ `loop-spawn.sh` の `resolve_base` は `.steering/*/_loop-config.json` を **どれか 1 つ**拾う

- **起票日**: 2026-09-21（★ 起票 18 の**再現作業中に偶然観測**した。⚠️ 狙って探したものではない）
- **何が起きたか**（★ 実測。⚠️ 推測ではない）:

  ```text
  $ LOOP_FORCE=1 bash scripts/loop-spawn.sh --no-exec zzz
  loop-spawn: base=docs/adr-030-stall-onset-definition (start=origin/docs/adr-030-stall-onset-definition) …
  HEAD is now at ca7764f docs(steering): 次タスク（前提条件 1〜6 の確かめ方）の引き継ぎを置く
  ```

  → ⚠️ **main（`a5c53a0`）ではなく 38 コミット前の枝から worktree が切られた。**
  （★ `git rev-list --left-right --count main...origin/docs/adr-030-stall-onset-definition` = `38  0`。
   ★ 当該ブランチは main の祖先なので**分岐はしていない**。⚠️ が、**38 コミットぶん古い**）

- **原因**（★ `scripts/loop-spawn.sh:37` 逐語）:

  ```bash
  cfg="$(ls -1 .steering/*/_loop-config.json 2>/dev/null | tail -1 || true)"
  ```

  → ⚠️ **いま回そうとしているタスクとは無関係に**、`.steering/` 配下の
  `_loop-config.json` を**名前順で最後の 1 つ**拾う。★ 今回拾われたのは
  `.steering/20260914-mhd-feature-offline-tiers/_loop-config.json`（★ 現存する唯一の config）で、
  その `base_branch` は **完了済みタスクの作業ブランチ**のまま残っていた。

- **実害（★ 実測ではなく推論。⚠️ まだ踏んでいない）**:
  1. ⚠️ 新しいタスクで Loop を回すと、**前のタスクの作業ブランチから worktree が切られる**。
     ★ `loop-spawn.sh:29` の注記は逆向きの事故（pin し忘れ → main から切られる）だけを警告しており、
     ⚠️ **pin が古いまま残る**形は書かれていない。
  2. ⚠️ ブランチが**削除済み**だと `git fetch` が失敗し、`ローカル base で続行` に落ちる
     （★ そこから先の挙動は未検証）。
- **★ 次に何をするか**（⚠️ 本タスク（起票 18）の範囲外）:
  1. ★ config を**タスクで選ぶ**（＝ 引数か env でタスクを指定する / `--task` を足す）か、
     ⚠️ **複数ヒット・不一致なら止める**（fail-closed）。★ `tail -1` で黙って選ばない。
  2. ★ 併せて「解決した base がいま何であるか」を**人が承認できる形**にする
     （⚠️ 現在も `base=… (start=…)` は出ているが、★ 無人モードC では誰も読まない）。
- ⚠️ **本タスクでは直していない**（★ 起票 18 の `--cleanup` と混ぜない）。

---

## 起票 24: ⚠️ `ci.yml` の `check` job に job レベルの `permissions:` が無い

- **起票日**: 2026-09-21（★ 起票 18 の是正レビューで `security-checker` が LOW として指摘）
- **状態**: ⚠️ **未解決**（★ 本タスクでは**触っていない** —— `.steering/20260921-loop-spawn-cleanup-fix/decisions.md` 判断 10）
- **内容**: ★ `frontend-check` は `permissions: contents: read` を**明示している**のに、
  ⚠️ `check` job（ビルド / テスト / ゴールデン / clippy / Loop 基盤の検査群）には**無い**。
  → ★ リポジトリ既定の `GITHUB_TOKEN` 権限がそのまま渡る。
- **なぜ問題か**: ⚠️ 既定が read/write なら、★ **CI から repo へ push できてしまう**。
  ★ 同じ理由づけは `ci.yml` の `frontend-check` に**逐語で既に書いてある**
  （「job レベルの permissions が無いと、リポジトリ既定の GITHUB_TOKEN 権限がそのまま渡る」）。
  → ⚠️ **番人の理屈が 1 つの job にしか適用されていない**。
- ⚠️★★★ **本コミットが作った穴ではない**（★ 既存条件。2026-09-21 より前から同じ）。
- **★ 次に何をするか**（⚠️ 独立したタスクで）:
  1. ★ `check` job が **tag push / release 経路**で何を書くのかを先に確かめる
     （⚠️ 権限を絞ると別の job が**無言で壊れる**）。
  2. ★ 必要最小を `permissions:` で明示する。
  3. ⚠️ **`supply-chain.yml` 側も同じ目で見る**（★ workflow は 2 枚ある）。
