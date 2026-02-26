/* ── Avatar barrel exports ─────────────────────────────── */

// Main component
export { default as RichyAvatar } from './RichyAvatar';

// Sub-components (for advanced usage / storybook)
export { default as SVGFace } from './SVGFace';
export { default as AvatarParticles } from './AvatarParticles';
export { default as AmbientGlow } from './AmbientGlow';
export { default as SpeechBubble } from './SpeechBubble';

// Hooks
export { useKeystrokeWatcher } from './useKeystrokeWatcher';
export { useEyeTracking } from './useEyeTracking';
export { useBlinking } from './useBlinking';

// Engine & data
export { resolveExpression, getExpressionConfig } from './AvatarExpressionEngine';
export { EXPRESSIONS, KEYSTROKE_TRIGGERS, REACTION_BUBBLES } from './expressions';
export { EXPRESSION_FACES, EXPRESSION_PALETTES, EYE_SHAPES, MOUTH_SHAPES, BROW_SHAPES } from './faceShapes';
