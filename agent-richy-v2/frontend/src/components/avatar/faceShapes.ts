/* ── SVG path definitions for each facial feature & expression ──────── */

/**
 * All face parts are defined in a 100×100 viewBox coordinate system.
 * Eyes are positioned at roughly (30, 42) and (70, 42).
 * Mouth center is at (50, 68).
 * Brows are at y ≈ 30.
 *
 * Each path is designed to morph smoothly between expressions when
 * animated with framer-motion's `d` interpolation.
 */

// ── EYE PATHS ───────────────────────────────────────────────────────────

export interface EyeShape {
  /** Main eye outline path (filled) */
  outline: string;
  /** Pupil path (filled darker) — null for closed eyes */
  pupil: string | null;
  /** Pupil radius for gaze tracking offset */
  pupilRadius: number;
  /** Highlight/sparkle path or null */
  highlight: string | null;
}

export const EYE_SHAPES: Record<string, EyeShape> = {
  // Normal relaxed eye — almond shape
  normal: {
    outline: 'M3,10 C3,4 7,0 12,0 C17,0 21,4 21,10 C21,16 17,20 12,20 C7,20 3,16 3,10 Z',
    pupil: 'M8,10 A4,4 0 1,1 16,10 A4,4 0 1,1 8,10 Z',
    pupilRadius: 4,
    highlight: 'M13,7 A1.5,1.5 0 1,1 16,7 A1.5,1.5 0 1,1 13,7 Z',
  },
  // Wide open — surprise/excited
  wide: {
    outline: 'M2,10 C2,2 6,-1 12,-1 C18,-1 22,2 22,10 C22,18 18,21 12,21 C6,21 2,18 2,10 Z',
    pupil: 'M7,10 A5,5 0 1,1 17,10 A5,5 0 1,1 7,10 Z',
    pupilRadius: 5,
    highlight: 'M13,6 A2,2 0 1,1 17,6 A2,2 0 1,1 13,6 Z',
  },
  // Squinting — confused/skeptical
  squint: {
    outline: 'M3,10 C3,7 7,5 12,5 C17,5 21,7 21,10 C21,13 17,15 12,15 C7,15 3,13 3,10 Z',
    pupil: 'M9,10 A3,2 0 1,1 15,10 A3,2 0 1,1 9,10 Z',
    pupilRadius: 3,
    highlight: null,
  },
  // Happy squint — laughing
  happy: {
    outline: 'M3,12 C3,8 7,5 12,5 C17,5 21,8 21,12 C21,14 17,14 12,14 C7,14 3,14 3,12 Z',
    pupil: null,
    pupilRadius: 0,
    highlight: null,
  },
  // Soft/gentle — empathetic
  soft: {
    outline: 'M3,11 C3,5 7,2 12,2 C17,2 21,5 21,11 C21,15 17,17 12,17 C7,17 3,15 3,11 Z',
    pupil: 'M8,10 A4,4.5 0 1,1 16,10 A4,4.5 0 1,1 8,10 Z',
    pupilRadius: 4,
    highlight: 'M13,7 A1.2,1.2 0 1,1 15.4,7 A1.2,1.2 0 1,1 13,7 Z',
  },
  // Closed (blink)
  closed: {
    outline: 'M3,10 Q12,14 21,10',
    pupil: null,
    pupilRadius: 0,
    highlight: null,
  },
  // Looking up — thinking
  lookUp: {
    outline: 'M3,11 C3,5 7,1 12,1 C17,1 21,5 21,11 C21,16 17,19 12,19 C7,19 3,16 3,11 Z',
    pupil: 'M8,7 A4,4 0 1,1 16,7 A4,4 0 1,1 8,7 Z',
    pupilRadius: 4,
    highlight: 'M13,4 A1.5,1.5 0 1,1 16,4 A1.5,1.5 0 1,1 13,4 Z',
  },
  // Focused — serious
  focused: {
    outline: 'M4,10 C4,6 7,3 12,3 C17,3 20,6 20,10 C20,14 17,17 12,17 C7,17 4,14 4,10 Z',
    pupil: 'M9,10 A3,3 0 1,1 15,10 A3,3 0 1,1 9,10 Z',
    pupilRadius: 3,
    highlight: null,
  },
  // Star eyes — celebrating
  star: {
    outline: 'M2,10 C2,2 6,-1 12,-1 C18,-1 22,2 22,10 C22,18 18,21 12,21 C6,21 2,18 2,10 Z',
    pupil: null,
    pupilRadius: 0,
    highlight: null,
    // The star will be rendered specially by the component
  },
};

