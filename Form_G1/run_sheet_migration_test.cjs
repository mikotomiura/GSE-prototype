// 「G1 実施トラッキング」の**列の移行**をローカルで実測する。
// ★ 実シートには一切触らない（SpreadsheetApp をスタブする）。
//
// ⚠️ ★ なぜテストするか: この移行は**実データのあるシートの列を消す**。
//    `runCol_` は**コード側の RUN_HEADER しか見ない**ので、実シートとずれると
//    **静かに別の列へ書き込む**（2026-08-03 に実際に起きた）。
//    ★ 「例外が出ないこと」ではなく「**値が正しい列に残っていること**」を見る。
//
// ⚠️ ★ 陽性対照を必ず置く: 見覚えのない形のシートでは**止まる**こと。
//    止まるだけのガードは「全部止める」でも緑になるので、正常系も併せて見る。
//
// 実行: node Form_G1/run_sheet_migration_test.cjs

const fs = require("fs");
const path = require("path");
const vm = require("vm");

const src = fs.readFileSync(
  process.argv[2] || path.join(__dirname, "GSE_G1_Form_Builder.gs"),
  "utf8"
);

// --- 最小の偽シート（1 始まり座標・列の挿入/削除に対応）----------------------
function makeSheet(grid) {
  const cells = grid.map((r) => r.slice());
  // ★ merges は「実物と同じ制約」を再現するために持つ:
  //   ⚠️ 2026-08-08 実測: A 列に掛かる結合があると setFrozenColumns(1) が
  //      「結合されたセルの一部だけを含む列を固定することはできません」で**落ちる**。
  //      ★ 偽シートがこれを知らなかったので、ローカルは緑・実シートで例外だった。
  const style = { widths: {}, rowHeights: {}, frozenRows: 0, frozenCols: 0, condRules: [], merges: [] };
  function ensure(r, c) {
    while (cells.length < r) cells.push([]);
    const row = cells[r - 1];
    while (row.length < c) row.push("");
  }
  const sheet = {
    _cells: cells,
    _style: style,
    getName: () => "G1 実施トラッキング",
    getParent: () => sheet._parent,
    getLastRow: () => cells.length,
    // ★ 実物の getLastColumn は「**中身のある**最後の列」を返す（末尾の空セルは数えない）。
    //   ⚠️ 単純に配列長を返すと、getValues のパディングで水増しされて実物と食い違う。
    getLastColumn: () =>
      cells.reduce((m, r) => {
        let last = 0;
        r.forEach((v, i) => { if (String(v === undefined || v === null ? "" : v) !== "") last = i + 1; });
        return Math.max(m, last);
      }, 0),
    setColumnWidth(c, w) { style.widths[c] = w; return sheet; },
    setRowHeight(r, h) { style.rowHeights[r] = h; return sheet; },
    setFrozenRows(n) { style.frozenRows = n; return sheet; },
    setFrozenColumns(n) {
      // ★ 固定の境界が結合を分断していたら実物と同じ例外を投げる。
      const bad = style.merges.some((m) => m.c <= n && m.c + m.nc - 1 > n);
      if (bad) {
        throw new Error(
          "結合されたセルの一部だけを含む列を固定することはできません。"
        );
      }
      style.frozenCols = n;
      return sheet;
    },
    getMaxColumns: () => Math.max(sheet.getLastColumn(), 26),
    setConditionalFormatRules(rules) { style.condRules = rules; return sheet; },
    insertColumnAfter(idx) {
      cells.forEach((row) => { while (row.length < idx) row.push(""); row.splice(idx, 0, ""); });
      return sheet;
    },
    insertColumnBefore(idx) {
      cells.forEach((row) => { while (row.length < idx - 1) row.push(""); row.splice(idx - 1, 0, ""); });
      return sheet;
    },
    deleteColumn(idx) {
      cells.forEach((row) => row.splice(idx - 1, 1));
      return sheet;
    },
    getRange(r, c, nr, nc) {
      const rows = nr === undefined ? 1 : nr;
      const colsN = nc === undefined ? 1 : nc;
      const rg = {
        getRow: () => r,
        getSheet: () => sheet,
        getValue() { ensure(r, c); return cells[r - 1][c - 1]; },
        setValue(v) { ensure(r, c); cells[r - 1][c - 1] = v; return rg; },
        getValues() {
          const out = [];
          for (let i = 0; i < rows; i++) {
            const row = [];
            for (let j = 0; j < colsN; j++) { ensure(r + i, c + j); row.push(cells[r + i - 1][c + j - 1]); }
            out.push(row);
          }
          return out;
        },
        setValues(vals) {
          vals.forEach((row, i) => row.forEach((v, j) => { ensure(r + i, c + j); cells[r + i - 1][c + j - 1] = v; }));
          return rg;
        },
        isPartOfMerge: () =>
          style.merges.some(
            (m) => m.r === r && c >= m.c && c <= m.c + m.nc - 1
          ),
        merge() {
          style.merges.push({ r, c, nc: colsN });
          return rg;
        },
        breakApart() {
          style.merges = style.merges.filter(
            (m) => !(m.r >= r && m.r <= r + rows - 1 && m.c >= c && m.c <= c + colsN - 1)
          );
          return rg;
        },
        applyRowBanding: () => rg,
        setDataValidation: () => rg,
        clearDataValidations: () => rg,
      };
      // 見た目系はすべてチェーン（★ 実 GAS と同じく自分を返す）
      [
        "setFontWeight", "setFontColor", "setBackground", "setWrap", "setFontSize",
        "setHorizontalAlignment", "setVerticalAlignment", "setBorder", "setNumberFormat",
      ].forEach((m) => { rg[m] = () => rg; });
      return rg;
    },
  };
  return sheet;
}

