const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType,
  HeadingLevel, ShadingType, PageOrientation, LevelFormat, AlignmentType, BorderStyle, TableLayoutType,
} = require("docx");

const FONT = "Yu Gothic";
const PAGE_W = 16838, PAGE_H = 11906, MARGIN = 1000;
const CONTENT_W = PAGE_W - 2 * MARGIN; // landscape content width

// "**bold**" をラン配列にする
function runs(text, opts = {}) {
  const out = [];
  const parts = String(text).split(/(\*\*[^*]+\*\*)/g);
  for (const p of parts) {
    if (!p) continue;
    const bold = p.startsWith("**") && p.endsWith("**");
    out.push(new TextRun({ text: bold ? p.slice(2, -2) : p, bold: bold || opts.bold, size: opts.size, color: opts.color }));
  }
  return out;
}
const P = (t, o = {}) => new Paragraph({ children: runs(t, o), spacing: { after: 80 }, ...o.para });
const H1 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun(t)], spacing: { before: 240, after: 120 } });
const H2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(t)], spacing: { before: 200, after: 100 } });
const B = (t) => new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: runs(t), spacing: { after: 60 } });
const NOTE = (t) => new Paragraph({
  children: runs(t, { size: 19 }), spacing: { after: 80 },
  shading: { type: ShadingType.CLEAR, fill: "FFF4E5", color: "auto" },
  border: { left: { style: BorderStyle.SINGLE, size: 18, color: "E08A00", space: 6 } },
});

// 表: widths は比率。セルの "\n" は段落に分ける
function T(header, rows, ratios) {
  const sum = ratios.reduce((a, b) => a + b, 0);
  const widths = ratios.map((r) => Math.floor((CONTENT_W * r) / sum));
  widths[widths.length - 1] += CONTENT_W - widths.reduce((a, b) => a + b, 0);
  const cell = (text, i, head) => new TableCell({
    width: { size: widths[i], type: WidthType.DXA },
    shading: head ? { type: ShadingType.CLEAR, fill: "DCE6F1", color: "auto" } : undefined,
    margins: { top: 60, bottom: 60, left: 90, right: 90 },
    children: String(text).split("\n").map((line) => new Paragraph({ children: runs(line, { bold: head, size: 18 }) })),
  });
  return new Table({
    layout: TableLayoutType.FIXED,
    width: { size: CONTENT_W, type: WidthType.DXA },
    columnWidths: widths,
    rows: [
      new TableRow({ tableHeader: true, children: header.map((h, i) => cell(h, i, true)) }),
      ...rows.map((r) => new TableRow({ children: r.map((c, i) => cell(c, i, false)) })),
    ],
  });
}
const GAP = () => new Paragraph({ children: [], spacing: { after: 120 } });

const body = [];
const add = (...xs) => body.push(...xs);

add(new Paragraph({ heading: HeadingLevel.TITLE, children: [new TextRun("G1 / O1 運営ワークフロー")] }));
add(P("どのフォームを、いつ、誰が記入・送付するか — 参加者 1 人を受け入れてから終えるまで", { size: 24 }));
add(P("作成 2026-10-07 ／ 研究者用（非公開）／ 版 2（O1 リンク集を追加）"));
add(NOTE("この文書は索引です。手順の本文は各行の「正本」（リポジトリ GSE-prototype の中のファイル）にあります。食い違ったら正本が正しいものとします。"));
add(NOTE("書いてあるのはコードと文書の記述です。Drive・フォーム・Apps Script の実物の状態ではありません。実物は「0. 始める前のゲート」と人手の記録票で確かめます。"));
add(GAP());
add(T(["研究", "中身", "期間", "主な正本"], [
  ["**G1**", "統制課題実験（10 ブロック・約 70 分・課題ページに文章を書く）", "1 回", "experiments/20260801-controlled-friction-task/protocol.md\nForm_G1/README.md"],
  ["**O1**", "ふだんの作業の常時記録（形成的・ADR-014）", "3〜5 名 × 3 週間（暫定・事前登録草案 §3）\n※ 同意文書の表記は「数日〜数週間」", "Form_O1/*.gs の冒頭コメント\ndocs/o1-roster-operations.md\ndocs/o1-deletion-ledger.md"],
], [1, 4, 3, 4]));

