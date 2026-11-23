//! 手跡の背景の窓を「デスクトップのすぐ上」に保ち、アイコンを模様の上に写すための純関数（OS 非依存・判断 9・10）。
//!
//! Windows の窓を動かすのは `handmark_desktop_windows.rs` で、ここは判定と画素の整えだけを持つ（両 OS でテストが走る）。
//! アイコンの画素は `PrintWindow` で取ったデスクトップの一覧の絵で、名前の文字も画素に含まれる。
//! 画素は記録しない・tracing に出さない・背景の窓（`handmark_stage::LABEL`）以外へ送らない（判断 10）。
//! このファイルの型は `Debug`・`Serialize` を持たない（記録の型に入れられない）。

/// アイコンの区画の一辺（物理ピクセル）。
pub const TILE: u32 = 64;

/// 背景の窓の z 順の直し方。
#[derive(Clone, Copy, PartialEq, Eq)]
pub enum Restack<H> {
    /// いまのままでよい（背景の窓がデスクトップのすぐ上の見える窓）。
    Keep,
    /// この窓の下へ入れる（デスクトップの 1 つ上の窓。見えない窓のこともある）。
    Below(H),
    /// デスクトップが見つからない。z 順の最下へ置く（アイコンの上に重なる見え方に落ちる）。
    Bottom,
}

/// z 順の直し方を決める。`progman_found` はデスクトップの窓が見つかったか。`first_visible_above` は
/// デスクトップより上で最初に見える窓、`just_above` はデスクトップのすぐ上の窓（見えなくても）。
pub fn decide_restack<H: Copy + PartialEq>(
    progman_found: bool,
    first_visible_above: Option<H>,
    just_above: Option<H>,
    stage: H,
) -> Restack<H> {
    if !progman_found {
        return Restack::Bottom;
    }
    if first_visible_above == Some(stage) {
        return Restack::Keep;
    }
    match just_above {
        // すぐ上が自分なら、見える窓の判定と食い違っても動かさない（自分を自分の下へは入れられない）。
        Some(h) if h == stage => Restack::Keep,
        Some(h) => Restack::Below(h),
        // デスクトップが z 順の最上（他に窓が無い）。最下へ置けばデスクトップの下になりうるので、そのままにする。
        None => Restack::Keep,
    }
}

/// premultiplied の BGRA（`0xAARRGGBB`）の各色を透明度で抑える（`PrintWindow` は色が透明度を超える画素を返すことがある）。
pub fn clamp_premultiplied(px: u32) -> u32 {
    let a = px >> 24;
    let mut out = a << 24;
    for shift in [0, 8, 16] {
        out |= ((px >> shift) & 0xFF).min(a) << shift;
    }
    out
}

/// premultiplied の BGRA を、canvas の `ImageData` が受ける straight の RGBA の 4 バイトへ直す。
pub fn to_straight_rgba(px: u32) -> [u8; 4] {
    let px = clamp_premultiplied(px);
    let a = px >> 24;
    if a == 0 {
        return [0, 0, 0, 0];
    }
    let un = |c: u32| ((c * 255 + a / 2) / a).min(255) as u8;
    [
        un((px >> 16) & 0xFF),
        un((px >> 8) & 0xFF),
        un(px & 0xFF),
        a as u8,
    ]
}

/// 一覧の絵 `src`（`lw` × `lh`・左上が仮想画面の (`left`, `top`)）から、主画面（(0,0) から `sw` × `sh`）の分を
/// `out` へ切り出す。主画面の外の画素は 0（透明）。多画面で一覧が負の座標から始まるときも、主画面より小さいときも扱う。
/// `src` か `out` の長さが合わなければ `out` を 0 で塗って偽を返す。
#[allow(clippy::too_many_arguments)]
pub fn crop_primary(
    src: &[u32],
    lw: u32,
    lh: u32,
    left: i32,
    top: i32,
    out: &mut [u32],
    sw: u32,
    sh: u32,
) -> bool {
    out.fill(0);
    if src.len() != (lw as usize) * (lh as usize) || out.len() != (sw as usize) * (sh as usize) {
        return false;
    }
    for y in 0..sh as i64 {
        let sy = y - i64::from(top);
        if !(0..i64::from(lh)).contains(&sy) {
            continue;
        }
        for x in 0..sw as i64 {
            let sx = x - i64::from(left);
            if (0..i64::from(lw)).contains(&sx) {
                out[(y as usize) * (sw as usize) + x as usize] =
                    src[(sy as usize) * (lw as usize) + sx as usize];
            }
        }
    }
    true
}

