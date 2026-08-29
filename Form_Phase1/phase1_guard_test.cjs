// GSE_Phase1_Form_Builder.gs のガード 2 本をローカルで実測する。
//   §1〜§4  「Phase1 集計の凍結」(T-25)
//   §5      ウェブアプリ URL をコードに焼かないこと (T-29)
// ★ 実スプレッドシートにも実フォームにも一切触らない（全部スタブ）。
//
// ⚠️★★★ ここで測るのは「凍結を書いた」ではなく **「凍結が止める」** である。
//   → ★ 陽性対照（実施中なら集計が**実際に走る**）を必ず含める。
//     含めないと、常に何もしない実装でも「止まっている」ように見えて緑になる
//     （browser-verification §2.0 の「対照を取る」と同じ理屈）。
//
// ⚠️ 凍結が必要な理由（＝この検査が守っているもの）:
//   参加者ロスターは Phase1 / G1 / O1 の**共用**で、集計は全行を Phase1 の母数として数える。
//   → Phase1 終了後に集計を続けると、完了率・平均セッション数が**実際より低く出る**（誤った値）。
//
// 実行: node Form_Phase1/phase1_guard_test.cjs
const fs = require("fs");
const vm = require("vm");
const path = require("path");

const BUILDER =
  process.argv[2] || path.join(__dirname, "GSE_Phase1_Form_Builder.gs");
const src = fs.readFileSync(BUILDER, "utf8");

// ============================================================
// Google Apps Script のスタブ
// ============================================================

/** シート。★ 何を読み書きしたかを後から数えられるように記録する。 */
function makeSheet(name, opts) {
  opts = opts || {};
  const sh = {
    __name: name,
    __writes: [], // setValue / setValues の呼び出し記録
    __cleared: 0,
    __cellThrows: !!opts.cellThrows,
    __values: opts.values || {}, // "r,c" → 値
    getName: () => name,
    getMaxRows: () => 50,
    getMaxColumns: () => 12,
    getLastRow: () => opts.lastRow || 0,
    clear: () => {
      sh.__cleared++;
      return sh;
    },
    setRowHeight: () => sh,
    setColumnWidth: () => sh,
    setFrozenRows: () => sh,
    getBandings: () => [],
    setConditionalFormatRules: () => sh,
    getRange: (r, c, nr, nc) => {
      // ⚠️★ A1 表記 ("B2") を解釈できないと、phase1Frozen_ のタブ B2 フォールバックが
      //   「値が空」で必ず false を返し、★ 検査が空回りする（実測で踏んだ）。
      if (typeof r === "string") {
        const m = /^([A-Z]+)(\d+)$/.exec(r.trim().toUpperCase());
        if (!m) throw new Error("stub: 未対応の A1 表記: " + r);
        let col = 0;
        for (const ch of m[1]) col = col * 26 + (ch.charCodeAt(0) - 64);
        return makeRange(sh, Number(m[2]), col, 1, 1);
      }
      return makeRange(sh, r, c, nr || 1, nc || 1);
    },
  };
  return sh;
}

function makeRange(sh, r, c, nr, nc) {
  const rng = {
    getValue: () => {
      if (sh.__cellThrows) throw new Error("stub: セルを読めません");
      const v = sh.__values[r + "," + c];
      return v === undefined ? "" : v;
    },
    getValues: () => {
      const out = [];
      for (let i = 0; i < nr; i++) {
        const row = [];
        for (let j = 0; j < nc; j++) {
          const v = sh.__values[r + i + "," + (c + j)];
          row.push(v === undefined ? "" : v);
        }
        out.push(row);
      }
      return out;
    },
    setValue: (v) => {
      sh.__writes.push({ r, c, v });
      return rng;
    },
    setValues: (vs) => {
      sh.__writes.push({ r, c, v: vs });
      return rng;
    },
    merge: () => rng,
    breakApart: () => rng,
    setBackground: () => rng,
    setFontColor: () => rng,
    setFontWeight: () => rng,
    setFontSize: () => rng,
    setFontFamily: () => rng,
    setWrap: () => rng,
    setVerticalAlignment: () => rng,
    setHorizontalAlignment: () => rng,
    setNumberFormat: () => rng,
    setNote: () => rng,
    setDataValidation: () => rng,
    clearDataValidations: () => rng,
    setBorder: () => rng,
    setBanding: () => rng,
    applyRowBanding: () => ({ setHeaderRowColor: () => ({ setFirstRowColor: () => ({ setSecondRowColor: () => ({}) }) }) }),
  };
  return rng;
}

