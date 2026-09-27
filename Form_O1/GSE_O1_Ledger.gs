/**
 * GSE O1 (R3-a) — 受領台帳 ＋ 途絶検知（研究者だけが見る・被験者には何も送らない）
 *
 * 真実源:
 *   .steering/20260927-o1-receipt-ledger/decisions.md（★ 本ファイルを作った判断 1〜7）
 *   .steering/20260927-g1-o1-release-and-o1-resilience/t3-gas-pj-management-design.md 提案 1
 *   docs/adr/ADR-034-g1-o1-parallel-conduct.md D3 / D4（★ 「途絶」を「やめた」に変換しない）
 *
 * ============================================================================
 * ★ 何のためにあるか
 * ============================================================================
 *
 *   O1 には **自動起動 (G-1) も定期再送 (G-2) も 32 MB 超の対処 (G-5) も無い**。
 *   研究者の裁定（2026-09-27）は「今回は実装せず**運用で受ける**」。
 *   → ★ その**代替統制**が本ファイルである: **届いていない人を数日以内に研究者が知る。**
 *
 * ⚠️★★★ **言えるのは「届いたか」だけ。**
 *   アプリ未起動・回線断・32 MB 超は区別できない（対応は同じ: 被験者へ連絡）。
 * ⚠️★★★ **「途絶」「未受領」は「やめた」ではない。** 「やめた」は本人の申し出だけで決まる
 *   （ADR-034 D4 2b/2c）。★ 本ファイルは判定を**人に変換しない**。
 * ⚠️ **被験者宛てのメール・リマインドは送らない**（連絡文＝被験者向け文書＝別承認）。
 *   ★ 送るのは **研究者宛ての 1 通だけ**（宛先はスクリプト プロパティ・ソースに書かない）。
 *
 * ============================================================================
 * ⚠️★★★ **第 3 の Apps Script プロジェクトに貼る**（判断 1）
 * ============================================================================
 *
 *   ★ 受け口 (`GSE_O1_Submit.gs`) にも、ビルダー (`GSE_O1_Form_Builder.gs`) にも貼らない。
 *     理由: 受け口は稼働中の Web App、ビルダーは同意フォームのトリガーを持つ。
 *     ★ 本ファイルは Drive / Sheets / Mail / Trigger の 4 つのスコープを要するので、
 *       どちらに足しても**稼働中のものへスコープが増える**。
 *   ★ 受け口の `doPost` は**変えない**（本ファイルは Drive を**読むだけ**）。
 *
 * ============================================================================
 * 配備手順（研究者が手で行う。⚠️ ★ 自動操作しない・承認が要る）
 * ============================================================================
 *
 *   1. script.google.com で **新しいプロジェクト**を作り（例: `GSE_O1_ledger`）このファイルを貼る。
 *   2. ⚙️「スクリプト プロパティ」に 3 つ入れる（★ **`.gs` に書かない**・repo は一時 public になりうる）:
 *        | キー | 中身 |
 *        |---|---|
 *        | `O1_RECEIVE_FOLDER_ID`   | O1 の受け取りフォルダの ID（⚠️ 受け口の `FOLDER_ID` と同じ**値**。名前は変えてある） |
 *        | `O1_MGMT_SHEET_ID`       | O1 管理シートの ID（★ 登録ログのある表・ビルダーと同じ**値**） |
 *        | `O1_LEDGER_NOTIFY_EMAIL` | 通知の宛先（研究者本人）。★ 空のままなら**送らずログに残す** |
 *   3. `o1LedgerCheck()` を実行する（★ **読み取りのみ**）。⚠️ 出力を読んで確かめる:
 *        - フォルダ名が **O1 のものか**（G1 の受け取りフォルダを指していないか）
 *        - **`.age` 以外が置かれていないか**・受領日時（`getDateCreated`）と名前の日時が
 *          常識的にずれているか（判断 6 の未確認 2 点）
 *        - 走査の所要時間（判断 5 の未実測）
 *      ⚠️ **プロジェクトの設定のタイムゾーンを、ビルダーのプロジェクトと同じにする**（登録ログの日時を読むため）。
 *   3b. ⚠️★★★ **トリガーの「エラー通知設定」を「今すぐ通知」にしておく**（Apps Script の「トリガー」画面。
 *      画面の表記は要確認）。本ファイルは失敗時に研究者宛てに 1 通送るが、★ **トリガー自体が消えた・認可が切れた**
 *      ときは本ファイルは走らないので、これだけが最後の砦である。併せて、**途絶タブのバナーの「更新」時刻を
 *      ときどき見る**（★ 「通知が来ない = 異常なし」ではない）。
 *   4. `o1LedgerRun()` を 1 回手で実行する（★ 台帳と途絶のタブが**足される**・初回は現在の異常を 1 通で通知）。
 *   5. `installO1LedgerTrigger()` を実行する（6 時間ごと・★ 冪等）。
 *   6. ⚠️★★★ **関数セレクタは表示を信用しない**（押す直前に読み直す）。このプロジェクトには
 *      書き込む関数 (`o1LedgerRun` / `installO1LedgerTrigger`) と読み取りの関数が同居する。
 *
 * ⚠️★★ **`GmailApp` を使わない**（ビルダーと同じ理由）。★ OAuth スコープは静的解析で決まるので、
 *   `GmailApp` を 1 行でも書くと**受信箱の読み書き権限**を求める。使うのは `MailApp`（送信のみ）だけ。
 */

// ============================================================
// 設定
// ============================================================

/** ★ 台帳（追記のみ・行は消さない）。⚠️ O1 管理シートの**同じ表**に足す（判断 2）。 */
var O1_LEDGER_TAB = "O1 受領台帳";
/** ★ 途絶（P-ID ごとに毎回**上書き**する派生表）。 */
var O1_LEDGER_DASH_TAB = "O1 途絶";
/** ★ ビルダーが書く登録ログのタブ名（⚠️ `GSE_O1_Form_Builder.gs` の `O1_MGMT_TAB` と**同じ文字列**）。 */
var O1_LEDGER_REG_TAB = "O1 登録ログ";
/** ビルダーの `O1_MGMT_HEAD`（`GSE_O1_Form_Builder.gs`）と**同じ 6 語**。見出しの一致を確かめるのに使う。 */
var O1_LEDGER_REG_HEAD = ["記録日時", "種別", "P-ID", "結果", "理由", "備考"];

var O1_LEDGER_DAY_MS = 24 * 60 * 60 * 1000;
/** ★ 途絶 = 最終受領からこの日数（前段の裁定 2026-09-27）。猶予 48 時間 ＋ 1 日ローテート ＋ 余裕 2 日。 */
var O1_LEDGER_STALE_DAYS = 5;
/** ★ 欠番 = 欠けた番号より**後ろの番号が届いてから**この日数たっても埋まらない（★ 私の既定・判断 4）。 */
var O1_LEDGER_GAP_DAYS = 5;
/** ★ 未受領 = 登録ログの登録からこの日数たっても受領 0 件（研究者裁定 2026-09-27・判断 3）。 */
var O1_LEDGER_NEVER_DAYS = 7;
/** ★ 走査の時間予算。⚠️ Apps Script は 1 実行 6 分で止まる → 余裕を持って打ち切る（判断 5）。 */
var O1_LEDGER_TIME_BUDGET_MS = 240000;

