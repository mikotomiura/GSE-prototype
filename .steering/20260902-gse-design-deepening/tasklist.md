# タスクリスト — GSE 設計の深掘り

## B. 文献の真偽確認 — ★ 完了

- [x] §9.1 状態推定・外在化（Kuvar / Dias da Silva & Postma / Alqahtani）
- [x] §9.2 表現メディア（Liu / An(EmoWear) / Consolvo / Murnane / Zheng / Majeed）
- [x] §9.3 JITAI・離席 prompt（Hardeman / Fiedler / Chueh / Zhuang / Mainsbridge / Leppe-Zamora / Albulescu）
- [x] §9.4 自律性・反応性・通知（Busch / Bonvanie / Karyda / Graben / Upshaw / König）
- [x] 横断: §14 の ML 主張 4 件（abstention / calibration / 競合リスク / MRT）
- [x] 結果を `survey-verification.md` に記録（★ **重大な誤り 5 件・中程度 14 件**）

## Stage 4 サーヴェイ — ★ 完了（★ 研究者指示「具体的なサーヴェイ後に議論する」）

- [x] 系統 1: 深層系列モデル vs 単純ベースライン
- [x] 系統 2: 長期プロファイル層（N-of-1 / DSEM / エルゴード性 / state–trait / ラベリング）
- [x] 系統 3: 打鍵 ML の到達点（★ 追補のみ到着 → 統合版を再送依頼して受領）
- [x] 結果を `stage4-survey.md` に記録

## C. Mh-D / ML 段階の再定義 — ★ 完了

- [x] 既存 ADR・glossary との衝突監査（`conflict-audit.md`・★ **改善案 7 件のうち 6 件が既決**）
- [x] 判断 1: 層番号 `L1〜L4` を採らない
- [x] 判断 2: 「認知体力」を新設しない
- [x] 判断 3: 長期プロファイル層を**置かない**（★ サーヴェイ後に確定）
- [x] 判断 4: Stage 表は維持し、「降ろした理由」に一次証拠を足す
- [x] 判断 5: `.idea` の ML の形を採り、6 点を修正する
- [x] 判断 6: `md2pptx.py` を `python-pptx` へ

## 成果物 — ★ 大半完了

- [x] `docs/references.md` へ 43 件 append（`[P219]`–`[P238]` / `[V89]`–`[V111]`）
      ★ **書く前に DOI 9 件を検算し、タイトルの誤り 2 件を発見・訂正**
      ★ 既存 `[V84]` の書誌を補完（★ 番号は変えていない）
- [x] **ADR-019**（ML の段の再定義と昇格ゲートの置き換え）起票
- [x] **ADR-020**（長期プロファイル層を置かない）起票
- [x] `docs/adr/README.md` / `docs/glossary.md` / `docs/architecture/gse-v2-overview.md` を更新
- [x] 未踏提出資料 3 本を更新（技術設計書 §4.4 書き直し ＋ §4.5 新設 / 設計スライド / 参考文献 `[72]`–`[81]`）
- [x] `scripts/check_doc_lexicon.py` = **違反なし**
- [x] 引用番号の整合を機械確認（**未定義の引用なし・未引用の新規なし**）
- [x] ★ **詳細資料は 1 バイトも触っていない**（10 ページ規約を悪化させていない）
- [x] ★ **`.docx` / `.pptx` の生成を再現可能にした**（ZIP の日時固定・2 回生成して SHA-256 一致を実測）
- [ ] `/cross-review`（★ 実行中・`-- docs scripts ':!*.docx' ':!*.pptx'` でパス限定）

## 未着手 — ★ 次セッションへ

- [ ] **A. §7 の未決事項 8 件**（★ 表現チャネルと身体回帰の接続）
      ★ 既存 ADR との衝突は `conflict-audit.md` F7–F10 に洗い出し済み:
      - 双方向通信は **ADR-017 D3 と正面衝突**（★ 却下済みだが恒久否決ではない。
        `data-privacy` の位置情報節が埋まれば再検討可）
      - `intervention_active` は **ADR-017 D2 で既に 4 値契約に入っている**（★ 分けるなら新規 ADR）
      - Physical Anchor の「起動」は **ADR-018 D1/D2 により語として使えない**
      - §4.3 の閲覧モデルは **ADR-017 D6 の 2 層（層 A ≤4 秒 / 層 B 数十秒）を知らずに書かれている**
- [ ] ⚠️★★★ **`.pptx` を Google Slides で実地確認**（★ 機械検査は緑だが、**前回も緑だった**）
- [ ] ⚠️ **`.docx` を Google Docs で実地確認**（★ 症状は出ていないが、パート構成は `.pptx` と同じ形をしている）
- [ ] **ADR-019 D6 の実装**（★ 語・文境界のリズム特徴を `features.rs` へ）— ★ **別タスク・別ブランチ**
- [ ] 出版版 **UMUAI 33(3):617-641** の本文入手
      （★ 「タイミングのみの特徴群は κ=0.018–0.050」が **2 系統で食い違っており未確定**）
- [ ] ⚠️ `[V103]` の N/T 数値は **二次引用**（★ 本文未到達）—— 提出資料で使うなら原本を入手する
- [ ] ★ Stage 4 の逆側の探索を 1 ラウンド
      （★ **self-supervised pre-training による小標本 HAR が未探索**）
