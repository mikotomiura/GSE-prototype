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
 *   2. Google ドライブに受け取り用フォルダを 1 つ作り、その ID を
 *      ⚙️「プロジェクトの設定」→「スクリプト プロパティ」の `FOLDER_ID` に入れる。
 *      （フォルダの URL `https://drive.google.com/drive/folders/<ここ>` の `<ここ>`）
 *      ⚠️ ★ **`.gs` に書かない**（このリポジトリは一時 public にする運用がある）。
 *   3. 同じ場所の `SHARED_SECRET` に **長いランダム文字列**を入れる（32 文字以上を推奨）。
 *      ⚠️ ★ これが守るのは **可用性と、記録の完全性**である。★ **機密性は age が守る**
 *      （中身は研究者の公開鍵で暗号化済みなので、経路が漏れても読めない）。
 *      ⚠️ ただしシークレットを持つ者は **偽の提出を投入できる**（完全性）ので、
 *      ★ 「可用性だけ」と過小評価もしない。★ 全被験者に同じ値が配られる点に留意する。
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
// 設定
// ============================================================
//
// ⚠️★★ **シークレットとフォルダ ID をこのファイルに書かない。**
//   ★ このリポジトリは Actions の分数都合で **一時的に public にする運用がある**
//     (`.steering` / memory に記録あり)。⚠️ `.gs` に `SHARED_SECRET = 'xxxx'` と書いて
//     commit すると、public にした瞬間に **誰でも研究者の Drive 受け取りフォルダへ
//     書き込めるようになる**。★ git 履歴に入るので、後からローテートしても痕跡は消せない。
//   → ★ **Apps Script の「スクリプト プロパティ」に置く**（repo に入れられない場所）。
//
//   置き方: エディタ左下の ⚙️「プロジェクトの設定」→「スクリプト プロパティ」→
//           `FOLDER_ID` と `SHARED_SECRET` を追加する。
//   ⚠️ ★ 設定したら `checkSubmitConfig()` を 1 回実行して確かめる。

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
    // ★ 上限の検査は **デコードの前に 1 回だけ**行う。
    //   ⚠️★ 当初はデコード後にも同じ検査を置いていたが、**片方を壊しても赤にならなかった**
    //   （もう片方が同じ入力を捕まえる）。★ 発火しない検査を残さないので 1 本にした。
    //   ★ base64 の長さから元のバイト数は決まるので、前段でも**正確に**判定できる。
    if (decodedLength_(b64) > MAX_BYTES) {
      return json_({ ok: false, error: 'too large' });
    }
    var bytes = Utilities.base64Decode(b64);
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
 * ファイル名を検証する。★ 通すのは **提出物の形をした `.age` だけ**（design.md §4）。
 *
 * ⚠️ ★ 名前は被験者の端末から来る = **信用しない**。
 *
 * ★ 脅威を取り違えないこと: Drive のファイル名は **パスではない**ので、
 *   ここでの危険は「ディレクトリ traversal」ではなく
 *   **「提出物でないものを受け取ってしまう」「研究者が中身を取り違える」** である。
 *
 * ## ⚠️★★ 検査を **1 本にまとめた経緯**（★ どちらも実測で決めた）
 *
 * 1. 最初は `/` `\` `..` を個別に弾く行を書いた
 *    → ★ **1 行ずつ壊しても赤にならなかった**（許可リストが同じ入力を先に捕まえる）。
 * 2. そこで許可リスト・先頭ドット・拡張子・長さの 4 本に整理した
 *    → security-checker の指摘で **提出物の形**まで絞る 1 本を足したところ、
 *      ★ **その 1 本が残り 4 本をすべて包含し、また 1 つも赤にならなくなった**（実測）。
 *
 * → ★ **発火しない検査を残さない**（`logger.rs` の Rotate ガードと同じ判断）。
 *   残したこの 1 本は、⚠️ **壊すと `submit_guard_test.cjs` の名前ケースが全部赤になる**。
 *
 * 通ったら名前をそのまま返し、通らなければ空文字を返す（★ 直して通さない。
 * 黙って別名で保存すると、どの提出物か分からなくなる）。
 */
function sanitizeName_(name) {
  if (!name) return '';
  // ★ **提出物そのものの形**しか通さない（`P012_block03_gse_20260807_101112.age`）。
  //   参加者 ID(英数字 1〜16) ＋ `_block` ＋ 2〜3 桁 ＋ `_gse_` ＋ 日付 8 桁 ＋ `_` ＋ 時刻 6 桁 ＋ `.age`
  //   ★ 名前の規約は `submission::age_file_name` と対である（片方を変えたら両方直す）。
  return /^[A-Za-z0-9]{1,16}_block\d{2,3}_gse_\d{8}_\d{6}\.age$/.test(name) ? name : '';
}

/**
 * 共有シークレットの照合。★ 長さで早期 return せず、全文字を舐める。
 *
 * ⚠️ GAS は本当の定数時間比較を保証しないが、★ **先頭一致で早く返る実装にはしない**。
 *   守っているのは可用性だけなので、ここに強い保証は求めない（design.md §4）。
 */
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
 * ⚠️★★ 当初は「同名かつ同サイズなら再送とみなして保存しない」にしていた。
 *   security-checker の指摘で **これが提出を握り潰す経路になる**と分かった:
 *   シークレットを持つ者（= 全被験者の端末に平文で配られる非ローテーション資格情報なので、
 *   被験者本人やその端末に触れる者で成立する）が **同名・同サイズのダミーを先回りして置く**と、
 *   本物の提出に対して `ok` を返してしまう。★ 端末側は `.sent` を書き、
 *   ⚠️ **その記録は永久に回収されない**（送信先から成否を追えないので誰も気づけない）。
 *
 * ★ この研究の絶対条件は「1 本も失わない」である。
 *   → **重複が Drive に並ぶ**（研究者が中身を見て捨てられる）ほうが、
 *     **1 本消える**（取り返せない）より桁違いにましである。
 *   ⚠️ 重複が生まれる正常な経路もある（送れたのに `.sent` を書けずに再送した場合）。
 *     ★ それでも保存する。判断は人に返す。
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
  var folder = DriveApp.getFolderById(config_().folderId);
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
