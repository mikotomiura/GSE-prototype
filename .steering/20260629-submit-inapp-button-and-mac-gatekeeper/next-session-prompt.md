# 次セッション開始プロンプト（提出のアプリ内ボタン化 ＋ mac Gatekeeper 対策）

このタスクは **新しいセッションで実行**する。下の「===」以下をそのままコピペして開始する。

---

GSE の macOS 被験者がセッション後の提出でつまずく Gatekeeper(quarantine) 問題を、**提出をアプリ内ボタン化**して
根絶し、同時に **暫定対策（mac ランチャの xattr 修正コミット＋参加者ガイド追記）** を入れる。これは Phase1
ユーザー検証のブロッカー解消の一部。**実装系タスクなので必ず `/start-task` を先に実行**し、`.steering/` に記録する。

## まず読むこと（順守）
1. `.steering/20260629-submit-inapp-button-and-mac-gatekeeper/requirement.md`（背景・ゴール・**A/B 設計分岐**・受け入れ条件）。
2. 関連 Skill を Read してから着手: `data-privacy`（匿名化/暗号/PII・**必須**）/ `architecture-rules`（Tauri コマンド追加）/
   `rust-standards` / `typescript-standards` / `git-workflow`。
3. メモリ: 提出/配布まわり（`build-ci-and-pilot-distribution` / `participant-launcher-encoding`）。

## 背景（Phase1 ブロッカーの文脈）
2026-06-29 の Phase1 実行可否レビューで、外部被験者の前に閉じるべき4ブロッカーを特定:
1. **P007 を M0 ビルドで confirmatory 再走していない**（GATE2/3 のベースライン未取得）— 別タスク。
2. **task_kind が論述にロックされていない**（非論述選択で C-index 交絡）— 別タスク（`App.tsx` の TASK_KINDS 制限）。
3. **本タスク = macOS 提出の Gatekeeper ブロック**（被験者が提出不能）。
4. **論述お題テンプレ＋研究者進行ガイド未作成** — 運用（研究者）。
ゲート凍結・測定配線・Windows 配布・盲検・overlay 修正は ready。Windows 提出は既に通る（本件は mac 固有）。

## Gatekeeper/quarantine の要点（原因）
- GSE mac バイナリは **ad-hoc 署名・未 notarize**（tauri.conf に signingIdentity なし／CI `APPLE_SIGNING_IDENTITY:"-"`）。
- ダウンロードで付く `com.apple.quarantine` を Gatekeeper が弾く。macOS15(Sequoia) は「マルウェアが含まれていないことを
  Apple が確認できない」表示で、**右クリック→開く の回避は廃止**（システム設定→プライバシーとセキュリティ→「このまま開く」のみ）。
- **2層**: ①`.command` 自身が quarantine（被験者がここで停止）②`gse-submit` も quarantine→SIGKILL。
  未コミットの `xattr -dr ...`（`提出する_mac.command`）は②のみ対策で①に無力。

## やること

### タスクA（恒久・主目的）: 提出をアプリ内ボタン化
被験者は **既に承認済みの GSE アプリ**から「提出する」を押すだけにする。別スクリプト/別バイナリの Gatekeeper を発生させない。

- **設計分岐 A/B を design.md で評価**（必要なら `/reimagine`）。第一候補は **案A=sidecar**:
  - `age` は `package` feature 隔離で **app 本体に非搭載**（Cargo.toml `package=["dep:age"]`）。これを壊さない案が望ましい。
  - **案A（推奨）sidecar(externalBin)**: CI が別ビルドする `gse-submit` を `.app` に同梱し `tauri-plugin-shell` の
    `Command::sidecar` で起動。**バンドル内バイナリは app 署名に内包＝単独 quarantine が付かない**＝Gatekeeper 根絶。
    参加者 ID は env `GSE_PARTICIPANT_ID`（submit.rs 対応済）で渡し、stdout/exit を UI に反映。
    要: `tauri.conf.json bundle.externalBin` 追加 ＋ CI で `gse-submit` を target-triple 接尾辞付きで配置 ＋
    capability に shell:sidecar 権限。
  - **案B in-process**: app に `package`(age) を載せ `packaging::package_session()` を新 Tauri コマンド直呼び。
    UX 最良だが age 隔離撤回・バイナリ増・ビルド OOM 懸念。採るなら理由を decisions.md に明記。
