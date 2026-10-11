import React from "react";

// EH3 の招待の図像（Physical Anchor の PC 面・ADR-026）。
//
// 守ること（`.steering/20261011-portrait-eh3-prereg/implementation-requirements.md` R-I1・R-I11・R-I14）:
// - 文字を置かない。状態も理由も言わない（aria-label は支援技術のための操作名だけ）。
// - 提示ごとに不変: 大きさ・動き・色・出ている時間で、強さや回数を表さない（props で変えられる値は形の候補だけ）。
// - 量（回数・残り・時刻）を描かない。
// - 肖像（壁紙）の色を使わない・壁紙の一部に見せない。
// ⚠️ この検査は `scripts/check_invitation_surface.py` が静的に行う（ADR-026 M11 ①）。

// 図像の候補。研究者が見本で 1 つに選ぶ（F-3）。選ぶまでは "door" を使う。
export type GlyphVariant = "door" | "horizon" | "steps";

// 配布物で使う図像（overlay の図像と、説明と設定の窓の「この印」の両方がこれを使う）。
// ⚠️ 選んだ図像に替えるときは、ここ 1 か所だけを替える（`docs/eh3-distribution-tag.md` §1）。
export const INVITATION_GLYPH: GlyphVariant = "door";

export const GLYPH_SIZE_PX = 40;

const STROKE = "#4b5563";
const FILL = "#f3f4f6";

const paths: Record<GlyphVariant, React.ReactElement> = {
    // 少し開いた扉
    door: (
        <g fill="none" stroke={STROKE} strokeWidth={2} strokeLinejoin="round">
            <rect x={11} y={7} width={18} height={26} />
            <path d="M11 7 L22 10 L22 36 L11 33 Z" fill={STROKE} fillOpacity={0.15} />
        </g>
    ),
    // 地平線と半分の円
    horizon: (
        <g fill="none" stroke={STROKE} strokeWidth={2} strokeLinecap="round">
            <path d="M8 27 H32" />
            <path d="M13 27 A7 7 0 0 1 27 27" />
        </g>
    ),
    // 二つの足あと
    steps: (
        <g fill={STROKE} fillOpacity={0.55}>
            <ellipse cx={15} cy={24} rx={4} ry={6.5} />
            <ellipse cx={25} cy={15} rx={4} ry={6.5} />
        </g>
    ),
};

interface InvitationGlyphProps {
    variant: GlyphVariant;
}

const InvitationGlyph: React.FC<InvitationGlyphProps> = ({ variant }) => (
    <svg
        width={GLYPH_SIZE_PX}
        height={GLYPH_SIZE_PX}
        viewBox="0 0 40 40"
        aria-hidden="true"
        focusable="false"
    >
        <circle cx={20} cy={20} r={19} fill={FILL} stroke={STROKE} strokeOpacity={0.25} />
        {paths[variant]}
    </svg>
);

export default InvitationGlyph;
