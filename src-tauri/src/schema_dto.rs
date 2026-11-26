//! Phase 1 dataset-repo-setup: NDJSON セッションログの JSON Schema を機械生成するための
//! DTO (Data Transfer Object) ミラー型。
//!
//! **本モジュールは production path ではない**。logger::LogEntry の手書き NDJSON 出力を
//! 忠実に反映したミラー型であり、`bin/emit_schema` からのみ使用される。schemars による
//! JsonSchema 派生と serde Serialize のみが目的で、実際の NDJSON 書き込みは `logger.rs`
//! の `writeln!` ベース実装が行う (float フォーマット固定のため手書き実装を維持)。
//!
//! ## なぜ DTO ミラーが必要か
//!
//! `logger::LogEntry` は `f64` の小数桁数固定フォーマット (`{:.4}`) を `writeln!` で
//! 直接指定しており、`serde::Serialize` 経由で出すと形式が崩れて gse-replay の
//! ゴールデン byte-equal が落ちる。したがって `LogEntry` 本体には `Serialize` を
//! 派生させない方針で、schema 生成のためだけに本 DTO を用意する。
//!
//! ## 追加時のメンテ
//!
//! `LogEntry` に新バリアントや新フィールドが入ったら、本 DTO も同期する必要がある。
//! 同期漏れは `.github/workflows/ci.yml` の schema drift check で機械的に検知される
//! (emit_schema の出力が `src-tauri/schema/current.json` と diff すると CI が FAIL)。

use schemars::JsonSchema;
use serde::Serialize;

