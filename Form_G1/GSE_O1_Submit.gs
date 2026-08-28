/**
 * GSE O1 (R3-a) — 提出物 (.age) の受け口 (Web App / doPost)
 *
 * 真実源:
 *   docs/adr/ADR-014-continuous-natural-work-collection.md D8（保管と 48 時間の猶予）
 *   .steering/20260827-o1-collection-enablement/decisions.md R-13（提出物の名前空間）
 *   .steering/20260828-o1-infra-and-key-verification/decisions.md（★ 本ファイルを作った判断）
 *   src-tauri/src/submission.rs:267 `o1_age_file_name`（★ 名前の規約の対）
 *
 * ============================================================================
 * ⚠️★★★ **G1 の受け口 (`GSE_G1_Submit.gs` / プロジェクト B) とは別のプロジェクトに置く**
 * ============================================================================
 *
 * ★ 研究者判断（2026-08-28・C-1）: **O1 は別に立てる**。
 *
 * 理由 3 点:
 *   1. ⚠️ **G1 は実施中である。** 稼働中の受け口を編集して再デプロイすると、
 *      その瞬間に G1 の提出が壊れうる（★ `preregistration.md §3.6` はブロックの
 *      事後除外を禁じており、取り返しがつかない）。
 *   2. ★ **同じ Drive フォルダに 2 研究のデータを混ぜない**（同意範囲が違う）。
 *   3. ★ シークレットを分けられる（片方が漏れてももう片方は無事）。
 *
 * ⚠️★★★ **「同じ受け口を使えば手間ゼロ」は成り立たなかった。**
 *   ★ G1 の `sanitizeName_` は `_block<NN>_gse_` 形しか通さず、
 *     O1 の `<pid>_o1day<NN>_gse_o1_….age` を **`bad name` で全弾き**する
 *     （2026-08-28 に node で当該正規表現を評価して実測）。
 *   → ★ どちらを選んでも `.gs` の改修が要る以上、**触らない側を選ぶのが安い。**
 *
 * ============================================================================
 * ★ G1 の受け口から意図的に**変えた**ところ（⚠️ ここ以外は同じ）
 * ============================================================================
 *
 *   V-1  `sanitizeName_` が **O1 の名前しか通さない**。
 *        ⚠️★★★ **G1 の `_block<NN>_` 形は明示的に落とす。**
 *        ★ これが「2 研究を混ぜない」の**実装上の担保**である
 *          （配布物を取り違えても、受け口が構造的に受け取らない）。
 *
 *   V-2  `MAX_BYTES` が大きい。⚠️ **O1 の単位はブロック (5 分) ではなく日 (24 時間)** である。
 *        ★ 実測に基づく（下の定数コメント）。G1 の 8 MB では毎日弾かれる。
 *
 * ============================================================================
 * ★ G1 から引き継いだ実測前提（⚠️ 推測で書き換えない・出所は GSE_G1_Submit.gs）
 * ============================================================================
 *
 *   M-1  POST は **302 を返す**。クライアントはリダイレクトを追う必要がある。
 *   M-3  `e` に **ヘッダも IP も無い**。→ ★ 認証は **本文** でしかできない。
 *   M-5  実行数ページは **ログ本文を出さない** し Cloud ログも開けない。
 *        → ⚠️★ **送信の成否は研究者側から追えない。** 端末側の `.sent` が唯一の真実源。
 *        → ★ だからこの `doPost` は **明示的な受領応答 `{"ok":true}`** を返す。
 *
 * ============================================================================
 * 配備手順（研究者が手で行う。⚠️ ★ 自動操作しない）
 * ============================================================================
 *
 *   ⚠️★ Apps Script の**関数セレクタは自動操作を受け付けない**ことが実測済みである
 *     （4 回試して 4 回とも選択が反映されなかった）。★ **実行は人が行う。**
 *
 *   1. script.google.com で **新しいプロジェクト**を作り（名前の例: `GSE_O1_submit`）、
 *      このファイルを貼る。
 *      ⚠️★★★ **`GSE_Gate1_submit`（G1 の受け口）にも `GSE_Gate1`（フォームビルダー）にも貼らない。**
 *   2. Google ドライブに **O1 専用の**受け取りフォルダを 1 つ作り、その ID を
 *      ⚙️「プロジェクトの設定」→「スクリプト プロパティ」の `FOLDER_ID` に入れる。
 *      ⚠️ ★ **G1 の受け取りフォルダを指さない**（混ざる）。
 *      ⚠️ ★ **`.gs` に書かない**（このリポジトリは一時 public にする運用がある）。
 *   3. 同じ場所の `SHARED_SECRET` に **G1 とは別の**長いランダム文字列を入れる（32 文字以上）。
 *   4. `checkSubmitConfig()` を実行し、`✅` が出ることを確認する（★ 読み取りのみ）。
 *      ⚠️★★★ **配備のたびに必ず実行する。** ★ `secretMatches_` は `expected` が空でも
 *      `false` を返すので、**設定し忘れと打ち間違いが同じ症状**（`unauthorized` で全弾き）になる
 *      （2026-08-08 に G1 で実際に踏んだ）。
 *   5. 「デプロイ」→「新しいデプロイ」→ 種類=**ウェブアプリ**
 *        - 実行ユーザー: **自分**
 *        - アクセスできるユーザー: **全員**（★ 被験者は Google ログインしない）
 *      → 出てくる `/exec` URL を控える。
 *   6. **O1 の**配布フォルダ（`o1.mode` と同じ場所）に `g1-submit.json` を置く:
 *        { "endpoint": "https://script.google.com/macros/s/…/exec", "secret": "<3 と同じ>" }
 *      ⚠️★ ファイル名は `g1-submit.json` のままである（`submission.rs:63`
 *        `SUBMIT_CONFIG_FILE_NAME` は 1 つしかない）。★ **中身で行き先が決まる。**
 *      ⚠️ ★ このファイルが無ければアプリは **送信しない**（`.age` はローカルに貯まる）。
 *   7. ⚠️ ★ `.gs` を直したら **必ず「デプロイを管理」→ 新バージョン**を出す。
 *      保存しただけでは `/exec` は古いコードのままである。
 *      ⚠️ さらに「変更が保存されていません」の表示のまま保存が通っていないことがある
 *      （2026-08-07 に実測）。★ **リロードして実体を読み直して確かめる。**
 *   8. ⚠️★★★ **1 日ぶんの実サイズで通し確認をする**（下の `MAX_BYTES` の注意を読むこと）。
 */

