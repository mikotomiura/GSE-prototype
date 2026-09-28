// GSE_O1_Submit.gs の受け口ガードをローカルで実測する。
// ★ 実 Drive にも実エンドポイントにも一切触らない（DriveApp / Utilities をスタブする）。
//
// ⚠️ ★ ここで測るのは「ガードを書いた」ではなく **「ガードが止める」** である。
//   陽性対照（正当な提出は通る）を必ず含めること。含めないと、全部拒否する実装でも緑になる。
//
// ⚠️★★★ **本ファイル固有の眼目**: O1 の受け口は
//   **G1 の提出物を受け取ってはならない**（同意範囲の違うデータを混ぜないため）。
//   ★ その陰性対照が §4c である。⚠️ そこを消すと「分離」の主張を誰も検査しなくなる。
const fs = require("fs");
const vm = require("vm");
const path = require("path");

const src = fs.readFileSync(
  process.argv[2] || path.join(__dirname, "GSE_O1_Submit.gs"),
  "utf8"
);

/**
 * ★ ロックの保持状態（Codex 指摘 2026-09-28）: フォルダの検索・作成が**ロックを持った状態で**行われたかを見る。
 *   ⚠️ 偽のロックが固定値を返すだけだと、「検索の前にロックを返す」回帰が緑のまま通る。
 */
const LOCK = { held: false, violations: 0 };
/** Drive の 1 フォルダの代わり。作られたファイルを配列に貯める（★ 消す操作は持たせない）。 */
function makeDir(name, created, trashed) {
  const dir = {
    name,
    files: [],
    subs: [],
    getName: () => name,
    getDateCreated: () => new Date(created || 0),
    isTrashed: () => !!trashed,
    getFilesByName(n) {
      const hits = dir.files.filter((f) => f.name === n);
      let i = 0;
      return {
        hasNext: () => i < hits.length,
        next: () => {
          const f = hits[i++];
          return { getSize: () => f.size, getName: () => f.name };
        },
      };
    },
    getFoldersByName(n) {
      if (!LOCK.held) LOCK.violations++;
      // ⚠️ 実 Drive が大文字小文字を区別するかは未確認 → 偽物は**区別しない**側（厳しい側）に倒す。
      const hits = dir.subs.filter((d) => d.name.toLowerCase() === n.toLowerCase());
      let i = 0;
      return { hasNext: () => i < hits.length, next: () => hits[i++] };
    },
    createFolder(n) {
      if (!LOCK.held) LOCK.violations++;
      const d = makeDir(n, 1e12 + dir.subs.length);
      dir.subs.push(d);
      dir.createdFolders = (dir.createdFolders || 0) + 1;
      return d;
    },
    createFile(blob) {
      dir.files.push({ name: blob.__name, size: blob.__bytes.length });
      return { setTrashed: () => {} };
    },
  };
  return dir;
}

/**
 * 受け取りフォルダ（ルート）の代わり。
 * ★ `preexisting` の要素に `dir` があれば、その名前の P-ID サブフォルダに置く（無ければ直下）。
 * ★ `all()` = 直下 ＋ サブフォルダの全ファイル（どこに入ったかを問わない件数検査用）。
 */
function makeFolder(preexisting) {
  const root = makeDir("STUB", 0);
  (preexisting || []).forEach((f) => {
    if (!f.dir) return root.files.push({ name: f.name, size: f.size });
    let d = root.subs.find((x) => x.name === f.dir);
    if (!d) {
      d = makeDir(f.dir, 0);
      root.subs.push(d);
    }
    d.files.push({ name: f.name, size: f.size });
  });
  root.all = () => root.files.concat(...root.subs.map((d) => d.files));
  root.sub = (n) => root.subs.filter((d) => d.name === n);
  return root;
}