var O1_LEDGER_FLAG_STALE = "途絶";
var O1_LEDGER_FLAG_GAP = "欠番";
var O1_LEDGER_FLAG_NEVER = "未受領";
var O1_LEDGER_FLAG_FOREIGN = "対象外の名前";

/** ⚠️★★★ **氏名・メール・URL の列は無い**（★ 増やすときも足さないこと）。 */
var O1_LEDGER_HEAD = [
  "Drive ファイル ID",
  "ファイル名",
  "P-ID",
  "日番号",
  "セッション開始(名前より)",
  "受領日時",
  "受領(epoch ms)",
  "バイト数",
  "重複",
  "形式"
];
/** 列の位置（0 始まり）。⚠️ `O1_LEDGER_HEAD` と**必ず同時に**直す（テストが突合する）。 */
var O1_LEDGER_COL = { id: 0, name: 1, pid: 2, day: 3, start: 4, received: 5, ms: 6, bytes: 7, dup: 8, kind: 9 };
var O1_LEDGER_BANNER =
  "⚠ O1 の受領台帳（研究者のみ・追記のみ）。★ 氏名・メールは持ちません。⚠ 言えるのは「届いたか」だけです。";

var O1_LEDGER_DASH_HEAD = [
  "P-ID",
  "判定",
  "最終受領",
  "経過日数",
  "受領番号数",
  "重複",
  "合計 MB",
  "欠番(日番号)",
  "登録からの日数"
];

var O1_LEDGER_KIND_OK = "O1";
var O1_LEDGER_KIND_FOREIGN = "対象外";
/**
 * ★ 削除の求めに応じた行の印（tombstone）。⚠️ **行は消さず**、P-ID・ファイル名・日番号・セッション開始の列を空にして
 *   「形式」を本値にする（`docs/o1-deletion-ledger.md` A-14）。★ Drive ファイル ID は残す（さもないと、
 *   ごみ箱に入れ損ねたファイルが次の走査で**別の行として復活**する）。集計・通知の対象外。
 */
var O1_LEDGER_KIND_ERASED = "削除済";
/** 判定の中身ではなく「台帳そのものが信用できない」ことを知らせる運用アラート（★ 判定とは別枠）。 */
var O1_LEDGER_OPS_TRUNCATED = "走査打切り";
var O1_LEDGER_OPS_REGSKIP = "登録ログの日時が読めない";
var O1_LEDGER_OPS_BADROWS = "台帳の読めない行";
/** 欠番を本文に並べる上限（★ 壊れた行で 998 件並ぶのを防ぐ）。 */
var O1_LEDGER_GAP_LIST_MAX = 10;

/** スクリプト プロパティのキー（★ 受け口の `FOLDER_ID` とは**別名**にしてある）。 */
var O1_LEDGER_PROP_FOLDER = "O1_RECEIVE_FOLDER_ID";
var O1_LEDGER_PROP_SHEET = "O1_MGMT_SHEET_ID";
var O1_LEDGER_PROP_EMAIL = "O1_LEDGER_NOTIFY_EMAIL";
var O1_LEDGER_PROP_STATE = "O1_LEDGER_STATE";
var O1_LEDGER_PROP_OPS = "O1_LEDGER_OPS";
var O1_LEDGER_PROP_OPS_LAST = "O1_LEDGER_OPS_LAST_MS";
var O1_LEDGER_PROP_FAIL = "O1_LEDGER_FAIL";
/** ★ 走査打ち切りが続く間、運用アラートを**沈黙させない**再通知の間隔（2026-09-27 レビュー指摘・判断 14）。 */
var O1_LEDGER_OPS_RENOTIFY_MS = 7 * 24 * 60 * 60 * 1000;

// ============================================================
// 純関数（★ ローカルの guard test が同じ関数を呼ぶ）
// ============================================================

/**
 * 受領ファイル名を読む。★ 通すのは **O1 の提出物の形だけ**。読めなければ null。
 *
 * ★ 形は `GSE_O1_Submit.gs` の `sanitizeName_` と**対**（テストが両方のソースを読んで突合する）:
 *   `<participant>_o1day<NN>_gse_o1_<YYYYMMDD>_<HHMMSS>[_<連番>].age`
 * ★ **重複で足された名前**（`saveWithoutOverwriting_` の `_dup-<epoch>`）も読む
 *   （⚠️ 弾くと「届いているのに O1 の形でない」と誤って数える）。
 *
 * ⚠️ 名前は被験者の端末から来る = **信用しない**。★ 通らなければ**直さず** null を返す。
 */
function o1LedgerParseName_(name) {
  var m = /^([A-Za-z0-9]{1,16})_o1day(\d{2,3})_gse_o1_(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})(?:_\d{1,10})?(_dup-\d{1,15})?\.age$/.exec(
    String(name || "")
  );
  if (!m) return null;
  return {
    pid: m[1],
    day: parseInt(m[2], 10),
    start: m[3] + "-" + m[4] + "-" + m[5] + " " + m[6] + ":" + m[7] + ":" + m[8],
    dup: !!m[9]
  };
}

/**
 * 登録ログの値から、P-ID ごとの**最古の登録日時**を求める。
 *
 * @param {Array<Array>} values  登録ログのデータ行（★ 見出しは含めない）。列は
 *   `["記録日時","種別","P-ID","結果","理由","備考"]`（ビルダーの `O1_MGMT_HEAD`）。
 * @return {{registered: Object<string, number>, skipped: number}}
 *   `skipped` = P-ID があるのに日時を読めなかった行数（★ 黙って捨てず、表に出す）。
 *
 * ★ 数えるのは `ok` / `partial`（`blocked` は却下）・種別が `system` でない行・P-ID が `P<数字>`。
 * ★ 記録日時は `yyyy-MM-dd HH:mm:ss` の文字列で書かれるが、Sheets が Date に自動変換しうる → **両方を受ける**。
 * ⚠️ 読むのは P-ID と日時だけ。氏名・メールの列は**そもそも無い**。
 */
function o1LedgerRegisteredFromLog_(values) {
  // ★ pid はファイル名由来ではなく登録ログの P-ID 欄（`/^P\d+$/` で絞っている）だが、
  //   `o1LedgerJudge_` からは `o1LedgerParseName_` 由来（英数字のみ）の pid でも引かれるため、
  //   `Object.create(null)` で `constructor` 等の辞書キー汚染を閉じる（3 回目レビュー指摘 LOW）。
  var registered = Object.create(null);
  var skipped = 0;
  for (var i = 0; i < (values || []).length; i++) {
    var row = values[i];
    var kind = String(row[1] === undefined || row[1] === null ? "" : row[1]).trim();
    var pid = String(row[2] === undefined || row[2] === null ? "" : row[2]).trim();
    var result = String(row[3] === undefined || row[3] === null ? "" : row[3]).trim();
    if (kind === "system") continue;
    if (!/^P\d+$/.test(pid)) continue;
    if (result !== "ok" && result !== "partial") continue;
    var ms = o1LedgerParseLogTime_(row[0]);
    if (ms === null) {
      skipped++;
      continue;
    }
    if (registered[pid] === undefined || ms < registered[pid]) registered[pid] = ms;
  }
  return { registered: registered, skipped: skipped };
}

