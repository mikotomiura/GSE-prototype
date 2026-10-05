# 判断の記録

## 判断 1: 直す消費者と直さない消費者（2026-10-05・G-GEAR・メインの選択・研究者が覆せる）

grep（`公開 ?API が(存在しない|無い|ない)`・`公開の API が無い`・`no public interface` などを `docs/`・`.claude/`・`.steering/`・`src-tauri/src/`・`AGENTS.md` で）の結果:

| 場所 | 扱い | 理由 |
|---|---|---|
| `docs/agent-shared.md` 制約 7 の末尾 | **直した** | 引き継ぎの指定。Codex も読む共通文書。⚠️ 最小にしたかったが、レビュー（判断 4）で content-free の但し書きと「未決」を足した |
| `survey-input-channels.md` §3.2・§7.5・§7.6 | **直した** | 引き継ぎの指定。主張の出どころ |
| `docs/architecture.md`「IME 状態機械」 | **直した** | 「WinEvent に相当する IME イベント通知がない」は現行の説明で、アプリしだいの通知まで無いと読める |
| `docs/architecture/workspace-behavior-observation.md` 83 行 | **注を足した**（2 巡目で変更・判断 4） | 「他プロセスの IME composition は原理的に不可能」に「アプリを問わない経路としては」の注。分類（原理的に不可能）は変えていない |
| ⚠️ `src-tauri/src/input/ime_compose.rs` 16 行 | **直さない**（初版で直し、レビューで戻した・判断 4） | ⚠️ IME 論文の kit `papers/ime-observation/kit/logger/src/input/ime_compose.rs` がこのファイルの**逐語コピー**で、`PROVENANCE.internal.md` が「1 バイトも変えない」、`manifest.json` の `ime_compose` が SHA-256 を記録し、`check_manifest_upstream.internal.py --against-upstream` が照合する（凍結のタグに入っている）。コメントの言い過ぎより、凍結のロガーと上流のバイトの一致を優先する。文の訂正は `survey §7.5` が持つ |
| `docs/adr/ADR-036…md` 68 行 | 直さない | ADR の本文は書き換えない規約。「同節が『公開 API が存在しない』とする」は当時の引用として正しく、旧文は agent-shared の訂正の行でたどれる。⚠️ ただし判断 2 |
| `.steering/` の過去の記録（`20260821…/decisions.md` 359 行・`20260911…` の tasklist と issue 008・IME 論文の attack-me の context-B・`design.md`・`design-v1.md`・`paper-suggest.md`） | 直さない | その時点の記録。IME 論文の steering は論文の枝が持つ（判断 151 で外枠と節は直した） |
| `docs/mitou_submission/…技術設計書.docx.md` | 直さない | 提出した文書の写し |
| 凍結した事前登録（`papers/ime-observation/experiment/preregistration.md` §1.1）・kit の `ime_compose.rs` | 直さない | 凍結物。原稿の注で扱う（IME 論文の判断 151） |

## 判断 2: 研究者に渡す 4 点（直さず記録する）

1. **ADR-036 の (a)「確定イベントそのものの時刻を取る経路」**: macOS の `NSAccessibilityTextInputMarkingSessionEnded` は、
   それを出すアプリ（WebKit のソースは出す）では変換の終わりの通知の**候補**になりうる。⚠️ ただし終了の通知が確定・取消・フォーカスの喪失を
   区別するか、通知の受信の時刻と確定の時刻のずれは確かめていない（Codex の指摘・判断 4）。ADR-036 の結論「現実的な選択肢としては残っていない」は
   *アプリを問わない* 経路としては今も成り立つ。アプリしだいの経路を候補に入れるかは研究者が決めること。⚠️ その経路は範囲（文字数の量）と
   同じ要素・同じ権限で文字列を返す属性に届くので、`data-privacy` の論点になる（採るなら別 ADR が先）。
2. **`workspace-behavior-observation.md` の分類**: 注は足したが、「原理的に不可能」の分類そのもの（アプリを問わない経路に限るか）は設計文書の判断なので変えていない。
3. **上流の `ime_compose.rs` のコメントの言い過ぎ**（判断 4・5）: kit の照合（`check_manifest_upstream.internal.py --against-upstream`）が作業ツリーの上流と比べるので、
   このタスクでは直さなかった。照合を凍結の commit に固定すれば上流のコメントを直せる（Codex 2 巡目）—— IME 論文のタスクで研究者が決める。
4. **`data-privacy` Skill の凍結表**（security-checker の LOW・このタスクの範囲外）: ルール 7 の表に macOS の Accessibility の文字列を返す属性
   （`kAXValueAttribute`・`kAXStringForRangeParameterizedAttribute` など）が載っていない。この経路を採るかを決めるときに、禁止の行を足すかも決める。

## 判断 3: [Vn] は `docs/` に書かない（2026-10-05・メインの選択）

[V206]・[V224]・[V225] は IME 論文の枝（`docs/ime-manuscript-outline`・未 merge）の `docs/references.md` にあり、main には無い。
`check_citations.py` は `docs/` の本文の `[Pn]`/`[Vn]` が `references.md` にあるかを見るので、この枝が先に merge されると赤になる。
→ `docs/` では文書名で引き（制約 7 の既存の書き方と同じ）、番号は `.steering/` の調査メモにだけ「IME 論文の枝で登録」と添えた。
却下案: 論文の枝の `references.md` の 46 行をこの枝へ cherry-pick する（このタスクに関係しない 40 行以上を持ち込み、両枝の結合を強める）。

