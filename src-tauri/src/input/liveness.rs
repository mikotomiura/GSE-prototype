//! キーボードフックが「生きているか」を、**フックとは独立した情報源**で確かめる。
//!
//! ## ⚠️★★ なぜ要るか (2026-08-09 の Windows 実機)
//!
//! G1 の 1 ブロック (5 分) が **打鍵 1 件のまま「正常なブロック」として自動提出された**。
//! アプリ側に異常を示すログは 1 行も無く、トレイは終始「● 計測中」だった。
//! 一次記録: `experiments/20260801-controlled-friction-task/windows-verification.md` §5-7。
//!
//! 構造的な理由は 2 つある:
//!
//! 1. `HOOK_ACTIVE` は **`SetWindowsHookExW` が成功した**ことしか意味しない
//!    (`hook_windows.rs`)。OS が低レベルフックを黙って外しても `true` のままである。
//! 2. フックスレッドのメッセージループは **`WM_QUIT` でしか抜けない**ので、
//!    再設置経路 (`Keyboard hook message loop exited`) も発火しない。
//!    ★ 実測: 当該ログでその行は **0 件**、対照の `Keyboard hook installed` は 3 件。
//!
//! → ★ **「設置済み」と「イベントが届いている」を別の概念として分ける**のが本モジュールである。
//!
//! ## 設計
//!
//! - **測る**: `last_system_input_tick()` = OS が持つ「最後の入力時刻」の**生 tick**。
//!   ★ 値の**変化**しか見ないので、絶対時刻へ変換せず、⚠️ 32bit tick のラップアラウンドも
//!   踏まない (等値比較なので巻き戻っても壊れない)。
//!   ⚠️ ★ **キーの内容も種別も読まない** (`data-privacy`)。得られるのは「何か入力があったか」だけ。
//! - **判断する**: `step()` / `health()` は **OS 非依存の純関数**。閾値は引数
//!   (`Thresholds`) なので、境界を単体テストで固定できる。
//! - **配線する**: `lib.rs` の 1 Hz 監視スレッド。⚠️ ★ **トレイのスレッドには載せない**
//!   (トレイは生成に失敗しうるので、そこに載せると検知ごと消える)。
//!
//! ## ⚠️ 既知の限界 (★ 隠さずテストで固定してある)
//!
//! `GetLastInputInfo` は **マウスも含む**。したがって「2 分間ずっと読んで
//! スクロールしていただけ」も **starvation として数えられる** (= 誤検知しうる)。
//! ★ だから NDJSON には**判断ではなく測った量** (`starved_ms`) を残し、
//! 後から閾値を変えて再解釈できるようにする。

/// フックの健康状態。★ 認知状態ではない (盲検)。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum HookHealth {
    /// 正常、または判断材料が無い。
    Ok,
    /// ⚠️ 疑わしい。★ ログにだけ残す段階 (トレイは変えない)。
    Suspect,
    /// ⚠️★ 届いていないとみなす段階。トレイを「計測できていません」にし、再設置を要求する。
    Down,
}

/// 判定のしきい値 (ms)。★ **定数ではなく値**にしてあるのは、境界をテストで固定するため。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Thresholds {
    /// この時間 starve したら `Suspect` (ログに 1 回だけ `ERROR`)。
    pub log_after_ms: u64,
    /// この時間 starve したら `Down` (トレイ表示 + 再設置)。
    pub down_after_ms: u64,
}

impl Default for Thresholds {
    /// 既定は 30 秒 / 120 秒 (二段)。
    ///
    /// ⚠️ ★ トレイ側を長く取るのは、**被験者の目に入る警告**だからである
    /// (マウス中心の作業で誤検知しうる)。ログ側は研究者が後から読むので短くてよい。
    fn default() -> Self {
        Self {
            log_after_ms: 30_000,
            down_after_ms: 120_000,
        }
    }
}

/// 「システムには入力があるのに、自前のフックには何も来ていない」時間の累積。
#[derive(Debug, Clone, Copy, PartialEq, Eq, Default)]
pub struct Starvation {
    pub starved_ms: u64,
}

/// 1 tick 分の状態遷移。★ **純関数**。時計もグローバルも触らない。
///
/// - `session_active`: 計測中か。⚠️ 非計測中は打鍵が無くて当たり前なので数えない。
/// - `system_input_seen`: この tick の間に **OS 側の最終入力時刻が変化した**か
///   (= 誰かがキーかマウスを触った)。
/// - `hook_event_seen`: この tick の間に **自前のフックが呼ばれた**か。
/// - `tick_ms`: この tick の長さ。
///
/// ★ 「システム入力が無い」ときは **進めも戻しもしない** (`prev` をそのまま返す)。
/// ⚠️ 本人が席を外しているだけの沈黙を starvation として数えないためである。
pub fn step(
    prev: Starvation,
    session_active: bool,
    system_input_seen: bool,
    hook_event_seen: bool,
    tick_ms: u64,
) -> Starvation {
    if !session_active || hook_event_seen {
        // ★ 届いた瞬間に 0 へ戻す (復帰の判定はここに集約する)。
        return Starvation { starved_ms: 0 };
    }
    if !system_input_seen {
        // 判断材料が無い = 凍結する。
        return prev;
    }
    Starvation {
        starved_ms: prev.starved_ms.saturating_add(tick_ms),
    }
}