// ============================================================
// 設定
// ============================================================
//
// ⚠️★★ **シークレットとフォルダ ID をこのファイルに書かない。**
//   → ★ **Apps Script の「スクリプト プロパティ」に置く**（repo に入れられない場所）。

/** スクリプト プロパティから設定を読む。★ ソースには秘密を置かない。 */
function config_() {
  var props = PropertiesService.getScriptProperties();
  return {
    folderId: String(props.getProperty('FOLDER_ID') || '').trim(),
    secret: String(props.getProperty('SHARED_SECRET') || '').trim()
  };
}

/**
 * 受け取る 1 本の上限バイト数。
 *
 * ⚠️★★★ **G1 の 8 MB を流用してはならない。** ★ O1 の提出単位は **1 日 (24 時間)** であり、
 * G1 の **1 ブロック (5 分)** とは 288 倍違う。
 *
 * ## ★ 実測（2026-08-28・本機・`GSE_O1_MODE=1` の実走 → `gse-package`）
 *
 *   | 何 | 値 |
 *   |---|---|
 *   | raw NDJSON | **6,388,517 B / 7.21 時間** |
 *   | 匿名化 + age 暗号化後の `.age` | **5,730,783 B** |
 *   | → 24 時間換算 | **約 18 MB** |
 *
 *   ⚠️★★ **この実測区間は打鍵 0 本のほぼ無操作である。**
 *   ★ 実作業日は `key` / `paste` / `pointer_bin` 行が上乗せされるので、**これは下限**である。
 *   → ★ G1 の 8 MB なら **毎日 `too large` で弾かれ、1 本も届かない**。
 *
 * ## ⚠️ 上限に当たったときの壊れ方
 *
 *   ★ `too large` が返ると収束器は「未送信」のまま何度でも失敗を繰り返す
 *   （＝ **その日は永久に届かない**）。⚠️ しかも研究者側からは追えない（M-5）。
 *   → ★ **迷ったら大きい側に倒す。**
 *
 * ## ⚠️★★★ **未実測**: GAS 側が受け取れる本文の実際の上限
 *
 *   ★ `GSE_G1_Submit.gs` は逐語「実測では 50 MB でも通った（上限未到達）」と記す。
 *   ⚠️ ただし **それが base64 本文のサイズかデコード後かは、その記録からは決まらない**。
 *   ★ base64 は 4/3 に膨らむので、48 MB のデコード後は本文 **約 64 MB** になる。
 *   → ⚠️ **配備時に「1 日ぶんの実サイズ」で通し確認をすること**（手順 8）。
 *     ★ ここを測らずに被験者を走らせない。
 */
var MAX_BYTES = 48 * 1024 * 1024;

// ============================================================
// 受け口
// ============================================================

/**
 * 提出物を 1 本受け取る。
 *
 * ★ 応答は **必ず JSON** で、成功時だけ `{"ok":true,...}` を返す。
 * ⚠️ ★ 例外でも HTTP 200 になるので、`ok` を見ない実装は「送ったつもり」を作る。
 */
