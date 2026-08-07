/**
 * GSE G1 統制タスク実験 — Google Form ビルダー（3 フォームを 1 本にまとめる）
 *
 * 真実源:
 *   experiments/20260801-controlled-friction-task/preregistration.md（凍結・§2.6 / §2.8 / §2.10）
 *   experiments/20260801-controlled-friction-task/consent.md（同意文面の真実源）
 *   experiments/20260801-controlled-friction-task/protocol.md（進行）
 *   .steering/20260802-g1-execution-prep/decisions.md E-11（フォーム方式の採用）
 *
 * ★ このファイルは**配布と記録の手段**であって、文面の真実源ではない。
 *   文面を変えるときは consent.md を先に直し、ここへ写す（逆をやらない）。
 *
 * ============================================================================
 * ⚠️⚠️ 3 フォームは制約が正反対である。取り違えると実験が壊れる。
 * ============================================================================
 *
 *              | G1-C 同意          | G1-M 強制比較            | G1-S 終了後アンケート
 *   -----------+--------------------+--------------------------+----------------------
 *   いつ       | 開始前・1 回       | ブロック 3〜9 の直後・7回 | 最後の copy の後・1 回
 *   PII        | 氏名・メール       | ★ 被験者 ID のみ         | ★ 被験者 ID のみ
 *   形式       | 必須チェック＋記名 | ★ 二択のみ               | 二択＋自由記述
 *   禁止       | どのブロックが難しい条件か（protocol.md §4.3）
 *              |                    | ★ HI / LO の語           | ★ HI / LO の語
 *   所要       | 余裕をもって       | ★ 1 分休憩に収まること   | 5 分程度
 *
 * ★ **「1〜5 のリッカート」を G1-M に入れてはならない**（preregistration.md §2.6）。
 *   Phase1 の straight-lining（P013 の Q1 が全て "1"）が GATE3 を DataInsufficient にした
 *   近因であり、同じ計器を使わない。強制比較（二択・「どちらでもない」なし）だけを使う。
 *
 * ============================================================================
 * ⚠️ 固定 ID 方式（FormApp.create を使わない）
 * ============================================================================
 * Phase1 で `FormApp.create` が実行のたびに別フォームを量産し、被験者に配った短縮 URL が
 * 指すフォームと集計が読むフォームがズレて「回答が記録されない」不具合を起こした。
 * → **必ず先に Google Forms で空フォームを 3 つ作り、その編集 URL の ID をここに書く。**
 *    docs.google.com/forms/d/<ここ>/edit の <ここ>。空のままだと各 build は停止する。
 */

// ============================================================
// 設定（★ 実行前に埋める）
// ============================================================
// ★ 研究者が 2026-08-03 に作成した空フォーム 3 本を割り当てた（Phase1 と同じく .gs に置く規約）。
// ⚠️ 3 本とも**空フォーム**なので、どれがどの役割になるかは**この割り当てが決める**。
//    setupG1Forms() を実行すると、各フォームにタイトル・説明・設問が書き込まれる。
//    ★ 一度でも被験者に URL を配ったら、**この割り当てを入れ替えてはならない**
//      （配った URL が別のフォームを指すことになる — Phase1 の量産バグと同じ壊れ方）。
var FORM_ID_CONSENT = "1Hs3NtuOB3IRKHaU6xspL8jd1y4BdVKFK0s4JxHTQdsE"; // G1-C 説明・同意（form1）
var FORM_ID_MCHECK = "1iDcr0uc_51dEEI_idyJhcozYMX02N3ug-JQ7zSVMHIA"; // G1-M 強制比較（form2）
var FORM_ID_SURVEY = "1ScM_420irB8DUA8EFYyDJBaPBR-_lOa4evtveQBVWjU"; // G1-S 終了後アンケート（form3）

// 既存設問を毎回作り直すか（通常 true）。
var CLEAR_EXISTING = true;

// ★★ 回答があるフォームを作り直してよいか（既定 false = fail-closed）。
//
// ⚠️★ **2026-08-07 の事故を受けて追加した。** 実際に起きたこと:
//    「回答を保全する」と決めていたのに、Apps Script の関数セレクタの選択が反映されないまま
//    `setupG1Forms` を実行してしまい、`buildConsentForm()` が `clearForm()` で全設問を削除した。
//    → G1-C の**回答レコード 3 件は残ったが、答えがどの設問のものか失われた**
//      （要約・個別のどちらも「回答なし」表示になった。★ 実測で確認）。
//    ⚠️ ★ **Forms に回答の版履歴は無い。取り返しがつかない。**
//
// ★ 教訓: 「気をつける」では防げない。**コード側で止める。**
//    人間の 1 クリックのミスが同意記録を壊せる設計そのものが欠陥だった。
//
// ★ 意図して作り直すときだけ true にし、⚠️ **作業が終わったら false に戻す**。
//    → 回答を保ったまま文面を更新したいときは `migrateConsentForm()` を使う（削除しない）。
var ALLOW_REBUILD_WITH_RESPONSES = false;

// ★ clearForm() の直前に必ず通す関門。⚠️ **黙って進めない**（`data-privacy` / 研究記録の保全）。
function assertSafeToRebuild_(form, label) {
  var n;
  try {
    n = form.getResponses().length;
  } catch (e) {
    // ★ 回答数を確認できないなら **安全側に倒して止める**。
    //   ⚠️ 「確認できなかった」を「0 件」と読み替えない（silent-failure 型の典型）。
    throw new Error(
      "★ " + label + " の回答数を確認できませんでした: " + e + "\n" +
        "⚠️ 確認できない以上、作り直しません（fail-closed）。"
    );
  }
  if (n === 0) return;

  if (ALLOW_REBUILD_WITH_RESPONSES) {
    Logger.log(
      "⚠️⚠️ " + label + ": 回答が " + n + " 件あるが ALLOW_REBUILD_WITH_RESPONSES=true のため作り直します。\n" +
        "   ★ この操作で **回答と設問の紐付けが失われます**。作業後は必ず false に戻してください。"
    );
    return;
  }

  throw new Error(
    "⛔ " + label + " には既に回答が " + n + " 件あります。作り直しを中止しました（fail-closed）。\n" +
      "\n" +
      "★ 回答を保ったまま文面を更新したい場合（ほぼ常にこちら）:\n" +
      "    migrateConsentForm()  … 既存設問を消さず、足りない項目だけを挿入する\n" +
      "    checkConsentFormParity()  … 実フォームとコードのズレを読み取り専用で報告する\n" +
      "\n" +
      "⚠️ どうしても作り直す場合は ALLOW_REBUILD_WITH_RESPONSES = true にしてから再実行し、\n" +
      "   ★ **回答と設問の紐付けが失われることを承知したうえで**行ってください。\n" +
      "   （2026-08-07 に実際にこれを事故で起こしています。Forms に版履歴はありません。）"
  );
}

// 問い合わせ先（PII ではないのでここに置いてよい）。
var CONTACT_EMAIL = "mmiura.network@gmail.com";

// G1 運用管理シートの ID を覚えておく Script Property キー。
// ⚠️ Phase1 の GSE_MGMT_SHEET_ID とは**別のキー**（別シート）。ただし P-ID は共有する（下記）。
var MGMT_SHEET_PROP_G1 = "GSE_G1_MGMT_SHEET_ID";

// ============================================================
// ★★ P-ID は Phase1 と共有する（研究者判断 2026-08-03）
// ============================================================
// 同じ人には同じ P-ID を使う。1 人の人間に 2 つの識別子を作らない。
//
// ★ したがって **本ファイルは P-ID を採番しない**。採番元は
//   `Form_Phase1/GSE_Phase1_Form_Builder.gs` の `addParticipant()` /
//   Phase1 運用管理シートの「参加者ロスター」**ただ 1 つ**である。
//   ⚠️ 2 か所で採番すると必ず衝突する（別シートを走査しても相手の最大値が見えないため）。
//   新規の被験者が来たら **Phase1 側で採番してから** G1 を回すこと。
//
// ★ 同じ理由で、本シートは **実名・メールを持たない**。実名↔P-ID の対応表を 2 か所に作らない
//   (data-privacy)。G1 の同意フォーム(G1-C)の回答シートと Phase1 のロスターに既にある。
//
// ⚠️⚠️ **ID 共有の帰結（必ず読む）**: G1 は第 1 週(blind 較正)モードで回すため
//   session_meta に condition=blind_calibration / label_pool=calibration_blind が刻まれ、
//   **Phase1 の較正セッションと同じラベル**になる（data.md の B-4）。
//   ID まで同じにすると、**ID 範囲による分離が使えなくなる**。
//   → 分離は次の 2 つだけが担う。どちらも省略しないこと:
//     1. `blocks/P0xx.json` の `file` 列（どの NDJSON が G1 のブロックかを列挙している）
//     2. gse-dataset への送付時に **G1 のセッションであることを明示**する（data.md の送付フロー）

// ============================================================
// ★ 設問タイトルの契約（forms_to_blocks.py がこの語で列を探す）
// ============================================================
// ⚠️ ここを変えたら `experiments/20260801-controlled-friction-task/forms_to_blocks.py` の
//    HEADER_KEYS も同じ版に直すこと。**文書だけ直して実装が追随しない**事故が
//    このプロジェクトで 2 回起きている（decisions.md E-6 / E-7）。
var Q_SUBJECT_ID = "被験者ID";

// ★★ 第 8 版 §2.12-4: 事前にどれだけ読んだかを G1-S で記録する。
//    ⚠️ **判定に使わない・除外にも使わない**（§3.6 無変更）。§3.8 の限界の記述に使う。
var Q_S_PREREAD = "事前にお送りした資料を、当日までにどのくらいご覧になりましたか。";
var Q_S_PREREAD_NOTE = "書く内容を考えておいた場合、どのくらい考えたか教えてください（任意）。";
var Q_BLOCK_NO = "ブロック番号";
var Q_HARDER = "より詰まったのはどちらですか";
// 二択の選択肢文字列（相対表現。★ ブロック番号を被験者に計算させない）。
var CHOICE_PREV = "1つ前のブロックのほう";
var CHOICE_CURRENT = "直前のブロックのほう";

// ============================================================
// 入口
// ============================================================
function setupG1Forms() {
  buildConsentForm();
  buildManipulationCheckForm();
  buildPostSurveyForm();
  // ★ 短縮 URL は任意。XGD_API_KEY が未設定なら何もしない（実施に支障は無い）。
  //   管理シートより先に呼ぶ — リンク集タブが短縮 URL を読むため。
  shortenFormUrls();
  var url = buildManagementSheet();
  Logger.log("🎉 G1 フォーム 3 本 ＋ 管理シート 作成完了: " + url);
  Logger.log(listG1FormUrls());
  if (!G1_CONTACT) {
    Logger.log("⚠️ ★ G1_CONTACT が空です。受付メールは送れません（fail-closed）。");
  }
  if (!PHASE1_MGMT_SHEET_ID) {
    Logger.log("⚠️ ★ PHASE1_MGMT_SHEET_ID が空です。P-ID の採番ができません（採番元は Phase1 のロスター）。");
  }
}

function listG1FormUrls() {
  var props = PropertiesService.getScriptProperties();
  var out = [];
  ["G1_CONSENT", "G1_MCHECK", "G1_SURVEY"].forEach(function (key) {
    var raw = props.getProperty("FORMURL_" + key);
    if (!raw) {
      out.push(key + ": (未生成)");
      return;
    }
    var o = JSON.parse(raw);
    var shortUrl = getShortUrl_(props, key);
    out.push(
      key + ": " + o.label +
        "\n  回答: " + o.publishedUrl +
        (shortUrl ? "\n  短縮: " + shortUrl : "") +
        "\n  編集: " + o.editUrl
    );
  });
  return out.join("\n");
}

// ★ G1-C の設問タイトル。**回答取得（onG1ConsentSubmit）と共有する**。
//   ⚠️ 片方だけ変えると、提出されても氏名やメールが取れずに黙って発番が止まる。
var Q_C_PID = "参加者ID（お持ちの方のみ）";
var Q_C_NAME = "お名前";
var Q_C_EMAIL = "メールアドレス";

// ============================================================
// G1-C 同意フォーム（consent.md が文面の真実源）
// ============================================================
// ★★ 説明文と同意項目は **この 2 つの関数だけが真実源**である。
//   ⚠️ buildConsentForm()（新規構築）と migrateConsentForm()（既存フォームへの差分適用）の
//      両方がここを見る。★ **文面を 2 か所に書かない。**
//      このプロジェクトは「片方だけ直して食い違わせる」事故を繰り返している。
//   ⚠️ 文面の真実源はさらに上流の consent.md である（先に consent.md を直し、ここへ写す）。
function consentFormTitle_() {
  return "GSE G1 統制タスク実験 — 説明・同意";
}

