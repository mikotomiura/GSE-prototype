# panel（stage: manuscript・対象: 原稿の全体（結果の前の版）・round 1）

外枠の round（outline-threat-model）と同じ立場・同じ接地の文献を使う（引き継ぎの指示）。原本は outline-threat-model/round-1/tmp/raw/ から写し、SHA-256 の先頭 16 桁が下の表と一致することを 2026-10-21 に確かめた。本文は round-1/tmp/sources/ に写した。

- R3 に、原稿が使う統計手法（ブートストラップの区間など）そのものの方法論の論文は入れなかった（任意の項。時間を優先した）。

| 役 | 立場 | 批判的な下位人格 | 接地の文献（確認済み=OpenAlex で題・筆頭著者・年・DOI と OA を確認／読めた=本文の題が一致） |
|---|---|---|---|
| R1 | 再識別・匿名化への攻撃の評価の専門家（プライバシーの攻撃研究の伝統） | 「その評価は本当にリスクを測っているか・脅威モデルは攻撃者に甘すぎないか／厳しすぎないか」を疑う懐疑家 | Narayanan & Shmatikov, How To Break Anonymity of the Netflix Prize Dataset, arXiv cs/0610105（OpenAlex: 10.48550/arxiv.cs/0610105・OA）SHA-256 562f57b9b2b147a3…・manuscript-matching/round-1/tmp/sources/narayanan.txt ／ Stadler, Oprisanu & Troncoso, Synthetic Data – Anonymisation Groundhog Day, arXiv 2011.07018（OA）SHA-256 7300c9f9f588021a…・manuscript-matching/round-1/tmp/sources/stadler.txt ／ Rocher, Hendrickx & de Montjoye 2019, Nat Commun, 10.1038/s41467-019-10933-3（OA）SHA-256 d65d99af3ec15135…・manuscript-matching/round-1/tmp/sources/rocher.txt |
| R2 | データを公開・管理する側（大学・教育データの管理と、行動の生体情報の匿名化の実務） | 「で、データを公開する側は何に使えるのか」と問う実務家／冗長さに厳しい読者 | Borgman 2018, Open Data, Grey Data, and Stewardship: Universities at the Privacy Frontier, Berkeley Tech. L.J., 10.15779/z38b56d489（OA）→ arXiv 1802.02953 の版で代えた（題と筆頭著者が一致）SHA-256 dd114edf1d89fe72…・manuscript-matching/round-1/tmp/sources/borgman.txt ／ Hanisch, Arias-Cabarcos, Parra-Arnau & Strufe, Anonymization Techniques for Behavioral Biometric Data: A Survey（ACM CSUR 2025, 10.1145/3729418・OA）→ arXiv 2109.04120 の版で代えた（ACM の PDF はボットに閉じる。arXiv 版の題は "Privacy-Protecting Techniques for Behavioral Biometric Data: A Survey"）SHA-256 2922e10a8ae31281…・manuscript-matching/round-1/tmp/sources/hanisch.txt |
| R3 | 投稿先の方法論・倫理・再現性の番人（セキュリティ研究の評価の落とし穴と研究倫理） | 過剰主張と、現実離れした脅威モデル・検証できない手順の摘発者 | Arp et al., Dos and Don'ts of Machine Learning in Computer Security, arXiv 2010.09470（OA）SHA-256 895ab4622260bba9…・manuscript-matching/round-1/tmp/sources/arp.txt ／ Kohno, Acar & Loh, Ethical Frameworks and Computer Security Trolley Problems, arXiv 2302.14326（OA）SHA-256 4bf0055552d48a4f…・manuscript-matching/round-1/tmp/sources/kohno.txt |

- 試して外した候補: Leinonen et al. 2017（OA の場所が landing page だけで本文に届かなかった）・Nosek et al. 2018（PMC がボットに閉じた）・Drachsler & Greller 2016（OA なし）。
- 立場の角度: R1 = 攻撃側の評価、R2 = 公開する側の管理と実務、R3 = 方法と倫理の審査。系譜は互いに違う。
