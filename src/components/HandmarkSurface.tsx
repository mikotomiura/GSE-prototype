// 手跡の案 A の小面の試作（spike・本線に入れない）。
// 打鍵のたびに印を約 120 ms 光らせる。数値・文字は描かない（親タスク判断 16）。
// 計測を有効にして起動したときだけ、描画の後の 2 つ目のフレームで遅れを Rust へ返す。
import { useEffect, useRef } from "react";
import { invoke } from "@tauri-apps/api/core";
import { getCurrentWebviewWindow } from "@tauri-apps/api/webviewWindow";

interface HandmarkKeyPayload {
  seq: number;
  t_key_ms: number;
  measure: boolean;
}

const FLASH_MS = 120;

export default function HandmarkSurface() {
  const markRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let unlisten: (() => void) | null = null;
    let disposed = false;

    getCurrentWebviewWindow()
      .listen<HandmarkKeyPayload>("handmark-key", (event) => {
        const mark = markRef.current;
        if (mark === null) {
          return;
        }
        // 変化中に次の打鍵が来たら打ち切って最初からやり直す（試作の判断 2）。
        mark.classList.remove("handmark-flash");
        void mark.offsetWidth;
        mark.classList.add("handmark-flash");

        const { seq, t_key_ms, measure } = event.payload;
        if (!measure) {
          return;
        }
        requestAnimationFrame(() => {
          requestAnimationFrame(() => {
            const latencyMs = Date.now() - t_key_ms;
            invoke("handmark_spike_latency", { seq, latencyMs }).catch(() => {
              // 計測の書き込みの失敗は小面の動作に影響させない。
            });
          });
        });
      })
      .then((fn) => {
        if (disposed) {
          fn();
        } else {
          unlisten = fn;
        }
      })
      .catch(() => {
        // listen に失敗したら小面は光らないだけで、他に影響させない。
      });

    return () => {
      disposed = true;
      if (unlisten !== null) {
        unlisten();
      }
    };
  }, []);

  return (
    <div
      style={{
        width: "100vw",
        height: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "transparent",
        pointerEvents: "none",
      }}
    >
      <style>{`
        .handmark-mark {
          width: 14px;
          height: 14px;
          border-radius: 50%;
          background: rgba(148, 163, 184, 0.35);
        }
        .handmark-flash {
          animation: handmark-flash ${FLASH_MS}ms ease-out;
        }
        @keyframes handmark-flash {
          from { background: rgba(226, 232, 240, 0.95); transform: scale(1.25); }
          to { background: rgba(148, 163, 184, 0.35); transform: scale(1); }
        }
      `}</style>
      <div ref={markRef} className="handmark-mark" />
    </div>
  );
}