function consentFormDescription_() {
  return (
    "ご協力ありがとうございます。以下をお読みのうえ、ご回答ください。\n\n" +
      "▼ 何を調べる研究か\n" +
      "キーボードの打ち方から「作業がどれくらい詰まっているか」を推定できるかを調べています。" +
      "今回は難しさの違う書く課題を用意し、打ち方の違いが出るかを確かめます。\n\n" +
      "▼ お願いすること（約 70 分）\n" +
      "・全部で 10 ブロックあります。1 ブロックは 5 分、間に 1 分の休憩があります。\n" +
      "・★ 最初と最後の 1 ブロックずつは「書き写し」の課題です。考える必要はありません。\n" +
      "  これは計測器がちゃんと動いているかを確かめるための課題で、隠していることはありません。\n" +
      "・残りの 8 ブロックが本番です。資料を読んで 300〜400 字の文章を書いてもらいます。\n" +
      "・8 ブロックのうち 7 回、「直前のブロックと 1 つ前のどちらが詰まったか」を 1 つ選んでもらいます。\n" +
      "・★ 文章はこの実験専用の記入画面に打っていただきます（全員・毎回同じ画面／本文は保存されません）。\n" +
      "・★ 最後に短いアンケート（5 分ほど）にお答えいただきます。手続きの改善と記録のためのもので、" +
      "実験の判定には使いません。\n\n" +
      "▼ 記録するもの\n" +
      "・キーを押した時刻（ミリ秒）とキーの種類（文字キー / バックスペース / 空白 / 改行 など）\n" +
      "・日本語入力の変換にかかった時間\n" +
      "・貼り付けの回数と文字数（中身は取得しません）\n" +
      "・★ 記録を送った日時と、送信が成功したかどうか\n\n" +
      "▼ 記録しないもの（一切保存されません）\n" +
      "・★ あなたが書いた文章そのもの（実験者が文字数だけを数えます）\n" +
      "・どの文字を打ったか（本文の復元はできません）\n" +
      "・画面の内容・ウィンドウのタイトル・アプリ名・音声・映像\n" +
      "・★ 位置情報・端末の中の他のファイル・お使いの端末の種類\n\n" +
      "▼ ★ 記録の送られ方（毎回、あなたに確認します）\n" +
      "・★ 1 つのブロック（5 分）が終わるたびに、画面に「このブロックの記録を送信しますか？」と\n" +
      "  出ます。「送信する」を押したときだけ、その記録が研究者に送られます。\n" +
      "  ★ 押さない限り送られません。「あとで」を選ぶこともできます。\n" +
      "・★ 「あとで」を選んでも記録は消えません。端末に残るので、次のブロックの後にまとめて\n" +
      "  送れます。★ ただし最後まで送信しなければ研究者には届きません（端末に残るだけです）。\n" +
      "  その場合は研究者が後で直接受け取ります。\n" +
      "・★ 送られるのは暗号化されたファイルだけです。中身は研究者の鍵でしか開けません。\n" +
      "  途中で通る場所（インターネット上のサービス）では誰も中身を読めません。\n" +
      "・★ 送られるファイルに、あなたが書いた文章は入っていません。どの文字を押したかは、\n" +
      "  送られる前に「文字キー / バックスペース / 空白」のような種類に置き換えられます。\n" +
      "・送り先は研究者が管理する Google ドライブです（途中で Google のサービスを経由します）。\n" +
      "・送信のときに研究者の手元に残るのは「いつ送られたか」と「送れたかどうか」だけで、\n" +
      "  あなたの端末やアカウントを特定する情報は残りません。ただし、途中で通る Google の\n" +
      "  サービスが内部で何を記録しているかは研究者には確認できません（一般的なインターネット\n" +
      "  利用と同じです）。\n" +
      "・★ インターネットに接続していないと送れません。そのときは記録が端末に残り、あとで\n" +
      "  自動的に送り直します（送信を一度確認したものは、あらためて押す必要はありません）。\n" +
      "  画面に「まだ送れていない件数」が出ます。0 にならないまま\n" +
      "  終わった場合は研究者にお知らせください（記録は端末に残っています）。\n" +
      "・★ 送ったあとも、同じ記録があなたの端末に残ります。勝手に消すことはしません。\n" +
      "・★ なぜこの形にするのか: 予備の実施で、記録の一部が失われたことがありました。\n" +
      "  あなたの手間を省くためではなく、記録を確実に残すために、記録そのものは自動で\n" +
      "  作られます（ここは操作不要です）。★ ただし研究者へ送るかどうかは毎回あなたが決めます。\n\n" +
      "▼ リスクと負担\n" +
      "・身体的なリスクはありません。約 70 分の拘束と、書く作業による軽い疲労が負担です。\n" +
      "・★ 難しく感じるブロックがあります。それは設計上わざとそうしてあります。\n" +
      "  うまく書けなくても能力の評価ではありません。採点も比較もしません。\n\n" +
      "▼ 参加は任意です\n" +
      "断っても不利益はありません。途中でやめられ、理由の説明も要りません。" +
      "後からデータの削除を求められます（★ すでに送信されたものも対象です。" +
      "ただし公表済みの集計から個別に取り除くことはできません）。\n" +
      "・★ 送信をやめたいときは、確認の画面で「あとで」を選んでください。それだけで送られません" +
      "（記録は端末に残ります）。以後もずっと送りたくない場合は研究者にお知らせください。" +
      "送信を止める設定にしたうえで、記録を端末に残したまま進めることができます" +
      "（記録は研究者が後で直接受け取ります）。" +
      "★ 設定の変更は研究者が行いますので、お申し出からお手続きまでに時間がかかることがあります。\n\n" +
      "▼ 結果の使われ方\n" +
      "個人が特定できる形では公表しません。分析スクリプトや集計結果は公開される可能性がありますが、" +
      "そこに含まれるのは P0xx という記号と数値だけで、氏名・実施日時・本文は含みません。\n\n" +
      "▼ お問い合わせ先\n" +
      CONTACT_EMAIL
  );
}

// ★ consent.md の同意欄 8 項目をそのまま設問化する。★ **順序が意味を持つ**（挿入位置の基準）。
//   ⚠️ 2 と 3 は G1 固有（欺瞞を用いない・preregistration.md §2.8）。落とさないこと。
//   ⚠️ ★ 自動送信の 1 項目は 2026-08-07 に追加した（研究者判断 D-1 / D-4）。
//      consent.md 同意欄 / protocol.md §4.1-1 / 本ファイルの 3 箇所を同時に直すこと。
function consentItemTitles_() {
  return [
    "上の説明を読み、質問する機会がありました。",
    "★ 最初と最後のブロックが「書き写し」であることの説明を受けました。",
    "★ 一部のブロックが意図的に難しく作られていることの説明を受けました。",
    "書いた文章は保存されないことを理解しました。",
    "★ 最後に短いアンケートがあり、それは実験の判定には使われないことの説明を受けました。",
    "いつでも中断でき、後からデータの削除を求められることを理解しました。",
    "★ ブロックごとに送信の確認画面が出て、「送信する」を押したときだけ暗号化された記録がインターネット経由で送られることの説明を受けました。",
    "打鍵の記録（本文を除く）と、その研究利用に同意します。",
  ];
}

function buildConsentForm() {
  var form = openFixed_(FORM_ID_CONSENT, "FORM_ID_CONSENT");
  if (CLEAR_EXISTING) {
    assertSafeToRebuild_(form, "G1-C 説明・同意");
    clearForm(form);
  }

  form.setTitle(consentFormTitle_());
  form.setDescription(consentFormDescription_());
  form.setCollectEmail(false); // 下の設問で明示的に取る（何を取るかを本人に見せる）
  form.setShowLinkToRespondAgain(false);
  // ★ 募集でも当日でも使える文言にする（当日は実験者が同席している）。
  form.setConfirmationMessage(
    "ご回答ありがとうございます。参加者ID と当日のご案内をメールでお送りします。\n" +
      "（その場でご回答いただいた場合は、実験者にお知らせください。）"
  );

  addSectionHeader(
    form,
    "同意の確認",
    "以下のすべてに同意いただける場合のみ、参加をお願いします。"
  );

  consentItemTitles_().forEach(function (title) {
    var q = form.addCheckboxItem();
    q.setTitle(title);
    q.setChoices([q.createChoice("同意する / 理解した")]);
    q.setRequired(true);
  });

  addSectionHeader(
    form,
    "ご記名",
    "撤回のお申し出を受け付けるために必要です。ログとは別に保管し、P0xx とのみ結び付けます。"
  );
  // ★ P-ID は Phase1 と共有する（同じ人＝同じ ID）。以前ご参加の方は既にお持ちなので書いてもらう。
  //   ⚠️ 必須にしない — 初参加の方は持っていない（その場合は実験者が Phase1 側で採番する）。
  var pid = form.addTextItem();
  pid.setTitle(Q_C_PID);
  pid.setHelpText(
    "以前 GSE の検証にご参加いただいた方は、そのときお伝えした P から始まる記号をご記入ください。" +
      "初めての方は空欄で構いません。"
  );
  form.addTextItem().setTitle(Q_C_NAME).setRequired(true);
  var mail = form.addTextItem();
  mail.setTitle(Q_C_EMAIL);
  mail.setRequired(true);
  mail.setValidation(FormApp.createTextValidation().requireTextMatchesPattern(".+@.+").build());


  recordFormUrl_("G1_CONSENT", form, "G1-C 説明・同意");
  Logger.log("G1-C 同意フォームを構築した: " + form.getPublishedUrl());
}

// ============================================================
// ★★ G1-C を「作り直さずに」最新の文面へ揃える（差分適用・2026-08-07）
// ============================================================
// ⚠️ ★ **buildConsentForm() は CLEAR_EXISTING=true で全設問を削除して作り直す。**
//    公開済みフォームに既存回答があるとき、それをやると
//    **どの回答がどの設問へのものだったかが失われる**（同意記録なので取り返しがつかない）。
//    → ★ 本関数は **既存項目を消さず、足りないものだけを正しい位置に挿入する**。
//
// ★ 何度実行しても同じ状態になる（idempotent）:
//    - 既に在る同意項目は**触らない**（title 一致で判定）
//    - 無い項目だけを consentItemTitles_() の順序どおりの位置に挿入する
//    - 説明文・題名は毎回 consentFormDescription_() / consentFormTitle_() で上書きする
//
// ⚠️ ★ **設問の削除は一切行わない。** consentItemTitles_() から項目を消したとしても、
//    本関数は実フォームから消さない。★ 消すのは人間の判断であり、
//    「回答が消える操作」を自動化しない（`data-privacy` / 研究記録の保全）。
//    → 余分な項目が残っていないかは checkConsentFormParity() が**報告**する。
function migrateConsentForm() {
  var form = openFixed_(FORM_ID_CONSENT, "FORM_ID_CONSENT");

  form.setTitle(consentFormTitle_());
  form.setDescription(consentFormDescription_());

  var wanted = consentItemTitles_();
  var inserted = [];

  wanted.forEach(function (title, wantedIdx) {
    if (findItemByTitle_(form, title)) return; // 既に在る → 触らない

    // ★ 挿入位置: 「自分より前に在るべき項目」のうち実在する最後のものの直後。
    //   ⚠️ 実フォームの index で数える（コード側の配列 index で数えない）。
    //   ★ これが `runCol_` 型の「コード側だけ見て実物を見ない」バグの回避である。
    var anchorIndex = -1;
    for (var k = 0; k < wantedIdx; k++) {
      var prev = findItemByTitle_(form, wanted[k]);
      if (prev) anchorIndex = prev.getIndex();
    }
    if (anchorIndex < 0) {
      // 前に置くべき項目が 1 つも無い → 「同意の確認」セクションの直後に置く
      var header = findItemByTitle_(form, "同意の確認");
      anchorIndex = header ? header.getIndex() : 0;
    }

    var q = form.addCheckboxItem();
    q.setTitle(title);
    q.setChoices([q.createChoice("同意する / 理解した")]);
    q.setRequired(true);
    form.moveItem(q.getIndex(), anchorIndex + 1);
    inserted.push(title);
  });

  Logger.log(
    "G1-C を差分適用した: 挿入 " + inserted.length + " 件" +
      (inserted.length ? "\n  + " + inserted.join("\n  + ") : "（説明文の更新のみ）")
  );
  checkConsentFormParity(); // ★ 自分でログに出すので Logger.log で包まない (二重に出る)
  return inserted;
}

function findItemByTitle_(form, title) {
  var items = form.getItems();
  for (var i = 0; i < items.length; i++) {
    if (items[i].getTitle() === title) return items[i];
  }
  return null;
}

