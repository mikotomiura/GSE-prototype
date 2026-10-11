//! EH3 の肖像（壁紙）の層（OS API 非依存）。
//!
//! 何を出すかだけを決め、壁紙への書き込みは OS 依存の層（`crate::wallpaper`）が行う（R-P10）。
//! 要件の SSOT は `.steering/20261011-portrait-eh3-prereg/implementation-requirements.md` R-P1〜R-P10、
//! 設計は `.steering/20261011-portrait-eh3-impl/design.md` §4。
//!
//! - 空: 元の壁紙のまま（[`Show::Original`]）。
//! - D: 日替わりの地模様（打鍵を材料にしない・日付と種から作る・R-P7）。
//! - A: その回の形（[`generator`]・更新は [`schedule`] の `recent`）。終わりで none なら何もしない、
//!   seed なら形を重心の小さな印へ畳む（R-P6・`render_e18.py` の最後のコマ）。
//!
//! ⚠️ 本人の操作（止める・戻す・自分で替える）はこの層に届かない。届けば出力が変わり、記録や時刻へ
//! 横に漏れる経路になる（R-P9）。止めた・替えたの扱いは OS 依存の層が持つ。

pub mod canvas;
pub mod generator;
pub mod schedule;

use std::collections::VecDeque;

use crate::eh3::{Assignment, Condition};
use canvas::{Canvas, COVERAGE_EPS, H, W};
use generator::{Generator, Second, SplitMix};
use schedule::{Schedule, LATE_TOLERANCE_MS, RECENT_MS};

/// 壁紙に何を出すか。
#[derive(Debug, Clone, PartialEq)]
pub enum Show {
    /// 本人の元の壁紙。
    Original,
    /// この画（320×180）。
    Image(Canvas),
}

/// D の地模様の種（全参加者で同じ。日付だけで模様が決まる）。
const DECOR_SEED: u64 = 0x4548_335f_4445_434f; // "EH3_DECO"

/// D の地模様（R-P7）: 日付（4:00 区切りの日）と種から作る。打鍵を材料にしない。
///
/// 地の上に、低い彩度の大きな印を 9 つ。位置・色相・大きさは日付から決まり、その日のうちは変わらない。
pub fn decor(local_day: i64) -> Canvas {
    let mut r = SplitMix::new(DECOR_SEED ^ (local_day as u64).wrapping_mul(0x9E37_79B9_7F4A_7C15));
    let mut c = Canvas::ground();
    let base_hue = r.unit();
    for _ in 0..9 {
        let x = r.unit() * W as f32;
        let y = r.unit() * H as f32;
        let sigma = 18.0 + 22.0 * r.unit();
        let hue = base_hue + 0.15 * (r.unit() - 0.5);
        let col = canvas::hsv(hue, 0.18, 0.80);
        c.blob(x, y, sigma, col, 0.25);
    }
    c
}

/// seed の畳み方（R-P6・R-4）: 地の上に、形の重心に平均の色の小さな印を 1 つ（σ 4・α 0.8）。
/// 形が地のままなら `None`（何も書かない）。
pub fn seed_fold(img: &Canvas) -> Option<Canvas> {
    let (mut sw, mut sx, mut sy) = (0.0_f64, 0.0_f64, 0.0_f64);
    let mut col = [0.0_f64; 3];
    let mut n = 0u32;
    for (i, p) in img.px.iter().enumerate() {
        let dev = img.deviation(i);
        if dev > COVERAGE_EPS {
            let w = dev as f64;
            sw += w;
            sx += w * (i % W) as f64;
            sy += w * (i / W) as f64;
            for c in 0..3 {
                col[c] += p[c] as f64;
            }
            n += 1;
        }
    }
    if n == 0 {
        return None;
    }
    let mut out = Canvas::ground();
    let mean = col.map(|v| (v / n as f64) as f32);
    out.blob((sx / sw) as f32, (sy / sw) as f32, 4.0, mean, 0.8);
    Some(out)
}

/// 1 セッションの肖像の層。
#[derive(Debug)]
pub struct PortraitLayer {
    assignment: Assignment,
    condition: Option<Condition>,
    generator: Option<Generator>,
    schedule: Option<Schedule>,
    pending: Vec<Second>,
    presses: VecDeque<u64>,
    last_shown: Option<Show>,
}

impl PortraitLayer {
    pub fn new(assignment: Assignment) -> Self {
        Self {
            assignment,
            condition: None,
            generator: None,
            schedule: None,
            pending: Vec::new(),
            presses: VecDeque::new(),
            last_shown: None,
        }
    }

    fn emit(&mut self, show: Show) -> Option<Show> {
        if self.last_shown.as_ref() == Some(&show) {
            return None;
        }
        self.last_shown = Some(show.clone());
        Some(show)
    }

