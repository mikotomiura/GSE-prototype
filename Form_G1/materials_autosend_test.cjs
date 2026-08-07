// 事前資料メールの自動送信ガードの赤/緑をローカルで実測する。
// ★ 実シート・実メールには一切触らない（SpreadsheetApp / MailApp をスタブする）。
//
// ⚠️ ★ ガードのテストは「止まること」だけ見てはいけない。**陽性対照**（正常な行は送る）を
//    必ず併せて見る。止めるだけのガードは「全部止める」でも緑になってしまう。
//
// 実行: node Form_G1/materials_autosend_test.cjs

const fs = require("fs");
const path = require("path");
const vm = require("vm");

const src = fs.readFileSync(
  process.argv[2] || path.join(__dirname, "GSE_G1_Form_Builder.gs"),
  "utf8"
);

/**
 * 二次元配列を Sheets 風に見せる最小の偽シート（1 始まりの座標）。
 * @param failWriteCol … この列番号への setValue を必ず失敗させる（書き込み失敗の再現用・任意）
 */
function makeSheet(grid, failWriteCol) {
  const cells = grid.map((row) => row.slice());
  function ensure(r, c) {
    while (cells.length < r) cells.push([]);
    const row = cells[r - 1];
    while (row.length < c) row.push("");
  }
  const sheet = {
    _cells: cells,
    _widths: {},
    getLastRow: () => cells.length,
    getLastColumn: () => cells.reduce((m, r) => Math.max(m, r.length), 0),
    setColumnWidth(c, w) {
      this._widths[c] = w;
    },
    insertColumnBefore(idx) {
      cells.forEach((row) => row.splice(idx - 1, 0, ""));
    },
    getRange(r, c, nr, nc) {
      const rows = nr === undefined ? 1 : nr;
      const colsN = nc === undefined ? 1 : nc;
      return {
        getRow: () => r,
        getSheet: () => sheet,
        getValue() {
          ensure(r, c);
          return cells[r - 1][c - 1];
        },
        setValue(v) {
          if (failWriteCol && c === failWriteCol) {
            throw new Error("TEST: この列は書けない (col " + c + ")");
          }
          ensure(r, c);
          cells[r - 1][c - 1] = v;
          return this;
        },
        getValues() {
          const out = [];
          for (let i = 0; i < rows; i++) {
            const row = [];
            for (let j = 0; j < colsN; j++) {
              ensure(r + i, c + j);
              row.push(cells[r + i - 1][c + j - 1]);
            }
            out.push(row);
          }
          return out;
        },
        setValues(vals) {
          vals.forEach((row, i) =>
            row.forEach((v, j) => {
              ensure(r + i, c + j);
              cells[r + i - 1][c + j - 1] = v;
            })
          );
          return this;
        },
        setFontWeight: () => sheet.getRange(r, c),
        setFontColor() {
          return this;
        },
        setBackground() {
          return this;
        },
        setWrap() {
          return this;
        },
        merge() {
          return this;
        },
        clearDataValidations() {
          return this;
        },
      };
    },
  };
  // setFontWeight はチェーンで使われるので自分自身を返す形に直す
  const origGetRange = sheet.getRange.bind(sheet);
  sheet.getRange = (...args) => {
    const rg = origGetRange(...args);
    rg.setFontWeight = () => rg;
    return rg;
  };
  return sheet;
}

/**
 * @param {object} opts
 *   runRows   … 「G1 実施トラッキング」のデータ行（ヘッダ行は RUN_HEADER から自動生成）
 *   roster    … Phase1 ロスター [[pid, name, email], ...]
 *   props     … Script Properties の初期値
 *   omitUrlCol… true なら「配布フォルダURL」列を持たない**移行前**のシートを作る
 */
