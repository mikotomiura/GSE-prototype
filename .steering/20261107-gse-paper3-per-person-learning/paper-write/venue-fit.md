# 投稿先の適合（paper-write Step 0）—— 2026-11-07

読者（判断 2）: 行動ログから 1 人ごとのモデルを作る個人化の研究者。変えたいこと: 共通の側の構造を良くした相手と比べてから個人化の効きを主張させる。費用ゼロを既定にする（memory「無料で済ませる」）。

原文の逐語・取得元・最近の論文の表は同じ dir の `venue-umuai-ijhcs.md`・`venue-jedm-tiis.md`（サブエージェント 2 本が取得。curl は Springer・ScienceDirect・ACM で止められ Chrome で読んだ。JEDM は curl）。メインの裏取り: JEDM の "There are no article processing charges, submissions fees, or any other costs required of authors" を curl の原文で照合した（2026-11-07）。他の引用はノートの取得元のとおりで、メインは再取得していない。

| | UMUAI（Springer） | JEDM | IJHCS（Elsevier） | ACM TiiS |
|---|---|---|---|---|
| 費用ゼロの道 | あり（購読モデルは "no APC charges apply"・採択後に選ぶ） | あり（diamond OA・費用なし） | あり（購読は "No open access publication fee"） | 無し（2026 から全誌 OA・独立研究者は APC 対象・2027 受理で 1,800 USD） |
| 範囲の重なり | 強い（user model の獲得と表現・設計と評価の方法・"mainly publishes empirical research papers"） | 教育の場に限る（"generalized or applied across different educational contexts"）。CS1 は合うが CoAuthor は外れうる | 弱い（具体の利用者に向けた設計と評価を求める） | 人間の側が無いと desk reject の恐れ |
| 分量の上限 | 規定の文なし（要旨 150〜250 語）。最近の 3 本は本文 約 9.8k〜13.3k 語 | 規定の文なし（要旨 100〜300 語）。最近は 23〜48 頁 | 規定の文なし（要旨 ≤250 語・Highlights 必須） | 規定の文なし（要旨 150〜250 語） |
| 補足資料 | "Online Resource"・受け取ったまま公開・査読者が読むかは記載なし | 参考文献の後の付録・コードは要旨の末尾に URL | 本文で引用・受け取ったまま公開 | 電子付録・査読者には主文書の一部として見える |
| 査読と書式 | 単盲検・Springer Nature の LaTeX | 匿名化は任意・jedm.cls | 単匿名・Elsevier LaTeX・著者略歴と写真が必須 | 二重匿名が必須・acmtiis |
| プレプリント | 未照合（読んだページに文なし） | 投稿前と投稿中も許可・推奨 | 許可（先行の出版に数えない） | 査読中は控えることを推奨 |

未照合のこと: UMUAI のプレプリントの方針・投稿システムの分量の制限、IJHCS のテンプレートのページ、TiiS の査読手順。最近の論文は UMUAI 3 本・IJHCS 2 本・JEDM 3 本・TiiS 1 本で、IJHCS と TiiS は最低の 3 本に届かない（取れなかった理由はノートに書いてある）。

## 結論（3 行）— 研究者の選択の後に確定する

- 推奨: UMUAI の empirical research paper（個人化の評価の方法についての実証の反証寄りの貢献）。
- 読者: user model を作り評価する研究者。費用は購読モデルでゼロ。プレプリントは方針を一次で確かめてから。
- 分量: 規定の上限は無い。最近の論文の本文は 1 万語前後だが、paper-write の目安（5,000〜7,000 語）を先に置く。
