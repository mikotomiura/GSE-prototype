# Task — intervention-ux-clarity (Monk Mode UX 整理 + 介入仕様明文化 + opportunity ゲート検討)

## 背景

実機 smoke (gse_20260617_112924.ndjson) のフィードバックから 2 点:
1. **Monk Mode と 介入トグル (interventionEnabled) が重複に見える**。実体は別物
   (interventionEnabled=セッション開始時のマスタ ON/OFF・`lib.rs:135` で全介入を gate /
   Monk Mode=実行中トグルで Lv2 Wall のみ無効化) だが、UX 上「介入操作が2つ」で紛らわしい。
   特に較正 blind 画面で interventionEnabled OFF 時に Monk Mode を出すと「効かないのに見える」不整合。
2. **10分放置で介入が出ない**。調査の結果これは**仕様どおり** (バグでない):
   - 放置すると p_stuck が ~0.01 に低下 (無打鍵=Stuck でなく idle 判定)・Need 閾値 0.60 未満。
   - 加えて idle≥3分で `away_idle` サプレッション (`intervention.rs:176`)。
   - 当該セッションは intervention_enabled:true で 154 decision が走行。能動タイプ中は p_stuck 0.65〜0.92 を
     検知していたが「タイプ中=好機でない」で defer。`gse-replay --intervention`: none1082/defer29/nudge0/wall0、
     **DC=1.000** (defer した苦闘は全て自己回復) = 介入しなかったのは妥当。

## ゴール

1. **Monk Mode UX 整理**: interventionEnabled が無効なセッションでは Monk Mode トグルを出さない
   (効かない操作を見せない)。介入有効時は従来どおり Wall mute 操作として機能。
2. **介入仕様の明文化**: 「放置→away_idle で黙る」「idle≠Stuck で p_stuck 低下」「苦闘検知はタイプ中×小休止」
   「Need/Opportunity 2層・閾値」を docs に明記し、期待ギャップ (放置で介入が出ると思い込む) を防ぐ。
3. **opportunity ゲート検討 (調査・記録)**: 高 need で defer が多い件を `gse-replay --intervention` で定量化し
   recommendation を残す。**閾値変更は n=1・DC=1.0 では正当化されない**ため本タスクでは行わず、
   ラベル付き複数セッションでの再評価を申し送る (HMM/閾値は ml-workflow 準拠で慎重に)。

## スコープ

### 含むもの
- Monk Mode トグルの表示条件変更 (frontend: App→Dashboard へ interventionEnabled を渡し条件表示)。
- docs/functional-design.md (+必要なら glossary) への介入挙動の明文化。
- opportunity ゲートの調査結果と推奨を decisions.md / docs に記録。

### 含まないもの
- `intervention.rs` の閾値・ロジック変更 (n=1・DC=1.0 では非正当・別タスクで実データ駆動)。
- HMM / engine / features の変更。介入の新規追加・廃止。
- Monk Mode 機能自体の削除 (Wall mute の実体は残す。表示条件のみ整理)。

## 受け入れ条件

- [ ] interventionEnabled=false のセッションで Monk Mode トグルが表示されない (較正 blind 含む)。
      interventionEnabled=true では従来どおり表示・機能する。
- [ ] docs に「放置→away_idle / idle≠Stuck / 苦闘検知=タイプ中×小休止 / Need・Opportunity 2層と閾値」が明記される。
- [ ] opportunity ゲートの調査結果 (none/defer/nudge/wall 件数・DC) と推奨 (n 増で再評価) が記録される。
- [ ] `npm run build` 緑。`intervention.rs` 無変更で intervention 系テスト・snapshot 回帰維持。製品ロジック不変。
- [ ] TypeScript any を増やさない。

## 関連
- `src-tauri/src/analysis/intervention.rs` (Need/Opportunity・閾値・away_idle)
- `src-tauri/src/lib.rs` (`get_intervention_decision` の INTERVENTION_ENABLED gate)
- `src/App.tsx` / `src/components/Dashboard.tsx` (Monk Mode トグル)
- `docs/functional-design.md` / intervention-design Skill / `gse-replay --intervention`

## 運用メモ
- /reimagine 適用: **No** (UX 表示条件 + 明文化 + 調査記録。設計再構築なし)。Monk Mode の hide vs 一本化は Step C で選択。
- ブランチ: `feature/intervention-ux-clarity` (起点 = origin/main)。
