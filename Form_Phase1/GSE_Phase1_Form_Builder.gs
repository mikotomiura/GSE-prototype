/**
 * GSE ユーザー検証 Phase1 – Google Form 設問自動投入スクリプト
 * 設計企画書 v0.4 / codex-review v0.4 準拠
 *
 * 【使い方】
 * 1. 対象フォームを開く → 右上メニュー「⋮」→「スクリプトエディタ」
 * 2. このコードを全選択して貼り付け（既存コードは上書きでOK）
 * 3. 上部メニュー「実行」→「buildForm」を選択して実行
 * 4. 初回は Google アカウントの権限許可が求められるので許可する
 *
 * 【注意】
 * - 既存の設問はすべて削除してから投入します（上書きモード）
 * - 既存設問を残したい場合は CLEAR_EXISTING を false に変更してください
 */

var FORM_ID = "1iNJthNn6myw7mmuKV6NEnpLHFRt5BTFQBOuCsroCtyI"; // F1 参加同意・スクリーニング (buildForm)
// F5 事後アンケート (buildF5): ユーザー作成済みフォームを固定 ID で再利用する (#C)。
// FormApp.create だと実行ごとに別フォームが量産されるため、F1 と同じ openById 方式に統一。
var F5_FORM_ID = "1I-X1B8F-tQk7aEAdqderOLhjobeHct48KU23NWwfhlY";
// F2 事前アンケート (buildF2) / F4 セッション後アンケート (buildF4) も固定 ID で再利用する。
// 旧 FormApp.create は実行ごとにフォームを量産し、被験者に配った短縮URL(x.gd)が指すフォームと、
// 集計が読むフォーム(FORMURL_F2/F4)がズレて「回答が管理シートに記録されない」不具合の原因だった。
// ⚠ 被験者に配った短縮URLが指すフォームを「正本」とし、その【編集用フォームID】
//   (docs.google.com/forms/d/<ここ>/edit の <ここ>) を記入すること。
//   空のままだと buildF2/F4 はエラーメッセージを出して停止する（量産防止のガード）。
var F2_FORM_ID = "1rIgGukudblKEMIef8EkC_KmjUBumrpoLkIew5w6kRWY"; // F2 事前アンケート（被験者配布 x.gd/m3q89 の正本・編集ID）
var F4_FORM_ID = "1Q4Iy2r7Uswth9zVOpV81jIKOdKj5dJSW2L-ScKaurqU"; // F4 セッション後アンケート（被験者配布 x.gd/3qba4 の正本・編集ID）
var CLEAR_EXISTING = true; // 既存設問を削除してから投入するか

// セッションログ (.age) の提出先 Dropbox **File Request** URL（/request/ 形式・提出専用で相互不可視）。
// 共有フォルダ (/scl/fo/) は提出者同士がファイル名で互いに見えるため不可 (pilot-runbook D6)。
// buildManagementSheet() がシート「リンク集」の既定値に使う（シート側で手動上書きも可）。
// 短縮版 x.gd/PHtwA のリダイレクト先 = https://www.dropbox.com/request/5oak4xpqjt19zx8zvh03（同一）。
var DROPBOX_FILE_REQUEST_URL = "https://x.gd/PHtwA";

// ============================================================
// 被験者管理の自動化（F1 提出トリガ → P-ID 自動発番 + 通知メール下書き）の設定
// ============================================================
// 自動メール送信の可否。
// true : MailApp.sendEmail で適格判定後にそのまま自動送信する（ユーザー明示承認 2026-06-27 で採用）。
// false: GmailApp.createDraft で下書きを作り、研究者が内容確認後に手動送信する（安全側へ戻す場合）。
// ⚠ true の間は、適格な F1 提出があった瞬間に本人宛メールが送られる（研究者の確認ステップ無し）。
//   適格判定（同意・年齢・IME・OS・メール@検証）と冪等性（同一メール二重送信防止）が誤送信を抑える。
var AUTO_SEND = true;

// condition（実験条件）の既定値。Phase1 は単群・対照なし(FD1)のため全員 baseline 固定
// （ユーザー決定 2026-06-27）。将来 AB 設計を入れる場合はロスターのドロップダウンで手動上書き。
var DEFAULT_CONDITION = "baseline";

// 通知メールの件名・配布情報。PII ではないので .gs に置いてよい（フォームID/Dropbox URL/公開鍵置き場と同様）。
// ⚠ アプリ入手先・公開鍵(pubkey.txt)の入手先は配布実態に合わせて研究者が書き換える。
var F1_EMAIL_SUBJECT = "【GSE ユーザー検証】参加者ID（P-ID）と次のステップのご案内";
var APP_DOWNLOAD_INFO =
  "アプリ一式は研究者が用意した Google Drive（閲覧専用）からまとめて入手できます: https://x.gd/6crxj\n" +
  "       ・Windows: gse-next.exe（インストール不要のポータブル版。x64-setup.exe ではなくこちらを使用）\n" +
  "       ・macOS(Apple Silicon): gse-next_0.1.21_aarch64.dmg\n" +
  "       ・暗号化ツール gse-package(.exe) と公開鍵 pubkey.txt（全員共通）も同じフォルダに同梱\n" +
  "       初回セッションは研究者が同席し、起動・権限付与・初回警告の確認まで一緒に行います";
var PUBKEY_SOURCE_INFO =
  "配布フォルダ同梱の pubkey.txt（研究者の age 公開鍵・全員共通）。" +
  "暗号化はこの公開鍵だけで完結し、復号は研究者しかできません。";

// 被験者に渡してよい「公開用リンク集」スプレッドシート（フォーム URL を集約した閲覧専用シート）。
// ⚠ 実名↔P-ID 対応表を含む【運用管理シート（MGMT_SHEET）とは別物】。こちらは PII を一切含まない、
//   閲覧専用で共有してよいシートであること。空文字なら通知メールでは個別フォーム URL のみ案内する。
// 短縮版 x.gd/qcpwX のリダイレクト先 = spreadsheet 18vs0qbEa…（既存と同一シート・検証済 2026-06-27）。
var PUBLIC_LINKS_URL = "https://x.gd/qcpwX";

// 被験者に案内する各フォームの「回答用」短縮 URL（x.gd）。いずれも viewform を短縮したもので、
// 編集 URL ではない（2026-06-27 リダイレクト先を全件検証済み）。メール本文(f1EmailBody_)の
// F2/F4/F5 案内に優先利用し、空文字なら formPublishedUrl_ の動的取得にフォールバックする。
// ⚠ FORM_ID / F5_FORM_ID は openById 用の内部IDで別物。短縮URLでこれらを置換しないこと。
var SHORT_URL_F1 = "https://x.gd/k8nAi"; // F1 参加同意・スクリーニング（募集・公開リンク集用）
var SHORT_URL_F2 = "https://x.gd/m3q89"; // F2 事前アンケート（始める前に1回。正本フォーム F2_FORM_ID を指す）
var SHORT_URL_F4 = "https://x.gd/3qba4"; // F4 セッション後アンケート（毎回。正本フォーム F4_FORM_ID を指す）
var SHORT_URL_F5 = "https://x.gd/b4hRB"; // F5 事後アンケート（全終了後に1回）
// key(F1/F2/F4/F5) → 短縮回答URL の対応表。管理シート「リンク集」タブの回答URL列に短縮版を載せるのに使う。
var SHORT_FORM_URLS = { F1: SHORT_URL_F1, F2: SHORT_URL_F2, F4: SHORT_URL_F4, F5: SHORT_URL_F5 };


// 自作尺度「作業再開感・自己調整感」(#D / FD9・ユーザー承認 2026-06-24)。
// F2-C(事前) と F5(事後) で matched 再測定するため、両者が必ず byte 一致するよう
// 単一定数として一元定義する（code-reviewer LOW: 二重定義による pre/post 不一致事故を構造的に防止）。
//   尺度: 4 件法（強制選択, 1–4）。中心化傾向(中央選択)バイアス回避のため 5→4 件法に変更
//         （FD10, 2026-06-25 ユーザー確定）。GSE-10 公式副指標(4 件法)と件法が揃う。
//   facet: 項目1=効力感(正) / 項目2=逆転(行動傾向, 採点時 5-x で再コード) /
//          項目3=行動信念(正) / 項目4=選好(正)。
//   採点: 項目2を逆転再コード(5-回答値)後、4項目の平均を合成スコア(範囲 1.0–4.0)。α は報告のみ(基準.70参照)。
//   主仮説: pre→post の合成スコア変化を記述的に観察(単群・対照なし FD1 のため因果主張しない)。
//   ※ 旧版は全項目「AIに頼らず/自力で」正方向偏重で黙従・方向バイアスを招いたため混在へ改訂。
var TSE_ITEMS = [
  "詰まっても、自分なりの糸口を見つけて書き進められると思う",                 // 効力感(正)
  "難しい場面になると、自分で考えるより先に AI に答えを求めてしまう",         // 逆転(採点時 5-x)
  "いったん自分で考えてから AI を使う方が、最終的に良い文章になると思う",     // 行動信念(正)
  "詰まったときは、すぐ答えを見るより、自分で糸口を探す時間をとりたい",       // 選好(正)
];

// 自作 TSE 尺度の件法・アンカー・両端ラベルも pre(F2-C)/post(F5) で必ず一致させるため
// 単一定数で一元定義する（TSE_ITEMS と同じく byte 一致を構造的に保証。FD10）。
// ScaleItem は両端ラベルのみ表示可能なため、中間 2/3 のアンカーはセクション説明(教示文)に明記する
// （GSE-10 / TLX と同方式）。
var TSE_SCALE_MIN = 1;
var TSE_SCALE_MAX = 4;
var TSE_LABEL_LOW = "全くそう思わない";
var TSE_LABEL_HIGH = "強くそう思う";
var TSE_ANCHOR_INSTRUCTION =
  "1: 全くそう思わない　2: あまりそう思わない　3: ややそう思う　4: 強くそう思う";