/// 累積 starvation を健康状態へ写す。★ 純関数。
pub fn health(s: Starvation, th: Thresholds) -> HookHealth {
    if s.starved_ms >= th.down_after_ms {
        HookHealth::Down
    } else if s.starved_ms >= th.log_after_ms {
        HookHealth::Suspect
    } else {
        HookHealth::Ok
    }
}

/// OS が持つ「最後の入力時刻」の生 tick。⚠️ ★ **値の変化だけを見る**こと。
///
/// `None` は「この OS では判断材料が無い」を意味し、呼び出し側は
/// `system_input_seen = false` として扱う (= starvation を進めない = 安全側)。
#[cfg(target_os = "windows")]
pub fn last_system_input_tick() -> Option<u32> {
    use windows::Win32::UI::Input::KeyboardAndMouse::{GetLastInputInfo, LASTINPUTINFO};

    let mut lii = LASTINPUTINFO {
        cbSize: std::mem::size_of::<LASTINPUTINFO>() as u32,
        dwTime: 0,
    };
    // SAFETY: `lii` は正しい `cbSize` を持つローカル変数で、API は当該構造体へ
    // 書き込むだけである (ポインタを保持しない)。失敗時は戻り値 FALSE で判別する。
    let ok = unsafe { GetLastInputInfo(&mut lii) };
    if ok.as_bool() {
        Some(lii.dwTime)
    } else {
        None
    }
}

/// tick が「揺れ」ではなく **本当に入力があった** ことを示しているか。
///
/// ⚠️★ Windows と macOS で規則が違うのは、**tick の出どころが違う**からである。
/// - Windows (`GetLastInputInfo`): OS が持つ値をそのまま読む。揺れない → 等値比較でよい。
/// - macOS (`CGEventSourceSecondsSinceLastEventType`): 「最後の入力からの秒数」なので
///   ★ `now - since` に直す必要があり、その引き算に**サンプリングの揺れが乗る**。
pub fn system_input_seen(prev: Option<u32>, now: Option<u32>) -> bool {
    match (prev, now) {
        (Some(a), Some(b)) => tick_indicates_input(a, b),
        // 判断材料が無い OS は安全側に倒す = starvation を進めない。
        _ => false,
    }
}

/// macOS 以外: 値が変われば入力があった。⚠️ 32bit のラップアラウンドは等値比較なので無害。
#[cfg(not(target_os = "macos"))]
fn tick_indicates_input(a: u32, b: u32) -> bool {
    a != b
}

/// macOS で「揺れ」と「入力」を分ける閾値 (ms)。
///
/// ## ★ 実測 (2026-08-10・離席 12 秒 / 200ms 間隔 60 サンプル)
///
/// `now - since` の広がりは **55.5 ms** だった (隣接差の中央値 0.001 ms、最大 55.46 ms が 1 回)。
/// 一方、**連続打鍵中**は 1 秒 tick ごとに約 **1000 ms** 動く。
/// → 55 ms と 1000 ms の間に線を引けばよい。★ 実測の 4 倍以上の余裕を取って 250 ms とする。
#[cfg(target_os = "macos")]
const MACOS_JITTER_TOLERANCE_MS: u32 = 250;

/// macOS: **250 ms 以上**動いたときだけ入力とみなす。
///
/// ⚠️★★ ここを「秒に量子化して等値比較」にしてはならない。**一度そう書いて赤を見た**:
/// 秒に丸めると、真の最終入力時刻が秒境界の近くにあるとき 55 ms の揺れが
/// バケツをまたいで「入力があった」に化ける (= 離席中の誤警告)。
/// ⚠️ かといって「±1 秒の差を無視する」にすると、**連続打鍵 (毎 tick +1 秒) まで
/// 無視して**しまい、★ 検出器が一番必要な場面で盲目になる。
/// → ms のまま持ち、**許容幅で比べる**のが正しい形である。
#[cfg(target_os = "macos")]
fn tick_indicates_input(a: u32, b: u32) -> bool {
    // ★ `i32` の wrapping 差で比べる。u32 の `wrapping_sub` だと **負の揺れ** (-55ms) が
    //   約 42.9 億に化けて閾値を越え、⚠️ 揺れを入力と誤読する。
    (b as i32).wrapping_sub(a as i32).unsigned_abs() >= MACOS_JITTER_TOLERANCE_MS
}

/// macOS の「最後の入力からの秒数」を、**ミリ秒**の絶対時刻 tick に写す純関数。
///
/// ⚠️★★ **`since_secs` をそのまま返してはならない。** `since_secs` は離席中に
/// 増え続けるので、「変化した = 入力があった」と読む呼び出し側から見ると
/// **常に入力があることになり**、⚠️ 離席中ずっと starvation が進んで
/// 「フックが死んだ」と誤警告する (`step` は `system_input_seen && !hook_event_seen` で進む)。
/// → ★ **絶対時刻 (`now - since`)** に直す。これは入力があったときにだけ動く。
///
/// 揺れの吸収は `tick_indicates_input` (許容幅) が担当する。★ ここでは丸めない。
#[cfg(target_os = "macos")]
pub(crate) fn last_input_tick_ms(now_ms: u64, since_secs: f64) -> Option<u32> {
    // ⚠️ 異常値は「判断材料が無い」に倒す (`None` = starvation を進めない = 安全側)。
    if !since_secs.is_finite() || since_secs < 0.0 {
        return None;
    }
    let since_ms = (since_secs * 1000.0) as u64;
    let last_ms = now_ms.saturating_sub(since_ms);
    // ★ u32 への切り捨ては意図的。約 49.7 日で巻き戻るが、`tick_indicates_input` が
    //   `i32` の wrapping 差で比べるので巻き戻りは 1 tick しか誤らない。
    Some(last_ms as u32)
}

