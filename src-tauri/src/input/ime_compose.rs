//! ⚠️★★★ **IME 変換セッションを「1 変換 = 1 行」へ畳む純粋な状態機械 (OS 非依存)。**
//!
//! # なぜ `hook_macos.rs` の中に書かないのか
//!
//! ⚠️ `hook_macos.rs` の `#[cfg(test)] mod tests` は **Windows では 1 行も走らない**
//! (あちらのテストモジュール冒頭が自分でそう書いている)。
//! → ★ 状態機械をあちらに書くと、**Windows の CI も開発機も一切検証しない**。
//! `docs/agent-shared.md` 逐語「**OS ごとに規則が違うロジックは両 OS に対のテストを置く**」に反する。
//!
//! → ★ `ime_cloak.rs` と**同じ形**にする: 判断だけを `#[cfg]` 無しのここへ置き、
//!   `hook_macos.rs` は Atomic を読み書きするだけの薄いドライバにする。
//!   ⚠️ Win32 / macOS API 呼び出しはここに 1 つも無い。
//!
//! # ⚠️★★★ これは「打鍵からの推論」であって、IME の内部状態ではない
//!
//! ★ macOS には**他プロセスの変換状態を観測する公開 API が無い**
//! (`.steering/20260821-workspace-behavior-triage/survey-input-channels.md §7`)。
//! ⚠️ ただし **Windows 側の `nav` / `abandon` も同じく打鍵推論**である
//! (`hook_windows.rs::classify_ime_nav_key` —— `0x1B`→放棄 / `0x25..0x28`→ナビ)。
//! → ★ 手法としては**同型**であり、macOS だけが特別に弱いわけではない。
//!
//! ⚠️ 違うのは `dwell_ms` の由来だけである:
//!
//! | | Windows | macOS |
//! |---|---|---|
//! | `dwell_ms` | 窓イベント (`EVENT_OBJECT_IME_*` / DWM cloak) | ★ **打鍵** (最初の英数字キー 〜 終端キー) |
//! | `nav` / `abandon` | 打鍵 | 打鍵 (同型) |
//!
//! → ⚠️ **解析時にこの差を知っている必要がある。** `capabilities` は両 OS とも
//!   `config_gated` (0 行は**判定不能**) に置いてあり、`unconditional` へは上げない。
//!
//! # ⚠️★★★ セッションの母数が Windows と違う (★ ここを読まずに混ぜると誤る)
//!
//! ★ Windows の 1 行は **候補ウィンドウが出た変換** に対応する
//! (`IME_ACTIVE` は cloak/uncloak か `EVENT_OBJECT_IME_*` で立つ)。
//! ⚠️ macOS の 1 行は **かな入力の一区切り全部**に対応する ——
//! ★ **Space を一度も押さず確定しただけの入力でも 1 行出る**。
//!
//! → ⚠️ **macOS の行集合は Windows の行集合より広い。**
//! ★ 連鎖して `nav` / `abandon` の母数も違う:
//!
//! | | Windows | macOS |
//! |---|---|---|
//! | 1 行になる変換 | 候補ウィンドウが出たもの | ★ かな入力の一区切り**すべて** |
//! | `nav` を数える区間 | `IME_ACTIVE` 中 | ★ 変換セッション全体 |
//! | `abandon` に入るもの | 候補表示中の ESC | ★ **候補を出さずに未確定文字列を捨てた ESC も入る** |
//!
//! ⚠️ **`abandon` 率を OS 間で直接比べてはならない。**
//! ★ macOS 純正の「ライブ変換」は Space を押さずに変換が進むので、
//! この差は環境によってさらに開く (`survey-input-channels.md:153`)。
//!
//! # ⚠️ 拾えないもの (★ 記録しないと「無かった」と誤読される)
//!
//! - **マウスで候補を確定した変換** —— 打鍵が無いので終端を観測できない。
//!   ★ 次の打鍵で「その他キー」として閉じるか、[`MAX_SESSION_MS`] で打ち切られる。
//! - **ANSI キーボードのセッション先頭** —— `IME_OPEN` が 100ms の TIS ポーリング由来なので、
//!   変換開始直後の数打鍵が `ime_open = false` として渡りうる (`ime_macos.rs` の Path B)。
//! - **20 秒を超えた変換** —— [`MAX_SESSION_MS`] で打ち切り、⚠️ **行を出さない**。
//! - **数字キーによる候補確定** —— 候補表示中の `1`〜`9` は実機ではその変換を確定するが、
//!   本状態機械は英数字として扱い**セッションを続ける**。
//!   ⚠️ → その `dwell_ms` は**複数の変換を覆う**。★ 旧実装と同値だが、
//!   `dwell_ms` が本 issue で初めて計測値になったので意味が変わった。
//! - ⚠️ **`now_ms` は壁時計 (`SystemTime`) 由来で単調ではない。**
//!   ★ 時計が巻き戻ると `saturating_sub` が 0 になり、**`dwell_ms == 0` の行**が黙って出る
//!   (打ち切りも効かなくなる)。⚠️ 解析側は `dwell_ms == 0` を実測値として扱わないこと。

use super::hook::VK_KANJI;

/// ⚠️★★★ **1 セッションの上限 (ms)。超えたら打ち切って行を出さない。**
///
/// ★ **`ime_cloak::MAX_SESSION_MS` の別名である** (写しではない)。
/// ⚠️ 写しの `const` を置くと、`ime_cloak.rs` が 2026-08-23 に踏んだ事故
/// (逐語「下の静的表明は**同じファイル内の 2 定数を比べていただけ**で、
/// `lib.rs` の実値を 1 バイトも参照していなかった」) をそのまま再演する。
/// → ★ **持ち主を 1 人にする**のが唯一の正解で、静的表明では代用できない。
///
/// ★ 同値にする理由: Windows の cloak セッションと macOS の変換セッションは
/// **同じ現象 (1 変換)** を測っており、片方だけ動かすと
/// ⚠️ **同じ変換が OS によって違う上限で切られる**。
///
/// # ⚠️ なぜ「打ち切ったら行を出さない」のか
///
/// ★ 上限そのものを `dwell_ms` として出すと、⚠️ **上限値が実測値のふりをする**。
/// `ime_cloak.rs` が同じ判断をしている (逐語「1 行失う方が、上限そのものを dwell と
/// 偽る 1 行より安全である」)。★ 0 行は `config_gated` により「判定不能」と読まれる。
pub const MAX_SESSION_MS: u64 = super::ime_cloak::MAX_SESSION_MS;

