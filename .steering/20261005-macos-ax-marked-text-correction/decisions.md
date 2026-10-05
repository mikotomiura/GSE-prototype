# 判断の記録

## 判断 1: 直す消費者と直さない消費者（2026-10-05・G-GEAR・メインの選択・研究者が覆せる）

grep（`公開 ?API が(存在しない|無い|ない)`・`公開の API が無い`・`no public interface` などを `docs/`・`.claude/`・`.steering/`・`src-tauri/src/`・`AGENTS.md` で）の結果:

| 場所 | 扱い | 理由 |
|---|---|---|
| `docs/agent-shared.md` 制約 7 の末尾 | **直した**（最小） | 引き継ぎの指定。Codex も読む共通文書 |
| `survey-input-channels.md` §3.2・§7.5・§7.6 | **直した** | 引き継ぎの指定。主張の出どころ |
| `docs/architecture.md`「IME 状態機械」 | **直した** | 「WinEvent に相当する IME イベント通知がない」は現行の説明で、アプリしだいの通知まで無いと読める |
| `src-tauri/src/input/ime_compose.rs` 16 行 | **直した**（コメントだけ） | 現行のコードの説明 |
| `docs/adr/ADR-036…md` 68 行 | 直さない | ADR の本文は書き換えない規約。「同節が『公開 API が存在しない』とする」は当時の引用として正しい。⚠️ ただし下の判断 2 |
| `docs/architecture/workspace-behavior-observation.md` 83 行 | 直さない | 理由 (a) が挙げるのは「他プロセスの **TSF** composition」（Windows）。macOS の言い過ぎではない。⚠️ 行の「他プロセスの IME composition は原理的に不可能」は、アプリが用意する経路（両 OS）まで含めると広い → 判断 2 |
| `.steering/` の過去の記録（`20260821…/decisions.md` 359 行・`20260911…` の tasklist と issue 008・IME 論文の attack-me の context-B・`design.md`・`design-v1.md`・`paper-suggest.md`） | 直さない | その時点の記録。IME 論文の steering は論文の枝が持つ（判断 151 で外枠と節は直した） |
| `docs/mitou_submission/…技術設計書.docx.md` | 直さない | 提出した文書の写し |
| 凍結した事前登録（`papers/ime-observation/experiment/preregistration.md` §1.1） | 直さない | 凍結物。原稿の注で扱う（IME 論文の判断 151） |

## 判断 2: 研究者に渡す 2 点（直さず記録する）

1. **ADR-036 の (a)「確定イベントそのものの時刻を取る経路」**: macOS の `NSAccessibilityTextInputMarkingSessionEnded` は、
   それを出すアプリ（WebKit を使うアプリ）では変換の終わりの時刻を知らせうる。ADR-036 の結論「現実的な選択肢としては残っていない」は
   *アプリを問わない* 経路としては今も成り立つが、アプリしだいの経路を候補に入れるかは研究者が決めること。⚠️ その経路は
   範囲から文字列を読む属性と同じ API にあり、WinEvent のように content-free が構造で保証されるわけではない（`data-privacy` の論点になる）。
2. **`workspace-behavior-observation.md` の「他プロセスの IME composition は原理的に不可能」**: 両 OS ともアプリが用意する
   Accessibility の経路があるので、「アプリを問わない経路としては」と限定するのが一次に近い。設計文書の言い方の変更なので、このタスクでは触らない。

## 判断 3: [Vn] は `docs/` に書かない（2026-10-05・メインの選択）

[V206]・[V224]・[V225] は IME 論文の枝（`docs/ime-manuscript-outline`・未 merge）の `docs/references.md` にあり、main には無い。
`check_citations.py` は `docs/` の本文の `[Pn]`/`[Vn]` が `references.md` にあるかを見るので、この枝が先に merge されると赤になる。
→ `docs/` では URL と文書名で引き（制約 7 の既存の書き方と同じ）、番号は `.steering/` の調査メモにだけ「IME 論文の枝で登録」と添えた。
却下案: 論文の枝の `references.md` の 46 行をこの枝へ cherry-pick する（このタスクに関係しない 40 行以上を持ち込み、両枝の結合を強める）。