function makeCtx(opts) {
  opts = opts || {};
  const logs = [];
  const sent = [];
  const drafts = [];

  // まず RUN_HEADER を取るためだけに素の文脈で 1 回評価する
  const probe = { Logger: { log() {} }, console };
  vm.createContext(probe);
  vm.runInContext(src, probe);
  let header = probe.RUN_HEADER.slice();
  if (opts.omitUrlCol) header = header.filter((h) => h !== "配布フォルダURL");

  const runGrid = [["banner"], header];
  (opts.runRows || []).forEach((r) => {
    const row = new Array(header.length).fill("");
    Object.keys(r).forEach((k) => {
      const i = header.indexOf(k);
      if (i < 0) throw new Error("テストの列名が RUN_HEADER に無い: " + k);
      row[i] = r[k];
    });
    runGrid.push(row);
  });

  const failWriteCol = opts.failWriteHeader ? header.indexOf(opts.failWriteHeader) + 1 : 0;
  const runSheet = makeSheet(runGrid, failWriteCol);
  const rosterSheet = makeSheet(opts.roster || []);
  const props = Object.assign({ G1_MGMT_SHEET_ID: "run-sheet" }, opts.props || {});

  const ctx = {
    Logger: { log: (m) => logs.push(String(m)) },
    console,
    PropertiesService: {
      getScriptProperties: () => ({
        getProperty: (k) => (k in props ? props[k] : null),
        setProperty: (k, v) => {
          props[k] = v;
        },
      }),
    },
    SpreadsheetApp: {
      openById: (id) => ({
        getSheetByName: (name) =>
          name === "参加者ロスター" ? rosterSheet : name === "G1 実施トラッキング" ? runSheet : null,
        getUrl: () => "https://example.invalid/sheet",
      }),
      flush: () => {},
      newDataValidation: () => ({ requireValueInList: () => ({ build: () => ({}) }) }),
    },
    MailApp: { sendEmail: (to, subject) => sent.push({ to, subject }) },
    GmailApp: { createDraft: (to, subject) => drafts.push({ to, subject }) },
    FormApp: { openById: () => ({}) },
    DriveApp: {},
    Session: {},
    LockService: {
      getScriptLock: () => ({
        waitLock: () => {
          if (opts.lockBusy) throw new Error("TEST: ロックを取れない");
        },
        releaseLock: () => {},
      }),
    },
    ScriptApp: { getProjectTriggers: () => [] },
    UrlFetchApp: {},
    Utilities: {},
    __logs: logs,
    __sent: sent,
    __drafts: drafts,
    __runSheet: runSheet,
  };
  vm.createContext(ctx);
  vm.runInContext(src, ctx);
  // ★ MGMT_SHEET_PROP_G1 が実際に何という名前でも、その値を "run-sheet" にしておく
  props[ctx.MGMT_SHEET_PROP_G1] = "run-sheet";
  ctx.PHASE1_MGMT_SHEET_ID = "roster-sheet";
  return ctx;
}

let failures = 0;
function ok(name, cond, detail) {
  if (cond) {
    console.log("  ✅ " + name);
  } else {
    failures++;
    console.log("  ❌ " + name + (detail ? "  … " + detail : ""));
  }
}

const GOOD_URL = "https://drive.google.com/drive/folders/1xzoU4wpEiBfiic-wKdtC2HTEweqoFzWq";
const ROSTER = [
  ["P015", "テスト太郎", "t15@example.com"],
  ["P016", "テスト次郎", "t16@example.com"],
  ["P017", "テスト三郎", "t17@example.com"],
  ["P018", "テスト四郎", "t18@example.com"],
  ["P019", "メール無し", ""],
];

console.log("1. 陽性対照 — 正常な行は送る（★ ガードが全部止めていないこと）");
{
  const ctx = makeCtx({
    runRows: [{ "P-ID": "P015", 配布フォルダURL: GOOD_URL }],
    roster: ROSTER,
  });
  ctx.g1AutoSendPendingMaterials();
  ok("1 通送った", ctx.__sent.length === 1, "sent=" + ctx.__sent.length);
  ok("宛先が P015 のもの", (ctx.__sent[0] || {}).to === "t15@example.com");
}

console.log("2. ガード 1 — キルスイッチ");
{
  const ctx = makeCtx({
    runRows: [{ "P-ID": "P015", 配布フォルダURL: GOOD_URL }],
    roster: ROSTER,
    props: { G1_MATERIALS_AUTOSEND_OFF: "1" },
  });
  ctx.g1AutoSendPendingMaterials();
  ok("1 通も送らない", ctx.__sent.length === 0, "sent=" + ctx.__sent.length);
}
{
  // ★ "false" は「止めない」。⚠️ 文字列 "false" が真になる罠を踏んでいないか。
  const ctx = makeCtx({
    runRows: [{ "P-ID": "P015", 配布フォルダURL: GOOD_URL }],
    roster: ROSTER,
    props: { G1_MATERIALS_AUTOSEND_OFF: "false" },
  });
  ctx.g1AutoSendPendingMaterials();
  ok('"false" では止まらない', ctx.__sent.length === 1, "sent=" + ctx.__sent.length);
}

