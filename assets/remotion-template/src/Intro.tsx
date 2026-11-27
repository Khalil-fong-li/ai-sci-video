import React from 'react';
import {AbsoluteFill, interpolate, spring, useCurrentFrame} from 'remotion';
import {alpha, StyleDef} from './style';
import {clamp, TL, U, V} from './timeline';

export const Intro: React.FC<{s: StyleDef}> = ({s}) => {
  const f = useCurrentFrame();
  const local = f - TL.intro.from;
  const p = s.palette;
  const title = spring({frame: Math.max(0, local - 5), fps: TL.fps, config: {damping: 15, stiffness: 110}});
  const kick = interpolate(local, [0, 12], [0, 1], clamp);
  const rule = interpolate(local, [16, 34], [0, 1], clamp);

  const titleSize = Math.round((V ? 96 : 84) * U * (V ? 1 : 0.95));
  const kickerSize = Math.round((V ? 32 : 26) * U);

  const decor = () => {
    if (s.name === 'flat-kids') {
      return (
        <>
          <div
            style={{
              position: 'absolute',
              width: V ? 780 : 860,
              height: V ? 780 : 620,
              borderRadius: '50%',
              background: p.pop,
              opacity: 0.5,
              transform: `translateY(${V ? -150 : -30}px)`,
            }}
          />
          <div
            style={{
              position: 'absolute',
              width: V ? 520 : 600,
              height: V ? 520 : 420,
              borderRadius: '50%',
              background: p.accent2,
              opacity: 0.2,
              transform: `translate(${V ? 190 : 330}px, ${V ? 310 : 170}px)`,
            }}
          />
        </>
      );
    }
    if (s.name === 'dark-tech') {
      return (
        <>
          <div
            style={{
              position: 'absolute',
              inset: 0,
              backgroundImage: `linear-gradient(${alpha(p.line, 0.9)} 1px, transparent 1px),
                linear-gradient(90deg, ${alpha(p.line, 0.9)} 1px, transparent 1px)`,
              backgroundSize: '56px 56px',
              opacity: 0.5,
            }}
          />
          <div
            style={{
              position: 'absolute',
              width: 900,
              height: 900,
              left: '50%',
              top: '50%',
              marginLeft: -450,
              marginTop: -450,
              borderRadius: '50%',
              background: `radial-gradient(circle, ${alpha(p.accent, 0.22)} 0%, transparent 62%)`,
            }}
          />
        </>
      );
    }
    if (s.name === 'editorial') {
      return (
        <>
          <div style={{position: 'absolute', left: 60, top: 60, width: 120, height: 8, background: p.accent}} />
          <div
            style={{
              position: 'absolute',
              right: 60,
              top: 60,
              fontFamily: s.font.mono,
              fontSize: 26 * U,
              letterSpacing: 4,
              color: alpha(p.ink, 0.4),
            }}
          >
            SCI · EXPLAINER
          </div>
          <div
            style={{
              position: 'absolute',
              left: 60,
              right: 60,
              bottom: 60,
              height: 1,
              background: alpha(p.line, 1),
            }}
          />
        </>
      );
    }
    // paper：胶带 + 页码
    return (
      <>
        <div
          style={{
            position: 'absolute',
            left: '12%',
            top: V ? 210 : 120,
            width: 200,
            height: 54,
            background: alpha(p.pop, 0.5),
            transform: 'rotate(-8deg)',
          }}
        />
        <div
          style={{
            position: 'absolute',
            right: '12%',
            bottom: V ? 190 : 110,
            width: 150,
            height: 44,
            background: alpha(p.accent2, 0.28),
            transform: 'rotate(6deg)',
          }}
        />
      </>
    );
  };

  return (
    <AbsoluteFill style={{background: p.bg, justifyContent: 'center', alignItems: 'center'}}>
      {decor()}
      <div style={{position: 'relative', textAlign: 'center', padding: '0 8%', zIndex: 2}}>
        <div
          style={{
            display: 'inline-block',
            padding: s.caption === 'bracket' ? '6px 16px' : '9px 24px',
            borderRadius: s.caption === 'sticker' ? 999 : 2,
            border: s.caption === 'sticker' ? `4px solid ${p.ink}` : s.caption === 'bracket' ? `1px solid ${alpha(p.accent, 0.6)}` : 'none',
            background: s.caption === 'sticker' ? p.paper : s.caption === 'bracket' ? alpha(p.accent, 0.1) : 'transparent',
            color: s.caption === 'bracket' ? p.accent : p.muted,
            fontFamily: s.caption === 'bracket' ? s.font.mono : s.font.body,
            fontWeight: 700,
            fontSize: kickerSize,
            letterSpacing: s.caption === 'bracket' ? 2 : 5,
            opacity: kick,
            marginBottom: V ? 46 : 34,
          }}
        >
          {s.caption === 'bracket' ? `// ${TL.intro.kicker}` : TL.intro.kicker}
        </div>
        <div
          style={{
            fontFamily: s.font.display,
            fontWeight: s.look.headWeight,
            fontSize: titleSize,
            lineHeight: 1.26,
            color: p.ink,
            letterSpacing: s.look.tracking + 1,
            transform: `scale(${0.9 + 0.1 * title})`,
            opacity: title,
            maxWidth: V ? 920 : 1300,
            whiteSpace: 'pre-line',
          }}
        >
          {TL.intro.line}
        </div>
        <div
          style={{
            height: s.name === 'paper' ? 5 : 10,
            width: (V ? 130 : 160) * rule,
            margin: '36px auto 0',
            borderRadius: 99,
            background: p.accent,
            opacity: 0.9,
          }}
        />
      </div>
    </AbsoluteFill>
  );
};