/// 区画の数（横・縦）。
pub fn tile_grid(w: u32, h: u32) -> (u32, u32) {
    (w.div_ceil(TILE), h.div_ceil(TILE))
}

/// 区画の要約（FNV-1a・64 ビット）。全部が透明なら 0 を返す（送らなくてよい空の区画の印）。
pub fn tile_digest(px: &[u32], w: u32, h: u32, tx: u32, ty: u32) -> u64 {
    let (x0, y0) = (tx * TILE, ty * TILE);
    let (x1, y1) = ((x0 + TILE).min(w), (y0 + TILE).min(h));
    let mut hash: u64 = 0xcbf2_9ce4_8422_2325;
    let mut any = false;
    for y in y0..y1 {
        let row = (y * w) as usize;
        for x in x0..x1 {
            let v = clamp_premultiplied(px[row + x as usize]);
            any |= v >> 24 != 0;
            for b in v.to_le_bytes() {
                hash ^= u64::from(b);
                hash = hash.wrapping_mul(0x0000_0100_0000_01b3);
            }
        }
    }
    if any {
        hash | 1
    } else {
        0
    }
}

/// 送る区画。`rgba` が空なら「この区画を消す」。
pub struct TileOut {
    pub x: u32,
    pub y: u32,
    pub w: u32,
    pub h: u32,
    pub rgba: Vec<u8>,
}

