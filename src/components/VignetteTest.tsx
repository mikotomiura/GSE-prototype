import React, { useCallback, useEffect, useRef, useState } from "react";
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
// (記録は vignette_id + expected_quadrant + q1/q2 + 回答挙動メタのみ。data-privacy)。
//
// ⚠️ 場面文の制約 (`.steering/20260817-prereg1-scale-instructions/decisions.md` D-7):
//    Q1/Q2 のアンカー語 (詰ま / 進 / 引っかか / 近づ / 手応え / はかど / 停滞 / スラスラ) を
//    **使わない**。旧版は 8 問すべてが逐語ヒントを含み、尺度を理解していなくても
//    文字列マッチングで解けたため、理解度テストとして識別力が無かった。
//    → 場面は「観察できる行動 + 成果物の変化」だけで書く。
//    `scripts/check_vignettes.py` が禁止語と象限構成を機械検査する。
//
// ⚠️ 提示順は象限が連続しない固定順 (D-8): flow → stuck → incubation → idle の 2 巡。
//    旧版は同一象限が隣接していたため 2 問目が 1 問目の答えを写せた。
//    ランダム化は再現性 (reproducibility-discipline) と衝突するので採らない。
const VIGNETTES: Vignette[] = [
  {
    id: "v2f1",
    quadrant: "flow",
    text: "30 分のあいだ、ほとんど画面から目を離さずに打ち続けた。段落が 3 つ増え、書き直したのは 1 行だけだった。",
  },
  {
    id: "v2s1",
    quadrant: "stuck",
    text: "同じ一文を 10 分間、書いては消している。書き直すたびに、最初に書いた言い回しへ戻ってきてしまう。",
  },
  {
    id: "v2i1",
    quadrant: "incubation",
    text: "難しい論点で 10 分ほど手が止まった。そのあいだに構成の見取り図ができ、書き直した段落は前より短く強くなった。",
  },
  {
    id: "v2d1",
    quadrant: "idle",
    text: "参考文献の書式をそろえる作業を惰性で続けている。難しいところはないが、本文は 1 文字も増えていない。",
  },
  {
    id: "v2f2",
    quadrant: "flow",
    text: "頭の中にある順番のまま打てている。消したのは数えるほどで、下書きの残りは節ひとつになった。",
  },
  {
    id: "v2s2",
    quadrant: "stuck",
    text: "どう論を運べばよいのか決められないまま、カーソルが同じ行で点滅している。この 15 分で残ったのは見出しだけだ。",
  },
  {
    id: "v2i2",
    quadrant: "incubation",
    text: "反論の扱いに迷って何度も書き直しを重ねている。分量はむしろ減ったが、通して読むと筋が一本になった。",
  },
  {
    id: "v2d2",
    quadrant: "idle",
    text: "画面を眺めているだけで、何も打っていない。難しいところに当たったわけではなく、気持ちが向かないだけだ。",
  },
];

/// スライダー未操作時に表示する既定位置。**回答値ではない** (未操作は `*Touched === false`)。
const SLIDER_NEUTRAL = 3;

/// PreReg-1 の合格最小一致数。⚠️ **事前登録で凍結された値**であり変更禁止。
/// backend の `calibration_eval.rs::VIGNETTE_PASS_MIN` と同値でなければならない。
const VIGNETTE_PASS_MIN = 6;

/// `<input type="range">` が値を変えるキー。⚠️ **`Tab` を含めてはならない。**
/// `onKeyUp` は「キーを離した時点でフォーカスがある要素」で発火するため、
/// Tab で入ってきただけで keyup がスライダー上で起き、
/// **触っていないのに「3 を選んだ」ことになってしまう** (本改修の核心が無効化される)。
/// → keydown 側で、値を動かしうるキーだけを操作とみなす。
const RANGE_KEYS = new Set([
  "ArrowLeft",
  "ArrowRight",
  "ArrowUp",
  "ArrowDown",
  "Home",
  "End",
  "PageUp",
  "PageDown",
]);

/// `changes` は backend で `u16`。上限を超えると IPC のデシリアライズごと失敗し、
/// **被験者がその問から進めなくなる**ため frontend 側で飽和させる
/// (q1/q2 が `logger.rs` で clamp されているのと同じ方針)。
const MAX_CHANGES = 65535;

// client-side フィードバック専用の象限推論。権威的採点は backend
// (`calibration_eval.rs::infer_quadrant`) 側で、**同一規則**を持つ。
// 端 (1-2 / 4-5) のみを採り、3 は曖昧として不一致扱いにする。
//
// ⚠️ 3 を救う採点にはしない (D-6)。中点の逃げ場は教示文と「未操作では進めない」入力側で
//    塞ぐ。採点で 3 を救うと「想定象限を答えた」の意味が壊れるため。
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

