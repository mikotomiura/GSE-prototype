# 本人の段 1 の版に手跡の canvas の直しだけを載せる（v0.1.45・v0.1.42 が元）

## 背景
- 2026-11-28、本人の段 1 の試行（デスクトップの v0.1.42・12/9 ごろまで）で手跡の線が半分の幅に描かれた。直しは main に入った（PR #443・e656ca62）。v0.1.44 として配布物も作った。
- 入れ替えの前に、v0.1.44 が段 1 の同意の版を `s1-n3-1` に上げていることに気づいた（v0.1.42 は `s1-self-trial-1`）。`~/.gse/s1_probe_consent` の版と合わないと、段 1 の毎日の問いが何も表示されずに止まる。
- v0.1.44 は段 1 の 3 名向けの変更も含む（7 択の Q3・1 タップで答える方式・Q2 を先に聞く順・ほかの窓をどける操作）。
- 研究者は「v0.1.42 に直しだけ」を選んだ（2026-11-28 の AskUserQuestion）。

## ゴール
- v0.1.42 に e656ca62 だけを載せた版を CI で組み、デスクトップの `S1_実施用_macOS/gse-next.app` と入れ替える。
- 問いの形と同意の版は v0.1.42 のまま。

## 受け入れ条件
- 同意の版が `s1-self-trial-1` のまま（`S1_PROBE_CONSENT_VERSION`）。
- `npm run test:handmark`、tsc、`cargo test --lib handmark_store::guard` が緑。
- 入れ替えの前後で `handmark_assignment.json`・`.sha256`・`s1.mode`・`o1.mode`・`o1.autostart` の SHA-256 が変わらない。
- 再起動の後、gse-app.log に input_monitoring=true と Measuring が出る。

## スコープ外
- main へのマージ（この枝は main に入れない。main の版は v0.1.44 のまま）。
- 供給網の advisory（cookie・url）。
