# 次セッション開始プロンプト — **Phase1 の GAS を repo に取り込み、O1 に足りない機能を洗い出す**

> ★ このファイルの「===」以下をコピペして開始する。
> ⚠️ 前セッションから `/clear` して**新セッション**で始めること。
> ★ モデル: **Opus**（⚠️ 「どちらを正本にするか」の判断が中心であり、取り違えると戻せない）。

---

===

## §0 ⚠️★★★ このセッションで最初に読むもの

1. `CLAUDE.md`（★ セッション開始時の行動規範 / 禁止事項 / `.steering/` の運用）
2. `.claude/skills/verify-before-claiming/SKILL.md`（★ **断定の前に実測する**）
3. `.claude/skills/browser-verification/SKILL.md` **§2.0a / §2.3 / §2.3b**
   （⚠️ タブが `hidden` だと入力が黙って落ちる ／ `monaco.getValue()` でハッシュ検証する ／
   ⚠️ リロードで関数セレクタが先頭に戻る）
4. `.claude/skills/data-privacy/SKILL.md`（⚠️ ロスターは **PII への直接ポインタ**）

## §1 ⚠️★★★ 何が起きているか（★ 2026-08-29 に実測）

| | 行数 | 関数 |
|---|---|---|
| repo `Form_Phase1/GSE_Phase1_Form_Builder.gs` | 1,969 | 41 |
| **GAS `GSE_検証フォーム(事前・事後)_Phase1`** | **3,095** | **84** |

★ プロジェクト ID: ⚠️ **ここには書かない**（security-checker MEDIUM・2026-08-29）。
★ `GSE_検証フォーム(事前・事後)_Phase1` を Apps Script のプロジェクト一覧から開き、
URL の `/home/projects/<ここ>/edit` を使う。⚠️ 実値を**追跡ファイルに書き戻さない**
（★ 秘密ではないが **PII への到達経路**であり、⚠️ 一度入れると履歴から消せない ——
起票 T-15 / T-21 と同じ形）。

⚠️ **GAS 側にしかない関数（★ 判明しているもの）**:
`sendReminders` / `reminderClassify_` / `reminderSend_` / `reminderConfirmPage_` /
`reminderRecordResponse` / `reminderHtmlPage_` / `reminderButtonUrl_` / `buildReminderLogTab_` /
`rosterHasPid_` / `doGet`（★ ウェブアプリ）

★ 裏取り済み: `Grep` で repo 全体に **1 件も無い**／`git log --all -S "sendReminders"` が **空**
（＝ **コミットされたことが一度も無い**）。

> ### ⚠️★★★ **絶対にやってはいけないこと**
> **repo の `Form_Phase1/GSE_Phase1_Form_Builder.gs` を GAS に貼らない。**
> ★ Apps Script が**唯一のコピー**であり、貼った瞬間に ~1,100 行が消える。
> ⚠️ Google Forms と違って Apps Script には版履歴があるが、**それに頼る設計にしない**。

## §2 ゴール（★ Done は exit code / 実測で言える形）

- [ ] GAS 上の全文が `Form_Phase1/GSE_Phase1_Form_Builder.gs` に入り、
      ★ **repo と GAS が SHA-256 で一致**する（⚠️ `monaco.getValue()` のハッシュで実測）
- [ ] ⚠️ 取り込んだコードに**秘密や PII が直書きされていないか**を検査
      （★ `bash scripts/check-o1-release-readiness.sh` の直書き検査は O1 のファイルしか見ていない。
      ⚠️ Phase1 にも同じ検査を広げるか、少なくとも目視して起票する）
- [ ] **T-25**（Phase1 の集計を凍結）を実装 → 貼り戻し → ★ 再度 SHA 一致を確認
- [ ] **機能の棚卸し表**が `.steering/[task]/design.md` にある（→ §4）
- [ ] `bash scripts/check-o1-release-readiness.sh` が **通過 16 / 未達 1** のまま（★ 悪化させない）

## §3 ★ 取り込みの手順（⚠️ 一次資料は GAS 側）

### 3-1. ★ 取り込み方は 2 つある。**clasp を推す**

```bash
# ★ 推奨: clasp（★ 全文を確実に落とせる。⚠️ 対話ログインが要る）
npx @google/clasp login          # ⚠️ 研究者が `! npx @google/clasp login` で実行する
npx @google/clasp clone <プロジェクト ID>   # ⚠️ ID は上記のとおり画面から取る
```

