
import React, { useMemo, useRef, useState, useEffect } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Text, Html, QuadraticBezierLine, Billboard } from '@react-three/drei';
import * as THREE from 'three';
import { generateMockNodes, SECTOR_COLORS, STATUS_COLORS, EvoNode, CENTER } from '../lib/evo';

interface EvoPyramidProps {
  onSelectNode: (node: EvoNode | null) => void;
  selectedNode: EvoNode | null;
  panX: number;
  panY: number;
  activeZLevel: number;
  viewMode: string;
}

const GRID_SPACING = 1.2; // Space between nodes
const LEVEL_HEIGHT = 1.5; // Space between levels

const AgentHtmlBadge: React.FC<{ model: string; color: string }> = ({ model, color }) => {
  const badgeRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (badgeRef.current) {
      badgeRef.current.style.backgroundColor = color;
    }
  }, [color]);

  return (
    <div
      ref={badgeRef}
      className="px-1.5 py-0.5 rounded text-[8px] font-bold text-white shadow-sm whitespace-nowrap"
    >
      🤖 {model}
    </div>
  );
};

interface NodeMeshProps {
  node: EvoNode;
  isSelected: boolean;
  isDimmed: boolean;
  onClick: (e: any) => void;
  onDoubleClick: (node: EvoNode) => void;
  onLongPress: (node: EvoNode) => void;
}