console.log("3. ガード 2 — URL 形式");
{
  const bad = [
    ["http (https でない)", "http://drive.google.com/drive/folders/x"],
    ["別サイト", "https://example.com/drive/folders/x"],
    ["ただの文字列", "あとで貼る"],
    ["紛らわしいドメイン", "https://drive.google.com.evil.test/x"],
  ];
  bad.forEach(([name, url]) => {
    const ctx = makeCtx({ runRows: [{ "P-ID": "P015", 配布フォルダURL: url }], roster: ROSTER });
    ctx.g1AutoSendPendingMaterials();
    ok("止めた: " + name, ctx.__sent.length === 0, "sent=" + ctx.__sent.length);
  });
}

console.log("4. ガード 3 — 冪等（送信済みには送らない）");
{
  const ctx = makeCtx({
    runRows: [{ "P-ID": "P015", 配布フォルダURL: GOOD_URL, 課題文リンク送信日: new Date() }],
    roster: ROSTER,
  });
  ctx.g1AutoSendPendingMaterials();
  ok("送信日があれば送らない", ctx.__sent.length === 0, "sent=" + ctx.__sent.length);
}
{
  // ★ 2 回連続で発火しても 1 通のまま（トリガーは何度でも走る）
  const ctx = makeCtx({
    runRows: [{ "P-ID": "P015", 配布フォルダURL: GOOD_URL }],
    roster: ROSTER,
  });
  ctx.g1AutoSendPendingMaterials();
  ctx.g1AutoSendPendingMaterials();
  ok("2 回発火しても 1 通", ctx.__sent.length === 1, "sent=" + ctx.__sent.length);
}

console.log("5. ガード 4 — 1 回の上限");
{
  const ctx = makeCtx({
    // ★ 被験者ごとに別のフォルダなので URL も別（同じにするとガード 5 が止める = 正しい）
    runRows: [
      { "P-ID": "P015", 配布フォルダURL: GOOD_URL + "15" },
      { "P-ID": "P016", 配布フォルダURL: GOOD_URL + "16" },
      { "P-ID": "P017", 配布フォルダURL: GOOD_URL + "17" },
      { "P-ID": "P018", 配布フォルダURL: GOOD_URL + "18" },
    ],
    roster: ROSTER,
  });
  ctx.g1AutoSendPendingMaterials();
  ok("4 人いても 3 通まで", ctx.__sent.length === 3, "sent=" + ctx.__sent.length);
  ctx.g1AutoSendPendingMaterials();
  ok("次の発火で残り 1 通", ctx.__sent.length === 4, "sent=" + ctx.__sent.length);
}

console.log("6. メールが引けない行は飛ばす（★ 黙って落とさず理由を出す）");
{
  const ctx = makeCtx({
    runRows: [{ "P-ID": "P019", 配布フォルダURL: GOOD_URL }],
    roster: ROSTER,
  });
  ctx.g1AutoSendPendingMaterials();
  ok("送らない", ctx.__sent.length === 0);
  ok(
    "理由をログに出す",
    ctx.__logs.some((l) => l.indexOf("P019") >= 0 && l.indexOf("メール") >= 0),
    ctx.__logs.join(" / ")
  );
}

console.log("7. URL 未記入は「正常な待ち状態」（★ 警告を出さない）");
{
  const ctx = makeCtx({ runRows: [{ "P-ID": "P015" }], roster: ROSTER });
  ctx.g1AutoSendPendingMaterials();
  ok("送らない", ctx.__sent.length === 0);
  ok("⚠️ を出さない", !ctx.__logs.some((l) => l.indexOf("飛ばす") >= 0), ctx.__logs.join(" / "));
}

console.log("8. 移行関数");
{
  // 移行前のシート → 列が挿さり、コードと一致する
  const ctx = makeCtx({ omitUrlCol: true, runRows: [{ "P-ID": "P015" }], roster: ROSTER });
  ctx.migrateRunSheetAddUrlColumn();
  const header = ctx.__runSheet.getRange(2, 1, 1, ctx.RUN_HEADER.length).getValues()[0];
  ok("ヘッダが RUN_HEADER と一致", header.join("|") === ctx.RUN_HEADER.join("|"), header.join("|"));
  ok("P-ID が 1 列目に残っている", ctx.__runSheet.getRange(3, 1).getValue() === "P015");
}
{
  // 既に移行済み → 何もしない（冪等）
  const ctx = makeCtx({ runRows: [{ "P-ID": "P015" }], roster: ROSTER });
  const before = ctx.__runSheet.getLastColumn();
  ctx.migrateRunSheetAddUrlColumn();
  ok("列を増やさない", ctx.__runSheet.getLastColumn() === before);
}
{
  // ⚠️ 見覚えのない形 → 止める（黙って 1 列ずらさない）
  const ctx = makeCtx({ omitUrlCol: true, runRows: [{ "P-ID": "P015" }], roster: ROSTER });
  ctx.__runSheet.getRange(2, 3).setValue("知らない列");
  let threw = false;
  try {
    ctx.migrateRunSheetAddUrlColumn();
  } catch (e) {
    threw = true;
  }
  ok("止めた", threw);
}

