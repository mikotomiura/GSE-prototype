# 次セッション開始プロンプト — G1 の被験者分用意（P001–P015）と、Phase1.5 以降の完全自動化

このファイルの「===」以下をコピペして開始する。

**前提**: 2026-08-07 に **配布と通知の自動化を一通り完了**した（`.steering/20260807-g1-distribution-automation/`）。
★ 残っているのは **(A) P001–P015 の課題ページを用意して Drive に置く**ことと、
**(B) Phase1.5 / Phase2 に向けた VPS での完全随時自動化**である。

---

===

## §0 このセッションでやること

★ **A を先に終わらせる**（G1 が始められない状態が続いているため）。B は設計から。

```
【A】P001–P015 の課題ページを用意 → Drive へ配置 → 1 つずつ共有
【B】Phase1.5 / Phase2 の完全随時自動化（VPS）を設計する
```

⚠️ ★ **G1 の被験者は「過去の参加者」が主**である（研究者判断 2026-08-07）。
既存 P-ID で登録されるので `onG1ConsentSubmit` は**採番せず既存 ID を再利用**する
（`g1FindInPhase1Roster_` がメールで引く）。★ だから **P001 から P015 まで全部**要る。

## §1 いまの状態（★ 2026-08-07 実測）

- ブランチ `feature/g1-distribution-automation`（⚠️ **未 push が数コミットある**）
- ★ Drive の配布物は**完成・検証済み**:
  - `GSE_ユーザー検証_G1_アプリダウンロードリンク/`（被験者に渡す親・`1FDkU52n…`）
    - `G1_実施用_macOS.zip` 10,214,008 B / `G1_実施用_Windows.zip` 5,925,275 B
    - ★ 旧フォルダは削除済み。**zip 2 個だけ**が正しい状態
  - `G1/G1_課題ページ_被験者別/`（`1qhl28IDeh-19upuZf_YxPwwdq_d9xVcI`）★ **制限付き（非公開）**
    - ⚠️ **中身は空**。ここに P001–P015 を作るのが【A】
- Apps Script（`GSE_Gate1`）は配備済み: 列移行 / 事前資料メールの自動送信トリガー /
  `refreshG1RunSheet` / `G1_SUBMIT_FOLDER_ID` 設定済み
- ⚠️ ★ **`.gs` の最新版はまだ貼っていない**（受付メール 1 通化・`checkMaterialsProvisioning` が入った版）

## §2 【A】P001–P015 を用意する

### 手順（1 人ぶん）

```bash
cd experiments/20260801-controlled-friction-task
python3 assign.py --subject P001 --json > blocks/P001.json   # ★ --json とリダイレクトが要る
python3 validate_blocks.py
python3 build_task_pages.py --subject P001                   # → pages/P001/block01..10.html
./make-upload-manifest.sh P001                               # ⚠️ make-distribution.sh が先に要る
```

⚠️★ **2026-08-07 に踏んだ罠**: `python3 assign.py --subject P001` だけでは
`blocks/P001.json` は**作られない**（印刷用の表を出すだけ）。`--json > blocks/<ID>.json` が要る。
→ ★ 15 人ぶんを回すなら**ループスクリプトを書くところから**始めるとよい
（`prepare-subjects.sh --range P001 P015` のような形。⚠️ まだ無い）。

### Drive へ置く

★ **課題ページは HTML（テキスト）なので、研究者が Drive 画面へドラッグしてよい。**
⚠️ `.app` のときと違い**実行ビットに依存しない**ので、Drive のフォルダ経路で壊れない。
→ ★ **私（Claude）が MCP で 15 人ぶんを上げるのは非現実的**（1 人あたり base64 で
約 32k トークン × 15）。**人がドラッグ → 私が照合**という分担にする。

```bash
./verify-drive-upload.py dist/P001/_upload/manifest.tsv <search_files の出力.json>
```

⚠️ ★ **rc=1 のあいだは配らない。**

### ⚠️ 共有（★ ここが一番手間）

★ **フォルダを 1 つずつ**「リンクを知っている全員（閲覧者）」にする（15 回）。
⚠️ ★ **親を共有にして継承させてはならない**（`decisions.md` D-7）。
親のリンクを渡してしまった 1 回で**全被験者分が見える** = fail-open になる。

★ 共有し忘れは `g1MaterialsFolderProblem_`（ガード 7）が Drive に問い合わせて止めるので、
**届いても開けないメールは飛ばない**。

### 確認

`GSE_Gate1` で **`checkMaterialsProvisioning()`**（引数なし・読むだけ）。
⚠️ ただしこれは「次に発番される P-ID から 5 人」しか見ない。
★ **過去参加者が主**という運用に合わせて、**P001–P015 を全部見る形に直す**とよい。

## §3 【B】Phase1.5 / Phase2 の完全随時自動化（VPS）

★ **今回 G1 で「完全 on-demand にできなかった理由」が、そのまま設計の出発点**である。

