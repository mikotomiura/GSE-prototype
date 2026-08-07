# tasklist — G1 配布の自動化

## 1. macOS README の修復（D-4）
- [x] `dist-readme-macos.txt` を分割配布に合わせて書き直す
- [x] `§2.13`/`§2.14-2` の 3 指示が残っていることを grep で確認（欠落 0）
- [x] 再生成して byte 数を確認（3,470 → 4,251 B）
- [x] ★ Drive の旧 README を削除 → 新版を配置（4,251 B・ローカルと byte 一致を実測）

## 2. 課題ページの Drive 配置
- [x] `G1/G1_課題ページ_被験者別/` を作成（`1qhl28IDeh-19upuZf_YxPwwdq_d9xVcI`）
      ★ 親「アプリダウンロードリンク」の**外**に置いた（他被験者の割付が見えるため・§2.12）
- [x] `make-upload-manifest.sh`（base64 + 期待 byte 数 + Win/mac の同一性検査）
- [x] `verify-drive-upload.py`（照合・1 件でも不一致なら rc=1）
- [x] PILOT-win で実走（4 枚の manifest 生成 ✅）
- [x] ⚠️ 壊れた入力で rc=1 を実測（合成 5 パターン: ok=0 / -44B=1 / 欠落=1 / 変換=1 / 余分=1）
- [x] ★ 実 Drive で実測: 部分アップロード → rc=1 / 完全一致 → rc=0
- [x] ★ base64 経路のバイト忠実性: `fileSize` 9519 = ローカルと一致、`text/html` のまま
- [x] ⚠️ ★ 方針変更 (D-7): 親は**制限付き（非公開）**にした。owner のみであることを実測
- [ ] ★ 人: 被験者フォルダを作るたびに、そのフォルダだけ「リンクを知っている全員（閲覧者）」にする
- [x] ★ 疎通試験の残骸 `PILOT-win/` を削除（親フォルダが空であることを実測）

## 3. Apps Script（D-3）
- [x] `RUN_HEADER` に「配布フォルダURL」を追加（方針転換の理由をコメントに明記）
- [x] `migrateRunSheetAddUrlColumn()`（列を**挿す**・冪等・見知らぬ形なら止める）
- [x] `g1AutoSendPendingMaterials()` + ガード 4 本
- [x] `previewPendingTaskMaterials()`（送らない）
- [x] `installMaterialsAutoSendTrigger()` / `removeMaterialsAutoSendTriggers()`
- [x] ★ cross-review の指摘でガード 5（URL 重複）・6（LockService）を追加（D-6）
- [x] ★ 送信後に送信日を読み直す後始末を追加（「送れたのに記録が無い → 再送」を潰す・D-6）
- [x] node 単体テスト `materials_autosend_test.cjs` — 36 項目緑（★ 陽性対照込み）
- [x] `python3 scripts/check_g1_emails.py` 緑（列参照・開示範囲とも一致）
- [x] 既存テスト非回帰: `guard_test.cjs` 4/4 ・ `submit_guard_test.cjs` 33/33
- [x] ★ `GSE_Gate1` に最新 `.gs` を貼り直し、DriveApp スコープを再承認、
      `migrateRunSheetAddUrlColumn()` / `previewPendingTaskMaterials()` /
      `installMaterialsAutoSendTrigger()` を実行（2026-08-07・ユーザー報告）
      ★ 列が入っていることは管理シートを読んで独立に確認済み

## 4. 記録と引き継ぎ
- [x] `Form_G1/README.md` に運用手順を追記
- [x] `.idea/短縮版リンク集.md` に新フォルダを記録（⚠️ gitignore 済み）
- [x] `/cross-review`（Claude + Codex 並列・指摘 4 件すべて採用 → D-6）
- [x] `make-upload-manifest.sh` の nullglob（D-6 #4）
- [x] ★ D-7: 親を非公開に戻し、ガード 7（フォルダ実体の検査）を追加（commit ed383e8）
- [ ] ⚠️ `git push` は deny。ユーザーに `! git push` を打ってもらう

## ★ 本タスク外だが「実施前に必須」だったもの（2026-08-07 に解消）

