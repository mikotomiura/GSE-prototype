//! IME 候補ウィンドウの **cloak/uncloak** から `IME_ACTIVE` を駆動する (Windows 限定)。
//!
//! # ⚠️★★★ なぜこれが要るのか
//!
//! ★ この Windows 11 の IME 候補 UI は、表示/非表示を `ShowWindow` ではなく
//! **DWM の cloak/uncloak** で行っている。実測 (60 秒 × 8 回) で:
//!
//! | 経路 | 結果 |
//! |---|---|
//! | `EVENT_OBJECT_IME_SHOW/HIDE/CHANGE` (0x8027-29) | ⚠️ **1 件も飛ばない** |
//! | `EnumWindows` による可視候補窓の走査 | ⚠️ **0/2400** |
//! | UI Automation のフォーカス要素 | ⚠️ **0** |
//! | `EVENT_OBJECT_TEXTEDIT_CONVERSIONTARGETCHANGED` (0x8030) | ⚠️ **0** |
//! | ★ `EVENT_OBJECT_CLOAKED`/`UNCLOAKED` + クラス `IME` | ★ **変換回数に比例して飛ぶ** |
//!
//! 詳細: `.steering/20260822-ime-active-rewiring/findings-enumwindows-probe.md` §15-16 /
//! `.steering/20260823-ime-active-cloak-rewiring/`。
//!
//! # ⚠️ 旧実装 (〜v0.1.27) との違い
//!
//! ★ 旧コードも偶然この経路を使っていた (定数 `IME_SHOW=0x8017` が実は `EVENT_OBJECT_CLOAKED`
//! だった) が、⚠️ **クラス絞りが無く、無関係な窓の cloak も同じ `IME_ACTIVE` に流していた**。
//! ★ 本モジュールは **クラスを `IME` に限定**し、**HWND 別に畳み**、
//! **DWM に現在状態を聞き直す**。
//!
//! # 責務の境界
//!
//! ★ 本ファイルは **OS 非依存の畳み込みロジック ([`CloakFold`]) だけ**を持つ。
//! ⚠️ Win32 呼び出し (`GetClassNameW` / `DwmGetWindowAttribute`) は `ime_windows.rs` 側にある
//! (★ `architecture-rules`: OS 依存は 1 か所に閉じる)。
//! → ★ おかげでここは **両 OS でコンパイル・テストできる** (`agent-shared.md` の
//! 「OS ごとに規則が違うロジックは両 OS に対のテストを置く」に沿う)。

use std::collections::BTreeSet;

/// ⚠️★★★ **`IME_ACTIVE` を cloak で駆動するときのクラス絞り。**
///
/// ★ 完全一致 `"IME"` (IMM32 のシステムウィンドウ) **だけ**を通す。
///
/// # ⚠️ なぜ `Xaml_WindowedPopupClass` / `ApplicationFrameWindow` を使わないか
///
/// ★ 実測では候補 UI と同じ周期で cloak されるが、⚠️ **どちらも汎用クラス**である
/// (前者はツールチップ・メニュー・フライアウト、後者は全 UWP のホストフレーム)。
/// ★ 60 秒の計測でたまたま候補 UI しか出なかっただけで、
/// ⚠️ **被験者が別のアプリを使えばツールチップ 1 個で誤検知する。**
/// ★ `IME` の「1 変換 = 2 周期」は畳めば済むが、汎用クラスの誤検知は畳んでも消えない。
///
/// # ⚠️★★★ `is_ime_candidate_class_name` が `"IME"` を *除外* しているのと矛盾しないのか
///
/// ★ **しない。判定している軸が違う。**
///
/// | | 既存 `is_ime_candidate_class_name` | ★ ここ |
/// |---|---|---|
/// | 軸 | **可視性** (`IsWindowVisible`) | ★ **cloak 遷移** |
/// | `IME` 窓の挙動 | ⚠️ **常時可視** → 含めると永久に true | ★ **静止時は遷移しない** (無操作 60 秒で 0 件・実測) |
///
/// ⚠️ 既存関数と**そのテスト (`excludes_language_bar_and_imm32_system_window`) は触らない。**
/// ★ あちらの除外理由 (常時可視) は今も正しい。
pub fn is_ime_cloak_class(class: &str) -> bool {
    class == "IME"
}

