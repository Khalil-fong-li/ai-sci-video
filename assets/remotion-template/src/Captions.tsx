import React from 'react';
import {spring, useCurrentFrame} from 'remotion';
import {alpha, StyleDef} from './style';
import {TL, U, V} from './timeline';
import type {Chunk} from './types';

/** 数字挑出来染色，科普片里数字最好认 */
const Highlight: React.FC<{text: string; s: StyleDef}> = ({text, s}) => {
  const parts = text.split(/(\d+(?:\.\d+)?%?)/g);
  const hot = s.caption === 'sticker' ? s.palette.accent : s.palette.accent;
  return (
    <>
      {parts.map((p, i) =>
        /^\d/.test(p) ? (
          <span key={i} style={{color: hot}}>
            {p}
          </span>
        ) : (
          <span key={i}>{p}</span>
        ),
      )}
    </>
  );
};

export const Captions: React.FC<{s: StyleDef}> = ({s}) => {
  const f = useCurrentFrame();
  let active: Chunk | null = null;
  for (const sc of TL.scenes) {
    for (const c of sc.chunks) {
      if (f >= c.from && f < c.from + c.dur) active = c;
    }
  }
  if (!active) return null;

  const local = f - active.from;
  const enter = spring({frame: local, fps: TL.fps, config: {damping: 18, stiffness: 240}});
  const p = s.palette;
  const size = Math.round((V ? 60 : 44) * U * (V ? 1.04 : 1));

  const common: React.CSSProperties = {
    fontFamily: s.caption === 'bracket' ? s.font.mono : s.font.body,
    fontSize: size,
    lineHeight: 1.34,
    letterSpacing: s.look.tracking,
    textAlign: 'center',
    maxWidth: V ? TL.width - 110 : TL.width * 0.82,
    color: p.ink,
  };

  let box: React.CSSProperties = {};
  if (s.caption === 'sticker') {
    box = {
      padding: V ? '16px 26px' : '12px 22px',
      borderRadius: 20,
      background: alpha(p.paper, 0.95),
      border: `4px solid ${p.ink}`,
      boxShadow: `7px 7px 0 ${alpha(p.ink, 0.85)}`,
      fontWeight: 900,
    };
  } else if (s.caption === 'herald') {
    box = {
      padding: V ? '14px 26px 14px 30px' : '10px 22px 10px 26px',
      background: alpha(p.paper, 0.94),
      borderLeft: `6px solid ${p.accent}`,
      borderTop: `1px solid ${alpha(p.line, 0.9)}`,
      borderBottom: `1px solid ${alpha(p.line, 0.9)}`,
      fontWeight: 500,
      boxShadow: '0 10px 30px rgba(22,24,29,0.12)',
    };
  } else if (s.caption === 'bracket') {
    box = {
      padding: V ? '12px 24px' : '8px 20px',
      background: alpha(p.bg, 0.78),
      borderLeft: `4px solid ${p.accent}`,
      fontWeight: 500,
      backdropFilter: 'blur(2px)',
    };
  } else {
    box = {
      padding: V ? '10px 22px' : '8px 18px',
      background: `linear-gradient(180deg, transparent 12%, ${alpha(p.pop, 0.62)} 12%, ${alpha(p.pop, 0.62)} 92%, transparent 92%)`,
      fontWeight: 700,
    };
  }

  return (
    <div
      style={{
        position: 'absolute',
        left: 0,
        right: 0,
        bottom: V ? 168 : 54,
        display: 'flex',
        justifyContent: 'center',
        padding: '0 24px',
        opacity: enter,
        transform: `translateY(${(1 - enter) * 22}px)`,
      }}
    >
      <div style={{...common, ...box}}>
        <Highlight text={active.text} s={s} />
      </div>
    </div>
  );
};
