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
  // ★ 設定は **スクリプト プロパティ**から読む（ソースに秘密を置かないため）。
  const props = {
    FOLDER_ID: "FOLDER",
    SHARED_SECRET: secret === undefined ? "s".repeat(32) : secret,
  };
  const ctx = {
    console: { log: (m) => logs.push(String(m)) },
    PropertiesService: {
      getScriptProperties: () => ({
        getProperty: (k) => (k in props ? props[k] : null),
      }),
    },
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
  ctx.__setProp = (k, v) => {
    props[k] = v;
  };
  vm.createContext(ctx);
  vm.runInContext(src, ctx);
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
    () => post(ctx, { secret: SECRET, name: "P012_block01_gse_20260808_101112.age", b64: b64(1000) }),
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
    () => post(ctx, { secret: "wrong", name: "P012_block01_gse_20260808_101112.age", b64: b64(10) }),
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

// --- 4. 名前の検査 ------------------------------------------------------------
//   ⚠️★★ 経緯（★ どちらも実測）:
//     1. 最初は `/` `\` `..` を個別に弾いていた → **1 行ずつ壊しても赤にならなかった**
//     2. 許可リスト / 先頭ドット / 拡張子 / 長さ の 4 本に整理した
//        → **提出物の形**まで絞る 1 本を足したら、★ その 1 本が 4 本を包含して
//          **どれを壊しても赤にならなくなった**
//   → ★ **1 本に統合した。** 下のケースは「その 1 本が何を落とすか」を並べたものであり、
//     ⚠️ ガードを壊すと **全部まとめて赤になる**（1 対 1 対応ではない）。
{
  const ctx = makeCtx(makeFolder(), SECRET);
  check(
    "名前に空白を含む",
    () => post(ctx, { secret: SECRET, name: "P012 block01.age", b64: b64(10) }),
    false
  );
}
{
  const ctx = makeCtx(makeFolder(), SECRET);
  check(
    "名前にパス区切りを含む",
    () => post(ctx, { secret: SECRET, name: "../../P012_block01_gse_20260808_101112.age", b64: b64(10) }),
    false
  );
}
{
  const ctx = makeCtx(makeFolder(), SECRET);
  check(
    "先頭がドット（隠しファイル）",
    () => post(ctx, { secret: SECRET, name: ".P012_block01_gse_20260808_101112.age", b64: b64(10) }),
    false
  );
}
{
  const ctx = makeCtx(makeFolder(), SECRET);
  check(
    "名前が長すぎる",
    () => post(ctx, { secret: SECRET, name: "P".repeat(130) + ".age", b64: b64(10) }),
    false
  );
}
{
  const ctx = makeCtx(makeFolder(), SECRET);
  // ★ security-checker の指摘: 「`.age` でありさえすればよい」では足りない。
  check(
    "提出物の形をしていない .age",
    () => post(ctx, { secret: SECRET, name: "evil.age", b64: b64(10) }),
    false
  );
}

// --- 4b. ★★ 端末が **実際に作る**名前は全部通る（陽性対照）---------------------
//   ⚠️★ ここが本当に守っているもの: 名前の規約は 2 か所にあり
//     (Rust `submission::age_file_name` ＋ セッション名 `logger::unique_path_from` と、
//      GAS `sanitizeName_`)、★ **片方だけ動くと「毎回 bad name で永久に届かない」**になる。
//   ★ 下の一覧は logger の命名規則から導いた実在の形である（cross-review: Codex 指摘で追加）:
//     - 通常          `gse_YYYYMMDD_HHMMSS`
//     - 同秒ローテート `gse_YYYYMMDD_HHMMSS_2` … `_999`（★ 静かな全損を防ぐための正規の名前）
//     - 1000 本衝突    `gse_YYYYMMDD_HHMMSS_<pid>`
//     - ブロック 3 桁  `_block100_`
{
  const accepted = [
    "P012_block01_gse_20260808_101112.age",
    "P012_block10_gse_20260808_101112.age",
    "P012_block100_gse_20260808_101112.age",
    "P012_block02_gse_20260808_101112_2.age",
    "P012_block02_gse_20260808_101112_999.age",
    "P012_block02_gse_20260808_101112_48213.age",
    "a_block01_gse_20260808_101112.age",
    "P0123456789abcde_block01_gse_20260808_101112.age",
  ];
  accepted.forEach((name) => {
    const folder = makeFolder();
    const ctx = makeCtx(folder, SECRET);
    const res = post(ctx, { secret: SECRET, name, b64: b64(100) });
    cases.push({
      name: `端末が作る名前は通る: ${name}`,
      ok: res.ok === true && folder.files.length === 1,
      expectOk: true,
      got: { error: res.error, files: folder.files.length },
    });
  });
}
{
  // ⚠️ ★ 連番を許したことで **何でも通る**ようになっていないことを測る（境界の陰性対照）。
  const rejected = [
    "P012_block02_gse_20260808_101112_x.age", // 連番が数字でない
    "P012_block02_gse_20260808_101112_.age", // 連番が空
    "P012_block02_gse_20260808_101112_2_3.age", // 連番が 2 段
    "P012_block02_gse_20260808_1011_2.age", // 時刻が 6 桁でない
  ];
  rejected.forEach((name) => {
    const folder = makeFolder();
    const ctx = makeCtx(folder, SECRET);
    const res = post(ctx, { secret: SECRET, name, b64: b64(100) });
    cases.push({
      name: `連番を許しても形が崩れた名前は落とす: ${name}`,
      ok: res.ok === false && res.error === "bad name" && folder.files.length === 0,
      expectOk: true,
      got: { error: res.error, files: folder.files.length },
    });
  });
}

// --- 5. 上限超え → 止まるべき -------------------------------------------------
{
  const ctx = makeCtx(makeFolder(), SECRET);
  ctx.MAX_BYTES = 1024;
  check(
    "上限を超える大きさ",
    () => post(ctx, { secret: SECRET, name: "P012_block01_gse_20260808_101112.age", b64: b64(2048) }),
    false
  );
}

// --- 6. 空 / 壊れた本文 → 止まるべき ------------------------------------------
{
  const ctx = makeCtx(makeFolder(), SECRET);
  check("本文が空", () => post(ctx, { secret: SECRET, name: "P012_block01_gse_20260808_101112.age", b64: "" }), false);
}
{
  // ★ 空でない base64 が 0 バイトに解ける形。⚠️ この入力だけが `bytes.length === 0` を
  //   単独で赤にできる（`!b64` は通ってしまう）。
  const ctx = makeCtx(makeFolder(), SECRET);
  check(
    "空でない base64 が 0 バイトに解ける",
    () => post(ctx, { secret: SECRET, name: "P012_block01_gse_20260808_101112.age", b64: "====" }),
    false
  );
}
{
  // ★ POST 本文そのものが無い。⚠️ この入力だけが「本文の有無」チェックを単独で赤にできる
  //   （壊すと 'server error' になってしまい、原因が研究者に伝わらない）。
  const ctx = makeCtx(makeFolder(), SECRET);
  const res = JSON.parse(ctx.doPost({}).__text);
  cases.push({
    name: "本文が無い POST は 'no body' と返す",
    ok: res.ok === false && res.error === "no body",
    expectOk: true,
    got: res,
  });
}
{
  // ⚠️ ★ `ok:false` だけを見ると赤にならない（壊すと unauthorized 側に落ちて
  //   結局 ok:false になるため — 実測）。★ **どの理由で断ったか**まで固定する。
  const ctx = makeCtx(makeFolder(), SECRET);
  const res = JSON.parse(ctx.doPost({ postData: { contents: "{" } }).__text);
  cases.push({
    name: "JSON として壊れている本文は 'bad json' と返す",
    ok: res.ok === false && res.error === "bad json",
    expectOk: true,
    got: res,
  });
}

{
  // ⚠️ ★ base64 として壊れた本文。**Node の Buffer は壊れた base64 でも例外を投げない**ので、
  //   ここだけ本物 (GAS の `Utilities.base64Decode`) と同じく**投げる**スタブに差し替える。
  //   ★ そうしないと「検査を書いたが一度も発火しない」テストになる。
  //   測っているのは「止まる」ではなく **「理由が研究者に伝わる」** (server error に丸めない)。
  const ctx = makeCtx(makeFolder(), SECRET);
  ctx.Utilities.base64Decode = () => {
    throw new Error("Invalid argument");
  };
  const res = post(ctx, {
    secret: SECRET,
    name: "P012_block01_gse_20260808_101112.age",
    b64: "!!!not-base64!!!",
  });
  cases.push({
    name: "壊れた base64 は 'server error' でなく 'bad base64' と返す",
    ok: res.ok === false && res.error === "bad base64",
    expectOk: true,
    got: res,
  });
}

// --- 7. 未設定のまま公開されている → 止まるべき -------------------------------
{
  const ctx = makeCtx(makeFolder(), "");
  check(
    "SHARED_SECRET 未設定で公開",
    () => post(ctx, { secret: "", name: "P012_block01_gse_20260808_101112.age", b64: b64(10) }),
    false
  );
}
{
  // ★ FOLDER_ID だけ未設定（シークレットは正しい）。⚠️ この入力だけが
  //   「設定チェック」を単独で赤にできる（シークレット照合は通ってしまうため）。
  const ctx = makeCtx(makeFolder(), SECRET);
  ctx.__setProp("FOLDER_ID", "");
  const res = post(ctx, {
    secret: SECRET,
    name: "P012_block01_gse_20260808_101112.age",
    b64: b64(10),
  });
  cases.push({
    name: "FOLDER_ID 未設定は 'server error' でなく設定不足として返す",
    ok: res.ok === false && res.error === "endpoint not configured",
    expectOk: true,
    got: res,
  });
}

// --- 8. ★★ 同名・同サイズが既にあっても **必ず保存する（握り潰さない）** -------
//     ⚠️★ 当初は「同名・同サイズなら保存せず ok を返す」にしていた。
//     ★ これは **提出を握り潰す経路**になる: シークレットを持つ者が同名・同サイズの
//     ダミーを先回りして置くと、本物の提出に ok を返してしまい、端末側は `.sent` を書く。
//     ⚠️ 送信先から成否を追えないので **誰も気づかないまま 1 本失われる**。
//     → ★ 「重複が並ぶ」より「1 本消える」ほうが桁違いに悪い。**必ず保存する。**
{
  const folder = makeFolder([{ name: "P012_block01_gse_20260808_101112.age", size: 1000 }]);
  const ctx = makeCtx(folder, SECRET);
  const res = post(ctx, {
    secret: SECRET,
    name: "P012_block01_gse_20260808_101112.age",
    b64: b64(1000),
  });
  cases.push({
    name: "同名・同サイズでも握り潰さず保存する",
    ok:
      res.ok === true &&
      res.duplicate === true &&
      folder.files.length === 2 &&
      res.saved !== "P012_block01_gse_20260808_101112.age",
    expectOk: true,
    got: { saved: res.saved, duplicate: res.duplicate, files: folder.files.length },
  });
  cases.push({
    name: "  └ 既にあったほうを消していない",
    ok: folder.files.some((f) => f.name === "P012_block01_gse_20260808_101112.age"),
    expectOk: true,
    got: { names: folder.files.map((f) => f.name) },
  });
}

// --- 9. ★★ 同名だが中身が違う → **上書きせず別名で両方残す** ------------------
{
  const folder = makeFolder([{ name: "P012_block01_gse_20260808_101112.age", size: 1000 }]);
  const ctx = makeCtx(folder, SECRET);
  const res = post(ctx, { secret: SECRET, name: "P012_block01_gse_20260808_101112.age", b64: b64(2000) });
  cases.push({
    name: "同名・別サイズは上書きしない",
    ok: res.ok === true && folder.files.length === 2 && res.saved !== "P012_block01_gse_20260808_101112.age",
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
