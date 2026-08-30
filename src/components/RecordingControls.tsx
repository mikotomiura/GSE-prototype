import React, { useCallback, useEffect, useRef, useState } from "react";
import { invoke } from "@tauri-apps/api/core";

/**
 * O1（普段の作業の長期記録）で被験者に約束した **3 点セット** の UI。
 *
 * ⚠️★★★ ADR-014 **判断 3** は倫理審査を不要と判断したが、その **根拠 3** は逐語
 * 「**被験者が停止・削除できる** —— 稼働中インジケータ / 即時の一時停止 / 事後の区間指定削除」であり、
 * ⚠️ 崩れる条件も逐語で「**削除 UI が実装されないまま収集を始めた時点で崩れる**」と書かれている。
 *
 * | # | 要件（ADR-014 D7） | ★ ここでの実装 |
 * |---|---|---|
 * | i | 稼働中インジケータ | ★ 常時表示のバッジ（⚠️ **止まっているときは「記録していません」と明示**） |
 * | ii | 即時の一時停止 | ★ ボタン 1 つ。⚠️ **理由を聞かない** |
 * | iii | 事後の区間指定削除 | ★ 時間帯を入れて消す。⚠️ **理由の入力欄を置かない** |
 *
 * ## ⚠️ 判断は Rust 側が持つ
 *
 * `architecture-rules` ルール 3 / `typescript-standards` に従い、
 * ★ 「記録しているか」「何行消えたか」は **backend が返した値をそのまま描く**だけにする。
 */

/** backend `get_recording_status` / `RecordingStatusDto` と同期。 */
interface RecordingStatusDto {
  paused: boolean;
  current_file: string;
  session_dir: string;
  /** ★ O1 モードの引き金 (`"marker"` / `"env"`)。⚠️ 通常運用 / G1 では `null`。 */
  o1_mode: string | null;
  /**
   * ⚠️★★★ いま宣言されている作業の種類。**`null` = 未宣言**。
   *
   * ★ ADR-016 判断 4b-3: `unknown` を enum に足さず、`session_meta` 行の *不在* で
   * 未宣言を表す。→ ⚠️ 画面は「**未設定**」と描き、**こちらで推測して埋めない**
   * (同意文書 §2 の逐語)。
   */
  task_kind: string | null;
  /**
   * ⚠️★★★ **実際に記録できているか** (研究者判断 R-11)。
   *
   * ★ `paused` だけを見ると、⚠️ **フックが死んでいても「記録しています」と出る**。
   * → ★ 同意文書 §4 の逐語「印が出ていないときは記録していません」を守るため、
   * **「止めた」と「壊れている」を分けて描く**。⚠️ 判定は Rust 側が持つ
   * (`architecture-rules` ルール 3 / `typescript-standards` ルール 2)。
   */
  health: "recording" | "paused" | "broken";
  /** ⚠️ `health === "broken"` のとき、何が壊れているかの 1 行。 */
  health_detail: string | null;
}

/**
 * ⚠️★★★ O1 の宣言 4 択 (ADR-016 **判断 4b-2**: 既存 4 値をそのまま出す)。
 *
 * ★ ラベルと補足は **同意文書 §2 の表と逐語で一致させる**。
 * ⚠️ **新しい値を足さない** —— `task_kind` は `schema/current.json` で 4 値の enum に
 * 制約されており、足すと gse-dataset の parity 更新が要る (判断 4b-3)。
 *
 * ⚠️★ `creative` の語は **「創作」を捨てて「デザイン・映像・制作作業」**にした
 * (判断 O1-3)。★ 「制作」も執筆と読めうるので、**補足を 1 行必ず添える**。
 */
const O1_TASK_KINDS: { value: string; label: string; note: string }[] = [
  { value: "argumentative", label: "論述", note: "意見や説明を組み立てて書く作業" },
  { value: "correspondence", label: "通信文", note: "メール・チャットなどのやりとり" },
  {
    value: "creative",
    label: "デザイン・映像・制作作業",
    note: "図面・動画編集・3D など、文字をあまり打たない作業",
  },
  { value: "vibe_coding", label: "vibe coding", note: "AI と対話しながらのコーディング" },
];

/** 宣言値 → 画面に出す語。⚠️ 未宣言 (`null`) は「未設定」。 */
function taskKindLabel(value: string | null): string {
  if (value === null) return "未設定";
  return O1_TASK_KINDS.find((k) => k.value === value)?.label ?? value;
}