    /// 始まり（起動・スリープからの復帰・日付の区切りの直後）。`condition` はその日の条件
    /// （まだ数えていない日・期間の後は `None` で、何も変えない）。`seed` はこのセッションの乱数の種。
    pub fn start(
        &mut self,
        now_ms: u64,
        local_day: i64,
        condition: Option<Condition>,
        seed: u64,
    ) -> Option<Show> {
        self.condition = condition;
        self.pending.clear();
        self.generator = None;
        self.schedule = None;
        match condition? {
            Condition::Blank => self.emit(Show::Original),
            Condition::Decor => self.emit(Show::Image(decor(local_day))),
            Condition::PortraitNone | Condition::PortraitSeed => {
                self.generator = Some(Generator::new(
                    self.assignment.grammar,
                    self.assignment.drift,
                    seed,
                ));
                self.schedule = Some(Schedule::new(now_ms));
                self.emit(Show::Image(Canvas::ground()))
            }
        }
    }

    /// その日を初めて数えた（その日の最初の打鍵）。始まりの時点でまだ条件が無かったときに呼ぶ。
    pub fn condition_assigned(
        &mut self,
        now_ms: u64,
        local_day: i64,
        condition: Condition,
        seed: u64,
    ) -> Option<Show> {
        if self.condition.is_some() {
            return None;
        }
        self.start(now_ms, local_day, Some(condition), seed)
    }

    /// 1 秒ぶんの材料（打鍵の時刻は `press_ms` に渡す）。予定に当たって形が変わったら出す画を返す。
    pub fn second(&mut self, now_ms: u64, s: Second, press_ms: &[u64]) -> Option<Show> {
        self.presses.extend(press_ms.iter().copied());
        while self
            .presses
            .front()
            .is_some_and(|p| now_ms.saturating_sub(*p) > RECENT_MS + LATE_TOLERANCE_MS + 1000)
        {
            self.presses.pop_front();
        }
        let gen = self.generator.as_mut()?;
        self.pending.push(s);
        let sched = self.schedule.as_mut()?;
        let presses: Vec<u64> = self.presses.iter().copied().collect();
        if !sched.due(now_ms, &presses) {
            return None;
        }
        let img = gen.update(&std::mem::take(&mut self.pending)).clone();
        self.emit(Show::Image(img))
    }

    /// 終わり（終了・スリープの直前・日付の区切り）。A-seed なら seed を、それ以外は何も出さない。
    pub fn end(&mut self) -> Option<Show> {
        let cond = self.condition.take();
        let gen = self.generator.take();
        self.schedule = None;
        self.pending.clear();
        match (cond, gen) {
            (Some(Condition::PortraitSeed), Some(g)) => {
                let folded = seed_fold(g.image())?;
                self.emit(Show::Image(folded))
            }
            _ => None,
        }
    }

