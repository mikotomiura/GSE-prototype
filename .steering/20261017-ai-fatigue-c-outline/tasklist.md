# タスクリスト

- [x] grill（判断 1）
- [x] outline.md を書く
- [x] 受け入れ条件の確認
- [x] /cross-review（1 巡・判断 2）
- [x] 判断 3（著者・G1〜G10）を骨子に入れる
- [x] プレ査読 3 巡（major → major → minor・判断 8〜10）
- [x] 集計の脚本とダミーの表（判断 10・11）
- [x] /cross-review 1 巡（判断 11）
- [x] コミット・push（PR は研究者が確かめてから）

## 選別の道具（判断 33・2026-10-18）

- [x] 道具の設計を決める（AskUserQuestion 2 回）
- [x] `c_screening.py`・`check_screening.py`・DB のシートの分割
- [x] 守りを外した写しで検査が赤くなるかを確かめる
- [x] 本物の 264 件で入力を作る（判定なし）・34 件の 3 回目で端から端まで
- [x] 登録版との突き合わせ（GSRR-33・36・37・41）と直し・添付 6 に入れる
- [x] /cross-review 1 巡目と対応
- [x] /cross-review 2 巡目と対応
- [x] コミット・push（PR は研究者が確かめてから）

## DB を仕上げる（判断 36・2026-10-18）
- [x] 「全体の DB」の意味を研究者に聞く（264＋34 の 1 冊）
- [x] 全文と判定者 1 用の DB を Drive の AI-fatigue/TRACE へ（ID の照合・本物を 1 つに）
- [x] 作り直しで記入を引き継ぐ（確かめと陽性対照）
- [x] 全体の DB（make_trace_all_db.py）・34 件の訳
- [x] OSF の全文 3 件（R02・R22・R35）
- [x] 1 本の手順（update_trace_db.py）
- [x] 元の DB の最終版（AF002 を含める）を全体の DB に入れ、登録版の時系列・GSRR-32 を足す（判断 37）
- [x] 研究者が Excel で 2 冊を開き、リンク・プルダウン・色を確かめる（2026-10-18・研究者: できていた）
- [ ] コミット・push（PR は研究者が確かめてから）

## 見落としを数える検索（判断 38・2026-10-18）
- [x] 提案を読み、OpenAlex・Europe PMC・ACM DL で数え直す
- [x] 研究者と決める（案 D の形・Q6・期間と種類の制限なし・3 つの情報源・300 件・別の層で符号化・12/31 を保つ）
- [x] `c_search.py`・`acm_export.js`（自己検査と変異・Europe PMC で試しに通す）
- [x] `c_synthesis.py`・`make_dummy.py` に層 coverage と見落としの数の見込み
- [x] 登録版 0.12・骨子 Version 4・草稿・添付 3 の第 16 節・手順・添付の目録
- [x] /cross-review 1 巡目（判断 36〜38 の差分・判断 39 で対応）
- [ ] 研究者: OpenAlex の API キーを `~/.config/openalex/api_key` に置く
- [ ] 検索の本番（3 つの情報源を同じ日に）・抽出・`registration-attachments/coverage/` に書誌と数・登録版の **[at registration]**
- [ ] 確かめの標本 300 件を DB の材料に（訳・`make_screening_candidates.py`・`make_trace_db.py`・`c_screening.py` が CS の記録を読む）
- [ ] コミット・push（PR は研究者が確かめてから）
