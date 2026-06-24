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
var CLEAR_EXISTING = true; // 既存設問を削除してから投入するか

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

  // 既存設問を全削除
  if (CLEAR_EXISTING) {
    var items = form.getItems();
    for (var i = items.length - 1; i >= 0; i--) {
      form.deleteItem(items[i]);
    }
    // 既存セクション（ページ区切り）も含めて削除済み
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
    "対応表は共有されません。いつでも理由を告げずに参加を撤回でき、提出済みデータの削除を求められます。"
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
  var form = FormApp.create("GSE ユーザー検証 Phase1 – F2 事前アンケート（ベースライン）");
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

  Logger.log("✅ F2 事前アンケート作成完了");
  Logger.log("🔗 編集URL: " + form.getEditUrl());
  Logger.log("🔗 回答URL: " + form.getPublishedUrl());
}


// ============================================================
// F3: プローブ申告フォーム（Q1/Q2）
// ============================================================
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
  var form = FormApp.create("GSE ユーザー検証 Phase1 – F4 セッション後アンケート");
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
  // ログ突合キーは F3 と同形式のセッションIDで統一する（"s03" 等の略記はログの session_id と
  // 一致せず join が壊れるため）。
  var snum = form.addTextItem();
  snum.setTitle("セッションID（エディタ画面に表示されている ID。F3 と同じ形式）");
  snum.setHelpText("例: ses_20260624_001。ログとの突合に使用します。");
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
  // (create 方式には不要だったが openById では必須)。
  if (CLEAR_EXISTING) {
    var items = form.getItems();
    for (var i = items.length - 1; i >= 0; i--) {
      form.deleteItem(items[i]);
    }
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
    "1: 全く当てはまらない　2: 当てはまらない　3: まあ当てはまる　4: 全くその通り"
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
    "作業負荷（NASA-TLX 簡易版）",
    "Phase 1 全体を通じての感覚でお答えください。\n1: 非常に低い　〜　5: 非常に高い"
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

  Logger.log("✅ F5 事後アンケート作成完了");
  Logger.log("🔗 編集URL: " + form.getEditUrl());
  Logger.log("🔗 回答URL: " + form.getPublishedUrl());
}


// ============================================================
// F2〜F5 を一括作成するユーティリティ
// ============================================================
function buildAllSupportForms() {
  buildF2();
  buildF3();
  buildF4();
  buildF5();
  Logger.log("🎉 F2〜F5 全フォーム作成完了。上記の編集URLをスプレッドシート等に保存してください。");
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
