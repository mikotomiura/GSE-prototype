# 本文中の外部情報源参照（Table 5 の 3 行との対応関係に関わらず全て列挙）

各項目: task_id / 逐語引用（頁ラベル） / Table 5（documentation・social-technical・web の
いずれか）に既に挙がっているか

1. **P7TA** — Table 1 の分析例に付されたメモ本文（表そのものではなく、表の下の説明段落）:
   「However, upon a quick function inspection, the participant expressed uncertainty toward the
   function and turned to use AI as a support for debugging, relying on it as an external source.」
   (FSE049:5)
   → Table 5 に既出: **はい**（web sources: P7TA）

2. **P7TA** — 「Similarly, P7's choice of using AI to help understand and debug certain components
   of the code, ... can all be seen as efforts to avoid the never-ending effort of understanding the
   system.」(FSE049:10)
   → Table 5 に既出: **はい**（web sources: P7TA）

3. **S2TA** — 同じ文の中: 「... S2 consulting experts ... can all be seen as efforts to avoid the
   never-ending effort of understanding the system.」(FSE049:10)
   → Table 5 に既出: **はい**（social-technical sources: S2TA）

4. **P2TB** — 「In debugging task B, a packaging issue that P2's mentee had struggled with, P2
   quickly recognized the error after reproducing it (“I have seen this error before”), turned to web
   searches, and quickly found a working resolution through Stack Overflow.」(FSE049:13)
   ⚠️ 本文が明示的に「task B」と書いているため task_id を P2TB と確定した（P2 には Table 4 で
   2 task (P2TA/P2TB) あるが、本項目は開発者 ID のみの記載ではないため「特定不能」扱いにしない）。
   → Table 5 に既出: **はい**（web sources: P2TB）

