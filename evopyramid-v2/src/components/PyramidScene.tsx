import React, { useMemo, useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Float, PerspectiveCamera, OrbitControls, Stars, Line } from '@react-three/drei';
import * as THREE from 'three';
import { EvoNode } from '../lib/evo';

interface PyramidSceneProps {
  nodes: EvoNode[];
  selectedNodeId: string | null;
  onSelectNode: (id: string | null) => void;
}

function NodePoints({ nodes, selectedNodeId, onSelectNode }: PyramidSceneProps) {
  return (
    <>
      {nodes.map((node) => {
        const isSelected = node.id === selectedNodeId;
        // Same formula as WireframePyramid layers
        const y = (node.z - 8.5) * 0.45;
        const layerWidth = (18 - node.z) * 0.4;
        
        // Map node.x/node.y (0-100) to local layer coordinate space
        // node.x - 50 is [-50, 50]. 
        // We want to map this to [-layerWidth, layerWidth]
        const x = ((node.x - 50) / 50) * layerWidth;
        const z = ((node.y - 50) / 50) * layerWidth;

        return (
          <Float key={node.id} speed={2} rotationIntensity={0.5} floatIntensity={0.5}>
            <mesh 
              position={[x, y, z]} 
              onClick={(e) => {
                e.stopPropagation();
                onSelectNode(node.id);
              }}
            >
              <sphereGeometry args={[0.12, 16, 16]} />
              <meshStandardMaterial 
                color={isSelected ? '#10b981' : (node.layer === 'alpha' ? '#3b82f6' : '#94a3b8')} 
                emissive={isSelected ? '#10b981' : (node.layer === 'alpha' ? '#3b82f6' : '#000000')}
                emissiveIntensity={isSelected ? 4 : 1.5}
                toneMapped={false}
              />
            </mesh>
          </Float>
        );
      })}
    </>
  );
}

function WireframePyramid() {
  const meshRef = useRef<THREE.Group>(null);

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.y = state.clock.getElapsedTime() * 0.05;
    }
  });

  const layers = useMemo(() => {
    const items = [];
    for (let i = 1; i <= 17; i++) {
      const width = (18 - i) * 0.4;
      const y = (i - 8.5) * 0.45;
      items.push({ i, width, y });
    }
    return items;
  }, []);

  return (
    <group ref={meshRef}>
      {layers.map((layer: any) => (
        <mesh key={layer.i} position={[0, layer.y, 0]} rotation={[Math.PI / 2, 0, Math.PI / 4]}>
          <ringGeometry args={[layer.width - 0.02, layer.width, 4]} />
          <meshBasicMaterial color="#3b82f6" opacity={0.2} transparent />
        </mesh>
      ))}
      {/* Connecting "Spines" */}
      {[0, 1, 2, 3].map((corner) => {
        const points = layers.map((l: any) => {
          const angle = (corner * Math.PI / 2) + Math.PI / 4;
          return new THREE.Vector3(l.width * Math.SQRT2 * Math.cos(angle), l.y, l.width * Math.SQRT2 * Math.sin(angle));
        });
        return (
          <Line
            key={corner}
            points={points}
            color="#3b82f6"
            lineWidth={2}
            opacity={0.3}
            transparent
          />
        );
      })}

      {/* Central "Truth" Axis */}
      <Line
        points={[
          new THREE.Vector3(0, layers[0].y - 1, 0),
          new THREE.Vector3(0, layers[layers.length - 1].y + 1, 0)
        ]}
        color="#10b981"
        lineWidth={1}
        opacity={0.4}
        transparent
        dashed
        dashSize={0.2}
        gapSize={0.1}
      />

      {/* Solid Foundation at Z1 (Layer 0) */}
      <mesh position={[0, layers[0].y, 0]} rotation={[Math.PI / 2, 0, Math.PI / 4]}>
        <planeGeometry args={[layers[0].width * 2, layers[0].width * 2]} />
        <meshBasicMaterial color="#071024" opacity={0.6} transparent />
      </mesh>
      <mesh position={[0, layers[0].y, 0]} rotation={[Math.PI / 2, 0, Math.PI / 4]}>
        <ringGeometry args={[layers[0].width - 0.05, layers[0].width, 4]} />
        <meshBasicMaterial color="#10b981" opacity={1} transparent />
      </mesh>

      {/* Large Environmental Grid */}
      <gridHelper args={[40, 20, '#1e293b', '#0f172a']} position={[0, layers[0].y - 0.1, 0]} />
    </group>
  );
}

export default function PyramidScene({ nodes, selectedNodeId, onSelectNode }: PyramidSceneProps) {
  return (
    <div className="w-full h-full absolute inset-0 z-0 pointer-events-auto">
      <Canvas shadows dpr={[1, 2]} gl={{ alpha: true, preserveDrawingBuffer: true }}>
        <PerspectiveCamera makeDefault position={[0, 0, 18]} fov={30} />
        <OrbitControls 
          enableZoom={false} 
          enablePan={false} 
          autoRotate 
          autoRotateSpeed={0.3} 
          target={[0, 0, 0]}
        />
        
        <ambientLight intensity={0.4} />
        <pointLight position={[10, 10, 10]} intensity={2} color="#3b82f6" />
        <pointLight position={[-10, -10, -10]} intensity={1} color="#10b981" />

        <NodePoints nodes={nodes} selectedNodeId={selectedNodeId} onSelectNode={onSelectNode} />
        <WireframePyramid />
      </Canvas>

      {/* Glassmorphism Title Overlay */}
      <div className="absolute bottom-10 left-10 p-6 rounded-2xl border border-white/10 bg-black/20 backdrop-blur-xl pointer-events-none">
        <h2 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent">
          Nucleus V2
        </h2>
        <p className="text-sm text-slate-400">3D Cognitive Mapping Active</p>
      </div>
    </div>
  );
}
