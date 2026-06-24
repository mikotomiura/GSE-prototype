# 設計判断（decisions）

このセッション（2026-06-24）でユーザー承認済み。ソースを併記する。

## FD1: Phase 1 = X1 較正・単群（介入は経験するが対照なし）
- Phase 1 の真値 = アプリ内 **blind ランダムプローブ**の Q1摩擦/Q2前進（F3）。較正中はモデル状態を見せない。
- **Wall(Lv2) と 2分 Zen Timer は経験する。Physical Anchor(Lv3/4 散歩)は実装しない**（intervention-response-capture「Physical Anchor は Phase E」）。
- **AB/BA 対照群は無い（単群）**。よって自己効力感 pre/post は記述的観察のみ・因果主張しない（AB/BA は v0.4 §5.3 Phase 2）。
- 根拠: v0.4 §5.2（Phase 1=X1 較正）、ユーザー訂正（Wall/Timer 経験・PA 非実装）。
- 訂正: 旧 md L174「介入もないため」は誤り → 「単群・対照群が無いため」へ修正済。

## FD2: 2相プロトコル＝`intervention_enabled` で week1 を blind 化（Monk Mode は使わない）
- **Week1**: 開始画面で `intervention_enabled=false`＋較正モード ON → `condition=blind_calibration` / `label_pool=calibration_blind`。Nudge も Wall も発火しない。
- **Week2**: `intervention_enabled=true` → Wall+2分Timer 実発火 / `label_pool=post_intervention`。
- **Monk Mode は不可**: (i) Wall しか止めず Nudge が残る（`showNudge=p_stuck>0.60`、blind が崩れる）、(ii) `wall_accum_ms=0` にリセットし would-fire 信号を消す（`intervention.rs update_wall_accumulation`）。
- 実装状況: `intervention_enabled=false` は backend で全介入を gate 済（`src-tauri/src/lib.rs:182` が policy 前に `safe_default()` 返却）。開始画面に介入/較正の2チェックボックス既存（`src/App.tsx:271-286`）。
- 根拠: コード確認、codex-consult（shadow-mode 二相提案）、v0.4 §3.1/§3.2。

## FD3: blind 汚染対策＝プール分離＋anticipation contamination
- `calibration_blind`（X1 判定用）と `post_intervention` プールは絶対に混ぜない（md 既出）。
- Wall 発火は「Stuck 判定」の強い開示 → プローブ汚染。time 隔離＋直近介入経過時間タグ＋プール分離で統制。
- **anticipation contamination**（被験者が「この後 Wall が来る」と学習し非近接プローブも歪む）に注意 → 初回 Wall 前を純 baseline として別集計＋プローブをスコア帯で層化（codex-consult ①）。

## FD4: 自己効力感の二本立て（GSE-10 無改変 + 自作 主指標）
- **副指標 = Schwarzer & Jerusalem(1995) GSE-10**（4件法・得点10-40・[15]）。**無改変・公式日本語版を逐語使用**（D3）。
- **主観主指標 = 自作 bespoke 尺度「作業再開感・自己調整感」**（旧称「課題特異的自己効力感」）。
  - GSE-10 を“改変”するのではなく**別の自作尺度を追加**（v0.4 §4.3：一般性は短期・領域特異の介入に感度が低い）。
  - 「自己効力感」と称さない（過剰主張回避、codex-consult ③）。要 Cronbach α 報告・採点法/仮説プレレジ固定。
  - 全項目「AIに頼らず」偏重を是正（逆転/行動信念/選好項目を混在）。
- pre/post は項目1–4を matched 再測定。介入体験項目（取り戻す感覚/継続意欲）は SE と別構成概念で分離。

## FD5: Form の役割＝主観のみ（行動はアプリ内ログ）
- dismiss 理由・Wall 早期解除/2分順守/タイマー満了 は**アプリ内 NDJSON で捕捉済**（重複させない）。
- Form が担うのは主観: **annoyance**（F4・任意）、**NASA-TLX short**（F5・3項目, v0.4 §4.4/[11]）、継続意欲（F5）。
- **helpfulness は介入直後のアプリ内1タップ（サンプリング）で取得**（想起バイアス回避、codex-consult ⑤）。F4 では聞かない。
- (a)(b) は Form 設問にしない（ログ派生、D7）。

## FD7: 週セレクタ統合の実装判断 (2026-06-24, tasklist #A 実装時)
- スタート画面の介入/較正2チェックボックスを単一の週セレクタ (`PhaseWeek` = `week1_blind` / `week2_intervention`) に統合。
  各週が `interventionEnabled`/`calibrationMode`/`condition`/`labelPool` のタプルを `WeekConfig` で保持し、
  「介入 ON なのに calibration_blind プール」のような FD3 汚染を**型レベルで表現不能**にした (`src/App.tsx`)。
