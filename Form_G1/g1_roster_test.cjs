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
    "★ その行のメールが空なら申告 P-ID を採用する（正当な経路・陰性対照）"
  );
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
  check(ctx.g1IsValidPid_("") === false, "空欄は妥当でない");
  check(ctx.g1IsValidPid_("まだ") === false, "日本語は妥当でない");
  check(ctx.g1IsValidPid_("P-ID") === false, "見出し行の値は妥当でない");
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
if (pass < 25) {
  console.log("  ❌ ★ 通過件数が少なすぎます（" + pass + " 件）。検査が読み込めていない疑い。");
  process.exit(1);
}
// ⚠️★ 行頭に空白や絵文字を置かないこと。★ `run.sh` の `guard_count` が
//   `^全 \([0-9]*\) ケース期待どおり$` で件数を読む（行頭アンカー）。
//   ⚠️ ずらすと「件数不明」と表示され、**何件走ったか分からないまま緑になる**。
console.log("全 " + pass + " ケース期待どおり");