5. **P2TB** — 上記と同一事象の別セクションでの言及: 「Guided by past experience with a similar
   packaging issue, P2 quickly resolved a reported bug that junior developers on the team had
   struggled with... I have experienced this before... P2 then identified the solution through web
   search. Experience enabled P2 to reduce the debugging process to a single web search.」
   (FSE049:15)
   ⚠️ このパラグラフ自体は開発者 ID (P2) のみで task 番号を書いていないが、「packaging issue」
   「junior developers ([P2's] mentee) had struggled with」という記述が項目 4 (FSE049:13, task B
   と明記) と一致するため、同一事象として task_id = P2TB と判断した。
   → Table 5 に既出: **はい**（web sources: P2TB）

6. **S1TA** — 「S1 used Claude Sonnet [5] to inquire about the struct that caused the syntax error.
   Referencing the sample code, S1 was able to fix the syntax error more efficiently than after
   longer unsuccessful attempts to consult the documentation.」(FSE049:13)
   → Table 5 に既出: **はい**（documentation: S1TA／web sources: S1TA の両方）

7. **P7TA** — 「P7 used IDE-embedded AI extensively for debugging, highlighting that exploring the
   use of LLMs was encouraged in their company.」および「Despite mentioning LLMs' power in
   working across files and web resources and providing expertise in unfamiliar fields, P7's attempts
   at using AI to generate a fix were not effective, eventually fixing the issue manually.」
   (FSE049:13)
   → Table 5 に既出: **はい**（web sources: P7TA）

8. **S3TA** と **S5TA** — 「some streamers engaged directly with chat participants to brainstorm
   solutions with viewers in real time (S3, S5). S3 identified the root cause during this interaction,
   illustrating the potential of pair programming-like collaboration in debugging.」(FSE049:14)
   - S3TA → Table 5 に既出: **はい**（social-technical sources: S3TA）
   - S5TA → Table 5 に既出: **いいえ**（Table 5 の documentation/social-technical/web sources
     いずれの行にも S5TA は挙がっていない。★ 新規の発見）

9. **S2TA** — 「Meanwhile, S2 reached out to another maintainer on Discord to ask targeted
   questions about what issue was triggered in which portion of the codebase.」(FSE049:14)
   → Table 5 に既出: **はい**（social-technical sources: S2TA）

10. **P1TA** — 「P1 similarly identified colleagues with relevant expertise and redirected the issue
    to those best equipped to resolve it.」(FSE049:14)
    → Table 5 に既出: **いいえ**（Table 5 の 3 行のいずれにも P1TA は挙がっていない。★ 新規の発見）

11. **S1TA** — 「Consulting documentation and related codebases. ... This included referring to
    syntax documentation within the IDE (S1) ...」(FSE049:14)
    → Table 5 に既出: **はい**（documentation: S1TA）

12. **S2TA** — 同じ文の中: 「... checking guides for external service integration and comparing
    them with corresponding code (S2) ...」(FSE049:14)
    → Table 5 に既出: **はい**（documentation: S2TA）

13. **S4 — 特定不能（S4TA / S4TB のどちらか判断できない）** — 同じ文の中: 「... and examining
    documentation to clarify the structure of parsed items (S4).」(FSE049:14)
    ⚠️ 本文は開発者 ID「S4」のみで、Table 4 上 S4 には task が 2 つ (S4TA, S4TB) あるため、
    指示に従い task_id を「特定不能」とした。
    → Table 5 との対応: Table 5 の documentation 行には S4TB のみが挙がっている
    （S4TB=はい、S4TA=いいえ）。本文だけからはどちらの task かは判断できない。

14. **P1TA** — 「P1 also demonstrated the use of vicarious experience. Rather than immediately
    inspecting the code, P1 spent time reviewing reports of similar issues to learn how they had been
    handled. After about ten minutes, P1 concluded, “I don’t see anybody has fixed this.” Although
    these reports did not resolve the bug, this method enabled P1 to rule out simpler solutions
    before investing effort in more complex approaches.」(FSE049:15)
    → Table 5 に既出: **いいえ**（Table 5 の 3 行のいずれにも P1TA は挙がっていない。★ 新規の発見）

## 除外したもの

- **P5（該当 task 不明）** — 「P5 described this practice: “When I come into a company, I will ask
  if someone will show me how they found their bug . . . I pick out pieces from them of how I can
  approach it.”」(FSE049:15)
  → 除外理由: 「観察対象の task 中に」ではなく、P5 が一般的な習慣として語った回顧的発言
  （"when I come into a company" という一般論）であり、本研究で観察された特定の task 中の
  行動ではないため。

- **P5（P5TB 文脈だが一般論の引用）** — 「Despite showing a personal project, P5 observed,
  “being able to go to commits and see what people actually did and how that happened gives me
  a lot of context.”」(FSE049:14)
  → 除外理由: (1) 観察中の具体的行動ではなく P5 の一般的な感想の引用であること、(2) 言及されて
  いる「commits」はコードベース内（バージョン管理履歴）の情報であり、コードベース外部の情報源
  ではないこと。

- **P4TA** — 「P4 had to analyze the performance issue without access to the code, mentioning,
  “One way is to go [to the] platform team, and talk to them about how their APIs are performing
  bad, [and discuss] what we can do about them. . . .”」(FSE049:14)
  → 除外理由: 「One way is to...」という仮定・提案の話法であり、実際に観察中にプラットフォーム
  チームに話しかけたという記述ではないため（指示の「仮定の話は除外」に該当）。

- **P1TA** — 「P1 spent considerable time investigating a bug that turned out already fixed, but
  debugging was challenging because another contributor had used the version control system in
  an unusual way, resulting in reapplying an old patch with the same commit message.」(FSE049:14)
  → 除外理由: 外部情報源への参照ではなく、バージョン管理システム（コードベース内部の履歴）の
  扱いにくさについての記述であるため。

- **P3TA** — 「... P3 applying temporary DOM fixes before moving to implementing the changes in
  the codebase ...」(FSE049:10)
  → 除外理由: 外部情報源の参照ではなく、実装上の一時的な回避策（DOM への直接的な変更）についての
  記述であるため。

- **P3TA / P6TA（アクセス制限の記述）** — 「... both P3 and P6 were blocked by authentication
  issues. Because of this, P6 had to switch to a different task to show, while P3 had to schedule a
  follow-up session after asking for credentials.」(FSE049:14)
  → 除外理由: バグの原因についての情報源への参照ではなく、認証情報の取得というアクセス上の障壁
  についての記述であるため（「バグ調査のために外部情報源を参照した」という要件に当たらない）。

## 読み切れなかった部分

- 本文の全 22 ページ・Discussion/Limitations 節（FSE049:17 以降）まで一通り確認し、task_id
  (`PnTx` / `SnTx`) の出現箇所は全てページ単位で機械的に検索して照合したが、Introduction /
  Related Work / Methodology の一般的記述（Table 1・2・3 周辺を除く）は逐語では読み切っておらず、
  タスク固有の外部情報源参照が無いことを前提に除外している。締切内では、この前提の再確認までは
  行えなかった。
