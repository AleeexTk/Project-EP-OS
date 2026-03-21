
/**
 * EvoPyramid OS - Hardware Probe
 * Paste into Console (F12) to test WebSocket connectivity.
 */
(async function() {
    console.log("%c EvoPyramid OS: Socket Probe Starting...", "color: #3b82f6; font-weight: bold; font-size: 14px;");

    const testSocket = (name, url) => {
        return new Promise((resolve) => {
            console.log(`Testing ${name}: ${url}...`);
            const ws = new WebSocket(url);
            const timeout = setTimeout(() => {
                console.error(`%c ${name} FAILED (Timeout)`, "color: #ef4444;");
                ws.close();
                resolve(false);
            }, 3000);

            ws.onopen = () => {
                clearTimeout(timeout);
                console.log(`%c ${name} CONNECTED.`, "color: #10b981; font-weight: bold;");
                ws.close();
                resolve(true);
            };

            ws.onerror = (e) => {
                clearTimeout(timeout);
                console.error(`%c ${name} ERROR:`, "color: #ef4444;", e);
                resolve(false);
            };
        });
    };

    const mainOk = await testSocket("Main Z-Bus (/ws)", "ws://127.0.0.1:8000/ws");
    const swarmOk = await testSocket("Swarm Tab (/v1/ws/swarm)", "ws://127.0.0.1:8000/v1/ws/swarm");

    if (mainOk && swarmOk) {
        console.log("%c CONNECTIVITY AUDIT PASSED.", "color: #10b981; font-weight: bold; font-size: 14px;");
    } else {
        console.error("%c CONNECTIVITY AUDIT FAILED.", "color: #ef4444; font-weight: bold; font-size: 14px;");
        console.log("Check if Python is running and port 8000 is open.");
    }
})();
