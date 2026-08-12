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

    // ★★ 2026-08-12 追加（S4-D12: 層 2 の音を作り直す）——
    //   音色候補の切替は「目標値」を置いて**一次遅れで寄せる**。
    //   ⚠️★★★ 段差で切り替えると **それ自体がオンセット**であり、
    //     spec §2 の禁止事項を UI 操作で作りに行くことになる（引き継ぎ §5-5 が Step 3 で踏んだ形）。
    //   ★ 既定 6.0 s の一次遅れ = 実効 0.027 Hz。禁止帯（0.5–20 Hz / 15–70 Hz）から 1 桁以上離れている。
    //   ⚠️ とくに normExp は、段差で変えると重なり 4 枚で **2 倍のレベル跳ね**になる。
    this.morphS = o.morphS === undefined ? 6.0 : o.morphS;
    this.tgt = {
      grainSec: this.grainSec, centerHz: this.centerHz,
      spreadCents: this.spreadCents, normExp: this.normExp,
    };

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
          // ★ 「いま効いている値」を返す。目標値ではない（見本が no-op でないことを外から実測できる）
          cur: {
            grainMs: +(this.grainSec * 1000).toFixed(3),
            centerHz: +this.centerHz.toFixed(3),
            spreadCents: +this.spreadCents.toFixed(3),
            densityNormExp: +this.normExp.toFixed(4),
          },
          tgt: {
            grainMs: +(this.tgt.grainSec * 1000).toFixed(3),
            centerHz: +this.tgt.centerHz.toFixed(3),
            spreadCents: +this.tgt.spreadCents.toFixed(3),
            densityNormExp: +this.tgt.normExp.toFixed(4),
          },
        });
      } else if (e.data && e.data.cmd === "set") {
        // ★ 音色候補 / 密度手がかりの切替（S4-D12）。★ 受け付ける鍵を明示し、
        //   ⚠️ **想定外の鍵を黙って無視しない**（黙って無視すると「効かない候補」が緑のまま通る）
        const p = e.data.params || {};
        const allow = ["grainMs", "centerHz", "spreadCents", "densityNormExp"];
        const unknown = Object.keys(p).filter((k) => !allow.includes(k));
        const bad = [];
        if (p.grainMs !== undefined) {
          if (!(p.grainMs > 0)) bad.push("grainMs"); else this.tgt.grainSec = p.grainMs / 1000;
        }
        if (p.centerHz !== undefined) {
          if (!(p.centerHz > 0)) bad.push("centerHz"); else this.tgt.centerHz = p.centerHz;
        }
        if (p.spreadCents !== undefined) {
          if (!(p.spreadCents >= 0)) bad.push("spreadCents"); else this.tgt.spreadCents = p.spreadCents;
        }
        if (p.densityNormExp !== undefined) {
          if (!(p.densityNormExp >= 0 && p.densityNormExp <= 1)) bad.push("densityNormExp");
          else this.tgt.normExp = p.densityNormExp;
        }
        this.port.postMessage({ ack: "set", unknown, rejected: bad, tgt: { ...this.tgt } });
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

    // ★★ 音色パラメータを目標値へ一次遅れで寄せる（ブロックごとに 1 回・S4-D12）。
    //   ★ ブロック内では一定なので、粒の発火・加算は従来どおり段差を持たない。
    {
      const a = 1 - Math.exp(-(n / sampleRate) / Math.max(1e-3, this.morphS));
      this.grainSec += (this.tgt.grainSec - this.grainSec) * a;
      this.centerHz += (this.tgt.centerHz - this.centerHz) * a;
      this.spreadCents += (this.tgt.spreadCents - this.spreadCents) * a;
      this.normExp += (this.tgt.normExp - this.normExp) * a;
    }

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
