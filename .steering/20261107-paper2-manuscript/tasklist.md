# タスクリスト

## 準備
- [x] 引き継ぎ・外枠 v8・判断 1〜16・notes.md・conditions.md・論文 1 の原稿の形を読む

## 原稿（paper-write Step 2〜6）
- [x] 図の集計表を results/ から作るスクリプト（定義ごとの集計値だけ）
- [x] references.bib（論文 1 の bib から写し、足りない文献を足す）
- [x] 本文の各節（序論・関連研究・データと方法・結果 4 節・考察・限界・結論・抄録・宣言）
- [x] 補足 S1〜S9
- [x] ビルド・語数・n-gram の検査（length-log.md）
- [x] 数の照合（本文の数 ↔ results/）・公開物の規則の検査

## attack-me（Step 7）
- [x] 原稿を commit
- [x] 査読者 3・編集者・意図の監査役・Codex（既知の未決の一覧を添える）
- [x] 一次で裏取り → 直す一覧 → 研究者の採否（判断 3: 全部行う）

## 場面ごとの対応（完了前に照合）
- 論文の査読 → attack-me（paper-reviewer）＋ Codex
- 文献 → 既登録の番号だけ（新しく要れば /literature-review）
- 数 → notes.md と results/ の集計値だけ

## 完了処理
- [ ] decisions.md・引き継ぎ
- [ ] コミット（push・PR は研究者に確かめる）

## 判断 3 の後（次のセッション）
- [x] 追加の条件 5 を書いてコミット（休止の系統・θ の再推定・長さ。量・数え方・読み方・看板を替えないこと）
- [x] 計算（repo の外の作業場・集計値だけ repo へ）・notes.md
- [x] /literature-review（休止の特徴と作文の得点の関連）
- [x] 直す一覧 A〜U を当てて原稿を組み直す・語数と n-gram・数の照合
- [x] attack-me round 2（同じ立場・同じ文献・引き継ぎを渡す・Codex に既知の未決）

## round 2 の後（判断 4・5）
- [x] V（暖機の非対称）を計算で答える（追加の条件 7・90907ea1）
- [x] 追加の条件 8（因果の二段の区間）を計算の前にコミット（029b694e）
- [x] 計算 8・読み方どおり一段を主に戻す・notes.md
- [x] 直す一覧 A〜N を当てる（結果を 3 小節に・長さを見出し・速さは探索・分位の休止は対照・3 値の提案に先例の格子を足す）
- [x] ビルド・語数（6,222）・n-gram（49）・公開物の検査
- [ ] attack-me round 3 を回すかを研究者に確かめる（判定の推移を添える）

## round 5 の後（判断 8）
- [x] 直す一覧 A〜O・Codex C2〜C4・監査役を当てる（698b06ca）
- [x] 追加の条件 9 を計算の前にコミット（b9ce9885）・計算 9・読み方どおり添える・notes.md
- [x] ビルド・語数（7,276）・n-gram（119）・公開物の検査
- [x] メインの照合で attack-me を閉じる（round-5/verdict.md §8）
- [x] 本文を削る（6,878 語・727448cb）
- [x] 条件の英訳の要約・送付状の下書き（0214240a・442da558）・単盲で確定
- [x] 公開物の組み立て（public/assemble.py・参照を伏せた写し・verify.py と対照・README 英日・図）→ GitHub mikotomiura/stall-shape-multiverse（公開）
- [x] Zenodo の下書き 24047695・DOI 10.5281/zenodo.24047695 を予約・zip（md5 2622e3b1…）を上げた・原稿と README に DOI
- [x] Zenodo を publish（2026-11-08・研究者の確認の後）。record の zip を取り直し、手元と SHA-256（37219bd7…）が一致
- [x] 投稿（2026-11-08・JEDM 1486・submission/submission-record.md）
- [x] 公開 repo の README を作り直した（ロゴ・検出器の GIF・定義の格子・動くもの残るもの・英日。38e4a04・GitHub で全画像の表示を確かめた）。Zenodo 0.1.0 は README の変更を含まない
- [x] 公開 repo から投稿先・状態の表記を外した（README のバッジと文・main.tex の冒頭のコメント）。履歴を 1 コミット（8e4890b）に作り直して force push。GitHub は古いコミットを SHA で当面開ける（Support への削除依頼はしない・研究者の判断）。Zenodo 0.1.0 の zip の README には残る（原稿が版の DOI を引くのでそのまま・研究者の判断）
