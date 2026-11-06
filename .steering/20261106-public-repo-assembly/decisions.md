# 重要な設計判断

## 判断 1: 名前・置き方・入れる文書・許諾（2026-11-06）

- **背景**: 引き継ぎ（12）の §2 の 1。研究者が決めた順は切り出し → 公開 repo → attack-me round 3。組み方の未決を AskUserQuestion で聞いた。
- **採用（研究者の選択・いずれも推奨案）**:
  - 名前: `stall-runup-equivalence`（GitHub は mikotomiura の下・手元は `~/stall-runup-equivalence`）。
  - 置き方: GSE のパスのまま写す（repo の根で `shasum -c confirm-manifest.sha256` が通る）。
  - manifest の内部文書 5 本（ADR-030・`docs/preregistration-p1-episode.md`・事前登録の草案の日英・英語版の照合の記録）は逐語で入れる。入れる前に私が読み、出せない記述があれば止めて相談する。
  - 実験の記録（conditions・notes・data・env）は日本語のまま入れる。notes.md は書き手ごとの値が無いかを確かめてから。
  - 許諾: コード MIT OR Apache-2.0、文書と結果 CC BY 4.0。
  - /reimagine は使わない。
- **却下案**: 整理し直して対応表を付ける（照合が一段増える）／内部文書は SHA-256 だけ（manifest の照合が部分的になる）／スクリプトと結果だけ（条件を先にコミットしたことを時刻で示せない）。
- **影響範囲**: 公開 repo の中身・README。

## 判断 2: GSE の文書と .steering を入れない・ADR-030 の点検の結果（2026-11-06〜07）

- **経緯**: 判断 1 で内部文書 5 本を逐語で入れると決めた後、点検役（general-purpose・Opus）が ADR-030 の 940〜941 行に未踏の提出書類のファイル名と訂正の経緯を見つけた。逐語のまま入れるかを聞き、研究者は一度「逐語のまま入れる」を選んだが、その後に「未踏や GSE 関連の docs は公開 repo では出さないで」「公開 repo や論文でのコード、実験記録や tex のみ。steering なども公開してはダメ。作業や個人、GSE 研究情報だから」と改めた。
- **採用**: 入れるのは推定器の crate・論文と公開 repo のコード・実験の記録（experiments/ の条件・notes・結果）・原稿の tex（paper/）だけ。`docs/`（ADR-030・preregistration-p1-episode.md）・`.steering/`（事前登録の草案の日英・英語版の照合とそのスクリプト）・`src-tauri/` は入れない。manifest の照合は `tools/check_manifest.py` が、公開物の 14 件と停滞の定義の JSON（`estimator/prereg/` の同じバイト）を照合し、6 件を「公開しない」と示す。事前登録の草案 3 本は OSF の mrkxt に別名で添えてあることを README に書く。
- **点検で分かったことで、変えなかったもの**: 取り置きの抽選の手順（seed と方法）は事前登録で公開済み（OSF の英語版の草案）なので、README にも書く。CS1 の 1 課題の期間（36.1 日）・取り置きの 1 人の生の記録の形（deviation-1.md）は、研究者が入れてよいとした実験の記録の中身なので残す。
- **研究者に伝えること**: OSF の登録 mrkxt には `frozen-files-63885bad.zip`（manifest の全ファイル＝ADR-030 と .steering の草案を含む）が公開で添えてある（notes.md 126 行）。登録の添付は凍結されている。扱いは研究者が決める（私は OSF を触らない）。
- **私の誤り**: 判断 1 で、manifest の照合を通すために GSE の内部文書を入れる案を推奨にした。照合は SHA-256 と OSF の公開ファイルで示せたので、その形を先に出すべきだった。memory に記録した（feedback-public-repo-no-steering-gse-docs）。
- **影響範囲**: `assemble.sh` の一覧・公開 repo の README・tools。

## 判断 3: security-checker と /cross-review（Claude と Codex）の指摘への対応（2026-11-07）

- **実行**: security-checker（公開物の全体）と cross-reviewer（新しく書いた tools・README・LICENSE-docs・CITATION.cff・assemble.sh。Codex は走った・約 35k トークン・台帳に記録）を並列。HIGH は両者一致の 1 件。
- **直した**:
  - 両者一致（HIGH）: `check_release.py` が存在しない root で「0 files・0 findings」の緑になり、UTF-8 で読めないファイルは中身を見ずに通していた。root が無い・検査するファイルが 0 件は 2、UTF-8 でないファイルは見つけたとして扱う。
  - 両者一致: `assemble.sh` が、別の checkout や古いコミットで一部しか写さなくても 0 で終わっていた。ディレクトリごとの件数が 0・必須のファイルが無い・シンボリックリンク（mode 120000）・来歴の行が空なら止める。出力先の検査を作る前に行い、`pwd -P` で実パスを比べる。
  - security のみ（MEDIUM）: 最初のコミットの committer が Mac のユーザー名とホスト名（`.local`）になっていた（amend で `-c` を付けなかったため）。repo の設定に名前とメールを入れて付け直した。検査も git のコミットの author・committer・本文を見て、手元のパス・`.local` のホスト・id・秘密を探すようにした。未コミットの変更があれば見つけたとする。
  - security のみ: 表の形の検査が広すぎた穴（数の配列・辞書の配列・任意の形のキー・Markdown と TeX の表）。いまの中身の最大（辞書の配列 26 件・キー 25 個・表 20 行未満）を測ってから、30 件以上を見つけたとする。秘密の形を足した（`github_pat_`・Slack・Google）。ハッシュは 8 桁以上の前置きで照合する。`target` などを名前でどこでも飛ばすのをやめ、git の追跡済みと未追跡（ignore を除く）を見る。`.gitignore` にデータの拡張子を足した。
  - Claude のみ: 陽性対照が終了コード 1 だけを見ていた（例外で落ちても通る）。期待する `FOUND` の行を確かめる。検出器ごとに 1 件ずつ混ぜる（27 件）。対照は `git archive HEAD` の写しで回す（コミットした中身を検査する）。`verify.sh` の Rust の版（1.85→1.88）と、図の照合を verify に入れた。README の検査の書き方を「形の検査・意味は見ない」に限り、estimator の README が CC BY であることを書いた。
- **採らなかった**: Codex の「age の鍵の形が自分に当たる」（cross-reviewer がフィルタを通すために 1 行を置き換えたことによる偽陽性。実ファイルは実行時に組み立てていて当たらない）。KLiCKe の数字の id を本文の中から探す案（数字は数え上げと区別できない。表の形の検査で拾う）。
- **研究者に確かめること**: 最初のコミットの本文の `Claude-Session:` の行（共有すれば会話が見える）を公開する前に外すか。取り置きの抽選の手順を README に書くこと（事前登録で公開済み・データを持つ人は引き直せる）。experiments の記録の中の ADR の要旨と GSE の内部の言葉（研究者が実験の記録は入れてよいとした範囲）。
