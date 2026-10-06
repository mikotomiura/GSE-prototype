# タスクリスト

## 本タスク（評価設計と外枠）
- [x] grill で投稿先・正解の源・入力・範囲・公開・貢献・時期を確定（decisions.md 判断 1–8）
- [x] requirement.md / design.md 初版
- [x] paper-suggest.md（論文の案・タイトル案・投稿計画）と次セッションへの handoff を作成（2026-09-27）
- [x] 一次で接地が要る箇所を確認（2026-09-28）: MS（IMM 互換は文書に列挙なし → 2 経路を試す）/ Apple（呼び出し順は文書に無い・`unmarkText` は確定側）/ CPU 0.98% は無効 / BRM の規程
- [x] 研究者が design.md 初版を承認（訂正 4 点入り・判断 10）＋ 較正パイロット（判断 11）・E3 の範囲（判断 12）・CHI の開示（判断 13）
- [x] `/reimagine` 1 回目で v2 案と比較 → ハイブリッドを採用（判断 14・`design-comparison.md`）
- [x] タイトル T1・ライセンス Apache-2.0 / CC BY 4.0（判断 15）
- [x] BRM の規程（非アーカイブ発表・code availability）を確認（判断 13・design.md §4 / §5）
- [x] [P321] 2 本目の再検討（サーヴェイ 4 本 ＋ 一次の裏取り → 判断 16: 並行で進める）→ 別トラックの handoff `next-session-p321-reanalysis-paper.md`
- [x] 後続 issue を `issues/` に分解（2026-09-28・Opus・`issue-slicing`）: **27 本**（うち任意 3 本は blocked）＋ `_acceptance-lib.sh` ＋ 各 `NNN-acceptance.sh` ＋ `_issue-plan.md`（DAG・交差表・機械の割り当て・マイルストーン M0〜M13）＋ `_loop-config.json`（モード C・G-GEAR のパス）。分解の前に研究者が判断 17–21 を確定、slicer の裁定は判断 22
- [ ] ⚠️ **ループの実行は別セッション**（`/clear` → `.steering/_handoff/next-session-ime-paper-loop.md`）。W1（001）→ merge → W2 … の順（`_issue-plan.md` §4）
  - [x] base `feature/ime-eval-kit` を origin/main（afe6b0d7）から作って push（2026-09-28）
  - [x] **W1（001）**: モード C・attempt 1 で `issue_done`（6.17M トークン・$2.68）。merge ゲート（clean な checkout で acceptance 失敗 0 件・verify 3 本・変異・code-reviewer ∥ security-checker）→ 契約の指摘を研究者に問い判断 23〜26 → メインが直して `32b3fdc2` で base へ merge。`papers/.gitignore` を base に追加。詰まりは `blockers.md` B1〜B4
  - [x] **判断 25**: `plan/1` / `oracle/1` / `corpus/1` の型をメインが `FORMATS.md` に足し、研究者が差分を承認して base へ（2026-09-28）
  - [ ] W2（G-GEAR: 002 003 008 010 011 015 016 ／ Mac: 004 007）。⚠️ token_ceiling は run ごと（B4）→ 2〜3 回の run に分ける
    - [x] G-GEAR の 7 本をループで実行（2 run・parallel=1・計 $20）。`issue_done` 4 本（002 003 016 015）・watchdog の空応答で `blocked` 3 本（010 008 011）。7 本とも clean な checkout で acceptance 失敗 0 件（B5）
    - [x] レビュー 6 本（code-reviewer 4・security-checker 2）→ 判断 27〜34 を研究者に問い確定。002 / 003 / 010 は作業用エージェント（Sonnet）が直し、016 はメインが直した
    - [x] 002 003 008 010 016 を base へ merge（`c968670b`）・merge 後の base で 6 本の acceptance が緑・push
    - [x] 判断 34: 未実行の recheck 14 本を parse に・009 / 020 の依存から 008 / 010 を外す（`1ab259b2`）
    - [x] 011 / 015 の直し（HIGH あり・判断 31〜33）→ メインが独立に検証（015: 封印の大きさが行数によらず 1 MiB・開封で元の SHA-256 ／ 011: 逐語コピーが GSE と一致・lock の共通 53 crate の版の差 0）→ merge。012 / 013 / 023 / 024 の依存から 011 を外した。merge 後の base（`7ed5e6c0`）で 8 本の acceptance・selftest 11 本・compile・lint・`--against-gse` が緑 → push（2026-09-28）
    - [x] Mac: 004 / 007（2026-09-29）。前段取り: Mac の base で verify が赤（Python 3.14 で `gt_sessions.py` の入れ子の検査が通らない）→ selftest の深さを上げた・004 / 007 の依存から 001 を外した（判断 47・B10）。main checkout を別セッションが使っていたので base は別 worktree で扱った（B10）
      - [x] 1 run・parallel=1 で 2 本とも attempt 1 の `issue_done`。clean な checkout で acceptance 失敗 0 件（004 ✅ 28 / 007 ✅ 14）
      - [x] レビュー 4 本（code-reviewer 2・security-checker 2）→ 判断 48〜50 を研究者に問い確定（送出の門は Emitter に・退避先の既定をなくし前面化を読み戻す・参照入力欄は確定のたびに本文を空に）
      - [x] 直しを作業用エージェント（Sonnet）に渡し、メインが clean な checkout で acceptance を回し直し（004 ✅ 28 / 007 ✅ 14）、写しへの変異で確かめた（004: `run()` のフラグ検査を消すとバックエンドを読む前に番兵で赤 ／ 007: 本文の消去を殺すと selftest が赤）→ merge（004 `4dc39558` / 007 `d0e7ee78`）。004 の後の base を先に push（`06494ee5`）
  - [ ] W3（G-GEAR: 009 013 017 021 022 ／ Mac: 012・005 / 006 は 004 の後）
    - [x] Mac: 012（2026-09-29）: attempt 1 の `issue_done`・clean な checkout で acceptance 失敗 0 件（✅ 16・macOS で初めて単体ロガーをビルド）。レビュー 2 本 → HIGH（main queue が回らず入力ソースの問い合わせが完了しない）を判断 51 で 011 の追補として `main.rs` に入れた（`32e57125`・再現プログラムで陰性対照つきに実測）。残りの指摘は作業用エージェントが直し、メインが acceptance と変異で確かめて merge（`2a449dbf`）
    - [x] merge 後の base（`2a449dbf`）の clean な checkout で、Mac で回せる merge 済みの全 acceptance 16 本（001 002 003 004 007 010 011 012 015 016 017 018 019 021 022 028）が失敗 0 件（Windows 専用の 008 009 013 014 は exit 2 ＝対象外）・`_style_check.py` 違反 0 件 → push
    - [x] ⚠️ G-GEAR: 判断 51 で `main.rs` を変えた（macOS だけ `cfg` で分岐）→ 次の G-GEAR のセッションで 011 / 013 / 014 の acceptance を回し、Windows 側のコンパイルが壊れていないことを確かめる
      - [x] 2026-09-29（G-GEAR）: base `91289c09` の clean な checkout で 011 / 013 / 014 の cargo の項目（build・test）はすべて緑。ただし全 acceptance が `kit/check.sh` の 1 件で赤 → 004 の `emit.py` の selftest（Windows の Python 3.11 の時計が 16 ms 刻み・機械の負荷）→ 判断 52 / 53 で `emit.py` を直した（004 の追補）・判断 54 で 005 / 006 の依存から 004 を外した（B11）
      - [x] ⚠️ Mac: `emit.py` を変えたので、次の Mac のセッションで `004-acceptance.sh` を回し直す
        → 2026-09-29（Mac・Python 3.14.4）: base `af40cd12` の clean な worktree で `004-acceptance.sh` exit 0（失敗 0 件）・`emit.py --selftest --full` exit 0（48 件すべて ok・遅れの 95 パーセンタイル -0.00 ms・時計の分解能 1 ms 以下と高分解能の時計の検査も ok。`perf_counter` = `mach_absolute_time()`・`time` = `CLOCK_REALTIME` 1 µs）・`kit/check.sh` exit 0（22 本すべて緑）。`--full` なしでは遅れの上限が info 行に落ちることも確かめた
    - [x] 009: `issue_done`・clean な checkout で acceptance 失敗 0 件（✅ 16）
    - [x] 013: attempt 1 で worker が Stop（`is_observed_key` の抜粋が `crate::analysis::key_gate` を呼ぶ）→ 判断 35 でメインが 011 の追補（`key_gate.rs` の逐語コピー）を base に入れた（`dd58dd9d`）
    - [x] 013 を回し直す（止まったときの記録は `archive/ime-013-attempt1-stop` に残した）→ `issue_done`
    - [x] 017 / 021 / 022（W3b）→ `issue_done`（3 本で $12.3）
    - [x] レビュー 5 本（code-reviewer 3・security-checker 2）→ 判断 37〜41 を研究者に問い確定。014 の仕様と acceptance を判断 41 に合わせて直した（`d2f596b1`）
    - [x] 5 本の直しを作業用エージェント（Sonnet）に渡し、メインが clean な checkout で acceptance を回して確かめてから merge（013 `a63b5976` / 009 `32d40022` / 017 `f6cf6fcb` / 022 `c5309fd5` / 021 `3fef7971`）
  - [x] ★ **判断 36 の整理（issue 028）**: 機械の門 `_style_check.py`・`style_ok` を置き、6 つの束を作業用エージェントが並列で直してメインが統合（違反 2,404 → 0 件・`74a2e028`）。判断 42（`--against-gse` → `--against-upstream`・`gse_*` → `upstream_*`）。判断 43（公開物から写した元との関係の説明も除き、照合の道具を公開用 `check_manifest.py --self` と内部用 `check_manifest_upstream.internal.py` に分けた・`e2633aae`）
  - [x] W4（G-GEAR: 014 018 019 ／ 023 は 006 待ち）
    - [x] 2026-09-29: 止めていた 014 の worktree を片付けて回し直し、3 本とも attempt 1 で `issue_done`（1 run・parallel=1・13.0M トークン・$5.53）
    - [x] clean な checkout で acceptance 失敗 0 件（014 ✅ 17 / 018 ✅ 12 / 019 ✅ 11）・レビュー 5 本（code-reviewer 3・security-checker 2）→ 判断 44〜46 を研究者に問い確定
    - [x] 3 本の直しを作業用エージェント（Sonnet）に渡し、メインが clean な checkout で acceptance を回し直し（3 本とも失敗 0 件）、HIGH の直しを写しへの変異で確かめてから merge（014 `b2d7373e` / 018 `5dbacf66` / 019 `e02dc266`）。判断 44 の写した元との違いを `kit/logger/PROVENANCE.internal.md` に記録
    - [x] merge 後の base（`c5acf429`）の clean な checkout で merge 済みの全 acceptance 17 本（001 002 003 008 009 010 011 013 014 015 016 017 018 019 021 022 028）がすべて失敗 0 件・`_style_check.py` 違反 0 件（`--selftest` も緑）・入口の所要時間の警告なし → push → ループの worktree 3 本と検証用の checkout を片付けた
  - [x] W3 の残り（G-GEAR: 005 / 006）。★ 004 は base に入った（Mac・2026-09-29）。依存は判断 54 で解いた
    - [x] 2026-09-29: 1 run・parallel=1 で 2 本とも attempt 1 の `issue_done`（5.36M トークン・$2.60）。clean な checkout で acceptance 失敗 0 件（005 ✅ 19 / 006 ✅ 14）
    - [x] レビュー 3 本（code-reviewer 2・security-checker 1）→ 判断 55〜57 を研究者に問い確定（前面の確認は runner がバックエンドで・リセットは送出のフラグで門・manifest の置換＋寄託前の検査）・判断 58 はメインの判断（停止の記録を実態に）。FORMATS の reset 行の条件（001 の追補）と 020 の寄託前の検査を base に入れた（`08541088`）
    - [x] 直しを作業用エージェント（Sonnet）に渡し、メインが clean な checkout で acceptance を回し直し（2 本とも失敗 0 件）、写しへの変異で確かめてから merge（005: 4 本 / 006: 5 本がすべて赤 → 005 `9098e1ee` / 006 `5668dccd`）
    - [x] merge 後の全 acceptance で 005 の AC5（`emit.py --selftest`）が 1 回だけ赤 → 200 回で 2 回「計画より早く送った」を捕捉（B12）→ 判断 59 で送出の基準を `trial_begin` の刻印に（004 の追補・`96a19df6`・直した後は 200 回中 0 回）
  - [x] W5（020 / 023）（2026-09-29〜30）
    - [x] 1 run で 020 は attempt 1 の `issue_done`・023 は worker が Stop（AC2 と公開物の書き方の矛盾）→ 判断 60 / 61 で 023 の issue と acceptance を直し（`96a19df6`）、回し直して attempt 1 の `issue_done`（止まった記録は `archive/ime-023-attempt1-stop`）
    - [x] clean な checkout で acceptance 失敗 0 件（020 ✅ 28 / 023 ✅ 27）。レビュー 4 本（code-reviewer 2・security-checker 2）→ 判断 62〜64 を研究者に問い確定（セルの `label`〔006 の追補 `1c4b025e`〕・凍結の門・E3 は 8 時間）
    - [x] 直しを作業用エージェント（Sonnet）に渡し、メインが clean な checkout で acceptance を回し直し、写しへの変異で確かめてから merge（023: 4 本 / 020: 4 本がすべて赤 → 023 `038645a8` / 020 `82a74e22`）。020 の selftest は 56 秒 → 既定 17 秒と `--full` 29 秒に分けた
    - [x] merge 後の base（`82a74e22`）の clean な checkout で全 acceptance 21 本（G-GEAR で回るもの）が失敗 0 件・`_style_check.py` 違反 0 件 → push → 片付け（2026-09-30）
    - [x] ⚠️ Mac: `emit.py`（判断 59）を変えたので `004-acceptance.sh` を回し直す・E3 のプロセス名が 16 文字で切れるか（`ps -c -o comm= -p <pid>`）を確かめる（判断 64）
      → 2026-09-30（Mac・macOS 27.0・Python 3.14.4）: base `44241f49` の clean な worktree で、Mac で回せる merge 済みの全 acceptance 19 本（001 002 003 004 006 007 010 011 012 015〜023 028）が失敗 0 件（005 は exit 2 ＝対象外）。`emit.py --selftest --full` exit 0（49 件 ok・遅れの 95 パーセンタイル 0.01 ms）・`run_cell.py --selftest` exit 0（ok 51 件・★「a child that ignores the termination request is killed」も Mac では ok で実際に走った）・`pipeline.py --selftest --full` exit 0（9 ケース・Mac では 4 秒）・`summarize_e3.py --selftest` exit 0
      → ⚠️ E3 のプロセス名は**前提が外れた**（`pgrep -x` は 22 文字の完全な名前で照合する）→ 判断 66 で `run_e3.sh` を完全な名前に直し、023 の acceptance を回し直した
      → G-GEAR で Mac の push（`2c3a2781`）を取り込み、clean な checkout で `023-acceptance.sh` 失敗 0 件（Windows・2026-09-30）。W6 の引き継ぎ（`next-session-ime-paper-ggear-w6.md`）を更新
  - [x] W6（024: 公開 repo への書き出し）（2026-09-30・G-GEAR）
    - [x] 着手の前に研究者に 3 問 → 判断 67（絶対パスは実在の値＋名前つきの形・架空の名前の一覧だけ通す）・68（測定用のロガーは書き出しからビルド・機械によらずバイト一致）・69（逐語コピーの日本語の文字列リテラルは内部の対訳表で英訳）。issue 024 と acceptance を直し、判断 42 / 43 より前の記述を現行に合わせ、`_style_check.py` の明示パスの `*.internal.*` を対象外に
    - [x] メインが使い捨ての試作 `export.py` で acceptance を通しで検証（失敗 0 件）→ 変異で陰性対照を確かめる
    - [x] ループ（`--issues 024`）: 1 run・attempt 1 の `issue_done`（約 17 分・`a193c751`）。clean な checkout で acceptance 失敗 0 件（✅ 58）
    - [x] merge ゲート: 対訳 72 項目をメインが全件確認・レビュー 2 本（CRITICAL なし・HIGH 3）→ 判断 70 / 71 を研究者に問い確定 → acceptance に追補（陰性対照 10 本・ケース 6 つ）→ 作業用エージェント（Sonnet）が直し（`24264d40`・`d8e3f1d9`・`9cf4eac9`）→ 直した版の clean な checkout で失敗 0 件（✅ 74）・変異 7 本がすべて赤 → merge（`c6305340`）
    - [x] merge 後の base（`c6305340`）の clean な checkout で全 acceptance 25 本: G-GEAR で回る 22 本がすべて失敗 0 件（024 ✅ 74・一覧の SHA-256 `9e586e5254063ec6a27ef50971ab83557da17d0c1343bc046faa8682b8b0b3b5`・91 ファイル）、macOS 専用の 004 / 007 / 012 は exit 2（対象外）。`_style_check.py papers/ime-observation` 違反 0 件 → push → 片付け（2026-09-30）
    - [x] ⚠️ Mac: `024-acceptance.sh` を回す（macOS の専用ファイルの書き出し後の `cargo test`・一覧の SHA-256 が G-GEAR と同じ commit で一致するか〔判断 68〕）
      → 2026-09-30（Mac・macOS 27.0・Python 3.14.4）: base `8bcf2a81`（`c6305340` との差は `.steering/` だけ）の clean な worktree で `024-acceptance.sh` exit 0（✅ 74・失敗 0 件・書き出した側の `cargo test` も緑）。★ 一覧の SHA-256 は Mac `577caaff…`・G-GEAR `9e586e52…` で**不一致に見えたが、書き出しの中身は一致**: Mac の一覧を「行の区切り CRLF・末尾 LF」にすると `9e586e52…` と完全一致した → 原因は測定器（一覧を Python のテキストの stdout に書いていて、Windows で改行が CRLF になる）。判断 68 は成り立っている（B13）
      → 測定器を直した: 一覧を `sys.stdout.buffer` にバイトで書く＋一覧に CR があれば ❌ にする検査を足した。直した版は Mac で ✅ 74・失敗 0 件・`577caafffe2c0aa743f34ae1491cdaa8297d119296e72f03a42d29200936f34a`（91 ファイル）。陰性対照（一覧を CRLF で書く写し）は新しい検査で ❌ になった
      → あわせて Mac で回せる merge 済みの全 acceptance 22 本（001〜004 006 007 010〜012 015〜024 028）が失敗 0 件（Windows 専用の 005 008 009 013 014 は exit 2 ＝対象外・blocked の 025〜027 は未実装で赤）。`_style_check.py papers/ime-observation` 違反 0 件
    - [x] ⚠️ G-GEAR: 直した `024-acceptance.sh` を回し、一覧の SHA-256 が Mac と同じ `577caafffe2c0aa743f34ae1491cdaa8297d119296e72f03a42d29200936f34a`（91 ファイル）になるかを確かめる（B13・`papers/` が `c6305340` と同じ内容の commit で）
      → 2026-09-30（G-GEAR・Windows 11・Python 3.11.9）: Mac の push `b2e284e2` を取り込み（`c6305340` からの `papers/` の差は 0）、clean な checkout（`C:/wt/clean-024m`）で `024-acceptance.sh` exit 0（✅ 74・失敗 0 件）。★ 一覧の SHA-256 = `577caafffe2c0aa743f34ae1491cdaa8297d119296e72f03a42d29200936f34a`（91 ファイル）で **Mac と一致** → 判断 68（同じ commit の書き出しは機械によらず同じバイト列）を両 OS で確かめた。⚠️ 以前の G-GEAR の値 `9e586e52…` は測定器の CRLF を含んだ値（B13）で、比べる値としては使わない
  - [ ] （旧項目）判断 36 の整理の issue（W3 の後に切る）: merge 済みの W1〜W3 の `papers/ime-observation/` を学術的な英語にし、GSE への言及・★ ⚠️ を除く。acceptance が名指す日本語の文字列と GSE を指す識別子（`--against-gse` など）も同時に直す。024 の acceptance に判断 36 の検査を足す