/// NDJSON 1 行の種別を表す tagged union。`type` フィールドでバリアントを識別する。
/// logger::LogEntry の NDJSON 出力と同じ shape。
#[derive(Serialize, JsonSchema)]
#[serde(tag = "type", rename_all = "snake_case")]
pub enum LogEntryDto {
    /// セッション境界マーカー。
    /// - 開始: `{"type":"meta","session_start":<ms>,"hmm_version":"<semver>"}`
    /// - 終了: `{"type":"meta","session_end":<ms>}`
    ///
    /// **排他制約 (schema では表現されていない producer 側の事実上のルール)**:
    /// 実際の `logger.rs` は上記 2 形状のどちらか一方しか emit しない。
    /// 具体的には:
    /// - start: `session_start` と `hmm_version` が Some、`session_end` は None
    /// - end:   `session_end` が Some、他 2 つは None
    /// 「3 つとも Some」「3 つとも None」「start と end を同時に」は不正だが
    /// schemars の tagged enum では 2 形状を別 variant にすると同一 tag 衝突が
    /// 発生するため、スキーマ上は loose にして Option 3 つを並列にしている。
    /// validator 側の追加チェックを入れたい場合は外部 JSON Logic で補う。
    //
    // ⚠️★★★ **この doc は整形してはならない** (clippy `doc_lazy_continuation`)。
    //   ★ このファイルの doc コメントは **schemars が JSON Schema の `description` に載せる**
    //     (⚠️ `schema/current.json` に本文がそのまま入っている・2026-09-12 実測)。
    //   ★ 連続行は**空白**で連結され、空の `///` 行は **`\n\n`** になる。
    //     → ⚠️ 字下げも空行の挿入も **description の文字列を変え、schema drift になる**
    //       (`emit_schema` の byte-equal 比較と gse-dataset 側の parity が同時に落ちる)。
    //   → ★ 見た目の是正よりも**外部契約の不変**を採り、lint をここだけ黙らせる。
    #[allow(clippy::doc_lazy_continuation)]
    Meta {
        #[serde(skip_serializing_if = "Option::is_none")]
        session_start: Option<u64>,
        #[serde(skip_serializing_if = "Option::is_none")]
        hmm_version: Option<String>,
        #[serde(skip_serializing_if = "Option::is_none")]
        session_end: Option<u64>,
        /// G1 統制タスク実験モードの引き金 (`"marker"` | `"env"`)。**start 形状のみ**。
        ///
        /// ⚠️ ★ **G1 実施時にしか出ない**ので、通常運用の NDJSON は従来と byte 単位で同一である
        /// (ゴールデンスナップショットと既存フィクスチャの非回帰がこれに依存する)。
        ///
        /// ★ なぜ記録するか: マーカーが外れる / アプリをフォルダの外に出す /
        /// launcher の `open -a` で通常アプリが起動する、のいずれでも**黙って通常モードになる**。
        /// この行が無いブロックは「G1 モードで取れていない」と**事後に判定できる**
        /// (`preregistration.md §5.4` 第 10 版 / `.steering/20260805-g1-app-mode-and-log-rotation`)。
        #[serde(skip_serializing_if = "Option::is_none")]
        g1_mode: Option<String>,
        /// ⚠️★★★ O1 (R3-a・自然作業の常時収集) モードの引き金 (`"marker"` | `"env"`)。
        /// **start 形状のみ**。
        ///
        /// ⚠️ ★ **O1 実施時にしか出ない**ので、通常運用 / G1 の NDJSON は従来と byte 単位で
        /// 同一である (★ ゴールデンスナップショットと既存フィクスチャの非回帰がこれに依存する)。
        ///
        /// ## ★ なぜ記録するか (研究者判断 R-1・2026-08-26)
        ///
        /// ⚠️ 当初はファイル名 (`gse_o1_*`) だけで表していたが、
        /// ★ **提出物そのものを見て「O1 モードで取れていたか」を事後に判定できない**。
        /// ⚠️ セッション置き場は**被験者が書き込めるフォルダ**なので、
        /// リネームは事故でも故意でも起こりうる (cross-review / Codex 指摘)。
        /// → ★ `g1_mode` と**同じ形**で `meta` 行に刻み、**記録の中身を根拠にする**。
        ///
        /// ⚠️ **`Option` である** —— ★ 2026-08-26 より前の NDJSON には本フィールドが無いので、
        /// `required` に入れると**旧ログが schema 検証に落ちる** (ADR-005 の additive-only 違反)。
        #[serde(skip_serializing_if = "Option::is_none")]
        o1_mode: Option<String>,
        /// ⚠️★★★ O1 の**導入ごとの識別子** (16 桁の小文字 hex・導入時に乱数で生成)。**start 形状のみ**。
        ///
        /// ★ 目的: 1 人が複数端末で O1 を走らせても、**解析で端末を分けられる** (2026-10-07・研究者判断)。
        /// ⚠️ **ハードウェア・MAC・ホスト名・ユーザー名・OS の機械 ID は使わない** (ADR-013 D6)。
        /// ⚠️ **O1 実施時にしか出ない** (通常運用 / G1 の NDJSON は従来と byte 単位で同一)。
        /// ⚠️ **`Option` である** —— 旧ログ (v0.1.39 以前の O1 を含む) には無いので `required` に入れない (ADR-005)。
        #[serde(skip_serializing_if = "Option::is_none")]
        #[schemars(regex(pattern = r"^[0-9a-f]{16}$"))]
        o1_install_id: Option<String>,
        /// 段 1（ADR-043・C4 のプローブと日の終わりの問い）モードの引き金 (`"marker"` | `"env"`)。**start 形状のみ**。
        ///
        /// 段 1 は O1 の上に載せた層なので、段 1 のときは `o1_mode` も出る。O1 の記録と分けるのはこの
        /// フィールドである。EH3 と同時には出ない（両方の印があれば両方を落とす）。
        /// 段 1 の実施時にしか出ない（印の無い O1 の NDJSON は従来と byte 単位で同一）。
        /// `Option` である（旧ログには無い・ADR-005）。
        #[serde(skip_serializing_if = "Option::is_none")]
        s1_mode: Option<String>,
        /// EH3（肖像と招待の参加者内比較）モードの引き金 (`"marker"` | `"env"`)。**start 形状のみ**。
        ///
        /// EH3 は O1 の収集の器に載せた層なので、EH3 のときは `o1_mode` も出る。O1 の記録と分けるのはこの
        /// フィールドである（`.steering/20261011-portrait-eh3-impl/decisions.md` 判断 3 #1・R-L5）。
        /// EH3 実施時にしか出ない（通常運用 / G1 / O1 の NDJSON は従来と byte 単位で同一・R-L6）。
        /// `Option` である（旧ログには無い・ADR-005）。
        #[serde(skip_serializing_if = "Option::is_none")]
        eh3_mode: Option<String>,
        /// 招待用の研究の条件（EH3 のときだけ出て、常に `true`）。**start 形状のみ**。
        ///
        /// `session_meta.intervention_enabled`（Nudge の研究の条件）とは別に持つ。EH3 では Nudge は出さず
        /// 招待だけを出すので、条件を 2 つとも記録に残して取り違えを防ぐ（ADR-035 D1 の内側の制約 ④ を
        /// 招待の条件として読む・`.steering/20261011-portrait-eh3-impl/decisions.md` 判断 1 #1 = R-1 (i)）。
        /// `Option` である（ADR-005）。
        #[serde(skip_serializing_if = "Option::is_none")]
        invitation_enabled: Option<bool>,
        /// 招待の契機の段 (`"main"` | `"proto"`)。EH3 のときだけ出る。**start 形状のみ**。
        ///
        /// `proto` は試作と利用者の検証の段で、招待を出やすい側の契機の値を使う。本番の値は
        /// `proto` の記録を根拠に凍結の前に決めるので、解析で 2 つの段の記録を分けるためにこの欄を読む
        /// （`.steering/20261012-eh3-trigger-values/`）。`Option` である（旧ログには無い・ADR-005）。
        #[serde(skip_serializing_if = "Option::is_none")]
        invitation_trigger: Option<InvitationTriggerDto>,
        /// ★ アプリの版 (**粗い semver のみ**)。**start 形状のみ** (ADR-013 D1)。
        ///
        /// ⚠️ git SHA / ビルドホスト名 / ビルド時刻 / マシン GUID は
        /// **フィンガープリントになる**ので入れない (D6)。
        #[serde(skip_serializing_if = "Option::is_none")]
        app_version: Option<String>,
        /// ★★★ **このビルドが何を記録できたか** (ADR-013 D1)。**start 形状のみ**。
        ///
        /// ⚠️ 解析側は `unconditional` の行が 0 行なら「**信号が無かった**」、
        /// `threshold_gated` の行が 0 行なら「**判定不能**」、
        /// どちらにも無いなら「**計器が無かった**」と機械判定する。
        /// ★ `hmm_version` では代用できない (HMM の版であって記録能力ではない)。
        #[serde(skip_serializing_if = "Option::is_none")]
        capabilities: Option<CapabilitiesDto>,
        /// ★ **キーボードレイアウトの識別子**（O1 / ADR-014 D4）。**start 形状のみ**。
        ///
        /// 例: Windows `00000411`（日本語）/ macOS `com.apple.keylayout.US`。
        ///
        /// ## ⚠️★★★ なぜ要るのか
        ///
        /// ★ **文境界の妥当性が配列に依存する** —— macOS の keycode は**物理キー位置**なので、
        /// Dvorak では `.` が US の `E` の位置に来る。→ ★ どの配列だったかが後から要る。
        ///
        /// ⚠️★★★ **文字への変換はしていない**（`ToUnicodeEx` / `UCKeyTranslate` を呼ばない）。
        /// ★ 取れなかった端末では**フィールドごと出ない**（0 値で埋めない）。
        #[serde(skip_serializing_if = "Option::is_none")]
        keyboard_layout: Option<String>,
    },
    /// ユーザーが「開始する」ボタンを押した時刻。
    SessionStart { t: u64 },
    /// キーストロークイベント (**キー種別カテゴリ** + 押下/離上)。
    ///
    /// ⚠️★★★ **2026-08-23 (ADR-014 判断 6): `vk` (生 VK コード) から `category` へ変えた。**
    /// `consent.md` の記録項目表は「キーの**種類**」と約束しており、生 VK (キー個体) を
    /// ローカル NDJSON に残すのは文言とずれていた。量子化は従来 transfer 境界
    /// (`gse-package`) でのみ効いていたが、`logger.rs` の書き出し境界へ前倒しした。
    ///
    /// 値は `analysis::anonymize::KeyCategory::as_str()` の 14 種:
    /// `alphabetic` / `numeric` / `punctuation` / `sentence_punctuation` / `tab` /
    /// `backspace` / `delete` / `space` / `enter` / `navigation` / `modifier` /
    /// `function` / `escape` / `other`。
    ///
    /// ⚠️ **旧ログ (`vk` を持つ) は `gse-replay` がそのまま読める** (`resolve_key_vk` が
    /// `vk` を優先し、無ければ `category` を代表 VK へ逆写像する)。
    Key {
        t: u64,
        category: String,
        press: bool,
    },
    /// ペーストイベント (Ctrl+V / Cmd+V) の発生時刻と文字数。
    /// AI 依存度指標 (D4) 向けに**回数** (行数) を、(b) 自力解決率 (v0.4 §4.2
    /// `manual_contribution_ratio`) 向けに `external_paste_chars` (ペースト**文字数=整数のみ**)
    /// を記録する。1 ペースト = 1 行。VK + 修飾キー状態から検出し、クリップボードは
    /// **長さのみ取得して中身は即破棄**する (**中身は一切記録しない**・data-privacy CD1)。
    /// 旧フィクスチャ互換のため `external_paste_chars` は省略可 (取得不能時も `null`)。
    Paste {
        t: u64,
        external_paste_chars: Option<u64>,
    },
    /// 1Hz ゲートで吐かれる特徴量 + HMM 状態確率 + 診断データ。
    ///
    /// **obs の型について**: `logger::LogEntry::Feat` 本体では `obs: usize` だが、
    /// schema 上は `u64` に格上げしている。理由:
    /// - `usize` は 32-bit ターゲットで u32 に縮む可能性があり、schema の
    ///   `uint64` 指定と実 NDJSON 数値表現の間に乖離が生まれる
    /// - 実運用では obs は 0..=25 の小さな整数しか入らないため u64 で十分安全
    /// - 将来 usize → u64 の意図的格上げを logger 側に反映する場合でも schema は不変
    Feat {
        t: u64,
        f1: f64,
        f3: f64,
        f4: f64,
        f5: f64,
        f6: f64,
        p_flow: f64,
        p_inc: f64,
        p_stuck: f64,
        raw_x: f64,
        raw_y: f64,
        ewma_x: f64,
        ewma_y: f64,
        obs: u64,
        alpha: f64,
        /// ★ Tier 0 (記録のみ): 特徴量ウィンドウ内の総キー押下数 (= `f3` の分母)。
        /// **打鍵の数のみ**で、どのキーか・何を書いたかは含まない (data-privacy CD1)。
        ///
        /// ⚠️★★★ **累積カウンタではなく、窓の右端は「最後の打鍵時刻」であって `t` ではない。**
        /// **沈黙中は同じ値が毎秒くり返される**ので、**feat 行をまたいで足し上げてはいけない**
        /// (実測つきの説明は `analysis/loop_step.rs` の `FeatSnapshot::keys` の doc が正本)。
        ///
        /// ⚠️ **producer は常に値を書く**が、schema 上は省略可 (`Option`) にしている。
        /// Tier 0 配線より前に収集された NDJSON には本フィールドが無く、それらも
        /// この schema で検証できる必要があるため (`Paste.external_paste_chars` と同じ扱い・
        /// ADR-005 additive)。「読むときは省略可・書くときは必須」の非対称は意図的。
        ///
        /// ⚠️★ HMM にも X/Y 合成式にも流していない (記録のみ)。`HMM_VERSION` は不変。
        #[serde(default)]
        keys: Option<u64>,
        /// ★ Tier 0 (記録のみ): 特徴量ウィンドウ内の BS/Del 押下数 (= `f3` の分子)。
        /// `f3` は `{:.4}` 丸めのため、`keys − bs_keys` を整数で得るには分子も整数で必要になる。
        /// 窓の意味・省略可の理由は `keys` と同じ。
        #[serde(default)]
        bs_keys: Option<u64>,
    },
    /// IME 入力モード/候補ウィンドウ状態の切替。
    ImeState { t: u64, on: bool, active: bool },
    /// ⚠️★★★ **記録の一時停止 / 再開の遷移** (O1 / ADR-014 **D7-ii**)。
    ///
    /// ★ 被験者が「止める」「再開する」を押した**瞬間**に 1 行。`paused=true` が停止、
    /// `false` が再開である。⚠️ **状態が変わらない押下では出ない**（★ 回数を残さない）。
    ///
    /// ⚠️★★★ **これが無いと「被験者が止めていた時間」と「信号が無かった時間」を
    /// 事後に区別できない**（ADR-013 D1 と同じ理屈）。
    /// ★ 一時停止中も本行と `meta` だけは書かれる（`recording::is_writable_while_paused`）。
    RecordingPause { t: u64, paused: bool },
    /// ⚠️★★★ **フォーカス遷移の時刻**（O1 / ADR-014 **D4** の L-c）。
    ///
    /// ★ フィールドは `t` **だけ**である。⚠️ HWND / PID / アプリ識別子 / ウィンドウタイトル /
    /// 通し番号は 1 バイトも含まない（★ 擬似識別子になるため・D4 の禁止表）。
    ///
    /// ⚠️★★★ **「注意の逸脱の頻度」として読んではならない** ——
    /// ★ 同一アプリ内のウィンドウ切替も同じ 1 行になり、両 OS とも識別子なしには分離できない。
    /// ★ 言えるのは **遷移の時刻**と、2 時刻の差である**離脱の滞在時間**まで。
    FocusTransition { t: u64 },
    /// ⚠️★★★ **ポインタ活動の 1 秒ビン**（O1 / ADR-014 **D4** の L-b）。
    ///
    /// ★ すべて**粗い量子化スカラ**である。⚠️ 座標・軌跡・方向・速度・解像度は含まない
    /// （★ 累積すれば軌跡が復元でき画面内容の代理になるため）。
    ///
    /// ⚠️ **ゼロ抑制**されている（D5）—— 活動が無い秒には**行が無い**。
    /// → ★ 「行が無い＝活動が無かった」と読んでよい（⚠️ ただし `capabilities` に
    /// `pointer_bin` がある場合に限る。無ければ「計器が無かった」である）。
    PointerBin {
        t: u64,
        /// 移動量のバケット `0..=7`（★ `Σ(|dx|+|dy|)` の対数的な階級。⚠️ 単位はデバイス依存）。
        moved: u8,
        /// ボタン**押下**回数（★ `0..=15` に飽和）。⚠️ どのボタンかは含まない。
        buttons: u8,
        /// ホイールの刻み回数（★ `0..=15` に飽和）。⚠️ 向きは含まない。
        wheel: u8,
    },
    /// ⚠️★★★ **`EnableSecureEventInput` の区間フラグ**（O1 / **macOS のみ**）。
    ///
    /// ★ 有効な間は **tap が「有効」のまま KeyDown だけが届かない**ので、
    /// ⚠️ この行が無いと「**打鍵ゼロ**」と「**打鍵が見えない**」を混同する。
    ///
    /// ⚠️ **2026-08-23 時点で送出元は無い**（macOS 実装がスタブ）。
    /// ★ `capabilities` にも宣言していないので、0 行は「**計器が無かった**」と読む。
    SecureInput { t: u64, on: bool },
    /// ⚠️★ キーボードフックの生存状態の変化 (`input::liveness`)。
    ///
    /// `alive=false` は「フックは設置済みだが、システムに入力があるのに
    /// コールバックが呼ばれていない」状態を指す。★ **判断ではなく測った量** (`starved_ms`) を
    /// 併記するので、解析側が閾値を変えて再解釈できる。
    /// 背景: `windows-verification.md` §5-7 (5 分間 0 打のブロックが正常提出された)。
    HookHealth {
        t: u64,
        alive: bool,
        starved_ms: u64,
        rehook: bool,
        /// 分析スレッドへ渡せずに捨てた打鍵イベントの累計。
        /// ★ 「フックが呼ばれた」と「記録できた」は別なので両方残す。
        dropped: u64,
        /// ⚠️★ **前の `hook_health` 行からの `dropped` の増分** (ADR-013 D4・穴 B)。
        /// ★ `dropped` は累積なのに解析側が「この区間で落ちた」と読む誤りが実際に起きたため、
        /// 改名 (breaking) ではなく**併記**で誤読を消す。
        ///
        /// ## ⚠️★★★ なぜ `Option` なのか (現行コードは**必ず**書くのに)
        ///
        /// ★ 本 DTO は「**このバージョンが出す形**」ではなく「**NDJSON がとりうる形**」を表す。
        /// ⚠️ **2026-08-19 より前のログには本フィールドが無い**ので、`required` に入れると
        /// **旧ログが schema 検証に落ちる** ＝ ADR-005 の additive-only と、ADR-013 Consequences
        /// 逐語「`required` を増やさないので**旧ログは読めるまま**」に反する。
        /// ★ 実際 `emit_schema` の diff で `required` に入ったのを見て `Option` へ直した
        /// (2026-08-19)。★ `g1_mode` が `Option` なのと同じ理由である。
        #[serde(skip_serializing_if = "Option::is_none")]
        dropped_delta: Option<u64>,
    },
    /// ★ 30 秒未満の在席×非打鍵 (micro 帯) の 60 秒窓集計 (ADR-013 D4・穴 A)。
    ///
    /// ⚠️ **`n_lt30 == 0` の窓は出力されない** —— 毎分必ず 1 行出すと
    /// 「分単位の在席/中断の連続タイムライン」になり労務監視的な二次利用に転用されうるため。
    /// ★ したがって本行が無いことは「micro 沈黙が無かった」を意味しない。
    StarveWindow {
        t: u64,
        win_ms: u64,
        n_lt30: u64,
        sum_lt30_ms: u64,
    },
    /// Phase 1 Ground Truth ユーザーラベル。
    /// `recovered_at` はログ記録時は常に null、`gse-replay --metrics` で後付け算出。
    UserLabel {
        t: u64,
        label: UserLabelKindDto,
        recovered_at: Option<u64>,
    },
    /// 事後レビュー用ブックマークマーカー。認知状態ラベルではなく、
    /// 「ここを後で見返したい」という意図のみを記録する。
    ReviewMarker { t: u64 },
    /// IME 変換セッションの影ログ (Phase 2b, 両 OS)。
    /// `dwell_ms` は IME 変換セッションの長さ (ローマ字入力の開始から確定まで)、
    /// `nav` は変換中の矢印キー押下回数、`abandon` は ESC による変換放棄。
    /// 2026-08-23 訂正: 旧文は「IME 候補ウィンドウ表示〜非表示の時間」としていたが、
    /// 実測でこの区間は候補リスト表示だけでなく変換セッション全体を覆うと分かった。
    /// 2026-09-11 訂正 (issue 008): 旧文の「Windows のみ」は失効した。macOS 側に送出元を
    /// 実装したため両 OS で出る。ただし `dwell_ms` の由来が OS で異なる —— Windows は
    /// 窓イベント (EVENT_OBJECT_IME_* / DWM cloak) の観測値、macOS は打鍵の状態機械
    /// (input/ime_compose.rs) による推定値である。`nav` / `abandon` は両 OS とも打鍵由来。
    /// 由来は meta 行の os と capabilities 宣言で判別する。両 OS のデータを混ぜて
    /// 学習・評価してはならない。20 秒を超えた変換は打ち切られ行が出ない (両 OS 共通)。
    /// 由来だけでなく母数も違う: 1 行になる変換は Windows が「候補ウィンドウが出たもの」、
    /// macOS は「かな入力の一区切りすべて (Space 不要)」。nav を数える区間は Windows が
    /// IME_ACTIVE 中、macOS は変換セッション全体。abandon には macOS のみ「候補を出さずに
    /// 未確定文字列を捨てた ESC」が入る。abandon 率を OS 間で直接比べてはならない。
    /// dwell_ms は壁時計由来なので、時計の巻き戻しで 0 になった行を実測値として扱わないこと。
    /// macOS の dwell_ms は 1 変換分とは限らない: マウスでの候補確定・候補表示中の数字キー
    /// 確定は打鍵として終端を観測できないため、その変換は次の変換と合算されて 1 行になる
    /// (欠測ではない)。20 秒を超えたセッションは打ち切られ行が出ない (両 OS 共通)。
    ImeShadow {
        t: u64,
        dwell_ms: u64,
        nav: u32,
        abandon: bool,
    },
    /// MVP Opportunity 判定ログ。
    /// Need/Opportunity と抑制理由を後から検証するための固定カテゴリ記録。
    InterventionDecision {
        t: u64,
        action: InterventionActionDto,
        need_score: f64,
        opportunity_score: f64,
        p_stuck: f64,
        idle_ms: u64,
        reason: String,
        suppressed_by: Vec<String>,
    },
    /// 介入提示に対するユーザー応答 (reason)。`intervention_decision` (判定側) とは別の
    /// 「ユーザー応答側」ログ (WBS 0.8 / v0.4 §9)。Nudge dismiss は Need/Opportunity 誤りを分離、
    /// 固定カテゴリ + 時刻のみ。本文は含まない。
    /// ⚠️★★★ **`elapsed_ms` を書く経路は Wall だけだった** (2026-08-23 に Wall 削除)。
    /// ★ additive なフィールドなので schema には残すが、**現状 production では常に `null`** である。
    InterventionResponse {
        t: u64,
        action: InterventionActionDto,
        reason: DismissReasonDto,
        #[serde(skip_serializing_if = "Option::is_none")]
        elapsed_ms: Option<u64>,
    },
    /// v0.3 較正スモーク: セッション開始宣言 (track / task_kind / Monk・介入トグル)。
    /// timestamp は既存の `t` と別命名の `ts` (§14 設計準拠)。
    /// `condition` = 実験条件 (WBS 0.11)、`label_pool` = ラベルプール (WBS 0.4)。
    /// 旧フィクスチャ互換のため両者とも省略可 (`null`)。
    SessionMeta {
        track: TrackDto,
        task_kind: TaskKindDto,
        intervention_enabled: bool,
        condition: Option<ConditionDto>,
        label_pool: Option<LabelPoolDto>,
        /// ADR-006 Phase 2b: どの domain head がこのセッションを採点したか。
        ///
        /// ⚠️ **read-optional / write-required**: 現行の logger は**常に出力する**
        /// (`LogEntry::SessionMeta.head_id` は `Option` ではなく `HeadId` 型なので、
        /// 出力側の必須性は型で守られている)。`Option` なのは
        /// **ADR-006 Phase 2b 以前に収集した旧ログを読むため**だけである。
        ///
        /// ⚠️★ **下流での `null` の解釈は `meta` 行の `hmm_version` で判別すること**:
        /// - `hmm_version < 0.4.0` かつ `head_id == null` → **旧ログ。Writing head 相当**
        /// - `hmm_version >= 0.4.0` かつ `head_id == null` → ⚠️ **バグ。Writing 相当に丸めない**
        ///
        /// 「`null` は常に Writing 相当」と一律に解釈すると、将来の欠測やバグ由来の `null` まで
        /// 同じ意味に潰れる (cross-review Codex 指摘・2026-08-18)。
        head_id: Option<HeadIdDto>,
        ts: u64,
    },
    /// v0.3 較正スモーク: ランダムプローブ割当の監査記録。
    /// `probe_id` は backend 生成の不透明 ID (本文非由来)。
    ProbeAssignment {
        probe_id: String,
        scheduled_ts: u64,
        session_elapsed_ms: u64,
        /// このプローブが**なぜ発火したか** (ADR-031 D2)。
        ///
        /// ⚠️★★★ **`Option` にしない。** `random` を含む 3 値を常に書くので、
        /// **キーの不在がそのまま「本フィールドを持たない古いビルド」を意味する**
        /// (⚠️ `capabilities` は行種粒度でしか宣言できず、フィールドの有無を宣言しない。
        /// → `meta` 行の `app_version` と併せて判定する)。
        ///
        /// ⚠️★★★ **推定器の出力 (`p_stuck` / HMM 状態) で層化してはならない** ——
        /// 監査 criterion が主 criterion に依存し、criterion の二重化が意味を失う。
        ///
        /// ⚠️★★★ **DTO 側だけ `Option` である** (2026-09-14・code-reviewer HIGH)。
        /// 旧ログ (本フィールドを持たない `probe_assignment` 行) を `required` で弾くと
        /// **ADR-005 の additive versioning が成立しない** —— 実測で `gse-dataset` 側の
        /// 既存ファイルが `validate_schema.py` で落ちた。
        /// 書き手 (`logger::LogEntry::ProbeAssignment.stratum`) は **非 `Option` のまま**で、
        /// ADR-031 D4 の「3 値を常に書く / キーの不在 = 古いビルド」は writer 側で保たれる。
        #[serde(skip_serializing_if = "Option::is_none")]
        stratum: Option<ProbeStratumDto>,
        /// 段 1 の研究者の画面の確かめ用のカード（M5 の 3 本目の判断 3）。本物の行には無く、確かめの行だけ `true`。
        #[serde(skip_serializing_if = "Option::is_none")]
        debug: Option<bool>,
    },
    /// v0.3 較正スモーク: 主データ (リアルタイム/自己マーカー回答)。
    ///
    /// **不変条件 (schema では緩く、producer 側で強制)**:
    /// - skip (`answered=false`) ⇒ `q1_friction`/`q2_progress` は null
    /// - `q1_friction`/`q2_progress` があれば 1..=5。`q2_progress` は `q1_friction` が無ければ null
    /// - 較正と自己マーカーの `answered=true` ⇒ `q1_friction`/`q2_progress` は 1..=5
    /// - 段 1（3 名の版・ADR-057）の `answered=true` は、答えた分だけ q が入り残りは null
    ///   （Q3 の選択肢によって Q1・Q2 を聞かない、または答える前に閉じた。対の `activity_label` で分かる）
    /// - `source=self_marker` ⇒ `probe_id` は null
    ///
    /// `logger.rs` の `LogEntry::realtime_label_answered` / `..._s1_answered` / `..._skipped`
    /// コンストラクタがこれらを保証する。schemars は Option を緩く出すため validator 側で補検証する。
    RealtimeLabel {
        probe_id: Option<String>,
        source: ProbeSourceDto,
        q1_friction: Option<u8>,
        q2_progress: Option<u8>,
        answered: bool,
        skip_reason: SkipReasonDto,
        latency_ms: u64,
        analysis_window_start_ms: u64,
        analysis_window_end_ms: u64,
        ts: u64,
        /// 段 1 の研究者の画面の確かめ用のカード（M5 の 3 本目の判断 3）。本物の行には無く、確かめの行だけ `true`。
        #[serde(skip_serializing_if = "Option::is_none")]
        debug: Option<bool>,
    },
    /// v0.3 較正スモーク: 尺度理解テスト回答 (ビネット)。常に回答あり (q1/q2 は 1..=5)。
    /// `expected_quadrant` は教示の正解ラベル (`UserLabelKindDto` とは別物で `idle` を含む)。
    VignetteResponse {
        vignette_id: String,
        expected_quadrant: ExpectedQuadrantDto,
        q1_friction: u8,
        q2_progress: u8,
        /// 場面の表示から**記録に成功するまで**の所要時間 (ms)。読まずに送った回答の事後分離用。
        /// 送信に失敗して再送した場合は、初回表示からの累積になる。
        elapsed_ms: u64,
        /// Q1/Q2 スライダー合計の値変更回数。即答と熟慮を分ける。
        changes: u16,
        ts: u64,
    },
    /// O1 の**監査 criterion** (ADR-031 D1): 「直前は何をしていたか」の自己申告。
    ///
    /// **主データ (`realtime_label`) とは別の行種である。**
    /// 前者は 1..5 の Likert 2 問で、本行は固定 6 択の行動カテゴリを 1 つ持つ。
    /// 別の行種にしてあるのは、`capabilities` が**行種粒度でしか能力を宣言しない**ためで、
    /// `realtime_label` のフィールドとして足すと「計器が無かった (古いビルド)」と
    /// 「被験者が答えなかった」を機械的に分離できなくなる (ADR-013 D1 / ADR-031 D4)。
    ///
    /// **content-free の保証 (ADR-031 D3)**: 自由記述・相手の識別子・アプリ名・URL・
    /// 理由のいずれも持たない。持つのは時刻と 6 択のどれかだけである。
    ///
    /// **時刻キーは `t` である** (ADR-031 D6)。`redaction::line_timestamp` が
    /// 区間指定削除でこの行を拾えるようにするためで、`ts` にすると**消えない行**になる。
    ActivityLabel {
        probe_id: Option<String>,
        category: ActivityCategoryDto,
        answered: bool,
        latency_ms: u64,
        /// この回答が**指している区間**の開始 (ms)。
        ///
        /// ⚠️★★★ **区間指定削除がこの行を拾うために要る** (ADR-031 D6・2026-09-14 追加)。
        /// `t` は**回答した時刻**であって、被験者が思い出している時間帯ではない。
        /// → `t` だけで削除判定すると、「14:20-14:45 に会話していた」という申告を
        /// 14:46 に記録した行が、**14:20-14:45 を削除しても端末に残る**
        /// (＝ 同意文書の「お答えもいっしょに消えます」が破れる)。
        recall_window_start_ms: u64,
        /// この回答が指している区間の終了 (ms)。[`Self::ActivityLabel::recall_window_start_ms`] 参照。
        recall_window_end_ms: u64,
        t: u64,
        /// 段 1 の研究者の画面の確かめ用のカード（M5 の 3 本目の判断 3）。本物の行には無く、確かめの行だけ `true`。
        #[serde(skip_serializing_if = "Option::is_none")]
        debug: Option<bool>,
    },
    /// EH3 のその日の条件（`meta.eh3_mode` があるときだけ出る）。
    ///
    /// その日を稼働日として数えた時点（その日に打鍵を初めて観測した時点）に 1 回出す。すでに数えた日に
    /// アプリが起動したときにも、起動の時点で 1 回出す。ある時刻の条件は、その時刻と同じ日（現地時刻の
    /// 4:00 区切り）の `eh3_day` 行で読む。`day` は 1 始まりの稼働日の番号（1〜15）。期間の後の日には出さない。
    ///
    /// 記録しないもの（`.steering/20261011-portrait-eh3-prereg/implementation-requirements.md` R-L1・R-P9）:
    /// 壁紙を書き込んだ時刻・復元の成否・「戻せない背景なので動かさない」。本人が肖像を止める・戻す・
    /// 自分で替えると、その後の書き込みが無くなり、時刻の列から本人の操作が読めてしまうため（台帳 肖13）。
    ///
    /// 時刻キーは `t`（区間指定削除の対象に入る・ADR-031 D6）。
    Eh3Day {
        t: u64,
        day: u32,
        condition: Eh3ConditionDto,
    },
    /// EH3 の招待を出した時刻（理由を載せない）。`meta.eh3_mode` があるときだけ出る。
    ///
    /// 解除の時刻は記録しない（即時の解除から「本人が止めた」が読めるため）。時間切れの解除は、提示の時刻と
    /// 閉じるまでの時間（定数）から決まる。本人が招待を止めた後に提示が出なくなることは、この行の列から
    /// 避けがたく読めるので、ADR-035 D4 の条件（系の負担の兆候としてだけ・オフライン・本人に返さない）の
    /// 中で扱い、同意文書に書く。
    ///
    /// 時刻キーは `t`。
    InvitationPresent { t: u64 },
    /// 通常のモードで招待を許すセッションの条件（契機の種類と値・推定器の版）。
    ///
    /// `session_meta` とは別の行。招待を許すセッションの開始時（条件が決まった時点）に 1 行出す。EH3 は出さない
    /// （EH3 の条件は `eh3_day`）。`condition` ごとに持つ欄が決まっている: `estimator` は `p_stuck`・`hold_ms`、
    /// `rising` は `delta`・`window_ms`、`random` は `per_active_hour`・`seed`・`seed_effective`、`none` は持たない。
    /// 1 つのファイルに複数行ありうる（セッションの宣言が再び呼ばれたとき。後の行がその時点からの条件）。
    /// 立ったが出さなかった契機は記録しない。提示は `invitation_present` で読む。
    ///
    /// 時刻キーは `t`。
    InvitationCondition {
        t: u64,
        condition: InvitationConditionDto,
        hmm_version: String,
        #[serde(skip_serializing_if = "Option::is_none")]
        p_stuck: Option<f64>,
        #[serde(skip_serializing_if = "Option::is_none")]
        hold_ms: Option<u64>,
        #[serde(skip_serializing_if = "Option::is_none")]
        delta: Option<f64>,
        #[serde(skip_serializing_if = "Option::is_none")]
        window_ms: Option<u64>,
        #[serde(skip_serializing_if = "Option::is_none")]
        per_active_hour: Option<f64>,
        /// 設定の seed(2^53 - 1 以下)。
        #[serde(skip_serializing_if = "Option::is_none")]
        seed: Option<u64>,
        /// セッションの開始時刻(`session_start` 行の `t`)と設定の seed から導いた実効 seed(u64 を 10 進の文字列で)。
        #[serde(skip_serializing_if = "Option::is_none")]
        seed_effective: Option<String>,
    },
    /// 段 1 の問いの枠（seed・起点・調停器の版と定数）。`meta.s1_mode` があるときだけ出る。
    ///
    /// 記録のファイルを開いたとき（と、同意の印ができたとき）に 1 行出す。無作為の候補の時刻の列は
    /// `frame_seed` と `anchor_ms` だけで決まり、記録から再現できる。系の設定だけで、行動も申告も持たない。
    /// ★ 区間指定削除で消さない（`meta`・`invitation_condition` と同じ側）。数値は探索用の仮の定数。
    ///
    /// 時刻キーは `t`。
    ProbeFrame {
        t: u64,
        /// 2^53 − 1 以下。
        frame_seed: u64,
        anchor_ms: u64,
        arbiter_version: String,
        lambda_per_ms: f64,
        gap_min_ms: u64,
        cap_window_ms: u64,
        cap_count: u64,
        max_gap_ms: u64,
        away_idle_ms: u64,
        warmup_ms: u64,
        strata_enabled: bool,
        strat_low_op_min_gap_ms: u64,
        strat_resume_min_gap_ms: u64,
        strat_guard_after_any_ms: u64,
        strat_cap_count: u64,
        strat_cap_window_ms: u64,
        strat_yield_before_random_ms: u64,
        no_ask_enabled: bool,
        no_ask_block_ms: u64,
        no_ask_fraction: f64,
        eod_window_start_min: u32,
        eod_window_end_min: u32,
        eod_idle_ms: u64,
        eod_yield_before_random_ms: u64,
    },
    /// 段 1 の問いの候補を出さなかった記録。`meta.s1_mode` があるときだけ出る。
    ///
    /// `t` は判定した時刻、`candidate_ts` は候補の時刻（無作為は枠の候補・層化は引き金の押下）。
    /// 区間指定削除では `candidate_ts` 〜 `t` の区間で消える。
    ProbeSuppressed {
        t: u64,
        candidate_ts: u64,
        stratum: ProbeStratumDto,
        reason: ProbeSuppressReasonDto,
    },
    /// 段 1 の日の終わりの問い（ADR-048 D3）。`meta.s1_mode` があるときだけ出る。カードが閉じた時刻に 1 行。
    ///
    /// `target_day` は現地の日の番号（4:00 区切り・1970-01-01 からの日数）。時差は書かない
    /// （現地の分も書かない。UTC の時刻と並べると時差が分の精度で出るため）。
    /// `motivation` は 1..5 の 1 項目（答えていなければ `null`）。自由記述・理由を持たない。
    /// 区間指定削除では `shown_ts` 〜 `t` の区間で消える。
    DayQuestion {
        t: u64,
        shown_ts: u64,
        /// 問いを出したとき現地の時刻が時間帯の中だったか（現地の分そのものは書かない・時差が出るため）。
        in_eod_window: bool,
        target_day: i64,
        trigger: DayQuestionTriggerDto,
        delayed: bool,
        answered: bool,
        closed_by: DayQuestionClosedByDto,
        items_version: String,
        motivation: Option<u8>,
        latency_ms: Option<u64>,
        duration_ms: Option<u64>,
        /// 段 1 の研究者の画面の確かめ用のカード（M5 の 3 本目の判断 3）。本物の行には無く、確かめの行だけ `true`。
        #[serde(skip_serializing_if = "Option::is_none")]
        debug: Option<bool>,
    },
    /// 段 1 の後期の手跡の、その日の累計の写し（ADR-051 D4）。`meta.s1_mode` があるときだけ出る。
    ///
    /// 書く時点は起動（門の判定の後）・日付の変わり目・終了・5 分ごと。**机上では日ごとに最後の行を採る**
    /// （`shown_ms` は再起動をまたいで累計なので、同じ日の行を足し合わせない）。
    /// 5 分ごとの行にも日の累計が載るので、隣り合う行の `shown_ms`・`visible_ms` の差から、その 5 分に出ていた量と、
    /// 帯が見えていなかった量（画面のロック・ユーザーの切り替え・主画面のスリープ）が読める。
    /// 記録の一時停止中は量を足さず、その間の切った／戻した・起点の時刻を残さない（再開の時刻で違いを 1 件ずつ足す）。
    /// `day` は現地の日の番号（4:00 区切り）。現地の分は書かない。
    /// 区間指定削除では、区間の中の行を消し、区間の外の行は残して削除区間に入る `toggles`・`input_toggles`・
    /// `stage_starts` の要素を消す（割付・SHA-256・種・出せなかった理由は日の属性で、消すと ITT の分母が欠ける）。
    /// あわせて、区間より後の同じ日の行と走行中の累計から、区間の直前と直後の行の差を引く（区間の端の行の間隔ぶんまで
    /// 多めに引くので、削除のあった日の量は小さく出る）。区間の中の量はどの行の差からも読めない。
    /// 打鍵の時刻・キー・風の値（速さ・不規則さ・位相）を持つ欄は無い。
    HandmarkDay {
        t: u64,
        day: i64,
        assigned: HandmarkAssignedDto,
        late_start_day: Option<i64>,
        first_shown_day: Option<i64>,
        /// その日に出ていた時間（ms）。
        shown_ms: u64,
        /// 帯（下の縁）が出ていて、覆われておらず、画面のロック・ユーザーの切り替え・主画面のスリープの最中でなかった時間（ms）。ロックしないスクリーンセーバーと Dock に隠れた分は差し引けない。背景の層は数えない（透明な部分が多く、覆われていても見えている扱いになりうるため）。記録が無いときは null。
        visible_ms: Option<u64>,
        /// その日にトレイの「ほかの窓をどける」を選んだ回数（どけただけ数え、戻したのは数えない）。押した時刻は持たない
        /// （回数は次の 5 分ごとの行に載る）。記録の一時停止中は数えない。区間指定削除では `shown_ms` と同じく、区間の
        /// 直前と直後の行の差を区間より後の同じ日の行と走行中の累計から引く。記録が無いときは null。古い行には無い。
        #[serde(default)]
        reveal_count: Option<u64>,
        /// 切った（`on: false`）／戻した（`on: true`）時刻。
        toggles: Vec<HandmarkToggleDto>,
        /// 入力ごとに切った／戻した（カーソル・クリック）。ポインタの値は持たない。区間指定削除では `toggles` と同じく区間に入る要素を消す。古い行には無い。
        #[serde(default)]
        input_toggles: Vec<HandmarkInputToggleDto>,
        /// 手跡を出し始めた時刻（再生で位相の起点に使う）。
        stage_starts: Vec<u64>,
        /// `toggles`・`input_toggles`・`stage_starts` のどれかが 1 日 64 個を超えた。
        overflow: bool,
        /// 割付の表のバイト列の SHA-256（64 桁の小文字の 16 進）。
        table_sha256: Option<String>,
        /// 描画の種（16 桁の 16 進の文字列。JSON の数の精度を避ける）。
        draw_seed: Option<String>,
        /// 出せなかった理由（出せたら `null`）。
        reason: Option<HandmarkReasonDto>,
    },
}

