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
  opts = Object.assign({ folders: FOLDERS }, opts || {});
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
    // ★ フォーム回答を最小限だけ真似る。opts.formResponses は {formId: [{設問: 値}]}。
    FormApp: {
      openById: (id) => ({
        getResponses: () =>
          ((opts.formResponses || {})[id] || []).map((ans) => ({
            getItemResponses: () =>
              Object.keys(ans).map((title) => ({
                getItem: () => ({ getTitle: () => title }),
                getResponse: () => ans[title],
              })),
          })),
      }),
    },
    // ★ Drive のフォルダを最小限だけ真似る。opts.folders は {id: {name, parent, access}}。
    //   id が opts.folders に無ければ「開けない」= 実 Drive の getFolderById が投げるのと同じ。
    DriveApp: {
      getFolderById: (id) => {
        const f = (opts.folders || {})[id];
        if (!f) throw new Error("TEST: そんなフォルダは無い (" + id + ")");
        return {
          getName: () => f.name,
          getSharingAccess: () => f.access,
          getFiles: () => {
            const names = f.files || [];
            let i = 0;
            return {
              hasNext: () => i < names.length,
              next: () => ({ getName: () => names[i++] }),
            };
          },
          getParents: () => {
            const list = f.parent ? [f.parent] : [];
            let i = 0;
            return {
              hasNext: () => i < list.length,
              next: () => ({ getId: () => list[i++] }),
            };
          },
        };
      },
    },
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

// ★ 実コードの G1_MATERIALS_PARENT_ID と同じ値。ずれたらガード 7 の検査が空振りする。
const PARENT_ID = "1qhl28IDeh-19upuZf_YxPwwdq_d9xVcI";
const urlFor = (pid) => "https://drive.google.com/drive/folders/FOLDER-" + pid;
/** 既定の Drive: P015..P019 のフォルダが親の下にあり、リンク共有済み。 */
const FOLDERS = { [PARENT_ID]: { name: "G1_課題ページ_被験者別", access: "PRIVATE" } };
["P015", "P016", "P017", "P018", "P019"].forEach((p) => {
  FOLDERS["FOLDER-" + p] = { name: p, parent: PARENT_ID, access: "ANYONE_WITH_LINK" };
});
const GOOD_URL = urlFor("P015");
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
      { "P-ID": "P015", 配布フォルダURL: urlFor("P015") },
      { "P-ID": "P016", 配布フォルダURL: urlFor("P016") },
      { "P-ID": "P017", 配布フォルダURL: urlFor("P017") },
      { "P-ID": "P018", 配布フォルダURL: urlFor("P018") },
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
      { "P-ID": "P015", 配布フォルダURL: urlFor("P015") },
      { "P-ID": "P016", 配布フォルダURL: urlFor("P016") },
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

console.log("13. ガード 7 — フォルダの実体（★ 親を非公開に戻した分、ここが受け皿）");
{
  // (a) ★★ 親フォルダの URL を貼った = 全被験者分が見える
  const ctx = makeCtx({
    runRows: [{ "P-ID": "P015", 配布フォルダURL: "https://drive.google.com/drive/folders/" + PARENT_ID }],
    roster: ROSTER,
  });
  ctx.g1AutoSendPendingMaterials();
  ok("親の URL は送らない", ctx.__sent.length === 0, "sent=" + ctx.__sent.length);
  ok(
    "「親」だと理由に書く",
    ctx.__logs.some((l) => l.indexOf("親") >= 0),
    ctx.__logs.join(" / ")
  );
}
{
  // (b) 別の被験者のフォルダ（名前が P-ID と違う）
  const ctx = makeCtx({
    runRows: [{ "P-ID": "P015", 配布フォルダURL: urlFor("P016") }],
    roster: ROSTER,
  });
  ctx.g1AutoSendPendingMaterials();
  ok("別の被験者のフォルダは送らない", ctx.__sent.length === 0, "sent=" + ctx.__sent.length);
}
{
  // (c) 配布用の親の下に無い
  const folders = Object.assign({}, FOLDERS, {
    "FOLDER-P015": { name: "P015", parent: "よそのフォルダ", access: "ANYONE_WITH_LINK" },
  });
  const ctx = makeCtx({
    runRows: [{ "P-ID": "P015", 配布フォルダURL: GOOD_URL }],
    roster: ROSTER,
    folders: folders,
  });
  ctx.g1AutoSendPendingMaterials();
  ok("親の下に無ければ送らない", ctx.__sent.length === 0, "sent=" + ctx.__sent.length);
}
{
  // (d) ★ 共有し忘れ — 送っても被験者は開けない
  const folders = Object.assign({}, FOLDERS, {
    "FOLDER-P015": { name: "P015", parent: PARENT_ID, access: "PRIVATE" },
  });
  const ctx = makeCtx({
    runRows: [{ "P-ID": "P015", 配布フォルダURL: GOOD_URL }],
    roster: ROSTER,
    folders: folders,
  });
  ctx.g1AutoSendPendingMaterials();
  ok("共有し忘れなら送らない", ctx.__sent.length === 0, "sent=" + ctx.__sent.length);
  ok(
    "共有せよと理由に書く",
    ctx.__logs.some((l) => l.indexOf("リンクを知っている全員") >= 0),
    ctx.__logs.join(" / ")
  );
}
{
  // (e) 存在しない / 消された ID
  const ctx = makeCtx({
    runRows: [{ "P-ID": "P015", 配布フォルダURL: urlFor("存在しない") }],
    roster: ROSTER,
  });
  ctx.g1AutoSendPendingMaterials();
  ok("開けないフォルダは送らない", ctx.__sent.length === 0, "sent=" + ctx.__sent.length);
}
{
  // (f) /folders/<ID> の形でない Drive URL
  const ctx = makeCtx({
    runRows: [{ "P-ID": "P015", 配布フォルダURL: "https://drive.google.com/file/d/abc/view" }],
    roster: ROSTER,
  });
  ctx.g1AutoSendPendingMaterials();
  ok("フォルダ URL でなければ送らない", ctx.__sent.length === 0, "sent=" + ctx.__sent.length);
}