// ============================================================
// メイン関数
// ============================================================
function buildForm() {
  var form = FormApp.openById(FORM_ID);

  // 既存設問を全削除（分岐ナビゲーションを先に解除する clearForm 経由）。
  // 直接 deleteItem で末尾から消すと、まだ go-to-page 参照されているページを
  // 先に削除して "Invalid data updating form" になる（buildForm 再実行時の典型エラー）。
  if (CLEAR_EXISTING) {
    clearForm(form);
  }

  // フォーム基本設定
  form.setTitle("GSE ユーザー検証 Phase1 – 参加同意・スクリーニング");
  form.setDescription(
    "GSE（Generative Struggle Engine）ユーザー検証へのご協力ありがとうございます。\n\n" +
    "本研究は、執筆・思考作業中の操作ログ（打鍵リズム・変換イベント・貼り付け回数など）と、" +
    "ご自身の主観的な「詰まり感」「前進感」の対応を調べるものです。\n\n" +
    "▼ 記録するもの\n" +
    "・打鍵のタイミング・間隔\n" +
    "・日本語入力の変換／確定イベント\n" +
    "・貼り付けの回数と文字数、操作の種類\n\n" +
    "▼ 記録しないもの（一切保存されません）\n" +
    "・入力した本文そのもの\n" +
    "・クリップボードの中身\n" +
    "・開いているウィンドウのタイトル\n\n" +
    "▼ データの扱い\n" +
    "お名前・メールアドレスは、ログとは別に保管され、匿名の参加者IDでのみ結びつけられます。" +
    "対応表は共有されません。いつでも理由を告げずに参加を撤回でき、提出済みデータの削除を求められます。\n\n" +
    "▼ 秘密保持のお願い\n" +
    "GSE は未公開のソフトウェアです。検証中に知り得た画面・介入の挙動・仕組み等を第三者に口外しないよう" +
    "お願いします。適格と判定された方には、別途「守秘同意書」をお送りし、署名のご返送をアプリ配布の条件と" +
    "させていただきます（協力者の方には正式な秘密保持契約書をお願いする場合があります）。\n\n" +
    "▼ お問い合わせ先\n" +
    "研究・データに関するご質問は mmiura.network@gmail.com までご連絡ください。"
  );
  form.setCollectEmail(false); // メールはF1設問で別途収集
  form.setShowLinkToRespondAgain(false);
  form.setConfirmationMessage(
    "ご回答ありがとうございます。研究者より参加者ID（P-ID）と次のステップをメールでご連絡します。"
  );

  // ============================================================
  // セクション 0: F1 同意・スクリーニング
  // ============================================================
  addSectionHeader(form,
    "F1｜参加同意・スクリーニング",
    "以下の同意事項をご確認の上、ご回答ください。"
  );

  // Q1: 説明理解
  var q1 = form.addCheckboxItem();
  q1.setTitle("上記の説明を読み、内容を理解しました。");
  q1.setChoices([q1.createChoice("説明を理解した")]);
  q1.setRequired(true);

  // Q2: 同意
  var q2 = form.addCheckboxItem();
  q2.setTitle("操作ログ（本文を除く）の記録と研究利用に同意します。");
  q2.setChoices([q2.createChoice("同意する")]);
  q2.setRequired(true);

  // Q2b: 任意性・撤回の自由（インフォームド・コンセントの明示）
  var qVoluntary = form.addCheckboxItem();
  qVoluntary.setTitle(
    "参加は任意であり、いつでも理由を告げずに撤回でき、提出済みデータの削除を求められること、" +
    "撤回によって不利益を受けないことを理解しました。"
  );
  qVoluntary.setChoices([qVoluntary.createChoice("理解した")]);
  qVoluntary.setRequired(true);

  // Q2c: 匿名管理・公表範囲
  var qAnon = form.addCheckboxItem();
  qAnon.setTitle(
    "氏名・メールは匿名の参加者ID（P-ID）で管理され、実名との対応表は共有されないこと、" +
    "研究の公表時は匿名の集計のみが用いられることに同意します。"
  );
  qAnon.setChoices([qAnon.createChoice("同意する")]);
  qAnon.setRequired(true);

  // Q2d: 秘密保持（高位の同意）。具体の守秘事項と記名署名はフォーム末尾セクションで行う。
  // onF1Submit はこの項目を適格判定に使う（キーワード「口外」。"署名"/"守秘事項" は末尾項目と
  // 照合衝突するため、ここの文言には入れない）。
  var qConfidential = form.addCheckboxItem();
  qConfidential.setTitle(
    "検証中に知り得た GSE（未公開ソフトウェア）の情報を第三者に口外しないことに同意します" +
    "（詳しい内容はこのフォームの最後でご確認・ご記名いただきます）。"
  );
  qConfidential.setChoices([qConfidential.createChoice("同意する")]);
  qConfidential.setRequired(true);

  // Q3: 年齢（分岐あり）
  var q3 = form.addMultipleChoiceItem();
  q3.setTitle("年齢を教えてください。");
  q3.setRequired(true);

  // Q4: 未成年者向け保護者同意確認（条件付きセクション）
  // ※ セクション分岐は後でまとめて設定する
  var secMinor = form.addPageBreakItem();
  secMinor.setTitle("未成年の方へ");
  secMinor.setHelpText("18歳未満の方は保護者同意が必要です。");

  var q4 = form.addMultipleChoiceItem();
  q4.setTitle("保護者同意フォームを提出済みですか。");
  q4.setRequired(true);

  var secMinorEnd = form.addPageBreakItem();
  secMinorEnd.setTitle("参加資格がありません");
  secMinorEnd.setHelpText(
    "保護者同意が確認できないため、現時点では参加いただけません。\n" +
    "保護者の方と一緒に保護者同意フォームをご提出の上、改めてご連絡ください。"
  );
  // 不適格者をここで送信終了させる（これが無いと「次へ」で本流へ落ちて続行できてしまう）
  secMinorEnd.setGoToPage(FormApp.PageNavigationType.SUBMIT);

  // メインに戻るセクション
  var secMain = form.addPageBreakItem();
  secMain.setTitle("スクリーニング（続き）");

  // Q5: 利用頻度
  var q5 = form.addMultipleChoiceItem();
  q5.setTitle("普段、文章作成や思考作業に PC を週どのくらい使いますか。");
  q5.setChoices([
    q5.createChoice("ほぼ毎日"),
    q5.createChoice("週数回"),
    q5.createChoice("週1回以下"),
  ]);
  q5.setRequired(true);

  // Q6: IME（不適格分岐あり）
  var q6 = form.addMultipleChoiceItem();
  q6.setTitle("日本語入力（IME）で文章を書きますか。");
  q6.setRequired(true);

  var secIneligible = form.addPageBreakItem();
  secIneligible.setTitle("参加資格がありません");
  secIneligible.setHelpText(
    "本検証は日本語IMEによる入力を対象としています。\n" +
    "ご参加いただけませんが、ご関心をお持ちいただきありがとうございます。"
  );
  secIneligible.setGoToPage(FormApp.PageNavigationType.SUBMIT);

  var secAfterQ6 = form.addPageBreakItem();
  secAfterQ6.setTitle("スクリーニング（続き）");

  // Q7: OS（不適格分岐あり）
  var q7 = form.addMultipleChoiceItem();
  q7.setTitle("検証に使用する OS を教えてください。");
  q7.setRequired(true);

  var secOSIneligible = form.addPageBreakItem();
  secOSIneligible.setTitle("参加資格がありません");
  secOSIneligible.setHelpText(
    "本検証は Windows / macOS のみ対応しています。\n" +
    "ご関心をお持ちいただきありがとうございます。"
  );
  secOSIneligible.setGoToPage(FormApp.PageNavigationType.SUBMIT);

  var secContact = form.addPageBreakItem();
  secContact.setTitle("連絡先");

  // Q8: メールアドレス
  var q8 = form.addTextItem();
  q8.setTitle("連絡先メールアドレス（謝礼・連絡用。ログとは分離して保管されます）");
  q8.setHelpText("例: your.name@example.com");
  q8.setRequired(true);
  q8.setValidation(
    FormApp.createTextValidation()
      .requireTextIsEmail()
      .build()
  );

  // Q9: 氏名
  var q9 = form.addTextItem();
  q9.setTitle("お名前またはニックネーム（対応表管理用）");
  q9.setHelpText("公開されません。研究者の内部管理にのみ使用します。");
  q9.setRequired(true);

  // ============================================================
  // 守秘同意（軽量・F1 内で記名署名して成立。D8/D9）
  // ============================================================
  // ※ このセクションは適格者のみが到達する（不適格分岐は手前で SUBMIT 終了するため）。
  //   記名（氏名入力）を署名に代え、これをもって被験者の守秘同意の成立とする。正式 NDA（押印・
  //   損害賠償）は協力者にのみ別途。全文は Form_Phase1/守秘同意書_被験者向け.md と byte 一致させること。
  addSectionHeader(form,
    "守秘事項のご確認とご署名",
    "GSE は未公開のソフトウェアです。以下の守秘事項をご確認のうえ、ご署名（お名前の入力）をお願いします。\n\n" +
    "【守秘事項】\n" +
    "・検証中に知り得た GSE の画面・介入の挙動・仕組み・未公開機能・不具合等を、第三者に口外・公開・" +
    "再配布しません。\n" +
    "・配布されたアプリ・ファイルを第三者に再配布しません。\n" +
    "・この義務は検証終了後も、情報が公知になるまで継続します。\n" +
    "・すでに公知の情報、ご自身が以前から正当に知っていた情報、独自に得た情報、法令上開示が必要な情報は" +
    "対象外です。\n" +
    "・本守秘はあなたのデータやプライバシーを制限するものではありません（データの扱いは上記説明のとおり）。"
  );

  var ndaAgree = form.addCheckboxItem();
  ndaAgree.setTitle("上記の守秘事項に同意します。");
  ndaAgree.setChoices([ndaAgree.createChoice("同意する")]);
  ndaAgree.setRequired(true);

  var ndaSign = form.addTextItem();
  ndaSign.setTitle("ご署名（お名前を入力してください。これを署名に代えます）");
  ndaSign.setHelpText("未成年の方は保護者のお名前も併記してください（例: 本人氏名／保護者氏名）。");
  ndaSign.setRequired(true);

  // ============================================================
  // セクション分岐を設定
  // ============================================================
  // Q3: 年齢分岐
  q3.setChoices([
    q3.createChoice("18歳以上", secMain),
    q3.createChoice("18歳未満", secMinor),
  ]);

  // Q4: 保護者同意分岐
  q4.setChoices([
    q4.createChoice("提出済み", secMain),
    q4.createChoice("未提出", secMinorEnd),
  ]);

  // Q6: IME分岐
  q6.setChoices([
    q6.createChoice("はい", secAfterQ6),
    q6.createChoice("いいえ", secIneligible),
  ]);

  // Q7: OS分岐
  q7.setChoices([
    q7.createChoice("Windows", secContact),
    q7.createChoice("macOS", secContact),
    q7.createChoice("その他（Linux等）", secOSIneligible),
  ]);

  recordFormUrl("F1", form, "F1 同意・スクリーニング");
  Logger.log("✅ F1 同意・スクリーニング 設問投入完了");


  // ============================================================
  // F2 フォームは別フォームとして作成予定
  // ※ 同一フォームに混在させると同意フォームとして機能しなくなるため
  // 以下の関数で別途呼び出せる構成にしている
  // ============================================================

  Logger.log("🎉 buildForm() 完了 – F1 同意・スクリーニングフォームが完成しました");
}