function makeCtx(folder, secret, opt) {
  const logs = [];
  const lockOk = !(opt && opt.lockFails);
  let released = 0;
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
    LockService: {
      getScriptLock: () => ({
        tryLock: () => {
          if (lockOk) LOCK.held = true;
          return lockOk;
        },
        releaseLock: () => {
          LOCK.held = false;
          released++;
        },
      }),
    },
    DriveApp: {
      getFolderById: (id) => {
        if (id !== "FOLDER") throw new Error("no such folder");
        return folder;
      },
    },
    Utilities: {
      base64Decode: (b64) => Array.from(Buffer.from(b64, "base64")),
      newBlob: (bytes, type, name) => ({ __bytes: bytes, __type: type, __name: name }),
    },
    ContentService: {
      MimeType: { JSON: "JSON" },
      createTextOutput: (t) => ({ setMimeType: () => ({ __text: t }) }),
    },
    __logs: logs,
  };
  ctx.__released = () => released;
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

// --- 1. ★ 陽性対照: 正当な O1 提出は **通る** --------------------------------
{
  const folder = makeFolder();
  const ctx = makeCtx(folder, SECRET);
  check(
    "正当な O1 の .age（陽性対照）",
    () =>
      post(ctx, {
        secret: SECRET,
        name: "P012_o1day01_gse_o1_20260828_012103.age",
        b64: b64(1000),
      }),
    true
  );
  cases.push({
    name: "  └ Drive に 1 本作られている",
    ok: folder.all().length === 1,
    expectOk: true,
    got: { files: folder.all().length },
  });
}

// --- 2. シークレット不一致 → 止まるべき --------------------------------------
{
  const ctx = makeCtx(makeFolder(), SECRET);
  check(
    "シークレットが違う",
    () =>
      post(ctx, {
        secret: "wrong",
        name: "P012_o1day01_gse_o1_20260828_012103.age",
        b64: b64(10),
      }),
    false
  );
}

// --- 3. `.age` 以外 → 止まるべき ---------------------------------------------
{
  const ctx = makeCtx(makeFolder(), SECRET);
  check(
    "拡張子が .age でない",
    () => post(ctx, { secret: SECRET, name: "gse_o1_20260828_012103.ndjson", b64: b64(10) }),
    false
  );
}

// --- 4. 名前の検査（★ 1 本のガードが何を落とすかを並べたもの）-----------------
[
  ["名前に空白を含む", "P012 o1day01.age"],
  ["名前にパス区切りを含む", "../../P012_o1day01_gse_o1_20260828_012103.age"],
  ["先頭がドット（隠しファイル）", ".P012_o1day01_gse_o1_20260828_012103.age"],
  ["名前が長すぎる", "P".repeat(130) + ".age"],
  ["提出物の形をしていない .age", "evil.age"],
].forEach(([label, name]) => {
  const ctx = makeCtx(makeFolder(), SECRET);
  check(label, () => post(ctx, { secret: SECRET, name, b64: b64(10) }), false);
});

// --- 4b. ★★ 端末が **実際に作る** O1 の名前は全部通る（陽性対照）--------------
//   ⚠️★ ここが本当に守っているもの: 名前の規約は 2 か所にあり
//     (Rust `submission::o1_age_file_name` ＋ セッション名 `logger::unique_path_from` と、
//      GAS `sanitizeName_`)、★ **片方だけ動くと「毎回 bad name で永久に届かない」**になる。
//   ★ 一覧の導出:
//     - `o1_age_file_name` = `format!("{participant}_o1day{day:02}_{stem}.age")`
//     - `stem` = `gse_o1_<YYYYMMDD>_<HHMMSS>`（`o1.rs:263` + logger のタイムスタンプ）
//     - 同秒ローテート `_2` … `_999`（★ 静かな全損を防ぐための正規の名前）
//     - 1000 本衝突    `_<pid>`
//     - ⚠️ `gse_o1_20260828_012103` は **2026-08-28 の実走で実際に生成された stem** である
{
  const accepted = [
    "P012_o1day01_gse_o1_20260828_012103.age", // ★ 実走で生成された stem
    "P012_o1day10_gse_o1_20260828_012103.age",
    "P012_o1day100_gse_o1_20260828_012103.age", // 3 桁（〜999 日）
    "P012_o1day02_gse_o1_20260828_012103_2.age", // 同秒ローテート
    "P012_o1day02_gse_o1_20260828_012103_999.age",
    "P012_o1day02_gse_o1_20260828_012103_48213.age", // pid 付き
    "a_o1day01_gse_o1_20260828_012103.age", // 参加者 ID 1 文字
    "P0123456789abcde_o1day01_gse_o1_20260828_012103.age", // 参加者 ID 16 文字
  ];
  accepted.forEach((name) => {
    const folder = makeFolder();
    const ctx = makeCtx(folder, SECRET);
    const res = post(ctx, { secret: SECRET, name, b64: b64(100) });
    cases.push({
      name: `端末が作る名前は通る: ${name}`,
      ok: res.ok === true && folder.all().length === 1,
      expectOk: true,
      got: { error: res.error, files: folder.all().length },
    });
  });
}

