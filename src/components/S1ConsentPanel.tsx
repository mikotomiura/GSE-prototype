import React, { useCallback, useEffect, useState } from "react";
import { invoke } from "@tauri-apps/api/core";
import type { S1ModeDto } from "../probeTypes";

/**
 * 段 1 の問いへの本人の同意と取り消し（ADR-043 D7・本タスクの decisions 判断 2）。
 * ★ 段 1 でなければ何も出さない。同意の前は問いが出ない（行も 0）。取り消すと以後の行は 0。
 */
const S1ConsentPanel: React.FC = () => {
  const [mode, setMode] = useState<S1ModeDto | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(() => {
    invoke<S1ModeDto>("get_s1_mode")
      .then(setMode)
      .catch((e) => console.warn("get_s1_mode failed:", e));
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  if (!mode?.s1) return null;

  const run = (command: string) => {
    setBusy(true);
    setError(null);
    invoke(command)
      .then(() => refresh())
      .catch((e) => setError(typeof e === "string" ? e : String(e)))
      .finally(() => setBusy(false));
  };

  return (
    <div
      style={{
        marginTop: "0.75rem",
        padding: "0.6rem 0.9rem",
        borderRadius: "6px",
        border: "1px solid rgba(255,255,255,0.25)",
      }}
    >
      <strong>画面に出る問い</strong>
      {mode.consent ? (
        <>
          <p style={{ fontSize: "0.9em", margin: "0.4rem 0" }}>
            問いに同意しています。作業中にときどき「直前の30秒」について尋ね、夕方に 1 日 1 回、その日の作業について尋ねます。
          </p>
          <p style={{ fontSize: "0.9em", margin: "0.4rem 0" }}>
            取り消すと、問いは出なくなります。記録そのもの（打鍵の時刻など）はこれまでどおり続きます。
          </p>
          <button type="button" onClick={() => run("revoke_s1_probe_consent")} disabled={busy}>
            問いへの同意を取り消す
          </button>
        </>
      ) : (
        <>
          <p style={{ fontSize: "0.9em", margin: "0.4rem 0" }}>
            作業中にときどき「直前の30秒」について 3 つ（詰まり・前進・何をしていたか）を尋ね、
            夕方に 1 日 1 回、その日の作業について 1 つ尋ねます。答えたくないときは閉じられます。
          </p>
          <p style={{ fontSize: "0.9em", margin: "0.4rem 0" }}>
            説明を受け、問いに同意される場合は「問いに同意する」を押してください。押されるまで問いは出ません。
          </p>
          <button type="button" onClick={() => run("acknowledge_s1_probe_consent")} disabled={busy}>
            問いに同意する
          </button>
        </>
      )}
      {error && (
        <p role="alert" style={{ color: "#ff6b6b", marginTop: "0.3rem" }}>
          {error}
        </p>
      )}
    </div>
  );
};

export default S1ConsentPanel;