/** 登録ログの日時（Date か `yyyy-MM-dd HH:mm:ss`）→ epoch ms。読めなければ null。 */
function o1LedgerParseLogTime_(v) {
  if (v instanceof Date) {
    var t = v.getTime();
    return isFinite(t) ? t : null;
  }
  var m = /^(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d{2}):(\d{2})$/.exec(String(v === undefined || v === null ? "" : v).trim());
  if (!m) return null;
  // ★ スクリプトのタイムゾーンで解く（登録ログは `Session.getScriptTimeZone()` で書かれている）。
  var d = new Date(+m[1], +m[2] - 1, +m[3], +m[4], +m[5], +m[6]);
  var ms = d.getTime();
  return isFinite(ms) ? ms : null;
}

/**
 * P-ID ごとに判定する。★ 純関数（時刻は引数で受ける）。
 *
 * @param {Array<{pid:string, day:number, receivedMs:number, bytes:number, dup:boolean}>} files
 *   ★ **O1 の形として読めたファイルだけ**（読めなかったものは呼び側が数える）。
 * @param {Object<string, number>} registered  P-ID → 最古の登録 epoch ms
 * @param {number} nowMs
 * @return {Array<Object>} P-ID の昇順。`flags` は判定の配列（空 = 正常）。
 *
 * ## 判定（★ 4 つのうちここでは 3 つ。「対象外の名前」はフォルダ全体の話なので呼び側）
 *
 *   - **途絶**: 最終受領から `O1_LEDGER_STALE_DAYS` 日以上（★ 受領が 1 本以上ある人）。
 *   - **欠番**: 日番号 `1..最大` のうち欠けた番号 d があり、★ **d より後ろの番号のいずれかが
 *     届いてから** `O1_LEDGER_GAP_DAYS` 日以上たっている。
 *       ⚠️ 番号は**暦日ではなく端末の通し番号**（`reconcile.rs` `next_o1_day_number`）。
 *         → 休んだ日は欠けない。欠けるのは「端末で作られたのに届いていない」ときだけ。
 *       ⚠️ 猶予 48 時間・再送で**順序が前後して届く**のは正常 → 届いた直後は欠番にしない。
 *   - **未受領**: 受領 0 件で、登録から `O1_LEDGER_NEVER_DAYS` 日以上。
 *
 * ⚠️ **重複（`_dup-`）は番号を増やさない**（同じ番号の再着）。ただし「最終受領」には数える
 *   （★ 何かが届いた = 端末は生きている）。
 */
function o1LedgerJudge_(files, registered, nowMs) {
  // ⚠️★★★ **P-ID を素のオブジェクトのキーにしない**（2026-09-27 レビュー指摘・Codex 実測で確定）。
  //   ★ 受け口の正規表現は英数字なら何でも通す（`constructor` 等の Object.prototype のプロパティ名も含む）ので、
  //   ⚠️ `byPid[f.pid]` が継承された関数を返し `.push` で例外になる。★ `Object.create(null)` で継承を断つ。
  var byPid = Object.create(null);
  for (var i = 0; i < files.length; i++) {
    var f = files[i];
    if (!byPid[f.pid]) byPid[f.pid] = [];
    byPid[f.pid].push(f);
  }
  var seen = Object.create(null);
  var pids = [];
  Object.keys(byPid).forEach(function (p) {
    seen[p] = true;
    pids.push(p);
  });
  Object.keys(registered || {}).forEach(function (p) {
    if (!seen[p]) pids.push(p);
  });
  pids.sort();

  return pids.map(function (pid) {
    var fs = byPid[pid] || [];
    var last = null;
    var totalBytes = 0;
    var dupCount = 0;
    var earliestByDay = {}; // ★ キーは日番号（数値）。P-ID 由来の文字列キーが来ないので素のオブジェクトで安全
    var maxDay = 0;
    fs.forEach(function (f) {
      if (last === null || f.receivedMs > last) last = f.receivedMs;
      totalBytes += f.bytes;
      if (f.dup) dupCount++;
      // ⚠️ 日番号 0（`_o1day00_`・受け口は通すが端末は作らない）は「受領」には数えるが、番号の集合には入れない
      //   （★ さもないと「届いているのに未受領」になる）。
      if (f.day >= 1) {
        if (earliestByDay[f.day] === undefined || f.receivedMs < earliestByDay[f.day]) {
          earliestByDay[f.day] = f.receivedMs;
        }
        if (f.day > maxDay) maxDay = f.day;
      }
    });

    // ★ 欠番: 大きい番号から小さい番号へ、「それより後ろの番号の最古の受領」を持ち回る。
    var gaps = [];
    var minLater = null;
    for (var d = maxDay; d >= 1; d--) {
      if (earliestByDay[d] === undefined) {
        if (minLater !== null && nowMs - minLater >= O1_LEDGER_GAP_DAYS * O1_LEDGER_DAY_MS) gaps.push(d);
      } else if (minLater === null || earliestByDay[d] < minLater) {
        minLater = earliestByDay[d];
      }
    }
    gaps.reverse();

    var elapsedDays = last === null ? null : Math.max(0, Math.floor((nowMs - last) / O1_LEDGER_DAY_MS));
    var regMs = registered && registered[pid] !== undefined ? registered[pid] : null;
    var sinceRegDays = regMs === null ? null : Math.max(0, Math.floor((nowMs - regMs) / O1_LEDGER_DAY_MS));

    var flags = [];
    if (last !== null && nowMs - last >= O1_LEDGER_STALE_DAYS * O1_LEDGER_DAY_MS) {
      flags.push(O1_LEDGER_FLAG_STALE);
    }
    if (gaps.length > 0) flags.push(O1_LEDGER_FLAG_GAP);
    if (fs.length === 0 && regMs !== null && nowMs - regMs >= O1_LEDGER_NEVER_DAYS * O1_LEDGER_DAY_MS) {
      flags.push(O1_LEDGER_FLAG_NEVER);
    }

    return {
      pid: pid,
      files: fs.length,
      uniqueDays: Object.keys(earliestByDay).length,
      dupCount: dupCount,
      totalBytes: totalBytes,
      lastReceivedMs: last,
      elapsedDays: elapsedDays,
      registeredMs: regMs,
      sinceRegDays: sinceRegDays,
      gaps: gaps,
      flags: flags
    };
  });
}

