// GSE_G1_Submit.gs の受け口ガードをローカルで実測する。
// ★ 実 Drive にも実エンドポイントにも一切触らない（DriveApp / Utilities をスタブする）。
//
// ⚠️ ★ ここで測るのは「ガードを書いた」ではなく **「ガードが止める」** である。
//   陽性対照（正当な提出は通る）を必ず含めること。含めないと、全部拒否する実装でも緑になる。
const fs = require("fs");
const vm = require("vm");
const path = require("path");

const src = fs.readFileSync(
  process.argv[2] || path.join(__dirname, "GSE_G1_Submit.gs"),
  "utf8"
);

/** Drive の代わり。作られたファイルを配列に貯める（★ 消す操作は持たせない）。 */
function makeFolder(preexisting) {
  const files = (preexisting || []).map((f) => ({ ...f }));
  return {
    files,
    getName: () => "STUB",
    getFilesByName(name) {
      const hits = files.filter((f) => f.name === name);
      let i = 0;
      return {
        hasNext: () => i < hits.length,
        next: () => {
          const f = hits[i++];
          return { getSize: () => f.size, getName: () => f.name };
        },
      };
    },
    createFile(blob) {
      files.push({ name: blob.__name, size: blob.__bytes.length });
      return { setTrashed: () => {} };
    },
  };
}

function makeCtx(folder, secret) {
  const logs = [];
  const ctx = {
    console: { log: (m) => logs.push(String(m)) },
    DriveApp: {
      getFolderById: (id) => {
        if (id !== "FOLDER") throw new Error("no such folder");
        return folder;
      },
    },
    Utilities: {
      // 本物と同じく「base64 文字列 → バイト列」。バイト長だけが検査対象なので Buffer で十分。
      base64Decode: (b64) => Array.from(Buffer.from(b64, "base64")),
      newBlob: (bytes, type, name) => ({ __bytes: bytes, __type: type, __name: name }),
    },
    ContentService: {
      MimeType: { JSON: "JSON" },
      createTextOutput: (t) => ({ setMimeType: () => ({ __text: t }) }),
    },
    __logs: logs,
  };
  vm.createContext(ctx);
  vm.runInContext(src, ctx);
  ctx.FOLDER_ID = "FOLDER";
  ctx.SHARED_SECRET = secret === undefined ? "s".repeat(32) : secret;
  return ctx;
}

/** doPost を呼んで応答 JSON を返す。 */
function post(ctx, body) {
  const out = ctx.doPost({ postData: { contents: JSON.stringify(body) } });
  return JSON.parse(out.__text);
}

const b64 = (n) => Buffer.alloc(n, 120).toString("base64");
const SECRET = "s".repeat(32);

const cases = [];
function check(name, fn, expectOk) {
  let got;
  try {
    got = fn();
  } catch (e) {
    got = { ok: false, error: "threw: " + e.message };
  }
  cases.push({ name, ok: got.ok === expectOk, expectOk, got });
}

// --- 1. ★ 陽性対照: 正当な提出は **通る** ------------------------------------
{
  const folder = makeFolder();
  const ctx = makeCtx(folder, SECRET);
  check(
    "正当な .age（陽性対照）",
    () => post(ctx, { secret: SECRET, name: "P012_block01_gse_20260807_101112.age", b64: b64(1000) }),
    true
  );
  cases.push({
    name: "  └ Drive に 1 本作られている",
    ok: folder.files.length === 1,
    expectOk: true,
    got: { files: folder.files.length },
  });
}

// --- 2. シークレット不一致 → 止まるべき --------------------------------------
{
  const ctx = makeCtx(makeFolder(), SECRET);
  check(
    "シークレットが違う",
    () => post(ctx, { secret: "wrong", name: "P012_block01_x.age", b64: b64(10) }),
    false
  );
}

// --- 3. `.age` 以外 → 止まるべき（design.md §4） -----------------------------
{
  const ctx = makeCtx(makeFolder(), SECRET);
  check(
    "拡張子が .age でない",
    () => post(ctx, { secret: SECRET, name: "P012_gse_20260807.ndjson", b64: b64(10) }),
    false
  );
}

