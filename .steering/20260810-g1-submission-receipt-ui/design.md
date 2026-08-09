# 設計

## ⚠️★ 前提の訂正（引き継ぎメモの誤り）

引き継ぎメモ §2 は「`SubmissionStatus` は
`{awaiting_approval, errors, packaged, sent, skipped_busy, unsent, upload_disabled}`
（実機ログの JSON で実測済み）。`sent` の増分を検出する」と書いているが、**これは別物である**。

| 構造体 | 場所 | `sent` |
|---|---|---|
| `ReconcileReport` | `reconcile.rs:50` → `gse-submit` が `GSE_RECONCILE {…}` で 1 行出す | ★ **在る** |
| `SubmissionStatusDto` | `lib.rs:1078`。`get_submission_status` がフロントへ返す | ⚠️ **無い**（4 フィールドのみ） |

実機ログで見えていたのは前者（アプリログに出る子プロセスの出力）。
★ **フロントには送信実績が 1 バイトも届いていない** ので、
「`sent` の増分を検出する」には**まず配線を足す**必要がある。

## 実装アプローチ

★ **レシートの根拠を「収束器が `.sent` を置いた事実」に固定する。**
`.sent` はアップロードが `Ok(())` を返したときにだけ置かれる (`reconcile.rs` の設計核 ③)。
これが端末から手に入る**最も強い証拠**である。ボタン押下や `awaiting_approval` の
減少を根拠にすると **偽のレシート**になる（今回いちばん避けたい形）。

配線は既存の経路に**足すだけ**にする:
`gse-submit --reconcile` → `GSE_RECONCILE {…"sent":N…}` →
`run_reconcile_blocking` が既に `summary_count()` で読める → ★ ここで静的変数に記録 →
`get_submission_status` が返す → 既存の 3 秒ポーリングが拾う。

⚠️ 新しいイベント経路を作らない。`reconcile` はイベント駆動を意図的に避けた設計 (`reconcile.rs` §0)。

## 変更対象

### 修正するファイル

- `src-tauri/src/lib.rs`
  - `SUBMIT_LAST_SENT_MS: AtomicU64` — 最後に **1 件以上送れた** 時刻 (epoch ms、0 = 未達)
  - `SUBMIT_LAST_SENT_COUNT: AtomicU64` — そのとき送れた件数
  - `SUBMIT_IN_FLIGHT: AtomicU64` — 走っている収束器の本数（0 でなければ送信中）
  - `run_reconcile_blocking`: 要約行の `sent` が **> 0 のときだけ**上記 2 つを更新する
    （★ exit code に関係なく更新する。部分成功 = 「送れた分は送れた」を捨てない）
  - `spawn_reconcile`: `run_reconcile_blocking` の前後で in-flight を増減する
    （⚠️ 「ブロック実行中なので見送る」早期 return **より後**で増やす。見送りは送信中ではない）
  - `SubmissionStatusDto` に `sending: bool` / `last_sent_ms: Option<u64>` / `last_sent_count: usize`

- `src/App.tsx`
  - `SubmissionStatus` interface に 3 フィールドを追加（backend と同期）
  - 送信中カード（新規）／レシートカード（新規）／未送信カードの表示条件に `!sending` を追加

### 新規作成するファイル
- `scripts/tests/submission-receipt-view.html` — ★ 実マウント検証ハーネス
  （`__TAURI_INTERNALS__` shim で `invoke` を差し替え、**実 CSS に対して**各状態を描かせる）

### 削除するファイル
- なし

## 表示仕様（★ 排他の順序を決める）

スタート画面 (G1 モード) で上から:

| 条件 | 表示 |
|---|---|
| `awaiting_approval > 0` | （既存）緑「このブロックの記録を送信しますか？」 |
| `sending && unsent > 0` | ★ 新「⏳ 記録を送信しています…（数秒かかります）」 |
| `unsent - awaiting > 0 && !sending` | （既存）オレンジ「まだ送れていない記録が N 件」 |
| `awaiting == 0 && !sending && last_sent_ms != null` | ★ 新「✅ この回の記録を送信しました（HH:MM・N 件）」 |
| `awaiting == 0 && !sending && unsent == 0 && last_sent_ms == null` | ★ 新「✅ 送信を待っている記録はありません」 |

- ⚠️ ★ **`awaiting_approval > 0` の間はレシートを出さない。**
  出すと、次のブロックが終わって確認待ちになっている画面に
  「この回の記録を送信しました」が並び、★ **まだ送っていない回の偽レシート**に読める。
  隠しておけば、レシートが見えている時の「この回」は**必ず直近のブロック**を指す。
- ⚠️ ★ 未送信カードは `sending` の間は出さない。
  文面が「次のブロックの後に自動で送信を再試行します」なので、
  ★ **いま送っている最中**に出すと嘘になる。
- ⚠️ `last_sent_ms` が在って `unsent > 0`（部分成功）のときは
  レシートと未送信カードが**両方**出る。これは正しい（「1 件送れた / 1 件残っている」）。

## 影響範囲

- ⚠️ `SubmissionStatusDto` はフロント専用の DTO で、`schema_dto.rs`（NDJSON schema）とは無関係。
  → **schema parity check には影響しない**。
- 通常運用 (`g1_mode() == None`) では `spawn_reconcile` が即 return するため、
  静的変数は初期値のまま・UI は `!!g1Mode` gate の中なので **1 バイトも変わらない**。

## 既存パターンとの整合性

- 静的変数 + `get_submission_status` での取り出しは `SUBMIT_LAST_ERROR` /
  `SUBMIT_UPLOAD_DISABLED` と**同じ形**（既存 2 つに 3 つ目を並べるだけ）。
- カードの見た目は既存 3 種（緑 `#4caf50` / オレンジ `#ffa726` / 赤 `#ff6b6b`）に合わせる。
- ⚠️★ ボタンと同じく、**文字色を明示する**（`color` は継承されない・2026-08-08 の教訓）。

## テスト戦略

- 単体テスト (`lib.rs`):
  - 要約行の `sent` を読む純関数のテスト（`summary_count` 経由・0 件では更新しない）
  - `sent > 0` で時刻と件数が更新され、`sent == 0` では**据え置かれる**こと
- 実マウント検証（★ 機械検査では見えない層）:
  - `npm run dev` + shim で 5 状態すべてを描かせ、
    `getComputedStyle().color` と背景の**輝度差を対照つきで測る**
  - ⚠️ tsc は色を見ない。スクショだけでも見ない（印象で判断しない）
- `cargo test --workspace --features package`（⚠️ `--features package` が無いと
  `packaging` の 23 件が走らない = 315 件しか出ない）

## ロールバック計画

`lib.rs` の 3 変数と `App.tsx` の 2 カードを消せば元に戻る（既存表示に手を入れていないため、
未送信カードの `&& !sending` を外すだけで旧挙動に戻る）。
