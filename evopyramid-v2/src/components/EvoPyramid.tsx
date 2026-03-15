import React, { useMemo, useRef, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Billboard, Html, OrbitControls, QuadraticBezierLine, Text } from '@react-three/drei';
import * as THREE from 'three';
import { CENTER, EvoNode, SECTOR_COLORS } from '../lib/evo';

interface EvoPyramidProps {
  nodes: EvoNode[];
  onSelectNode: (node: EvoNode | null) => void;
  selectedNode: EvoNode | null;
  panX: number;
  panY: number;
  activeZLevel: number;
  viewMode: string;
}

const GRID_SPACING = 1.2;
const LEVEL_HEIGHT = 1.5;

interface NodeMeshProps {
  node: EvoNode;
  isSelected: boolean;
  isDimmed: boolean;
  onSelect: (node: EvoNode) => void;
  onDoubleClick: (node: EvoNode) => void;
  onLongPress: (node: EvoNode) => void;
}

function NodeMesh({ node, isSelected, isDimmed, onSelect, onDoubleClick, onLongPress }: NodeMeshProps) {
  const meshRef = useRef<THREE.Mesh>(null);
  const [hovered, setHovered] = useState(false);
  const timerRef = useRef<number | null>(null);
  const x = (node.x - CENTER) * GRID_SPACING;
  const y = (node.z - 1) * LEVEL_HEIGHT;
  const z = (node.y - CENTER) * GRID_SPACING;
  const isEmpty = node.kind === 'empty';
  const opacity = isDimmed ? 0.06 : isEmpty ? (node.type === 'link' ? 0.05 : 0.1) : node.type === 'link' ? 0.26 : 0.92;
  const nodeColor = isEmpty ? '#8fa4bf' : isSelected ? '#3b82f6' : hovered ? '#60a5fa' : SECTOR_COLORS[node.sector];

  useFrame((state) => {
    if (!meshRef.current) {
      return;
    }
    if (isSelected) {
      meshRef.current.rotation.y += 0.02;
      return;
    }
    if (node.status === 'active' && node.type === 'structural' && !isDimmed) {
      meshRef.current.scale.setScalar(1 + Math.sin(state.clock.elapsedTime * 2) * 0.02);
      return;
    }
    meshRef.current.rotation.y = 0;
    meshRef.current.scale.setScalar(1);
  });

  return (
    <mesh
      ref={meshRef}
      position={[x, y, z]}
      onClick={(event) => {
        event.stopPropagation();
        onSelect(node);
      }}
      onDoubleClick={(event) => {
        event.stopPropagation();
        onDoubleClick(node);
      }}
      onPointerDown={(event) => {
        event.stopPropagation();
        timerRef.current = window.setTimeout(() => onLongPress(node), 900);
      }}
      onPointerUp={(event) => {
        event.stopPropagation();
        if (timerRef.current !== null) {
          clearTimeout(timerRef.current);
        }
      }}
      onPointerLeave={() => {
        if (timerRef.current !== null) {
          clearTimeout(timerRef.current);
        }
        setHovered(false);
      }}
      onPointerOver={(event) => {
        event.stopPropagation();
        setHovered(true);
      }}
      onPointerOut={() => setHovered(false)}
    >
      <boxGeometry args={[0.8, 0.4, 0.8]} />
      <meshStandardMaterial
        color={nodeColor}
        transparent
        opacity={opacity}
        emissive={isEmpty ? '#000000' : node.status === 'failed' ? '#ef4444' : node.status === 'warning' ? '#f97316' : isSelected ? '#3b82f6' : '#000000'}
        emissiveIntensity={isEmpty ? 0 : isSelected ? 0.45 : node.status === 'failed' || node.status === 'warning' ? 0.5 : 0}
        roughness={0.68}
        metalness={0.1}
      />

      {!isDimmed && node.kind !== 'empty' && (
        <Billboard position={[0, 0.4, 0]}>
          <Text
            fontSize={isSelected || hovered ? 0.25 : 0.18}
            color={isSelected || hovered ? '#f8fafc' : '#e2e8f0'}
            anchorX="center"
            anchorY="bottom"
            outlineWidth={0.03}
            outlineColor="#031226"
            textAlign="center"
          >
            {node.label}
            {(isSelected || hovered) && `\n${node.kind} - ${node.status}`}
          </Text>
        </Billboard>
      )}

      {!isDimmed && node.kind !== 'empty' && (
        <Html transform position={[0, 1.1, 0]} distanceFactor={10} zIndexRange={[100, 0]}>
          <div className="flex flex-col items-center gap-1 pointer-events-none">
            {/* Architectural State Badge */}
            {node.status === 'quarantined' ? (
              <div className="px-1.5 py-0.5 rounded text-[7px] font-bold text-white bg-purple-600 shadow-sm whitespace-nowrap border border-purple-400/50">QUARANTINED</div>
            ) : node.status === 'degraded' || node.status === 'warning' ? (
              <div className="px-1.5 py-0.5 rounded text-[7px] font-bold text-black bg-amber-500 shadow-sm whitespace-nowrap border border-amber-400/50">DEGRADED</div>
            ) : node.runtime_canon_flag === 'canon' ? (
              <div className="px-1.5 py-0.5 rounded text-[7px] font-bold text-white bg-slate-900 shadow-sm whitespace-nowrap border border-slate-700/80">CANON</div>
            ) : node.runtime_canon_flag === 'runtime' ? (
              <div className="px-1.5 py-0.5 rounded text-[7px] font-bold text-slate-300 bg-black/40 shadow-sm whitespace-nowrap border border-slate-500/50">RUNTIME</div>
            ) : null}

            {/* Active Agents */}
            {node.activeAgents && node.activeAgents.length > 0 && (
              <div className="flex gap-1">
                {node.activeAgents.map((agent) => {
                  const colorMap: Record<string, string> = {
                    '#10a37f': 'bg-[#10a37f]',
                    '#4285f4': 'bg-[#4285f4]',
                    '#f5a623': 'bg-[#f5a623]',
                    '#7c3aed': 'bg-[#7c3aed]',
                    '#94a3b8': 'bg-[#94a3b8]',
                    '#1a73e8': 'bg-[#1a73e8]',
                    '#043b72': 'bg-[#043b72]',
                    '#d97757': 'bg-[#d97757]',
                  };
                  const bgClass = colorMap[agent.color.toLowerCase()] || 'bg-slate-600';
                  return (
                    <div
                      key={agent.id}
                      className={`px-1.5 py-0.5 rounded text-[8px] font-bold text-white shadow-sm whitespace-nowrap ${bgClass}`}
                    >
                      {agent.model}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </Html>
      )}
    </mesh>
  );
}

function EvoScene({
  nodes,
  onSelectNode,
  selectedNode,
  panX,
  panY,
  activeZLevel,
  focusNode,
  setFocusNode,
  routeNodes,
  onDoubleClick,
  onLongPress,
  viewMode,
}: {
  nodes: EvoNode[];
  onSelectNode: (node: EvoNode) => void;
  selectedNode: EvoNode | null;
  panX: number;
  panY: number;
  activeZLevel: number;
  focusNode: EvoNode | null;
  setFocusNode: (node: EvoNode | null) => void;
  routeNodes: EvoNode[];
  onDoubleClick: (node: EvoNode) => void;
  onLongPress: (node: EvoNode) => void;
  viewMode: string;
}) {
  const controlsRef = useRef<any>(null);
  const activeId = selectedNode?.id;
  const activeLinks = selectedNode?.links ?? [];

  const visibleNodes = useMemo(() => {
    let filtered = nodes;

    if (viewMode === 'active') {
      filtered = filtered.filter((node) => node.status === 'active' || node.status === 'warning');
    } else if (viewMode === 'canon') {
      filtered = filtered.filter((node) => node.kind === 'canon');
    } else if (viewMode === 'directory') {
      filtered = filtered.filter((node) => node.kind !== 'empty');
    } else if (viewMode === 'collaboration') {
      filtered = filtered.filter(
        (node) =>
          (node.activeAgents && node.activeAgents.length > 0) ||
          (selectedNode &&
            (node.id === selectedNode.id || selectedNode.links.includes(node.id) || node.links.includes(selectedNode.id))),
      );
    }

    if (activeZLevel > 0) {
      filtered = filtered.filter((node) => {
        if (node.z === activeZLevel) {
          return true;
        }
        if (!selectedNode) {
          return false;
        }
        return node.id === selectedNode.id || selectedNode.links.includes(node.id) || node.links.includes(selectedNode.id);
      });
    }

    return filtered;
  }, [activeZLevel, nodes, selectedNode, viewMode]);

  useFrame((state) => {
    if (!controlsRef.current) {
      return;
    }

    if (focusNode) {
      const target = new THREE.Vector3(
        (focusNode.x - CENTER) * GRID_SPACING,
        (focusNode.z - 1) * LEVEL_HEIGHT,
        (focusNode.y - CENTER) * GRID_SPACING,
      );
      const cameraTarget = target.clone().add(new THREE.Vector3(6, 4, 6));
      state.camera.position.lerp(cameraTarget, 0.05);
      controlsRef.current.target.lerp(target, 0.05);
      controlsRef.current.update();
      return;
    }

    const targetY = activeZLevel > 0 ? (activeZLevel - 1) * LEVEL_HEIGHT : (17 * LEVEL_HEIGHT) / 2 + (panY - 50) * 0.5;
    const targetX = activeZLevel > 0 ? 0 : (panX - 50) * 0.5;

    controlsRef.current.target.lerp(new THREE.Vector3(targetX, targetY, 0), 0.1);
    if (activeZLevel > 0) {
      const cameraPosition = state.camera.position;
      const nextCamera = new THREE.Vector3(cameraPosition.x, targetY + 2, cameraPosition.z);
      state.camera.position.lerp(nextCamera, 0.02);
    }
    controlsRef.current.update();
  });

  return (
    <>
      <fog attach="fog" args={['#0e2144', 24, 92]} />
      <ambientLight intensity={0.62} />
      <hemisphereLight args={['#7fb4f8', '#0b1324']} intensity={0.16} />
      <pointLight position={[10, 20, 10]} intensity={0.8} />
      <pointLight position={[-10, 10, -10]} intensity={0.6} />

      <OrbitControls
        ref={controlsRef}
        makeDefault
        target={[0, (17 * LEVEL_HEIGHT) / 2, 0]}
        enablePan
        enableZoom
        minDistance={2}
        maxDistance={100}
        maxPolarAngle={Math.PI}
      />

      <group>
        {selectedNode &&
          selectedNode.links.map((targetId) => {
            const targetNode = nodes.find((node) => node.id === targetId);
            if (!targetNode) {
              return null;
            }
            return (
              <QuadraticBezierLine
                key={`link-${selectedNode.id}-${targetId}`}
                start={[
                  (selectedNode.x - CENTER) * GRID_SPACING,
                  (selectedNode.z - 1) * LEVEL_HEIGHT,
                  (selectedNode.y - CENTER) * GRID_SPACING,
                ]}
                end={[
                  (targetNode.x - CENTER) * GRID_SPACING,
                  (targetNode.z - 1) * LEVEL_HEIGHT,
                  (targetNode.y - CENTER) * GRID_SPACING,
                ]}
                mid={[
                  ((selectedNode.x + targetNode.x) / 2 - CENTER) * GRID_SPACING,
                  Math.max(selectedNode.z, targetNode.z) * LEVEL_HEIGHT + 2,
                  ((selectedNode.y + targetNode.y) / 2 - CENTER) * GRID_SPACING,
                ]}
                color="#3b82f6"
                lineWidth={2}
                dashed
              />
            );
          })}

        {routeNodes.length === 2 && (
          <QuadraticBezierLine
            start={[
              (routeNodes[0].x - CENTER) * GRID_SPACING,
              (routeNodes[0].z - 1) * LEVEL_HEIGHT,
              (routeNodes[0].y - CENTER) * GRID_SPACING,
            ]}
            end={[
              (routeNodes[1].x - CENTER) * GRID_SPACING,
              (routeNodes[1].z - 1) * LEVEL_HEIGHT,
              (routeNodes[1].y - CENTER) * GRID_SPACING,
            ]}
            mid={[
              ((routeNodes[0].x + routeNodes[1].x) / 2 - CENTER) * GRID_SPACING,
              Math.max(routeNodes[0].z, routeNodes[1].z) * LEVEL_HEIGHT + 4,
              ((routeNodes[0].y + routeNodes[1].y) / 2 - CENTER) * GRID_SPACING,
            ]}
            color="#f97316"
            lineWidth={3}
            dashed
          />
        )}

        {visibleNodes.map((node) => {
          const isDimmed = Boolean(activeId && node.id !== activeId && !activeLinks.includes(node.id) && !node.links.includes(activeId));
          return (
            <NodeMesh
              key={node.id}
              node={node}
              isSelected={selectedNode?.id === node.id}
              isDimmed={isDimmed}
              onSelect={(selected) => {
                setFocusNode(null);
                onSelectNode(selected);
              }}
              onDoubleClick={onDoubleClick}
              onLongPress={onLongPress}
            />
          );
        })}
      </group>
    </>
  );
}

export default function EvoPyramid({
  nodes,
  onSelectNode,
  selectedNode,
  panX,
  panY,
  activeZLevel,
  viewMode = 'structure',
}: EvoPyramidProps) {
  const [focusNode, setFocusNode] = useState<EvoNode | null>(null);
  const [routeNodes, setRouteNodes] = useState<EvoNode[]>([]);

  return (
    <Canvas camera={{ position: [25, 20, 25], fov: 45 }} gl={{ antialias: true, alpha: true }} style={{ background: 'transparent' }}>
      <EvoScene
        nodes={nodes}
        onSelectNode={onSelectNode}
        selectedNode={selectedNode}
        panX={panX}
        panY={panY}
        activeZLevel={activeZLevel}
        viewMode={viewMode}
        focusNode={focusNode}
        setFocusNode={setFocusNode}
        routeNodes={routeNodes}
        onDoubleClick={(node) => {
          setFocusNode(node);
          onSelectNode(node);
        }}
        onLongPress={(node) => {
          setRouteNodes((prev) => {
            if (prev.length >= 2) {
              return [node];
            }
            if (prev.some((entry) => entry.id === node.id)) {
              return prev;
            }
            return [...prev, node];
          });
        }}
      />
    </Canvas>
  );
}