/// ⚠️★★★ **どちらの cloak 状態が「候補ウィンドウが見えている」か。**
///
/// ★ DWM の意味論では `cloaked = true` は「**DWM が描画していない = 見えていない**」である
/// (`DWMWA_CLOAKED` は逐語「the window is cloaked」/ 0 = not cloaked)。
/// → ★ 素直に **`見えている = !cloaked`**。
///
/// ⚠️★★★ **旧 v0.1.27 のコードはこの逆を仮定していた**
/// (`IME_SHOW`=0x8017=`EVENT_OBJECT_CLOAKED` で `IME_ACTIVE=true`)。
/// ★ 向きを取り違えると `ime_dwell` は「候補の滞在時間」ではなく
/// **「変換と変換のあいだ (候補が隠れている時間)」** を測ることになる。
/// ⚠️ 件数はどちらでも同じに見えるので、**実測しないと決まらない**。
///
/// ★ 実測で確定した向きを**この 1 関数に閉じ込め**、回帰テストで固定する。
/// → ⚠️ 将来向きを変えるなら、変えるのはここ 1 行とテストだけで済む。
pub fn candidate_shown_from_cloak(cloaked: bool) -> bool {
    !cloaked
}

/// ★ [`CloakFold`] が外へ出す唯一の出力。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum FoldAction {
    /// ★ 候補ウィンドウのセッションが始まった (値 = 開始時刻 epoch ms)。
    Begin(u64),
    /// ★ セッションが終わった。
    End {
        /// ★ 候補ウィンドウの滞在時間 (ms)。
        dwell_ms: u64,
        /// ⚠️★★★ **`true` = uncloak を取りこぼし、[`MAX_SESSION_MS`] で打ち切った。**
        ///
        /// ★ **この区別が無いと計器が嘘をつく**: 打ち切りで出た `dwell_ms` は
        /// 「候補を眺めていた時間」ではなく**上限そのもの**なのに、
        /// ⚠️ NDJSON では本物の変換と**見分けがつかない 1 行**になる。
        /// → ★ `ime_dwell_med` が計器由来の値で汚れ、⚠️ 解析側に検知手段が無い
        /// (`ime_dwell_med` が別物を測っていた 2026-08-22 の失敗と同型)。
        ///
        /// ★ 呼び出し側は `forced` のとき **行を出さない** こと。
        /// ⚠️ 1 行失う方が、偽の dwell を 1 行足すより安全である。
        forced: bool,
    },
}