// --- 4. 名前の検査。★★ **各ガードに専用の入力を与える** --------------------
//     ⚠️ 当初は "../../x.age" 1 本だけ置いていたが、★ 許可リスト・パス区切り・`..` の
//     どれを壊しても他が捕まえるので **赤にならなかった**（実測）。
//     → ★ 1 つ壊したら 1 つ赤になる形に組み直す。
{
  const ctx = makeCtx(makeFolder(), SECRET);
  // (2) 許可リストだけが捕まえる: 空白は `/` も `..` も含まない。
  check(
    "名前に空白を含む（許可リスト）",
    () => post(ctx, { secret: SECRET, name: "P012 block01.age", b64: b64(10) }),
    false
  );
}
{
  const ctx = makeCtx(makeFolder(), SECRET);
  // (2) 許可リストだけが捕まえる: パス区切りもここで落ちる。
  check(
    "名前にパス区切りを含む（許可リスト）",
    () => post(ctx, { secret: SECRET, name: "../../P012_block01_x.age", b64: b64(10) }),
    false
  );
}
{
  const ctx = makeCtx(makeFolder(), SECRET);
  // (3) 先頭ドットだけが捕まえる: 許可リストも拡張子も通る入力。
  check(
    "先頭がドット（隠しファイル）",
    () => post(ctx, { secret: SECRET, name: ".P012_block01_x.age", b64: b64(10) }),
    false
  );
}
{
  const ctx = makeCtx(makeFolder(), SECRET);
  // (1) 長さだけが捕まえる: 許可リストも拡張子も先頭も通る入力。
  check(
    "名前が長すぎる（長さ）",
    () => post(ctx, { secret: SECRET, name: "P".repeat(130) + ".age", b64: b64(10) }),
    false
  );
}

// --- 5. 上限超え → 止まるべき -------------------------------------------------
{
  const ctx = makeCtx(makeFolder(), SECRET);
  ctx.MAX_BYTES = 1024;
  check(
    "上限を超える大きさ",
    () => post(ctx, { secret: SECRET, name: "P012_block01_x.age", b64: b64(2048) }),
    false
  );
}

// --- 6. 空 / 壊れた本文 → 止まるべき ------------------------------------------
{
  const ctx = makeCtx(makeFolder(), SECRET);
  check("本文が空", () => post(ctx, { secret: SECRET, name: "P012_block01_x.age", b64: "" }), false);
}
{
  const ctx = makeCtx(makeFolder(), SECRET);
  check(
    "JSON として壊れている",
    () => JSON.parse(ctx.doPost({ postData: { contents: "{" } }).__text),
    false
  );
}

// --- 7. 未設定のまま公開されている → 止まるべき -------------------------------
{
  const ctx = makeCtx(makeFolder(), "");
  check(
    "SHARED_SECRET 未設定で公開",
    () => post(ctx, { secret: "", name: "P012_block01_x.age", b64: b64(10) }),
    false
  );
}

// --- 8. ★★ 同じものを二度送っても **消さない・増やさない**（再送の冪等性） ----
{
  const folder = makeFolder([{ name: "P012_block01_x.age", size: 1000 }]);
  const ctx = makeCtx(folder, SECRET);
  check(
    "同名・同サイズの再送（陽性対照: 受領扱い）",
    () => post(ctx, { secret: SECRET, name: "P012_block01_x.age", b64: b64(1000) }),
    true
  );
  cases.push({
    name: "  └ Drive の本数が増えていない",
    ok: folder.files.length === 1,
    expectOk: true,
    got: { files: folder.files.length },
  });
}

// --- 9. ★★ 同名だが中身が違う → **上書きせず別名で両方残す** ------------------
{
  const folder = makeFolder([{ name: "P012_block01_x.age", size: 1000 }]);
  const ctx = makeCtx(folder, SECRET);
  const res = post(ctx, { secret: SECRET, name: "P012_block01_x.age", b64: b64(2000) });
  cases.push({
    name: "同名・別サイズは上書きしない",
    ok: res.ok === true && folder.files.length === 2 && res.saved !== "P012_block01_x.age",
    expectOk: true,
    got: { saved: res.saved, files: folder.files.length },
  });
}

// --- 10. GET では受け取らない --------------------------------------------------
{
  const ctx = makeCtx(makeFolder(), SECRET);
  check("GET は受け取らない", () => JSON.parse(ctx.doGet({}).__text), false);
}

let ng = 0;
cases.forEach((c) => {
  if (!c.ok) ng++;
  console.log(
    `${c.ok ? "OK  " : "NG  "} ${c.name} → ${JSON.stringify(c.got)}`
  );
});
console.log(
  ng === 0
    ? `\n全 ${cases.length} ケース期待どおり`
    : `\n${ng} 件が期待と違う（全 ${cases.length} ケース）`
);
process.exit(ng === 0 ? 0 : 1);