/**
 * 通知の要否を決める。★ 純関数。
 *
 * ★ **悪化方向に変わったときだけ 1 回**: 前回の状態に無かった判定が加わった P-ID を返す。
 *   ⚠️ 復帰（異常 → 正常）では送らない（★ ただし次の状態には反映する → 再び異常になれば送る）。
 *   ⚠️ 異常が**続いている**だけでは送らない（毎回送ると読まれなくなる）。
 *
 * ⚠️★★★ **「同じ判定のまま中身が悪化した」も悪化に数える**（2026-09-27 レビュー指摘 3 本が独立に一致）:
 *   - **欠番**: 新しい欠番の番号が**増えた**とき（旗が既に立っていても）。減った・入れ替わらずに縮んだだけなら送らない。
 *   - **対象外の名前**: 件数が**増えた**とき。★ 台帳は追記のみで件数は減らないので、旗だけを見ると
 *     **最初の 1 回しか通知されず、以後の G1 の混入を検知できない**。
 *
 * @param {Object<string,string>|null} prev  前回の状態（P-ID → `旗[:詳細]` の `,` 区切り）。null = 初回。
 *   詳細 = 欠番なら番号の `|` 区切り／対象外の名前なら件数。
 * @param {Array<Object>} rows  `o1LedgerJudge_` の戻り
 * @param {number} foreignCount  O1 の形でないファイルの数（★ P-ID に属さない・キーは `*`）
 * @return {{alerts: Array<{key:string, added:string[]}>, next: Object<string,string>}}
 */
function o1LedgerAlerts_(prev, rows, foreignCount) {
  var before = prev || {};
  var next = {}; // ★ 書き込み専用（読み取りが無い）。P-ID が Object.prototype 名でも代入は安全
  var alerts = [];
  var consider = function (key, entries) {
    next[key] = entries
      .map(function (e) {
        return e.flag + (e.detail ? ":" + e.detail : "");
      })
      .join(",");
    var was = {}; // ★ キーは固定の旗名（途絶/欠番/未受領/対象外の名前）で P-ID 由来ではない
    (before[key] ? String(before[key]).split(",") : []).forEach(function (tok) {
      var i = tok.indexOf(":");
      was[i < 0 ? tok : tok.slice(0, i)] = i < 0 ? "" : tok.slice(i + 1);
    });
    var added = entries
      .filter(function (e) {
        if (was[e.flag] === undefined) return true;
        if (e.flag === O1_LEDGER_FLAG_GAP) {
          var old = was[e.flag] ? was[e.flag].split("|") : [];
          return e.detail.split("|").some(function (n) {
            return old.indexOf(n) < 0;
          });
        }
        if (e.flag === O1_LEDGER_FLAG_FOREIGN) return Number(e.detail) > Number(was[e.flag] || 0);
        return false;
      })
      .map(function (e) {
        return e.flag;
      });
    if (added.length > 0) alerts.push({ key: key, added: added });
  };
  rows.forEach(function (r) {
    consider(
      r.pid,
      r.flags.map(function (f) {
        return { flag: f, detail: f === O1_LEDGER_FLAG_GAP ? (r.gaps || []).join("|") : "" };
      })
    );
  });
  consider("*", foreignCount > 0 ? [{ flag: O1_LEDGER_FLAG_FOREIGN, detail: String(foreignCount) }] : []);
  return { alerts: alerts, next: next };
}

/**
 * 運用アラート（台帳そのものが信用できない）の要否。★ 純関数。
 *   `ops` = { truncated: boolean, regSkipped: number, badRows: number }
 * ★ 有効になった（前回は無かった）ものだけ返す。解消したら次の状態から消える（再発すれば再通知）。
 */
function o1LedgerOpsAlerts_(prevOps, ops) {
  var before = prevOps || {};
  var active = {}; // ★ キーは固定の運用アラート名で P-ID 由来ではない
  if (ops.truncated) active[O1_LEDGER_OPS_TRUNCATED] = true;
  if (ops.regSkipped > 0) active[O1_LEDGER_OPS_REGSKIP] = true;
  if (ops.badRows > 0) active[O1_LEDGER_OPS_BADROWS] = true;
  var added = Object.keys(active).filter(function (k) {
    return !before[k];
  });
  return { added: added, next: active };
}

/** 欠番の番号を本文に並べる。★ 上限を超えたら「他 N 件」に丸める。 */
function o1LedgerListGaps_(gaps) {
  var shown = gaps.slice(0, O1_LEDGER_GAP_LIST_MAX).join(", ");
  return gaps.length > O1_LEDGER_GAP_LIST_MAX ? shown + " …他 " + (gaps.length - O1_LEDGER_GAP_LIST_MAX) + " 件" : shown;
}

/**
 * 文字列セルに書く前の無害化。★ 先頭が `=` `+` `-` `@` `\t` `\r` なら見えるマークを前置する。
 * ⚠️ **表示形式（`@`）に頼らない**（`Range.setValues` が形式で数式解釈を必ず止めるかは、公式に保証されていない）。
 *   ★ ファイル名は被験者の端末由来で、フォルダには研究者も置ける = 信用しない。二重に守る（形式＋本関数）。
 */
function o1LedgerSafeCell_(v) {
  if (typeof v !== "string") return v;
  return /^[=+\-@\t\r]/.test(v) ? "⚠" + v : v;
}

/**
 * 通知メールの本文。⚠️ **P-ID・判定・日数だけ**（★ シートの URL・Drive の ID・ファイル名は載せない）。
 * ⚠️ 「やめた」とは書かない（★ 判定は届いたかの話・ADR-034 D4 2b）。
 */
function o1LedgerMailText_(alerts, rows, foreignCount, opsAdded, opsOnly) {
  var byPid = {};
  rows.forEach(function (r) {
    byPid[r.pid] = r;
  });
  var lines = [];
  alerts.forEach(function (a) {
    if (a.key === "*") {
      lines.push(
        "- （フォルダ全体）O1 の形でないファイルが " + foreignCount + " 件あります。G1 の提出物の混入か、手で置かれたファイルの可能性があります。"
      );
      return;
    }
    var r = byPid[a.key];
    var parts = a.added.map(function (flag) {
      if (flag === O1_LEDGER_FLAG_STALE) return "途絶（最終受領から " + r.elapsedDays + " 日）";
      if (flag === O1_LEDGER_FLAG_GAP) return "欠番（日番号 " + o1LedgerListGaps_(r.gaps) + "）";
      if (flag === O1_LEDGER_FLAG_NEVER) return "未受領（登録から " + r.sinceRegDays + " 日・受領 0 件）";
      return flag;
    });
    lines.push("- " + a.key + ": " + parts.join(" / "));
  });
  var opsText = {};
  opsText[O1_LEDGER_OPS_TRUNCATED] = "走査が時間予算で打ち切られました（★ 判定の通知は保留し、次回に持ち越します）。";
  opsText[O1_LEDGER_OPS_REGSKIP] = "登録ログに日時を読めない行があります（★ その人の「未受領」を判定できません）。";
  opsText[O1_LEDGER_OPS_BADROWS] = "台帳に読めない行があります。";
  (opsAdded || []).forEach(function (k) {
    lines.push("- （運用）" + (opsText[k] || k));
  });
  var heading = opsOnly
    ? "O1 受領台帳: 台帳の運用に要確認があります（★ P-ID の異常ではありません）。"
    : "O1 受領台帳: 新しく要確認になったものがあります。";
  return (
    heading + "\n\n" +
    lines.join("\n") +
    "\n\n※ 分かるのは「届いたか」だけです（アプリ未起動・回線断・32 MB 超は区別できません）。" +
    "\n※ 「途絶」「未受領」は「やめた」ではありません。本人へ連絡して確かめてください。" +
    "\n※ 詳細は O1 管理シートの「" + O1_LEDGER_DASH_TAB + "」タブを見てください。\n"
  );
}

