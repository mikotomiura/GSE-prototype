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
- [ ] ★ main への merge（判断 72・2026-09-30・研究者が「今日・Codex の上限を一時的に引き上げる」を選択）
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
  - [ ] PR #276 の CI 緑なら merge → main の CI を確かめる
  - [ ] ⚠️ Mac: 024-acceptance.sh を回し、一覧の SHA-256 が Windows と一致するか・POSIX だけの検査（読めない dir・実行権限）が緑か（判断 68）
- [ ] M0〜M13（`_issue-plan.md` §5）。★ 凍結物は **`papers/ime-observation/experiment/preregistration.md`**（判断 21 で `experiments/<date>-…/` から変更）
- [ ] 論文の外枠（節構成・主張 ↔ 根拠の対応表）を `papers/ime-observation/manuscript/outline.md` に置く（★ 判断 21）
- [ ] /finish-task
