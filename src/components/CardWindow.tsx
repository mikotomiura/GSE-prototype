import React, { useEffect, useMemo, useState } from "react";
import { getCurrentWindow, currentMonitor } from "@tauri-apps/api/window";
import { PhysicalPosition } from "@tauri-apps/api/dpi";
import { invoke } from "@tauri-apps/api/core";
import ProbeCard from "./ProbeCard";

// 介入カード (Probe / Nudge) を載せる **不透明な専用小窓** のルート。
// 透明 overlay 窓は macOS でマウスイベントを webview へ配送しないため、カードはこの
// 不透明窓に分離する (overlay は全画面透明・Wall 専用)。
//
// 重要: macOS では hide() した窓 (orderOut) の webview JS が休眠し Tauri イベントを
// 取りこぼす (実測: probe_triggered が届かず onActiveChange(true) が出ない)。そこで
// **hide() せず、常に show のまま「画面外 ⇄ 右上」を setPosition で出し入れ**する。
// start_session で一度 show 済みなので JS は起き続ける。
const CARD_W = 380;
const CARD_MARGIN = 12;
const OFFSCREEN = -20000;

// DIAG TEMP: stdout へ可視化。検証後に削除する。
const dbg = (msg: string) => {
    void invoke("card_dbg", { msg }).catch(() => {});
};

const CardWindow: React.FC = () => {
    const win = useMemo(() => getCurrentWindow(), []);
    const [probeActive, setProbeActive] = useState(false);

    // マウント確認 + ハートビート (画面外退避中も JS が生きているかを stdout で確認)。
    useEffect(() => {
        dbg("CardWindow mounted");
        let n = 0;
        const hb = setInterval(() => {
            n += 1;
            dbg(`heartbeat ${n} (probeActive=${probeActive})`);
        }, 2000);
        return () => clearInterval(hb);
    // probeActive を依存に入れない (interval 再生成を避ける。値は closure 経由で十分)
    }, []); // eslint-disable-line react-hooks/exhaustive-deps

    const visible = probeActive;

    // 表示状態に応じて窓を「右上 ⇄ 画面外」へ移動する (hide はしない)。
    useEffect(() => {
        let cancelled = false;
        (async () => {
            try {
                if (visible) {
                    dbg("move on-screen (probeActive=true)");
                    const mon = await currentMonitor();
                    if (cancelled) return;
                    const scale = mon?.scaleFactor ?? 1;
                    const baseX = mon?.position.x ?? 0;
                    const baseY = mon?.position.y ?? 0;
                    const monW = mon?.size.width ?? 0;
                    const w = Math.round(CARD_W * scale);
                    const x = mon
                        ? Math.max(baseX, baseX + monW - w - Math.round(CARD_MARGIN * scale))
                        : 40;
                    const y = baseY + Math.round(CARD_MARGIN * scale);
                    await win.setPosition(new PhysicalPosition(x, y));
                    if (cancelled) return;
                    await win.setAlwaysOnTop(true).catch(() => {});
                    await win.show().catch(() => {}); // 念のため (既に show 済みのはず)
                    dbg("on-screen OK");
                } else {
                    await win.setPosition(new PhysicalPosition(OFFSCREEN, OFFSCREEN));
                    dbg("moved off-screen");
                }
            } catch (e) {
                dbg(`position FAILED: ${String(e)}`);
                console.error("card window reposition failed:", e);
            }
        })();
        return () => {
            cancelled = true;
        };
    }, [visible, win]);

    return (
        <div className="card-window-root">
            <ProbeCard
                onActiveChange={(active) => {
                    dbg(`ProbeCard onActiveChange(${active})`);
                    setProbeActive(active);
                }}
            />
        </div>
    );
};

export default CardWindow;