console.log("9. preview は 1 通も送らない");
{
  const ctx = makeCtx({
    runRows: [{ "P-ID": "P015", 配布フォルダURL: GOOD_URL }],
    roster: ROSTER,
  });
  ctx.previewPendingTaskMaterials();
  ok("送信ゼロ", ctx.__sent.length === 0 && ctx.__drafts.length === 0);
  ok(
    "対象を出す",
    ctx.__logs.some((l) => l.indexOf("P015") >= 0),
    ctx.__logs.join(" / ")
  );
}

console.log("10. ガード 5 — URL の重複（★ 別の被験者の URL を貼った事故）");
{
  // 同じ URL を 2 人に貼った → どちらにも送らない
  const ctx = makeCtx({
    runRows: [
      { "P-ID": "P015", 配布フォルダURL: GOOD_URL },
      { "P-ID": "P016", 配布フォルダURL: GOOD_URL },
    ],
    roster: ROSTER,
  });
  ctx.g1AutoSendPendingMaterials();
  ok("1 通も送らない", ctx.__sent.length === 0, "sent=" + ctx.__sent.length);
  ok(
    "両方の P-ID を理由に挙げる",
    ctx.__logs.some((l) => l.indexOf("P015") >= 0 && l.indexOf("P016") >= 0),
    ctx.__logs.join(" / ")
  );
}
{
  // ★ 既に P015 へ送った URL を P016 に貼った → 送信済みの行も数に入れるので捕まる
  const ctx = makeCtx({
    runRows: [
      { "P-ID": "P015", 配布フォルダURL: GOOD_URL, 課題文リンク送信日: new Date() },
      { "P-ID": "P016", 配布フォルダURL: GOOD_URL },
    ],
    roster: ROSTER,
  });
  ctx.g1AutoSendPendingMaterials();
  ok("送信済みの行とも突き合わせる", ctx.__sent.length === 0, "sent=" + ctx.__sent.length);
}
{
  // ★ 陽性対照: 違う URL なら 2 人とも送る（重複検出が全部止めていないこと）
  const ctx = makeCtx({
    runRows: [
      { "P-ID": "P015", 配布フォルダURL: GOOD_URL },
      { "P-ID": "P016", 配布フォルダURL: GOOD_URL + "2" },
    ],
    roster: ROSTER,
  });
  ctx.g1AutoSendPendingMaterials();
  ok("違う URL なら 2 通", ctx.__sent.length === 2, "sent=" + ctx.__sent.length);
}

console.log("11. ガード 6 — 排他制御（トリガーの重なり・手動実行との衝突）");
{
  const ctx = makeCtx({
    runRows: [{ "P-ID": "P015", 配布フォルダURL: GOOD_URL }],
    roster: ROSTER,
    lockBusy: true,
  });
  ctx.g1AutoSendPendingMaterials();
  ok("ロックが取れなければ送らない", ctx.__sent.length === 0, "sent=" + ctx.__sent.length);
}

console.log("12. ★ 送信は済んだが送信日を書けない（放置すると再送される）");
{
  const ctx = makeCtx({
    runRows: [{ "P-ID": "P015", 配布フォルダURL: GOOD_URL }],
    roster: ROSTER,
    failWriteHeader: "課題文リンク送信日",
  });
  ctx.g1AutoSendPendingMaterials();
  ok("メールは送られている", ctx.__sent.length === 1, "sent=" + ctx.__sent.length);
  ok(
    "★ 二重送信の恐れをログに出す",
    ctx.__logs.some((l) => l.indexOf("二重送信") >= 0),
    ctx.__logs.join(" / ")
  );
  const header = ctx.RUN_HEADER;
  const noteCol = header.indexOf("備考") + 1;
  const note = String(ctx.__runSheet.getRange(3, noteCol).getValue());
  ok("備考にフラグが立つ", note.indexOf("送信済") >= 0, "note=" + note);
}

console.log("");
if (failures) {
  console.log("❌ " + failures + " 件失敗");
  process.exit(1);
}
console.log("✅ すべて通りました");