// --- 4c. ⚠️★★★ **G1 の名前は落とす**（★ 研究の分離を守っている当の検査）--------
//   ★ 研究者判断 C-1「O1 は別に立てる」の**実装上の担保**である。
//   ⚠️ 配布物を取り違えた被験者の G1 提出物が O1 フォルダに混ざるのを、
//     受け口が**構造的に**防ぐ。★ ここを緩めると同意範囲の違うデータが同居する。
{
  const g1Names = [
    "P012_block01_gse_20260808_101112.age",
    "P012_block100_gse_20260808_101112.age",
    "P012_block02_gse_20260808_101112_2.age",
    // ⚠️ 紛らわしい形も落ちること（O1 の接頭辞だけ真似た G1 stem）
    "P012_o1day01_gse_20260808_101112.age", // stem が `gse_o1_` でない
    "P012_block01_gse_o1_20260828_012103.age", // 日番号が `block`
  ];
  g1Names.forEach((name) => {
    const folder = makeFolder();
    const ctx = makeCtx(folder, SECRET);
    const res = post(ctx, { secret: SECRET, name, b64: b64(100) });
    cases.push({
      name: `⚠️ G1 / 紛らわしい名前は落とす: ${name}`,
      ok: res.ok === false && res.error === "bad name" && folder.all().length === 0,
      expectOk: true,
      got: { error: res.error, files: folder.all().length },
    });
  });
}

// --- 4d. 境界の陰性対照（連番を許したことで何でも通るようになっていないこと）----
{
  const rejected = [
    "P012_o1day02_gse_o1_20260828_012103_x.age", // 連番が数字でない
    "P012_o1day02_gse_o1_20260828_012103_.age", // 連番が空
    "P012_o1day02_gse_o1_20260828_012103_2_3.age", // 連番が 2 段
    "P012_o1day02_gse_o1_20260828_0121_2.age", // 時刻が 6 桁でない
    "P012_o1day1_gse_o1_20260828_012103.age", // 日番号が 1 桁（`{day:02}` は 2 桁以上）
  ];
  rejected.forEach((name) => {
    const folder = makeFolder();
    const ctx = makeCtx(folder, SECRET);
    const res = post(ctx, { secret: SECRET, name, b64: b64(100) });
    cases.push({
      name: `連番を許しても形が崩れた名前は落とす: ${name}`,
      ok: res.ok === false && res.error === "bad name" && folder.all().length === 0,
      expectOk: true,
      got: { error: res.error, files: folder.all().length },
    });
  });
}