/**
 * スプレッドシート。
 * @param opts.status         「運用コントロール」の状態値（null なら名前付き範囲もタブも無い＝未設置）
 * @param opts.viaNamedRange  true=名前付き範囲で返す / false=タブ B2 フォールバックで返す
 * @param opts.statusThrows   状態セルの読み取りが例外を投げる（＝壊れている状態）
 */
function makeSS(opts) {
  opts = opts || {};
  const control =
    opts.status === null && !opts.statusThrows
      ? null
      : makeSheet("運用コントロール", {
          values: { "2,2": opts.status },
          cellThrows: !!opts.statusThrows,
        });
  // ロスター: ヘッダ行 1（A1="P-ID"）＋ データ行 2 行
  const roster = makeSheet("参加者ロスター", {
    lastRow: 3,
    values: {
      "1,1": "P-ID",
      "2,1": "P001",
      "3,1": "P002",
    },
  });
  const sheets = { 参加者ロスター: roster };
  if (control) sheets["運用コントロール"] = control;
  const ss = {
    __sheets: sheets,
    __roster: roster,
    __control: control,
    getSheetByName: (n) => sheets[n] || null,
    insertSheet: (n) => {
      sheets[n] = makeSheet(n);
      return sheets[n];
    },
    getRangeByName: (n) => {
      if (!opts.viaNamedRange || !control) return null;
      return makeRange(control, 2, 2, 1, 1);
    },
    getId: () => "STUB_SS_ID",
    getSheets: () => Object.keys(sheets).map((k) => sheets[k]),
  };
  return ss;
}

/** 実行環境を 1 つ組み立てる。countByPid_ が呼ばれた回数を数える（＝集計が走ったか）。 */
function makeCtx(opts) {
  opts = opts || {};
  const counters = { formOpens: 0, logs: [] };
  const ss = opts.ss || makeSS(opts);

  const props = {
    __p: Object.assign(
      {
        GSE_MGMT_SHEET_ID: opts.noMgmtSheet ? undefined : "STUB_SS_ID",
        // countByPid_ が実際にフォームを開きに行くために必要（＝集計が走った証拠になる）
        FORMURL_F2: JSON.stringify({ id: "STUB_F2" }),
        FORMURL_F4: JSON.stringify({ id: "STUB_F4" }),
        FORMURL_F5: JSON.stringify({ id: "STUB_F5" }),
      },
      opts.props || {}
    ),
    getProperty: (k) => {
      const v = props.__p[k];
      return v === undefined ? null : v;
    },
    setProperty: (k, v) => {
      props.__p[k] = v;
    },
    deleteProperty: (k) => {
      delete props.__p[k];
    },
  };

  const sandbox = {
    console,
    JSON,
    Math,
    Date,
    String,
    Number,
    Boolean,
    Array,
    Object,
    RegExp,
    Error,
    isNaN,
    parseInt,
    parseFloat,
    encodeURIComponent,
    decodeURIComponent,
    Logger: { log: (m) => counters.logs.push(String(m)) },
    PropertiesService: { getScriptProperties: () => props },
    SpreadsheetApp: {
      BorderStyle: { SOLID: 'SOLID', SOLID_MEDIUM: 'SOLID_MEDIUM', DASHED: 'DASHED' },
      BandingTheme: { LIGHT_GREY: 'LIGHT_GREY', BLUE: 'BLUE' },
      openById: (id) => {
        if (opts.openByIdThrows) throw new Error("stub: 開けません");
        return ss;
      },
      create: () => ss,
      newDataValidation: () => {
        const b = {
          requireValueInList: () => b,
          setAllowInvalid: () => b,
          setHelpText: () => b,
          build: () => ({}),
        };
        return b;
      },
      newConditionalFormatRule: () => {
        const b = {
          whenTextEqualTo: () => b,
          setBackground: () => b,
          setFontColor: () => b,
          setRanges: () => b,
          build: () => ({}),
        };
        return b;
      },
    },
    FormApp: {
      openById: () => {
        counters.formOpens++; // ★ 集計が走った回数（＝凍結できていない証拠）
        return { getResponses: () => [] };
      },
    },
    Session: { getScriptTimeZone: () => "Asia/Tokyo" },
    Utilities: {
      formatDate: () => "2026-08-29 00:00",
      newBlob: () => ({}),
    },
    ScriptApp: {
      getProjectTriggers: () => [],
      newTrigger: () => {
        const b = {
          forSpreadsheet: () => b,
          timeBased: () => b,
          onOpen: () => b,
          atHour: () => b,
          everyDays: () => b,
          create: () => ({}),
        };
        return b;
      },
    },
  };
  vm.createContext(sandbox);
  vm.runInContext(src, sandbox, { filename: BUILDER });
  return { sandbox, counters, ss, props };
}

