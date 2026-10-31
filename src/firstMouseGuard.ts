import { useEffect, useRef } from "react";
import { getCurrentWindow } from "@tauri-apps/api/window";

/** 窓が焦点を得た時刻と押し下げの時刻が、これより近ければ窓を前に出すクリックとみなす。 */
const NEAR_MS = 300;
/** Tauri の焦点の知らせは押し下げの後に届くことがあるので、判断をこれだけ遅らせる。 */
const DECIDE_DELAY_MS = 150;
/** これより古い押し下げの時刻は使わない（ボタンの外で離して click が来なかった押し下げなど）。 */
const STALE_POINTER_MS = 1000;

/**
 * 窓を前に出すつもりの 1 回目のクリックを、ボタンの押下として扱わないための見張り。
 *
 * ★ 主窓は `acceptFirstMouse: true`（`tauri.conf.json`）なので、macOS では前面にない窓への
 *   1 回目のクリックもボタンに届く。⚠️ 「すぐ止める」には要る（1 回で止まる約束）が、
 *   自己ラベルや G1 の「送信する」には、窓を前に出すクリックが混ざってはいけない
 *   (`.steering/20261031-pause-auto-resume/decisions.md` 判断 5・6)。
 *
 * ★ 窓が焦点を得た時刻（Tauri が知らせる OS の key window の変化）と押し下げの時刻が
 *   `NEAR_MS` 以内なら、そのクリックを捨てる。⚠️ 知らせは押し下げの前にも後にも届きうる
 *   （実機で約 1ms 後に届いた）ので、順序に頼らず、判断を `DECIDE_DELAY_MS` 遅らせて前後を見る。
 * ⚠️ `document.hasFocus()` と WebKit の `focus` イベントは使わない。窓を前に出すクリックの
 *   押し下げの時点で既に「焦点あり」を返した（2026-10-31 に実機で確かめた）。
 */
export function useFirstMouseGuard() {
  const focusedAt = useRef(Number.NEGATIVE_INFINITY);
  const pointerAt = useRef(Number.NEGATIVE_INFINITY);
  // ★ 判断待ちの間の 2 回目のクリックを予約しない（二重に送らない）。アンマウントで取り消す。
  const pendingTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    let unlisten: (() => void) | null = null;
    let cancelled = false;
    getCurrentWindow()
      .onFocusChanged(({ payload }) => {
        if (payload) focusedAt.current = Date.now();
      })
      .then((fn) => {
        if (cancelled) fn();
        else unlisten = fn;
      })
      .catch((e) => console.error("onFocusChanged failed:", e));
    return () => {
      cancelled = true;
      if (unlisten) unlisten();
      if (pendingTimer.current !== null) clearTimeout(pendingTimer.current);
      pendingTimer.current = null;
    };
  }, []);

  /** ボタンの `onPointerDown` に渡す。 */
  const onPointerDown = () => {
    pointerAt.current = Date.now();
  };

  /**
   * ボタンの `onClick` で、本来の処理を包んで呼ぶ。窓を前に出すクリックなら `action` を呼ばない。
   * ★ キーボードでの押下（押し下げが無い）は、焦点を得た時刻と離れているので通る。
   */
  const guardClick = (action: () => void) => {
    if (pendingTimer.current !== null) return;
    const at = pointerAt.current;
    // ★ 使ったら消す（後のキーボードでの押下が、古い押し下げの時刻で捨てられないように）。
    pointerAt.current = Number.NEGATIVE_INFINITY;
    // ★ 押し下げが無い・古い（キーボードでの押下など）なら、窓を前に出すクリックではない。
    const fromPointer = Number.isFinite(at) && Date.now() - at < STALE_POINTER_MS;
    pendingTimer.current = setTimeout(() => {
      pendingTimer.current = null;
      const firstMouse =
        fromPointer &&
        Number.isFinite(focusedAt.current) &&
        Math.abs(focusedAt.current - at) < NEAR_MS;
      if (!firstMouse) action();
    }, DECIDE_DELAY_MS);
  };

  return { onPointerDown, guardClick };
}