- [x] ★ main への merge（判断 72・2026-09-30・研究者が「今日・Codex の上限を一時的に引き上げる」を選択）
  - [x] 研究者に 2 問（merge するか・凍結を公開で示す方法）→ 判断 72 / 73。M3 / M6 の Done に OSF の登録を足した
  - [x] origin/main（`c11b8b80`）を base に取り込む（衝突 2 件: 台帳は合算 546,201 / 9 回・Mac の handoff は base の新しい方）→ `c8eb467d` → push（ブランチの CI 緑）
  - [x] Codex の上限を 750,000 に一時的に引き上げ（`3ba24091`）→ /cross-review 1 巡目: code-reviewer ∥ security-checker ∥ Codex（機密フィルタが受け入れ検査の架空の値に当たり、研究者の承認で `--ack-filtered`・B14）→ CRITICAL / HIGH 0
  - [x] 研究者に 3 問 → 判断 74〜76（書き出し器を公開しない・書き出しが全規則を回す・角括弧の例外をやめる）＋ 仕様の範囲の直し (a)〜(m)。024 の issue と acceptance に追補 2（`3eb83d84`）。直す前の版（引数だけ受け取る差し替え）で既存の検査 80 件は緑・追補 2 の陰性対照 37 件はすべて赤（`9023ca30`）
  - [x] 作業用エージェント（Sonnet）が `loop/024-fix2` で直す（約 22 分）。字義どおりの (f) は実物の `pipeline.py:1481` に当たり Stop → 同じ区切り文字の連なりだけを飛ばす読みを採った（判断 77・`e6932553`）。メインが説明を直した（`d8db7a80`）
    → clean な checkout（base と merge した木）で 024-acceptance.sh 失敗 0 件（✅ 117・一覧の SHA-256 `74e48394b9ed51de505257d1791df891997a1bada1e6049fe0c6875162ee4ac0`・89 ファイル・Windows）。直しを 1 つずつ戻す変異 18 本がすべて狙った selftest のケースで赤 → base へ merge（`b33e0818`）
  - [x] /cross-review 2 巡目（直しの境界条件）: Codex ∥ code-reviewer ∥ security-checker → CRITICAL / HIGH 0 → 研究者に 1 問 → 判断 78（混ざった区切りも飛ばし、pipeline.py の selftest の架空の名前を一覧の名前に）＋ 仕様の範囲の直し (a)〜(n)（`70b4a8a8`・`192219a3`）。直す前の版で既存 118 件は緑・新しい 21 件は赤
  - [x] 作業用エージェント（Sonnet）が `loop/024-fix3` で直す（約 21 分・名前は `harry`〔`alice` は pipeline の selftest のログイン名と重なる〕）→ base と merge した木の clean な checkout で 024-acceptance.sh 失敗 0 件（✅ 139・一覧の SHA-256 `298a470b94f0fe6a5b0d953ff0b37c0420e38afaedca757b0f227e309d5ca4a0`・89 ファイル）。変異 17 本: 15 本が赤・`localhost` はケースを足して赤（`4a610eb1`）・消した対訳表は git status の削除の検出と重なる → base へ merge（`403a7933`）
  - [x] Codex の上限を 300,000 に戻した（2 巡・計 93,392 トークン・当日の合算 639,593 / 11 回）
  - [x] clean な checkout で Windows で回る全 acceptance: G-GEAR（Windows 11・`5eda5dca` の clean な checkout）で Windows で回る 22 本（001〜003 005 006 008〜011 013〜024 028）がすべて失敗 0 件・macOS 専用の 004 / 007 / 012 は exit 2（対象外）・`_style_check.py papers/ime-observation` 違反 0 件。 origin/main（`1653e8b8`）を 2 度目に取り込み（台帳の合算 800,363 / 14 回・`6b5973a4`）→ PR #276
  - [x] PR #276 の CI 緑（head `57210663`）→ merge（`2319a1cb`・2026-09-30）→ main の CI（run 36708619521）緑。続く #277 の `6bf24b59` も success
  - [x] ⚠️ Mac: 024-acceptance.sh を回し、一覧の SHA-256 が Windows と一致するか・POSIX だけの検査（読めない dir・実行権限）が緑か（判断 68）
    → 2026-09-30（Mac・macOS 27.0・Python 3.14.4）: main（`6bf24b59`・`57210663` からの `papers/` の差は 0）の clean な worktree で 024 は ✅ 140・❌ 1（SCOPE だけ・B15）。★ 一覧の SHA-256 = `298a470b94f0fe6a5b0d953ff0b37c0420e38afaedca757b0f227e309d5ca4a0`（89 ファイル）で **G-GEAR と一致**。POSIX だけの検査（(c) 読めない dir で exit 2・(j) `*.rs` に実行権限なし・`*.sh` にあり）と (g) ホスト名の陰性対照は緑
    → あわせて Mac で回せる全 acceptance 20 本（001〜004 006 007 010〜012 015〜024 028）: **SCOPE を除く失敗 0 件**。SCOPE は 028 を除く 19 本で 1 件ずつ ❌ ＝ main の上では base が定まらない測定器の適用範囲の外（B15）。`_style_check.py papers/ime-observation` 違反 0 件
