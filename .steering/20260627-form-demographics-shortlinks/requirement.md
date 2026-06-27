# 要件: F2 属性設問の追加 ＋ 短縮URLのフォーム反映

pilot-smoke-verify 検証中にユーザーから派生指示で発生したフォーム修正タスク。
対象: `Form_Phase1/GSE_Phase1_Form_Builder.gs`（Google Apps Script）。

## 背景・指摘
1. **人口統計属性の欠落**: F1 Q3「年齢」は「18歳以上/18歳未満」の2択（成人かの適格分岐用）で、
   研究データとしての年代は記録されない。F2-A「属性」セクションも作業種類・AI利用習慣のみで
   年代・職業が無い。→ サンプル特性（被験者の年代・職業）を記述できない。
2. **短縮URLの未反映**: `.idea/短縮版リンク集.md` に各フォーム/Dropbox の x.gd 短縮URLを作成済だが
   .gs に反映されていない。

## ゴール / 受け入れ条件
- [ ] F2-A に **年代**（18〜19歳/20代/30代/40代/50代/60代以上）と **職業** の単一選択・必須設問を追加。
      （ユーザー決定: 取得は年代＋職業のみ／配置は F2-A 事前アンケート）
- [ ] メール本文(f1EmailBody_)の F2/F4/F5 回答URLが **短縮URL優先**（空なら従来の動的取得にフォールバック）。
- [ ] `DROPBOX_FILE_REQUEST_URL` が短縮版 `x.gd/PHtwA`（リダイレクト先は現行 request/5oak... と同一）。
- [ ] 短縮URLは全て `/viewform`（回答用）であることを検証済み（編集URL混入なし）。
- [ ] F2-B(GSE-10)/F2-C(TSE) の pre/post byte 一致（matched 制約）に影響しない＝F2-A への追加のみ。
- [ ] f1Answers_ のキーワード照合（"年齢"/"OS"/"メールアドレス"等）と衝突しない（F2 側の追加・F1 不変）。

## 確定事実（WebFetch で裏取り 2026-06-27）
- x.gd/k8nAi(F1) → forms/d/e/1FAIpQLSeQkV.../viewform
- x.gd/fpstM(F2) → .../1FAIpQLScE16.../viewform
- x.gd/kK8i7(F4) → .../1FAIpQLSeUak.../viewform
- x.gd/b4hRB(F5) → .../1FAIpQLSemu5.../viewform
- x.gd/PHtwA(Dropbox) → www.dropbox.com/request/5oak4xpqjt19zx8zvh03（現行定数と完全一致）

## 制約
- `FORM_ID`/`F5_FORM_ID` は openById 用内部IDなので短縮URLに**置換しない**。
- 検証フェーズ派生のため最小差分。HMM/Rust 側・schema は不変。