// ============================================================
// F2: 事前アンケート（別フォーム作成）
// ============================================================
function buildF2() {
  // 固定 ID で再利用 (F1/F5 と同方式)。create 量産による「集計フォームのズレ＝記録されない」を防ぐ。
  if (!F2_FORM_ID) {
    Logger.log("❌ F2_FORM_ID 未設定。正本フォーム（被験者配布の短縮URL先）の編集IDを定数に記入してください");
    return;
  }
  var form = FormApp.openById(F2_FORM_ID);
  // openById は同一フォーム再利用のため再実行時の設問重複を防ぐべく既存設問を全削除する。
  if (CLEAR_EXISTING) {
    clearForm(form);
  }
  form.setTitle("GSE ユーザー検証 Phase1 – F2 事前アンケート（ベースライン）");
  form.setDescription(
    "検証開始前に一度だけ回答してください。\n" +
    "参加者ID（P-ID）は研究者からメールで通知されます。回答欄に入力してください。"
  );
  form.setCollectEmail(false); // PII 分離: 回答者メールを収集しない（P-ID のみで突合）
  form.setShowLinkToRespondAgain(false);
  form.setConfirmationMessage("ありがとうございます。事前アンケートの回答を受け付けました。");

  // P-ID
  var pid = form.addTextItem();
  pid.setTitle("参加者ID（P-ID）");
  pid.setHelpText("研究者からメールで通知された P-ID を入力してください（例: P017）");
  pid.setRequired(true);

  // ---- F2-A: 属性・AI利用習慣 ----
  addSectionHeader(form, "F2-A｜属性・AI 利用習慣", "");

  // 人口統計属性（年代・職業）。サンプル特性の記述用に匿名（P-ID 紐付け）で記録する。
  // F1 Q3「年齢」は 18歳以上/未満の適格判定分岐用で年代を残さないため、ここで年代を取得する。
  var d1 = form.addMultipleChoiceItem();
  d1.setTitle("年代を教えてください。");
  d1.setChoices([
    d1.createChoice("18〜19歳"),
    d1.createChoice("20代"),
    d1.createChoice("30代"),
    d1.createChoice("40代"),
    d1.createChoice("50代"),
    d1.createChoice("60代以上"),
  ]);
  d1.setRequired(true);

  var d2 = form.addMultipleChoiceItem();
  d2.setTitle("ご職業を教えてください。");
  d2.setChoices([
    d2.createChoice("学生"),
    d2.createChoice("会社員・公務員"),
    d2.createChoice("専門職（研究・士業・医療など）"),
    d2.createChoice("自営業・フリーランス"),
    d2.createChoice("その他"),
  ]);
  d2.setRequired(true);

  var a1 = form.addCheckboxItem();
  a1.setTitle("主に行う作業の種類（複数選択可）");
  a1.setChoices([
    a1.createChoice("論述・小論文"),
    a1.createChoice("レポート・報告書"),
    a1.createChoice("企画書・提案書"),
    a1.createChoice("創作・物語"),
    a1.createChoice("コーディング"),
    a1.createChoice("その他"),
  ]);
  a1.setRequired(true);

  var a2 = form.addMultipleChoiceItem();
  a2.setTitle("詰まったとき、AI（ChatGPT 等）にどのくらい頼りますか。");
  a2.setChoices([
    a2.createChoice("ほぼ毎回"),
    a2.createChoice("時々"),
    a2.createChoice("まれ"),
    a2.createChoice("ほとんど使わない"),
  ]);
  a2.setRequired(true);

  var a3 = form.addMultipleChoiceItem();
  a3.setTitle("1週間に AI 生成物をコピー＆ペーストする頻度。");
  a3.setChoices([
    a3.createChoice("1日複数回"),
    a3.createChoice("1日1回程度"),
    a3.createChoice("週数回"),
    a3.createChoice("ほぼ無し"),
  ]);
  a3.setRequired(true);

  // ---- F2-B: 一般性自己効力感（GSE-10 日本語版）副指標 ----
  // 4件法アンカーは原版どおり 4 段階だが、Google Forms の ScaleItem は両端ラベルのみ表示可能。
  // 中間 2/3 のアンカー文はセクション説明に明記する（既存 F2-C/TLX と同方式）。
  addSectionHeader(form,
    "F2-B｜一般性自己効力感（副指標・GSE-10 日本語版）",
    "以下のそれぞれの質問について、あなたはどの程度自信がありますか？\n" +
    "1: 全く当てはまらない　2: 当てはまらない　3: まあ当てはまる　4: 全くその通り\n\n" +
    "※ 出典: Ito, K., Schwarzer, R., & Jerusalem, M. (2005) Japanese Adaptation of the General Self-Efficacy Scale."
  );

  // GSE-10 公式日本語版（Ito, Schwarzer & Jerusalem, 2005）の逐語項目。
  //   出典: http://userpage.fu-berlin.de/~health/japan.htm（Schwarzer 公式配布ページの日本語版）。
  //   ⚠ 運用前に必ず: (1) 上記公式ページで項目文・アンカーが逐語一致するか目視で最終確認
  //       （本項目は WebFetch 経由取得のため、わずかな表記揺れがないか人手で照合する）、
  //     (2) 研究利用条件（無償利用・要引用か）を公式ページで確認する（明示の利用制限記載は見当たらず）。
  //   ※ pre(F2-B)/post(F5) は完全に同一の項目文・尺度でなければならない（pre/post 比較の前提・受け入れ条件）。
  //   ※ 名称注意: ここでの "GSE" は本システム GSE ではなく Schwarzer の自己効力感尺度。
  //     和文略称「GSES」は坂野・東條(1986)=16項目2件法 を指すことが多く別物。混同しないこと。
  var gsesItems = [
    "私は、一生懸命がんばれば、困難な問題でもいつも解決することができる",
    "私は、誰かが私に反対しても、自分が欲しいものを手にするための手段や道を探すことができる",
    "目的を見失わず、ゴールを達成することは私にとって難しいことではない",
    "予期せぬ出来事に遭遇しても、私は効率よく対処できる自信がある",
    "私は色々な才略に長けているので、思いがけない場面に出くわしても、どうやってきりぬければよいのか分かる",
    "必要な努力さえ惜しまなければ、私はだいたいの問題を解決することができる",
    "自分の物事に対処する能力を信じているので、困難なことに立ち向かっても取り乱したりしない",
    "問題に直面しても、いつもいくつかの解決策を見つけることができる",
    "苦境に陥っても、いつも解決策を考えつく",
    "どんなことが起ころうとも、私はいつもその事に対処することができる",
  ];

  gsesItems.forEach(function(text) {
    var item = form.addScaleItem();
    item.setTitle(text);
    item.setBounds(1, 4);
    item.setLabels("全く当てはまらない", "全くその通り");
    item.setRequired(true);
  });

  // ---- F2-C: 作業再開感・自己調整感（主観主指標・自作 bespoke 尺度）----
  // 旧称「課題特異的自己効力感」。検証済み尺度ではないため「自己効力感」と称さない（codex-consult 助言）。
  // 項目は単一定数 TSE_ITEMS（ファイル冒頭）を参照。facet/採点/逆転コード/α/主仮説は同定数のコメント参照（#D / FD9）。
  // ⚠ F5(buildF5) も同じ TSE_ITEMS を参照するため byte 一致（matched pre/post）が構造的に保証される。
  addSectionHeader(form,
    "F2-C｜作業再開感・自己調整感（主観主指標）",
    "執筆・思考作業について、今のあなたにどの程度あてはまりますか。\n" +
    TSE_ANCHOR_INSTRUCTION
  );

  TSE_ITEMS.forEach(function(text) {
    var item = form.addScaleItem();
    item.setTitle(text);
    item.setBounds(TSE_SCALE_MIN, TSE_SCALE_MAX);
    item.setLabels(TSE_LABEL_LOW, TSE_LABEL_HIGH);
    item.setRequired(true);
  });

  recordFormUrl("F2", form, "F2 事前アンケート（ベースライン）");
  Logger.log("✅ F2 事前アンケート作成完了");
  Logger.log("🔗 編集URL: " + form.getEditUrl());
  Logger.log("🔗 回答URL: " + form.getPublishedUrl());
}


// ============================================================
// F3: プローブ申告フォーム（Q1/Q2）【廃止・フォールバック専用】
// ============================================================
// ⚠ 通常運用では不要。プローブ回答は **アプリ内 ProbeCard** が正規ルートで、
//   `record_realtime_answer` → NDJSON `realtime_label` として記録される
//   （v0.3 較正の主データ源・docs/functional-design.md / docs/glossary.md）。
//   in-app は probe_id・時間隔離窓(t−31s..t−1s)・latency を自動付与してログと精密突合するため、
//   手入力の本フォームより構造的に優れる（このフォームは probe_id/session_id の手転記が必要で
//   窓精度も落ちる）。
//   本関数は **in-app カードが壊れた場合のフォールバック**としてのみ残す。被験者には配らない
//   （`buildAllSupportForms` からも除外済み）。
function buildF3() {
  var form = FormApp.create("GSE ユーザー検証 Phase1 – F3 プローブ申告（Q1摩擦／Q2前進）");
  form.setDescription(
    "【重要】このフォームはセッション中のランダムプローブ通知が来たときに回答します。\n" +
    "直前の作業を振り返って、2つの軸でお答えください。正解・不正解はありません。直感で構いません。\n\n" +
    "※ システムの判定（詰まっているかどうか）は表示されません。あなた自身の感覚のみで回答してください。"
  );
  form.setCollectEmail(false); // PII 分離: 回答者メールを収集しない
  form.setShowLinkToRespondAgain(true); // プローブは複数回回答する
  form.setConfirmationMessage("ありがとうございます。次のプローブが来るまで作業を続けてください。");

  // P-ID
  var pid = form.addTextItem();
  pid.setTitle("参加者ID（P-ID）");
  pid.setRequired(true);

  // セッションID
  var sid = form.addTextItem();
  sid.setTitle("セッションID（エディタ画面に表示されている ID）");
  sid.setHelpText("例: ses_20260624_001");
  sid.setRequired(true);

  // probe_id: ログ側プローブと一意突合するためのキー（md F3 運用注: participant_id + probe_id で突合）
  // これが無いと同一セッション内の複数プローブを区別できず criterion label を窓に対応付けられない。
  var probe = form.addTextItem();
  probe.setTitle("プローブ番号 / probe_id（通知またはエディタに表示された番号）");
  probe.setHelpText("例: pb_07。番号が表示されない場合は通知が出た時刻 hh:mm:ss を入力してください。");
  probe.setRequired(true);

  // Q1: 摩擦
  var q1 = form.addScaleItem();
  q1.setTitle("Q1｜直前の作業は、どのくらい「詰まって」いましたか？（摩擦）");
  q1.setBounds(1, 5);
  q1.setLabels("1: まったく詰まっていない", "5: 強く詰まっていた");
  q1.setRequired(true);

  // Q2: 前進
  var q2 = form.addScaleItem();
  q2.setTitle("Q2｜直前の作業は、どのくらい「前に進んだ」感覚でしたか？（前進）");
  q2.setBounds(1, 5);
  q2.setLabels("1: まったく進まなかった", "5: はっきり前進した");
  q2.setRequired(true);

  // Q3: 任意・介入受容性（Opportunity層探索用、X1判定には使わない）
  var q3 = form.addMultipleChoiceItem();
  q3.setTitle("Q3｜（任意）もし今この瞬間に通知が来ていたら、受け取れる状態でしたか？");
  q3.setHelpText("※ この設問はX1判定に使用しません。Phase3（X2）の探索的収集です。");
  q3.setChoices([
    q3.createChoice("受け取れた"),
    q3.createChoice("邪魔だった"),
    q3.createChoice("どちらでもない"),
  ]);
  q3.setRequired(false);

  Logger.log("✅ F3 プローブ申告フォーム作成完了");
  Logger.log("🔗 編集URL: " + form.getEditUrl());
  Logger.log("🔗 回答URL: " + form.getPublishedUrl());
}


// ============================================================
// F4: セッション後アンケート
// ============================================================
function buildF4() {
  // 固定 ID で再利用 (F1/F5 と同方式)。create 量産による「集計フォームのズレ＝記録されない」を防ぐ。
  if (!F4_FORM_ID) {
    Logger.log("❌ F4_FORM_ID 未設定。正本フォーム（被験者配布の短縮URL先）の編集IDを定数に記入してください");
    return;
  }
  var form = FormApp.openById(F4_FORM_ID);
  // openById は同一フォーム再利用のため再実行時の設問重複を防ぐべく既存設問を全削除する。
  if (CLEAR_EXISTING) {
    clearForm(form);
  }
  form.setTitle("GSE ユーザー検証 Phase1 – F4 セッション後アンケート");
  form.setDescription(
    "各執筆セッション終了後にご回答ください。5問以内で終わります。\n" +
    "Dropbox へのログ提出もこのタイミングで行ってください。"
  );
  form.setCollectEmail(false); // PII 分離: 回答者メールを収集しない
  form.setShowLinkToRespondAgain(true);
  form.setConfirmationMessage("ありがとうございます。次のセッションまでゆっくりお過ごしください。");

  // P-ID
  var pid = form.addTextItem();
  pid.setTitle("参加者ID（P-ID）");
  pid.setRequired(true);

  // セッション番号
  // ログ突合キーはログファイル名 gse_<YYYYMMDD_HHMMSS>.ndjson の日時部分に統一する（独自表記や
  // "s03" 等の略記はログと一致せず join が壊れるため、提出ファイル名の日時をそのまま入力してもらう）。
  // ※ アプリ画面にセッションID表示は無いため「エディタ画面に表示」という旧文言は実態と不一致だった。
  var snum = form.addTextItem();
  snum.setTitle("セッションID（提出するログファイル名 gse_◯◯◯.ndjson の ◯◯◯ 部分）");
  snum.setHelpText("例: gse_20260302_075721.ndjson なら「20260302_075721」。ログとの突合に使用します。");
  snum.setRequired(true);

  // S1: 集中度
  var s1 = form.addScaleItem();
  s1.setTitle("今回のセッション全体で、どのくらい集中できましたか？");
  s1.setBounds(1, 5);
  s1.setLabels("1: 全く集中できなかった", "5: 非常に集中できた");
  s1.setRequired(true);

  // S1b: 介入(Wall/2分Timer)の煩わしさ — 介入害の主観側 (v0.4 §4.4)。
  //   helpfulness は想起バイアスの小さい「介入直後アプリ内1タップ」で取得する方針のため Form では聞かない。
  //   Week1(介入なし)は発火しないので optional。
  var s1b = form.addScaleItem();
  s1b.setTitle("今回出た Wall / 2分タイマーは、邪魔・ストレスに感じましたか？");
  s1b.setHelpText("Wall / タイマーが出たセッションのみ回答（Week1 など出なければ空欄でOK）。");
  s1b.setBounds(1, 5);
  s1b.setLabels("1: 全く邪魔でない", "5: 非常に邪魔");
  s1b.setRequired(false);

  // S2: プローブ頻度
  var s2 = form.addMultipleChoiceItem();
  s2.setTitle("プローブ（途中の問い）の頻度は適切でしたか？");
  s2.setChoices([
    s2.createChoice("多すぎた"),
    s2.createChoice("ちょうど良かった"),
    s2.createChoice("少なすぎた"),
  ]);
  s2.setRequired(true);

  // S3: IME不具合（健全性クロスチェック）
  var s3 = form.addMultipleChoiceItem();
  s3.setTitle("日本語入力（変換・確定）で不具合や違和感はありましたか？");
  s3.setHelpText("IMEログ健全性の確認のため必ずご回答ください。");
  s3.setChoices([
    s3.createChoice("なかった"),
    s3.createChoice("あった（次の欄に内容を入力）"),
  ]);
  s3.setRequired(true);

  var s3detail = form.addTextItem();
  s3detail.setTitle("IME不具合の内容（「なかった」場合は空欄でOK）");
  s3detail.setRequired(false);

  // S4: Dropbox提出確認
  var s4 = form.addMultipleChoiceItem();
  s4.setTitle("セッションログ（NDJSON）を Dropbox に提出しましたか？");
  s4.setChoices([
    s4.createChoice("提出済み"),
    s4.createChoice("これから提出する"),
    s4.createChoice("エラーが出て提出できなかった"),
  ]);
  s4.setRequired(true);

  // S5: 自由記述
  var s5 = form.addParagraphTextItem();
  s5.setTitle("気づいた点・困った点（任意）");
  s5.setRequired(false);

  recordFormUrl("F4", form, "F4 セッション後アンケート");
  Logger.log("✅ F4 セッション後アンケート作成完了");
  Logger.log("🔗 編集URL: " + form.getEditUrl());
  Logger.log("🔗 回答URL: " + form.getPublishedUrl());
}


