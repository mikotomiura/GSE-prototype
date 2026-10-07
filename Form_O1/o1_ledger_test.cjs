// GSE_O1_Ledger.gs（受領台帳＋途絶検知）をローカルで実測する。
// ★ 実 Drive・実シート・実メールには一切触れない（すべてスタブ）。
//
// ⚠️★★ **偽の Sheets / Drive は実物の制約を知らない**（memory `gas-live-state-vs-code`）。
//   ここで固定できるのは「ロジック」と「私が知っている制約（範囲外への setValues は例外・
//   テキスト形式なら数式にならない）」までである。★ 実フォルダでの通し確認は別に要る（配備時）。
//
// ⚠️ ★ ここで測るのは「書いた」ではなく **「止める / 通す」** である。
//   陽性対照（正しい入力は通る・異常は検知する）と陰性対照（正常なら通知しない）を両方含める。
//
// 使い方: node Form_O1/o1_ledger_test.cjs [<GSE_O1_Ledger.gs のパス>]
//   （★ 引数は変異テストが壊したコピーを渡すために使う）
const fs = require("fs");
const vm = require("vm");
const path = require("path");

const LEDGER_PATH = process.argv[2] || path.join(__dirname, "GSE_O1_Ledger.gs");
// ⚠️ 兄弟ファイルが無いときに ENOENT で即死すると、ゲートに「原因不明の赤」が出る（★ NG を 1 件も出せない）。
//   → 先に存在を見て、無ければ **NG ケースとして出す**。
const SUBMIT_PATH = path.join(__dirname, "GSE_O1_Submit.gs");
const BUILDER_PATH = path.join(__dirname, "GSE_O1_Form_Builder.gs");
const missingSiblings = [SUBMIT_PATH, BUILDER_PATH].filter((f) => !fs.existsSync(f)).map((f) => path.basename(f));
if (missingSiblings.length) {
  console.log(`NG   検査に必要な兄弟ファイルが無い → ${JSON.stringify(missingSiblings)}`);
  console.log(`\n1 件が期待と違う（全 1 ケース）`);
  process.exit(1);
}
const src = fs.readFileSync(LEDGER_PATH, "utf8");
const submitSrc = fs.readFileSync(SUBMIT_PATH, "utf8");

const DAY = 24 * 60 * 60 * 1000;
const cases = [];
function check(name, got, want) {
  const g = JSON.stringify(got);
  const w = JSON.stringify(want);
  cases.push({ name, ok: g === w, got: g === w ? got : { got, want } });
}

// ---------------------------------------------------------------------------
// 時刻を固定できる Date（★ スクリプトの `new Date()` を差し替える）
// ---------------------------------------------------------------------------
let NOW = new Date(2026, 8, 30, 12, 0, 0).getTime(); // 2026-09-30 12:00（ローカル）
class FakeDate extends Date {
  constructor(...a) {
    if (a.length === 0) super(NOW);
    else super(...a);
  }
  static now() {
    return NOW;
  }
}
const ago = (days) => NOW - days * DAY;

// ---------------------------------------------------------------------------
// 偽の GAS サービス
// ---------------------------------------------------------------------------
function makeSheet(name, opts) {
  const o = opts || {};
  const s = {
    name,
    maxRows: o.maxRows || 1000,
    rows: [], // 1 始まりでなく 0 始まりの配列（行 r は rows[r-1]）
    formats: {}, // "r,c" → 形式
    cells: {}, // "r,c" → {v, kind} kind: 'text' | 'number' | 'formula'
    getLastRow() {
      let last = 0;
      s.rows.forEach((r, i) => {
        if (r && r.some((c) => c !== "" && c !== undefined)) last = i + 1;
      });
      return last;
    },
    getMaxRows: () => s.maxRows,
    getLastColumn() {
      let m = 0;
      s.rows.forEach((r) => r && (m = Math.max(m, r.length)));
      return m;
    },
    getMaxColumns() {
      // ★ 実 Sheets の新規シートは既定で多くの空列を持つ（★ 内容幅とは無関係）。
      //   列削除で初めて `getMaxColumns()` が小さくなる。既定は `opts.maxColumns` が無ければ 26。
      return o.maxColumns || Math.max(this.getLastColumn(), 26);
    },
    insertRowsAfter(after, n) {
      if (after !== s.maxRows) throw new Error("insertRowsAfter は最終行の後ろだけを想定");
      s.maxRows += n;
    },
    appendRow(arr) {
      const r = s.getLastRow() + 1;
      if (r > s.maxRows) s.maxRows = r; // ★ 実物の appendRow は行を足す
      s.rows[r - 1] = arr.slice();
    },
    clearContents() {
      s.rows = [];
      s.cells = {};
    },
    // ★ 書式（2026-09-28 見た目の改修）。値とは別に記録し、テストで配置・色を確かめる。
    style: {}, // "r,c" → { bg, fg, bold, size, halign, wrap }
    merges: [], // "r,c,nr,nc"
    frozen: 0,
    widths: {},
    heights: {},
    tabColor: null,
    rules: [],
    clear() {
      s.rows = [];
      s.cells = {};
      s.formats = {};
      s.style = {};
      s.merges = [];
    },
    getFrozenRows: () => s.frozen,
    setFrozenRows: (n) => {
      s.frozen = n;
    },
    setColumnWidth: (c, w) => {
      s.widths[c] = w;
    },
    setRowHeight: (r, h) => {
      s.heights[r] = h;
    },
    setTabColor: (c) => {
      s.tabColor = c;
    },
    setConditionalFormatRules: (rules) => {
      s.rules = rules.slice();
    },
    getConditionalFormatRules: () => s.rules.slice(),
    styleAt: (r, c) => s.style[r + "," + c] || {},
    getRange(r, c, nr, nc) {
      if (typeof r === "string") return { __a1: r }; // 条件付き書式の範囲だけに使う
      if (nr === undefined) nr = 1;
      if (nc === undefined) nc = 1;
      if (r < 1 || c < 1 || nr < 1 || nc < 1) throw new Error("range 引数が不正");
      if (r + nr - 1 > s.maxRows) throw new Error("The coordinates of the range are outside the dimensions of the sheet.");
      const rng = {
        getValues() {
          const out = [];
          for (let i = 0; i < nr; i++) {
            const row = [];
            for (let j = 0; j < nc; j++) {
              const v = (s.rows[r - 1 + i] || [])[c - 1 + j];
              row.push(v === undefined ? "" : v);
            }
            out.push(row);
          }
          return out;
        },
        setValues(vals) {
          if (vals.length !== nr || vals.some((row) => row.length !== nc)) {
            throw new Error("setValues の次元が範囲と合わない");
          }
          for (let i = 0; i < nr; i++) {
            s.rows[r - 1 + i] = s.rows[r - 1 + i] || [];
            for (let j = 0; j < nc; j++) {
              const v = vals[i][j];
              const fmt = s.formats[r + i + "," + (c + j)];
              let kind = typeof v === "number" ? "number" : "text";
              // ★ 私が知っている挙動のモデル: テキスト形式でなければ "=" で始まる文字列は数式になる。
              if (typeof v === "string" && v.startsWith("=") && fmt !== "@") kind = "formula";
              if (typeof v === "number" && fmt === "@") kind = "text";
              s.cells[r + i + "," + (c + j)] = { v, kind };
              s.rows[r - 1 + i][c - 1 + j] = v;
            }
          }
        },
        setNumberFormat(f) {
          for (let i = 0; i < nr; i++) for (let j = 0; j < nc; j++) s.formats[r + i + "," + (c + j)] = f;
        },
      };
      const range = rng;
      const paint = (k, v) => {
        for (let i = 0; i < nr; i++)
          for (let j = 0; j < nc; j++) {
            const key = r + i + "," + (c + j);
            s.style[key] = Object.assign({}, s.style[key], { [k]: v });
          }
        return range;
      };
      Object.assign(range, {
        setBackground: (v) => paint("bg", v),
        setFontColor: (v) => paint("fg", v),
        setFontWeight: (v) => paint("bold", v === "bold"),
        setFontSize: (v) => paint("size", v),
        setHorizontalAlignment: (v) => paint("halign", v),
        setVerticalAlignment: (v) => paint("valign", v),
        setWrap: (v) => paint("wrap", v),
        setBorder: () => range,
        merge: () => {
          s.merges.push([r, c, nr, nc].join(","));
          return range;
        },
        breakApart: () => {
          s.merges = s.merges.filter((m) => {
            const [mr] = m.split(",").map(Number);
            return mr < r || mr >= r + nr;
          });
          return range;
        },
      });
      return range;
    },
  };
  return s;
}

function makeSpreadsheet(tabs) {
  const sheets = {};
  (tabs || []).forEach((t) => (sheets[t] = makeSheet(t)));
  return {
    sheets,
    getSheetByName: (n) => sheets[n] || null,
    insertSheet(n) {
      if (sheets[n]) throw new Error("同名のシートがある");
      sheets[n] = makeSheet(n);
      return sheets[n];
    },
  };
}

function makeFile(id, name, size, createdMs, opts) {
  return {
    getId: () => id,
    getName: () => name,
    getSize: () => size,
    getDateCreated: () => new FakeDate(createdMs),
    isTrashed: () => !!(opts && opts.trashed),
  };
}

function goodName(pid, day, stamp, extra) {
  return `${pid}_o1day${String(day).padStart(2, "0")}_gse_o1_${stamp || "20260920_101112"}${extra || ""}.age`;
}