/// ⚠️★★★ **打鍵に Command / Control が伴っていたか。**
///
/// ★ **なぜ要るか** (2026-09-11・code-reviewer HIGH):
/// `Cmd+S` / `Cmd+A` / `Ctrl+Z` は VK としては**英字キー**である。
/// ⚠️ そのまま [`step`] の英数字アームへ落とすと、日本語入力モード中の保存操作が
/// **変換セッションを開始し、`dwell_ms` を `Cmd+S` の時刻から測り始める**。
/// ★ `Cmd+Esc` 系なら**存在しない放棄行**まで作れる。
///
/// ⚠️ 旧 `update_compose_state` も同じ穴を持っていたが、`IME_COMPOSING` を
/// **誰も読んでいなかったので無害だった**。★ 本 issue で初めて計測値になる。
///
/// # ⚠️ Shift は含めない
///
/// ★ `Shift+A` は**ただの大文字 A** であり、変換の素材である。
/// ⚠️ Option (Alt) も除く —— macOS では特殊文字入力に使われ、ショートカットとは限らない。
/// ★ `Ctrl+J` / `Ctrl+K` など IME の変換ショートカットは `Modified` に落ちるが、
///   **透過 (状態を変えない)** なので変換の途中として正しく扱われる。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Chord {
    /// 修飾なし (⚠️ Shift / Option は「修飾なし」に数える)。
    Plain,
    /// ⚠️ Command または Control を伴う = アプリのショートカット。**変換の状態を語らない**。
    Modified,
}

/// 1 回の変換セッションの要約 (= `ime_shadow` 行 1 行ぶん)。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct ComposeSummary {
    /// 最初の英数字キー 〜 終端キー までの時間 (ms)。
    pub dwell_ms: u64,
    /// セッション中の矢印キー押下回数。
    pub nav: u32,
    /// ⚠️ `true` = **ESC で放棄**された。`false` = 確定 (Enter / その他キー / モード離脱)。
    pub abandon: bool,
}

/// セッションの終わり方。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ComposeEnd {
    /// ★ `ime_shadow` を 1 行出す。
    Emit(ComposeSummary),
    /// ⚠️ [`MAX_SESSION_MS`] 超過で打ち切った。**行は出さない。**
    Truncated {
        /// 打ち切り時点の経過時間 (ms)。★ 診断用で、NDJSON には載らない。
        dwell_ms: u64,
    },
}

/// 変換セッションの状態。
///
/// ⚠️★★★ **`composing` フラグを持たない。** ★ 「変換セッション中か」は
/// `session_start_ms.is_some()` と**同値**である (不変条件 2)。
/// ⚠️ 2 つ持つと片方だけ更新する経路ができ、必ずどこかで食い違う。
///
/// # 不変条件
///
/// 1. `active == true` ⇒ `session_start_ms.is_some()`
///    (候補ウィンドウは変換セッションの内側でしか出ない)
/// 2. `session_start_ms.is_some()` ⇔ 旧 `IME_COMPOSING == true`
///
/// ⚠️★ **時刻に `0` を「無し」の番兵として使わない** —— `Option<u64>` で持つ。
/// ★ `ime_cloak.rs` が同じ罠で 2026-08-23 にテストを 5 本落としている。
/// ⚠️ Atomic (`AtomicU64`) との境界でだけ `0 = 無し` に畳む (`hook_macos.rs` のドライバ)。
#[derive(Debug, Clone, Copy, PartialEq, Eq, Default)]
pub struct ComposeState {
    /// セッション開始時刻 (epoch ms)。`None` = 変換セッション中でない。
    pub session_start_ms: Option<u64>,
    /// 候補ウィンドウ表示中 (= `IME_ACTIVE`)。
    pub active: bool,
    /// セッション中の矢印キー押下回数。
    pub nav: u32,
}

// ⚠️★★★ **`abandon` は状態に持たない。**
//   ★ ESC は**その場でセッションを閉じる**ので、「セッション中に ESC が押されたか」を
//     持ち越す必要が無い ([`step`] の `0x1B` 腕が直接 `finish(prev, true, ..)` を呼ぶ)。
//   ⚠️ 初版は持っていたが **1 度も読まれない死んだ状態**で、
//     Atomic へ写し戻す経路だけが残って回収待ちの要約を壊していた
//     (`hook.rs::IME_COMPOSE_NAV` の doc を参照)。

impl ComposeState {
    /// 変換セッション中か (= 旧 `IME_COMPOSING`)。
    pub fn is_composing(&self) -> bool {
        self.session_start_ms.is_some()
    }
}

/// [`step`] の結果。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct ComposeStep {
    /// 次の状態。★ ドライバはこれを Atomic へ書き戻す。
    pub next: ComposeState,
    /// セッションが終わったなら、その終わり方。
    pub end: Option<ComposeEnd>,
}

