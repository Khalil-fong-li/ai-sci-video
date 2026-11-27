import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {alpha, StyleDef} from './style';
import {clamp, TL, U} from './timeline';

/** 进度条：风格不同，位置与粗细不同 */
export const Progress: React.FC<{s: StyleDef}> = ({s}) => {
  const f = useCurrentFrame();
  const p = interpolate(f, [0, TL.total], [0, 1], clamp);
  const p2 = s.palette;

  if (s.name === 'paper') {
    return (
      <div
        style={{
          position: 'absolute',
          left: U * 44,
          right: U * 44,
          top: U * 40,
          height: 3,
          backgroundImage: `repeating-linear-gradient(90deg, ${alpha(p2.ink, 0.35)} 0 14px, transparent 14px 22px)`,
        }}
      >
        <div
          style={{
            width: `${p * 100}%`,
            height: 4,
            marginTop: -1,
            background: p2.accent,
            opacity: 0.85,
          }}
        />
      </div>
    );
  }

  const h = s.name === 'sticker' ? 10 : s.name === 'dark-tech' ? 3 : 4;
  return (
    <div
      style={{
        position: 'absolute',
        left: 0,
        top: 0,
        width: TL.width,
        height: h,
        background: alpha(p2.ink, s.name === 'dark-tech' ? 0.3 : 0.12),
      }}
    >
      <div
        style={{
          width: `${p * 100}%`,
          height: '100%',
          background: p2.accent,
          boxShadow: s.name === 'dark-tech' ? `0 0 14px ${p2.accent}` : undefined,
        }}
      />
    </div>
  );
};