/**
 * スクリプト プロパティ（の値の連想配列）から設定の問題を返す。空配列なら問題なし。
 * ⚠️ 宛先の**不在は問題にしない**（★ 送らずにログへ出す = fail-closed。台帳自体は動かす）。
 */
function o1LedgerConfigProblems_(cfg) {
  var problems = [];
  if (!cfg.folderId) problems.push("スクリプト プロパティ " + O1_LEDGER_PROP_FOLDER + " が未設定");
  if (!cfg.sheetId) problems.push("スクリプト プロパティ " + O1_LEDGER_PROP_SHEET + " が未設定");
  if (cfg.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(cfg.email)) {
    problems.push(O1_LEDGER_PROP_EMAIL + " がメールアドレスの形ではない（★ 値は表示しない）");
  }
  return problems;
}

// ============================================================
// GAS 側（★ Drive は読むだけ・Sheets は自分のタブにだけ書く）
// ============================================================

function o1LedgerConfig_() {
  var props = PropertiesService.getScriptProperties();
  return {
    folderId: String(props.getProperty(O1_LEDGER_PROP_FOLDER) || "").trim(),
    sheetId: String(props.getProperty(O1_LEDGER_PROP_SHEET) || "").trim(),
    email: String(props.getProperty(O1_LEDGER_PROP_EMAIL) || "").trim()
  };
}

/**
 * O1 管理シートを開く。⚠️★★★ **「参加者ロスター」タブを持つ表なら書かずに止まる**
 * （ビルダーの `o1OpenMgmtLog_` と同じ歯止め・★ 2 か所採番の芽を作らない）。
 */
function o1LedgerOpenSheet_(cfg) {
  var ss = SpreadsheetApp.openById(cfg.sheetId);
  if (ss.getSheetByName("参加者ロスター")) {
    throw new Error(
      "⛔⚠️★★★ " + O1_LEDGER_PROP_SHEET + " の表に「参加者ロスター」タブがあります。★ 何も書いていません。" +
        "O1 の管理シート（ロスターを持たない表）を指してください。"
    );
  }
  return ss;
}

/** 台帳タブを用意する（★ 冪等・⚠️ 既存の行を消さない）。 */
function o1LedgerEnsureTab_(ss, tab, banner, head) {
  var sheet = ss.getSheetByName(tab);
  if (!sheet) sheet = ss.insertSheet(tab);
  if (sheet.getLastRow() === 0) {
    sheet.appendRow([banner]);
    sheet.appendRow(head.slice());
  } else if (sheet.getLastRow() < 2) {
    throw new Error("⛔⚠️ 「" + tab + "」に見出し行（2 行目）がありません。★ 中身があるので自動では直しません。");
  }
  return sheet;
}

/** 行が足りなければ足す（⚠️ `setValues` は範囲外へ書くと例外になる）。 */
function o1LedgerEnsureRows_(sheet, lastRowNeeded) {
  var max = sheet.getMaxRows();
  if (max < lastRowNeeded) sheet.insertRowsAfter(max, lastRowNeeded - max);
}

function o1LedgerFmt_(ms) {
  return Utilities.formatDate(new Date(ms), Session.getScriptTimeZone(), "yyyy-MM-dd HH:mm:ss");
}

/**
 * ★ 1 回の実行（時間トリガーの実体）: 走査 → 途絶の再計算 → 通知。
 * ⚠️ 同時に 2 本走らせない（★ 手動実行とトリガーが重なると台帳に重複行が入る）。
 */
function o1LedgerRun() {
  var lock = LockService.getScriptLock();
  if (!lock.tryLock(30000)) {
    console.log("⚠️ 別の実行が動いているので今回は何もしませんでした。");
    return;
  }
  try {
    var cfg = o1LedgerConfig_();
    var problems = o1LedgerConfigProblems_(cfg);
    if (problems.length) throw new Error("❌ 設定が揃っていません: " + problems.join(" / "));
    var ss = o1LedgerOpenSheet_(cfg);
    var scan = o1LedgerSync_(cfg, ss);
    var result = o1LedgerDashboard_(cfg, ss, scan);
    o1LedgerNotify_(cfg, result);
    PropertiesService.getScriptProperties().deleteProperty(O1_LEDGER_PROP_FAIL); // 成功した = 失敗の解消
  } catch (e) {
    o1LedgerNotifyFailure_(e); // ⚠️ 検知器の沈黙を外へ出す。例外は握りつぶさず再送出する。
    throw e;
  } finally {
    lock.releaseLock();
  }
}

/**
 * Drive の受領フォルダを走査し、**新しいファイルだけ**台帳へ追記する。
 * ★ Drive ファイル ID で冪等（何度回しても行が増えない）。⚠️ 行は消さない。
 * ★ ⚠️ 走査は**全走査**（Drive の ID は時刻順である保証がない・判断 5）。時間予算で打ち切る。
 */