// ★★ 実フォームとコードのズレを **実物を読んで** 報告する（`browser-verification` §3）。
//    ⚠️ コード側の配列を数えるだけの検査は、コードと外界のズレを原理的に検出できない。
//    ★ 「順序」まで見る。⚠️ 同意項目は順序が意味を持つ（consent.md の並びと対応させる）。
function checkConsentFormParity() {
  var form = openFixed_(FORM_ID_CONSENT, "FORM_ID_CONSENT");
  var wanted = consentItemTitles_();
  var lines = [];

  var missing = wanted.filter(function (t) {
    return !findItemByTitle_(form, t);
  });
  if (missing.length) lines.push("❌ 不足 " + missing.length + " 件:\n  - " + missing.join("\n  - "));

  // 実フォーム上でのチェックボックス設問の並び（= 被験者が見る順序）
  var actual = form
    .getItems(FormApp.ItemType.CHECKBOX)
    .map(function (it) {
      return it.getTitle();
    });
  var extra = actual.filter(function (t) {
    return wanted.indexOf(t) < 0;
  });
  if (extra.length) {
    lines.push(
      "⚠️ コードに無い設問が実フォームに " + extra.length + " 件ある（★ 自動では消さない）:\n  - " +
        extra.join("\n  - ")
    );
  }

  var actualWanted = actual.filter(function (t) {
    return wanted.indexOf(t) >= 0;
  });
  if (actualWanted.join("") !== wanted.join("")) {
    lines.push("❌ 順序がコードと一致しない:\n  実物: " + actualWanted.join(" / ") + "\n  期待: " + wanted.join(" / "));
  }

  var descOk = form.getDescription() === consentFormDescription_();
  if (!descOk) lines.push("❌ 説明文がコードと一致しない");

  var n = form.getResponses().length;
  var msg = !lines.length
    ? "✅ G1-C はコードと一致している（同意項目 " + wanted.length + " 件・既存回答 " + n + " 件）"
    : "G1-C parity（既存回答 " + n + " 件）\n" + lines.join("\n");
  // ⚠️★★ **自分でログに出す。** 戻り値だけだと、エディタから ▶ で単独実行したときに
  //   実行ログが「実行開始 / 実行完了」だけになり、★ **判定が 1 文字も見えない**。
  //   （2026-08-07 に実際に起きた: 研究者が単独実行し、空ログを見て「通った」と読みかけた）
  //   ★ 手順書は「ログに ✅ が出ることを確認」と書いているので、コードをそれに合わせる。
  Logger.log(msg);
  return msg;
}

// ============================================================
// G1-M 強制比較フォーム（preregistration.md §2.6・★ 7 回答える）
// ============================================================
function buildManipulationCheckForm() {
  var form = openFixed_(FORM_ID_MCHECK, "FORM_ID_MCHECK");
  if (CLEAR_EXISTING) {
    assertSafeToRebuild_(form, "G1-M 強制比較");
    clearForm(form);
  }

  form.setTitle("GSE G1 — ブロック直後の 1 問");
  form.setDescription(
    "各ブロックが終わったら、そのブロックについて 1 問だけ答えてください。\n\n" +
      "★ 「どちらでもない」はありません。どちらか一方を必ず選んでください。\n" +
      "★ 良し悪しを聞いていません。詰まった感じがどちらで強かったかだけを答えてください。"
  );
  form.setCollectEmail(false); // ★ PII を取らない（被験者 ID のみ）
  // ★ 7 回答えるので「もう一度回答」リンクを残す。ブラウザを開き直す時間が休憩に収まらない。
  form.setShowLinkToRespondAgain(true);
  form.setConfirmationMessage("ありがとうございます。次のブロックまでお待ちください。");

  var sid = form.addTextItem();
  sid.setTitle(Q_SUBJECT_ID);
  sid.setHelpText("実験者から伝えられた P から始まる記号（例: P015）");
  sid.setRequired(true);
  sid.setValidation(FormApp.createTextValidation().requireTextMatchesPattern("P[0-9]+").build());

  // ★ ブロック番号は 3〜9 のみ。copy（1・10）と G1 の最初（2）には比較対象が無い（§2.6）。
  var blk = form.addMultipleChoiceItem();
  blk.setTitle(Q_BLOCK_NO);
  blk.setHelpText("いま終わったブロックの番号を選んでください。");
  blk.setChoices(
    [3, 4, 5, 6, 7, 8, 9].map(function (n) {
      return blk.createChoice(String(n));
    })
  );
  blk.setRequired(true);

  // ★ 二択のみ。★ 選択肢を**相対表現**にして、被験者にブロック番号を計算させない。
  //   （番号を答えさせると 1 つずれた転記が起きうる。ここは protocol.md §3.1 の紙と同じ文言。）
  var harder = form.addMultipleChoiceItem();
  harder.setTitle(Q_HARDER);
  harder.setHelpText(
    "いま終わったブロックと、その 1 つ前のブロックを比べてください。" +
      "より「詰まった / 手が止まった」のはどちらでしたか。"
  );
  harder.setChoices([harder.createChoice(CHOICE_PREV), harder.createChoice(CHOICE_CURRENT)]);
  harder.setRequired(true);

  recordFormUrl_("G1_MCHECK", form, "G1-M 強制比較（ブロック 3〜9 の直後）");
  Logger.log("G1-M 強制比較フォームを構築した: " + form.getPublishedUrl());
}

// ============================================================
// G1-S 終了後アンケート（preregistration.md §2.10・★ 判定には使わない）
// ============================================================
function buildPostSurveyForm() {
  var form = openFixed_(FORM_ID_SURVEY, "FORM_ID_SURVEY");
  if (CLEAR_EXISTING) {
    assertSafeToRebuild_(form, "G1-S 終了後アンケート");
    clearForm(form);
  }

  form.setTitle("GSE G1 — 終了後アンケート");
  form.setDescription(
    "お疲れさまでした。最後にいくつか伺います。\n\n" +
      "★ この回答は**実験の判定には使いません**（判定は打鍵の記録だけで行います）。" +
      "手続きの改善と、記録のために伺うものです。正解はありません。\n" +
      "答えたくない設問は飛ばして構いません。"
  );
  form.setCollectEmail(false); // ★ PII を取らない（被験者 ID のみ）
  form.setShowLinkToRespondAgain(false);
  form.setConfirmationMessage("ご協力ありがとうございました。");

  var sid = form.addTextItem();
  sid.setTitle(Q_SUBJECT_ID);
  sid.setRequired(true);
  sid.setValidation(FormApp.createTextValidation().requireTextMatchesPattern("P[0-9]+").build());

  // --- 1. デブリーフ / demand characteristics -------------------------------
  addSectionHeader(form, "1. この実験について", "思ったままで構いません。");
  form.addParagraphTextItem().setTitle("この実験は何を測っていると思いましたか。");
  var noticed = form.addMultipleChoiceItem();
  noticed.setTitle("ブロックによって難しさが違うと感じましたか。");
  noticed.setChoices([noticed.createChoice("感じた"), noticed.createChoice("感じなかった")]);
  form
    .addParagraphTextItem()
    .setTitle("そう感じた場合、どのあたりが違うと思いましたか（任意）。");

  // --- 1b. ★★ 事前にどれだけ読んだか（第 8 版 §2.12-4）---------------------
  // ⚠️★ **判定に使わない。除外にも使わない**（§3.6 無変更）。§3.8 の限界の記述に使う。
  //    §2.12（第 8 版）で課題文を来所前に開示したので、事前学習の量が
  //    被験者ごとにばらつく。⚠️ 強制できないので、せめて記録する。
  //    ⚠️ ★ **自己申告であり検証できない**ことも §3.8 に書いてある。
  addSectionHeader(
    form,
    "1b. 事前にお送りした資料について",
    "★ 正解はありません。**読んでいなくても全く問題ありません。**\n" +
      "⚠️ この回答で参加者を除外したり、評価を変えたりすることはありません。"
  );
  var preread = form.addMultipleChoiceItem();
  preread.setTitle(Q_S_PREREAD);
  preread.setChoices([
    preread.createChoice("開いていない"),
    preread.createChoice("ざっと目を通した"),
    preread.createChoice("一通り読んだ"),
    preread.createChoice("読んだうえで、書く内容も考えておいた"),
  ]);
  preread.setRequired(true);
  form.addParagraphTextItem().setTitle(Q_S_PREREAD_NOTE);

  // --- 2. ★ B-1 の実測（プローブが本当に出なかったか）----------------------
  // preregistration.md §2.6 は「アプリ内プローブを使わない」と凍結し、§5.4 の kill switch で
  // 止めている。★ ここは**主観側の裏取り**であり、客観検証は NDJSON 側で行う
  // （validate_blocks.py --dataset が probe_assignment 行 0 を検査する）。
  addSectionHeader(form, "2. アプリの挙動について", "気づいたことを教えてください。");
  var popup = form.addMultipleChoiceItem();
  popup.setTitle("書いている最中に、アプリから質問やお知らせが表示されましたか。");
  popup.setChoices([
    popup.createChoice("一度も出なかった"),
    popup.createChoice("出た"),
    popup.createChoice("覚えていない"),
  ]);
  popup.setRequired(true);
  form.addTextItem().setTitle("「出た」場合、だいたい何回でしたか（任意）。");

  // --- 3. 手続きの改善（§2.8 が改訂を許容する範囲）--------------------------
  addSectionHeader(form, "3. 課題と進め方について", "次回の改善に使います。");
  var len = form.addMultipleChoiceItem();
  len.setTitle("1 ブロック 5 分という長さはどうでしたか。");
  len.setChoices([len.createChoice("短い"), len.createChoice("ちょうどよい"), len.createChoice("長い")]);
  var amount = form.addMultipleChoiceItem();
  amount.setTitle("配られた資料の量はどうでしたか。");
  amount.setChoices([
    amount.createChoice("少ない"),
    amount.createChoice("ちょうどよい"),
    amount.createChoice("多い"),
  ]);
  form.addParagraphTextItem().setTitle("分かりにくかった課題文があれば教えてください（任意）。");

  // --- 4. ★ 入力パッドについて（B-5 の実測）--------------------------------
  // 入力先を固定したこと自体が統制である（bs_rate の汚染防止）。使い勝手が悪ければ
  // 統制を保ったまま直す必要があるので、P-1 で必ず聞く。
  addSectionHeader(form, "4. 記入パッドについて", "文章を書いた画面についてです。");
  var pad = form.addMultipleChoiceItem();
  pad.setTitle("普段お使いのエディタと比べて、書きにくさはありましたか。");
  pad.setChoices([
    pad.createChoice("特に無かった"),
    pad.createChoice("少しあった"),
    pad.createChoice("かなりあった"),
  ]);
  form.addParagraphTextItem().setTitle("あった場合、どんな点でしたか（任意）。");
  var counter = form.addMultipleChoiceItem();
  counter.setTitle("画面の文字数表示は気になりましたか。");
  counter.setChoices([
    counter.createChoice("気にならなかった"),
    counter.createChoice("ときどき見た"),
    counter.createChoice("ずっと気にしていた"),
  ]);

  // --- 5. 生態学的妥当性の記録（§3.8-4）------------------------------------
  addSectionHeader(form, "5. 普段の作業について", "");
  var howoften = form.addMultipleChoiceItem();
  howoften.setTitle("普段、今回のような論述（資料を読んでまとめる文章）を書く機会はありますか。");
  howoften.setChoices([
    howoften.createChoice("よくある"),
    howoften.createChoice("ときどきある"),
    howoften.createChoice("ほとんどない"),
  ]);

  recordFormUrl_("G1_SURVEY", form, "G1-S 終了後アンケート（判定には使わない）");
  Logger.log("G1-S 終了後アンケートを構築した: " + form.getPublishedUrl());
}

// ============================================================
// x.gd 短縮 URL（任意・Phase1 は手作業で作っていたものを自動化する）
// ============================================================
// ★ **API キーを .gs にもリポジトリにも置かない。** 本リポジトリは一時 public にする運用があるため。
//   キーは Apps Script の **Script Properties** に置く。設定は 1 回だけ、エディタで次を実行する:
//
//     function setXgdKey() {
//       PropertiesService.getScriptProperties().setProperty("XGD_API_KEY", "★ここにキー★");
//     }
//     ⚠️ 実行したらこの関数は消すこと（エディタのソースにキーが残る）。
//
// ★ キー未設定なら**何もしないで戻る**（壊れない）。短縮は運用の利便であって、
//   実施に必須ではない（G1 は対面実施で、実験者がブックマークから開く）。
var XGD_KEY_PROP = "XGD_API_KEY";
var XGD_ENDPOINT = "https://xgd.io/V1/shorten";

// 短縮 URL を Script Properties に覚えておくキー（リンク集タブが読む）。
function shortUrlProp_(key) {
  return "SHORTURL_" + key;
}

function getShortUrl_(props, key) {
  return props.getProperty(shortUrlProp_(key)) || "";
}

/**
 * ★ 3 フォームの「回答用 URL」を x.gd で短縮し、Script Properties に保存する。
 *
 * 冪等: **既に短縮済みのものは作り直さない**（毎回叩くと別の短縮 URL が量産され、
 * 被験者に配った URL と集計が読む URL がズレる — Phase1 の FormApp.create と同じ壊れ方）。
 * 作り直したいときは Script Properties の SHORTURL_* を消してから再実行する。
 */
