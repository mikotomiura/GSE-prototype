# 設計

## 実装アプローチ

**2 段構え（Wave 0 = 取り込み / Wave 1 = 新規裁定）とし、issue の DAG で直列化する。**

```
Wave 0 ── 取り込み（案 C）: 既に書かれた SSOT を main に載せる ── Loop Engineering 適合
  001 アウトカム系      ADR-023/024 + metrics.rs +909 + 実験     AC: cargo test / gse-replay / emit_schema
  002 表現層 ADR        ADR-025..028 + expression-channel +337   AC: check_doc_lexicon.py
  003 サーヴェイ        references +112 + literature 3 本         AC: check_citations.py
  004 ツール            secrets-filter 4 件 + md2pptx + svg2png   AC: secrets-filter-test.sh
  005 提出文書図版      mitou_submission の png/svg/pptx          AC: check_doc_lexicon.py
  006 残り docs         agent-shared / positioning / wbs 等       AC: check_doc_lexicon.py

Wave 1 ── 新規裁定 ── Loop Engineering 不適（機械 AC は衛生条件のみ・人が承認する）
  007 ★最優先  転帰定義の一本化（ADR-009 と ADR-024 の関係を確定）
  008 P1       macOS IME の確定/放棄判別（ime_shadow 相当）
  009 P3       修飾キー同時押下フラグ
  （010 以降は Wave 0 完了後に分解する。理由は下記「なぜ Wave 1 を全部書かないか」）
```

### なぜ Wave 0 を先にやるか

`.idea/20260907` と `.idea/20260908` は ADR-024 / 025 / 028 を「正式 SSOT」として参照している。
これらは**未マージ**であって参照切れではない。取り込み前に新規 ADR を書くと、
**既に裁定済みの論点に重複 ADR を書く**。W-2（invitation 単独変化時の発火条件）は
ADR-027 が、W-3（チャネル生存の示し方）は ADR-028 が既に閉じている。

### なぜ Wave 1 を全部書かないか

Wave 1 の残り（メディア表現 A 区分・Mh-D 用語整理・Practice Portrait 理論 docs 等）は、
**Wave 0 の取り込み結果を見ないと正確に切れない**。取り込み後の `expression-channel.md`（+337 行）や
`glossary.md`（+27 行）に既に書かれている可能性があり、重複判定ができない。
→ Wave 0 完了後に `issue-slicing` を再度回して 010 以降を分解する。

## 変更対象

### 取り込み元（未マージブランチ）

`feat/resumption-outcome-arbitration`（200 files / +26,924 / −1,707 / 88 commits）

⚠️★★★ **`git checkout` / `git switch` でブランチを切り替えない。** main で作業し、
`git checkout <branch> -- <paths>` でファイル単位に取り出すか、`git show <branch>:<path>` で読む。

| 系統 | パス | 取り込み手法 |
|---|---|---|
| ADR（新規ファイル） | `docs/adr/ADR-023..028-*.md` | `git checkout <branch> -- <path>`（main に存在しないので衝突なし） |
| `metrics.rs` ほかコード | `src-tauri/src/analysis/metrics.rs` (+909) / `intervention.rs` (+10) / `intervention_eval.rs` (+10) / `bin/replay.rs` (+6) / `scripts/build_analysis_db.py` (+75) | ⚠️ **main 側も変化しているので単純上書き禁止**。`git diff main...<branch> -- <path>` で差分を確認してから適用 |
| docs（既存ファイル） | `expression-channel.md` (+337) / `glossary.md` (+27) / `adr/README.md` / `references.md` (+112) ほか | 同上。差分を確認してから適用 |
| 図版・バイナリ | `docs/mitou_submission/**` の png/svg/pptx | `git checkout <branch> -- <path>` |

### 新規作成するファイル

- `docs/adr/ADR-029-*.md` — 転帰定義の一本化（issue 007）。⚠️ 番号は取り込み後の最大値 +1 を確認して決める
- `src-tauri/src/input/ime_macos.rs` への `ime_shadow` 相当の追加（issue 008）

### 削除するファイル

なし。⚠️ ADR-024 は既存 `self_recovery_without_paste` 系を**削除せず副次指標へ降格・改名**する方針
（新旧の差自体を「推定器依存の大きさ」の証拠にするため）。

## 影響範囲