add(H1("0. 始める前のゲート（通過するまで始めない）"));
add(T(["対象", "コマンド（リポジトリ直下で）", "2026-10-07 の結果"], [
  ["G1 の新コホートの収集", "bash scripts/check-g1-collection-readiness.sh", "通過 26/26（gse-dataset の schema を PR #2 で同期した後）"],
  ["O1 の配布", "bash scripts/check-o1-release-readiness.sh", "通過 24/24（Form_O1/o1_submit.json を置き、秘密の値の混入の判定まで含む）"],
], [2, 4, 4]));
add(B("G1 のゲートが見ていないもの: 配布したアプリの実行時の挙動・Drive とフォームの実物・CI の実行。→ 人手の記録票 collection-readiness-record.md。"));
add(B("O1 のゲートの [5] は、手順書に「案内日を分ける」規則があるかを見るだけで、**実際に日を分けたかは見ない**。"));
add(B("O1 のゲートは、Form_O1/o1_submit.json の無い機械では秘密の値の混入を判定しない（「未確認」と出る）。"));

add(H1("1. 1 人の参加者についての大原則"));
add(T(["#", "原則", "正本"], [
  ["1", "**O1 に先に参加した人を G1 に入れない**（取り返せない）。G1 → O1 は、G1 の完了（か本人の「やめた」）の後・**翌日以降**・別の同意・**同じ P-ID**", "docs/person-lifecycle-ledger-template.md §1 制約 4・ADR-034 D4-2"],
  ["2", "**G1 と O1 の記録は結合しない**", "同 制約 5・ADR-034 D4-6 / D4-7"],
  ["3", "**G1 と O1 の案内を同じ日に出さない**（2 つの登録フォームは別の Apps Script で、採番の排他が効かない）", "docs/o1-roster-operations.md §5"],
  ["4", "**P-ID は Phase1 と共有**。既に P-ID を持つ人は再利用、新規は採番", "Form_G1/README.md・protocol.md §2.0"],
  ["5", "「中断」「やめた」「削除の求め」は**別の申し出**。本人の申し出で確定し、**理由は聞かない**", "docs/person-lifecycle-ledger-template.md §1 制約 1〜3"],
  ["6", "**記録は公開しない**（G1 は「生ログは公開しません」と約束済み・O1 は公開の同意を取っていない）。公開と 2 本目の論文の扱いは ADR-039", "ADR-039 D1・D2・D8"],
], [0.4, 7, 3]));