/// ★ キー押下 1 件を食わせて状態を進める。**純粋関数**。
///
/// - `prev`: 現在の状態 (ドライバが Atomic から読む)
/// - `vk`: Windows VK に写像済みのキーコード (`hook_macos.rs::macos_vk_to_vk`)
/// - `ime_open`: 日本語入力モードか (`IME_OPEN`)
/// - `chord`: ⚠️ Command / Control を伴うか ([`Chord`])
/// - `now_ms`: epoch ms
///
/// # ⚠️ 遷移表 (★ `ime_open == true` のとき)
///
/// | キー | 遷移 |
/// |---|---|
/// | 英数字 `0x30..=0x39` / `0x41..=0x5A` | `active` を下ろす (候補確定 → 次の変換へ)。セッション中でなければ**開始** |
/// | Space `0x20` | セッション中かつ `!active` なら `active` を立てる (候補表示) |
/// | Enter `0x0D` | **確定して終了** (`abandon = false`) |
/// | Escape `0x1B` | ⚠️ **放棄して終了** (`abandon = true`) |
/// | Backspace `0x08` | `active` を下ろす。⚠️ **セッションは続く** (インライン編集へ戻る) |
/// | 矢印 `0x25..=0x28` | `nav += 1` (セッション中のみ)。状態は変えない |
/// | IME モードキー (`>= 0xF0` / `VK_KANJI`) | 何もしない (別経路が `IME_OPEN` を動かす) |
/// | その他 | **確定して終了** (`abandon = false`)。★ IME の自動確定にあたる |
///
/// `ime_open == false` のときは、どのキーでも**確定して終了**する
/// (★ かな → 英数 の切替は未確定文字列を確定させる)。
///
/// ⚠️★★★ **`chord == Modified` の打鍵は完全に透過する** (状態を変えず、行も出さない)。
/// ★ アプリのショートカットは変換の状態について何も語らないからである ([`Chord`] の doc)。
///
/// ⚠️★★★ **上限超過は最優先で処理する。** 先に打ち切ってから、そのキーを
/// **まっさらな状態に対して**適用する (★ その打鍵が新しいセッションを開始できる)。
pub fn step(prev: ComposeState, vk: u32, ime_open: bool, chord: Chord, now_ms: u64) -> ComposeStep {
    // ── 1. 上限超過の打ち切り (最優先・自己修復) ──────────────────────────
    if let Some(start) = prev.session_start_ms {
        if now_ms.saturating_sub(start) >= MAX_SESSION_MS {
            let truncated = ComposeEnd::Truncated {
                dwell_ms: now_ms.saturating_sub(start),
            };
            // ★ まっさらな状態に対して、このキーをもう一度適用する。
            //   ⚠️ まっさらからは `End` が返らない (終了はセッション中にしか起きない) ので、
            //   ここで打ち切りの報告が上書きされることはない。
            // ⚠️ `debug_assert!` は置かない —— ここは CGEventTap コールバックの中であり、
            //   ★ `extern "C"` 越しの panic は abort になる (2026-09-11・review LOW)。
            //   ⚠️ まっさらな状態からは `finish` が必ず `None` を返す
            //   (`session_start_ms` が `None` なので) という不変条件で担保する。
            let restarted = apply(ComposeState::default(), vk, ime_open, chord, now_ms);
            return ComposeStep {
                next: restarted.next,
                end: Some(truncated),
            };
        }
    }

    // ── 2. 通常の遷移 ──────────────────────────────────────────────────
    apply(prev, vk, ime_open, chord, now_ms)
}

/// 上限判定を除いた素の遷移。⚠️ [`step`] からのみ呼ぶ。
fn apply(prev: ComposeState, vk: u32, ime_open: bool, chord: Chord, now_ms: u64) -> ComposeStep {
    // ⚠️★★★ **ショートカットは変換の状態を語らない。** 完全に透過する ([`Chord`] の doc)。
    //   ★ `!ime_open` の判定より**先**に置く —— `Cmd+Space` (入力ソース切替) のように
    //     モードを動かすショートカット自体でセッションを閉じないため。
    //     ⚠️ モードが実際に変わったなら、次の**修飾なし**打鍵が閉じる。
    if matches!(chord, Chord::Modified) {
        return ComposeStep {
            next: prev,
            end: None,
        };
    }

    // ★ 日本語入力モードを抜けている = 未確定文字列は確定している。
    if !ime_open {
        return finish(prev, false, now_ms);
    }

    match vk {
        // 英数字 — 変換の素材。★ セッションの開始点でもある。
        0x30..=0x39 | 0x41..=0x5A => {
            let mut next = prev;
            // 候補表示中に別の字を打った = その候補を確定して次の変換へ。
            // ⚠️ セッション**そのもの**は続く (Windows の `IME_CHANGE` に相当し、
            //   あちらでも `ime_shadow` は出ない)。
            next.active = false;
            if next.session_start_ms.is_none() {
                // ★ セッション開始 — カウンタをここで 0 に戻す
                //   (`hook_windows.rs` が `IME_SHOW` で同じことをしている)。
                next.session_start_ms = Some(now_ms);
                next.nav = 0;
            }
            ComposeStep { next, end: None }
        }
        // Space — 変換 (候補ウィンドウを出す)。★ 既に出ていれば次候補へ送るだけ。
        0x20 => {
            let mut next = prev;
            if prev.session_start_ms.is_some() && !prev.active {
                next.active = true;
            }
            ComposeStep { next, end: None }
        }
        // Enter — 確定。
        0x0D => finish(prev, false, now_ms),
        // Escape — ⚠️ 放棄。★ **この 1 行のためにこのモジュールがある。**
        0x1B => finish(prev, true, now_ms),
        // Backspace — 候補表示から抜けてインライン編集へ戻る。⚠️ セッションは続く。
        0x08 => {
            let mut next = prev;
            next.active = false;
            ComposeStep { next, end: None }
        }
        // 矢印 — 候補ナビゲーション。
        0x25..=0x28 => {
            let mut next = prev;
            if prev.session_start_ms.is_some() {
                next.nav = next.nav.saturating_add(1);
            }
            ComposeStep { next, end: None }
        }
        // IME モードキー — `IME_OPEN` は別経路が動かす。ここでは何もしない。
        _ if vk >= 0xF0 || vk == VK_KANJI => ComposeStep {
            next: prev,
            end: None,
        },
        // その他 (Tab / 記号 / ファンクションキー) — IME の自動確定にあたる。
        _ => finish(prev, false, now_ms),
    }
}

/// セッションを閉じる。⚠️ セッション中でなければ**何も起きない** (行は出ない)。
///
/// ★ `abandon` は「**この終端キーが ESC だったか**」であって、
/// セッション中のどこかで ESC が押されたかではない
/// (⚠️ ESC はその場でセッションを閉じるので、両者は一致する)。
fn finish(prev: ComposeState, abandon: bool, now_ms: u64) -> ComposeStep {
    let Some(start) = prev.session_start_ms else {
        // ★ 変換していないときの Enter / Escape / その他キーは、ただのキーである。
        // ⚠️ それでも**まっさらに揃えて返す** —— 旧 `update_compose_state` は
        //   `ime_open == false` の枝で `IME_ACTIVE` を毎回 `swap(false)` しており、
        //   ★ 外部 (lib.rs の safety valve など) が壊した不変条件 1 をここで拭っていた。
        //   その防御を落とさない。
        return ComposeStep {
            next: ComposeState::default(),
            end: None,
        };
    };
    ComposeStep {
        next: ComposeState::default(),
        end: Some(ComposeEnd::Emit(ComposeSummary {
            dwell_ms: now_ms.saturating_sub(start),
            nav: prev.nav,
            abandon,
        })),
    }
}