/// 手跡の切った／戻した。
#[derive(Serialize, JsonSchema)]
pub struct HandmarkToggleDto {
    pub t: u64,
    pub on: bool,
}

/// 手跡の入力ごとの切った／戻した。
#[derive(Serialize, JsonSchema)]
pub struct HandmarkInputToggleDto {
    pub t: u64,
    pub input: HandmarkPointerInputDto,
    pub on: bool,
}

/// 入力ごとの入れ切りの対象。
#[derive(Serialize, JsonSchema)]
#[serde(rename_all = "snake_case")]
pub enum HandmarkPointerInputDto {
    Cursor,
    Click,
}

/// 手跡のその日の割付。`unknown` は表が読めないなど。
#[derive(Serialize, JsonSchema)]
#[serde(rename_all = "snake_case")]
pub enum HandmarkAssignedDto {
    Before,
    LateFirst,
    On,
    Off,
    After,
    Unknown,
}

/// 手跡を出せなかった（出さなかった）理由。
#[derive(Serialize, JsonSchema)]
#[serde(rename_all = "snake_case")]
pub enum HandmarkReasonDto {
    TableMissing,
    TableBroken,
    ShaMissing,
    ShaMismatch,
    StateBroken,
    StateUnwritable,
    OffToday,
    AssignedOff,
    BeforeLate,
    AfterTable,
    WindowUnavailable,
    PathsUnavailable,
}

