import React from 'react';
import {AbsoluteFill, Img, interpolate, spring, staticFile, useCurrentFrame} from 'remotion';
import {alpha, StyleDef} from './style';
import {clamp, TL, U, V} from './timeline';

export const EndCard: React.FC<{s: StyleDef}> = ({s}) => {
  const f = useCurrentFrame();
  const t = f - TL.end.from;
  const p = s.palette;
  const a = spring({frame: Math.max(0, t), fps: TL.fps, config: {damping: 16, stiffness: 100}});
  const b = interpolate(t, [10, 24], [0, 1], clamp);

  const dark = s.name !== 'paper';
  const bg = dark ? (s.name === 'dark-tech' ? p.bg : p.ink) : p.paper;
  const fg = dark ? p.paper : p.ink;
  const hasQr = Boolean(TL.end.qr);

  const rule = (
    <div
      style={{
        width: (V ? 110 : 130) * b,
        height: 8,
        borderRadius: 99,
        background: dark ? p.pop : p.accent,
      }}
    />
  );

  return (
    <AbsoluteFill style={{background: bg, justifyContent: 'center', alignItems: 'center'}}>
      {s.name === 'dark-tech' ? (
        <div
          style={{
            position: 'absolute',
            width: 760,
            height: 760,
            borderRadius: '50%',
            background: `radial-gradient(circle, ${alpha(p.accent, 0.16)} 0%, transparent 66%)`,
          }}
        />
      ) : null}

      <div
        style={{
          display: 'flex',
          flexDirection: hasQr && !V ? 'row' : 'column',
          alignItems: 'center',
          gap: hasQr ? U * 70 : 0,
          padding: '0 8%',
          position: 'relative',
        }}
      >
        <div style={{textAlign: 'center'}}>
          <div
            style={{
              fontFamily: s.font.display,
              fontWeight: s.look.headWeight,
              fontSize: Math.round((V ? 78 : 64) * U),
              color: fg,
              letterSpacing: s.look.tracking + 1,
              lineHeight: 1.4,
              opacity: a,
              transform: `translateY(${(1 - a) * 26}px)`,
              maxWidth: V ? 900 : 900,
              whiteSpace: 'pre-line',
            }}
          >
            {TL.end.line1}
          </div>
          <div style={{display: 'flex', justifyContent: 'center', margin: `${U * 34}px 0`}}>{rule}</div>
          <div
            style={{
              fontFamily: s.font.body,
              fontWeight: 600,
              fontSize: Math.round((V ? 38 : 30) * U),
              color: alpha(fg, 0.72),
              letterSpacing: 4,
              opacity: b,
            }}
          >
            {TL.end.line2}
          </div>
        </div>

        {hasQr ? (
          <div
            style={{
              width: U * (V ? 260 : 240),
              height: U * (V ? 260 : 240),
              padding: U * 12,
              background: p.paper,
              borderRadius: s.look.radius,
              opacity: b,
            }}
          >
            <Img src={staticFile(TL.end.qr as string)} style={{width: '100%', height: '100%', objectFit: 'contain'}} />
          </div>
        ) : null}
      </div>
    </AbsoluteFill>
  );
};
