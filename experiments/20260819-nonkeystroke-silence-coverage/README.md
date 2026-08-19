# 非打鍵タスクにおける沈黙の被覆率（形成的トラック）

> ⚠️★★★ **未実施。** 本ディレクトリには **事前登録のみ**が入っている。
> ★ Stage 0 は **G1 ログの提供待ち**、Stage 1 は **募集待ち**である。

## この実験は何か

⚠️★★★ **非打鍵タスクの「打鍵が沈黙している時間」は、content-free に取れるどの信号で、
どれだけ覆えるか** を実測する。

★ 目的は **superset（何を集めるか）を dev の推測ではなく実測で決めること**であり、
⚠️ **利得の推定ではない**（**形成的研究 = measurement development**）。

- 判断: **ADR-012**（形成的トラック・T3 の位置づけ変更）/ **ADR-013**（収集仕様の自己記述性）
- 上位タスク: `.steering/20260819-nonkeystroke-observation-space/`
- 事前登録: `preregistration.md`（★ **実データを見る前に凍結済み**）

## ⚠️★★★ 語彙の制約

**利得を主張する語を本ディレクトリの全文で使わない。**
⚠️★ **例外は 1 つだけ**: **先行研究の逐語引用**（[V83] の
`significantly improve over the baseline` 等）。★ 引用であることが分かる形にし、
**GSE 自身の結果に対して使わない。**
★ 一言でも使えば `docs/research-positioning.md §9` A-Q3 の解除条件が発動し、
**検出力の算術**と **`task_kind`→β 配線**の 2 条件が要求される（ADR-012 §Consequences）。

## 2 段階の構造

```
  Stage 0 ── 募集ゼロ・既存計器・新規収集ゼロ ────────────────────────
    入力  : G1 コホートのログ（⚠️ ローカルに無い。研究者からの提供が要る）
    実装  : ★ experiments/20260819-silence-presence-decomposition/ を
            抽出に使う。⚠️ 被覆率の集計層だけは新規（事前登録 §2.1）
    出す量: ★ 打鍵タスクの沈黙被覆率 C_write ＝ ★★★ 閾値 θ の出所
    副産物: ADR-011 Migration 3b（未了）の消化
              ↓ ★ ここで θ が データから 決まる。人が選ばない
  Stage 1 ── 形成的コホート・専用計測器 ──────────────────────────────
    入力  : 非打鍵タスクを普段行う人 ＋ 同一人物の短い論述ブロック
    出す量: ★ 層別（L-a → L-b → L-c）の被覆率・限界寄与・null
```

## ⚠️ 実行前に必ず読むもの

1. `preregistration.md` **§4**（★ **前処理の先頭に置く必須検査** —— 対象ログの行種を数える）
2. `preregistration.md` **§7**（Stop 条件）と **§12**（事前に認めている限界）
3. `docs/adr/ADR-012-nonkeystroke-observation-formative-track.md`
4. `docs/adr/ADR-013-collection-self-description.md`

## ⚠️ 実行時に追加するファイル（★ `reproducibility-discipline` ルール 2）

★ 本ディレクトリは**事前登録のみ**なので、次は**実行時**に作る:

| ファイル | 内容 |
|---|---|
| `env.md` | OS / Python / 依存版 / `HMM_VERSION` / ★ **依存している `src-tauri/` の実装**の表 |
| `SEED` | 乱数 seed（★ null 被覆率の置換検定で使う） |
| `requirements.txt` | 依存の固定 |
| `config.json` | `w` / `δ` / 層の定義（★ **事前登録の値をそのまま写す**） |
| `run.sh` | 自己検査 → 抽出 → manifest 照合 → 解析 → 漏洩検査（★ **どこかで落ちたら結果を書かない**） |
| `scripts/` | 解析スクリプト |
| `data.md` | 入力の来歴（★ **生 NDJSON は repo の外**） |
| `notes.md` | 結果 |

## ⚠️★★★ データの取り扱い

- ⚠️ **生 NDJSON を repo の中に置かない。**
  ★ 2026-08-19 に 60MB が repo 作業ツリー内にあり security-checker が **CRITICAL** を出した
  （`.steering/20260819-low-typing-window-discrimination/decisions.md` D-11）。
  ⚠️ **`.gitignore` は最後の網であって境界ではない**（★ 本 repo は**一時 public にする運用がある**）。
- ⚠️ **画面録画（参照チャネル）は研究者 PC の暗号化領域のみ。**
  ★ **repo にもデータ repo にも置かない。コード化直後に破棄する**（ADR-012 D12）。
- ★ 入力パスは環境変数で渡す（repo 外）。
