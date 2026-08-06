import { useEffect, useState, useMemo, useRef } from "react";
import { invoke } from "@tauri-apps/api/core";
import { getCurrentWindow } from "@tauri-apps/api/window";
import { listen } from "@tauri-apps/api/event";
import Dashboard from "./components/Dashboard";
import Overlay from "./components/Overlay";
import VignetteTest from "./components/VignetteTest";
import type { TaskKind } from "./probeTypes";
import "./App.css";

// Task C: session_meta の task_kind 宣言 (start 画面のセレクタ)。
// Phase1 ロック: 較正は **論述 (argumentative) に固定**する。非論述を混ぜると C-index が
// タスク種別で交絡するため (Phase1 実行可否レビューのブロッカー #2)。Phase1 完了後に
// 他種別へ広げる時は下のコメントアウトを戻す (型 TaskKind は 4 種を保持・backend は不変)。
const TASK_KINDS: { value: TaskKind; label: string }[] = [
  { value: "argumentative", label: "論述" },
  // --- Phase1 較正中はロックのため非表示 (復活させる時はコメントを外す) ---
  // { value: "correspondence", label: "通信文" },
  // { value: "creative", label: "創作" },
  // { value: "vibe_coding", label: "vibe coding" },
];

/** 自動提出の状態 DTO (backend `get_submission_status` / SubmissionStatusDto と同期)。 */
interface SubmissionStatus {
  /** 未送信の `.age` 本数。★ 突き合わせで数える (カウンタではない)。 */
  unsent: number;
  /** 直近の自動提出で起きた問題 (無ければ null)。 */
  last_error: string | null;
}

/**
 * 提出ラベル用参加者 ID の妥当性。★ backend `participant_id::is_valid_participant_id`
 * (英数字のみ・1〜16 文字) と **同じ規則**である。⚠️ 片方だけ緩めると、画面は通すのに
 * バックエンドが弾く (またはその逆) 状態になる。
 */
function isValidParticipantId(id: string): boolean {
  return /^[A-Za-z0-9]{1,16}$/.test(id);
}

// Phase 1 の 2 相プロトコル週セレクタ (tasklist #A / decisions FD2)。
// 介入有効化・較正モード・condition・label_pool を 1 つの選択にまとめ、不整合な組合せ
// (例: 介入 ON なのに calibration_blind プール) を構造的に表現不能にする。各 condition /
// label_pool 文字列は backend の Condition / LabelPool enum (logger.rs) と同期。
type PhaseWeek = "week1_blind" | "week2_intervention";

interface WeekConfig {
  value: PhaseWeek;
  label: string;
  description: string;
  /** session_meta.intervention_enabled。false で backend が全介入を gate (lib.rs safe_default)。 */
  interventionEnabled: boolean;
  /** 較正モード = モデル出力を非表示にし主観回答の測定独立性を守る。 */
  calibrationMode: boolean;
  /** backend Condition enum と同期 (blind_calibration / baseline)。 */
  condition: "blind_calibration" | "baseline";
  /** backend LabelPool enum と同期。X1 判定は calibration_blind のみ使用。 */
  labelPool: "calibration_blind" | "post_intervention";
}

const PHASE_WEEKS: WeekConfig[] = [
  {
    value: "week1_blind",
    label: "第1週 (blind 較正)",
    description: "介入は発火せず推定状態も非表示。X1 較正ラベルを収集 (calibration_blind)。",
    interventionEnabled: false,
    calibrationMode: true,
    condition: "blind_calibration",
    labelPool: "calibration_blind",
  },
  {
    value: "week2_intervention",
    label: "第2週 (介入)",
    description: "Wall + 2分タイマーが実発火。介入下のラベルを別プールで収集 (post_intervention)。",
    interventionEnabled: true,
    calibrationMode: false,
    condition: "baseline",
    labelPool: "post_intervention",
  },
];

interface CognitiveStateRaw {
  flow: number;
  incubation: number;
  stuck: number;
}

type InterventionAction = "none" | "nudge" | "wall" | "defer";

interface InterventionDecision {
  action: InterventionAction;
  need_score: number;
  opportunity_score: number;
  p_stuck: number;
  idle_ms: number;
  wall_accum_ms: number;
  reason: string;
  suppressed_by: string[];
}

