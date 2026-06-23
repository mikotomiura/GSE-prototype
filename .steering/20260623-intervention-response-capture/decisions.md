# 設計判断 (intervention-response-capture)

## D1: 3つの設計フォークを AskUserQuestion で確定 (ユーザー承認 2026-06-23)
- ①イベント表現 = **(i) 既存 InterventionResponse 拡張** (action=wall + reason + Option<elapsed_ms>)。
- ②早期/通常判定 = **(A) Rust サーバ側 elapsed (HTML 不変)**。
- ③`idle_timeout` enum 値 = **予約する** (未配線)。
- 根拠は design.md「アプローチ」参照。NDJSON は不可逆 (roadmap §2) のため凍結前にユーザー確定。

## D2: /reimagine は実施せず AskUserQuestion で代替 (記録)
- requirement.md では /reimagine 適用 Yes とした (イベント表現が複数案・公開 schema 定義のため)。
- 実際には深いコード調査後、中心フォーク (i vs ii) + 2 サブフォークを AskUserQuestion で
  ユーザーに直接選択させた。これは /reimagine の目的 (代替案を比較しユーザーが採用案を選ぶ) を
  そのまま達成している。確定済みの選択を /reimagine で再生成し再検討するのは重複かつ
  「決定済み判断の再litigate」に当たるため省略。判断記録のみ残す。

## D3: 早期 vs 通常(順守) は server elapsed が押下ボタンを一意決定 (false positive 検討)
- JS: `doUnlock()` は timerDone(elapsed>=120s on phone) 後のみ、`doEarlyUnlock()` は 120s 前のみ実行可。
- shake_at は `/shake` (phone scan = JS scanTime ≈ 同時刻) に記録 → server elapsed ≈ phone elapsed。
- 通常解除: phone elapsed>=120s かつ network latency が加算されるため server elapsed >= 120_000 が堅い。
- 早期解除: phone elapsed<120s → server elapsed < 120_000。
- 境界リスク: 120.0s 直前 (例 119.9s) の早期解除 + 高 latency で server が 120.0s を超えると completed 誤判定。
  通常操作では発生せず、解析時の許容誤差内 (capture-freeze CD5 A3 と同様「境界外れ値」前提)。

## D4: shake_at==0 (通常フロー外の /unlock) は early_unlock + elapsed_ms=None (堅牢性)
- 通常は phone が /shake で timer ページを取得してから /unlock するため shake_at!=0。
- 直 curl 等で /shake を経ず /unlock した場合 elapsed を `now-0` にすると巨大値で誤って completed になる。
  → shake_at==0 を明示ガードし「順守を主張できない=early_unlock」+ elapsed_ms=None。

## D5: try_send 失敗は無視 (解除 UX を壊さない・data-privacy 準拠)
- /unlock ハンドラ内は try_send で非ブロッキング (hook 制約に準じ I/O を持ち込まない)。
- channel full/disconnected 時も unlock レスポンスは返す (research 捕捉 < ユーザー解除の確実性)。
- 記録はカテゴリ + 時刻 + 経過ms のみ。本文・キーストロークは一切含まない (data-privacy ルール1)。

## D6: format_intervention_response_line(None) は従来出力と byte 同一 (後方互換)
- elapsed_ms=Some の時のみ `,"elapsed_ms":N` を付与。Nudge dismiss (None) 行は変更前と完全一致。
- schema_dto も serde の Option 欠落=None 規則で旧 NDJSON をパース可 (CD4 後方互換)。
- schema_dto の elapsed_ms に `#[serde(skip_serializing_if = "Option::is_none")]` を付与し Meta variant と
  流儀を揃えた (security LOW 指摘)。JsonSchema 出力は不変 (schemars は本属性を無視・elapsed_ms は
  引き続き `["integer","null"]` 非 required)。