/// ⚠️★ **debounce の幅** —— この時間内に候補が戻ってきたら「同じ変換の続き」とみなす。
///
/// ★ **なぜ要るか**: 実測で `IME` クラスは **1 変換につき 2 周期** cloak/uncloak する
/// (`IME` 18 : 候補 UI 9 : ホストフレーム 9 = 2 : 1 : 1)。
/// ⚠️ そのまま流すと `ime_shadow` が **変換 1 回につき 2 行**出る。
///
/// # ⚠️★★★ 2026-08-23 の実測で **前提が変わった** (★ それでも残す理由)
///
/// ★ 実測 D (打鍵 257・変換 12 回) で、`IME` : 候補UI : ホストフレーム = 2 : 1 : 1 は
/// **「1 変換 = 2 周期」ではなかった**と分かった。
/// ⚠️ 正しくは **`IME` クラスの窓が 2 個あり、候補 UI・ホストフレームと
/// *同じミリ秒で同時に* cloak/uncloak している** (★ 4 窓が完全同期)。
/// → ★ 畳むべきは「連続 2 往復」ではなく **「窓の重なり」**であり、
/// それは [`CloakFold`] の **HWND 別の集合**が既に処理している。
///
/// ★ **したがって debounce の当初の存在理由は消えた。** ⚠️ それでも 0 にしないのは、
/// **1 変換の途中に出る短い明滅**を吸収するためである
/// (★ 別の計測で 116ms だけ見えて消える区間を観測している)。
///
/// # ★ 値の根拠 (⚠️ 勘で置いていない)
///
/// ★ 実測 D の**候補が隠れている区間 (= 変換と変換のあいだ)** の分布 (n=11):
///
/// ```text
/// 最小 = 308 ms / p10 = 345 ms / 中央 = 1185 ms
/// ```
///
/// ★ 同じ実データを**本番の [`CloakFold`] そのもの**に流した掃き出し:
///
/// | debounce | 行 | ⚠️ 判定 |
/// |---|---|---|
/// | 0〜250 ms | **12** | ★ 変換回数と一致 (★ どの値でも結果は同一) |
/// | 300 ms | 11 | ⚠️ **最小ギャップ 308ms を跨いで融合し始める** |
/// | 400 ms | 9 (+打切 1) | ⚠️ 明確に壊れる |
///
/// → ★ **150 ms を採る**: ⚠️ 観測された最小ギャップ 308ms に対し **約 2 倍の余裕**があり、
/// ★ かつ debounce 中は `IME_ACTIVE` が立ったままなので
/// **pause の水増しを 1 変換あたり 150ms に抑える** (250ms だと 12 変換で 3 秒)。
///
/// ⚠️ **1 台・1 名・60 秒の実測である。** ★ 被験者環境で再確認すること。
pub const FOLD_GAP_MS: u64 = 150;

/// ⚠️★★ **セッションの上限** —— これを超えたら取りこぼしとみなして強制終了する。
///
/// ★ `lib.rs` の IME Monitor にも safety valve があるが、
/// ⚠️ **あちらは `IME_ACTIVE` を戻すだけで、この状態機械の中身は直せない。**
/// → ★ 自分で治せるようにしておく (fail-open。⚠️ fail-stuck にしない)。
///
/// # ⚠️★★★ 2026-08-23: **6 秒 → 20 秒**（★ 6 秒は実データを切っていた）
///
/// ★ 当初は「候補ウィンドウ表示は 1 秒前後」という前提で 6 秒にした。
/// ⚠️ **実測でその前提が崩れた** —— この信号は**変換セッション全体**
/// (ローマ字入力〜確定) を覆う。★ 自然な打鍵 60 秒での区間長:
///
/// ```text
/// 6464 / 5714 / 5004 / 3456 / 6974 / 3279 / 1574 / 363 / 267 / 203 / 133 / 88 ms
/// ```
///
/// → ⚠️★★★ **6 秒だと 13 セッション中 3 本が打ち切られ、行が消えていた**（23%）。
/// ★ 打ち切りは行を出さない設計なので、⚠️ **静かにデータが減る**。
///
/// ★ 20 秒なら実測の最長 (6974ms) に対し十分な余裕がある。
/// ⚠️ pause を外した (`decisions.md` D-10) ので、長く立ちっぱなしでも推論は止まらない。
pub const MAX_SESSION_MS: u64 = 20_000;

/// ⚠️★★★ **`lib.rs` の IME Monitor が `IME_ACTIVE` を強制リセットする閾値 (ms)。**
///
/// ★ **この定数が唯一の持ち主である。** ⚠️ `lib.rs` 側は
/// `Duration::from_millis(MONITOR_SAFETY_VALVE_MS)` としてここから導出すること。
///
/// # ⚠️★★★ なぜ `pub(crate)` にしてあるのか (2026-08-23・cross-review HIGH)
///
/// ⚠️ 初版はここに**写しの private const** を置き、`lib.rs` 側には
/// `Duration::from_secs(25)` を**別途ハードコード**していた。
/// → ★ 下の静的表明は **同じファイル内の 2 定数を比べていただけ**で、
/// ⚠️★★★ **`lib.rs` の実値を 1 バイトも参照していなかった。**
/// ★ つまり `lib.rs` の `25` だけを将来動かすと、**ビルドは緑のまま不変条件が黙って破れる**。
/// → ★ 「コンパイル時に固定した」という主張が**ファイル間では成立していなかった**。
///
/// ⚠️ 公開して `lib.rs` に使わせることで、初めて**本当に cross-file の不変条件**になる。
pub(crate) const MONITOR_SAFETY_VALVE_MS: u64 = 25_000;

