# /literature-review に「取れなかった本文は Chrome で読む」を足す

## 背景
2026-11-20 の S-CX（枝 docs/handmark-coexistence-survey）で、出版社のサイト（Cell・SAGE・MDPI・ACM）が WebFetch で 403 だった。ブラウザを装った一括取得は自動モードに止められた。研究者が「fetch・subagent などで取れなかったものは Chrome でとろう」と指示し、Chrome の javascript_tool で 4 本の本文を読めた。研究者が /literature-review への追記を決めた（2026-11-20）。

## ゴール
/literature-review の Step 2 に、本文が取れなかったときに Chrome で読む手順を足す。

## 受け入れ条件
- [x] Step 2 の「PDF の読み方」の後に手順（Skill の先読み・対象の選び方・有料と CAPTCHA の扱い・javascript_tool での抜き方・記録の書き方・タブの片づけ）
- [ ] allowed-tools に Chrome の道具を足す（自動モードに止められた。足すなら研究者が手で足す）
- [ ] /cross-review
- [ ] push → PR → CI 緑なら merge（git-workflow ルール 6）

## 運用メモ
- /reimagine 適用: No
- 理由: 手順の文書の追記で、設計判断を伴わない