// --- 5. 上限まわり -----------------------------------------------------------
//   ⚠️★★★ O1 の上限は **G1 (8 MB) では足りない**。実測（2026-08-28）:
//     raw 6,388,517 B / 7.21 時間（打鍵 0 本）→ `.age` 5,730,783 B → 24 時間換算 約 18 MB。
//   ★ 下の 2 ケースは「1 日ぶんが通り、青天井ではない」を同時に固定する。
{
  // ⚠️★ `ok===false` だけを見ると赤にならない（名前ガードが壊れても同じ結果になる）。
  //   ★ **どの理由で断ったか**と**保存されていないこと**まで固定する（code-reviewer 指摘）。
  const folder = makeFolder();
  const ctx = makeCtx(folder, SECRET);
  ctx.MAX_BYTES = 1024;
  const res = post(ctx, {
    secret: SECRET,
    name: "P012_o1day01_gse_o1_20260828_012103.age",
    b64: b64(2048),
  });
  cases.push({
    name: "上限を超える大きさは 'too large' で断り、保存しない",
    ok: res.ok === false && res.error === "too large" && folder.all().length === 0,
    expectOk: true,
    got: { error: res.error, files: folder.all().length },
  });
}
{
  // ★ `decodedLength_` の境界（padding 0 / 1 / 2）。⚠️ ここが 2 バイトずれても
  //   上のケースだけでは誰も赤にできない（code-reviewer 指摘）。
  const ctx = makeCtx(makeFolder(), SECRET);
  [
    [3, "AAAA"], // padding 0
    [2, "AAA="], // padding 1
    [1, "AA=="], // padding 2
  ].forEach(([expected, b64s]) => {
    const got = ctx.decodedLength_(b64s);
    cases.push({
      name: `decodedLength_("${b64s}") == ${expected}`,
      ok: got === expected,
      expectOk: true,
      got: { got, expected },
    });
  });
}
{
  // ★ **実測に基づく回帰**: 1 日ぶん（実測 24h 換算 約 18 MB）が上限に当たらないこと。
  //   ⚠️ `MAX_BYTES` を G1 の 8 MB に戻すと **このケースが赤になる**。
  const DAY_BYTES = 19 * 1024 * 1024;
  const ctx = makeCtx(makeFolder(), SECRET);
  const ok = ctx.MAX_BYTES >= DAY_BYTES;
  cases.push({
    name: `1 日ぶん（実測 24h 換算 ≒ 18 MB）が上限内: MAX_BYTES=${ctx.MAX_BYTES} >= ${DAY_BYTES}`,
    ok,
    expectOk: true,
    got: { MAX_BYTES: ctx.MAX_BYTES, needed: DAY_BYTES },
  });
}
{
  // ⚠️ 青天井にしない（いたずら投稿で Drive を埋められないため）。
  const ctx = makeCtx(makeFolder(), SECRET);
  cases.push({
    name: "上限は青天井ではない（<= 256 MB）",
    ok: ctx.MAX_BYTES <= 256 * 1024 * 1024,
    expectOk: true,
    got: { MAX_BYTES: ctx.MAX_BYTES },
  });
}

{
  // ⚠️★★★ **上限が「到達可能」であること**（★ 2026-09-05 に実測して足した）。
  //
  //   ★ 稼働中の受け口へ実際に POST して測った
  //   (`experiments/20260801-controlled-friction-task/o1-upload-timeout-measurement.md`):
  //     raw 36 MB（本文 48.0 MB）… ★ **通る**（97.3 s）
  //     raw 40 MB（本文 53.3 MB）… ⚠️ **HTTP 400** —— Apps Script Web App の
  //       **HTTP 本文の上限が先に効き、Google が `doPost` に届く前に弾く**。
  //
  //   ⚠️ そのとき受け口の `too large` は**返らない** = 研究者にも被験者にも理由が伝わらない。
  //   → ★ `MAX_BYTES` を到達不能な値にすると、**上の「上限の検査」が意味を失う**
  //     （★ 実際 2026-09-05 まで 48 MB で、⚠️ **一度も到達できなかった**）。
  const REACHABLE_MAX = 36 * 1024 * 1024; // ★ 実測で通った最大（raw）
  const ctx = makeCtx(makeFolder(), SECRET);
  cases.push({
    name: `上限が到達可能な範囲にある（<= 36 MB・実測）`,
    ok: ctx.MAX_BYTES <= REACHABLE_MAX,
    expectOk: true,
    got: { MAX_BYTES: ctx.MAX_BYTES, reachable_max: REACHABLE_MAX },
  });
}