// ---------------------------------------------------------------------------
// Atomic ドライバ
// ---------------------------------------------------------------------------
//
// ⚠️★★★ **ここも `#[cfg]` を付けない。** production で呼ぶのは `hook_macos.rs` だけだが、
//   ★ macOS 限定にすると「確定 / 放棄を Atomic へ書き戻す層」が
//     **どちらの OS の CI でも 1 行も走らない**状態に戻ってしまう。
//   ⚠️ Windows 側の `ime_shadow` は WinEvent / cloak 経路が同じ Atomic を駆動しており、
//     この関数は production の Windows 経路からは**呼ばれない**。

use std::sync::atomic::Ordering;

use super::hook::{
    IME_ACTIVE, IME_CANDIDATE_NAV_COUNT, IME_COMPOSE_NAV, IME_COMPOSING, IME_COMPOSITION_START_MS,
    IME_SHADOW_ABANDON, IME_SHADOW_DWELL_MS, IME_SHADOW_READY,
};

/// ★ キー押下 1 件を [`step`] に食わせ、結果を Atomic へ書き戻す。
///
/// ⚠️★★★ **CGEventTap コールバックから呼ばれる。** `hook-constraints` mac-1 により
/// ここで許されるのは **Atomic 操作だけ**である (ログ・アロケーション・ロックは禁止)。
/// ★ 判断は [`step`] (純粋関数) が済ませてあるので、ここには分岐が無い。
///
/// # ⚠️★★★ 進行中の値と、回収待ちの要約は**別の置き場**に書く
///
/// | 何 | 置き場 | いつ書くか |
/// |---|---|---|
/// | 進行中のセッション | `IME_COMPOSITION_START_MS` / `IME_COMPOSING` / `IME_ACTIVE` / `IME_COMPOSE_NAV` | ★ 毎打鍵 |
/// | 回収待ちの要約 | `IME_SHADOW_DWELL_MS` / `IME_CANDIDATE_NAV_COUNT` / `IME_SHADOW_ABANDON` / `IME_SHADOW_READY` | ★ **セッション終了時だけ** |
///
/// ⚠️ 分けないと、**セッション開始時のリセットが回収待ちの要約を壊す** ——
/// ESC で放棄した直後 100ms 以内に次の変換を打ち始めると
/// **`abandon` が `true` から `false` に化ける**。
/// ★ 理由と再現手順は `hook.rs::IME_COMPOSE_NAV` の doc が正本。
///
/// ⚠️ 要約の書き込み順序には意味がある: 値 3 つ → **最後に `READY` を Release** で立てる。
/// この Release store が値 3 つを IME Monitor 側へ可視にする。
///
/// ⚠️ 100ms のポーリング間隔より速く **2 つの変換が終わった**場合に前の要約が
/// 置き換わる (= **1 行の欠落**) のは **Windows と同じ既知の挙動**である
/// (`hook.rs::IME_SHADOW_READY` の doc)。★ 値の偽装は起きない。
pub fn drive(vk: u32, ime_open: bool, chord: Chord, now_ms: u64) {
    let ComposeStep { next, end } = step(load(), vk, ime_open, chord, now_ms);

    // 1. 進行中のセッション。⚠️ ここでは shadow 側の Atomic を一切触らない。
    IME_COMPOSITION_START_MS.store(next.session_start_ms.unwrap_or(0), Ordering::Relaxed);
    IME_COMPOSE_NAV.store(next.nav, Ordering::Relaxed);
    IME_COMPOSING.store(next.is_composing(), Ordering::Release);
    IME_ACTIVE.store(next.active, Ordering::Release);

    // 2. 回収待ちの要約。⚠️ `Truncated` は行を出さない (上限を dwell と偽らないため)。
    if let Some(ComposeEnd::Emit(summary)) = end {
        IME_SHADOW_DWELL_MS.store(summary.dwell_ms, Ordering::Relaxed);
        IME_CANDIDATE_NAV_COUNT.store(summary.nav, Ordering::Relaxed);
        IME_SHADOW_ABANDON.store(summary.abandon, Ordering::Relaxed);
        // ⚠️ **必ず最後**。
        IME_SHADOW_READY.store(true, Ordering::Release);
    }
}

/// ⚠️★★★ **`IME_SHADOW_READY` を回収してよいか** (IME Monitor スレッドの判断)。
///
/// ★ 純関数にして `is_windows` を**注入**してあるのは、⚠️ **両 OS の CI で
/// 両方の分岐を検証するため**である (`#[cfg]` で書くと片側しか走らない)。
///
/// | OS | 条件 | なぜ |
/// |---|---|---|
/// | Windows | `!active && ready` | ★ `active → false` 遷移経路が先に emit するので、ここは取りこぼしの受け皿。⚠️ 挙動を変えない |
/// | macOS | `ready` **だけ** | ★ `READY` が立つ時点で `drive` が必ず `IME_ACTIVE=false` を書いている (`finish` が `ComposeState::default()` を返す) ので `!active` は**構造的に冗長**。⚠️ それでも見ると、ポーリングが読んだ `active` が次セッションの `Space` 後だった場合に emit を先送りし、その間に要約が上書きされて**行が消える** |
pub fn should_drain_ready(ready: bool, active: bool, is_windows: bool) -> bool {
    if !ready {
        return false;
    }
    if is_windows {
        !active
    } else {
        true
    }
}

