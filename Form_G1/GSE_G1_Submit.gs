/**
 * GSE G1 — 提出物 (.age) の受け口 (Web App / doPost)
 *
 * 真実源:
 *   .steering/20260806-g1-auto-submit-on-block-end/design.md §4（送信先との約束）
 *   .steering/20260806-g1-auto-submit-on-block-end/gas-measurements.md（★ 実測値）
 *   experiments/20260801-controlled-friction-task/consent.md §3（何を送ると約束したか）
 *
 * ============================================================================
 * ⚠️★★ このファイルは **`GSE_G1_Form_Builder.gs` とは別の Apps Script プロジェクト** に置く
 * ============================================================================
 *
 * ★ 2026-08-07 の事故（`incident-20260807-g1c-rebuild.md`）は、
 *   **関数セレクタの選択が反映されないまま既定の `setupG1Forms` を実行**して起きた。
 *   `setupG1Forms` は `clearForm()` を呼ぶので、同意フォームの設問が全部消えた。
 *
 * → ★ 対策の 1 つは「取り返しのつかない操作の**隣に**行かないこと」である。
 *   本ファイルには **破壊的な関数が 1 つも無い**（作るだけ・消さない・上書きしない）。
 *   ⚠️ フォームビルダーと同じプロジェクトに置くと、セレクタの取り違えで
 *   **また同意記録を消せる位置**に研究者を立たせることになる。★ 混ぜない。
 *
 * ============================================================================
 * ★ 実測に基づく前提（⚠️ 推測で書き換えない）
 * ============================================================================
 *
 *   M-1  POST は **302 を返す**。クライアントはリダイレクトを追う必要がある
 *        （メソッドを強制すると 405）。→ 送信側は `reqwest` の既定方針に任せている。
 *   M-2  300 KB が 1.45 s で通る（`.age` の実サイズは 160〜225 KB）。分割は不要。
 *   M-3  `e` に **ヘッダも IP も無い**（キーは contextPath / parameter / parameters /
 *        queryString / contentLength / postData の 6 つだけ）。
 *        → ★ 認証は **本文** でしかできない。⚠️ クエリに置くと URL に残る。
 *   M-5  実行数ページは **ログ本文を出さない** し Cloud ログも開けない。
 *        → ⚠️★ **送信の成否は研究者側から追えない。** 端末側の `.sent` が唯一の真実源。
 *        → ★ だからこの `doPost` は **明示的な受領応答 `{"ok":true}`** を返す。
 *          クライアントは HTTP 200 だけでは成功と見なさない（GAS は例外でも 200 を返すため）。
 *
 * ⚠️ ★ **未実測**: `DriveApp` 保存を含む所要時間（`gas-measurements.md` §3）。
 *   → ★ 下の `measureSaveTiming()` をエディタで 1 回実行すれば測れる（読み取り専用ではないが、
 *     作るのは検証用フォルダ内の一時ファイルだけで、被験者データには触れない）。
 *
 * ============================================================================
 * 配備手順（研究者が手で行う。⚠️ ★ 自動操作しない）
 * ============================================================================
 *
 *   1. script.google.com で **新しいプロジェクト**を作り、このファイルを貼る。
 *      ⚠️ ★ フォームビルダーのプロジェクトに貼らない（上記の理由）。
 *   2. Google ドライブに受け取り用フォルダを 1 つ作り、その ID を `FOLDER_ID` に書く。
 *      （フォルダの URL `https://drive.google.com/drive/folders/<ここ>` の `<ここ>`）
 *   3. `SHARED_SECRET` に **長いランダム文字列**を書く（32 文字以上を推奨）。
 *      ⚠️ ★ これが守っているのは **可用性だけ**である。中身は研究者の age 公開鍵で
 *      暗号化済みなので、経路が漏れても読めない。★ 過大評価しない。
 *   4. `checkSubmitConfig()` を実行し、`✅` が出ることを確認する（読み取り専用）。
 *   5. 「デプロイ」→「新しいデプロイ」→ 種類=**ウェブアプリ**
 *        - 実行ユーザー: **自分**
 *        - アクセスできるユーザー: **全員**（★ 被験者は Google ログインしない・M-4）
 *      → 出てくる `/exec` URL を控える。
 *   6. 配布フォルダ（`g1.mode` と同じ場所）に `g1-submit.json` を置く:
 *        { "endpoint": "https://script.google.com/macros/s/…/exec", "secret": "<3 と同じ>" }
 *      ⚠️ ★ このファイルが無ければアプリは **送信しない**（`.age` はローカルに貯まる）。
 *      ★ これが「送信を止めるスイッチ」である（decisions D-4・研究者側にだけ置く）。
 *   7. `.gs` を直したら **必ず「デプロイを管理」→ 新バージョン**を出す。
 *      ⚠️ ★ 保存しただけでは `/exec` は古いコードのままである。
 *      ⚠️ ★ さらに「変更が保存されていません」の表示のまま保存が通っていないことがある
 *      （2026-08-07 に実測）。★ **リロードして実体を読み直して確かめる。**
 */