- [x] ⚠️★★ **G1-C の余分な同意項目 1 件を削除**（引き継ぎ `§5-1`）
  - 実測 (before): `⚠️ コードに無い設問が実フォームに 1 件ある（★ 自動では消さない）:`
    `★ ブロックごとに、暗号化された記録がインターネット経由で自動送信されることの説明を受けました。`
  - 実測 (after): `✅ G1-C はコードと一致している（同意項目 8 件・既存回答 3 件）`
  - ★ **一度「自動送信は v0.1.23 で実装されたのだから、この文言のほうが正しいのでは」と疑ったが、
    コードを読んで外れだと分かった。** 根拠:
    - `reconcile.rs:367-373` — 「⚠️★ **被験者が「送信する」を押した分だけ**送る (D-14: 同意の担保)」
    - `submission.rs` `approved_unsent_age_files` — `.filter(|p| approval_marker_path(p).exists())`
      = ★ **確認の印が無いものは送らない**
  - → v0.1.23 の「自動送信」が自動化したのは **いつ送るか**（収束器による再送・取りこぼし回収）
    であって、**送ってよいか**ではない。コード側の文言
    「送信の確認画面が出て、『送信する』を押したときだけ…送られる」が現在の実装と一致する。
  - ⚠️ 削除前の G1-C は、被験者に**矛盾する 2 つの説明**を同時に提示して両方に同意を求めていた。

## ⚠️ 見つけたが直していないこと（別タスク）
- `GSE_G1_Form_Builder.gs` の「`scripts/check_g1_topic_titles.py` が検査する」というコメントは
  **そのファイルが存在しない**（実在するのは `check_g1_emails.py`。検査内容は同等）
- 同一端末を 2 人が使うと `~/.gse/g1_participant_id` が前の人の値のまま残る（`lib.rs:1113`）
- `g1-submit.json`（共有シークレット）が `anyone: reader` のフォルダにある（D-2 で現状維持と決定）

## 5. 実運用で見つかった穴（D-8・2026-08-07 ユーザーが G1-C を実走して発見）
- [x] 受付メールに **アプリのダウンロードリンク** を追加（★ 入れない理由が無かった）
- [x] 事前資料メールの「閲覧のみ」を撤回し、ダウンロード → アプリのフォルダへ、に書き換え
- [x] `refreshG1RunSheet()` — 導出 5 列を自動集計（★ 判定に関わる列は触らない）
- [x] `installRunSheetRefreshTrigger()` / `removeRunSheetRefreshTriggers()`
- [x] 単体テスト 17 項目追加（計 53 項目緑・★ 陰性対照/上書き禁止/ヘッダ不一致を含む）
- [x] 列の要否を preregistration と突き合わせ（★ `実施形態` は `§2.14-3` により消せない）
- [ ] ★ 人: `.gs` を貼り直す → `installRunSheetRefreshTrigger()` を 1 回
- [ ] ★ 人: スクリプト プロパティ `G1_SUBMIT_FOLDER_ID` に受け口の `FOLDER_ID` と同じ値を入れる
      （⚠️ 無いと「完了ブロック数」「実施日」だけ埋まらない）

## 6. ★ 次セッションへ送るもの（引き継ぎ: `.steering/_handoff/next-session-prompt-g1-provisioning-and-vps.md`）
- [x] ★【A-1】被験者ぶんの一括生成 — `prepare-subjects.sh` を作った（2026-08-07）
      ★ `--range P006 P020` で 15 人ぶんの割付・課題ページ・照合表・ドラッグ用の置き場まで 1 コマンド
      ⚠️★ **既存の `blocks/<ID>.json` を上書きしない**（実施後に書き足された `produced_chars` /
      `file` / 操作チェックが消えるため）。整合の判定は `validate_blocks.py` に任せる
      ★ 負の対照を実測: ID 形式 / 逆範囲 / 範囲過大 / 重複 ID / `--json` 忘れ の 5 つで rc=1
      ★ 上書き禁止の実効性も実測: `produced_chars=1234` を書いた JSON が再走後も残る
      ★ 古い枚数が残らないことも実測（`block99.html` を置いて消えることを確認）
      ⚠️★ 踏んだ罠: **bash は全角文字を変数名の一部として読む**。`$DRIVE（` が
      `DRIVE（` という別の変数になり `set -u` で落ちた → `${DRIVE}` と括る
- [x] ★【A-1b】`make-upload-manifest.sh --from-pages` を足した
      ★ アプリが共通 zip になったので、被験者ごとに要るのは課題ページだけ。
      dmg のマウント・codesign・`gh release download` を 15 回回す理由が無い
      ⚠️ 既存の梱包が残っていれば突き合わせる（4 パターンで rc=1 を実測: 一致 / 1 バイト差 /
      向こうが少ない / 向こうに余分）
