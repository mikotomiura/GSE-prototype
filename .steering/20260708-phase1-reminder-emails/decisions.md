# 設計判断と根拠

## D1: 判定信号は F4 の最終提出日
F4 = セッション後アンケート(毎回) なので「最終 F4 提出日 = 最後に作業した日」。
既存 `countByPid_("F4")` がタイムゾーン安全に latest を算出済み。新規集計を作らず再利用。

## D2: 停滞は督促でなく気遣い (「至急」不採用)
研究参加者はボランティア。「至急」は脱落を早め関係を悪化させうる。同じ目的(詰まりの検知)を
「お困りごとはないですか」の気遣い文面で達成する。研究倫理・丁寧さ要件の両方に整合。

## D3: 参加フェーズのゲート (code-reviewer HIGH 対応)
同意直後で NDA未署名/F2未提出/アプリ未配布の被験者に「課題未提出」を送るのは誤送信。
対象を「F4 が1件以上ある(=作業開始済) OR オンボーディング完了(NDA署名済 かつ F2完了)」に限定。
停滞日数の起点も consentDate ではなく F2完了日を優先(準備完了からの経過で測る)。

## D4: ボタンは Web アプリ(doGet)、P-ID のみ URL 搭載
1クリックで即記録・完了画面が最も丁寧。P-ID は擬似匿名(既存短縮URLも P-ID を載せる方針)なので
URL 搭載可。実名・メールは載せない(PII 分離維持)。action はホワイトリスト、pid は正規表現検証。

## D5: doGet なりすまし (code-reviewer MEDIUM) — 受容
P-ID が低エントロピー連番のため、exec URL を知る第三者が任意 P-ID で応答を投げると
リマインド抑制やログ汚染が起きうる。ただし (a) exec URL は被験者メールにのみ記載され非公開、
(b) 2-3名運用の小規模内部研究、(c) 研究者はロスター/ログで実提出を確認でき silence は検知可能。
→ 現時点は**受容**。exec URL が漏れた/被験者が増える場合は per-PID HMAC トークン
(ScriptProperties の共有シークレット + pid 署名)を URL に付与し doGet で検証する。

## D6: 送信は手動起動・初日ドライラン
トリガー設置(`installReminderTrigger`)と Web アプリ公開は研究者が手動実行(誤送信防止)。
初日は `REMINDER_AUTO_SEND=false` で下書き確認 → 内容 OK なら true に切替。
緊急停止は `REMINDER_ENABLED=false`。

## D7: タイムゾーン依存
`atHour(20)` と全日付整形はプロジェクト TZ 依存。`appsscript.json` の
`timeZone: "Asia/Tokyo"` を運用前に必ず確認する(コメントは JST 前提)。

## D8: 管理シート刷新 (2026-07-08 後半)
- 進捗目標: 10 セッション/人 × 5 名 = 50 セッション(ユーザー確定)。到達率 = 総セッション/50。
  有効ラベル(GATE2 ≥20/人)は metrics.json 側で確認、本シートは F4 セッション数ベース。
- Phase1 終了トグルは **専用「運用コントロール」タブ(先頭)** に配置。進捗ダッシュボードは
  refreshRosterStatus で毎回 clear() 全再描画されるため、そこにトグルを置くと選択値が消える。
- ダッシュボードのセッション数は fresh な F4 集計(countByPid_)を一次ソース化。ロスター col8 は
  refreshRosterStatus のみが書くため buildManagementSheet 直呼び経路で古くなりうる(code-reviewer MEDIUM)。
- buildControlTab_ は buildManagementSheet の**最後**に呼ぶ(他タブの insertSheet(name,0) で
  先頭から押し下げられるのを防ぐ・code-reviewer MEDIUM)。

## D9: phase1Status_ は fail-open (code-reviewer MEDIUM)
読取失敗/シート未作成/名前付き範囲喪失時は「実施中」を返す(送信継続)。これは
「一時的な読取エラーで全リマインドが黙って止まる」事故を避ける意図的な選択。
→ **確実に止めたい場合は名前付き範囲やタブ名に依存せず `REMINDER_ENABLED=false` を併用**する。

## D10: cross-review (Claude+Codex) 対応 (2026-07-08)
- **両者一致: phase1Status_ fail-open** → 送信専用に `reminderSendingAllowed_()`(fail-closed)を新設。
  「終了」or 読取例外で当日送信スキップ(翌日回復)。表示用 phase1Status_ は fail-open のまま役割分離。
- **Claude HIGH: doGet の GET 副作用** → メールのリンクスキャナ(Safe Links 等)の自動 GET プリフェッチで
  誤記録→リマインド誤抑制のリスク。**確認ページ方式に変更**: doGet は確認ページを返すのみ、記録は
  ボタン押下(google.script.run → 公開関数 `reminderRecordResponse`)まで遅延。JS 実行=人間のクリックが必須。
- **Codex: doGet の pid 実在未検証** → `rosterHasPid_` でロスター突合、未登録 P-ID の応答は記録しない。
- **Codex: reminderLogAppend_ のロック未取得時 release** → `tryLock` + `locked` フラグで、保持時のみ release。
- **Codex: 日付差の DST/TZ** → `reminderParseYmd_` を `Date.UTC` 基準に(日本は DST 無しだが無コストで堅牢化)。
- **Codex 誤検知(却下)**: 「停滞が当日応答を無視」→ idleDays=min(submit,resp) により当日応答で 0 になり
  必ず日次側に落ちて respondedToday で抑制される。設計は正しい。
- Claude LOW: ダッシュボードの空 catch に Logger.log を追加。

## 範囲外(別タスク起票推奨)
- `scripts/run-codex-review.sh` のトークン集計が現行 Codex CLI の `turn.completed.usage` に未追随で
  tokens_used が常時 0 加算(予算追跡が事実上無効)。cross-review 中に判明。budget.json は実測で手動更新済み。
- GAS 用テストハーネス不在(reminderDiffDays_ 等の単体テストが書けない)。本 diff 固有の後退ではない。

## 反映済みの他レビュー指摘
- consentDate の Date型正規化漏れ → `readRoster_` で `reminderYmd_` を通して修正
- appendRow 競合 → `reminderLogAppend_` を `LockService` + `flush()` で排他化
- throttle=0 の同日二重送信 → 定数に「≥1 必須」の不変条件コメント追加
