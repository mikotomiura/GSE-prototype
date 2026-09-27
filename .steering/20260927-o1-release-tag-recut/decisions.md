# 決定 — o1-release-tag-recut

## D1 バージョンは 0.1.37 に上げる（研究者 2026-09-27）
- 決定: 4 ファイル（Cargo.toml / tauri.conf.json / package.json / Cargo.lock の gse-next）を 0.1.37 に上げ、そのコミットに v0.1.37 を切る。
- 理由: G1 の解析は `meta.app_version = 0.1.36` で G1 のファイルを見分ける契約（distribution-tag.md）。同じ番号のまま別バイナリを作ると区別できない。
- 却下案: 0.1.36 のまま現 main に別名タグ — app_version が衝突する。

## D2 O1 の配布タグ記録は docs/o1-distribution-tag.md を新設（研究者 2026-09-27）
- 理由: 既存の distribution-tag.md は冒頭で「--mode g1 専用・G1 凍結」を宣言している。O1 の運用文書（o1-roster-operations.md / o1-deletion-ledger.md）と並べる。
- 却下案: G1 の記録に O1 節を追記 — G1 凍結の宣言と混ざる。

## D3 範囲は O1 zip 作成と記録まで（研究者 2026-09-27）
- Drive 差し替え・送付は研究者。

## D4 G1 ゲートへの影響なし（一次確認）
- `scripts/check-g1-collection-readiness.sh` は git tag / distribution-tag / 版文字列を参照しない（grep 0 件）。O1 ゲートは「o1.rs を含む最新タグ」を `git tag --sort=-v:refname` で自動選択するので、v0.1.37 を切れば判定対象が切り替わる（scripts/check-o1-release-readiness.sh:261-265）。

## D5 package-lock.json は触らない（一次確認）
- `package-lock.json` の版は `0.1.21` のまま（v0.1.36 の T1 も「4 ファイル」で揃えており、前例どおり）。配布バイナリの版は tauri.conf.json / Cargo.toml が決める。

## D6 修正の目印は gse-submit で見る（実測 2026-09-27）
- reconcile は `gse-submit` に入り、`gse-next` には入らない（`gse-next` / `gse-next.exe` では v0.1.36・v0.1.37 とも `reconcile.lock` すら 0 件）。
- `gse-submit` で新 warn メッセージ `lock heartbeat` / `taken over or removed` が v0.1.37=1・v0.1.36=0、旧来の `taking over a stale lock` が両方 1（陽性対照）。記録は `docs/o1-distribution-tag.md`。

## D7 並行セッションとのチェックアウト共有事故（2026-09-27）
- 同じ作業ツリーで並行セッション（loop-run.sh 修正）が `git checkout -b fix/loop-run-progress-flag` した直後に私がコミットし、版上げコミット `7798874` がそちらのブランチに載った。
- 対処: 私のブランチ ref を `7798874` に付け替え、以後は `../GSE-o1-tag` の worktree で作業。並行セッション側ブランチの `reset --keep` は権限で拒否されたため研究者へ委ねた。
- 教訓: 並行実行可能な引き継ぎでも、**チェックアウトを共有するなら並行ではない**。最初から worktree を切る。

## D8 /cross-review の結果（2026-09-27・Claude ∥ Codex・縮退なし）
- CRITICAL/HIGH なし。Claude 側は 3 観点（版の整合・記録の事実性・機密混入）すべて裏取り済み（dmg の SHA-256 は Release API の digest と一致。reconcile は `#[cfg(feature = "package")]` で gse-submit 専用＝D6 をソースで確認）。
- Codex MEDIUM ① heartbeat の実動作は未検証 → 記録（docs/o1-distribution-tag.md「限界」）に既に明記。実機通し確認は別タスクへ申し送り。
- Codex MEDIUM ② 鮮度ゲートの監視パスが `src-tauri/src` / `src-tauri/Cargo.toml` / `src` だけで、`Cargo.lock` / `tauri.conf.json` / フロント依存 / 梱包スクリプトの変更は「古い」と判定されない（`scripts/check-o1-release-readiness.sh:286` で確認）。既存の盲点で本タスクの差分ではない。★ 今回のタグ `v0.1.37` は main の先頭なので該当しない。→ ゲート改修の候補として申し送り。

## D9 Drive の照合と記録票 C（2026-09-28）
- 研究者が G1 / O1 の zip 4 点を Drive に配置。コネクタで 4 点のバイト数が手元と一致（O1: 10423191 / 5981440、G1: 10414729 / 5974147）。
- 課題ページ: Drive の「G1課題文_P001〜P020」200 枚がブロックごとのバイト数で手元と全件一致。1 枚（P007 block02）をダウンロードして内容の区間一致を確認。`origin/main`（389427d）の生成器で作り直した 208 枚が手元と `diff -r` 一致。→ 記録票 C を記入（G1 ゲート 24 / 2）。
- ⚠️ コネクタの search_files はページ送り（nextPageToken）で同じ結果を返した → フォルダ（parentId）単位の検索に切り替えた。
- 研究者の指示で G-1 / G-2 / G-5 の実装を次セッションへ（`.steering/_handoff/next-session-o1-resilience-g1-g2-g5.md`）。