// ── MOUTH PATHS ─────────────────────────────────────────────────────────

export interface MouthShape {
  /** SVG path in a 40×20 local viewBox */
  path: string;
  /** Whether the mouth is "open" (filled vs stroked) */
  open: boolean;
  /** Fill color override (null = use default) */
  fill?: string;
}

export const MOUTH_SHAPES: Record<string, MouthShape> = {
  smile: {
    path: 'M4,8 Q20,22 36,8',
    open: false,
  },
  'slight-smile': {
    path: 'M6,9 Q20,17 34,9',
    open: false,
  },
  'big-smile': {
    path: 'M3,6 Q20,26 37,6 Q20,18 3,6 Z',
    open: true,
    fill: '#dc2626',
  },
  'open-laugh': {
    path: 'M4,4 Q20,28 36,4 Q20,20 4,4 Z',
    open: true,
    fill: '#dc2626',
  },
  flat: {
    path: 'M8,10 L32,10',
    open: false,
  },
  pursed: {
    path: 'M14,10 Q20,7 26,10 Q20,13 14,10 Z',
    open: true,
    fill: '#f87171',
  },
  'slight-frown': {
    path: 'M6,12 Q20,5 34,12',
    open: false,
  },
  wavy: {
    path: 'M6,10 Q12,6 18,10 Q24,14 30,10 Q34,7 36,10',
    open: false,
  },
  'o-shape': {
    path: 'M14,6 Q14,2 20,2 Q26,2 26,6 Q26,14 20,14 Q14,14 14,6 Z',
    open: true,
    fill: '#dc2626',
  },
};

// ── BROW PATHS ──────────────────────────────────────────────────────────

export interface BrowShape {
  /** Left brow path in a 20×8 local viewBox */
  left: string;
  /** Right brow path */
  right: string;
}

export const BROW_SHAPES: Record<string, BrowShape> = {
  normal: {
    left: 'M2,6 Q10,3 18,5',
    right: 'M2,5 Q10,3 18,6',
  },
  raised: {
    left: 'M2,7 Q10,0 18,4',
    right: 'M2,4 Q10,0 18,7',
  },
  'raised-one': {
    left: 'M2,7 Q10,1 18,4',
    right: 'M2,5 Q10,3 18,6',
  },
  furrowed: {
    left: 'M2,3 Q10,6 18,5',
    right: 'M2,5 Q10,6 18,3',
  },
  concerned: {
    left: 'M2,4 Q10,7 18,6',
    right: 'M2,6 Q10,7 18,4',
  },
};

// ── EXPRESSION → FACE MAPPING ───────────────────────────────────────────

export interface FaceConfig {
  eyes: string;       // key into EYE_SHAPES
  mouth: string;      // key into MOUTH_SHAPES
  brows: string;      // key into BROW_SHAPES
  blushIntensity: number;  // 0-1
  teardrops: boolean;
  stars: boolean;      // star-eye mode
  sweatdrop: boolean;
}

