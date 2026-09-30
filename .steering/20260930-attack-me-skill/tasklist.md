# tasklist —— attack-me skill

- [x] /start-task: 研究者に 4 問（立場の査読者・作って軽く検証・名前 attack-me・Codex は既定で加えない）→ requirement.md
- [x] design.md
- [x] `.claude/skills/attack-me/SKILL.md` を書く
- [x] empirical-prompt-tuning（Iteration 0 ＋ Lite 1 シナリオ・3 iter: ○ 6.5/7 → × 6.5/7 → ○ 7/7）→ 不明瞭点を潰す差分（`tuning.md`）
- [x] `CLAUDE.md` の研究トラック Skill の表に 1 行
- [x] commit ＋ push（★ PR は出さない —— 研究者の指示: 次のセッションのタスクが終わった後にまとめて出す）
- [x] 引き継ぎ（`.steering/_handoff/next-session-ime-paper-after-merge.md`）に、この枝の PR を次のタスクの終わりに出すことを書く
- [ ] ★ 次のセッション: 次のタスクが終わった後に、この枝の PR → CI 緑なら merge → main の CI（git-workflow ルール 6）
  - [x] 2026-10-01（G-GEAR）: 次のタスク（IME の M0）は Mac で終わり main に入った（PR #278）→ origin/main を取り込み（`211e51b1`・衝突 1 件 = IME の tasklist の PR #276 の行・両側の事実を 1 行に）
  - [x] 完了時レビュー 1 巡目: code-reviewer ∥ security-checker ∥ Codex（パス限定・30,667 トークン）→ HIGH 5 件（重なりを除く）ほか。すべて一次で裏取りし、偽陽性 1 件（部分）→ 判断 1 で直した（`paper-reviewer` の新設ほか）
  - [x] empirical-prompt-tuning iter 4（改訂後の文面・Lite・同じシナリオ）→ `tuning.md`（○ 8/8・不明瞭点 7 件を文言で潰した）
  - [ ] 完了時レビュー 2 巡目（直した規則の境界条件）
  - [ ] PR → CI 緑なら merge → main の CI
- [ ] ★ 最初の実戦: IME 論文の M3 の事前登録の下書き（stage `prereg`・凍結の前）