function makeCtx(runGrid) {
  const logs = [];
  const runSheet = makeSheet(runGrid);
  const ss = {
    getSheetByName: (n) => (n === "G1 実施トラッキング" ? runSheet : null),
    getSheets: () => [runSheet],
    getUrl: () => "https://example.invalid/sheet",
    getId: () => "run-sheet",
  };
  runSheet._parent = ss;
  const props = { GSE_G1_MGMT_SHEET_ID: "run-sheet" };
  const ctx = {
    Logger: { log: (m) => logs.push(String(m)) },
    console,
    PropertiesService: {
      getScriptProperties: () => ({
        getProperty: (k) => (k in props ? props[k] : null),
        setProperty: (k, v) => { props[k] = v; },
        deleteProperty: (k) => { delete props[k]; },
      }),
    },
    SpreadsheetApp: {
      openById: () => ss,
      create: () => ss,
      flush: () => {},
      newDataValidation: () => {
        const b = { requireValueInList: () => b, setAllowInvalid: () => b, build: () => ({}) };
        return b;
      },
      newConditionalFormatRule: () => {
        const b = {
          whenFormulaSatisfied: () => b, setBackground: () => b, setFontColor: () => b,
          setRanges: () => b, build: () => ({}),
        };
        return b;
      },
      BandingTheme: { LIGHT_GREY: "LIGHT_GREY" },
      BorderStyle: { SOLID: "SOLID" },
    },
    FormApp: { openById: () => { throw new Error("not used"); } },
    MailApp: { sendEmail: () => {} },
    GmailApp: { createDraft: () => {} },
    DriveApp: {},
    ScriptApp: { getProjectTriggers: () => [] },
    Session: { getScriptTimeZone: () => "Asia/Tokyo" },
    Utilities: { formatDate: () => "2026-01-01" },
    UrlFetchApp: {},
    LockService: { getScriptLock: () => ({ waitLock: () => {}, releaseLock: () => {} }) },
    __logs: logs,
    __sheet: runSheet,
  };
  vm.createContext(ctx);
  vm.runInContext(src, ctx);
  return ctx;
}

