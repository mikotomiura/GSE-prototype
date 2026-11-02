# 次の新しい形のユーザー検証の設計（C4 の取り方を中心に）

## 背景

- O1 では C4（作業の途中の自己申告の詰まり・6 択の問い）を取らないと決めた（`.steering/20261103-gse-stall-candidates-c1c2c6/decisions.md` 判断 9）。O1 はまもなく終わる。
- synthesis の H1〜H3（`.steering/20261102-gse-synthesis-redesign/synthesis.md` §5）と MhD の criterion 直結の段（同 §7）は、どれも C4 が無いと確かめられない。C4 は公開データで代えられない。
- WBS と research-positioning の 2026-10-31 改訂は、次の検証を「1 段目 統制課題で招待の出し方を 3 腕で比べる → 2 段目 自然作業の多重ベースライン」としている。その後の ADR-041（2026-11-02）で、推定器の腕の中身（`friction_rising`）と主要アウトカムは停滞の分解と O1 での数え直しの後に決めることになった。

## ゴール

次の新しい形のユーザー検証について、研究者と次を決め、`decisions.md` に記録する。

1. 何を確かめる検証か（C4 を取って H1〜H3 を確かめるのか、招待の効果まで含めるのか）と、small-n の判断 6 のどこが残るか。
2. 収集の形（自然作業 / 統制課題 / 段で重ねる）と、採択前（研究者本人）・採択後（3〜5 名）の分け方。
3. C4 の取り方（アプリ内か外か・無作為の枠と層化の配分・申告の時刻と停滞の段の対応）。
4. C4 を開く前の事前登録に書く項目。
5. 同意で決めること。
6. ADR-031・ADR-032 の扱いと、新しい ADR に起こすか。

終わりに MhD の議論の引き継ぎを作る。

## スコープ

### 含むもの
- 議論と決定の記録（`.steering/` のみ）
- 必要なら文献の確かめ（サブエージェントか `/literature-review`）と第二の案（codex-consult か /reimagine）

### 含まないもの
- コードの変更
- 既存の ADR の本文・凍結した事前登録・同意文書の書き換え（新しい ADR を起こすかは決めるが、起票は別タスクにしうる）
- 事前登録の本文の作成、ラベルの件数の見積もりの計算（項目を決めるまで）
- O1 の見ていない期間（11-01 以降）を開くこと

## 受け入れ条件

- [ ] ゴールの 1〜6 について、研究者の選択と理由が `decisions.md` に 1 判断ずつ書かれている
- [ ] 一次で確かめた現状（ADR-031・040・041・research-positioning・WBS・small-n 判断）が `decisions.md` の冒頭に書かれている
- [ ] MhD の議論の引き継ぎが `.steering/_handoff/` にある

## 関連ドキュメント

- `.steering/_handoff/next-session-gse-next-study-design.md`（入口）
- `.steering/_handoff/next-session-esm-consent-next-study.md`
- `docs/adr/ADR-031`・`ADR-040`・`ADR-041`
- `docs/research-positioning.md` §1 の 2026-10-31 改訂・`docs/wbs-verification-halfyear.md` の 2026-10-31 改訂

## 運用メモ
- /reimagine 適用: No（設計の第二の案は codex-consult で取った・判断 11。研究者が「Codex に第二意見→閉じる」を選んだ）
