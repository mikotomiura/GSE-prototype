import React, { useEffect, useState, useMemo, useRef } from 'react';
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
    const [showTypingWarning, setShowTypingWarning] = useState(false);
    const currentWindow = useMemo(() => getCurrentWindow(), []);

    // Wall発動中のキーボード打鍵検知に使うref群
    const wallStartTimeRef = useRef<number>(0);
    const lastWarnedKeyAtRef = useRef<number>(0);
    const warningTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

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

    // Wall発動時刻を記録し、Wall解除時にリセット
    useEffect(() => {
        if (isWallActive) {
            wallStartTimeRef.current = Date.now();
            lastWarnedKeyAtRef.current = 0;
            setShowTypingWarning(false);
        }
    }, [isWallActive]);

    // Wall発動中のキーボード打鍵検知: 打鍵を検知したら警告バナーを2.5秒表示
    // lastKeyAt = Date.now() - idle が wallStartTime より後なら Wall後の打鍵
    // 同一バーストへの重複警告を防ぐため1秒のデバウンスを設ける
    useEffect(() => {
        if (!isWallActive) {
            setShowTypingWarning(false);
            return;
        }
        const interval = setInterval(async () => {
            try {
                // get_last_keypress_timestamp() は Rust の LAST_KEY_MS をエポックmsで直接返す。
                // Date.now() - idle_ms の逆算より精度が高い (advice.md §D)
                const lastKeyAt = await invoke<number>("get_last_keypress_timestamp");
                if (
                    lastKeyAt > wallStartTimeRef.current &&
                    lastKeyAt > lastWarnedKeyAtRef.current + 1000
                ) {
                    lastWarnedKeyAtRef.current = lastKeyAt;
                    setShowTypingWarning(true);
                    if (warningTimerRef.current) clearTimeout(warningTimerRef.current);
                    warningTimerRef.current = setTimeout(() => setShowTypingWarning(false), 2500);
                }
            } catch (_) {}
        }, 300);
        return () => {
            clearInterval(interval);
            if (warningTimerRef.current) clearTimeout(warningTimerRef.current);
        };
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
                    {/* Wall発動中の打鍵警告バナー */}
                    {showTypingWarning && (
                        <div className="wall-typing-warning">
                            ⚠ キーボードは使えません！
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default Overlay;