console.log("14. refreshG1RunSheet — 導出列の自動集計");
{
  const SUBMIT_FOLDER = "SUBMIT-FOLDER";
  const folders = Object.assign({}, FOLDERS, {
    [SUBMIT_FOLDER]: {
      name: "提出物",
      access: "PRIVATE",
      files: [
        // P015: block01..03 の 3 種類（★ 同じ block の重複は 1 と数える）
        "P015_block01_gse_20260810_100000.age",
        "P015_block02_gse_20260810_101000.age",
        "P015_block02_gse_20260810_101500_2.age",
        "P015_block03_gse_20260810_102000.age",
        // P016: 1 種類だけ。⚠️ 日付が P015 より前 = 行ごとに独立して見ていること
        "P016_block01_gse_20260808_090000.age",
        // ★ 形が違うものは無視する（陰性対照）
        "readme.txt",
        "P015_block01.age",
      ],
    },
  });
  const ctx = makeCtx({
    runRows: [{ "P-ID": "P015" }, { "P-ID": "P016" }],
    roster: ROSTER,
    folders: folders,
    props: { G1_SUBMIT_FOLDER_ID: SUBMIT_FOLDER },
    formResponses: {
      // G1-M: P015 はブロック 3,4,5（★ 5 は 2 回答えている → 異なり数 3）
      "1iDcr0uc_51dEEI_idyJhcozYMX02N3ug-JQ7zSVMHIA": [
        { 被験者ID: "P015", ブロック番号: "3" },
        { 被験者ID: "P015", ブロック番号: "4" },
        { 被験者ID: "P015", ブロック番号: "5" },
        { 被験者ID: "P015", ブロック番号: "5" },
        { 被験者ID: "P016", ブロック番号: "3" },
      ],
      // G1-S: P015 のみ回答あり
      "1ScM_420irB8DUA8EFYyDJBaPBR-_lOa4evtveQBVWjU": [{ 被験者ID: "P015" }],
    },
  });
  ctx.refreshG1RunSheet();
  const H = ctx.RUN_HEADER;
  const cell = (row, name) => ctx.__runSheet.getRange(row, H.indexOf(name) + 1).getValue();

  ok("G1-C 同意 が埋まる", cell(3, "G1-C 同意") === "はい", String(cell(3, "G1-C 同意")));
  ok("完了ブロック数 = 3（重複を数えない）", cell(3, "完了ブロック数(/10)") === 3, String(cell(3, "完了ブロック数(/10)")));
  ok("G1-M 回答数 = 3（同じブロックの重複を数えない）", cell(3, "G1-M 回答数(/7)") === 3, String(cell(3, "G1-M 回答数(/7)")));
  ok("G1-S 回答 = はい", cell(3, "G1-S 回答") === "はい", String(cell(3, "G1-S 回答")));
  ok(
    "実施日 = 最も早い .age の日付",
    // ⚠️ ★ `instanceof Date` は使えない。vm の中で作った Date は**別レルム**なので常に false になる
    //    （実測で踏んだ。値は正しいのにテストだけ赤くなる = 偽陰性）。
    Object.prototype.toString.call(cell(3, "実施日")) === "[object Date]" &&
      cell(3, "実施日").getFullYear() === 2026 &&
      cell(3, "実施日").getMonth() === 7 &&
      cell(3, "実施日").getDate() === 10,
    String(cell(3, "実施日"))
  );
  ok("P016 は独立に数える（完了 1）", cell(4, "完了ブロック数(/10)") === 1, String(cell(4, "完了ブロック数(/10)")));
  ok("P016 は G1-S 未回答なので空", String(cell(4, "G1-S 回答")).trim() === "", String(cell(4, "G1-S 回答")));
  ok(
    "⚠️ 判定に関わる列は触らない",
    ["実施形態", "配置(A/B)", "撤回/除外", "verify-blocks 実施", "validate_blocks 緑", "gse-dataset 送付"]
      .every((h) => String(cell(3, h)).trim() === ""),
    "どれかが埋まっている"
  );
}
{
  // ⚠️ ★ 手入力の「実施日」を上書きしない
  const SUBMIT_FOLDER = "SUBMIT-FOLDER";
  const folders = Object.assign({}, FOLDERS, {
    [SUBMIT_FOLDER]: { name: "提出物", access: "PRIVATE", files: ["P015_block01_gse_20260810_100000.age"] },
  });
  const ctx = makeCtx({
    runRows: [{ "P-ID": "P015", 実施日: "研究者が書いた値" }],
    roster: ROSTER,
    folders: folders,
    props: { G1_SUBMIT_FOLDER_ID: SUBMIT_FOLDER },
  });
  ctx.refreshG1RunSheet();
  const H = ctx.RUN_HEADER;
  ok(
    "実施日の手入力を上書きしない",
    ctx.__runSheet.getRange(3, H.indexOf("実施日") + 1).getValue() === "研究者が書いた値"
  );
}
{
  // フォルダ ID 未設定 → 他の列は動き、飛ばしたことを言う
  const ctx = makeCtx({ runRows: [{ "P-ID": "P015" }], roster: ROSTER });
  ctx.refreshG1RunSheet();
  const H = ctx.RUN_HEADER;
  ok(
    "未設定でも G1-C 同意 は埋まる",
    ctx.__runSheet.getRange(3, H.indexOf("G1-C 同意") + 1).getValue() === "はい"
  );
  ok(
    "飛ばしたことをログに出す",
    ctx.__logs.some((l) => l.indexOf("G1_SUBMIT_FOLDER_ID") >= 0),
    ctx.__logs.join(" / ")
  );
}
{
  // ⚠️ ヘッダがずれていたら 1 行も書かない
  const ctx = makeCtx({ omitUrlCol: true, runRows: [{ "P-ID": "P015" }], roster: ROSTER });
  ctx.refreshG1RunSheet();
  const before = ctx.__runSheet.getRange(3, 3).getValue();
  ok("ヘッダ不一致なら集計しない", String(before).trim() === "", String(before));
  ok(
    "理由をログに出す",
    ctx.__logs.some((l) => l.indexOf("ヘッダ") >= 0),
    ctx.__logs.join(" / ")
  );
}

console.log("15. 受付メールにアプリのダウンロードリンクが入る");
{
  const ctx = makeCtx({});
  const body = ctx.g1RegisterAckBody_("P015");
  ok("アプリのリンクが本文にある", body.indexOf(ctx.G1_APP_DOWNLOAD_URL) >= 0);
  ok("P-ID も入っている", body.indexOf("P015") >= 0);
  ok(
    "⚠️ 課題ページは別便だと書いてある",
    body.indexOf("別便") >= 0,
    "「別便」が無いと被験者はアプリだけで始めようとする"
  );
  const mat = ctx.g1MaterialsBody_("P015", GOOD_URL);
  ok("事前資料メールに課題ページのリンクがある", mat.indexOf(GOOD_URL) >= 0);
  ok(
    "★「閲覧のみ」という実態と違う表現が消えている",
    mat.indexOf("閲覧のみ") < 0,
    "在宅実施では被験者が blockNN.html を手元に持つ"
  );
}

console.log("");
if (failures) {
  console.log("❌ " + failures + " 件失敗");
  process.exit(1);
}
console.log("✅ すべて通りました");
