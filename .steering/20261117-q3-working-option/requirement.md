# Q3 の選択肢に「作業」を足す（3 名の版）

## 背景

段 1 のプローブの Q3「直前の30秒、何をしていましたか」は ADR-031 D3 の固定 6 択（熟考・詰まり・外部資料・会話・離席・回答不能）で、どれも手が止まったときの中身を選ぶ形になっている。無作為の枠の問いは打鍵中にも出るので、作業を進めていたときの回答が「回答不能（当てはまらない）」に混ざる（`.steering/20261116-release-v0.1.42-handmark/decisions.md` 判断 5）。

判断 5 で、本人の段 1 は 6 択のまま通し（前期と後期で計器を変えない）、3 名に配る版の前に直すと決めた。

## ゴール

3 名に配る版の Q3 が 7 択（「作業」を回答不能の直前に足す）になり、それを許す ADR・同意文書の新しい版の草案・記録の型と schema・事前登録の草案が揃っていること。

## スコープ

### 含むもの

- ADR-055（ADR-031 D3 の条件 i の選択肢を 7 つに改める。Proposed、同意文書の新版を研究者が承認したら Accepted）
- 同意文書の新版の草案（`.steering/20261114-gse-stage1-n3-consent/consent-draft-s1.md` を元に、Q3 の表と記録に残るものの文を直す）
- 画面: `src/probeTypes.ts` の選択肢と `src/components/S1ProbeCard.tsx` の Q3 の文（いちばん長かったもの）
- 記録: `ActivityCategory`（`logger.rs`）・`ActivityCategoryDto`（`schema_dto.rs`）・`emit_schema` で `schema/current.json` を作り直す・gse-dataset との照合
- 同意の版の印 `S1_PROBE_CONSENT_VERSION` を上げる
- 事前登録の草案 `docs/preregistration-stage1.md` の Q3 を使う箇所（7 択と、本人の 6 択と並べるときの畳み方）
- 選択肢の中身を述べている現行の文書（data-privacy Skill のルール 7・glossary の C4・設計地図）

### 含まないもの

- リリース（タグ・配布物）。Windows 版の手跡といっしょに 3 名の版で行う。
- 本人の段 1 の配布物（`~/Desktop/S1_実施用_macOS/`）と、動いている gse-next。
- コードの注釈や検査の名前に出てくる「6 択」という呼び名の一斉の書き換え（意味が変わらない箇所は残す・decisions 判断 6）。
- 履歴の文書（`docs/history/`）と既存の ADR の本文。

## 受け入れ条件

- [ ] ADR-055 が書かれ、ADR README に載っている（Proposed）
- [ ] `ActivityCategory::ALL` が 7 つで、`working` の往復と行の書き出しのテストが緑
- [ ] `cargo run --bin emit_schema` の出力が `src-tauri/schema/current.json` と一致し、gse-dataset との parity check を通す（または drift を研究者に示す）
- [ ] カードに 7 つが出て、Q3 の文に「いちばん長かったもの」が入っているのを画面で確かめた
- [ ] `S1_PROBE_CONSENT_VERSION` が上がり、旧い印では同意済みにならないことをテストで確かめた
- [ ] 同意文書の新版の草案と事前登録の草案が直っている
- [ ] /cross-review（Codex を含む）を通した

## 関連ドキュメント

- docs/adr/ADR-031-self-reported-activity-audit-criterion.md D3
- docs/adr/ADR-052-stage1-pre-adoption-confirmatory-n3.md
- .steering/20261116-release-v0.1.42-handmark/decisions.md 判断 5
- .steering/_handoff/next-session-gse-stage1-n3-version-prep-while-waiting.md B

## 運用メモ

- /reimagine 適用: No
- 理由: 設計の分かれ目（文言・回答不能との境・6 択と 7 択の読み方・並び・範囲）は着手時に研究者が 1 問ずつ決めた。変更は選択肢を 1 つ足す形で決まっており、別案を作り直す余地が小さい。Codex の目は完了時の /cross-review で入れる。
