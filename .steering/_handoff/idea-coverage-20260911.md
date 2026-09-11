# `.idea/` 読解カバレッジ表（2026-09-11 時点）

> ⚠️★★★ **このファイルの目的は「どこをまだ熟読していないか」を追跡可能にすること。**
> ★ `_survey-*.md` は **索引**であって **原本の代替ではない**。
> ⚠️ 実際に 2026-09-11 の調査で、`20260908`（48KB・40 見出し）を 250 行に要約した結果、
> **§5（新規性・貢献候補）/ §6（先行系譜）/ §9（評価と反証）が丸ごと落ちた**。
> 掘り直して初めて出てきた。**同じことが実行セッションでも起きる。**

## ★ 運用ルール（これをタスクの作業項目に入れる）

1. **issue を実行するとき、該当する `.idea` の該当節を原本で読む。**
   `_survey-*.md` だけで書き始めない。
2. 原本を読む前に `grep -n "^#\{1,3\} " <file>` で**見出し一覧を出し**、
   `_survey` がどの節を拾い、どの節を落としているかを**突き合わせる**。
3. 落ちている節に判断材料があれば、**その場で読むか、survey subagent に節を指定して投げる**。
   ⚠️ subagent に投げるときは **「節を指定する」「要約しすぎるなと明示する」「行数制限を意識させる」**
   の 3 点を守る（この 3 つを欠いた最初の調査で中身が落ちた）。
4. 読んだ結果このカバレッジ表を更新する。**熟読済みの節に印を付ける。**

## カバレッジ表

凡例: ✅ 深掘り済み（原本の該当節を通読）／ 🔶 要約のみ（★ **原本の熟読が要る**）／
⬜ 未読／ ➖ SSOT 化の対象外

| ファイル | KB | 状態 | 調査結果の保存先 | 担当 |
|---|---:|---|---|---|
| `20260801-architecture-signal-and-online-learning.md` | 28 | 🔶 | — （「ADR-008/009 ＋ `personalization-and-online-learning.md` へ昇格済み」と報告されたが**未検証**） | T3 |
| `20260801-behavioral-context-online-latent-ml-design.md` | 24 | 🔶 | 同上 | T3 |
| `20260801-self-hosted-runner-setup.md` | 10 | ➖ | CI / セルフホストランナーの運用メモ。`public 化をやめる` 判断のみ記録価値あり | — |
| `20260806-media-self-reflection-and-behavioral-intervention.md` | 45 | ✅ | `20260911-practice-portrait-ssot/_survey-20260806-and-20260810-expression-and-sound.md` | T4 |
| `20260810-media-expression-sound-and-prototyping.md` | 55 | ✅ | 同上 | T4 |
| `20260819-smartphone-computational-media-channel.md` | 29 | 🔶 | — （★ **本文自身が 2026-08-30 に「本メモの論点は SSOT へ昇格した」と明記**し、無効化の対照表を付けている。優先度低） | T4 |
| `20260819-user-validation-workspace-behavior-and-mhd.md` | 22 | 🔶 | — （★ 本文自身が「2026-08-21/23 の自己追記でほぼ全節が ADR-009/012/013/014 と一致」と確認済み。**残 open item 5 件**のみ） | T3 |
| `20260901-smartphone-state-externalization-and-physical-return.md` | 54 | ✅ | `20260911-mhd-inference-ssot/_survey-20260901-externalization.md`（★ **T4 からも参照**） | T3/T4 |
| `20260905-data-to-social-media-expression-theory.md` | 8.8 | ✅ | — （★ **昇格保留が確定**。本人が明記 ＋ 後続メモへの波及なしを grep で確認済み・0 件） | — |
| `20260907-resumption-outcome-and-attention-sensitive-expression.md` | 9.8 | 🔶 | — （W-2 は ADR-027 が閉じた。★ **用語改訂提案が残る**） | T4 |
| `20260908-measurement-terminating-practice-portraiture.md` | 48 | ✅ | `_survey-20260908-claims-and-evaluation.md` ＋ `_survey-20260908-form-and-os-constraints.md` | T4 |
| `20260909-content-evanescent-context-portraiture.md` | 63 | ✅ | `_survey-20260909-content-and-pigment.md` | T4 |
| `20260909-physical-foreground-flip-cover-media.md` | 14 | 🔶 | — （★ ハードウェア試作 = **D 区分**。ADR の粒度ではない） | T4 |
| `20260909-pigment-fluid-practice-portrait-synthesis.md` | 14 | ✅ | `_survey-20260909-content-and-pigment.md` | T4 |
| `20260910-mhd-criterion-practice-trace-and-g-o-validation.md` | 20 | ✅ | `_survey-inference-architecture.md` | T3 |
| `20260910-mhd-feature-work-behavior-literature-gap-survey.md` | 35 | ✅ | `_survey-inference-architecture.md` | T3 |
| `20260911-mhd-growth-personalization-and-gse-overview-roadmap.md` | 18 | ✅ | `_survey-inference-architecture.md` | T3 |
| `memo.md` | 0.1 | ✅ | ポインタのみ | — |
| `短縮版リンク集.md` | 3.5 | ➖ | URL 短縮リンク集（Phase1 のフォーム等） | — |
| `秘密保持契約書_草案.md` | 3.6 | ➖ | NDA 草案（法務文書） | — |