/// 段 1 の候補を出さなかった理由。
#[derive(Serialize, JsonSchema)]
#[serde(rename_all = "snake_case")]
pub enum ProbeSuppressReasonDto {
    Away,
    Warmup,
    Gap,
    Cap,
    Yielded,
    CardOpen,
    NoAsk,
}

/// 段 1 の日の終わりの問いの契機。
#[derive(Serialize, JsonSchema)]
#[serde(rename_all = "snake_case")]
pub enum DayQuestionTriggerDto {
    EveningIdle,
    Quit,
    PauseResume,
    Pickup,
}

/// 段 1 の日の終わりの問いのカードが閉じた理由。
#[derive(Serialize, JsonSchema)]
#[serde(rename_all = "snake_case")]
pub enum DayQuestionClosedByDto {
    Answer,
    Dismiss,
    DayEnd,
    Quit,
}

/// 招待の契機の種類。NDJSON 文字列は "estimator" / "rising" / "random" / "none"。
#[derive(Serialize, JsonSchema)]
pub enum InvitationConditionDto {
    #[serde(rename = "estimator")]
    Estimator,
    #[serde(rename = "rising")]
    Rising,
    #[serde(rename = "random")]
    Random,
    #[serde(rename = "none")]
    None,
}

/// EH3 のその日の条件。NDJSON 文字列は "blank" / "decor" / "a_none" / "a_seed"。
///
/// 空（元の壁紙）・D（日替わりの地模様）・A（その回の形）の終わりの扱いが none か seed か。
#[derive(Serialize, JsonSchema)]
pub enum Eh3ConditionDto {
    #[serde(rename = "blank")]
    Blank,
    #[serde(rename = "decor")]
    Decor,
    #[serde(rename = "a_none")]
    PortraitNone,
    #[serde(rename = "a_seed")]
    PortraitSeed,
}

