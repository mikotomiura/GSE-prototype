# p321-paper-revision

## 背景

2 本目の論文 "When "no help" is not "solved": outcome-agnostic self-resolution measures in two public debugging datasets"（単著・論文用リポジトリ `C:/self-resolution-measure` = `mikotomiura/self-resolution-measure`）を 2026-09-29 に EMSE に投稿した（EMSE-D-26-01273）。2026-11-21 に査読に回らず不採択になった。理由は「投稿の急増で査読の手が足りない」で、原稿の中身への判断は付いていない（`.steering/20260929-p321-paper-submission-prep/decisions.md` 判断 24）。

投稿の後に当てたプレ査読（attack-me round 1・`.steering/20260929-p321-paper-submission-prep/attack-me/manuscript-emse/round-1/verdict.md`）では、査読者 3 人がそろって major だった。崩れているのは主張の外延で、論点は次の 3 つ。(1) 見出しの 11.2pp が「episode の中で未解決」を失敗に数える 1 つの選択の上に立っている。(2) 動機にした誤読の実例が無い。(3) 名前と用語が揃っていない。投稿していたあいだは原稿を変えられなかったが、いまは自由に変えられる。

## ゴール

verdict §5 の major 1〜10 と minor をすべて直した原稿を作る。直した版で attack-me round 2 と `/cross-review` を通し、研究者が選んだ別の雑誌（条件は登壇なし・費用ゼロ・購読型）に、研究者が投稿できる状態にする。改訂版の再現一式は新しいタグと Zenodo の新しい版で出し、プレプリントも Zenodo に置く（publish は研究者の確認の後）。

## スコープ

### 含むもの
- 出し先の候補を一次で比べる（費用・範囲・頁の上限・クラス・プレプリントの規程）→ 研究者が選ぶ
- verdict §5 の major 1〜10 と minor（nit も一緒に拾う）。方針は decisions.md 判断 1〜9
- 原著者（Alaboudi & LaToza）への照会の文面の下書き（送るのは研究者）
- 誤読の実例の検索（手順を先に決める）と、クラスタが少ないときの区間の手法の文献での確認（`citation-ssot`）
- D1 の episode 単位の派生表のアーカイブ（元データのライセンスが再配布を許す場合だけ）
- 題の案を 2〜3 本（用語をそろえた後）
- attack-me round 2・`/cross-review`
- 新しいタグ・Zenodo の新しい版（再現一式）・Zenodo のプレプリント（下書きまで Claude・publish は研究者）
- 出し先の書式への組み替え（cls・タイトル頁・声明）

### 含まないもの
- 新しいデータの収集・新しいデータセットの追加
- 凍結した主の定義（8 定義と R0）の変更（足すのは感度分析と補助の区間だけ）
- 公開済みのタグ `submission-2026-09-29` と Zenodo 23029603 の書き換え（EMSE 版として残す）
- arXiv（endorsement は止める。Shepperd には頼まない）
- 投稿の操作そのもの（研究者が行う）・原著者へのメールの送信（研究者が行う）
- 有料の文献・有料のデータベース

## 受け入れ条件

- [ ] 出し先が決まり、その規程の一次の確認が decisions.md にある（費用 0・登壇なし・プレプリントを許す）
- [ ] verdict §5 の major 1〜10 と minor が、それぞれ「直した箇所」か「直さない理由」で tasklist に閉じている
- [ ] 論文用リポジトリで `bash run.sh` と `bash paper/build.sh` が exit 0（自己検査を含む）
- [ ] 要旨・結論の数字が `results.tex`（機械生成）と一致する（自己検査で）
- [ ] attack-me round 2 の verdict が fatal 0・major 0、または残った major に研究者が採否を決めている
- [ ] `/cross-review`（Claude ＋ Codex）の指摘が裁定されている
- [ ] 新しいタグと Zenodo の版（再現一式・プレプリント）の下書きができ、研究者が publish した
- [ ] 原著者への照会を研究者が送り、その日付が記録されている

## 関連ドキュメント

- `.steering/20260929-p321-paper-submission-prep/`（判断 1〜24・attack-me round 1）
- `.steering/20260928-p321-reanalysis-paper/`・`.steering/20260928-p321-paper-draft/`
- memory: `feedback_venue_no_talk_zero_cost`・`feedback_no_paid_access`・`feedback_public_artifacts_academic_no_gse`・`reference_zenodo_token`・`reference_codex_review_other_repo`

## 運用メモ
- /reimagine 適用: Yes
- 理由: 研究者の選択（2026-11-21）。私の推奨は「使わない」（方針は判断 1〜9 で確定済み）だったが、研究者は改訂の設計（順序・節の組み替え）を作り直して比べることを選んだ。design.md を書いた後、着手の前に実行する。
- issue 単位のループ: 使わない（原稿の改訂は節どうしが絡み、Allowed Files を分けられない）