**SSOT 化の対象 = 20 本中 14 本**（➖ の 3 本と `memo.md` を除く）。

## ⚠️ 熟読が残っているもの（🔶 6 本）

| ファイル | なぜ残っているか | 優先度 |
|---|---|---|
| `20260801` ×2（52KB） | 「昇格済み」と**報告されただけで検証していない**。★ T3 で `personalization-and-online-learning.md` へ統合する際、**何が既に昇格済みで何が落ちたか**を確かめる必要がある | **中**（T3 の着手時） |
| `20260819-user-validation`（22KB） | 本文が自己申告で「ほぼ決着済み」。残 open item 5 件（同意粒度 / L-d feasibility / vibe_coding 段 2 判定量 / 6 段 ablation 事前登録 / Research・web Adapter）＋ `KeyCategory` の `Punctuation` 追加要否（★ **これは既に main にマージ済みで解決**） | 低 |
| `20260819-smartphone`（29KB） | 本文が「SSOT へ昇格した」と明記し無効化対照表つき | 低 |
| `20260907`（9.8KB） | W-2 は ADR-027 が閉じた。**用語改訂提案**（`physical return` → `self-chosen pause and resumption opportunity` 等）が残る | 中（T4） |
| `20260909-physical-foreground`（14KB） | D 区分（ハードウェア試作）。ADR 粒度でない | 低 |

## ⚠️ 調査の失敗から学んだこと（次に survey を投げるとき）

1. ⚠️ **ファイル単位で投げると中身が落ちる。** 48KB を 250 行に要約させると 40 見出し中 9 節しか残らなかった。
   → ★ **節（行番号つき）を指定して投げる。**
2. ⚠️ **「未 SSOT 論点の抽出」という観点で投げると、設計の中身が 1 行に潰れる。**
   → ★ **「要約しすぎるな」「命題・数値・引用番号・固有名はそのまま残せ」と明示する。**
3. ⚠️ **報告の行数制限が実質の情報量制限になる。** 300 行と言えば 300 行に圧縮される。
   → ★ **大きいファイルは 2 本以上の subagent に分けて投げる。**
4. ⚠️ **subagent の報告をチャットに流すと、次セッションで失われる。**
   → ★ **必ず `.steering/<task>/_survey-*.md` に保存する。**
5. ⚠️★★★ **指示に書いた「前提」自体が間違っていることがある。**
   → ★ **subagent には「前提が違ったら訂正せよ」と含みを持たせ、報告に一次確認の結果を書かせる。**
   実際 2026-09-11 の深掘りで、こちらが渡した前提の誤りが **2 件**見つかった:

   | 誤っていた前提 | 実際 |
   |---|---|
   | 「ADR-017 D5 が**音声全体**を Phase1 範囲外と決着させた」 | ⚠️ D5 が範囲外とするのは「**音声の自動開始**」限定。★ PC 画面内ドローン（案 α）は **D21 で採用済み**。→「範囲外だから SSOT 化不要」という理由づけが**成立しない** |
   | 「`.idea/20260806` に `[P75] Bodner & Prelec` と `moral placebo effect` がある」 | ⚠️ **そのファイルには一切登場しない**（grep 0 件）。本文は「自己シグナリング」の語だけを使い「**出典が GSE の書誌に存在しない・次ラウンドの候補**」と自己申告。`[P75]/[P76]` は**後続の `references.md` 追補 4** で追加された |

6. ⚠️★★★ **`.idea` の「未決」表記は古いことがある。**
   `20260810` は α/β/γ を「未決」と書いているが、⚠️ **同じ `.steering` の `decisions.md` D21 で
   α 採用・β は比較条件・γ は層 3 へ吸収と確定済み**。
   → ★ **`.idea` の未決を見たら、必ず後続の `decisions.md` / ADR を確認する。**