function shortenFormUrls() {
  var props = PropertiesService.getScriptProperties();
  var key = props.getProperty(XGD_KEY_PROP);
  if (!key) {
    Logger.log(
      "ℹ️ " + XGD_KEY_PROP + " が未設定なので短縮しない（実施には支障なし）。\n" +
        "   設定する場合: PropertiesService.getScriptProperties()" +
        '.setProperty("' + XGD_KEY_PROP + '", "…") を 1 回だけ実行し、その関数を消すこと。'
    );
    return;
  }

  ["G1_CONSENT", "G1_MCHECK", "G1_SURVEY"].forEach(function (k) {
    if (getShortUrl_(props, k)) {
      Logger.log("· " + k + ": 既に短縮済みなので触らない（" + getShortUrl_(props, k) + "）");
      return;
    }
    var raw = props.getProperty("FORMURL_" + k);
    if (!raw) {
      Logger.log("· " + k + ": フォーム未生成のため飛ばす");
      return;
    }
    var published = JSON.parse(raw).publishedUrl;
    if (!published) {
      Logger.log("· " + k + ": publishedUrl が空のため飛ばす");
      return;
    }
    var url =
      XGD_ENDPOINT +
      "?key=" + encodeURIComponent(key) +
      "&url=" + encodeURIComponent(published) +
      "&analytics=false";
    var res = UrlFetchApp.fetch(url, { muteHttpExceptions: true });
    var body = res.getContentText();
    var json = null;
    try {
      json = JSON.parse(body);
    } catch (e) {
      /* JSON でない = API 側の異常 */
    }
    // ⚠️ ★ 失敗を黙って飛ばさない。status を見ずに body を保存すると
    //    「短縮したつもりでエラー文字列を配る」事故になる。
    if (!json || json.status !== 200 || !json.shorturl) {
      Logger.log(
        "❌ " + k + ": 短縮に失敗した (HTTP " + res.getResponseCode() + ") — " +
          (json && json.message ? json.message : body.slice(0, 200))
      );
      return;
    }
    props.setProperty(shortUrlProp_(k), json.shorturl);
    Logger.log("✅ " + k + ": " + json.shorturl + "  →  " + published);
  });

  Logger.log("★ リンク集タブへ反映するには buildManagementSheet() を実行する。");
}

/** 短縮 URL を捨てて作り直せるようにする（配布前にだけ使うこと）。 */
function clearShortUrls() {
  var props = PropertiesService.getScriptProperties();
  ["G1_CONSENT", "G1_MCHECK", "G1_SURVEY"].forEach(function (k) {
    props.deleteProperty(shortUrlProp_(k));
  });
  Logger.log("🧹 短縮 URL を消した。⚠️ 既に配布済みなら、配った URL は生きたまま残る。");
}

// ============================================================
// 運用管理シート（Phase1 の buildManagementSheet と同じ型・★ 2 タブだけ）
// ============================================================
// Phase1 は「リンク集 / 参加者ロスター / セッション提出トラッキング / 進捗ダッシュボード」の
// 4 タブを持つ。★ G1 は **リンク集 / G1 実施トラッキング の 2 タブだけ**にする:
//   - **参加者ロスターを作らない** — P-ID と実名の対応表は Phase1 側が真実源だから（上記）。
//     2 か所に持つと必ずずれるうえ、PII の複製が増える。
//   - **進捗ダッシュボードを作らない** — G1 は 1 人 1 回の実施機会で完結するので、
//     Phase1 のような長期追跡の集計値（平均セッション数・継続率）に意味が無い。
function buildManagementSheet() {
  var props = PropertiesService.getScriptProperties();
  var ss = null;
  var ssId = props.getProperty(MGMT_SHEET_PROP_G1);
  if (ssId) {
    try {
      ss = SpreadsheetApp.openById(ssId);
    } catch (e) {
      ss = null; // 削除済み等 → 作り直す
    }
  }
  if (!ss) {
    ss = SpreadsheetApp.create("GSE G1 運用管理シート");
    props.setProperty(MGMT_SHEET_PROP_G1, ss.getId());
  }

  buildLinksTab_(ss, props); // 毎回 URL を再集約（手動入力セルは保持する）
  buildRunTab_(ss); // 既存があれば作らない（入力データを破壊しない）
  applyRunValidation_(ss); // 最後: ドロップダウン（型付き列に起因する読込順の事故を避ける）

  ["シート1", "Sheet1"].forEach(function (n) {
    var s = ss.getSheetByName(n);
    if (s && ss.getSheets().length > 1) ss.deleteSheet(s);
  });

  Logger.log("✅ G1 管理シート作成/更新完了");
  Logger.log("🔗 " + ss.getUrl());
  return ss.getUrl();
}

// リンク集: 3 フォームの URL を集約する。手動入力セル（B4/B5）は毎回退避して保持する。
function buildLinksTab_(ss, props) {
  var sh = ss.getSheetByName("リンク集") || ss.insertSheet("リンク集", 0);
  var prevPad = "";
  var prevDataset = "";
  try {
    prevPad = sh.getRange(4, 2).getValue();
    prevDataset = sh.getRange(5, 2).getValue();
  } catch (e) {
    /* 初回は空 */
  }
  sh.clear();
  var rows = [
    ["GSE G1 リンク集", "", "", ""],
    ["", "", "", ""],
    ["項目", "値 / URL", "種別", "備考"],
    [
      "ブロックページ (pages/<P-ID>/blockNN.html) の置き場",
      prevPad || "",
      "手動",
      "★ 課題文と記入欄を 1 画面にしたページ。**紙配布は 2026-08-03 に廃止した** (第 7 版 §2.13)。" +
        "実施前に `python3 build_task_pages.py --subject <P-ID>` で生成し、実施端末にコピーする。" +
        "⚠️ ブロック開始時に **そのブロックのファイルだけ**を、拡張機能なしのプロファイルで開く " +
        "(protocol.md §1.2)。次のファイルを先に開くと先読みで打鍵量の測定が壊れる",
    ],
    [
      "gse-dataset への送付先",
      prevDataset || "",
      "手動",
      "⚠️ G1 のセッションであることを明示して送る (data.md の B-4)。" +
        "第1週モードで回すため label_pool が Phase1 の較正と同じになる",
    ],
    ["", "", "", ""],
    ["フォーム", "タイトル", "編集URL", "回答URL（短縮があれば短縮版）"],
  ];
  ["G1_CONSENT", "G1_MCHECK", "G1_SURVEY"].forEach(function (k) {
    var raw = props.getProperty("FORMURL_" + k);
    // 回答 URL 列は短縮版(x.gd)を優先し、未作成なら publishedUrl にフォールバックする
    // （Phase1 の buildLinksTab_ と同じ考え方）。
    var shortUrl = getShortUrl_(props, k);
    if (raw) {
      var o = JSON.parse(raw);
      rows.push([k + "｜" + o.label, o.title, o.editUrl, shortUrl || o.publishedUrl]);
    } else {
      rows.push([k, "（未生成 — setupG1Forms を実行）", "", shortUrl]);
    }
  });
  rows.push(["", "", "", ""]);
  rows.push([
    "★ P-ID の採番元",
    "Phase1 運用管理シートの「参加者ロスター」",
    "参照",
    "⚠️ G1 では採番しない。同じ人には同じ P-ID を使う。新規は Phase1 側で採番してから回す",
  ]);
  sh.getRange(1, 1, rows.length, 4).setValues(rows);
  sh.getRange(1, 1).setFontWeight("bold").setFontSize(14);
  sh.getRange(3, 1, 1, 4).setFontWeight("bold");
  sh.getRange(7, 1, 1, 4).setFontWeight("bold");
  sh.setColumnWidth(1, 260);
  sh.setColumnWidth(2, 340);
  sh.setColumnWidth(3, 320);
  sh.setColumnWidth(4, 320);
}

// G1 実施トラッキングの列（1 被験者 1 行）。★ 実名・メールを持たない。
// ⚠️ ブロックごとの条件・題材・NDJSON 名は **ここに書かない**。
//    ラベルの真実源は記録用紙 → blocks/P0xx.json であり、二重に持つと必ずずれる
//    (protocol.md §2.3-1「転記は 1 方向だけ」)。
var RUN_HEADER = [
  "P-ID",
  // ★ 募集・日程調整。⚠️ 実名・メールはここに書かない。
  //   実名↔P-ID の対応表は Phase1 のロスターと G1-C 回答シートが真実源である。
  //   ⚠️ 「事前案内メール送信日」列は廃止した（事前案内メールを廃止したため・2026-08-03）。
  "実施予定日",
  "G1-C 同意",
  // ★★ 2026-08-07: 配布フォルダ（課題ページ）の URL。★ 研究者が貼る**唯一の手入力**であり、
  //    g1AutoSendPendingMaterials() の引き金でもある（貼られるまで送らない）。
  // ⚠️ ★ 第 8 版のコメントは「URL 自体はここに書かない（割付が推測されうる）」としていたが、
  //    2026-08-07 に**方針を変えた**。理由を隠さず書く:
  //      (a) Apps Script の関数セレクタは**引数を渡せない**。3 引数の sendTaskMaterialsEmail は
  //          研究者がラッパーを手書きしないと実行できず、そこが手作業として残っていた。
  //      (b) このシートは研究者しか開かない（実名・メールを持たないのは別の理由 = 匿名化）。
  //      (c) ★ URL は Drive の不透明な ID であって、**それ自体は割付を露呈しない**。
  //          露呈するのはリンク先の中身であり、それは被験者本人には元から開示している（§2.12）。
  //    ⚠️ ★ したがって「このシートを被験者や第三者に見せない」ことが前提条件である。
  "配布フォルダURL",
  // ★★ 第 8 版（2026-08-04）: 課題文の閲覧リンクを事前に送る（preregistration.md §2.12）。
  //    いつ送ったかを残す。★ 空 = 未送信。g1AutoSendPendingMaterials() の冪等キーである。
  "課題文リンク送信日",
  "実施日",
  // ★★ 第 9 版（2026-08-04）: 実施形態を共変量として記録する（preregistration.md §2.14）。
  //    ⚠️ **判定にも除外にも使わない**（§3.6 無変更）。報告時に内訳を併記するための列である。
  //    ⚠️ ここが無いと §2.14-3 の報告義務に対して**保存先が存在しない**ことになる
  //       （2026-08-04 の cross-review で Codex が指摘）。
  "実施形態",
  "実施OS",
  "アプリのビルド",
  "GSE_DISABLE_PROBES=1",
  "HMM_VERSION",
  "配置(A/B)",
  "完了ブロック数(/10)",
  "G1-M 回答数(/7)",
  "G1-S 回答",
  "verify-blocks 実施",
  "validate_blocks 緑",
  "gse-dataset 送付",
  "撤回/除外",
  "備考",
];

// ★★ 実シートのヘッダ行（row 2）と RUN_HEADER が一致しているか。
//   ⚠️ **runCol_ は「コード側の RUN_HEADER」しか見ない。** 実シートのヘッダが古いままだと、
//      列名で引いているのに**実シートでは別の列を指す**。
//   ★ 2026-08-03 に実際に起きた: 旧版で作られた 16 列のシート（実施予定日なし）に対し、
//      17 列の RUN_HEADER で applyRunValidation_ を回したため、
//      **日付列「実施日」に「はい/いいえ」のドロップダウンが付いた**（実測・スクリーンショット確認）。
//   → 黙ってずらさず、**ここで止める**。
function runHeaderDiff_(sh) {
  var live = sh.getRange(2, 1, 1, Math.max(sh.getLastColumn(), RUN_HEADER.length)).getValues()[0];
  var diff = [];
  for (var i = 0; i < RUN_HEADER.length; i++) {
    var a = String(RUN_HEADER[i]);
    var b = String(live[i] === undefined ? "" : live[i]).trim();
    if (a !== b) diff.push("col" + (i + 1) + ": コード='" + a + "' / シート='" + b + "'");
  }
  return diff;
}

function assertRunHeader_(sh) {
  var diff = runHeaderDiff_(sh);
  if (diff.length) {
    throw new Error(
      "★ 「G1 実施トラッキング」のヘッダがコードの RUN_HEADER と一致しません。\n" +
        "⚠️ このまま進めると runCol_ が**別の列**を指し、入力規則や備考が静かにずれます。\n" +
        diff.join("\n") +
        "\n→ データが無ければ setupG1Forms() が自動で作り直します。" +
        "データがある場合は、列を手で合わせてから再実行してください。"
    );
  }
}

