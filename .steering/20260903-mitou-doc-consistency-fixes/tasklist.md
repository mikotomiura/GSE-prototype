# タスクリスト — 未踏提出文書の整合性修正と提案書の整理

## A. 整合性修正（必須・コミット 1）

- [x] A-1 `docs/mitou_submission/README.md` の再生成コマンドに `--compact` を足す
      (★ 実測で判明: **詳細資料だけ compact / 補足資料 3 本は非 compact**。1 つのループで 4 本回すのが誤りだった)
      （★ 併せて「付けないと 15 ページになる」実測を注記）
- [x] A-2 技術設計書 §3.2 を現行実装に合わせる (★ **stale は 2 文あった**)
      （★ 候補ウィンドウ *検出* は生きている。撤回されたのは *推論の一時停止* だけ）
- [x] A-3 `docs/references.md` に Dhakal et al. (2018) を **[P269]** で append-only 登録
      + `glossary.md` の `β_writing_latin` 行に使用箇所を作った (ルール 6)
- [x] A-4 `docs/agent-shared.md` の ADR 範囲を 022 まで更新
      + 表現チャネル行に「ADR-017 単独で読むと古い契約を掴む」注記を追加
      (★ 本セッションで実際に取り違えた箇所)
      ★ `CLAUDE.md` / `docs/adr/README.md` は stale でなかった (実測)
- [x] A-5 `check_doc_lexicon.py` 実行 → 違反なし
- [x] A-6 README 手順で `.docx` 4 本を再生成 → 本文一致を確認

## B. 提案書の整理（コミット 2）

- [ ] B-1 対象をナレッジワーカーへ（問いは広く / 確証主張は論述・L0 のまま）
- [ ] B-2 「Markdown エディタを基準環境として」を削除し、統制実験と自然作業収集を書き分ける
- [ ] B-3 日本語 IME の主張を自前実測 2 本へ差し替え（decisions.md D2）
- [ ] B-4 モデル昇格を ADR-019 D1 の 4 段で書く／損失関数 2 ブロックを技術設計書 §4.4 へ移設
- [ ] B-5 図 2 (`gse-model-promotion.svg`) を 4 段に合わせて差し替え → PNG 再レンダ
- [ ] B-6 フェイルセーフ 2 節を統合し、技術設計書 §8 の撤退設計 A/B/C/D を入れる
- [ ] B-7 PC / スマホの表現を役割で書き分ける（decisions.md D1）
      → 縮退表の「PC の最小表現へ戻す」／図 1 のラベルも連動修正
- [ ] B-8 スマホ側 OS 制約（ADR-022）と向き合う計画を追記
- [ ] B-9 §6 に APNs 経由の留保を追記（`ADR-022:368` 逐語）
- [ ] B-10 学術的貢献を拡充（検証レポートの受容性実測など）
- [ ] B-11 `check_doc_lexicon.py` → 違反なし／`.docx` 再生成／ページ数実測

## C. 完了処理

- [ ] C-1 `/review-changes`（code-reviewer + security-checker 並列）
- [ ] C-2 `/cross-review`（パス限定。★ 無関係な未コミット変更で fail-closed するため
      `-- docs/mitou_submission docs/references.md docs/adr` の形で回す）
- [ ] C-3 `/finish-task`

## 別タスクへ送るもの（本タスクのスコープ外）

- ADR-017 既決 D21（PC 画面内の表現層）を降ろすかの判断 → 新規 ADR が要る
- [V5] Crotti et al. Hylog の精読カード ＋ `references.md` 登録 → `/literature-review` 1 ラウンド
- 提出 PDF の最終ページ数確定（レンダラ依存。提出経路が確定してから）