- **マッピング**: 第1週 = `intervention_enabled=false` + 較正 ON / `blind_calibration` / `calibration_blind`。
  第2週 = `intervention_enabled=true` + 較正 OFF / `baseline` / `post_intervention`。文字列は backend `Condition`/`LabelPool` enum と byte 一致。
- **セッション中ロック**: 週セレクタはスタート画面のみに描画。`isStarted=true` の Dashboard 中は非表示で変更不可。
  「戻る」(`handleBack`) でスタート画面へ戻った後の週再選択は**新セッション扱い**として許容する
  (既存の task_kind 変更と同じ onBack セマンティクス。`handleStart` が毎回 `start_session`+`record_session_meta` を呼び新規 session_meta を記録)。
- **fail-loud 化**: `record_session_meta` 失敗時は Dashboard へ進まず `setStartError`+return。
  失敗を握り潰すと condition/label_pool タグ欠落 + `INTERVENTION_ENABLED` が前セッション値のまま残り
  blind 較正が汚染されるため (code-reviewer MEDIUM 指摘)。

## FD6: GSE-10 逐語のソース
- repo 内には引用のみ・逐語項目は無し。出典 = Schwarzer 公式 `http://userpage.fu-berlin.de/~health/selfscal.htm`（多言語・日本語版あり）／英語原典 NFER-NELSON 1995 pp.35-37。
- GAS の現10項目はプレースホルダ。**捏造・自前翻訳しない**。公式日本語版へ差し替える（tasklist 参照）。
- **解決 (2026-06-24)**: 採用版 = **Ito, K., Schwarzer, R., & Jerusalem, M. (2005) Japanese Adaptation of the GSE**
  （`http://userpage.fu-berlin.de/~health/japan.htm`）。WebFetch で逐語取得し buildF2/buildF5 へ投入（byte 一致）。
  公式アンカー = 1 全く当てはまらない／2 当てはまらない／3 まあ当てはまる／4 全くその通り。
  ⚠ WebFetch 経由のため公式ページとの逐語一致を人手で最終照合し、研究利用条件を確認してから本番投入すること。

## FD9: 自作尺度「作業再開感・自己調整感」項目最終化 (2026-06-24, tasklist #D)
- **方針 = Approach A（4項目・混在指標）**。旧4項目は全て「AIに頼らず/自力で」方向偏重で黙従・方向
  バイアスを招いていたため、効力感(正)/逆転/行動信念/選好を **1項目ずつ混在**させた4項目へ改訂（FD4 履行）。
- **確定項目**（F2-C=`tseItems` / F5=`tsePost`、byte 一致・matched pre/post、5件法 1–5）:
  1. [効力感・正] 詰まっても、自分なりの糸口を見つけて書き進められると思う
  2. [逆転・行動傾向] 難しい場面になると、自分で考えるより先に AI に答えを求めてしまう（採点時 6−x）
  3. [行動信念・正] いったん自分で考えてから AI を使う方が、最終的に良い文章になると思う
  4. [選好・正] 詰まったときは、すぐ答えを見るより、自分で糸口を探す時間をとりたい
- **採点法（プレレジ）**: 項目2を逆転再コード（6−回答値）後、4項目の平均を合成スコアとする。
- **α（プレレジ）**: 4 facet 混在のため中程度を想定。**報告のみ**（基準 α=.70 を参照値とし Go/Kill 判定に使わない）。
- **主仮説（プレレジ）**: pre→post の合成スコア変化を **記述的に観察**（単群・対照なし(FD1)のため因果主張しない）。
- ユーザー承認: AskUserQuestion で方針 A・α 報告のみ(.70 参照)・記述的 pre→post を確定（2026-06-24）。
- 実装: GAS は単一定数 `TSE_ITEMS`（ファイル冒頭）を `buildF2`/`buildF5` 双方が参照する形に一元化し、
  pre/post の byte 一致を**構造的に保証**（code-reviewer LOW 指摘の二重定義事故を防止）。`node --check` 緑、
  `設問草案.md` F2-C 同期。code-reviewer は HIGH/MEDIUM なし・四者(GAS/md/prereg/FD9)整合を確認。
- プレレジ全文は `preregistration-tse-scale.md` を参照。

## FD8: 新フォーム ID 割当 (2026-06-24, tasklist #C)
- ユーザー指定により新フォーム `1I-X1B8F-tQk7aEAdqderOLhjobeHct48KU23NWwfhlY` を **F5 事後アンケート**へ割当。
- `buildF5` を `FormApp.create` → `openById(F5_FORM_ID)` 化（F1 と同方式に統一）。openById は同一フォーム
  再利用のため、再実行時の設問重複を防ぐ既存設問全削除（`CLEAR_EXISTING`）を buildF5 にも追加。
- F2/F3/F4 は当面 `FormApp.create` のまま（固定 ID 未指定）。
