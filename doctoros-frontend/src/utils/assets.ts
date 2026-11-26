export const IMG = {
  hero: '/images/hero-anatomy.webp',
  heroSm: '/images/hero-anatomy-sm.webp',
  watercolor: '/images/watercolor.webp',
  sushruta: '/images/sushruta.webp',
  collage: '/images/collage.webp',
  lungs: '/images/print-lungs.webp',
  digestive: '/images/print-digestive.webp',
  heart: '/images/print-heart.webp',
  brain: '/images/print-brain.webp',
} as const;
export const PRINTS = [IMG.heart, IMG.lungs, IMG.brain, IMG.digestive] as const;
