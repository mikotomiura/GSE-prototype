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
    getRange(r, c, nr, nc) {
      if (r < 1 || c < 1 || nr < 1 || nc < 1) throw new Error("range 引数が不正");
      if (r + nr - 1 > s.maxRows) throw new Error("The coordinates of the range are outside the dimensions of the sheet.");
      return {
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
      openById(id) {
        opened++;
        if (id !== "SHEET") throw new Error("no such spreadsheet " + id);
        return ss;
      },
    },
    DriveApp: {
      getFolderById(id) {
        if (id !== "FOLDER") throw new Error("no such folder");
        return {
          getName: () => "STUB-FOLDER",
          getFiles() {
            let i = 0;
            return {
              hasNext: () => i < files.length,
              next: () => {
                if (opt.tickPerFile) NOW += opt.tickPerFile;
                return files[i++];
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
  check("§6 途絶タブに P001 が正常で載る", ss.sheets[DASH].rows[2].slice(0, 2), ["P001", "正常"]);
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
  check("§6 復帰後は途絶タブが正常に戻る", ss.sheets[DASH].rows[2][1], "正常");
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
  const dash = ss.sheets[DASH].rows.slice(2).map((r) => [r[0], r[1]]);
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
  check("§6 対象外の名前がある旨を途絶タブのバナーに出す", /対象外の名前 2 件/.test(ss.sheets[DASH].rows[0][0]), true);
  check("§6★ 対象外の名前で通知する（P-ID とは別枠）", env.mails.length === 1 && /O1 の形でないファイルが 2 件/.test(env.mails[0].body), true);
  check("§6 対象外のファイルは P-ID の集計に混ざらない", ss.sheets[DASH].rows.slice(2).map((r) => r[0]), ["P005"]);
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
  check("§6 打ち切ったことを途絶タブのバナーに出す", /打ち切り/.test(ss.sheets[DASH].rows[0][0]), true);
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
  check("§8★ 通し: 日番号 0 だけ届いている人は未受領にならず、不読行にもならない", [env.mails.length, /読めない行/.test(ss.sheets[DASH].rows[0][0]), ss.sheets[DASH].rows[2][1]], [0, false, "正常"]);
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
  check("§8 バナーにも件数が出る", /読めない行 1/.test(ss.sheets[DASH].rows[0][0]) && /日時が読めない行 1/.test(ss.sheets[DASH].rows[0][0]), true);
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
  check("§8★ 削除済みの行は不読行に数えず、通知もしない", [env.mails.length, /読めない行/.test(ss.sheets[DASH].rows[0][0])], [0, false]);
  check("§8★ 削除済みの Drive ファイル ID は残り、同じファイルが別の行として復活しない", led.getLastRow(), 3);
  check("§8 削除済みは P-ID の集計に出ない", ss.sheets[DASH].rows.slice(2).length, 0);
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
  const env3 = makeEnv({ spreadsheet: ss, lockOk: false });
  call(env3, "o1LedgerRun");
  check("§8 ロックが取れなかった回は「失敗」として通知しない", env3.mails.length, 0);
}

// 8-10 登録ログの列が足りなければ、範囲外の例外でなく理由を言って止まる
{
  const ss = makeSpreadsheet(["O1 登録ログ"]);
  ss.sheets["O1 登録ログ"].appendRow(["b", "", "", "", ""]);
  ss.sheets["O1 登録ログ"].appendRow(["記録日時", "種別", "P-ID", "結果", "理由"]); // 5 列
  const env = makeEnv({ spreadsheet: ss, props: { O1_LEDGER_NOTIFY_EMAIL: null } });
  let msg = "";
  try {
    call(env, "o1LedgerRun");
  } catch (e) {
    msg = String(e.message);
  }
  check("§8 登録ログが 6 列未満なら理由を言って止まる", /6 列に足りません/.test(msg), true);
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
  check("§8 o1LedgerCheck はタイムゾーンを出す", /タイムゾーン: Asia\/Tokyo/.test(log), true);
  check("§8 o1LedgerCheck は実行ログに P-ID が残りうる注意を出す", /A-10/.test(log), true);
  NOW = startNow;
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
  check("§7 受け口のソースに台帳の語が無い（doPost を触っていない）", /O1_LEDGER|o1Ledger/.test(submitSrc), false);
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
