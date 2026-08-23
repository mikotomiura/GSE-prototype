import React, { useCallback, useEffect, useState } from "react";
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
        <span aria-hidden="true">{paused ? "⏸" : "●"}</span>
        <strong>
          {status === null
            ? "記録の状態を確認しています…"
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

        {/* ⚠️★★★ いま書いているファイルは触れない。★ 先に止めてもらう導線を出す。 */}
        {!paused && (
          <p style={{ fontSize: "0.85em", marginTop: "0.4rem" }}>
            ⚠️ いま記録中のファイルは消せません。さきに「すぐ止める」を押してください。
          </p>
        )}

        {outcome && (
          <p role="status" style={{ marginTop: "0.5rem" }}>
            消しました（{outcome.files_touched} 個のファイルから{" "}
            {outcome.lines_removed} 件）。
            {outcome.files_skipped > 0 && (
              <>
                {" "}
                ⚠️ 記録中のファイル {outcome.files_skipped} 個は消していません。
                「すぐ止める」を押してからもう一度実行してください。
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
