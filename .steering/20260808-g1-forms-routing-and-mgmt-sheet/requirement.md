# G1-M / G1-S の導線を作る ＋ 管理シートの手入れ

## 背景

2026-08-08 の実測で、★ **受付メール・`README_先に読む.txt`・`blockNN.html` のどれにも
G1-M / G1-S のリンクが 1 つも無い**ことが分かった。

- `protocol.md:711` の「G1-M / G1-S の回答 URL」は**研究者の持ち物リスト**（来所前提）
- `protocol.md:453` は「操作チェックは §3 の用紙へ」＝ **紙が既定**
- ⚠️ 第 13 版の実施形態（在宅・初回起動のみ同席）では**紙が使えない**

→ 在宅の被験者は 10 ブロック完走しても G1-M に 7 回とも答えられず、G1-S にも答えられない。
`§2.6` の操作チェックが**データ 0 件**になる（実証: P009 の行が `G1-M 回答数(/7) = 0`）。

管理シート（`【非公開】GSE_G1 運用管理シート`）も、第 13 版の運用と食い違う列が残っている。

## ゴール

1. 受付メール 1 通で、被験者が **3 つのフォームの関係**（いつ・何回・なぜ）を理解し、
   G1-M / G1-S に**自力でたどり着ける**。
2. 管理シートの列が第 13 版の運用と一致し、レイアウトが Phase1 並みに読める。
3. 上記が**検査で固定**され、文言・列が戻ったら赤くなる。

## スコープ

### 含むもの
- `Form_G1/GSE_G1_Form_Builder.gs` の受付メール本文（2 分岐とも）
- `scripts/check_g1_emails.py` への新しい不変条件
- `RUN_HEADER` / `applyRunValidation_` / 実シートの移行関数 / レイアウト
- GAS の貼り直しと `previewRegisterAckEmail()` での目視

### 含まないもの
- `§2.6` の設問文・タイミング（凍結）
- `blockNN.html` の再生成と Drive への再配布（150 件・別トラック）
- アプリの再ビルド（`§4` の「ローカルのログが無い」問題）

## 受け入れ条件

- [ ] 受付メールの**両分岐**に G1-M / G1-S のリンクと「いつ・何回」の説明がある
- [ ] `python3 scripts/check_g1_emails.py` が緑。⚠️ **新しい検査は壊して赤を見てから採用する**
- [ ] 短縮 URL がある側／無い側の**両方**で、リンクが本文に出る
- [ ] 管理シートの列が第 13 版と一致し、`assertRunHeader_` が実シートと合う
- [ ] `previewRegisterAckEmail()` の実物を目視した

## 関連ドキュメント

- `.steering/_handoff/next-session-prompt-g1-forms-routing-and-mgmt-sheet.md`（このタスクの出典）
- `experiments/20260801-controlled-friction-task/preregistration.md` §2.6 / §2.12 / §2.14
- `experiments/20260801-controlled-friction-task/protocol.md` §3.1b / §4b.1
- `Form_G1/README.md`
