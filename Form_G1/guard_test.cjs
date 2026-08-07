// assertSafeToRebuild_ の赤/緑をローカルで実測する。
// ★ 実フォームには一切触らない（FormApp をスタブする）。
const fs = require("fs");
const vm = require("vm");

const src = fs.readFileSync(
  process.argv[2] || require("path").join(__dirname, "GSE_G1_Form_Builder.gs"),
  "utf8"
);

function makeCtx() {
  const logs = [];
  const ctx = {
    Logger: { log: (m) => logs.push(String(m)) },
    console,
    FormApp: {
      ItemType: { CHECKBOX: "CHECKBOX", MULTIPLE_CHOICE: "MC", LIST: "LIST", PAGE_BREAK: "PB" },
      PageNavigationType: { CONTINUE: "CONTINUE" },
      createTextValidation: () => ({ requireTextMatchesPattern: () => ({ build: () => ({}) }) }),
      openById: () => ({}),
    },
    PropertiesService: { getScriptProperties: () => ({ getProperty: () => null, setProperty: () => {} }) },
    SpreadsheetApp: {},
    DriveApp: {},
    MailApp: {},
    GmailApp: {},
    Session: {},
    ScriptApp: {},
    UrlFetchApp: {},
    Utilities: {},
    __logs: logs,
  };
  vm.createContext(ctx);
  vm.runInContext(src, ctx);
  return ctx;
}

const cases = [];
function check(name, fn) {
  try {
    fn();
    cases.push({ name, result: "GREEN (通した)" });
  } catch (e) {
    cases.push({ name, result: "RED (止めた)", msg: String(e.message).split("\n")[0] });
  }
}

// --- 1. 回答 0 件 → 通るべき（★ 陽性対照: ガードが何でも止めるわけではないこと） ---
{
  const ctx = makeCtx();
  check("回答 0 件", () =>
    ctx.assertSafeToRebuild_({ getResponses: () => [] }, "TEST-0件")
  );
}

// --- 2. 回答 3 件 → 止まるべき（★ 今回の事故と同じ状況） ---
{
  const ctx = makeCtx();
  check("回答 3 件 / 既定", () =>
    ctx.assertSafeToRebuild_({ getResponses: () => [1, 2, 3] }, "TEST-3件")
  );
}

// --- 3. 回答 3 件 + 明示フラグ → 通るべき（意図した作り直しは可能） ---
{
  const ctx = makeCtx();
  ctx.ALLOW_REBUILD_WITH_RESPONSES = true;
  check("回答 3 件 / ALLOW=true", () =>
    ctx.assertSafeToRebuild_({ getResponses: () => [1, 2, 3] }, "TEST-override")
  );
}

// --- 4. 回答数を取れない → 止まるべき（★ silent-failure 型の封じ込め） ---
{
  const ctx = makeCtx();
  check("getResponses が例外", () =>
    ctx.assertSafeToRebuild_(
      { getResponses: () => { throw new Error("API 失敗"); } },
      "TEST-例外"
    )
  );
}

const expected = ["GREEN (通した)", "RED (止めた)", "GREEN (通した)", "RED (止めた)"];
let ng = 0;
cases.forEach((c, i) => {
  const ok = c.result === expected[i];
  if (!ok) ng++;
  console.log(`${ok ? "OK  " : "NG  "} ${c.name} → ${c.result}${c.msg ? "  | " + c.msg : ""}`);
});
console.log(ng === 0 ? "\n全 4 ケース期待どおり" : `\n${ng} 件が期待と違う`);
process.exit(ng === 0 ? 0 : 1);