/// macOS: `CGEventSourceSecondsSinceLastEventType` で OS 側の最終入力時刻を取る。
#[cfg(target_os = "macos")]
pub fn last_system_input_tick() -> Option<u32> {
    /// `kCGEventSourceStateCombinedSessionState`。
    const COMBINED_SESSION_STATE: i32 = 0;
    /// `kCGAnyInputEventType` (= `~0`)。キーだけでなくマウスも「システム入力」に数える。
    /// ⚠️ ★ ここをキーだけに絞ってはならない。`step` の意図は
    /// 「**人は居るのにフックだけ黙っている**」の検出であり、マウス操作も在席の証拠である。
    const ANY_INPUT_EVENT_TYPE: u32 = u32::MAX;

    #[link(name = "ApplicationServices", kind = "framework")]
    extern "C" {
        fn CGEventSourceSecondsSinceLastEventType(state_id: i32, event_type: u32) -> f64;
    }

    // SAFETY: 引数は 2 つとも値渡しの整数で、API は **読み取りのみ** を行い
    // ポインタを保持しない (pure read-only の問い合わせ)。権限も要らない。
    let since_secs = unsafe {
        CGEventSourceSecondsSinceLastEventType(COMBINED_SESSION_STATE, ANY_INPUT_EVENT_TYPE)
    };
    let now_ms = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .ok()?
        .as_millis() as u64;
    last_input_tick_ms(now_ms, since_secs)
}

/// Windows / macOS 以外: 判断材料が無い。
#[cfg(not(any(target_os = "windows", target_os = "macos")))]
pub fn last_system_input_tick() -> Option<u32> {
    None
}

// ---------------------------------------------------------------------------
// micro 帯 (30 秒未満) の窓集計 — ADR-013 D4 / 穴 A
// ---------------------------------------------------------------------------

/// **新しいブロックが始まったか** を、セッション開始時刻の変化から判定する純関数。
///
/// ## ⚠️★★★ なぜ `session_active` の立ち上がりでは足りないか (Codex HIGH・2026-08-19)
///
/// G-1 の「実行中の再押下」(`g1::StartAction::RotateForRestart`) は
/// **`session_active` を `true` のまま維持する**。→ ★ `false → true` の縁を見ていると
/// **この経路でだけ発火しない**。
///
/// ⚠️ 結果、`dropped_at_last_line` と `MicroStarveWindow` が**旧ファイルから新ファイルへ
/// 持ち越され**、`dropped_delta` / `starve_window` が**ファイル境界をまたいだ値**になる
/// —— ★ **まさに `dropped_delta` を足して消そうとした誤帰属**である。
///
/// → ★ **セッション開始時刻 (`SESSION_START_MS`) の変化**を見る。これは
/// 通常のブロック開始 (`0 → t`) でも、実行中の再押下 (`t1 → t2`) でも**必ず動く**。
///
/// ⚠️ `now == 0` (ブロック終了で 0 に戻された) は**新しいブロックではない**ので false。
pub fn is_new_block_epoch(prev_session_start_ms: u64, now_session_start_ms: u64) -> bool {
    now_session_start_ms != 0 && now_session_start_ms != prev_session_start_ms
}

/// `starve_window` 行の窓の長さ (ms)。
///
/// ⚠️ 1Hz の全 tick を残す案は採らない —— ★ **値の大半が 0** でログ量とバッテリに見合わない
/// (ADR-013 D6)。★ 窓集計で「micro 帯が何割あるか」＝**投資判断の材料としては足りる**。
pub const STARVE_WINDOW_MS: u64 = 60_000;

/// 窓が閉じたときの集計結果。⚠️ ★ `n_lt30 == 0` の窓は**呼び出し側が出力しない**。
#[derive(Debug, Clone, Copy, PartialEq, Eq, Default)]
pub struct StarveWindowTally {
    /// この窓で**閉じた** micro エピソードの本数。
    pub n_lt30: u64,
    /// その合計時間 (ms)。
    pub sum_lt30_ms: u64,
    /// ⚠️★★★ **この窓の実測の長さ** (ms)。
    ///
    /// ★ 公称 [`STARVE_WINDOW_MS`] を書いてはならない。窓は実測 `tick_ms` の累積で閉じるので
    /// **常に 60 秒以上**になり、⚠️ スリープ復帰後は 1 tick で数十分ぶん進んで即閉じることもある。
    /// → ★ `n_lt30 / win_ms` を「micro 帯の割合」として読む解析
    /// (**本行の存在理由そのもの**) が**過大評価**になる (code-reviewer MEDIUM・2026-08-19)。
    pub win_ms: u64,
}