// ============================================================
// ケース
// ============================================================
const cases = [];
const t = (name, got, want) =>
  cases.push({
    name,
    ok: JSON.stringify(got) === JSON.stringify(want),
    got,
    want,
  });

// ------------------------------------------------------------
// §1 phase1Frozen_ の状態表（正常 / 不在 / 壊れている の 3 状態）
// ------------------------------------------------------------
{
  const c = makeCtx({ status: "実施中", viaNamedRange: true });
  t("実施中(名前付き範囲) → 凍結しない", c.sandbox.phase1Frozen_(c.ss), false);
}
{
  const c = makeCtx({ status: "終了", viaNamedRange: true });
  t("終了(名前付き範囲) → 凍結する", c.sandbox.phase1Frozen_(c.ss), true);
}
{
  // 名前付き範囲が消えていてもタブ B2 へフォールバックすること
  const c = makeCtx({ status: "終了", viaNamedRange: false });
  t("終了(タブ B2 フォールバック) → 凍結する", c.sandbox.phase1Frozen_(c.ss), true);
}
{
  const c = makeCtx({ status: "実施中", viaNamedRange: false });
  t("実施中(タブ B2 フォールバック) → 凍結しない", c.sandbox.phase1Frozen_(c.ss), false);
}
{
  // ★ 不在: コントロール未設置＝初期段階。ここで凍結すると初回構築ができなくなる
  const c = makeCtx({ status: null });
  t("コントロール未設置(初期段階) → 凍結しない", c.sandbox.phase1Frozen_(c.ss), false);
}
{
  // ★ 壊れている: 読めないなら誤った数字を出さない側に倒す(fail-closed)
  const c = makeCtx({ statusThrows: true, viaNamedRange: true });
  t("状態セルが読めない → 凍結する(fail-closed)", c.sandbox.phase1Frozen_(c.ss), true);
}
{
  // ss を渡さない経路: 管理シート未作成なら初期段階として凍結しない
  const c = makeCtx({ noMgmtSheet: true, status: "終了", viaNamedRange: true });
  t("管理シート未作成(ss 省略) → 凍結しない", c.sandbox.phase1Frozen_(), false);
}
{
  // ss を渡さない経路: シートを開けない＝状態不明 → 凍結
  const c = makeCtx({ openByIdThrows: true, status: "終了", viaNamedRange: true });
  t("管理シートを開けない(ss 省略) → 凍結する(fail-closed)", c.sandbox.phase1Frozen_(), true);
}
{
  // ⚠️ 「終了」以外の未知の値を「終了」と誤読しないこと
  const c = makeCtx({ status: "一時停止", viaNamedRange: true });
  t("未知の状態値 → 凍結しない(終了とだけ一致する)", c.sandbox.phase1Frozen_(c.ss), false);
}
{
  // 前後の空白を落として比較していること
  const c = makeCtx({ status: "  終了  ", viaNamedRange: true });
  t("終了(前後に空白) → 凍結する", c.sandbox.phase1Frozen_(c.ss), true);
}

