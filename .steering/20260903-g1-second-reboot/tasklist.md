# tasklist — G1 第 18 版 ＋ 本日実施(P017/P018)の前提条件

## §1 G1 の 2 回目のリブート（主題）— ✅ 完了・コミット済み `1fcca96`

- [x] 欠陥の影響範囲を実測（資材 2 本 / 216 中 20 ブロック / 各被験者ちょうど 1）
- [x] ⚠️ 被験者が見た画面を旧スクリプトで**再現**（引き継ぎメモの「復元できない」を訂正）
- [x] 研究者決定: 2 回目のリブート・n=3 据え置き・確証は P017/P018
- [x] 凍結節の byte-identical 主張を機械検算（★ §3.5/§3.6 は append-only だった）
- [x] `check_frozen_sections.py` 新規（selftest 6 ケース・変異 5 件で赤を確認）
- [x] `run.sh [1]` に配線（★ 変異注入で run.sh が [RED] になることを実測）
- [x] `preregistration.md` 第 18 版
- [x] `config.json` の `revision`=18 / `sample_roster`（confirmatory=[P017,P018]）
- [x] `analyze.py` PREREG_REVISION 18（★ 版ゲートが実際に赤くなる陽性対照を確認）
- [x] ⚠️ `analyze.py` **実走** → 「確証標本が 2 名で n=3 に達していない」で正しく停止
- [x] `data.md` 更新（⚠️ セッション日時は書かない）
- [x] `record-sheet-confirmatory.md` 新規 ＋ `protocol.md §2.2` に「文字数」欄

## §2 ⚠️★★★ 本日実施の前提条件（★ 研究者の操作が要るもの）

- [x] 課題ページを修正後スクリプトで**再生成**（20 名分 200 枚・`**` 0 枚 / `<strong>` 200 枚）
- [ ] ⚠️★★★ **Drive の `G1課題文_P017` / `G1課題文_P018` を差し替える**（★ 人がドラッグ）
- [ ] ⚠️ 差し替え後に `verify-drive-upload.py` で照合 → **緑になるまでリンクを配らない**
- [x] schema parity（前提条件 4）→ ★ 修正して `rc=0`。gse-dataset 側にローカルコミット済み
- [ ] ⚠️ **gse-dataset を push**（★ 私は未実施・研究者判断）
- [ ] ⚠️ 同意文書・デブリーフの**連絡先を記入**（`consent.md:133,134` / `debrief.md:98,99`）
- [x] `record-sheet-confirmatory.md` を印刷できる状態にした
- [ ] ⚠️ 印刷用同意書 docx が旧版（機器トラブル時のみ使用・未検算）

## §3 O1 の残り HIGH（★ §1/§2 と独立・本セッションでは未着手）

- [ ] PR #148 のマージ（現在 OPEN / UNSTABLE）
- [ ] `O1_MGMT_SHEET_ID` の実装ゼロ
- [ ] G1 にロスター形の検査が無い
- [ ] conflict 行が無制限に積み上がる（小）
- [ ] ロスターの同一メール 2 行を黙って先頭採用（小）
- [ ] T-27 プロジェクト跨ぎの二重採番（`/reimagine` 規模）

## §4 既存の別問題（★ 本改訂とは無関係・記録のみ）

- [ ] ⚠️ `validate_blocks.py --dataset` が 17 件で赤
      （P010 10 件＝G1 ブロックが dataset に無い / P011・P012・P013＝Phase1 セッションを
      G1 と誤認する偽陽性 / PILOT-win 4 件＝dataset にディレクトリが無い）
      ★ **P007/P014/P016 は 1 件も出ない**
- [ ] ⚠️ Drive のページが**どの生成物とも 12 バイト違う**（`decisions.md` D-6・差し替え後に決着）
- [ ] ⚠️ 所要時間が 3 通り（protocol 62 分 / consent・guide 70 分 / guide「1 時間ほど」）

## レビュー

- [ ] `code-reviewer` + `security-checker` を並列
- [ ] `/cross-review`（Codex）