/// EH3 の招待の契機の段。NDJSON 文字列は "main" / "proto"（`eh3::TriggerStage::as_str`）。
#[derive(Serialize, JsonSchema)]
pub enum InvitationTriggerDto {
    #[serde(rename = "main")]
    Main,
    #[serde(rename = "proto")]
    Proto,
}

/// ★ 収集仕様の自己記述 (ADR-013 D1)。`meta`(session_start) 行にのみ現れる。
///
/// ## ⚠️★★★ 2 群を分ける理由 (分けないと自己矛盾する)
///
/// 閾値ゲート付きの行種では **「0 行」は「信号が無かった」を意味しない**
/// (閾値未達と区別できない)。★ 単一の集合にすると、
/// **本 ADR が防ごうとした取り違えを判定表が再導入する** (code-reviewer HIGH)。
///
/// ⚠️ 列挙されるのは **行種名**であって `meta` 行のフィールド名ではない
/// (`"session_start"` は `{"type":"session_start"}` という*行種*を指し、
/// 同名の `meta.session_start` *フィールド*とは別物である)。
#[derive(Serialize, JsonSchema)]
pub struct CapabilitiesDto {
    /// このビルドが**無条件に**出せる行種。★ 0 行なら「信号が無かった」と言える。
    pub unconditional: Vec<String>,
    /// ⚠️ 閾値ゲート付きの行種。★ 0 行は「**判定不能**」であって信号皆無ではない。
    pub threshold_gated: Vec<String>,
    /// ⚠️★★★ **設定で丸ごと止まる**行種 (2026-08-19 追加・code-reviewer HIGH)。
    ///
    /// ★ 0 行は「**判定不能**」である。例: `probe_assignment` は **G1 実施中は常に 0 行**
    /// (`probes_disabled`)、`intervention_decision` は **盲検較正では常に 0 行**
    /// (`intervention_enabled = false`)。
    /// ⚠️ これらを `unconditional` に置くと「**測れて、無かった**」という**偽の結論**が
    /// 機械的に出る —— ★ 「計器が無い」より質が悪い (**測ったふりをする**)。
    ///
    /// ⚠️ **旧ログには本フィールドが無い**ので `Option` にしてある (additive・`required` に入れない)。
    #[serde(skip_serializing_if = "Option::is_none")]
    pub config_gated: Option<Vec<String>>,
}