- **フロント**: `src/components/Dashboard.tsx`（または App.tsx）にセッション終了後の「提出する」ボタン＋
  進捗/結果/失敗表示（**fail-loud**: 既存の record 失敗インラインエラーと同じ思想で、静かに失わない・リトライ可能）。
- **提出ロジックは単一情報源を維持**: `src-tauri/src/packaging.rs`（`package_session`/`find_latest_session_ndjson`/
  `default_session_dir`/`read_persisted_participant_id` 等）。CLI `gse-submit` と重複実装しない。

### タスクB（暫定・即効）: ランチャ xattr 修正コミット ＋ 参加者ガイド許可手順
- 作業ツリー未コミットの `scripts/submit/提出する_mac.command` の `xattr -dr com.apple.quarantine "$(dirname "$0")"`
  （②対策）を**対象ファイルのみ明示 pathspec でコミット**（無関係な未ステージ変更を巻き込まない）。
- `docs/participant-setup-guide.md` に **mac 初回許可手順**を追記:
  - 方法A(GUI): システム設定→プライバシーとセキュリティ→下部「…ブロックされました」→「このまま開く」→再実行。
  - 方法B(Terminal・確実): `xattr -dr com.apple.quarantine <GSEフォルダ>`（フォルダを Terminal にドラッグ）で①②一括解除。
- アプリ内提出が入れば被験者はこの手順を踏まずに済むが、移行期/フォールバックとして併記する。

## 死守する非回帰・制約
- **data-privacy**: 匿名化（VK→KeyCategory・時刻相対化）・age 暗号・`P###_<stem>.age`・**実名/本文/タイトル混入なし**。
  キーストローク内容・NDJSON 生ログを外部送信しない。
- 既存 `gse-submit` CLI（研究者・Windows 経路）と **Windows 提出フローは非回帰**。
- `age` の feature 隔離方針を勝手に撤回しない（案B を採る場合のみ理由付きで）。
- 盲検: 提出ボタンは被験者ビルドで出てよい（debug 機能ではない）。介入/ゲートのロジックは触らない。

## 検証
- `cargo build`（aarch64-apple-darwin / x86_64-pc-windows-msvc 両 cfg）＋ `cargo test --workspace`。
- sidecar 採用時: `gse-submit` の単独 CLI ビルド（`--features package`）が壊れていないこと。
- **mac 実機 smoke**: ダウンロード→アプリ承認→アプリ内「提出する」→`.age` 生成・**追加の Gatekeeper ダイアログ無し**。
- 生成 `.age` を `gse-unpack` で復号し、匿名化済み NDJSON が従来と同等（byte 等価でなくても意味同値）であること。
- `/finish-task`（code-reviewer + security-checker + `/cross-review` 必須）。security は data-privacy 観点を重点。

## 仕上げ
- 完了後 `v0.1.21` を**同 ver 再リリース**（旧 Release+タグ削除→現 main に再タグ→push で CI ビルド。repo は現在 PUBLIC で Actions 可）。
- メモリ更新: 提出/配布まわり（`build-ci-and-pilot-distribution`）に mac 提出のアプリ内化を追記。

## 引き継ぎ注意
- 作業ツリーに無関係な未ステージ変更が多数。commit は対象ファイルを明示 pathspec で限定する（`-A` 禁止）。
- ローカル main が origin より古い場合は `git stash -u && git pull --ff-only && git stash pop` で整える。