const NodeMesh: React.FC<NodeMeshProps> = ({
  node,
  isSelected,
  isDimmed,
  onClick,
  onDoubleClick,
  onLongPress
}) => {
  const meshRef = useRef<THREE.Mesh>(null);
  const [hovered, setHover] = useState(false);
  const longPressTimer = useRef<NodeJS.Timeout | undefined>(undefined);

  // Calculate position based on grid coordinates
  // Center is (9,9), so offset by CENTER
  const x = (node.x - CENTER) * GRID_SPACING;
  const z = (node.y - CENTER) * GRID_SPACING; // Y in grid is Z in 3D space usually
  const y = (node.z - 1) * LEVEL_HEIGHT;

  const baseColor = SECTOR_COLORS[node.sector as keyof typeof SECTOR_COLORS] || '#ffffff';

  // Mix status color if not active
  const statusColor = STATUS_COLORS[node.status] || '#ffffff';

  useFrame((state) => {
    if (meshRef.current) {
      if (isSelected) {
        meshRef.current.rotation.y += 0.02;
      } else if (node.status === 'active' && node.type === 'structural' && !isDimmed) {
        // Subtle pulse for active nodes
        meshRef.current.scale.setScalar(1 + Math.sin(state.clock.elapsedTime * 2) * 0.02);
      } else {
        meshRef.current.rotation.y = 0;
        meshRef.current.scale.setScalar(1);
      }
    }
  });

  const handlePointerDown = (e: any) => {
    e.stopPropagation();
    longPressTimer.current = setTimeout(() => {
      onLongPress(node);
    }, 1000); // 1 second long press
  };

  const handlePointerUp = (e: any) => {
    e.stopPropagation();
    if (longPressTimer.current) {
      clearTimeout(longPressTimer.current);
    }
  };

  const handleDoubleClick = (e: any) => {
    e.stopPropagation();
    onDoubleClick(node);
  };

  const isFocused = isSelected || hovered;
  const opacity = isDimmed ? 0.1 : (node.type === 'link' ? 0.3 : 0.9);

  return (
    <mesh
      ref={meshRef}
      position={[x, y, z]}
      onClick={(e) => {
        e.stopPropagation();
        onClick(e);
      }}
      onDoubleClick={handleDoubleClick}
      onPointerDown={handlePointerDown}
      onPointerUp={handlePointerUp}
      onPointerLeave={handlePointerUp}
      onPointerOver={(e) => { e.stopPropagation(); setHover(true); }}
      onPointerOut={() => setHover(false)}
    >
      <boxGeometry args={[0.8, 0.4, 0.8]} />
      <meshStandardMaterial
        color={isSelected ? '#3b82f6' : (hovered ? '#60a5fa' : baseColor)}
        transparent
        opacity={opacity}
        emissive={node.status === 'failed' ? '#ef4444' : (node.status === 'warning' ? '#f97316' : (isSelected ? '#3b82f6' : '#000000'))}
        emissiveIntensity={isSelected ? 0.5 : ((node.status === 'failed' || node.status === 'warning') && !isDimmed ? 0.5 : 0)}
      />

      {/* Node Face Label (Billboard) */}
      {!isDimmed && node.kind !== 'empty' && (
        <Billboard position={[0, 0.4, 0]}>
          <Text
            fontSize={isFocused ? 0.25 : 0.18}
            color={isFocused ? '#111827' : '#6b7280'}
            anchorX="center"
            anchorY="bottom"
            outlineWidth={0.03}
            outlineColor="#ffffff"
            textAlign="center"
          >
            {node.label}
            {isFocused && `\n${node.kind} • ${node.status}`}
          </Text>
        </Billboard>
      )}

      {/* Agent Activity Badges */}
      {!isDimmed && node.activeAgents && node.activeAgents.length > 0 && (
        <Html transform position={[0, 0.8, 0]} distanceFactor={10} zIndexRange={[100, 0]}>
          <div className="flex gap-1 pointer-events-none">
            {node.activeAgents.map(agent => (
              <AgentHtmlBadge key={agent.id} model={agent.model} color={agent.color} />
            ))}
          </div>
        </Html>
      )}
    </mesh>
  );
};

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
  handleDoubleClick,
  handleLongPress,
  viewMode
}: any) {
  const controlsRef = useRef<any>(null);

  // Filter nodes based on viewMode and activeZLevel
  const visibleNodes = useMemo(() => {
    let filtered = nodes;
    if (viewMode === 'active') filtered = filtered.filter((n: EvoNode) => n.status === 'active' || n.status === 'warning');
    else if (viewMode === 'canon') filtered = filtered.filter((n: EvoNode) => n.kind === 'canon');
    else if (viewMode === 'directory') filtered = filtered.filter((n: EvoNode) => n.kind !== 'empty');
    else if (viewMode === 'collaboration') filtered = filtered.filter((n: EvoNode) => (n.activeAgents && n.activeAgents.length > 0) || (selectedNode && (n.id === selectedNode.id || selectedNode.links.includes(n.id) || n.links.includes(selectedNode.id))));

    if (activeZLevel > 0) {
      filtered = filtered.filter((n: EvoNode) => {
        // Show nodes exactly on this Z-level
        if (n.z === activeZLevel) return true;

        // If a node is selected, also show nodes it connects to (or that connect to it)
        if (selectedNode) {
          if (n.id === selectedNode.id) return true;
          if (selectedNode.links.includes(n.id)) return true;
          if (n.links.includes(selectedNode.id)) return true;
        }
        return false;
      });
    }

    return filtered;
  }, [nodes, viewMode, activeZLevel, selectedNode]);

  // Determine dimming
  const activeNodeId = selectedNode?.id;
  const activeNodeLinks = selectedNode?.links || [];

  // Camera animation for focus and Z-level panning
  useFrame((state) => {
    if (focusNode && controlsRef.current) {
      const targetPos = new THREE.Vector3(
        (focusNode.x - CENTER) * GRID_SPACING,
        (focusNode.z - 1) * LEVEL_HEIGHT,
        (focusNode.y - CENTER) * GRID_SPACING
      );

      // Move camera slightly above and in front of the node
      const camPos = targetPos.clone().add(new THREE.Vector3(6, 4, 6));

      state.camera.position.lerp(camPos, 0.05);
      controlsRef.current.target.lerp(targetPos, 0.05);
      controlsRef.current.update();
    } else if (controlsRef.current) {
      // Smoothly pan to Z-level or manual pan position
      const targetY = activeZLevel > 0
        ? (activeZLevel - 1) * LEVEL_HEIGHT
        : ((17 * LEVEL_HEIGHT) / 2) + (panY - 50) * 0.5;

      const targetX = activeZLevel > 0 ? 0 : (panX - 50) * 0.5;

      const targetPos = new THREE.Vector3(targetX, targetY, 0);
      controlsRef.current.target.lerp(targetPos, 0.1);

      // If snapping to a Z-level, also gently pull the camera to a horizontal view
      if (activeZLevel > 0) {
        const currentCamPos = state.camera.position;
        const desiredCamPos = new THREE.Vector3(currentCamPos.x, targetY + 2, currentCamPos.z);
        state.camera.position.lerp(desiredCamPos, 0.02); // Slower lerp for camera position so it doesn't feel jarring
      }

      controlsRef.current.update();
    }
  });

  // Remove the old useEffect for panning since useFrame handles it now smoothly

  return (
    <>
      <color attach="background" args={['#fafafa']} />
      <ambientLight intensity={0.8} />
      <pointLight position={[10, 20, 10]} intensity={0.8} />
      <pointLight position={[-10, 10, -10]} intensity={0.5} />

      <OrbitControls
        ref={controlsRef}
        makeDefault
        target={[0, (17 * LEVEL_HEIGHT) / 2, 0]}
        enablePan={true}
        enableZoom={true}
        minDistance={2}
        maxDistance={100}
        maxPolarAngle={Math.PI} // Allow looking from below if desired
      />

      <group>
        {/* Render Selected Node Links */}
        {selectedNode && selectedNode.links.map((targetId: string) => {
          const targetNode = nodes.find((n: EvoNode) => n.id === targetId);
          if (!targetNode) return null;
          return (
            <QuadraticBezierLine
              key={`link-${selectedNode.id}-${targetId}`}
              start={[
                (selectedNode.x - CENTER) * GRID_SPACING,
                (selectedNode.z - 1) * LEVEL_HEIGHT,
                (selectedNode.y - CENTER) * GRID_SPACING
              ]}
              end={[
                (targetNode.x - CENTER) * GRID_SPACING,
                (targetNode.z - 1) * LEVEL_HEIGHT,
                (targetNode.y - CENTER) * GRID_SPACING
              ]}
              mid={[
                ((selectedNode.x + targetNode.x) / 2 - CENTER) * GRID_SPACING,
                Math.max(selectedNode.z, targetNode.z) * LEVEL_HEIGHT + 2,
                ((selectedNode.y + targetNode.y) / 2 - CENTER) * GRID_SPACING
              ]}
              color="#3b82f6" // blue-500
              lineWidth={2}
              dashed
            />
          );
        })}

        {/* Render Routing Lines (Long Press) */}
        {routeNodes.length === 2 && (
          <QuadraticBezierLine
            start={[
              (routeNodes[0].x - CENTER) * GRID_SPACING,
              (routeNodes[0].z - 1) * LEVEL_HEIGHT,
              (routeNodes[0].y - CENTER) * GRID_SPACING
            ]}
            end={[
              (routeNodes[1].x - CENTER) * GRID_SPACING,
              (routeNodes[1].z - 1) * LEVEL_HEIGHT,
              (routeNodes[1].y - CENTER) * GRID_SPACING
            ]}
            mid={[
              ((routeNodes[0].x + routeNodes[1].x) / 2 - CENTER) * GRID_SPACING,
              Math.max(routeNodes[0].z, routeNodes[1].z) * LEVEL_HEIGHT + 5,
              ((routeNodes[0].y + routeNodes[1].y) / 2 - CENTER) * GRID_SPACING
            ]}
            color="#f97316" // orange-500
            lineWidth={3}
            dashed
          />
        )}

        {/* Render Nodes */}
        {visibleNodes.map((node: EvoNode) => {
          // Dimming logic: if a node is selected, dim everything except the selected node and its direct links
          let isDimmed = false;
          if (activeNodeId) {
            if (node.id !== activeNodeId && !activeNodeLinks.includes(node.id)) {
              // Also check if the node links TO the active node
              if (!node.links.includes(activeNodeId)) {
                isDimmed = true;
              }
            }
          }

          return (
            <NodeMesh
              key={node.id}
              node={node}
              isSelected={selectedNode?.id === node.id}
              isDimmed={isDimmed}
              onClick={() => {
                setFocusNode(null); // Reset focus on single click so sliders work again
                onSelectNode(node);
              }}
              onDoubleClick={handleDoubleClick}
              onLongPress={handleLongPress}
            />
          );
        })}
      </group>
    </>
  );
}

export default function EvoPyramid({ nodes, onSelectNode, selectedNode, panX, panY, activeZLevel, viewMode = 'structure' }: EvoPyramidProps & { nodes: EvoNode[] }) {
  const [focusNode, setFocusNode] = useState<EvoNode | null>(null);
  const [routeNodes, setRouteNodes] = useState<EvoNode[]>([]);

  // Handle double click to focus camera
  const handleDoubleClick = (node: EvoNode) => {
    setFocusNode(node);
    onSelectNode(node);
  };

  // Handle long press to route
  const handleLongPress = (node: EvoNode) => {
    setRouteNodes(prev => {
      if (prev.length >= 2) return [node]; // Reset if already 2
      if (prev.find(n => n.id === node.id)) return prev; // Ignore duplicate
      return [...prev, node];
    });
  };

  return (
    <Canvas camera={{ position: [25, 20, 25], fov: 45 }}>
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
        handleDoubleClick={handleDoubleClick}
        handleLongPress={handleLongPress}
      />
    </Canvas>
  );
}

