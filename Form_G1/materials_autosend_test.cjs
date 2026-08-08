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
    appendRow(vals) {
      cells.push(vals.slice());
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
          getId: () => id,
          getFoldersByName: (name) => {
            const hits = Object.keys(opts.folders || {}).filter(
              (k) => (opts.folders[k].parent === id) && opts.folders[k].name === name
            );
            let i = 0;
            return {
              hasNext: () => i < hits.length,
              next: () => {
                const fid = hits[i++];
                return { getId: () => fid, getName: () => opts.folders[fid].name };
              },
            };
          },
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
    runRows: [{ "P-ID": "P015", 配布フォルダURL: GOOD_URL, 課題ページ送付日: new Date() }],
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
      { "P-ID": "P015", 配布フォルダURL: GOOD_URL, 課題ページ送付日: new Date() },
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
    failWriteHeader: "課題ページ送付日",
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
    ["実施形態", "撤回/除外", "verify-blocks 実施", "validate_blocks 緑", "gse-dataset 送付"]
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

console.log("16. ★ 受付メール 1 通で課題ページまで渡す（pre-provision）");
{
  const ctx = makeCtx({});
  const found = ctx.g1MaterialsUrlForPid_("P015");
  ok("用意済みなら URL が返る", found.url === urlFor("P015"), found.url + " / " + found.problem);
  const body = ctx.g1RegisterAckBody_("P015", found.url);
  ok("受付メールにアプリのリンク", body.indexOf(ctx.G1_APP_DOWNLOAD_URL) >= 0);
  ok("受付メールに課題ページのリンク", body.indexOf(found.url) >= 0);
  ok("「別便」と書かない", body.indexOf("別便のメール") < 0, "1 通で渡すのに別便と書くと混乱する");
  ok("★ 専用だと明示する", body.indexOf("あなた専用") >= 0);
}
{
  // 用意されていない P-ID → 「別便」に落ちる（★ 壊れない）
  const ctx = makeCtx({});
  const found = ctx.g1MaterialsUrlForPid_("P099");
  ok("未用意なら URL は空", found.url === "", found.url);
  ok("理由を返す", found.problem.length > 0, found.problem);
  const body = ctx.g1RegisterAckBody_("P099", found.url);
  ok("別便と案内する", body.indexOf("別便のメール") >= 0);
  ok("それでもアプリのリンクはある", body.indexOf(ctx.G1_APP_DOWNLOAD_URL) >= 0);
}
{
  // ⚠️ 共有し忘れのフォルダは載せない（ガード 7 を通している）
  const folders = Object.assign({}, FOLDERS, {
    "FOLDER-P015": { name: "P015", parent: PARENT_ID, access: "PRIVATE" },
  });
  const ctx = makeCtx({ folders: folders });
  ok("共有前なら載せない", ctx.g1MaterialsUrlForPid_("P015").url === "");
}
{
  // ⚠️ 同名フォルダが 2 つ → どちらか決められないので載せない
  const folders = Object.assign({}, FOLDERS, {
    "FOLDER-P015b": { name: "P015", parent: PARENT_ID, access: "ANYONE_WITH_LINK" },
  });
  const ctx = makeCtx({ folders: folders });
  const found = ctx.g1MaterialsUrlForPid_("P015");
  ok("同名 2 つなら載せない", found.url === "", found.url);
  ok("理由に「2 つ以上」と書く", found.problem.indexOf("2 つ以上") >= 0, found.problem);
}

console.log("17. ★ 1 通で渡したら 2 通目が飛ばない（冪等キーを閉じる）");
{
  const ctx = makeCtx({ runRows: [], roster: [] });
  // G1-C の提出を模す
  const resp = {
    getItemResponses: () => [
      { getItem: () => ({ getTitle: () => ctx.Q_C_NAME }), getResponse: () => "試験 太郎" },
      { getItem: () => ({ getTitle: () => ctx.Q_C_EMAIL }), getResponse: () => "t@example.com" },
    ],
  };
  ctx.onG1ConsentSubmit({ response: resp });
  ok("受付メールが 1 通", ctx.__sent.length === 1, "sent=" + ctx.__sent.length);

  const H = ctx.RUN_HEADER;
  const rows = ctx.__runSheet._cells.length;
  const pidCell = String(ctx.__runSheet.getRange(rows, H.indexOf("P-ID") + 1).getValue());
  ok("トラッキング行ができる", /^P\d{3}$/.test(pidCell), pidCell);

  // ★ 発番された P-ID のフォルダが用意されていれば URL と送信日が入るはず
  const url = String(ctx.__runSheet.getRange(rows, H.indexOf("配布フォルダURL") + 1).getValue());
  const sent = ctx.__runSheet.getRange(rows, H.indexOf("課題ページ送付日") + 1).getValue();
  if (pidCell === "P001") {
    // 既定の FOLDERS には P001 が無いので「別便」経路。★ 記録もされない = 2 通目が正しく飛ぶ
    ok("未用意なら送信日を埋めない（2 通目に任せる）", String(sent).trim() === "", String(sent));
  }
  // 用意済みの P-ID で改めて確かめる
  // ⚠️★ ロスターは **1 行目がヘッダ**である（`g1NextParticipantId_` は `last > 1` のときだけ読む）。
  //    1 行だけのロスターを渡すと採番が P001 に落ちる（2026-08-07 に実測で踏んだ）。
  const ctx2 = makeCtx({ runRows: [], roster: [["P-ID", "氏名", "メール"], ["P014", "", ""]] });
  const resp2 = {
    getItemResponses: () => [
      { getItem: () => ({ getTitle: () => ctx2.Q_C_EMAIL }), getResponse: () => "t15@example.com" },
    ],
  };
  ctx2.onG1ConsentSubmit({ response: resp2 }); // → P015 が発番される
  const H2 = ctx2.RUN_HEADER;
  const r2 = ctx2.__runSheet._cells.length;
  ok("P015 が発番された", String(ctx2.__runSheet.getRange(r2, H2.indexOf("P-ID") + 1).getValue()) === "P015");
  ok(
    "★ 配布フォルダURL が記録される",
    String(ctx2.__runSheet.getRange(r2, H2.indexOf("配布フォルダURL") + 1).getValue()) === urlFor("P015")
  );
  ok(
    "★ 課題ページ送付日 が記録される",
    String(ctx2.__runSheet.getRange(r2, H2.indexOf("課題ページ送付日") + 1).getValue()).trim() !== ""
  );
  // ⚠️ ここが本題: 2 通目が飛ばないこと
  const before = ctx2.__sent.length;
  ctx2.g1AutoSendPendingMaterials();
  ok("⚠️ 2 通目が飛ばない", ctx2.__sent.length === before, "sent=" + ctx2.__sent.length);
}

console.log("18. ★ checkMaterialsProvisioning — ロスター全体を見る（過去参加者が主の運用）");
{
  // ⚠️ ロスターは 1 行目がヘッダ。★ ここでは P006..P010 が「過去の参加者」である。
  const roster = [
    ["P-ID", "氏名", "メール"],
    ["P006", "", ""],
    ["P007", "", ""],
    ["P008", "", ""],
    ["P009", "", ""],
    ["P010", "", ""],
  ];
  {
    const ctx = makeCtx({ roster: roster });
    const ids = ctx.g1RosterParticipantIds_(
      ctx.SpreadsheetApp.openById("roster-sheet").getSheetByName("参加者ロスター")
    );
    ok("実在する P-ID を全部拾う", ids.join(",") === "P006,P007,P008,P009,P010", ids.join(","));
    ok("ヘッダ行を拾わない", ids.indexOf("P-ID") < 0);
  }
  {
    // ⚠️ 重複と並び順の乱れを畳む（★ 手入力のロスターは順番が保証されない）
    const ctx = makeCtx({
      roster: [["P-ID"], ["P010"], ["P006"], ["P010"], ["（欠番）"], ["P008"]],
    });
    const ids = ctx.g1RosterParticipantIds_(
      ctx.SpreadsheetApp.openById("roster-sheet").getSheetByName("参加者ロスター")
    );
    ok("重複を畳んで昇順にする", ids.join(",") === "P006,P008,P010", ids.join(","));
  }
  {
    // ★★ 本題: 既定の Drive には P015..P019 しか無い。旧版（次の 5 人だけ見る）は
    //    P011..P015 を見て「先頭 1 人ぶんは渡せます」と**緑寄りに**報告していた。
    //    ⚠️ 実際には過去参加者 P006..P010 が 1 人も用意できていない。
    const ctx = makeCtx({ roster: roster });
    ctx.checkMaterialsProvisioning();
    const log = ctx.__logs.join("\n");
    ok("既存 5 人ぶんの未用意を名指しする", log.indexOf("P006 P007 P008 P009 P010") >= 0, log);
    ok("★ 既存が欠けていることを警告する", log.indexOf("既存参加者 5 / 5 人ぶんが未用意") >= 0);
    ok("再登録すると別便になると書く", log.indexOf("別便") >= 0);
    // ★ 既存と新規を**別に**数えていること（合算すると、どちらが欠けているか分からなくなる）
    ok("新規ぶんも別枠で見る", log.indexOf("P011 (新規)") >= 0 && log.indexOf("P013 (新規)") >= 0, log);
    ok("新規が未用意なら 2 便と言う", log.indexOf("**新規**の登録が来ると") >= 0, log);
    // ⚠️ 陰性対照: 読むだけであって、何も送らない・作らない
    ok("1 通も送らない", ctx.__sent.length === 0 && ctx.__drafts.length === 0);
  }
  {
    // ★ 陽性対照: 過去参加者ぶんが全部そろっていれば緑になる（★ 全部止めるガードではない）
    const folders = Object.assign({}, FOLDERS);
    ["P006", "P007", "P008", "P009", "P010"].forEach((p) => {
      folders["FOLDER-" + p] = { name: p, parent: PARENT_ID, access: "ANYONE_WITH_LINK" };
    });
    const ctx = makeCtx({ roster: roster, folders: folders });
    ctx.checkMaterialsProvisioning();
    const log = ctx.__logs.join("\n");
    ok("★ 全員そろえば緑", log.indexOf("既存 5 人ぶんは全員") >= 0, log);
    ok("未用意の警告は出ない", log.indexOf("人ぶんが未用意") < 0, log);
  }
  {
    // ⚠️ 共有し忘れが 1 人いれば、その 1 人だけ名指しされる（ガード 7 を通している）
    const folders = Object.assign({}, FOLDERS);
    ["P006", "P007", "P008", "P009", "P010"].forEach((p) => {
      folders["FOLDER-" + p] = {
        name: p,
        parent: PARENT_ID,
        access: p === "P008" ? "PRIVATE" : "ANYONE_WITH_LINK",
      };
    });
    const ctx = makeCtx({ roster: roster, folders: folders });
    ctx.checkMaterialsProvisioning();
    const log = ctx.__logs.join("\n");
    ok("共有し忘れ 1 人を名指し", log.indexOf("既存参加者 1 / 5 人ぶんが未用意: P008") >= 0, log);
    ok("理由が「まだ共有されていません」", log.indexOf("まだ共有されていません") >= 0);
  }
  {
    // ⚠️ ロスターが空（★ 管理シートを取り違えた形）→ 黙って緑にしない
    const ctx = makeCtx({ roster: [["P-ID", "氏名", "メール"]] });
    ctx.checkMaterialsProvisioning();
    const log = ctx.__logs.join("\n");
    ok("空ロスターを警告する", log.indexOf("P-ID が 1 つもありません") >= 0, log);
    ok("★「全員そろった」とは言わない", log.indexOf("人ぶんは全員") < 0, log);
  }
  {
    // ⚠️★ 人数が上限を超えたら「切ったこと」を必ず言う（★ 無言の打ち切りは「全部見た」と読まれる）
    const many = [["P-ID", "氏名", "メール"]];
    const folders = Object.assign({}, FOLDERS);
    for (let i = 1; i <= 45; i++) {
      const p = "P" + ("000" + i).slice(-3);
      many.push([p, "", ""]);
      folders["FOLDER-" + p] = { name: p, parent: PARENT_ID, access: "ANYONE_WITH_LINK" };
    }
    const ctx = makeCtx({ roster: many, folders: folders });
    ctx.checkMaterialsProvisioning(0);
    const log = ctx.__logs.join("\n");
    ok("★ 打ち切ったことを言う", log.indexOf("残り 5 人は未検査") >= 0, log.slice(0, 400));
    // ⚠️ 本丸: 見ていない人がいるのに「全員そろった」と読ませない
    ok("★「全員」と言わない", log.indexOf("人ぶんは全員") < 0, log.slice(0, 400));
    ok("見た分は緑と言う", log.indexOf("見た 40 人ぶんは") >= 0, log.slice(0, 400));
  }
  {
    // ★ 陰性対照: 上限以下なら打ち切りの警告は出ないし、「全員」と言ってよい
    const few = [["P-ID", "氏名", "メール"]];
    const folders = Object.assign({}, FOLDERS);
    ["P015", "P016", "P017"].forEach((p) => few.push([p, "", ""]));
    const ctx = makeCtx({ roster: few, folders: folders });
    ctx.checkMaterialsProvisioning(0);
    const log = ctx.__logs.join("\n");
    ok("上限以下なら打ち切りを言わない", log.indexOf("未検査") < 0, log);
    ok("★ 全員そろえば「全員」と言う", log.indexOf("既存 3 人ぶんは全員") >= 0, log);
  }
  {
    // ★ 先読み 0 なら新規の話をしない（既存の話だけ見たいとき）
    const ctx = makeCtx({ roster: roster });
    ctx.checkMaterialsProvisioning(0);
    const log = ctx.__logs.join("\n");
    ok("先読み 0 で新規の行が出ない", log.indexOf("新規は先頭") < 0 && log.indexOf("(新規)") < 0, log);
    ok("既存の判定は出る", log.indexOf("既存参加者 5 / 5 人ぶんが未用意") >= 0);
  }
}

console.log("19. ★ フォルダ名は「P-ID」と「G1課題文_P-ID」の 2 通りだけ認める");
{
  // ★ 陽性対照 1: 裸の P-ID（従来の名前）
  const ctx = makeCtx({});
  ok("裸の P-ID で引ける", ctx.g1MaterialsUrlForPid_("P015").url === urlFor("P015"));
}
{
  // ★ 陽性対照 2: 接頭辞つき（★ 実運用の名前。2026-08-07 に実 Drive で確認した形）
  const folders = { [PARENT_ID]: { name: "G1_課題ページ_被験者別", access: "PRIVATE" } };
  folders["FOLDER-P015"] = { name: "G1課題文_P015", parent: PARENT_ID, access: "ANYONE_WITH_LINK" };
  const ctx = makeCtx({ folders: folders });
  const found = ctx.g1MaterialsUrlForPid_("P015");
  ok("接頭辞つきでも引ける", found.url === urlFor("P015"), found.url + " / " + found.problem);
  // ⚠️ ガード 7 も同じ名前を認めていること（片方だけ直すと「探せたのに弾かれる」）
  ok("ガード 7 も通る", ctx.g1MaterialsFolderProblem_(urlFor("P015"), "P015") === "",
     ctx.g1MaterialsFolderProblem_(urlFor("P015"), "P015"));
}
{
  // ⚠️★ 本丸: 前方一致に**なっていない**こと。P01 系の名前で P010 を掴まない
  const folders = { [PARENT_ID]: { name: "G1_課題ページ_被験者別", access: "PRIVATE" } };
  folders["FOLDER-P010"] = { name: "G1課題文_P010", parent: PARENT_ID, access: "ANYONE_WITH_LINK" };
  const ctx = makeCtx({ folders: folders });
  ok("★ P01 で P010 を掴まない", ctx.g1MaterialsUrlForPid_("P01").url === "");
  ok("★ P0 で P010 を掴まない", ctx.g1MaterialsUrlForPid_("P0").url === "");
}
{
  // ⚠️★ 余計な語がついた名前は認めない（「G1課題文_P015_旧」を掴まない）
  const folders = { [PARENT_ID]: { name: "G1_課題ページ_被験者別", access: "PRIVATE" } };
  folders["FOLDER-old"] = { name: "G1課題文_P015_旧", parent: PARENT_ID, access: "ANYONE_WITH_LINK" };
  const ctx = makeCtx({ folders: folders });
  const found = ctx.g1MaterialsUrlForPid_("P015");
  ok("★ 後ろに語がつく名前は掴まない", found.url === "", found.url);
  // ⚠️ ガード 7 側も同じ（URL を直に貼られた場合の受け皿）
  const prob = ctx.g1MaterialsFolderProblem_(urlFor("old"), "P015");
  ok("ガード 7 も弾く", prob.indexOf("P-ID と違います") >= 0, prob);
}
{
  // ⚠️★ 2 通り認めた副作用: 両方の名前が同時に存在したら**送らない**
  const folders = { [PARENT_ID]: { name: "G1_課題ページ_被験者別", access: "PRIVATE" } };
  folders["FOLDER-A"] = { name: "P015", parent: PARENT_ID, access: "ANYONE_WITH_LINK" };
  folders["FOLDER-B"] = { name: "G1課題文_P015", parent: PARENT_ID, access: "ANYONE_WITH_LINK" };
  const ctx = makeCtx({ folders: folders });
  const found = ctx.g1MaterialsUrlForPid_("P015");
  ok("★ 両方あるなら送らない", found.url === "", found.url);
  ok("理由に「2 つ以上」と書く", found.problem.indexOf("2 つ以上") >= 0, found.problem);
}
{
  // ⚠️ 接頭辞つきでも共有し忘れは止まる（ガード 7 を通していることの確認）
  const folders = { [PARENT_ID]: { name: "G1_課題ページ_被験者別", access: "PRIVATE" } };
  folders["FOLDER-P015"] = { name: "G1課題文_P015", parent: PARENT_ID, access: "PRIVATE" };
  const ctx = makeCtx({ folders: folders });
  const found = ctx.g1MaterialsUrlForPid_("P015");
  ok("★ 共有前なら接頭辞つきでも載せない", found.url === "", found.url);
  ok("理由が「まだ共有されていません」", found.problem.indexOf("まだ共有されていません") >= 0, found.problem);
}
{
  // ★ 実運用そのまま: P006-P020 が接頭辞つきで全部そろっている状態を checkMaterialsProvisioning が緑と読む
  const roster = [["P-ID", "氏名", "メール"]];
  const folders = { [PARENT_ID]: { name: "G1_課題ページ_被験者別", access: "PRIVATE" } };
  for (let i = 6; i <= 20; i++) {
    const p = "P" + ("000" + i).slice(-3);
    if (i <= 14) roster.push([p, "", ""]);
    folders["FOLDER-" + p] = { name: "G1課題文_" + p, parent: PARENT_ID, access: "ANYONE_WITH_LINK" };
  }
  const ctx = makeCtx({ roster: roster, folders: folders });
  ctx.checkMaterialsProvisioning();
  const log = ctx.__logs.join("\n");
  ok("★ 実運用の形で既存が全員そろう", log.indexOf("既存 9 人ぶんは全員") >= 0, log.slice(0, 500));
  ok("★ 新規 3 人ぶんも用意できている", log.indexOf("新規は先頭 3 人ぶん") >= 0, log.slice(-400));
  ok("未用意の警告は出ない", log.indexOf("人ぶんが未用意") < 0);
  // ⚠️★ 案内の範囲は**いま見た P-ID から作る**（ハードコードすると実運用とずれる。
  //    2026-08-07 の実機ログに P001-P015 という古い案内が残っていた）
  ok("★ 案内の範囲が実運用と一致する", log.indexOf("--range P006 P017") >= 0, log.slice(-400));
  ok("★ 認めるフォルダ名も案内する", log.indexOf("G1課題文_P0NN") >= 0, log.slice(-400));
}
{
  // ⚠️ 陰性対照: 見る対象が 1 つも無くても壊れない（★ undefined を範囲に出さない）
  const ctx = makeCtx({ roster: [["P-ID", "氏名", "メール"]] });
  ctx.checkMaterialsProvisioning(0);
  const log = ctx.__logs.join("\n");
  ok("★ 対象ゼロで undefined を出さない", log.indexOf("undefined") < 0, log);
  ok("汎用の案内に落ちる", log.indexOf("<開始 P-ID>") >= 0, log);
}

console.log("20. ★ レビュー指摘の反映（2026-08-07）");
{
  // ⚠️★★ 名前の規約が **bash と GAS の 2 か所**にある。コメントは「同時に直せ」と言うが、
  //   ★ それを**機械が確かめていない**と、片方だけ直った状態が黙って通る。
  const shell = fs.readFileSync(
    path.join(__dirname, "..", "experiments", "20260801-controlled-friction-task", "prepare-subjects.sh"),
    "utf8"
  );
  const m = shell.match(/^DRIVE_PREFIX="([^"]*)"/m);
  const ctx = makeCtx({});
  ok("prepare-subjects.sh に DRIVE_PREFIX がある", !!m, shell.slice(0, 0));
  ok(
    "★ bash の DRIVE_PREFIX と GAS の G1_MATERIALS_FOLDER_PREFIX が一致",
    m && m[1] === ctx.G1_MATERIALS_FOLDER_PREFIX,
    (m ? m[1] : "(無し)") + " vs " + ctx.G1_MATERIALS_FOLDER_PREFIX
  );
}
{
  // ⚠️★ 打ち切りは **番号の小さい方**を落とす（直近の参加者ほど再登録しやすいため）
  const roster = [["P-ID", "氏名", "メール"]];
  const folders = { [PARENT_ID]: { name: "G1_課題ページ_被験者別", access: "PRIVATE" } };
  for (let i = 1; i <= 45; i++) {
    const p = "P" + ("000" + i).slice(-3);
    roster.push([p, "", ""]);
    // ★ P045 (直近) だけ用意されていない状態を作る
    if (i !== 45) folders["FOLDER-" + p] = { name: "G1課題文_" + p, parent: PARENT_ID, access: "ANYONE_WITH_LINK" };
  }
  const ctx = makeCtx({ roster: roster, folders: folders });
  ctx.checkMaterialsProvisioning(0);
  const log = ctx.__logs.join("\n");
  ok("★ 直近を残すと言う", log.indexOf("直近 40 人") >= 0, log.slice(0, 300));
  ok("★ 古い方を落とす (P001 は見ない)", log.indexOf("P001 (既存)") < 0, log.slice(0, 300));
  ok("★ 直近の未用意を捕まえる (P045)", log.indexOf("未用意: P045") >= 0, log.slice(-400));
  // ⚠️ 本丸: 打ち切り + 未用意ありのとき、分母が実ロスターでないことを**同じ行で**言う
  ok("★ 分母が「見た人数」だと同じ行で言う", log.indexOf("未検査 5 人は含みません") >= 0, log.slice(-400));
}
{
  // ⚠️★ 非正準な P-ID (ゼロ埋めなし) を名指しで警告する。★ 黙って P001 に直さない
  const ctx = makeCtx({ roster: [["P-ID"], ["P6"], ["P015"]] });
  ctx.checkMaterialsProvisioning(0);
  const log = ctx.__logs.join("\n");
  ok("★ 非正準を名指しする", log.indexOf("3 桁ゼロ埋めでない P-ID があります: P6") >= 0, log.slice(0, 400));
  ok("★ 直すのはロスター側だと言う", log.indexOf("直すのはロスター側") >= 0);
  ok("⚠️ 勝手に P006 へ正規化しない", log.indexOf("P006") < 0, log.slice(0, 400));
}
{
  // ⚠️★ 案内の範囲: 飛び番があるときは --range でなく ID 列挙にする
  //   (--range は連続前提。飛び番だと prepare-subjects.sh の 50 人上限に弾かれる)
  const ctx = makeCtx({ roster: [["P-ID"], ["P006"], ["P900"]] });
  ctx.checkMaterialsProvisioning(0);
  const log = ctx.__logs.join("\n");
  ok("★ 飛び番なら --range を出さない", log.indexOf("--range P006 P900") < 0, log.slice(-400));
  ok("★ ID 列挙で出す", log.indexOf("prepare-subjects.sh P006 P900") >= 0, log.slice(-400));
  ok("理由を書く", log.indexOf("飛び番があるので") >= 0);
}
{
  // ★ 陰性対照: 連続なら従来どおり --range
  const ctx = makeCtx({ roster: [["P-ID"], ["P006"], ["P007"], ["P008"]] });
  ctx.checkMaterialsProvisioning(0);
  const log = ctx.__logs.join("\n");
  ok("★ 連続なら --range のまま", log.indexOf("--range P006 P008") >= 0, log.slice(-400));
  ok("飛び番の注意は出ない", log.indexOf("飛び番があるので") < 0);
}
{
  // ⚠️ 空の P-ID で Drive を探しに行かない
  const ctx = makeCtx({});
  ok("空 P-ID の名前は空配列", ctx.g1MaterialsFolderNames_("").length === 0);
  ok("空 P-ID は null でも空配列", ctx.g1MaterialsFolderNames_(null).length === 0);
  const found = ctx.g1MaterialsUrlForPid_("");
  ok("★ 空 P-ID なら探さずに理由を返す", found.url === "" && found.problem.indexOf("P-ID が空") >= 0, found.problem);
}
{
  // ⚠️★ 大小の非対称は**意図的**。★ ガードは通るが finder は見つけない、を固定する
  //   (意図せず片方だけ変わったら、このテストが落ちて気づける)
  const folders = { [PARENT_ID]: { name: "G1_課題ページ_被験者別", access: "PRIVATE" } };
  folders["FOLDER-P015"] = { name: "g1課題文_p015", parent: PARENT_ID, access: "ANYONE_WITH_LINK" };
  const ctx = makeCtx({ folders: folders });
  ok("★ finder は大小違いを見つけない", ctx.g1MaterialsUrlForPid_("P015").url === "");
  ok(
    "★ ガード 7 は大小違いを通す（意図的な非対称）",
    ctx.g1MaterialsFolderProblem_(urlFor("P015"), "P015") === "",
    ctx.g1MaterialsFolderProblem_(urlFor("P015"), "P015")
  );
}

