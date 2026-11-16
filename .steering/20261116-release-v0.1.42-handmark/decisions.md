# decisions

## 判断 1: 本人の macOS の版だけを今配る（研究者・2026-11-16）

- 決定: v0.1.42 を本人の macOS の配布フォルダにだけ入れる。3 名への配布は Windows の手跡が通ってから。
- 理由: 研究者は最初「Windows の手跡の後に配布」を提案した。ADR-052 D4 は本人の段 1 について
  「Windows 版の手跡を待たない」、D5 は 3 名について「Windows 版の手跡が通るまで始めない」としている。
  後期は 11-24 に始まり、割付の表は作り直せないので、本人の版を待たせると関門 2 を失う。これを示して
  AskUserQuestion で聞き、推奨どおりに決まった。
- 却下案: 本人の版も Windows を待つ（D4 の見直しと段 1 の延長が要る）。

## 判断 2: 手跡の確かめは今回は手で、門への追加は 3 名の版の前に（Claude の既定・研究者に報告）

- 決定: バイナリの手跡の文字列・表の SHA-256・起動後の入口の門のログを手で確かめて記録する。
  門（`check-s1-release-readiness.sh`）への追加は、3 名の版の前に陽性対照つきの別タスクで行う。
- 理由: 本人の 1 回の配布では手の証拠で足り、繰り返し配る 3 名の版で門が効く。期日を圧迫しない。

## 記録: v0.1.42 の配布物の確かめ（2026-11-16）

- PR #419 → マージ d06da9da（package.json・Cargo.toml・tauri.conf.json が 0.1.42、`src-tauri/src` に handmark のファイル 17）。
- タグ v0.1.42 → run 43812713911（build-macos・build-windows・release とも success）。
- dmg `gse-next_0.1.42_aarch64.dmg` SHA-256 `082bda7de5767b58f48d36c4239d56ed3ac71a3789046aece7feed269148a88d`。.app の版 0.1.42。
- 今のフォルダの写しに新しい .app を入れた検査用フォルダで、門（--audience self --os-only macos）は通過 22 / 未達 0。
- 手跡の文字列（判断 2 の手の確かめ）: 対照の v0.1.41 は `handmark_assignment`・`handmark_day`・`handmark_assignment.sha256` がすべて 0、
  v0.1.42 は 1・6・1。フォルダの表の SHA-256 は記録の値 `e19e51c9…20da` と一致。

## 記録: 入れ替え（2026-11-16 16:57〜）

- 研究者がトレイから終了（gse-app.log 07:57:04Z `tray: quit requested`）。プロセスが無いことを確かめてから、
  `gse-next.app` だけを替えた（古い v0.1.41 はスクラッチパッドへ退避）。`handmark_assignment.json`・`s1.mode`・
  `o1.mode`・`o1.autostart` の SHA-256 は入れ替えの前後で同じ。`s1-release-tag.txt` を v0.1.42 に書き換えた。

## 判断 3: 問いへの同意が 11-09 から取り消されていた → 起動時に同意し直す（研究者・2026-11-16）

- 発見: 研究者が「プローブのような停滞の問いが来ない」と尋ねた。gse-app.log の起動の行は 11-07・11-08 が `consent=true`、
  11-14・11-15 が `consent=false`。`2026-11-09T01:25:08Z`（10:25 JST）に `stage 1: consent to the questions revoked`
  が 1 行あり（`revoke_s1_probe_consent` だけが書く行）、`~/.gse/s1_probe_consent` は無い（`~/.gse` の mtime も 11-09 10:25）。
  記録の行の種類の件数: 11-08 の記録は `probe_frame` 1・`probe_assignment` 8・`realtime_label` 7・`activity_label` 7、
  11-15 17:22 以降の 2 本は問いの行が 0（件数だけを見た・中身は開いていない）。
- 決定: v0.1.42 の起動後に登録の画面で問いへの同意をし直す。consent=true と問いの行の再開をログと件数で確かめる。
- 影響: 11-09 10:25〜同意し直すまで、無作為の枠の申告は 0。打鍵の記録は続いている（11-09 12:58〜11-16 02:22 は記録自体が止まっていた・
  stage1-recording-stopped）。前期の申告の数は少なくなる。回 1（手跡の漏れの確かめ）は記録から描き直すので申告を使わないかは回 1 の前に確かめる。
- 取り消しが意図したものでなかった理由（押し間違いか）は分からない。stage1-recording-stopped の調べはこの行を拾っていなかった。
- 却下案: 問いなしで続ける（関門 1 を後期で確かめられない）。

## 記録: 問いの再開（2026-11-16 17:02）

- 17:02:48 の起動は `input_monitoring=true`・Measuring。17:02:53 に `stage 1: consent to the questions acknowledged`、
  新しい記録 `gse_o1_20261116_080253.ndjson` に `probe_frame` 1・`probe_assignment` 1（件数だけ）。

## 判断 4: フォルダをデスクトップへ移した → デスクトップから起動し直す（研究者・2026-11-16）

- 研究者が 17:03 に配布フォルダを `~/Desktop/S1_実施用_macOS/` へ移した（起動しやすくするため）。種 `handmark_seed.txt` も同じフォルダに入った
  （アプリは読まない: 抽選の種は表の SHA-256 と日から作る `assignment::draw_seed`）。
- 17:02:48 の起動は移す前のパス。手跡の表のパスは `DiskFs::from_env(exe)` が起動時に exe から決め、自動起動の plist も古いパスを指す。
- 対応: トレイから終了してデスクトップから起動し直す。`autostart::handle` が印の不一致から Repoint で plist を付け替える（ログの
  `O1 autostart: re-pointed` と plist の ProgramArguments で確かめる）。

## 判断 5: Q3 に「作業していた」を 3 名の版で足す（研究者・2026-11-16）

- 発見: 研究者が「Q3 に作業（単純作業など）を含めないか」と尋ねた。6 択（熟考・詰まり・外部資料・会話・離席・回答不能）は ADR-031 D3 で固定で、
  どれも手が止まった時の中身。無作為の枠の問いは打鍵中にも出るので、「作業していた」が「回答不能（当てはまらない）」に混ざる。
- 決定: 本人の段 1 は今の 6 択のまま通す（前期と後期で計器を変えない）。この所見は本人の探索の結果として残す。
  3 名に配る版の前に、新しい ADR・段 1 の同意文書の版・`ActivityCategory`（logger・schema・gse-dataset の整合）・事前登録をあわせて直し、
  「作業していた」を足す。文言（単純作業を含むか・「作業」の範囲）はその ADR で決める。
- 却下案: 11-24 までに本人の版にも足す（8 日で ADR・同意・schema・再リリース、前期と後期で計器が変わる）／足さずに限界として書く。

## 記録: デスクトップからの起動と入口の門（2026-11-16 17:06〜17:11）

- 17:06:33 の起動（`~/Desktop/S1_実施用_macOS/`）: `consent=true`・`O1 autostart: re-pointed the login entry`・`input_monitoring=true`・Measuring。
  plist の ProgramArguments と `o1.autostart` はデスクトップのパス。
- 17:11 の `handmark_day`（要約だけ）: day 20773・late_start_day 20781・assigned=before・reason=before_late・shown_ms 0・
  table_sha256 が記録の値と一致。
