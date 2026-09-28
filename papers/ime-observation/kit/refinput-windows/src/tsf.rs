//! 参照入力欄 Windows (b) TSF 直受け（Windows のみ・**自分のスレッドの TSF だけ**）。
//!
//! ⚠️★★★ 文字列を取得しない。composition の長さは `ITfRangeACP::GetExtent` の `cch`（UTF-16 のコード単位数）だけで、
//! 範囲の本文を読む API は呼ばない。他プロセス・他スレッドの TSF は見ない（`ITfThreadMgr::Activate` は
//! 呼んだスレッドの TSF だけを起こす）。グローバルフック・WinEvent も使わない。
//!
//! ★ TSF の道: 道 1（RichEdit を載せ、フォーカス中のコンテキストの `ITfTextEditSink::OnEndEdit` で
//! `ITfContextComposition::EnumCompositions` を見て開始・更新・終了を判定する）。
//! 候補窓などは `ITfUIElementSink`。
//!
//! 構成: 純粋な状態遷移（`CompTracker` / `UiKinds`・COM を使わないので単体テストできる）と、COM のシンク・
//! 登録（`Tsf`）。⚠️ 通ったこと ≠ 実 IME で通知が届くこと（M5 で確かめる）。

use std::cell::RefCell;
use std::rc::Rc;

use refinput_windows::{Ev, UiKind};
use windows::core::{implement, Interface, Result};
use windows::Win32::Foundation::BOOL;
use windows::Win32::System::Com::{
    CoCreateInstance, CoInitializeEx, CoUninitialize, CLSCTX_INPROC_SERVER,
    COINIT_APARTMENTTHREADED,
};
use windows::Win32::UI::TextServices::{
    CLSID_TF_ThreadMgr, ITfCandidateListUIElement, ITfContext, ITfContextComposition,
    ITfDocumentMgr, ITfEditRecord, ITfRange, ITfRangeACP, ITfReadingInformationUIElement,
    ITfSource, ITfTextEditSink, ITfTextEditSink_Impl, ITfThreadMgr, ITfThreadMgrEventSink,
    ITfThreadMgrEventSink_Impl, ITfUIElementMgr, ITfUIElementSink, ITfUIElementSink_Impl,
};

/// 記録の出口（bin が渡す。事象を時刻つきで書く）。シンクは自分のスレッド（STA）でしか呼ばれない。
pub type Recorder = Rc<dyn Fn(Ev)>;

// ---- 純粋な状態遷移 ----------------------------------------------------------------------------

/// composition の観測（長さ・文書末）から `tsf_start` / `tsf_update` / `tsf_end` を導く。
///
/// ⚠️ 解釈しない: 編集が終わるたびに composition があれば `tsf_update` を書く（長さが同じでも書く）。
/// `tsf_end` の `result_len` は、composition の文字が文書に**残った**長さ
/// （= 終了後の文書末 − 直前まで composition を除いた文書の長さ）。確定なら composition の長さ、
/// 取消なら 0。⚠️ 文書末の位置が得られなかったときは `None`（省略）。
#[derive(Debug, Default)]
pub struct CompTracker {
    active: bool,
    last_len: u32,
    /// 直前の観測での文書末の位置（composition の文字を含む）
    doc_end: Option<i64>,
}

impl CompTracker {
    pub fn is_active(&self) -> bool {
        self.active
    }

    /// `comp_len`: 今の composition の長さの合計（無ければ `None`）。`doc_end`: 文書末の位置（分からなければ `None`）。
    pub fn observe(&mut self, comp_len: Option<u32>, doc_end: Option<i64>) -> Vec<Ev> {
        match (self.active, comp_len) {
            (false, None) => Vec::new(),
            (was_active, Some(len)) => {
                let mut out = Vec::with_capacity(2);
                if !was_active {
                    out.push(Ev::TsfStart);
                }
                self.active = true;
                self.last_len = len;
                self.doc_end = doc_end;
                out.push(Ev::TsfUpdate { len });
                out
            }
            (true, None) => {
                let result_len = match (self.doc_end, doc_end) {
                    (Some(before), Some(after)) => {
                        let without_comp = before - i64::from(self.last_len);
                        Some(u32::try_from((after - without_comp).max(0)).unwrap_or(u32::MAX))
                    }
                    _ => None,
                };
                self.reset();
                vec![Ev::TsfEnd { result_len }]
            }
        }
    }