// ★ 移行前（2026-08-08 以前）の実物と同じ 20 列。
const OLD_HEADER = [
  "P-ID", "実施予定日", "G1-C 同意", "配布フォルダURL", "課題文リンク送信日", "実施日",
  "実施形態", "実施OS", "アプリのビルド", "GSE_DISABLE_PROBES=1", "HMM_VERSION", "配置(A/B)",
  "完了ブロック数(/10)", "G1-M 回答数(/7)", "G1-S 回答", "verify-blocks 実施",
  "validate_blocks 緑", "gse-dataset 送付", "撤回/除外", "備考",
];
// ★ P009 の実物に近い 1 行（★ 値が正しい列に残るかを見るための目印を全列に入れる）。
const OLD_ROW = [
  "P009", "", "はい", "https://drive.google.com/drive/folders/ABC", "2026-08-08", "2026-08-08",
  "無人在宅", "macOS", "v2.31", "はい", "hmm-7", "A",
  "1", "0", "", "いいえ", "いいえ", "いいえ", "除外", "研究者テスト",
];

let failed = 0;
function check(name, cond, extra) {
  if (cond) { console.log("✅ " + name); } else { failed++; console.log("❌ " + name + (extra ? "\n   " + extra : "")); }
}

// --- 1) 旧 20 列 + データ 1 行 → 移行 ----------------------------------------
{
  const ctx = makeCtx([["banner"], OLD_HEADER.slice(), OLD_ROW.slice()]);
  ctx.migrateRunSheetToV14();
  const head = ctx.__sheet._cells[1].slice(0, ctx.RUN_HEADER.length);
  check("移行後のヘッダがコードの RUN_HEADER と一致する",
    JSON.stringify(head) === JSON.stringify(ctx.RUN_HEADER),
    "実際: " + JSON.stringify(head));
  check("列数が RUN_HEADER と同じ（右に余りが残らない）",
    ctx.__sheet.getLastColumn() === ctx.RUN_HEADER.length,
    "実際: " + ctx.__sheet.getLastColumn());

  // ★★ 本命: **値が正しい列に残っている**こと（ズレの検出）。
  const get = (h) => ctx.__sheet._cells[2][ctx.RUN_HEADER.indexOf(h)];
  const expect = {
    "P-ID": "P009",
    "G1-C 同意": "はい",
    "配布フォルダURL": "https://drive.google.com/drive/folders/ABC",
    "配布URL(短縮)": "", // ★ 新設列は空で入る（refreshG1RunSheet が埋める）
    "課題ページ送付日": "2026-08-08",
    "実施日": "2026-08-08",
    "実施形態": "在宅（初回起動のみ同席）", // ★ 値も第 13 版に合わせる
    "実施OS": "macOS",
    "アプリのビルド": "v2.31",
    "G1モード確認": "はい",
    "HMM_VERSION": "hmm-7",
    "完了ブロック数(/10)": "1",
    "G1-M 回答数(/7)": "0",
    "G1-S 回答": "",
    "verify-blocks 実施": "いいえ",
    "validate_blocks 緑": "いいえ",
    "gse-dataset 送付": "いいえ",
    "撤回/除外": "除外",
    "備考": "研究者テスト",
  };
  Object.keys(expect).forEach((h) => {
    check('値が正しい列に残る: "' + h + '"', get(h) === expect[h],
      "期待=" + JSON.stringify(expect[h]) + " 実際=" + JSON.stringify(get(h)));
  });

  const logs = ctx.__logs.join("\n");
  check("★ 削除する列の中身をログに出す（黙って捨てない）",
    logs.indexOf("配置(A/B)") >= 0 && logs.indexOf("消える値") >= 0, logs);
  check("★ 削除された値 A がログに出ている", /消える値 1 件: A/.test(logs), logs);
  check("実施予定日は空だったので「すべて空」と出る", /実施予定日[\s\S]*すべて空/.test(logs), logs);
  check("★ 見た目を張り直している（ヘッダ 2 行を固定）", ctx.__sheet._style.frozenRows === 2);
  check("★ P-ID 列を固定している", ctx.__sheet._style.frozenCols === 1);
  check("★ バナーの結合が A 列を巻き込んでいない（固定と両立する）",
    ctx.__sheet._style.merges.every((m) => m.c >= 2), JSON.stringify(ctx.__sheet._style.merges));
  check("★ 条件付き書式を 3 本張っている", ctx.__sheet._style.condRules.length === 3,
    "実際: " + ctx.__sheet._style.condRules.length);

  // --- 2) 冪等: もう一度実行しても壊れない ------------------------------------
  const before = JSON.stringify(ctx.__sheet._cells);
  ctx.migrateRunSheetToV14();
  check("★ 冪等（2 回実行しても中身が変わらない）",
    JSON.stringify(ctx.__sheet._cells) === before);
  check("★ 2 回目は「既に最新」と言う", /既に最新の列構成/.test(ctx.__logs.join("\n")));
}

