/* =========================================================================
 * GSE 表現層 Step 4 — 層 2（粒子）AudioWorkletProcessor
 *
 * ★ 設計の拘束（すべて一次資料に接地。勝手に変えない）
 *   - media-expression-spec.md §2 層 2: グラニュラー密度で前進を写す。
 *     ★★ 粒子率の下限 = 100 grains/s（下回ると粒が個別に聞こえ、リズムとして分節する = ISE 側 [P64]）
 *   - spec §2 全層共通の禁止: オンセット / 拍・リズム / 音高のステップ / 実物音の引用
 *   - S3-D14: 音の幅は「合成音の範囲」で広げる。★ 実物音の引用禁止は維持
 *   - D18 / S3-D15: ★ グラニュラー合成は乱数を使う → seed を固定し、SEED に実値を書く
 *
 * ★★ なぜ Worklet でサンプルを直接書くのか（AudioBufferSourceNode を粒ごとに作らない）
 *   S3-D3 の要件 (a)「メモリが増え続けない」——100 grains/s × 600 s = 6 万個。
 *   粒ごとにノードを作れば生成と GC が積み上がる。★ ここで書けばノード生成は 0 回であり、
 *   確保するメモリは同時発音数（voices）ぶんだけで、時間に依らず一定である。
 *
 * ★ オンセットを作らないための実装上の約束
 *   1. 1 粒 = Hann 窓を掛けた正弦バースト。★ Hann は端点が厳密に 0 なので粒頭にクリックが立たない
 *   2. 粒子率・ゲインは AudioParam（a-rate）で受ける。★ 値の飛びはグラフ側でランプ済み
 *   3. 粒の発火間隔にジッタを入れる。★ 等間隔だと「拍」そのものになり spec §2 の禁止事項に当たる
 * ========================================================================= */
"use strict";

