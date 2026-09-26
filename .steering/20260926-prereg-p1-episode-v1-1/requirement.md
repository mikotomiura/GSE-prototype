# prereg-p1-episode-v1-1 —— P1 事前宣言の新版 v1.1

## 背景

`docs/preregistration-p1-episode.md` は 2026-09-25 に凍結された（凍結 JSON `src-tauri/prereg/p1-episode.json` は `1.0.0`）。
凍結のあとに、ADR-030 補訂 2 と前タスク（`.steering/20260921-p1-prereg-cli-poles/`）の判断 16・25・28・29 が次のことを決めた。そのため、凍結文書が一次と食い違ったまま残っている（2026-09-26 に一次で確認した）:

1. §4 表 #5 は「**頻度は下限として読む**」と書いている → 判断 29／補訂 2 項目 9 は「**両方向の誤差がある観測値**（Windows に限り下限として読める）」へ上書きした。
2. 「併せて出力に載せるもの」の表に `ime_overlap` が無い。補訂 2 項目 9 の最後の項が、新版を切るかを研究者判断へ回している。
3. §2 の見出しは「草案 —— 研究者の承認待ち」のまま → 判断 16 には「§2 は 4 件とも草案どおり承認された（2026-09-21）」とある。
4. 両極の上下界の取り方（min / max・`pole_applicable=false` の極を入れない）が §3 に無い（補訂 2 項目 4・5／判断 25・28）。
5. 探索の実行で `q` と従属変数の `warmup_count` を対で指定することが §2 に無い（補訂 2 項目 2・起票 P1-F）。

★ **実データを 1 件も見る前に**閉じる（forking paths の排除。PG-1 より前）。後続タスク D はこれを待っている。

## ゴール

凍結文書の**冒頭に「v1.1 改訂宣言（2026-09-26）」ブロックを足して再凍結する**。上の 1〜5 を、本文を書き換えずに「上書きする箇所を名指しする」形で入れる（前例: `preregistration-v0.3.md` のバージョンカット宣言／追記）。

## スコープ

### 含むもの
- `docs/preregistration-p1-episode.md` の冒頭へのブロック追加（追加だけで、削除行は 0）
- `.steering/` の記録（requirement / design / tasklist / decisions）

### 含まないもの
- 凍結文書 §1〜§5 の本文の書き換え
- 凍結 JSON の変更（`version` は `1.0.0` のまま・sha 不変）とコードの変更（`replay.rs` のテストを含む）
- 起票 P1-A（凍結既定で restart の非退化検査が走らない）: fixture／テスト側の宿題なので、事前宣言には入れない
- CLI に `q → warmup_count` の連動を持たせるかどうかの裁定（P1-F の実装形。探索プロトコルを実装するときに決める）
- PG-1（一人あたり episode 数の下限の値）: WP1 の yield が出た直後の別ゲートで、次の版で扱う
- 実データ（NDJSON・metrics）を開くこと・集計すること／タスク D（P1 本体の段取り）
- ADR-030 本文と補訂の書き換え

## 受け入れ条件

- [ ] `python scripts/check_prereg_parity.py` が exit 0
- [ ] `python scripts/check_prereg_parity.py --self-test` が exit 0
- [ ] `git diff main -- src-tauri/` が空（JSON もコードも不変）
- [ ] `git diff main --numstat -- docs/preregistration-p1-episode.md` の削除行数が 0（本文を書き換えていない）
- [ ] 新しいブロックが上の 1〜5 をすべて、一次（判断番号・補訂 2 の項目番号）を付けて名指ししている
- [ ] `/cross-review` を通している（Codex gpt-6-astra・パスを限定する）

## 関連ドキュメント

- `docs/adr/ADR-030-stall-onset-and-decision-episode.md` 補訂 2（全文）
- `.steering/20260921-p1-prereg-cli-poles/decisions.md` 判断 16・19・25・28・29・起票 P1-A / P1-F
- `docs/preregistration-v0.3.md` 冒頭（版の切り方の前例）
- 引き継ぎメモ: `.steering/_handoff/next-session-prereg-p1-episode-v1-1.md`

## 運用メモ
- /reimagine 適用: No
- 理由: 文書の版上げであり、設計の選択肢は grill（判断 1〜4）で閉じている。アーキテクチャ・API の判断を伴わない