function o1LedgerSync_(cfg, ss) {
  var sheet = o1LedgerEnsureTab_(ss, O1_LEDGER_TAB, O1_LEDGER_BANNER, O1_LEDGER_HEAD);
  var known = {};
  var last = sheet.getLastRow();
  if (last >= 3) {
    var ids = sheet.getRange(3, O1_LEDGER_COL.id + 1, last - 2, 1).getValues();
    for (var i = 0; i < ids.length; i++) known[String(ids[i][0])] = true;
  }

  var folder = DriveApp.getFolderById(cfg.folderId);
  var it = folder.getFiles();
  var t0 = new Date().getTime();
  var truncated = false;
  var rows = [];
  while (it.hasNext()) {
    if (new Date().getTime() - t0 > O1_LEDGER_TIME_BUDGET_MS) {
      truncated = true;
      break;
    }
    var f = it.next();
    var id = f.getId();
    if (known[id]) continue;
    if (f.isTrashed()) continue; // ★ ごみ箱の中は受領に数えない（台帳に既にあるものは残る）
    var name = f.getName();
    var parsed = o1LedgerParseName_(name);
    var created = f.getDateCreated().getTime();
    // ⚠️★★★ **Drive ファイル ID には無害化を掛けない**（2026-09-27 レビュー指摘 HIGH）。
    //   ★ ID は Drive 由来で被験者端末由来ではなく、先頭に `-` が来ると `⚠-` が前置され、
    //   ⚠️ 次回の走査が生の ID で `known[id]` を引くため**一致せず、同じファイルが毎回別行として増殖する**
    //   （＝冪等性が壊れる）。★ 無害化が要るのはファイル名など被験者端末由来の列だけ。
    var row = [
      id,
      name,
      parsed ? parsed.pid : "",
      parsed ? parsed.day : "",
      parsed ? parsed.start : "",
      o1LedgerFmt_(created),
      created,
      f.getSize(),
      parsed && parsed.dup ? "dup" : "",
      parsed ? O1_LEDGER_KIND_OK : O1_LEDGER_KIND_FOREIGN
    ];
    for (var ci = 1; ci < row.length; ci++) row[ci] = o1LedgerSafeCell_(row[ci]); // 0 列目（ID）は除く
    rows.push(row);
  }

  if (rows.length > 0) {
    var start = sheet.getLastRow() + 1;
    o1LedgerEnsureRows_(sheet, start + rows.length - 1);
    // ⚠️★★ **文字列の列はテキスト形式で書く**（★ 数式注入を避ける・判断 7）。
    //   ID・ファイル名・P-ID・開始・受領日時・重複・形式が対象。数値列（日番号・epoch・バイト）は既定の形式のまま。
    [O1_LEDGER_COL.id, O1_LEDGER_COL.name, O1_LEDGER_COL.pid, O1_LEDGER_COL.start,
      O1_LEDGER_COL.received, O1_LEDGER_COL.dup, O1_LEDGER_COL.kind].forEach(function (c) {
      sheet.getRange(start, c + 1, rows.length, 1).setNumberFormat("@");
    });
    sheet.getRange(start, 1, rows.length, O1_LEDGER_HEAD.length).setValues(rows);
  }
  console.log("台帳: 追記 " + rows.length + " 件" + (truncated ? "（⚠️ 時間予算で打ち切り・次回へ持ち越し）" : ""));
  return { added: rows.length, truncated: truncated };
}

/**
 * 台帳を読み直して P-ID ごとに判定し、「O1 途絶」タブを**上書き**する（★ 派生表なので上書きでよい）。
 * @return {{rows: Array<Object>, foreignCount: number}}
 */
function o1LedgerDashboard_(cfg, ss, scan) {
  var ledger = o1LedgerEnsureTab_(ss, O1_LEDGER_TAB, O1_LEDGER_BANNER, O1_LEDGER_HEAD);
  var last = ledger.getLastRow();
  var files = [];
  var foreignCount = 0;
  var badRows = 0;
  if (last >= 3) {
    var values = ledger.getRange(3, 1, last - 2, O1_LEDGER_HEAD.length).getValues();
    values.forEach(function (v) {
      if (String(v[O1_LEDGER_COL.kind]) === O1_LEDGER_KIND_ERASED) return; // ★ 削除済み（tombstone）は数えない
      if (String(v[O1_LEDGER_COL.kind]) === O1_LEDGER_KIND_FOREIGN) {
        foreignCount++;
        return;
      }
      // ⚠️★★★ **`Number("")` は `0` になる**ので、空セルの日番号が「day 0 の受領」に化けていた
      //   （2026-09-27 レビュー指摘 MEDIUM）。★ 形を先に見る（空・小数・負号を弾く）。
      var dayRaw = String(v[O1_LEDGER_COL.day] === undefined || v[O1_LEDGER_COL.day] === null ? "" : v[O1_LEDGER_COL.day]).trim();
      var ms = Number(v[O1_LEDGER_COL.ms]);
      var bytes = Number(v[O1_LEDGER_COL.bytes]);
      var pid = String(v[O1_LEDGER_COL.pid] || "");
      var day = Number(dayRaw);
      // ⚠️★★★ **`Number.isSafeInteger` を戻す**（2026-09-27 3 回目レビュー指摘 HIGH・Codex 発見）。
      //   ★ 判断 17（`Number("")===0` の穴を塞ぐ）で `!isFinite(day)` を落としたため、
      //   ⚠️ 桁あふれの数字文字列（例: 400 桁）が `Number()` で `Infinity` になっても
      //   `/^\d+$/` は**素通りしてしまい**、`maxDay = Infinity` が判定ループ
      //   （`for (var d = maxDay; d >= 1; d--)`）を**実質無限**にしていた（GAS のタイムアウトまで
      //   ハングし、その回の途絶判定・通知が丸ごと欠落する）。★ `/^\d+$/` の形検査に加え、
      //   `Number.isSafeInteger` で有限・整数であることも見る（2 つを併置する・判断 16 と同じ流儀）。
      if (!pid || !isFinite(ms) || !/^\d+$/.test(dayRaw) || !Number.isSafeInteger(day) || !isFinite(bytes)) {
        badRows++;
        return;
      }
      files.push({ pid: pid, day: day, receivedMs: ms, bytes: bytes, dup: String(v[O1_LEDGER_COL.dup]) === "dup" });
    });
  }

  // ★ 登録ログ（未受領の判定に使う）。⚠️ 読めないときは**止める**（黙って未受領の判定を落とさない）。
  var reg = ss.getSheetByName(O1_LEDGER_REG_TAB);
  if (!reg) {
    throw new Error(
      "❌ 「" + O1_LEDGER_REG_TAB + "」タブがありません。★ 登録ログが無いと「未受領」を判定できません" +
        "（ビルダー側で buildO1MgmtSheet() を実行済みか確かめてください）。"
    );
  }
  // ⚠️★★★ 列数だけでなく**見出しの中身**を見る（2026-09-27 レビュー指摘 MEDIUM）。
  //   ★ 列数だけの検査は「列を 1 本挿入されて中身がずれた」を見逃す
  //   （P-ID 列が「種別」になり、登録の突合が**黙って**全員 0 件になる）。★ ビルダー側と同じ流儀。
  if (reg.getMaxColumns() < O1_LEDGER_REG_HEAD.length) {
    throw new Error(
      "❌ 「" + O1_LEDGER_REG_TAB + "」タブの列が " + O1_LEDGER_REG_HEAD.length + " 列に足りません（★ 現在 " +
        reg.getMaxColumns() + " 列）。"
    );
  }
  // ⚠️★★★ **見出し行が無ければ止める**（2026-09-27 3 回目レビュー指摘 MEDIUM・自己後退の修正）。
  //   ★ 直前まで「`reg.getLastRow() >= 2` のときだけ見出しを見る」だったため、
  //   **タブはあるが空**（研究者が手で作った・`clearContents` した等）だと見出し検査ごと**スキップ**され、
  //   ⚠️ `regValues` も空のまま完走し、**「未受領」の判定が全員ぶん無音で失われる**（実測で再現・確定）。
  //   ★ ビルダーが作った正常なタブは必ず `lastRow >= 2`（バナー行＋見出し行）なので、
  //   `< 2` を「見出しが無い」として弾く（黙って未受領の判定を落とさない、という本関数冒頭の約束と同じ）。
  if (reg.getLastRow() < 2) {
    throw new Error(
      "❌ 「" + O1_LEDGER_REG_TAB + "」タブに見出し行がありません（★ 行数 " + reg.getLastRow() +
        "）。★ buildO1MgmtSheet() を実行済みか確かめてください。"
    );
  }
  var regHead = reg.getRange(2, 1, 1, O1_LEDGER_REG_HEAD.length).getValues()[0];
  for (var hc = 0; hc < O1_LEDGER_REG_HEAD.length; hc++) {
    if (String(regHead[hc]).trim() !== O1_LEDGER_REG_HEAD[hc]) {
      throw new Error(
        "❌ 「" + O1_LEDGER_REG_TAB + "」の見出しの " + (hc + 1) + " 列目が「" + String(regHead[hc]).slice(0, 20) +
          "」です（★「" + O1_LEDGER_REG_HEAD[hc] + "」のはず・ビルダーの O1_MGMT_HEAD と食い違っています）。"
      );
    }
  }
  var regLast = reg.getLastRow();
  var regValues = regLast >= 3 ? reg.getRange(3, 1, regLast - 2, 6).getValues() : [];
  var regInfo = o1LedgerRegisteredFromLog_(regValues);

  var nowMs = new Date().getTime();
  var rows = o1LedgerJudge_(files, regInfo.registered, nowMs);

  var dash = ss.getSheetByName(O1_LEDGER_DASH_TAB) || ss.insertSheet(O1_LEDGER_DASH_TAB);
  dash.clearContents();
  var banner =
    "⚠ 派生表（毎回上書き・研究者のみ）。更新 " + o1LedgerFmt_(nowMs) +
    " ／ 走査 " + (scan && scan.truncated ? "⚠️打ち切り（次回へ持ち越し）" : "完了") +
    " ／ 対象外の名前 " + foreignCount + " 件" +
    (badRows ? " ／ ⚠️台帳の読めない行 " + badRows : "") +
    (regInfo.skipped ? " ／ ⚠️登録ログの日時が読めない行 " + regInfo.skipped : "") +
    " ／ ★ 言えるのは「届いたか」だけ・「やめた」ではない ／ 表示専用（全て文字列）";
  var out = [[banner], O1_LEDGER_DASH_HEAD.slice()];
  var width = O1_LEDGER_DASH_HEAD.length;
  rows.forEach(function (r) {
    out.push([
      r.pid,
      r.flags.length ? r.flags.join("・") : "正常",
      r.lastReceivedMs === null ? "" : o1LedgerFmt_(r.lastReceivedMs),
      r.elapsedDays === null ? "" : r.elapsedDays,
      r.uniqueDays,
      r.dupCount,
      Math.round((r.totalBytes / (1024 * 1024)) * 100) / 100,
      r.gaps.join(", "),
      r.sinceRegDays === null ? "" : r.sinceRegDays
    ]);
  });
  out = out.map(function (r) {
    var padded = r.slice();
    while (padded.length < width) padded.push("");
    return padded.map(function (c) {
      // ⚠️★ **台帳と同じ無害化を通す**（security-checker L-1 指摘・2026-09-27）。
      //   ★ ここは `pid` / 数値の整形結果が主だが、研究者の手編集（tombstone 作業中の半端な値等）で
      //   先頭が `=` 等になりうる。テキスト形式（下の `setNumberFormat("@")`）だけに頼らない。
      return o1LedgerSafeCell_(String(c));
    });
  });
  o1LedgerEnsureRows_(dash, out.length);
  var range = dash.getRange(1, 1, out.length, width);
  range.setNumberFormat("@"); // ★ 表示専用。すべて文字列で書く（数式注入を避ける）。
  range.setValues(out);
  console.log("途絶: " + rows.length + " 人・判定あり " + rows.filter(function (r) { return r.flags.length; }).length + " 人");
  return {
    rows: rows,
    foreignCount: foreignCount,
    ops: { truncated: !!(scan && scan.truncated), regSkipped: regInfo.skipped, badRows: badRows }
  };
}