function buildRunTab_(ss) {
  var exist = ss.getSheetByName("G1 実施トラッキング");
  if (exist) {
    var diff = runHeaderDiff_(exist);
    if (!diff.length) return; // 一致している = 何もしない（入力データを破壊しない）
    // ★ ヘッダが古い。データが無いときだけ作り直す（データがあれば人が判断する）。
    var used = exist.getLastRow() > 2
      ? exist.getRange(3, 1, exist.getLastRow() - 2, 1).getValues().filter(function (r) {
          return String(r[0]).trim() !== "";
        })
      : [];
    if (used.length) {
      throw new Error(
        "★ 「G1 実施トラッキング」のヘッダが古いのに、データが " + used.length + " 行あります。\n" +
          diff.join("\n") +
          "\n⚠️ 勝手に列をずらすと記録が壊れるので中止しました。手で列を合わせてから再実行してください。"
      );
    }
    Logger.log("⚠️ ヘッダが古いのでタブを作り直します（データ行 0）: " + diff.join(" / "));
    ss.deleteSheet(exist); // ★ 古い入力規則ごと消す（残すと新旧の規則が二重に付く）
  }
  var sh = ss.insertSheet("G1 実施トラッキング");
  // 行1: 注意バナー。★ ここに何を書いてはいけないかを、シートの上で明示する。
  sh.getRange(1, 1).setValue(
    "⚠ P-ID は Phase1 と共有（同じ人＝同じ ID）。採番は Phase1 の参加者ロスターで行う。" +
      "★ 実名・メールをこのシートに書かない（Phase1 ロスターと G1-C 回答が真実源）。" +
      "★ ブロックごとの条件・題材・NDJSON 名も書かない（記録用紙 → blocks/P0xx.json が真実源）。"
  );
  sh.getRange(1, 1, 1, RUN_HEADER.length).merge();
  sh.getRange(1, 1)
    .setFontWeight("bold")
    .setFontColor("#ffffff")
    .setBackground("#b71c1c")
    .setWrap(true);
  sh.getRange(2, 1, 1, RUN_HEADER.length).setValues([RUN_HEADER]).setFontWeight("bold");
  sh.setFrozenRows(2);
  sh.setColumnWidth(1, 70);
  sh.setColumnWidth(runCol_("備考"), 260);
}

// ★ ヘッダ名 → 列番号（1 始まり）。
//   ⚠️ 列番号をハードコードしない。第 6 版で列を 2 つ足したときに、
//      ハードコードしていた applyRunValidation_ の入力規則が**全部 1 つずつズレた**。
//      ズレても画面上はドロップダウンが「別の列」に付くだけで、静かに間違う。
function runCol_(header) {
  var i = RUN_HEADER.indexOf(header);
  if (i < 0) {
    throw new Error("★ RUN_HEADER に列 '" + header + "' がありません（列名を変えたら参照側も直す）");
  }
  return i + 1;
}

// 取り違えを減らすためのドロップダウン。★ 判定に関わる列は 1 つも無い（運用の記録だけ）。
function applyRunValidation_(ss) {
  var sh = ss.getSheetByName("G1 実施トラッキング");
  if (!sh) return;
  assertRunHeader_(sh); // ★ ずれたまま規則を貼らない（上のコメント参照）
  var rows = 200;
  // ★ 先に全部消す。⚠️ 消さないと、列構成を変えたときに**旧位置の規則が残って二重に付く**
  //   （2026-08-03 実測: B〜G 列すべてにドロップダウンが付いた状態になっていた）。
  sh.getRange(3, 1, rows, RUN_HEADER.length).clearDataValidations();
  function listRule(values) {
    return SpreadsheetApp.newDataValidation().requireValueInList(values, true).build();
  }
  function apply(header, values) {
    sh.getRange(3, runCol_(header), rows, 1).setDataValidation(listRule(values));
  }
  var yn = ["はい", "いいえ"];
  apply("G1-C 同意", yn);
  apply("実施形態", ["来所", "無人在宅"]);
  apply("実施OS", ["Windows 11", "macOS"]);
  apply("GSE_DISABLE_PROBES=1", yn);
  apply("配置(A/B)", ["A", "B"]);
  apply("G1-S 回答", yn);
  apply("verify-blocks 実施", yn);
  apply("validate_blocks 緑", yn);
  apply("gse-dataset 送付", yn);
  apply("撤回/除外", ["", "撤回", "除外"]);
}

// ============================================================
// 共通ユーティリティ（Phase1 builder と同じ型）
// ============================================================

// ★ 固定 ID 方式のガード。空 ID のまま走らせるとフォームを量産するので**止める**。
function openFixed_(id, varName) {
  if (!id) {
    throw new Error(
      "★ " + varName + " が空です。フォームを量産しないため停止しました。\n" +
        "先に Google Forms で空フォームを作り、編集 URL\n" +
        "  https://docs.google.com/forms/d/<ここ>/edit\n" +
        "の <ここ> を " + varName + " に貼ってから再実行してください。"
    );
  }
  return FormApp.openById(id);
}

