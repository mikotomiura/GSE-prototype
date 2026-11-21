# design — p321-paper-revision（v1・/reimagine の前の初回案）

## 0. 前提（一次で確かめた・判断 11 と 2026-11-21 の追記）

- 出し先は JSS。JSS の投稿ガイド（`sciencedirect.com/journal/journal-of-systems-and-software/publish/guide-for-authors`・Chrome で読んだ・逐語）:
  - LaTeX: "We encourage you use our LaTeX template when preparing a LaTeX submission. You will be asked to provide all relevant editable source files upon submission or revision." → elsarticle は**勧め**で、必須ではない。
  - 形式: "Submit files with .doc/.docx extensions for Word and .tex for LaTeX files. A PDF is not an acceptable source file." ・ "Double-column formatting is only permitted for LaTeX submissions."
  - 要旨: "does not exceed 250 words"（いまの要旨は 234 語の 1 段落 ＋ マクロ。展開後の語数は組んだ PDF で数える）。
  - Highlights: "You are required to provide article highlights at submission." ・ "3 to 5 bullet points, each a maximum of 85 characters, including spaces." ・ 別のファイル（名前に "highlights"）。
  - キーワード: "1 to 7 keywords"（いまは 6）。
  - 生成 AI: "Authors must declare the use of generative AI tools in the manuscript preparation process upon submission of the paper." ・ 文献表の直前の新しい節 "Declaration of generative AI and AI-assisted technologies in the manuscript preparation process"。⚠️ 著者の責任の項に "Editing and adapting all material thoroughly to ensure the manuscript represents the author's authentic and original contribution and reflects their own analysis, interpretation, insights, and ideas." → **研究者が原稿を自分で読み、手を入れる時間**を工程に置く（§3 の段 6）。
  - データ: "Option C … Deposit your research data in a relevant data repository. | Provide a link to the dataset during the submission process."
  - Open Science Initiative: 採択の後に Open Science Board（"chaired by Christoph Treude"）が "availability and usability" を審査し、"which does not affect acceptance of the paper"。
  - 範囲: "All articles should provide evidence to support their claims, e.g. through empirical studies …" ・ "The journal welcomes reports of practical experience for all of these topics, as well as replication studies and studies with negative results."
- ⚠️ **JSS でも査読に回らないことがある**: 編集者の論考 arXiv 2601.19217v2（Menzies, Avgeriou, Feldt, Pezzè, Roychoudhury, Staron, Uchitel, Zimmermann・PDF を pypdf で読んだ）の逐語 "JSS decided in 2025 to establish a cap of 20 review invitations per submission. If this limit was reached, the submission was assumed to not fit the scope of the journal, and was desk-rejected." → 査読者が集まりやすい形にする（題・要旨・キーワードで分野を明確に・投稿画面で査読者を推薦できるなら推薦の候補を用意する）。
- D1 の元データのライセンス（`DATA.md`）: "CC BY 4.0 … (shown on both figshare item pages)"。→ 判断 8 の派生表の再配布は、帰属表示をすれば許される見込み（⚠️ figshare のページを実装の段で Chrome で読み直す）。元データは公開の動画とリポジトリの URL をセッションごとに含む（`DATA.md`）→ 派生表は episode 単位の符号と時刻だけにし、URL・配信者の名前を入れない。
- 原稿の分量: `main.tex` 401 行・約 8,600 語・表 5・図 0・参考文献 21。

## 1. 変える場所

| 場所 | 何を |
|---|---|
| 論文用リポジトリ `C:/self-resolution-measure`（`main` から作業ブランチ `revision-jss`） | `analysis/`（感度・区間・算術）・`config.json`・`results/`・`paper/`（原稿・組版・自己検査）・`NOTES.md`（凍結の後に足したものの記録）・`README.md`・`DATA.md` |
| GSE の作業記録 | `.steering/20261121-p321-paper-revision/`（判断・tasklist・照会の文面・検索の手順と結果） |
| repo の外 | 照会の文面（研究者が送る）・JSS の投稿画面の文（研究者が入れる）・Zenodo の下書き |

⚠️ 公開する成果物（論文用リポジトリ・Zenodo）には GSE への言及を入れない（memory `feedback_public_artifacts_academic_no_gse`）。

## 2. 方針の柱

1. **凍結を壊さない**: 既存の `results/metrics.json` のキーと値は 1 つも変えない。足す解析はすべて新しいキー（`sensitivity/…`・`interval_alt/…` など）にし、`NOTES.md` に「凍結の後に足した（post hoc）」と理由つきで記録する。原稿でも、凍結した解析と後から足した解析を書き分ける。→ 検査: 改訂の前後で、既存のキーの値が byte 一致することを `make_results.py` の自己検査に足す。
2. **数字は機械生成だけ**: 本文の数字はすべて `results.tex` のマクロから出す（いまと同じ）。足した数字にも、`make_results.py` に質的な主張の検査（例:「DF3 を除くと R0 − R0′ は 3pp 未満」）を足す。
3. **外延を絞る**: 主張の範囲を、データが支える所まで下げる（A の上限としての読み・B の実例の有無・C の名前）。
4. **組版は elsarticle に移す**（★ /reimagine で比べたい分かれ道）: CTAN にあるので Tectonic が自動で取れる。これで Springer の zip とハッシュの検査（`build.sh` Step 1）が要らなくなり、cls の再配布の問題（前タスク判断 19）も消える。
   - 却下しうる案: sn-jnl のまま出す（JSS は template を勧めるだけなので通る。差分は最小だが、Springer の体裁の原稿を Elsevier に出すことになる）。