// --- 6. 空 / 壊れた本文 → 止まるべき ------------------------------------------
{
  const ctx = makeCtx(makeFolder(), SECRET);
  check(
    "本文が空",
    () => post(ctx, { secret: SECRET, name: "P012_o1day01_gse_o1_20260828_012103.age", b64: "" }),
    false
  );
}
{
  // ★ 空でない base64 が 0 バイトに解ける形。
  const ctx = makeCtx(makeFolder(), SECRET);
  check(
    "空でない base64 が 0 バイトに解ける",
    () =>
      post(ctx, { secret: SECRET, name: "P012_o1day01_gse_o1_20260828_012103.age", b64: "====" }),
    false
  );
}
{
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
  // ⚠️ ★ `ok:false` だけを見ると赤にならない。★ **どの理由で断ったか**まで固定する。
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
  // ⚠️ ★ **Node の Buffer は壊れた base64 でも例外を投げない**ので、ここだけ本物
  //   (GAS の `Utilities.base64Decode`) と同じく**投げる**スタブに差し替える。
  //   ★ そうしないと「検査を書いたが一度も発火しない」テストになる。
  const ctx = makeCtx(makeFolder(), SECRET);
  ctx.Utilities.base64Decode = () => {
    throw new Error("Invalid argument");
  };
  const res = post(ctx, {
    secret: SECRET,
    name: "P012_o1day01_gse_o1_20260828_012103.age",
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
    () =>
      post(ctx, {
        secret: "",
        name: "P012_o1day01_gse_o1_20260828_012103.age",
        b64: b64(10),
      }),
    false
  );
}
{
  const ctx = makeCtx(makeFolder(), SECRET);
  ctx.__setProp("FOLDER_ID", "");
  const res = post(ctx, {
    secret: SECRET,
    name: "P012_o1day01_gse_o1_20260828_012103.age",
    b64: b64(10),
  });
  cases.push({
    name: "FOLDER_ID 未設定は 'server error' でなく設定不足として返す",
    ok: res.ok === false && res.error === "endpoint not configured",
    expectOk: true,
    got: res,
  });
}

// --- 8. GET は受け取らない ----------------------------------------------------
{
  const ctx = makeCtx(makeFolder(), SECRET);
  const res = JSON.parse(ctx.doGet({}).__text);
  cases.push({
    name: "GET は 'use POST' で断る（秘密も件数も返さない）",
    ok: res.ok === false && res.error === "use POST" && Object.keys(res).length === 2,
    expectOk: true,
    got: res,
  });
}

// --- 9. ★★ 同名でも握り潰さず保存する ----------------------------------------
{
  const NAME = "P012_o1day01_gse_o1_20260828_012103.age";
  const folder = makeFolder([{ name: NAME, size: 1000, dir: "P012" }]);
  const ctx = makeCtx(folder, SECRET);
  const res = post(ctx, { secret: SECRET, name: NAME, b64: b64(1000) });
  cases.push({
    name: "同名・同サイズでも握り潰さず保存する",
    ok:
      res.ok === true &&
      res.duplicate === true &&
      folder.all().length === 2 &&
      res.saved !== NAME,
    expectOk: true,
    got: { saved: res.saved, duplicate: res.duplicate, files: folder.all().length },
  });
  cases.push({
    name: "  └ 既にあったほうを消していない",
    ok: folder.all().some((f) => f.name === NAME),
    expectOk: true,
    got: { names: folder.all().map((f) => f.name) },
  });
}

// --- 11. ★★ P-ID ごとのサブフォルダに保存する（2026-09-28・V-3） ---------------
//   ⚠️ 陰性対照を必ず並べる: 直下に置かない／ロックが取れなければ保存しない。
{
  const N1 = "P012_o1day01_gse_o1_20260828_012103.age";
  const N2 = "P012_o1day02_gse_o1_20260829_012103.age";
  const M1 = "P013_o1day01_gse_o1_20260828_012103.age";
  const folder = makeFolder();
  const ctx = makeCtx(folder, SECRET);
  const r1 = post(ctx, { secret: SECRET, name: N1, b64: b64(10) });
  const r2 = post(ctx, { secret: SECRET, name: N2, b64: b64(10) });
  const r3 = post(ctx, { secret: SECRET, name: M1, b64: b64(10) });
  const p12 = folder.sub("P012");
  const p13 = folder.sub("P013");
  cases.push({
    name: "★ P-ID のサブフォルダに保存し、直下には置かない",
    ok: r1.ok === true && folder.files.length === 0 && p12.length === 1 && p12[0].files.some((f) => f.name === N1),
    expectOk: true,
    got: { ok: r1.ok, root: folder.files.length, p12: p12.map((d) => d.files.map((f) => f.name)) },
  });
  cases.push({
    name: "  └ 同じ P-ID の 2 本目はフォルダを作らず同じフォルダへ",
    ok: r2.ok === true && p12.length === 1 && p12[0].files.length === 2,
    expectOk: true,
    got: { ok: r2.ok, p12Folders: p12.length, p12Files: p12.length ? p12[0].files.length : 0 },
  });
  cases.push({
    name: "  └ 別の P-ID は別のフォルダへ（混ざらない）",
    ok: r3.ok === true && p13.length === 1 && p13[0].files.length === 1 && folder.createdFolders === 2,
    expectOk: true,
    got: { ok: r3.ok, p13: p13.length, created: folder.createdFolders },
  });
  cases.push({
    name: "  └ 保存のたびにロックを返している",
    ok: ctx.__released() === 3,
    expectOk: true,
    got: { released: ctx.__released() },
  });
}
{
  // 同名の P-ID フォルダが複数ある → 最古に入れる。⚠️ ごみ箱のフォルダは最古でも使わない。
  const NAME = "P012_o1day01_gse_o1_20260828_012103.age";
  const folder = makeFolder();
  const trashedOldest = makeDir("P012", 100, true);
  const newer = makeDir("P012", 300);
  const older = makeDir("P012", 200);
  folder.subs.push(trashedOldest, newer, older);
  const ctx = makeCtx(folder, SECRET);
  const res = post(ctx, { secret: SECRET, name: NAME, b64: b64(10) });
  cases.push({
    name: "★ 同名の P-ID フォルダが複数あれば最古（ごみ箱を除く）に入れ、新たに作らない",
    ok: res.ok === true && older.files.length === 1 && newer.files.length === 0 && trashedOldest.files.length === 0 && !folder.createdFolders,
    expectOk: true,
    got: { ok: res.ok, older: older.files.length, newer: newer.files.length, trashed: trashedOldest.files.length, created: folder.createdFolders || 0 },
  });
}
{
  // ごみ箱のフォルダしか無い → 新しく作る（捨てたフォルダへ入れない）
  const NAME = "P012_o1day01_gse_o1_20260828_012103.age";
  const folder = makeFolder();
  const trashed = makeDir("P012", 100, true);
  folder.subs.push(trashed);
  const ctx = makeCtx(folder, SECRET);
  const res = post(ctx, { secret: SECRET, name: NAME, b64: b64(10) });
  cases.push({
    name: "★ ごみ箱の P-ID フォルダしか無ければ新しく作る",
    ok: res.ok === true && trashed.files.length === 0 && folder.createdFolders === 1,
    expectOk: true,
    got: { ok: res.ok, trashed: trashed.files.length, created: folder.createdFolders || 0 },
  });
}
{
  // 重複の判定は P-ID フォルダの中で行う（別の P-ID の同名は重複ではない・直下の旧形式も見ない）
  const NAME = "P012_o1day01_gse_o1_20260828_012103.age";
  const folder = makeFolder([{ name: NAME, size: 10 }]);
  const ctx = makeCtx(folder, SECRET);
  const res = post(ctx, { secret: SECRET, name: NAME, b64: b64(10) });
  cases.push({
    name: "  └ 直下の旧形式と同名でも P-ID フォルダ内に無ければ重複扱いしない",
    ok: res.ok === true && res.duplicate === false && res.saved === NAME,
    expectOk: true,
    got: { ok: res.ok, duplicate: res.duplicate, saved: res.saved },
  });
}
{
  // ⚠️ ロックが取れない → 保存しない・フォルダも作らない・ok:false（★ 端末は未送信のまま再送する）
  const folder = makeFolder();
  const ctx = makeCtx(folder, SECRET, { lockFails: true });
  const res = post(ctx, { secret: SECRET, name: "P012_o1day01_gse_o1_20260828_012103.age", b64: b64(10) });
  cases.push({
    name: "⚠️ ロックが取れなければ保存せず busy を返す",
    ok: res.ok === false && res.error === "busy" && folder.all().length === 0 && !folder.createdFolders,
    expectOk: true,
    got: { res, files: folder.all().length, created: folder.createdFolders || 0 },
  });
}

{
  // フォルダ作成が例外 → server error（★ 端末は再送する）・ロックは返している（finally）
  const folder = makeFolder();
  folder.createFolder = () => {
    throw new Error("Drive quota");
  };
  const ctx = makeCtx(folder, SECRET);
  const res = post(ctx, { secret: SECRET, name: "P012_o1day01_gse_o1_20260828_012103.age", b64: b64(10) });
  cases.push({
    name: "  └ フォルダ作成が例外でも server error を返し、ロックを返している",
    ok: res.ok === false && res.error === "server error" && ctx.__released() === 1 && folder.all().length === 0,
    expectOk: true,
    got: { res, released: ctx.__released(), files: folder.all().length },
  });
}

{
  // 大文字小文字だけ違う P-ID は別フォルダ（名前の検索が区別しなくても混ぜない）
  const folder = makeFolder([{ name: "P012_o1day01_gse_o1_20260828_012103.age", size: 1, dir: "P012" }]);
  const ctx = makeCtx(folder, SECRET);
  const res = post(ctx, { secret: SECRET, name: "p012_o1day01_gse_o1_20260828_012103.age", b64: b64(10) });
  const upper = folder.sub("P012")[0];
  const lower = folder.subs.filter((d) => d.name === "p012");
  cases.push({
    name: "★ 大文字小文字だけ違う P-ID を既存フォルダに混ぜない",
    ok: res.ok === true && upper.files.length === 1 && lower.length === 1 && lower[0].files.length === 1,
    expectOk: true,
    got: { ok: res.ok, upper: upper.files.length, lower: lower.map((d) => d.files.length) },
  });
}

cases.push({
  name: "★ P-ID フォルダの検索・作成はすべてロックを持った状態で行われた（全ケース通算）",
  ok: LOCK.violations === 0 && LOCK.held === false,
  expectOk: true,
  got: { violations: LOCK.violations, heldAtEnd: LOCK.held },
});

// --- 10. ⚠️ このファイルは **秘密を含まない** --------------------------------
//   ★ repo は一時 public にする運用がある。`.gs` に FOLDER_ID / SHARED_SECRET を
//     書いた瞬間に誰でも研究者の Drive へ書き込めるようになる（git 履歴からも消せない）。
{
  const hardcoded =
    /(SHARED_SECRET|FOLDER_ID)\s*=\s*['"][^'"]+['"]/.test(src) ||
    /['"][A-Za-z0-9_-]{25,}['"]/.test(src.replace(/^\s*\*.*$/gm, ""));
  cases.push({
    name: "⚠️ .gs にシークレット / フォルダ ID を直書きしていない",
    ok: !hardcoded,
    expectOk: true,
    got: { hardcoded },
  });
}

// --- 出力 ---------------------------------------------------------------------
// ⚠️★ 末尾 1 行の書式は `submit_guard_test.cjs` と**同一にする**。
//   ★ `run.sh` の `guard_count()` が `^全 <N> ケース期待どおり$` を sed で読むので、
//     書式を変えると **件数が「件数不明」に落ちる**（★ 赤にはならないので気づきにくい）。
let ng = 0;
cases.forEach((c) => {
  if (!c.ok) ng++;
  console.log(`${c.ok ? "OK  " : "NG  "} ${c.name} → ${JSON.stringify(c.got)}`);
});

// ⚠️ ★ 「NG が 0 件なら緑」だけだと、**ケースを 0 件にしても緑になる**。★ 下限を置く。
//   （`verify-before-claiming` ルール 5b: 検査自体が空回りしていないかを見る）
if (cases.length < 30) {
  console.log(
    `\n${cases.length} 件しかケースが無い（30 未満）。テストが削られていないか確認すること。`
  );
  process.exit(1);
}

console.log(
  ng === 0
    ? `\n全 ${cases.length} ケース期待どおり`
    : `\n${ng} 件が期待と違う（全 ${cases.length} ケース）`
);
process.exit(ng === 0 ? 0 : 1);