/// Atomic 群から [`ComposeState`] を組み立てる。
///
/// ⚠️ `IME_COMPOSITION_START_MS` は **`0` = セッション無し**の番兵だが、
/// ★ 純粋層では `Option<u64>` で持つ ([`ComposeState`] の doc)。
/// 番兵と `Option` の変換は**この 1 か所だけ**で行う。
///
/// ⚠️ `nav` は **`IME_COMPOSE_NAV`** から読む (`IME_CANDIDATE_NAV_COUNT` ではない) ——
/// ★ 後者は「回収待ちの要約」であって進行中の値ではない。
/// ⚠️ セッション中でなければ `0` として読み、前セッションの値を持ち込ませない。
fn load() -> ComposeState {
    let composing = IME_COMPOSING.load(Ordering::Acquire);
    ComposeState {
        session_start_ms: composing.then(|| IME_COMPOSITION_START_MS.load(Ordering::Relaxed)),
        active: IME_ACTIVE.load(Ordering::Acquire),
        nav: if composing {
            IME_COMPOSE_NAV.load(Ordering::Relaxed)
        } else {
            0
        },
    }
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------
//
// ⚠️★★★ **これは両 OS で走る** (`input/mod.rs` が `ime_compose` に `#[cfg]` を付けていない)。
//   ★ 実機でしか確かめられないのは「CGEventTap がこのキーを届けるか」であって、
//     **確定と放棄を分ける判断そのものはここで固定できる**。

#[cfg(test)]
mod tests {
    use super::*;

    const ENTER: u32 = 0x0D;
    const ESC: u32 = 0x1B;
    const SPACE: u32 = 0x20;
    const BACKSPACE: u32 = 0x08;
    const LEFT: u32 = 0x25;
    const RIGHT: u32 = 0x27;
    const A: u32 = 0x41;
    const K: u32 = 0x4B;
    const TAB: u32 = 0x09;

    /// 打鍵列を順に食わせ、出た `ComposeEnd` を全部集める。
    fn run(keys: &[(u32, bool, u64)]) -> (ComposeState, Vec<ComposeEnd>) {
        let chorded: Vec<_> = keys
            .iter()
            .map(|&(vk, open, t)| (vk, open, Chord::Plain, t))
            .collect();
        run_chords(&chorded)
    }

    /// ★ 修飾キーを明示して打鍵列を流す。
    fn run_chords(keys: &[(u32, bool, Chord, u64)]) -> (ComposeState, Vec<ComposeEnd>) {
        let mut state = ComposeState::default();
        let mut ends = Vec::new();
        for &(vk, ime_open, chord, t) in keys {
            let s = step(state, vk, ime_open, chord, t);
            state = s.next;
            if let Some(e) = s.end {
                ends.push(e);
            }
        }
        (state, ends)
    }

    fn emitted(ends: &[ComposeEnd]) -> Vec<ComposeSummary> {
        ends.iter()
            .filter_map(|e| match e {
                ComposeEnd::Emit(s) => Some(*s),
                ComposeEnd::Truncated { .. } => None,
            })
            .collect()
    }

    // ── ★★★ 本 issue の核心: 確定と放棄が分かれること ──────────────────

    /// ★ Enter で終わった変換は `abandon = false`。
    #[test]
    fn enter_confirms_the_session() {
        let (_, ends) = run(&[(A, true, 100), (SPACE, true, 300), (ENTER, true, 900)]);
        assert_eq!(
            emitted(&ends),
            vec![ComposeSummary {
                dwell_ms: 800,
                nav: 0,
                abandon: false,
            }]
        );
    }

    /// ⚠️★★★ ESC で終わった変換は `abandon = true`。
    /// ★ **これが判別できないまま O1 を配ると、永久に復元できない。**
    #[test]
    fn escape_abandons_the_session() {
        let (_, ends) = run(&[(A, true, 100), (SPACE, true, 300), (ESC, true, 900)]);
        assert_eq!(
            emitted(&ends),
            vec![ComposeSummary {
                dwell_ms: 800,
                nav: 0,
                abandon: true,
            }]
        );
    }

    /// ★ 同じ打鍵長・同じ nav でも、終端キーだけで確定 / 放棄が分かれる。
    #[test]
    fn confirm_and_abandon_differ_only_by_the_terminating_key() {
        let (_, confirmed) = run(&[(A, true, 0), (SPACE, true, 100), (ENTER, true, 500)]);
        let (_, abandoned) = run(&[(A, true, 0), (SPACE, true, 100), (ESC, true, 500)]);
        let c = emitted(&confirmed);
        let a = emitted(&abandoned);
        assert_eq!(c[0].dwell_ms, a[0].dwell_ms);
        assert_eq!(c[0].nav, a[0].nav);
        assert_ne!(c[0].abandon, a[0].abandon);
    }

    // ── セッションの境界 ────────────────────────────────────────────────

    /// ★ セッションは「最初の英数字キー」から始まる (Space からではない)。
    #[test]
    fn dwell_starts_at_the_first_alphanumeric_key() {
        let (_, ends) = run(&[
            (A, true, 1_000),
            (K, true, 1_200),
            (SPACE, true, 1_500),
            (ENTER, true, 2_000),
        ]);
        assert_eq!(emitted(&ends)[0].dwell_ms, 1_000);
    }

    /// ⚠️ 候補表示中に別の字を打っても**セッションは切れない** (Windows の `IME_CHANGE` と同型)。
    #[test]
    fn typing_during_candidates_does_not_close_the_session() {
        let (state, ends) = run(&[
            (A, true, 0),
            (SPACE, true, 100),
            (K, true, 200), // 候補を確定して次の変換へ
            (SPACE, true, 300),
            (ENTER, true, 400),
        ]);
        assert_eq!(emitted(&ends).len(), 1, "1 変換 = 1 行でなければならない");
        assert_eq!(emitted(&ends)[0].dwell_ms, 400);
        assert!(!state.is_composing());
    }

    /// ⚠️ Backspace は候補表示から抜けるだけで、**セッションは続く**。
    #[test]
    fn backspace_leaves_candidates_but_keeps_the_session() {
        let (state, ends) = run(&[(A, true, 0), (SPACE, true, 100), (BACKSPACE, true, 200)]);
        assert!(ends.is_empty(), "Backspace で行が出てはならない");
        assert!(state.is_composing());
        assert!(!state.active);
    }

    /// ★ Tab / 記号などの「その他キー」は IME の自動確定にあたる → 確定で閉じる。
    #[test]
    fn other_keys_close_the_session_as_confirmed() {
        let (_, ends) = run(&[(A, true, 0), (TAB, true, 700)]);
        assert_eq!(
            emitted(&ends),
            vec![ComposeSummary {
                dwell_ms: 700,
                nav: 0,
                abandon: false,
            }]
        );
    }

    /// ★ かな → 英数 の切替 (= `ime_open` が false) も確定で閉じる。
    #[test]
    fn leaving_japanese_mode_closes_the_session_as_confirmed() {
        let (state, ends) = run(&[(A, true, 0), (A, false, 600)]);
        assert_eq!(emitted(&ends)[0].abandon, false);
        assert_eq!(emitted(&ends)[0].dwell_ms, 600);
        assert!(!state.is_composing());
    }

    /// ⚠️ 変換していないときの Enter / Escape は**ただのキー**である (行を出さない)。
    #[test]
    fn terminating_keys_outside_a_session_emit_nothing() {
        let (_, ends) = run(&[(ENTER, true, 10), (ESC, true, 20), (TAB, true, 30)]);
        assert!(ends.is_empty());
    }

    /// ⚠️ IME が閉じている間は 1 行も出ない (英数入力で `ime_shadow` が湧かない)。
    #[test]
    fn nothing_is_emitted_while_ime_is_closed() {
        let (state, ends) = run(&[(A, false, 0), (K, false, 100), (ENTER, false, 200)]);
        assert!(ends.is_empty());
        assert!(!state.is_composing());
    }

    // ── nav ────────────────────────────────────────────────────────────

    /// ★ 矢印キーはセッション中だけ数える。
    #[test]
    fn arrows_are_counted_within_the_session() {
        let (_, ends) = run(&[
            (LEFT, true, 0), // ⚠️ セッション前 — 数えない
            (A, true, 100),
            (SPACE, true, 200),
            (RIGHT, true, 300),
            (RIGHT, true, 400),
            (LEFT, true, 500),
            (ENTER, true, 600),
        ]);
        assert_eq!(emitted(&ends)[0].nav, 3);
    }

    /// ★ `nav` は次のセッションへ持ち越さない (セッション開始で 0 に戻す)。
    #[test]
    fn nav_does_not_leak_into_the_next_session() {
        let (_, ends) = run(&[
            (A, true, 0),
            (RIGHT, true, 100),
            (ENTER, true, 200),
            (A, true, 300),
            (ENTER, true, 400),
        ]);
        let rows = emitted(&ends);
        assert_eq!(rows.len(), 2);
        assert_eq!(rows[0].nav, 1);
        assert_eq!(rows[1].nav, 0, "前セッションの nav が漏れている");
    }

    /// ⚠️ `abandon` も次のセッションへ持ち越さない。
    #[test]
    fn abandon_does_not_leak_into_the_next_session() {
        let (_, ends) = run(&[
            (A, true, 0),
            (ESC, true, 100),
            (A, true, 200),
            (ENTER, true, 300),
        ]);
        let rows = emitted(&ends);
        assert_eq!(rows.len(), 2);
        assert!(rows[0].abandon);
        assert!(!rows[1].abandon, "前セッションの abandon が漏れている");
    }

    // ── ⚠️★★★ 修飾キー (Command / Control) ────────────────────────────

    /// ⚠️★★★ **`Cmd+S` が変換セッションを開始してはならない。**
    ///
    /// ★ `Cmd+S` の VK は `0x53` (= `S`) なので、修飾を見ないと英数字アームに落ちて
    ///   セッションが始まり、⚠️ **その後の実変換の `dwell_ms` が保存操作の時刻から測られる**。
    #[test]
    fn a_command_chord_does_not_open_a_session() {
        let (state, ends) = run_chords(&[
            (0x53, true, Chord::Modified, 0),   // Cmd+S
            (0x41, true, Chord::Modified, 100), // Cmd+A
        ]);
        assert!(
            !state.is_composing(),
            "ショートカットでセッションが始まっている"
        );
        assert!(ends.is_empty());
    }

    /// ⚠️★★★ **`Cmd+Esc` 系が存在しない放棄行を作ってはならない。**
    #[test]
    fn a_command_chord_does_not_forge_an_abandon_row() {
        let (state, ends) = run_chords(&[
            (A, true, Chord::Plain, 0),
            (ESC, true, Chord::Modified, 300), // ⚠️ ショートカットであって放棄ではない
        ]);
        assert!(ends.is_empty(), "修飾付き ESC で放棄行が出た");
        assert!(state.is_composing(), "セッションが不当に閉じられた");
    }

    /// ★ 変換中の `Cmd+S` (保存) はセッションを**素通り**し、dwell を汚さない。
    #[test]
    fn a_command_chord_mid_session_is_transparent() {
        let (_, ends) = run_chords(&[
            (A, true, Chord::Plain, 1_000),
            (0x53, true, Chord::Modified, 1_200), // Cmd+S
            (SPACE, true, Chord::Plain, 1_400),
            (ENTER, true, Chord::Plain, 1_800),
        ]);
        assert_eq!(
            emitted(&ends),
            vec![ComposeSummary {
                dwell_ms: 800,
                nav: 0,
                abandon: false,
            }],
            "修飾付き打鍵が dwell を汚している"
        );
    }

    /// ⚠️ `Ctrl+J` / `Ctrl+K` (IME の変換ショートカット) もセッションを壊さない。
    #[test]
    fn ime_conversion_chords_keep_the_session_alive() {
        let (state, ends) = run_chords(&[
            (A, true, Chord::Plain, 0),
            (0x4A, true, Chord::Modified, 100), // Ctrl+J (ひらがな変換)
            (0x4B, true, Chord::Modified, 200), // Ctrl+K (カタカナ変換)
        ]);
        assert!(ends.is_empty());
        assert!(state.is_composing());
    }

    /// ★ 修飾付き打鍵でも**上限の打ち切りは効く** (時間による自己修復を止めない)。
    #[test]
    fn truncation_still_fires_on_a_modified_key() {
        let (_, ends) = run_chords(&[
            (A, true, Chord::Plain, 0),
            (0x53, true, Chord::Modified, MAX_SESSION_MS + 1),
        ]);
        assert!(matches!(ends[0], ComposeEnd::Truncated { .. }));
    }

    // ── 上限 ────────────────────────────────────────────────────────────

    /// ⚠️★★★ 上限を超えた変換は**打ち切り、行を出さない** (上限を dwell と偽らない)。
    #[test]
    fn over_long_sessions_are_truncated_without_a_row() {
        let (_, ends) = run(&[(A, true, 0), (ENTER, true, MAX_SESSION_MS)]);
        assert_eq!(
            ends,
            vec![ComposeEnd::Truncated {
                dwell_ms: MAX_SESSION_MS
            }]
        );
        assert!(emitted(&ends).is_empty(), "打ち切りで行を出してはならない");
    }

    /// ★ 上限の 1ms 手前はちゃんと行になる (境界を内側へずらさない)。
    #[test]
    fn just_under_the_cap_still_emits() {
        let (_, ends) = run(&[(A, true, 0), (ENTER, true, MAX_SESSION_MS - 1)]);
        assert_eq!(emitted(&ends)[0].dwell_ms, MAX_SESSION_MS - 1);
    }

    /// ★ 打ち切った直後の英数字キーは、**新しいセッションを開始する**。
    /// ⚠️ ここを落とすと、放置後の 1 変換が丸ごと消える。
    #[test]
    fn a_key_after_truncation_starts_a_fresh_session() {
        let (state, ends) = run(&[
            (A, true, 0),
            (K, true, MAX_SESSION_MS + 5), // 打ち切り → 同じ打鍵で再開
            (ENTER, true, MAX_SESSION_MS + 205),
        ]);
        assert!(matches!(ends[0], ComposeEnd::Truncated { .. }));
        assert_eq!(
            emitted(&ends),
            vec![ComposeSummary {
                dwell_ms: 200,
                nav: 0,
                abandon: false,
            }]
        );
        assert!(!state.is_composing());
    }

    // ── 不変条件 ────────────────────────────────────────────────────────

    /// ⚠️ 不変条件 1: `active` はセッションの外では立たない。
    #[test]
    fn active_never_outlives_the_session() {
        let mut state = ComposeState::default();
        for &(vk, open, t) in &[
            (SPACE, true, 0),
            (A, true, 10),
            (SPACE, true, 20),
            (ESC, true, 30),
            (SPACE, true, 40),
        ] {
            state = step(state, vk, open, Chord::Plain, t).next;
            assert!(
                !state.active || state.is_composing(),
                "active なのにセッションが無い (不変条件 1 違反)"
            );
        }
    }

    /// ⚠️ 不変条件 1 が外部要因で壊れていても、終端キーで**拭って直す**。
    /// ★ 旧 `update_compose_state` の `ime_open == false` 枝 (毎回 `IME_ACTIVE.swap(false)`)
    ///   が担っていた防御を落とさないためのテスト。
    #[test]
    fn a_terminating_key_repairs_a_broken_invariant() {
        // ⚠️ セッションが無いのに active だけ立っている壊れた状態。
        let broken = ComposeState {
            session_start_ms: None,
            active: true,
            nav: 7,
        };
        for &vk in &[ENTER, ESC, TAB] {
            let s = step(broken, vk, true, Chord::Plain, 100);
            assert_eq!(
                s.next,
                ComposeState::default(),
                "vk=0x{vk:02X} で拭えていない"
            );
            assert!(s.end.is_none(), "セッションが無いのに行を出してはならない");
        }
        // ★ IME モードから抜ける枝でも同じ。
        let s = step(broken, A, false, Chord::Plain, 100);
        assert_eq!(s.next, ComposeState::default());
        assert!(s.end.is_none());
    }

    /// ★ Space だけではセッションは始まらない (変換する素材が無い)。
    #[test]
    fn space_alone_does_not_open_a_session() {
        let (state, ends) = run(&[(SPACE, true, 0), (SPACE, true, 100)]);
        assert!(!state.is_composing());
        assert!(!state.active);
        assert!(ends.is_empty());
    }

    /// ★ 候補表示中の Space は次候補送り —— `active` のままで行は出ない。
    #[test]
    fn space_during_candidates_stays_active() {
        let (state, ends) = run(&[(A, true, 0), (SPACE, true, 100), (SPACE, true, 200)]);
        assert!(state.active);
        assert!(state.is_composing());
        assert!(ends.is_empty());
    }

    /// ★ IME モードキーはセッションを壊さない (`IME_OPEN` は別経路が動かす)。
    #[test]
    fn ime_mode_keys_are_transparent() {
        let (state, ends) = run(&[(A, true, 0), (VK_KANJI, true, 100), (0xF2, true, 150)]);
        assert!(ends.is_empty());
        assert!(state.is_composing());
    }
}

// ---------------------------------------------------------------------------
// ドライバのテスト (Atomic 層)
// ---------------------------------------------------------------------------
//
// ⚠️★★★ **これも両 OS で走る。** ★ `hook_macos.rs` に置いていたら Windows では
//   1 行も検証されなかった層である。
//
// ⚠️ グローバル Atomic を触るので、**テスト同士が並列に走ると壊れる**。
//   → ★ `DRIVER_LOCK` で直列化し、各テストの入口で初期状態へ戻す。

#[cfg(test)]
mod driver_tests {
    use super::*;
    use std::sync::{Mutex, MutexGuard};

    static DRIVER_LOCK: Mutex<()> = Mutex::new(());

    const ENTER: u32 = 0x0D;
    const ESC: u32 = 0x1B;
    const SPACE: u32 = 0x20;
    const RIGHT: u32 = 0x27;
    const A: u32 = 0x41;
    const K: u32 = 0x4B;

    /// ⚠️ グローバル Atomic をテスト用に掴み、初期状態へ戻す。
    /// ★ `MutexGuard` を返すので、テストが終わるまで他のテストは待つ。
    fn acquire() -> MutexGuard<'static, ()> {
        // ⚠️ 毒された Mutex でもテストは続ける (前のテストの panic で全部落とさない)。
        let guard = DRIVER_LOCK.lock().unwrap_or_else(|e| e.into_inner());
        IME_COMPOSITION_START_MS.store(0, Ordering::Relaxed);
        IME_COMPOSING.store(false, Ordering::Release);
        IME_ACTIVE.store(false, Ordering::Release);
        IME_COMPOSE_NAV.store(0, Ordering::Relaxed);
        IME_CANDIDATE_NAV_COUNT.store(0, Ordering::Relaxed);
        IME_SHADOW_ABANDON.store(false, Ordering::Relaxed);
        IME_SHADOW_READY.store(false, Ordering::Release);
        guard
    }

    /// IME Monitor がやっていることと同じ回収 (`lib.rs::emit_ime_shadow` の正常経路)。
    fn collect_row() -> Option<ComposeSummary> {
        if !IME_SHADOW_READY.swap(false, Ordering::AcqRel) {
            return None;
        }
        Some(ComposeSummary {
            dwell_ms: IME_SHADOW_DWELL_MS.swap(0, Ordering::Relaxed),
            nav: IME_CANDIDATE_NAV_COUNT.swap(0, Ordering::Relaxed),
            abandon: IME_SHADOW_ABANDON.swap(false, Ordering::Relaxed),
        })
    }

    /// ★★★ Enter で終えると `abandon = false` の行が 1 本立つ。
    #[test]
    fn driver_emits_a_confirmed_row() {
        let _g = acquire();
        drive(A, true, Chord::Plain, 100);
        drive(SPACE, true, Chord::Plain, 300);
        drive(ENTER, true, Chord::Plain, 900);
        assert_eq!(
            collect_row(),
            Some(ComposeSummary {
                dwell_ms: 800,
                nav: 0,
                abandon: false,
            })
        );
        assert!(!IME_COMPOSING.load(Ordering::Acquire));
        assert!(!IME_ACTIVE.load(Ordering::Acquire));
    }

    /// ⚠️★★★ ESC で終えると `abandon = true` の行が立つ。**本 issue の受け入れ条件そのもの。**
    #[test]
    fn driver_emits_an_abandoned_row() {
        let _g = acquire();
        drive(A, true, Chord::Plain, 100);
        drive(SPACE, true, Chord::Plain, 300);
        drive(RIGHT, true, Chord::Plain, 400);
        drive(ESC, true, Chord::Plain, 900);
        assert_eq!(
            collect_row(),
            Some(ComposeSummary {
                dwell_ms: 800,
                nav: 1,
                abandon: true,
            })
        );
    }

    /// ⚠️★★★ **回収前に英数入力が挟まっても `abandon` が消えない。**
    #[test]
    fn a_keystroke_after_the_session_does_not_erase_the_pending_row() {
        let _g = acquire();
        drive(A, true, Chord::Plain, 100);
        drive(ESC, true, Chord::Plain, 500);
        // ⚠️ ここで IME Monitor はまだ回収していない。英数モードで打鍵が続く。
        drive(K, false, Chord::Plain, 520);
        drive(K, false, Chord::Plain, 540);
        assert_eq!(
            collect_row(),
            Some(ComposeSummary {
                dwell_ms: 400,
                nav: 0,
                abandon: true,
            }),
            "回収前の打鍵で放棄フラグが消えている"
        );
    }

    /// ⚠️★★★ **回収前に *次の変換が始まっても* 放棄フラグが化けない。**
    ///
    /// ★ これがドライバ設計の肝である。⚠️ 進行中の `nav` と回収待ちの要約を
    ///   同じ Atomic に置くと、**新セッションの開始時リセットが要約を上書きし**、
    ///   「前セッションの `dwell_ms`」＋「0 の `nav`」＋「`false` の `abandon`」という
    ///   **存在しない変換が 1 行出る** (★ 行が消えるより悪い —— 値が偽装される)。
    ///
    /// ⚠️ 実際の操作: ESC で放棄 → 100ms 以内に次の変換を打ち始める。
    #[test]
    fn a_new_session_before_collection_does_not_forge_the_pending_row() {
        let _g = acquire();
        drive(A, true, Chord::Plain, 0);
        drive(RIGHT, true, Chord::Plain, 100);
        drive(ESC, true, Chord::Plain, 400); // 放棄。READY=true / abandon=true / nav=1
                                             // ⚠️ IME Monitor が来る前に次の変換が始まる (100ms 以内)。
        drive(A, true, Chord::Plain, 450);
        drive(SPACE, true, Chord::Plain, 480);
        assert_eq!(
            collect_row(),
            Some(ComposeSummary {
                dwell_ms: 400,
                nav: 1,
                abandon: true,
            }),
            "次の変換の開始で、回収待ちの行が偽装された"
        );
        // ★ 2 本目のセッションはそのまま続いていること。
        assert!(IME_COMPOSING.load(Ordering::Acquire));
        assert!(IME_ACTIVE.load(Ordering::Acquire));
    }

    /// ★ セッション中は `IME_COMPOSING` / `IME_COMPOSITION_START_MS` が立っている。
    #[test]
    fn driver_mirrors_the_session_fields() {
        let _g = acquire();
        drive(A, true, Chord::Plain, 7_000);
        assert!(IME_COMPOSING.load(Ordering::Acquire));
        assert_eq!(IME_COMPOSITION_START_MS.load(Ordering::Relaxed), 7_000);
        assert!(!IME_ACTIVE.load(Ordering::Acquire));
        drive(SPACE, true, Chord::Plain, 7_100);
        assert!(IME_ACTIVE.load(Ordering::Acquire), "Space で候補表示になる");
        assert!(
            collect_row().is_none(),
            "セッション途中で行が出てはならない"
        );
    }

    /// ⚠️ 上限超過は **行を出さない** (READY を立てない)。
    #[test]
    fn driver_emits_nothing_when_truncated() {
        let _g = acquire();
        drive(A, true, Chord::Plain, 0);
        drive(ENTER, true, Chord::Plain, MAX_SESSION_MS + 1);
        assert!(collect_row().is_none(), "打ち切りで行を出してはならない");
        assert!(!IME_COMPOSING.load(Ordering::Acquire));
    }

    /// ★ 新しいセッションの開始で `nav` が 0 に戻る (前セッションの値を持ち込まない)。
    #[test]
    fn a_new_session_resets_nav() {
        let _g = acquire();
        drive(A, true, Chord::Plain, 0);
        drive(RIGHT, true, Chord::Plain, 50);
        drive(RIGHT, true, Chord::Plain, 60);
        drive(ENTER, true, Chord::Plain, 100);
        let first = collect_row().expect("1 本目が出ていない");
        assert_eq!(first.nav, 2);
        drive(A, true, Chord::Plain, 200);
        drive(ENTER, true, Chord::Plain, 300);
        assert_eq!(collect_row().expect("2 本目が出ていない").nav, 0);
    }

    /// ★ `should_drain_ready` の OS 対のテスト (⚠️ **両 OS で両分岐を検証する**)。
    #[test]
    fn drain_policy_differs_by_os() {
        // ⚠️ READY が立っていなければ、どちらの OS でも回収しない。
        assert!(!should_drain_ready(false, false, true));
        assert!(!should_drain_ready(false, false, false));
        // ★ Windows: active が立っている間は遷移経路に任せる (挙動を変えない)。
        assert!(should_drain_ready(true, false, true));
        assert!(!should_drain_ready(true, true, true));
        // ★ macOS: READY だけを見る (⚠️ 先送りすると要約が上書きされて行が消える)。
        assert!(should_drain_ready(true, false, false));
        assert!(should_drain_ready(true, true, false));
    }

    /// ⚠️ `IME_ACTIVE` を外部 (lib.rs の safety valve) が落としても、
    /// ★ セッションは続き、終端キーでちゃんと 1 行出る。
    #[test]
    fn an_external_active_reset_does_not_lose_the_session() {
        let _g = acquire();
        drive(A, true, Chord::Plain, 0);
        drive(SPACE, true, Chord::Plain, 100);
        // ⚠️ safety valve 相当の外部リセット。
        IME_ACTIVE.store(false, Ordering::Release);
        drive(ENTER, true, Chord::Plain, 400);
        assert_eq!(
            collect_row(),
            Some(ComposeSummary {
                dwell_ms: 400,
                nav: 0,
                abandon: false,
            })
        );
    }
}
