# タスクリスト

## 事前検証（★ A の前に前倒し）

- [x] `build_task_pages.py --selftest` が緑
- [x] `dist/_drive` が `build_task_pages.py` より新しい（02:16 > 01:57）／ゲート文言が入っている
- [x] ★ **実マウス押下**でゲートが開く（`isTrusted: true` を実測。§2 の最大の未検証を解消）
- [x] ★ 押す前は課題文・記入欄・footer が `display: none`（`getClientRects().length === 0`）
- [x] ★ 押した瞬間に課題（313px）と記入欄が**同時に**出て `#gate` が消える
- [x] ★ 実キーボードで打鍵 → 文字数が `count_chars` 規則で一致（`"test abc"` 8 文字 → 表示 7）
- [x] ★ 対照つき選択検査（`.notice` 251 文字選択可 / `.task` 0 ＝ `user-select:none` が効いている）
- [x] `spellcheck=false` / `autocorrect=off` / `autocomplete=off` / `autocapitalize=off`（`§2.11-2`）
- [x] 外部リソース 0 件 / `localStorage`・`sessionStorage`・`cookie` すべて 0
- [ ] ⚠️ `file://` そのもの（★ 拡張から原理的に触れない。C で実機確認する）
- [ ] ⚠️ Windows 実機・実 IME・拡張ありプロファイル（C で確認する）
- [ ] ⚠️ 第三者レビュー（`/cross-review`）が前タスクで未実施

## 【A】Drive の差し替え ★ 完了（2026-08-08）

- [x] A-1: Drive 側の古い 15 フォルダを削除（研究者が実施）
- [x] A-2: `dist/_drive` の 15 フォルダをドラッグしてアップロード（研究者が実施・フォルダ ID は全部変わった）
- [x] A-3: 15 フォルダすべて `anyone: reader` を実測確認
- [x] A-4: 15 フォルダ × 10 件 = **150 件すべて byte 照合が緑**（`verify-drive-upload.py`）
- [x] A-5: 親フォルダは owner のみ＝制限付き（D-7）を実測確認
- [x] A-6: 親フォルダ直下がちょうど 15 フォルダ（同名重複なし）
- [x] A-7: `drive-folder-map.md` を新 ID で更新

## 【B】GAS 再配備と G1-S 作り直し ★ 完了（2026-08-08）

- [x] B-1: `GSE_G1_Form_Builder.gs` を貼る（研究者が実施）
- [x] B-2: `buildPostSurveyForm()` を実行（研究者が実施）。★ 公開 URL
      `.../e/1FAIpQLScXWKQQ_lXuoRRnj1A-SEhLEHlTi2Z7cj266BggryKYaDqr6w/viewform` が
      `.idea/短縮版リンク集.md:30` と**一致** ＝ 配布済み URL は変わっていない
- [x] B-3: 15 件緑（研究者の報告 ＋ ★ Drive 側から独立に裏取り。`decisions.md` 判断 3）
- [x] B-4: ★ 実物の G1-S を読んで第 11 版であることを確認
      - 設問文「当日より前に、課題ページの「課題を表示して始める」を押して中をご覧になりましたか。」＝ 一致
      - 選択肢 4 つすべて一致 / 補足設問あり / セクション「1b. 当日より前に開いたかどうか」あり
      - ★ 第 8 版の痕跡（「どのくらい」「事前にお送りした課題文」「下調べ」）は **0 件**

## ★ cross-review（前タスク `b49685d` 対象・積み残しを解消）

- [x] 実施（Claude ＋ Codex 独立レビュー。skip 無し）
- [x] ⚠️ 確定 A: **文書に経路を明記するのみ**（研究者判断 2026-08-08。設問は変えない）
      - `§2.12-1` に「押さなくても View Source で読める」を追記
      - `§2.13-1b` に「ゲートが担保するのはタイマー起点と非消費の 2 つ」を明記
      - `§2.12-4` に「この設問は View Source 経路を捕捉しない」を明記
- [x] ⚠️ 確定 B: 「取りこぼしが構造的にゼロ」を訂正
      - `preregistration.md §9-1` / `protocol.md:68` / `protocol.md:563` / `lib.rs:2449`
      - ★ 第 10 版の改訂履歴（`:210`）は**履歴なので書き換えず**、訂正済みのポインタだけ足した
- [x] 第 12 版として改訂履歴を起こし、★ 向きを両方記録（厳しくする側 / 報告が増える側）
- [ ] ⚠️ 確定 C: `beforeunload` に `started` を足す → ★ **保留**
      理由: 生成 HTML が変わると Drive の 150 ファイルを上げ直すことになり、実害に見合わない。
      ★ 次に生成物を作り直す機会にまとめる

### ★ 文書修正が配布物を壊していないことの確認

- [x] `dist/_drive` の sha256 が**不変**（P006 / P015 / P020 で抽出確認）→ Drive は有効なまま
- [x] `build_task_pages.py --selftest` 緑
- [x] `scripts/check_g1_emails.py` 緑（§2.12 第 11 版を守っている）
- [x] `cargo check --lib` 通過（`lib.rs` はコメントのみの変更）

## 【C】実働検証（P015 を消費）

- [ ] C-1: G1-C 提出 → メール受信（★ 文面が撤回後か目で読む）
- [ ] C-2: zip → 展開 → 起動 → 「G1 モードで動作しています」
- [ ] C-3: ★ `file://` で課題ページを開き、**実マウスで**「課題を表示して始める」を押す
- [ ] C-4: ★ 押す前に課題が読めないことを目で確認
- [ ] C-5: 提出 → `.age` → 受け口 → Drive
- [ ] C-6: `refreshG1RunSheet` が「完了ブロック数」「実施日」を埋める
- [ ] C-7: 後片付け（ロスターで P015 を `撤回/除外` に）