// ============================================================
// F5: 事後アンケート
// ============================================================
function buildF5() {
  // #C: 事前作成フォームを固定 ID で再利用 (F1 と同方式)。
  var form = FormApp.openById(F5_FORM_ID);
  // openById は同一フォームを再利用するため、再実行時の設問重複を防ぐべく既存設問を全削除する
  // (create 方式には不要だったが openById では必須)。clearForm でナビゲーションを先に解除して
  // "Invalid data updating form" を回避する（F5 自体は分岐を持たないが buildForm と同一経路に統一）。
  if (CLEAR_EXISTING) {
    clearForm(form);
  }
  form.setTitle("GSE ユーザー検証 Phase1 – F5 事後アンケート");
  form.setDescription(
    "Phase 1 の全セッションが終了したらご回答ください。\n" +
    "F2 と同じ項目を含みます（ベースラインとの比較のため）。"
  );
  form.setCollectEmail(false); // PII 分離: 回答者メールを収集しない
  form.setShowLinkToRespondAgain(false);
  form.setConfirmationMessage("ご参加ありがとうございました。研究者より謝礼等についてご連絡します。");

  // P-ID
  var pid = form.addTextItem();
  pid.setTitle("参加者ID（P-ID）");
  pid.setRequired(true);

  // ---- 一般性自己効力感（F2-B と同一） ----
  // pre/post 比較の前提として F2-B と「完全に同一の項目文・尺度・アンカー」でなければならない。
  // 下記は F2-B の GSE-10 公式日本語版（Ito, Schwarzer & Jerusalem, 2005）と byte 一致させること。
  addSectionHeader(form,
    "一般性自己効力感（再測定・F2-B と同じ項目）",
    "以下のそれぞれの質問について、あなたはどの程度自信がありますか？\n" +
    "1: 全く当てはまらない　2: 当てはまらない　3: まあ当てはまる　4: 全くその通り\n\n" +
    "※ 出典: Schwarzer, R., & Jerusalem, M. (1995) Generalized Self-Efficacy Scale; " +
    "日本語版 Ito, K., Schwarzer, R., & Jerusalem, M. (2005) Japanese Adaptation of the General Self-Efficacy Scale.（F2-B と同一・byte 一致）"
  );

  var gsesItems = [
    "私は、一生懸命がんばれば、困難な問題でもいつも解決することができる",
    "私は、誰かが私に反対しても、自分が欲しいものを手にするための手段や道を探すことができる",
    "目的を見失わず、ゴールを達成することは私にとって難しいことではない",
    "予期せぬ出来事に遭遇しても、私は効率よく対処できる自信がある",
    "私は色々な才略に長けているので、思いがけない場面に出くわしても、どうやってきりぬければよいのか分かる",
    "必要な努力さえ惜しまなければ、私はだいたいの問題を解決することができる",
    "自分の物事に対処する能力を信じているので、困難なことに立ち向かっても取り乱したりしない",
    "問題に直面しても、いつもいくつかの解決策を見つけることができる",
    "苦境に陥っても、いつも解決策を考えつく",
    "どんなことが起ころうとも、私はいつもその事に対処することができる",
  ];

  gsesItems.forEach(function(text) {
    var item = form.addScaleItem();
    item.setTitle(text);
    item.setBounds(1, 4);
    item.setLabels("全く当てはまらない", "全くその通り");
    item.setRequired(true);
  });

  // ---- 作業再開感・自己調整感（F2-C と同一4項目を matched で再測定）----
  // 旧称「課題特異的自己効力感」。pre/post の変化量を出すため項目1〜4を同一に再測定する。
  // ★ F2-C と同じ単一定数 TSE_ITEMS（ファイル冒頭）を参照 → byte 一致が構造的に保証される。
  //   facet/採点/逆転コードは TSE_ITEMS のコメント（#D / FD9）を参照。
  addSectionHeader(form,
    "作業再開感・自己調整感（再測定・F2-C と同一項目）",
    TSE_ANCHOR_INSTRUCTION
  );

  TSE_ITEMS.forEach(function(text) {
    var item = form.addScaleItem();
    item.setTitle(text);
    item.setBounds(TSE_SCALE_MIN, TSE_SCALE_MAX);
    item.setLabels(TSE_LABEL_LOW, TSE_LABEL_HIGH);
    item.setRequired(true);
  });

  // ---- GSE 利用体験・継続意向（事後のみ）----
  // 注: 下記2項目は「自己効力感」ではなく介入の主観的効果・受容性を測る別構成概念。
  //     上の SE スコアに混ぜて平均しないこと（pre 対応も存在しない post-only 項目）。
  addSectionHeader(form,
    "GSE 利用体験・継続意向（事後のみ）",
    "1: 全くそう思わない　〜　5: 強くそう思う"
  );

  var experienceItems = [
    "GSE を使う中で、詰まったときに自分で考え直す感覚が戻る場面があった",
    "今後も GSE を使い続けたいと思う",
  ];

  experienceItems.forEach(function(text) {
    var item = form.addScaleItem();
    item.setTitle(text);
    item.setBounds(1, 5);
    item.setLabels("全くそう思わない", "強くそう思う");
    item.setRequired(true);
  });

  // ---- NASA-TLX short（介入害の同時監視, v0.4 §4.4 / 文献[11]）----
  // 介入で AI 依存が下がっても負荷・フラストレーションが上がればプロダクト失敗。Phase 末に簡易測定。
  addSectionHeader(form,
    "作業負荷（修正 NASA-TLX・1–5 件法の短縮版）",
    "Phase 1 全体を通じての感覚でお答えください。\n1: 非常に低い　〜　5: 非常に高い\n\n" +
    "※ 出典: Hart, S. G., & Staveland, L. E. (1988) Development of NASA-TLX (Task Load Index).\n" +
    "※ 本研究では原版（0–100 / 20 段階・6 次元・重み付け）ではなく、精神的要求 / 努力 / フラストレーションの " +
    "3 次元を 1–5 件法に短縮した修正版として使用します（重み付けなし・記述的観察用、設計企画書 v0.4 §4.4）。"
  );

  var tlxItems = [
    "精神的な負担（考える量・集中の要求）はどのくらいでしたか",
    "目標達成のために払った努力はどのくらいでしたか",
    "イライラ・ストレス（フラストレーション）はどのくらいでしたか",
  ];

  tlxItems.forEach(function(text) {
    var item = form.addScaleItem();
    item.setTitle(text);
    item.setBounds(1, 5);
    item.setLabels("1: 非常に低い", "5: 非常に高い");
    item.setRequired(true);
  });

  // ---- 総括設問 ----
  addSectionHeader(form, "総括", "");

  var e1 = form.addParagraphTextItem();
  e1.setTitle("検証期間で最も「自分の作業が見えた」と感じた瞬間があれば教えてください。（任意）");
  e1.setRequired(false);

  var e2 = form.addMultipleChoiceItem();
  e2.setTitle("プライバシー（本文非保存・データ分離）について不安は残りましたか？");
  e2.setChoices([
    e2.createChoice("不安はなかった"),
    e2.createChoice("少し不安があった"),
    e2.createChoice("かなり不安だった"),
  ]);
  e2.setRequired(true);

  var e2detail = form.addParagraphTextItem();
  e2detail.setTitle("不安があった場合、具体的にどの点が気になりましたか？（任意）");
  e2detail.setRequired(false);

  recordFormUrl("F5", form, "F5 事後アンケート");
  Logger.log("✅ F5 事後アンケート作成完了");
  Logger.log("🔗 編集URL: " + form.getEditUrl());
  Logger.log("🔗 回答URL: " + form.getPublishedUrl());
}


// ============================================================
// 被験者運用フォームを一括作成するユーティリティ
// ============================================================
// F3（プローブ申告）は in-app ProbeCard が正規ルートのため **除外**する（廃止・フォールバック専用）。
// 一括実行は実行時間/クォータに当たりやすいので、落ちたら各 build を単独実行すること。
function buildAllSupportForms() {
  buildF2(); // 事前ベースライン
  buildF4(); // セッション後
  buildF5(); // 事後（固定 ID 再利用）
  Logger.log("🎉 F2 / F4 / F5 作成完了。次に buildManagementSheet() で管理シートに URL を集約してください。");
  Logger.log("ℹ️ F3（プローブ申告）は in-app ProbeCard が正規ルートのため除外。フォールバックが必要な時のみ buildF3 を単独実行。");
}


// ============================================================
// 運用管理スプレッドシート（フォーム URL 集約 + 参加者ロスター + 提出トラッキング）
// ============================================================
// P-ID を単一キーに forms / NDJSON(P###) / Dropbox(P###_*.age) / metrics を ID 連携する
// 研究運用の中枢シート。実名↔P-ID 対応表を含むため **repo 外・研究者のみ**がアクセスする
// (data-privacy / docs/pilot-runbook.md §0)。
//
// 実行順:
//   1. buildForm()          … F1（固定 ID 再利用）
//   2. buildAllSupportForms() … F2 / F4 / F5（各 build が URL を Script Properties に記録）
//   3. buildManagementSheet() … 管理シートを新規作成し URL を自動集約（シート ID は保持し再利用）
//   4. Dropbox で File Request を作成し、その URL を「リンク集」タブのセルに貼る（手動・下記）
//   ※ 一括は setupPhase1Forms() でも可。ただし実行時間/クォータに当たったら各ステップを単独実行。
//
// 【Dropbox File Request 作成手順（研究者・手動）】GAS からは作成不可（外部サービス）。
//   a. dropbox.com → 左メニュー「ファイルリクエスト」→「ファイルリクエストを作成」。
//   b. タイトル=「GSE Phase1 セッションログ提出 (.age)」、保存先フォルダ=例 /GSE-Phase1/submissions/。
//   c. 作成後の **リクエスト URL** をコピー → 管理シート「リンク集」タブの該当セルに貼る。
//   d. 被験者にはこの URL のみ渡す（pilot-runbook §3 Step 3）。受領者(研究者)だけが中身を見られ、
//      提出者同士は互いのファイルを見られない。提出物は P###_*.age（暗号化済）のみ。
//   e. ID 連携: ファイル名の先頭 P### がフォーム回答(P-ID)・NDJSON(P###)・metrics/P###/ と突合する
//      単一キー。実名↔P### の対応表は本シート「参加者ロスター」（repo 外・研究者のみ）で管理する。

var MGMT_SHEET_PROP = "GSE_MGMT_SHEET_ID";

