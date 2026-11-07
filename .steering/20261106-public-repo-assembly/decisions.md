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

## 判断 4: 公開（GitHub・Zenodo）と原稿の直し（2026-11-07）

- **研究者の採否（AskUserQuestion）**: GitHub に公開の repo を作って push する／公開 repo のコミットの本文から `Claude-Session:` の行を外す／Zenodo の DOI は私が Chrome で取る／Zenodo が CITATION.cff を読めないときは `.zenodo.json` を置く。
- **公開**: <https://github.com/mikotomiura/stall-runup-equivalence>（v0.1.0 = b3bdc9a）。Zenodo: 全版 10.5281/zenodo.24014042・0.1.0 は 10.5281/zenodo.24014043（ライセンスの表示は MIT。2 つめ以降の許諾は notes と LICENSE-docs）。Zenodo の zip（770,841 バイト）を取り、`git archive v0.1.0` とファイル単位で同じこと・漏れの検査が 0 件（取り置きの一覧つき）を確かめた。GitHub の README と 2 つの図（動く図を含む）の表示を Chrome で確かめた。
- **Zenodo の失敗 4 回**: GitHub 連携が CITATION.cff を読めず "Citation metadata load failed"（理由は示されない）。cffconvert では 4 回とも規格どおり。試したのは references を外す・ライセンスを 2 つに・公開日を UTC に（当時 UTC はまだ 11-06）。4 回で止めて研究者に聞き、`.zenodo.json` を置いて 5 回目で公開された。原因は特定していない。失敗の 4 件は Zenodo の連携の画面に残る（公開物ではない）。
- **原稿の直し**: 要旨の置き字を DOI に（要旨は texcount で 300 語）。Materials を「archive（DOI・version 0.1.0）に、評価・探索・変換のコード、seed・環境・manifest、先にコミットした条件と集計の結果、版を固定した推定器と replay（見た書き手の全呼び出しでバイト一致の門つき）」に。限界の「推定器が公開できなければ外から再現できない」を「ファイルを得て公開のコードと推定器を回し直せば再現できる」に。補足の係数の節の「公開しない」を「archive で公開」に。`papers/public-data-findings/README.md` の「置き場は未定」を DOI に。組むと誤り 0・overfull 1（直す前と同じ。2 つの URL を並べた版は 2 になったので 1 つに戻した）。
- **公開 repo の paper/ は直す前の版**（v0.1.0 の写し）。原稿を次に直して出すとき（attack-me round 3 の後など）に、assemble.sh で写し直して版を上げる。

## 判断 5: 版 0.2.0（取り置きを再計算する入口・条件の英語の要約・原稿 v4）（2026-11-07）

- **背景**: attack-me manuscript round 3 の B（Materials の再現の約束が公開物の実体より強い・3/4）と Codex 1（独立再実行の入口が無い）。研究者の採否は論文の判断 38 (4)（条件の英語の要約と、取り置きを再計算する入口を公開物に足す）。
- **足したもの**: `tools/rerun-holdout.sh`（`run-confirm-holdout.sh` と同じ段を、著者の実行だけが通れる git の履歴と OSF の記録の検査を除いて回し、`confirm_holdout.json` が公開のものとバイト単位で同じときだけ 0）・`tools/rerun_confirm.py`（変えていない `confirm_p1.py` を呼び、`holdout_gate` だけを外す）・`docs/conditions-summary.md`（条件の文書すべての英語の要約・最初のコミットの時刻つき・正本は日本語。サブエージェントが書き、内部の語が無いことと漏れの検査 0 件を確かめた）・`experiments/20261107-findings-paper1-round3-checks/`・原稿 v4（`paper/`）。README（英・日）は題・要約へのリンク・表 6（S4 節）・再計算の節・門の範囲（CS1 2019・KLiCKe・CoAuthor。2021 と陽性対照は比べていない）を直した。CITATION.cff と `.zenodo.json` は版 0.2.0・題・要旨（"matched" を外す）。LICENSE-docs に要約と `.zenodo.json` を足した。
- **再計算の結果**: 公開した推定器（`estimator/` から組んだ `gse-replay`・SHA-256 1839c83e…3e80b・macOS arm64・並列 4）で回し、`confirm_holdout.json` は公開のものとバイト単位で同じ（3a73346f…72018）。1 回目は selftest で止まった（`OMP_NUM_THREADS=1` が要る）ので、スクリプトで export するよう直した。
- **検査**: `tools/verify.sh ~/gse-public-data` が 0（manifest・cargo test 228 件・provenance・図の照合 18 行・漏れの検査 211 ファイル 0 件・陽性対照 27 件）。原稿は誤り 0・overfull 1（前と同じ・補足の 2 pt）。
- **公開（研究者の採否・AskUserQuestion）**: push して release を作る／原稿は出してから版の DOI に差し替える。main = e9a595a（v0.2.0）→ 29464a6（DOI を README と CITATION に）。Zenodo: 0.2.0 は 10.5281/zenodo.24025183（zip 802,068 バイト・MIT・OSF の 2 件）。公開 repo の `paper/` の DOI は 0.1.0 のまま（その版の DOI は版の中に書けない）。次に版を上げるときに写し直す。