// ⚠️★★★ **コンパイル時に固定する。** ★ どちらかを動かした瞬間にビルドが落ちる。
//   ★ 揃えたり逆転させたりすると 1 変換で `ime_shadow` が 2 行出る
//   ([`MAX_SESSION_MS`] の doc を参照)。★ 100ms ポーリング + 配送遅延を吸収する余裕も要る。
const _: () = assert!(
    MAX_SESSION_MS + 1_000 <= MONITOR_SAFETY_VALVE_MS,
    "CloakFold の上限は lib.rs の safety valve より 1 秒以上内側でなければならない"
);

/// ⚠️★★★ **cloak/uncloak を「1 変換 = 1 セッション」へ畳む純粋な状態機械。**
///
/// # 2 段構えである理由
///
/// ★ 実測は「1 変換 = `IME` クラス 2 周期」までしか言っておらず、⚠️ その 2 周期が
/// **(a) 同じ窓の連続 2 往復** なのか **(b) 別々の窓の重なり** なのかを見ていない。
/// → ★ **どちらでも壊れないように両方入れる**:
///
/// 1. **HWND 別の集合** —— 集合が空でない間はセッション継続。★ (b) 重なりが 1 区間に融合する。
///    ⚠️ プローブが単一スロットで畳んでしまった問題 (引き継ぎ §2.4) の解でもある。
/// 2. **ギャップ debounce** ([`FOLD_GAP_MS`]) —— 空になっても即終了せず、
///    その時間内に埋まれば同一セッション。★ (a) 連続 2 往復が 1 行に畳まれる。
///
/// ⚠️★ **時刻に `0` を「無し」の番兵として使わない** —— `Option<u64>` で持つ。
/// ★ epoch ms なら実運用で 0 は来ないが、⚠️ **テストが t=0 から始めた瞬間に壊れる**
/// (2026-08-23 に実際に 5 本落ちた)。★ 型で表せるものを値で表さない。
#[derive(Debug)]
pub struct CloakFold {
    /// ★ いま「候補表示中」とみなしている窓。⚠️ HWND は**識別にしか使わない**。
    shown: BTreeSet<isize>,
    /// ★ セッション開始時刻。`None` = セッション無し。
    session_start_ms: Option<u64>,
    /// ★ 集合が空になった時刻。`None` = まだ空になっていない。debounce の起点。
    empty_since_ms: Option<u64>,
    /// ★ debounce の幅。★ 既定は [`FOLD_GAP_MS`]。
    ///
    /// ⚠️★ **可変にしてあるのは `examples/ime_winevent_probe.rs` が
    /// 実機の 1 回の計測で複数の値を掃くため**である
    /// (★ 定数を勘で決めず、同じ実データで比べて選ぶ)。
    /// ⚠️ **production は既定値しか使わない。**
    gap_ms: u64,
}

impl Default for CloakFold {
    fn default() -> Self {
        Self::with_gap(FOLD_GAP_MS)
    }
}

impl CloakFold {
    pub fn new() -> Self {
        Self::default()
    }

    /// ★ debounce 幅を指定して作る (⚠️ **較正用**。production は [`CloakFold::new`])。
    pub fn with_gap(gap_ms: u64) -> Self {
        Self {
            shown: BTreeSet::new(),
            session_start_ms: None,
            empty_since_ms: None,
            gap_ms,
        }
    }

