import React, { useCallback, useEffect, useState } from "react";
import { invoke } from "@tauri-apps/api/core";
import { listen } from "@tauri-apps/api/event";
import type { S1CardState } from "../probeTypes";
import S1ProbeCard from "./S1ProbeCard";
import DayQuestionCard from "./DayQuestionCard";

/** 取り直しの間隔（イベントを取りこぼしても、この間隔で backend の状態に戻る）。 */
const S1_CARD_POLL_MS = 5000;

interface S1CardHostProps {
  /** カードを出しているか（親が overlay の箱を出す）。 */
  onActiveChange: (active: boolean) => void;
  onResize: (size: { w: number; h: number } | null) => void;
}

/**
 * 段 1 のカードの受け手。★ どのカードを出すかは backend が決める（`get_s1_card` / `s1_card_state`）。
 * 日の問いを伏せて無作為の問いを出し、無作為が閉じたら日の問いに戻すのも backend の状態だけで決まる
 * （ここは伏せていることを知らない）。プローブと日の問いは同時に出ない。
 */
const S1CardHost: React.FC<S1CardHostProps> = ({ onActiveChange, onResize }) => {
  const [card, setCard] = useState<S1CardState>({ kind: "none" });

  const refresh = useCallback(() => {
    invoke<S1CardState>("get_s1_card")
      .then(setCard)
      // ⚠️ 読めないときは何も出さない（安全側・typescript-standards ルール 5）
      .catch((e) => console.warn("get_s1_card failed:", e));
  }, []);

  useEffect(() => {
    refresh();
    const unlisten = listen<S1CardState>("s1_card_state", (event) => setCard(event.payload));
    const onVisible = () => refresh();
    window.addEventListener("focus", onVisible);
    document.addEventListener("visibilitychange", onVisible);
    const t = setInterval(refresh, S1_CARD_POLL_MS);
    return () => {
      unlisten.then((f) => f());
      window.removeEventListener("focus", onVisible);
      document.removeEventListener("visibilitychange", onVisible);
      clearInterval(t);
    };
  }, [refresh]);

  useEffect(() => {
    onActiveChange(card.kind !== "none");
    if (card.kind === "none") onResize(null);
  }, [card, onActiveChange, onResize]);

  if (card.kind === "probe") {
    return (
      <S1ProbeCard
        key={card.probe_id}
        probeId={card.probe_id}
        step={card.step}
        onResize={onResize}
        onDone={refresh}
      />
    );
  }
  if (card.kind === "day") {
    return (
      <DayQuestionCard
        key={card.card_id}
        cardId={card.card_id}
        delayed={card.delayed}
        quitFlow={card.quit_flow}
        onResize={onResize}
        onDone={refresh}
      />
    );
  }
  return null;
};

export default S1CardHost;