add(H1("2. フォームの早見表"));
add(T(["フォーム", "研究", "記入", "いつ", "回数", "記入すると自動で起きること"], [
  ["**G1-C 説明・同意（＝参加登録）**", "G1", "参加者", "募集時（当日その場でも可）", "1", "onG1ConsentSubmit: P-ID の検証 → 採番（既存なら再利用）→ 管理シート「G1 実施トラッキング」に行 → **受付メール**"],
  ["**G1-M 強制比較**", "G1", "参加者", "**ブロック 3〜9 の直後**の 1 分休憩の中", "7", "なし（1 時間ごとの集計で「G1-M 回答数」が埋まる）"],
  ["**G1-S 終了後アンケート**", "G1", "参加者", "**最後のブロックの後**。デブリーフはこの**後**に渡す", "1", "なし（集計列が埋まる）"],
  ["**O1-C 説明・同意（＝参加登録）**", "O1", "参加者", "募集時。**配布物と入手先 URL がそろってから** URL を渡す", "1", "onO1ConsentSubmit: 採番 → 管理シート「O1 登録ログ」→ **受付メール**（P-ID・アプリの入手先・毎日の起動・止める/消す・連絡先）"],
  ["**O1-S 終了後アンケート**", "O1", "参加者\n（URL は**研究者が手で送る**）", "**終了判定の後**、研究者が 1 人ずつ終了の連絡と一緒に送る（O-7）", "1", "なし（自動の送付は無い。研究者の手動）"],
], [3, 0.7, 1.6, 3.4, 0.6, 4.5]));
add(GAP());
add(P("**管理シート・台帳（研究者が見る・非公開）**"));
add(T(["シート", "研究", "更新", "正本"], [
  ["「リンク集」「G1 実施トラッキング」", "G1", "登録時に行・**1 時間ごと**に集計列（refreshG1RunSheet）", "Form_G1/README.md"],
  ["**「O1 リンク集」**（2026-10-07 追加）", "O1", "refreshO1LinksTab() か buildO1MgmtSheet() で作り直す。O1-C / O1-S の回答 URL と編集 URL・アプリの入手先・他のタブと文書の所在・手で入れる欄（受取フォルダ・終了判定の基準・メモ。作り直しても保つ）。参加者ロスターへのリンクは置かない", "GSE_O1_Form_Builder.gs の o1BuildLinksTab_"],
  ["「O1 登録ログ」「O1 却下ログ」", "O1", "登録時（追記のみ・氏名とメールは無し）", "GSE_O1_Form_Builder.gs の buildO1MgmtSheet"],
  ["「O1 受領台帳」「O1 途絶」", "O1", "**6 時間ごと**（o1LedgerRun）。途絶（最終受領から 5 日）・欠番（5 日）・未受領（登録から 7 日）を、悪化したときだけ研究者宛てに 1 通で通知。被験者には送らない", "Form_O1/GSE_O1_Ledger.gs"],
  ["**「O1 終了判定」（新設・未実装）**", "O1", "6 時間ごと（受領台帳と同じ走査）に、人ごとの期間が終わったかを機械的に判定する。研究者は「終了連絡日」「O1-S 送付日」「最終日の受領確認」を記入（§4 O-7・§6 の 2）", "未作成（実装は別タスク）"],
  ["人単位の台帳", "両方", "手入力（同意の版・やめた・削除の求め・終了連絡）", "docs/person-lifecycle-ledger-template.md（設計のみ・実物は未作成）"],
], [3, 0.7, 6, 3.3]));

add(H1("3. G1 — 時系列"));
add(T(["段階", "誰が", "何をする", "使うもの", "自動で起きること", "正本"], [
  ["**G-0** 基盤（1 度だけ）", "研究者", "受け口の配備・トリガー 3 本（installG1ConsentTrigger・installMaterialsAutoSendTrigger・installRunSheetRefreshTrigger）・Drive の親フォルダを「制限付き」に", "Form_G1/", "—", "Form_G1/README.md 配備手順"],
  ["**G-1** 前日まで", "研究者", "割付（assign.py・validate_blocks.py）→ 課題ページ → 配布フォルダ（make-distribution.sh・prepare-subjects.sh）→ Drive へ上げて照合（verify-drive-upload.py が通るまで URL を配らない）。共通アプリ zip は make-common-app-zip.sh --mode g1 --tag v0.1.36（G1 の配布物は最初の配布のタグで固定）", "experiments/20260801-controlled-friction-task/", "—", "protocol.md §2.1・§6「前日まで」・distribution-tag.md・ADR-034 D3"],
  ["**G-2** 募集・登録", "研究者 → 参加者", "案内（**O1 と別の日**）→ 参加者が **G1-C**", "G1-C", "採番・トラッキング行・**受付メール**", "Form_G1/README.md・o1-roster-operations.md §5"],
  ["**G-3** 日程・事前資料", "研究者", "日程は返信で決める（自動化なし）。管理シートの「配布フォルダURL」列に URL を貼る", "管理シート", "**1 時間以内に事前資料メール**（7 本のガード・送付日を記録）", "Form_G1/README.md"],
  ["**G-4** 初回起動", "研究者＋参加者", "zip を展開して初回起動。**研究者が同席**（macOS は必須・Windows は「G1 モードで動作しています」を目視）", "同梱の README・初回セットアップ_mac.sh", "—", "protocol.md §1.1「第 13 版の手順」"],
  ["**G-5** 当日・開始前", "研究者", "**G1-C が回答済みか**を確かめる（同意の正本）→ participant-guide.md を渡す（冒頭の実験者向け注記は切り取る）。ブロック 1 を起動した直後に HMM_VERSION を読んで記録", "G1-C の回答・participant-guide.md", "—", "protocol.md §4.1・§6・§6.1"],
  ["**G-6** 10 ブロック", "参加者", "ページを開いてからアプリの「開始する」。**ブロック 3〜9 の直後に G1-M**", "課題ページ・**G1-M**", "ブロックごとに暗号化ファイルを作り「送信しますか？」→ 押すと Drive へ", "protocol.md §4.2・§6（無人在宅は §4b）"],
  ["**G-7** 終了", "参加者 → 研究者", "**G1-S** → その**後**に debrief.md（口外しないお願いを読み上げる）。画面で「未確認 0・未送信 0」を確認。お礼メール（sendThankYouEmail・手動）", "**G1-S**・debrief.md", "集計列が 1 時間ごとに更新", "protocol.md §6「当日・終了後」"],
  ["**G-8** 受領・検証", "研究者", "analyze.py --verify-blocks・forms_to_blocks.py・validate_blocks.py --dataset。復号は gse-unpack。**gse-dataset へ送るときは G1 のセッションだと明記し、Phase1 の較正プールに入らないことを確かめる**（P-ID 共有のため）。G1 の解析は meta に g1_mode と app_version = 0.1.36 を持つファイルだけ", "—", "—", "protocol.md §6・data.md B-4・distribution-tag.md・pilot-runbook.md §4.1"],
  ["**G-9** やめた・削除の求め（随時）", "参加者 → 研究者", "**やめた**: 理由を聞かず、その場で**削除も希望するかを必ず確かめ**、人単位の台帳に書く（沈黙を「削除は求めていない」と読まない）。\n**削除の求め**: P-ID と範囲だけ受け取る → チェックリスト → 削除台帳に 1 行", "—", "—", "docs/g1-deletion-ledger.md §1〜§3・§5"],
], [1.6, 1.1, 5, 1.8, 2, 2.2]));

