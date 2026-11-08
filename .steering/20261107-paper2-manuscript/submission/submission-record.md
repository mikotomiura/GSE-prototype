# 投稿の記録（JEDM・論文 2）

- 受付: JEDM の投稿番号 1486。受付の画面は「Submission complete」（確認のメールを送ったとの文）。API で submissionProgress 空・status 1（Queued）・stage 1・dateSubmitted 2026-11-08 04:31:15（サイトの時刻）。
- 操作の分け方: ログインは研究者が先にしていた（私はパスワードを入れていない）。最初のチェックリストの印は自動の安全確認に止められたので研究者が付け、Begin Submission を押した。著作権の同意と Submit も研究者が押した。それ以外（題・節 Articles・プライバシーの同意・キーワード・要旨・参考文献・ファイル・著者の所属・編集者への欄）は私が Claude in Chrome で入れた。
- 上げたファイル: 本文の PDF（Article Text・441,182 バイト・31 頁・SHA-256 8bab070e…）と送付状の PDF（Letter to Editor・12,916 バイト・2 頁・SHA-256 c50fa9b4…）。サイトから取り直した 2 つが手元と SHA-256 で一致。
- 詳細: 題は原稿のまま。キーワード 6 つ（原稿と同じ）。要旨は abstract.tex から LaTeX を外した 1,828 文字（API で長さ一致）。参考文献は main.bbl から 1 行 1 件の素の文 43 件（API で 43 行）。
- 寄与者: 所属にプロフィール由来の壊れた表記（PHP の serialize の文字列）が論文 1 と同じく入っていたので、OJS の API（PUT contributors）で「Independent Researcher」に直し、読み直して確かめた。ORCID の欄は空（原稿と送付状に番号）。国 Japan・メールは登録のまま。
- 編集者への欄: 送付状の本文（pandoc の HTML）。
- 送付状: 論文 1 の形に合わせた（利益相反: 停滞の検出器を著者が設計・金銭の利害なし・資金なし・編集者との関係なし。単盲。論文 1 は投稿番号 1484 とプレプリントで示す）。