/** 実行環境を作る。★ 呼ぶたびに新しい vm コンテキスト（状態が混ざらない）。 */
function makeEnv(o) {
  const opt = o || {};
  // ★ `propsObj` を渡すと、複数回の実行でスクリプト プロパティ（状態）を共有できる。
  const props =
    opt.propsObj ||
    Object.assign(
      { O1_RECEIVE_FOLDER_ID: "FOLDER", O1_MGMT_SHEET_ID: "SHEET", O1_LEDGER_NOTIFY_EMAIL: "researcher@example.invalid" },
      opt.props || {}
    );
  Object.keys(props).forEach((k) => props[k] === null && delete props[k]);
  const ss = opt.spreadsheet || makeSpreadsheet(["O1 登録ログ"]);
  const files = opt.files || [];
  const mails = [];
  const logs = [];
  const triggers = opt.triggers || [];
  const lockOk = opt.lockOk !== false;
  let opened = 0;
  const ctx = {
    console: { log: (m) => logs.push(String(m)) },
    Date: FakeDate,
    PropertiesService: {
      getScriptProperties: () => ({
        getProperty: (k) => (k in props ? props[k] : null),
        setProperty: (k, v) => {
          props[k] = String(v);
        },
        deleteProperty: (k) => {
          delete props[k];
        },
      }),
    },
    LockService: {
      getScriptLock: () => ({ tryLock: () => lockOk, releaseLock: () => {} }),
    },
    SpreadsheetApp: {
      BorderStyle: { SOLID: "SOLID" },
      newConditionalFormatRule() {
        const rule = {};
        const b = {
          whenFormulaSatisfied: (f) => ((rule.formula = f), b),
          setBackground: (v) => ((rule.bg = v), b),
          setFontColor: (v) => ((rule.fg = v), b),
          setRanges: (rs) => ((rule.ranges = rs.map((x) => x.__a1 || "?")), b),
          build: () => rule,
        };
        return b;
      },
      openById(id) {
        opened++;
        if (id !== "SHEET") throw new Error("no such spreadsheet " + id);
        return ss;
      },
    },
    DriveApp: {
      getFolderById(id) {
        if (id !== "FOLDER") throw new Error("no such folder");
        // ★ `opt.subfolders` = [{ trashed?, files: [...] }]（受け口が作る `<P-ID>/`・2026-09-28）。
        const iterOf = (list) => {
          let i = 0;
          return {
            hasNext: () => i < list.length,
            next: () => {
              if (opt.tickPerFile) NOW += opt.tickPerFile;
              return list[i++];
            },
          };
        };
        const subs = (opt.subfolders || []).map((d) => ({
          isTrashed: () => !!d.trashed,
          getFiles: () => iterOf(d.files),
        }));
        return {
          getName: () => "STUB-FOLDER",
          getFiles: () => iterOf(files),
          getFolders() {
            let i = 0;
            return {
              hasNext: () => i < subs.length,
              next: () => {
                if (opt.tickPerFolder) NOW += opt.tickPerFolder;
                return subs[i++];
              },
            };
          },
        };
      },
    },
    MailApp: {
      sendEmail(to, subject, body) {
        if (opt.mailFails) throw new Error("mail quota");
        mails.push({ to, subject, body });
      },
    },
    Utilities: {
      formatDate(d) {
        const p = (n) => String(n).padStart(2, "0");
        return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}:${p(d.getSeconds())}`;
      },
    },
    Session: { getScriptTimeZone: () => "Asia/Tokyo" },
    ScriptApp: {
      getProjectTriggers: () => triggers.slice(),
      deleteTrigger(t) {
        const i = triggers.indexOf(t);
        if (i >= 0) triggers.splice(i, 1);
      },
      newTrigger(fn) {
        return {
          timeBased() {
            return {
              everyHours(n) {
                return {
                  create() {
                    triggers.push({ getHandlerFunction: () => fn, hours: n });
                  },
                };
              },
            };
          },
        };
      },
    },
  };
  vm.createContext(ctx);
  vm.runInContext(opt.source || src, ctx, { filename: "GSE_O1_Ledger.gs" });
  return { ctx, props, ss, files, mails, logs, triggers, opened: () => opened };
}

const call = (env, fn, ...args) => env.ctx[fn](...args);
/** vm 内の値は別 realm の配列/オブジェクトなので、JSON を通して比べる。 */
const plain = (v) => JSON.parse(JSON.stringify(v));

// ---------------------------------------------------------------------------
// §1 名前の読み取り（★ 受け口の sanitizeName_ と対）
// ---------------------------------------------------------------------------
const E = makeEnv();
const parse = (n) => plain(call(E, "o1LedgerParseName_", n));

check("§1 正しい名前を読める（P-ID・日番号・開始・重複でない）", parse("P012_o1day03_gse_o1_20260920_101112.age"), {
  pid: "P012", day: 3, start: "2026-09-20 10:11:12", dup: false,
});
check("§1 連番つきの名前を読める", (parse("P012_o1day03_gse_o1_20260920_101112_2.age") || {}).day, 3);
check("§1 3 桁の日番号を読める", (parse("P012_o1day120_gse_o1_20260920_101112.age") || {}).day, 120);
check("§1 重複で足された名前（_dup-）を読み、dup を立てる", parse("P012_o1day03_gse_o1_20260920_101112_dup-1790000000000.age"), {
  pid: "P012", day: 3, start: "2026-09-20 10:11:12", dup: true,
});
check("§1 連番＋重複の名前も読める", (parse("P012_o1day03_gse_o1_20260920_101112_2_dup-1790000000000.age") || {}).dup, true);
[
  ["G1 の名前は読まない（★ 混入の検知）", "P012_block03_gse_20260807_101112.age"],
  [".age 以外は読まない", "P012_o1day03_gse_o1_20260920_101112.txt"],
  ["日番号が 1 桁は読まない", "P012_o1day3_gse_o1_20260920_101112.age"],
  ["P-ID が 17 文字は読まない", "P0123456789012345_o1day03_gse_o1_20260920_101112.age"],
  ["P-ID に記号があれば読まない", "P_12_o1day03_gse_o1_20260920_101112.age"],
  ["数式の形の名前は読まない", "=HYPERLINK(1)_o1day03_gse_o1_20260920_101112.age"],
  ["空文字は読まない", ""],
  ["_dup が数字でなければ読まない", "P012_o1day03_gse_o1_20260920_101112_dup-x.age"],
  ["拡張子の後ろに何かあれば読まない", "P012_o1day03_gse_o1_20260920_101112.age.exe"],
].forEach(([n, name]) => check("§1 " + n, parse(name), null));
check("§1 undefined でも例外にならず null", plain(call(E, "o1LedgerParseName_", undefined)), null);

// ★ 受け口の sanitizeName_ と突合する（片方を直してもう片方を直し忘れる事故を止める）
{
  const sctx = { console: { log() {} } };
  vm.createContext(sctx);
  vm.runInContext(submitSrc, sctx);
  const corpus = [
    "P012_o1day03_gse_o1_20260920_101112.age",
    "P012_o1day03_gse_o1_20260920_101112_2.age",
    "P012_o1day120_gse_o1_20260920_101112.age",
    "P012_o1day1000_gse_o1_20260920_101112.age",
    "P012_o1day3_gse_o1_20260920_101112.age",
    "P012_o1day03_gse_o1_2026092_101112.age",
    "P012_o1day03_gse_o1_20260920_101112_12345678901.age",
    "P012_block03_gse_20260807_101112.age",
    "P0123456789012345_o1day03_gse_o1_20260920_101112.age",
    "P01234567890123456_o1day03_gse_o1_20260920_101112.age",
    "p012_o1day03_gse_o1_20260920_101112.age",
    "P012_o1day03_gse_o1_20260920_101112.AGE",
    "../P012_o1day03_gse_o1_20260920_101112.age",
    "P012_o1day03_gse_o1_20260920_101112.age\n",
    "",
  ];
  const disagree = corpus.filter((n) => (sctx.sanitizeName_(n) !== "") !== (parse(n) !== null));
  check("§1★ 受け口の sanitizeName_ と、読める名前の集合が一致する（_dup- 以外）", disagree, []);

  // 受け口が重複時に実際に作る名前を、台帳が読めること
  const created = [];
  const folder = {
    getFilesByName: (n) => ({ hasNext: () => n === "P012_o1day03_gse_o1_20260920_101112.age" }),
    createFile: (blob) => created.push(blob.__name),
  };
  sctx.Utilities = { newBlob: (bytes, type, name) => ({ __name: name, __bytes: bytes }) };
  sctx.DriveApp = {};
  vm.runInContext("1", sctx);
  const saved = sctx.saveWithoutOverwriting_(folder, "P012_o1day03_gse_o1_20260920_101112.age", [1, 2, 3]);
  check("§1★ 受け口が重複時に付ける名前（_dup-）を台帳が読める", { dupFlag: saved.duplicate, parsed: (parse(saved.name) || {}).dup === true }, {
    dupFlag: true, parsed: true,
  });
}

// ---------------------------------------------------------------------------
// §2 判定（純関数）
// ---------------------------------------------------------------------------
const F = (pid, day, recvDaysAgo, extra) =>
  Object.assign({ pid, day, receivedMs: ago(recvDaysAgo), bytes: 1024 * 1024, dup: false }, extra || {});
const judge = (files, reg) => plain(call(E, "o1LedgerJudge_", files, reg || {}, NOW));
const flagsOf = (rows, pid) => (rows.find((r) => r.pid === pid) || {}).flags;

// 途絶の境界
check("§2 最終受領が 4 日 23 時間前 → 正常", flagsOf(judge([F("P001", 1, 4 + 23 / 24)]), "P001"), []);
check("§2 最終受領がちょうど 5 日前 → 途絶", flagsOf(judge([F("P001", 1, 5)]), "P001"), ["途絶"]);
check("§2 最終受領が 10 日前でも 1 本が新しければ正常", flagsOf(judge([F("P001", 1, 10), F("P001", 2, 1)]), "P001"), []);
check("§2 経過日数は切り捨て", judge([F("P001", 1, 2.9)])[0].elapsedDays, 2);
check("§2 重複ファイルも「最終受領」に数える（生きている）", flagsOf(judge([F("P001", 1, 9), F("P001", 1, 0.5, { dup: true })]), "P001"), []);
check("§2 重複は番号を増やさない（番号数 1・重複 1）", (() => {
  const r = judge([F("P001", 1, 1), F("P001", 1, 1, { dup: true })])[0];
  return [r.uniqueDays, r.dupCount, r.files];
})(), [1, 1, 2]);
check("§2 合計バイトは MB でなくバイトで持つ", judge([F("P001", 1, 1, { bytes: 3 }), F("P001", 2, 1, { bytes: 4 })])[0].totalBytes, 7);

// 欠番の規則
check("§2 番号 1,3 が届き 3 が 5 日前 → 2 が欠番", judge([F("P001", 1, 9), F("P001", 3, 5)])[0].gaps, [2]);
check("§2 欠番の判定は途絶と別に立つ（最終受領が新しければ欠番だけ）", flagsOf(judge([F("P001", 1, 9), F("P001", 3, 5), F("P001", 4, 1)]), "P001"), ["欠番"]);
check("§2 3 が 4 日前に届いたばかりなら 2 は欠番にしない（順序が前後して届くのは正常）", judge([F("P001", 1, 9), F("P001", 3, 4)])[0].gaps, []);
check("§2 番号 1 が欠けている（2 だけ届く・5 日前）→ 1 が欠番", judge([F("P001", 2, 6)])[0].gaps, [1]);
check("§2 番号が連続なら欠番なし", judge([F("P001", 1, 9), F("P001", 2, 8), F("P001", 3, 7)])[0].gaps, []);
check("§2 欠番の基準は「後ろの番号の最古の受領」（後の番号が複数でも最古を使う）", judge([F("P001", 1, 9), F("P001", 3, 6), F("P001", 4, 1)])[0].gaps, [2]);
check("§2 欠番が複数でも昇順で返す", judge([F("P001", 1, 20), F("P001", 4, 10), F("P001", 7, 10)])[0].gaps, [2, 3, 5, 6]);
check("§2 欠番の穴が後から埋まれば消える", judge([F("P001", 1, 9), F("P001", 2, 1), F("P001", 3, 6)])[0].gaps, []);
check("§2 最大番号より後ろは欠番と数えない（まだ来ていないだけ）", judge([F("P001", 1, 9), F("P001", 2, 8)])[0].gaps, []);

// 未受領
const REG = (d) => ({ P010: ago(d) });
check("§2 登録から 6 日・受領 0 件 → 未受領にしない", flagsOf(judge([], REG(6)), "P010"), []);
check("§2 登録から 7 日・受領 0 件 → 未受領", flagsOf(judge([], REG(7)), "P010"), ["未受領"]);
check("§2 登録から 30 日でも 1 本でも受領があれば未受領にしない", flagsOf(judge([F("P010", 1, 1)], REG(30)), "P010"), []);
check("§2 登録ログに無く受領 0 件の P-ID は行を作らない", judge([], {}).length, 0);
check("§2 受領だけあり登録ログに無い P-ID も行を作る（正常）", flagsOf(judge([F("P020", 1, 1)], {}), "P020"), []);
check("§2 登録からの日数を返す", judge([], REG(8.5))[0].sinceRegDays, 8);
check("§2 P-ID ごとに独立して判定する", (() => {
  const rows = judge([F("P001", 1, 9), F("P002", 1, 1)], {});
  return [flagsOf(rows, "P001"), flagsOf(rows, "P002")];
})(), [["途絶"], []]);
check("§2 P-ID の昇順で返す", judge([F("P003", 1, 1), F("P001", 1, 1), F("P002", 1, 1)]).map((r) => r.pid), ["P001", "P002", "P003"]);
check("§2 未来の受領時刻（時計のずれ）でも経過日数は負にならない", judge([F("P001", 1, -3)])[0].elapsedDays, 0);
check("§2 途絶と欠番は同時に立つ", flagsOf(judge([F("P001", 1, 20), F("P001", 3, 8)]), "P001"), ["途絶", "欠番"]);

// ---------------------------------------------------------------------------
// §3 通知の差分（純関数）
// ---------------------------------------------------------------------------
const row = (pid, flags, gaps) => ({ pid, flags, gaps: gaps || [] });
const alerts = (prev, rows, foreign) => plain(call(E, "o1LedgerAlerts_", prev, rows, foreign || 0));
check("§3 初回（前回なし）は現在の異常を全部通知する", alerts(null, [row("P001", ["途絶"]), row("P002", [])]).alerts, [{ key: "P001", added: ["途絶"] }]);
check("§3 正常だけなら通知なし", alerts(null, [row("P001", [])]).alerts, []);
check("§3 異常が続いているだけなら再通知しない", alerts({ P001: "途絶", "*": "" }, [row("P001", ["途絶"])]).alerts, []);
check("§3 正常 → 途絶で通知する", alerts({ P001: "", "*": "" }, [row("P001", ["途絶"])]).alerts, [{ key: "P001", added: ["途絶"] }]);
check("§3 途絶 → 途絶＋欠番では、増えた欠番だけを通知する", alerts({ P001: "途絶" }, [row("P001", ["途絶", "欠番"])]).alerts, [{ key: "P001", added: ["欠番"] }]);
check("§3 復帰（途絶 → 正常）では通知しないが状態は更新する", (() => {
  const r = alerts({ P001: "途絶" }, [row("P001", [])]);
  return [r.alerts, r.next.P001];
})(), [[], ""]);
check("§3 復帰の後にまた途絶になれば再度通知する", (() => {
  const s1 = alerts({ P001: "途絶" }, [row("P001", [])]).next;
  return alerts(s1, [row("P001", ["途絶"])]).alerts;
})(), [{ key: "P001", added: ["途絶"] }]);
check("§3 対象外の名前（フォルダ全体）は P-ID と別枠で通知する", alerts({ "*": "" }, [], 2).alerts, [{ key: "*", added: ["対象外の名前"] }]);
check("§3 対象外の名前が続いているだけ（件数が同じ）なら再通知しない", alerts({ "*": "対象外の名前:5" }, [], 5).alerts, []);
check("§3★ 対象外の名前は**件数が増えたら**再通知する（台帳は追記のみ・旗だけでは 2 回目以降の G1 混入を見逃す）", alerts({ "*": "対象外の名前:5" }, [], 6).alerts, [{ key: "*", added: ["対象外の名前"] }]);
check("§3 対象外の名前の件数が減っても通知しない", alerts({ "*": "対象外の名前:5" }, [], 4).alerts, []);
check("§3★ 欠番は**新しい番号が増えたら**再通知する（旗が既に立っていても）", alerts({ P001: "欠番:2" }, [row("P001", ["欠番"], [2, 5])]).alerts, [{ key: "P001", added: ["欠番"] }]);
check("§3 欠番が同じなら再通知しない", alerts({ P001: "欠番:2|5" }, [row("P001", ["欠番"], [2, 5])]).alerts, []);
check("§3 欠番が減った（埋まった）だけなら通知しない", alerts({ P001: "欠番:2|5" }, [row("P001", ["欠番"], [5])]).alerts, []);
check("§3 欠番が別の番号に入れ替わったら通知する", alerts({ P001: "欠番:2" }, [row("P001", ["欠番"], [7])]).alerts, [{ key: "P001", added: ["欠番"] }]);
check("§3 次の状態に欠番の番号と対象外の件数が入る", (() => {
  const r = alerts(null, [row("P001", ["欠番"], [2, 5])], 3);
  return [r.next.P001, r.next["*"]];
})(), ["欠番:2|5", "対象外の名前:3"]);
check("§3 次の状態には全 P-ID が入る", Object.keys(alerts(null, [row("P001", []), row("P002", ["途絶"])]).next).sort(), ["*", "P001", "P002"]);

// 本文
{
  const rows = judge([F("P001", 1, 20)]);
  const plan = alerts(null, rows, 1);
  const body = call(E, "o1LedgerMailText_", plan.alerts, rows, 1);
  check("§3 本文に P-ID と判定と日数が入る", /P001: 途絶（最終受領から 20 日）/.test(body), true);
  check("§3 本文に「やめた」と断定する語が無い（否定の注記を除く）", /やめた」ではありません/.test(body) && !/やめました|辞退|脱落/.test(body), true);
  check("§3 本文に URL・Drive の ID・メールアドレスが無い", /https?:|docs\.google|@|[A-Za-z0-9_-]{28,}/.test(body), false);
}

// ---------------------------------------------------------------------------
// §4 登録ログの読み取り
// ---------------------------------------------------------------------------
{
  const D = (y, m, d, h, mi, s) => new FakeDate(y, m - 1, d, h || 0, mi || 0, s || 0);
  const reg = (vals) => plain(E.ctx.o1LedgerRegisteredFromLog_(vals)); // ★ 関数名を文字列で書かない（ゲートの ID 形検査に当たる）
  const t = (y, m, d) => new Date(y, m - 1, d, 9, 0, 0).getTime();
  const r1 = reg([
    ["2026-09-01 09:00:00", "register", "P010", "ok", "", ""],
    ["2026-09-03 09:00:00", "assign", "P010", "ok", "", ""],
    [D(2026, 9, 2, 9), "register", "P011", "partial", "", ""],
    ["2026-09-04 09:00:00", "register", "P012", "blocked", "", ""],
    ["2026-09-04 09:00:00", "system", "", "partial", "reject-log-full", ""],
    ["2026-09-04 09:00:00", "register", "", "ok", "", ""],
    ["2026-09-04 09:00:00", "register", "Pxyz", "ok", "", ""],
  ]);
  check("§4 最古の登録日時を P-ID ごとに採る", r1.registered.P010, t(2026, 9, 1));
  check("§4 Date 型の記録日時も読める（Sheets の自動変換）", r1.registered.P011, t(2026, 9, 2));
  check("§4 blocked・system・P-ID なし・形が違う P-ID は数えない", Object.keys(r1.registered).sort(), ["P010", "P011"]);
  check("§4 日時が読めない行は捨てずに skipped に数える", reg([["昨日", "register", "P010", "ok", "", ""]]).skipped, 1);
  check("§4 空の登録ログでも例外にならない", reg([]), { registered: {}, skipped: 0 });
}

// ---------------------------------------------------------------------------
// §5 設定
// ---------------------------------------------------------------------------
const problems = (cfg) => plain(call(E, "o1LedgerConfigProblems_", cfg));
check("§5 全部あれば問題なし", problems({ folderId: "a", sheetId: "b", email: "x@example.invalid" }), []);
check("§5 宛先が空でも問題にしない（送らずログ・fail-closed）", problems({ folderId: "a", sheetId: "b", email: "" }), []);
check("§5 フォルダ ID が無ければ問題", problems({ folderId: "", sheetId: "b", email: "" }).length, 1);
check("§5 管理シート ID が無ければ問題", problems({ folderId: "a", sheetId: "", email: "" }).length, 1);
check("§5 宛先がメールの形でなければ問題（値は出さない）", (() => {
  const p = problems({ folderId: "a", sheetId: "b", email: "not-an-address" });
  return [p.length, p.join("").includes("not-an-address")];
})(), [1, false]);

// ---------------------------------------------------------------------------
// §6 通し（偽 Drive / 偽 Sheets）
// ---------------------------------------------------------------------------
const LEDGER = "O1 受領台帳";
const DASH = "O1 途絶";
// ★ 途絶タブは状況ボード（行 1〜4 が表題・件数・凡例・注意、行 5 が見出し、行 6〜 がデータ）。2026-09-28
const DASH_HEAD_ROW = 5;
const DASH_EMPTY = "（まだ登録も受領もありません）";
const dashData = (ss) => ss.sheets[DASH].rows.slice(DASH_HEAD_ROW).filter((r) => r[0] !== DASH_EMPTY);
const dashTop = (ss) => ss.sheets[DASH].rows.slice(0, DASH_HEAD_ROW - 1).map((r) => r.join(" ")).join("\n");
const regTab = (ss, rows) => {
  const s = ss.sheets["O1 登録ログ"];
  s.appendRow(["banner"]);
  s.appendRow(["記録日時", "種別", "P-ID", "結果", "理由", "備考"]);
  rows.forEach((r) => s.appendRow(r));
};
const stamp = (d) => "202609" + String(d).padStart(2, "0") + "_101112";

{
  // 6-1 冪等: 2 回回しても行が増えない
  const ss = makeSpreadsheet(["O1 登録ログ"]);
  regTab(ss, []);
  const files = [
    makeFile("id1", goodName("P001", 1, stamp(20)), 5000, ago(9)),
    makeFile("id2", goodName("P001", 2, stamp(21)), 5000, ago(1)),
  ];
  const env = makeEnv({ spreadsheet: ss, files });
  call(env, "o1LedgerRun");
  const n1 = ss.sheets[LEDGER].getLastRow();
  call(env, "o1LedgerRun");
  const n2 = ss.sheets[LEDGER].getLastRow();
  check("§6 台帳に 2 行が追記される（見出し 2 行＋データ 2 行）", n1, 4);
  check("§6★ 2 回回しても行が増えない（Drive ファイル ID で冪等）", n2, n1);
  check("§6 台帳は 10 列の見出しを持つ", ss.sheets[LEDGER].rows[1].length, 10);
  check("§6 途絶タブに P001 が正常で載る", dashData(ss)[0].slice(0, 2), ["P001", "正常"]);
  check("§6 正常のときはメールを送らない（陰性対照）", env.mails.length, 0);

  // 新着だけが足される
  files.push(makeFile("id3", goodName("P001", 3, stamp(22)), 7000, ago(0.5)));
  call(env, "o1LedgerRun");
  check("§6 新しいファイルだけが追記される", ss.sheets[LEDGER].getLastRow(), 5);
  check("§6 追記した行の P-ID と日番号が名前から入る", [ss.sheets[LEDGER].rows[4][2], ss.sheets[LEDGER].rows[4][3]], ["P001", 3]);
}

{
  // 6-2 途絶 → メール 1 通・続いても再送しない・復帰後に再送
  const ss = makeSpreadsheet(["O1 登録ログ"]);
  regTab(ss, []);
  const files = [makeFile("a1", goodName("P002", 1, stamp(10)), 100, ago(8))];
  const env = makeEnv({ spreadsheet: ss, files });
  call(env, "o1LedgerRun");
  check("§6★ 途絶（8 日）でメールが 1 通届く", env.mails.length, 1);
  check("§6 宛先は設定のとおり・件名に件数", [env.mails[0].to, /要確認 1 件/.test(env.mails[0].subject)], ["researcher@example.invalid", true]);
  check("§6 本文に P-ID・判定・日数が入る", /P002: 途絶（最終受領から 8 日）/.test(env.mails[0].body), true);
  call(env, "o1LedgerRun");
  call(env, "o1LedgerRun");
  check("§6★ 途絶が続いても再送しない（状態が変わったときだけ 1 回）", env.mails.length, 1);
  files.push(makeFile("a2", goodName("P002", 2, stamp(29)), 100, ago(0.1)));
  call(env, "o1LedgerRun");
  check("§6 復帰（新しい受領）ではメールを送らない", env.mails.length, 1);
  check("§6 復帰後は途絶タブが正常に戻る", dashData(ss)[0][1], "正常");
  NOW += 6 * DAY;
  call(env, "o1LedgerRun");
  check("§6★ 復帰の後にまた途絶になれば再送する", env.mails.length, 2);
  NOW -= 6 * DAY;
}

{
  // 6-3 宛先未設定 → 送らず、通知済みにもしない（設定後に 1 通届く）
  const ss = makeSpreadsheet(["O1 登録ログ"]);
  regTab(ss, []);
  const files = [makeFile("b1", goodName("P003", 1, stamp(10)), 100, ago(8))];
  const env = makeEnv({ spreadsheet: ss, files, props: { O1_LEDGER_NOTIFY_EMAIL: null } });
  call(env, "o1LedgerRun");
  check("§6★ 宛先が未設定なら送らない", env.mails.length, 0);
  check("§6 送らなかったことをログに残す", env.logs.some((l) => /通知を送っていません/.test(l)), true);
  check("§6★ 通知済みにしない（状態を保存しない）", "O1_LEDGER_STATE" in env.props, false);
  env.props.O1_LEDGER_NOTIFY_EMAIL = "researcher@example.invalid";
  call(env, "o1LedgerRun");
  check("§6★ 宛先を設定した後の次回に 1 通届く", env.mails.length, 1);
}

{
  // 6-4 送信失敗 → 通知済みにしない・次回に再送
  const ss = makeSpreadsheet(["O1 登録ログ"]);
  regTab(ss, []);
  const files = [makeFile("c1", goodName("P004", 1, stamp(10)), 100, ago(8))];
  const env = makeEnv({ spreadsheet: ss, files, mailFails: true });
  call(env, "o1LedgerRun");
  check("§6★ 送信に失敗したら通知済みにしない", "O1_LEDGER_STATE" in env.props, false);
  check("§6 送信失敗をログに残す（例外にはしない）", env.logs.some((l) => /送信に失敗/.test(l)), true);
}

{
  // 6-5 未受領: 登録ログと突合する
  const ss = makeSpreadsheet(["O1 登録ログ"]);
  regTab(ss, [
    [new Date(ago(9)).toISOString().replace(/T.*/, "") + " 09:00:00", "register", "P030", "ok", "", ""],
    [new Date(ago(2)).toISOString().replace(/T.*/, "") + " 09:00:00", "register", "P031", "ok", "", ""],
  ]);
  const env = makeEnv({ spreadsheet: ss, files: [] });
  call(env, "o1LedgerRun");
  const dash = dashData(ss).map((r) => [r[0], r[1]]);
  check("§6★ 登録から 9 日・受領 0 件は未受領、2 日は正常", dash, [["P030", "未受領"], ["P031", "正常"]]);
  check("§6 未受領でメールが 1 通届く", [env.mails.length, /P030: 未受領/.test(env.mails[0].body)], [1, true]);
}

{
  // 6-6 対象外の名前（G1 の混入）→ 台帳に残し・通知・数式にならない
  const ss = makeSpreadsheet(["O1 登録ログ"]);
  regTab(ss, []);
  const evil = "=HYPERLINK(\"http://x\")_o1day03_gse_o1_20260920_101112.age";
  const files = [
    makeFile("d1", "P005_block03_gse_20260807_101112.age", 100, ago(1)),
    makeFile("d2", evil, 100, ago(1)),
    makeFile("d3", goodName("P005", 1, stamp(29)), 100, ago(1)),
  ];
  const env = makeEnv({ spreadsheet: ss, files });
  call(env, "o1LedgerRun");
  const led = ss.sheets[LEDGER];
  check("§6 対象外の名前も台帳に残る（3 行）", led.getLastRow(), 5);
  check("§6 対象外の行は P-ID が空・形式が「対象外」", [led.rows[2][2], led.rows[2][9]], ["", "対象外"]);
  const formulaCells = Object.values(led.cells).filter((c) => c.kind === "formula");
  check("§6★ 数式の形のファイル名がセルの数式にならない（テキスト形式）", formulaCells.length, 0);
  check("§6 対象外の名前がある旨を途絶タブのバナーに出す", /対象外の名前 2 件/.test(dashTop(ss)), true);
  check("§6★ 対象外の名前で通知する（P-ID とは別枠）", env.mails.length === 1 && /O1 の形でないファイルが 2 件/.test(env.mails[0].body), true);
  check("§6 対象外のファイルは P-ID の集計に混ざらない", dashData(ss).map((r) => r[0]), ["P005"]);
}

{
  // 6-7 ごみ箱のファイルは数えない
  const ss = makeSpreadsheet(["O1 登録ログ"]);
  regTab(ss, []);
  const files = [makeFile("e1", goodName("P006", 1, stamp(20)), 100, ago(1), { trashed: true })];
  const env = makeEnv({ spreadsheet: ss, files });
  call(env, "o1LedgerRun");
  check("§6 ごみ箱の中のファイルは台帳に入れない", ss.sheets[LEDGER].getLastRow(), 2);
}

{
  // 6-8 時間予算で打ち切る → 次回に持ち越し（冪等なので取りこぼさない）
  const ss = makeSpreadsheet(["O1 登録ログ"]);
  regTab(ss, []);
  const files = [];
  for (let i = 1; i <= 6; i++) files.push(makeFile("f" + i, goodName("P007", i, stamp(20 + i)), 100, ago(1)));
  const startNow = NOW;
  const env = makeEnv({ spreadsheet: ss, files, tickPerFile: 100000 });
  call(env, "o1LedgerRun");
  const first = ss.sheets[LEDGER].getLastRow() - 2;
  check("§6★ 時間予算（240 秒）を超えたら打ち切る（6 件中 3 件だけ）", first, 3);
  check("§6 打ち切ったことを途絶タブのバナーに出す", /打ち切り/.test(dashTop(ss)), true);
  // 次回: 既知は飛ばされ、残りが足される
  const env2 = makeEnv({ spreadsheet: ss, files, tickPerFile: 0 });
  call(env2, "o1LedgerRun");
  check("§6★ 次回に残りが足され、重複行は出ない", ss.sheets[LEDGER].getLastRow() - 2, 6);
  NOW = startNow;
}

{
  // 6-9 ロスターのタブを持つ表には書かない
  const ss = makeSpreadsheet(["O1 登録ログ", "参加者ロスター"]);
  regTab(ss, []);
  const env = makeEnv({ spreadsheet: ss, files: [makeFile("g1", goodName("P008", 1, stamp(20)), 100, ago(1))] });
  let threw = false;
  try {
    call(env, "o1LedgerRun");
  } catch (e) {
    threw = /参加者ロスター/.test(String(e.message));
  }
  check("§6★ 「参加者ロスター」を持つ表には書かず止まる", [threw, ss.sheets[LEDGER] === undefined, ss.sheets[DASH] === undefined], [true, true, true]);
}

{
  // 6-10 ロックが取れなければ何もしない
  const ss = makeSpreadsheet(["O1 登録ログ"]);
  regTab(ss, []);
  const env = makeEnv({ spreadsheet: ss, files: [makeFile("h1", goodName("P009", 1, stamp(20)), 100, ago(1))], lockOk: false });
  call(env, "o1LedgerRun");
  check("§6★ ロックが取れなければ書かない・開きもしない", [ss.sheets[LEDGER] === undefined, env.opened()], [true, 0]);
}

{
  // 6-11 登録ログのタブが無ければ止まる（黙って未受領の判定を落とさない）
  const ss = makeSpreadsheet([]);
  const env = makeEnv({ spreadsheet: ss, files: [] });
  let msg = "";
  try {
    call(env, "o1LedgerRun");
  } catch (e) {
    msg = String(e.message);
  }
  check("§6★ 登録ログのタブが無ければ止まり、理由を言う", /登録ログ/.test(msg), true);
}

{
  // 6-12 設定が欠けていれば止まる
  const env = makeEnv({ props: { O1_RECEIVE_FOLDER_ID: null } });
  let msg = "";
  try {
    call(env, "o1LedgerRun");
  } catch (e) {
    msg = String(e.message);
  }
  check("§6 フォルダ ID が無ければ止まる", /O1_RECEIVE_FOLDER_ID/.test(msg), true);
}

{
  // 6-13 行が足りない表でも追記できる（setValues は範囲外で例外になる）
  const ss = makeSpreadsheet(["O1 登録ログ"]);
  regTab(ss, []);
  ss.sheets["O1 登録ログ"].maxRows = 1000;
  const files = [];
  for (let i = 1; i <= 30; i++) files.push(makeFile("k" + i, goodName("P011", i, stamp(1)), 100, ago(0.5)));
  const env = makeEnv({ spreadsheet: ss, files });
  // 台帳タブを、作った直後に行数を絞って追記が範囲外になるようにする
  const led = ss.insertSheet(LEDGER);
  led.maxRows = 5;
  led.appendRow(["banner"]);
  led.appendRow(plain(env.ctx.O1_LEDGER_HEAD));
  let err = "";
  try {
    call(env, "o1LedgerRun");
  } catch (e) {
    err = String(e.message);
  }
  check("§6★ 行数が足りない台帳タブでも追記できる（範囲外で落ちない）", [err, led.getLastRow()], ["", 32]);
}

{
  // 6-14 トリガー: 冪等・他のトリガーに触らない
  const other = { getHandlerFunction: () => "onO1ConsentSubmit" };
  const mine = { getHandlerFunction: () => "o1LedgerRun" };
  const env = makeEnv({ triggers: [other, mine] });
  call(env, "installO1LedgerTrigger");
  call(env, "installO1LedgerTrigger");
  const fns = env.triggers.map((t) => t.getHandlerFunction()).sort();
  check("§6★ トリガーは 1 つだけ（冪等）・他のトリガーは残る", fns, ["o1LedgerRun", "onO1ConsentSubmit"]);
  check("§6 6 時間ごと", env.triggers.find((t) => t.getHandlerFunction() === "o1LedgerRun").hours, 6);
}

{
  // 6-15 o1LedgerCheck は読み取りのみ
  const ss = makeSpreadsheet(["O1 登録ログ"]);
  const env = makeEnv({
    spreadsheet: ss,
    files: [makeFile("m1", goodName("P012", 1, stamp(20)), 100, ago(1)), makeFile("m2", "memo.txt", 9, ago(1))],
  });
  call(env, "o1LedgerCheck");
  check("§6★ o1LedgerCheck は何も書かず・メールも送らない", [Object.keys(ss.sheets), env.mails.length, "O1_LEDGER_STATE" in env.props], [["O1 登録ログ"], 0, false]);
  check("§6 o1LedgerCheck は対象外の名前と所要時間を出す", [env.logs.some((l) => /対象外: memo\.txt/.test(l)), env.logs.some((l) => /走査の所要/.test(l))], [true, true]);
}

// ---------------------------------------------------------------------------
// §8 2026-09-27 レビュー指摘の反映（無害化・運用アラート・失敗通知・削除済み・day 0・列数・時間予算）
// ---------------------------------------------------------------------------
const LEDGER_HEAD = () => plain(makeEnv().ctx.O1_LEDGER_HEAD);
const sharedProps = (extra) =>
  Object.assign({ O1_RECEIVE_FOLDER_ID: "FOLDER", O1_MGMT_SHEET_ID: "SHEET", O1_LEDGER_NOTIFY_EMAIL: "researcher@example.invalid" }, extra || {});

// 8-1 運用アラート（純関数）
{
  const ops = (prev, o) => plain(E.ctx.o1LedgerOpsAlerts_(prev, o));
  check("§8 運用アラート: 何も無ければ空", ops(null, { truncated: false, regSkipped: 0, badRows: 0 }), { added: [], next: {} });
  check("§8 運用アラート: 打ち切り・日時不読・不読行が有効になったら 3 つとも追加", ops(null, { truncated: true, regSkipped: 2, badRows: 1 }).added.sort(), ["登録ログの日時が読めない", "台帳の読めない行", "走査打切り"].sort());
  check("§8 運用アラート: 続いているだけなら再通知しない", ops({ "走査打切り": true }, { truncated: true, regSkipped: 0, badRows: 0 }).added, []);
  check("§8 運用アラート: 解消したら次の状態から消える（再発すれば再通知）", (() => {
    const s1 = ops({ "走査打切り": true }, { truncated: false, regSkipped: 0, badRows: 0 }).next;
    return [s1, ops(s1, { truncated: true, regSkipped: 0, badRows: 0 }).added];
  })(), [{}, ["走査打切り"]]);
}

// 8-2 無害化（純関数）＋書き込み結果
{
  const safe = (v) => E.ctx.o1LedgerSafeCell_(v);
  check("§8 無害化: 先頭が = + - @ タブ CR なら ⚠ を前置", ["=A1", "+1", "-1", "@SUM(1)", "\tx", "\rx"].map(safe), ["⚠=A1", "⚠+1", "⚠-1", "⚠@SUM(1)", "⚠\tx", "⚠\rx"]);
  check("§8 無害化: 普通の名前・数値・空文字は変えない", [safe("P012_o1day03.age"), safe(5), safe("")], ["P012_o1day03.age", 5, ""]);
  check("§8 無害化: 途中に = があるだけなら変えない", safe("a=b"), "a=b");

  const ss = makeSpreadsheet(["O1 登録ログ"]);
  regTab(ss, []);
  const names = ["=HYPERLINK(\"x\").age", "+1+1.age", "-2.age", "@SUM(1).age", "memo.txt"];
  const files = names.map((n, i) => makeFile("z" + i, n, 10, ago(1)));
  const env = makeEnv({ spreadsheet: ss, files });
  call(env, "o1LedgerRun");
  const led = ss.sheets[LEDGER];
  const startRow = 3;
  const nameCol = 2;
  const stored = names.map((_, i) => led.rows[startRow - 1 + i][nameCol - 1]);
  check("§8★ 名前列に書かれた値は = + - @ で始まらない（表示形式に頼らない防御）", stored.some((v) => /^[=+\-@\t\r]/.test(v)), false);
  const fm = (col) => led.formats[startRow + ",".concat(col)];
  check("§8★ 文字列の列（ID・名前・P-ID・開始・受領日時・重複・形式）はテキスト形式で書かれる（二重の防御）", [1, 2, 3, 5, 6, 9, 10].map(fm), ["@", "@", "@", "@", "@", "@", "@"]);
  check("§8 数値の列（日番号・epoch・バイト数）はテキスト形式にしない", [4, 7, 8].map(fm), [undefined, undefined, undefined]);
}

// 9-5 途絶タブの書き込みにも無害化がかかる
//   ★ 台帳の P-ID 列は同期時にファイル名の正規表現で絞られるが、**研究者が台帳の行を手で編集**すると
//   任意の文字列になりうる（欠番の tombstone 作業中の誤入力などを含む）。その値が「途絶」タブへ
//   そのまま転記されないことを、実際の書き込み経路（`o1LedgerRun` → setValues）で確かめる。
{
  const ss = makeSpreadsheet(["O1 登録ログ"]);
  regTab(ss, []);
  const led = ss.insertSheet(LEDGER);
  led.appendRow(["banner"]);
  led.appendRow(LEDGER_HEAD());
  led.appendRow(["x9", "whatever.age", "=EVIL()", 1, "", "2026-09-20 10:11:12", ago(1), 5, "", "O1"]);
  const env = makeEnv({ spreadsheet: ss, files: [] });
  call(env, "o1LedgerRun");
  check(
    "§9★ 台帳の P-ID を手編集で「=EVIL()」にしても、途絶タブへ数式の形のまま転記されない",
    /^[=+\-@\t\r]/.test(dashData(ss)[0][0]),
    false
  );
}

// 9-6 運用アラートだけの回は、件名・見出しで「P-ID の異常ではない」と分かる（code-reviewer L-3 指摘）
{
  const ss2 = makeSpreadsheet(["O1 登録ログ"]);
  regTab(ss2, []);
  const files2 = Array.from({ length: 6 }, (_, i) => makeFile("o" + i, goodName("P110", i + 1, stamp(20 + i)), 100, ago(1)));
  const env2 = makeEnv({ spreadsheet: ss2, files: files2, tickPerFile: 100000 });
  call(env2, "o1LedgerRun");
  check(
    "§9★ 運用アラートだけの通知は件名が「運用アラート」・本文が「P-ID の異常ではありません」",
    [env2.mails[0].subject, /P-ID の異常ではありません/.test(env2.mails[0].body)],
    ["[GSE O1] 受領台帳: 運用アラート 1 件", true]
  );
}

// 8-3 欠番の列挙の丸め（純関数）
{
  const list = (g) => E.ctx.o1LedgerListGaps_(g);
  check("§8 欠番の列挙: 10 件までは全部", list([1, 2, 3]), "1, 2, 3");
  check("§8 欠番の列挙: 上限を超えたら「他 N 件」に丸める", list(Array.from({ length: 25 }, (_, i) => i + 1)), "1, 2, 3, 4, 5, 6, 7, 8, 9, 10 …他 15 件");
  const rows = judge([F("P001", 1, 30), F("P001", 999, 10)]);
  const body = E.ctx.o1LedgerMailText_(plain(alerts(null, rows).alerts), rows, 0, []);
  check("§8 欠番が 997 件でも本文は短い", body.length < 700, true);
}

// 8-4 日番号 0
{
  check("§8 日番号 00 の名前も読める（受け口と同じ）", (parse("P012_o1day00_gse_o1_20260920_101112.age") || {}).day, 0);
  const r = judge([F("P050", 0, 1)], { P050: ago(30) })[0];
  check("§8★ 日番号 0 のファイルも「受領」に数える（届いているのに未受領にしない）", [r.files, r.flags], [1, []]);
  check("§8 日番号 0 は番号の集合に入れない（欠番の基準にしない）", [r.uniqueDays, r.gaps], [0, []]);
  // 通し: 登録から 30 日・日番号 0 のファイルだけが届いている人は「未受領」ではなく、台帳の不読行にもならない
  const ss = makeSpreadsheet(["O1 登録ログ"]);
  const d30 = new Date(ago(30));
  const p2 = (n) => String(n).padStart(2, "0");
  regTab(ss, [[`${d30.getFullYear()}-${p2(d30.getMonth() + 1)}-${p2(d30.getDate())} 09:00:00`, "register", "P051", "ok", "", ""]]);
  const env = makeEnv({ spreadsheet: ss, files: [makeFile("d0", "P051_o1day00_gse_o1_20260920_101112.age", 10, ago(1))] });
  call(env, "o1LedgerRun");
  check("§8★ 通し: 日番号 0 だけ届いている人は未受領にならず、不読行にもならない", [env.mails.length, /読めない行/.test(dashTop(ss)), dashData(ss)[0][1]], [0, false, "正常"]);
}

// 8-5 受け口との突合を、生成した大量の名前で（手選びの 15 件だけに頼らない）
{
  const sctx = { console: { log() {} } };
  vm.createContext(sctx);
  vm.runInContext(submitSrc, sctx);
  const pids = ["P012", "A", "P0123456789012345", "P01234567890123456", "P_1", "", "p1", "9"];
  const days = ["", "0", "00", "01", "1", "001", "999", "1000", "ab"];
  const stamps = ["20260920_101112", "2026092_101112", "20260920_10111", "20260920-101112"];
  const seqs = ["", "_2", "_12345678901", "_x", "_"];
  const exts = [".age", ".AGE", ".age.bak", ""];
  let n = 0;
  const disagree = [];
  for (const pid of pids) for (const d of days) for (const st of stamps) for (const sq of seqs) for (const ex of exts) {
    const name = `${pid}_o1day${d}_gse_o1_${st}${sq}${ex}`;
    n++;
    if ((sctx.sanitizeName_(name) !== "") !== (parse(name) !== null)) disagree.push(name);
  }
  check("§8★ 受け口の sanitizeName_ と、生成した " + n + " 件の名前で読める集合が一致する", disagree.slice(0, 3), []);
}

// 8-6 走査の打ち切り: 判定の通知を保留し、運用アラートを 1 回だけ出す → 次の完全な走査で保留分が届く
{
  const ss = makeSpreadsheet(["O1 登録ログ"]);
  regTab(ss, []);
  const P = sharedProps();
  const files = [
    makeFile("t1", goodName("P040", 1, stamp(20)), 100, ago(8)), // 部分台帳では「途絶」に見える（本当は下の t6 が届いている）
    makeFile("t2", goodName("P042", 1, stamp(20)), 100, ago(9)), // 本当に途絶
    makeFile("t3", goodName("P041", 1, stamp(21)), 100, ago(1)),
    makeFile("t4", goodName("P041", 2, stamp(22)), 100, ago(1)),
    makeFile("t5", goodName("P041", 3, stamp(23)), 100, ago(1)),
    makeFile("t6", goodName("P040", 2, stamp(29)), 100, ago(0.1)),
  ];
  const startNow = NOW;
  const env1 = makeEnv({ spreadsheet: ss, files, propsObj: P, tickPerFile: 100000 });
  call(env1, "o1LedgerRun");
  check("§8★ 打ち切りの回は、部分台帳による誤報（P040 途絶）を送らない", env1.mails.some((m) => /P040/.test(m.body)), false);
  check("§8★ 打ち切りの回は判定の状態を保存しない", "O1_LEDGER_STATE" in P, false);
  check("§8★ 打ち切りは運用アラートとして 1 通だけ通知する", [env1.mails.length, /走査が時間予算で打ち切られました/.test((env1.mails[0] || {}).body || "")], [1, true]);
  NOW = startNow;
  const env2 = makeEnv({ spreadsheet: ss, files, propsObj: P, tickPerFile: 0 });
  call(env2, "o1LedgerRun");
  check("§8★ 次の完全な走査で、保留していた本当の途絶（P042）が届く（誤報だった P040 は届かない）", [env2.mails.length, /P042: 途絶/.test((env2.mails[0] || {}).body || ""), env2.mails.some((m) => /P040/.test(m.body))], [1, true, false]);
  const env3 = makeEnv({ spreadsheet: ss, files, propsObj: P, tickPerFile: 0 });
  call(env3, "o1LedgerRun");
  check("§8 その後は再通知しない", env3.mails.length, 0);
  NOW = startNow;
}

// 8-7 登録ログの日時が読めない行・台帳の読めない行 → 運用アラート
{
  const ss = makeSpreadsheet(["O1 登録ログ"]);
  regTab(ss, [["昨日", "register", "P060", "ok", "", ""]]);
  const led = ss.insertSheet(LEDGER);
  led.appendRow(["banner"]);
  led.appendRow(LEDGER_HEAD());
  led.appendRow(["bad1", "P061_o1day01_gse_o1_20260920_101112.age", "", 1, "", "", ago(1), 5, "", "O1"]); // P-ID が空の O1 行
  const env = makeEnv({ spreadsheet: ss, files: [] });
  call(env, "o1LedgerRun");
  const body = (env.mails[0] || {}).body || "";
  check("§8★ 登録ログの日時が読めない行は、バナーだけでなく通知する", /登録ログに日時を読めない行/.test(body), true);
  check("§8★ 台帳の読めない行も通知する", /台帳に読めない行/.test(body), true);
  check("§8 バナーにも件数が出る", /読めない行 1/.test(dashTop(ss)) && /日時が読めない行 1/.test(dashTop(ss)), true);
}

// 8-8 削除済み（tombstone）: 数えない・不読行にしない・復活しない
{
  const ss = makeSpreadsheet(["O1 登録ログ"]);
  regTab(ss, []);
  const led = ss.insertSheet(LEDGER);
  led.appendRow(["banner"]);
  led.appendRow(LEDGER_HEAD());
  led.appendRow(["tomb1", "", "", "", "", "2026-09-20 10:11:12", ago(30), 5, "", "削除済"]);
  const env = makeEnv({ spreadsheet: ss, files: [makeFile("tomb1", goodName("P070", 1, stamp(20)), 5, ago(30))] });
  call(env, "o1LedgerRun");
  check("§8★ 削除済みの行は不読行に数えず、通知もしない", [env.mails.length, /読めない行/.test(dashTop(ss))], [0, false]);
  check("§8★ 削除済みの Drive ファイル ID は残り、同じファイルが別の行として復活しない", led.getLastRow(), 3);
  check("§8 削除済みは P-ID の集計に出ない", dashData(ss).length, 0);
}

// 8-9 実行の失敗: 研究者へ 1 回通知・同じ原因では再送しない・直ったら解消・例外は再送出
{
  const ss = makeSpreadsheet([]); // 登録ログのタブが無い → 実行が失敗する
  const P = sharedProps();
  const files = [makeFile("q1", goodName("P080", 1, stamp(20)), 100, ago(1))];
  const runFail = () => {
    const env = makeEnv({ spreadsheet: ss, files, propsObj: P });
    let threw = false;
    try {
      call(env, "o1LedgerRun");
    } catch (e) {
      threw = true;
    }
    return { env, threw };
  };
  const a = runFail();
  check("§8★ 実行が失敗したら例外を握りつぶさず再送出する", a.threw, true);
  check("§8★ 実行の失敗を研究者へ通知する（検知器の沈黙を外へ出す）", [a.env.mails.length, /実行が失敗しました/.test((a.env.mails[0] || {}).subject || ""), /登録ログ/.test((a.env.mails[0] || {}).body || "")], [1, true, true]);
  const b = runFail();
  check("§8★ 同じ原因では再送しない", b.env.mails.length, 0);
  ss.insertSheet("O1 登録ログ");
  regTab(ss, []);
  const c = makeEnv({ spreadsheet: ss, files, propsObj: P });
  call(c, "o1LedgerRun");
  check("§8★ 成功すると失敗の状態が解消する", "O1_LEDGER_FAIL" in P, false);
  ss.sheets["O1 登録ログ"].clearContents();
  delete ss.sheets["O1 登録ログ"];
  const d = runFail();
  check("§8 解消後に再び失敗すれば再通知する", d.env.mails.length, 1);
}
{
  // 宛先が無ければ失敗の通知も送らない（例外は出る）／本文に ID を載せない／ロック不成立は失敗ではない
  const ss = makeSpreadsheet(["O1 登録ログ"]);
  regTab(ss, []);
  const longId = "A".repeat(40);
  const env = makeEnv({ spreadsheet: ss, props: { O1_MGMT_SHEET_ID: longId } });
  let threw = false;
  try {
    call(env, "o1LedgerRun");
  } catch (e) {
    threw = true;
  }
  const body = (env.mails[0] || {}).body || "";
  check("§8★ 失敗の通知に長い英数字（ID の形）を載せない", [threw, env.mails.length, body.includes(longId), /<ID>/.test(body)], [true, 1, false, true]);
  const env2 = makeEnv({ spreadsheet: ss, props: { O1_MGMT_SHEET_ID: longId, O1_LEDGER_NOTIFY_EMAIL: null } });
  try {
    call(env2, "o1LedgerRun");
  } catch (e) {}
  check("§8 宛先が未設定なら失敗の通知は送らない", env2.mails.length, 0);
  check("§8★ 宛先未設定時も理由をログに残す（沈黙させない）", env2.logs.some((l) => /未設定なので実行失敗の通知を送っていません/.test(l)), true);
  const env3 = makeEnv({ spreadsheet: ss, lockOk: false });
  call(env3, "o1LedgerRun");
  check("§8 ロックが取れなかった回は「失敗」として通知しない", env3.mails.length, 0);
}

// 8-10 登録ログの列が足りない・見出しの中身が違う場合、理由を言って止まる（範囲外の例外にしない）
{
  // (a) 列そのものが削除された表（★ 実 Sheets は既定で 26 列あるので、これは「列削除」を模す）
  const ss = makeSpreadsheet(["O1 登録ログ"]);
  ss.sheets["O1 登録ログ"] = makeSheet("O1 登録ログ", { maxColumns: 5 });
  ss.sheets["O1 登録ログ"].appendRow(["b", "", "", "", ""]);
  ss.sheets["O1 登録ログ"].appendRow(["記録日時", "種別", "P-ID", "結果", "理由"]);
  const env = makeEnv({ spreadsheet: ss, props: { O1_LEDGER_NOTIFY_EMAIL: null } });
  let msg = "";
  try {
    call(env, "o1LedgerRun");
  } catch (e) {
    msg = String(e.message);
  }
  check("§8 登録ログの列そのものが 6 列未満なら理由を言って止まる", /6 列に足りません/.test(msg), true);
}
{
  // (b) 列数は足りる（既定 26 列）が、内容が挿入されて 3 列目が「P-ID」でなくなっている
  //   （2026-09-27 レビュー指摘 MEDIUM: 列数だけの検査は、列を挿入されて中身がずれても気づけない）
  const ss = makeSpreadsheet(["O1 登録ログ"]);
  ss.sheets["O1 登録ログ"].appendRow(["banner"]);
  ss.sheets["O1 登録ログ"].appendRow(["記録日時", "種別", "担当", "P-ID", "結果", "理由"]);
  const env = makeEnv({ spreadsheet: ss, props: { O1_LEDGER_NOTIFY_EMAIL: null } });
  let msg = "";
  try {
    call(env, "o1LedgerRun");
  } catch (e) {
    msg = String(e.message);
  }
  check("§8★ 見出しの中身が違えば、列数が足りていても理由を言って止まる", /見出しの 3 列目が「担当」です/.test(msg), true);
}

// 8-11 o1LedgerCheck: 時間予算・タイムゾーン・実行ログの注意
{
  const files = [];
  for (let i = 1; i <= 6; i++) files.push(makeFile("c" + i, i % 2 ? goodName("P090", i, stamp(20)) : "memo" + i + ".txt", 9, ago(1)));
  const startNow = NOW;
  const env = makeEnv({ spreadsheet: makeSpreadsheet(["O1 登録ログ"]), files, tickPerFile: 100000 });
  call(env, "o1LedgerCheck");
  const log = env.logs.join("\n");
  check("§8★ o1LedgerCheck も時間予算で打ち切り、打ち切ったことと件数を出す", [/時間予算で打ち切り/.test(log), /O1 の形: \d+ 件 ／ 対象外: \d+ 件/.test(log)], [true, true]);
  // ★ 件数まで固定する（2026-09-28）: 走査の期限はイテレータ側にもあるので、ループの予算検査を外しても
  //   「打ち切り」の文言だけは出てしまう（変異が素通りした）。★ 予算内に読めたのは 3 本（100 秒 × 3 > 240 秒）。
  check("§8★ o1LedgerCheck は予算を超えた時点で止まる（6 本中 3 本だけ読む）", /O1 の形: 2 件 ／ 対象外: 1 件/.test(log), true);
  check("§8 o1LedgerCheck はタイムゾーンを出す", /タイムゾーン: Asia\/Tokyo/.test(log), true);
  check("§8 o1LedgerCheck は実行ログに P-ID が残りうる注意を出す", /A-10/.test(log), true);
  NOW = startNow;
}

// ---------------------------------------------------------------------------
// §9 2026-09-27 2 回目レビュー指摘の反映（辞書キーの安全化・Drive ID の無害化除外・打切りの再通知）
// ---------------------------------------------------------------------------

// 9-1 P-ID が Object.prototype のプロパティ名と同じでも例外にならない（Codex 実測で確定した穴）
{
  check("§9★ P-ID が「constructor」でも判定が例外にならない", (() => {
    try {
      return { rows: judge([F("constructor", 1, 1)]).length, ok: true };
    } catch (e) {
      return { ok: false, msg: String(e.message) };
    }
  })(), { rows: 1, ok: true });
  ["toString", "__proto__", "hasOwnProperty", "valueOf"].forEach((pid) => {
    check(`§9 P-ID が「${pid}」でも判定が例外にならない`, (() => {
      try {
        judge([F(pid, 1, 1)]);
        return true;
      } catch (e) {
        return false;
      }
    })(), true);
  });
  check("§9 「constructor」と他 P-ID を混ぜても互いに混線しない", (() => {
    const rows = judge([F("constructor", 1, 9), F("P001", 1, 1)]);
    return [flagsOf(rows, "constructor"), flagsOf(rows, "P001")];
  })(), [["途絶"], []]);
  check("§9★ 受領 0 件・登録ログにだけ「constructor」がいても行が作られる（seen の辞書キー汚染）", judge([], { constructor: ago(30) }).map((r) => r.pid), ["constructor"]);
  // 通知の差分・登録ログの突合でも同じキーが安全か
  check("§9 通知の差分で P-ID が「constructor」でも例外にならない", (() => {
    try {
      alerts(null, [row("constructor", ["途絶"])]);
      return true;
    } catch (e) {
      return false;
    }
  })(), true);
  check("§9 登録ログで P-ID 相当が「constructor」でも例外にならない（形は P\d+ なので実際は弾かれる）", (() => {
    const r = E.ctx.o1LedgerRegisteredFromLog_([["2026-09-01 09:00:00", "register", "constructor", "ok", "", ""]]);
    return Object.keys(plain(r.registered));
  })(), []);
}

// 9-2 Drive ファイル ID が「-」で始まっても、無害化されず冪等性が保たれる（H-1）
{
  const ss = makeSpreadsheet(["O1 登録ログ"]);
  regTab(ss, []);
  const files = [makeFile("-Ab3xY_dash-leading-id", goodName("P095", 1, stamp(20)), 100, ago(1))];
  const env = makeEnv({ spreadsheet: ss, files });
  call(env, "o1LedgerRun");
  const led = ss.sheets[LEDGER];
  check("§9★ 先頭が「-」の Drive ファイル ID がそのまま（無害化されず）書かれる", led.rows[2][0], "-Ab3xY_dash-leading-id");
  call(env, "o1LedgerRun"); // 2 回目
  check("§9★ 先頭が「-」の ID でも 2 回目で増殖しない（冪等性）", led.getLastRow(), 3);
}

// 9-3 走査打ち切りが続く間、運用アラートを沈黙させない（M-4・cross-review #1 一致）
{
  const ss = makeSpreadsheet(["O1 登録ログ"]);
  regTab(ss, []);
  const P = sharedProps();
  const manyFiles = Array.from({ length: 5 }, (_, i) => makeFile("m" + i, goodName("P100", i + 1, stamp(20 + i)), 100, ago(1)));
  const startNow = NOW;
  const env1 = makeEnv({ spreadsheet: ss, files: manyFiles, propsObj: P, tickPerFile: 100000 });
  call(env1, "o1LedgerRun");
  check("§9 初回の打ち切りで運用アラートが 1 通", env1.mails.length, 1);
  const env2 = makeEnv({ spreadsheet: ss, files: manyFiles, propsObj: P, tickPerFile: 100000 });
  call(env2, "o1LedgerRun");
  check("§9 直後の 2 回目は再通知しない（同じ理由が続いているだけ）", env2.mails.length, 0);
  NOW += 8 * DAY; // 再通知の間隔（7 日）を超える
  const env3 = makeEnv({ spreadsheet: ss, files: manyFiles, propsObj: P, tickPerFile: 100000 });
  call(env3, "o1LedgerRun");
  check("§9★ 打ち切りが続いたまま 7 日たつと、沈黙させず再通知する", env3.mails.length, 1);
  NOW = startNow;
}

// 9-4 台帳の日番号セルが空・非数値なら不読行にする（day 0 への取り違えを防ぐ）
{
  const mk = (dayCell) => {
    const ss = makeSpreadsheet(["O1 登録ログ"]);
    regTab(ss, []);
    const led = ss.insertSheet(LEDGER);
    led.appendRow(["banner"]);
    led.appendRow(LEDGER_HEAD());
    led.appendRow(["x1", "P099_o1day01_gse_o1_20260920_101112.age", "P099", dayCell, "", "2026-09-20 10:11:12", ago(1), 5, "", "O1"]);
    const env = makeEnv({ spreadsheet: ss, files: [] });
    call(env, "o1LedgerRun");
    return { mails: env.mails, banner: dashTop(ss), dashRows: dashData(ss) };
  };
  const empty = mk("");
  check("§9★ 日番号セルが空なら「受領 0 件」（day 0 に化けず不読行として数える・行も作らない）", [empty.dashRows.length, /読めない行 1/.test(empty.banner), /読めない行/.test((empty.mails[0] || {}).body || "")], [0, true, true]);
  const bad = mk("abc");
  check("§9 日番号セルが非数値でも不読行として扱う", /読めない行 1/.test(bad.banner), true);
}

// 9-7 登録ログのタブはあるが空（見出しが無い）なら、未受領の判定を無音で落とさず止める（3 回目レビュー指摘・自己後退の修正）
{
  const ss = makeSpreadsheet(["O1 登録ログ"]); // タブは作られるが append は一切しない＝空
  const env = makeEnv({ spreadsheet: ss, files: [], props: { O1_LEDGER_NOTIFY_EMAIL: null } });
  let msg = "";
  try {
    call(env, "o1LedgerRun");
  } catch (e) {
    msg = String(e.message);
  }
  check("§9★ 登録ログのタブが空（見出し行が無い）なら理由を言って止まる（未受領判定を無音で失わない）", /見出し行がありません/.test(msg), true);
}

// 9-8 registered のキーが「constructor」でも例外にならず・値が正しく引ける（辞書キー安全化の同型 2 件目）
{
  const reg = E.ctx.o1LedgerRegisteredFromLog_([["2026-09-01 09:00:00", "register", "constructor", "ok", "", ""]]);
  check("§9 registered のキーが「constructor」でも取り出せる（形は P\\d+ 限定なのでここには来ないが、辞書として安全）", plain(reg.registered), {});
}

// 9-9 実運用の経路（登録ログ→o1LedgerRun）で、P-ID「constructor」の受領があっても
//   「登録からの日数」が NaN にならない（registered の辞書キー汚染が実際に効く唯一の経路）
{
  const ss = makeSpreadsheet(["O1 登録ログ"]);
  regTab(ss, []); // ★ 登録ログは空（"constructor" は P\d+ の形でないので、正規の経路では絶対に登録されない）
  const env = makeEnv({ spreadsheet: ss, files: [makeFile("ctor1", goodName("constructor", 1, stamp(20)), 100, ago(1))] });
  call(env, "o1LedgerRun");
  const row = ss.sheets[DASH].rows.find((r) => r[0] === "constructor");
  check("§9★ P-ID が「constructor」でも「登録からの日数」が NaN にならない（registered の辞書キー安全化）", row[8], "");
}

// 9-10 日番号セルが桁あふれ（Number() が Infinity）でも、判定ループがハングしない
//   （2026-09-27 3 回目レビュー指摘 HIGH・Codex 発見。判断17 が isFinite チェックを落とした副作用）
{
  const bigDigits = "1".repeat(400); // Number(...) === Infinity
  const ss = makeSpreadsheet(["O1 登録ログ"]);
  regTab(ss, []);
  const led = ss.insertSheet(LEDGER);
  led.appendRow(["banner"]);
  led.appendRow(LEDGER_HEAD());
  led.appendRow(["h1", "P120_o1dayXXX_gse_o1_20260920_101112.age", "P120", bigDigits, "", "2026-09-20 10:11:12", ago(1), 5, "", "O1"]);
  const env = makeEnv({ spreadsheet: ss, files: [] });
  const t0 = Date.now();
  let threw = false;
  let msg = "";
  try {
    call(env, "o1LedgerRun");
  } catch (e) {
    threw = true;
    msg = String(e.message);
  }
  const elapsedMs = Date.now() - t0;
  check("§9★ 桁あふれの日番号（Number が Infinity）でもハングしない（1 秒未満で返る）", elapsedMs < 1000, true);
  check("§9★ 桁あふれの日番号は不読行として扱う（欠番ループへ Infinity を渡さない）", /読めない行 1/.test(dashTop(ss)), true);
}

// ---------------------------------------------------------------------------
// §10 2026-09-28 受け口が `<受け取りフォルダ>/<P-ID>/` に保存する版になった（受け口 V-3）
//   ⚠️★★★ 直下しか読まない台帳だと、全員が「未受領・途絶」と誤報される。その陰性対照を含む。
// ---------------------------------------------------------------------------
{
  const ss = makeSpreadsheet(["O1 登録ログ"]);
  const d9 = new Date(ago(9));
  const p2 = (n) => String(n).padStart(2, "0");
  const reg9 = `${d9.getFullYear()}-${p2(d9.getMonth() + 1)}-${p2(d9.getDate())} 09:00:00`;
  regTab(ss, [
    [reg9, "register", "P070", "ok", "", ""],
    [reg9, "register", "P071", "ok", "", ""],
    [reg9, "register", "P072", "ok", "", ""],
  ]);
  const env = makeEnv({
    spreadsheet: ss,
    // 直下 = 旧形式の P071 ＋ 対象外 1 本
    files: [makeFile("r1", goodName("P071", 1, stamp(26)), 10, ago(1)), makeFile("r2", "memo.txt", 3, ago(1))],
    subfolders: [
      { files: [] }, // 空のサブフォルダでも壊れない
      { files: [makeFile("s1", goodName("P070", 1, stamp(26)), 10, ago(2)), makeFile("s2", goodName("P070", 2, stamp(27)), 10, ago(1))] },
      // ⚠️ ごみ箱のサブフォルダ（削除要求で捨てた P072）は受領に数えない
      { trashed: true, files: [makeFile("t1", goodName("P072", 1, stamp(26)), 10, ago(1))] },
    ],
  });
  call(env, "o1LedgerRun");
  const ids = ss.sheets[LEDGER].rows.slice(2).map((r) => r[0]).sort();
  check("§10★ サブフォルダ内のファイルも台帳に載る（直下の旧形式・対象外も載る）", ids, ["r1", "r2", "s1", "s2"]);
  const dash = Object.fromEntries(dashData(ss).map((r) => [r[0], r[1]]));
  check("§10★ サブフォルダにだけ届いた P070 は未受領にならない", dash.P070, "正常");
  check("§10 直下の旧形式の P071 も正常", dash.P071, "正常");
  check("§10★ ごみ箱のサブフォルダにしか無い P072 は受領に数えない（未受領）", dash.P072, "未受領");
  call(env, "o1LedgerRun");
  check("§10 サブフォルダを含めても 2 回目で行が増えない（冪等）", ss.sheets[LEDGER].rows.length - 2, 4);

  const env2 = makeEnv({
    spreadsheet: makeSpreadsheet(["O1 登録ログ"]),
    files: [],
    subfolders: [{ files: [makeFile("s1", goodName("P070", 1, stamp(26)), 10, ago(2))] }, { files: [makeFile("s9", "x.bin", 1, ago(2))] }],
  });
  call(env2, "o1LedgerCheck");
  check("§10★ o1LedgerCheck もサブフォルダを数える", env2.logs.some((l) => /O1 の形: 1 件 ／ 対象外: 1 件/.test(l)), true);
}

{
  // ⚠️★★ 空のサブフォルダが大量にある（シークレット保持者が P-ID を変えて作れる）→
  //   列挙も時間予算の中で打ち切り、実行ごと落ちない（2026-09-28 security-checker MEDIUM）
  const ss = makeSpreadsheet(["O1 登録ログ"]);
  regTab(ss, []);
  const empties = Array.from({ length: 50 }, () => ({ files: [] }));
  const env = makeEnv({
    spreadsheet: ss,
    files: [makeFile("r1", goodName("P080", 1, stamp(26)), 10, ago(1))],
    subfolders: empties.concat([{ files: [makeFile("s1", goodName("P081", 1, stamp(26)), 10, ago(1))] }]),
    tickPerFolder: 10000, // 50 × 10 秒 = 500 秒 > 予算 240 秒
  });
  let threw = null;
  try {
    call(env, "o1LedgerRun");
  } catch (e) {
    threw = String(e);
  }
  check("§10★ 空フォルダの列挙が予算を超えても例外で落ちない", threw, null);
  check("§10★ その場合は「打ち切り」としてバナーに出る（完走と偽らない）", /打ち切り/.test(dashTop(ss)), true);
  check("§10 打ち切りの前に読めた直下のファイルは台帳に載る", ss.sheets[LEDGER].rows.slice(2).map((r) => r[0]), ["r1"]);
  const env2 = makeEnv({
    spreadsheet: makeSpreadsheet(["O1 登録ログ"]),
    files: [],
    subfolders: empties,
    tickPerFolder: 10000,
  });
  call(env2, "o1LedgerCheck");
  check("§10★ o1LedgerCheck も空フォルダの列挙で打ち切りを出す", env2.logs.some((l) => /時間予算で打ち切り/.test(l)), true);
}

// ---------------------------------------------------------------------------
// §11 見た目（2026-09-28 状況ボード・`.steering/20260928-o1-mgmt-sheet-design/`）
//   ★ 値の意味は変えず、配置・並び・色だけを固定する。
// ---------------------------------------------------------------------------
{
  const UI = plain(E.ctx.O1_UI);
  const ss = makeSpreadsheet(["O1 登録ログ"]);
  const p2 = (n) => String(n).padStart(2, "0");
  const regAt = (daysAgo) => {
    const d = new Date(ago(daysAgo));
    return `${d.getFullYear()}-${p2(d.getMonth() + 1)}-${p2(d.getDate())} 09:00:00`;
  };
  regTab(ss, [[regAt(9), "register", "P012", "ok", "", ""]]);
  const files = [
    makeFile("n1", goodName("P010", 1, stamp(20)), 10, ago(8)), // 途絶
    makeFile("g1", goodName("P011", 1, stamp(20)), 10, ago(8)), // 欠番（2 が抜け・3 が 6 日前）
    makeFile("g3", goodName("P011", 3, stamp(22)), 10, ago(6)),
    makeFile("g4", goodName("P011", 4, stamp(23)), 10, ago(1)),
    makeFile("a1", goodName("P10", 1, stamp(27)), 10, ago(0.5)), // 正常
    makeFile("b1", goodName("P9", 1, stamp(27)), 10, ago(0.5)), // 正常
  ];
  const env = makeEnv({ spreadsheet: ss, files });
  call(env, "o1LedgerRun");
  const D = ss.sheets[DASH];
  const H = DASH_HEAD_ROW;
  check("§11 行 5 が見出し・見出しより上は固定される", [D.rows[H - 1].slice(0, 2), D.frozen], [["P-ID", "判定"], H]);
  check("§11 表題帯に「O1 受領状況」と更新時刻が出る", /^O1 受領状況.*更新 \d{4}-\d{2}-\d{2}/.test(D.rows[0][0]), true);
  check("§11★ 要対応順（途絶 → 欠番 → 未受領 → 正常）、同順位は P-ID の数字順（P9 < P10）", dashData(ss).map((r) => [r[0], r[1]]), [
    ["P010", "途絶"], ["P011", "欠番"], ["P012", "未受領"], ["P9", "正常"], ["P10", "正常"],
  ]);
  check("§11 件数の行に内訳が出る", /要対応 3 人（途絶 1・欠番 1・未受領 1）.*正常 2 人/.test(D.rows[1][0]), true);
  {
    // ★ 内訳は 1 人 1 回（いちばん重い判定）。「途絶・欠番」の人は途絶に数える → 内訳の和 = 要対応の人数
    const sh = makeSpreadsheet([]).insertSheet("B");
    call(E, "o1LedgerWriteBoard_", sh, [
      { pid: "P1", flags: ["途絶", "欠番"], lastReceivedMs: ago(6), elapsedDays: 6, uniqueDays: 1, dupCount: 0, totalBytes: 0, gaps: [2], sinceRegDays: 9 },
      { pid: "P2", flags: ["欠番"], lastReceivedMs: ago(1), elapsedDays: 1, uniqueDays: 2, dupCount: 0, totalBytes: 0, gaps: [1], sinceRegDays: 9 },
    ], { nowMs: NOW, truncated: false, foreignCount: 0, badRows: 0, regSkipped: 0 });
    check("§11★ 内訳は 1 人 1 回（途絶・欠番の人は途絶）＝内訳の和が要対応の人数", /要対応 2 人（途絶 1・欠番 1・未受領 0）/.test(sh.rows[1][0]), true);
  }
  check("§11 要対応がいれば件数の行は赤地", D.styleAt(2, 1).bg, UI.dangerBg);
  check("§11 凡例の日数は定数から（途絶 5・欠番 5・未受領 7）", [D.rows[2][2], D.rows[2][5], D.rows[2][8]], [
    "最終受領から 5 日以上届かない", "後の番号から 5 日埋まらない", "登録から 7 日で 0 件",
  ]);
  check("§11 凡例の色見本は判定の色と同じ", [D.styleAt(3, 2).bg, D.styleAt(3, 5).bg, D.styleAt(3, 8).bg], [UI.dangerBg, UI.gapBg, UI.warnBg]);
  const flagBg = (i) => D.styleAt(H + 1 + i, 2).bg;
  check("§11★ 判定セルの色（途絶=赤・欠番=橙・未受領=黄・正常=塗らない）", [flagBg(0), flagBg(1), flagBg(2), flagBg(3) || null], [
    UI.dangerBg, UI.gapBg, UI.warnBg, null,
  ]);
  check("§11 正常は緑字", D.styleAt(H + 4, 2).fg, UI.okFg);
  check("§11 経過日数が途絶の日数以上なら赤字（途絶の行）", D.styleAt(H + 1, 4).fg, UI.dangerFg);
  check("§11 見出しは紺帯・白字", [D.styleAt(H, 1).bg, D.styleAt(H, 1).fg], [UI.navy, UI.white]);
  check("§11 表題帯・件数・注意の行は結合される", ["1,1,1,9", "2,1,1,9", "4,1,1,9"].every((m) => D.merges.includes(m)), true);
  check("§11 タブの色は要対応があれば赤", D.tabColor, UI.dangerFg);
  check("§11★ 通知メールの判定は並べ替えに影響されない（同じ 3 人）", /P010: 途絶/.test(env.mails[0].body) && /P011: 欠番/.test(env.mails[0].body) && /P012: 未受領/.test(env.mails[0].body), true);

  // 再実行: P010 が復帰 → 前回の赤が残らない（clear で書式も消す）
  files.push(makeFile("n2", goodName("P010", 2, stamp(28)), 10, ago(0.1)));
  call(env, "o1LedgerRun");
  const row010 = dashData(ss).findIndex((r) => r[0] === "P010");
  check("§11★ 復帰した行に前回の赤が残らない", [dashData(ss)[row010][1], D.styleAt(H + 1 + row010, 2).bg || null], ["正常", null]);
  check("§11 結合が重ならない（再実行しても表題帯の結合は 1 つ）", D.merges.filter((m) => m === "1,1,1,9").length, 1);

  // 受領台帳: 値に触れず、見出し・固定・条件付き書式
  const L = ss.sheets[LEDGER];
  check("§11 受領台帳: 2 行を固定・見出しは紺帯", [L.frozen, L.styleAt(2, 1).bg], [2, UI.navy]);
  check("§11★ 受領台帳: 条件付き書式は列だけで開いた範囲（追記した行にも効く）", plain(L.rules).map((r) => r.ranges[0]), ["A3:J", "A3:J", "A3:J"]);
  check("§11 受領台帳: 削除済は灰・対象外は橙・dup は黄（列は形式=J・重複=I）", plain(L.rules).map((r) => [r.formula, r.bg]), [
    ['=$J3="削除済"', UI.grayBg], ['=$J3="対象外"', UI.gapBg], ['=$I3="dup"', UI.warnBg],
  ]);
  L.widths[2] = 999; // 研究者が列幅を変えた
  call(env, "o1LedgerRun");
  check("§11★ 受領台帳: 2 回目以降は書式を付け直さない（研究者の列幅を戻さない）", L.widths[2], 999);
}
{
  // ★ 同じ位置の行が「途絶 → 正常」になる: 前回の赤が残らない（⚠️ clearContents だと書式が残る）
  const ss = makeSpreadsheet(["O1 登録ログ"]);
  regTab(ss, []);
  const files = [makeFile("q1", goodName("P050", 1, stamp(20)), 10, ago(8))];
  const env = makeEnv({ spreadsheet: ss, files });
  call(env, "o1LedgerRun");
  const D = ss.sheets[DASH];
  const was = D.styleAt(DASH_HEAD_ROW + 1, 2).bg;
  files.push(makeFile("q2", goodName("P050", 2, stamp(28)), 10, ago(0.1)));
  call(env, "o1LedgerRun");
  check("§11★ 途絶 → 正常になった同じ位置の行に赤が残らない", [was, dashData(ss)[0][1], D.styleAt(DASH_HEAD_ROW + 1, 2).bg || null], [
    plain(E.ctx.O1_UI).dangerBg, "正常", null,
  ]);
}
{
  // 空: 見出しの下に案内の 1 行・件数の行は緑地
  const ss = makeSpreadsheet(["O1 登録ログ"]);
  regTab(ss, []);
  const env = makeEnv({ spreadsheet: ss, files: [] });
  call(env, "o1LedgerRun");
  const D = ss.sheets[DASH];
  const UI = plain(E.ctx.O1_UI);
  check("§11 空: 見出しの下に「まだ無い」の 1 行", D.rows[DASH_HEAD_ROW][0], DASH_EMPTY);
  check("§11 空: 件数の行は緑地・タブは緑", [D.styleAt(2, 1).bg, D.tabColor], [UI.okBg, UI.okFg]);
  // 空 → データが入る: 案内行の結合が残らない（fake の clear は結合を消さない側に倒す）
  const keep = D.clear;
  D.clear = () => {
    const m = D.merges.slice();
    keep();
    D.merges = m; // ★ 実物で clear が結合を解かない場合を再現する
  };
  env.files.push(makeFile("e1", goodName("P001", 1, stamp(27)), 10, ago(0.1)));
  call(env, "o1LedgerRun");
  check("§11★ 空 → データ: 案内行の結合が残らない（clear が結合を解かなくても）", D.merges.includes(DASH_HEAD_ROW + 1 + ",1,1,9"), false);
}
{
  // ⚠️ 見た目の処理が例外でも、値は書かれ・通知は届く（code-reviewer MEDIUM・2026-09-28）
  const ss = makeSpreadsheet(["O1 登録ログ"]);
  regTab(ss, []);
  const D = ss.insertSheet(DASH);
  const orig = D.getRange;
  D.getRange = (...a) => {
    const r = orig(...a);
    if (typeof a[0] !== "string") r.merge = () => { throw new Error("手で結合されたセルと重なる"); };
    return r;
  };
  const env = makeEnv({ spreadsheet: ss, files: [makeFile("m1", goodName("P060", 1, stamp(20)), 10, ago(8))] });
  let threw = null;
  try { call(env, "o1LedgerRun"); } catch (e) { threw = String(e); }
  check("§11★ 途絶タブの書式が例外でも実行は落ちず、値は書かれ、途絶の通知が届く", [threw, dashData(ss)[0].slice(0, 2), env.mails.length, env.logs.some((l) => /見た目を整えられませんでした/.test(l))], [
    null, ["P060", "途絶"], 1, true,
  ]);
}
{
  // ⚠️ 受領台帳の書式が例外でも、走査と通知は続く
  const ss = makeSpreadsheet(["O1 登録ログ"]);
  regTab(ss, []);
  const L = ss.insertSheet(LEDGER);
  L.appendRow(["banner"]);
  L.appendRow(plain(E.ctx.O1_LEDGER_HEAD));
  L.setConditionalFormatRules = () => { throw new Error("rules quota"); };
  const env = makeEnv({ spreadsheet: ss, files: [makeFile("m2", goodName("P061", 1, stamp(20)), 10, ago(8))] });
  let threw = null;
  try { call(env, "o1LedgerRun"); } catch (e) { threw = String(e); }
  check("§11★ 受領台帳の書式が例外でも走査は続き、途絶の通知が届く", [threw, L.rows.length - 2, env.mails.length], [null, 1, 1]);
}
{
  // ★ 受領台帳の既存行の値は書式付けで変わらない（追記のみの約束）
  const ss = makeSpreadsheet(["O1 登録ログ"]);
  regTab(ss, []);
  const env = makeEnv({ spreadsheet: ss, files: [makeFile("x1", goodName("P001", 1, stamp(27)), 10, ago(1))] });
  call(env, "o1LedgerRun");
  const before = JSON.stringify(ss.sheets[LEDGER].rows);
  ss.sheets[LEDGER].frozen = 0; // 固定が外された → 次回に書式を付け直す
  call(env, "o1LedgerRun");
  check("§11★ 書式を付け直しても受領台帳の値は 1 つも変わらない", JSON.stringify(ss.sheets[LEDGER].rows), before);
  check("§11 固定が外れていれば付け直す", ss.sheets[LEDGER].frozen, 2);
}

// ---------------------------------------------------------------------------
// §12 O1 終了判定（2026-10-07・`.steering/20261007-o1-end-judgement/`）
//   ★ 起算日 = 最初に記録した日・その日を 1 日目として 21 日目が過ぎたら終了
// ---------------------------------------------------------------------------
const END = "O1 終了判定";
const END_HEAD_ROW = 3;
const endData = (ss) => ss.sheets[END].rows.slice(END_HEAD_ROW).filter((r) => r && r[0] && !/まだ登録も受領も/.test(r[0]));
const endRowOf = (ss, pid) => endData(ss).find((r) => r[0] === pid);
const key = (s) => call(E, "o1LedgerDayKey_", s);
const TODAY = key("2026-09-30"); // NOW と同じ日
/** ★ 受領日の既定 = 名前の日付の翌日の正午（48 時間の猶予に近い形）。`recvYmd` で変えられる。 */
const ymdMs = (ymd, h) => {
  const [y, m, d] = ymd.split("-").map(Number);
  return new Date(y, m - 1, d, h === undefined ? 12 : h, 0, 0).getTime();
};
const EF = (pid, ymd, recvYmd) => ({ pid, start: ymd + " 10:11:12", receivedMs: recvYmd ? ymdMs(recvYmd) : ymdMs(ymd) + DAY });
/** ★ 既定では全員を 2026-08-01 に登録済みにする（⚠️ 登録の無い P-ID は判定しない規則のため）。 */
const regAll = (files) => {
  const r = {};
  files.forEach((f) => (r[f.pid] = ymdMs("2026-08-01", 9)));
  return r;
};
const endJudge = (files, reg, today) =>
  plain(call(E, "o1LedgerEndJudge_", files, reg === undefined ? regAll(files) : reg, today === undefined ? TODAY : today));
{
  check("§12 日付の通し番号: 1 日違いは 1", key("2026-09-21") - key("2026-09-20"), 1);
  check("§12 月をまたいでも暦日で数える", key("2026-10-01") - key("2026-09-30"), 1);
  check("§12★ ありえない日付（2026-02-31）は読まない", key("2026-02-31"), null);
  check("§12 形の違う文字列は読まない", key("20260920"), null);
  check("§12 番号 → 文字列が元に戻る", call(E, "o1LedgerKeyToStr_", key("2026-09-05")), "2026-09-05");

  // 境界: 起算日 09-10 → 21 日目 = 09-30
  const f = [EF("P001", "2026-09-10"), EF("P001", "2026-09-29")];
  const d20 = endJudge(f, undefined, key("2026-09-29"))[0];
  const d21 = endJudge(f, undefined, key("2026-09-30"))[0];
  const d22 = endJudge(f, undefined, key("2026-10-01"))[0];
  check("§12★ 20 日目は期間中", [d20.status, d20.dayNo], ["期間中", 20]);
  check("§12★ 21 日目（当日）はまだ期間中", [d21.status, d21.dayNo], ["期間中", 21]);
  check("§12★ 22 日目に入ったら終了（連絡待ち）", [d22.status, d22.dayNo], ["終了（連絡待ち）", 22]);
  check("§12 21 日目の日付", call(E, "o1LedgerKeyToStr_", d22.endKey), "2026-09-30");

  // 片づけの案内
  const arrived = endJudge([EF("P002", "2026-09-01"), EF("P002", "2026-09-21")], undefined, key("2026-09-22"))[0];
  check("§12★ 21 日目以降の記録が届いていれば片づけ可", arrived.settle, "可（21 日目以降の記録が届いた）");
  const waiting = endJudge([EF("P003", "2026-09-01"), EF("P003", "2026-09-15")], undefined, key("2026-09-23"))[0];
  check("§12★ 21 日目の記録が無く、終了から 3 日たっていなければ待つ", waiting.settle, "待つ（最後の記録が届く途中かもしれない）");
  const elapsed = endJudge([EF("P003", "2026-09-01"), EF("P003", "2026-09-15")], undefined, key("2026-09-25"))[0];
  check("§12★ 終了から 3 日たてば片づけ可", elapsed.settle, "可（終了から 3 日たった）");
  check("§12 期間中は片づけの案内を出さない", d21.settle, "");

  // 届いた日の数: 同じ日は 1・期間の後は数えない
  const many = endJudge([EF("P004", "2026-09-01"), EF("P004", "2026-09-01"), EF("P004", "2026-09-05"), EF("P004", "2026-09-21"), EF("P004", "2026-09-25")], undefined, TODAY)[0];
  check("§12★ 届いた日の数は期間内の日付の種類（同じ日は 1・22 日目以降は数えない）", many.daysIn, 3);
  check("§12 最後の記録の日は期間の後も含む", call(E, "o1LedgerKeyToStr_", many.lastKey), "2026-09-25");

  // 登録日より前の日付は使わない（端末の時計が狂っていても即終了にしない）
  const reg = { P005: new Date(2026, 8, 20, 9, 0, 0).getTime() };
  const clock = endJudge([EF("P005", "2025-01-01"), EF("P005", "2026-09-21")], reg, TODAY)[0];
  check("§12★ 登録日より前の日付は起算日にしない（除外数を出す）", [call(E, "o1LedgerKeyToStr_", clock.firstKey), clock.ignored, clock.status], ["2026-09-21", 1, "期間中"]);
  check("§12 登録だけで記録が無ければ記録待ち", endJudge([], { P006: ago(3) }, TODAY)[0].status, "記録待ち");
  check(
    "§12★ P-ID が Object.prototype の名前（constructor）でも壊れない",
    (() => {
      try {
        return endJudge([EF("constructor", "2026-09-20"), EF("toString", "2026-09-21")], undefined, TODAY).map((r) => [r.pid, r.status]);
      } catch (e) {
        return "threw: " + e;
      }
    })(),
    [["constructor", "期間中"], ["toString", "期間中"]]
  );

  // 研究者の記入で表示を進める
  const blank12 = Array(12).fill("");
  const withCol = (c, v) => blank12.map((x, i) => (i === c ? v : x));
  check("§12 終了連絡日があれば「終了（連絡済み）」", call(E, "o1LedgerEndShown_", "終了（連絡待ち）", withCol(8, "2026-10-01")), "終了（連絡済み）");
  check("§12 片づけ確認日があれば「完了」", call(E, "o1LedgerEndShown_", "終了（連絡待ち）", withCol(10, "2026-10-05")), "完了");
  check("§12 期間中は記入があっても期間中のまま", call(E, "o1LedgerEndShown_", "期間中", withCol(8, "x")), "期間中");

  // 通知の要否
  const rowsE = [{ pid: "P001", status: "終了（連絡待ち）" }, { pid: "P002", status: "期間中" }];
  const a1 = plain(call(E, "o1LedgerEndAlerts_", null, rowsE));
  check("§12★ 新しく終了になった人だけを知らせる", [a1.added.map((r) => r.pid), a1.next], [["P001"], ["P001"]]);
  const a2 = plain(call(E, "o1LedgerEndAlerts_", ["P001"], rowsE));
  check("§12★ 終了が続いても再び知らせない", a2.added.length, 0);
  const a3 = plain(call(E, "o1LedgerEndAlerts_", ["P001", "P009"], rowsE));
  check("§12 消えた P-ID（削除）は状態から落ちる", a3.next, ["P001"]);
}
{
  // 統合: 21 日目が過ぎた人がタブに出て、研究者宛てに 1 回だけ知らせる
  const ss = makeSpreadsheet(["O1 登録ログ"]);
  regTab(ss, [["2026-09-01 09:00:00", "register", "P011", "ok", "new-pid", ""], ["2026-09-19 09:00:00", "register", "P012", "ok", "new-pid", ""]]);
  const files = [
    makeFile("e1", goodName("P011", 1, stamp(5)), 100, ago(23)),
    makeFile("e2", goodName("P011", 2, stamp(26)), 100, ago(2)),
    makeFile("e3", goodName("P012", 1, stamp(20)), 100, ago(8)),
    makeFile("e4", goodName("P012", 2, stamp(28)), 100, ago(1)),
  ];
  const env = makeEnv({ spreadsheet: ss, files });
  call(env, "o1LedgerRun");
  check("§12★ 「O1 終了判定」タブができ、見出しが 12 列", ss.sheets[END] && ss.sheets[END].rows[END_HEAD_ROW - 1].length, 12);
  check("§12★ 起算 09-05 の人は終了（連絡待ち）・09-20 の人は期間中", [endRowOf(ss, "P011")[1], endRowOf(ss, "P012")[1]], ["終了（連絡待ち）", "期間中"]);
  check("§12 終了の人が上に並ぶ", endData(ss).map((r) => r[0]), ["P011", "P012"]);
  check("§12 起算日・21 日目・片づけの案内", endRowOf(ss, "P011").slice(2, 8), ["2026-09-05", "2026-09-25", "終了（26 日目）", "1", "2026-09-26", "可（21 日目以降の記録が届いた）"]);
  check("§12★ 期間終了をメールで知らせる（件名と本文）", [env.mails.length, /期間終了 1 人/.test(env.mails[0] && env.mails[0].subject), /P011: 終了（連絡待ち）/.test(env.mails[0] && env.mails[0].body)], [1, true, true]);
  check("§12 終了だけの回は見出しが終了の知らせ（要確認と読ませない）", /期間（21 日）が終わった人がいます/.test(env.mails[0].body), true);
  check("§12★ 期間中の人は知らせない", /P012/.test(env.mails[0].body), false);
  call(env, "o1LedgerRun");
  check("§12★ 終了が続いても 2 通目は送らない", env.mails.length, 1);

  // 研究者の記入は P-ID ごとに残り、判定の表示が進む
  const rIdx = ss.sheets[END].rows.findIndex((r) => r && r[0] === "P011");
  ss.sheets[END].rows[rIdx][8] = "2026-09-30";
  ss.sheets[END].rows[rIdx][11] = "電話で連絡";
  call(env, "o1LedgerRun");
  check("§12★ 終了連絡日を書くと「終了（連絡済み）」になり、記入は残る", [endRowOf(ss, "P011")[1], endRowOf(ss, "P011")[8], endRowOf(ss, "P011")[11]], ["終了（連絡済み）", "2026-09-30", "電話で連絡"]);
  const rIdx2 = ss.sheets[END].rows.findIndex((r) => r && r[0] === "P011");
  ss.sheets[END].rows[rIdx2][10] = "2026-10-02";
  ss.sheets[END].rows[rIdx2][11] = "=HYPERLINK(\"x\")";
  call(env, "o1LedgerRun");
  check("§12 片づけ確認日を書くと「完了」", endRowOf(ss, "P011")[1], "完了");
  check("§12★ 記入欄の数式は文字列に倒す", String(endRowOf(ss, "P011")[11]).startsWith("⚠="), true);
  check("§12★ タブ全体をテキスト形式で書く（記入した日付が日付に化けない）", ss.sheets[END].formats["4,9"], "@");
  check("§12 タブにメールアドレスの形が無い", /[^\s@"]+@[^\s@"]+\.[^\s@"]+/.test(JSON.stringify(ss.sheets[END].rows)), false);
}
{
  // 削除で台帳から消えた P-ID の行（研究者の記入ごと）は残らない
  const ss = makeSpreadsheet(["O1 登録ログ"]);
  regTab(ss, [["2026-09-15 09:00:00", "register", "P013", "ok", "new-pid", ""]]);
  const files = [makeFile("k1", goodName("P013", 1, stamp(20)), 100, ago(8))];
  const env = makeEnv({ spreadsheet: ss, files });
  call(env, "o1LedgerRun");
  const i = ss.sheets[END].rows.findIndex((r) => r && r[0] === "P013");
  ss.sheets[END].rows[i][11] = "メモ";
  // 削除の求め（A-14）: 台帳の行を tombstone にする
  const L = ss.sheets[LEDGER].rows;
  const li = L.findIndex((r) => r && r[0] === "k1");
  L[li][2] = "";
  L[li][3] = "";
  L[li][4] = "";
  L[li][1] = "";
  L[li][9] = "削除済";
  // 削除の求め（A-13）: 登録ログの P-ID も空にする
  const R = ss.sheets["O1 登録ログ"].rows;
  const ri = R.findIndex((r) => r && r[2] === "P013");
  R[ri][2] = "";
  call(env, "o1LedgerRun");
  check("§12★ 削除された P-ID の行は記入ごと残らない", endRowOf(ss, "P013"), undefined);
}
{
  // 走査が打ち切られた回は、終了の通知を保留する（状態も保存しない）
  const ss = makeSpreadsheet(["O1 登録ログ"]);
  regTab(ss, [["2026-09-01 09:00:00", "register", "P014", "ok", "new-pid", ""]]);
  const files = [];
  for (let i = 1; i <= 6; i++) files.push(makeFile("t" + i, goodName("P014", i, stamp(i)), 100, ago(20)));
  const startNow = NOW;
  const env = makeEnv({ spreadsheet: ss, files, tickPerFile: 100000 });
  call(env, "o1LedgerRun");
  check("§12★ 打ち切りの回は期間終了を知らせない・状態を保存しない", [env.mails.some((m) => /期間終了/.test(m.subject)), "O1_LEDGER_ENDED" in env.props], [false, false]);
  NOW = startNow;
}
{
  // 終了判定のタブが書けなくても、途絶の通知は止まらない
  const ss = makeSpreadsheet(["O1 登録ログ"]);
  regTab(ss, []);
  const orig = ss.insertSheet.bind(ss);
  ss.insertSheet = (n) => {
    if (n === END) throw new Error("stub: cannot insert");
    return orig(n);
  };
  const env = makeEnv({ spreadsheet: ss, files: [makeFile("s1", goodName("P015", 1, stamp(10)), 100, ago(8))] });
  const r = (() => {
    try {
      call(env, "o1LedgerRun");
      return "ok";
    } catch (e) {
      return String(e);
    }
  })();
  check("§12★ 終了判定のタブが書けなくても実行は止まらず、途絶は通知される", [r, env.mails.length, /途絶/.test(env.mails[0] && env.mails[0].body)], ["ok", 1, true]);
  check("§12 書けなかったことをログに肯定形で残す", env.logs.some((l) => /更新できていません/.test(l)), true);
}

{
  // ★ 2026-10-08 レビュー指摘（3 系統一致）: 名前の日付を受領日で挟む・登録の無い P-ID は判定しない
  const fut = endJudge([EF("P021", "2026-09-01"), EF("P021", "2026-12-01", "2026-09-10")], undefined, key("2026-09-22"))[0];
  check("§12★ 受領日より後（未来）の日付は使わない（片づけ可を早めない）", [fut.settle, fut.ignored, call(E, "o1LedgerKeyToStr_", fut.lastKey)], ["待つ（最後の記録が届く途中かもしれない）", 1, "2026-09-01"]);
  const old = endJudge([EF("P022", "2026-08-02", "2026-09-25"), EF("P022", "2026-09-24", "2026-09-25")], undefined, TODAY)[0];
  check("§12★ 受領日より 14 日以上前の日付は使わない（起算日を過去へ飛ばさない・遅れの数を別に出す）", [call(E, "o1LedgerKeyToStr_", old.firstKey), old.ignored, old.late, old.status], ["2026-09-24", 0, 1, "期間中"]);
  const lag = endJudge([EF("P023", "2026-09-11", "2026-09-25")], undefined, TODAY)[0];
  check("§12 受領日の 14 日前ちょうどまでは使う（後送りを見込む）", call(E, "o1LedgerKeyToStr_", lag.firstKey), "2026-09-11");
  const unreg = endJudge([EF("P024", "2026-09-01")], {}, TODAY)[0];
  check("§12★★ 登録ログに無い P-ID は判定しない", [unreg.status, unreg.firstKey], ["判定できない（登録が見つからない）", null]);
  check("§12★ 登録の無い P-ID は通知しない", plain(call(E, "o1LedgerEndAlerts_", null, [unreg])).added.length, 0);
  check("§12 2000 年より前の年は読まない", key("0099-01-01"), null);
}
{
  // 統合: 見出しが違えば書かない（研究者の記入をずらさない）・書き込みの失敗で記入を消さない・日付の貼り付け・メールに日付を載せない
  const ss = makeSpreadsheet(["O1 登録ログ"]);
  regTab(ss, [["2026-09-01 09:00:00", "register", "P031", "ok", "new-pid", ""]]);
  const files = [makeFile("h1", goodName("P031", 1, stamp(5)), 100, ago(23)), makeFile("h2", goodName("P031", 2, stamp(26)), 100, ago(2))];
  const env = makeEnv({ spreadsheet: ss, files });
  call(env, "o1LedgerRun");
  check("§12★ メールの本文に日付（YYYY-MM-DD）を載せない", /\d{4}-\d{2}-\d{2}/.test(env.mails[0] && env.mails[0].body), false);
  check("§12 メールの本文は日数で書く", /21 日目が過ぎました（今日 26 日目）/.test(env.mails[0] && env.mails[0].body), true);
  check("§12 終了だけの回は途絶の注意を付けない", /「途絶」「未受領」は「やめた」ではありません/.test(env.mails[0].body), false);
  const T = ss.sheets[END];
  const ri = T.rows.findIndex((r) => r && r[0] === "P031");
  T.rows[ri][8] = new env.ctx.Date(2026, 9, 1); // ★ スクリプト側の Date（実物では同じ realm）
  call(env, "o1LedgerRun");
  check("§12★ 貼られた日付（Date）は長い英語の文字列にしない", /GMT|Thu|Oct/.test(String(endRowOf(ss, "P031")[8])), false);
  // 書き込みの失敗: 記入が消えない
  const ri2 = T.rows.findIndex((r) => r && r[0] === "P031");
  T.rows[ri2][11] = "残すメモ";
  const origGet = T.getRange.bind(T);
  T.getRange = (r, c, nr, nc) => {
    const rg = origGet(r, c, nr, nc);
    if (r === 1 && nr > 3) rg.setValues = () => { throw new Error("stub: write failed"); };
    return rg;
  };
  call(env, "o1LedgerRun");
  check("§12★★ 書き込みが失敗しても研究者の記入は消えない（clear しない）", JSON.stringify(T.rows).includes("残すメモ"), true);
  check("§12 書き込みの失敗をログに肯定形で残す", env.logs.some((l) => /更新できていません/.test(l)), true);
  T.getRange = origGet;
  // 見出しが違えば書かない
  T.rows[END_HEAD_ROW - 1].splice(1, 0, "挿入した列");
  const snap = JSON.stringify(T.rows);
  call(env, "o1LedgerRun");
  check("§12★★ 見出しが違えば書かない（記入をずらさない）", JSON.stringify(T.rows), snap);
  check("§12 見出しが違うことをログに出す", env.logs.some((l) => /見出しの .* 列目が想定と違います/.test(l)), true);
}
{
  // Codex 再レビュー（2026-10-08）: 重複行の記入を捨てない・全部除外でも件数を出す・遅れて届いた分を知らせる
  const ss = makeSpreadsheet(["O1 登録ログ"]);
  regTab(ss, [["2026-09-01 09:00:00", "register", "P051", "ok", "new-pid", ""], ["2026-09-01 09:00:00", "register", "P052", "ok", "new-pid", ""], ["2026-09-01 09:00:00", "register", "P053", "ok", "new-pid", ""]]);
  const files = [
    makeFile("d1", goodName("P051", 1, stamp(20)), 100, ago(9)),
    // P052: 全部が登録日より前（2026-08-xx）→ 有効な日付なし
    makeFile("d2", "P052_o1day01_gse_o1_20260810_101112.age", 100, ago(9)),
    // P053: 初日の記録が 20 日遅れて届いた
    makeFile("d3", goodName("P053", 1, stamp(2)), 100, ago(8)),
    makeFile("d4", goodName("P053", 2, stamp(21)), 100, ago(8)),
  ];
  const env = makeEnv({ spreadsheet: ss, files });
  call(env, "o1LedgerRun");
  const T = ss.sheets[END];
  const i1 = T.rows.findIndex((r) => r && r[0] === "P051");
  T.rows[i1][11] = "";
  const dup = T.rows[i1].slice();
  dup[8] = "2026-10-01";
  dup[11] = "下の行だけのメモ";
  T.rows.splice(i1 + 1, 0, dup);
  call(env, "o1LedgerRun");
  check("§12★★ 同じ P-ID の行が重複しても、下の行だけの記入を捨てない", [endRowOf(ss, "P051")[8], endRowOf(ss, "P051")[11], endData(ss).filter((r) => r[0] === "P051").length], ["2026-10-01", "下の行だけのメモ", 1]);
  check("§12★ 全部が範囲外でも除外の件数を出す（記録待ちと区別できる）", [endRowOf(ss, "P052")[1], /範囲外の日付 1 件を除外/.test(endRowOf(ss, "P052")[5])], ["記録待ち", true]);
  check("§12★ 14 日より遅れて届いた日付を除外したら、起算日を確かめるよう出す", /14 日より遅れて届いた日付 1 件を除外・起算日を確かめる/.test(endRowOf(ss, "P053")[5]), true);
}
{
  // 重複行で両方に違う記入 → 両方残す
  const ss = makeSpreadsheet(["O1 登録ログ"]);
  regTab(ss, [["2026-09-01 09:00:00", "register", "P061", "ok", "new-pid", ""]]);
  const env = makeEnv({ spreadsheet: ss, files: [makeFile("q1", goodName("P061", 1, stamp(20)), 100, ago(9))] });
  call(env, "o1LedgerRun");
  const T = ss.sheets[END];
  const i = T.rows.findIndex((r) => r && r[0] === "P061");
  T.rows[i][11] = "上";
  const dup = T.rows[i].slice();
  dup[11] = "下";
  T.rows.splice(i + 1, 0, dup);
  call(env, "o1LedgerRun");
  check("§12★ 重複行の記入が食い違えば、両方を「／」でつないで残す", endRowOf(ss, "P061")[11], "上 ／ 下");
}
{
  // タイムゾーンが日本でなければ表題に出す
  const ss = makeSpreadsheet(["O1 登録ログ"]);
  regTab(ss, [["2026-09-20 09:00:00", "register", "P041", "ok", "new-pid", ""]]);
  const env = makeEnv({ spreadsheet: ss, files: [makeFile("z1", goodName("P041", 1, stamp(21)), 100, ago(1))] });
  env.ctx.Session = { getScriptTimeZone: () => "America/New_York" };
  call(env, "o1LedgerRun");
  check("§12 タイムゾーンが Asia/Tokyo でなければ表題に警告", /タイムゾーンが America\/New_York/.test(ss.sheets[END].rows[0][0]), true);
}

// ---------------------------------------------------------------------------
// §7 ソースの性質（★ 歯止め）
// ---------------------------------------------------------------------------
{
  const code = src.replace(/\/\*[\s\S]*?\*\//g, "").replace(/^\s*\/\/.*$/gm, "");
  check("§7★ GmailApp を使わない（受信箱の権限を求めない）", /\bGmailApp\b/.test(code), false);
  check("§7★ MailApp の呼び出しは sendEmail だけ", [...code.matchAll(/MailApp\.(\w+)/g)].map((m) => m[1]).filter((v, i, a) => a.indexOf(v) === i), ["sendEmail"]);
  check("§7★ Drive は読むだけ（作成・削除・共有の呼び出しが無い）", /\.(createFile|createFolder|setTrashed|setSharing|addEditor|addViewer|moveTo|makeCopy|setContent|removeFile)\(/.test(code), false);
  check("§7★ 宛先・ID を直書きしていない（メールアドレス・25 文字以上の英数字列・URL）", /@[A-Za-z0-9-]+\.[A-Za-z]{2,}|['"][A-Za-z0-9_-]{25,}['"]|https?:\/\//.test(code), false);
  check("§7 見出し（O1_LEDGER_HEAD）と列の位置（O1_LEDGER_COL）が同じ長さ", (() => {
    const c = E.ctx;
    return [plain(c.O1_LEDGER_HEAD).length, Object.keys(plain(c.O1_LEDGER_COL)).length];
  })(), [10, 10]);
  check("§7 見出しに氏名・メール・URL の列が無い", plain(E.ctx.O1_LEDGER_HEAD).some((h) => /氏名|名前$|メール|mail|URL/i.test(h) && h !== "ファイル名"), false);
  check("§7 判定の日数は前段の裁定どおり（途絶 5・未受領 7・欠番 5）", [E.ctx.O1_LEDGER_STALE_DAYS, E.ctx.O1_LEDGER_NEVER_DAYS, E.ctx.O1_LEDGER_GAP_DAYS], [5, 7, 5]);
  check("§7 登録ログのタブ名はビルダーの O1_MGMT_TAB と同じ", (() => {
    const b = fs.readFileSync(BUILDER_PATH, "utf8");
    const m = /var O1_MGMT_TAB = "([^"]+)"/.exec(b);
    return m ? m[1] : null;
  })(), E.ctx.O1_LEDGER_REG_TAB);
  check("§7 受け口のソースに台帳の語が無い（受け口は台帳の関数・状態に依存しない）", /O1_LEDGER|o1Ledger/.test(submitSrc), false);
}

// ---------------------------------------------------------------------------
// 出力（★ 末尾 1 行の書式は既存の guard test と同一）
// ---------------------------------------------------------------------------
let ng = 0;
cases.forEach((c) => {
  if (!c.ok) ng++;
  console.log(`${c.ok ? "OK  " : "NG  "} ${c.name} → ${JSON.stringify(c.got)}`);
});

// ⚠️ ★ 「NG が 0 件なら緑」だけだと、ケースを 0 件にしても緑になる。★ 下限を置く。
if (cases.length < 100) {
  console.log(`\n${cases.length} 件しかケースが無い（100 未満）。テストが削られていないか確認すること。`);
  process.exit(1);
}
console.log(ng === 0 ? `\n全 ${cases.length} ケース期待どおり` : `\n${ng} 件が期待と違う（全 ${cases.length} ケース）`);
process.exit(ng === 0 ? 0 : 1);