    /// ★ 「いまセッション中か」= `IME_ACTIVE` が立つべきか。
    pub fn is_active(&self) -> bool {
        self.session_start_ms.is_some()
    }

    /// ★ cloak/uncloak が 1 件届いた。
    ///
    /// - `hwnd`: 窓の識別子 (⚠️ 保存も送出もしない)
    /// - `shown`: [`candidate_shown_from_cloak`] を通した結果
    pub fn on_event(&mut self, hwnd: isize, shown: bool, now_ms: u64) -> Option<FoldAction> {
        if shown {
            self.shown.insert(hwnd);
            // ★ 戻ってきたので debounce は取り消す。
            self.empty_since_ms = None;
            if self.session_start_ms.is_none() {
                self.session_start_ms = Some(now_ms);
                return Some(FoldAction::Begin(now_ms));
            }
            // ⚠️ 既にセッション中 = 同じ変換の続き。★ 行は増やさない。
            return None;
        }
        self.shown.remove(&hwnd);
        if self.shown.is_empty() && self.session_start_ms.is_some() && self.empty_since_ms.is_none()
        {
            // ⚠️ **ここではまだ終わらせない。** ★ debounce の起点を刻むだけ。
            self.empty_since_ms = Some(now_ms);
        }
        None
    }

    /// ★ 時間経過だけで起きる遷移 (debounce の満了 / セッション上限) を進める。
    ///
    /// ⚠️ resolver スレッドは受信の合間に**必ずこれを呼ぶ**こと。
    /// ★ 呼ばないと「最後の uncloak のあと二度とイベントが来ない」ケースで
    /// セッションが閉じない (= 永久 pause)。
    ///
    /// # ⚠️ 時計について (2026-08-23・cross-review)
    ///
    /// ⚠️ `now_ms` は呼び出し側が **wall-clock (`SystemTime`)** から渡している
    /// (★ `IME_COMPOSITION_START_MS` が epoch ms で NDJSON に載るため)。
    /// → ⚠️ **システム時計が巻き戻ると `MAX_SESSION_MS` の自己修復が効かなくなる。**
    /// ★ 最終防御は `lib.rs` の safety valve で、あちらは **monotonic な `Instant`** を
    /// 使っているので巻き戻りの影響を受けない ([`MONITOR_SAFETY_VALVE_MS`])。
    /// ★ 二重防御の**外側だけが monotonic** である、と理解しておくこと。
    pub fn on_tick(&mut self, now_ms: u64) -> Option<FoldAction> {
        let start = self.session_start_ms?;
        // ⚠️★ 上限超過は最優先。★ 取りこぼしても必ず自分で治る。
        if now_ms.saturating_sub(start) >= MAX_SESSION_MS {
            // ★ dwell は「空になった時刻まで」。空になっていないなら上限そのもの。
            let end = self.empty_since_ms.unwrap_or(now_ms);
            let dwell = end.saturating_sub(start);
            self.reset();
            // ⚠️★★★ **打ち切りであることを必ず伝える** (`FoldAction::End::forced` の doc)。
            return Some(FoldAction::End {
                dwell_ms: dwell,
                forced: true,
            });
        }
        if let Some(empty_since) = self.empty_since_ms {
            if self.shown.is_empty() && now_ms.saturating_sub(empty_since) >= self.gap_ms {
                // ★ dwell は **debounce の待ち時間を含めない** (候補が消えた時刻まで)。
                let dwell = empty_since.saturating_sub(start);
                self.reset();
                return Some(FoldAction::End {
                    dwell_ms: dwell,
                    forced: false,
                });
            }
        }
        None
    }

    fn reset(&mut self) {
        self.shown.clear();
        self.session_start_ms = None;
        self.empty_since_ms = None;
    }
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn cloak_class_matches_only_exact_ime() {
        assert!(is_ime_cloak_class("IME"));
    }