add(H1("4. O1 — 時系列"));
add(T(["段階", "誰が", "何をする", "使うもの", "自動で起きること", "正本"], [
  ["**O-0** 基盤（1 度だけ）", "研究者", "Apps Script 3 プロジェクト（フォームビルダー・受け口・受領台帳）に貼り、スクリプト プロパティを設定。checkO1FormConfig → buildO1MgmtSheet → checkO1MgmtSheet → setupO1Forms → refreshO1LinksTab（リンク集）→ previewO1RegisterAckEmail → installO1ConsentTrigger。受け口のデプロイ。台帳は o1LedgerCheck → o1LedgerRun → installO1LedgerTrigger", "Form_O1/*.gs", "設定が欠ければ止まる（fail-closed）", "各 .gs の冒頭コメント"],
  ["**O-1** 同意文書の改訂（版が変わるとき）", "研究者", "consent-draft-o1.md を**先に**直す → GSE_O1_Form_Builder.gs に写す → node Form_O1/o1_form_builder_test.cjs → migrateO1ConsentForm()（setupO1Forms で作り直さない）", "—", "新しい同意項目は**末尾**に付き、既に回答した人は未同意（ログで警告）", "GSE_O1_Form_Builder.gs"],
  ["**O-2** 配布物", "研究者", "make-common-app-zip.sh --mode o1 --tag v0.1.40 --config Form_O1/o1_submit.json → **O1 専用**の Drive フォルダ → O1_APP_DOWNLOAD_URL に設定。使ったタグを記録", "—", "—", "docs/o1-distribution-tag.md §v0.1.40"],
  ["**O-3** 募集・登録", "研究者 → 参加者", "案内（**G1 と別の日**）→ 参加者が **O1-C**。ロスターに**氏名だけの行を先に作らない**。登録後に checkO1RosterShape で行の増加を確かめてから氏名を埋める。案内の翌日にロスター A 列の重複を確かめる", "**O1-C**", "採番・登録ログ・**受付メール**", "docs/o1-roster-operations.md §2・§5"],
  ["**O-4** 初回起動", "研究者＋参加者", "**macOS は研究者と一緒に**初回セットアップ（約 5 分・対面か画面共有）。最初の画面で**参加者 ID の入力と同意の確認**（1 つの操作）", "同梱の README_先に読む.txt【1】", "確認後、ログイン時の**自動起動が 1 回だけ登録**される。確認までは研究者へ送らない", "dist-readme-macos-o1.txt・dist-readme-windows-o1.txt"],
  ["**O-5** 常時記録（3 週間・暫定）", "参加者", "ふだんどおり作業。作業種別の宣言（5 択・忘れてよい）。記録中は印が出る。一時停止・時間帯の削除ができる", "アプリ", "1 日ごとに閉じ、**48 時間後**に暗号化して自動送信 → 受け口が参加者ごとのフォルダに保存", "同意フォームの説明・README【3】〜【6】"],
  ["（該当者のみ）", "研究者 → 参加者", "文字をあまり打たない作業の人に、別の測定（宣言ブロック）・短い画面録画を**後日あらためて個別に**お願いすることがある（O1-C では同意を取らない）", "個別の説明と同意", "—", "consent-draft-o1.md §6（運用しているかは未確認）"],
  ["**O-6** 見守り（期間中）", "研究者", "台帳の通知を見て連絡する。**「途絶」を「やめた」に変換しない**。通知は悪化したときだけ来る。トリガーが消える・認可が切れると何も来ないので、**通知が無いことは異常が無い証拠にならない** → 台帳の「更新」時刻を見る", "「O1 受領台帳」「O1 途絶」", "6 時間ごとに更新・悪化時に通知", "GSE_O1_Ledger.gs 冒頭"],
  ["**O-7a** 終了判定", "**運営シート（機械）**", "人ごとに期間が終わったかを判定し、「O1 終了判定」タブに「終了（連絡待ち）」と出す。基準は §6 の 2（研究者が決める）", "「O1 終了判定」（未実装）", "6 時間ごとに判定（予定）", "—（実装は別タスク）"],
  ["**O-7b** 終了の連絡と O1-S", "**研究者（手動・1 人ずつ）**", "終了判定が出た人に、個別に連絡する: (1) 研究が終わったこと・お礼 (2) **O1-S の URL**（「O1 リンク集」の O1-S 回答 URL） (3) アプリの片づけ方。**最終日の記録の受領を台帳で確かめてから**、「自動起動をオフ → フォルダを消す」を案内する（先に消すと、48 時間待ちの最後の記録が届かない）。台帳に「終了連絡日」「O1-S 送付日」を書く", "メール・**O1-S**・README【4】末尾", "—", "README【4】【5】（文面は研究者が作る・被験者向け文書）"],
  ["**O-7c** アンケートと片づけ", "参加者", "**O1-S** に回答（約 5 分）→ 自動起動をオフ → フォルダを消す（分からなければ研究者が一緒に行う）", "**O1-S**", "—", "README【3】【4】"],
  ["**O-8** 受領・復号", "研究者", "gse-unpack で復号。**gse-dataset へ出さない**（削除が git 履歴の書き換えになるため sync-session が O1 を弾く）。解析は事前登録（凍結後）どおり。(P-ID, o1_install_id) で端末を分ける", "—", "—", "pilot-runbook.md §4.1〜4.2・o1-deletion-ledger.md §4"],
  ["**O-9a** やめた（随時）", "参加者 → 研究者", "理由を聞かず、その場で**削除も希望するかを確かめ**、人単位の台帳に書く。**削除の求めが無くても自動起動を外してもらう**（外さないと次のログインで記録が再開する）", "—", "—", "o1-deletion-ledger.md §2・§3 B-8・person-lifecycle-ledger-template.md 制約 3"],
  ["**O-9b** 削除の求め（随時）", "参加者 → 研究者", "理由を聞かず P-ID と時間帯だけ受け取る → チェックリスト A（研究者側）・B（端末側）→ 削除台帳に 1 行。登録ログと受領台帳は**行を消さず**該当列を空にして「削除済」にする（手作業）", "—", "—", "o1-deletion-ledger.md §2・§3・§6"],
], [1.6, 1.3, 5, 1.8, 2, 2.1]));