/// micro 帯 (`0 < peak < log_after_ms`) のエピソードを 60 秒窓で数える累算器。
///
/// ## ★ 何を 1 エピソードと数えるか
///
/// [`step`] は **フックが呼ばれた瞬間に `starved_ms` を 0 に戻す**。
/// → ★ **エピソードの終わり = 値が正から 0 に落ちた tick**であり、その直前値がピークである。
///
/// ⚠️★★★ **`peak >= log_after_ms` のものは数えない。** それらは `hook_health`
/// (`Suspect` 以上) が既に記録しており、★ **2 つのトラックは閾値できれいに分割される**
/// (＝二重計上しない)。
///
/// ## ★ 時計を読まない
///
/// 窓の進行は**実測経過 `tick_ms` の累積**で決める。[`step`] と同じく純関数なので、
/// ★ 両 OS で境界をテストできる (`docs/agent-shared.md`「OS ごとに規則が違うロジックは
/// 両 OS に対のテストを置く」の趣旨に沿って、そもそも OS 差を持ち込まない)。
#[derive(Debug, Clone, Copy, PartialEq, Eq, Default)]
pub struct MicroStarveWindow {
    elapsed_ms: u64,
    tally: StarveWindowTally,
}

impl MicroStarveWindow {
    pub fn new() -> Self {
        Self::default()
    }

