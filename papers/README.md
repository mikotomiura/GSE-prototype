# papers/

論文ごとの作成物（キット・実験・原稿）の置き場。1 論文 = 1 ディレクトリ（例: `ime-observation/`）。

- `papers/` は **GSE 本体（`src-tauri/` / `src/` / `scripts/`）から import・参照しない**。
  逆向き（`papers/` が GSE のファイルを使う）は、**写して出典を記録したもの**に限る。
  - 逐語コピーは `kit/logger/manifest*.json`（照合器つき）。
  - それ以外の写し（例: 実行コストの計器）は、各ディレクトリの README の表に
    元のパス・SHA-256・変えた行を書く。
  - 実行時に GSE のパスを読みに行かない（公開時に書き出せなくなるため）。
- GSE のビルド・CI の対象ではない。ただし repo 全体を見る門（`scripts/check-shell-portability.sh` 等）にはかかる。
- 生ログ（`*.jsonl` / `*.ndjson` / run ディレクトリ）は git に入れない。Zenodo に寄託し、SHA-256 を
  `experiment/data.md` に記録する。
- 人の打鍵データ・GSE の被験者データ（Phase1 / G1 / O1）を置かない。
- 公開時に書き出す（公開 repo へ export する）ので、`papers/` の文書・コード・コメントに次を書かない:
  GSE の作業記録置き場へのパス・被験者 ID（大文字の `P` ＋ 3 桁の数字。★ 角括弧で囲んでも同じ —— 公開物では非公開の書誌の番号
  `[Pn]` / `[Vn]` を使わず、普通の学術的な引用を使う・IME 論文の判断 76）・
  データ用の別 repo の名前・メールアドレス・絶対パス。
  設計の根拠は「どこそこの節」ではなく、**内容そのもの**を書く。
  - 例外: `kit/logger/manifest*.json` に載った **GSE からの逐語コピー**は repo の中では 1 バイトも変えないので、
    元のコメントの作業記録のパスや日本語をそのまま持つ。★ 公開の書き出しはコメントを除き、日本語の文字列リテラルを
    内部の対訳表で英訳してから検査する（IME 論文の判断 69。許可リストは使わない）。

## 公開物の書き方（2026-09-28 から・IME 論文の判断 36）

公開する論文ディレクトリ（例 `ime-observation/`）の中身は、公開 repo でそのまま読まれる。次を守る。

- **学術的な英語で書く**: コードのコメント・docstring・README・形式の契約（`FORMATS.md`）・CLI のヘルプ・selftest の説明。
  論文の方法節のような平叙文（主語と述語をはっきり・断定の強さを根拠に合わせる）。★ ⚠️ などの記号・口語・感嘆は使わない。
- **GSE への言及を一切書かない**: `GSE` という名前、`src-tauri/` などの GSE のパス、GSE のファイル名・関数名・用語
  （Phase1 / G1 / O1 / Nudge など）、「GSE と同じ判断」のような関係の説明。識別子（関数名・CLI のフラグ）も同じ。
- **内部の番号を書かない**: 判断の番号・issue の番号・マイルストーン（M0〜M13）・波（W1〜）。公開の読者には意味が無い。
  必要なら内容そのもの（例「the calibration pilot」）で書く。
- **機械の門**: `.steering/20260927-ime-observation-paper-eval-design/issues/_style_check.py`（公開しない道具）。
  各 issue の acceptance は `style_ok` でその issue が変えたファイルを検査する。★ 公開の書き出し
  （`kit/export/export.internal.py`）も、書き出した全体にこの道具を回し、違反があれば止まる（IME 論文の判断 75）。
- **出どころは公開しない所にだけ書く**: `kit/logger/manifest*.json` の `gse_*` の欄と、書き出しの対象外の
  `*.internal.*`（例 `kit/logger/PROVENANCE.internal.md`・★ 書き出し器そのもの `kit/export/*.internal.*`）。
  公開の書き出しがそれらを落とす（IME 論文の判断 74: 書き出し器は公開しない）。
- **逐語コピーは変えない**。コメントは公開の書き出しで機械的に除き、学術的な英語の説明を冒頭に 1 つ付ける。
- ⚠️ acceptance が名指す文字列（selftest のケース名など）は、その acceptance が直されるまでそのまま使う。