add(H1("5. 2026-10-07〜08 の O1 開始に固有のこと"));
add(T(["いつ", "誰が", "何をする", "正本"], [
  ["10-07", "研究者", "Drive の zip を v0.1.40 に差し替える", "docs/o1-distribution-tag.md §v0.1.40"],
  ["10-07", "研究者", "同意の改訂（識別子の 1 行＋結果の公表と記録の公開の一文）を O-1 の手順で反映", ".steering/20261007-o1-install-id/consent-revision-proposal.md\n.steering/20261007-research-use-and-release/o1-consent-today-proposal.md"],
  ["10-07", "研究者", "**反映の前に登録した人がいれば**、新しい項目について説明して同意を取り直す（取り直すまで、その人の結果は公表の対象にしない）", "ADR-039 D2"],
  ["10-08", "研究者", "O1 の案内（G1 の案内と同じ日にしない）", "§1 の原則 3"],
  ["随時", "研究者", "参加者ごとに**どの版の同意に答えたか**を人単位の台帳に記録する（再同意で足りない層だけを尋ねるため）", "ADR-039 D2・D4"],
  ["並行", "研究者", "倫理の問い合わせ（ZEN大学 → 外部の委員会 → BRM の編集者）", ".steering/20261007-research-use-and-release/inquiry-drafts.md"],
], [1, 1.2, 7, 4]));

