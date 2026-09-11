# 詰まりと解決

## 起票 1: macOS `secure_input` 行の実送出状況が不明（P4）

- **起票日**: 2026-09-11
- **状態**: 未解決
- **内容**: `src-tauri/src/schema_dto.rs` の doc コメントは `secure_input` 行について
  「2026-08-23 時点で送出元なし（スタブ）」と書いているが、`src-tauri/src/input/observe_macos.rs` は
  `SECURE_INPUT_AVAILABLE = true` になっている。**doc とコードが食い違っている。**
- **なぜ問題か**: ⚠️ `secure_input`（パスワード欄など macOS が入力を秘匿する状態）が
  記録されないまま O1 を配布すると、**「打鍵ゼロ」と「打鍵が見えない」が区別できないデータ**が
  本番に紛れ込む。停滞の誤判定に直結する。
- **どう処理するか**: 確認作業は 5 分程度で issue の粒度に満たないため、
  **Wave 0 完了時のチェック項目として処理する**（`decisions.md` 判断 5）。
  1. `observe_macos.rs` が実際に `secure_input` 行を送出しているかコードで確認
  2. 送出していれば `schema_dto.rs` の doc を訂正
  3. 送出していなければ `SECURE_INPUT_AVAILABLE` を `false` にするか、送出を実装する
  4. ⚠️ どちらにせよ **O1 配布前に決着させる**
- **解決**: （未）

## 起票 2: `gse-dataset` 側 `metrics.json` の後方互換

- **起票日**: 2026-09-11
- **状態**: 未解決（外部 repo のため本タスクでは確認のみ）
- **内容**: ADR-024 が `metrics.rs` の識別子を改名する（`recovery` → `pflow_exit`、
  `self_recovery_without_paste` → `pflow_exit_without_receipt` 等）。
  ⚠️ **ADR-024 自身が「`gse-dataset` 側 `metrics/P*/<os>/metrics.json` の後方互換は
  実在する懸念」と自認している。**
- **なぜ問題か**: `gse-dataset`（private repo・本機では `C:\gse-dataset`）に
  既に置かれている `metrics.json` は旧フィールド名を持つ。
  ⚠️ **schema drift check の対象外**なので、壊れても無音。
- **どう処理するか**:
  1. issue 001 の実行時に `C:\gse-dataset` の `metrics/P*/<os>/metrics.json` を確認
  2. 旧フィールド名を使っている既存ファイルがあるか、`scripts/build_analysis_db.py` が
     新旧どちらを期待するかを突き合わせる
  3. ⚠️ **外部 repo を勝手に書き換えない。** 対応が要るなら研究者にエスカレートする
- **解決**: （未）

## 起票 3: `_issue-plan.md` の自己検査で `acceptance.sh` が未作成

- **起票日**: 2026-09-11
- **状態**: 未解決
- **内容**: `issue-slicing` の締めの自己検査項目
  「**test/lint が無条件に緑になる issue に `acceptance.sh` を書いたか**」が未実施。
- **なぜ問題か**: ⚠️ issue 002 / 003 / 005 / 006 は**何も取り込まなくても**
  `check_doc_lexicon.py` / `check_citations.py` が exit 0 になる。
  このまま無人ループに載せると「**客観に見えて無意味な緑**」を量産する
  （`docs/loop-engineering.md` が警告する failure mode そのもの）。
- **どう処理するか**: 実行セッションで各 issue に `acceptance.sh` を書く。例:
  - 002: ADR-025〜028 の 4 ファイルが存在し、README のテーブルに ADR-023〜028 の 6 行がある
  - 003: `references.md` に `[P356]` と `[V145]` が存在し、`literature/` に新規カード 3 本がある
  - 005: `mitou_submission/` の図版数が取り込み前より増えている
  - 006: 7 ファイルそれぞれに branch 側の差分が反映されている
- **解決**: （未）

## 起票 4: ⚠️★★★ AC 6 (macOS 実機で確定 / 放棄が区別できること) が未実施