    /// ⚠️★★★ 汎用クラスを通さないことが本フィルタの存在意義である。
    #[test]
    fn cloak_class_rejects_generic_and_similar_classes() {
        // ★ 実測で同じ周期で cloak されるが、汎用なので使わない。
        assert!(
            !is_ime_cloak_class("Xaml_WindowedPopupClass"),
            "ツールチップ・メニュー・フライアウトと同じクラス → 誤検知する"
        );
        assert!(
            !is_ime_cloak_class("ApplicationFrameWindow"),
            "全 UWP のホストフレーム → 誤検知する"
        );
        // ★ 部分一致にしない (前方/後方に何か付いたら別物として扱う)。
        assert!(!is_ime_cloak_class("MSCTFIME UI"));
        assert!(!is_ime_cloak_class("IMEClass"));
        assert!(!is_ime_cloak_class("MyIME"));
        assert!(!is_ime_cloak_class("ime"));
        assert!(!is_ime_cloak_class(""));
    }

    /// ⚠️★★★ **辺の向きの回帰テスト。** ★ ここが実測で決めた向きの唯一の固定点。
    #[test]
    fn shown_means_not_cloaked() {
        assert!(
            candidate_shown_from_cloak(false),
            "DWM 逐語: cloaked=0 は「cloak されていない」= 描画されている"
        );
        assert!(
            !candidate_shown_from_cloak(true),
            "cloaked=1 は DWM が描画していない = 候補は見えていない"
        );
    }

    #[test]
    fn single_window_begin_then_end_after_gap() {
        let mut f = CloakFold::new();
        assert_eq!(f.on_event(1, true, 1_000), Some(FoldAction::Begin(1_000)));
        assert!(f.is_active());
        assert_eq!(f.on_event(1, false, 1_700), None, "★ 即座には終わらせない");
        assert_eq!(f.on_tick(1_700 + FOLD_GAP_MS - 1), None);
        assert_eq!(
            f.on_tick(1_700 + FOLD_GAP_MS),
            Some(FoldAction::End {
                dwell_ms: 700,
                forced: false
            }),
            "★ dwell は debounce の待ち時間を含めない"
        );
        assert!(!f.is_active());
    }

    /// ★ (a) 同じ窓が連続 2 往復するケース —— ⚠️ **1 行に畳まれること**。
    #[test]
    fn two_cycles_within_gap_fold_into_one_session() {
        let mut f = CloakFold::new();
        assert_eq!(f.on_event(1, true, 0), Some(FoldAction::Begin(0)));
        assert_eq!(f.on_event(1, false, 300), None);
        // ★ debounce 内に戻ってきた → 同じセッションの続き (Begin は出ない)。
        assert_eq!(f.on_tick(300 + FOLD_GAP_MS - 10), None);
        assert_eq!(f.on_event(1, true, 300 + FOLD_GAP_MS - 10), None);
        assert_eq!(f.on_event(1, false, 900), None);
        assert_eq!(
            f.on_tick(900 + FOLD_GAP_MS),
            Some(FoldAction::End {
                dwell_ms: 900,
                forced: false
            }),
            "★ 2 周期がまとめて 1 行 (dwell は最後に消えた時刻まで)"
        );
    }

    /// ★ (b) 別々の窓が重なるケース —— ⚠️ **1 区間に融合すること**。
    #[test]
    fn overlapping_windows_merge_into_one_session() {
        let mut f = CloakFold::new();
        assert_eq!(f.on_event(1, true, 0), Some(FoldAction::Begin(0)));
        assert_eq!(f.on_event(2, true, 100), None, "★ 2 個目で Begin は出ない");
        // ★ 1 個目が消えても、2 個目が残っている間は終わらない。
        assert_eq!(f.on_event(1, false, 400), None);
        assert_eq!(f.on_tick(400 + FOLD_GAP_MS + 100), None, "★ まだ空ではない");
        assert_eq!(f.on_event(2, false, 800), None);
        assert_eq!(
            f.on_tick(800 + FOLD_GAP_MS),
            Some(FoldAction::End {
                dwell_ms: 800,
                forced: false
            })
        );
    }