console.log("21. ★ 配布形式 (zip) と文面が食い違わないこと（2026-08-08 に実在した不具合）");
{
  // ⚠️★★ Drive に置いてあるのは **zip 2 個**。⚠️ 文面が「フォルダを丸ごと保存」と言っていた。
  //   ★ それは zip 配布へ切り替えた理由そのものに反する（Drive はパーミッションを保存しないので
  //     フォルダ経由だと .app の実行ビットが落ちる）。→ 文面側を固定する。
  const ctx = makeCtx({});
  const body = ctx.g1RegisterAckBody_("P015", urlFor("P015"));
  ok("★ zip だと言う", body.indexOf("G1_実施用_Windows.zip") >= 0 && body.indexOf("G1_実施用_macOS.zip") >= 0);
  ok("★ 展開（解凍）を指示する", body.indexOf("展開（解凍）してください") >= 0);
  ok("★ macOS / Windows の展開手順を書く", body.indexOf("すべて展開") >= 0);
  ok("⚠️ 展開せずに開くなと言う", body.indexOf("展開せずに中身を開かないでください") >= 0);
  // ⚠️★ 本丸: 「フォルダを丸ごと保存」に戻っていないこと
  ok("⚠️★ 「フォルダを丸ごと保存」に戻っていない", body.indexOf("丸ごと**保存") < 0 && body.indexOf("フォルダがあります") < 0, body.slice(0, 0));
  // ★ 課題ページの移動先が「展開してできたフォルダ」であること（展開前は存在しない）
  ok("★ 移動先は展開後のフォルダ", body.indexOf("展開してできた") >= 0);
  ok("★ アプリのリンクが入る", body.indexOf(ctx.G1_APP_DOWNLOAD_URL) >= 0);
  ok("★ 課題ページのリンクが入る", body.indexOf(urlFor("P015")) >= 0);
  ok("「別便」と書かない", body.indexOf("別便のメール") < 0);
}
{
  // ⚠️★★ プレビューが **1 通運用の本文を一度も出せていなかった** 不具合の再発防止。
  //   原因: g1RegisterAckBody_(pid, materialsUrl) を **引数 1 つ**で呼んでいた。
  const ctx = makeCtx({ roster: [["P-ID", "氏名", "メール"], ["P015", "", ""]] });
  ctx.previewRegisterAckEmail();
  const log = ctx.__logs.join("\n");
  ok("★ 用意済みなら課題ページの URL が本文に出る", log.indexOf(urlFor("P015")) >= 0, log.slice(0, 600));
  ok("★ 本番と同じだと言い切る", log.indexOf("本番とまったく同じ本文") >= 0);
  ok("⚠️ 別便の分岐は出さない", log.indexOf("別便のメールでお送りします") < 0, log.slice(0, 600));
  ok("★ アプリのリンクも確認用に出す", log.indexOf(ctx.G1_APP_DOWNLOAD_URL) >= 0);
  // ⚠️ 2 通目のプレースホルダは「バグでは？」と読まれない書き方であること
  ok("⚠️ example.com を出さない", log.indexOf("example.com") < 0, log.slice(-600));
  ok("★ プレースホルダだと明示する", log.indexOf("プレースホルダ") >= 0);
  ok("★ 1 通も送らない", ctx.__sent.length === 0 && ctx.__drafts.length === 0);
}
{
  // ★ 陰性対照: 用意できていない P-ID なら、別便の分岐を出しつつ「用意しろ」と言う
  const ctx = makeCtx({ roster: [["P-ID", "氏名", "メール"], ["P099", "", ""]] });
  ctx.previewRegisterAckEmail();
  const log = ctx.__logs.join("\n");
  ok("★ 未用意だと言う", log.indexOf("まだ用意できていません") >= 0, log.slice(0, 400));
  ok("★ 別便に落ちた本文だと断る", log.indexOf("別便に落ちたとき") >= 0);
}

console.log("");
if (failures) {
  console.log("❌ " + failures + " 件失敗");
  process.exit(1);
}
console.log("✅ すべて通りました");