// ------------------------------------------------------------
// §2 ★★ 陽性対照: 実施中なら集計が**実際に走る**
//    ⚠️ これが無いと「常に何もしない実装」でも §3 が緑になる
// ------------------------------------------------------------
{
  const c = makeCtx({ status: "実施中", viaNamedRange: true });
  c.sandbox.buildDashboardTab_(c.ss);
  t("陽性対照: 実施中ならダッシュボードが集計する(FormApp を開く)", c.counters.formOpens > 0, true);
}
{
  const c = makeCtx({ status: "実施中", viaNamedRange: true });
  c.sandbox.buildReminderPlanTab_(c.ss);
  t("陽性対照: 実施中なら予定タブが集計する(FormApp を開く)", c.counters.formOpens > 0, true);
}
{
  const c = makeCtx({ status: "実施中", viaNamedRange: true });
  c.sandbox.refreshRosterStatus();
  t(
    "陽性対照: 実施中なら refreshRosterStatus がロスターへ書く",
    c.ss.__roster.__writes.length > 0,
    true
  );
}

// ------------------------------------------------------------
// §3 凍結中は集計しない（★ §2 と対で読むこと）
// ------------------------------------------------------------
{
  const c = makeCtx({ status: "終了", viaNamedRange: true });
  c.sandbox.buildDashboardTab_(c.ss);
  t("凍結: ダッシュボードはフォームを開かない", c.counters.formOpens, 0);
  t(
    "凍結: ダッシュボードは凍結タブを描く",
    c.ss.__sheets["進捗ダッシュボード"].__writes.length > 0,
    true
  );
}
{
  const c = makeCtx({ status: "終了", viaNamedRange: true });
  c.sandbox.buildReminderPlanTab_(c.ss);
  t("凍結: 予定タブはフォームを開かない", c.counters.formOpens, 0);
  t(
    "凍結: 予定タブは凍結タブを描く",
    c.ss.__sheets["本日のリマインド予定"].__writes.length > 0,
    true
  );
}
{
  const c = makeCtx({ status: "終了", viaNamedRange: true });
  c.sandbox.refreshRosterStatus();
  t(
    "⚠️★ 凍結: refreshRosterStatus はロスターへ 1 セルも書かない",
    c.ss.__roster.__writes.length,
    0
  );
  t("凍結: refreshRosterStatus はフォームを開かない", c.counters.formOpens, 0);
  t(
    "凍結: 止めたことがログに残る(黙って止まらない)",
    c.counters.logs.some((m) => m.indexOf("T-25") !== -1),
    true
  );
}
{
  // ★ 凍結表示に「誤解を生む数字」を出していないこと。
  //   ⚠️ 凍結後に出せる完了率・平均セッション数は古い値ではなく**誤った値**である。
  const c = makeCtx({ status: "終了", viaNamedRange: true });
  c.sandbox.buildDashboardTab_(c.ss);
  const text = JSON.stringify(c.ss.__sheets["進捗ダッシュボード"].__writes);
  // ⚠️★ 素の単語で探すと凍結メッセージの**説明文**に当たって偽陽性になる。
  //   → 実ダッシュボードが出す見出し（絵文字つきの実文字列）そのもので探す。
  const forbidden = [
    "🎯 目標到達率",
    "📈 総セッション数",
    "👥 登録参加者",
    "⏱ 平均セッション/人",
    "✅ NDA署名",
    "⚠ 要フォロー",
    "参加者別進捗",
  ];
  t(
    "凍結: 集計項目のラベルを 1 つも出さない",
    forbidden.filter((w) => text.indexOf(w) !== -1),
    []
  );
  t(
    "凍結: 再開の手順が書いてある",
    text.indexOf("運用コントロール") !== -1 && text.indexOf("実施中") !== -1,
    true
  );
}
{
  // ★ 状態が読めないときも凍結側へ倒れること（§1 の判定が実際の経路で効くか）
  const c = makeCtx({ statusThrows: true, viaNamedRange: true });
  c.sandbox.refreshRosterStatus();
  t(
    "状態不明: refreshRosterStatus はロスターへ書かない(fail-closed)",
    c.ss.__roster.__writes.length,
    0
  );
}