// ============================================================
// 設定（★ 配備時に埋める）
// ============================================================

/** 受け取った `.age` を置く Google ドライブのフォルダ ID。 */
var FOLDER_ID = '';

/** 共有シークレット（本文で照合する）。⚠️ 守るのは可用性だけ。 */
var SHARED_SECRET = '';

/**
 * 受け取る 1 本の上限バイト数。
 * ★ `.age` の実サイズは 160〜225 KB（P-1 の 4 本）。★ 8 MB は **35 倍以上**の余裕である。
 * ⚠️ 実測では 50 MB でも通った（上限未到達）が、★ **受け取る側で絞る**のが正しい
 *    （いたずら投稿でドライブを埋められないため）。
 */
var MAX_BYTES = 8 * 1024 * 1024;

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
    if (!FOLDER_ID || !SHARED_SECRET) {
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
    if (!secretMatches_(String(body.secret || ''), SHARED_SECRET)) {
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
    var bytes = Utilities.base64Decode(b64);
    if (bytes.length === 0) {
      return json_({ ok: false, error: 'empty payload' });
    }
    if (bytes.length > MAX_BYTES) {
      return json_({ ok: false, error: 'too large', bytes: bytes.length });
    }

    var folder = DriveApp.getFolderById(FOLDER_ID);
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
 * ファイル名を検証する。★ 通すのは **`.age` だけ**（design.md §4）。
 *
 * ⚠️ ★ 名前は被験者の端末から来る = **信用しない**。
 *
 * ★ 脅威を取り違えないこと: Drive のファイル名は **パスではない**ので、
 *   ここでの危険は「ディレクトリ traversal」ではなく
 *   **「提出物でないものを受け取ってしまう」「研究者が中身を取り違える」** である。
 *   → 検査は **許可リスト** 1 本を軸にする。
 *
 * ⚠️★★ **冗長なガードを置かない。** 当初は `/` `\` `..` を個別に弾く行も書いたが、
 *   ★ **わざと 1 行ずつ壊しても検査が赤にならなかった**（許可リストが同じ入力を先に捕まえるため）。
 *   発火しない検査を残すと「守られているつもり」を作るので置かない
 *   （`logger.rs` の Rotate ガードで同じ判断をしている）。
 *   → ★ いま残っている 4 つは、**どれを壊しても `submit_guard_test.cjs` が赤になる**
 *     ことを実測してある（各チェックに専用の入力がある）。
 *
 * 通ったら名前をそのまま返し、通らなければ空文字を返す（★ 直して通さない。
 * 黙って別名で保存すると、どの提出物か分からなくなる）。
 */
function sanitizeName_(name) {
  // (1) 長さ。★ 極端に長い名前は Drive の一覧を壊し、研究者が読めなくなる。
  if (!name || name.length > 120) return '';
  // (2) ★ 許可リスト。英数字と `. _ -` 以外は**すべて**拒否する
  //     （空白・制御文字・パス区切り `/` `\`・全角・引用符などはここで落ちる）。
  if (!/^[A-Za-z0-9._-]+$/.test(name)) return '';
  // (3) 先頭ドット（隠しファイル・`.age` そのもの）を拒否。
  if (name.charAt(0) === '.') return '';
  // (4) ★ 拡張子は `.age` に限る（生 NDJSON を受け取る経路を作らない）。
  if (!/\.age$/.test(name)) return '';
  return name;
}

/**
 * 共有シークレットの照合。★ 長さで早期 return せず、全文字を舐める。
 *
 * ⚠️ GAS は本当の定数時間比較を保証しないが、★ **先頭一致で早く返る実装にはしない**。
 *   守っているのは可用性だけなので、ここに強い保証は求めない（design.md §4）。
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
 * 上書きせずに保存する。
 *
 * ⚠️★ **既にあるものを消さない・置き換えない。** 1 本も失えない。
 * - 同名 **かつ同サイズ** が既にある → ★ **再送とみなして何もしない**（`duplicate: true`）。
 *   端末側で「送れたのに `.sent` を置けなかった」ときに二重に届くのが主な経路であり、
 *   同じものが 2 本並ぶより、1 本だけ在るほうが研究者の手間が少ない。
 * - 同名だがサイズが違う → ★ **別名で保存**して両方残す（人が見て判断する）。
 */
function saveWithoutOverwriting_(folder, name, bytes) {
  var existing = folder.getFilesByName(name);
  while (existing.hasNext()) {
    var f = existing.next();
    if (f.getSize() === bytes.length) {
      return { name: name, duplicate: true };
    }
  }
  var finalName = name;
  if (folder.getFilesByName(name).hasNext()) {
    // ★ サイズ違いの同名。⚠️ 消さずに別名で残す。
    finalName = name.replace(/\.age$/, '') + '_conflict-' + new Date().getTime() + '.age';
  }
  folder.createFile(Utilities.newBlob(bytes, 'application/octet-stream', finalName));
  return { name: finalName, duplicate: false };
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
 */
function checkSubmitConfig() {
  var problems = [];
  if (!FOLDER_ID) problems.push('FOLDER_ID が空');
  if (!SHARED_SECRET) problems.push('SHARED_SECRET が空');
  if (SHARED_SECRET && SHARED_SECRET.length < 24) {
    problems.push('SHARED_SECRET が短い（24 文字以上を推奨）');
  }
  if (FOLDER_ID) {
    try {
      var folder = DriveApp.getFolderById(FOLDER_ID);
      console.log('受け取りフォルダ: ' + folder.getName());
    } catch (err) {
      problems.push('FOLDER_ID のフォルダを開けない: ' + err);
    }
  }
  if (problems.length) {
    console.log('❌ 配備できていない: ' + problems.join(' / '));
    throw new Error(problems.join(' / '));
  }
  console.log('✅ 受け口の設定は揃っている（デプロイして /exec URL を控えること）');
}

/**
 * ⚠️★ `gas-measurements.md §3` の **未実測** を埋めるための計測。
 *
 * ★ 実運用サイズ（300 KB 相当）の blob を **`DriveApp` に保存するところまで**含めて測る。
 *   前回の実測（1 KB〜50 MB）は Drive 保存を **含んでいない**ので、この値では見積もれなかった。
 *
 * ⚠️ 作った一時ファイルは **同じ実行の中で削除する**（受け取りフォルダを汚さない）。
 *   ★ 削除するのはこの関数が自分で作ったファイルだけである。
 */
function measureSaveTiming() {
  checkSubmitConfig();
  var folder = DriveApp.getFolderById(FOLDER_ID);
  var sizes = [1024, 300 * 1024, 1024 * 1024];
  var results = [];
  for (var i = 0; i < sizes.length; i++) {
    var payload = new Array(sizes[i] + 1).join('x');
    var bytes = Utilities.newBlob(payload).getBytes();
    var t0 = new Date().getTime();
    var file = folder.createFile(
      Utilities.newBlob(bytes, 'application/octet-stream', 'TIMING_PROBE_' + t0 + '.bin')
    );
    var elapsed = new Date().getTime() - t0;
    file.setTrashed(true); // ★ 自分で作った一時ファイルだけを片付ける
    results.push(sizes[i] + ' bytes -> ' + elapsed + ' ms');
  }
  console.log('DriveApp 保存の所要時間（★ この値を gas-measurements.md §3 に書く）:');
  console.log(results.join('\n'));
}
