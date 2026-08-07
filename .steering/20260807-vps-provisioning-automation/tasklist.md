# tasklist — 課題ページ配布の随時自動化

⚠️ ★ **このタスクは設計まで**。実装は Phase1.5 の着手時に別タスクで start-task する。

## 1. 設計（このセッション・2026-08-07）
- [x] 引き継ぎ §3 の 3 つの詰まりを 1 つずつ検分し、★ **VPS が効くのは 1 つも無い**ことを示した（D-1）
- [x] ⚠️ 「サービスアカウント」の前提を訂正（個人 Gmail では成立しない）→ OAuth ユーザー資格情報（D-2）
- [x] 起動方式を push でなく **収束器 (reconciler)** に決めた（D-3）
      ★ 帰結: **GAS を 1 行も変えずに済む**（`g1MaterialsUrlForPid_` が名前で引く設計がそのまま活きる）
- [x] ⚠️ 「照合が緑になるまで共有しない」を順序として固定（D-4）
- [x] 手作業版を退路として残すことを決めた（D-5）
- [x] ⚠️ G1 本番には差し込まない（D-6）
- [x] ★ 未検証の前提を spike 1〜4 として列挙した（`design.md`）

## 2. 実装前に潰す spike（★ 次のタスクの最初）
- [ ] spike-1: `drive.file` スコープで既存の親フォルダ配下に子フォルダを作れるか
      ⚠️ 外れたら「親もアプリに作らせる」へ切り替える
- [ ] spike-2: `permissions.create(type=anyone, role=reader)` が個人 Gmail で通るか
- [ ] spike-3: リフレッシュトークンの寿命（★ 短命なら失効を**検出して止める**）
- [ ] spike-4: アップロードした HTML が `text/html` のままか（Google 形式に変換されないか）
- [ ] ⚠️ spike は**本番の親フォルダで試さない**（捨てフォルダを作る）

## 3. Stage 1（ローカル + Drive API・★ 手作業 15 回が 0 回になる）
- [ ] `drive_client.py`（folder 作成 / file 作成 / list / permissions.create）
- [ ] `provision.py`（★ 割付〜共有まで。⚠️ 照合が赤なら共有しない）
- [ ] 単体テスト（⚠️ **陽性対照込み**・「照合が赤 → 共有まで進まない」を本丸に）
- [ ] `scripts/provision-credentials.md`（⚠️ 秘密そのものは置かない）
- [ ] 捨てフォルダで 1 人ぶんを実走

## 4. Stage 2（VPS・★ 随時性を足す）
- [ ] VPS の実体と秘密の置き場を決める（⚠️ 追跡ファイルに置かない）
- [ ] `provision-reconcile.py`（ロスターを読んで寄せる）
- [ ] systemd timer（★ cron でなく timer。失敗が journal に残る）
- [ ] ⚠️ Drive API のクォータを実測してから周期を決める
- [ ] `checkMaterialsProvisioning()` で外側から監視できることを確認（★ GAS は変えない）

## ⚠️ 見つけたが直していないこと（別タスク）
- ★ ロスターに **旧管理シート由来の P001–P005 が無い**（現行は P006–P014・次は P015）。
  引き継ぎの「P001–P015」はロスターの実体より広かった。→ 研究者判断で **P006–P020** に変更済み。
- `GSE_G1_Form_Builder.gs` の「`scripts/check_g1_topic_titles.py` が検査する」というコメントは
  **そのファイルが存在しない**（実在するのは `check_g1_emails.py`）
