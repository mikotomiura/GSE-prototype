# 前提条件 8（計器の未完了/離脱対応）＋ T3 人単位台帳の仕様化 ＋ consent.md 文言の整合

> 作成: 2026-09-27。grill（Opus・本セッション）で判断分岐を閉じた結果。
> 一次: `experiments/20260801-controlled-friction-task/preregistration.md` 第 20 版
> 「9 マス」(i)(ii)(iii) / 「公表物の書き方」/ `§3.9` / `§2.13-1b`、
> `.steering/20260927-o1-receipt-ledger/{t3-person-ledger-design.md, t2-record-a-draft.md}`、
> `docs/o1-deletion-ledger.md`。

## 背景

第 20 版（2026-09-26）は「途中でやめた人・削除を求めた人・1 つも開始していない人」の数え方を
**文書としては**確定したが、⚠️ **計器（`validate_blocks.py` / `analyze.py`）の挙動を 1 行も変えていない**。
第 20 版自身が「本版が**していないこと**」節で次を明記している（一次・`preregistration.md:70-75`）:

1. `validate_blocks.py` は一部のブロックだけ `file` が埋まった割付を **記入漏れとして FAIL** にする
   → **未完了者の割付ファイルは現状 FAIL になる**（`validate_blocks.py:233-245` で確認）。
2. `analyze.py:196-200` は `len(conf) < n_subjects` で**無条件 NG**
   → 削除・離脱で名簿が縮むと **確証解析そのものが走らない**。
3. 「登録 k 名・解析 m 名」の併記が実装されていない。
4. **G1 の人単位の記録破棄手順が無い**（O1 には `docs/o1-deletion-ledger.md` がある）
   → `consent.md §5`「後からデータの削除を求められます／すでに送信されたものも対象」が
   **履行不能になりうる**。

⚠️★★★ 第 20 版は「⚠️ **本版の規則は、この挙動変更が済むまで実行できない**」「**最初の参加者を
走らせる前に済ませるべき**」と書いている。→ これを **前提条件 8** として実施する（研究者決定）。

併せて、2026-09-27 の `checkConsentFormParity` 実測（`t2-record-a-draft.md`）で判明した
**consent.md と配布済みフォームの文言の食い違い 3 点**を、md 側をフォームに合わせる向きで直す。

### ★ 本タスク着手時に測り直した事実（2026-09-27・一次）

