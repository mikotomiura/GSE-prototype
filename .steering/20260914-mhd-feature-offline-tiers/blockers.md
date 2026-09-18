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

## 起票 2: ⚠️ `--features` の出力に「由来の封筒」が無い

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

## 起票 3: ⚠️ `permission_denials` の中身が依然未検証

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

## 起票 5: ⚠️★★★ 「`--features` 出力を共有しない」に**機械的な門が無い**

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

## 起票 10: ⚠️★★★ worker が `git checkout main` で **worktree 隔離を自分で外せた**（★ 実測）

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

- **起票日**: 2026-09-18（★ issue 005 レビュー・`code-reviewer` H2）
- **ADR の逐語**: 「極 A（抑制しない）と極 B（ポインタ活動区間を抑制する）の**両方で episode 集合を作り** … ★ 独立に報告する」。
- **決まっていないこと**: ⚠️ `--features` は 1 tick 1 行・`stall_onset` は 1 列である。★ 両極を出すには
  **列を 2 本にする**か **別モードにする**かを決める必要がある（★ どちらも出力形状の変更 ＝ 全 acceptance の前提に触る）。
  ⚠️ かつ `pointer_bin` は `--features` の collector にまだ無い。
- **本タスクでの扱い**: ⚠️ **実装しない**。★ 現行の onset は**極 A（抑制しない）に相当する**と module doc に書く。

## 起票 14: ⚠️ ADR-030 D4 の小標本対策（`warmup_count` の値・`cold_start` の集団 prior・版と時点の刻印）

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

- **起票日**: 2026-09-18（★ 判断 18）
- **中身**: ★ issue 008 は既定を **`2 * ENGINE_TICK_MS`**（「1Hz の予定行が少なくとも 1 本欠けた」の構造的な下限）に置いたが、
  ⚠️ **ADR-030 は値を決めていない**。⚠️ 実データの `feat` 行間隔（負荷・スリープ復帰での遅延）の分布は**未測定**である。
- **★ 次に何をするか**: ★ P1 の実データで `feat` 行の隣接差の分布を見て、`W` / `q` / `B` と一緒に**事前宣言**する。
  ⚠️ 大きくすると削除区間の短いものが穴と判定されず、小さくすると負荷による遅延で連続が切れる（★ どちらも onset の数を動かす）。

## 起票 16: ⚠️ 事前宣言した値を `--features` へ外から渡す経路が無い

- **起票日**: 2026-09-18（★ issue 005 レビュー・`code-reviewer` M3）
- **中身**: ★ issue 008 で `StallOnsetConfig` は `build_feature_rows` の引数になるが、⚠️ **`gse-replay` の本番経路は `Default` を渡す**。
  → ★ P1 前に `W` / `q` / `B` / `hole_gap_ms` / `warmup_count` を宣言しても、**CLI から注入できない**。
- **★ 次に何をするか**: ★ 値の事前宣言（起票 14 / 15）が決まった時点で、CLI フラグか設定ファイルを足す（★ `bin/replay.rs` の `--features` 経路・小さな issue）。
  ⚠️ **値が決まる前に経路だけ作らない**（★ 使われない CLI は drift する）。

## 起票 17: ⚠️★★★ issue 006（`T1d` restart）の算出式が無い（★ しかも「再停止」は転帰側の語）

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
