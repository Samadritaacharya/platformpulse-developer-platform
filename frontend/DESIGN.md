# PlatformPulse web design system

The interactive web layer uses one original portfolio design language: dark editorial surfaces, restrained glass, large product typography, evidence-dense cards, and motion that explains system state instead of decorating it.

## References translated into implementation

- **Taste Skill v2:** audit-first redesign, deliberate hierarchy, avoid generic SaaS sections, infer a product-specific visual direction before implementation.
- **awesome-design-md:** treat design decisions as explicit system constraints. The interface borrows the precision and near-black restraint seen across developer-tool design analyses without copying any one brand.
- **React Three Fiber:** declarative Three.js system map for the product workflow.
- **ShaderGradient v2:** low-density animated ambient field behind the hero; pixel density is capped for performance.
- **liquid-glass-js:** visual reference only. CSS backdrop-filter glass is used instead of the library runtime because the upstream project still lists React wrappers, accessibility, and performance/mobile optimization as roadmap work.
- **liquid-logo:** shader concept reference only. The central R3F orb uses original GLSL displacement, moving bands, and Fresnel metallic edges rather than copied source.

## Rules

1. Motion must communicate state and honor `prefers-reduced-motion`.
2. WebGL must have a readable fallback.
3. No remote font is required.
4. No model key, database, analytics service, or paid API is required.
5. Synthetic data and deterministic behavior remain explicit.
6. Dense evidence beats decorative dashboard chrome.

## Palette

- Canvas `#07090d`
- Accent `#7c5cff`
- Secondary `#22d3ee`
- Success `#53e3b0`
- Warning `#f5c86a`
- Risk `#ff7188`

## Deployment

Deploy `frontend/` as the Vercel Root Directory. The project is compatible with local `npm run dev` and requires no environment variables.
