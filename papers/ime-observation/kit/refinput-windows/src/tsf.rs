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
//! 構成: 純粋な状態遷移（`CompTracker` / `FocusTrackers` / `UiKinds`・COM を使わないので単体テストできる）と、
//! COM のシンク・登録（`Tsf`）。⚠️ 通ったこと ≠ 実 IME で通知が届くこと（M5 で確かめる）。

use std::cell::RefCell;
use std::rc::Rc;

use refinput_windows::{Ev, UiKind};
use windows::core::{implement, IUnknown, Interface, Result};
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

/// A single composition observation: (total length across all ranges, start offset of the
/// first range, number of ranges). Offsets are opaque integers, never text.
pub type CompObs = (u32, i64, usize);

/// Derives `tsf_start` / `tsf_update` / `tsf_end` from a stream of composition observations.
///
/// An edit is reported as an update for as long as a composition is present, even when its
/// length is unchanged. `result_len` on `tsf_end` is the length that remains committed to the
/// document (document end after the composition closed, minus the document end that excludes
/// the composition, both derived from the last known document end). A commit reports the
/// composition length, a cancellation reports zero; when either document end is unavailable,
/// `result_len` is omitted.
///
/// If the start offset or the range count changes while a composition is already active, the
/// new observation is treated as a different composition: a commit followed immediately by a
/// new composition can otherwise be collapsed into a single update by an edit notification that
/// only reports the current state, silently losing the boundary between the two.
#[derive(Debug, Default)]
pub struct CompTracker {
    active: bool,
    last_len: u32,
    /// Start offset and range count last observed while active.
    start: Option<i64>,
    count: usize,
    /// Document end at the last observation (includes any composition text).
    doc_end: Option<i64>,
}

impl CompTracker {
    pub fn is_active(&self) -> bool {
        self.active
    }

