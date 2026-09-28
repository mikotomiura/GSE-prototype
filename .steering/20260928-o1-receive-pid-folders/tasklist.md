# tasklist — o1-receive-pid-folders

- [x] 受け口: P-ID フォルダへ保存（ロック・最古・ごみ箱除外・名前の完全一致・busy）
- [x] 台帳: 直下 ＋ サブフォルダ 1 段を遅延に走査し、時間予算の期限で打ち切る（Sync / Check）
- [x] guard test（受け口 56 / 台帳 200）緑
- [x] 変異検査（受け口 15/15 新設・台帳 80/80）
- [x] 削除台帳 A-1（P-ID フォルダ・旧形式・ファイル名で全配下を検索・再作成の確認）
- [x] O1 リリースゲート 23/1（作業前と同じ・残りは範囲外の同意文書「未了」）
- [x] code-reviewer ＋ security-checker（並列）→ MEDIUM 2 件・LOW を反映（D5〜D7）
- [x] /cross-review → Claude 側 LOW 2 件反映。Codex は secrets-filter の誤検知（`secret: SECRET` 等の識別子参照 14 行）で
      一度 BLOCKED → 研究者が確認して `--ack-filtered` で再実行（2026-09-28）→ P2×2 反映・P1 は D8 で受け入れ
- [ ] コミット → PR → CI → merge
- [ ] 研究者: 配備（researcher-steps.md）