/** スクリプト プロパティの JSON を読む。壊れていたら null（= 初回扱い・現在の異常を 1 回通知し直す）。 */
function o1LedgerReadJson_(props, key) {
  try {
    var raw = props.getProperty(key);
    return raw ? JSON.parse(raw) : null;
  } catch (e) {
    return null;
  }
}

/**
 * 悪化方向に変わったときだけ、研究者宛てに 1 通送る。
 * ⚠️★ **宛先が未設定・送信に失敗したときは「通知済み」にしない**（★ 設定後 / 次回に 1 通届く）。
 * ⚠️★★★ **走査が打ち切られた回は、判定の通知を保留する**（状態も更新しない）。
 *   ★ 台帳が部分的なまま判定すると、届いている人を「途絶」「未受領」と誤報し、
 *     しかも**復帰では通知しない**ので、誤報が訂正されない（2026-09-27 レビュー指摘）。
 *   → 代わりに「走査が打ち切られた」という**運用アラート**を 1 回だけ出す（★ 沈黙させない）。
 */
function o1LedgerNotify_(cfg, result) {
  var props = PropertiesService.getScriptProperties();
  var prev = o1LedgerReadJson_(props, O1_LEDGER_PROP_STATE);
  var prevOps = o1LedgerReadJson_(props, O1_LEDGER_PROP_OPS);
  var reliable = !result.ops.truncated;
  var plan = o1LedgerAlerts_(prev, result.rows, result.foreignCount);
  var alerts = reliable ? plan.alerts : [];
  var opsPlan = o1LedgerOpsAlerts_(prevOps, result.ops);

  // ⚠️★★★ **打ち切りが続く間、運用アラートを沈黙させない**（2026-09-27 レビュー指摘・両系統一致）。
  //   ★ `o1LedgerOpsAlerts_` は「前回無かったものだけ」返すので、原因が変わらない限り 2 回目以降は
  //   `added` が空になる。⚠️ そのままだと、フォルダが育って打ち切りが恒常化したとき**最初の 1 通で
  //   通知が永久に止まる**（＝台帳が「代替統制」の役目を果たさなくなる）。
  //   → ★ アクティブなアラートが 1 つでも残っている間、`O1_LEDGER_OPS_RENOTIFY_MS` ごとに**全件**を
  //   まとめて再送する（新規分だけでなく、続いているものも含める＝研究者は最新の全体像を見られる）。
  var nowForOps = new Date().getTime();
  var opsStillActive = Object.keys(opsPlan.next).length > 0;
  var lastOpsMs = Number(props.getProperty(O1_LEDGER_PROP_OPS_LAST) || 0);
  var opsDue = opsPlan.added.length === 0 && opsStillActive && nowForOps - lastOpsMs >= O1_LEDGER_OPS_RENOTIFY_MS;
  var opsToSend = opsDue ? Object.keys(opsPlan.next) : opsPlan.added;

  var persist = function () {
    if (reliable) props.setProperty(O1_LEDGER_PROP_STATE, JSON.stringify(plan.next));
    props.setProperty(O1_LEDGER_PROP_OPS, JSON.stringify(opsPlan.next));
    if (opsToSend.length > 0) props.setProperty(O1_LEDGER_PROP_OPS_LAST, String(nowForOps));
  };
  if (alerts.length === 0 && opsToSend.length === 0) {
    persist();
    return;
  }
  var body = o1LedgerMailText_(alerts, result.rows, result.foreignCount, opsToSend, alerts.length === 0);
  if (!cfg.email) {
    console.log("⚠️ " + O1_LEDGER_PROP_EMAIL + " が未設定なので通知を送っていません（★ 設定後の次回に 1 通届きます）:\n" + body);
    return;
  }
  try {
    MailApp.sendEmail(
      cfg.email,
      "[GSE O1] 受領台帳: " + (alerts.length === 0 ? "運用アラート " + opsToSend.length : "要確認 " + (alerts.length + opsToSend.length)) + " 件",
      body
    );
  } catch (err) {
    console.log("⚠️ 通知メールの送信に失敗しました（★ 通知済みにしていません・次回に再送）: " + err);
    return;
  }
  persist();
  console.log("✉️ 研究者宛てに通知しました（" + (alerts.length + opsToSend.length) + " 件）。");
}