    /// 1 tick 進める。★ **純関数的** (時計もグローバルも触らない)。
    ///
    /// - `session_active`: 計測中か。⚠️★★★ **窓をブロックに閉じるために要る**（下記）。
    /// - `prev_starved_ms` / `now_starved_ms`: [`step`] の**前後**の `starved_ms`。
    /// - `th`: 閾値。⚠️ ★ **30_000 を直書きしない** —— `hook_health` 側と同じ値を使うことで、
    ///   閾値を動かしたときに 2 トラックの分割が自動で追随する。
    ///
    /// 戻り値が `Some` なら**窓が閉じた**。⚠️ ★ `n_lt30 == 0` の窓は `None` を返す
    /// (＝行を出さない・ADR-013 D4)。
    ///
    /// ## ⚠️★★★ なぜ `session_active` を見るか (security-checker MEDIUM・2026-08-19)
    ///
    /// 見ないと **2 つの誤りが出る**:
    ///
    /// 1. ⚠️ **偽エピソードを 1 本計上する。** [`step`] は `!session_active` でも
    ///    `starved_ms` を 0 に落とすので、ブロック終了の tick が
    ///    「正 → 0」に見え、**打鍵で終わっていないエピソード**が数えられる
    ///    (最大 +29,999 ms)。★ ブロックごとに毎回起きる**系統誤差**である。
    /// 2. ⚠️ **窓がブロックをまたぐ。** 1 分休憩とローテートを越えて走り続けるので、
    ///    **ブロック N で貯めた集計がブロック N+1 のファイルに書かれる**、または
    ///    `session_end` の後ろに 1 行付く。→ ★ 「1 ブロック = 1 ファイル」
    ///    (`protocol.md §1`) の前提で読む解析が**誤帰属**する。
    ///
    /// → ★ **非計測になったら窓ごと捨てる。**
    /// ⚠️ **既知の切り捨て**: ブロック末尾の 60 秒未満の端数に入っていた本数は**失われる**
    /// (★ 数え漏らしは下側に振れる)。⚠️ ここで「端数を吐く」ようにすると、
    /// `session_end` との**順序が保証されない**ため誤帰属のほうが起きる。
    /// ★ **誤帰属より既知の切り捨てを採る**。
    #[must_use]
    pub fn tick(
        &mut self,
        session_active: bool,
        prev_starved_ms: u64,
        now_starved_ms: u64,
        th: Thresholds,
        tick_ms: u64,
    ) -> Option<StarveWindowTally> {
        if !session_active {
            // ★ 窓をブロックに閉じる。⚠️ 計上もしない (この 0 復帰は打鍵由来ではない)。
            *self = Self::default();
            return None;
        }
        // ★ エピソードが閉じた瞬間だけを拾う。
        if now_starved_ms == 0 && prev_starved_ms > 0 && prev_starved_ms < th.log_after_ms {
            self.tally.n_lt30 = self.tally.n_lt30.saturating_add(1);
            self.tally.sum_lt30_ms = self.tally.sum_lt30_ms.saturating_add(prev_starved_ms);
        }

        self.elapsed_ms = self.elapsed_ms.saturating_add(tick_ms);
        if self.elapsed_ms < STARVE_WINDOW_MS {
            return None;
        }

        let mut tally = self.tally;
        // ★ **実測の窓長**を載せる (公称 60_000 ではない)。分母を嘘にしない。
        tally.win_ms = self.elapsed_ms;
        // ⚠️ ★ 窓は必ず閉じる (集計をゼロに戻す)。**出力しないだけ**で、数え漏らしにはしない。
        //
        // ⚠️★★ **超過分を次の窓へ繰り越してはならない。** 一見「窓が毎回 1 tick ぶん長くなる
        //   系統誤差」を消せそうに見えるが (code-reviewer LOW)、★ 繰り越した時間は
        //   **直前の窓の `win_ms` に既に数えられている**ので、次の窓でも数えると
        //   **経過時間を二重計上する** (窓長の総和が実時間を超える)。
        //   → ★ 0 に戻し、**各窓は自分の実測長を正直に申告する**。窓長がばらつくこと自体は
        //   誤差ではない (分母が正しいので割合の計算は歪まない)。
        self.elapsed_ms = 0;
        self.tally = StarveWindowTally::default();

        // ⚠️★★★ 空の窓は出さない (在席の連続タイムラインを作らない・security-checker MEDIUM)。
        if tally.n_lt30 == 0 {
            None
        } else {
            Some(tally)
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    const TICK: u64 = 1_000;

    fn th() -> Thresholds {
        Thresholds {
            log_after_ms: 30_000,
            down_after_ms: 120_000,
        }
    }

    /// ★ OS 非依存: 判断材料が片方でも無ければ、必ず `false` (= starvation を進めない)。
    /// ⚠️ ここが `true` に倒れると、**判断材料が無い OS で誤警告**が出る。
    #[test]
    fn missing_tick_never_counts_as_input() {
        assert!(!system_input_seen(None, Some(5)));
        assert!(!system_input_seen(Some(5), None));
        assert!(!system_input_seen(None, None));
    }

    /// ★ OS 非依存: **同じ値なら入力ではない**。どちらの規則でも成立する不変条件。
    #[test]
    fn an_unchanged_tick_is_never_input() {
        assert!(!system_input_seen(Some(1_234_567), Some(1_234_567)));
    }

    /// 正常: フックが呼ばれ続けている → 何度回しても `Ok` で 0 のまま。
    #[test]
    fn healthy_hook_never_starves() {
        let mut s = Starvation::default();
        for _ in 0..300 {
            s = step(s, true, true, true, TICK);
        }
        assert_eq!(s.starved_ms, 0);
        assert_eq!(health(s, th()), HookHealth::Ok);
    }

    /// ★★ 本命: システムには入力があるのにフックが呼ばれない → 30 秒で Suspect、120 秒で Down。
    #[test]
    fn silent_hook_is_detected_at_both_thresholds() {
        let mut s = Starvation::default();
        for _ in 0..29 {
            s = step(s, true, true, false, TICK);
        }
        assert_eq!(health(s, th()), HookHealth::Ok, "29 秒ではまだ Ok");

        s = step(s, true, true, false, TICK);
        assert_eq!(s.starved_ms, 30_000);
        assert_eq!(
            health(s, th()),
            HookHealth::Suspect,
            "30 秒ちょうどで Suspect"
        );

        for _ in 0..89 {
            s = step(s, true, true, false, TICK);
        }
        assert_eq!(
            health(s, th()),
            HookHealth::Suspect,
            "119 秒ではまだ Suspect"
        );

        s = step(s, true, true, false, TICK);
        assert_eq!(s.starved_ms, 120_000);
        assert_eq!(health(s, th()), HookHealth::Down, "120 秒ちょうどで Down");
    }

    /// ⚠️★ **既知の誤検知を仕様として固定する**: マウスだけ動かしている人も Down になる。
    ///
    /// ★ `GetLastInputInfo` はマウスを含むので、キーボードだけを見分けることはできない。
    /// この挙動を「バグ」ではなく「限界」として明示的に残す。
    /// → だから NDJSON には `starved_ms` を載せ、**後から再解釈できる**ようにしてある。
    #[test]
    fn mouse_only_work_is_a_known_false_positive() {
        let mut s = Starvation::default();
        for _ in 0..120 {
            // system_input_seen = true (マウス) / hook_event_seen = false (打鍵なし)
            s = step(s, true, true, false, TICK);
        }
        assert_eq!(
            health(s, th()),
            HookHealth::Down,
            "マウスのみの作業は Down に化ける (既知の限界)"
        );
    }

    /// 計測していないときは数えない。
    #[test]
    fn inactive_session_never_starves() {
        let mut s = Starvation::default();
        for _ in 0..300 {
            s = step(s, false, true, false, TICK);
        }
        assert_eq!(s.starved_ms, 0);
        assert_eq!(health(s, th()), HookHealth::Ok);
    }

    /// 誰も何も触っていない沈黙は starvation ではない (凍結する)。
    #[test]
    fn no_system_input_freezes_instead_of_accumulating() {
        let mut s = Starvation::default();
        for _ in 0..40 {
            s = step(s, true, true, false, TICK); // まず 40 秒 starve させる
        }
        let frozen = s.starved_ms;
        assert_eq!(frozen, 40_000);
        for _ in 0..600 {
            s = step(s, true, false, false, TICK); // 10 分間、誰も触らない
        }
        assert_eq!(s.starved_ms, frozen, "沈黙中は進まない");
        assert_eq!(
            health(s, th()),
            HookHealth::Suspect,
            "Down へ勝手に落ちない"
        );
    }

    /// 復帰: フックが 1 回でも呼ばれたら 0 に戻る。
    #[test]
    fn recovery_resets_to_zero() {
        let mut s = Starvation::default();
        for _ in 0..200 {
            s = step(s, true, true, false, TICK);
        }
        assert_eq!(health(s, th()), HookHealth::Down);
        s = step(s, true, true, true, TICK);
        assert_eq!(s.starved_ms, 0);
        assert_eq!(health(s, th()), HookHealth::Ok);
    }

    /// ★ 判断材料が無い OS (macOS 等) では安全側 = 何も起きない。
    #[test]
    fn platform_without_a_source_never_reports_down() {
        // `last_system_input_tick()` が None のとき、呼び出し側は
        // `system_input_seen = false` を渡す契約である。
        let mut s = Starvation::default();
        for _ in 0..600 {
            s = step(s, true, false, false, TICK);
        }
        assert_eq!(s.starved_ms, 0);
        assert_eq!(health(s, th()), HookHealth::Ok);
    }
    // -----------------------------------------------------------------------
    // micro 帯の窓集計 (ADR-013 D4 / 穴 A)
    // -----------------------------------------------------------------------

    /// 窓が閉じるまで `tick` を回す補助。`episodes` は (ピーク値) の並び。
    ///
    /// ★ 1 エピソードにつき「ピークまで上げて 0 に落とす」を 1 回ずつ行う。
    fn run_window(episodes: &[u64], filler_ticks: usize) -> Option<StarveWindowTally> {
        let mut w = MicroStarveWindow::new();
        let mut out = None;
        let mut ticks = 0usize;
        for &peak in episodes {
            // ★ 落ちる瞬間だけが数えられる (prev>0 かつ now==0)。
            let r = w.tick(true, peak, 0, th(), TICK);
            out = out.or(r);
            ticks += 1;
        }
        for _ in ticks..filler_ticks {
            let r = w.tick(true, 0, 0, th(), TICK);
            out = out.or(r);
        }
        out
    }

    /// ⚠️★★★ **`n_lt30 == 0` の窓は 1 行も出さない** (ADR-013 D4)。
    ///
    /// ★ 理由は「在席の連続タイムラインを作らない」ことである
    /// (毎分必ず出すと労務監視的な二次利用に転用されうる・security-checker MEDIUM)。
    #[test]
    fn starve_window_omits_empty_windows() {
        // 60 秒ぶん回しても micro エピソードが 0 本なら None。
        assert_eq!(run_window(&[], 60), None);
        // ★ 念のため 3 窓ぶん回しても出ないこと。
        let mut w = MicroStarveWindow::new();
        for _ in 0..180 {
            assert_eq!(w.tick(true, 0, 0, th(), TICK), None, "空の窓が出力された");
        }
    }

    /// ⚠️★★★ **ブロック終了の 0 復帰を micro エピソードとして数えない**
    /// (security-checker MEDIUM・2026-08-19)。
    ///
    /// ★ `step` は `!session_active` でも `starved_ms` を 0 に落とすので、
    /// 素直に書くと**打鍵で終わっていないエピソード**が毎ブロック 1 本混入する
    /// (＝ **系統誤差**)。
    #[test]
    fn block_end_does_not_count_a_fake_episode() {
        let mut w = MicroStarveWindow::new();
        // 計測中に 5 秒 starve していた状態から、**ブロック終了**で 0 に落ちる。
        assert_eq!(w.tick(false, 5_000, 0, th(), TICK), None);
        // ★ その後 1 窓ぶん回しても、偽エピソードが計上されていないので何も出ない。
        let mut out = None;
        for _ in 0..60 {
            out = out.or(w.tick(true, 0, 0, th(), TICK));
        }
        assert_eq!(out, None, "ブロック終了の 0 復帰が計上されている");
    }

    /// ⚠️★★★ **窓はブロックをまたがない** (security-checker MEDIUM・2026-08-19)。
    ///
    /// ★ またぐと **ブロック N の集計がブロック N+1 のファイルに書かれる**、または
    /// `session_end` の後ろに 1 行付く ＝ 「1 ブロック = 1 ファイル」の前提で読む解析が
    /// **誤帰属**する。
    #[test]
    fn window_is_closed_at_block_boundary() {
        let mut w = MicroStarveWindow::new();
        // ブロック N: 59 tick のあいだに micro を 3 本ためる (★ まだ窓は閉じていない)。
        for _ in 0..3 {
            assert_eq!(w.tick(true, 4_000, 0, th(), TICK), None);
        }
        for _ in 3..59 {
            assert_eq!(w.tick(true, 0, 0, th(), TICK), None);
        }
        // ★ ブロック終了 → 窓ごと捨てる (⚠️ 端数は失われる = 既知の切り捨て)。
        assert_eq!(w.tick(false, 0, 0, th(), TICK), None);

        // ブロック N+1: 1 本だけ。⚠️ 前ブロックの 3 本が混ざっていないこと。
        let mut out = None;
        out = out.or(w.tick(true, 6_000, 0, th(), TICK));
        for _ in 1..60 {
            out = out.or(w.tick(true, 0, 0, th(), TICK));
        }
        let t = out.expect("N+1 の窓が閉じるはず");
        assert_eq!(t.n_lt30, 1, "前ブロックの集計が持ち越されている: {t:?}");
        assert_eq!(t.sum_lt30_ms, 6_000);
    }

    /// ★ micro 帯 (`0 < peak < log_after_ms`) だけを数える。
    ///
    /// ⚠️ `peak >= log_after_ms` は `hook_health` (Suspect 以上) が既に記録しているので
    /// **二重計上しない**。★ 2 つのトラックは閾値できれいに分割される。
    #[test]
    fn starve_window_counts_only_micro_episodes() {
        // 2 秒 / 15 秒 = micro、30 秒 (境界) と 45 秒 = hook_health 側。
        let t = run_window(&[2_000, 30_000, 15_000, 45_000], 60).expect("窓が出るはず");
        assert_eq!(t.n_lt30, 2, "micro だけを数えること");
        assert_eq!(t.sum_lt30_ms, 17_000);
    }

    /// ⚠️★★★ **`win_ms` は実測の窓長であって公称 60_000 ではない**
    /// (code-reviewer MEDIUM・2026-08-19)。
    ///
    /// ★ `n_lt30 / win_ms` を「micro 帯の割合」として読む解析が**過大評価**にならないため。
    #[test]
    fn win_ms_reports_the_measured_window_length() {
        // ① 1 秒 tick ちょうど 60 回 → 実測も 60_000。
        let t = run_window(&[3_000], 60).expect("窓が閉じるはず");
        assert_eq!(t.win_ms, 60_000);

        // ② ⚠️ スリープ復帰などで 1 tick が巨大な場合。
        //    ★ 公称を書いていたらここが 60_000 のまま嘘になる。
        let mut w = MicroStarveWindow::new();
        assert_eq!(w.tick(true, 5_000, 0, th(), 1_000), None);
        let t2 = w
            .tick(true, 0, 0, th(), 3_600_000)
            .expect("巨大 tick で窓が閉じるはず");
        assert_eq!(t2.n_lt30, 1);
        assert_eq!(t2.win_ms, 3_601_000, "実測の窓長を載せること");
    }

    /// ⚠️★★★ **実行中の再押下 (`RotateForRestart`) でも「新しいブロック」と判定できること**
    /// (Codex HIGH・2026-08-19)。
    ///
    /// ★ この経路は `session_active` を `true` のまま維持するので、
    /// ⚠️ `false → true` の縁を見ていると**発火しない** ＝ 計器の状態が旧ファイルから
    /// 持ち越され、`dropped_delta` / `starve_window` がファイル境界をまたぐ。
    #[test]
    fn new_block_epoch_fires_on_rotate_while_active() {
        // ★ 通常のブロック開始 (0 → t)。
        assert!(is_new_block_epoch(0, 1_700_000_000_000));
        // ★★★ 本命: 実行中の再押下 (t1 → t2)。どちらも非ゼロ。
        assert!(is_new_block_epoch(1_700_000_000_000, 1_700_000_268_500));
        // ⚠️ 同じブロックのあいだは発火しない (毎 tick リセットしてはならない)。
        assert!(!is_new_block_epoch(1_700_000_000_000, 1_700_000_000_000));
        // ⚠️ ブロック終了 (t → 0) は「新しいブロック」ではない。
        assert!(!is_new_block_epoch(1_700_000_000_000, 0));
        assert!(!is_new_block_epoch(0, 0));
    }

    /// ⚠️★★★ **窓長の総和が実経過時間を超えない** (＝ 経過時間を二重計上しない)。
    ///
    /// ★ 「超過分を次の窓へ繰り越す」案を**採らない**根拠である ——
    /// 繰り越した時間は**直前の窓の `win_ms` に既に数えられている**ので、
    /// 次の窓でも数えると総和が実時間を超える。
    #[test]
    fn window_lengths_never_double_count_elapsed_time() {
        let mut w = MicroStarveWindow::new();
        const TICKS: u64 = 27;
        const TICK_MS: u64 = 7_000;
        let mut sum = 0u64;
        for _ in 0..TICKS {
            if let Some(t) = w.tick(true, 2_000, 0, th(), TICK_MS) {
                sum += t.win_ms;
            }
        }
        assert!(
            sum <= TICKS * TICK_MS,
            "窓長の総和 {sum} が実経過 {} を超えている (二重計上)",
            TICKS * TICK_MS
        );
        // ★ どの窓も 60 秒以上ではある (閾値を下回って閉じない)。
        assert!(sum >= 60_000, "1 窓も閉じていない: {sum}");
    }

    /// ⚠️ 境界値: `log_after_ms` **ちょうど**は micro ではない (`<` であって `<=` ではない)。
    #[test]
    fn starve_window_boundary_is_exclusive() {
        assert_eq!(run_window(&[29_999], 60).map(|t| t.n_lt30), Some(1));
        assert_eq!(run_window(&[30_000], 60), None);
    }

    /// ★ 窓は 60 秒で閉じ、集計は持ち越さない。
    #[test]
    fn starve_window_resets_between_windows() {
        let mut w = MicroStarveWindow::new();
        // 1 窓目: 1 本。
        let mut first = None;
        for i in 0..60 {
            let r = if i == 0 {
                w.tick(true, 5_000, 0, th(), TICK)
            } else {
                w.tick(true, 0, 0, th(), TICK)
            };
            first = first.or(r);
        }
        assert_eq!(first.map(|t| t.n_lt30), Some(1));
        // 2 窓目: 0 本 → 出力しない (⚠️ 1 窓目の集計が残っていたらここで出てしまう)。
        let mut second = None;
        for _ in 0..60 {
            second = second.or(w.tick(true, 0, 0, th(), TICK));
        }
        assert_eq!(second, None, "前の窓の集計が持ち越されている");
    }

    /// ⚠️★★★ **`hook_health` の意味論が変わっていないこと** (ADR-013 D3-3a ③)。
    ///
    /// ★ ここが壊れると **ADR-011 の探索トラックと ADR-012 Stage 0 が再計算**になる。
    /// → ★ `step` / `health` / 既定閾値を「動かしていない」ことを値で固定する。
    #[test]
    fn hook_health_semantics_unchanged() {
        // ① 既定閾値は 30 秒 / 120 秒の二段のまま。
        let d = Thresholds::default();
        assert_eq!(d.log_after_ms, 30_000);
        assert_eq!(d.down_after_ms, 120_000);

        // ② `step` の 3 規則: 非計測は 0 / フック到達は 0 / システム入力が無ければ凍結。
        let s = Starvation { starved_ms: 7_000 };
        assert_eq!(step(s, false, true, false, TICK).starved_ms, 0);
        assert_eq!(step(s, true, true, true, TICK).starved_ms, 0);
        assert_eq!(step(s, true, false, false, TICK).starved_ms, 7_000);
        assert_eq!(step(s, true, true, false, TICK).starved_ms, 8_000);

        // ③ `health` の境界 (`>=`)。
        assert_eq!(health(Starvation { starved_ms: 29_999 }, d), HookHealth::Ok);
        assert_eq!(
            health(Starvation { starved_ms: 30_000 }, d),
            HookHealth::Suspect
        );
        assert_eq!(
            health(
                Starvation {
                    starved_ms: 119_999
                },
                d
            ),
            HookHealth::Suspect
        );
        assert_eq!(
            health(
                Starvation {
                    starved_ms: 120_000
                },
                d
            ),
            HookHealth::Down
        );
    }
}

// ---------------------------------------------------------------------------
// ⚠️★★ **OS ごとに「対になるテスト」を置くこと。**
//
// `tick_indicates_input` は OS ごとに規則が違う。片方だけテストを書くと、
// ★ もう片方は **CI で走るテストが減るだけ**になり、その OS の規則が未検証のまま残る。
// 2026-08-10 に実際にその状態を作った (macOS 前提のテストを Windows でも走らせて赤 →
// `cfg` で閉じたが、Windows 側の対を書き忘れた)。
// ---------------------------------------------------------------------------

/// Windows の規則: `GetLastInputInfo` の値は OS が持つものをそのまま読むので**揺れない**。
/// → ★ 許容幅を入れてはならない (入れると、1 秒 tick で進む連続打鍵を取りこぼす)。
#[cfg(all(test, target_os = "windows"))]
mod windows_tick_tests {
    use super::*;

    /// ★ 1 でも動けば入力である (macOS のような許容幅を持たない)。
    #[test]
    fn any_change_is_input() {
        assert!(system_input_seen(Some(1000), Some(1001)));
        assert!(system_input_seen(Some(1000), Some(999)));
    }

    /// ⚠️ 32bit のラップアラウンドをまたいでも「変わった」と読めること
    /// (等値比較なので巻き戻っても壊れない)。
    #[test]
    fn wraparound_is_still_a_change() {
        assert!(system_input_seen(Some(u32::MAX), Some(0)));
    }

    /// ★ 同じ値なら入力ではない。
    #[test]
    fn an_unchanged_tick_is_not_input() {
        assert!(!system_input_seen(Some(42), Some(42)));
    }
}

// ⚠️★★ **`target_os = "macos"` で閉じる。** ここのテストは macOS の比較規則
//   (許容幅つき) を前提にしており、Windows の規則 (等値比較) では成立しない。
//   ★ 2026-08-10 に閉じ忘れ、**手元 (macOS) では緑・Windows CI で赤**になった
//   (memory `windows-only-code-needs-ci` の裏返し: 手元で走るテストが
//   他方の OS でも走ることを忘れる形)。
#[cfg(all(test, target_os = "macos"))]
mod macos_tick_tests {
    use super::*;

    /// ★★ 本命: **離席中の揺れを入力と読まない**こと。
    ///
    /// ⚠️ ここが `true` になると `system_input_seen` が立ち続け、`hook_event_seen = false` と
    /// 組んで starvation が進み、**席を外しただけで「フックが死んだ」と警告する**。
    /// 2026-08-10 の実測 (揺れ 55.5 ms・境界に乗る最悪配置) をそのまま入力にする。
    #[test]
    fn idle_jitter_is_not_read_as_input() {
        // ★ 真の最終入力時刻を **わざと秒境界ちょうど**に置く (秒量子化だと必ず割れる配置)。
        let base_last_ms: u64 = 1_786_338_674_000;
        let jitter = [0.0_f64, 0.001, -0.02, 55.46, 0.0, -0.003];
        let mut prev: Option<u32> = None;
        for i in 0..60u64 {
            let now_ms = base_last_ms + 100_000 + i * 200;
            let since_ms = (now_ms - base_last_ms) as f64 + jitter[(i % 6) as usize];
            let tick = last_input_tick_ms(now_ms, since_ms / 1000.0);
            if let Some(p) = prev {
                assert!(
                    !system_input_seen(Some(p), tick),
                    "★ 離席中の揺れ ({:?} -> {:?}) を入力と読んだ = 誤警告になる",
                    p,
                    tick
                );
            }
            prev = tick;
        }
    }

    /// ★★ 逆向き: **連続打鍵は必ず入力と読む**こと。
    ///
    /// ⚠️ ここが `false` になると、フックが死んでいて被験者が打ち続けている
    /// **一番検出したい場面**で検出器が黙る。
    #[test]
    fn continuous_typing_is_always_read_as_input() {
        let mut prev: Option<u32> = None;
        for i in 0..60u64 {
            // 打鍵し続けている = 最後の入力は常に「たった今」。tick は 1 秒ごとに約 +1000ms。
            let now_ms = 1_786_338_674_000 + i * 1000;
            let tick = last_input_tick_ms(now_ms, 0.01);
            if let Some(p) = prev {
                assert!(
                    system_input_seen(Some(p), tick),
                    "★ 連続打鍵を入力と読めなかった = 検出器が盲目になる"
                );
            }
            prev = tick;
        }
    }

    /// ⚠️ 異常値は `None` に倒す。★ 進めるより凍結するほうが安全である。
    #[test]
    fn bogus_values_fall_back_to_none() {
        let now_ms: u64 = 1_786_338_800_000;
        assert_eq!(last_input_tick_ms(now_ms, f64::NAN), None);
        assert_eq!(last_input_tick_ms(now_ms, f64::INFINITY), None);
        assert_eq!(last_input_tick_ms(now_ms, -1.0), None);
    }
}
