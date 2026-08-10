# block07 で露見した「1 ファイル 2 セッション」を検出側で塞ぐ

## 背景

2026-08-10、実参加者 P010（Windows・来所）が G1 を 10 ブロック通しで実施した。
復号と検証の一次記録は
`experiments/20260801-controlled-friction-task/notes.md §10`。

10 ブロック中 **block07 だけ**が `protocol.md §1`「1 ブロック = 1 セッション」を破っていた。

```
session_start   n=2   （他の 9 本はすべて n=1）
```

経緯（★ すべて実測・`notes.md §10-3`）:

1. 17:51:17 「開始する」→ ⚠️ **3 分 17 秒のあいだ打鍵が 1 件も記録されない**
2. 17:53:46 starved 120,077 ms で `HookHealth::Down` → `HOOK_STARVED` が立ち、
   ★ トレイが「⚠ 計測できていません」に変わる（`tray.rs:65-70`）+ rehook
3. 17:54:35 復帰（peak starved 165,312 ms）。散発的に 36 打鍵
4. 17:55:45 ★ **参加者がもう一度「開始する」を押した**
   （`start_session` の呼び出し元は `App.tsx:478` の押下ハンドラだけ）。
   ⚠️ 5 分の自動終了が来る**前**だった
5. → 5 分タイマーが引き直され（`lib.rs:2019`）、268.5s + 300s = 568.5s。
   実際の `session_end` は 569.05s で**一致**する
6. その 4:44 で **1387 打鍵** — 他 9 本と同等の健全なブロック

★ **8/09 に入れた生存監視は仕事をした。** 8/09 の事故（5 分 0 打が「● 計測中」のまま
自動提出された）と違い、今回は表示が変わり、記録が残り、参加者が対処できた。
⚠️ 残った穴は **「対処の結果が 1 ファイルに 2 セッションとして積まれた」**ことである。

### ⚠️★ なぜ「検出側」の問題なのか

アプリ側の非対称が原因ではあるが（`engine.reset()` も 5 分タイマーも押し直しで引き直されるのに、
ファイルだけ引き直されない = `lib.rs:1973` の `!was_active` 条件）、
★ **今回はアプリを変えない**（研究者判断）。P010 と以後の参加者が同じバイナリで走ることを優先する。

⚠️★★ **問題は、この破れを検出する仕組みが 2 つとも素通りしたこと**である:

1. `validate_blocks.py` の hook 検査は「`alive=false` **かつ** key 行 0」の AND なので、
   第 2 セッションの 2846 行が key>0 側に効いて **FAIL にならない**。
   しかも出た WARN の文面は「★ **誤検知の可能性が高い**（マウスのみの時間が 2 分続くと出る）」
   と述べており、⚠️ **本件を誤検知として片付けるよう読者を誘導する**。
2. `analyze.py` の `read_block`（`analyze.py:99`）は `session_start` 境界を**見ない**。
   このまま解析すると block07 は「1423 打鍵 / 6:00」として読まれ、
   ★ 失敗した試行の 36 打鍵と 3 分の空白が**黙って混入する**。

★ これは `protocol.md §1` が (b) を却下した理由「**沈黙して間違った結果を出す**」そのものである。

## ゴール

「1 ファイルに複数セッション」が **2 つの独立した検査で必ず露見し**、
解析が黙ってデータを混ぜないこと。

Done は exit code で言える:

- `python3 validate_blocks.py --selftest` → 0（新しい 2 ケースを含む）
- `python3 analyze.py --selftest` → 0（新しいケースを含む）
- ★ P010 の実データに対し `validate_blocks.py --dataset` が **block07 で FAIL を出す**
- ★ `analyze.py`（フラグ無し）が **P010 で止まる**、`--last-session-on-restart` 付きで通る

## スコープ

### 含むもの

- `validate_blocks.py`: `session_start` が 2 行以上あれば **FAIL**（`protocol.md §1` の直接検査）
- `validate_blocks.py`: `alive=false` + key>0 の WARN 文面を、誤読を誘わない形に直す
- `analyze.py`: `read_block` がセッション数を返す。解析経路は既定で **fail-loud**、
  `--last-session-on-restart` を明示したときだけ最終セッションを採り、結果に刻む
- `analyze.py --verify-blocks`: 再開始を**報告する**（★ 死なない・0 を返す）
- `preregistration.md`: 「複数セッションがある場合は最終セッションを採る」を**規則として凍結**
- 両スクリプトの `--selftest` に回帰ケースを追加

### 含まないもの

- ⚠️ **`src-tauri/` の変更**（`lib.rs:1973` のローテート意味論・`lib.rs:2001` の fail-loud・
  `meta` へのアプリ版刻印）。★ 研究者判断で今回は触らない。P010 と以後で版を分けない
- P010 の**解析そのもの**（`§3.4` の見る順序があるため、本タスクでは判定を出さない）
- block07 の**除外**。`§3.6` は事後除外を禁じている。本タスクは「どの行がそのブロックか」を
  決めるだけで、ブロックは落とさない
- 記録用紙との突き合わせ（`file` 列の出所検証・`notes.md §10-5`）

## 受け入れ条件

- [ ] `validate_blocks.py --selftest` が 0
- [ ] `analyze.py --selftest` が 0
- [ ] ★ 対照つきで確かめる: 1 セッションのログは緑のまま／2 セッションのログだけが赤
- [ ] P010 実データで `validate_blocks.py --dataset` が block07 を FAIL にする
- [ ] P010 実データで `analyze.py` がフラグ無しでは止まり、フラグ付きでは通る
- [ ] `--verify-blocks` は再開始を表示したうえで **0 を返す**（当日その場の対処を誘わない）
- [ ] `preregistration.md` に規則が凍結され、改訂履歴に「★ 結果を見る前に決めた」と残る

## 関連ドキュメント

- `experiments/20260801-controlled-friction-task/notes.md` §10（一次記録）
- `experiments/20260801-controlled-friction-task/protocol.md` §1（1 ブロック = 1 セッション）
- `experiments/20260801-controlled-friction-task/preregistration.md` §3.4 / §3.6
- `.claude/skills/verify-before-claiming/SKILL.md`

## 運用メモ

- /reimagine 適用: **No**
- 理由: 実装案は自明（既存の検査に 1 本足す + 既存の `--unseal` の刻印作法に揃える）。
  ★ 設計判断（アプリを触るか／規則を凍結するか）は本セッションで既に確定済み。