- [x] ★【A-2】P006–P020 を生成（★ 範囲は研究者判断で変更・下記）
      ⚠️★ **ロスターの実体を読んで引き継ぎの前提を訂正した**: 現行の管理シート
      (`1ND5HSXZ…`) の「参加者ロスター」は **P006–P014**（P006–P009 は撤回/除外・
      P010–P014 が実参加者）で、**次の発番は P015**。★ **P001–P005 は現行ロスターに無い**
      （旧シート `12T8WU4D…` だけにあるテスト ID）。共有は 1 フォルダずつの手作業なので、
      使われない 5 枠を新規枠に振り替えるほうが同じ手間で価値が高い
      → ★ 研究者判断で **P006–P020**（現行ロスター全員 ＋ 新規 6 枠）
      ★ 実測: 15 フォルダ・150 枚・課題ページ以外 0 件・**名前+byte 数が 15 人ぶんすべて相異なる**
      （⚠️ SHA を混ぜて「相異なる」と言わない。Drive の一覧は `fileSize` しか返さないので、
      SHA まで含めると**実際の検出力より強い保証を名乗る**ことになる）
- [x] ★ 人: 15 フォルダを Drive の `G1_課題ページ_被験者別/` へ配置（2026-08-07）
- [x] ★ 人: **フォルダを 1 つずつ**「リンクを知っている全員（閲覧者）」にした（15 回）
- [x] ★ 私: **byte 照合 15 人ぶん全件緑**（`verify-drive-upload.py` rc=0 × 15・150 枚・
      各 10 件 90,894 or 90,980 B）。⚠️ 取り違え 0 / 欠落 0 / 余分 0 / Google 形式への変換 0
      （全件 `mimeType: text/html` かつ `fileSize` あり）
- [x] ★ 私: 共有設定を実測 — **15 フォルダすべて `{"role":"reader","type":"anyone"}`**、
      ⚠️★ 親は **owner のみ**（D-7 の非公開が保たれている）
- [x] ⚠️★ **フォルダ名のでこぼこを解消**（実運用の名前は `G1課題文_P006` 形式だった）
      ★ GAS は `parent.getFoldersByName(pid)` の**完全一致**で引くので、このままだと
      受付メールが**黙って 2 便運用に落ちる**（壊れないので気づきにくい）
      → 研究者判断で **GAS 側を実運用の名前に合わせた**（15 回の手作業リネームを避ける）
      ★ `g1MaterialsFolderNames_()` を単一の真実源にし、探す側 (`g1MaterialsUrlForPid_`) と
        検査する側 (ガード 7) の**両方**がそこを読む形にした
        （⚠️ 片方だけ直すと「探せたのにガードで弾かれる」という分かりにくい失敗になる）
      ⚠️★ **前方一致にしていない**。完全一致を 2 通り認めるだけ
        （実測: 「P01」で P010 を掴まない / 「G1課題文_P015_旧」を掴まない）
      ⚠️ 2 通り認めた副作用（両方の名前が同時にある）は「2 つ以上」で**送らない**（実測）
      ★ `prepare-subjects.sh` も `DRIVE_PREFIX` で同じ名前を出すので、次回以降は
        ドラッグするだけで一致する（★ 名前の検査もフォルダ数の検査も足した）
      ★ テスト 14 項目追加（計 **112 項目緑**）
- [x] ★【B】Phase1.5 / Phase2 の完全随時自動化を設計した
      → `.steering/20260807-vps-provisioning-automation/`
      ⚠️★ **引き継ぎの前提を 2 つ組み替えた**:
      (1) 3 つの詰まりのうち **VPS が効くのは 1 つも無い**。VPS が足すのは「常時起動」だけで、
          手作業 15 回を消すのは **Drive API の資格情報**である → Stage 1（ローカル）を先に出す
      (2) **サービスアカウントは個人 Gmail で成立しない**（所有者になるが容量を持たず、
          共有ドライブ / ドメイン委任は Workspace 機能）→ OAuth ユーザー資格情報 + `drive.file`
      ★ 起動方式は push でなく **収束器**。帰結として **GAS を 1 行も変えずに済む**
- [x] ⚠️ `checkMaterialsProvisioning()` を**ロスター全体**を見る形に直した
      ★ 「次に発番される P-ID から 5 人」は**新規しか来ない前提**であり、過去参加者が主という
      運用と食い違う。⚠️ その前提のままだと **再参加者のフォルダが 1 つも無くても緑寄りに見えた**
      → `g1RosterParticipantIds_()` を足し、**既存**（ロスター実在）と**新規**（先読み既定 3）を
      分けて数える。`checkMaterialsProvisioning(0)` で新規ぶんを見ない
      ★ node テスト 19 項目追加（計 **93 項目緑**・⚠️ 陽性対照 / 陰性対照 / 空ロスター / 共有し忘れ 1 人）
      ★ 非回帰: `guard_test.cjs` 4/4 ・`submit_guard_test.cjs` 33/33 ・`check_g1_emails.py` 緑
- [ ] ⚠️ `.gs` の最新版（受付メール 1 通化・`checkMaterialsProvisioning` 改）を `GSE_Gate1` へ貼る
- [ ] ⚠️ `git push`（deny なのでユーザーが打つ）
