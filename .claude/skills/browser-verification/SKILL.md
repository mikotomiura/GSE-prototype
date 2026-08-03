---
name: browser-verification
description: >
  Chrome (claude-in-chrome) で「実物を動かして確かめる」ときに必須参照。
  Apps Script / Google フォーム / スプレッドシートの配備検証、生成した HTML の表示確認、
  被験者が見る画面の実地チェックなど。以下の状況で必須参照:
  - mcp__claude-in-chrome__* を使おうとするとき（★ 最初の 1 回で必ず読む）
  - GAS を Apps Script 上で実行する / フォームにテスト提出する / 管理シートを直すとき
  - 生成した HTML (pages/*.html など) をブラウザで確認するとき
  - スクリーンショットを何枚も撮って状態を追いかけそうになっているとき
  - 「機械検査が全部緑だから動くはず」と言いそうになっているとき
allowed-tools: Bash, Read, Grep, mcp__claude-in-chrome__tabs_context_mcp, mcp__claude-in-chrome__tabs_create_mcp, mcp__claude-in-chrome__tabs_close_mcp, mcp__claude-in-chrome__navigate, mcp__claude-in-chrome__computer, mcp__claude-in-chrome__javascript_tool, mcp__claude-in-chrome__read_page, mcp__claude-in-chrome__read_console_messages
---

# ブラウザで実物を確かめる

## このスキルの目的

★ **機械検査が全部緑でも、実物は動いていないことがある。**

2026-08-03 の G1 配備検証が典型である。`run.sh` も `--selftest` も
`check_g1_emails.py` も**全部緑**だったが、Apps Script 上で実行したら欠陥が 2 件出た:

1. 受付メールが、その日に廃止したはずの「署名をお願いします」を言い続けていた
2. `runCol_` がコード側の配列しか見ておらず、**実スプレッドシートと 1 列ずれ**、
   日付列に「はい/いいえ」のドロップダウンが付いていた

⚠️ どちらも **検査が見ている範囲の外**にあった。詳細は
`.steering/20260804-g1-pilot-execution/decisions.md` の J-1 / J-2。

> ### ★ 中心となる問い
> **この検査は「どちら側」を見ているか。**
> コード側だけを見る検査は、コードと外界（デプロイ済みシート・実フォーム・実端末・
> 実バイナリ）のズレを**原理的に検出できない**。外界は読みに行くしかない。

---

## 0. ★ まず「何を満たせば合格か」を先に確定する

⚠️ **開いてから考えない。** 検査項目を実行者が発明すると、通ったかどうかを後から言えない。
★ **要件は必ずリポジトリ側に一次資料がある。** ブラウザを開く前にそれを Read する:

| 検証対象 | 要件の一次資料 |
|---|---|
| `pages/<ID>/blockNN.html`（課題文ページ） | `experiments/20260801-controlled-friction-task/preregistration.md` **§2.13**（提示方法）＋ **§2.11**（記入欄の要件） |
| `writing-pad.html`（記入パッド単体） | 同 **§2.11** ＋ ファイル冒頭のコメント（設計上の約束 4 点） |
| Apps Script / フォーム / 管理シート | `Form_G1/README.md`（配備手順）＋ `.gs` の `RUN_HEADER` など実装側の定義 |
| 被験者に見えるもの全般 | `preregistration.md` **§2.12**（開示してよい / いけない） |

★ **見つけた要件を箇条書きにしてから開く。** 報告はその箇条書きに 1 対 1 で対応させる。

## 1. ★★ コンテキストを食い潰さない

⚠️ **スクリーンショットは画像であり、極めて高価である。** 状態確認を全部スクショで
やると、1 セッションで数十万トークン消える（2026-08-03 に実測: `computer` の消費が
セッション最大になった）。

### 原則: **見た目はスクショ / 状態は `javascript_tool`**

| やりたいこと | ★ 使うもの |
|---|---|
| 値・属性・DOM の状態を知る | ★ `javascript_tool` で **1 回にまとめて JSON を返す** |
| 実行ログの本文を読む | ★ `javascript_tool` で `document.body.innerText` を切り出す |
| レイアウト崩れ・本当に見えているかの確認 | `computer screenshot`（★ **ここだけ**） |
| 要素の座標を知る | `javascript_tool` で `getBoundingClientRect()` |

```js
// ★ 良い例: 1 回の呼び出しで検証項目を全部集める
JSON.stringify({
  count: document.getElementById('count').textContent,
  block_readOnly: document.getElementById('block').readOnly,
  title: document.title,
  task_userSelect: getComputedStyle(document.querySelector('.task')).webkitUserSelect,
  external_res: [...document.querySelectorAll('script[src],link[href],img,iframe')].length
})
```

⚠️ **悪い例**: 「クリック → スクショ → クリック → スクショ」を繰り返す。
座標が要るとき以外、スクショで状態を確かめない。

### 独立した操作は 1 メッセージにまとめる

`browser_batch` が使えるなら使う。使わない場合でも、**依存のないツール呼び出しは
同じメッセージに並べる**（`Bash` の検証と `javascript_tool` の確認など）。

---

## 2. ⚠️ 実測で潰した落とし穴（GSE 固有・繰り返し踏むもの）

### 2.0 ★★ 「できないはず」を確かめるときは、**必ず対照を取る**

⚠️ ★ **これが最も危険な失敗である。** 否定的テスト（選択できないはず・出ないはず・
送信されないはず）は、**「本当にブロックされた」と「そもそも操作が届いていない」を
区別できない**。届いていないだけなのに **合格と誤読する**（実測で 2 回起きている）。

★ **必ず、効くはずの場所で同じ操作をして、効くことを見る。**

```js
// ✅ 対照つき: .notice は選択できる / .task は選択できない、を同時に見る
const s = window.getSelection(); const mk = el => { const r = document.createRange();
  r.selectNodeContents(el); s.removeAllRanges(); s.addRange(r); const n = s.toString().length;
  s.removeAllRanges(); return n; };
JSON.stringify({
  control: mk(document.querySelector('.notice')),  // ★ >0 でなければ検査自体が空回り
  target:  mk(document.querySelector('.task')),    // ★ 0 なら本当に効いている
})
```

⚠️ **`control` が 0 なら、`target` が 0 でも何も言えない。** 先に control を直す。
★ これはリポジトリ側の「検査が空回りしていないか実測する」（`--selftest` の作法）と同じ思想である。

### 2.0b ★ クリックが効かないときは、**着弾したかを先に見る**

⚠️ `computer` に渡す座標と `getBoundingClientRect()` の CSS px が**一致しない環境がある**
（実測でスクリーンショット空間と 1.5 倍前後ずれた例あり。ウィンドウ倍率で変わる）。
★ 座標がずれていると **全クリックが黙って外れる**。「反応しない」を要素の仕様と誤読しない。

```js
// ★ 着弾プローブ: このあと computer left_click して、記録が入るかを見る
window.__hits = [];
document.addEventListener('mousedown', e => window.__hits.push(
  {x: e.clientX, y: e.clientY, tag: e.target.tagName, cls: e.target.className}), true);
```

→ クリック後に `window.__hits` を読む。★ **空なら座標系の問題**であって要素の問題ではない。

### 2.1 ★ `file://` は拡張機能から触れない

`mcp__claude-in-chrome__navigate` に `file:///…` を渡すと
`Can't interact with browser-internal or unparseable URLs` で**必ず失敗する**。

→ **ローカル HTTP で配信して検証する**:

```bash
# ★ ポートは固定しない。⚠️ 並行セッション / 前回の残骸が専有していることがある
PORT=$((8700 + RANDOM % 200))
cd <生成物のディレクトリ>
nohup python3 -m http.server $PORT --bind 127.0.0.1 > /dev/null 2>&1 &
sleep 1
CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:$PORT/block02.html)
# ★★ 200 でなければ**先に進まない**。⚠️ `nohup … &` はポート専有時に**無言で死ぬ**
[ "$CODE" = 200 ] || { echo "サーバが上がっていない (code=$CODE)。ポートを変えて再試行"; }
echo "PORT=$PORT"
# 検証が終わったら必ず止める（★ 自分が立てたポートだけ）
pkill -f "http.server $PORT"
```

⚠️ ★ **`nohup … &` は silent failure 型である。** 起動したつもりで 404 / 000 のまま
「ページが壊れている」と誤読した実例がある。**必ず 200 を確かめてから開く。**

⚠️ ★ **`file://` そのものを検証したことにはならない。** 被験者は `file://` で開く。
外部リソース・`fetch`・storage を一切持たないページなら差は出ないはずだが、
**「はず」は結論ではない**。完了報告に「`http://127.0.0.1` で検証した」と書く。

### 2.2 ★ Google フォーム / スプレッドシートは合成イベントを受け付けない

`element.click()` を `javascript_tool` から呼んでも **`aria-checked` は変わらない**。
→ `computer left_click` で**実クリック**する。座標は直前に
`scrollIntoView({block:'center'})` してから `getBoundingClientRect()` で取る。

⚠️ ★ **座標を取ってから click するまでの間にページがスクロールするとズレる。**
実測でテキスト欄への入力が丸ごと空振りした。
→ **入力後は必ず `value` を読んで入ったことを確かめる**:

```js
JSON.stringify({values: [...document.querySelectorAll('input[type="text"]')].map(i=>i.value)})
```

### 2.3 ★★ Apps Script エディタ — 貼り付けが「入らない」事故

⚠️ **実行ログのパネルが画面の下半分を占める。** そこをクリックしてから
`cmd+a` / `cmd+v` しても**コードは 1 文字も変わらず、`cmd+s` は no-op になる**
（2026-08-03 に実際に踏み、シートが直らない原因を 1 往復ぶん探した）。

**手順**:

1. 実行ログを **`×` で閉じる**
2. **コード領域（上半分）** をクリックする
3. `cmd+a` → `cmd+v` → `cmd+s`
4. ★ **貼れたことを検証する**: 末尾行番号がファイルの行数と一致するか
   （`cmd+Down` で末尾へ飛び、スクショ 1 枚）。ヘッダが
   「変更が保存されていません」→「ドライブに保存しました」に変わることも見る

★ **コードは必ずクリップボード経由で貼る**（`pbcopy < file.gs`）。
⚠️ `computer type` で直接打つと、エディタの自動インデント・括弧補完が働いて**壊れる**。

### 2.4 ★ 実行ログはエディタでなく「実行数」ページで読む

トリガー経由の実行（`onFormSubmit` 等）はエディタのログに出ない。
`https://script.google.com/home/projects/<ID>/executions` を開き、
行をクリックして展開してから `javascript_tool` で `innerText` を切り出す。

### 2.5 ★ OAuth の同意画面は別ウィンドウに出る

MCP のタブグループに入らないので**操作できない**。多くの場合は自動で通るが、
止まったら**ユーザーに委ねる**。⚠️ 権限付与は勝手に進めない（下記 §4）。

---

## 3. ★ デプロイ先を持つものは「実物のスキーマ」を読んで比べる

GAS / スプレッドシート / フォーム / 本番設定のように **repo の外に状態があるもの**は、
コード側の期待値と**実物**を突き合わせる仕組みを実装側に入れる。

```js
// ★ 実シートのヘッダ行を読み、コードの配列と比べる。ズレたら止める。
function assertRunHeader_(sh) {
  var diff = runHeaderDiff_(sh);   // 実シート row2 と RUN_HEADER を列ごとに比較
  if (diff.length) throw new Error("ヘッダ不一致:\n" + diff.join("\n"));
}
```

- ★ **黙って進めない**（ズレたまま書き込むと、静かに間違った列へ入る）
- ★ **データが無いときだけ自動修復**し、データがあれば**止めて人に返す**
- ★ 規則・書式を貼り直す前に **`clearDataValidations()` で古い残骸を消す**
  （消さないと新旧が二重に付く。実測で B〜G 列すべてにドロップダウンが付いていた）

⚠️ ★ **「名前で引く」だけでは足りない。** 引き先がコード側の定数なら、
コードと外界のズレは見えない（`runCol_` がまさにこれだった）。

---

## 4. ⚠️⚠️ 勝手にやらないこと

`data-privacy` と全体の安全規約が優先する。**ユーザーに確認してから**行う:

| 行為 | なぜ |
|---|---|
| ★ **フォームの送信**（テスト提出を含む） | 個人データの入力と送信にあたる |
| ★ **メールの実送信**（`AUTO_SEND=true` にして提出することを含む） | 取り消せない |
| ★ **OAuth 権限の付与** | Gmail 送信・Drive 全体へのアクセスを与える |
| ★ **本番シート / ロスターへの書き込み** | 採番が本番に混ざる |
| 認証情報の入力 | ★ **絶対にやらない**（ユーザー自身に依頼する） |

### ⚠️★ ユーザーの状態を壊さない（**戻せないもの**がある）

| 壊しやすいもの | どうする |
|---|---|
| ★ **クリップボード** | ⚠️ **`cmd+c` を試す前に `pbpaste > /tmp/clip.bak` で退避**し、終わったら `pbcopy < /tmp/clip.bak` で戻す。★ 退避せずに上書きすると**永久に戻せない**（実例あり） |
| 他セッションのタブ / サーバ | ★ **触らない。** 自分が作ったものだけ片付ける（`pkill` は自分のポートに限定する） |
| 未保存のタブ | ⚠️ `beforeunload` が出ると自動化が**固まる**。`navigate` / `tabs_close_mcp` がタイムアウトしたらこれを疑う。★ **自分で開いたタブ以外を閉じにいかない** |

### ★ テストしたら必ず後片付けし、**片付けられなかったものを書く**

- 作ったテスト行は消す（消したことを報告に書く）
- ⚠️ ★ **フォームの回答（＝データ）は勝手に削除しない。** 残っていることを報告する
- 氏名欄には `TEST-…-delete-me` のように**後から探せる文字列**を入れる
- ★ **自分が作っていないもの**（他セッションのタブ・サーバ・未コミット差分）は
  **触らず、報告に「自分のものではない」と書く**

---

## 5. ★ 完了報告に必ず書くこと

⚠️ ★ **「検証した」と「試していない」を混ぜない。**

- 通ったもの（★ **何をどう測ったか**まで。例:「JS 11 / Python 11 で一致」）
- ★ **試していないもの**（例:「`file://` そのものでは未確認」「Windows 実機は未実施」
  「新規採番の経路は通っていない」）
- ★ **代替手段で検証したもの**と、その差がどこに残るか
- 後片付けの結果（消したもの / 残したもの / ★ **戻せなかったもの**）
- ★ **合否の言い方**: 「要件 N 件中 M 件を実測で確認、未検証 K 件」と数で言う。
  ⚠️ ★ **未検証が残っているうちは「問題なし」と書かない。**
- ⚠️ ★ **ブラウザでは原理的に検証できない要件**（他 OS での見え方・実 IME の変換・
  拡張機能ありの環境）は、**「試していない」に落として明示する**。
  ★ 「たぶん同じはず」で埋めない。

---

## 関連

- `verify-before-claiming` — ★ **断定の前に一次資料へ降りる**（本スキルはその実地版）
- `data-privacy` — 外部送信・PII・NDJSON の扱い
- `reproducibility-discipline` — `experiments/` 配下の実験を回すときの規約
- `.steering/20260804-g1-pilot-execution/decisions.md` J-1 / J-2 — 本スキルの元になった実例