// 分岐ナビゲーションを先に解除してから末尾削除する。
// 直接 deleteItem すると go-to-page 参照が残って "Invalid data updating form" になる。
function clearForm(form) {
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

function addSectionHeader(form, title, description) {
  var section = form.addSectionHeaderItem();
  section.setTitle(title);
  if (description) section.setHelpText(description);
}

function recordFormUrl_(key, form, label) {
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
// 募集・日程調整の自動化（第 6 版・研究者判断 2026-08-03）
// ============================================================
// ★ preregistration.md §2.12 が「事前案内で何を開示し、何を伏せるか」を凍結している。
//   本節はその実装であり、**文面を変えるときは §2.12 の表と突き合わせること。**
//   ⚠️ このプロジェクトは「文書だけ改訂して実装が追随しない」事故を繰り返している
//      (.steering/20260802-g1-execution-prep/decisions.md E-6 / E-7)。
//
// ⚠️⚠️ P-1（パイロット）では使わない。研究者本人が被験者であり課題文の作成者である（§2.12-5）。

// ★★ Phase1 の運用管理シート ID（参加者ロスターがあるスプレッドシート）。
//    採番元は **Phase1 のロスターただ 1 つ**である（protocol.md §2.0 / Form_G1/README.md）。
//    ⚠️ G1 側で採番すると 2 か所採番になり、相手の最大値が見えないので**必ず衝突する**。
//    URL の /spreadsheets/d/<ここ>/edit の <ここ> を貼る。空なら採番系は動かない（fail-closed）。
//
// ⚠️★★ **Drive に「【非公開】GSE_Phase1_運用管理シート」が 2 つある**（2026-08-03 実測）。
//    取り違えると **P-ID が既存参加者と衝突する**ので、下の ID を勝手に差し替えないこと。
//      ✅ 1ND5HSXZ...  参加者ロスター = P006..P014（現行・最終更新 2026-08-03）→ 次は P015
//      ❌ 12T8WU4D...  参加者ロスター = P001..P008（古い・最終更新 2026-06-28）
//         → こちらを指すと g1NextParticipantId_ が **P009 を返し、実在する P009..P014 と衝突する**。
//    ★ 見分け方: 「参加者ロスター」タブに **P010 以降が入っているほうが正**。
var PHASE1_MGMT_SHEET_ID = "1ND5HSXZcD_9vHjKAcM8K8Ow9VFVVwuP4L3pulP6ud7Y";

// ★ true にすると MailApp で自動送信する。既定は false（GmailApp で下書きを作る）。
//   ⚠️ Phase1 は AUTO_SEND=true で運用しているが、G1 は**対面・少人数**なので既定を下書きにした。
//      メール送信は取り消せない。文面を一度目で確認してから true にすること。
// ⚠️ ★ 2026-08-03 の研究者判断で **true**（実送信）に切り替えた。
//    登録直後に受付メールが届かないと、被験者は P-ID を知らないまま待つことになる。
//    ⚠️ 送信は取り消せない。文面を変えたら previewRegisterAckEmail() で必ず先に確認する。
var G1_AUTO_SEND = true;

// 連絡先（★ 実施前に埋める）。空欄のままだと受付メールが止まる（fail-closed）。
// ⚠️ ★ 日時・場所はメールに書かない（研究者判断 2026-08-03）。対面 1 回きりなので、
//    日程の確定連絡は研究者が普通に返信するほうが早く、自動化する価値が無い。
var G1_CONTACT = "三浦尊統（mmiura.network@gmail.com）"; // 研究者判断 2026-08-03
// ⚠️ ★ consent.md §8「所属・連絡先（実施前に記入）」を埋めるときは、**ここと同じ文字列**にする。
//    片方だけ直すと、同意文書とメールで連絡先が食い違う。

// ⚠️ ★ 第 6 版にあった G1_TOPIC_TITLES（課題の分野を事前案内メールに載せる）は
//    **第 7 版で撤回した**。課題文は当日その場で画面提示する（§2.13）ので、
//    事前に題材を教える必要が無い。→ §2.6 の操作チェックが元の強さに戻る。
//    ⚠️ ★ **題材名をこのファイルに書き戻さないこと。**
//       scripts/check_g1_topic_titles.py がメール本文に題材名が混ざっていないかを検査する。

// ------------------------------------------------------------
// P-ID の採番（★ Phase1 のロスターに対して行う）
// ------------------------------------------------------------
// Phase1 の nextParticipantId_ と同じ規則（P + 3 桁ゼロ埋め・既存の最大値 + 1）。
// ⚠️ ★ 実装を 2 つ持つことになるので、**規則を変えるときは両方**（Form_Phase1 側が正）。
function g1NextParticipantId_(sheet) {
  var max = 0;
  var last = sheet.getLastRow();
  var values = last > 1 ? sheet.getRange(1, 1, last, 1).getValues() : [];
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

// G1 の新規参加者に P-ID を採番し、**Phase1 のロスターに 1 行追加**して返す。
// ★ 既に Phase1 に参加した人はここを通さない。その人の既存 P-ID をそのまま使う（§2.0）。
function assignG1ParticipantId() {
  if (!PHASE1_MGMT_SHEET_ID) {
    throw new Error(
      "★ PHASE1_MGMT_SHEET_ID が空です。採番元は Phase1 の参加者ロスターただ 1 つなので、\n" +
        "Phase1 の運用管理シートの ID を .gs に貼ってから実行してください。\n" +
        "⚠️ G1 側にロスターを作って採番すると、2 か所採番になり必ず衝突します。"
    );
  }
  var ss = SpreadsheetApp.openById(PHASE1_MGMT_SHEET_ID);
  var sheet = ss.getSheetByName("参加者ロスター");
  if (!sheet) {
    throw new Error("★ Phase1 の管理シートに「参加者ロスター」タブがありません。ID を確認してください。");
  }
  var pid = g1NextParticipantId_(sheet);
  sheet.appendRow([pid]);
  Logger.log("✅ P-ID を採番しました: " + pid + "（氏名・メールは Phase1 ロスターに手入力）");
  Logger.log("🔗 " + ss.getUrl());
  return pid;
}

// ログに実アドレスを残さない（data-privacy）。Phase1 の maskEmail_ と同じ考え方。
function g1MaskEmail_(email) {
  var s = String(email);
  var at = s.indexOf("@");
  if (at <= 1) return "***";
  return s.charAt(0) + "***" + s.substring(at);
}

// 終了後のお礼（★ 任意。デブリーフ資料は当日紙で渡す。結果概要の送付希望者向け）。
function sendThankYouEmail(pid, email) {
  if (!pid || !email) throw new Error("★ pid と email は必須です。");
  if (!G1_CONTACT) throw new Error("★ G1_CONTACT が空です。");
  var subject = "【御礼】研究へのご参加ありがとうございました";
  var body = [
    "本日はご参加いただきありがとうございました（参加者ID: " + pid + "）。",
    "",
    "当日お渡しした説明のとおり、記録したのはキーを押した時刻とキーの種類、",
    "日本語変換にかかった時間、書いた文字数だけです。",
    "★ お書きいただいた文章そのものは保存していません。",
    "",
    "★ お願い: 同じ課題をこれから参加される方にも使います。",
    "  課題の中身（どんな資料が出たか・どちらが難しかったか）は、",
    "  参加予定のある方にはお話しにならないようお願いします。",
    "",
    "結果がまとまりましたら、ご希望の方には概要をお送りします。",
    "記録の削除をご希望の場合は、いつでもこのメールにご返信ください。",
    "",
    G1_CONTACT,
  ].join("\n");
  if (G1_AUTO_SEND) {
    MailApp.sendEmail(email, subject, body);
    Logger.log("📧 送信しました: " + pid);
  } else {
    GmailApp.createDraft(email, subject, body);
    Logger.log("📝 下書きを作成しました: " + pid);
  }
  return subject;
}

// Phase1 ロスターを P-ID またはメールで引く。見つかれば {pid, row} を返す。
function g1FindInPhase1Roster_(sheet, opts) {
  var last = sheet.getLastRow();
  if (last < 1) return null;
  var rows = sheet.getRange(1, 1, last, 3).getValues(); // P-ID / 氏名 / メール
  var email = opts.email ? String(opts.email).trim().toLowerCase() : "";
  var pid = opts.pid ? String(opts.pid).trim().toUpperCase() : "";
  for (var i = 0; i < rows.length; i++) {
    var rowPid = String(rows[i][0]).trim().toUpperCase();
    var rowEmail = String(rows[i][2]).trim().toLowerCase();
    if (pid && rowPid === pid) return { pid: rowPid, row: i + 1 };
    if (email && rowEmail && rowEmail === email) return { pid: rowPid, row: i + 1 };
  }
  return null;
}

// G1 実施トラッキングに P-ID の行が無ければ作る。備考セル（失敗の可視化先）を返す。
function g1EnsureRunRow_(pid) {
  var props = PropertiesService.getScriptProperties();
  var ssId = props.getProperty(MGMT_SHEET_PROP_G1);
  if (!ssId) {
    Logger.log("⚠️ G1 管理シートが未作成なのでトラッキング行は作れません（buildManagementSheet() を実行）");
    return null;
  }
  var sh = SpreadsheetApp.openById(ssId).getSheetByName("G1 実施トラッキング");
  if (!sh) return null;
  // ★ ヘッダがずれていると「備考」が別の列（見出しの無い列）に書かれ、
  //   送信失敗のフラグを研究者が**見つけられなくなる**。ずれていたら行を作らず記録に残す。
  //   ⚠️ ここで throw すると onG1ConsentSubmit の採番まで巻き戻るので、null を返して続行させる
  //      （P-ID の発番と受付メールのほうが優先度が高い）。
  try {
    assertRunHeader_(sh);
  } catch (headerErr) {
    Logger.log("❌ トラッキング行を作れません（ヘッダ不一致・setupG1Forms を再実行）: " + headerErr);
    return null;
  }

  var colPid = runCol_("P-ID");
  var colNote = runCol_("備考");
  var last = sh.getLastRow();
  for (var r = 3; r <= last; r++) {
    if (String(sh.getRange(r, colPid).getValue()).trim().toUpperCase() === pid) {
      return sh.getRange(r, colNote); // 既にある（再登録）
    }
  }
  var row = Math.max(last + 1, 3);
  sh.getRange(row, colPid).setValue(pid);
  return sh.getRange(row, colNote);
}

function g1RegisterAckSubject_() {
  return "【受付】キーボードの打ち方に関する研究 — 参加登録を承りました";
}

// ★ 受付メール。⚠️ preregistration.md §2.12 の開示範囲を守る:
//   題材（分野）・課題の型・難易度の示唆・条件名を **書かない**。
//   （課題文は当日その場で画面提示する = §2.13。事前に教える必要が無い。）
function g1RegisterAckBody_(pid) {
  return [
    "ご登録ありがとうございます。参加登録を承りました。",
    "",
    "■ あなたの参加者ID（P-ID）",
    "    " + pid,
    "    ※ 記録はこの記号で管理します。お名前とは別に保管します。",
    "    ※ 当日までこのメールを保管してください。",
    "",
    "■ 当日の流れ（約 70 分）",
    "    ・5 分の作業を 10 回、間に 1 分の休憩をはさみます。",
    "    ・最初と最後の 1 回ずつは「書き写し」です。考える必要はありません。",
    "      これは計測器が正しく動いているか確かめるための課題で、隠していることはありません。",
    "    ・間の 8 回は、資料を読んで 300〜400 字の文章を書いていただきます。",
    "    ・途中で 7 回、「直前の回と 1 つ前の回のどちらが詰まったか」を 1 つだけ選んでいただきます。",
    "    ・最後に短いアンケート（5 分ほど）にお答えいただきます。",
    "",
    // ★★ 第 8 版（2026-08-04）: 課題文の本文を来所前に開示する（preregistration.md §2.12）。
    //    ⚠️ 本文そのものはメールに書かず、**別便の閲覧リンク**で渡す
    //       （sendTaskMaterialsEmail）。理由は 2 つ:
    //       (a) 登録時点ではまだ割付を作っていない（どの題材が出るか決まっていない）
    //       (b) ★ メール本文に題材名を書くと、書いた順序が **提示順** を示唆しうる。
    //          §2.12 は提示順を「開示しない」側に置いている。
    //    ⚠️ ★ **題材名をこのメール本文に書き戻さないこと。**
    //       scripts/check_g1_emails.py が両方のメールを同じ基準で検査する。
    "■ 課題の内容について",
    "    ★ 当日お読みいただく資料は、**事前にメールでお送りします**（別便）。",
    // ★ 第 9 版（§2.14）: 在宅実施があるので「お越し」と書かない。
    "      目を通しておいていただいて構いませんし、読まずに当日を迎えても構いません。",
    "      ⚠️ どちらでも問題ありません。**準備の量で評価することはありません。**",
    "    ・専門知識は要りません。ふだんの生活の感覚で判断できる話題だけを使っています。",
    "    ・資料はすべて本実験のために作成した架空のものです。",
    "      ★ 数値・地名・調査結果は実在しません。外部で事実として引用しないでください。",
    "    ・課題文は当日も画面に表示されます。同じ画面で文章を書いていただきます。",
    "",
    "■ 記録するもの / しないもの",
    "    記録する: キーを押した時刻とキーの種類、日本語変換にかかった時間、書いた文字数",
    "    記録しない: ★ どの文字を打ったか（本文）、画面の内容、音声・映像",
    // ⚠️ ★ 紙署名は 2026-08-03 に廃止した（D-1(a)）。このフォーム（G1-C）の回答が同意の正本である。
    //    ⚠️ ここを「署名をお願いします」に戻すと、protocol.md §4.1-1 / consent.md /
    //       Form_G1/README.md と食い違う。**4 か所を同時に直すこと。**
    "    ※ 書いた文章そのものは保存しません。ご同意はこのフォームの回答で完了しています。",
    "",
    "■ 当日までにお願いしたいこと",
    "    ・日本語入力（IME）は、ふだん使っている設定のままにしてください。",
    "    ・当日は携帯電話の電源を切ってください。",
    "",
    "■ 参加は任意です",
    "    途中でやめられます。理由の説明は要りません。終わった後でも記録の削除を求められます。",
    "",
    "ご不明な点があれば、このメールにご返信ください。",
    G1_CONTACT,
  ].join("\n");
}

// ★ 送信前に内容を確認する（引数なし・送信しない）。
function previewRegisterAckEmail() {
  Logger.log("件名: " + g1RegisterAckSubject_());
  Logger.log("--------");
  Logger.log(g1RegisterAckBody_("P0XX"));
  Logger.log("--------");
  Logger.log("★ §2.12 の開示範囲と一致しているか確認（題材・課題の型・難易度を書かない）。");
  Logger.log("");
  Logger.log("件名: " + g1MaterialsSubject_());
  Logger.log("--------");
  Logger.log(g1MaterialsBody_("P0XX", "https://example.com/★閲覧専用リンク★"));
  Logger.log("--------");
  Logger.log("★ こちらも同じ基準（題材名・課題の型・条件名・提示順を書かない）。");
}

// ============================================================
// ★★ 課題文の事前開示（第 8 版・2026-08-04・preregistration.md §2.12）
// ============================================================
// ⚠️ ★ **これは判定を緩める可能性のある変更である。** 第 8 版の改訂履歴に向きごとに記録した。
//    ここは実装であって根拠ではない。文面を変えるときは §2.12 の表と突き合わせること。
//
// ⚠️⚠️ **自動化しない。** 送るのは研究者が明示的に実行したときだけである。理由:
//   (a) 登録時点では割付が無く、その被験者にどの題材が出るか決まっていない
//   (b) ★ 閲覧専用ドキュメントを作る手作業（権限設定）が必ず挟まる
//   (c) 送信は取り消せない。⚠️ ★ **URL を取り違えると別の被験者の割付を渡すことになる**
//
// ⚠️ ★ **本文に題材名・課題の型・条件名・提示順を書かない。** 中身はリンク先にある。
//    scripts/check_g1_emails.py が受付メールと同じ基準で本文を検査する。

function g1MaterialsSubject_() {
  return "【事前資料】キーボードの打ち方に関する研究 — 当日お読みいただく資料";
}

function g1MaterialsBody_(pid, url) {
  return [
    "当日お読みいただく資料をお送りします。",
    "",
    "■ 参加者ID（P-ID）",
    "    " + pid,
    "",
    "■ 資料（閲覧のみ）",
    "    " + url,
    "",
    "■ お願い",
    "    ★ 目を通しておいていただいて構いませんし、読まずに当日を迎えても構いません。",
    "      ⚠️ **準備の量で評価することはありません。** どちらでも問題ありません。",
    "    ・当日は同じ内容が画面にも表示されます。手元に印刷する必要はありません。",
    "    ・終わったあとのアンケートで「事前にどのくらい読んだか」を伺います。",
    "      ★ 正解はありません。**実験の判定には使いません。**",
    "",
    "■ 資料について",
    "    ・すべて本実験のために作成した架空のものです。",
    "      ★ 数値・地名・調査結果は実在しません。外部で事実として引用しないでください。",
    "    ・★ **他の方に見せないでください。** 同じ資料を他の参加者にもお願いしています。",
    "",
    "ご不明な点があれば、このメールにご返信ください。",
    G1_CONTACT,
  ].join("\n");
}

// 課題文の閲覧リンクを 1 人に送る。★ 研究者が閲覧専用ドキュメントを用意してから実行する。
//   使い方: sendTaskMaterialsEmail("P015", "xxx@example.com", "https://…")
function sendTaskMaterialsEmail(pid, email, url) {
  if (!G1_CONTACT) throw new Error("★ G1_CONTACT が空です。");
  if (!pid || !email || !url) {
    throw new Error("★ sendTaskMaterialsEmail(pid, email, url) の 3 つとも必要です。");
  }
  // ⚠️ ★ URL の取り違えは「別の被験者の割付を渡す」事故になる。最低限の形式検査をする。
  if (!/^https:\/\//.test(url)) {
    throw new Error("★ URL が https:// で始まっていません: " + url);
  }
  var subject = g1MaterialsSubject_();
  var body = g1MaterialsBody_(pid, url);
  if (G1_AUTO_SEND) {
    MailApp.sendEmail(email, subject, body);
    Logger.log("📧 事前資料メールを送信しました → " + g1MaskEmail_(email) + "（" + pid + "）");
  } else {
    GmailApp.createDraft(email, subject, body);
    Logger.log("📝 事前資料メールの下書きを作成しました → " + g1MaskEmail_(email));
    Logger.log("   ⚠️ ★ 下書きのままでは被験者に届きません。Gmail から送信してください。");
  }
  // 送った日を実施トラッキングに残す（★ URL 自体は書かない。割付が推測されうる）。
  try {
    var noteCell = g1EnsureRunRow_(pid);
    if (noteCell) {
      var sh = noteCell.getSheet();
      sh.getRange(noteCell.getRow(), runCol_("課題文リンク送信日")).setValue(new Date());
    }
  } catch (e) {
    Logger.log("⚠️ 送信日を記録できませんでした（メールは送信済み）: " + e);
  }
}

// ============================================================
// ★★ 事前資料メールの自動送信（2026-08-07・decisions.md D-3）
// ============================================================
// ⚠️ ★ **なぜ「登録時に自動」ではなく「URL が貼られたら自動」なのか。**
//   登録時点では割付がまだ無く、その被験者にどの課題文が出るか決まっていない（§3-1）。
//   割付は seed を使う科学的な行為なので、梱包やメールのついでに走らせてはならない。
//   → ★ **研究者が配布フォルダの URL を貼った** ことを「割付が確定した」合図として使う。
//
// ⚠️⚠️ ★ **メール送信は取り消せない。** ガードを 4 本、fail-closed で置く:
//   1. キルスイッチ  … Script Properties G1_MATERIALS_AUTOSEND_OFF
//   2. URL 形式      … https://drive.google.com/ で始まること
//   3. 冪等          … 「課題文リンク送信日」が空の行だけ
//   4. 1 回の上限    … G1_MATERIALS_MAX_PER_RUN 人まで（列の貼り間違いを頑健に抑える）
//
// ★ 本文 (g1MaterialsBody_) は**変えていない**。scripts/check_g1_emails.py の基準を跨がない。

/** ★ これを Script Properties に真値で置くと自動送信が止まる（値は何でもよい）。 */
var G1_AUTOSEND_OFF_PROP = "G1_MATERIALS_AUTOSEND_OFF";

/** ★ 1 回の発火で送る上限。⚠️ 0 にしないこと（0 は「無効」ではなく「1 人も送らない」）。 */
var G1_MATERIALS_MAX_PER_RUN = 3;

/** 配布フォルダ URL として受け付ける形。⚠️ ★ ここを緩めると別サイトの URL を配れてしまう。 */
var G1_MATERIALS_URL_RE = /^https:\/\/drive\.google\.com\/[^\s]+$/;

/**
 * ★★ 被験者別フォルダを束ねる**親**フォルダの ID（`G1_課題ページ_被験者別`）。
 *
 * ⚠️★★ **この親は「制限付き（非公開）」にしてある。** 2026-08-07 の判断:
 *   親を「リンクを知っている全員」にすると、★ 被験者へ送る URL を**親のほうにしてしまった
 *   1 回**で全被験者のフォルダ一覧が渡る（`preregistration.md §2.12`「他の被験者の割付」）。
 *   → 親を非公開にすると、同じ取り違えは「アクセス権が必要です」で**止まる**（fail-closed）。
 *   ★ 代わりに **被験者フォルダを 1 つずつ共有する**手作業が要る。その付け忘れは下の検査が拾う。
 */
var G1_MATERIALS_PARENT_ID = "1qhl28IDeh-19upuZf_YxPwwdq_d9xVcI";

/** Drive のフォルダ URL から ID を取り出す。取れなければ ""。 */
function g1FolderIdFromUrl_(url) {
  var m = String(url).match(/\/folders\/([A-Za-z0-9_-]+)/);
  return m ? m[1] : "";
}

/**
 * ★★ 配布フォルダの **実体** を確かめる（ガード 7）。問題が無ければ ""、あれば理由を返す。
 *
 * ⚠️ ★ 形式検査（ガード 2）は文字列しか見ない。ここは Drive に問い合わせて
 *    「**そのフォルダが本当にこの被験者のもので、本人が開けるか**」を見る。
 *    次の 4 つは、どれも形式検査を素通りする事故である:
 *      (a) 親フォルダの URL を貼った        → ★ 全被験者が見える
 *      (b) 別の被験者のフォルダの URL を貼った → ★ 割付を取り違えて渡す
 *      (c) 配布用の親の下に無いフォルダ       → 置き場所を間違えている
 *      (d) ★ **共有し忘れ**                 → 被験者はリンクを開けない（届いても使えない）
 *
 * ⚠️★ この関数のために **DriveApp のスコープが増える**。次回実行時に Apps Script が
 *    再承認を求めるので、⚠️ 研究者が「承認」を押すまで自動送信は走らない（安全側に倒れる）。
 */
function g1MaterialsFolderProblem_(url, pid) {
  var id = g1FolderIdFromUrl_(url);
  if (!id) return "URL からフォルダ ID を取り出せません（/folders/<ID> の形ではない）";
  if (G1_MATERIALS_PARENT_ID && id === G1_MATERIALS_PARENT_ID) {
    return "★★ これは被験者別フォルダの**親**の URL です（⚠️ 全被験者分が見えます）";
  }
  var folder;
  try {
    folder = DriveApp.getFolderById(id);
  } catch (e) {
    return "フォルダを開けません（ID 違い・削除済み・権限なし）: " + e;
  }
  var name = String(folder.getName()).trim().toUpperCase();
  if (name !== String(pid).trim().toUpperCase()) {
    return "フォルダ名が「" + folder.getName() + "」で P-ID と違います（★ 別の被験者の URL かも）";
  }
  if (G1_MATERIALS_PARENT_ID) {
    var inParent = false;
    try {
      var ps = folder.getParents();
      while (ps.hasNext()) {
        if (ps.next().getId() === G1_MATERIALS_PARENT_ID) {
          inParent = true;
          break;
        }
      }
    } catch (e2) {
      return "親フォルダを確かめられません: " + e2;
    }
    if (!inParent) return "配布用の親フォルダ（G1_課題ページ_被験者別）の下にありません";
  }
  // ⚠️ ★ 共有し忘れの検出。親を非公開にした分、ここが**唯一の**受け皿である。
  var access;
  try {
    access = String(folder.getSharingAccess());
  } catch (e3) {
    return "共有設定を読めません: " + e3;
  }
  if (access !== "ANYONE_WITH_LINK" && access !== "ANYONE") {
    return (
      "★ まだ共有されていません（共有=" + access + "）。⚠️ このまま送っても被験者は開けません。" +
      "Drive で「リンクを知っている全員（閲覧者）」にしてください"
    );
  }
  return "";
}

/** 「G1 実施トラッキング」シートを返す。無ければ null（★ throw しない）。 */
function g1RunSheet_() {
  var ssId = PropertiesService.getScriptProperties().getProperty(MGMT_SHEET_PROP_G1);
  if (!ssId) return null;
  return SpreadsheetApp.openById(ssId).getSheetByName("G1 実施トラッキング") || null;
}

/**
 * ★★ 実シートに「配布フォルダURL」列を挿す（1 回だけ・冪等）。
 *
 * ⚠️ ★ **setupG1Forms() を実行してはならない**（フォームを作り直してしまう）。
 *    列を足すのはこの関数の仕事である。
 *
 * ⚠️ ★ なぜ「コードの RUN_HEADER を直すだけ」で済まないか:
 *    runCol_ は **コード側の RUN_HEADER しか見ない**。実シートが古いままだと、
 *    列名で引いているのに実シートでは**別の列**を指す。
 *    2026-08-03 に実際に起きている（16 列のシートへ 17 列の定義で入力規則を貼り、
 *    日付列「実施日」に「はい/いいえ」のドロップダウンが付いた）。
 *
 * ★ 列の「挿入」であって作り直しではないので、既存データも入力規則も右へずれて保たれる。
 */
function migrateRunSheetAddUrlColumn() {
  var sh = g1RunSheet_();
  if (!sh) {
    throw new Error("★ G1 管理シートが見つかりません（buildManagementSheet() を先に実行）。");
  }

  var NEW_COL = "配布フォルダURL";
  if (runHeaderDiff_(sh).length === 0) {
    Logger.log("✅ 既に「" + NEW_COL + "」列があります（何もしません）。");
    return;
  }

  // ★ 「新列を抜いたヘッダ」= 移行前に期待される姿。これと一致するときだけ触る。
  var idx = runCol_(NEW_COL); // 1 始まり
  var expectedOld = RUN_HEADER.slice(0, idx - 1).concat(RUN_HEADER.slice(idx));
  var live = sh.getRange(2, 1, 1, Math.max(sh.getLastColumn(), expectedOld.length)).getValues()[0];
  var mismatch = [];
  for (var i = 0; i < expectedOld.length; i++) {
    var a = String(expectedOld[i]);
    var b = String(live[i] === undefined ? "" : live[i]).trim();
    if (a !== b) mismatch.push("col" + (i + 1) + ": 期待='" + a + "' / シート='" + b + "'");
  }
  if (mismatch.length) {
    // ⚠️ ★ 見覚えのない形。黙って列を挿すと記録が 1 列ずれる。**止める。**
    throw new Error(
      "★ 「G1 実施トラッキング」が、移行前として期待する形と違います。\n" +
        "⚠️ このまま列を挿すと既存の記録が 1 列ずれます。中止しました。\n" +
        mismatch.join("\n") +
        "\n→ 列を手で合わせてから、もう一度この関数を実行してください。"
    );
  }

  sh.insertColumnBefore(idx);
  sh.getRange(2, idx).setValue(NEW_COL).setFontWeight("bold");
  sh.setColumnWidth(idx, 260);
  SpreadsheetApp.flush();

  assertRunHeader_(sh); // ★ 挿したあとに、コードと実シートが本当に一致したか確かめる
  Logger.log("✅ 「" + NEW_COL + "」列を " + idx + " 列目に挿しました。");
  Logger.log("★ 次: 被験者ごとに配布フォルダの URL をこの列に貼ると、自動で事前資料メールが出ます。");
  Logger.log("ℹ️ 自動送信を止めるには Script Properties に " + G1_AUTOSEND_OFF_PROP + " を置きます。");
}

/** P-ID から Phase1 ロスターのメールを引く。見つからなければ ""。 */
function g1EmailForPid_(pid) {
  if (!PHASE1_MGMT_SHEET_ID) return "";
  var roster = SpreadsheetApp.openById(PHASE1_MGMT_SHEET_ID).getSheetByName("参加者ロスター");
  if (!roster) return "";
  var found = g1FindInPhase1Roster_(roster, { pid: pid });
  if (!found) return "";
  return String(roster.getRange(found.row, 3).getValue()).trim();
}

/**
 * 送信対象を集める（★ 送らない）。g1AutoSendPendingMaterials と previewPendingTaskMaterials で共有する。
 * ⚠️ ★ 「なぜ送らないか」を必ず理由付きで返す。黙って飛ばすと、研究者は
 *    「URL は貼ったのに永久に届かない」状態に気づけない。
 */
function g1CollectPendingMaterials_() {
  var sh = g1RunSheet_();
  if (!sh) return { rows: [], skipped: [], error: "G1 管理シートが見つかりません" };
  try {
    assertRunHeader_(sh);
  } catch (e) {
    return { rows: [], skipped: [], error: String(e.message).split("\n")[0] };
  }

  var colPid = runCol_("P-ID");
  var colUrl = runCol_("配布フォルダURL");
  var colSent = runCol_("課題文リンク送信日");
  var last = sh.getLastRow();
  var rows = [];
  var skipped = [];

  // --- 1 周目: ★ URL の重複を数える（送信済みの行も含める） ---------------------
  // ⚠️★★ 形式検査 (ガード 2) は「Drive の URL か」しか見ない。**宛先が正しいか**は見ない。
  //   実際に起こる事故は「別の被験者の URL を貼る」「1 人ぶんを複数行にコピペする」であり、
  //   どちらも形式検査を素通りする。★ 同じ URL が 2 人以上に紐づいていたら **貼り間違い**なので、
  //   自動では送らず人に返す（送信は取り消せないので、疑わしいときは送らない側に倒す）。
  //   ★ 送信済みの行も数に入れる: 既に P015 へ送った URL を P016 に貼る事故を捕まえるため。
  var pidsByUrl = {};
  for (var r0 = 3; r0 <= last; r0++) {
    var p0 = String(sh.getRange(r0, colPid).getValue()).trim().toUpperCase();
    var u0 = String(sh.getRange(r0, colUrl).getValue()).trim();
    if (!p0 || !u0) continue;
    if (!pidsByUrl[u0]) pidsByUrl[u0] = [];
    if (pidsByUrl[u0].indexOf(p0) < 0) pidsByUrl[u0].push(p0);
  }

  // --- 2 周目: 送る相手を決める -------------------------------------------------
  for (var r = 3; r <= last; r++) {
    var pid = String(sh.getRange(r, colPid).getValue()).trim().toUpperCase();
    if (!pid) continue;
    var url = String(sh.getRange(r, colUrl).getValue()).trim();
    var sent = sh.getRange(r, colSent).getValue();

    if (sent !== "" && sent !== null && sent !== undefined) continue; // ガード 3: 冪等（静かでよい）
    if (!url) continue; // まだ配布フォルダを作っていない = 正常な待ち状態
    if (!G1_MATERIALS_URL_RE.test(url)) {
      skipped.push(pid + ": URL が https://drive.google.com/ で始まっていません"); // ガード 2
      continue;
    }
    if (pidsByUrl[url] && pidsByUrl[url].length > 1) {
      // ガード 5: ★ 同じ URL が複数の P-ID に紐づいている = 貼り間違い
      skipped.push(
        pid + ": 同じ URL が " + pidsByUrl[url].join(" / ") + " に貼られています" +
          "（★ 貼り間違いの可能性。人が直してから送ってください）"
      );
      continue;
    }
    var email = g1EmailForPid_(pid);
    if (!email) {
      skipped.push(pid + ": Phase1 ロスターにメールがありません");
      continue;
    }
    // ガード 7: ★ Drive に問い合わせて実体を確かめる（親の URL / 別人 / 共有し忘れ）
    var problem = g1MaterialsFolderProblem_(url, pid);
    if (problem) {
      skipped.push(pid + ": " + problem);
      continue;
    }
    rows.push({ row: r, pid: pid, url: url, email: email });
  }
  return { rows: rows, skipped: skipped, error: "" };
}

/**
 * ★ 送らずに対象だけ出す（引数なし・安全）。⚠️ 実送信の前に必ず一度これを見る。
 */
function previewPendingTaskMaterials() {
  var found = g1CollectPendingMaterials_();
  if (found.error) {
    Logger.log("❌ " + found.error);
    return;
  }
  Logger.log("ℹ️ 自動送信: " + (g1AutoSendDisabled_() ? "⛔ 停止中（キルスイッチ）" : "有効"));
  Logger.log("ℹ️ G1_AUTO_SEND=" + G1_AUTO_SEND + "（false=下書き作成 / true=実送信）");
  Logger.log("ℹ️ 1 回の上限: " + G1_MATERIALS_MAX_PER_RUN + " 人");
  Logger.log("--------");
  if (!found.rows.length) {
    Logger.log("送る相手はいません（URL 未記入 or 送信済み）。");
  }
  for (var i = 0; i < found.rows.length; i++) {
    var it = found.rows[i];
    var mark = i < G1_MATERIALS_MAX_PER_RUN ? "→ 今回送る" : "… 次回に回る（上限）";
    Logger.log(mark + ": " + it.pid + " → " + g1MaskEmail_(it.email));
  }
  for (var j = 0; j < found.skipped.length; j++) {
    Logger.log("⚠️ 飛ばす " + found.skipped[j]);
  }
  Logger.log("--------");
  Logger.log("★ 実際に送るのは g1AutoSendPendingMaterials()（トリガーが自動で呼びます）。");
}

/** キルスイッチが入っているか。 */
function g1AutoSendDisabled_() {
  var v = PropertiesService.getScriptProperties().getProperty(G1_AUTOSEND_OFF_PROP);
  return !!(v && String(v).trim() !== "" && String(v).trim().toLowerCase() !== "false");
}

/**
 * ★★ 時間トリガーが呼ぶ本体（引数なし）。
 * ⚠️ 送信は取り消せない。上のガード 4 本を通ったものだけ送る。
 */
function g1AutoSendPendingMaterials() {
  if (g1AutoSendDisabled_()) {
    Logger.log("⛔ " + G1_AUTOSEND_OFF_PROP + " が立っているので送信しません。"); // ガード 1
    return;
  }

  // ⚠️★★ **排他制御が要る理由**（onG1ConsentSubmit と同じ流儀・2026-08-07 の cross-review で Codex が指摘）:
  //   「送信日が空か調べる → 送る → 送信日を書く」は **原子的ではない**。
  //   時間トリガーの実行が延びて次の発火と重なる、あるいは研究者が手で実行すると、
  //   ★ **両方が「まだ空」を見て同じ相手に 2 通送る**。⚠️ 送信は取り消せない。
  //   → 収集から記録までを丸ごとロックで囲む。取れなければ **何もしない**（次の発火で拾う）。
  var lock = LockService.getScriptLock();
  try {
    lock.waitLock(30000);
  } catch (lockErr) {
    Logger.log("⏳ 他の実行が動いているので今回は送りません（次の発火で拾います）: " + lockErr);
    return;
  }

  try {
    var found = g1CollectPendingMaterials_();
    if (found.error) {
      Logger.log("❌ " + found.error + "（送信しません）");
      return;
    }
    for (var j = 0; j < found.skipped.length; j++) {
      Logger.log("⚠️ 飛ばす " + found.skipped[j]);
    }
    if (!found.rows.length) return;

    var sh = g1RunSheet_();
    var colNote = runCol_("備考");
    var colSent = runCol_("課題文リンク送信日");
    var n = Math.min(found.rows.length, G1_MATERIALS_MAX_PER_RUN); // ガード 4
    if (found.rows.length > n) {
      Logger.log("ℹ️ " + found.rows.length + " 人が対象ですが、1 回の上限 " + n + " 人まで送ります（残りは次回）。");
    }
    for (var i = 0; i < n; i++) {
      var it = found.rows[i];
      try {
        // ★ 既存関数をそのまま使う。本文の生成はあちらが持っている（二重に持たない）。
        sendTaskMaterialsEmail(it.pid, it.email, it.url);
      } catch (e) {
        // ⚠️ ★ 黙って落とさない。onG1ConsentSubmit と同じく備考に出す。
        Logger.log("❌ " + it.pid + " への事前資料メールに失敗: " + e);
        try {
          sh.getRange(it.row, colNote).setValue("⚠事前資料メール失敗-要手動送信: " + e);
        } catch (e2) {
          Logger.log("⚠️ 備考にも書けませんでした: " + e2);
        }
        continue;
      }

      // ⚠️★★ **「送れたのに記録できていない」を捕まえる**（cross-review 2026-08-07・MEDIUM）:
      //   sendTaskMaterialsEmail は送信日の書き込み失敗を try/catch で握りつぶし、
      //   Logger に出すだけで再スローしない。人が 1 件ずつ呼んでいた頃はログで気づけたが、
      //   ★ トリガー化でその人間のチェックが消えた。放置すると **次の発火で同じ人に再送**される。
      //   → 書けたことを**読み直して確かめ**、空なら自分で書く。それも駄目なら備考で可視化する。
      try {
        var mark = sh.getRange(it.row, colSent).getValue();
        if (mark === "" || mark === null || mark === undefined) {
          sh.getRange(it.row, colSent).setValue(new Date());
          SpreadsheetApp.flush();
          var again = sh.getRange(it.row, colSent).getValue();
          if (again === "" || again === null || again === undefined) {
            throw new Error("送信日を書けませんでした");
          }
          Logger.log("⚠️ " + it.pid + ": 送信日が空だったので補って書きました（★ 二重送信の芽を潰した）");
        }
      } catch (e3) {
        // ⚠️★ ここに来たら **送信済みなのに記録が無い**。次の発火で再送されるので、必ず目に付ける。
        Logger.log("❌ " + it.pid + ": ★ 送信は済んだが送信日を記録できません。⚠️ 二重送信の恐れ: " + e3);
        try {
          sh.getRange(it.row, colNote).setValue(
            "⚠★送信済だが送信日を記録できず-手で日付を入れること（放置すると再送される）: " + e3
          );
        } catch (e4) {
          Logger.log("⚠️ 備考にも書けませんでした: " + e4);
          Logger.log("★ " + G1_AUTOSEND_OFF_PROP + " を立てて自動送信を止めることを検討してください。");
        }
      }
    }
  } finally {
    lock.releaseLock();
  }
}

/** ★ 時間トリガーを 1 回だけ設置する（1 時間ごと）。 */
function installMaterialsAutoSendTrigger() {
  removeMaterialsAutoSendTriggers();
  ScriptApp.newTrigger("g1AutoSendPendingMaterials").timeBased().everyHours(1).create();
  Logger.log("✅ g1AutoSendPendingMaterials を 1 時間ごとに実行するトリガーを設置しました。");
  Logger.log("ℹ️ 止めるには Script Properties に " + G1_AUTOSEND_OFF_PROP + " を置く"
    + "（★ トリガーを消さずに止められる）か、removeMaterialsAutoSendTriggers() を実行します。");
  if (!G1_AUTO_SEND) {
    Logger.log("⚠️ ★ G1_AUTO_SEND=false なので**下書きが溜まるだけ**で被験者に届きません。");
  }
  try {
    assertRunHeader_(g1RunSheet_());
  } catch (e) {
    Logger.log("⚠️ ★ 実シートに「配布フォルダURL」列がまだありません: " + String(e.message).split("\n")[0]);
    Logger.log("   → migrateRunSheetAddUrlColumn() を先に 1 回実行してください。");
  }
}

function removeMaterialsAutoSendTriggers() {
  var triggers = ScriptApp.getProjectTriggers();
  var n = 0;
  for (var i = 0; i < triggers.length; i++) {
    if (triggers[i].getHandlerFunction() === "g1AutoSendPendingMaterials") {
      ScriptApp.deleteTrigger(triggers[i]);
      n++;
    }
  }
  if (n) Logger.log("🧹 既存の g1AutoSendPendingMaterials トリガを " + n + " 件削除しました");
}

// ============================================================
// ★★ G1-C の提出 → P-ID 採番 → 受付メール（Phase1 の onF1Submit と同型）
// ============================================================
// ★ **G1-C がそのまま参加登録である**（研究者判断 2026-08-03）。
//   G1-C は説明文に consent.md の内容を全部載せ、同意 8 項目・氏名・メールを取っている。
//   ⚠️ 別に「参加登録フォーム」を作るのは**重複**だった（一度作って廃止した）。
//   Phase1 も F1（スクリーニング＋同意）を募集時に使い、それをトリガーにしている。
//
// 運用:
//   1. setupG1Forms() を実行済みにする（管理シートが要る）。
//   2. installG1ConsentTrigger() を **一度だけ** 実行。
//   3. 以後、G1-C が提出されるたびに onG1ConsentSubmit(e) が自動で走る:
//      P-ID 採番（Phase1 ロスター）→ G1 実施トラッキングに行追加 → 受付メール。
//
// ⚠️ ★ 当日その場で G1-C に回答した場合も同じ経路を通る（受付メールが届くだけで害は無い）。
//    ★★ **この G1-C の回答が同意の正本である**（研究者判断 2026-08-03 = D-1(a)）。
//    ⚠️ 紙署名は廃止した。`handouts/G1_説明・同意文書.docx` は
//       **フォームが開けない機器トラブル時の予備**である（protocol.md §4.1-1）。

function installG1ConsentTrigger() {
  removeG1ConsentTriggers();
  if (!FORM_ID_CONSENT) {
    throw new Error("★ FORM_ID_CONSENT が空です。");
  }
  ScriptApp.newTrigger("onG1ConsentSubmit")
    .forForm(FormApp.openById(FORM_ID_CONSENT))
    .onFormSubmit()
    .create();
  Logger.log("✅ onG1ConsentSubmit トリガを G1-C に設定しました");
  Logger.log("ℹ️ G1_AUTO_SEND=" + G1_AUTO_SEND + "（false=下書き作成 / true=自動送信）");
  if (!G1_AUTO_SEND) {
    Logger.log(
      "⚠️ ★ G1_AUTO_SEND=false のままだと、登録されても**下書きが作られるだけ**で被験者に届きません。"
    );
  }
  if (!PHASE1_MGMT_SHEET_ID) {
    Logger.log("⚠️ ★ PHASE1_MGMT_SHEET_ID が空です。採番できないので提出時に中止されます。");
  }
}

function removeG1ConsentTriggers() {
  var triggers = ScriptApp.getProjectTriggers();
  var n = 0;
  for (var i = 0; i < triggers.length; i++) {
    if (triggers[i].getHandlerFunction() === "onG1ConsentSubmit") {
      ScriptApp.deleteTrigger(triggers[i]);
      n++;
    }
  }
  if (n) Logger.log("🧹 既存の onG1ConsentSubmit トリガを " + n + " 件削除しました");
}

// G1-C の回答を取り出す。★ 設問タイトルは Q_C_* 定数と共有する（片方だけ変えない）。
// ⚠️ 同意 8 項目はフォーム側で必須なので、ここでは検査しない（未同意の提出は原理的に来ない）。
function g1ConsentAnswers_(response) {
  var out = { name: "", email: "", pid: "" };
  var items = response.getItemResponses();
  for (var i = 0; i < items.length; i++) {
    var title = items[i].getItem().getTitle();
    var v = items[i].getResponse();
    var s = Array.isArray(v) ? v.join(" / ") : String(v == null ? "" : v);
    if (title === Q_C_NAME) out.name = s.trim();
    else if (title === Q_C_EMAIL) out.email = s.trim();
    else if (title === Q_C_PID) out.pid = s.trim().toUpperCase();
  }
  return out;
}

// ★★ G1-C の提出で走る。P-ID 採番 → トラッキング行追加 → 受付メール。
function onG1ConsentSubmit(e) {
  if (!e || !e.response) {
    Logger.log("❌ onG1ConsentSubmit: response が取得できません（トリガ経由で呼んでください）");
    return;
  }
  var a = g1ConsentAnswers_(e.response);
  if (!a.email) {
    Logger.log("⛔ G1-C 提出: メールアドレスが空のため発番しません");
    return;
  }
  if (!PHASE1_MGMT_SHEET_ID) {
    Logger.log("❌ PHASE1_MGMT_SHEET_ID が未設定。採番元が無いので中止します（回答は失われません）");
    return;
  }

  // ★ 同時提出で同じ P-ID が 2 人に出るのを防ぐ（Phase1 と同じ）。
  var lock = LockService.getScriptLock();
  try {
    lock.waitLock(30000);
  } catch (lockErr) {
    Logger.log("❌ ロックを取得できませんでした。手動で assignG1ParticipantId してください: " + lockErr);
    return;
  }

  try {
    var roster = SpreadsheetApp.openById(PHASE1_MGMT_SHEET_ID).getSheetByName("参加者ロスター");
    if (!roster) {
      Logger.log("❌ Phase1 の管理シートに「参加者ロスター」タブがありません（発番中止）");
      return;
    }

    // 1) 既存の人か（★ 再提出でも再発番しない = 冪等。Phase1 参加者は既存 ID をそのまま使う）
    var found = g1FindInPhase1Roster_(roster, { pid: a.pid, email: a.email });
    var pid;
    var isNew = false;
    if (found && found.pid) {
      pid = found.pid;
      Logger.log("♻️ 既存の参加者として扱います: " + pid + "（" + g1MaskEmail_(a.email) + "）");
      if (!String(roster.getRange(found.row, 3).getValue()).trim()) {
        roster.getRange(found.row, 3).setValue(a.email);
      }
    } else {
      pid = g1NextParticipantId_(roster);
      roster.appendRow([pid, a.name, a.email]);
      isNew = true;
      SpreadsheetApp.flush(); // ★ ロック解放前に確定させる
      Logger.log("✅ P-ID 発番: " + pid + "（" + g1MaskEmail_(a.email) + "）");
    }

    // 2) G1 実施トラッキングに行を用意する（★ 実名・メールは書かない）
    var noteCell = g1EnsureRunRow_(pid);

    // 3) 受付メール。⚠️ ★ ここで例外が出ると「発番済みだが通知が無い」状態になり、
    //    再提出しても 1) で冪等スキップされるので**永久に届かない**。備考列に可視化する。
    try {
      var subject = g1RegisterAckSubject_();
      var body = g1RegisterAckBody_(pid);
      if (G1_AUTO_SEND) {
        MailApp.sendEmail(a.email, subject, body);
        Logger.log("📧 受付メールを送信しました → " + g1MaskEmail_(a.email));
      } else {
        GmailApp.createDraft(a.email, subject, body);
        Logger.log("📝 受付メールの下書きを作成しました → " + g1MaskEmail_(a.email));
        Logger.log("   ⚠️ ★ 下書きのままでは被験者に届きません。Gmail から送信してください。");
      }
    } catch (mailErr) {
      if (noteCell) noteCell.setValue("⚠受付メール未作成-要手動送信: " + mailErr);
      Logger.log("❌ 受付メールに失敗（P-ID は確定済 " + pid + "）。備考にフラグを立てました: " + mailErr);
    }
    Logger.log(isNew ? "🎉 新規登録: " + pid : "🔁 再提出（発番なし）: " + pid);
  } finally {
    lock.releaseLock();
  }
}