    /// 期間の後・研究を終える: 元の壁紙へ（seed の印を残さない・R-P8）。
    pub fn finish(&mut self) -> Option<Show> {
        self.condition = None;
        self.generator = None;
        self.schedule = None;
        self.pending.clear();
        self.emit(Show::Original)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::eh3::parse_assignment;

    const T0: u64 = 1_760_000_000_000;

    fn assign() -> Assignment {
        parse_assignment("order=A,E,D;a_first=seed;grammar=raw;drift=none").unwrap()
    }

    fn sec(active: bool) -> Second {
        Second {
            f1: 150.0,
            f3: 0.1,
            f4: 6.0,
            f6: 0.3,
            active,
        }
    }

    /// 70 秒ごとに 50 秒打つ（20 秒の間が予定の時刻に当たることがある: 900 秒目は 11 秒の間の中）。
    /// ⚠️ 周期が 300 の約数だと、予定の時刻がいつも打鍵の最中に当たり、一度も更新しない。
    fn type_for(layer: &mut PortraitLayer, from: u64, secs: u64) -> Vec<Show> {
        let mut out = Vec::new();
        for k in 0..secs {
            let now = from + k * 1000;
            let active = k % 70 < 50;
            let presses = if active { vec![now] } else { vec![] };
            if let Some(s) = layer.second(now, sec(active), &presses) {
                out.push(s);
            }
        }
        out
    }

    #[test]
    fn blank_shows_the_original_and_decor_does_not_use_typing() {
        let mut l = PortraitLayer::new(assign());
        assert_eq!(
            l.start(T0, 100, Some(Condition::Blank), 1),
            Some(Show::Original)
        );
        assert!(
            type_for(&mut l, T0, 1000).is_empty(),
            "空は打鍵で変わらない"
        );
        let mut l = PortraitLayer::new(assign());
        let d = l.start(T0, 100, Some(Condition::Decor), 1).unwrap();
        assert!(
            type_for(&mut l, T0, 1000).is_empty(),
            "D は打鍵で変わらない"
        );
        assert_eq!(d, Show::Image(decor(100)));
        assert_ne!(decor(100), decor(101), "日替わり");
    }

    #[test]
    fn portrait_starts_from_the_ground_and_grows_at_slots() {
        let mut l = PortraitLayer::new(assign());
        assert_eq!(
            l.start(T0, 100, Some(Condition::PortraitSeed), 7),
            Some(Show::Image(Canvas::ground()))
        );
        let shows = type_for(&mut l, T0, 1000);
        assert!(!shows.is_empty(), "予定に当たれば形が変わる");
        assert!(shows
            .iter()
            .all(|s| matches!(s, Show::Image(c) if !c.is_ground())));
    }

    #[test]
    fn seed_folds_and_none_leaves_the_shape() {
        let mut l = PortraitLayer::new(assign());
        l.start(T0, 100, Some(Condition::PortraitSeed), 7);
        type_for(&mut l, T0, 1000);
        let folded = l.end().expect("seed は印を書く");
        let Show::Image(c) = folded else {
            panic!("seed は画");
        };
        let covered = (0..W * H)
            .filter(|i| c.deviation(*i) > COVERAGE_EPS)
            .count();
        assert!(covered > 0 && covered < 400, "小さな印 1 つ: {covered}");
        let mut l = PortraitLayer::new(assign());
        l.start(T0, 100, Some(Condition::PortraitNone), 7);
        type_for(&mut l, T0, 1000);
        assert_eq!(l.end(), None, "none は何もしない");
    }

    #[test]
    fn nothing_changes_before_the_day_is_counted_and_finish_restores() {
        let mut l = PortraitLayer::new(assign());
        assert_eq!(
            l.start(T0, 100, None, 7),
            None,
            "まだ数えていない日は何も変えない"
        );
        assert!(type_for(&mut l, T0, 30).is_empty());
        assert!(l.condition_assigned(T0, 100, Condition::Blank, 7).is_some());
        assert_eq!(
            l.condition_assigned(T0, 100, Condition::Decor, 7),
            None,
            "日中は変わらない"
        );
        let mut l = PortraitLayer::new(assign());
        l.start(T0, 100, Some(Condition::PortraitSeed), 7);
        assert_eq!(l.finish(), Some(Show::Original));
    }

    /// 見本の書き出し（手で回す・F-1 の選択の材料）: `GSE_PORTRAIT_SAMPLES=<dir>` を置いて
    /// `cargo test --lib render_portrait_samples -- --ignored`。合成の打鍵（書いては止まる 2 時間）で、
    /// `raw` / `lattice` × drift `none` / `diffuse` の 2 時間後の画、その seed、D の地模様（3 日ぶん）を
    /// 1280×720 の PNG にする。⚠️ 合成の材料であり、実際の打鍵の見え方ではない。
    #[test]
    #[ignore]
    fn render_portrait_samples() {
        use crate::eh3::{Drift, Grammar};
        let Ok(dir) = std::env::var("GSE_PORTRAIT_SAMPLES") else {
            return;
        };
        let dir = std::path::PathBuf::from(dir);
        std::fs::create_dir_all(&dir).unwrap();
        let save = |name: &str, c: &Canvas| {
            let rgb = canvas::upscale_rgb8(c, 1280, 720);
            let f = std::fs::File::create(dir.join(name)).unwrap();
            let mut enc = png::Encoder::new(std::io::BufWriter::new(f), 1280, 720);
            enc.set_color(png::ColorType::Rgb);
            enc.set_depth(png::BitDepth::Eight);
            let mut w = enc.write_header().unwrap();
            w.write_image_data(&rgb).unwrap();
        };
        // 合成の打鍵: 書く区間（打鍵の速さと訂正が区間ごとに違う）と止まる区間が交互に来る
        let mut r = SplitMix::new(7);
        let mut seconds = Vec::new();
        let mut t = 0u64;
        while t < 2 * 3600 {
            let typing = 60 + (r.unit() * 240.0) as u64;
            let pause = 10 + (r.unit() * 110.0) as u64;
            let (f1, f3, f4, f6) = (
                80.0 + 400.0 * r.unit() as f64,
                0.4 * r.unit() as f64,
                1.0 + 15.0 * r.unit() as f64,
                0.9 * r.unit() as f64,
            );
            for _ in 0..typing {
                seconds.push(Second {
                    f1,
                    f3,
                    f4,
                    f6,
                    active: r.unit() < 0.7,
                });
            }
            for _ in 0..pause {
                seconds.push(Second {
                    f1: f64::NAN,
                    f3: f64::NAN,
                    f4: f64::NAN,
                    f6: f64::NAN,
                    active: false,
                });
            }
            t += typing + pause;
        }
        for (grammar, gname) in [(Grammar::Raw, "raw"), (Grammar::Lattice, "lattice")] {
            for (drift, dname) in [(Drift::None, "none"), (Drift::Diffuse, "diffuse")] {
                let mut g = Generator::new(grammar, drift, 42);
                for chunk in seconds.chunks(300) {
                    g.update(chunk);
                }
                save(&format!("portrait-{gname}-{dname}.png"), g.image());
                if let Some(s) = seed_fold(g.image()) {
                    save(&format!("seed-{gname}-{dname}.png"), &s);
                }
            }
        }
        for day in 0..3 {
            save(&format!("decor-day{day}.png"), &decor(20_000 + day));
        }
    }

    #[test]
    fn seed_of_a_ground_canvas_writes_nothing() {
        assert_eq!(seed_fold(&Canvas::ground()), None);
    }
}