/** ★ seed 固定 PRNG（mulberry32）。Math.random() を使わない = 再現できる。 */
function mulberry32(seed) {
  let a = seed >>> 0;
  return function () {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const MAX_VOICES = 2048; // ★ 上限は固定。400 grains/s × 40 ms なら同時 16 枚なので桁で余裕がある

class GrainProcessor extends AudioWorkletProcessor {
  static get parameterDescriptors() {
    // ⚠️★★★ ゲインの AudioParam を**ここに置かない**。
    //   実測で踏んだ欠陥（2026-08-12）: `gain` を既定 0 でここに持たせたところ、
    //   player 側は**外部の GainNode だけ**を設定していたため、
    //   ★ **層 2 が完全に無音のまま（RMS = 0.000e+0）静的検査 56 件が全部緑になった。**
    //   捕まえたのは陽性対照だけである。→ ★ **ゲインの制御点を 1 つに絞る**（外部 GainNode）。
    return [
      // ★ 粒子率。下限を割った状態も鳴らせるようにしてある（引き継ぎ §4a の「逆検査と同じ思想」）
      { name: "rate", defaultValue: 100, minValue: 0, maxValue: 2000, automationRate: "a-rate" },
    ];
  }

  constructor(options) {
    super();
    const o = (options && options.processorOptions) || {};
    this.grainSec = (o.grainMs || 40) / 1000;
    this.centerHz = o.centerHz || 440;
    this.spreadCents = o.spreadCents || 600;
    this.jitter = o.jitter === undefined ? 0.5 : o.jitter;
    // ★ 重なり枚数の何乗で割るか。0.5 = エネルギー保存（密度を上げても音量が変わらず、質感だけが変わる）
    this.normExp = o.densityNormExp === undefined ? 0.5 : o.densityNormExp;
    this.rnd = mulberry32(o.seed || 1);

    // 固定長のボイスプール。★ 実行中に確保し直さない（メモリを増やさない）
    this.vPhase = new Float64Array(MAX_VOICES); // 粒内の位置 0..1
    this.vStep = new Float64Array(MAX_VOICES);  // 1 サンプルあたりの粒内進み
    this.vOmega = new Float64Array(MAX_VOICES); // 角周波数 rad/sample
    this.vAng = new Float64Array(MAX_VOICES);   // 現在位相 rad
    this.vOn = new Uint8Array(MAX_VOICES);
    this.nextFree = 0;

    this.toNextGrain = 0;   // 次の粒までの残りサンプル数
    this.grainsEmitted = 0; // ★ 実際に発した粒の総数（A6 の実測に使う。設定値ではなく実体）
    this.dropped = 0;       // ★ ボイス枯渇で落とした粒。0 でないことを黙って隠さない
    this.frames = 0;

    this.port.onmessage = (e) => {
      if (e.data && e.data.cmd === "stats") {
        this.port.postMessage({
          grainsEmitted: this.grainsEmitted,
          dropped: this.dropped,
          seconds: this.frames / sampleRate,
          activeVoices: this.countActive(),
        });
      }
    };
  }

  countActive() {
    let n = 0;
    for (let i = 0; i < MAX_VOICES; i++) if (this.vOn[i]) n++;
    return n;
  }

  /** 1 粒を起こす。★ 周波数は seed 固定 PRNG で中心 ± spread から引く。 */
  spawn() {
    let slot = -1;
    for (let k = 0; k < MAX_VOICES; k++) {
      const i = (this.nextFree + k) % MAX_VOICES;
      if (!this.vOn[i]) { slot = i; break; }
    }
    if (slot < 0) { this.dropped++; return; }
    this.nextFree = (slot + 1) % MAX_VOICES;

    const cents = (this.rnd() * 2 - 1) * this.spreadCents;
    const hz = this.centerHz * Math.pow(2, cents / 1200);
    this.vOmega[slot] = (2 * Math.PI * hz) / sampleRate;
    this.vAng[slot] = this.rnd() * 2 * Math.PI; // ★ 位相もばらす（揃うと粒頭が加算されて段差になる）
    this.vPhase[slot] = 0;
    this.vStep[slot] = 1 / Math.max(1, this.grainSec * sampleRate);
    this.vOn[slot] = 1;
    this.grainsEmitted++;
  }

  process(inputs, outputs, params) {
    const out = outputs[0][0];
    if (!out) return true;
    const n = out.length;
    const rateArr = params.rate;
    const rateConst = rateArr.length === 1;

    for (let i = 0; i < n; i++) {
      const rate = rateConst ? rateArr[0] : rateArr[i];

      // ---- 粒の発火 -------------------------------------------------------
      if (rate > 0) {
        this.toNextGrain -= 1;
        while (this.toNextGrain <= 0) {
          this.spawn();
          const mean = sampleRate / rate;
          // ★ ジッタ: 等間隔にしない。等間隔の発火は「拍」そのもの（spec §2 ✗拍・リズム）
          const j = 1 + (this.rnd() * 2 - 1) * this.jitter;
          this.toNextGrain += Math.max(1, mean * j);
        }
      }

      // ---- 加算合成 -------------------------------------------------------
      let s = 0;
      for (let v = 0; v < MAX_VOICES; v++) {
        if (!this.vOn[v]) continue;
        const p = this.vPhase[v];
        if (p >= 1) { this.vOn[v] = 0; continue; }
        // ★ Hann 窓。端点が厳密に 0 なので粒頭・粒尾にクリックが立たない
        const w = 0.5 - 0.5 * Math.cos(2 * Math.PI * p);
        s += w * Math.sin(this.vAng[v]);
        this.vAng[v] += this.vOmega[v];
        this.vPhase[v] = p + this.vStep[v];
      }

      // ★ 重なり枚数の normExp 乗で割る。既定 0.5 = エネルギー保存。
      //   ⚠️ 帰結: 密度を上げても**音量はほぼ変わらない**。変わるのは
      //      「粒が融けるか個別に聞こえるか」という質感であり、これは spec §2 が層 2 に求めた軸そのもの。
      // ★ ゲインは掛けない。音量は**外部の GainNode 一箇所**で決める（上の parameterDescriptors 参照）
      const overlap = Math.max(1, rate * this.grainSec);
      out[i] = s / Math.pow(overlap, this.normExp);
    }
    this.frames += n;
    return true;
  }
}

registerProcessor("grain-processor", GrainProcessor);