// --- 3) 途中まで手で直されたシート（改名だけ済み）----------------------------
{
  const partial = OLD_HEADER.slice();
  partial[4] = "課題ページ送付日"; // 改名だけ済んでいる
  const ctx = makeCtx([["banner"], partial, OLD_ROW.slice()]);
  ctx.migrateRunSheetToV14();
  const head = ctx.__sheet._cells[1].slice(0, ctx.RUN_HEADER.length);
  check("途中まで直されたシートでも最後まで揃う",
    JSON.stringify(head) === JSON.stringify(ctx.RUN_HEADER), JSON.stringify(head));
  check("★ 値がズレていない（部分移行）",
    ctx.__sheet._cells[2][ctx.RUN_HEADER.indexOf("備考")] === "研究者テスト");
}

// --- 4) 既に新形式 → 何もしない ----------------------------------------------
{
  const ctx0 = makeCtx([["banner"], ["dummy"]]);
  const NEW = ctx0.RUN_HEADER.slice();
  const row = NEW.map((h) => (h === "P-ID" ? "P010" : ""));
  const ctx = makeCtx([["banner"], NEW, row]);
  ctx.migrateRunSheetToV14();
  check("★ 既に新形式なら「何もしません」",
    /既に最新の列構成/.test(ctx.__logs.join("\n")), ctx.__logs.join("\n"));
  check("★ 既に新形式でも見た目は張り直す", ctx.__sheet._style.frozenRows === 2);
}

// --- 5) ⚠️ 陽性対照: 見覚えのない形なら**止まる** ----------------------------
{
  const weird = ["なにか", "ぜんぜん", "ちがう", "ヘッダ"];
  const ctx = makeCtx([["banner"], weird, ["a", "b", "c", "d"]]);
  let threw = "";
  try { ctx.migrateRunSheetToV14(); } catch (e) { threw = String(e.message); }
  check("★ 見覚えのない形では例外で止まる（黙って列をずらさない）",
    /一致しません/.test(threw), threw || "(例外が出なかった)");
}

// --- 6) ⚠️ 陽性対照: 削除対象に値があっても、ログに出したうえで消す ------------
{
  const grid = [["banner"], OLD_HEADER.slice(), OLD_ROW.slice()];
  grid[2][1] = "2026-08-20"; // 実施予定日に値を入れる
  const ctx = makeCtx(grid);
  ctx.migrateRunSheetToV14();
  check("★ 消える値（実施予定日）がログに出る",
    /消える値 1 件: 2026-08-20/.test(ctx.__logs.join("\n")), ctx.__logs.join("\n"));
}

console.log(failed ? "\n❌ " + failed + " 件失敗" : "\n✅ すべて緑");
process.exit(failed ? 1 : 0);