/** backend `get_o1_enrollment` / `O1EnrollmentDto` と同期 (研究者判断 R-7)。 */
interface O1EnrollmentDto {
  /** ★ 1 回きりの同意確認が済んでいるか。⚠️ 済むまで送信経路は開かない。 */
  consent_acknowledged: boolean;
  /** ★ O1 専用の参加者 ID (未登録なら null)。 */
  participant_id: string | null;
}

/** 参加者 ID の妥当性。★ backend `participant_id::is_valid_participant_id` と同じ規則。 */
function isValidParticipantId(id: string): boolean {
  return /^[A-Za-z0-9]{1,16}$/.test(id);
}

/** backend `delete_time_range` / `RedactionOutcomeDto` と同期。 */
interface RedactionOutcomeDto {
  files_touched: number;
  lines_removed: number;
  files_skipped: number;
}

/**
 * `datetime-local` の値（ローカル時刻・秒なし）を UNIX ミリ秒へ直す。
 *
 * ⚠️★ `new Date(value)` は文字列にタイムゾーンが無いと**実装依存**になりうるので、
 * ★ 各要素を取り出して `new Date(y, m, d, h, min)` で**ローカル時刻として**組み立てる。
 * → ★ 被験者が「昨日の 14:00」と入れたら、**その端末の 14:00** になる。
 */
export function localInputToEpochMs(value: string): number | null {
  const m = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})$/.exec(value);
  if (!m) return null;
  const [, y, mo, d, h, mi] = m;
  const dt = new Date(
    Number(y),
    Number(mo) - 1,
    Number(d),
    Number(h),
    Number(mi),
    0,
    0,
  );
  const ms = dt.getTime();
  return Number.isNaN(ms) ? null : ms;
}