- **起票日**: 2026-09-11
- **状態**: ⚠️ **一部解決**（★ CI の macOS ビルドは通った。**実機確認だけが残る**）
- **内容**: issue 008 の AC 6 は「実機で日本語変換を ①確定 ②ESC 放棄 の 2 通り行い、
  生成された NDJSON の `ime_shadow` 行で `abandon` が区別されていること」を求めるが、
  ⚠️ **本セッションは Windows 機 (G-GEAR) で動いており実施できない**。
- **なぜ問題か**: ⚠️ `input/` の OS フックは**実機手動確認が規約**である
  (`docs/agent-shared.md` テスト方針)。★ さらに macOS は `hook_macos.rs` が
  Windows では 1 行もコンパイルされないため、⚠️ **本機では macOS のコンパイルすら通していない**。
  → ★ 判断ロジックとドライバは `input/ime_compose.rs` (OS 非依存) に出して
    Windows で 28 テストを緑にしてあるが、⚠️ **CGEventTap が実際にそのキーを届けるか**は
    実機でしか分からない。
- **どう処理するか**:
  1. ✅ ★ **CI (self-hosted macOS runner) で macOS ビルドが通った** —— PR #182 /
     `check (gse-mac-selfhosted, aarch64-apple-darwin)` が **pass (4m54s)**。
     ⚠️★★★ **これで「macOS でコンパイルすら通していない」という状態は解消した。**
     ★ ただし CI が保証するのは**コンパイルと `analysis/` のテスト**までで、
     ⚠️ **CGEventTap が実際にそのキーを届けるか**は依然として実機でしか分からない。
  2. ⚠️ **残るのはこれ** —— mac 側で実機確認:
     - 日本語変換を ①Enter で確定 ②ESC で放棄
     - NDJSON の `ime_shadow` 行で `abandon` が `false` / `true` に分かれることを確認
     - ⚠️ **macOS 純正の「ライブ変換」でも試す** (起票 6)
  3. 結果を `design-008-macos-ime-shadow.md` §7 に追記する
- **解決**: （未）

## 起票 5: `schema/current.json` を再生成したので `gse-dataset` 側と drift する

- **起票日**: 2026-09-11
- **状態**: 未解決（⚠️ **外部 repo なので勝手に書き換えない**）
- **内容**: `schema_dto.rs` の `ImeShadow` doc から「Windows のみ」を外したため、
  `schema/current.json` の `description` が 1 行変わった。
  ★ **構造 (フィールドの追加 / 削除 / 改名) は 1 つも変わっていない**ので既存ログは妥当である。
  ⚠️ しかし `scripts/check_schema_parity.py` は **意味等価**を見るので、
  `gse-dataset` (`C:\gse-dataset`) の `schema/current.json` と食い違う。
- **なぜ問題か**: ⚠️ `sync-all.ps1` / `sync-all.sh` の pre-flight で落ちる
  （★ ファイルコピーや `gse-replay` 実行の**前**に fail-fast する設計）。
- **どう処理するか**:
  1. `python scripts/check_schema_parity.py --dataset C:/gse-dataset` で drift を確認
  2. ★ スクリプトが出す repair コマンドどおりに `gse-dataset` 側へコピーする
  3. ⚠️ **外部 repo のコミットは研究者が行う**
- **解決**: （未）

## 起票 6: ⚠️ macOS 純正「ライブ変換」下での ESC の挙動が未検証

- **起票日**: 2026-09-11
- **状態**: 未解決
- **内容**: `.steering/20260821-workspace-behavior-triage/survey-input-channels.md:153` 逐語:
  「⚠️ **macOS 純正の「ライブ変換」は Space を押さずに変換が進む**ので、推定が特に外れる。」
