# タスクリスト

## 準備
- [x] 引き継ぎ（12）・前のタスクの判断 1〜4・判断 35・37・原稿の Materials を読む
- [x] 研究者に名前・置き方・内部文書・記録の扱い・文書の許諾・/reimagine を聞く（判断 1）
- [x] 論文の 3 ディレクトリのスクリプトが読み込む他のファイルを grep で洗い出す
- [x] 内部文書 5 本と notes.md を読み、出せない記述が無いか確かめる

## 実装
- [x] `assemble.sh`（写す一覧）
- [x] `tools/check_release.py`（漏れの検査）と陽性対照
- [x] `tools/verify.sh`（manifest・cargo test・provenance・漏れ）
- [x] README（英・日）・LICENSE-docs・CITATION.cff
- [x] `tools/readme_media.py` と図（自分で見る）

## テスト
- [x] 写した先で `tools/verify.sh` が緑
- [x] 陽性対照で赤（偽の id・manifest の 1 バイト違い）

## レビュー
- [x] security-checker と cross-reviewer（Claude の code-reviewer の観点と Codex）を並列
- [x] /cross-review（Codex あり）
- [x] 指摘への対応（decisions.md）

## 公開（研究者の確認の後）
- [ ] GitHub の repo の作成・push
- [ ] Zenodo の公開・DOI
- [ ] 要旨の置き字と Materials を DOI に（別の commit）

## 完了処理
- [ ] Skill の対応表（design.md）との照合
- [x] design.md の最終化・decisions.md
- [ ] git commit（[skip ci]・push は研究者）
- [ ] 引き継ぎ（attack-me round 3 の要否）
