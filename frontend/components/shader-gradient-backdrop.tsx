'use client'

import { ShaderGradient, ShaderGradientCanvas } from '@shadergradient/react'
import { project } from '@/lib/engine'

export function ShaderGradientBackdrop({ reducedMotion = false }: { reducedMotion?: boolean }) {
  return (
    <div className="shader-gradient" aria-hidden="true">
      <ShaderGradientCanvas style={{ position: 'absolute', inset: 0 }} pixelDensity={1} fov={45} lazyLoad>
        <ShaderGradient
          control="props"
          type="plane"
          animate={reducedMotion ? 'off' : 'on'}
          color1={project.accent}
          color2="#0a0d12"
          color3={project.secondary}
          uSpeed={reducedMotion ? 0 : 0.11}
          uStrength={1.35}
          uDensity={1.15}
          uFrequency={4.2}
          brightness={0.66}
          grain="on"
          grainBlending={0.14}
          cDistance={4.8}
          cPolarAngle={110}
          cAzimuthAngle={170}
          lightType="3d"
          reflection={0.15}
        />
      </ShaderGradientCanvas>
    </div>
  )
}
