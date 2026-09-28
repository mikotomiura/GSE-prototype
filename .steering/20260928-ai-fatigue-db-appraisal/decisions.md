# 判断記録

## 判断 1: 出力は「元と同じ列構成の評価版シート」を追加した別ファイル（2026-09-28・研究者の確認）

- 研究者（逐語）: 「出力としては, 具体的な評価結果とこの, 我々用で同じ形での具体評価版のスプレッドシートを作成する感じにする？」
- 採用: 元 16 シートは不変のまま、既存 AI 評価と**同じ列順**の自前シート（右端に列を追加）を足した別名ファイル。
- ⚠️ スクリーニングの判定者列は、見出しを「Claude 予備判定（…段）」に変えて人間の判定者欄と区別する（★ 元ワークブック逐語「判定者1・2は独立した人間の担当者を想定し、AIの予備整理を独立判定に数えません」）。選択肢の語彙（未判定／含める／除外／保留 ほか）は元の入力規則と同じにする。

## 判断 2: repo 内にアーカイブする（2026-09-28・研究者の確認）

- 研究者（逐語）: 「このスプレッドシートなどが有益であれば, 一応このディレクトリ内にアーカイブに近い感じで保管しとく？」
- 置き場所: `.steering/20260928-ai-fatigue-db-appraisal/archive/`（入力スナップショット・評価版・抽出ノート・検索ログ・README＋SHA-256）。
- ⚠️ `papers/`（公開する論文の成果物）には置かない —— GSE 照合列を含むため（memory「公開する論文の成果物は GSE への言及なし」）。
- ⚠️ コミットは `feature/ime-eval-kit`（無関係の作業ブランチ）ではなく、main から切った別ブランチで行う。

## 判断 3: AF006 と AF007 の標本の独立性 —— 算術照合で強い手がかり（メインが一次 PDF で確認）

- 一次（AF006 PDF・DOI 10.26803/ijlter.25.3.29・Table 3、メインが pypdf で開いて確認）:
  `Cognitive fatigue 472 44.8% / Motivational fatigue 311 29.5% / Emotional fatigue 289 27.4% / No fatigue expression 418 39.7%`、抄録は「1,000 open-ended online survey responses」。
- 算術: ÷1000 なら 47.2 / 31.1 / 28.9 / 41.8%。**÷1054 なら 44.78 / 29.51 / 27.42 / 39.66% で 4 つとも表の値に一致**。
  1054 は AF007（同じ著者群・DOI 10.26803/ijlter.25.5.5）の解析 N（抄録逐語「open-ended responses from 1,054 university students」）。
- 一方 Table 5 の注「582 responses that contained at least one fatigue dimension」は 1000 − 418 = 582 で N=1000 と整合 → **件数は 1000 基準・百分率は 1054 基準**という分母の混在。
- 解釈の幅（★ 断定しない）: (a) 1,054 件の回収から実質的内容のない回答を除いて 1,000 件にし、百分率だけ回収数で割った（AF006 は除外件数を書いていない）／(b) AF007 と同じ回収データを使っている。どちらでも「AF006 の百分率は表記どおりではない」ことと「AF006・AF007 を独立標本として数えない」ことは言える。
- 扱い: E5（重複）は**確立していない**ので除外しない。両方 `含める` とし、統合時は同一標本の可能性として 1 つに数える。照合事項 C 番号で起票。⚠️ 研究不正の認定ではない。

## 判断 4: AF008 の疲労は AI に帰属させて定義されている（メインが一次 PDF で確認）

- 一次（AF008 PDF・Table 1）: 「General fatigue levels — The overall physical and mental exhaustion experienced from prolonged or frequent AI use. 3 / Likert scale / [35], [36]」。
- → 既存 AI 評価（「一般疲労等の指標…AI に特異的な疲労の測定とは限らない」）とは異なる。**構成概念の定義は AI 帰属**。ただし項目文は本文に無い（`記載なし`）ので、項目レベルで AI 帰属かは確かめられない。→ プロトコル §2 の「定義に AI が明示される」に当たり **中心-A**。
- 同じ Table 1 の項目数の合計は 2+3+3+2+3+3+2+3+3 = **24**、本文は「The survey instrument consisted of 36 items, with 31 items adapted from existing validated studies (Table 1)」→ 12 項目の食い違い（照合事項で起票）。
- クラス数: Table 3 で BIC 最小は k=8（4673.59）、採用は k=6（5268.31・最小クラス 3.61% = 14 人）。★ **k=5（5183.44）も k=6 より BIC が低い**（既存 AI 評価は 8 群との比較だけを挙げていた）。
- ★ 追加（メインが Table 3 を PDF で確認）: BIC−AIC＝p(ln 388−2) から p を逆算すると 1 成分あたり 55（9 変数の完全共分散）で整合。−2LL＝AIC−2p は k=3 4390.9 → k=4 4539.4、k=8 2056.7 → k=9 2338.8 と増えている＝成分を増やして最大尤度が下がっている → **k=4・k=9 の解は最大尤度解ではない**（局所解）。他の k の解の良否はこの算術では言えない。

## 判断 5: 研究者の追加許可で、ブラウザ経由で本文を取り込んだ（2026-09-28）