function doPost(e) {
  var t0 = new Date().getTime();
  try {
    var cfg = config_();
    if (!cfg.folderId || !cfg.secret) {
      return json_({ ok: false, error: 'endpoint not configured' });
    }
    if (!e || !e.postData || !e.postData.contents) {
      return json_({ ok: false, error: 'no body' });
    }
    var body;
    try {
      body = JSON.parse(e.postData.contents);
    } catch (parseErr) {
      return json_({ ok: false, error: 'bad json' });
    }
    if (!secretMatches_(String(body.secret || ''), cfg.secret)) {
      // ⚠️ ★ 何が違うか（長さ・前方一致）を返さない。
      return json_({ ok: false, error: 'unauthorized' });
    }

    var name = sanitizeName_(String(body.name || ''));
    if (!name) {
      return json_({ ok: false, error: 'bad name' });
    }
    var b64 = String(body.b64 || '');
    if (!b64) {
      return json_({ ok: false, error: 'empty payload' });
    }
    // ★ 上限の検査は **デコードの前に 1 回だけ**行う（★ base64 長から元のバイト数は決まる）。
    if (decodedLength_(b64) > MAX_BYTES) {
      return json_({ ok: false, error: 'too large' });
    }
    // ⚠️ base64 として壊れている本文は **ここで例外になる**。catch まで飛ばすと
    //   `server error` にまとめられ、★ 研究者に「壊れた本文が来た」と伝わらない。
    var bytes;
    try {
      bytes = Utilities.base64Decode(b64);
    } catch (decodeErr) {
      return json_({ ok: false, error: 'bad base64' });
    }
    // ⚠️ 空でない base64 が 0 バイトに解ける形（`"===="` 等）を通さない。
    if (bytes.length === 0) {
      return json_({ ok: false, error: 'empty payload' });
    }

    var folder = DriveApp.getFolderById(cfg.folderId);
    var saved = saveWithoutOverwriting_(folder, name, bytes);
    return json_({
      ok: true,
      saved: saved.name,
      duplicate: saved.duplicate,
      bytes: bytes.length,
      elapsed_ms: new Date().getTime() - t0
    });
  } catch (err) {
    // ⚠️ ★ 例外を握り潰さない。★ ただしスタックは返さない（内部構造を漏らさない）。
    console.log('doPost failed: ' + err);
    return json_({ ok: false, error: 'server error' });
  }
}

/**
 * GET は使わない。⚠️ ★ ここで受け取れる形にすると、URL を踏んだだけで何かが起きる。
 * 疎通確認だけできるようにしておく（★ 秘密も件数も返さない）。
 */
function doGet(e) {
  return json_({ ok: false, error: 'use POST' });
}

// ============================================================
// 純関数（★ ローカルの guard test が同じ関数を呼ぶ）
// ============================================================

/**
 * ファイル名を検証する。★ 通すのは **O1 の提出物の形をした `.age` だけ**。
 *
 * ⚠️ ★ 名前は被験者の端末から来る = **信用しない**。
 *
 * ## ★ 通す形（`src-tauri/src/submission.rs:267` `o1_age_file_name` と対）
 *
 *   `<participant>_o1day<NN>_<stem>.age`
 *
 *   - `participant` … 英数字 1〜16（`P012` 等）
 *   - `o1day<NN>`   … `format!("{day:02}")` なので **2 桁以上**。3 桁まで許す（〜999 日）
 *   - `stem`        … `gse_o1_<日付 8 桁>_<時刻 6 桁>`
 *                     (`o1.rs:263` `SESSION_FILE_PREFIX = "gse_o1_"` ＋ `logger` のタイムスタンプ)
 *   - 任意の連番 `_<1〜10 桁>` … ⚠️★★ **削ってはならない。**
 *     ★ セッション名は**秒粒度**なので、同じ秒に 2 度ローテートすると
 *       `logger::unique_path_from` が `gse_o1_20260828_012103_2` を作る。
 *       これは **静かな全損を防ぐための正規の命名**であり、端末はその名前で `.age` を作って送る。
 *       ⚠️ ここで弾くと `bad name` が毎回返り、★ **その日は永久に届かない**。
 *
 * ## ⚠️★★★ **G1 の名前は落とす**（★ これが「混ぜない」の担保である）
 *
 *   ★ `P012_block03_gse_20260807_101112.age` は **通さない**。
 *   ⚠️ 通してしまうと、配布物を取り違えた被験者の **G1 の提出物が O1 のフォルダに入り**、
 *     ★ 同意範囲の違うデータが混ざる（⚠️ 混ざったあとに分けるのは名前頼みになる）。
 *   → ★ `_o1day` を要求する時点で構造的に落ちるが、**テストで明示的に固定してある**
 *     （`o1_submit_guard_test.cjs` の「G1 の名前は落とす」ケース）。
 *
 * 通ったら名前をそのまま返し、通らなければ空文字を返す（★ 直して通さない。
 * 黙って別名で保存すると、どの提出物か分からなくなる）。
 */
