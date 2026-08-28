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
    asMultipleChoiceItem: () => it,
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

/** スプレッドシート（参加者ロスター）のスタブ。★ 2 次元配列を素で持つ。 */
function makeSheet(rows) {
  const data = rows.map((r) => [r[0] || "", r[1] || "", r[2] || ""]);
  return {
    __rows: data,
    getLastRow: () => data.length,
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
            const src = data[r] || ["", "", ""];
            out.push(src.slice(col - 1, col - 1 + (numCols || 1)));
          }
          return out;
        },
      };
    },
    appendRow: (r) => {
      data.push([r[0] || "", r[1] || "", r[2] || ""]);
    },
  };
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
    Logger: { log: (m) => logs.push(String(m)) },
    console: { log: (m) => logs.push(String(m)) },
    FormApp: {
      ItemType: {
        MULTIPLE_CHOICE: "MULTIPLE_CHOICE",
        LIST: "LIST",
        PAGE_BREAK: "PAGE_BREAK",
        TEXT: "TEXT",
        CHECKBOX: "CHECKBOX",
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
      openById: (id) => {
        if (!ctx.__sheets[id]) throw new Error("stub: no such spreadsheet " + id);
        return {
          getUrl: () => "https://sheets.example/" + id,
          getSheetByName: (name) => ctx.__sheets[id][name] || null,
        };
      },
      flush: () => {},
    },
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

/** 設定が全部揃った文脈を作る（★ 陽性対照の土台）。 */
function makeReadyCtx(extra) {
  const o = extra || {};
  const forms = {
    [O1_C]: makeForm(O1_C, { responses: o.consentResponses || 0 }),
    [O1_S]: makeForm(O1_S, { responses: o.surveyResponses || 0 }),
  };
  const sheets = {
    [ROSTER_ID]: { 参加者ロスター: makeSheet(o.roster || [["P006", "既存", "old@example.com"]]) },
  };
  const ctx = makeCtx({ forms, sheets, lockFails: o.lockFails });
  // ⚠️★★ 設定は **スクリプト プロパティ**から読む (2026-08-29 に移した)。
  //   ★ ロスター ID も .gs の既定値ではなくなったので、ここで明示的に入れる。
  ctx.__props.FORM_ID_O1_CONSENT = O1_C;
  ctx.__props.FORM_ID_O1_SURVEY = O1_S;
  ctx.__props.O1_APP_DOWNLOAD_URL = "https://drive.example/o1";
  ctx.__props.PHASE1_MGMT_SHEET_ID = ROSTER_ID;
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
    const got = ctx.o1NextParticipantId_(makeSheet(rows));
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
  const ctx = makeReadyCtx({ roster: [["", "既存", "dup@example.com"]] });
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
    roster.__rows.length === 1 && /^P\d{3}$/.test(roster.__rows[0][0]),
    { rows: roster.__rows.length, pid: roster.__rows[0][0] }
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
  const ctx = makeReadyCtx({ roster: [["見出し", "既存", "broken@example.com"]] });
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
    "§6 ★ 宣言の 4 択が同意文書と同じ語で載っている",
    ["論述", "通信文", "デザイン・映像・制作作業", "vibe coding"].every((s) => desc.indexOf(s) >= 0),
    {}
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
  const hardcoded = /(SHARED_SECRET|FOLDER_ID|O1_APP_DOWNLOAD_URL|PHASE1_MGMT_SHEET_ID|FORM_ID_O1_CONSENT|FORM_ID_O1_SURVEY)\s*=\s*['"][^'"]+['"]/.test(src);
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

// --- 出力 ---------------------------------------------------------------------
// ⚠️★ 末尾 1 行の書式は `o1_submit_guard_test.cjs` と**同一にする**
//   （`run.sh` / `check-o1-release-readiness.sh` が `^全 <N> ケース期待どおり$` を読む）。
let ng = 0;
cases.forEach((c) => {
  if (!c.ok) ng++;
  console.log(`${c.ok ? "OK  " : "NG  "} ${c.name} → ${JSON.stringify(c.got)}`);
});

// ⚠️ ★ 「NG が 0 件なら緑」だけだと、**ケースを 0 件にしても緑になる**。★ 下限を置く。
// ⚠️★ 下限は**実数に近づける**（code-reviewer 指摘・2026-08-28）。
//   ★ 45 のままだと実数 89 に対して**半分近く削っても緑**で、「削られていないか」を測れていない。
// ⚠️★ 実数に近づけて保つ（★ 2026-08-29: 98 件なので下限 95）。
//   ⚠️ 離れたままだと「テストが 13 件消えても気づかない」状態になる。
if (cases.length < 95) {
  console.log(
    `\n${cases.length} 件しかケースが無い（95 未満）。テストが削られていないか確認すること。`
  );
  process.exit(1);
}

console.log(
  ng === 0
    ? `\n全 ${cases.length} ケース期待どおり`
    : `\n${ng} 件が期待と違う（全 ${cases.length} ケース）`
);
process.exit(ng === 0 ? 0 : 1);