## 3. 段の順序（v1）

| 段 | 何を | 誰が | 依存 |
|---|---|---|---|
| 1 | 外に出るものを先に出す: 原著者への照会の文面（G）→ 研究者が送る ／ 誤読の実例の検索の手順（B）を決める | 私 → 研究者 | なし |
| 2 | 調べもの（並列・サブエージェント）: B の検索 ／ クラスタが少ないときの区間の手法（H）／ 先行研究の系統（F） | Sonnet の汎用エージェント ×3 → 私が一次で裏取り | 段 1 の手順 |
| 3 | 解析を足す（論文用リポジトリ）: A の感度 3 通りと [R0′, R0]・D1 の DF3 の位置と k ／ H の補助の区間 ／ I の P1TA の感度 ／ M の時間で重みをつけた版 ／ G の報告値どうしの算術 ／ K の派生表 → `run.sh` 緑・既存のキーは不変 | 私 | 段 2 の H の手法 |
| 4 | 本文を直す: 用語をそろえる（C）→ 題の案 2〜3 本 → 研究者が選ぶ ／ 要旨を 250 語以内 ／ 節ごとに major・minor を反映（下の対応表）／ 提言を受け手別にし、2×2 表を最小の報告形式に（J）／ LLM の節（E）／ 生成 AI の申告の節・声明・Data availability | 私（題は研究者） | 段 2・3 |
| 5 | 組版を elsarticle に移す ／ Highlights のファイル ／ `build.sh` に検査を足す（要旨の語数・Highlights の字数・既存のキーの不変）→ `build.sh` 緑 | 私 | 段 4 |
| 6 | 研究者の通読と手入れ（JSS の生成 AI の規程が求める）| 研究者 | 段 5 |
| 7 | attack-me round 2（席は JSS の読者に合わせる: 測定の妥当性・debugging の行動研究・再現性）→ 研究者が採否 → 直す | 私（Opus の paper-reviewer ×4） | 段 6 |
| 8 | `/cross-review`（論文用リポジトリの差分を GSE の worktree に fetch して範囲指定）→ 裁定 | 私 | 段 7 |
| 9 | 出す: 新しいタグ（`submission-jss-YYYY-MM-DD`）・Zenodo の新しい版（再現一式 23029603 の new version）・Zenodo のプレプリントの下書き → 研究者が publish → 研究者が JSS に投稿（照会の返事は待たない・2 週間が目安） | 私 → 研究者 | 段 8・段 1 から 2 週間 |

## 4. 指摘と直す場所の対応（verdict §5）

| 指摘 | 節 | 段 |
|---|---|---|
| A 打ち切り | §5.2・§6.1・§6.2・§8 Threats・要旨・結論 | 3・4 |
| B 誤読の実例 | §1・§2.5・§7 | 2・4 |
| C 名前と題 | 題・要旨・§3 全体・本文の用語 | 4 |
| G RQ4 | §6.4・§7.4・§5.3 | 1・3・4 |
| E LLM | §5.5・生成 AI の申告の節 | 4 |
| H 区間 | §5.2・§8・表 2 | 2・3・4 |
| I D2 の転用 | §4.2・§8 | 3・4 |
| F 先行研究 | §2 | 2・4 |
| J 提言 | §7.3 | 4 |
| K 入力のアーカイブ | Data availability・`DATA.md`・`README.md` | 3・9 |
| minor・nit（§5 の列挙） | 各所 | 4 |

## 5. テスト（受け入れの検査）

- `bash run.sh` が exit 0（入力のハッシュ・自己検査）。
- `bash paper/build.sh` が exit 0（未定義の引用・参照 0・`results.tex` が新しい・質的な主張の検査）。
- 足す検査（`make_results.py` か `build.sh`）: (1) 既存の `metrics.json` のキーの値が改訂の前と byte 一致（基準はタグ `submission-2026-09-29` の `results/metrics.json`）(2) 要旨が 250 語以内（組んだ PDF から数える）(3) Highlights が 3〜5 項目・各 85 字以内 (4) キーワードが 1〜7。
- 陰性対照: 各検査が、わざと壊した入力で赤になることを一度ずつ確かめる（memory `feedback_acceptance_self_test`）。

## 6. 研究者に決めてもらうこと（段の途中で）

- 題（段 4）・Open Science Initiative への参加（段 9。私の推奨は参加）・照会を送る時期（段 1）・round 2 の指摘の採否（段 7）・推薦する査読者（JSS の投稿画面にその欄があれば・段 9）。