const DEFAULT_INTERVENTION_DECISION: InterventionDecision = {
  action: "none",
  need_score: 0,
  opportunity_score: 0,
  p_stuck: 0,
  idle_ms: 0,
  wall_accum_ms: 0,
  reason: "safe_default",
  suppressed_by: [],
};

function App() {
  const [cognitiveState, setCognitiveState] = useState<CognitiveStateRaw>({
    flow: 0.80,
    incubation: 0.15,
    stuck: 0.05,
  });
  const [interventionDecision, setInterventionDecision] = useState<InterventionDecision>(
    DEFAULT_INTERVENTION_DECISION
  );
  const [isWallActive, setIsWallActive] = useState(false);
  const [isMonkMode, setIsMonkMode] = useState(false);
  // Overlay ウィンドウは start_session 時に動的生成されるため、
  // overlay なら最初からセッション開始済みとして扱う。
  const currentWindow = useMemo(() => getCurrentWindow(), []);
  const windowLabel = currentWindow.label;
  const [isStarted, setIsStarted] = useState(windowLabel === "overlay");
  const [keyboardIdleMs, setKeyboardIdleMs] = useState(0);
  const [hookActive, setHookActive] = useState<boolean | null>(null);
  const [startError, setStartError] = useState<string | null>(null);
  // G1 統制タスク実験モード。null = 通常運用、"marker" / "env" = 引き金つきで G1 モード。
  // ⚠️ ★ マーカーが外れる / launcher の `open -a` で通常アプリが起動する、のいずれでも
  // 黙って通常モードになるため、開始する前に画面で分かるようにする (decisions D-7 / R-7)。
  const [g1Mode, setG1Mode] = useState<string | null>(null);
  // G1: このプロセスで終了したブロック数 (5 分での自動終了ごとに増える)。
  const [g1BlocksDone, setG1BlocksDone] = useState(0);
  // G1: 直前のブロックが 5 分で自動終了したか (スタート画面に「終わった」だけを出す)。
  // ⚠️ ★ 残り時間は出さない (§4.4「残り時間のアナウンスをしない」/ §2.2 が却下した時間圧)。
  const [blockEnded, setBlockEnded] = useState(false);
  // G1: 研究者が割り当てた参加者 ID。★ 起動時に 1 回だけ入力し、以後のブロックで使い回す。
  // ⚠️ ★ 通常運用では **この欄自体を出さない** (g1Mode === null なら描画しない)。
  const [g1ParticipantId, setG1ParticipantId] = useState("");
  const [g1IdError, setG1IdError] = useState<string | null>(null);
  // G1: 自動提出の状態。★ 送信先から成否を追えないので (gas-measurements M-5)、
  // ⚠️ **未送信件数の表示は「あれば親切」ではなく必須の安全装置**である。
  const [submissionStatus, setSubmissionStatus] = useState<SubmissionStatus>({
    unsent: 0,
    last_error: null,
  });
  // 二重起動を検出した (別インスタンスの起動をブロックした)。
  const [duplicateBlocked, setDuplicateBlocked] = useState(false);
  // Task C: session_meta 宣言 + ビネット導線。
  const [taskKind, setTaskKind] = useState<TaskKind>("argumentative");
  const [showVignette, setShowVignette] = useState(false);
  // Phase 1 の 2 相プロトコル週セレクタ (tasklist #A / FD2)。既定は第1週 (blind 較正)。
  // 介入有効化・較正モード・condition・label_pool はこの 1 選択から派生し、開始後はスタート
  // 画面を離れるためセッション中は変更できない (実質ロック)。
  const [phaseWeek, setPhaseWeek] = useState<PhaseWeek>("week1_blind");
  // phaseWeek は PhaseWeek 型で PHASE_WEEKS を必ず網羅するため find は非 undefined。
  // 黙った `?? PHASE_WEEKS[0]` フォールバックは（万一の不整合時に）week1 blind 較正へ
  // 静かに倒れて汚染を隠すため使わない。不変条件を型で表明し、破れれば下の分割代入で fail-loud に落とす（FD7 思想）。
  const weekConfig = PHASE_WEEKS.find((w) => w.value === phaseWeek)!;
  // 派生値: Dashboard 表示制御と session_meta 記録に使う。週セレクタが唯一の真実源。
  const { interventionEnabled, calibrationMode } = weekConfig;
  // Ref mirrors: setInterval 内からステート最新値を参照するため
  // (依存配列に含めるとintervalが破棄・再作成され、タイマー精度が低下する)
  const isWallActiveRef = useRef(isWallActive);
  const isMonkModeRef = useRef(isMonkMode);
  // Wall を「1 エピソードにつき 1 回だけ」起動するためのエッジ検出フラグ。
  // 解除 (sensor-accelerometer) 後も判定が "wall" のまま lingering する
  // (特に overlay は last_decision を読む) ため、これが無いと毎ポーリングで再起動してしまう。
  const wallHandledRef = useRef(false);
  useEffect(() => { isWallActiveRef.current = isWallActive; }, [isWallActive]);
  useEffect(() => { isMonkModeRef.current = isMonkMode; }, [isMonkMode]);

  // D-1: currentWindow / windowLabel は isStarted 初期値算出のため上方で宣言済み

  // 2. Hook status: 継続的にポーリング（タップ無効化→自動復旧に追従）
  //    macOS では CGEventTap がスリープ復帰・権限変更時に無効化されることがある。
  //    バックエンドが自動復旧するため、フロントエンドも状態変化を継続監視する。
  //    旧実装では active 検知後にポーリングを停止していたが、inactive への遷移を
  //    検知できなかった。常時 3 秒間隔でポーリングを継続する。
  useEffect(() => {
    invoke<boolean>("get_hook_status")
      .then((active) => setHookActive(active))
      .catch(() => setHookActive(false));

    const interval = setInterval(() => {
      invoke<boolean>("get_hook_status")
        .then((active) => setHookActive(active))
        .catch(() => {});
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  // 3. 統合ポーリング (500ms): cognitive state + keyboard idle + intervention decision
  //    単一の setInterval 内で Promise.all で並行取得し、同じブロック内で
  //    Rust 側の Opportunity 判定結果を UI に反映する。
  //    isWallActive/isMonkMode は Ref 経由で Rust に渡し、依存配列に含めない。
  //    これにより interval の破棄・再作成が発生せず、タイマー精度が向上する。
  useEffect(() => {
    if (!isStarted) return;

    const interval = setInterval(async () => {
      try {
        const [state, idle, decision] = await Promise.all([
          invoke<CognitiveStateRaw>("get_cognitive_state"),
          invoke<number>("get_keyboard_idle_ms"),
          invoke<InterventionDecision>("get_intervention_decision", {
            windowLabel,
            isMonkMode: isMonkModeRef.current,
            isWallActive: isWallActiveRef.current,
          }),
        ]);
        setCognitiveState(state);
        setKeyboardIdleMs(idle);
        setInterventionDecision(decision);

        // Wall は新エピソードの立ち上がり (非 wall → wall) でのみ起動する。
        // 解除後も判定が "wall" のまま続く (overlay は last_decision を読むため lingering)
        // ケースで毎回再発火していたのを、wallHandledRef のエッジ検出で防ぐ。
        if (decision.action === "wall") {
          if (!isWallActiveRef.current && !wallHandledRef.current) {
            wallHandledRef.current = true;
            setIsWallActive(true);
          }
        } else {
          // 判定が wall を離れたら次のエピソードを許可する (cooldown 明け等)。
          wallHandledRef.current = false;
        }
      } catch (e) {
        console.error("Failed to fetch state:", e);
        setCognitiveState({ flow: 1.0, incubation: 0.0, stuck: 0.0 });
        setInterventionDecision(DEFAULT_INTERVENTION_DECISION);
      }
    }, 500);

    return () => clearInterval(interval);
  }, [isStarted, windowLabel]);

  // 4. Sensor Integration (Unlock Logic)
  //    Wall解除後にメインウィンドウをフォーカス:
  //    オーバーレイが透過に戻っても、ユーザーがクリックしないと
  //    メインウィンドウに操作が戻らないため、自動でフォーカスする。
  useEffect(() => {
    const unlisten = listen("sensor-accelerometer", (event) => {
      if (event.payload === "move") {
        setIsWallActive(false);
        // メインウィンドウ側でのみフォーカスを取り直す
        if (windowLabel !== "overlay") {
          currentWindow.setFocus().catch(() => {});
        }
      }
    });

    return () => {
      unlisten.then((f) => f());
    };
  }, [windowLabel, currentWindow]);

  // 4b. G1 モードの取得 (起動時 1 回)。null なら通常運用で、画面には何も足さない。
  //     ⚠️ ★ G1 実施者は「G1 モード」の表示が出ていることを開始前に確認する
  //     (participant-guide.md)。出ていなければ通常アプリが起動している
  //     = プローブが復活していて、実施後まで気づけない (decisions R-7)。
  useEffect(() => {
    invoke<string | null>("get_g1_mode")
      .then((mode) => setG1Mode(mode))
      .catch((e) => console.error("get_g1_mode failed:", e));
  }, []);

  // 4b-2. G1: 登録済みの参加者 ID を復元する (次回起動で入力し直させない)。
  //       ⚠️ ★ 通常運用では **呼ばない** (g1Mode === null なら何も起きない)。
  useEffect(() => {
    if (g1Mode === null) return;
    invoke<string | null>("get_g1_participant_id")
      .then((id) => {
        if (id) setG1ParticipantId(id);
      })
      .catch((e) => console.error("get_g1_participant_id failed:", e));
  }, [g1Mode]);

  // 4b-3. G1: 自動提出の状態 (未送信件数 / 直近の失敗) を、スタート画面にいる間だけ見る。
  //       ★ 送信の成否は送信先から追えない (gas-measurements.md M-5) ので、
  //       ⚠️ **端末側のこの表示が唯一の安全装置**である。
  //       ⚠️ ★ ブロック実施中はポーリングしない (測定中の端末に余計な仕事をさせない)。
  useEffect(() => {
    if (g1Mode === null || isStarted) return;
    let cancelled = false;
    const read = () => {
      invoke<SubmissionStatus>("get_submission_status")
        .then((s) => {
          if (!cancelled) setSubmissionStatus(s);
        })
        .catch((e) => console.error("get_submission_status failed:", e));
    };
    read();
    // 自動提出は別プロセスなので完了イベントが無い。★ スタート画面にいる間だけ 3 秒で追う。
    const t = setInterval(read, 3000);
    return () => {
      cancelled = true;
      clearInterval(t);
    };
  }, [g1Mode, isStarted, g1BlocksDone]);

  // 4c. G1: 5 分でのブロック自動終了。バックエンドがログを閉じたのでスタート画面へ戻す。
  //     ⚠️ ★ 出すのは「終わった」だけ。残り時間・カウントダウンは出さない
  //     (protocol.md §4.4「残り時間のアナウンスをしない」/ §2.2 が却下した時間圧)。
  useEffect(() => {
    const unlisten = listen("g1-block-ended", () => {
      setIsWallActive(false);
      setIsStarted(false);
      setBlockEnded(true);
      setG1BlocksDone((n) => n + 1);
    });
    return () => {
      unlisten.then((f) => f());
    };
  }, []);

  // 4d. 二重起動の検出。★ 2 個目のプロセスはプラグインが終了させ、この通知は
  //     **1 個目** に届く。黙って前面に出すだけだと、被験者は「開いたのに何も起きない」
  //     としか分からないため、理由を画面に出す (decisions R-7)。
  useEffect(() => {
    const unlisten = listen("second-instance-blocked", () => {
      setDuplicateBlocked(true);
    });
    return () => {
      unlisten.then((f) => f());
    };
  }, []);

  // 5. Monk Mode: Dashboard のトグルから monk-mode-changed を受け取り isMonkMode を更新。
  //    両ウィンドウ(main/overlay)がこのイベントをリッスンし状態を同期する。
  //    Monk Mode ON 時は LV2 Wall タイマーが無効化される。
  useEffect(() => {
    const unlisten = listen("monk-mode-changed", (event) => {
      setIsMonkMode(event.payload as boolean);
    });

    return () => {
      unlisten.then((f) => f());
    };
  }, []);

  // 6-7. (削除) Overlay は start_session 時に Rust 側で動的生成されるため、
  // session-started イベント購読と window.show() は不要。

  // Render based on Window Label
  if (windowLabel === "overlay") {
    return (
      <Overlay
        interventionDecision={interventionDecision}
        isWallActive={isWallActive}
      />
    );
  }

  const handleQuit = () => {
    invoke("quit_app").catch(console.error);
  };

  const handleStart = async () => {
    setStartError(null);
    setG1IdError(null);
    // 新しいブロックを始めるので、前ブロックの終了通知を消す。
    setBlockEnded(false);
    // ★ G1: 参加者 ID を先に確定させる。⚠️ **ここで保存しないと `.age` に ID が付かない**
    //   (P-1 で実際に起きた: 提出時の手打ちだったので提出しない限り ID がどこにも付かなかった)。
    //   ⚠️ ★ 通常運用 (g1Mode === null) では 1 行も走らない。
    if (g1Mode !== null) {
      const id = g1ParticipantId.trim();
      if (!isValidParticipantId(id)) {
        setG1IdError("参加者 ID を入力してください (英数字のみ・1〜16 文字。例: P012)。");
        return;
      }
      try {
        await invoke("set_g1_participant_id", { id });
      } catch (e) {
        console.error("set_g1_participant_id failed:", e);
        setG1IdError("参加者 ID を保存できませんでした。研究者に連絡してください。");
        return;
      }
    }
    try {
      await invoke("start_session");
    } catch (e) {
      console.error("Failed to start session:", e);
      setStartError("セッション開始に失敗しました。アプリを再起動してください。");
      return;
    }
    // Task C / tasklist #A: セッション開始宣言を記録 (track は較正スモークでは main 固定)。
    // condition / label_pool (WBS 0.11 / 0.4) は週セレクタ (weekConfig) が一括決定する。
    // 第1週=blind_calibration / calibration_blind (X1 判定はこのプールのみ使用)、
    // 第2週=baseline / post_intervention (合算せず別管理)。組合せは型で固定済み。
    // NOTE: Phase 2 AB/BA (a|b) と Phase 3 MRT (nudge|defer) の condition 配線は
    // それぞれの割付実装時に行う (本タスクは enum 凍結のみ。decisions CD8)。
    try {
      await invoke("record_session_meta", {
        track: "main",
        taskKind,
        monkMode: isMonkMode,
        interventionEnabled,
        condition: weekConfig.condition,
        labelPool: weekConfig.labelPool,
      });
    } catch (e) {
      // 週セレクタが運ぶ condition/label_pool は X1 プール分離 (FD3) の真値タグであり、
      // intervention_enabled は backend のグローバル介入ゲートを設定する。記録に失敗した
      // まま Dashboard へ進むと、タグ欠落かつ INTERVENTION_ENABLED が前セッションの値の
      // ままになり blind 較正が汚染されうる。ここで停止しユーザーに再開を促す。
      console.error("record_session_meta failed:", e);
      setStartError("セッション情報の記録に失敗しました。もう一度開始してください。");
      return;
    }
    setIsStarted(true);
  };

  // Task C: 尺度理解テスト (ビネット) フロー
  if (!isStarted && showVignette) {
    return <VignetteTest onComplete={() => setShowVignette(false)} />;
  }

  // セッション未開始時はスタート画面を表示
  if (!isStarted) {
    return (
      <div className="start-screen">
        <img src="/doe.svg" alt="GSE Logo" className="start-logo" />
        <div className="start-header">
          <h1>Generative Struggle Engine</h1>
          <p className="start-description">
            キーストロークを解析し、介入判断に必要な作業状態をリアルタイムで推定します。
          </p>
        </div>

        {/* ★ 二重起動の検出 (decisions R-7)。2 個目は起動を止めてあるが、
            被験者から見ると「開いたのに何も起きない」ので理由を出す。 */}
        {duplicateBlocked && (
          <div
            role="alert"
            style={{
              margin: "0.5rem 0",
              padding: "0.6rem 0.9rem",
              borderRadius: "6px",
              border: "1px solid #ff6b6b",
              background: "rgba(255,107,107,0.12)",
              fontSize: "0.85rem",
              maxWidth: "34rem",
            }}
          >
            ⚠️ <b>GSE が 2 つ動いている可能性があります。</b>
            <br />
            2 つ同時に動くと、打鍵の記録が 2 つのファイルに分かれて<b>そのブロックが使えなくなります</b>。
            <br />
            <span style={{ fontSize: "0.8rem" }}>
              ほかに開いている GSE（Dock / タスクバーを確認）を<b>終了してから</b>、
              このウィンドウで開始してください。心当たりが無ければ研究者にご連絡ください。
            </span>
          </div>
        )}

        {/* ★ G1 モードの表示 (fail-loud・decisions D-7 / R-7)。
            ⚠️ 通常運用 (g1Mode === null) では何も足さない = 既定の画面を変えない。 */}
        {g1Mode !== null && (
          <div
            style={{
              margin: "0.5rem 0",
              padding: "0.6rem 0.9rem",
              borderRadius: "6px",
              border: "2px solid #4caf50",
              background: "rgba(76,175,80,0.15)",
              fontSize: "0.9rem",
            }}
          >
            <b>G1 モードで動作しています</b>
            <span style={{ opacity: 0.7, fontSize: "0.8rem" }}>（{g1Mode}）</span>
            <br />
            <span style={{ fontSize: "0.8rem", opacity: 0.85 }}>
              1 ブロックは 5 分で自動的に終了し、ここに戻ります。記録は自動で研究者へ送られます。
              {g1BlocksDone > 0 && <> これまでに {g1BlocksDone} ブロック終了しました。</>}
            </span>

            {/* ★ 参加者 ID (G1 モード限定)。⚠️ 妥当な ID が入るまで「開始する」を押せない。 */}
            <div style={{ marginTop: "0.7rem", fontSize: "0.85rem" }}>
              <label htmlFor="g1-participant-id">
                参加者 ID（研究者から渡された番号。例: P012）
              </label>
              <div style={{ marginTop: "0.3rem" }}>
                <input
                  id="g1-participant-id"
                  type="text"
                  value={g1ParticipantId}
                  onChange={(e) => {
                    setG1ParticipantId(e.target.value.toUpperCase());
                    setG1IdError(null);
                  }}
                  placeholder="P012"
                  maxLength={16}
                  autoComplete="off"
                  spellCheck={false}
                  aria-invalid={!isValidParticipantId(g1ParticipantId.trim())}
                  style={{
                    padding: "0.35rem 0.6rem",
                    borderRadius: "6px",
                    border: isValidParticipantId(g1ParticipantId.trim())
                      ? "1px solid #4caf50"
                      : "1px solid #ff6b6b",
                    fontSize: "1rem",
                    width: "9rem",
                    textAlign: "center",
                  }}
                />
              </div>
              {g1IdError && (
                <p role="alert" style={{ color: "#ff6b6b", margin: "0.3rem 0 0", fontSize: "0.8rem" }}>
                  {g1IdError}
                </p>
              )}
            </div>
          </div>
        )}

        {/* ★ 未送信の可視化 (G1 モード限定)。⚠️ **0 件なら何も出さない** (被験者のノイズにしない)。
            ★ 送信の成否は送信先から追えないので、ここが唯一の安全装置である。 */}
        {g1Mode !== null && submissionStatus.unsent > 0 && (
          <div
            role="status"
            style={{
              margin: "0.5rem 0",
              padding: "0.6rem 0.9rem",
              borderRadius: "6px",
              border: "1px solid #ffa726",
              background: "rgba(255,167,38,0.12)",
              fontSize: "0.85rem",
              maxWidth: "34rem",
            }}
          >
            未送信の記録が <b>{submissionStatus.unsent} 件</b> あります。
            <br />
            <span style={{ fontSize: "0.8rem", opacity: 0.85 }}>
              記録はお使いのパソコンに残っており、失われていません。次のブロックの後に自動で送信を再試行します。
              <b>そのまま実施を続けてください。</b>
              最後まで残る場合は研究者にご連絡ください。
            </span>
          </div>
        )}

        {/* ⚠️ ★ 自動提出そのものが起動できなかった / 失敗した場合。★ ログではなく画面に出す
            (「起こしたつもりで動いていない」を黙って通さない)。 */}
        {g1Mode !== null && submissionStatus.last_error && (
          <div
            role="alert"
            style={{
              margin: "0.5rem 0",
              padding: "0.6rem 0.9rem",
              borderRadius: "6px",
              border: "1px solid #ff6b6b",
              background: "rgba(255,107,107,0.12)",
              fontSize: "0.85rem",
              maxWidth: "34rem",
            }}
          >
            ⚠️ 記録の自動送信でエラーが起きています。
            <br />
            <span style={{ fontSize: "0.78rem", opacity: 0.85 }}>
              記録自体はお使いのパソコンに残っています。<b>実施はそのまま続けてください。</b>
              このまま消えない場合は、次の内容を研究者にお伝えください:
              <br />
              <code style={{ fontSize: "0.72rem" }}>{submissionStatus.last_error}</code>
            </span>
          </div>
        )}

        {/* ★ ブロック終了の通知。⚠️ 出すのは「終わった」だけ。残り時間は出さない (§4.4)。 */}
        {blockEnded && (
          <div
            role="status"
            style={{
              margin: "0.5rem 0",
              padding: "0.6rem 0.9rem",
              borderRadius: "6px",
              border: "1px solid #888",
              fontSize: "0.9rem",
            }}
          >
            5 分が経過したので、このブロックの記録を終了しました。
            <br />
            <span style={{ fontSize: "0.8rem", opacity: 0.85 }}>
              記入ページの文字数を控えてから本文を消去し、1 分休んで次のブロックを開始してください。
            </span>
          </div>
        )}

        {/* Task C: session_meta の task_kind 宣言 */}
        <div style={{ margin: "1rem 0" }}>
          <div style={{ fontSize: "0.85rem", marginBottom: "0.4rem" }}>今回の作業種別（Phase1 は論述に固定）:</div>
          <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", justifyContent: "center" }}>
            {TASK_KINDS.map((tk) => (
              <button
                key={tk.value}
                onClick={() => setTaskKind(tk.value)}
                style={{
                  padding: "0.4rem 0.8rem",
                  cursor: "pointer",
                  borderRadius: "6px",
                  border: taskKind === tk.value ? "2px solid #4caf50" : "1px solid #888",
                  background: taskKind === tk.value ? "rgba(76,175,80,0.15)" : "transparent",
                }}
              >
                {tk.label}
              </button>
            ))}
          </div>
          {/* tasklist #A: Phase 1 2 相プロトコルの週セレクタ。介入 ON/OFF・較正モード・
              condition・label_pool を 1 つの選択にまとめ、不整合な組合せを選べなくする。 */}
          <div style={{ marginTop: "1rem" }}>
            <div style={{ fontSize: "0.85rem", marginBottom: "0.4rem" }}>今回の実施週:</div>
            <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", justifyContent: "center" }}>
              {PHASE_WEEKS.map((w) => (
                <button
                  key={w.value}
                  onClick={() => setPhaseWeek(w.value)}
                  aria-pressed={phaseWeek === w.value}
                  style={{
                    padding: "0.4rem 0.8rem",
                    cursor: "pointer",
                    borderRadius: "6px",
                    border: phaseWeek === w.value ? "2px solid #4caf50" : "1px solid #888",
                    background: phaseWeek === w.value ? "rgba(76,175,80,0.15)" : "transparent",
                  }}
                >
                  {w.label}
                </button>
              ))}
            </div>
            <p style={{ marginTop: "0.5rem", fontSize: "0.78rem", opacity: 0.8 }}>
              {weekConfig.description}
            </p>
          </div>
        </div>

        {/* ⚠️ ★ G1 では **妥当な参加者 ID が入るまで押せない** (受け入れ条件 1)。
            ★ 通常運用 (g1Mode === null) では条件が常に false = 従来どおり常に押せる。 */}
        <button
          className="start-button"
          onClick={handleStart}
          disabled={g1Mode !== null && !isValidParticipantId(g1ParticipantId.trim())}
          title={
            g1Mode !== null && !isValidParticipantId(g1ParticipantId.trim())
              ? "参加者 ID を入力してください"
              : undefined
          }
        >
          開始する
        </button>
        <button
          className="start-button"
          onClick={() => setShowVignette(true)}
          style={{ background: "transparent", border: "1px solid #888", marginTop: "0.5rem" }}
        >
          尺度理解テスト (初回)
        </button>
        {startError && (
          <p className="start-error" style={{ color: '#ff6b6b', marginTop: '0.5rem', fontSize: '0.9rem' }}>
            {startError}
          </p>
        )}
        <p className="start-hint">
          自然にタイピングを始めると、検知が動作します。
        </p>
      </div>
    );
  }

  // Default to Main Dashboard (較正モード時は blind/minimal 表示)
  // onBack: アプリを終了せずスタート画面へ戻る (作業種別の変更・尺度理解テスト・再開のため)。
  //   戻る瞬間に Wall が出ていたら overlay が残らないよう介入もクリアする。
  const handleBack = () => {
    setIsWallActive(false);
    setIsStarted(false);
  };
  return (
    <Dashboard cognitiveState={cognitiveState} onQuit={handleQuit} onBack={handleBack} isMonkMode={isMonkMode} keyboardIdleMs={keyboardIdleMs} hookActive={hookActive} calibrationMode={calibrationMode} interventionEnabled={interventionEnabled} />
  );
}

export default App;