/// Ground Truth ラベルの種別。NDJSON 文字列は "flow" / "incubation" / "stuck"。
#[derive(Serialize, JsonSchema)]
#[serde(rename_all = "snake_case")]
pub enum UserLabelKindDto {
    Flow,
    Incubation,
    Stuck,
}

/// 介入ポリシーの出力種別。
#[derive(Serialize, JsonSchema)]
#[serde(rename_all = "snake_case")]
pub enum InterventionActionDto {
    None,
    Nudge,
    Defer,
}

/// v0.3 較正スモークのセッション系列。`main` = 本系列、`exploratory` = 探索系列。
#[derive(Serialize, JsonSchema)]
#[serde(rename_all = "snake_case")]
pub enum TrackDto {
    Main,
    Exploratory,
}

/// v0.3 較正スモークの課題種別 (session_meta)。
///
/// `other` = O1 の「その他・細切れの作業」(ADR-037)。
// ⚠️ variant に doc コメントを付けると schemars が `enum` を `oneOf` に組み替える
//    (gse-dataset 側の schema の形が変わる) ので、説明は型の doc に置く。
#[derive(Serialize, JsonSchema)]
#[serde(rename_all = "snake_case")]
pub enum TaskKindDto {
    Argumentative,
    Correspondence,
    Creative,
    VibeCoding,
    Other,
}