// ------------------------------------------------------------
// §4 ⚠️ 凍結はリマインダー送信の判定を置き換えていないこと
//    （送信は従来どおり reminderSendingAllowed_ が担う）
// ------------------------------------------------------------
{
  const c = makeCtx({ status: "終了", viaNamedRange: true });
  t("終了: 送信ゲートも閉じている", c.sandbox.reminderSendingAllowed_(), false);
}
{
  const c = makeCtx({ status: "実施中", viaNamedRange: true });
  t("実施中: 送信ゲートは開いている", c.sandbox.reminderSendingAllowed_(), true);
}
{
  // phase1Status_ は表示用で fail-open のまま（役割分離が壊れていないこと）
  const c = makeCtx({ statusThrows: true, viaNamedRange: true });
  t(
    "役割分離: phase1Status_ は読取失敗時も実施中を返す(fail-open)",
    c.sandbox.phase1Status_(c.ss),
    "実施中"
  );
}

// ------------------------------------------------------------
// §5 ウェブアプリ URL は**コードに焼かない**(T-29)
//    ⚠️ capability URL であり、かつ配備ごとに変わる。
// ------------------------------------------------------------
{
  // ★★ 一次資料に対する回帰ガード: ソースに実デプロイ URL が戻っていないこと。
  //   ⚠️ 実装をいくら直しても、定数として貼り直されたら意味が無い。
  const reDeploy = /https:\/\/script\.google\.com\/macros\/s\/[A-Za-z0-9_-]{30,}\/exec/;
  t("ソースに実デプロイ URL が直書きされていない", reDeploy.test(src), false);
  // 陽性対照: この正規表現が実物を実際に捕まえること（★ 捕まえないなら上の検査は空回り）
  t(
    "陽性対照: 判定器は実デプロイ URL 形を捕まえる",
    reDeploy.test(
      "https://script.google.com/macros/s/" + "A".repeat(60) + "/exec"
    ),
    true
  );
}
{
  const c = makeCtx({ status: "実施中", viaNamedRange: true });
  t(
    "URL 未設定 → ボタン URL は空(テキスト案内へ縮退)",
    c.sandbox.reminderButtonUrl_("P001", "will_do"),
    ""
  );
}
{
  const c = makeCtx({
    status: "実施中",
    viaNamedRange: true,
    props: { GSE_REMINDER_WEBAPP_URL: "https://example.invalid/exec" },
  });
  t(
    "URL 設定済み → pid / action を付けて組み立てる",
    c.sandbox.reminderButtonUrl_("P001", "will_do"),
    "https://example.invalid/exec?pid=P001&action=will_do"
  );
}
{
  const c = makeCtx({
    status: "実施中",
    viaNamedRange: true,
    props: { GSE_REMINDER_WEBAPP_URL: "  https://example.invalid/exec  " },
  });
  t(
    "URL の前後の空白を落とす",
    c.sandbox.reminderButtonUrl_("P002", "rest"),
    "https://example.invalid/exec?pid=P002&action=rest"
  );
}
{
  // プロパティが読めない状況でも例外を投げず縮退すること(メール送信を巻き添えにしない)
  const c = makeCtx({ status: "実施中", viaNamedRange: true });
  c.sandbox.PropertiesService = {
    getScriptProperties: () => {
      throw new Error("stub: プロパティを読めません");
    },
  };
  let got;
  try {
    got = c.sandbox.reminderButtonUrl_("P001", "rest");
  } catch (e) {
    got = "THREW: " + e.message;
  }
  t("プロパティ読取が失敗 → 投げずに空文字へ縮退", got, "");
}

// ============================================================
// 結果
// ============================================================
let ng = 0;
cases.forEach((c) => {
  if (!c.ok) ng++;
  console.log(
    `${c.ok ? "OK  " : "NG  "} ${c.name} → ${JSON.stringify(c.got)}${
      c.ok ? "" : ` (期待 ${JSON.stringify(c.want)})`
    }`
  );
});

// ⚠️ 「NG が 0 件なら緑」だけだと **ケースを 0 件にしても緑になる**。★ 下限を置く。
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