    /// ⚠️ debounce を**超えて**戻ってきたら別セッションになること。
    #[test]
    fn reentry_after_gap_starts_new_session() {
        let mut f = CloakFold::new();
        assert_eq!(f.on_event(1, true, 0), Some(FoldAction::Begin(0)));
        assert_eq!(f.on_event(1, false, 500), None);
        assert_eq!(
            f.on_tick(500 + FOLD_GAP_MS),
            Some(FoldAction::End {
                dwell_ms: 500,
                forced: false
            })
        );
        let t = 500 + FOLD_GAP_MS + 1;
        assert_eq!(f.on_event(1, true, t), Some(FoldAction::Begin(t)));
    }

    /// ⚠️★★★ 取りこぼしても**自分で治る**こと (fail-stuck にしない)。
    #[test]
    fn session_self_heals_after_max_duration() {
        let mut f = CloakFold::new();
        assert_eq!(f.on_event(1, true, 0), Some(FoldAction::Begin(0)));
        // ★ uncloak が二度と来ない。
        assert_eq!(f.on_tick(MAX_SESSION_MS - 1), None);
        assert_eq!(
            f.on_tick(MAX_SESSION_MS),
            Some(FoldAction::End {
                dwell_ms: MAX_SESSION_MS,
                forced: true
            }),
            "⚠️★★★ 打ち切りは forced=true でなければならない (行を出させないため)"
        );
        assert!(!f.is_active(), "★ 上限で必ず解ける");
    }

    // -----------------------------------------------------------------------
    // ⚠️★★★ 実データ回帰 — 2026-08-23 の実測 D をそのまま流す
    // -----------------------------------------------------------------------

    /// ★ 2026-08-23 の実測 D で記録した **`IME` クラスの cloak/uncloak 列**。
    ///
    /// `(プローブ開始からの ms, 窓の連番, 見えているか)`。
    /// ★ 打鍵 257・日本語変換 12 回の 60 秒。⚠️ 窓が **2 個 (3 と 4)** あり、
    /// **同じミリ秒で同時に**動いているのが読み取れる (★ これが 2:1:1 の正体)。
    ///
    /// ⚠️ **privacy**: ★ 時刻・不透明な連番・bool だけ。打鍵内容もクラス名も含まない。
    const RECORDED_IME_EVENTS: &[(u64, isize, bool)] = &[
        (7180, 3, true),
        (7180, 4, true),
        (10521, 3, false),
        (10521, 4, false),
        (12904, 3, true),
        (12904, 4, true),
        (16142, 3, false),
        (16142, 4, false),
        (16487, 3, true),
        (16487, 4, true),
        (19516, 3, false),
        (19516, 4, false),
        (19824, 3, true),
        (19824, 4, true),
        (21114, 3, false),
        (21114, 4, false),
        (22337, 3, true),
        (22337, 4, true),
        (24298, 3, false),
        (24298, 4, false),
        (24649, 3, true),
        (24649, 4, true),
        (25669, 3, false),
        (25669, 4, false),
        (26854, 3, true),
        (26854, 4, true),
        (28926, 3, false),
        (28926, 4, false),
        (30536, 3, true),
        (30536, 4, true),
        (32454, 3, false),
        (32454, 4, false),
        (33172, 3, true),
        (33172, 4, true),
        (35585, 3, false),
        (35585, 4, false),
        (38172, 3, true),
        (38172, 4, true),
        (42272, 3, false),
        (42272, 4, false),
        (42873, 3, true),
        (42873, 4, true),
        (45194, 3, false),
        (45194, 4, false),
        (47580, 3, true),
        (47580, 4, true),
        (52129, 3, false),
        (52129, 4, false),
    ];

