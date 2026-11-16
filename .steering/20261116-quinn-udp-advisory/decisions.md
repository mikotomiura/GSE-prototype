# 重要な設計判断

## 判断 1: `cargo update` の結果でなく、quinn-udp の 2 行だけを変えた lock を採る

- **判断日時**: 2026-11-16
- **背景**: `cargo update -p quinn-udp`（`--precise 0.5.16` でも同じ）は quinn-udp の windows-sys を 0.59.0 → 0.52.0 に寄せ、
  同時に arboard（0.60.2 → 0.52.0）と rustls-platform-verifier（0.59.0 → 0.52.0）の windows-sys まで変えた。
  三者とも windows-sys を範囲で要求している（quinn-udp `>=0.52, <=0.61`・arboard `>=0.52.0, <0.61.0`・
  rustls-platform-verifier `>=0.52.0, <0.62.0`）ので、範囲の中で選び直された。
- **選択肢**:
  - A: `cargo update` の結果（5 行）をそのまま採る
  - B: quinn-udp の version と checksum の 2 行だけを書き換え、`cargo metadata --locked` で cargo が lock を受け入れることを確かめる
- **採用**: B
- **理由**: arboard と rustls-platform-verifier は Windows でコンパイルされる依存で、0538 と無関係に Windows の
  ビルドの中身を変える。quinn-udp 0.5.16 の windows-sys の要求は 0.5.15 と同じ範囲なので、0.59.0 のままで成立する。
  `cargo metadata --locked` が通った（lock の書き換えが不要＝cargo が解として受け入れた）。checksum は `cargo update` が書いた値。
- **トレードオフ**: lock を手で書き換えた。後で誰かが `cargo update` を回せば A の形に寄る（それ自体は害ではない）。
- **影響範囲**: `src-tauri/Cargo.lock` の 2 行のみ
- **見直しタイミング**: windows-sys をまとめて上げるとき

## 判断 2（事実の記録）: quinn-udp はどのビルドにもコンパイルされていない

- quinn は reqwest 0.13.2 の `http3` feature（`dep:quinn`）でしか有効にならず、GSE も tauri も `http3` を有効にしていない。
- 実測: `cargo tree --locked --workspace --target all --all-features -e all -i quinn-udp`（build・dev の依存も含む）は `nothing to print`。
  （Cargo.toml に `[workspace]` は無く単一パッケージ gse-next。/cross-review で Codex が `-e normal` だけでは狭いと指摘し、広げて測り直した）
- cargo-audit は Cargo.lock の中身を見るので、コンパイルされない依存でも赤になる。
- したがって現 main の lock と feature の構成では、配布物（gse-next）のバイナリに quinn-udp は入っておらず、今回の変更は配っている版に影響しない。
  リリース・タグの扱いは研究者に確かめる。