    /// フォーカスが動いた・登録を外したときに、開いていた composition を**書かずに**忘れる
    /// （終わったかどうかが分からないものを、終わったと書かない）。
    pub fn reset(&mut self) {
        *self = CompTracker::default();
    }
}

/// UI 要素 ID → 種類（`BeginUIElement` で決め、`Update` / `End` で引く）。
#[derive(Debug, Default)]
pub struct UiKinds(Vec<(u32, UiKind)>);

impl UiKinds {
    /// `End` が来ないまま溜まっても増え続けないための上限。
    const CAP: usize = 64;

    pub fn begin(&mut self, id: u32, kind: UiKind) {
        self.0.retain(|(i, _)| *i != id);
        if self.0.len() >= Self::CAP {
            self.0.remove(0);
        }
        self.0.push((id, kind));
    }

    pub fn get(&self, id: u32) -> Option<UiKind> {
        self.0.iter().find(|(i, _)| *i == id).map(|(_, k)| *k)
    }

    pub fn end(&mut self, id: u32) -> Option<UiKind> {
        let kind = self.get(id);
        self.0.retain(|(i, _)| *i != id);
        kind
    }
}

// ---- TSF の呼び出し（unsafe はここに閉じる）----------------------------------------------------

/// 範囲の長さ（`cch`）だけ。⚠️ 本文は読まない。読めなければ 0。
fn cch_of(range: &ITfRange) -> u32 {
    let Ok(acp) = range.cast::<ITfRangeACP>() else {
        return 0;
    };
    let (mut start, mut cch) = (0i32, 0i32);
    // SAFETY: 出力先は有効な i32 へのポインタ。
    match unsafe { acp.GetExtent(&mut start, &mut cch) } {
        Ok(()) => u32::try_from(cch).unwrap_or(0),
        Err(_) => 0,
    }
}

/// コンテキストにある composition の長さの合計。composition が 1 つも無ければ `None`。
fn composition_len(ctx: &ITfContext) -> Option<u32> {
    let comps = ctx.cast::<ITfContextComposition>().ok()?;
    // SAFETY: 引数なしの列挙の取得。
    let views = unsafe { comps.EnumCompositions() }.ok()?;
    let (mut total, mut any) = (0u32, false);
    // ★ 列挙器が壊れていても止まるように、回数に上限を置く。
    for _ in 0..16 {
        let mut view = [None];
        let mut got = 0u32;
        // SAFETY: 長さ 1 のバッファと有効な u32 へのポインタ。
        if unsafe { views.Next(&mut view, &mut got) }.is_err() || got == 0 {
            break;
        }
        any = true;
        if let Some(Ok(range)) = view[0].take().map(|v| unsafe { v.GetRange() }) {
            total = total.saturating_add(cch_of(&range));
        }
    }
    any.then_some(total)
}

/// 文書末の位置（末尾で潰れた範囲の開始位置）。`ec` は `OnEndEdit` が渡す読み取り専用の cookie。
fn doc_end(ctx: &ITfContext, ec: u32) -> Option<i64> {
    // SAFETY: `ec` は `OnEndEdit` の呼び出しの間だけ有効で、その中でだけ使う。
    let range = unsafe { ctx.GetEnd(ec) }.ok()?;
    let acp = range.cast::<ITfRangeACP>().ok()?;
    let (mut start, mut cch) = (0i32, 0i32);
    // SAFETY: 出力先は有効な i32 へのポインタ。
    unsafe { acp.GetExtent(&mut start, &mut cch) }.ok()?;
    Some(i64::from(start) + i64::from(cch))
}

/// UI 要素の種類。`ITfCandidateListUIElement` なら候補、`ITfReadingInformationUIElement` なら読み、他は other。
fn ui_kind_of(mgr: &ITfUIElementMgr, id: u32) -> UiKind {
    // SAFETY: 要素の取得（ID は TSF が渡したもの）。
    let Ok(element) = (unsafe { mgr.GetUIElement(id) }) else {
        return UiKind::Other;
    };
    if element.cast::<ITfCandidateListUIElement>().is_ok() {
        UiKind::Candidate
    } else if element.cast::<ITfReadingInformationUIElement>().is_ok() {
        UiKind::Reading
    } else {
        UiKind::Other
    }
}

// ---- シンク ------------------------------------------------------------------------------------

