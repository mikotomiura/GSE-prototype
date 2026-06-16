import React, { useState } from "react";
import { invoke } from "@tauri-apps/api/core";
import type { ExpectedQuadrant } from "../probeTypes";

interface VignetteTestProps {
  onComplete: () => void;
}

interface Vignette {
  id: string;
  quadrant: ExpectedQuadrant;
  text: string;
}

// v0.3 §6.3 の 8 シナリオ (2×2 象限 ×2)。場面文は表示のみで **ログには送らない**
// (記録は vignette_id + expected_quadrant + q1/q2 のみ。data-privacy)。
const VIGNETTES: Vignette[] = [
  { id: "v1", quadrant: "flow", text: "言葉が次々浮かび、手が止まらずスラスラ書けている。" },
  { id: "v2", quadrant: "flow", text: "考えなくても文章が出てくる。詰まる感じはなく、どんどん進む。" },
  { id: "v3", quadrant: "stuck", text: "同じ一文を何度も消しては書き直し、まったく前に進まない。" },
  { id: "v4", quadrant: "stuck", text: "何を書けばいいか分からず、カーソルが点滅したまま手が止まる。" },
  { id: "v5", quadrant: "incubation", text: "難しい論点でうんうん唸っているが、少しずつ筋が見えて前進している感覚はある。" },
  { id: "v6", quadrant: "incubation", text: "言い回しに悩んで何度も書き直しているが、確実に良くなっていて手応えがある。" },
  { id: "v7", quadrant: "idle", text: "特に詰まってもいないが、ぼんやりして手も動かず、何も進んでいない。" },
  { id: "v8", quadrant: "idle", text: "楽な作業を惰性で触っているだけで、苦労はないが前進もしていない。" },
];

// client-side フィードバック専用の象限推論 (権威的採点は Task D)。
// 端 (1-2 / 4-5) のみを採り、3 は曖昧として不一致扱いにする。
function inferQuadrant(q1: number, q2: number): ExpectedQuadrant | null {
  const fHigh = q1 >= 4;
  const fLow = q1 <= 2;
  const pHigh = q2 >= 4;
  const pLow = q2 <= 2;
  if (fLow && pHigh) return "flow";
  if (fHigh && pLow) return "stuck";
  if (fHigh && pHigh) return "incubation";
  if (fLow && pLow) return "idle";
  return null;
}

/// v0.3 尺度理解テスト (Task C / §6)。8 ビネットに Q1摩擦/Q2前進 を回答 → vignette_response。
/// 完了後に PreReg-1 ゲート (6/8 想定象限) の結果を**表示のみ**で示す。
const VignetteTest: React.FC<VignetteTestProps> = ({ onComplete }) => {
  const [index, setIndex] = useState(0);
  const [q1, setQ1] = useState(3);
  const [q2, setQ2] = useState(3);
  const [matches, setMatches] = useState(0);
  const [done, setDone] = useState(false);

  const next = async () => {
    const v = VIGNETTES[index];
    // 記録成功後にのみ次へ進む (失敗時は留まり再送可能に・データ欠損回避)。
    try {
      await invoke("record_vignette_response", {
        vignetteId: v.id,
        expectedQuadrant: v.quadrant,
        q1Friction: q1,
        q2Progress: q2,
      });
    } catch (e) {
      console.error("record_vignette_response failed (not advancing):", e);
      return;
    }

    if (inferQuadrant(q1, q2) === v.quadrant) {
      setMatches((m) => m + 1);
    }
    setQ1(3);
    setQ2(3);
    if (index + 1 >= VIGNETTES.length) {
      setDone(true);
    } else {
      setIndex(index + 1);
    }
  };

  const slider = (
    label: string,
    value: number,
    setValue: (v: number) => void,
    lowLabel: string,
    highLabel: string
  ) => (
    <div style={{ margin: "0.6rem 0" }}>
      <div style={{ fontSize: "0.85rem", marginBottom: "0.2rem" }}>{label}</div>
      <input
        type="range"
        min={1}
        max={5}
        step={1}
        value={value}
        onChange={(e) => setValue(Number(e.target.value))}
        style={{ width: "100%" }}
      />
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.72rem", opacity: 0.7 }}>
        <span>{lowLabel}</span>
        <strong style={{ opacity: 1 }}>{value}</strong>
        <span>{highLabel}</span>
      </div>
    </div>
  );

  if (done) {
    const passed = matches >= 6;
    return (
      <div className="start-screen" style={{ textAlign: "center" }}>
        <h2>尺度理解テスト 結果</h2>
        <p style={{ fontSize: "1.1rem" }}>
          {matches} / {VIGNETTES.length} が想定どおり
        </p>
        <p style={{ color: passed ? "#4caf50" : "#ff9800" }}>
          {passed
            ? "合格 (PreReg-1: 6/8 以上)。本番に進めます。"
            : "6/8 未満。教示文を見直して再度受けることを推奨します。"}
        </p>
        <button className="start-button" onClick={onComplete}>
          閉じる
        </button>
      </div>
    );
  }

  const v = VIGNETTES[index];
  return (
    <div className="start-screen" style={{ maxWidth: "560px", margin: "0 auto" }}>
      <h2>尺度理解テスト ({index + 1} / {VIGNETTES.length})</h2>
      <p style={{ fontSize: "0.8rem", opacity: 0.7 }}>
        次の場面を読み、その瞬間の感覚として Q1 / Q2 を答えてください。Q1 と Q2 は独立した2軸です
        (詰まりながら進んでいる、も正当です)。
      </p>
      <blockquote
        style={{
          background: "rgba(0,0,0,0.06)",
          borderLeft: "3px solid #888",
          padding: "0.8rem 1rem",
          margin: "1rem 0",
          fontSize: "1rem",
        }}
      >
        {v.text}
      </blockquote>
      {slider("Q1. どれだけ詰まっていた感覚?", q1, setQ1, "詰まってない", "とても詰まった")}
      {slider("Q2. どれだけ前に進んでいる感覚?", q2, setQ2, "進んでない", "とても進んだ")}
      <button className="start-button" onClick={next} style={{ marginTop: "1rem" }}>
        {index + 1 >= VIGNETTES.length ? "完了" : "次へ"}
      </button>
    </div>
  );
};

export default VignetteTest;
