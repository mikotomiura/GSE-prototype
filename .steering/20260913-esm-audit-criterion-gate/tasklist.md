# タスクリスト — ESM 監査 criterion のゲート解除

## 準備
- [x] 一次資料を読む（起票 11 / `.idea` survey 見出し全件 / ADR-013 / 014 / 029 / 同意ドラフト）
- [x] 必須 Skill を読む（`verify-before-claiming` / `citation-ssot` / `data-privacy`）
- [x] 実測 4 件を確定（同意の逐語 / プローブ不発火 / 区間削除の穴 / 起票 11 #3 の失効）
- [x] 研究者確認（ADR-029/030 承認は保留 ／ ESM は O1 本体で発火させる）

## ⓪〜③（★ 文書と裁定。⚠️ コードより先）
- [ ] ADR-031 を書く（D1 配信 / D2 層化 / D3 規約 / D4 粒度 / D5 ⓪ / D6 削除の穴）
- [ ] ⚠️ 引用を付ける（`citation-ssot` ルール 1・★ ADR も対象）
- [ ] `docs/adr/README.md` に ADR-031 を足す
- [ ] ① `data-privacy` ルール 7 を改訂 ＋ チェックリスト
- [ ] ② 同意文書の改訂**案**（`consent-draft-o1.md` §3 表 / 注 C / §4）
- [ ] ② `docs/participant-setup-guide.md:105` / `:185-186` の「だけ」節
- [ ] ⚠️ **研究者承認待ちであることを案の冒頭に明記**

## ④（★ ここで初めてコードに触る）
- [ ] `schema_dto.rs` に `ActivityLabel` ＋ `ActivityCategoryDto` ＋ `ProbeStratumDto`
- [ ] `logger.rs` に書式 ＋ `line_type()` ＋ コンストラクタ
- [ ] `capabilities.rs` の `KNOWN_LINE_TYPES` ＋ `config_gated()`
- [ ] `recording.rs` の `paused_blocks_every_data_line_type` 列挙
- [ ] `redaction.rs` の `line_timestamp` 修正（⚠️ `session_meta` は残す）
- [ ] `emit_schema` を回して `schema/current.json` を再生成

## テスト
- [ ] `cargo test --manifest-path src-tauri/Cargo.toml --workspace`
- [ ] `cargo run --bin emit_schema` の byte-equal
- [ ] `gse-replay --snapshot` の回帰
- [ ] ⚠️ 検査を **正常 / 不在 / 壊れている** の 3 状態で試す（ルール 5b）

## 検査
- [ ] `PYTHONUTF8=1 python scripts/check_citations.py`（⚠️ 「違反なし」まで繰り返す）
- [ ] `PYTHONUTF8=1 python scripts/check_doc_lexicon.py`
- [ ] `bash scripts/check-o1-release-readiness.sh`（★ 前後で比較）

## レビュー
- [ ] `code-reviewer` ＋ `security-checker` を**並列**起動
- [ ] HIGH を消化
- [ ] `/cross-review`（⚠️ パス限定・`docs/mitou_submission/**` を送らない・`P0\d\d` を目視）

## 順序 B（★ A 完了後）
- [ ] 未踏 `.docx` 再生成（⚠️ 詳細資料だけ `--compact`）
- [ ] ⚠️ 10 ページ規約を測り直す

## 順序 C（★ B 完了後・時間が許せば）
- [ ] 起票 15: [V5] 全文 21 頁 ＋ [P273] APTIF 本文 11 頁を**同じラウンドで**読む
- [ ] 起票 18 / [V150] 書誌特定 / [V148] 本文 PDF