- [ ] M0〜M13（`_issue-plan.md` §5）。
  - [x] M0 コーパスの確定（2026-09-30・Mac・判断 79）: 研究者の承認で新字新仮名の 12 作品を青空文庫から取得 → `--seed 1 --per-work 150`（読み 6〜30・既定）で 1,800 句・SHA-256 `c8f890cb4d0848bf04e6d7d95efe4e4d3dfd02a23eb1c7f103344f14d13e4620`・`SudachiPy==0.7.0` / `sudachidict-core==20260723.1` を `kit/corpus/requirements.txt` に pin・`--validate` exit 0・2 回の書き出しでバイト一致・`experiment/data.md` に 6 項目と出典の作品表（`fece8020`）。`kit/check.sh` 緑・書き出し器が通る（91 ファイル）・仮の config で両 OS の計画の各シナリオ 225 試行がすべて別の句
    → PR #278。⚠️ /cross-review は**研究者の判断でスキップ**（コードの変更 0 行・差分はコーパスのデータと data.md と steering）。CI: Mac の check の 1 回目は runner の通信切れ（"lost communication with the server"・手順は未実行）→ 失敗ジョブだけ再実行して緑
  - [x] M1 macOS の較正パイロット（2026-10-01・Mac・`pilot-macos-1-notes.md`）: 1 回目で所見 6 件（変換後の Enter が確定しない・マーカー F13 が観測されない・bundle id・最初の IME の状態・自動確定・所要時間）→ 原因を実機で切り分け（IME 本来の挙動・研究者の手打ちでも同じ）→ recipes とマーカーを直して（判断 80・`b38b9904`・`3e729f99`）ON / OFF の再パイロットで確認（持ち越し ON 2 / 126・OFF 0 / 39）。ImeShadow は封印して読んでいない
  - [x] M1 の枝 `feature/ime-m1-pilot` の PR（2026-10-01・G-GEAR・引き継ぎ `next-session-ime-paper-m2.md` §2）→ **PR #283・merge `0081efe7`**
    - [x] PR の前の整え: `GENERATOR_VERSION` 1.2.0・OFF 用の手順書も selftest で照合・`_scenario_checks` の既定を無くす・`cell.example.json` の layout を JIS に（判断 81・`5e9f873a`）
    - [x] origin/main（`97381a7b`）を取り込む（衝突 1 件: after-merge の handoff の §6 → Mac の方を §7 に・`5a9cc805`）
    - [x] clean な checkout（`5a9cc805`）で Windows で回る全 acceptance 22 本: 失敗は SCOPE と GUARD だけ（どちらも main の上で比較の基準が `feature/ime-eval-kit` の merge-base になるため・B15 の型）。GUARD は #279 の `scripts/run-codex-consult.sh` を拾った。この枝だけの差分（`97381a7b..5a9cc805`）に `src-tauri/` `src/` `scripts/` `.github/` は 0 件。macOS 専用の 004 / 007 / 012 は exit 2。024 の一覧の SHA-256 `4f7c7bea9f35ef489f501ad1f1dbbc97402d02d8af08f9a6365ae89f3603dbb5`（92 ファイル・直す前の値）
    - [x] 完了時レビュー 1 巡目（Claude）: code-reviewer ∥ security-checker → CRITICAL / HIGH 0 → 指摘を判断 82 のとおり直した（マーカーの長さの検査ほか）
    - [x] 完了時レビュー（Codex）: 研究者の選択で上限を一時的に 350,000 に上げて 1 回（33,557）→ P1 2 件（`closed_set.py` の手順書の照合・`focus_cmd` の同意と順序）・P2 2 件（持ち越し → M2 へ・OFF の S11 を空に）→ 判断 83 のとおり直し、上限を 300,000 に戻した。2 巡目（今回足した規則の境界条件）は予算の都合で Claude の code-reviewer で見る
    - [x] 完了時レビュー 2 巡目（code-reviewer・`5a9cc805..8ae9ccd1`）: HIGH 1（手順書の改行で SHA-256 が変わる → `.gitattributes`）・MEDIUM 5（マーカーの検査を `plan_rows` へ移して観測に残る並びと計画の実際の連続で判定・E2 は config も照合・前面の確認を 5 回まで読み直す ほか）→ 判断 84 のとおり直した
    - [x] origin/main（#281）を 2 度目に取り込む（衝突は Codex の台帳の today だけ → 和 324,731 / 8 回・`f2c98d22`）。最後の commit の clean な checkout で Windows で回る全 acceptance 22 本: 失敗は SCOPE と GUARD だけ（B15）・macOS 専用の 004 / 007 / 012 は exit 2。024 の一覧の SHA-256 `f3271b3aa4700d7e515954736c8540a8ef11c7276c5a4389c6ca345a7f44a118`（92 ファイル・Windows）
    - [x] push → PR #283 → CI → merge → main の CI（2026-10-01）: PR のイベントの run（36814196074）で Mac の check が **runner の通信切れ**（`Cargo test` の途中・"The self-hosted runner lost communication with the server"）で赤 → 研究者に AskUserQuestion で確かめ、失敗したジョブだけを再実行して緑（attempt 2・5 分 44 秒）。同じ commit の push のイベントの run（36814170682）は Mac も Windows も緑だった → merge（`0081efe7`）→ main の CI（36817877790）success（Mac / Windows の check・frontend-check）
    - [x] ⚠️ Mac: 024-acceptance.sh を回し、一覧の SHA-256 が G-GEAR の `f3271b3a…a118`（92 ファイル）と一致するか（判断 68・`papers/` が `f2c98d22` と同じ内容の commit で）。あわせて `build.sh` と、例の `focus_cmd` の前面の確認（引き継ぎ §3-7）
      → 2026-10-01（Mac・macOS 27.0・Python 3.14.4）: main（`eb8409b3`・`f2c98d22` からの `papers/` の差は 0）の clean な worktree で 024 は ✅ 139・❌ 2（SCOPE と GUARD だけ・B15）。★ 一覧の SHA-256 = `f3271b3aa4700d7e515954736c8540a8ef11c7276c5a4389c6ca345a7f44a118`（92 ファイル）で **G-GEAR と一致**
      → `build.sh` を `/bin/bash` 3.2.57 で回して exit 0（bundle id `local.ime-observation.refinput` を PlistBuddy で読み戻した）。不正な `REFINPUT_BUNDLE_ID`（空白・先頭の `-`・`/`・非 ASCII・129 文字）はすべて exit 2、`ok-1.2` は exit 0
      → 例の `focus_cmd`: 参照入力欄（`--out` 付きで起動）が前面のとき exit 0、Finder が前面から呼んでも前面にして exit 0、前面化の文を抜いて Finder を前面にしたままでは約 2 秒（5 回の読み直し）で exit 1（`the reference input field is not in front`）。`run_cell.py --selftest` の「前面の確認の失敗でブロックの前に abort」「focus の失敗で abort」も ok。⚠️ 最初の試行は `open RefInput.app`（`--out` なし → usage で即終了）で組んだため `activate` が返らなかった（測定器の誤り・`focus_cmd` の欠陥ではない）
  - [ ] M2 の残り: 正解の定義（`gt_rules` の `mac_nstic`・ON の型は 2 形）・本番の n / think の上限（1 セル約 10 時間・研究者）・`experiment/pilot-macos.md`（公開用の英語）・パイロットの生ログの置き場（公開物に含める）
    - [x] 本番の n / think / マーカー（判断 85・研究者）: n = 75・think 0.2〜20 秒・マーカー ← → ← →
    - [x] 正解の定義（判断 86）: `experiment/gt_rules.json`（`mac_nstic` の commit に「50 ms 以内に `set_marked` が続かない」）・`config.json` をこれに向けた。一致率 ON 124 / 126・OFF 117 / 117・`verify-off` 39 / 39
    - [x] 持ち越し（判断 87・研究者）: `gt_sessions.py` に除外の理由 `carry_over`（2 試行とも）
    - [x] `experiment/pilot-macos.md`（公開用の英語）: 条件・run・1 回目の所見と直し・呼び出し列の型（途中の自動確定を畳むと各シナリオ 1 形・例外 3 種を一次で数え直した）・正解の定義・oracle 一致率（example の規則と本実験の規則）・時計（ブロック 1〜5 のドリフトは ±5 ms/時以内・−200 ms/時はブロック 0 の起動直後の約 100 ms による）・到達・1 試行の時間・本番の設定
    - [x] 最後の commit（`6ecfa5b4`）の clean な worktree で 004・010・020・021・024: 失敗は SCOPE と GUARD だけ（B15）。024 の一覧の SHA-256 = `bc2e68162d118e3e1de25a77869dbc9a3c86980b057a93a707a3c9b3c7385f3c`（94 ファイル・Mac）
    - [x] ⚠️ G-GEAR: 024 を回し、一覧の SHA-256 が Mac の `bc2e6816…5f3c`（94 ファイル）と一致するか（判断 68・`papers/` が `6ecfa5b4` と同じ内容の commit で）
      → 2026-10-01（G-GEAR・Windows 11・Python 3.11.9）: PR #285 の merge 後の main（`500c5685`・`6ecfa5b4` からの `papers/` の差は 0）の clean な worktree（`C:/wt/clean-m2`）で 024 は ✅ 137・❌ 2（SCOPE と GUARD だけ・B15）。★ 一覧の SHA-256 = `bc2e68162d118e3e1de25a77869dbc9a3c86980b057a93a707a3c9b3c7385f3c`（94 ファイル）で **Mac と一致**
      → あわせて Windows で回る残りの acceptance 21 本（001〜003 005 006 008〜011 013〜023 028）: **SCOPE と GUARD を除く失敗 0 件**（028 は SCOPE を持たないので GUARD の 1 件だけ）。`_style_check.py papers/ime-observation` 違反 0 件
      → 記録の PR #286（`.steering/` だけ・判断 90〜97 も同じ PR）: CI 緑（Windows の check 12 分 51 秒）→ merge `538517a1` → main の CI（run 36841292986）success（Mac / Windows の check・frontend-check）
    - [ ] パイロットの生ログの置き場（除外の基準を先に書く・逆向きの到達を数える道具）
    - [x] 完了時レビュー（Claude の 2 系統・判断 88）: MEDIUM 3 件・LOW 4 件を直した。Codex は判断 89（研究者の選択で今日だけ上限を 360,000 にして 1 回・P2 2 件・P3 1 件に対応・上限は 300,000 に戻した）
  - [ ] M3 事前登録（macOS 版）の下書き → attack-me（stage `prereg`）→ 凍結 → OSF の登録（研究者）
    - [x] 研究者に 8 問（2026-10-01・G-GEAR）→ 判断 90〜97（速さ 480 / 240 / 120 ms・学習はリセットしない・段階凍結は追補で印を更新・OSF はすぐ公開・時計のずれは補正しない・`dwell_ms == 0` は今のまま・自動確定の後の取り消しは層別の診断を足す・E2 は上端 ≤ 2/K）
    - [x] 凍結の前の直し: `gt_sessions.py` / `l1.py` に自動確定の層別の診断（判断 96）・`pilot-macos.md` の時計の一文（判断 94）・`e2/README.md` の「coarsest」（判断 97）・`notes.md` の主張の対応表と借りた手法の出典・`l1.py` / `l2.py` の「事前登録で決める」（判断 95）・`cell.example.json` の `learning` / `predictive_candidates`（判断 91）
      → `gt_sessions.py --selftest` 14 件・`l1.py --selftest` 12 件（1 件足した）が緑。変異: 数える処理を外す・閉じた確定まで数える（gt）、層の境界 `> 0` を `>= 0`・欄の無いものを「無し」に・unknown を数えない・`_measures` から外す（l1）→ 6 本すべて赤。`nfb` の条件を外す変異は等価（`nfb` の無い確定は必ず閉じる）。`kit/check.sh` 27 本緑・`run.sh --synthetic` 2 回でバイト一致（L1 の出力に新しい表・unknown 0 件）・`run_cell.py --selftest` 53 件 ok・`_style_check.py` 違反 0 件
    - [x] 本番の生成の config（判断 85・90）と、各 run の seed（計画・E2）を決めてファイルにする → `experiment/plan_config.macos.json`・seed はすべて `SEED`（判断 98）。G-GEAR で両セルの計画の生成と `--validate` が exit 0
    - [x] `experiment/preregistration.md` の下書き（学術的な英語・OSF Preregistration の節立て・凍結の前に計算した値をすべて開示）と、書誌の登録（`docs/references.md` に `[V184]`〜`[V189]`・判断 98）→ `--check-prereg` は exit 3（印なし＝未凍結を正しく判定）・`check_citations.py` 違反なし
    - [x] Mac で確かめる 3 点（引き継ぎ `next-session-ime-paper-m3.md` §4）→ 2026-10-01（Mac・macOS 27.0・Python 3.14.4・枝 `feature/ime-m3-prereg` の `d564c3a6`）
      → (1) 本番の計画を事前登録 §2.4 のコマンド（`--seed 20260929`）で各 2 回生成: ON `c7a5469de0febbbc2e90259e477900ab0eb68c74b86f420b1e9491799a1210ba`・OFF `3759ebf7832ba561820abab504929dbadd7e775a33e22ba0e89b92e4800009a2` で、**G-GEAR（Python 3.11.9）とバイト一致**・2 回の生成でも一致・`--validate` exit 0。コーパスの SHA-256 も `c8f890cb…` で事前登録の値と一致
      → (2) パイロットの生成の config（`~/ime-pilot/*-config.json`・計画のヘッダーと run の `plan_sha256` で 7 run すべて対応を確かめた）: `cand_index_max` 4・`key_hold_ms` 60・`iki_sigma` 0.3・`inter_trial_ms` 1,000・`marker_gap_ms` 150 は**本番と同じ**。think 0.2〜20 s・`nav_count_max` 3・`block_size` 25・`kana_len` 4〜8（パイロットは未指定で既定値）も同じ。違うのは速さ（300 / 200 / 120）・n（3。`verify-1` / `verify-off` は 1・`short-1` は 1 で 3 シナリオ）・マーカー（`pilot-1` / `short-1` は F13 / F14 / F13、以後 ← → ← の 3 キー）・`reset_ime_every_block`（パイロットは true だが cell の `reset_cmd` が空で、run.json の `resets` は全ブロック `skipped`）・seed（`pilot-1` と `pilot2-on` が 1・`pilot2-off` が 5・短い run が 2〜6）・`pilot2-off` は `recipes.json` に `scenarios` で 13 シナリオに絞った。→ 事前登録 §3.1 に、速さ・n・マーカー・seed・reset の要求と不実施、それ以外は本番と同じことを書いた。★ `pilot-macos.md` の Setup の Plan の行が「seed 1」「n = 3」と書いていて、`pilot2-off`（seed 5）と verify の run（n = 1）に合わなかった → 直した。⚠️ `pilot-config.json` の今の中身（マーカー F1 / F2 / F1・`7f019af9…`）は `pilot-1` の計画のヘッダーの `config_sha256`（`7e507351…`）と合わない（後から書き換えた）。計画のほうがマーカー F13 / F14 / F13 を持つので、記録は計画に依った
      → (3) macOS（Python 3.14.4）で `gt_sessions.py --selftest` 14 件・`l1.py --selftest` 12 件・`kit/check.sh` 27 本がすべて緑。直した後の `_style_check.py` 違反 0 件・`check_citations.py` 違反なし
    - [x] attack-me round 1（stage `prereg`・`paper-reviewer` 4 本・2026-10-01・G-GEAR）→ 記録 `attack-me/prereg-ime-macos/round-1/`（`c5bfbc65`）。3 人とも major・fatal 0 → 判定 major revision。指摘はメインが一次で裏取り（接地の引用の捏造 0・部分的な偽陽性 1）。研究者に 8 問 → 判断 99〜105（すべて推奨どおり）
    - [x] round 1 の直し（判断 99〜106・実装の選択は判断 107・2026-10-01・G-GEAR）
      - [x] 予測器（判断 100）→ `kit/analysis/spec_predict.py`（`f3c08a68`）。送出の記録に観測器の状態機械（`keymap.rs` の 73 本の写像と素通し・`handle_key` の順序〔モードの更新 → 押下だけ駆動〕・`ime_mode` の開閉・`ime_compose` の表・20 秒の打ち切りと当て直し）を当て、予測の行と試行ごとの `long`（始めたセッションが打ち切り）・`carried_out`・`n_started` を出す。ブロックの先頭で「かな」の押下を置く（runner の契約）。`focus_away` / `focus_back` は飛ばし、修飾キーを送る計画は拒む
        → selftest 8 件（Rust の源との照合を含む: 写像・定数・遷移の各行・`handle_key` の順序）。変異 10 本のうち 9 本が赤、1 本（セッションの外の矢印を数える）は開始時に `nav` を 0 に戻すので等価。`kit/check.sh` 28 本が緑・`_style_check.py` 違反 0 件
        → 本番の計画に当てた値（計画の時刻から組んだ擬似の oracle・使い捨て・送出の遅れは入らない）: ON は予測の行 2,638・打ち切り 719、試行 3,150 のうち `long` 677・`carried_out` 188（すべて S6）・分割 314・自分のセッションを始めない 113（S6 の持ち越しを受けた試行）。OFF は行 2,417・打ち切り 682・`long` 650・`carried_out` 186・分割 280・なし 109。slow の `long` は ON 423 / 1,050。分割の多くは、打っている途中の打ち切りの後に残りが新しいセッションになる断片（S1 でも 21・S8 は思考の後の数字キーで 58）
        → ⚠️ 事前登録に書くこと: S6 の持ち越しは次の試行（どのシナリオでも）を汚す。判断 99 の分割は「打ち切り」だけに当てる（持ち越し・Tab・記号による分割は推論規則の限界で、段 (i) で数える実際の誤り）
      - [x] 照合の 2 段（正解 対 予測・予測 対 観測）と、20 秒の打ち切りでの分母の分割（Q1・Q2 の主は 20 秒未満・断片の行を数える・L2 は全試行が主で 20 秒以上を除いた版が副）を pipeline に入れる
        → `match.py --prediction --scope`・`spec_predict.as_obs_bytes / as_sessions_bytes`・`pipeline.run_stages` の 3 比較 × 3 範囲・診断の層 4 つ・`closing_key_in_reading`。合成の run に打鍵と特別な試行（長音・21 s・Backspace）を足した
      - [x] `l2.py` に試行ごとの差をシナリオ × 速さ別に（判断 104）→ `per_trial`（3 量・ブロックのブートストラップ）
      - [x] E2: near chance の性質の表（K = 10・100 で真の正解率 1/K〜3/K のときの通る確率・予定の n）・K = 1000 は記述・2 セルの両方・ms の時刻を持つ集合は対象外・セッションの行は対象外（判断 101・102）→ 事前登録 §6.8・`e2/README.md`
      - [x] 精度の幅の表と「形容しない」の約束・Q3 を how closely に・n の根拠の書き直し（判断 103）→ §3.3・§6.1（打ち切りの後に残る試行数の表も）
      - [x] 妥当性への脅威と限界の節・目的の文（判断 105）→ §1.1・§7（節番号を振り直した: 予測 §4.5・範囲と比較 §6.4・E2 §6.8・追補 §8・凍結 §9）
      - [x] `verdict.md` §3 の minor 19 件・nit 9 件（ハッシュに入る `_note` を含む）→ L1 の LoA / kappa の区間と速さ別・`delivery.py`（配送・焦点の喪失）・公開物の古い記述。群 M の文献の段落だけ原稿へ回した（判断 107 の 8）
      - [x] 確認: selftest 全部・`kit/check.sh`・`run.sh --synthetic` 2 回でバイト一致・`_style_check.py`・`check_citations.py` → 29 本緑・4 ファイルともバイト一致・違反 0・違反なし・`--check-prereg` exit 3。変異 31 本（生き残り 5 → 4 本はテストを足して赤・1 本は等価で条件を削除）
    - [x] attack-me round 2（同じ立場・同じ接地・`carryover-*.md`・2026-10-01・G-GEAR）→ 記録 `attack-me/prereg-ime-macos/round-2/`。R1 minor・R2 major・R3 minor（条件つき）・fatal 0・捏造 0 → 判定 major revision。研究者に 10 問 → 判断 108〜110（すべて推奨どおり）
    - [x] round 2 の直し（判断 108〜110・実装の選択は判断 111・2026-10-01・G-GEAR）
      - [x] X2 `long` を打鍵が入った試行すべてに・持ち越しを受けた層の定義し直し（`spec_predict.py`・`match.py`）→ §3.1・§3.3 の数の計算し直し（`--from-plan` で再現できる形にした）
      - [x] X1 問 3 の主を `under_limit` に（`pipeline.py` の `PRIMARY`）・X5 問 3 の偏り・一致の限界・混合の偏りの区間（`l2.py`）・minor 15 試行ごとの差を層 none に限った版
      - [x] X4 E2 をブロックで合わせ直す（`closed_set.py`・`open_set.py`）・minor 3 正解率のブロック区間（記述）・nit 速さ別の正解率
      - [x] minor 4（層と範囲ごとの読みの長さと思考時間）・10（焦点を失った試行の観測の行）・13（文だけ: `match.py` が既に数える）
      - [x] 事前登録の文（X1〜X8・minor・nit）と公開物（`notes.md`・`pilot-macos.md`・`data.md`・`kit/refinput-macos/README.md`・`kit/e2/README.md`・`gt_rules.json` の `_note`・`stats.py` の docstring）。`kit/gen/README.md` は §8 の新しい範囲と合うので変えていない
      - [x] 確認（`kit/check.sh` 29 本・`run.sh --synthetic` 2 回でバイト一致・`_style_check.py` 0 件・`check_citations.py` 違反なし・`--check-prereg` exit 3・変異 17 本すべて赤）
    - [x] attack-me round 3（変わった節とコードに絞る・2026-10-02・G-GEAR）→ 記録 `attack-me/prereg-ime-macos/round-3/`（`5fd17972`）。R1 minor・R2 major・R3 major・fatal 0・捏造 0 → 判定 major revision。研究者に 6 問 → 判断 112〜114（すべて推奨どおり）
    - [x] round 3 の直し（判断 112〜114・実装の選択は判断 115・2026-10-02・G-GEAR）
      - [x] Y1 問 3 の `n_conversions` と `dwell_fraction` を範囲の上で定義し直す（`l2.py` の `aggregate`・selftest・§4.6・§6.4・§6.7）
      - [x] Y2 §3.4 の中止を参照の外からの入力だけ・閉じた規則・`delivery.py` 単体・各 run の直後に（§3.4・§3.2・§6.2・§6.3・`data.md` 手順 4）
      - [x] Y3 推奨の単位（§6.8・§1.2 の問 4・§7・`kit/e2/README.md`）
      - [x] minor 1 `align_blocks` の再開（偽の錨）・selftest〔コード〕
      - [x] minor 2 焦点の喪失の区間（`delivery.py`・`pipeline.py`）〔コード〕
      - [x] minor 4 速さごとの偏りの区間を 1 つに（`l2.py`）〔コード〕
      - [x] minor 6 重み付けし直しの版を汚染の層だけ除いたものに（`match.py`・`l2.py`）〔コード〕
      - [x] minor 3・5・7〜16・nit（文）
      - [x] 確認（selftest・`kit/check.sh`・`run.sh --synthetic` 2 回でバイト一致・`_style_check.py`・`check_citations.py`・`--check-prereg` exit 3・§9 の SHA-256・変異）→ 29 本緑・4 ファイルともバイト一致・違反 0・違反なし・exit 3・5 ファイル一致・節の参照はすべて実在。変異: 作業用エージェントの自己申告 19 本（赤 17・等価 1・pipeline の配線 1 は赤にならず判断 115 の 3 に記録）、メインの抜き取り 4 本（`l2.py` 1・`closed_set.py` 1・pipeline の新しい検査 1 は赤、`delivery.py` 1 は生き残り → selftest を足して赤）。本文 12,143 語
    - [x] attack-me round 4（round 3 の直しで変わった箇所だけ・判断 114・2026-10-02・G-GEAR）→ 記録 `attack-me/prereg-ime-macos/round-4/`。R1 major・R2 major・R3 minor・fatal 0・捏造 0 → 判定 major revision。研究者に 5 問 → 判断 116・117（すべて推奨どおり）
    - [x] round 4 の直し（判断 116・117・G-GEAR・実装の選択は判断 118・`4bd6cacd`・点検の後は判断 119・120）
      - [x] Z1 §3.4 の中止の規則をブロックごとの区間で（`delivery.py` に区間ごとの「説明されない参照の key_down の数」・`pipeline.py` が同じ規則で拒む・selftest・§3.4 に命令行と窓の値・拒否の扱い・検査の対象・§6.3 は参照だけ・§3.2）〔コード〕。⚠️ 上限の数（かなキーを数えるか）は Mac の結果で決める → 作業用エージェント A（Sonnet）。`delivery.py` に `segments`（両側）・`pipeline.py` に `reference_abort_segments` と暫定の `RUNNER_KANA_PRESSES_PER_BLOCK = 1`
      - [x] Z2 問 3 のテキストの大きさの開示（§6.7・§7）→ k の数は `plan_figures` から再現（作業用エージェント C・メインが出力で照合）
      - [x] minor 1 合わせ直しの錨を右に揃える・selftest（ブロック末の S7 の Enter の欠け）・§6.8・README〔コード〕→ 作業用エージェント B（Sonnet）。selftest 151 件・open_set 133 件が緑。メインの変異 1 本（左端の条件を戻す）で 14 件が赤
      - [x] minor 2 `per_trial` の空の層を null で・§6.7 に汚染の無い版で空の場面（S6・S13）〔コード〕→ 作業用エージェント C（`status`・層ごとの `trials_not_used`）。S6・S13 が 0 試行なことはメインが予測の出力で数えた
      - [x] minor 5 `spec_predict.py --from-plan` に層ごとの Σm²/Σm（計画・主の範囲）・§3.3 の「usually near 1」・最小の主の層の半幅〔コード〕→ `plan_figures`。本番の 2 計画（SHA-256 一致）で 2.36〜3.13 / 2.47〜3.43・33〜39 / 30〜37 ブロック・主の範囲の最大 3.05（S14 mid）/ 3.22（S15 mid）・k の分布がすべて再現
      - [x] minor 3・4・6・7・8・nit 8 件（文）→ OFF の carried out 186 のうち 185 が後の試行へ続く（残る 1 つは試行の外の打鍵で打ち切り）をメインが予測の出力で数えた
      - [x] 確認（selftest・`kit/check.sh`・`run.sh --synthetic` 2 回でバイト一致・`_style_check.py`・`check_citations.py`・`--check-prereg` exit 3・§9 の SHA-256・節の参照・変異） → 29 本緑・4 ファイルともバイト一致・違反 0・違反なし・exit 3・5 ファイル一致・節の参照はすべて実在。変異: 作業用エージェントの自己申告 16 本・メインの抜き取り 3 本ですべて赤。本文 13,422 語
      - [x] 作業中の点検（code-reviewer ∥ security-checker・`b1c3f213..4bd6cacd`）→ security HIGH 1・MEDIUM 2・LOW 3、code-reviewer MEDIUM 4・LOW 8（M2 の一部と範囲外の気づきは偽）。研究者に 2 問 → 判断 119（`--pack` で全 run に §3.4 を強制・S15 以外の焦点の喪失を中止に足す）。直しは作業用エージェント D ＋ メイン（判断 120）
      - [x] 点検の指摘の直しの確認（29 本緑・バイト一致・違反 0・違反なし・exit 3・節の参照・本文 13,902 語）
    - [x] ★ Mac（判断 113 の Y4 ＋ 判断 117 の Z3 ＋ 判断 119・120・凍結の前・引き継ぎ `next-session-ime-paper-m3-mac-work.md`）: (1) `pilot-macos.md` の Raw logs に預ける基準（時点は凍結の前・観測の余分な行は本計測と同じ扱い）と「封印したセッション行は預けるときだけ開け、解析しない」 (2) `pilot2-on`・`pilot2-off`・`verify-off` の観測の key 行に `align_plan` だけを `--markers-in-obs` とパイロットの 3 打鍵の印で流し、採点されたブロックの割合を §3.1 に（診断） (3) 同じ run の参照のログに `delivery.py` → かなキーと S14 のモードキーが参照に残るか・ブロックごとの「説明されない数」を §3.1 に書き、Z1 の上限を決める
      → 2026-10-02（Mac・macOS 27.0・Python 3.14.4）: (2) 3 本とも全ブロック採点（15 / 15・282 試行・割り当てのない打鍵 0）(3) k = 0・`REFERENCE_RECEIVES_MODE_KEYS = False`・滑りの最小 1,582 ms・区間の規則に当たらない。⚠️ `pilot2-off` に S15 以外の焦点の喪失 1 回（31 ms・打鍵なし）→ 研究者に戻し、焦点の規則を「喪失中の観測の打鍵で中止」に改めた（判断 121・余裕 500 ms は判断 122）。(1) `pilot-macos.md` の Raw logs を本計測と揃えた基準に。確認は判断 122 の 9
    - [x] G-GEAR で Mac の作業を取り込んで確かめた（2026-10-02・29 本緑・バイト一致・定数と文の一致・§3.1 の数の整合・本文 14,369 語）→ ⚠️ 判断 121 の焦点の規則が送った打鍵も数えていた（run の約 78% の時間が当たる）→ 研究者に問い判断 123（送った打鍵を差し引く）・実装は判断 124（作業用エージェント E・`OBS_SEND_DELAY_MS = 100`）→ 29 本緑・バイト一致・違反 0・違反なし・exit 3・本文 14,665 語
    - [x] attack-me round 5（§3.4・§3.1・§6.7・`delivery.py`・`closed_set.py` に絞る・G-GEAR・判断 117）。★ 判断 121〜124 の焦点の規則（喪失の区間の観測の行と送った打鍵の差し引き・余裕 500 ms・遅れ 100 ms）と `pilot-macos.md` の Raw logs も対象に・引き継ぎ `next-session-ime-paper-m3-round5.md`
      → 2026-10-02（G-GEAR）: 判定 minor revision（R1・R2・R3 とも minor・fatal 0・major 0・捏造 0・注入 0・有効な査読 3 / 3）。研究者の採否は判断 125（Y1 焦点の規則をコードで閉じる・Y2 計画の SHA-256 を解析で照合・Y3 感度は §7 に開示・直す一覧を全部承認・round 6 なし）
    - [x] round 5 の直し: Y1〔コード: `delivery.py`・`pipeline.py`〕・Y2〔コード: `pipeline.py`〕・Y3（§7）・minor 7 件（1 content-free を中止した run にも〔コード〕・5 78% を `plan_figures` に〔コード〕）・nit 14 件 → 確認（`kit/check.sh`・`run.sh --synthetic` 2 回でバイト一致・`_style_check.py`・`check_citations.py`・`--check-prereg` exit 3・節の参照・語数・定数と文の目視の照合）
      → 2026-10-02: 判断 126。29 本緑・バイト一致・exit 3・違反 0・違反なし・節の参照・本文 15,265 語・変異はすべて赤
    - [x] 完了時レビュー（code-reviewer ∥ security-checker は `965486554..f02cb49a` の公開物 24 ファイル・Codex は研究者の選択で直近の `kit/` に絞って 2 巡）
      → code-reviewer MEDIUM 1・LOW 6、security MEDIUM 1・LOW 4・範囲外 1、Codex 1 巡目 P1 1・P2 2（すべて真）→ 研究者に 4 問 → 判断 127（起動の前と止めた後も喪失・数える終わりの延長・計画をセルと対応・残り 12 件）・実装は判断 128。Codex 2 巡目 P1 1・P2 2 → 判断 129（文を揃える・FORMAT とテストは足さない）。29 本緑・バイト一致・exit 3・違反 0・違反なし・節の参照・本文 15,469 語
    - [x] PR → CI 緑なら merge → main の CI → PR #289（merge `c613bdf5`・PR の CI は Mac / Windows の self-hosted と frontend が緑）。attack-me の `tmp/`（round 1〜5）を消した（閉じたため）
    - [x] 凍結（研究者の最終の確認 → 印 → タグ → 書き出しの一覧の SHA-256）・引き継ぎ `next-session-ime-paper-m3-freeze.md`
      → 2026-10-02（G-GEAR）: 試しの書き出しが selftest の 2 行で拒否 → 直した（`eaaeea74`・判断 130）。024 は ✅ 137・❌ 2（SCOPE と GUARD だけ）。研究者に 3 問 → 判断 131（凍結する・タグ `ime-observation-prereg-macos`・一覧の道は M12 で公開 repo の最初の commit）
      → 凍結の commit `ff122e3246346da7869c4e990e4978acb1f191c6`・`frozen_at: 2026-10-02`・`sha256: 64dfbb6e…af2a`・`--check-prereg` exit 0。書き出しの一覧の SHA-256 `29b183ba245939ad82d9fa2d7db26e1a18520e2966f4aa9ec74478a4e51e6c49`（98 ファイル・`freeze-export-list-macos.txt`）。`experiment/notes.md` に凍結の commit・タグ・一覧の SHA-256 を書いた
    - [x] OSF Registries の登録（研究者・公開・最初の本計測の run より前）→ 登録の URL と日付を `experiment/notes.md` に（§9）
      → ★ 2026-10-03（G-GEAR）: **公開になった。登録は `https://osf.io/9nh7r`**（DOI `10.17605/OSF.IO/9NH7R`）。⚠️ 下の `mbgxz` は登録ではなく**登録の元のプロジェクト**（API の `registered_from` が `nodes/mbgxz`・非公開なので `nodes/mbgxz/` も `registrations/mbgxz/` も 404）。前日の 404 も 10-03 00:14 JST の 502 / 500（OSF の障害・API の入口 `/v2/` も 500）も、この ID を引いていた。研究者が 9nh7r を知らせた後、API（`registrations/9nh7r/`）で確かめた: `public: true`・`pending_registration_approval: false`・`reviews_state: accepted`・`withdrawn: false`・`embargoed: false`・**`date_registered: 2026-10-02T13:40:09.840630`**（`date_created` と同じ・API の値は時差の記号なし。UTC でも JST でも日付は 2026-10-02）・様式 Open-Ended Registration・ライセンス CC BY 4.0・分野は推奨の 2 つ（Graphics and Human Computer Interfaces・Quantitative Psychology と上位）・タグ 3 つ。Summary の文は印 2 つ・凍結の commit の 40 桁・一覧の SHA-256（98 ファイル）・判断 132 の一文（開発履歴は非公開・公開 repo の最初の commit から計算し直せる）を含み、値はすべて正しい。**添えたファイルを `https://osf.io/download/6abfb4566d9449407c24a04b` から取り、SHA-256 を計算して `fa6fd586…7773` と一致**（タグ `ime-observation-prereg-macos` の blob とも一致・API の `file_hashes` とも一致）。→ `notes.md` の凍結の段落の後に URL・DOI・登録日・添えたファイルの SHA-256 を 1 文（`_style_check.py` 違反 0 件）。M4 の run はまだ無いので「登録の日 < 最初の run」は守られている
      → 2026-10-02: 研究者が登録を送信した → **`https://osf.io/mbgxz`**・状態は **pending approval**（研究者の報告）。同日 23:17 JST に公開の API（`https://api.osf.io/v2/registrations/mbgxz/`）は 404（承認待ちは外から見えない）。OSF の承認は 48 時間で自動（help.osf.io「Welcome to Registrations」）。⚠️ 公開になってから: API の `date_registered` を読む・登録に添えたファイルの SHA-256 が `fa6fd586…7773` か確かめる・`notes.md` に URL と登録日（引き継ぎ `next-session-ime-paper-osf-m4.md` §2 の 1〜2）。M4 の run は公開の後
      → 研究者に渡した手順（このセッション・一次は help.osf.io の 5 頁と OSF の様式の定義 `osf-open-ended-3.json`・`osf-preregistration-3.json`）: プロジェクトなしで「Add a Registration」→ 推奨は Open-Ended Registration（必須は Summary だけ・uploader で凍結したファイルをそのまま添える）→ Summary の英文の案（印・commit・一覧の SHA-256・開発履歴は非公開で公開 repo の最初の commit から一覧を計算し直せる）→ すぐ公開。分野の推奨は OSF の API で実在を確かめた 2 つ（Computer Sciences → Graphics and Human Computer Interfaces・Psychology → Quantitative Psychology）。⚠️ 研究者が実際に選んだ様式・分野・ライセンス・Summary の文は聞いていない（公開後に頁で確かめる）
    - [ ] ★ M12 への申し送り（判断 131）: 公開 repo の最初の commit を、タグ `ime-observation-prereg-macos` から `--allow-missing-license` で書き出したものそのものにしてタグを付け、一覧の SHA-256 が `29b183ba…6c49` になることを確かめてから、ライセンスと M12 の書き出しを上に積む。公開 repo は `git init` の新しい履歴（fork・公開への切り替え・private の履歴の push は使わない）。`notes.md` に公開側のどの commit・タグが凍結の書き出しかを 1〜2 文（判断 132）
    - [x] ★ M6 への申し送り（判断 132）: 追補の節に「Status の日付は macOS の凍結の日で、印は追補で差し替えた」と 1 文（2026-10-03: §10.1 に書いた）
    - [x] 完了時レビュー（code-reviewer ∥ security-checker ∥ Codex 1 巡・`1086e3be..ce205e83`）→ 判断 132
    - [x] 出荷: ブランチ `docs/ime-m3-freeze` とタグ `ime-observation-prereg-macos` を push（`ls-remote` でタグが `ff122e32` を指すことを確かめた・タグの push でワークフローは起動しない）→ PR #293 → PR の CI（run 36977262693）は Mac・Windows の check と frontend-check が緑 → merge（merge commit 方式）。merge の前に main が 2 回進み、1 回目は `.codex/budget.json` の台帳だけが衝突 → 和で解いた（422,989 / 10 回・判断 132 の台帳のコメント）、2 回目（#294 の版上げ）は衝突なし → CI 緑（run 36984522344）→ **merge `2543f9fb`** → **main の CI（run 36988299913）success**（Mac / Windows の check・frontend-check）。凍結の commit `ff122e32` は main から辿れる
  - [x] M4 macOS 本計測（事前登録 §3.2 の順: ON → OFF → E3 `idle` → E3 `working`・各晩 1 項目）
    - [x] 準備の照合（2026-10-03・Mac・Python 3.14.4）: タグ `ime-observation-prereg-macos` のクリーンな worktree（detached・`ff122e32`・porcelain 0 行）から `export.internal.py --allow-missing-license` → exit 0・98 ファイル → §9 の定義で計算した一覧が **`29b183ba…6c49`**・`freeze-export-list-macos.txt` とバイト一致（G-GEAR と Mac で同じ）。計画: タグと書き出しの両方から §2.4 のコマンドで生成 → ON **`c7a5469d…10ba`**（3,277 行）・OFF **`3759ebf7…09a2`**（3,043 行）で §2.4 と一致。書き出し側で `cargo build --release --locked`（logger）と `refinput-macos/build.sh`（bundle id `local.ime-observation.refinput`）→ どちらも成功・`check_manifest.py --self` match。⚠️ 書き出しは scratchpad（セッションごとに消える）なので本計測の晩に同じ手順で作り直す
    - [x] ON の run `on-1`（2026-10-03・Mac）: 開始 2026-10-02T16:03:56Z（OSF の `date_registered` 13:40 UTC の後）→ 約 12.0 時間で完走・`aborted: false`・前面の確認 126 / 126・子は 2 つとも `terminated`。`~/ime-m4/`（書き出し `export-ff122e32/`・一覧 `29b183ba…` を照合・`cell-on.json`〔`live_conversion: "on"`・時刻同期と自動更新のオフは研究者の申告・スクリーンセーバーと時刻同期は権限がなく読めず〕・`caffeinate -di` で包み `nohup` で切り離して起動）。run の前に読めた設定: AC 電源・sleep 0・displaysleep 0・自動更新 4 項目 0・`JIMPrefLiveConversionKey = 1`・macOS 27.0.1（26A434）・JapaneseIM-RomajiTyping 6.3
      → §3.4 の点検（04:15 UTC・凍結の書き出しの `delivery.py`）: exit 0・計画 `c7a5469d…`（§2.4 の ON）・`reference.segments.excluding_mode_keys` の 2 つの数 0 / 0・`n_loss_spans_with_unexplained_presses` 0（失われた焦点 225 はすべて計画どおり〔S15〕）・到達 102,732 / 102,732 → **打ち切りに数えない**。`data.md` の点検の表に 1 行。`run.json` の SHA-256 `0257755c…c268`。預け入れはまだ
      → ⚠️ **背景の負荷（2026-10-03 に気づいた）**: この Mac は CI の macOS セルフホストランナー（`~/actions-runner`・`gse-mac-selfhosted`）を兼ねる。ON の run（16:03〜04:04 UTC）の間に `CI / Release` が **12 回**起動した（`gh run list`・各 7〜31 分・G-GEAR の別セッションのブランチと main のマージ・cargo のビルドとテスト）。§3.2 の条件（電源・自動更新・時刻同期・スリープ・ロック・スクリーンセーバー）には背景の負荷が無いので**逸脱ではない**が、時刻に効きうる妥当性の脅威として論文の §7 の限界・`env.md` に書く。所要が見込み 10 時間 → 12.0 時間に延びたのはこれかもしれない（推測・未検証）。点検の数（到達 100%・外からの押下 0）には出ていない。ON はやり直さない（§3.4: 完走して点検を通ったセルは 1 回）
    - [x] OFF の run `off-1`（開始 2026-10-03T04:19:38Z・ライブ変換 OFF を入力メニューの ✓ と `JIMPrefLiveConversionKey = 0` で確かめた・計画 `3759ebf7…` を照合・AC 電源・`cell-off.json`）→ 点検 → `data.md`。★ 研究者の選択: CI ランナーは止めず ON と同じ条件で測る（開始直後に PR #297 の CI が並行していた）
      → 2026-10-04: 約 11.1 時間で完走・`aborted: false`・前面の確認 117 / 117。run の間に `CI / Release` が 8 回起動（2026-10-05 に run の実の終わり 15:27:12Z で数え直した・前は 15:30 で切って 9 回）。§3.4 の点検（15:34 UTC）: exit 0・計画 `3759ebf7…`（§2.4 の OFF）・0 / 0・`n_loss_spans_with_unexplained_presses` 0 → **打ち切りに数えない**。`data.md` に 1 行。`run.json` の SHA-256 `4ac581cb…f519`。⚠️ ON に無かったもの: **計画に無い焦点の喪失が 1 回**（04:20:33.68〜04:20:36.35 UTC・開始から 55 秒・試行 `t00004`〔S10・mid〕の中）→ 参照に届かなかった押下 11（参照 93,400 / 93,411・観測は 93,411 / 93,411）。★ 原因（研究者の報告・2026-10-04）: **研究者がその約 2 秒にマウスで別の場所をクリックした** → 焦点が移り、送った押下 11 が別のアプリに入った（その秒の統合ログは 0 行で、機械の側からは裏づけられない）。キーは押していない。規則上は喪失の幅の中に説明のない観測の行が無いので数えない。解析では試行 `t00004` は焦点を失った試行として §6.2 の扱いに従う
    - [x] E3 `idle`（2026-10-04・Mac）: 先に `calibrate-cpu.sh`（真値 98.9% に `top -l 3` 98.8%・`-l 2` 44.0%・不在は空）と `summarize_e3.py --selftest` OK。観測器を 1 つだけ起動（`ps -c` の名前 `ime-observation-logger`・ログは `~/ime-m4/e3-idle-obs.jsonl`・§3.4 で預けない）→ `run_e3.sh idle 28800 30`（`caffeinate -di`・`nohup`）開始 2026-10-03T15:37:21Z → 8 時間で終了 → 観測器を止めた。`summarize_e3.py`: 使える行 777・不在 0・間隔の中央値 37 s・窓 7.99 h → **`status: measured`**（§6.10 の下限 480 行・4 時間を満たす）。`samples.tsv` の SHA-256 `f2fc37ef…1261222`・`conditions.txt` `25a08f08…7fba680f`。その間に `CI / Release` が 5 回起動（ON / OFF と同じく止めない）
    - [x] E3 `working`（ライブ変換を ON に戻す → `run_e3.sh working` を先に → ON の計画を通しで流す run〔約 12 時間・最初の 8 時間を使う〕→ §3.4 の点検）
      → 2026-10-04 12:52 JST: ライブ変換を ON に戻した（✓ の読み戻しと `JIMPrefLiveConversionKey = 1`）。`cell-e3-working.json`（`cell-on.json` のラベルだけ `macos-e3-working`）。★ 研究者の選択: **23:00 JST に自動で開始** → `~/ime-m4/e3-working-at-2300.sh` を `nohup caffeinate -i` で待機。23:00 に fail-closed で点検（AC 電源・ライブ変換 ON・観測器 / runner / サンプラーが動いていない・計画 `c7a5469d…`・出力先が無い）→ サンプラーを先に起動して行が出るのを待つ → runner。結果は `e3-working.status.txt`。止まる側を試した（開始を過去・計画の値を偽にした写し → バッテリーで動いていたので「AC 電源でない」で開始せず・出力先は作られない）
      → ★ 研究者の指示で 23:00 を待たず **22:03 JST に開始**（待機を止め、同じスクリプトを開始時刻だけ過去にして再起動）: 点検は通過 → サンプラー 13:03:31Z（観測器 0 個を確認）→ runner 13:03:31Z。前面の確認と 3 本のログの伸び・観測器 1 個を確かめた
      → 2026-10-05: 約 12.0 時間で完走（終了 01:04:16Z）・`aborted: false`・前面の確認 126 / 126。§3.4 の点検（01:17 UTC）: exit 0・計画 `c7a5469d…`・0 / 0・`n_loss_spans_with_unexplained_presses` 0・計画に無い焦点の喪失 0・到達は参照・観測とも 102,732 / 102,732 → **打ち切りに数えない**。`data.md` に 1 行（ラベル `macos-e3-working`）。`run.json` `a2fa68e4…de0f9`。`summarize_e3.py idle=… working=…` → **両方 `measured`**（working: 使える行 768・不在 1〔最初の行・観測器の起動前〕・窓 7.99 h・遷移 0）。`samples.tsv` `32fb0782…921ec`・`conditions.txt` `95f29b15…dd7ae4`。その間の CI は 1 回
    - [x] `env.md`: 3 つのセルの行（macOS 27.0.1 26A434・RomajiTyping 6.3・rustc 1.99.0・Swift 6.4）・`Cargo.lock` の SHA-256 `206d2ed8…`・背景の CI（ON 12 / OFF 8 / idle 5 / working 1 回・各 2〜35 分・`gh run list` の作成時刻が run の窓の中のもの）を限界として 1 段落。★ /cross-review（2026-10-05・Claude ∥ Codex）を受けて: 回数を「重なった workflow run の数と run の時間に占める割合」に直した（ON 13・23% / OFF 9・20% / idle 7・13% / working 1・2%・Windows のジョブも含むので上限）・idle は点検の表に行が無い理由を 1 文。`data.md` に OFF のクリックによる焦点の喪失を 1 段落（原因は研究者の報告で、ログでは確かめられないと明記）。⚠️ **§3.2「別々の晩」から外れた**（OFF は ON の 15 分後の昼に開始・OFF と idle が同じ夜）→ `deviations.md` に **D6**（§8: 解析の前に記録）。前にメインが「逸脱には当たらない」と言ったのは確かめないままの断定だった
    - [x] M4 の受け入れ条件（`_issue-plan.md`）: 3 つの run（`on-1`・`off-1`・`e3-working-run`）の `gt` / `obs` が凍結の書き出しの `validate_logs.py --kind` を、`oracle` が `emit.py --validate` を通る（9 本とも exit 0・2026-10-05）。`run.json` の SHA-256 は上に記録。⚠️ `data.md` の `- run_dir: … manifest_sha256: …` の行は預け入れから取り出した後に足す（`data.md` の規約）→ 預け入れ（`pipeline.py --pack`）と一緒に。生の run は `~/ime-m4/runs/`（この Mac だけ・git の外）
  - [ ] M5 Windows の較正パイロット → ~~別の Windows 実機で行う（判断 133）~~ → ★ **G-GEAR で行う**（2026-10-03・研究者の選択・判断 134: 数時間以上の run〔M7 のセル・Windows の E3〕だけ別の Windows 実機）。IME の学習はリセットしない・電源の設定はメインが一時的に切って戻す・実行の時間は未決。⚠️ 較正（G-GEAR）と計測（別の実機）の機械が違う → M7 の前に計測する機械で短い確認の run（推奨・M6 の前に研究者が決める）。G-GEAR ではまだ何もしていない。→ 引き継ぎ `next-session-ime-paper-m5-windows.md`
    - [x] 2026-10-03: 引き継ぎを開いた機械が Surface Pro 8（判断 134 の「別の Windows 実機」・研究者の答え）だった → M5 は G-GEAR に残し、計測する機械の OS・MS-IME の版・キーボード・道具の有無を記録した（判断 135・25H2 / 26200・MS-IME 10.0.26100.8875・Rust と Python は未導入）
    - [x] 2026-10-03: 研究者の指示で **M5 をこの Surface（計測する機械）で行う**（判断 136）。Python 3.11.9・Rust 1.98.1・MSVC を入れ、タグから書き出し（一覧 `29b183ba…` が一致）→ ビルド → selftest がすべて緑。短い試し（IMM / TSF 各 39 試行）と本体（各 117 試行・27.6 分）を打ち切りなしで回し、封印 → 集計した → `pilot-windows-1-notes.md`
    - [x] ★★★ 研究者の判断（2026-10-03・判断 137）: S4 は**逸脱 D1 として Windows だけ Esc 3 回**（`experiment/deviations.md`・生成器の `_PROFILES` に `cancel_converted`）、S8 は `after_digit` を `["enter"]`（§8 の範囲）→ 直して確認の run まで回す。正解の経路と起動の手順は M6 で。元の項目: **S4（Space → Esc 2 回）が MS-IME で取り消しにならない**（複数文節は Esc 3 回）—— 凍結の生成器が S4 を OS を問わず固定しており §8 の範囲で直せない（所見 1）。S8 の `after_digit`・正解の経路・起動の手順も（同じノートの「残り」）
    - [x] 2026-10-03: 直した手順で短い確認の run（IMM / TSF 各 39 試行）→ 持ち越し 0・S4 / S8 とも 3 / 3 で意図どおり・gt のマーカーが全ブロックで一致（`pilot-windows-1-notes.md` の「確認の run」）
    - [x] 公開用の `experiment/pilot-windows.md`（英語）→ M5 を閉じる（2026-10-03・M6 と一緒に書いた・attack-me round 1・2 で直した）
  - [x] M6 Windows の追補（2026-10-03・Surface・判断 138〜142）: §10・逸脱 D1〜D4・`pilot-windows.md`・`data.windows.md`・`kit/run/` の Windows の道具・`scope_windows.py`。attack-me round 1（major）→ round 2（minor）→ 直して完了時レビュー（code-reviewer ∥ security-checker・Codex は不在で省略）→ **凍結 `a57c4fd7`・タグ `ime-observation-prereg-windows`**（`sha256` は macOS と同じ・書き出し 108 ファイル・一覧の SHA-256 `f61af353…87b7`・`freeze-export-list-windows.txt`）
    - [x] 2026-10-03: 研究者が OSF Registries に追補を登録した → **https://osf.io/4jwzn**（DOI 10.17605/OSF.IO/4JWZN・公開・`date_registered` 2026-10-03T13:56:27 UTC・Open-Ended・添えたファイルの SHA-256 が凍結したファイル `f8620963…` と一致）→ `notes.md` に記録。元の項目: 研究者: OSF Registries に追補を登録する（凍結したファイル `f8620963…2b1d`・commit の 40 桁・一覧の SHA）→ URL と日付を `experiment/notes.md` に → 登録の日付は Windows の最初の計測より前
  - 全体: ★ 凍結物は **`papers/ime-observation/experiment/preregistration.md`**（判断 21 で `experiments/<date>-…/` から変更）