function sanitizeName_(name) {
  if (!name) return '';
  return /^[A-Za-z0-9]{1,16}_o1day\d{2,3}_gse_o1_\d{8}_\d{6}(_\d{1,10})?\.age$/.test(name)
    ? name
    : '';
}

/**
 * base64 文字列がデコード後に何バイトになるかを、★ **デコードせずに**求める。
 *
 * ⚠️ 巨大な payload を一度メモリに展開してから捨てるのを避けるため（可用性）。
 * ★ 4 文字が 3 バイトに対応し、末尾の `=` の数だけ減る。
 */
function decodedLength_(b64) {
  if (!b64) return 0;
  var padding = 0;
  if (b64.charAt(b64.length - 1) === '=') padding++;
  if (b64.charAt(b64.length - 2) === '=') padding++;
  return Math.floor(b64.length / 4) * 3 - padding;
}

/**
 * 共有シークレットの照合。★ 長さで早期 return せず、全文字を舐める。
 *
 * ⚠️ GAS は本当の定数時間比較を保証しないが、★ **先頭一致で早く返る実装にはしない**。
 */
function secretMatches_(given, expected) {
  if (!expected) return false;
  var diff = given.length ^ expected.length;
  var n = Math.max(given.length, expected.length);
  for (var i = 0; i < n; i++) {
    diff |= (given.charCodeAt(i) || 0) ^ (expected.charCodeAt(i) || 0);
  }
  return diff === 0;
}

/**
 * ★★ **必ず保存する。上書きも省略もしない。**
 *
 * ⚠️★★ 「同名かつ同サイズなら再送とみなして保存しない」は **提出を握り潰す経路**である:
 *   シークレットを持つ者（= 全被験者の端末に平文で配られる非ローテーション資格情報）が
 *   **同名・同サイズのダミーを先回りして置く**と、本物の提出に `ok` を返してしまう。
 *   ★ 端末側は `.sent` を書き、⚠️ **その記録は永久に回収されない**。
 *
 * ★ この研究の絶対条件は「1 本も失わない」である。
 *   → **重複が Drive に並ぶ**ほうが、**1 本消える**より桁違いにましである。
 */
function saveWithoutOverwriting_(folder, name, bytes) {
  var duplicateName = folder.getFilesByName(name).hasNext();
  var finalName = name;
  if (duplicateName) {
    // ★ 消さない・置き換えない。**別名で足す**。
    finalName = name.replace(/\.age$/, '') + '_dup-' + new Date().getTime() + '.age';
  }
  folder.createFile(Utilities.newBlob(bytes, 'application/octet-stream', finalName));
  return { name: finalName, duplicate: duplicateName };
}

function json_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(
    ContentService.MimeType.JSON
  );
}

// ============================================================
// 研究者が手で 1 回だけ走らせる検査（★ 破壊的な操作は無い）
// ============================================================

/**
 * 設定が埋まっていて、フォルダに書ける状態かを確かめる。
 * ★ **読み取りのみ**（ファイルを作らない）。
 *
 * ⚠️★★★ **配備のたびに実行すること。** ★ `secretMatches_` は `expected` が空でも
 * `false` を返すので、**設定し忘れと打ち間違いが同じ症状**になる。
 */
function checkSubmitConfig() {
  var cfg = config_();
  var problems = [];
  if (!cfg.folderId) problems.push('スクリプト プロパティ FOLDER_ID が未設定');
  if (!cfg.secret) problems.push('スクリプト プロパティ SHARED_SECRET が未設定');
  if (cfg.secret && cfg.secret.length < 24) {
    problems.push('SHARED_SECRET が短い（24 文字以上を推奨）');
  }
  if (cfg.folderId) {
    try {
      var folder = DriveApp.getFolderById(cfg.folderId);
      console.log('受け取りフォルダ: ' + folder.getName());
    } catch (err) {
      problems.push('FOLDER_ID のフォルダを開けない: ' + err);
    }
  }
  if (problems.length) {
    console.log('❌ 配備できていない: ' + problems.join(' / '));
    throw new Error(problems.join(' / '));
  }
  console.log('✅ O1 受け口の設定は揃っている（デプロイして /exec URL を控えること）');
  console.log('⚠️ G1 の受け取りフォルダを指していないか、フォルダ名で確かめること。');
}