- 研究者（逐語）: 「必要に応じて文献や論文本文などはダウンロードしてから取り込んでもよいよ」
- スクリプトからは CAPTCHA・403 で止まった ScienceDirect／Springer のページを、`browser-verification` Skill を読んだうえで Chrome から読んだ（`javascript_tool` と `get_page_text` のみ・スクリーンショットなし・フォーム送信なし・タブは閉じた）。
- 取り込めたもの: AF004 全文（OA）、AF034 訂正本文（OA）、AF019 全文の一部（OA）、AF002・AF003 の抄録と節の抜粋（購読制）、AF015 の抄録（受理原稿）。
- ★ 著作権: 本文・PDF はアーカイブに入れない（元 DB の方針「全文 PDF や尺度の全設問は同梱しない」と同じ）。抽出ノートの逐語は 1 引用 40 語以内。

## 判断 6: AF004 の交互作用の向きの矛盾（メインが全文で確認）

- 抄録『also amplified cognitive fatigue when AI reliance was high』・§4.3『information literacy amplifies the positive relationship between AI dependence and cognitive fatigue (β = −0.06, p = 0.025)』
- §3.4『high levels of information literacy attenuate the positive relationship』・§4.1『Contrary to earlier interpretation, the data do not suggest that higher literacy exacerbates fatigue; rather, it mitigates it.』
- 疲労尺度は MFI-20 の認知疲労下位尺度（一般疲労）→ **中心-B**。訂正通知 AF034 は参考文献 2 件のみ（本文で確認）で、この矛盾は訂正の対象外。
- ⚠️ GSE への含意: 「検証能力の高い人ほど疲れる」は返権の負荷逆説の証拠に見えるが、本論文のデータは逆向き。GSE では根拠にしない。

## 判断 7: 範囲の境界（AF019・AF024）をプロトコル §2 の規則で閉じた

- AF019: T2 の情緒的消耗（MBI-GS 5 項目）を T1 の AI テクノストレスが予測 → 中心-B（GPT は背景保持・要協議 → 唯一の用途判定の相違）。
- AF024: 題名は Learning Burnout だが、20 項目にバーンアウト・消耗・疲労を尋ねる項目が無い（サブエージェントが Wayback 全文で確認・検証担当に再照合を依頼）→ E2（区分は GPT と同じ背景だが、理由が「境界例」から「測定していない」に確定）。

## 判断 8: サブエージェント由来の主張を反証役で再照合した（偽の主張を 1 件混入）

- メインが自分で一次を開いていない主張から 9 件を選び、別のサブエージェント（Sonnet）に「誤りを探すつもりで」一次資料で判定させた。★ 検査の空回りを見るため、偽の主張 1 件（AF026 の RMSEA=.045。実際は .086）を知らせずに混ぜた。
- 結果（`archive/evidence/verify.md`）: 偽の主張は **否定**（＝検証は空回りしていない）。9 件は支持。ただし 2 件で記述を直した:
  - ⚠️ **AF005 の項目文は言い換えだった**（抽出が WebFetch の要約経由だったため）。メインが出版社 HTML で逐語を取り直した: 『Repeated verification of the authenticity of AI-generated information has left me affectively exhausted.』『Managing privacy settings and authorization requests for AI applications has left me utterly exhausted.』
  - AF017: 抽出は『one author』で、第 1 著者と同一かは明記なし（『第 1 著者のみ』を精密化）。
  - AF016: 『方向比較なし 4』は『方向比較なし 3・質的報告 1』（数は一致）。
- ★ 教訓: **WebFetch 要約経由の「逐語」は逐語ではないことがある**。引用符で示す文言は、要約を経ない取得（HTML の直接取得・PDF）で確かめる。

## プロトコルからの逸脱（design.md は書き換えない）

- **逸脱 1（出力シート）**: design §8 は `C0〜C7` の 8 シートとしたが、研究者の依頼（判断 1「同じ形」）に合わせて、元シート名に対応させた 10 シートにした（Claude評価概要／Claude適格性評価／Claude方法論評価／Claude領域別評価／Claude照合事項／Claudeスクリーニング案／Claude×GPT比較／GSE照合／検索漏れ候補／Claude評価基準）。
- **逸脱 2（領域別評価の対象）**: GPT 版の 12 件に、§2 の規則で中心-B とした AF019 を加えて 13 件にした。
- **逸脱 3（検索漏れの判定）**: §7 は「TA 段の含める候補として提案」だったが、141 件の抄録は読んでいない。判定は**題名と機械抽出の根拠語だけ**で行い、シートの説明にそう明記した。
- **逸脱 4（盲検の緩和の限界）**: 抽出担当には GPT の結論を渡していないが、AF006〜AF009・AF011・AF012 などへの**抽出の補足指示**（「分母」「倫理を本文と宣言欄で別々に」等）は、メインが既存評価を読んだ後に書いた。一般的な抽出項目として書いたが、着眼点が既存評価に影響された可能性は否定しない。
- **逸脱 5（再計算の手段）**: xlsx Skill の `recalc.py` は Windows で動かない（`socket.AF_UNIX` が無い）。LibreOffice をヘッドレスで直接呼んで**コピー**を変換し、数式 110 個の値を読んで検算した。納品ファイルは openpyxl で保存したもの（`fullCalcOnLoad=True`・Excel で開くと再計算）。