| 何 | 実測 |
|---|---|
| `analyze.py` の n=1 対応 | ✅ **既に実装済み**。`fisher_combine` は `n<2` で `applied:false`（`analyze.py:590-594`）、`cohort_verdict` は `n_subjects_analysed` を出し `n==1` の caveat も付ける（`:880, :904-907`）。`selftest` が `§3.9` を固定（`:1291-1296`） |
| 未完了者の主判定 | ✅ **既に skip される**。`len(g1) != 8` なら `primary = {skipped, reason}`（`analyze.py:701-704`）。`cohort_verdict` は `skipped` を除いて数える（`:877`） |
| → A-2 で足りないもの | ① `:196-200` の門（収集完了を見分けられない）② 「登録 k」の明示出力。**それだけ** |
| 開始ゲートの機械痕跡 | ❌ **存在しない**。`preregistration.md §2.13-1b` 逐語「⚠️ ★ **何も保存しないので、閉じて開き直せば元に戻る**」→ 押下はどこにも残らない。→ 「開始していない」の機械判別は**構造的に不可能**で、第 20 版の「実験者の実施記録で確認する」しかない |
| `blocks/*.json` の追跡 | ❌ 追跡されない（`config.json` の `sample_roster._note` 逐語「blocks/*.json は gitignore 対象でこの端末にしか無い」）→ 人単位のラベルを置いても repo に載らない |
| 配布済み G1-C | ✅ コードと一致（2026-09-27 `checkConsentFormParity`: 同意項目 8 件・順序一致・説明文完全一致）→ ⚠️ 「配布済みは古い文言のまま」と書く **3 箇所が古い** |
| G1 ゲート | 通過 17 / 未達 3（記録票 A/B/C のみ）。検査 [7] は緑だが逐語で「⚠️★★★ 緑でも**計器は未対応**」と注記している |
| O1 ゲート | 通過 22 / 未達 2（リリースタグが 5 コミット古い・本タスク範囲外） |

## ゴール

**計器が第 20 版の規則を実行できる状態にし、G1 の削除保証を文書として成立させ、
consent.md を配布済みフォームと整合させる。**

### Done（機械で言える形）

1. `cd src-tauri` 不要 —— 本タスクは Python / md のみ。以下がすべて exit 0:
   - `python3 experiments/20260801-controlled-friction-task/validate_blocks.py --selftest`
   - `python3 experiments/20260801-controlled-friction-task/analyze.py --selftest`
   - `bash scripts/check-g1-collection-readiness.sh`（★ **未達 3 件は記録票 A/B/C のみ**に減る。
     新設する削除台帳の検査が緑であること）
   - 各 issue の `*-acceptance.sh`
2. `validate_blocks.py` が **未完了・未実施の割付を FAIL にせず NOTE で報告する**
   （⚠️ ただし `participation_status` が無い割付の部分記入は**従来どおり FAIL**＝転記ミス検出を失わない）。
3. `analyze.py` が **収集完了フラグが立っているときだけ** n 未達で止まらず、
   **登録 k / 解析 m を分けて出力する**。`m=0` なら NG のまま。
4. `docs/g1-deletion-ledger.md` が存在し、`consent.md §5` の約束を履行する経路を網羅している。
5. `docs/person-lifecycle-ledger-template.md`（T3 の構築仕様書）が存在し、
   列定義・数式・矛盾検知 4 件・ダミー P-ID での赤/黄/緑の確かめ方を持つ。
6. `consent.md` / `protocol.md` / `Form_G1/README.md` の**差分案**が提示されている
   （⚠️ **最終反映＝コミットは研究者承認後**。フォーム自体は書き換えない）。

### Stop（人にエスカレートする）

- `preregistration.md §3.6`（凍結・除外規則）に触れる変更が必要になったとき。
- `config.json` の `revision` / `design.n_subjects` / `§3.1/3.2/3.4/3.5/3.6` を変えたくなったとき
  （⚠️ `check_frozen_sections.py` が赤になる）。
- 被験者向け文書の**意味**（約束の範囲）を変える必要が出たとき。

## スコープ

### 含むもの

- **A-1**: `validate_blocks.py` に `participation_status` を読む報告専用の検査を足す。
- **A-2**: `analyze.py:196-200` の門を `sample_roster.recruitment_closed` で分岐させ、
  `registered_k`（登録 k）と `analysed_m`（解析 m）を出力に足す。
- **A-3**: `docs/g1-deletion-ledger.md` を新設（O1 版と同型）＋
  `scripts/check-g1-collection-readiness.sh` に存在検査を 1 件足す。
- **B**: T3 人単位ライフサイクル台帳の**構築仕様書**を repo に置く（数式・入力規則・矛盾検知）。
- **C**: `consent.md` §3 / 同意欄 / 状態表、`protocol.md §4.1-1`、`Form_G1/README.md` の**差分案**。

### 含まないもの（★ やらないこと）

- `preregistration.md` の**改訂**（第 21 版を作らない）。⚠️ 本タスクは「第 20 版の規則を実行する計器」を作るだけ。
  ★ ただし `analyze.py` の `PREREG_REVISION` は **20 のまま**（版を上げない）。
- `config.json` の `revision` / `n_subjects` / 凍結節の変更。
- **実データの入力**（T3 台帳への実 P-ID・状態）。
- **実物のスプレッドシート作成**（Chrome での作成と赤/黄/緑の実測は**別タスク**・要研究者同席）。
- consent.md / protocol.md / Form_G1/README.md の**最終反映（コミット）**と、
  **配布済みフォームの書き換え**（`migrateConsentForm()` / `setupG1Forms()` は実行しない）。
- G1 削除保証の**自動化実装**（今回は手順の文書化のみ）。
- O1 リリースタグの更新（ゲート未達 2 件のうち 1 件。別タスク）。
- 記録票 A / B / C の記入（研究者が行う）。

## 受け入れ条件

- [ ] `validate_blocks.py --selftest` 緑。★ 新規に**陽性対照つき**のケースが入っている
      （status 無し＋部分記入 → FAIL のままであることを固定する negative control）
- [ ] `analyze.py --selftest` 緑。★ `closed=false` で NG・`closed=true` かつ m≥1 で続行・
      `m=0` で NG の 3 状態を固定する
- [ ] `bash scripts/check-g1-collection-readiness.sh` の未達が **記録票 A/B/C の 3 件のみ**
- [ ] `docs/g1-deletion-ledger.md` が `consent.md §5` の 3 対象（ローカル NDJSON・Drive の `.age`・
      集計の中間物）と**紙の記録用紙**・**同意の正本（フォーム回答シート）**を網羅
- [ ] `docs/person-lifecycle-ledger-template.md` が設計 §2.2-2.4 の 3 タブと矛盾検知 4 件を逐語で持つ
- [ ] consent.md ほか 3 文書の差分案が `.steering/.../consent-diff-proposal.md` にある（適用はしない）
- [ ] ⚠️ **repo に人単位の未完了/削除ラベルを追加していない**（`git diff` を grep して確認）

## 関連ドキュメント

- `experiments/20260801-controlled-friction-task/preregistration.md` 第 20 版（9 マス・公表物の書き方・§3.9・§2.13-1b）
- `docs/o1-deletion-ledger.md`（G1 版の型）
- `.steering/20260927-o1-receipt-ledger/t3-person-ledger-design.md`（T3 設計・研究者裁定済み）
- `.steering/20260927-o1-receipt-ledger/t2-record-a-draft.md`（consent.md ⇔ フォームの差異）
- `docs/loop-engineering.md`（モード C で実行する）

## 運用メモ

- /reimagine 適用: **No**
- 理由: 設計分岐は grill（本セッション・Opus）で研究者が全件裁定済み。代替案は
  `decisions.md` に却下理由つきで記録してあり、初回案を破棄して再生成する余地が無い。