add(H1("6. まだ決まっていない・仕組みが無いもの"));
add(T(["#", "項目", "状態", "次にすること"], [
  ["1", "O1-S の URL を誰がいつ渡すか", "**決定（2026-10-07）**: 終了判定の後、研究者が 1 人ずつ手で送る（O-7b）", "連絡文の文面を作る（被験者向け文書なので研究者が承認）"],
  ["2", "O1 の期間の終わりの判定", "**方針決定・未実装**: 非公開の運営スプレッドシートが機械的に判定し（O-7a）、研究者が個別に連絡する（O-7b）", "基準を決める: (a) 起算点（登録日か、最初の記録の受領日か） (b) 日数（事前登録草案は暦日 21 日を下限に検討中） (c) 有効日の数を条件にするか。決まったら受領台帳の Apps Script に「O1 終了判定」タブを足す（検査つき・別タスク）"],
  ["3", "G1 の受領ファイルの復号を G1 向けに書いた手順が無い（data.md に送付の流れはあるが復号のコマンドは無い）", "未対応", "G1 向けの復号の数行を data.md に足す"],
  ["4", "人単位の台帳の実物が無い（設計のみ）", "未対応", "テンプレートから実物を作る。列に「同意の版」「終了連絡日」「O1-S 送付日」を含める"],
  ["5", "O1 の期間の表記が、同意文書（「数日〜数週間」）と事前登録草案（3 週間）でずれる", "未決", "受付メールか終了の連絡で、期間を具体にするかを決める"],
  ["6", "O1 の「やめた」の扱いが正本どうしで食い違う（削除台帳は「全期間を削除」、人単位の台帳のテンプレートは「削除は別の申し出」）", "未決", "本書の O-9a は後者（削除の希望を確かめる）に寄せた。正本どうしを揃える"],
  ["7", "README【4】は「研究が終わったら自動起動をオフにしてフォルダを消す」とだけ書いており、最後の送信を待つことが書かれていない", "未対応", "当面は終了の連絡（O-7b）で「受領を確かめるまで消さない」と伝える。README を直すかは研究者が決める（配布物の版が変わる）"],
], [0.4, 4.5, 4, 5]));

add(H1("関連"));
add(B("ADR-014（O1）・ADR-034（G1 と O1 の並行）・ADR-038（o1_install_id）・ADR-039（研究利用と公開）"));
add(B("docs/g1-deletion-ledger.md・docs/o1-deletion-ledger.md・docs/person-lifecycle-ledger-template.md"));
add(B("docs/o1-roster-operations.md・docs/o1-distribution-tag.md・docs/pilot-runbook.md §4"));

const doc = new Document({
  creator: "GSE",
  title: "G1 / O1 運営ワークフロー",
  styles: {
    default: { document: { run: { font: { ascii: FONT, eastAsia: FONT, hAnsi: FONT }, size: 20 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 28, bold: true, color: "1F3864" } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 24, bold: true } },
      { id: "Title", name: "Title", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 36, bold: true } },
    ],
  },
  numbering: { config: [{ reference: "bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 360, hanging: 260 } } } }] }] },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838, orientation: PageOrientation.LANDSCAPE }, margin: { top: MARGIN, bottom: MARGIN, left: MARGIN, right: MARGIN } } },
    children: body,
  }],
});

Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(process.argv[2], buf); console.log("wrote", process.argv[2]); });