## D7: code-reviewer MEDIUM 対応 (本タスク内で消化・tech-debt-now 方針)
- **境界 skew (MEDIUM-1)**: shake_at=/shake 受信時刻 と JS scanTime=描画時刻 は δ(数十〜数百ms) ずれる。
  server elapsed = phone_elapsed + δ + 往復遅延 で常に phone より大きいため **通常解除(順守)判定は堅牢**
  (真の completed は必ず >=120s)。唯一のエッジ = 120s 直前 (例 119.8s) の早期解除を δ+遅延が押し上げ
  completed に誤分類しうる。120s 寸前に早期解除ボタンを押す行動は稀で、解析上 ±1 例は許容。閾値は
  ユーザー決定(A)どおり 120_000 を維持し、コメントを skew 明記に修正。
- **shake==0 フロー外 (MEDIUM-2)**: /shake を経ない /unlock は `EarlyUnlock` + `elapsed_ms=None` とし、
  `tracing::warn!` を追加。**None が「フロー外」を標識**し、後段は Some を持つ実 early_unlock と区別可能。
- **POST 限定 (MEDIUM-3)**: /unlock 分岐に `request.method()==Post` を追加 (intervention-design Rule6)。
  本タスクで /unlock に LogEntry 副作用を足したため、誤った GET 等で phantom な intervention_response が
  出るのを防ぎ捕捉純度を守る。実フォン JS は常に method:'POST' のため UX 不変 (OPTIONS は別分岐で処理)。
- **action 固定文字列 (LOW)**: `"wall".to_string()` → `InterventionAction::Wall.as_str().to_string()` に統一
  (lib.rs の parsed_action.as_str() と同流儀・自由文字列混入排除)。

## D8: shake_at は毎 /shake 上書き (最新優先) を維持 — cross-review HIGH [A] を reject
- **両 reviewer (Claude/Codex) が「最初の /shake を compare_exchange で保持すべき (Wall 提示からの経過)」と HIGH 指摘**。
- **reject 根拠**: 本タスクの elapsed 基準はユーザー決定(A)で **/shake (=phone scanTime)** と定義済み。
  HTML はページ読込ごとに `scanTime=Date.now()` を再設定しタイマーを 2:00 から再開する。/shake も
  各読込で発火するため、**最新 /shake を基準にするのが「今ユーザーが見ているタイマー」と一致**する。
  最初の /shake を保持すると、再読込後に 0:05 の新タイマーで早期解除したケースを「初回 shake から
  120s 超過」で誤って completed と判定してしまう (compliance の過大計上=より悪い誤り)。
- 全ケース検証: 真の completed は最新タイマーで >=120s 待機 → 正。真の early は最新タイマーで <120s で離脱
  → 正。よって最新優先が「表示中タイマーに対する順守」を正しく反映する。コードにコメントで根拠明記。

## D9: cross-review HIGH [B] 重複 unlock ガードを適用
- 二度押し/fetch リトライ/複数端末で /unlock が複数回届くと InterventionResponse が重複記録される懸念。
- `shutdown.compare_exchange(false→true)` に成功した **最初の解除のみ** が記録・sensor-accelerometer 通知。
  二回目以降も 200 応答は返す (UX 不変)。shutdown を単一の真実源に再利用 (新フラグ不要)。

## D10: cross-review LOW/MEDIUM の扱い
- **[D] now_ms の as u64 (reject)**: 既存 lib.rs (`as_millis() as u64`)・`epoch_ms` と同流儀で統一。truncation は
  西暦5.8億年まで非問題。コードベース一貫性を優先。
- **[F] 手書き format! と serde DTO の二重管理 (accept・既知)**: format/parse とロガー E2E のテストで一致を
  担保済み。logger を serde 化する統一は大規模で本タスク範囲外。次の schema 拡張時に再検討。
- **[H] CORS `*` (reject)**: 既存設計。LAN 内フォンアクセスに必要・128bit ランダム token で認証済み。