/// ADR-006 Phase 2b: どの domain head がセッションを採点したか (session_meta)。
///
/// `task_kind` (被験者の宣言) と対にして残す。ルーティング表が変われば
/// 同じ `task_kind` でも別の head になるため、実際に走った推論器を記録する。
/// `writing_fallback` = Creative / Other を Writing head で採点している状態
/// (Creative は ADR-006 #3 からの意図的な逸脱、Other は ADR-037 D2)。
#[derive(Serialize, JsonSchema)]
#[serde(rename_all = "snake_case")]
pub enum HeadIdDto {
    Writing,
    WritingFallback,
    CodingV0,
}

/// `probe_assignment` の層化理由 (ADR-031 D2)。
///
/// `random` = 既存のランダム枠、`low_operation_end` = 低操作区間が終わった時点、
/// `resumption` = フォーカスが戻ったあとに打鍵が戻った時点。
///
/// ⚠️★★★ **いずれも「時計と操作の事実」だけで決まる。** 推定器の出力は 1 バイトも読まない。
#[derive(Serialize, JsonSchema)]
#[serde(rename_all = "snake_case")]
pub enum ProbeStratumDto {
    Random,
    LowOperationEnd,
    Resumption,
}

/// `activity_label` の行動カテゴリ (ADR-031 D3・ADR-055)。固定 7 択で、増やすには別 ADR が要る。
///
/// 語は `.idea/20260910-mhd-feature-work-behavior-literature-gap-survey.md:140` の
/// 「熟考・詰まり・外部資料・会話・離席・回答不能」に、ADR-055 が「作業」を足した。
/// 本人の段 1 の配布物（タグ v0.1.42）の記録は `working` を持たない。`working` の不在から版を推さない (ADR-055 D5)。
///
/// ⚠️ 同メモ `:236` は「外部参照 / 観測不能」という別語で同じ並びを書いているが、
/// そちらは**解析側の混同率のカテゴリ**であって被験者に出す選択肢ではない (ADR-031 Context-1)。
///
/// ⚠️★★★ `external_material` と `conversation` は、計器由来なら ADR-014 D4 が禁じている
/// 役割カテゴリ (`editor` / `terminal` / `browser`) と**意味的に等価**である。
/// 自己申告経由に限って許可されており、条件は `data-privacy` ルール 7 にある。
#[derive(Serialize, JsonSchema)]
#[serde(rename_all = "snake_case")]
pub enum ActivityCategoryDto {
    /// 熟考: 手は止まっていたが考えていた。
    Deliberating,
    /// 詰まり: 先に進めずにいた。
    Stuck,
    /// 外部資料: 本・書類・画面などを読んでいた。
    ExternalMaterial,
    /// 会話: 会話・通話・打ち合わせをしていた。
    Conversation,
    /// 離席: その場を離れていた。
    Away,
    /// 作業: 手を動かして作業を進めていた（入力・編集・単純作業を含む）。ADR-055。
    Working,
    /// 回答不能: 思い出せない・当てはまらない。
    CannotAnswer,
}