const RecordingControls: React.FC = () => {
  const [status, setStatus] = useState<RecordingStatusDto | null>(null);
  const [busy, setBusy] = useState(false);
  const [from, setFrom] = useState("");
  const [to, setTo] = useState("");
  const [outcome, setOutcome] = useState<RedactionOutcomeDto | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [confirming, setConfirming] = useState(false);
  // ⚠️★★★ O1: 宣言 4 択を開いているか。★ 既定は閉じている (1 行だけ出す)。
  const [pickingTaskKind, setPickingTaskKind] = useState(false);
  // ★ O1: 研究者が割り当てた参加者 ID。⚠️ **これが無いと自動提出が動かない**
  //   (`run_reconcile_blocking` が「ID 未登録なので何もしない」で帰る)。
  const [participantId, setParticipantId] = useState("");
  const [participantIdError, setParticipantIdError] = useState<string | null>(null);
  // ⚠️★★★ O1 の開始前ゲート (研究者判断 R-7)。null = まだ読んでいない。
  const [enrollment, setEnrollment] = useState<O1EnrollmentDto | null>(null);

  const refresh = useCallback(() => {
    invoke<RecordingStatusDto>("get_recording_status")
      .then((s) => {
        setStatus(s);
        setError(null);
      })
      .catch((e) => {
        // ⚠️ 状態が読めないことを黙って「記録中」に見せない (fail-loud)。
        setStatus(null);
        setError(
          `記録の状態を確認できませんでした: ${typeof e === "string" ? e : String(e)}`,
        );
      });
  }, []);

  // ★ 稼働中インジケータ (D7-i) は**常に最新**でなければ意味が無いので定期に取り直す。
  useEffect(() => {
    refresh();
    const id = setInterval(refresh, 2000);
    return () => clearInterval(id);
  }, [refresh]);

  // ★ O1: 登録済みの参加者 ID を復元する (⚠️ 通常運用 / G1 では呼ばない)。
  const o1Mode = status?.o1_mode ?? null;

  // ⚠️★★★ ADR-016 **判断 4b-1** の逐語「**起動時に 1 回促す** ＋ 被験者が任意のタイミングで
  //   変更できる（⚠️ **強制しない**）」。★ 促さないと未宣言のまま数日走るのが既定になる。
  //   ⚠️ **1 回だけ**開く (`promptedRef`)。★ 閉じたら二度と自分からは開かない = 強制しない。
  const promptedRef = useRef(false);
  useEffect(() => {
    if (!o1Mode || promptedRef.current) return;
    if (status?.task_kind === null) {
      promptedRef.current = true;
      setPickingTaskKind(true);
    }
  }, [o1Mode, status?.task_kind]);
  // ★ O1: 開始前ゲートの状態を読む (⚠️ 通常運用 / G1 では呼ばない)。
  const refreshEnrollment = useCallback(() => {
    invoke<O1EnrollmentDto>("get_o1_enrollment")
      .then((e) => {
        setEnrollment(e);
        if (e.participant_id) setParticipantId(e.participant_id);
      })
      // ⚠️ 読めないときは **null のまま** = ゲートを描かない。
      //   ★ 「確認してください」を出せないだけで、送信は backend が塞いでいる (fail-closed)。
      .catch((e) => console.error("get_o1_enrollment failed:", e));
  }, []);
  useEffect(() => {
    if (!o1Mode) return;
    refreshEnrollment();
  }, [o1Mode, refreshEnrollment]);

  /**
   * ⚠️★★★ 作業の種類を宣言する / 宣言し直す。
   *
   * ★ backend の 1 コマンドが **3 つ同時に**行う (ADR-016 判断 4b-1):
   * `session_meta` 出力 → ログのローテート → `engine.reset()`。
   * ⚠️ Frontend 側で 3 回に分けて呼ばない —— 途中で失敗すると
   * 「宣言はしたがローテートしていない」状態になり、`gse-replay` が落ちる。
   */
  const declare = (taskKind: string) => {
    setBusy(true);
    setError(null);
    invoke("declare_task_kind", { taskKind })
      .then(() => {
        setPickingTaskKind(false);
        refresh();
      })
      .catch((e) => setError(typeof e === "string" ? e : String(e)))
      .finally(() => setBusy(false));
  };

  /**
   * ⚠️★★★ O1: **同意確認と参加者 ID を 1 アクションで登録する** (研究者判断 R-7)。
   *
   * ★ 被験者が押すのは**この 1 回だけ**である。⚠️ backend は ID が妥当でなければ
   * **確認の印も置かない** (fail-closed) —— ★ 「確認は済んだが ID が無いので送られない」
   * という中途半端な状態を作らない。
   */
  const acknowledgeEnrollment = () => {
    const id = participantId.trim();
    if (!isValidParticipantId(id)) {
      setParticipantIdError("英数字のみ・1〜16 文字で入力してください (例: P012)。");
      return;
    }
    setBusy(true);
    setParticipantIdError(null);
    invoke("acknowledge_o1_enrollment", { participantId: id })
      .then(() => refreshEnrollment())
      .catch((e) => setParticipantIdError(typeof e === "string" ? e : String(e)))
      .finally(() => setBusy(false));
  };

  const togglePause = () => {
    if (!status) return;
    setBusy(true);
    // ⚠️★★★ 理由を聞かない。★ 確認ダイアログも出さない（「すぐ止める」が約束である）。
    invoke<boolean>("set_recording_paused", { paused: !status.paused })
      .then(() => refresh())
      .catch((e) => setError(typeof e === "string" ? e : String(e)))
      .finally(() => setBusy(false));
  };

  const runDelete = () => {
    const fromMs = localInputToEpochMs(from);
    const toMs = localInputToEpochMs(to);
    if (fromMs === null || toMs === null) {
      setError("開始と終了の日時を両方入力してください。");
      return;
    }
    if (fromMs > toMs) {
      setError("開始時刻が終了時刻より後になっています。");
      return;
    }
    setBusy(true);
    setError(null);
    setOutcome(null);
    invoke<RedactionOutcomeDto>("delete_time_range", {
      fromMs,
      toMs,
    })
      .then((r) => {
        setOutcome(r);
        setConfirming(false);
      })
      .catch((e) => setError(typeof e === "string" ? e : String(e)))
      .finally(() => setBusy(false));
  };

  const paused = status?.paused === true;
  // ⚠️★★★ 止めていないのに記録できていない (フックの死 / 書込不可)。
  //   ★ backend が判定した値をそのまま描く (Frontend で判定しない)。
  const broken = status?.health === "broken";

  return (
    <div className="recording-controls" style={{ marginTop: "1.5rem" }}>
      {/* ── D7-i: 稼働中インジケータ ───────────────────────────────── */}
      {/* ⚠️★★★ 「記録していません」を**はっきり書く**。★ 同意文書 §4 の逐語
          「印が出ていないときは記録していません」を、印の側の文言で満たす。 */}
      <div
        role="status"
        aria-live="polite"
        style={{
          display: "flex",
          alignItems: "center",
          gap: "0.5rem",
          padding: "0.5rem 0.75rem",
          borderRadius: "6px",
          border: "1px solid rgba(255,255,255,0.15)",
        }}
      >
        {/* ⚠️★★★ **3 値で描く** (R-11)。★ 「止めた」と「壊れている」を分ける ——
            混ぜると、⚠️ **1 行も書けていないのに「記録しています」と出る**
            (同意文書 §4 の逐語と正面から矛盾する)。 */}
        <span aria-hidden="true">
          {status === null ? "…" : broken ? "⚠" : paused ? "⏸" : "●"}
        </span>
        <strong style={broken ? { color: "#ff6b6b" } : undefined}>
          {status === null
            ? "記録の状態を確認しています…"
            : broken
              ? "記録できていません"
              : paused
                ? "記録を止めています（このあいだは何も記録されません）"
                : "記録しています"}
        </strong>
        <button
          type="button"
          onClick={togglePause}
          disabled={busy || status === null}
          style={{ marginLeft: "auto" }}
        >
          {paused ? "記録を再開する" : "すぐ止める"}
        </button>
      </div>

      {/* ⚠️★★★ **黙って赤くしない。** ★ 何が壊れているかと、次に何をすればよいかを出す。 */}
      {broken && status?.health_detail && (
        <p role="alert" style={{ color: "#ff6b6b", margin: "0.4rem 0 0" }}>
          {status.health_detail}
        </p>
      )}

      {/* ── ⚠️★★★ O1 (R3-a): 作業の種類の宣言 (ADR-016 判断 4 / 4b) ───────────── */}
      {/* ★ 同意文書 §2 の逐語「記録中はいつも、画面のすみに『記録中 · 作業の種類: ○○』と
          出ています。そこを押すと、次の 4 つから選べます」を、この 1 行で満たす。
          ⚠️ 通常運用 / G1 では **1 行も出さない** (o1_mode === null なら描画しない)。 */}
      {o1Mode && (
        <div style={{ marginTop: "0.5rem" }}>
          <div
            role="status"
            aria-live="polite"
            style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}
          >
            <span>
              記録中 · 作業の種類:{" "}
              <strong>{taskKindLabel(status?.task_kind ?? null)}</strong>
            </span>
            <button
              type="button"
              onClick={() => setPickingTaskKind((v) => !v)}
              disabled={busy || status === null}
            >
              {pickingTaskKind ? "閉じる" : "選ぶ・変える"}
            </button>
          </div>

          {pickingTaskKind && (
            <div style={{ marginTop: "0.5rem" }}>
              <p style={{ fontSize: "0.85em", opacity: 0.85, margin: "0 0 0.4rem" }}>
                いま何の作業をしているかを選んでください。
                {/* ⚠️★★★ 「選ばなくてもよい」と「忘れても記録は続く」を明示する。
                    ★ 同意文書 §2 の逐語と一致させる (書いたことを画面でも守る)。 */}
                選ばなくてもかまいません（記録は止まりません）。
              </p>
              <div style={{ display: "flex", flexDirection: "column", gap: "0.35rem" }}>
                {O1_TASK_KINDS.map((k) => (
                  <button
                    key={k.value}
                    type="button"
                    onClick={() => declare(k.value)}
                    disabled={busy}
                    aria-pressed={status?.task_kind === k.value}
                    style={{
                      textAlign: "left",
                      padding: "0.4rem 0.6rem",
                      borderRadius: "6px",
                      border:
                        status?.task_kind === k.value
                          ? "2px solid #4caf50"
                          : "1px solid #888",
                      background:
                        status?.task_kind === k.value
                          ? "rgba(76,175,80,0.15)"
                          : "transparent",
                      cursor: busy ? "default" : "pointer",
                    }}
                  >
                    <strong>{k.label}</strong>
                    <span style={{ opacity: 0.8 }}>（{k.note}）</span>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* ⚠️★★★ **開始前ゲート — 1 回きり** (研究者判断 R-7)。
              ★ D-14 の `.age.ok` (毎回の送信確認) は O1 では外した (R-2・同意文書 §5 の
              逐語「**自動的に**送ります」を守るため)。⚠️ しかしそれは
              「**同意手続きを経ていない人が配布ビルドを起動する経路を塞ぐ**」役も担っていた。
              ⚠️★★★ 実測: **G1 をやった端末に O1 ビルドを置くだけで、人の操作ゼロで
              常時記録＋48 時間後の自動送信が始まる**。→ ★ **確認が済むまで送信経路を開かない。**
              ⚠️ `.age` は作られる (★ データは失われず、確認すればそのまま送られる)。 */}
          {enrollment !== null && !enrollment.consent_acknowledged && (
            <div
              role="alert"
              style={{
                marginTop: "0.75rem",
                padding: "0.6rem 0.9rem",
                borderRadius: "6px",
                border: "1px solid #ffb74d",
              }}
            >
              <strong>研究者へ送る前に、1 回だけ確認させてください。</strong>
              <p style={{ fontSize: "0.9em", margin: "0.4rem 0" }}>
                この記録は、1 日ごとにひとまとまりにして、
                <strong>そこから 48 時間おいてから</strong>
                暗号化して研究者へ送られます。
                <br />
                {/* ⚠️★★★ 同意文書 §4-3 の逐語と揃える (★ 書いたことを画面でも守る)。 */}
                送られる前なら、「この時間帯の記録を消す」でご自身の端末の上で消せます。
                理由を聞くことはありません。
              </p>
              <p style={{ fontSize: "0.9em", margin: "0.4rem 0" }}>
                説明を受け、記録と自動送信に同意される場合は、
                研究者からお伝えした記号を入れて「確認しました」を押してください。
                <br />
                <span style={{ opacity: 0.85 }}>
                  ⚠️ 押されるまで、研究者へは 1 本も送られません。
                </span>
              </p>
              <label style={{ fontSize: "0.9em" }}>
                参加者 ID（研究者からお伝えした記号）{" "}
                <input
                  type="text"
                  value={participantId}
                  onChange={(e) => setParticipantId(e.target.value)}
                  placeholder="P012"
                  style={{ width: "8rem" }}
                />
              </label>{" "}
              <button type="button" onClick={acknowledgeEnrollment} disabled={busy}>
                確認しました
              </button>
              {participantIdError && (
                <p role="alert" style={{ color: "#ff6b6b", marginTop: "0.3rem" }}>
                  {participantIdError}
                </p>
              )}
            </div>
          )}
        </div>
      )}

      {/* ── D7-iii: 事後の区間指定削除 ──────────────────────────────── */}
      {/* ⚠️★★★ **理由の入力欄を置かない。** 同意文書 §4 の逐語
          「理由を説明する必要はありません」。★ 欄があること自体が説明を求める圧力になる。 */}
      <details style={{ marginTop: "0.75rem" }}>
        <summary>この時間帯の記録を消す</summary>
        <p style={{ fontSize: "0.9em", opacity: 0.85, marginTop: "0.4rem" }}>
          消したい時間帯を入れて「消す」を押してください。理由を聞くことはありません。
        </p>
        <div
          style={{
            display: "flex",
            flexWrap: "wrap",
            gap: "0.5rem",
            alignItems: "center",
          }}
        >
          <label>
            開始{" "}
            <input
              type="datetime-local"
              value={from}
              onChange={(e) => setFrom(e.target.value)}
            />
          </label>
          <label>
            終了{" "}
            <input
              type="datetime-local"
              value={to}
              onChange={(e) => setTo(e.target.value)}
            />
          </label>
          {confirming ? (
            <>
              {/* ★ 確認は 1 段だけ。⚠️ 「本当に？」を重ねない（★ 消しにくくしない）。 */}
              <button type="button" onClick={runDelete} disabled={busy}>
                消す（元に戻せません）
              </button>
              <button
                type="button"
                onClick={() => setConfirming(false)}
                disabled={busy}
              >
                やめる
              </button>
            </>
          ) : (
            <button
              type="button"
              onClick={() => {
                setError(null);
                setOutcome(null);
                setConfirming(true);
              }}
              disabled={busy}
            >
              消す
            </button>
          )}
        </div>

        {/* ⚠️★★★ 案内を実態に合わせる (code-reviewer / security-checker HIGH・2026-08-27)。
            ★ O1 では削除の直前に**現行ファイルを閉じてから**消すので、いまの記録も消せる。
            ⚠️ 逆に**止めているあいだは閉じられない**ので、そのときだけ再開を促す。
            ★ 通常運用 / G1 は従来どおり「先に止める」を出す (挙動を変えていない)。 */}
        {o1Mode ? (
          paused ? (
            <p style={{ fontSize: "0.85em", marginTop: "0.4rem" }}>
              ⚠️ 記録を止めているあいだは、いちばん新しい記録だけ消せません。
              「記録を再開する」を押してからもう一度実行すると、そこまで消せます。
            </p>
          ) : (
            /* ⚠️★★★ **失敗する前に順序を教える** (2026-08-30・実機で発見)。
               ★ 旧実装は `paused` のときだけ案内を出していた。⚠️ つまり
               **正しい順序は「一度失敗してから」しか画面に出なかった**。
               ⚠️ 実際に研究者が 2 回続けて「すぐ止める」→「消す」の順で押し、
                  2 回とも `files_skipped=1` で空振りした (★ 2026-08-30 の実機記録)。
               ★ 「消す前に止める」は一般的な直感であり、⚠️ **Phase1 / G1 では実際に正しい**。
                  O1 だけ逆なので、⚠️ **被験者は研究者より確実に踏む**。 */
            <p style={{ fontSize: "0.85em", marginTop: "0.4rem" }}>
              ★ 記録を止めずに、このまま消せます。
              <br />
              ⚠️ さきに「すぐ止める」を押すと、
              <strong>いちばん新しい記録は消せなくなります</strong>
              （止めているあいだは切り替えられないため）。
            </p>
          )
        ) : (
          !paused && (
            <p style={{ fontSize: "0.85em", marginTop: "0.4rem" }}>
              ⚠️ いま記録中のファイルは消せません。さきに「すぐ止める」を押してください。
            </p>
          )
        )}

        {outcome && (
          <p role="status" style={{ marginTop: "0.5rem" }}>
            {/* ⚠️★★★ **0 件を「消しました」と言わない** (2026-08-30・実機で発見)。
                ★ 旧文は `lines_removed` が 0 でも逐語「消しました（0 個のファイルから 0 件）。」
                  と出していた。⚠️ **何も消えていないのに成功文で始まる。**
                ★ 実機では 6 回連続でこれが出た (★ そのうち 5 回は本当に 0 件)。
                → ⚠️ memory `silent-success-is-not-visible` と同型:
                  **成功は肯定形で、根拠は実測** —— 0 件は成功ではない。 */}
            {outcome.lines_removed > 0 ? (
              <>
                消しました（{outcome.files_touched} 個のファイルから{" "}
                {outcome.lines_removed} 件）。
              </>
            ) : (
              <>⚠️ この時間帯に消せる記録はありませんでした（0 件）。</>
            )}
            {/* ⚠️★★★ 削除の「後」の案内にも O1 の分岐が要る (2026-08-28)。
                ★ O1 は削除の直前に**現行ファイルを閉じてから**消すので、通常は消せる。
                ⚠️ 消し残るのは**一時停止中**である (停止中はローテートしない──
                `lib.rs` の `is_o1() && !is_paused()`)。★ そこで旧文のとおり
                「すぐ止める」を押すと、**止まったままなので何度やっても同じ結果**になる
                (★ 正しい出口を UI が一度も教えない = ループする)。

                ⚠️★★ **`o1Mode && !paused` も到達する** (code-reviewer / security-checker
                HIGH・2026-08-28)。★ ローテートが 5 秒の締切を超えた / `o1_rotate` が Err の経路で、
                `lib.rs` 自身が `"... the newest file will be skipped"` と警告している。
                ⚠️ そこで「すぐ止める」を出すと、**止めた瞬間に `is_o1() && !is_paused()` が偽になり
                ローテート経路そのものが消える** (= さらに消せなくなる)。
                → ★ 分岐は `:508` の案内と同じく **`o1Mode` を外側**に置く。
                ⚠️ 通常運用 / G1 の文言は **1 文字も変えていない**。 */}
            {outcome.files_skipped > 0 && (
              <>
                {" "}
                ⚠️ 記録中のファイル {outcome.files_skipped} 個は消していません。
                {o1Mode
                  ? paused
                    ? "「記録を再開する」を押してからもう一度実行してください。"
                    : "もう一度実行してください。それでも残る場合は研究者に連絡してください。"
                  : "「すぐ止める」を押してからもう一度実行してください。"}
              </>
            )}
          </p>
        )}
      </details>

      {error && (
        <p role="alert" style={{ color: "#ff6b6b", marginTop: "0.5rem" }}>
          {error}
        </p>
      )}
    </div>
  );
};

export default RecordingControls;
