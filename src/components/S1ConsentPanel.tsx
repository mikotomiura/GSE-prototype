import React, { useCallback, useEffect, useState } from "react";
import { invoke } from "@tauri-apps/api/core";
import type { S1AnswerKeys, S1ModeDto } from "../probeTypes";

/**
 * 直前の30秒の問いの答え方（ADR-057）。★ 優先の規則はカードから外し、ここで先に説明する（ADR-055 D2 の一文）。
 * `modifier` はキーの名前（macOS "⌥"・Windows "Ctrl＋Alt"）。
 */
const HowToAnswer: React.FC<{ modifier: string }> = ({ modifier }) => {
  // ★ 1 文字の記号（⌥）は数字に付け、名前（Ctrl＋Alt）は「＋」でつなぐ（カードの表示と同じ）
  const key = (d: number) => (modifier.length === 1 ? `${modifier}${d}` : `${modifier}＋${d}`);
  return (
    <ul style={{ fontSize: "0.85em", margin: "0.4rem 0", paddingLeft: "1.2em", lineHeight: 1.5 }}>
      <li>
        ボタンを 1 回押すか、{modifier}＋数字（例: {key(1)}）を押せば答えになります。キーは問いが出てから 2 分のあいだだけ使い、作業中の文書には入りません。2 分を過ぎたらボタンで答えます。
        {key(0)} で閉じます。
      </li>
      <li>
        何をしていたかは、いくつか当てはまるときはいちばん長かったものを選びます。同時にしていたときは、詰まっていたなら「詰まり」、そうでなく手が動いていたなら「作業」を選びます。
      </li>
      <li>「詰まり」「熟考」「作業」を選んだときだけ、続けて詰まりと前進の感覚を 1〜5 で尋ねます。</li>
    </ul>
  );
};

/**
 * 段 1 の問いへの本人の同意と取り消し（ADR-043 D7・本タスクの decisions 判断 2）。
 * ★ 段 1 でなければ何も出さない。同意の前は問いが出ない（行も 0）。取り消すと以後の行は 0。
 */
const S1ConsentPanel: React.FC = () => {
  const [mode, setMode] = useState<S1ModeDto | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [modifier, setModifier] = useState<string | null>(null);

  useEffect(() => {
    invoke<S1AnswerKeys>("get_s1_answer_keys")
      .then((k) => setModifier(k.modifier))
      .catch((e) => console.warn("get_s1_answer_keys failed:", e));
  }, []);

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
          {modifier && <HowToAnswer modifier={modifier} />}
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
            作業中にときどき「直前の30秒」に何をしていたかを尋ね（選んだものによっては、続けて詰まりと前進も尋ねます）、
            夕方に 1 日 1 回、その日の作業について 1 つ尋ねます。答えたくないときは閉じられます。
          </p>
          {modifier && <HowToAnswer modifier={modifier} />}
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
