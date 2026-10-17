# 引き継ぎ: C の外枠を詰める（見出し・背景の出典・比較の軸・TRACE の展開）→ 登録版の差分の確認 → /cross-review → 共著者への相談文

作成 2026-10-17（Mac）。返答・記録・AskUserQuestion の引数は日本語で。記号を多用しない。決めてほしいことは AskUserQuestion で、推奨と理由を添えて聞く。

## 始め方

worktree `/Users/johnd/GSE-prototype-af-c`（ブランチ `docs/ai-fatigue-c-outline`・push 済み・PR なし）で新しいセッションを開き、次を打ち込む。

```
.steering/_handoff/next-session-ai-fatigue-c-outline-finalize.md を読んで、§2 の順に進めて。
```

## 1. ここまで（一次は各ファイル）

- 外枠: `papers/ai-fatigue-measurement/manuscript/outline.md`（版 2）。抄録の見本: `manuscript/abstract-mock.md`。登録版: `.steering/20261017-ai-fatigue-c-outline/registration-en.md`（下書き 0.8）。脚本: 同 `scripts/`（make_dummy の検査は緑）。
- プレ査読: round 1 は major（判断 5）、round 2 は minor（判断 6・`attack-me/outline-c-manuscript/round-2/verdict.md` の G1〜G24 と §8）。
- 研究者が round 2 で決めたこと（判断 6）: 中心の問いは帰属を見出しにする。C7 は登録で 3 つの問題の型に分ける。C4f は表の値を含め、r・出どころ・不完全な報告の扱いを足す。登録版の GSRR-1・10・12・56・63 を外枠に揃える。
- 研究者の問いへの見立て（返答のみ・記録の主張ではない）: C は NR（問題の観察）と尺度の論文（AI 疲労の新しい尺度を作る）の間で「規則を固定した体系的な証拠」の役。尺度の論文の「なぜ新しい尺度が要るか」の根拠になる。C2b は内容的妥当性の証拠として引かない。

## 2. 次にやること（この順）

1. **見出しの確定と TRACE の展開を一緒に決める。** 帰属（C1・C7 (ii)）を前に出す言い方を、題の副題・抄録の問いの文・序論の最後の段落・寄与の前文で揃える。副題の動詞は "TRACE: Tracing" の重なりを避ける。TRACE の展開の案を 2〜3 出し、同名の有無を調べる（報告の手引き・尺度・チェックリスト）。決めたら登録版 GSRR-1 と README も揃える。研究者に AskUserQuestion。
2. **背景の文の出典**（外枠の未決の項）: 「AI 疲労の研究が増えている」「既存のレビューが、妥当化の証拠の無い尺度と構成概念の境のあいまいさを指摘している」。登録版 GSRR-10 の同じ文にも付ける。無料の一次で照合したものだけ（citation-ssot・次は P528）。NR の草稿が引く既存のレビュー（Ragolane & Patel 2025 ほか・`overlap-narrative-review.md` の「確かめていないこと」）が候補。
3. **比較の軸の文献**: AI に関わる構成概念の測定の実践を数えたレビュー（候補: Bach et al. 2022・信頼）と、statcheck 型の再計算を心理学の外で使った先例。Flake & Fried 2020 [P527] の本文の照合（PsyArXiv doi:10.31234/osf.io/hs7wm。2026-10-17 は OSF が 503）。照合したら provisional を active に。
4. **残りの箇所の修正**: 上の 1〜3 で変わる外枠・登録版・抄録の見本の語数（見出しを変えたら数え直す。上限 250 語・余裕は約 3 語）。
5. **登録版 0.8 の差分の確認**: prereg の attack-me（`.steering/20261017-ai-fatigue-c-outline/attack-me/prereg-c-registration/` round 1〜3）の後の変更なので、差分（`git diff e9629d8d -- .steering/20261017-ai-fatigue-c-outline/registration-en.md`）をどう確かめるかを研究者に問う（推奨の案: prereg の round 4 を差分だけに絞って回す）。
6. **/cross-review**（必須）: 外枠・登録版・脚本の diff。Codex の予算（`.codex/budget.json`・origin/main の台帳）を先に確かめる。送るのは公開予定の文と脚本だけ（NR の草稿・`.steering/` の内部の判断は送らない）。
7. **共著者への相談文**: 研究者が共著者に送る文の下書き（送るのは研究者・私は連絡しない）。中身の案: narrative review の著者・引き方（公刊 / 前刷り / 未公刊）・C との関係の書き方、C の見出し（帰属）、著者 2 の情報（名前・所属・ORCID）、coder 2 を引き受けられるか（GSRR-44）、投稿先の候補。形は .docx（pandoc。予備に LibreOffice の `soffice`）。原稿の草稿を組むなら MacTeX。

## 3. 守ること

- 結果を先取りしない。尺度の項目を逐語で公開物に載せない。GSE の話を混ぜない。
- 公開物（`papers/`）は英語・内部の番号やパスを書かない。`.steering/20260927-ime-observation-paper-eval-design/issues/_style_check.py` で違反 0 件を確かめる。
- 出典は citation-ssot（append-only）。断定に使う一次はメインが開く。
- `git add -A` を使わない。PR は研究者が確かめてから（push で止める）。
- attack-me の round 2 の `tmp/`（接地の本文）は、研究者が最後の round の採否を決め終えたら消す。
