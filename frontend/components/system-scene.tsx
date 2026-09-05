'use client'

import { Canvas, useFrame } from '@react-three/fiber'
import { useEffect, useMemo, useRef, useState } from 'react'
import * as THREE from 'three'
import { project } from '@/lib/engine'

const positions = [
  [-2.3, 1.2, 0.2],
  [-0.9, 2.15, -0.25],
  [1.05, 2.0, 0.15],
  [2.35, 0.7, -0.1],
  [2.0, -1.35, 0.2],
  [0.15, -2.15, -0.15],
  [-2.05, -1.25, 0.15],
] as const

const vertexShader = `
varying vec3 vPosition;
varying vec3 vNormal;
uniform float uTime;
void main() {
  vPosition = position;
  vNormal = normal;
  float wave = sin(position.y * 4.0 + uTime * 1.2) * 0.035;
  wave += sin(position.x * 5.0 - uTime * 0.8) * 0.025;
  vec3 displaced = position + normal * wave;
  gl_Position = projectionMatrix * modelViewMatrix * vec4(displaced, 1.0);
}`

const fragmentShader = `
varying vec3 vPosition;
varying vec3 vNormal;
uniform float uTime;
uniform vec3 uAccent;
uniform vec3 uSecondary;
void main() {
  float bands = sin((vPosition.x + vPosition.y) * 8.0 + uTime * 1.5) * 0.5 + 0.5;
  float flow = sin(vPosition.y * 12.0 - uTime * 2.0 + sin(vPosition.x * 4.0)) * 0.5 + 0.5;
  float fresnel = pow(1.0 - abs(dot(normalize(vNormal), vec3(0.0, 0.0, 1.0))), 2.4);
  vec3 base = mix(uSecondary * 0.42, uAccent, smoothstep(0.2, 0.9, bands * 0.65 + flow * 0.35));
  vec3 metal = mix(base * 0.45, vec3(0.95), fresnel * 0.72);
  gl_FragColor = vec4(metal, 0.94 + fresnel * 0.06);
}`

function LiquidCore({ reducedMotion }: { reducedMotion: boolean }) {
  const mesh = useRef<THREE.Mesh>(null)
  const material = useMemo(() => new THREE.ShaderMaterial({
    vertexShader,
    fragmentShader,
    uniforms: {
      uTime: { value: 0 },
      uAccent: { value: new THREE.Color(project.accent) },
      uSecondary: { value: new THREE.Color(project.secondary) },
    },
    transparent: true,
  }), [])

  useEffect(() => () => material.dispose(), [material])
  useFrame((state) => {
    if (reducedMotion) return
    material.uniforms.uTime.value = state.clock.elapsedTime
    if (mesh.current) {
      mesh.current.rotation.y = state.clock.elapsedTime * 0.16
      mesh.current.rotation.x = Math.sin(state.clock.elapsedTime * 0.23) * 0.12
    }
  })

  return <mesh ref={mesh}><icosahedronGeometry args={[0.92, 6]} /><primitive object={material} attach="material" /></mesh>
}

function Network({ activeIndex, completed, reducedMotion }: { activeIndex: number; completed: number; reducedMotion: boolean }) {
  const count = Math.min(project.nodes.length, positions.length)
  const geometry = useMemo(() => {
    const values: number[] = []
    positions.slice(0, count).forEach((position) => values.push(0, 0, 0, position[0], position[1], position[2]))
    const buffer = new THREE.BufferGeometry()
    buffer.setAttribute('position', new THREE.Float32BufferAttribute(values, 3))
    return buffer
  }, [count])
  const lineMaterial = useMemo(() => new THREE.LineBasicMaterial({ color: project.accent, transparent: true, opacity: 0.34 }), [])
  useEffect(() => () => { geometry.dispose(); lineMaterial.dispose() }, [geometry, lineMaterial])

  return (
    <group>
      <lineSegments geometry={geometry} material={lineMaterial} />
      <LiquidCore reducedMotion={reducedMotion} />
      {positions.slice(0, count).map((position, index) => {
        const active = index === activeIndex
        const done = index < completed
        return (
          <mesh key={project.nodes[index]} position={position} scale={active ? 1.35 : done ? 1.13 : 1}>
            <sphereGeometry args={[0.16, 28, 28]} />
            <meshStandardMaterial color={active || done ? '#f3f4ff' : '#28313d'} emissive={active ? project.accent : done ? project.secondary : '#000000'} emissiveIntensity={active ? 2.2 : 0.7} roughness={0.3} metalness={0.55} />
          </mesh>
        )
      })}
    </group>
  )
}

function supportsWebGL() {
  try {
    const canvas = document.createElement('canvas')
    return Boolean(canvas.getContext('webgl2') || canvas.getContext('webgl'))
  } catch { return false }
}

export function SystemScene({ activeIndex = -1, completed = 0, reducedMotion = false }: { activeIndex?: number; completed?: number; reducedMotion?: boolean }) {
  const [webgl, setWebgl] = useState<boolean | null>(null)
  useEffect(() => setWebgl(supportsWebGL()), [])

  if (webgl === false) return <div className="scene-fallback"><strong>{project.name}</strong><span>{project.nodes.join(' · ')}</span></div>
  if (webgl === null) return <div className="scene-fallback" aria-hidden="true" />

  return (
    <Canvas camera={{ position: [0, 0, 6.4], fov: 42 }} dpr={[1, 1.5]} frameloop={reducedMotion ? 'demand' : 'always'} gl={{ antialias: true, alpha: true, powerPreference: 'high-performance' }}>
      <ambientLight intensity={0.8} />
      <pointLight position={[4, 5, 5]} intensity={12} color="#ffffff" />
      <pointLight position={[-4, -2, 3]} intensity={8} color={project.secondary} />
      <Network activeIndex={activeIndex} completed={completed} reducedMotion={reducedMotion} />
    </Canvas>
  )
}