/// 前回の要約 `prev`（区画の数と同じ長さ・初回は空）と今回の画素から、変わった区画を返し、`prev` を今回の要約に置き換える。
/// 画面の大きさが変わったら全部を送り直す。`px` は `w * h` 個の premultiplied の BGRA。
pub fn changed_tiles(prev: &mut Vec<u64>, px: &[u32], w: u32, h: u32) -> Vec<TileOut> {
    let (gx, gy) = tile_grid(w, h);
    let n = (gx * gy) as usize;
    if px.len() != (w as usize) * (h as usize) {
        return Vec::new();
    }
    let fresh = prev.len() != n;
    if fresh {
        prev.clear();
        prev.resize(n, 0);
    }
    let mut out = Vec::new();
    for ty in 0..gy {
        for tx in 0..gx {
            let i = (ty * gx + tx) as usize;
            let d = tile_digest(px, w, h, tx, ty);
            // 初回は空の区画を送らない（受け手の層は空から始まる）。
            if d == prev[i] && !(fresh && d != 0) {
                continue;
            }
            prev[i] = d;
            let (x0, y0) = (tx * TILE, ty * TILE);
            let (tw, th) = ((x0 + TILE).min(w) - x0, (y0 + TILE).min(h) - y0);
            let rgba = if d == 0 {
                Vec::new()
            } else {
                let mut v = Vec::with_capacity((tw * th * 4) as usize);
                for y in y0..y0 + th {
                    let row = (y * w) as usize;
                    for x in x0..x0 + tw {
                        v.extend_from_slice(&to_straight_rgba(px[row + x as usize]));
                    }
                }
                v
            };
            out.push(TileOut {
                x: x0,
                y: y0,
                w: tw,
                h: th,
                rgba,
            });
        }
    }
    out
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn restack_keeps_when_the_stage_is_the_first_visible_window_above_the_desktop() {
        assert!(decide_restack(true, Some(5), Some(9), 5) == Restack::Keep);
        // 見えない窓（IME など）がすぐ上にいても、見える窓の最初が自分なら動かさない（試作の B3 の行き来の原因）。
        assert!(decide_restack(true, Some(5), Some(9), 5) == Restack::Keep);
    }

    #[test]
    fn restack_goes_below_the_window_just_above_the_desktop() {
        // Win+D・デスクトップのクリックでデスクトップが前に出た: すぐ上の窓の下へ。
        assert!(decide_restack(true, Some(7), Some(7), 5) == Restack::Below(7));
        assert!(decide_restack(true, Some(7), Some(9), 5) == Restack::Below(9));
        assert!(decide_restack(true, None, Some(9), 5) == Restack::Below(9));
    }

    #[test]
    fn restack_falls_back_to_the_bottom_without_a_desktop() {
        assert!(decide_restack(false, Some(5), Some(5), 5) == Restack::Bottom);
        assert!(decide_restack::<u32>(true, None, None, 5) == Restack::Keep);
        assert!(decide_restack(true, Some(7), Some(5), 5) == Restack::Keep);
    }

    #[test]
    fn clamp_keeps_each_color_at_or_below_alpha() {
        assert_eq!(clamp_premultiplied(0x40FF_8020), 0x4040_4020);
        assert_eq!(clamp_premultiplied(0x00FF_FFFF), 0);
        assert_eq!(clamp_premultiplied(0xFF12_3456), 0xFF12_3456);
    }

    #[test]
    fn straight_rgba_undoes_premultiplication() {
        assert_eq!(to_straight_rgba(0xFF10_2030), [0x10, 0x20, 0x30, 0xFF]);
        assert_eq!(to_straight_rgba(0x8040_2000), [0x80, 0x40, 0x00, 0x80]);
        assert_eq!(to_straight_rgba(0x0000_0000), [0, 0, 0, 0]);
        // 色が透明度を超える画素は抑えてから直す（白を超えない）。
        assert_eq!(to_straight_rgba(0x40FF_FFFF), [0xFF, 0xFF, 0xFF, 0x40]);
    }

    #[test]
    fn crop_handles_a_virtual_screen_starting_at_negative_coordinates() {
        // 左に 2 の画面がある多画面: 一覧は (-2, -1) から 5 × 3。主画面は 3 × 2。
        let (lw, lh) = (5u32, 3u32);
        let src: Vec<u32> = (0..lw * lh).collect();
        let mut out = vec![99u32; 6];
        assert!(crop_primary(&src, lw, lh, -2, -1, &mut out, 3, 2));
        // 主画面の (0,0) は一覧の (2,1) = 1 * 5 + 2 = 7。
        assert_eq!(out, vec![7, 8, 9, 12, 13, 14]);
    }

    #[test]
    fn crop_leaves_transparent_where_the_list_does_not_cover() {
        // 一覧が主画面より小さく、右下へずれている。
        let src = vec![0xFF00_0001u32; 4];
        let mut out = vec![7u32; 9];
        assert!(crop_primary(&src, 2, 2, 1, 1, &mut out, 3, 3));
        assert_eq!(
            out,
            vec![
                0,
                0,
                0,
                0,
                0xFF00_0001,
                0xFF00_0001,
                0,
                0xFF00_0001,
                0xFF00_0001
            ]
        );
        // 長さが合わなければ全部透明にして偽。
        let mut out = vec![7u32; 9];
        assert!(!crop_primary(&src, 3, 2, 0, 0, &mut out, 3, 3));
        assert!(out.iter().all(|&v| v == 0));
    }

    fn frame(w: u32, h: u32) -> Vec<u32> {
        vec![0; (w * h) as usize]
    }

    #[test]
    fn first_pass_sends_only_non_empty_tiles_then_only_changes() {
        let (w, h) = (130, 70); // 区画は 3 × 2（端は切れる）
        let mut px = frame(w, h);
        px[(5 * w + 70) as usize] = 0xFF00_00FF; // 区画 (1,0)
        let mut prev = Vec::new();
        let out = changed_tiles(&mut prev, &px, w, h);
        assert_eq!(out.len(), 1);
        assert_eq!((out[0].x, out[0].y, out[0].w, out[0].h), (64, 0, 64, 64));
        assert_eq!(out[0].rgba.len(), 64 * 64 * 4);
        // 変わらなければ何も送らない。
        assert!(changed_tiles(&mut prev, &px, w, h).is_empty());
        // 区画 (1,0) を消し、端の区画 (2,1) に描く: 消す印（空）と、切れた大きさの区画。
        px[(5 * w + 70) as usize] = 0;
        px[(69 * w + 129) as usize] = 0xFFFF_FFFF;
        let out = changed_tiles(&mut prev, &px, w, h);
        assert_eq!(out.len(), 2);
        assert!(out[0].rgba.is_empty() && (out[0].x, out[0].y) == (64, 0));
        assert_eq!((out[1].x, out[1].y, out[1].w, out[1].h), (128, 64, 2, 6));
        assert_eq!(out[1].rgba.len(), 2 * 6 * 4);
    }

    #[test]
    fn a_size_change_resends_and_a_wrong_length_sends_nothing() {
        let mut prev = Vec::new();
        let mut px = frame(64, 64);
        px[0] = 0xFF00_0000;
        assert_eq!(changed_tiles(&mut prev, &px, 64, 64).len(), 1);
        let mut px2 = frame(128, 64);
        px2[0] = 0xFF00_0000;
        assert_eq!(changed_tiles(&mut prev, &px2, 128, 64).len(), 1);
        assert!(changed_tiles(&mut prev, &px2, 64, 64).is_empty());
    }
}
