import React, { useEffect, useState, useMemo } from 'react';
import { getCurrentWindow } from "@tauri-apps/api/window";
import { invoke } from "@tauri-apps/api/core";

interface OverlayProps {
    stuckProb: number;
    isWallActive: boolean;
}

interface WallServerInfo {
    url: string;
    qr_svg: string;
}

const Overlay: React.FC<OverlayProps> = ({ stuckProb, isWallActive }) => {
    const [nudgeOpacity, setNudgeOpacity] = useState(0);
    const [wallServerInfo, setWallServerInfo] = useState<WallServerInfo | null>(null);
    const currentWindow = useMemo(() => getCurrentWindow(), []);

    // 透過背景を設定（overlay ウィンドウ用）
    useEffect(() => {
        document.documentElement.style.background = 'transparent';
        document.body.style.background = 'transparent';
    }, []);

    // マウント直後に即座にクリック透過を有効化 (初期状態保証)
    // React の useEffect は最初のレンダー後に実行されるため、起動時に
    // オーバーレイが一瞬クリックをブロックしてウィンドウをドラッグ不能にする問題を防ぐ。
    useEffect(() => {
        currentWindow.setIgnoreCursorEvents(true).catch(() => {});
    // currentWindow は useMemo で安定しているが lint 警告を避けるため含める
    }, [currentWindow]); // eslint-disable-line react-hooks/exhaustive-deps

    // isWallActive に応じてクリック透過をトグル
    // Lv1 (nudge): クリック透過 → ユーザーは下のウィンドウを操作可能
    // Lv2 (wall):  クリックブロック → QRコードをスキャンするまで操作不可
    useEffect(() => {
        currentWindow.setIgnoreCursorEvents(!isWallActive);
    }, [isWallActive, currentWindow]);

    // Wall発動/解除に連動してWall Serverを起動/停止する
    useEffect(() => {
        if (isWallActive) {
            invoke<WallServerInfo>("start_wall_server")
                .then(info => setWallServerInfo(info))
                .catch(e => console.error("Failed to start wall server:", e));
        } else {
            invoke("stop_wall_server").catch(console.error);
            setWallServerInfo(null);
        }
    }, [isWallActive]);

    useEffect(() => {
        // Nudge Logic: visual feedback starts at 0.6 stuck probability
        if (stuckProb > 0.6 && !isWallActive) {
            // Map 0.6-0.9 to 0.0-1.0 opacity
            const opacity = Math.min(1, (stuckProb - 0.6) / 0.3);
            setNudgeOpacity(opacity);
        } else {
            setNudgeOpacity(0);
        }
    }, [stuckProb, isWallActive]);

    return (
        <div className="overlay-root">
            {/* Nudge Layer (Red Vignette) */}
            <div
                className="nudge-layer"
                style={{ opacity: nudgeOpacity }}
            ></div>

            {/* The Wall (Blocking Layer) */}
            {isWallActive && (
                <div className="wall-layer">
                    <h1>Time to Move!</h1>
                    <p>スマートフォンでQRコードをスキャンして解除</p>
                    {wallServerInfo ? (
                        <>
                            {/* base64エンコードされたSVG QRコードをimg要素で表示 */}
                            <img
                                className="qr-code"
                                src={wallServerInfo.qr_svg}
                                alt="QR Code"
                            />
                            <p className="wall-url">{wallServerInfo.url}</p>
                        </>
                    ) : (
                        <div className="scramble-animation">
                            <span>QR生成中...</span>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default Overlay;