/// 3 つのシンクで共有する状態。
struct Shared {
    rec: Recorder,
    tracker: RefCell<CompTracker>,
    /// `OnEndEdit` を受けている最中のコンテキスト（`ITfSource` と cookie）。
    attached: RefCell<Option<(ITfSource, u32)>>,
}

impl Shared {
    fn detach(&self) {
        if let Some((source, cookie)) = self.attached.borrow_mut().take() {
            // SAFETY: `attach` が受け取った cookie を、同じ `ITfSource` に返す。
            let _ = unsafe { source.UnadviseSink(cookie) };
        }
        self.tracker.borrow_mut().reset();
    }

    fn attach(&self, ctx: &ITfContext, edit: &ITfTextEditSink) {
        let Ok(source) = ctx.cast::<ITfSource>() else {
            return;
        };
        // SAFETY: `edit` は生きているシンク。cookie は `detach` で返す。
        if let Ok(cookie) = unsafe { source.AdviseSink(&ITfTextEditSink::IID, edit) } {
            *self.attached.borrow_mut() = Some((source, cookie));
        }
    }
}

/// コンテキストの編集の終わり（`OnEndEdit`）で composition の有無と長さを見る。
#[implement(ITfTextEditSink)]
struct EditSink {
    sh: Rc<Shared>,
}

impl ITfTextEditSink_Impl for EditSink_Impl {
    fn OnEndEdit(
        &self,
        pic: Option<&ITfContext>,
        ecreadonly: u32,
        _peditrecord: Option<&ITfEditRecord>,
    ) -> Result<()> {
        let Some(ctx) = pic else { return Ok(()) };
        let comp = composition_len(ctx);
        let end = if comp.is_some() || self.sh.tracker.borrow().is_active() {
            doc_end(ctx, ecreadonly)
        } else {
            None
        };
        let events = self.sh.tracker.borrow_mut().observe(comp, end);
        for ev in events {
            (self.sh.rec)(ev);
        }
        Ok(())
    }
}

/// フォーカス中のドキュメントが変わったら、`OnEndEdit` を受けるコンテキストを付け替える。
#[implement(ITfThreadMgrEventSink)]
struct ThreadSink {
    sh: Rc<Shared>,
    edit: ITfTextEditSink,
}

impl ITfThreadMgrEventSink_Impl for ThreadSink_Impl {
    fn OnInitDocumentMgr(&self, _pdim: Option<&ITfDocumentMgr>) -> Result<()> {
        Ok(())
    }
    fn OnUninitDocumentMgr(&self, _pdim: Option<&ITfDocumentMgr>) -> Result<()> {
        Ok(())
    }
    fn OnSetFocus(
        &self,
        pdimfocus: Option<&ITfDocumentMgr>,
        _pdimprevfocus: Option<&ITfDocumentMgr>,
    ) -> Result<()> {
        self.sh.detach();
        match pdimfocus {
            Some(dim) => {
                // SAFETY: フォーカスを得たドキュメントの最上位のコンテキストを取る。
                if let Ok(ctx) = unsafe { dim.GetTop() } {
                    self.sh.attach(&ctx, &self.edit);
                }
                (self.sh.rec)(Ev::FocusIn);
            }
            None => (self.sh.rec)(Ev::FocusOut),
        }
        Ok(())
    }
    fn OnPushContext(&self, _pic: Option<&ITfContext>) -> Result<()> {
        Ok(())
    }
    fn OnPopContext(&self, _pic: Option<&ITfContext>) -> Result<()> {
        Ok(())
    }
}

/// 候補窓・読み窓などの UI 要素の表示（`Begin` / `Update` / `End`）。
#[implement(ITfUIElementSink)]
struct UiSink {
    rec: Recorder,
    mgr: ITfUIElementMgr,
    kinds: RefCell<UiKinds>,
}