| 段階 | G1 で詰まった理由 | VPS なら |
|---|---|---|
| 割付 (`assign.py`) | ⚠️ GAS は Python を実行できない。★ JS で書き直すと**凍結された科学的手続きの実装が 2 つ**になり、ずれても静かに壊れる | ★ VPS で **`assign.py` をそのまま**動かす（実装を 1 つに保てる） |
| Drive へ配置 | ローカルに Drive 資格情報が無い（`rclone`/`gcloud` 未導入） | サービスアカウントで API 直叩き |
| ★ **フォルダの共有** | ⚠️ **MCP に権限設定 API が無い**ので手作業 | ★ **ここが最大の利得**。Drive API なら `permissions.create` で自動化できる |
| メール送信 | GAS のトリガー（実装済み・動いている） | そのまま使うか、VPS へ寄せるか要検討 |

★ **割付は決定的**であることを実測済み（`SEED` + P-ID の純関数。同じ P-ID なら何度でも同一）。
→ ⚠️ **「先に用意する」と「登録後に用意する」で結果は一致する。** 自動化しても科学的な差は生じない。

### ⚠️ 設計時に持ち込んではいけないもの

1. ★ **割付を「梱包のついでに」走らせない**（`§3-1`）。取り違えると「同じ人に 2 通りの割付」が黙って生まれる
2. ★ **アプリを手元/VPS でビルドしない**。配るのは CI のリリース成果物だけ
3. ⚠️ ★ **`g1-submit.json`（共有シークレット）を public な場所・追跡ファイルに置かない**
4. ⚠️ ★ **NDJSON 生ログ・キーストローク内容を外部 LLM に送らない**（`data-privacy`）
5. ★ 親フォルダを共有にして継承させる設計へ戻さない（D-7 の fail-open）

## §4 ⚠️★ 環境と設計の罠（★ 先に読む）

| 罠 | 中身 |
|---|---|
| ⚠️★★ `git push` / `gh pr merge` は **deny** | ユーザに `! git push` を打ってもらう |
| ⚠️★★ Drive は**パーミッションを保存しない** | 実測: 落としたファイルが一律 `-rw-rw-r--`（元は `-rw-r--r--`）。★ `.app` は実行ビットに依存するので **zip で配る**。⚠️ HTML は影響なし |
| ⚠️★★ macOS の `g1.mode` は **exe から 4 階層上の 1 か所**しか見ない | dmg から起動すると `/Volumes/…` を見る → ★ **G1 モードにならず probe が出る**。しかも**警告が出ない**。2026-08-07 に実機で発生 |
| ⚠️★ macOS の launcher を**復活させない** | `open -a` が名前解決して `/Applications` の通常アプリを起こす。2026-08-05 に廃止済み（`§5.4-5`） |
| ⚠️★ `ditto` の zip は Windows で**日本語名が化ける** | UTF-8 フラグ（bit 11）が立たない。★ `scripts/make-participant-zip.sh` を使う |
| ⚠️ Apps Script の関数セレクタ | **自動操作を受け付けない**。★ 保存が通っていないことがある → リロードして実体で確かめる |
| ⚠️★ `strings \| grep -q` | grep が即終了 → SIGPIPE → `pipefail` が**偽陰性**を作る。★ `grep -c` を使う |
| ⚠️ ロスターは **1 行目がヘッダ** | `g1NextParticipantId_` は `last > 1` のときだけ読む。★ テストで 1 行だけ渡すと採番が P001 に落ちる |
| ⚠️ **Bash の cwd が持ち越される** | 絶対パスで書く |

## §5 ★ 使える道具（今回作ったもの）

| もの | 何 |
|---|---|
| `make-common-app-zip.sh` | ★ 全員共通のアプリ zip（Win/mac）。リリースが変わったときだけ回す |
| `make-distribution.sh` | 被験者 1 人ぶん（課題ページ入り）。⚠️ macOS は `.app` 同梱の zip も作る |
| `make-upload-manifest.sh` | 課題ページの base64 と期待 byte 数 |
| `verify-drive-upload.py` | Drive と手元の byte 照合。★ 1 件でも不一致なら rc=1 |
| `Form_G1/materials_autosend_test.cjs` | GAS のガードを node で実測（74 項目・★ 陽性対照込み） |

## §6 ⚠️★ やらないこと

- ★ `make-distribution.sh` / `make-common-app-zip.sh` を**作り直さない**（fail-closed ガードが実測済み）
- ★ 割付を梱包・アップロードに巻き込まない（`§3-1`）
- ⚠️ ★ `preregistration.md §3.1/§3.2/§3.4/§3.5/§3.6` を変更しない
- ⚠️ ★ `schema_dto.rs` を変えない
- ⚠️ ★ 受付メール・事前資料メールに**題材名・提示順**を書き戻さない
  （`scripts/check_g1_emails.py` が検査する）
- ⚠️ ★ トラッキング表の**判定に関わる列**を機械で埋めない
  （`実施形態` `配置(A/B)` `撤回/除外` `verify-blocks 実施` `validate_blocks 緑` `gse-dataset 送付`）