// 各 build 関数末尾から呼ぶ。作成/更新したフォームの URL を Script Properties に記録する。
// id も保存する: refreshRosterStatus() が destination sheet を介さず
// FormApp.openById(id).getResponses() で回答を直接読むため（後方互換: キー追加のみ）。
function recordFormUrl(key, form, label) {
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

// F1〜F5 を作成し管理シートまで一気通貫で作る（一貫運用の入口）。
// ⚠ 1 実行で全部走るため、実行時間/クォータに当たったら各 build を単独実行 → 最後に
//    buildManagementSheet() を回すこと（URL は Script Properties に残るので集約は成功する）。
function setupPhase1Forms() {
  buildForm();
  buildAllSupportForms();
  var url = buildManagementSheet();
  Logger.log("🎉 Phase1 フォーム一式 + 管理シート 作成完了: " + url);
}

// 管理シートを新規作成 or 既存を更新し、URL を返す。
function buildManagementSheet() {
  var props = PropertiesService.getScriptProperties();
  var ss = null;
  var ssId = props.getProperty(MGMT_SHEET_PROP);
  if (ssId) {
    try {
      ss = SpreadsheetApp.openById(ssId);
    } catch (e) {
      ss = null; // 削除済み等 → 作り直す
    }
  }
  if (!ss) {
    ss = SpreadsheetApp.create("GSE Phase1 運用管理シート");
    props.setProperty(MGMT_SHEET_PROP, ss.getId());
  }

  buildLinksTab_(ss, props); // 毎回 URL を再集約（手動入力セルは保持）
  buildRosterTab_(ss); // 既存があれば作らない（入力データを破壊しない）
  buildSubmissionTab_(ss); // 同上
  applyRosterValidation_(ss); // 毎回: condition/OS/撤回 のドロップダウン・条件付き書式
  buildDashboardTab_(ss); // 毎回: 進捗ダッシュボード（集計式は再描画）

  ["シート1", "Sheet1"].forEach(function (n) {
    var s = ss.getSheetByName(n);
    if (s && ss.getSheets().length > 1) ss.deleteSheet(s);
  });

  Logger.log("✅ 管理シート作成/更新完了");
  Logger.log("🔗 " + ss.getUrl());
  return ss.getUrl();
}

// --- タブ: リンク集（フォーム URL を自動集約 + Dropbox File Request URL は手動セル）---
function buildLinksTab_(ss, props) {
  var sh = ss.getSheetByName("リンク集") || ss.insertSheet("リンク集", 0);
  // Dropbox URL など手動入力済みの値を退避してから再描画する（毎回上書きで消さない）。
  var prevDropbox = "";
  var prevPubkey = "";
  try {
    prevDropbox = sh.getRange(4, 2).getValue();
    prevPubkey = sh.getRange(5, 2).getValue();
  } catch (e) {
    /* 初回は空 */
  }
  sh.clear();
  var rows = [
    ["GSE Phase1 リンク集", "", "", ""],
    ["", "", "", ""],
    ["項目", "値 / URL", "種別", "備考"],
    [
      "Dropbox File Request URL",
      prevDropbox || DROPBOX_FILE_REQUEST_URL || "（Dropbox で File Request を作成し、ここに URL を貼る）",
      "手動",
      "P###_*.age の提出先。受領者(研究者)のみ閲覧可・提出者同士は互いに見えない",
    ],
    [
      "被験者へ配る age 公開鍵 (pubkey.txt) の置き場",
      prevPubkey || "",
      "手動",
      "被験者が .age 暗号化(gse-package --recipient)に使う age 公開鍵。配布 zip に同梱 or DL リンクを記入。" +
        "公開鍵は配布して安全。※ 秘密鍵 ~/.gse/age-identity.txt は共有・コミット厳禁",
    ],
    ["", "", "", ""],
    ["フォーム", "タイトル", "編集URL", "回答URL(短縮)"],
  ];
  ["F1", "F2", "F4", "F5"].forEach(function (k) {
    var raw = props.getProperty("FORMURL_" + k);
    // 回答URL列は被験者に配る短縮版(x.gd)を載せる。短縮未設定なら publishedUrl にフォールバック。
    var shortUrl = SHORT_FORM_URLS[k] || "";
    if (raw) {
      var o = JSON.parse(raw);
      rows.push([k + "｜" + o.label, o.title, o.editUrl, shortUrl || o.publishedUrl]);
    } else {
      rows.push([k, "（未生成 — build" + k + " を実行）", "", shortUrl]);
    }
  });
  rows.push(["F3（廃止）", "in-app ProbeCard が正規ルート。フォールバック専用", "", ""]);
  sh.getRange(1, 1, rows.length, 4).setValues(rows);
  sh.getRange(1, 1).setFontWeight("bold").setFontSize(14);
  sh.getRange(3, 1, 1, 4).setFontWeight("bold");
  sh.getRange(7, 1, 1, 4).setFontWeight("bold");
  sh.setColumnWidth(1, 240);
  sh.setColumnWidth(2, 340);
  sh.setColumnWidth(3, 320);
  sh.setColumnWidth(4, 320);
}

// --- タブ: 参加者ロスター（P-ID 対応表 + 進捗）。再実行で入力を破壊しない ---
// 行1: 機密バナー（実名↔P-ID 対応表は研究者のみ・共有禁止）。行2: ヘッダ。行3+: データ。
// nextParticipantId_ は col A を /^P\d+$/ で走査するためバナー/ヘッダ行は無視され影響しない。
// 新規ヘルパ（appendRosterRow_ / refreshRosterStatus）は rosterHeaderRow_() で
// 「P-ID」ヘッダ行を動的に探すため、行構成に依存しない。
function buildRosterTab_(ss) {
  if (ss.getSheetByName("参加者ロスター")) return;
  var sh = ss.insertSheet("参加者ロスター");
  var header = [
    "P-ID", "氏名/ニックネーム", "メール", "OS", "条件(baseline/intervention)",
    "F1同意日", "F2事前", "セッション数", "F4回答(計)", "F5事後",
    "Dropbox提出", "NDA署名", "撤回/除外", "備考",
  ];
  // 行1: 機密注意バナー（data-privacy / pilot-runbook §0）。
  sh.getRange(1, 1).setValue(
    "⚠ 実名・メール↔P-ID 対応表（研究者のみ）。共有・コミット禁止。" +
    "外部送信は P-ID を単一キーにした集計値(metrics.json)・数値尺度(survey.csv)のみ。"
  );
  sh.getRange(1, 1, 1, header.length).merge();
  sh.getRange(1, 1)
    .setFontWeight("bold")
    .setFontColor("#ffffff")
    .setBackground("#b71c1c")
    .setWrap(true);
  // 行2: ヘッダ。
  sh.getRange(2, 1, 1, header.length).setValues([header]).setFontWeight("bold");
  sh.setFrozenRows(2);
  // 例データは入れない（addParticipant() が P001 から連番自動採番するため）。
  sh.setColumnWidth(1, 70);
  sh.setColumnWidth(2, 150);
  sh.setColumnWidth(3, 210);
}

// ロスターの「P-ID」ヘッダがある行番号を返す（バナー有無に依存しないため動的探索）。
// 見つからなければ 0（未構築）。データは返り値 + 1 行目から始まる。
function rosterHeaderRow_(sheet) {
  var last = sheet.getLastRow();
  var scan = Math.min(last, 5); // ヘッダは先頭付近にしか無い
  for (var r = 1; r <= scan; r++) {
    if (String(sheet.getRange(r, 1).getValue()).trim() === "P-ID") return r;
  }
  return 0;
}

// --- タブ: セッション提出トラッキング（per-session）。再実行で入力を破壊しない ---
function buildSubmissionTab_(ss) {
  if (ss.getSheetByName("セッション提出トラッキング")) return;
  var sh = ss.insertSheet("セッション提出トラッキング");
  var header = [
    "P-ID", "セッションID", "日付", "OS",
    "NDJSON生成", ".age提出(Dropbox)", "metrics生成", "F4回答", "備考",
  ];
  sh.getRange(1, 1, 1, header.length).setValues([header]).setFontWeight("bold");
  sh.setFrozenRows(1);
  sh.getRange(2, 1, 1, 2).setValues([["P001", "ses_20260628_001"]]);
}


// ============================================================
// 参加者 ID（P-ID）の連番自動採番
// ============================================================
// 手動割当の取り違え（pilot-runbook 警告）を防ぐため、管理シート「参加者ロスター」の
// 既存 P-ID を走査して **次の一意な連番** を発行する。形式 = P + 3桁ゼロ埋め（P001, P002, …）。
// 英数字16字以下を保ち、logger(is_valid_participant_id) と gse-package(package.rs) の両
// バリデータを満たす（`_`/`-` は gse-package で不可なので使わない）。
//
// 使い方: Apps Script エディタで関数 addParticipant を選んで実行 → ロスターに新規行＋P-ID 採番。
//   氏名/メール/OS/条件 等は発行後にシートへ手入力する。
function nextParticipantId_(sheet) {
  var max = 0;
  // ヘッダ行を動的に探し、その次行以降の col A を走査する（onF1Submit/appendRosterRow_ と
  // 探索方式を統一。ロスター行1の機密バナー等で行構成が変わっても破綻しない）。
  var hr = rosterHeaderRow_(sheet);
  var last = sheet.getLastRow();
  if (hr && last > hr) {
    var ids = sheet.getRange(hr + 1, 1, last - hr, 1).getValues();
    for (var i = 0; i < ids.length; i++) {
      var m = String(ids[i][0]).match(/^P(\d+)$/);
      if (m) {
        var n = parseInt(m[1], 10);
        if (n > max) max = n;
      }
    }
  }
  var next = max + 1;
  var num = next < 1000 ? ("000" + next).slice(-3) : String(next); // 3桁ゼロ埋め（1000以上は桁増）
  return "P" + num;
}

// ロスターに新規参加者行を追加し、次の一意 P-ID を自動採番する。採番した P-ID を返す。
function addParticipant() {
  var props = PropertiesService.getScriptProperties();
  var ssId = props.getProperty(MGMT_SHEET_PROP);
  if (!ssId) {
    Logger.log("❌ 管理シート未作成。先に buildManagementSheet() を実行してください。");
    return null;
  }
  var ss = SpreadsheetApp.openById(ssId);
  var sheet = ss.getSheetByName("参加者ロスター");
  if (!sheet) {
    Logger.log("❌ 「参加者ロスター」タブが見つかりません。buildManagementSheet() を実行してください。");
    return null;
  }
  var pid = nextParticipantId_(sheet);
  sheet.appendRow([pid]); // P-ID 列のみ。氏名/メール/OS/条件 等は手入力。
  Logger.log("✅ 参加者を追加: " + pid + "（氏名・メール・OS・条件をシートに手入力してください）");
  Logger.log("🔗 " + ss.getUrl());
  return pid;
}


// ============================================================
// Task 1: F1 提出トリガ → 適格判定 → P-ID 自動発番 → 通知メール下書き
// ============================================================
// 運用:
//   1. buildForm() / buildManagementSheet() を実行済みにする（ロスターが必要）。
//   2. installF1Trigger() を一度だけ実行 → F1 フォームに onFormSubmit トリガが付く。
//      初回は Gmail 送信 + Spreadsheet + Forms のスコープ承認が出る。
//   3. 以後、被験者が F1 を提出するたび onF1Submit(e) が自動実行される。
//      適格者 → P-ID 発番 + ロスター転記 + 通知メール「下書き」作成（AUTO_SEND=false 既定）。
//      不適格/非同意/二重 → 発番せずログのみ。
//
// ★ F1 はメール設問(setCollectEmail(false))のため、送信先は Q8（連絡先メール）の回答値のみを使う。
//   実名↔P-ID の対応表はロスター（repo 外・研究者のみ）に閉じ、外部へは出さない（data-privacy）。

// F1 フォームに installable な onFormSubmit トリガを設定する（二重作成防止に既存を全削除）。
function installF1Trigger() {
  removeF1Triggers();
  // forForm は Form オブジェクトを渡す（文字列 ID は環境差があるため openById で明示的に解決）。
  ScriptApp.newTrigger("onF1Submit")
    .forForm(FormApp.openById(FORM_ID))
    .onFormSubmit()
    .create();
  Logger.log("✅ onF1Submit トリガを F1 フォームに設定しました（FORM_ID=" + FORM_ID + "）");
  Logger.log("ℹ️ AUTO_SEND=" + AUTO_SEND + "（false=下書き作成 / true=自動送信）");
}

// onF1Submit に紐づく既存トリガを全削除（再設定・解除用）。
function removeF1Triggers() {
  var triggers = ScriptApp.getProjectTriggers();
  var removed = 0;
  for (var i = 0; i < triggers.length; i++) {
    if (triggers[i].getHandlerFunction() === "onF1Submit") {
      ScriptApp.deleteTrigger(triggers[i]);
      removed++;
    }
  }
  if (removed > 0) Logger.log("🧹 既存 onF1Submit トリガを " + removed + " 件削除しました");
}

// F1 提出ハンドラ（installable onFormSubmit トリガから呼ばれる）。
function onF1Submit(e) {
  if (!e || !e.response) {
    Logger.log("❌ onF1Submit: response が取得できません（手動実行ではなくトリガ経由で呼んでください）");
    return;
  }
  var a = f1Answers_(e.response); // {consent1, consent2, age, guardian, ime, os, email, name}

  // 1) 適格性判定（不適格・非同意は発番しない）
  var verdict = isEligibleF1_(a);
  if (!verdict.eligible) {
    Logger.log("⛔ F1 提出: 適格外のため発番しません（理由: " + verdict.reason + "）");
    return;
  }

  // 2) 管理シート / ロスター取得
  var props = PropertiesService.getScriptProperties();
  var ssId = props.getProperty(MGMT_SHEET_PROP);
  if (!ssId) {
    Logger.log("❌ 管理シート未作成。先に buildManagementSheet() を実行してください（発番中止）");
    return;
  }
  var ss = SpreadsheetApp.openById(ssId);
  var sheet = ss.getSheetByName("参加者ロスター");
  if (!sheet) {
    Logger.log("❌ 「参加者ロスター」タブが見つかりません（発番中止）");
    return;
  }

  // 3-5) 発番〜行追加〜通知を排他する。F1 がほぼ同時に複数提出されるとトリガが並行実行され、
  //      両方が同じ max を読んで同一 P-ID を重複発番しうる（GAS トリガはシリアライズ非保証）。
  //      重複 P-ID は突合の根幹を壊すため LockService で発番区間を直列化する。
  var lock = LockService.getScriptLock();
  try {
    lock.waitLock(30000);
  } catch (lockErr) {
    Logger.log("❌ ロック取得に失敗（他処理が長時間ロック中）。今回は発番を見送ります: " + lockErr);
    return;
  }
  try {
    // 3) 冪等性: 同一メールが既にロスターにあれば二重発番しない
    var existing = findRosterByEmail_(sheet, a.email);
    if (existing) {
      Logger.log("♻️ 既発番のためスキップ: " + maskEmail_(a.email) + " → " + existing + "（再送が必要なら手動対応）");
      return;
    }

    // 4) P-ID 発番 + ロスター行追加
    //    守秘同意は F1 内で記名署名して成立（D9）。末尾の「守秘事項に同意」チェック + 記名があれば
    //    NDA署名列を「署名済(F1)」にする（無ければ「未署名」で手動フォロー）。
    var ndaStatus =
      a.ndaSignature && a.ndaAgree.indexOf("同意する") !== -1 ? "署名済(F1)" : "未署名";
    var pid = nextParticipantId_(sheet);
    appendRosterRow_(sheet, {
      pid: pid,
      name: a.name,
      email: a.email,
      os: a.os,
      condition: DEFAULT_CONDITION,
      consentDate: e.response.getTimestamp(),
      nda: ndaStatus,
    });
    var appendedRow = sheet.getLastRow(); // 通知失敗時に備考へフラグするため行を控える
    SpreadsheetApp.flush(); // ロック解放前に書き込みを確定させる
    Logger.log("✅ P-ID 発番: " + pid + "（" + a.os + " / " + maskEmail_(a.email) + "）");

    // 5) 通知メール（既定は下書き作成）。
    //    ロスター行は確定済みなので、ここで例外が出ると findRosterByEmail_ により再提出が
    //    冪等スキップされ被験者が永久に通知未達になりうる。失敗を備考列に可視化して手動回復可能にする。
    var subject = F1_EMAIL_SUBJECT;
    // 回答 URL は短縮版(x.gd)を優先し、未設定なら Script Properties の publishedUrl にフォールバック。
    var urls = {
      f2: SHORT_URL_F2 || formPublishedUrl_(props, "F2"),
      f4: SHORT_URL_F4 || formPublishedUrl_(props, "F4"),
      f5: SHORT_URL_F5 || formPublishedUrl_(props, "F5"),
    };
    var body = f1EmailBody_(pid, urls); // プレーンテキスト（HTML 非対応クライアント向けフォールバック）
    var htmlBody = f1EmailHtml_(pid, urls); // スマホ/PC でレスポンシブ表示する HTML 版
    try {
      if (AUTO_SEND) {
        MailApp.sendEmail(a.email, subject, body, { htmlBody: htmlBody });
        Logger.log("📧 通知メールを自動送信しました → " + maskEmail_(a.email));
      } else {
        GmailApp.createDraft(a.email, subject, body, { htmlBody: htmlBody });
        Logger.log("📝 通知メールの下書きを作成しました → " + maskEmail_(a.email) + "（Gmail 下書きで内容確認後に送信）");
      }
    } catch (mailErr) {
      // 備考列(14)に未通知フラグを立てる（dedup で再発番されないため、ここを研究者が拾って手動通知）。
      sheet.getRange(appendedRow, 14).setValue("⚠通知未作成-要手動送信: " + mailErr);
      Logger.log("❌ 通知作成に失敗（P-ID は発番済 " + pid + "）。備考に未通知フラグを記録: " + mailErr);
    }
  } finally {
    lock.releaseLock();
  }
}

// メールアドレスをログ用にマスクする（PII 最小化。Apps Script 実行ログはクラウドに残るため）。
// 例: user@example.com → u***@example.com。
function maskEmail_(email) {
  var s = String(email);
  var at = s.indexOf("@");
  if (at <= 0) return "***";
  return s.charAt(0) + "***" + s.substring(at);
}

// F1 回答を設問タイトルのキーワード照合で取り出す（title 完全一致は脆いため部分一致で頑健化）。
// 不適格分岐は連絡先セクション到達前に SUBMIT するため、email/name が無い回答もあり得る（空で返す）。
// ⚠ 制約: find() は最初に一致した設問を採用する。下記キーワード（"OS"/"メールアドレス"/"お名前"/
//   "年齢" 等）を **F1 の別設問に重複させない**こと。特に "OS" を含む設問や "メールアドレス" を
//   含む別設問（確認用メール等）を F1 に追加すると、適格判定・送信先が取り違わる。
//   設問を増やす場合は buildForm() のタイトルとここの照合キーワードを必ず同時に見直す。
function f1Answers_(response) {
  var items = response.getItemResponses();
  function find(predicate) {
    for (var i = 0; i < items.length; i++) {
      var title = String(items[i].getItem().getTitle());
      if (predicate(title)) return items[i].getResponse();
    }
    return null;
  }
  function has(title, kw) {
    return title.indexOf(kw) !== -1;
  }
  var consent1 = find(function (t) { return has(t, "説明を読み"); });
  var consent2 = find(function (t) { return has(t, "記録と研究利用に同意"); });
  var confidential = find(function (t) { return has(t, "口外"); }); // Q2d 秘密保持（高位同意）
  var ndaAgree = find(function (t) { return has(t, "守秘事項"); }); // 末尾: 守秘事項に同意チェック
  var ndaSignature = find(function (t) { return has(t, "署名に代え"); }); // 末尾: 記名署名
  return {
    consent1: asArray_(consent1),
    consent2: asArray_(consent2),
    confidential: asArray_(confidential),
    ndaAgree: asArray_(ndaAgree),
    ndaSignature: trim_(ndaSignature),
    age: find(function (t) { return has(t, "年齢"); }),
    guardian: find(function (t) { return has(t, "保護者同意フォーム"); }),
    ime: find(function (t) { return has(t, "日本語入力") && has(t, "IME"); }),
    os: find(function (t) { return has(t, "OS"); }),
    email: trim_(find(function (t) { return has(t, "メールアドレス"); })),
    name: trim_(find(function (t) { return has(t, "お名前"); })),
  };
}

// チェックボックス回答（配列）を正規化。null/単値も配列にして includes 判定しやすくする。
function asArray_(v) {
  if (v === null || v === undefined) return [];
  return Array.isArray(v) ? v : [v];
}

function trim_(v) {
  return v === null || v === undefined ? "" : String(v).trim();
}

// 適格性判定。Q1理解 ∧ Q2同意 ∧ (18歳以上 ∨ (18歳未満 ∧ 保護者提出済)) ∧ IME=はい ∧ OS∈{Win,mac} ∧ email。
// 返り値 {eligible: bool, reason: string}。
function isEligibleF1_(a) {
  if (a.consent1.indexOf("説明を理解した") === -1) return { eligible: false, reason: "説明理解(Q1)未チェック" };
  if (a.consent2.indexOf("同意する") === -1) return { eligible: false, reason: "記録同意(Q2)未チェック" };
  if (a.confidential.indexOf("同意する") === -1) return { eligible: false, reason: "秘密保持(Q2d)未同意" };

  if (a.age === "18歳未満") {
    if (a.guardian !== "提出済み") return { eligible: false, reason: "未成年で保護者同意(Q4)未提出" };
  } else if (a.age !== "18歳以上") {
    return { eligible: false, reason: "年齢(Q3)未回答" };
  }

  if (a.ime !== "はい") return { eligible: false, reason: "IME利用(Q6)が「はい」でない" };
  if (a.os !== "Windows" && a.os !== "macOS") return { eligible: false, reason: "対象外OS(Q7): " + a.os };
  // 送信先の安全策（多層防御）: F1 Q8 は requireTextIsEmail 済だが、設問取り違え/空を弾く。
  if (!a.email || a.email.indexOf("@") <= 0) return { eligible: false, reason: "連絡先メール(Q8)が空 or 不正形式" };

  return { eligible: true, reason: "" };
}

// Script Properties に記録済みのフォーム公開 URL（回答 URL）を返す。未記録なら空文字。
function formPublishedUrl_(props, key) {
  var raw = props.getProperty("FORMURL_" + key);
  if (!raw) return "";
  try {
    return JSON.parse(raw).publishedUrl || "";
  } catch (e) {
    return "";
  }
}

// 通知メール本文テンプレート。守秘同意は F1 内で記名署名済み（D9）のため、本メールでは P-ID と
// アプリ入手以降の手順、各アンケート(F2/F4/F5)の回答タイミング、公開リンク集を案内する。
// pilot-runbook §3（被験者 3 ステップ）/ 設問草案（F2/F4/F5 の頻度）と整合させる。
// formUrls = {f2, f4, f5}（各フォームの回答 URL。未生成なら空でリンク集へ誘導）。
function f1EmailBody_(pid, formUrls) {
  formUrls = formUrls || {};
  // URL があれば「ラベル: URL」、無ければラベルのみ（リンク集を案内）。
  function link(label, url) {
    return url ? label + "\n      " + url : label + "\n      （下の「すべてのリンク集」からアクセスしてください）";
  }
  return [
    "GSE ユーザー検証へのご参加ありがとうございます。スクリーニングと守秘事項へのご署名を確認しました。",
    "ご参加いただけます。",
    "",
    "■ あなたの参加者ID（P-ID）",
    "    " + pid,
    "    ※ 以降のフォーム回答・ログ提出すべてでこの P-ID を使います。実名は使いません。",
    "",
    "■ アプリの準備と提出（毎セッション）",
    "  1) アプリ一式の入手",
    "     " + APP_DOWNLOAD_INFO,
    "  2) いつも通り作業すると、セッションログが端末に生成されます。",
    "  3) ログを 1 コマンドで匿名化 + 暗号化:",
    "       gse-package --input <生成された.ndjson> --participant " + pid + " --recipient pubkey.txt",
    "     → " + pid + "_*.age ができます（元の生ログは送りません）。pubkey.txt は " + PUBKEY_SOURCE_INFO,
    "  4) Dropbox ファイルリクエストに " + pid + "_*.age を提出:",
    "       " + (DROPBOX_FILE_REQUEST_URL || "（研究者が URL を案内します）"),
    "     （提出者同士は互いのファイルを見られません。中身は研究者だけが復号できます。）",
    "",
    "■ アンケートのご回答（いずれも冒頭の「参加者ID(P-ID)」に " + pid + " を入力してください）",
    "  ● F2 事前アンケート … 検証を【始める前に1回だけ】",
    "      " + link("回答ページ", formUrls.f2),
    "  ● F4 セッション後アンケート … 【各セッションの終了ごとに毎回】（ログ提出の確認も兼ねます）",
    "      " + link("回答ページ", formUrls.f4),
    "  ● F5 事後アンケート … 【全セッション終了後に1回だけ】",
    "      " + link("回答ページ", formUrls.f5),
    "  ※ セッション中の「途中の問い（プローブ）」はアプリ内に表示されます。フォーム回答は不要です。",
    "",
    "■ すべてのリンク集（公開用・ブックマーク推奨）",
    "    " + (PUBLIC_LINKS_URL || "（研究者がリンク集を別途ご案内します）"),
    "",
    "ご不明点があればこのメールにご返信ください。どうぞよろしくお願いいたします。",
  ].join("\n");
}

// 通知メールの HTML 版（スマホ/PC でレスポンシブに綺麗に表示）。f1EmailBody_(プレーンテキスト)を
// フォールバックとして併送する（{htmlBody:} 未対応クライアント向け）。メールクライアントは <style>/
// 外部CSS/メディアクエリを制限するため、レイアウトは max-width:600px + インライン CSS のみで組む
// （スマホは画面幅に収まり、PC は中央 600px で表示される）。
function f1EmailHtml_(pid, formUrls) {
  formUrls = formUrls || {};
  function esc(s) {
    return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }
  // APP_DOWNLOAD_INFO はプレーンテキスト用（先頭スペース整形）なので、各行を trim して <br> 連結。
  var appInfoHtml = String(APP_DOWNLOAD_INFO).split("\n").map(function (l) {
    return esc(l.replace(/^\s+/, ""));
  }).join("<br>");

  var H3 = "margin:28px 0 10px;font-size:17px;font-weight:700;color:#1a3a5c;border-left:4px solid #2f6db5;padding-left:10px;";
  var P = "margin:8px 0;font-size:15px;line-height:1.7;color:#333333;";
  var SMALL = "font-size:13px;color:#777777;line-height:1.6;";
  var CODE = "display:block;background:#f6f8fa;border:1px solid #e1e4e8;border-radius:6px;padding:12px;margin:8px 0;font-family:Menlo,Consolas,monospace;font-size:13px;color:#24292e;white-space:pre-wrap;word-break:break-all;";
  var BTN = "display:inline-block;margin-top:6px;padding:10px 18px;color:#ffffff;text-decoration:none;border-radius:6px;font-size:14px;font-weight:600;";

  function surveyRow(emoji, title, freq, url) {
    var btn = url
      ? '<a href="' + esc(url) + '" style="' + BTN + 'background:#2f6db5;">回答ページを開く</a>'
      : '<span style="' + SMALL + '">（下の「すべてのリンク集」からアクセスしてください）</span>';
    return '<div style="margin:14px 0;padding:14px;background:#f7f9fc;border-radius:8px;">' +
      '<div style="font-size:15px;font-weight:700;color:#1a3a5c;">' + emoji + " " + esc(title) + '</div>' +
      '<div style="' + SMALL + 'margin:4px 0 2px;">' + esc(freq) + '</div>' + btn + '</div>';
  }

  return [
    '<div style="margin:0;padding:0;background:#eef2f6;padding:16px 0;">',
    '<div style="max-width:600px;margin:0 auto;background:#ffffff;border-radius:10px;overflow:hidden;font-family:-apple-system,BlinkMacSystemFont,\'Segoe UI\',Roboto,\'Helvetica Neue\',Arial,sans-serif;">',
    '<div style="background:#1a3a5c;padding:22px 24px;">',
    '<div style="color:#ffffff;font-size:18px;font-weight:700;">GSE ユーザー検証</div>',
    '<div style="color:#a9c4e0;font-size:13px;margin-top:4px;">参加者ID（P-ID）と次のステップのご案内</div>',
    '</div>',
    '<div style="padding:24px;">',
    '<p style="' + P + '">GSE ユーザー検証へのご参加ありがとうございます。スクリーニングと守秘事項へのご署名を確認しました。ご参加いただけます。</p>',
    '<div style="margin:18px 0;padding:18px;background:#eaf2fb;border:1px solid #c5dcf2;border-radius:8px;text-align:center;">',
    '<div style="' + SMALL + '">あなたの参加者ID（P-ID）</div>',
    '<div style="font-size:26px;font-weight:800;color:#1a3a5c;letter-spacing:2px;margin-top:4px;">' + esc(pid) + '</div>',
    '<div style="' + SMALL + 'margin-top:6px;">以降のフォーム回答・ログ提出すべてでこの P-ID を使います（実名は使いません）。</div>',
    '</div>',
    '<div style="' + H3 + '">アプリの準備と提出（毎セッション）</div>',
    '<p style="' + P + '"><b>1) アプリ一式の入手</b><br>' + appInfoHtml + '</p>',
    '<p style="' + P + '"><b>2)</b> いつも通り作業すると、セッションログが端末に生成されます。</p>',
    '<p style="' + P + '"><b>3)</b> ログを 1 コマンドで匿名化＋暗号化:</p>',
    '<code style="' + CODE + '">gse-package --input &lt;生成された.ndjson&gt; --participant ' + esc(pid) + ' --recipient pubkey.txt</code>',
    '<p style="' + SMALL + '">→ ' + esc(pid) + '_*.age ができます（元の生ログは送りません）。pubkey.txt は ' + esc(PUBKEY_SOURCE_INFO) + '</p>',
    '<p style="' + P + '"><b>4)</b> Dropbox ファイルリクエストに ' + esc(pid) + '_*.age を提出:</p>',
    (DROPBOX_FILE_REQUEST_URL
      ? '<a href="' + esc(DROPBOX_FILE_REQUEST_URL) + '" style="' + BTN + 'background:#0061ff;">Dropbox 提出ページを開く</a>'
      : '<span style="' + SMALL + '">（研究者が URL を案内します）</span>'),
    '<p style="' + SMALL + '">提出者同士は互いのファイルを見られません。中身は研究者だけが復号できます。</p>',
    '<div style="' + H3 + '">アンケートのご回答</div>',
    '<p style="' + SMALL + '">いずれも冒頭の「参加者ID（P-ID）」に <b>' + esc(pid) + '</b> を入力してください。</p>',
    surveyRow("📋", "F2 事前アンケート", "検証を始める前に 1 回だけ", formUrls.f2),
    surveyRow("📝", "F4 セッション後アンケート", "各セッションの終了ごとに毎回（ログ提出の確認も兼ねます）", formUrls.f4),
    surveyRow("✅", "F5 事後アンケート", "全セッション終了後に 1 回だけ", formUrls.f5),
    '<p style="' + SMALL + '">※ セッション中の「途中の問い（プローブ）」はアプリ内に表示されます。フォーム回答は不要です。</p>',
    '<div style="' + H3 + '">すべてのリンク集</div>',
    (PUBLIC_LINKS_URL
      ? '<a href="' + esc(PUBLIC_LINKS_URL) + '" style="' + BTN + 'background:#5a6b7b;">リンク集を開く（ブックマーク推奨）</a>'
      : '<span style="' + SMALL + '">（研究者がリンク集を別途ご案内します）</span>'),
    '<p style="' + P + 'margin-top:24px;">ご不明点があればこのメールにご返信ください。どうぞよろしくお願いいたします。</p>',
    '</div>',
    '<div style="padding:16px 24px;background:#f4f6f8;' + SMALL + 'text-align:center;">GSE ユーザー検証 事務局</div>',
    '</div>',
    '</div>'
  ].join("\n");
}

// ロスターに新規参加者行を追加する（ヘッダ行を動的に探し、列順に整合させる）。
function appendRosterRow_(sheet, p) {
  // 列順: P-ID(1) 氏名(2) メール(3) OS(4) 条件(5) F1同意日(6) F2事前(7) セッション数(8)
  //       F4回答(計)(9) F5事後(10) Dropbox提出(11) NDA署名(12) 撤回/除外(13) 備考(14)
  var consent = p.consentDate
    ? Utilities.formatDate(p.consentDate, Session.getScriptTimeZone(), "yyyy-MM-dd")
    : "";
  sheet.appendRow([
    p.pid, p.name || "", p.email || "", p.os || "", p.condition || DEFAULT_CONDITION,
    consent, "", "", "", "", "", p.nda || "未署名", "", "自動発番(onF1Submit)",
  ]);
}

// ロスターのメール列(col 3)を走査し、同一メール（trim/小文字比較）の P-ID を返す。無ければ null。
function findRosterByEmail_(sheet, email) {
  var target = String(email).trim().toLowerCase();
  if (!target) return null;
  var hr = rosterHeaderRow_(sheet);
  if (!hr) return null;
  var last = sheet.getLastRow();
  if (last <= hr) return null;
  var rows = sheet.getRange(hr + 1, 1, last - hr, 3).getValues(); // P-ID, 氏名, メール
  for (var i = 0; i < rows.length; i++) {
    if (String(rows[i][2]).trim().toLowerCase() === target) return rows[i][0];
  }
  return null;
}


// ============================================================
// Task 2: 管理シートでの被験者管理（回答取り込み・ダッシュボード・検証）
// ============================================================

// F2/F4/F5 の回答を P-ID キーで集計し、ロスターの該当列を自動更新する。
// 手動実行 or 時間トリガ（installRosterRefreshTrigger）で回す。destination sheet は不要
// （FormApp.openById(id).getResponses() で直接読む。id は recordFormUrl が保存済み）。
function refreshRosterStatus() {
  var props = PropertiesService.getScriptProperties();
  var ssId = props.getProperty(MGMT_SHEET_PROP);
  if (!ssId) {
    Logger.log("❌ 管理シート未作成。先に buildManagementSheet() を実行してください");
    return;
  }
  var ss = SpreadsheetApp.openById(ssId);
  var sheet = ss.getSheetByName("参加者ロスター");
  if (!sheet) {
    Logger.log("❌ 「参加者ロスター」タブが見つかりません");
    return;
  }
  var hr = rosterHeaderRow_(sheet);
  var last = sheet.getLastRow();
  if (!hr || last <= hr) {
    Logger.log("ℹ️ ロスターに参加者がいません（先に F1 提出 or addParticipant）");
    return;
  }

  // フォーム別 P-ID 集計を作る
  var f2 = countByPid_("F2", props); // {pid: {count, latest}}
  var f4 = countByPid_("F4", props); // セッションIDも集計
  var f5 = countByPid_("F5", props);

  var nRows = last - hr;
  var pids = sheet.getRange(hr + 1, 1, nRows, 1).getValues();
  // 既存値を読み、必要列だけ書き換える（F2事前=7, セッション数=8, F4回答計=9, F5事後=10, Dropbox提出=11）
  var out = sheet.getRange(hr + 1, 7, nRows, 5).getValues();
  for (var i = 0; i < nRows; i++) {
    var pid = String(pids[i][0]).trim();
    if (!/^P\d+$/.test(pid)) continue;
    out[i][0] = f2[pid] ? f2[pid].latest : ""; // F2事前: 最新提出日
    out[i][1] = f4[pid] ? f4[pid].sessions : ""; // セッション数: F4 の distinct session_id 数
    out[i][2] = f4[pid] ? f4[pid].count : ""; // F4回答(計)
    out[i][3] = f5[pid] ? "○" : ""; // F5事後
    // Dropbox提出: F4 の自己申告「提出済み」数 / F4 回答総数（真の提出確認は研究者が Dropbox を参照）。
    out[i][4] = f4[pid] ? f4[pid].dropboxDone + "/" + f4[pid].count + "（F4自己申告）" : "";
  }
  sheet.getRange(hr + 1, 7, nRows, 5).setValues(out);

  buildDashboardTab_(ss); // 集計後にダッシュボードを再描画
  Logger.log("✅ ロスター状態を更新しました（F2/F4/F5 を P-ID で集計）");
}

// 指定フォーム(FORMURL_<key> の id)の回答を P-ID で集計する。
// 返り値: {pid: {count, latest(yyyy-MM-dd), sessions(distinct session_id 数)}}。
function countByPid_(key, props) {
  var raw = props.getProperty("FORMURL_" + key);
  var acc = {};
  if (!raw) return acc;
  var meta = JSON.parse(raw);
  if (!meta.id) {
    Logger.log("⚠️ " + key + ": form id 未記録（build" + key + " を再実行すると id が保存されます）");
    return acc;
  }
  var form;
  try {
    form = FormApp.openById(meta.id);
  } catch (e) {
    Logger.log("⚠️ " + key + ": フォームを開けません（id=" + meta.id + "）: " + e);
    return acc;
  }
  var responses = form.getResponses();
  var tz = Session.getScriptTimeZone();
  for (var i = 0; i < responses.length; i++) {
    var r = responses[i];
    var pid = "";
    var sessionId = "";
    var dropboxAns = ""; // F4 の「Dropbox に提出しましたか？」自己申告（F2/F5 では空のまま）
    var itemResps = r.getItemResponses();
    for (var j = 0; j < itemResps.length; j++) {
      var title = String(itemResps[j].getItem().getTitle());
      if (title.indexOf("参加者ID") !== -1 || title.indexOf("P-ID") !== -1) {
        pid = String(itemResps[j].getResponse()).trim().toUpperCase();
      } else if (title.indexOf("セッションID") !== -1) {
        sessionId = String(itemResps[j].getResponse()).trim();
      } else if (title.indexOf("Dropbox") !== -1 && title.indexOf("提出しましたか") !== -1) {
        dropboxAns = String(itemResps[j].getResponse()).trim();
      }
    }
    if (!/^P\d+$/.test(pid)) continue; // 不正/空 P-ID は集計しない
    if (!acc[pid]) acc[pid] = { count: 0, latest: "", _latestMs: 0, sessions: 0, _sids: {}, dropboxDone: 0 };
    acc[pid].count++;
    if (dropboxAns.indexOf("提出済み") !== -1) acc[pid].dropboxDone++; // 自己申告ベースの提出済みセッション数
    // 最新提出日は timestamp の数値(ms)で比較し、表示時のみ整形する
    // （文字列 "yyyy-MM-dd" 比較は TZ 跨ぎで日付が丸まり誤判定しうるため）。
    var ms = r.getTimestamp().getTime();
    if (ms >= acc[pid]._latestMs) {
      acc[pid]._latestMs = ms;
      acc[pid].latest = Utilities.formatDate(r.getTimestamp(), tz, "yyyy-MM-dd");
    }
    if (sessionId && !acc[pid]._sids[sessionId]) {
      acc[pid]._sids[sessionId] = true;
      acc[pid].sessions++;
    }
  }
  return acc;
}

// 進捗ダッシュボードタブを（再）描画。完了率・未提出者・MNAR 観点の無回答フラグ。
// 撤回/除外（col 13 に値あり）の参加者は集計から除外する。
function buildDashboardTab_(ss) {
  var roster = ss.getSheetByName("参加者ロスター");
  var sh = ss.getSheetByName("進捗ダッシュボード") || ss.insertSheet("進捗ダッシュボード");
  sh.clear();

  var rows = [];
  rows.push(["GSE Phase1 進捗ダッシュボード", "", ""]);
  rows.push(["（自動生成タブ・手動編集禁止。refreshRosterStatus 実行で全再描画されます）", "", ""]);

  var data = readRoster_(roster);
  var active = data.filter(function (d) { return !d.excluded; });
  var n = active.length;
  var f2done = active.filter(function (d) { return d.f2; }).length;
  var f5done = active.filter(function (d) { return d.f5; }).length;
  var ndaDone = active.filter(function (d) { return d.ndaSigned; }).length;
  var sessSum = active.reduce(function (s, d) { return s + (Number(d.sessions) || 0); }, 0);
  var avgSess = n > 0 ? (sessSum / n).toFixed(1) : "0";

  rows.push(["指標", "値", "備考"]);
  rows.push(["登録参加者（撤回/除外を除く）", n, "撤回/除外: " + (data.length - n) + " 名"]);
  rows.push(["NDA 署名済（配布の前提）", ndaDone + " / " + n, n > 0 ? pct_(ndaDone, n) : "—"]);
  rows.push(["F2 事前 完了", f2done + " / " + n, n > 0 ? pct_(f2done, n) : "—"]);
  rows.push(["F5 事後 完了", f5done + " / " + n, n > 0 ? pct_(f5done, n) : "—"]);
  rows.push(["平均セッション数（F4 由来）", avgSess, "セッション総数 " + sessSum]);
  rows.push(["", "", ""]);

  // 未提出者・無回答フラグ（MNAR 観点）
  // ⚠ 実名はこのタブに出さない（PII 露出面の最小化）。突合は P-ID のみで行い、
  //   実名↔P-ID はロスタータブ（機密バナー付き・研究者のみ）に閉じる。
  rows.push(["⚠ 要フォロー（未提出 / 無回答フラグ）", "", ""]);
  rows.push(["P-ID", "フラグ", "セッション数"]);
  var flagged = 0;
  active.forEach(function (d) {
    var flags = [];
    if (!d.ndaSigned) flags.push("NDA未署名(配布前提)");
    if (!d.f2) flags.push("F2未提出");
    // セッションあり（F4回答あり）なのに F5 未 → 終了したのに事後未回答（脱落 MNAR 候補）
    if (Number(d.sessions) > 0 && !d.f5) flags.push("セッション有/F5未(MNAR候補)");
    // F2提出済みなのにセッション 0 → 開始したが収集に至らず（早期脱落 MNAR 候補）
    if (d.f2 && Number(d.sessions) === 0) flags.push("F2済/セッション0(早期脱落候補)");
    if (flags.length > 0) {
      rows.push([d.pid, flags.join(", "), Number(d.sessions) || 0]); // 実名は出さず P-ID のみ
      flagged++;
    }
  });
  if (flagged === 0) rows.push(["（なし）", "", ""]);
  rows.push(["", "", ""]);
  rows.push(["最終更新", Utilities.formatDate(new Date(), Session.getScriptTimeZone(), "yyyy-MM-dd HH:mm"),
    "refreshRosterStatus() で更新"]);

  sh.getRange(1, 1, rows.length, 3).setValues(rows);
  sh.getRange(1, 1).setFontWeight("bold").setFontSize(14);
  sh.getRange(3, 1, 1, 3).setFontWeight("bold");
  sh.setColumnWidth(1, 280);
  sh.setColumnWidth(2, 160);
  sh.setColumnWidth(3, 320);
}

function pct_(a, b) {
  return b > 0 ? Math.round((a / b) * 100) + "%" : "—";
}

// ロスターを構造化して読む。返り値: [{pid,name,os,condition,f2,sessions,f5,ndaSigned,excluded}]。
// ⚠ 列オフセット（[6]=F2事前/[7]=セッション数/[9]=F5/[11]=NDA署名/[12]=撤回）は buildRosterTab_ の
//   header と appendRosterRow_ の列順に固定依存する。列順を変えたら 3 箇所すべてを同時に直すこと。
function readRoster_(sheet) {
  if (!sheet) return [];
  var hr = rosterHeaderRow_(sheet);
  var last = sheet.getLastRow();
  if (!hr || last <= hr) return [];
  var vals = sheet.getRange(hr + 1, 1, last - hr, 14).getValues();
  var out = [];
  for (var i = 0; i < vals.length; i++) {
    var pid = String(vals[i][0]).trim();
    if (!/^P\d+$/.test(pid)) continue;
    out.push({
      pid: pid,
      name: vals[i][1],
      os: vals[i][3],
      condition: vals[i][4],
      f2: !!String(vals[i][6]).trim(), // F2事前(col7)
      sessions: vals[i][7], // セッション数(col8)
      f5: !!String(vals[i][9]).trim(), // F5事後(col10)
      ndaSigned: String(vals[i][11]).trim().indexOf("署名済") !== -1, // NDA署名(col12)
      excluded: !!String(vals[i][12]).trim(), // 撤回/除外(col13)
    });
  }
  return out;
}

// ロスターのデータ検証: condition/OS/撤回 にドロップダウン、撤回/除外 行をグレーアウト。
function applyRosterValidation_(ss) {
  var sheet = ss.getSheetByName("参加者ロスター");
  if (!sheet) return;
  var hr = rosterHeaderRow_(sheet);
  if (!hr) return;
  var startRow = hr + 1;
  var nRows = 500; // 入力余地を見込んで広めに検証範囲を張る

  var condRule = SpreadsheetApp.newDataValidation()
    .requireValueInList(["baseline", "intervention"], true)
    .setAllowInvalid(false)
    .build();
  sheet.getRange(startRow, 5, nRows, 1).setDataValidation(condRule); // 条件(col5)

  var osRule = SpreadsheetApp.newDataValidation()
    .requireValueInList(["Windows", "macOS"], true)
    .setAllowInvalid(true) // 既存記録を弾かないよう許容
    .build();
  sheet.getRange(startRow, 4, nRows, 1).setDataValidation(osRule); // OS(col4)

  var ndaRule = SpreadsheetApp.newDataValidation()
    .requireValueInList(["未署名", "送付済", "署名済"], true)
    .setAllowInvalid(true)
    .build();
  sheet.getRange(startRow, 12, nRows, 1).setDataValidation(ndaRule); // NDA署名(col12)

  var exclRule = SpreadsheetApp.newDataValidation()
    .requireValueInList(["撤回", "除外"], true)
    .setAllowInvalid(true) // 空欄（=有効参加者）を許容
    .build();
  sheet.getRange(startRow, 13, nRows, 1).setDataValidation(exclRule); // 撤回/除外(col13)

  // 撤回/除外に値がある行をグレーアウト（条件付き書式）。既存ルールは置き換える。
  var range = sheet.getRange(startRow, 1, nRows, 14);
  var rule = SpreadsheetApp.newConditionalFormatRule()
    .whenFormulaSatisfied("=$M" + startRow + '<>""') // M列=13列目=撤回/除外
    .setBackground("#e0e0e0")
    .setFontColor("#9e9e9e")
    .setRanges([range])
    .build();
  sheet.setConditionalFormatRules([rule]);
}

// P-ID の形式・重複を検証してログに警告する（手動実行）。条件付き書式での着色も行う。
function validateRoster() {
  var props = PropertiesService.getScriptProperties();
  var ssId = props.getProperty(MGMT_SHEET_PROP);
  if (!ssId) {
    Logger.log("❌ 管理シート未作成。先に buildManagementSheet() を実行してください");
    return;
  }
  var ss = SpreadsheetApp.openById(ssId);
  var sheet = ss.getSheetByName("参加者ロスター");
  var hr = rosterHeaderRow_(sheet);
  var last = sheet.getLastRow();
  if (!hr || last <= hr) {
    Logger.log("ℹ️ ロスターに参加者がいません");
    return;
  }
  var pids = sheet.getRange(hr + 1, 1, last - hr, 1).getValues();
  var seen = {};
  var issues = 0;
  for (var i = 0; i < pids.length; i++) {
    var pid = String(pids[i][0]).trim();
    if (!pid) continue;
    if (!/^P\d{3,}$/.test(pid)) {
      Logger.log("⚠️ 不正な P-ID 形式（行 " + (hr + 1 + i) + "）: '" + pid + "'（期待: P + 3桁以上）");
      issues++;
    }
    if (seen[pid]) {
      Logger.log("⚠️ P-ID 重複（行 " + (hr + 1 + i) + "）: " + pid);
      issues++;
    }
    seen[pid] = true;
  }
  Logger.log(issues === 0 ? "✅ ロスター検証 OK（形式・重複に問題なし）" : "⚠️ ロスター検証: " + issues + " 件の問題");
}

// refreshRosterStatus() を定期実行する時間トリガを設定する（任意・既存を置換）。
function installRosterRefreshTrigger() {
  var triggers = ScriptApp.getProjectTriggers();
  for (var i = 0; i < triggers.length; i++) {
    if (triggers[i].getHandlerFunction() === "refreshRosterStatus") {
      ScriptApp.deleteTrigger(triggers[i]);
    }
  }
  ScriptApp.newTrigger("refreshRosterStatus").timeBased().everyHours(6).create();
  Logger.log("✅ refreshRosterStatus を 6 時間ごとに自動実行するトリガを設定しました");
}


// ============================================================
// ヘルパー: 既存設問の安全な全削除（分岐ナビゲーション対応）
// ============================================================
// buildForm を 2 回目以降に実行すると、F1 フォームが持つ分岐
// （Q3/Q4/Q6/Q7 の go-to-page 選択肢・ページの setGoToPage(SUBMIT)）が原因で
// 末尾からの deleteItem が "Invalid data updating form" を投げる
// （まだ参照されているページを先に削除してナビゲーションが orphan 化するため）。
// 対策: 削除の前に全ナビゲーション参照を解除（選択肢を plain 化・ページを CONTINUE 化）し、
// クロス参照を断ってから削除する。
function clearForm(form) {
  var items = form.getItems();

  // 1) 分岐ナビゲーションを解除（go-to-page 参照を断つ）
  for (var i = 0; i < items.length; i++) {
    var type = items[i].getType();
    try {
      if (type === FormApp.ItemType.MULTIPLE_CHOICE) {
        var mc = items[i].asMultipleChoiceItem();
        mc.setChoices(mc.getChoices().map(function (c) { return mc.createChoice(c.getValue()); }));
      } else if (type === FormApp.ItemType.LIST) {
        var li = items[i].asListItem();
        li.setChoices(li.getChoices().map(function (c) { return li.createChoice(c.getValue()); }));
      } else if (type === FormApp.ItemType.PAGE_BREAK) {
        items[i].asPageBreakItem().setGoToPage(FormApp.PageNavigationType.CONTINUE);
      }
    } catch (e) {
      // ナビゲーションを持たない項目（Checkbox/Scale/Text 等）はスキップ
    }
  }

  // 2) ナビゲーション解除後に末尾から全削除（安全に消える）
  var remaining = form.getItems();
  for (var j = remaining.length - 1; j >= 0; j--) {
    form.deleteItem(remaining[j]);
  }
}


// ============================================================
// ヘルパー: セクションヘッダー追加
// ============================================================
function addSectionHeader(form, title, description) {
  var section = form.addSectionHeaderItem();
  section.setTitle(title);
  if (description) {
    section.setHelpText(description);
  }
}