impl ITfUIElementSink_Impl for UiSink_Impl {
    fn BeginUIElement(&self, dwuielementid: u32, pbshow: *mut BOOL) -> Result<()> {
        // ★ 表示を奪わない: IME 自身の窓を出したままにする（TRUE = 出す）。
        if !pbshow.is_null() {
            // SAFETY: TSF が渡した BOOL の出力先（非 NULL を確かめた）。
            unsafe { *pbshow = BOOL(1) };
        }
        let kind = ui_kind_of(&self.mgr, dwuielementid);
        self.kinds.borrow_mut().begin(dwuielementid, kind);
        (self.rec)(Ev::UiBegin { kind });
        Ok(())
    }
    fn UpdateUIElement(&self, dwuielementid: u32) -> Result<()> {
        let known = self.kinds.borrow().get(dwuielementid);
        let kind = known.unwrap_or_else(|| ui_kind_of(&self.mgr, dwuielementid));
        (self.rec)(Ev::UiUpdate { kind });
        Ok(())
    }
    fn EndUIElement(&self, dwuielementid: u32) -> Result<()> {
        let known = self.kinds.borrow_mut().end(dwuielementid);
        // ⚠️ 終わった要素は問い合わせられないことがあるので、`Begin` で決めた種類を使う（知らなければ other）
        (self.rec)(Ev::UiEnd {
            kind: known.unwrap_or(UiKind::Other),
        });
        Ok(())
    }
}

// ---- 登録 --------------------------------------------------------------------------------------

/// このスレッドの TSF の登録一式。`start` で COM（STA）を起こしてシンクを登録し、`stop` で外す。
pub struct Tsf {
    mgr: ITfThreadMgr,
    source: ITfSource,
    thread_cookie: u32,
    ui_cookie: u32,
    sh: Rc<Shared>,
}

impl Tsf {
    /// ⚠️ 窓（RichEdit）を作る**前**に呼ぶ（フォーカスの通知を取りこぼさないため）。呼んだスレッドで
    /// メッセージループを回すこと。
    pub fn start(rec: Recorder) -> Result<Tsf> {
        // SAFETY: このスレッドを STA にして、このスレッドの TSF を起こし、シンクを登録する。
        unsafe {
            CoInitializeEx(None, COINIT_APARTMENTTHREADED).ok()?;
            let mgr: ITfThreadMgr =
                CoCreateInstance(&CLSID_TF_ThreadMgr, None, CLSCTX_INPROC_SERVER)?;
            let _client_id = mgr.Activate()?;
            let source: ITfSource = mgr.cast()?;
            let ui_mgr: ITfUIElementMgr = mgr.cast()?;

            let sh = Rc::new(Shared {
                rec: rec.clone(),
                tracker: RefCell::new(CompTracker::default()),
                attached: RefCell::new(None),
            });
            let edit: ITfTextEditSink = EditSink { sh: sh.clone() }.into();
            let thread_sink: ITfThreadMgrEventSink = ThreadSink {
                sh: sh.clone(),
                edit,
            }
            .into();
            let ui_sink: ITfUIElementSink = UiSink {
                rec,
                mgr: ui_mgr,
                kinds: RefCell::new(UiKinds::default()),
            }
            .into();
            let thread_cookie = source.AdviseSink(&ITfThreadMgrEventSink::IID, &thread_sink)?;
            let ui_cookie = source.AdviseSink(&ITfUIElementSink::IID, &ui_sink)?;
            Ok(Tsf {
                mgr,
                source,
                thread_cookie,
                ui_cookie,
                sh,
            })
        }
    }