- **なぜ問題か**:
  - ★ 本実装はセッションを **`composing` の寿命**（最初の英数字キー 〜 終端キー）に取ったので、
    **Space を押さないライブ変換でもセッション自体は成立する**（`active` が立たないだけ）。
    → ★ 旧来の「`active` (候補表示) に合わせる」案より**ライブ変換に強い**。
  - ⚠️ **ただし ESC の意味が違う可能性がある。** ライブ変換では ESC 1 回で「読みに戻す」だけで、
    変換の放棄になるとは限らない。→ ⚠️ **`abandon` が過大に立つおそれ**。
  - ⚠️ この点はリポジトリ内に**一次記録が無い**（推測で埋めない）。
- **どう処理するか**: 起票 4 の実機確認で**ライブ変換 ON / OFF の両方**を試し、
  ESC 1 回・2 回の挙動を記録する。★ 外れるなら `ime_compose::step` の `0x1B` 腕を見直す。
- **解決**: （未）

## 起票 7: ⚠️ macOS の `dwell_ms` は **1 変換分とは限らない**（★ 直せない限界・解析側の前提）

- **起票日**: 2026-09-11（`/cross-review` の Codex 指摘 #2 を受けて）
- **状態**: ⚠️ **直せない**（★ 打鍵が無い終端は原理的に観測できない）。**周知が対処**。
- **内容**: macOS のセッションは「最初の英数字キー 〜 終端キー」で区切るため、
  **打鍵を伴わない確定**は終端として観測できず、⚠️ **その変換は次の変換と合算される**。
  該当するのは:
  1. **マウスで候補をクリックして確定**した変換
  2. 候補表示中の**数字キー**による確定（本状態機械は英数字として扱いセッションを続ける）
- **⚠️ なぜ問題か**: ★ これは**欠測ではない**。行は出るが `dwell_ms` が
  **2 つ以上の変換を覆う**。⚠️ 「1 行 = 1 変換」と仮定して解析すると
  **変換時間の分布が右に伸びる**（`nav` / `abandon` も合算される）。
  ⚠️★★★ 2026-09-11 まで `ime_compose.rs` の doc は「次の打鍵で『その他キー』として閉じる」
  と書いていたが **誤りだった**（★ マウス確定のあとは打ち続けるのが普通で、
  次の打鍵は英数字なのでセッションは継続する）。→ 訂正済み。
- **どう処理するか**:
  1. ✅ `ime_compose.rs` のモジュール doc / `schema/current.json` の `description` に明記済み
  2. ✅ 回帰テスト `a_mouse_confirmed_conversion_merges_into_the_next_one` で**挙動を固定**した
  3. ⚠️ **起票 4 の実機確認で、マウス確定をどれくらい使うかを観察する**
     （★ 頻度が高いなら `dwell_ms` の解析上の扱いを決め直す必要がある）
  4. ★ 上限 `MAX_SESSION_MS`(20 秒) が最終的な歯止めになる（超えたら行を出さない）
- **解決**: （★ 直せない。周知と記録で閉じる）

## 起票 8: `hook` ↔ `lib` の時系列競合を突く統合テストが無い（★ 次 issue へ）

- **起票日**: 2026-09-11（`/cross-review` の Codex 指摘 #4）
- **状態**: 未解決（★ 本 issue のスコープ外）
- **内容**: 純粋層 (`ime_compose::step`) と Atomic ドライバ (`drive`) の単体テストは
  37 本あるが、⚠️ **`lib.rs` の IME Monitor スレッドとの時系列競合**
  （`READY=true` の最中に次セッションが始まる / G1 のブロック境界で `READY` が立つ）を
  端から端まで通すテストは無い。
- **なぜ問題か**: ★ 今回の HIGH-1（`abandon` の偽装）は**まさにこの層の競合**だった。
  ⚠️ 単体テストで再現できたのは、ドライバを OS 非依存にして Atomic を直接叩けたからである。
  → ★ 同型の欠陥がもう 1 つあっても、いまの粒度では見えない可能性がある。
- **どう処理するか**: ★ 次の issue でバックログ化する。
  `drive` と `emit_ime_shadow` を同じテスト内で交互に呼ぶ統合テストを 1 本置けば足りる見込み。
- **解決**: （未）