/// 尺度の教示。ビネット提示前に 1 度読ませ、各問からも再表示できる。
///
/// ⚠️ 本文は `empirical-prompt-tuning` の実測で確定した版
/// (`.steering/20260817-prereg1-scale-instructions/tuning-log.md`)。
/// 文言を変えたら**必ず測り直す**こと。特に次の 2 つは実測で**入れると悪化した**ため入れない:
///   - 「6 問そろわなければ再施行します」→ 被験者が出題構成を推測して答えを配分し始める
///   - 「両方が高い場面も低い場面もあります」→ 同上 (4 通りが 2 問ずつだと推測させる)
const ScaleInstructions: React.FC = () => (
  <div style={{ textAlign: "left", fontSize: "0.86rem", lineHeight: 1.7 }}>
    <p>
      これから 8 つの場面を読み、それぞれについて 2 つの質問に答えてもらいます。
      あなたを評価するものではありません。2 つのものさしの説明が伝わっているかを
      確かめるためのものです。
    </p>

    <h3 style={{ fontSize: "0.95rem", marginBottom: "0.2rem" }}>
      Q1「どれだけ引っかかっていたか」
    </h3>
    <p style={{ margin: "0.2rem 0" }}>課題の難しさに、どれだけ足を取られていたかを答えてください。</p>
    <ul style={{ margin: "0.3rem 0", paddingLeft: "1.2rem" }}>
      <li>1 = まったく引っかからなかった</li>
      <li>2 = あまり引っかからなかった</li>
      <li>3 = どちらとも言えない</li>
      <li>4 = かなり引っかかった</li>
      <li>5 = 手も思考も奪われるほど引っかかった</li>
    </ul>
    <p style={{ margin: "0.2rem 0" }}>
      手が動いているかどうかは関係ありません。書いては消すのを繰り返している人も、
      画面を見たまま止まっている人も、どちらも強く引っかかっていることがあります。
      逆に、手が止まっていても引っかかってはいないことがあります。
    </p>

    <h3 style={{ fontSize: "0.95rem", marginBottom: "0.2rem" }}>
      Q2「作業がどれだけ仕上がりに近づいたか」
    </h3>
    <p style={{ margin: "0.2rem 0" }}>
      提出する文章の本文が、完成にどれだけ近づいたかを答えてください。
    </p>
    <ul style={{ margin: "0.3rem 0", paddingLeft: "1.2rem" }}>
      <li>1 = まったく近づかなかった</li>
      <li>2 = あまり近づかなかった</li>
      <li>3 = どちらとも言えない</li>
      <li>4 = かなり近づいた</li>
      <li>5 = 完成が見えるところまで近づいた</li>
    </ul>
    <p style={{ margin: "0.2rem 0" }}>
      打った量ではありません。手が止まっていても中身が近づくことはあり、
      打ち続けていても中身が近づかないことがあります。
      中身がよくなったのなら、書いた量が増えていなくても、減っていても、
      近づいたと数えてください。
    </p>

    <h3 style={{ fontSize: "0.95rem", marginBottom: "0.2rem" }}>
      Q1 と Q2 は別々のものさしです
    </h3>
    <p style={{ margin: "0.2rem 0" }}>
      一方が高いから他方が低い、とは限りません。次の 4 通りすべてが起こります。
    </p>
    <ul style={{ margin: "0.3rem 0", paddingLeft: "1.2rem" }}>
      <li>引っかからず、近づいた</li>
      <li>強く引っかかり、近づかなかった</li>
      <li>強く引っかかったが、それでも近づいた</li>
      <li>引っかかってはいないが、近づかなかった</li>
    </ul>

    <h3 style={{ fontSize: "0.95rem", marginBottom: "0.2rem" }}>答え方</h3>
    <p style={{ margin: "0.2rem 0" }}>
      8 つの場面は、Q1 と Q2 のそれぞれについて、高い側か低い側かがはっきりするように
      書いてあります。どちらとも言えないと感じたら、より近いほうへ振ってください。
    </p>
  </div>
);

