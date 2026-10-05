# 次セッション（小さな別タスク）— GSE 本体の「macOS は公開 API が存在しない」を一次に戻して直す

> 作成: 2026-10-05（G-GEAR・IME 論文の結果を待たない節を書いたセッション）。研究者の選択は `.steering/20260927-ime-observation-paper-eval-design/decisions.md` の **判断 151-2**（「この枝に混ぜず、別の小さなタスクで直す」）。
> ⚠️ **このメモを一次資料にしない。** 一次は下の §1 の 3 つ。着手時に `git fetch` し、`main` から新しい枝（例 `docs/macos-ax-marked-text-correction`）を切る。⚠️ 作業ツリーには別の枝の未コミット作業がある → `git add` はパス指定（`-A` 禁止）。並行セッションがあれば `git worktree`。

## §0 打ち込む用

```
git fetch → main から枝 docs/macos-ax-marked-text-correction を切る。
.steering/_handoff/next-session-gse-macos-ax-correction.md を読んで §2 から始めてください。
一次は decisions.md の判断 151、docs/references.md の [V206]（WebKit のソース）・[V224]〜[V229] 付近（Apple の Accessibility の定数の一覧。番号は references.md で確かめる）。
/start-task で .steering を作る。Skill: verify-before-claiming・citation-ssot・git-workflow。応答は日本語。
⚠️ 既存の文の「結論」を勝手に変えない —— 直すのは「macOS には公開 API が存在しない」という事実の言い過ぎだけ（memory「古い記述は一次へ戻す」）。設計の結論（打鍵から推す・アプリを問わない経路を使う）を変えるかは研究者の判断。
```

## §1 何が違っていたか（一次）

1. **Apple の AppKit の Accessibility の定数**（`https://developer.apple.com/documentation/appkit/nsaccessibility-swift.struct/attribute`・`…/notification`）に、**`textInputMarkedRangeAttribute`**（変換中の範囲）と **`NSAccessibilityTextInputMarkingSessionBegan` / `…Ended`**（変換の開始・終了）がある。3 つとも macOS 10.6 から・説明の文は無い（2026-10-05 に JSON で取得）。
2. **WebKit のソース**（commit `1a5a134d14845e9bf54a67049a36a2585e62897c`）: `Source/WebCore/accessibility/mac/AXObjectCacheMac.mm` 361〜366 行が変換の開始・終了を 2 つの通知に写し、`WebAccessibilityObjectWrapperMac.mm` 2290〜2295 行が変換中の範囲を `NSRange`（位置と長さ・文字列なし）で返す。
3. 内部の調査メモ `.steering/20260821-workspace-behavior-triage/survey-input-channels.md` §7.5 の「Attributes 101 ＋ Parameterized 9 ＋ Notifications 25 = 135 個でゼロ」は **C（Carbon）の定数だけ**を数えていた（2026-10-05 も同じ数・該当なし）。AppKit の定数（属性 132・パラメータ付き 19・通知 43）は見ていなかった。

## §2 やること

1. 消費者を洗う（verify-before-claiming ルール 2）: `grep -rn "公開 API が存在しない\|公開 API が無い\|no public interface\|no public API" docs/ .claude/ .steering/ src-tauri/src/ papers/ --include=*.md --include=*.rs` などで、同じ言い過ぎを持つ箇所を全部出す（⚠️ `papers/` の凍結物＝事前登録は**変えない**。原稿の側は判断 151 で済んでいる）。
2. 直す候補: `docs/agent-shared.md` の技術的制約 7 の末尾「詳細と macOS 側（**公開 API が存在しない**）は…」、`survey-input-channels.md` §3.2・§7.5・§7.6 の表、`src-tauri/src/input/` の doc コメント（あれば）、`CLAUDE.md`・Skill（`hook-constraints` など）にあれば。★ 直し方は「アプリを問わない公開の経路は見つかっていない。アプリが用意する Accessibility の経路（範囲の属性・開始・終了の通知）はあり、WebKit は出す（AppKit の NSTextView が出すかは未確認）」。
3. ⚠️ `docs/agent-shared.md` は Codex も読む共通文書 → 変更は最小にし、詳細は調査メモの側に書く。
4. citation-ssot: 新しい出典は増えない（[V206]〜 を引く）。`python scripts/check_citations.py` を回す。
5. 完了時: code-reviewer ∥ security-checker ＋ /cross-review（パス限定）→ 出荷フロー（git-workflow ルール 6）。⚠️ Mac の計測が終わっていなければ PR を出さず push だけ（memory「計測中は PR を出さない」）。