/// `realtime_label` の出所。`random_probe` = backend 割当、`self_marker` = 自発 hotkey。
#[derive(Serialize, JsonSchema)]
#[serde(rename_all = "snake_case")]
pub enum ProbeSourceDto {
    RandomProbe,
    SelfMarker,
}

/// `realtime_label` の skip 理由。`none` = 回答済み、`dont_remember` / `dismissed` = skip、
/// `superseded` = 段 1 で層化のカードが無作為の問いに差し替えられた（調停器だけが書く）。
#[derive(Serialize, JsonSchema)]
#[serde(rename_all = "snake_case")]
pub enum SkipReasonDto {
    None,
    DontRemember,
    Dismissed,
    Superseded,
}

/// `vignette_response` の想定象限。教示の正解ラベル (`idle` を含む)。
#[derive(Serialize, JsonSchema)]
#[serde(rename_all = "snake_case")]
pub enum ExpectedQuadrantDto {
    Flow,
    Stuck,
    Incubation,
    Idle,
}

/// `intervention_response` の理由 (reason)。
/// Nudge dismiss (WBS 0.8 / v0.4 §9): `not_stuck` = Need 誤り、`want_to_struggle` = Opportunity 誤り、
/// `just_close` = 単に閉じる、`silent` = 理由未選択 (フェードアウト)。
/// ⚠️★★★ Wall 応答 (`early_unlock` / `completed` / `idle_timeout`) は 2026-08-23 に削除した。
#[derive(Serialize, JsonSchema)]
#[serde(rename_all = "snake_case")]
pub enum DismissReasonDto {
    NotStuck,
    WantToStruggle,
    JustClose,
    Silent,
}

/// `session_meta` の実験条件 (WBS 0.11)。Phase 1b=`blind_calibration`、Phase 2 AB/BA=`a`/`b`、
/// Phase 3 MRT=`nudge`/`defer`、それ以外=`baseline`。
#[derive(Serialize, JsonSchema)]
#[serde(rename_all = "snake_case")]
pub enum ConditionDto {
    BlindCalibration,
    A,
    B,
    Nudge,
    Defer,
    Baseline,
}

/// `session_meta` のラベルプール (WBS 0.4)。X1 判定には `calibration_blind` のみ使用。
#[derive(Serialize, JsonSchema)]
#[serde(rename_all = "snake_case")]
pub enum LabelPoolDto {
    CalibrationBlind,
    PostIntervention,
}