    /// `comp`: the current composition observation, or `None` if no composition is present.
    /// `doc_end`: the current document end offset, or `None` if it could not be read.
    pub fn observe(&mut self, comp: Option<CompObs>, doc_end: Option<i64>) -> Vec<Ev> {
        match (self.active, comp) {
            (false, None) => Vec::new(),
            (was_active, Some((len, start, count))) => {
                let mut out = Vec::with_capacity(3);
                let replaced = was_active && (self.start != Some(start) || self.count != count);
                if replaced {
                    // The start offset or range count changed while a composition was open:
                    // this observation belongs to a different composition than the one that was
                    // active before. The document end in between the two is unknown, so
                    // `result_len` is omitted on this synthetic end.
                    out.push(Ev::TsfEnd { result_len: None });
                    out.push(Ev::TsfStart);
                } else if !was_active {
                    out.push(Ev::TsfStart);
                }
                self.active = true;
                self.last_len = len;
                self.start = Some(start);
                self.count = count;
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

    /// Forgets an open composition without writing an end event. Used only when its outcome is
    /// genuinely unknown (for example, when the whole registration is torn down at exit).
    pub fn reset(&mut self) {
        *self = CompTracker::default();
    }
}

/// Tracks composition state for several contexts concurrently, keyed by an opaque identifier
/// supplied by the caller. This lets an observer keep watching a context that just lost focus
/// until its own composition genuinely ends, instead of discarding it the moment focus moves
/// away, which would otherwise merge a real end-of-composition into the next context or drop it
/// entirely. Holds no platform-specific types, so it can be unit tested directly.
#[derive(Debug, Default)]
pub struct FocusTrackers<Id> {
    // (identifier, composition state machine, whether this entry already lost focus)
    entries: Vec<(Id, CompTracker, bool)>,
}

impl<Id: Copy + Eq> FocusTrackers<Id> {
    /// Records a focus change to `new` (`None` if nothing is focused now). Every existing entry
    /// is first marked as having lost focus; an entry with no open composition is then removed
    /// and its identifier returned, so the caller can release whatever registration backs it.
    /// An entry that still has an open composition is kept so its eventual end is still
    /// observed and reported. If `new` names an identifier that is still tracked, its
    /// lost-focus flag is cleared instead of creating a duplicate entry.
    pub fn focus_changed(&mut self, new: Option<Id>) -> Vec<Id> {
        for entry in self.entries.iter_mut() {
            entry.2 = true;
        }
        let mut removed = Vec::new();
        self.entries.retain(|(id, tracker, lost_focus)| {
            let drop_it = *lost_focus && !tracker.is_active();
            if drop_it {
                removed.push(*id);
            }
            !drop_it
        });
        if let Some(id) = new {
            match self.entries.iter_mut().find(|(i, _, _)| *i == id) {
                Some(entry) => entry.2 = false,
                None => self.entries.push((id, CompTracker::default(), false)),
            }
        }
        removed
    }

    /// Feeds an observation to the entry for `id`. Returns the events produced and whether the
    /// entry may now be released (it has lost focus and its composition just closed). Does
    /// nothing if `id` is not tracked.
    pub fn observe(
        &mut self,
        id: Id,
        comp: Option<CompObs>,
        doc_end: Option<i64>,
    ) -> (Vec<Ev>, bool) {
        let Some(entry) = self.entries.iter_mut().find(|(i, _, _)| *i == id) else {
            return (Vec::new(), false);
        };
        let events = entry.1.observe(comp, doc_end);
        let may_remove = entry.2 && !entry.1.is_active();
        (events, may_remove)
    }

    pub fn is_active(&self, id: Id) -> bool {
        self.entries
            .iter()
            .any(|(i, t, _)| *i == id && t.is_active())
    }

    pub fn remove(&mut self, id: Id) {
        self.entries.retain(|(i, _, _)| *i != id);
    }

    pub fn clear(&mut self) {
        self.entries.clear();
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

/// A stable identity for a context, derived from `IUnknown` per COM identity rules (querying
/// the same object for `IUnknown` always yields the same pointer). Used to route callbacks to
/// the right tracked entry without relying on an interface-specific pointer, which COM does not
/// guarantee to be stable across queries.
fn ctx_id(ctx: &ITfContext) -> Option<usize> {
    ctx.cast::<IUnknown>().ok().map(|u| u.as_raw() as usize)
}

/// Start offset and length (`cch`) of a range. Never reads its text; returns `(0, 0)` on
/// failure.
fn extent_of(range: &ITfRange) -> (i64, u32) {
    let Ok(acp) = range.cast::<ITfRangeACP>() else {
        return (0, 0);
    };
    let (mut start, mut cch) = (0i32, 0i32);
    // SAFETY: 出力先は有効な i32 へのポインタ。
    match unsafe { acp.GetExtent(&mut start, &mut cch) } {
        Ok(()) => (i64::from(start), u32::try_from(cch).unwrap_or(0)),
        Err(_) => (0, 0),
    }
}

/// The composition observation for a context: total length across all ranges, the start offset
/// of the first range, and the number of ranges. `None` if no composition is present.
fn composition_info(ctx: &ITfContext) -> Option<CompObs> {
    let comps = ctx.cast::<ITfContextComposition>().ok()?;
    // SAFETY: 引数なしの列挙の取得。
    let views = unsafe { comps.EnumCompositions() }.ok()?;
    let (mut total, mut count, mut first_start) = (0u32, 0usize, None::<i64>);
    // Bound the loop in case the enumerator misbehaves.
    for _ in 0..16 {
        let mut view = [None];
        let mut got = 0u32;
        // SAFETY: 長さ 1 のバッファと有効な u32 へのポインタ。
        if unsafe { views.Next(&mut view, &mut got) }.is_err() || got == 0 {
            break;
        }
        if let Some(Ok(range)) = view[0].take().map(|v| unsafe { v.GetRange() }) {
            let (start, cch) = extent_of(&range);
            if first_start.is_none() {
                first_start = Some(start);
            }
            total = total.saturating_add(cch);
            count += 1;
        }
    }
    (count > 0).then(|| (total, first_start.unwrap_or(0), count))
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

/// State shared by the sinks: the recording sink, the per-context composition trackers keyed by
/// `ctx_id`, and the registrations backing them. A registration is kept alive until the
/// `FocusTrackers` entry for the same identifier says it may be released (see `on_focus_change`
/// and `on_end_edit`), not simply whenever focus moves away.
struct Shared {
    rec: Recorder,
    trackers: RefCell<FocusTrackers<usize>>,
    /// identifier -> registered `ITfSource` and cookie, released by `unadvise`.
    sources: RefCell<Vec<(usize, ITfSource, u32)>>,
}

impl Shared {
    fn new(rec: Recorder) -> Self {
        Shared {
            rec,
            trackers: RefCell::new(FocusTrackers::default()),
            sources: RefCell::new(Vec::new()),
        }
    }

    /// Registers an edit sink on `ctx` and records its cookie for later release.
    fn attach(&self, ctx: &ITfContext, edit: &ITfTextEditSink) {
        let Some(id) = ctx_id(ctx) else { return };
        let Ok(source) = ctx.cast::<ITfSource>() else {
            return;
        };
        // SAFETY: `edit` は生きているシンク。cookie は `unadvise` で同じ `source` に返す。
        if let Ok(cookie) = unsafe { source.AdviseSink(&ITfTextEditSink::IID, edit) } {
            self.sources.borrow_mut().push((id, source, cookie));
        }
    }

    fn unadvise(&self, id: usize) {
        let entry = {
            let mut sources = self.sources.borrow_mut();
            sources
                .iter()
                .position(|(i, _, _)| *i == id)
                .map(|pos| sources.remove(pos))
        };
        if let Some((_, source, cookie)) = entry {
            // SAFETY: `attach` が受け取った cookie を同じ `ITfSource` に返す。
            let _ = unsafe { source.UnadviseSink(cookie) };
        }
    }

    /// Releases every registration and forgets all tracked compositions without reporting them,
    /// because no further notification will ever arrive to say how they ended.
    fn detach_all(&self) {
        let ids: Vec<usize> = self.sources.borrow().iter().map(|(i, _, _)| *i).collect();
        for id in ids {
            self.unadvise(id);
        }
        self.trackers.borrow_mut().clear();
    }

    /// Handles a focus change: a context that lost focus and has no open composition is
    /// released immediately; one that still has an open composition stays registered until it
    /// is observed to end on its own. The newly focused context, if any, is registered.
    fn on_focus_change(&self, new_ctx: Option<&ITfContext>, edit: &ITfTextEditSink) {
        let new_id = new_ctx.and_then(ctx_id);
        let removed = self.trackers.borrow_mut().focus_changed(new_id);
        for id in removed {
            self.unadvise(id);
        }
        if let Some(ctx) = new_ctx {
            self.attach(ctx, edit);
        }
    }

    /// Handles `OnEndEdit` for `ctx`: derives the composition observation, feeds it to that
    /// context's tracker, records the resulting events, and releases the context once it has
    /// both lost focus and closed its composition.
    fn on_end_edit(&self, ctx: &ITfContext, ec: u32) {
        let Some(id) = ctx_id(ctx) else { return };
        let comp = composition_info(ctx);
        let was_active = self.trackers.borrow().is_active(id);
        let end = if comp.is_some() || was_active {
            doc_end(ctx, ec)
        } else {
            None
        };
        let (events, may_remove) = self.trackers.borrow_mut().observe(id, comp, end);
        for ev in events {
            (self.rec)(ev);
        }
        if may_remove {
            self.trackers.borrow_mut().remove(id);
            self.unadvise(id);
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
        if let Some(ctx) = pic {
            self.sh.on_end_edit(ctx, ecreadonly);
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
        let ctx = match pdimfocus {
            // SAFETY: フォーカスを得たドキュメントの最上位のコンテキストを取る。
            Some(dim) => unsafe { dim.GetTop() }.ok(),
            None => None,
        };
        self.sh.on_focus_change(ctx.as_ref(), &self.edit);
        (self.sh.rec)(if pdimfocus.is_some() {
            Ev::FocusIn
        } else {
            Ev::FocusOut
        });
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

            let sh = Rc::new(Shared::new(rec.clone()));
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
            let ui_cookie = match source.AdviseSink(&ITfUIElementSink::IID, &ui_sink) {
                Ok(cookie) => cookie,
                Err(err) => {
                    // Undo the first registration rather than leaking it if the second fails.
                    let _ = source.UnadviseSink(thread_cookie);
                    return Err(err);
                }
            };
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
        self.sh.detach_all();
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

    // ---- CompTracker ----------------------------------------------------------------------------

    #[test]
    fn a_commit_keeps_the_composition_length_as_the_result() {
        let mut t = CompTracker::default();
        // The document already has 2 characters; a 1-character composition starts at offset 2.
        assert_eq!(
            t.observe(Some((1, 2, 1)), Some(3)),
            vec![Ev::TsfStart, Ev::TsfUpdate { len: 1 }]
        );
        assert!(t.is_active());
        assert_eq!(
            t.observe(Some((3, 2, 1)), Some(5)),
            vec![Ev::TsfUpdate { len: 3 }]
        );
        // Commit: the composition disappears, its text stays in the document (end still 5).
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
        t.observe(Some((3, 2, 1)), Some(5));
        // Cancel: the composition's text also disappears from the document (5 -> 2).
        assert_eq!(
            t.observe(None, Some(2)),
            vec![Ev::TsfEnd {
                result_len: Some(0)
            }]
        );
    }

    #[test]
    fn a_commit_that_shrinks_the_text_reports_the_remaining_length() {
        // 3 characters converted and committed as 2 (document end 5 -> 4).
        let mut t = CompTracker::default();
        t.observe(Some((3, 2, 1)), Some(5));
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
        t.observe(Some((3, 0, 1)), None);
        assert_eq!(
            t.observe(None, Some(5)),
            vec![Ev::TsfEnd { result_len: None }]
        );
        let mut t = CompTracker::default();
        t.observe(Some((3, 0, 1)), Some(5));
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
        t.observe(Some((2, 0, 1)), Some(2));
        assert_eq!(
            t.observe(Some((2, 0, 1)), Some(2)),
            vec![Ev::TsfUpdate { len: 2 }]
        );
    }

    #[test]
    fn a_result_never_underflows_or_overflows() {
        let mut t = CompTracker::default();
        t.observe(Some((3, 0, 1)), Some(3));
        // The document shrinking past zero must not go negative.
        assert_eq!(
            t.observe(None, Some(-5)),
            vec![Ev::TsfEnd {
                result_len: Some(0)
            }]
        );
        let mut t = CompTracker::default();
        t.observe(Some((0, 0, 1)), Some(0));
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
        t.observe(Some((2, 0, 1)), Some(2));
        t.reset();
        assert!(!t.is_active());
        // Nothing is written for a composition that was forgotten, even once it disappears.
        assert!(t.observe(None, Some(2)).is_empty());
        // The next composition starts fresh.
        assert_eq!(
            t.observe(Some((1, 2, 1)), Some(3)),
            vec![Ev::TsfStart, Ev::TsfUpdate { len: 1 }]
        );
    }

    #[test]
    fn a_commit_immediately_followed_by_a_new_composition_at_a_different_offset_splits_into_end_and_start(
    ) {
        let mut t = CompTracker::default();
        assert_eq!(
            t.observe(Some((2, 0, 1)), Some(2)),
            vec![Ev::TsfStart, Ev::TsfUpdate { len: 2 }]
        );
        // Within a single edit notification: the first composition committed, and a second one
        // started at a different offset. The changed start offset signals a new composition.
        assert_eq!(
            t.observe(Some((1, 5, 1)), Some(6)),
            vec![
                Ev::TsfEnd { result_len: None },
                Ev::TsfStart,
                Ev::TsfUpdate { len: 1 }
            ]
        );
        assert!(t.is_active());
    }

    #[test]
    fn a_change_in_the_range_count_also_splits_into_end_and_start() {
        let mut t = CompTracker::default();
        t.observe(Some((2, 0, 1)), Some(2));
        // Same offset, but the range count changed from 1 to 2: still treated as a new
        // composition rather than a continuation of the same one.
        assert_eq!(
            t.observe(Some((3, 0, 2)), Some(3)),
            vec![
                Ev::TsfEnd { result_len: None },
                Ev::TsfStart,
                Ev::TsfUpdate { len: 3 }
            ]
        );
    }

    #[test]
    fn continuing_at_the_same_offset_and_range_count_is_a_plain_update() {
        let mut t = CompTracker::default();
        t.observe(Some((1, 0, 1)), Some(1));
        assert_eq!(
            t.observe(Some((4, 0, 1)), Some(4)),
            vec![Ev::TsfUpdate { len: 4 }]
        );
    }

    // ---- FocusTrackers --------------------------------------------------------------------------

    #[test]
    fn a_composition_that_outlives_a_focus_change_still_reports_exactly_one_end() {
        let mut ft: FocusTrackers<i32> = FocusTrackers::default();
        assert!(ft.focus_changed(Some(1)).is_empty());
        let (evs, may_remove) = ft.observe(1, Some((2, 0, 1)), Some(2));
        assert_eq!(evs, vec![Ev::TsfStart, Ev::TsfUpdate { len: 2 }]);
        assert!(!may_remove);

        // Focus moves to a different context while 1's composition is still open: it must not
        // be dropped or forced closed.
        assert!(ft.focus_changed(Some(2)).is_empty());
        assert!(ft.is_active(1));

        // The old context's own composition now ends.
        let (evs, may_remove) = ft.observe(1, None, Some(2));
        assert_eq!(
            evs,
            vec![Ev::TsfEnd {
                result_len: Some(2)
            }]
        );
        assert!(may_remove);
        ft.remove(1);
        assert!(!ft.is_active(1));
    }

    #[test]
    fn a_new_composition_starting_before_the_old_one_ends_keeps_them_separate() {
        let mut ft: FocusTrackers<i32> = FocusTrackers::default();
        ft.focus_changed(Some(1));
        ft.observe(1, Some((1, 0, 1)), Some(1));
        ft.focus_changed(Some(2));

        // A composition starts in the newly focused context; it is a separate state machine
        // from context 1's still-open composition.
        let (evs, _) = ft.observe(2, Some((3, 0, 1)), Some(3));
        assert_eq!(evs, vec![Ev::TsfStart, Ev::TsfUpdate { len: 3 }]);

        // Context 1's composition finally ends on its own, unaffected by context 2.
        let (evs, may_remove) = ft.observe(1, None, Some(1));
        assert_eq!(
            evs,
            vec![Ev::TsfEnd {
                result_len: Some(1)
            }]
        );
        assert!(may_remove);
    }

    #[test]
    fn an_entry_with_no_open_composition_is_removed_as_soon_as_focus_leaves() {
        let mut ft: FocusTrackers<i32> = FocusTrackers::default();
        ft.focus_changed(Some(1));
        // No composition was ever observed for 1, so moving focus away removes it immediately.
        let removed = ft.focus_changed(Some(2));
        assert_eq!(removed, vec![1]);
    }

    #[test]
    fn focus_returning_to_a_still_open_context_clears_its_lost_focus_flag() {
        let mut ft: FocusTrackers<i32> = FocusTrackers::default();
        ft.focus_changed(Some(1));
        ft.observe(1, Some((1, 0, 1)), Some(1));
        ft.focus_changed(Some(2));
        // Focus returns to 1 while its composition is still open. Context 2 never had a
        // composition, so it is released now that it has lost focus in turn.
        assert_eq!(ft.focus_changed(Some(1)), vec![2]);
        // Now that 1 is focused again, its own end must not be treated as removable.
        let (evs, may_remove) = ft.observe(1, None, Some(1));
        assert_eq!(
            evs,
            vec![Ev::TsfEnd {
                result_len: Some(1)
            }]
        );
        assert!(!may_remove);
    }

    // ---- UiKinds --------------------------------------------------------------------------------

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