| 変更 | 影響 | 対処 |
|---|---|---|
| `metrics.rs` の識別子改名（`recovery` → `pflow_exit`） | ⚠️ `scripts/build_analysis_db.py` が**無音で壊れる**（schema drift check の対象外） | 同一 issue（001）で両方を変更する。ブランチ側で既に +75 行の変更あり |
| `metrics.rs` 変更 | `gse-dataset` 側 `metrics/P*/<os>/metrics.json` の後方互換 | ⚠️ ADR-024 自身が「実在する懸念」と自認。外部 repo なので本タスクでは**確認のみ**し blockers に記録 |
| `schema_dto.rs` 変更（issue 008/009） | `emit_schema` と `schema/current.json` の byte-equal 比較が割れる | **意図的に再生成**し、diff が意図通りか `.steering/` に記録する |
| `ime_macos.rs` / `hook_*.rs` 変更 | OS ごとに規則が違うロジック | **両 OS に対のテストを置く**（`docs/development-guidelines.md §3`。macOS 前提のテストが Windows CI で赤になった前例あり） |
| ADR-023〜028 の取り込み | ADR-017 D2 / ADR-021 D4 / ADR-022 D1 を改訂する | ADR 本文は書き換えない規約。README の「番号順に重なる」注記で追跡する |

## 既存パターンとの整合性

- **ADR の昇格レーン**: ADR-008 / ADR-009 のヘッダが `昇格元: .idea/20260801-....md §3-B/§4（.idea は追跡外・SSOT ではない）`
  と書く形式を既に確立している。Wave 1 の新規 ADR も同じ形式で `昇格元` を書く。
- **重ね書き**: ADR 本文は書き換えず、後続 ADR が条項を改訂する。README に改訂関係を記す。
- **`.idea` の自己訂正**: `.idea/20260819` はファイル末尾に「本文で無効・要改訂になった記述」の表を
  追記する運用をしている。⚠️ `.idea/20260901` の `level` 4 値写像表と個人化境界は
  ADR-021 D4 / ADR-022 D3 に上書き済みで**旧仕様のまま残っている**ため、同じ処置を Wave 1 で行う。

## テスト戦略

⚠️★★★ **`Cargo.toml` は repo 直下に無い（`src-tauri/` にある）。** repo 直下で
`cargo test --workspace` を叩くと即座に空振りする。

```bash
cd src-tauri
cargo run --bin gse-replay -- tests/fixtures/minimal.ndjson --snapshot tests/snapshots/minimal.json
cargo test --workspace
cargo run --bin emit_schema   # 出力を src-tauri/schema/current.json と byte-equal 比較
```

repo 直下から動かずに叩くなら `--manifest-path src-tauri/Cargo.toml` を付ける。

| 検査 | コマンド | どの issue で使うか |
|---|---|---|
| 回帰（最優先） | `cargo run --bin gse-replay -- tests/fixtures/minimal.ndjson --snapshot tests/snapshots/minimal.json` | 001 / 008 / 009 |
| 単体 | `cargo test --manifest-path src-tauri/Cargo.toml --workspace` | 001 / 008 / 009 |
| schema drift | `cargo run --bin emit_schema` → `schema/current.json` と byte-equal | 001 / 008 / 009 |
| 禁止用語 | `PYTHONUTF8=1 python scripts/check_doc_lexicon.py` | 002 / 005 / 006 / 007 |
| 引用採番 | `PYTHONUTF8=1 python scripts/check_citations.py` | 003 / 007 |
| 秘密フィルタ | `bash scripts/secrets-filter-test.sh` | 004 |

⚠️ **`check_citations.py` は違反を 1 回で全件出さない**。「違反なし」になるまで是正 → 再実行を繰り返す。

## ロールバック計画

- Wave 0 の各 issue は **1 issue = 1 PR** で、単独 revert できる。
- ⚠️ 001（`metrics.rs`）で golden が割れた場合: `HMM_VERSION` bump の要否を判断する。
  ADR-024 は bump 不要（`engine.rs` / `schema_dto.rs` / `schema/current.json` に差分なし）と
  実測確認済みだが、main 側の変化で崩れた場合は **ADR-023 A3 節が検討した A3-(i) 案
  （回復判定を `p_stuck` 低下へ置換）を採ると bump が必要**になる点に注意。
- 008 / 009 で `schema/current.json` を再生成した後に問題が出た場合: 再生成前の
  `schema/current.json` に戻し、`emit_schema` の出力が一致することを確認してから revert する。
