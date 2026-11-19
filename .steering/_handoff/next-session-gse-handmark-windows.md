# 引き継ぎ —— 手跡の Windows 版（ADR-051 D1・ADR-050 の条件 (a)）

> **使用済み（2026-11-19）**: このメモから `.steering/20261119-handmark-windows/`（枝 `feature/handmark-windows`）を始め、PR #428 で main に入れた（merge 2f39fcbf）。CI の無料分が尽きていたので、研究者の決定で self-hosted の check（G-GEAR・Mac）の緑と、手元の frontend-check 全 37 段の緑で merge した（frontend-check は無料分が戻ったら main で回し直す）。同じ日に CI の負荷を軽くする PR #429（`.steering/20261119-ci-selfhosted-light/`）も入れた。

> 作成: 2026-11-08（`.steering/20261108-handmark-to-main-plan/` 判断 P）。研究者「とりま mac だけ入れといて、windows は適宜作ってから入れる感じにしよう」。Windows 版の手跡は、まだ何も書かれていない。このメモは、ばらばらにあった材料を集めたものである。
>
> 始めるきっかけ: 確認の段の参加者に Windows の人がいると分かったとき。または研究者が始めると決めたとき。

## 入口の文

```
/Users/johnd/GSE-prototype/.steering/_handoff/next-session-gse-handmark-windows.md を読んで、手跡の Windows 版の実現の確かめを /start-task から始めて。
```

## 材料の在り処（2026-11-08 に grep で集めた・どれも main には無い）

| 何 | 在り処（枝 `docs/tangibility-design` の `.steering/_handoff/`） |
|---|---|
| 壁紙の層（WorkerW など）・タスクバー・最前面の透過窓が候補で、試していない | `next-session-handmark-window-boundary.md` 48・58・70 行 |
| WorkerW は非公開で、24H2 で Lively が作り直しを要した [V284]。取り込みからの除外の API はトップレベルの窓だけ [V283]。Windows で背景の層が成り立つかを確かめるタスクは無い | `next-session-handmark-expression-design.md` 29・31・45 行 |
| `GetCursorPos`・`GetAsyncKeyState` は実測していない。ホイールは Raw Input の受け先を O1 の `observe_windows.rs` と奪い合う | `next-session-handmark-input-adr.md` 34・43 行、`next-session-handmark-stage-pointer.md` 52 行 |
| ADR-050 D6・D7（Windows の読み方・ホイールは使わない）と補訂 1 の冒頭の条件 (a) | main の `docs/adr/ADR-050-handmark-input-not-recorded.md` |
| EH3 の肖像の壁紙は、Windows で `IDesktopWallpaper` を使う（動かない壁紙の先例） | main の `src-tauri/src/wallpaper_*.rs`・`analysis/portrait/` |

## 確かめること（順に）

1. 背景の層を Windows でどう出すか。候補は 3 つ。
   - WorkerW の下に窓を差し込む。
   - 最前面でクリックを通す透過の窓。
   - 動かない壁紙の更新（`IDesktopWallpaper`）で代える。ただし、動かないので手跡の性質が変わる。
   
   それぞれ、24H2 での成り立ち・画面共有に写るか・CPU を測る。
2. 帯をタスクバーの上に出せるか（全画面・自動で隠す設定・多画面）。
3. ADR-050 の条件 (a): `GetCursorPos`・`GetAsyncKeyState(VK_LBUTTON)` を、権限なしで描画のたびに読めるか。キーボードの仮想キーを読まないことを検査に入れる（ADR-050 D3 の末尾）。
4. ホイールは使わない（ADR-050 D7）。

## 進め方

- Windows 機の Claude Code には収集だけを頼み、直すのは文脈を持つ側で行う（memory: windows-agent-collection-only）。陽性対照を要求する。
- Windows 固有のコードの検査は CI だけである（macOS の手元では `*_windows.rs` が 1 行もコンパイルされない・memory: windows-only-code-needs-ci）。両 OS に対のテストを置く。
- G-GEAR は 11 月いっぱいふさがっている。職場の PC（HP Z2 G9）でもよい（memory: workpc-hp-z2-for-research）。
- Windows 版が入るまで、Windows の参加者の「あり」の日は、日ごとの行に「出せなかった理由」を書く（ADR-051 D1）。その日を解析でどう扱うかは、事前登録の改訂で決める。