## 判断 4: 完了時レビュー（code-reviewer ∥ security-checker ＋ Codex）の採否（2026-10-05・メインの選択・研究者が覆せる）

`51d76ffe` に対して 3 本を並列に回した（code-reviewer 約 5.7 分・security-checker 約 2.2 分・Codex 1 回）。指摘はすべて一次で裏取りした。

| 出どころ | 指摘 | 裏取り | 対応 |
|---|---|---|---|
| code-reviewer HIGH | `ime_compose.rs` は kit の逐語コピーで、コメントを変えると上流との照合が赤になる | `PROVENANCE.internal.md` 10 行「1 バイトも変えない」・`manifest.json` の `ime_compose`（`upstream_path`）を確認 → **真** | 戻した（`cf320319` と同じバイト）。判断 1 |
| code-reviewer MEDIUM | 「公開の経路は見つかっていない」は、同じ §7.5 の候補窓のポーリング（アプリを問わない公開の経路）と食い違う。差は「通知」 | §7.5 の表の「候補ウィンドウの検知」の行 → **真** | 「アプリを問わずに変換を知らせる公開の通知」にそろえ、候補窓は通知ではないと添えた |
| code-reviewer MEDIUM ・security-checker MEDIUM | `agent-shared.md` に `NSTextView` 未確認と content-free の但し書きが無い。「頼らない」が決まったことのように読める | 差分 → **真** | 3 点を足し、「使うかは未決・研究者」にした |
| Codex P2 | 「WebKit は出す」の根拠が写しのコードだけで、発火の経路を示していない | WebKit を同じ commit で追加取得: `AXObjectCache.cpp` 3692〜3719 行が変換の開始・終了で投げる（`HAVE(INLINE_PREDICTIONS)`・`PlatformHave.h` 1326〜1331 行が Mac で 1）・呼ぶのは `Editor.cpp` → 発火のコードはある。実機で受け取れるかは未確認 → **部分的に真** | 「ソースは出す」と発火の経路を書き、「実機で別のプロセスが受け取れるかは確かめていない」を足した |
| Codex P2 | 判断 2-1 の「終わりの時刻を知らせうる」は意味論（確定・取消の区別・遅れ）が未確認 | Apple の頁に説明の文が無い → **真** | 「候補」に弱め、未確認の 2 点を書いた |
| Codex P2 | `workspace-behavior-observation.md` の過大な断定を据え置くと誤判断を再生産する | 83 行 → **真** | 注を足した（分類は変えない） |
| Codex P3・security-checker LOW | 「同じ API に文字列を読む属性がある」だけでは通知の経路の content-free を否定できない。範囲（位置と長さ）は文字数の量 | `AXObjectCacheMac.mm` 375 行は userInfo `nil` で投げる・範囲は `NSValue valueWithRange` → **真** | 「通知そのものは文字列を運ばない・範囲は文字数の量・同じ要素と権限で文字列の属性に届く → 採るなら呼ばない属性を能力で書く」に直した |
| code-reviewer LOW | Obj-C の名・受ける側は C の `AXObserver` | JSON の `navigatorTitle` → **真** | 足した |
| code-reviewer LOW | §7.6 の本文の「0x8027-0x8030」の 0x8030 はアプリしだいの側 | §7.4 の前提 1 → **真** | 注に足した |
| code-reviewer LOW | 判断 151・153 は main に無い | `git show origin/main:` の decisions.md は 143 まで（レビューの報告）→ 枝の違いとして**真** | 「枝 `docs/ime-manuscript-outline`・merge の前に確かめ直す」を添えた |

- 偽陽性 0。code-reviewer が確かめられなかった「macOS 10.6」と C の数はメインが一次（各頁の JSON の `introducedAt`・C の一覧の JSON）で確かめ済み（design.md）。
- Codex の 1 回は 84,173 トークン（台帳 `.codex/budget.json` の today 21,212 → 105,385・2 回）。

## 判断 5: Codex の 2 巡目（足した文の境界条件・`51d76ffe..c3f97264`）の採否（2026-10-05・メインの選択・研究者が覆せる）

| 指摘 | 裏取り | 対応 |
|---|---|---|
| P2: `workspace-behavior-observation.md` の注は「経路」と広く、「調べた範囲で見つからない」は不可能の証明ではないのに分類は「原理的に不可能」のまま | 83 行・§7.5 → **真** | 注を「言い過ぎの疑い・調べた範囲で見つかっていないだけ・分類を変えるかは研究者（判断 2）」に直した。分類そのものは変えない（設計文書の判断） |
| P2: content-free の基準が OS で揃っていない（Windows は引数、macOS は権限で判定）。通知の中身・範囲・受ける側の実装を分けよ | 自分の §7.5 の文 → **真**（通知だけの構成まで不当に排除していた） | §7.5 を 3 つ（通知の中身・範囲の属性・受ける側の実装）に分けて書き直し、agent-shared.md は「通知そのものは文字列を運ばない・範囲を読めば文字数の量」にした（権限の議論を外した） |
| P3: 凍結した kit のバイトの保持と、上流のコメントの訂正は、照合を凍結の commit に固定すれば両立する | `check_manifest_upstream.internal.py` の照合先は作業ツリーの上流（レビューの報告・判断 4）→ 指摘の前提は**真** | このタスクでは戻したまま。照合を凍結の commit に固定して上流を直すかは、IME 論文のタスクの研究者の判断に回す（判断 2 に足す） |

- Codex の 2 回目は 26,754 トークン（today 105,385 → 132,139・3 回）。3 巡目は回さない（指摘は文の言い方で、直した箇所は 2 巡目の指摘の範囲だけ）。