    /// シンクを外し、TSF を止め、COM を閉じる（窓を壊した後に呼ぶ）。
    pub fn stop(self) {
        self.sh.detach();
        // SAFETY: `start` で得た cookie を同じ `ITfSource` に返し、`Activate` と対に `Deactivate` する。
        unsafe {
            let _ = self.source.UnadviseSink(self.ui_cookie);
            let _ = self.source.UnadviseSink(self.thread_cookie);
            let _ = self.mgr.Deactivate();
        }
        // ★ COM のインターフェースを全部手放してから閉じる。
        drop(self);
        // SAFETY: `start` の `CoInitializeEx` と対。
        unsafe { CoUninitialize() };
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn a_commit_keeps_the_composition_length_as_the_result() {
        let mut t = CompTracker::default();
        // 既に 2 文字ある文書に、composition 1 文字 → 3 文字
        assert_eq!(
            t.observe(Some(1), Some(3)),
            vec![Ev::TsfStart, Ev::TsfUpdate { len: 1 }]
        );
        assert!(t.is_active());
        assert_eq!(t.observe(Some(3), Some(5)), vec![Ev::TsfUpdate { len: 3 }]);
        // 確定: composition が消え、文字は文書に残る（文書末は 5 のまま）
        assert_eq!(
            t.observe(None, Some(5)),
            vec![Ev::TsfEnd {
                result_len: Some(3)
            }]
        );
        assert!(!t.is_active());
    }

    #[test]
    fn a_cancel_leaves_nothing_in_the_document() {
        let mut t = CompTracker::default();
        t.observe(Some(3), Some(5));
        // 取消: composition の文字も文書から消える（5 → 2）
        assert_eq!(
            t.observe(None, Some(2)),
            vec![Ev::TsfEnd {
                result_len: Some(0)
            }]
        );
    }

    #[test]
    fn a_commit_that_shrinks_the_text_reports_the_remaining_length() {
        // かな 3 文字 → 変換して 2 文字で確定（文書末 5 → 4）
        let mut t = CompTracker::default();
        t.observe(Some(3), Some(5));
        assert_eq!(
            t.observe(None, Some(4)),
            vec![Ev::TsfEnd {
                result_len: Some(2)
            }]
        );
    }

    #[test]
    fn an_unknown_document_end_omits_the_result_length() {
        let mut t = CompTracker::default();
        t.observe(Some(3), None);
        assert_eq!(
            t.observe(None, Some(5)),
            vec![Ev::TsfEnd { result_len: None }]
        );
        let mut t = CompTracker::default();
        t.observe(Some(3), Some(5));
        assert_eq!(t.observe(None, None), vec![Ev::TsfEnd { result_len: None }]);
    }

    #[test]
    fn nothing_is_written_without_a_composition() {
        let mut t = CompTracker::default();
        assert!(t.observe(None, Some(10)).is_empty());
        assert!(t.observe(None, None).is_empty());
        assert!(!t.is_active());
    }

    #[test]
    fn every_edit_during_a_composition_is_an_update_even_if_the_length_is_the_same() {
        let mut t = CompTracker::default();
        t.observe(Some(2), Some(2));
        assert_eq!(t.observe(Some(2), Some(2)), vec![Ev::TsfUpdate { len: 2 }]);
    }

    #[test]
    fn a_result_never_underflows_or_overflows() {
        let mut t = CompTracker::default();
        t.observe(Some(3), Some(3));
        // 文書が composition より小さくなっても負にならない
        assert_eq!(
            t.observe(None, Some(-5)),
            vec![Ev::TsfEnd {
                result_len: Some(0)
            }]
        );
        let mut t = CompTracker::default();
        t.observe(Some(0), Some(0));
        assert_eq!(
            t.observe(None, Some(i64::MAX)),
            vec![Ev::TsfEnd {
                result_len: Some(u32::MAX)
            }]
        );
    }

    #[test]
    fn reset_forgets_an_open_composition_without_writing_an_end() {
        let mut t = CompTracker::default();
        t.observe(Some(2), Some(2));
        t.reset();
        assert!(!t.is_active());
        // 忘れた後に composition が無くても `tsf_end` は出ない
        assert!(t.observe(None, Some(2)).is_empty());
        // 次の composition は新しく始まる
        assert_eq!(
            t.observe(Some(1), Some(3)),
            vec![Ev::TsfStart, Ev::TsfUpdate { len: 1 }]
        );
    }

    #[test]
    fn ui_kinds_are_remembered_from_begin_to_end() {
        let mut k = UiKinds::default();
        assert_eq!(k.get(7), None);
        k.begin(7, UiKind::Candidate);
        k.begin(8, UiKind::Reading);
        assert_eq!(k.get(7), Some(UiKind::Candidate));
        assert_eq!(k.end(7), Some(UiKind::Candidate));
        assert_eq!(k.get(7), None);
        assert_eq!(k.end(7), None);
        assert_eq!(k.get(8), Some(UiKind::Reading));
        // 同じ ID の Begin は種類を置き換える（重複しない）
        k.begin(8, UiKind::Other);
        assert_eq!(k.get(8), Some(UiKind::Other));
        assert_eq!(k.0.len(), 1);
    }

    #[test]
    fn ui_kinds_do_not_grow_without_bound() {
        let mut k = UiKinds::default();
        for id in 0..1000u32 {
            k.begin(id, UiKind::Other);
        }
        assert_eq!(k.0.len(), UiKinds::CAP);
        // 古いものから捨てる
        assert_eq!(k.get(0), None);
        assert_eq!(k.get(999), Some(UiKind::Other));
    }
}