    /// ★ 本番の resolver と同じ刻み (`FOLD_GAP_MS/4+1`) で時間を進めながら流す。
    fn replay(gap_ms: u64) -> (Vec<u64>, u32) {
        let tick = gap_ms.max(1) / 4 + 1;
        let mut fold = CloakFold::with_gap(gap_ms);
        let mut dwells = Vec::new();
        let mut forced = 0u32;
        let mut sink = |a: FoldAction| match a {
            FoldAction::End {
                dwell_ms,
                forced: true,
            } => {
                let _ = dwell_ms;
                forced += 1;
            }
            FoldAction::End {
                dwell_ms,
                forced: false,
            } => dwells.push(dwell_ms),
            FoldAction::Begin(_) => {}
        };
        let mut clock = RECORDED_IME_EVENTS[0].0;
        for (t, hwnd, shown) in RECORDED_IME_EVENTS {
            while clock + tick <= *t {
                clock += tick;
                if let Some(a) = fold.on_tick(clock) {
                    sink(a);
                }
            }
            clock = *t;
            if let Some(a) = fold.on_event(*hwnd, *shown, *t) {
                sink(a);
            }
            if let Some(a) = fold.on_tick(*t) {
                sink(a);
            }
        }
        let last = RECORDED_IME_EVENTS[RECORDED_IME_EVENTS.len() - 1].0;
        while clock <= last + gap_ms + MAX_SESSION_MS {
            clock += tick;
            if let Some(a) = fold.on_tick(clock) {
                sink(a);
            }
        }
        (dwells, forced)
    }

    /// ⚠️★★★ **実データで「行数 = 変換回数」になること。**
    ///
    /// ★ 60 秒で日本語変換を **12 回**行った記録である。
    #[test]
    fn recorded_session_yields_one_row_per_conversion() {
        let (dwells, forced) = replay(FOLD_GAP_MS);
        assert_eq!(
            dwells.len(),
            12,
            "★ 実測の変換回数と一致しなければならない (得られた dwell: {dwells:?})"
        );
        assert_eq!(forced, 0, "⚠️ 実データで打ち切りが出てはならない");
        // ★ 明滅由来の極端に短い行が混じっていないこと。
        assert!(
            dwells.iter().all(|d| *d >= 300),
            "⚠️ 300ms 未満の行は明滅の取り込みを疑う: {dwells:?}"
        );
    }

    /// ⚠️★★★ **`FOLD_GAP_MS` を上げすぎると別々の変換が 1 行に融合すること**を固定する。
    ///
    /// ★ 実測の「候補が隠れている区間」の最小は **308ms** だった。
    /// → ⚠️ 300ms 以上にすると融合が始まる。★ この境界がテストで見えるようにしておく。
    #[test]
    fn too_large_a_debounce_merges_separate_conversions() {
        assert_eq!(replay(FOLD_GAP_MS).0.len(), 12, "★ 採用値では 12 行");
        assert!(
            replay(400).0.len() < 12,
            "⚠️ 400ms では融合が起きるはず (この境界が動いたら FOLD_GAP_MS の根拠を測り直す)"
        );
    }

    /// ⚠️ セッション外の uncloak で状態が壊れないこと。
    #[test]
    fn hide_without_session_is_ignored() {
        let mut f = CloakFold::new();
        assert_eq!(f.on_event(1, false, 100), None);
        assert!(!f.is_active());
        assert_eq!(f.on_tick(100_000), None, "★ 何も起きない");
    }

    /// ⚠️ 同じ窓の重複 shown で二重 Begin が出ないこと。
    #[test]
    fn duplicate_shown_does_not_double_begin() {
        let mut f = CloakFold::new();
        assert_eq!(f.on_event(1, true, 0), Some(FoldAction::Begin(0)));
        assert_eq!(f.on_event(1, true, 50), None);
        assert_eq!(f.on_event(1, false, 200), None);
        assert_eq!(
            f.on_tick(200 + FOLD_GAP_MS),
            Some(FoldAction::End {
                dwell_ms: 200,
                forced: false
            })
        );
    }
}
