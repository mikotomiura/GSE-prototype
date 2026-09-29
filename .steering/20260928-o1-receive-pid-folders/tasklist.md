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
- [x] コミット → PR → CI → merge（PR #253・`da114dc0`）
- [x] 研究者: 配備（researcher-steps.md）— 2026-09-29 に台帳・受け口・ビルダーの `.gs` を貼り替え（PR #257 の見た目と同時）
- [x] 実配備での通し確認（2026-09-29・Mac の Claude が送信、研究者が Apps Script を実行）:
      - 合成 `P999_o1day01_gse_o1_20260929_120000.age`（14 B）を本番の受け口へ POST → `{"ok":true,"duplicate":false,"bytes":14}`（3.2 s）
      - Drive コネクタで確認: ファイルの親 = `P999` フォルダ、`P999` の親 = 受け取りフォルダ `GSE_Observation-1_.age-receiving`（**直下ではない**）。`P999/` は送信の 1.6 s 前に受け口が作成
      - 研究者が `o1LedgerRun()` → 「追記 1 件」・途絶タブの P999 は「正常」（★ サブフォルダを台帳が数えた）
      - 片付け: 研究者が `P999` を削除 → Drive で名前・ID とも見つからないことを確認
      - ⚠️ 未確認: ごみ箱に入れた直後の `o1LedgerCheck()`（ごみ箱のフォルダを数えないこと）の実測・台帳の P999 行の tombstone