- [x] 投稿計画の見直し（2026-10-04・G-GEAR・判断 145）: BRM に **10 月末**に投稿・原稿は計測と並行で書く（次のセッションから・引き継ぎ `next-session-ime-paper-writing.md`）。BRM の購読モデルの費用 0 を一次で確認（Chrome）。CHI の残りの記述（`design.md` §6・`requirement.md`・`paper-suggest.md`）を直した
- [x] 合成入力の記録一式を 5 つ目の貢献「データセット」として加える（2026-10-04・研究者の選択・判断 146）→ 説明書・Zenodo の DOI・パイロットの生ログの判断は M12 の枠で
- [x] G-GEAR の Windows パイロットの最初の試し（2026-10-03 未明）を `pilot-windows-ggear-notes.md` として残した（判断 144・M5 の記録ではない）。枝 `docs/ime-m5-pilot-ggear` は研究者の了承で消した（2026-10-04）
- [ ] 論文の外枠（節構成・主張 ↔ 根拠の対応表）を `papers/ime-observation/manuscript/outline.md` に置く（★ 判断 21）
  - [x] 外枠の初稿（2026-10-04・G-GEAR・枝 `docs/ime-manuscript-outline`）: 13 節 ＋ Open Practices ＋ Declarations・貢献 5 つ・主張 ↔ 根拠の表 23 行（OB / LG / AG / RC / RT / DS）・図 5・表 10。内部の対応（判断・`[Pn]`/`[Vn]`・未登録の引用）は `manuscript-map.md`。`_style_check.py` 違反 0（変異で赤になることも確認）
  - [x] 研究者の確定（判断 147）: データセットは専用の短い節・パイロットの生ログは別の区分で数える・原稿は LaTeX（Springer の雛形）
  - [x] attack-me（外枠）round 1 → **major**（有効 3/3・捏造 0・注入 0・偽陽性 0）→ 研究者の採否（判断 149・7 問とも推奨）→ 外枠を全面的に直した（31 行）・D6 と §10.8 の点検を公開の記録に（`deviations.md`・`data.windows.md`）
  - [x] attack-me（外枠）round 2 → **major**（R1 major・R2 minor・R3 major・有効 3/3・捏造 0・注入 0・偽陽性 0）→ 研究者の採否（判断 150・6 問とも推奨＋事実 1 問）→ 外枠を直した（Y1〜Y44・要旨の規則を事前登録 §6.1 に合わせた・推奨 (d) を 2 段に・表を 13 に）・`method.tex`・D6 の言い方
  - [ ] ★ round 3 は回さない → 原稿の attack-me（stage `manuscript`・10-18〜22）に外枠の round 1・2 の引き継ぎを渡す（判断 150-4）
  - [x] 試行 2 の間に Surface で何が動いていたか（Y12・判断 150-6）→ `data.windows.md` に書かれていた。原稿 §6.1 に写した（判断 188・Z4）
  - [x] 手法の節の残り: 問 4（`sections/recoverability.tex`）と問 5（`sections/cost.tex`）の手法（2026-10-05・`730edd64`）
  - [x] 手法の節の草稿 `manuscript/sections/method.tex`（LaTeX・約 5,200 語・判断 148）・`references.bib`・`main.tex` の骨組み。⚠️ 未コンパイル（この機械に LaTeX が無い）
  - [x] 公開物の文体検査を `.tex` / `.bib` に広げた（判断 148・selftest ＋ 変異 2 本）
  - [x] 題を Logging に揃える（`README.md`・`CITATION.cff`・`.zenodo.json`・`main.tex`・`kit/logger/README.md` の古い一文も・2026-10-05・判断 150）。`kit/` に題の文字列は無かった
  - [ ] `data.windows.md` の §10.8 の点検の計画の SHA-256 を全桁にする（Surface の点検の run の manifest から）
  - [x] 後の節（§2 比較表・§3 観測可能性〔方法・一次の文書の登録〕・§4 ロガー・Table 4・§10 データセット）・未登録の引用の登録（Plant・Pinet・Bridges・Monaco・Gebru・MS / Apple の文書・Inputlog の版・Translog-II・ScriptLog）
    → 2026-10-05（G-GEAR）: `sections/related.tex`（§2・Table 1）・`observability.tex`（§3・Table 2）・`logger.tex`（§4・Table 3・Table 4）・`dataset.tex`（§10・Table 13）。MS 16・Apple 13・WebKit のソースを取得して逐語を確かめ、Wayback に写しを作った（`docs/references.md` [V192]〜[V235]）。★★★ macOS の Accessibility にも変換の範囲の属性と開始・終了の通知があった → 判断 151（§3 と貢献 1 を対称の形に・研究者の選択）。macOS の観測するキーが登録の書き方より狭いこと・ヘッダの SHA-256 が共通部分だけを覆うこと・Windows の補助の信号を原稿の注にした。ScriptLog は scriptlog.net で 1.1 が有償で売られていた（サブエージェントの「入手できない」は不正確だった）
    → 同日: 独立の照合（Opus）の指摘 17 件をすべて一次で裏取りして直した（判断 153）・書誌 [V192]〜[V235] を登録（`4e5e5184`）・補遺の文書一覧 `manuscript/supplement/observability-documents.tex`（31 件・Wayback の写しつき）
  - [x] main に入った M4（PR #297）と Windows の解析（PR #304）を取り込んだ（`745a551f`）。逸脱の番号の衝突は研究者の選択で main の D6（macOS の晩）を保ち、この枝の Windows の試行の数え方を **D7** に（判断 152）。macOS の版（27.0.1・26A434）を原稿に記入
  - [ ] Mac で: AppKit と C の Accessibility の定数の数と `TextInputSources.h` を計測の版（macOS 27.0.1）の SDK のヘッダで確かめる（外枠の Open items・判断 151・153）
  - [ ] 結果の節（引き継ぎ `next-session-ime-paper-results-3.md`）
    - [x] 結果の表の道具（判断 156・165・168〜172）: 表 7〜12・KT1・補遺の層ごとの表・予測の層・D10 の直した併合の率・selftest 78 件・変異 29 本（判断 171）
    - [x] 登録が報告を求めていた残り（層ごとの問 2・全スコープの層ごとの検出・スコープの構成・除外・打ち切り・Windows の診断）と表 9 の区間（判断 172・selftest 91 件・変異 20 本）
    - [x] Windows の印の時刻（§6.9・判断 171・`results/windows/clock_sync_windows-msime-tsf.json`）
    - [x] Mac で: macOS の 2 セルの印の時刻（§6.9・判断 171 の手順・`gt_vks` は 123・124）→ `results/clock_sync_<cell>.json`・`data.md`
      → 2026-10-05（Mac・Python 3.14.4・判断 177）: on 126・off 117 ブロックすべてで印が見つかった（欠け 0）・2 回目とバイト一致・`--check` 一致・未生成の値 0・文体違反 0（組版は G-GEAR）
    - [x] 表 11 の「規則の性質」（§6.8 の確率の表）の置き方 → 手法の節の静的な表 `tab:nearchance` のまま（判断 174）
    - [x] `sections/results-*.tex`（RF1 → 問 1・2 → 問 3 → 問 4 → 問 5）の草稿（判断 174）
    - [x] Windows の開いた集合が macOS OFF とバイト一致する理由を確かめた（判断 173）
    - [x] 図 1〜5（判断 181: pgfplots・図 2〜5 の座標は表の道具が生成・selftest 125 件・変異 12 本）
    - [x] 要旨と結論（外枠の Rule for the abstract・248 語）・§1・§11〜13・Declarations・Open Practices・D10 を手法の節に（判断 182）
    - [x] 完了時レビュー（code-reviewer ∥ security-checker ＋ /cross-review 2 巡・判断 183・184）→ PR
    - [x] M12 の寄託の 4 点（E3 の標本・working の観測ログ・パイロットの生ログ・コードの DOI）を研究者が決めた（判断 183）
    - [x] 原稿の attack-me（stage manuscript）round 1 → **major**（R1・R2・R3 とも・有効 3/3・捏造 0・注入 0・偽陽性 0）→ 研究者の採否（判断 188・8 問とも推奨＋dwell の分位点の問い直し）→ 直した（`verdict.md` §8）→ 作業中の点検と /cross-review 2 巡の指摘を直した（判断 189）（2026-10-06・G-GEAR）
    - [x] Mac で: macOS の 2 セルの探索的な dwell の分位点（`kit/analysis/explore_dwell_quantiles.py`・判断 188-4）→ `experiment/results/exploratory/dwell_quantiles_<cell>.json`（原稿の `\rv` 8 個が埋まる）
      → 2026-10-06（Mac・判断 190）。G-GEAR で通しのビルド（生成されていない値 0）と、Python の版で `values.json` の最後の桁が変わる問題の直し（`math.fsum`・判断 191）
    - [x] 表の道具に Windows の 2 つの定義の差の大きさ（Z40）→ 2026-10-06（G-GEAR・判断 192）: 登録 §5 が「報告しない」としていたので研究者の選択で逸脱 D12・§6 に数と値・補遺に両定義の表
    - [x] 原稿の attack-me round 2 → **minor**（R1・R2・R3 とも・有効 3/3・捏造 0・注入 0・偽陽性 1）→ 研究者の採否（判断 204・8 問とも推奨）→ 直した（`round-2/verdict.md` §8）→ 点検（security 0・code MEDIUM 5・LOW 10）と /cross-review 2 巡の直し → 研究者が直した Discussion と AI 宣言を改めて採った（2026-10-06・G-GEAR）→ PR → CI → merge
    - [x] round 3 を回すか → 回さない（2026-10-06・研究者の選択・判断 206）。`round-1/tmp/`・`round-2/tmp/` を消した
    - [x] 著者・所属・Funding・利益相反・貢献（研究者・判断 185）と AI Declaration（判断 185〜187）→ PR #309 で main に
    - [ ] 研究者が結果・推奨・限界・結論を読んで直す（判断 185・186・投稿の前・AI Declaration の前提）＋ Discussion を研究者の解釈から書く（判断 188-6）＋ 断りの重複を削る（Z10）
      - [x] 読み直しの資料 `reading-results-discussion.md`（主張 ↔ 根拠・Discussion の事実 F1〜F8 と問い・断りの重複）を渡した（2026-10-06・判断 193）
      - [x] Discussion: 研究者の方向性 → 事実と照らし Codex に第二意見 → D12 の層ごとの範囲 → 5 段落を英語に → 研究者が採った → 点検と /cross-review 2 巡の直し（2026-10-06・判断 195〜199）
      - [x] 研究者の答え（§A は今のまま・§C は案どおり・§B.4 の 5〜7・Discussion の仕上げの方針）を受けた（2026-10-06・判断 200）
      - [x] 判断 200 の方針で Discussion を仕上げ（数字を §6 に寄せる・観測可能性と書字研究の尺度の段落・研究者が採った）、断りを寄せた（−235 語）（2026-10-06・判断 201・202）
      - [x] 点検（code-reviewer ∥ security-checker）・/cross-review 2 巡の指摘を直した（2026-10-06・判断 203）→ PR → CI → merge
    - [ ] OSF のプロフィール名が「Mikto Miura」→ 研究者に確かめてもらう（判断 189 の記録）
    - [ ] M12: Zenodo の下書きと DOI の予約・GitHub の公開 repo・原稿の `\tbd` の DOI と URL・データの引用（進め方は判断 207）
      - [x] 研究者の 4 点（リリースの DOI は手で予約・repo 名・履歴の 4 commit と非公開の参照の置き換え・書庫は G-GEAR に集める）（判断 207）
      - [x] Zenodo の下書き 2 つと DOI の予約: データセット `10.5281/zenodo.23183438`・ソフトウェア `10.5281/zenodo.23183441`（判断 208）
      - [ ] 非公開の repo `mikotomiura/ime-conversion-logging` を作り（済）、A・B・C を push（タグ 2 つ）→ ⚠️ push は自動モードで拒まれた・研究者が `C:/wt/ime-conversion-logging.git` から push する
      - [x] 書き出しの道具を .tex・.bib と LaTeX の ignore に対応させ、`rv@` を `rv:` に、研究者のアドレスだけを通す（selftest・変異 10 本・判断 208）
      - [x] 非公開の commit の参照 12 か所の置き換え・`\tbd`（DOI・URL・外枠の commit・表 1 の版）・`references.bib`・CITATION.cff・.zenodo.json・ライセンスの全文・.gitattributes・凍結の一覧を計算し直す手順（README）（判断 209）
      - [x] README の先頭にロゴと動く SVG（研究者の求め・判断 210）
      - [x] 作業中の点検（code-reviewer ∥ security-checker）の指摘 14 件を直した（判断 211）
      - [x] 研究者が公開 repo に A〜C を push した（2026-10-06・`git ls-remote` で main = `cb29a1a9…`・タグ 2 つが A・B を指す・非公開のまま）
      - [x] PR #316 の /cross-review 2 巡（Codex・パス限定 3 回）の指摘を直した（SVG を XML として読む層・文字参照を戻した走査・凍結の一覧の手順・`xml:base` ほか・変異 21 本すべて赤・本番の形の書き出し exit 0・`kit/check.sh` 31 本が緑）（2026-10-06・G-GEAR・判断 212）→ CI → merge
      - [ ] GitHub での README（ロゴ・動く図）の見え方を確かめる（ロゴと図はリリース D の README に入る → D を push した後）
      - [ ] datasheet（Claude の下書き → AI 宣言に足す → 研究者が確かめる）
        - [x] 下書き `experiment/datasheet.md`・点検（code ∥ security）の指摘で書き直し・研究者の 5 問（連絡先はメール・§10.8 の確かめの run はパイロットの部・青空文庫の出どころと作業履歴・方針の文）・書き出しの例外・`dataset.tex`・AI 宣言（2026-10-06・G-GEAR・判断 213・枝 `docs/ime-m12-datasheet`）
        - [ ] 研究者が全文を日本語で確かめる（`datasheet-reading-ja.md`）→ 直し → /cross-review → PR → CI → merge
        - [ ] 寄託のとき: 「(to be filled in at deposit)」を埋める（G-GEAR §2.4）
      - [ ] Mac / Surface: working・パイロット・標本の書庫（`--pack`・`--check-deposit`）→ SHA-256 を記録 → G-GEAR へ。A〜D を各機械で書き出し直して exit 0 と一覧の一致
      - [ ] G-GEAR: 書庫を照らして下書きに上げる → 「at deposit」の 6 か所と `confirmed at deposit` → D を作る → 研究者に公開を確かめる（repo を公開・Zenodo 2 つを公開）
  - [ ] ★ 別タスク（判断 151-2）: GSE 本体の `docs/agent-shared.md` 技術的制約 7 の「macOS 側（公開 API が存在しない）」と `.steering/20260821-workspace-behavior-triage/survey-input-channels.md` §7.5 を一次（WebKit のソース・Apple の定数の一覧）に戻して直す
- [ ] /finish-task