/// v0.3 尺度理解テスト (Task C / §6)。8 ビネットに Q1摩擦/Q2前進 を回答 → vignette_response。
/// 完了後に PreReg-1 ゲート (6/8 想定象限) の結果を**表示のみ**で示す。
const VignetteTest: React.FC<VignetteTestProps> = ({ onComplete }) => {
  const [showIntro, setShowIntro] = useState(true);
  const [showHelp, setShowHelp] = useState(false);
  const [index, setIndex] = useState(0);
  // ⚠️ 「未操作」と「3 を選んだ」を分離する (D-6)。旧実装はスライダーを 3 で初期化して
  //    おり、`inferQuadrant` が 3 を必ず不一致に落とすため「一度も動かさなかった被験者は
  //    機械的に 0/8」になっていた。
  //
  //    値そのもの (`*Value`) と「答えたか」(`*Touched`) を**別の state に分ける**。
  //    値を `number | null` にして描画時に `?? 3` する作りだと、`onChange` の直後に
  //    `onPointerUp` が古いクロージャの `null` を読んだ場合に
  //    **被験者が選んだ値を既定値 3 で上書きしうる**。値を常に number に保てば、
  //    どちらの順序で発火しても被験者の入力が壊れない。
  const [q1Value, setQ1Value] = useState(SLIDER_NEUTRAL);
  const [q2Value, setQ2Value] = useState(SLIDER_NEUTRAL);
  const [q1Touched, setQ1Touched] = useState(false);
  const [q2Touched, setQ2Touched] = useState(false);
  const [matches, setMatches] = useState(0);
  const [done, setDone] = useState(false);
  const [submitting, setSubmitting] = useState(false); // 送信中フラグ (二重送信防止)
  const [error, setError] = useState<string | null>(null);
  // 回答挙動メタ (content-free)。場面表示からの経過と、スライダーの値変更回数。
  const shownAtRef = useRef<number>(0);
  const [changes, setChanges] = useState(0);

  // 場面が切り替わったら計測を張り直す (intro を閉じた直後の 1 問目も含む)。
  useEffect(() => {
    shownAtRef.current = performance.now();
  }, [index, showIntro]);

  /// スライダーに触れたことを記録する。
  /// `onChange` は値が実際に変わったときだけ発火するため、
  /// 「既定位置 (3) をそのまま選びたい」操作を取りこぼす。`onPointerUp` / `onKeyUp` で
  /// 触れたこと自体を確定させ、**未操作と 3 を選んだを分離**する。
  ///
  /// ⚠️ 値には触らない。値の確定は `onChange` だけが行う。
  const markTouched = useCallback((setTouched: (t: boolean) => void) => {
    setTouched(true);
  }, []);

  const answered = q1Touched && q2Touched;

  const next = async () => {
    if (submitting || !answered) return; // 二重送信・未回答での前進を防ぐ
    setSubmitting(true);
    setError(null);
    const v = VIGNETTES[index];
    const elapsedMs = Math.max(0, Math.round(performance.now() - shownAtRef.current));
    // 記録成功後にのみ次へ進む (失敗時は留まり再送可能に・データ欠損回避)。
    try {
      await invoke("record_vignette_response", {
        vignetteId: v.id,
        expectedQuadrant: v.quadrant,
        q1Friction: q1Value,
        q2Progress: q2Value,
        elapsedMs,
        changes,
      });
      if (inferQuadrant(q1Value, q2Value) === v.quadrant) {
        setMatches((m) => m + 1);
      }
      setQ1Value(SLIDER_NEUTRAL);
      setQ2Value(SLIDER_NEUTRAL);
      setQ1Touched(false);
      setQ2Touched(false);
      setChanges(0);
      setShowHelp(false);
      if (index + 1 >= VIGNETTES.length) {
        setDone(true);
      } else {
        setIndex(index + 1);
      }
    } catch (e) {
      console.error("record_vignette_response failed (not advancing):", e);
      setError("記録に失敗しました。もう一度お試しください。");
    } finally {
      setSubmitting(false);
    }
  };

  const slider = (
    label: string,
    value: number,
    touched: boolean,
    setValue: (v: number) => void,
    setTouched: (t: boolean) => void,
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
        onChange={(e) => {
          setValue(Number(e.target.value));
          setTouched(true);
          setChanges((c) => Math.min(MAX_CHANGES, c + 1));
        }}
        // 既定位置 (3) をそのまま選ぶ操作は値が変わらず `onChange` が発火しないので、
        // ポインタ/キー側で「触れた」ことを拾う。⚠️ 値には触らない。
        onPointerUp={() => markTouched(setTouched)}
        // タッチのスクロール割り込み等で pointerup が来ない経路を取りこぼさない。
        onPointerCancel={() => markTouched(setTouched)}
        // ⚠️ `onKeyUp` ではなく `onKeyDown`、かつ RANGE_KEYS に限定する (上記コメント参照)。
        onKeyDown={(e) => {
          if (RANGE_KEYS.has(e.key)) markTouched(setTouched);
        }}
        style={{ width: "100%", opacity: touched ? 1 : 0.45 }}
      />
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          fontSize: "0.72rem",
          opacity: 0.7,
        }}
      >
        <span>{lowLabel}</span>
        <strong style={{ opacity: 1 }}>{touched ? value : "未回答"}</strong>
        <span>{highLabel}</span>
      </div>
    </div>
  );

  // --- 教示画面 (ビネット提示前に 1 度) ---
  if (showIntro) {
    return (
      <div className="start-screen" style={{ maxWidth: "560px", margin: "0 auto" }}>
        <h2>尺度理解テスト</h2>
        <ScaleInstructions />
        <button
          className="start-button"
          onClick={() => setShowIntro(false)}
          style={{ marginTop: "1rem" }}
        >
          はじめる
        </button>
        <button className="back-button" onClick={onComplete} style={{ marginTop: "0.6rem" }}>
          ← 戻る (中断)
        </button>
      </div>
    );
  }

  // --- 結果画面 ---
  if (done) {
    // ⚠️ ここは**表示のみ**。権威的な合否は backend
    //    (`calibration_eval.rs::score_vignettes_internal`) が決める。
    const passed = matches >= VIGNETTE_PASS_MIN;
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
        {/* ⚠️ 反応性の打ち消し (D-6・法則 L5)。テスト側は「どちらか一方に寄せる」ことを
            求めるので、本番プローブへその癖を持ち越させない。省略しないこと。 */}
        <p
          style={{
            fontSize: "0.85rem",
            textAlign: "left",
            margin: "1rem auto",
            maxWidth: "460px",
            lineHeight: 1.7,
          }}
        >
          このテストはここまでです。
          <br />
          <strong>
            ここから先の本番のプローブでは、「どちらとも言えない」も正当な回答です。
          </strong>
          <br />
          無理にどちらかへ寄せないでください。
        </p>
        <button className="start-button" onClick={onComplete}>
          閉じる
        </button>
      </div>
    );
  }

  // --- ビネット提示画面 ---
  const v = VIGNETTES[index];
  return (
    <div className="start-screen" style={{ maxWidth: "560px", margin: "0 auto" }}>
      <h2>
        尺度理解テスト ({index + 1} / {VIGNETTES.length})
      </h2>
      <p style={{ fontSize: "0.8rem", opacity: 0.7 }}>
        次の場面を読み、その瞬間の感覚として Q1 / Q2 を答えてください。
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
      {slider(
        "Q1. どれだけ引っかかっていたか",
        q1Value,
        q1Touched,
        setQ1Value,
        setQ1Touched,
        "引っかからない",
        "強く引っかかった"
      )}
      {slider(
        "Q2. 本文がどれだけ仕上がりに近づいたか",
        q2Value,
        q2Touched,
        setQ2Value,
        setQ2Touched,
        "近づかない",
        "完成が見える"
      )}
      {!answered && (
        <p style={{ fontSize: "0.75rem", opacity: 0.7, margin: "0.4rem 0" }}>
          Q1 と Q2 の両方に答えると次へ進めます。
        </p>
      )}
      {error && (
        <p style={{ fontSize: "0.78rem", color: "#e53935", margin: "0.4rem 0" }}>{error}</p>
      )}
      <button
        className="start-button"
        onClick={next}
        disabled={submitting || !answered}
        style={{ marginTop: "1rem", opacity: answered ? 1 : 0.5 }}
      >
        {index + 1 >= VIGNETTES.length ? "完了" : "次へ"}
      </button>
      <button
        className="back-button"
        onClick={() => setShowHelp((s) => !s)}
        disabled={submitting}
        style={{ marginTop: "0.6rem", maxWidth: "560px" }}
      >
        {showHelp ? "説明を閉じる" : "ものさしの説明をもう一度見る"}
      </button>
      {showHelp && (
        <div
          style={{
            background: "rgba(0,0,0,0.04)",
            padding: "0.8rem 1rem",
            margin: "0.6rem 0",
            borderRadius: "4px",
          }}
        >
          <ScaleInstructions />
        </div>
      )}
      {/* テストを途中でやめてスタート画面に戻る導線。 */}
      <button
        className="back-button"
        onClick={onComplete}
        disabled={submitting}
        style={{ marginTop: "0.6rem", maxWidth: "560px" }}
      >
        ← 戻る (中断)
      </button>
    </div>
  );
};

export default VignetteTest;