/**
 * 実行そのものが失敗したとき、研究者宛てに 1 通送る（★ 同じ原因では 1 回だけ・成功すると解消）。
 * ⚠️★★★ **検知器が黙って死ぬと「通知が来ない = 異常なし」と読まれる**（2026-09-27 レビュー指摘）。
 *   ★ 登録ログのタブ名変更・シート ID の失効・ロスターのタブ混入・設定欠落などで `o1LedgerRun` が例外になると、
 *     途絶タブの更新も通知も止まる。→ 失敗を**外へ出す**。⚠️ 本文に ID・URL を載せない（長い英数字は伏せる）。
 * ⚠️ 例外は握りつぶさず、呼び側が再送出する（★ Apps Script の実行ログにも失敗が残る）。
 */
function o1LedgerNotifyFailure_(err) {
  try {
    var props = PropertiesService.getScriptProperties();
    var email = String(props.getProperty(O1_LEDGER_PROP_EMAIL) || "").trim();
    if (!email) {
      // ⚠️★ 宛先未設定の分岐だけログが無かった（security-checker L-3 指摘）。★ 本文・原因文字列は出さない。
      console.log("⚠️ " + O1_LEDGER_PROP_EMAIL + " が未設定なので実行失敗の通知を送っていません。");
      return;
    }
    var msg = String(err && err.message ? err.message : err)
      .replace(/https?:\/\/\S+/g, "<URL>")
      .replace(/[0-9A-Za-z_-]{25,}/g, "<ID>")
      .slice(0, 300);
    if (props.getProperty(O1_LEDGER_PROP_FAIL) === msg) return; // 同じ原因では再送しない
    MailApp.sendEmail(
      email,
      "[GSE O1] 受領台帳: 実行が失敗しました",
      "O1 受領台帳の実行が失敗しました。★ このあいだ、途絶の判定と通知は止まっています。\n\n原因: " + msg +
        "\n\n※ 原因が直るまで、同じ原因では再送しません。直ると自動で解消します。\n"
    );
    props.setProperty(O1_LEDGER_PROP_FAIL, msg);
  } catch (e2) {
    console.log("⚠️ 失敗の通知も送れませんでした: " + e2);
  }
}

// ============================================================
// 研究者が手で走らせる関数
// ============================================================

/**
 * 6 時間ごとの時間トリガーを 1 つだけ置く。★ 冪等（既存の同じ関数のトリガーを消してから置く）。
 * ⚠️ 他のトリガーは触らない。
 */
function installO1LedgerTrigger() {
  var triggers = ScriptApp.getProjectTriggers();
  for (var i = 0; i < triggers.length; i++) {
    if (triggers[i].getHandlerFunction() === "o1LedgerRun") ScriptApp.deleteTrigger(triggers[i]);
  }
  ScriptApp.newTrigger("o1LedgerRun").timeBased().everyHours(6).create();
  console.log("✅ o1LedgerRun を 6 時間ごとに設置しました。");
}

/**
 * ★ **読み取りのみ**の点検（配備時に 1 回・判断 5/6 の未確認を実フォルダで確かめる）。
 * ⚠️ 何も書かない・メールも送らない。
 */
function o1LedgerCheck() {
  var cfg = o1LedgerConfig_();
  var problems = o1LedgerConfigProblems_(cfg);
  if (problems.length) throw new Error("❌ " + problems.join(" / "));
  var folder = DriveApp.getFolderById(cfg.folderId);
  console.log("受け取りフォルダ: " + folder.getName() + "  ★ O1 のものか確かめること（G1 のフォルダを指していないか）");
  console.log(cfg.email ? "通知先: 設定あり" : "⚠️ 通知先が未設定（送らずログに出します）");
  // ⚠️ 登録ログの日時は「ビルダーのプロジェクトのタイムゾーン」で書かれ、本プロジェクトの設定で読む。
  //   ★ ずれると「未受領」の 7 日が数時間ずれる。→ ビルダーと**同じ**（Asia/Tokyo 等）にすること。
  console.log("このプロジェクトのタイムゾーン: " + Session.getScriptTimeZone() + "（★ ビルダーのプロジェクトと同じか確かめること）");

  var t0 = new Date().getTime();
  var it = folder.getFiles();
  var ok = 0;
  var foreignCount = 0;
  var foreign = [];
  var samples = [];
  var truncated = false;
  while (it.hasNext()) {
    // ⚠️ 本関数も時間予算を持つ（★ 走査時間を測る関数が 6 分制限で死ぬと「測れなかった」しか分からない）。
    if (new Date().getTime() - t0 > O1_LEDGER_TIME_BUDGET_MS) {
      truncated = true;
      break;
    }
    var f = it.next();
    var name = f.getName();
    var parsed = o1LedgerParseName_(name);
    if (parsed) {
      ok++;
      if (samples.length < 5) {
        samples.push(name + " → 名前の開始 " + parsed.start + " / 受領(作成) " + o1LedgerFmt_(f.getDateCreated().getTime()));
      }
    } else {
      foreignCount++;
      if (foreign.length < 20) foreign.push(name + " (" + f.getSize() + " B)");
    }
  }
  var elapsed = new Date().getTime() - t0;
  console.log(
    "O1 の形: " + ok + " 件 ／ 対象外: " + foreignCount + " 件（表示は 20 まで）" +
      (truncated ? " ／ ⚠️ 時間予算で打ち切り（★ ここまでの件数と経過であり、フォルダ全体ではない）" : "")
  );
  foreign.forEach(function (n) {
    console.log("  対象外: " + n);
  });
  samples.forEach(function (s) {
    console.log("  例: " + s);
  });
  console.log("走査の所要: " + elapsed + " ms（★ 時間予算 " + O1_LEDGER_TIME_BUDGET_MS + " ms・判断 5 の実測値として記録すること）");
  console.log("⚠️ 受領(作成)が名前の開始日時より**前**なら、getDateCreated を受領時刻とみなせない（判断 6）。");
  console.log("⚠️ 上の「対象外」の名前には P-ID が含まれうる（★ 実行ログは削除の保証台帳 A-10 の保管対象）。");
}