⚠️ clasp が使えないときの代替は **Claude in Chrome で `monaco.getValue()` を分割して取る**。
★ 120,825 文字あるので、**8〜10 分割**して 1 回ずつファイルに追記し、
⚠️ **最後に必ず全文の SHA-256 を GAS 側と突き合わせる**（★ 分割の取りこぼしは無音で起きる）。

### 3-2. ⚠️ 取り込んだあとに**必ず**やること

- [ ] `git diff` で「repo にあって GAS に無い」変更が**消えていない**ことを見る
      （★ repo 側が新しい部分があるかもしれない。⚠️ 一方向だと決めつけない）
- [ ] ⚠️ **秘密・PII の直書き**を探す（★ `PHASE1_MGMT_SHEET_ID` は T-21 で既知）
- [ ] 1 コミットで入れる（★ 「取り込み」と「T-25 の実装」を**別コミット**にする）

## §4 ★★ 本題: **Phase1 にあって O1 / G1 に無い機能**を洗い出す

> ★ 研究者判断 2026-08-29:「Phase1 にあった良い機能が O1 に整備されていない事態がありうるので、
> それらの確認もついでにやる」

★ 取り込みが終わったら、**3 つのビルダーの関数を突き合わせて表を作る**:

| 機能 | Phase1 | G1 | O1 | ★ O1 に要るか |
|---|---|---|---|---|
| **未提出者へのリマインダー**（`sendReminders`） | ✅ | ? | ❌ | ⚠️★★★ **要検討の筆頭** |
| リマインダーの応答記録（`reminderRecordResponse` / ログタブ） | ✅ | ? | ❌ | ? |
| ロスターの形式・重複検証（`validateRoster`） | ✅ | ? | ❌ | ★ T-24 で一部代替済み |
| 進捗ダッシュボード | ✅ | ❌ | ❌ | ⚠️ Phase1 は凍結する（T-25） |
| 定期実行トリガ（`installRosterRefreshTrigger`） | ✅ | ? | ❌ | ? |

⚠️★★★ **リマインダーは O1 の設計に直結する。**
★ O1 は「**ふだんの作業のあいだ、ずっと動いている**」ことで成り立つ研究であり、
受付メールも逐語で「**アプリが起動していない日は、記録がまるごと空になります**」と言っている。
→ ⚠️ **「昨日の提出がありません」を送る仕組みが無い**なら、
★ 欠測は**起きたあとでしか分からない**（⚠️ 事後に埋め合わせはできない）。

⚠️ ただし **送るかどうかは研究者判断**である（★ 介入になりうる ——
`docs/research-positioning.md` の「機会保存」と衝突しないか確認すること）。
→ ★ 表を作って**提案し、判断を仰ぐ**。⚠️ 勝手に実装しない。

## §5 ⚠️ スコープ外（★ 触らない）

- ⚠️★★★ **`Form_G1/` は 1 バイトも触らない**（★ G1 実施中）。
  ★ G1 の GAS プロジェクト（`GSE_Gate1_Form`）も**乖離しているかは未確認**。
  → ⚠️ **読み取りだけ**（ハッシュ比較）は行ってよい。**書き込みは禁止。**
- O1 のフォーム / トリガ（★ 2026-08-29 に配備完了。⚠️ 触ると被験者に影響する）
- 配布 zip（→ `next-session-prompt-o1-macos-distribution.md`）

## §6 ★ 関連する起票

- **T-26** repo と GAS の乖離を機械で検出する（→ `.steering/20260828-o1-gate-closeout-and-deployment/open-issues.md`）
- **T-21** 参加者ロスターの実 ID が `Form_G1` に直書き（⚠️ 履歴にも入っており repo では消せない）
- **T-25** Phase1 の集計を凍結（★ 本タスクで実装する）

## §7 ⚠️ 完了報告に必ず書くこと

- ★ 取り込み前後の **SHA-256**（GAS 側 / repo 側）
- ⚠️ **消えていないことをどう確かめたか**（★ 関数の数・行数・目視した差分）
- ★ §4 の棚卸し表と、**O1 に足すべきと判断した機能／その根拠**
- ⚠️ 判断を仰ぐ項目（★ リマインダーを送るか否かは研究者判断）
