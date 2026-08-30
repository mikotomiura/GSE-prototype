# 設計

## 実装アプローチ

★ **本タスクは実装を含まない。** サーヴェイ 4 ラウンドを回し、`docs/` の SSOT へ append-only で載せ、
次セッションの議論の材料を揃えるところまでである。

### ★ 採った実行方式（★ 理由つき）

| 論点 | 採った形 | ★ 理由 |
|---|---|---|
| **探索** | ★ **サブエージェント 4 本を並列**（R-1〜R-4・opus） | ★ 4 ラウンドは互いに独立で、探索は I/O 律速である |
| **採番** | ⚠️★★★ **サブエージェントに採番させない。** 出典は DOI / arXiv / 正規化 URL の key で識別させ、`[Pn]`/`[Vn]` はメインが直列で振る | ⚠️ **並列で `references.md` を書くと採番が衝突し、append-only が壊れる**（citation-ssot ルール 2） |
| **SSOT 登録** | ★ **1 ラウンドずつ直列**（カード → references append → `_index` 追記 → §3 還元 → コミット） | ★ memory「Commit each survey round」—— **複数ラウンドが同居すると `git add -p` で分離できない** |
| **書き込み手段** | ★ `scratchpad/splice_refs.py`（アンカー行の直後に append。既存行は 1 バイトも変えない） | ⚠️ ヒアドキュメントは CJK ＋ 記号でシェル引用が壊れた。★ Write ツールで行ファイルを作り Python で差し込む形に倒した |
| **検算** | ★ 各ラウンド後に `PYTHONUTF8=1 python scripts/check_citations.py` | ★ 未登録参照 / 欠番 / tombstone 引用 / 相互リンク無しの同一 key を機械検出する |

### ★ サブエージェントに課した契約（★ 4 本共通）

- **反証 angle を 1 つ以上必ず含める**
- **敵対的 3 票**（内的妥当性 / 外的妥当性・外挿 / 効果量の頑健性）。`1-2`・`0-3` は**否決リストへ**
- ⚠️★★★ **対称性**: GSE に有利な主張も不利な主張も**同じフィルタ**にかける
- ⚠️★★★ **`判定不能`（該当研究ゼロ）を「弱い支持」に丸めない**。★ **「空白は有望を意味しない」を併記する**
- ⚠️ **書誌を捏造しない**。未確認は `provisional` とし、**何が未確認かを書く**
- ★ **PDF は保存 → pypdf**（★ WebFetch は PDF 本文を読めない）。届かなければ「abstract 水準」と正直に書く
- ⚠️ **`docs/` を 1 バイトも編集しない**（★ 出力は scratchpad の指定ファイル 1 本のみ）
- ⚠️ **キーストローク内容・NDJSON セッションログを検索クエリにも外部送信にも含めない**（data-privacy）

## 変更対象

### 新規作成
- `docs/literature/20260830-auto-onset-acceptance-and-wearing-detection.md`（R-2・カード 6 枚）
- `docs/literature/20260830-smartphone-ambient-surface.md`（R-1・カード 9 枚）
- `docs/literature/20260830-unmeasured-embodied-return.md`（R-3・カード 9 枚）
- `docs/literature/20260830-theory-scaffold-inconvenience-sdt-reflection.md`（R-4・カード 9 枚）

### 追記（append-only）
- `docs/references.md` — **[P133]–[P191] / [V87]–[V88]**（★ renumber ゼロ）
- `docs/literature/_index.md` — 4 行
- `docs/research-positioning.md` **§3 のみ** — 4 ブロック

### ★ 既存行の更新（★ 二重登録を避けるため。renumber ではない）
- **[P101] / [P102]** — 表示面の同定（★ **携帯電話の壁紙 / lock・home 画面**）を追記
- **[P77]** — 実験 4 の実数と、⚠️ **減衰の内訳（ベースライン低下 d ≈ 0.60）**を追記
- **[P113]** — 一次取得により **key を DOI へ確定し provisional → active へ昇格**、⚠️ 逐語の語順を訂正
- **[P104]** — ⚠️ **昇格できなかったこと**を明記
- **[P6]** — ⚠️★★★ **書誌が未検証であることを追記し `active` → `provisional` に降格**

### ⚠️ 触っていないもの
- ⚠️ `src-tauri/`（★ 計器は 2026-08-21 に凍結）
- ⚠️ `docs/preregistration-v0.3.md` / G1 事前登録（★ 凍結・ADR-015 D5）
- ⚠️ `docs/research-positioning.md` **§4（差分）・§5（仮説）**（★ 次セッションの研究者判断）
- ⚠️ `docs/architecture.md` / ADR（★ 本タスクの範囲外）
- ⚠️ `.idea/` のメモ本体（★ 追跡外・議題の本体であって書き換える対象ではない）

## 影響範囲

- ★ **`docs/` のみ。コードへの影響ゼロ**（`cargo test` 不要）。
- ⚠️★★★ **ただし §3 の内容は §4 / §5 の書き換えを要求する** —— ★ **それは次セッションで裁く**。
  ★ 本タスクは **「§4 に影響するか」の判定までを記録し、書き換えていない。**

## テスト戦略

- ★ **機械検算**: `PYTHONUTF8=1 python scripts/check_citations.py` が **違反なし**（★ 4 ラウンドとも実施）。
- ★ **append-only の確認**: `git diff --stat` の削除行が、**意図した既存行の更新分のみ**であること。
- ⚠️ **カードの内容そのものに機械テストは無い**。★ 代わりに **各カードに自己点検チェックリストを置き、
  否決リストと対称性の記録を必須にした**（★ `/literature-review` Step 9）。

## ロールバック計画

★ ラウンドごとに分離コミットしてあるので、**`git revert` で 1 ラウンドだけ戻せる。**
⚠️ ただし **[P101] / [P102] / [P77] / [P113] / [P104] / [P6] の既存行更新は R-1・R-3・R-4 に分散している**ので、
★ **戻すと訂正した誤りが復活する**（★ 特に **[P101] を「可搬な物理オブジェクト」と読める状態**に戻る）。
