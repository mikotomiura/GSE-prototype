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

// ============================================================
// G1-C 同意フォーム（consent.md が文面の真実源）
// ============================================================
function buildConsentForm() {
  var form = openFixed_(FORM_ID_CONSENT, "FORM_ID_CONSENT");
  if (CLEAR_EXISTING) clearForm(form);

  form.setTitle("GSE G1 統制タスク実験 — 説明・同意");
  form.setDescription(
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
      "・貼り付けの回数と文字数（中身は取得しません）\n\n" +
      "▼ 記録しないもの（一切保存されません）\n" +
      "・★ あなたが書いた文章そのもの（実験者が文字数だけを数えます）\n" +
      "・どの文字を打ったか（本文の復元はできません）\n" +
      "・画面の内容・ウィンドウのタイトル・アプリ名・音声・映像\n\n" +
      "▼ リスクと負担\n" +
      "・身体的なリスクはありません。約 70 分の拘束と、書く作業による軽い疲労が負担です。\n" +
      "・★ 難しく感じるブロックがあります。それは設計上わざとそうしてあります。\n" +
      "  うまく書けなくても能力の評価ではありません。採点も比較もしません。\n\n" +
      "▼ 参加は任意です\n" +
      "断っても不利益はありません。途中でやめられ、理由の説明も要りません。" +
      "後からデータの削除を求められます（公表済みの集計から個別に取り除くことはできません）。\n\n" +
      "▼ 結果の使われ方\n" +
      "個人が特定できる形では公表しません。分析スクリプトや集計結果は公開される可能性がありますが、" +
      "そこに含まれるのは P0xx という記号と数値だけで、氏名・実施日時・本文は含みません。\n\n" +
      "▼ お問い合わせ先\n" +
      CONTACT_EMAIL
  );
  form.setCollectEmail(false); // 下の設問で明示的に取る（何を取るかを本人に見せる）
  form.setShowLinkToRespondAgain(false);
  form.setConfirmationMessage("ご回答ありがとうございます。実験者にお知らせください。");

  addSectionHeader(
    form,
    "同意の確認",
    "以下のすべてに同意いただける場合のみ、参加をお願いします。"
  );

  // ★ consent.md の同意欄 6 項目をそのまま設問化する。
  //   ⚠️ 2 と 3 は G1 固有（欺瞞を用いない・preregistration.md §2.8）。落とさないこと。
  [
    "上の説明を読み、質問する機会がありました。",
    "★ 最初と最後のブロックが「書き写し」であることの説明を受けました。",
    "★ 一部のブロックが意図的に難しく作られていることの説明を受けました。",
    "書いた文章は保存されないことを理解しました。",
    "★ 最後に短いアンケートがあり、それは実験の判定には使われないことの説明を受けました。",
    "いつでも中断でき、後からデータの削除を求められることを理解しました。",
    "打鍵の記録（本文を除く）と、その研究利用に同意します。",
  ].forEach(function (title) {
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
  pid.setTitle("参加者ID（お持ちの方のみ）");
  pid.setHelpText(
    "以前 GSE の検証にご参加いただいた方は、そのときお伝えした P から始まる記号をご記入ください。" +
      "初めての方は空欄で構いません。"
  );
  form.addTextItem().setTitle("お名前").setRequired(true);
  var mail = form.addTextItem();
  mail.setTitle("メールアドレス");
  mail.setRequired(true);
  mail.setValidation(FormApp.createTextValidation().requireTextMatchesPattern(".+@.+").build());

  recordFormUrl_("G1_CONSENT", form, "G1-C 説明・同意");
  Logger.log("G1-C 同意フォームを構築した: " + form.getPublishedUrl());
}

// ============================================================
// G1-M 強制比較フォーム（preregistration.md §2.6・★ 7 回答える）
// ============================================================
function buildManipulationCheckForm() {
  var form = openFixed_(FORM_ID_MCHECK, "FORM_ID_MCHECK");
  if (CLEAR_EXISTING) clearForm(form);

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
  if (CLEAR_EXISTING) clearForm(form);

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
//   - **進捗ダッシュボードを作らない** — G1 は 1 人 1 回の来所で完結するので、
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
      "記入パッド (writing-pad.html) の置き場",
      prevPad || "",
      "手動",
      "★ 被験者の入力先。全被験者・全ブロックで同一 (preregistration.md §2.11)。" +
        "実施端末にコピーし、拡張機能なしのプロファイルで開く (protocol.md §1.2)",
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
  // ★ 募集・日程調整（第 6 版・§2.12）。⚠️ 実名・メールはここに書かない。
  //   実名↔P-ID の対応表は Phase1 のロスターと G1-C 回答シートが真実源である。
  "事前案内メール送信日",
  "実施予定日",
  "G1-C 同意",
  "実施日",
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

function buildRunTab_(ss) {
  if (ss.getSheetByName("G1 実施トラッキング")) return;
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
  var rows = 200;
  function listRule(values) {
    return SpreadsheetApp.newDataValidation().requireValueInList(values, true).build();
  }
  function apply(header, values) {
    sh.getRange(3, runCol_(header), rows, 1).setDataValidation(listRule(values));
  }
  var yn = ["はい", "いいえ"];
  apply("G1-C 同意", yn);
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
var PHASE1_MGMT_SHEET_ID = "";

// ★ true にすると MailApp で自動送信する。既定は false（GmailApp で下書きを作る）。
//   ⚠️ Phase1 は AUTO_SEND=true で運用しているが、G1 は**対面・少人数**なので既定を下書きにした。
//      メール送信は取り消せない。文面を一度目で確認してから true にすること。
var G1_AUTO_SEND = false;

// 実施場所・連絡先（★ 実施前に埋める）。空欄のままだと sendPreVisitEmail が止まる。
var G1_VISIT_PLACE = "";     // 例: "○○大学 △△棟 3F 会議室"
var G1_CONTACT = "";         // 例: "研究責任者 ○○（mmiura.network@example.com）"

// ★★ 課題の分野（preregistration.md §2.12-1 で「事前に開示する」と凍結した）。
//    ⚠️ materials/topicNN_*.md の front matter `title:` と**同じ文字列**でなければならない。
//    → scripts/check_g1_topic_titles.py が両者の一致を機械検査する（run.sh から走る）。
var G1_TOPIC_TITLES = [
  "町立図書館の開館時間",
  "商店街の駐輪場",
  "小学校の屋外プール",
  "燃やすごみの収集",
  "公民館の部屋の予約",
  "コミュニティバス",
  "公園でのボール遊び",
  "学校から家庭への連絡",
];

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

// ------------------------------------------------------------
// 事前案内メール（★ §2.12 の開示範囲を厳守する）
// ------------------------------------------------------------
function g1PreVisitSubject_() {
  return "【ご案内】キーボードの打ち方に関する研究へのご参加について";
}

function g1PreVisitBody_(pid, visitDate) {
  var topics = G1_TOPIC_TITLES.map(function (t, i) {
    return "    ・" + t;
  }).join("\n");
  return [
    "この度は研究へのご参加をご承諾いただき、ありがとうございます。",
    "当日の内容を事前にお知らせします。**当日までにお読みください。**",
    "",
    "■ あなたの参加者ID（P-ID）",
    "    " + pid,
    "    ※ 記録はこの記号で管理します。お名前とは別に保管します。",
    "",
    "■ 日時・場所",
    "    日時: " + (visitDate || "（調整中）"),
    "    場所: " + G1_VISIT_PLACE,
    "    所要: 約 70 分（説明・休憩を含みます）",
    "",
    "■ 当日やっていただくこと",
    "    5 分の作業を 10 回、間に 1 分の休憩をはさんで行います。",
    "    ・最初と最後の 1 回ずつは「書き写し」です。考える必要はありません。",
    "      これは計測器が正しく動いているか確かめるための課題で、隠していることはありません。",
    "    ・間の 8 回が本番です。資料を読んで 300〜400 字の文章を書いていただきます。",
    "    ・8 回のうち 7 回、「直前の回と 1 つ前の回のどちらが詰まったか」を 1 つだけ選んでいただきます。",
    "    ・文章は本実験専用の記入画面に打っていただきます。**書いた文章は保存されません。**",
    "    ・最後に短いアンケート（5 分ほど）にお答えいただきます。",
    "",
    "■ 課題の種類（2 種類あります）",
    "    ・資料が 1 本のもの … それを指定の読み手に向けて要約します。",
    "    ・資料が 3 本のもの … 3 本は互いに食い違っています。踏まえて 1 つの主張にまとめます。",
    "    ※ どちらも書く量は 300〜400 字で、読む量（資料の総文字数）もほぼ同じに揃えてあります。",
    "    ※ ★ どの回がどちらになるかは、当日その場でお渡しする紙に書いてあります。",
    "",
    "■ 課題の分野（下記のような、身近な地域の話題です）",
    topics,
    "    ※ ★ **資料はすべて本実験のために作成した架空のものです。**",
    "       自治体名・数値・調査結果は実在しません。事前の下調べは必要ありません。",
    "    ※ 専門知識は要りません。ふだんの生活の感覚で判断できる話題だけを使っています。",
    "",
    "■ 当日までにお願いしたいこと",
    "    ・日本語入力（IME）は、ふだん使っている設定のままでお越しください。",
    "    ・当日は携帯電話の電源を切っていただきます。",
    "",
    "■ 記録するもの / しないもの",
    "    記録する: キーを押した時刻とキーの種類、日本語変換にかかった時間、書いた文字数",
    "    記録しない: ★ **どの文字を打ったか（本文）**、画面の内容、音声・映像",
    "    ※ 詳しくは添付の説明・同意文書をご覧ください。当日、署名をお願いします。",
    "",
    "■ 参加は任意です",
    "    途中でやめられます。理由の説明は要りません。終わった後でも記録の削除を求められます。",
    "",
    "ご不明な点があれば、このメールにご返信ください。",
    G1_CONTACT,
  ].join("\n");
}

// 事前案内メールを 1 通作る（既定は下書き。G1_AUTO_SEND=true で自動送信）。
// ★ §2.12-5「開示は全被験者に同一の文面で行う」ため、宛先ごとに文面を書き分けないこと。
function sendPreVisitEmail(pid, email, visitDate) {
  if (!pid || !email) {
    throw new Error("★ pid と email は必須です。例: sendPreVisitEmail('P015','xxx@example.com','8/10(月) 14:00')");
  }
  if (!G1_VISIT_PLACE || !G1_CONTACT) {
    throw new Error(
      "★ G1_VISIT_PLACE / G1_CONTACT が空です。場所と連絡先が空欄のまま送らないため停止しました。"
    );
  }
  var subject = g1PreVisitSubject_();
  var body = g1PreVisitBody_(pid, visitDate);
  if (G1_AUTO_SEND) {
    MailApp.sendEmail(email, subject, body);
    Logger.log("📧 送信しました: " + pid + " → " + g1MaskEmail_(email));
  } else {
    GmailApp.createDraft(email, subject, body);
    Logger.log("📝 下書きを作成しました: " + pid + " → " + g1MaskEmail_(email));
    Logger.log("   （内容を確認して送信してください。自動送信にするなら G1_AUTO_SEND=true）");
  }
  return subject;
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
