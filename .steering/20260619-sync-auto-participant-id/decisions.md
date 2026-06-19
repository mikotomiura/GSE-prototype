# 設計判断

## D1: PID の真実源は raw のディレクトリ構造 (パス導出を最優先)

**背景**: Part 2 で logger は `raw/<auto-id>/` に書く。sync が `GSE_PID` 単一前提だと raw と
metrics の ID が乖離する。

**決定**: sync-session の PID 解決は **パス導出 (`.../raw/<PID>/`) を最優先**とし、導出不可時のみ
`GSE_PID` → `~/.gse/participant_id` → `P000`。これで raw 配下のファイルは必ず raw のディレクトリ名で
metrics に対応付き、構造的に一致する。

**Why / トレードオフ (明示)**: handoff の受け入れ条件「`GSE_PID` 明示時の従来挙動が不変」は、
**raw 配下のファイルに対しては厳密には変わる**。例: `GSE_PID=P003` でも `raw/P000/x.ndjson` を
sync すると新挙動は P000 (旧挙動は P003)。しかし旧挙動こそが「raw と metrics が乖離する」本バグで
あり、これを直すのが本タスクの目的。fallback dir のファイル (`~/Documents/GSE-sessions/`、raw 構造
外) では導出が成立せず `GSE_PID` が従来どおり効くため、典型ワークフローの後方互換は保たれる。
本プロジェクトの重視品質「正確性」(ID 不一致 = 静かなデータ汚染) を優先。

## D2: スクリプト allowlist は logger と完全一致 (Windows 予約名も拒否)

**背景**: handoff は allowlist を `[A-Za-z0-9_-]`, 1..=64 と指定。logger の
`is_valid_participant_id` (logger.rs:930) はこれに加え **Windows 予約名** (CON/PRN/AUX/NUL/
COM1-9/LPT1-9, 大小無視) も拒否する (logger.rs:918-921)。

**決定**: スクリプト側も予約名拒否を含めて logger と完全一致させる。handoff の「logger と挙動を
揃える」を文字どおり満たす。raw ディレクトリ名由来の PID にも全経路で適用し、`../` 等を弾く。

**Why**: 非対称だと「logger は弾くがスクリプトは通す (またはその逆)」の挙動差が残り、Part 1
code-reviewer MEDIUM の指摘が部分解消に留まる。予約名は raw に紛れ込めば metrics 生成が
`ERROR_INVALID_NAME` で失敗し原因が分かりにくいので、スクリプト側でも早期に弾く。

## D3: 構造ガード — パス導出は祖父ディレクトリ名 == `raw` を必須とする

**背景**: fallback dir のパスは `~/Documents/GSE-sessions/gse_*.ndjson`。親ディレクトリ名
"GSE-sessions" は allowlist (`[A-Za-z0-9_-]`) を**通ってしまう**ため、単純な親名導出だと
誤って PID="GSE-sessions" になる。

**決定**: 親名が allowlist を通るだけでなく、**祖父ディレクトリ名が厳密に `raw`** のときのみ
導出成立とする。これで raw 構造外のファイルは導出されず、ローカル PID 解決 (GSE_PID→永続化→P000)
へ正しく落ちる。

## D4: sync-all のローカル PID 解決は GSE_PID → 永続化 → P000 (パス導出は使わない)

**背景**: sync-all の Step 1 (fallback→raw コピー) はフラットな fallback ファイル群を扱う。
これらは raw 構造を持たないためパス導出できない。

**決定**: fallback コピー先 `raw/<local>/` の `<local>` は端末ローカルの PID =
`GSE_PID` → `~/.gse/participant_id` → `P000`。fallback dir は端末ローカルかつ単一被験者の作業
記録なので、この端末の永続化 ID が正しい帰属先。Step 2 の metrics 生成は raw 構造を全反復し、
各ファイルはパス導出 (sync-session に委譲) で解決する。

## D5: `.ps1` に UTF-8 BOM を付与 (PS 5.1 + 非 ASCII の CP932 誤読対策、実装中に発覚)

**背景**: 参加者 ID 解説コメント (日本語) を追記後、`sync-session.ps1` が PS 5.1 の
`Parser::ParseFile` で「Unexpected token ')'」となり parse 不能に。調査の結果、本機の
`[Text.Encoding]::Default` は **CP932 (Shift-JIS)** で、BOM 無し `.ps1` を PS 5.1 が
Shift-JIS として読むと、追記した日本語のバイト列が誤って `#>` を生成し comment-based help
ブロックを途中で閉じてしまうのが原因と判明 (`powershell.exe -File` も同経路で読むため
**実行時にも壊れる** 実害)。既存スクリプトは偶然問題バイト列を含まず通っていただけ。

**決定**: 編集した `.ps1` (`sync-session.ps1` / `sync-all.ps1`) に **UTF-8 BOM** を付与する。
これで PS 5.1 はロケール (CP932) に依存せず常に UTF-8 として読む (Microsoft 推奨)。両ファイルとも
BOM 付与後に `ParseFile` 緑を確認。`.sh` は影響なし (bash はバイト列をそのまま扱い `#` 行コメントも
誤閉じしない)。

**Why**: BOM 無し日本語 `.ps1` は「どの日本語を書くか」で parse 可否が変わる極めて脆い状態。
将来の日本語追記でも再発しないよう、文字単位の回避 (ASCII 化) ではなく BOM で構造的に解決した。
§10.2.1 にも footgun として追記。

**注意**: §10.2.1 が警告する BOM は `>` リダイレクトが**出力ファイル**に付ける UTF-16 BOM の話で、
本件 (ソース `.ps1` の UTF-8 BOM) とは別。前者は git diff 汚染で回避対象、後者は PS 5.1 が
非 ASCII を正しく読むための必須対応。