export const EXPRESSION_FACES: Record<string, FaceConfig> = {
  idle: {
    eyes: 'normal', mouth: 'smile', brows: 'normal',
    blushIntensity: 0.15, teardrops: false, stars: false, sweatdrop: false,
  },
  watching: {
    eyes: 'normal', mouth: 'slight-smile', brows: 'raised-one',
    blushIntensity: 0, teardrops: false, stars: false, sweatdrop: false,
  },
  confused: {
    eyes: 'squint', mouth: 'wavy', brows: 'furrowed',
    blushIntensity: 0, teardrops: false, stars: false, sweatdrop: true,
  },
  excited: {
    eyes: 'wide', mouth: 'big-smile', brows: 'raised',
    blushIntensity: 0.3, teardrops: false, stars: false, sweatdrop: false,
  },
  thinking: {
    eyes: 'lookUp', mouth: 'pursed', brows: 'raised-one',
    blushIntensity: 0, teardrops: false, stars: false, sweatdrop: false,
  },
  presenting: {
    eyes: 'normal', mouth: 'smile', brows: 'normal',
    blushIntensity: 0.1, teardrops: false, stars: false, sweatdrop: false,
  },
  laughing: {
    eyes: 'happy', mouth: 'open-laugh', brows: 'raised',
    blushIntensity: 0.35, teardrops: true, stars: false, sweatdrop: false,
  },
  empathetic: {
    eyes: 'soft', mouth: 'slight-frown', brows: 'concerned',
    blushIntensity: 0.1, teardrops: false, stars: false, sweatdrop: false,
  },
  serious: {
    eyes: 'focused', mouth: 'flat', brows: 'furrowed',
    blushIntensity: 0, teardrops: false, stars: false, sweatdrop: false,
  },
  celebrating: {
    eyes: 'star', mouth: 'big-smile', brows: 'raised',
    blushIntensity: 0.3, teardrops: false, stars: true, sweatdrop: false,
  },
  teaching: {
    eyes: 'soft', mouth: 'smile', brows: 'raised-one',
    blushIntensity: 0.1, teardrops: false, stars: false, sweatdrop: false,
  },
  friendly: {
    eyes: 'normal', mouth: 'big-smile', brows: 'normal',
    blushIntensity: 0.2, teardrops: false, stars: false, sweatdrop: false,
  },
};

// ── COLOR PALETTES PER EXPRESSION ───────────────────────────────────────

export interface ExpressionPalette {
  /** Primary glow color */
  glow: string;
  /** Secondary ring color */
  ring: string;
  /** Particle/accent color */
  accent: string;
  /** Background gradient stops [from, to] */
  bgGradient: [string, string];
}

export const EXPRESSION_PALETTES: Record<string, ExpressionPalette> = {
  idle:        { glow: '#f59e0b', ring: '#fbbf24', accent: '#f59e0b', bgGradient: ['#fef3c7', '#fde68a'] },
  watching:    { glow: '#3b82f6', ring: '#60a5fa', accent: '#3b82f6', bgGradient: ['#dbeafe', '#bfdbfe'] },
  confused:    { glow: '#f59e0b', ring: '#fbbf24', accent: '#f97316', bgGradient: ['#fef3c7', '#fed7aa'] },
  excited:     { glow: '#10b981', ring: '#34d399', accent: '#10b981', bgGradient: ['#d1fae5', '#a7f3d0'] },
  thinking:    { glow: '#8b5cf6', ring: '#a78bfa', accent: '#8b5cf6', bgGradient: ['#ede9fe', '#ddd6fe'] },
  presenting:  { glow: '#2563eb', ring: '#3b82f6', accent: '#2563eb', bgGradient: ['#dbeafe', '#bfdbfe'] },
  laughing:    { glow: '#f59e0b', ring: '#fbbf24', accent: '#f59e0b', bgGradient: ['#fef3c7', '#fde68a'] },
  empathetic:  { glow: '#8b5cf6', ring: '#a78bfa', accent: '#c084fc', bgGradient: ['#ede9fe', '#e9d5ff'] },
  serious:     { glow: '#ef4444', ring: '#f87171', accent: '#ef4444', bgGradient: ['#fee2e2', '#fecaca'] },
  celebrating: { glow: '#f59e0b', ring: '#fbbf24', accent: '#eab308', bgGradient: ['#fef9c3', '#fde68a'] },
  teaching:    { glow: '#06b6d4', ring: '#22d3ee', accent: '#06b6d4', bgGradient: ['#cffafe', '#a5f3fc'] },
  friendly:    { glow: '#f59e0b', ring: '#fbbf24', accent: '#f59e0b', bgGradient: ['#fef3c7', '#fde68a'] },
};
