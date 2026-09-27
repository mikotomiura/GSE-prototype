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
