import { useState, useEffect, useCallback } from 'react';
import { EvoNode, generateMockNodes } from './evo';

const WS_URL = 'ws://127.0.0.1:8000/ws';

export function usePyramidState() {
    const [nodes, setNodes] = useState<EvoNode[]>(generateMockNodes());
    const [isConnected, setIsConnected] = useState(false);

    useEffect(() => {
        let ws: WebSocket;
        let reconnectTimeout: number;

        const connect = () => {
            ws = new WebSocket(WS_URL);

            ws.onopen = () => {
                console.log('Connected to EvoPyramid Core Engine');
                setIsConnected(true);
            };

            ws.onmessage = (event) => {
                const message = JSON.parse(event.data);
                handleMessage(message);
            };

            ws.onclose = () => {
                console.log('Disconnected from Core Engine. Reconnecting...');
                setIsConnected(false);
                reconnectTimeout = window.setTimeout(connect, 3000);
            };

            ws.onerror = (error) => {
                console.error('WebSocket Error:', error);
                ws.close();
            };
        };

        const handleMessage = (message: any) => {
            switch (message.type) {
                case 'full_state':
                    // Convert Python models to EvoNode format if necessary
                    // For now, we merge with our static structure
                    updateNodesFromBackend(message.data.nodes);
                    break;
                case 'node_update':
                    updateSingleNode(message.data);
                    break;
                default:
                    break;
            }
        };

        const updateNodesFromBackend = (backendNodes: Record<string, any>) => {
            setNodes((prevNodes) => {
                return prevNodes.map((node) => {
                    const update = backendNodes[node.id];
                    if (update) {
                        return {
                            ...node,
                            status: update.state,
                            label: update.title,
                            description: update.summary,
                            kind: update.kind,
                            // Add other fields as they mapped
                        };
                    }
                    return node;
                });
            });
        };

        const updateSingleNode = (update: any) => {
            setNodes((prevNodes) => {
                return prevNodes.map((node) => {
                    if (node.id === update.id) {
                        return {
                            ...node,
                            status: update.state,
                            label: update.title,
                            description: update.summary,
                            kind: update.kind,
                        };
                    }
                    return node;
                });
            });
        };

        connect();

        return () => {
            if (ws) ws.close();
            clearTimeout(reconnectTimeout);
        };
    }, []);

    return { nodes, isConnected };
}
