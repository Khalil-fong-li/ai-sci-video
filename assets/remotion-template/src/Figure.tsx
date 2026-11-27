import React from 'react';
import {interpolate, spring} from 'remotion';
import {alpha, StyleDef} from './style';
import {ease, TL, U, V} from './timeline';
import type {Visual} from './types';

type Props = {v: Visual; s: StyleDef; local: number; dur: number};

/** 竖屏字号要更大（手机上一臂距离看），横屏克制一点 */
const fs = (n: number) => Math.round(n * U * (V ? 1.26 : 1));

const pop = (local: number, delay: number, damping = 14, stiffness = 130) =>
  spring({frame: Math.max(0, local - delay), fps: TL.fps, config: {damping, stiffness}});

const rise = (local: number, delay: number, dist = 30) => {
  const p = pop(local, delay, 16, 120);
  return {opacity: p, transform: `translateY(${(1 - p) * dist}px)`};
};

const charLen = (s: string) => [...s].reduce((n, ch) => n + (/[\x00-\xff]/.test(ch) ? 0.55 : 1), 0);

// ── 关键词：1–5 个大词，逐条砸下来 ─────────────────────────
const Keywords: React.FC<Props> = ({v, s, local}) => {
  if (v.type !== 'keywords') return null;
  const words = v.words || [];
  const n = words.length || 1;
  const base = n === 1 ? 160 : n === 2 ? 126 : n === 3 ? 100 : n === 4 ? 82 : 68;
  // 按最长词收一下字号，避免顶着边框
  const longest = Math.max(...words.map(charLen), 1);
  const cap = (TL.width - fs(150)) / longest;
  const size = Math.min(fs(base), cap);
  const p = s.palette;
  return (
    <div
      style={{
        width: '100%',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        gap: fs(16),
        padding: `0 ${fs(70)}px`,
        boxSizing: 'border-box',
      }}
    >
      {words.map((w, i) => {
        const pr = pop(local, i * 5, 13, 160);
        const line = ease(local, i * 5 + 4, 14);
        return (
          <div
            key={i}
            style={{position: 'relative', opacity: pr, transform: `scale(${0.92 + 0.08 * pr})`}}
          >
            <div
              style={{
                fontFamily: s.font.display,
                fontWeight: s.look.headWeight,
                fontSize: size,
                lineHeight: 1.2,
                color: i === 0 ? p.ink : s.caption === 'bracket' ? p.accent : p.ink,
                letterSpacing: s.look.tracking,
                textAlign: 'center',
              }}
            >
              {w}
            </div>
            <div
              style={{
                position: 'absolute',
                left: 0,
                bottom: fs(-4),
                width: '100%',
                height: fs(s.caption === 'marker' ? 22 : 9),
                background: i % 2 === 0 ? p.accent : p.pop,
                opacity: s.caption === 'marker' ? 0.55 : 0.95,
                borderRadius: 99,
                transform: `scaleX(${line})`,
                transformOrigin: 'left center',
                zIndex: -1,
              }}
            />
          </div>
        );
      })}
      {v.note ? (
        <div
          style={{
            ...rise(local, words.length * 5 + 8),
            fontFamily: s.font.body,
            fontSize: fs(40),
            color: p.muted,
            letterSpacing: s.look.tracking,
            marginTop: fs(18),
            textAlign: 'center',
          }}
        >
          {v.note}
        </div>
      ) : null}
    </div>
  );
};

// ── 大数字：count-up + 单位 + 说明 ─────────────────────────
const Stat: React.FC<Props> = ({v, s, local}) => {
  if (v.type !== 'stat') return null;
  const p = s.palette;
  const m = /^(.*?)(-?\d+(?:\.\d+)?)(.*)$/.exec(v.value || '');
  const pr = ease(local, 4, 22);
  const dec = m && m[2].includes('.') ? m[2].split('.')[1].length : 0;
  const shown = m ? (parseFloat(m[2]) * pr).toFixed(dec) : null;
  const head = m ? m[1] : '';
  const tail = m ? m[3] : '';
  // 数字位数多时收字号，别顶边
  const digits = (m ? m[1] + m[2] + m[3] : v.value || '').length;
  const numSize = fs(digits > 4 ? 220 : digits > 3 ? 260 : 300);

  return (
    <div
      style={{
        width: '100%',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        padding: `0 ${fs(60)}px`,
        boxSizing: 'border-box',
      }}
    >
      <div
        style={{
          width: fs(96),
          height: fs(7),
          background: p.accent,
          borderRadius: 99,
          marginBottom: fs(40),
          transform: `scaleX(${ease(local, 0, 12)})`,
        }}
      />
      <div style={{display: 'flex', alignItems: 'flex-end', gap: fs(10)}}>
        <div
          style={{
            fontFamily: s.font.display,
            fontWeight: s.look.headWeight,
            fontSize: numSize,
            lineHeight: 0.94,
            color: p.ink,
            letterSpacing: -2,
            fontVariantNumeric: 'tabular-nums',
          }}
        >
          {head}
          {shown ?? v.value}
          {tail}
        </div>
        {v.unit ? (
          <div
            style={{
              fontFamily: s.font.body,
              fontWeight: 700,
              fontSize: fs(84),
              color: p.accent,
              lineHeight: 1.15,
              paddingBottom: fs(24),
            }}
          >
            {v.unit}
          </div>
        ) : null}
      </div>
      {v.label ? (
        <div
          style={{
            ...rise(local, 16),
            fontFamily: s.font.body,
            fontSize: fs(52),
            color: p.ink,
            opacity: 0.82,
            marginTop: fs(32),
            textAlign: 'center',
            maxWidth: fs(760),
            lineHeight: 1.45,
          }}
        >
          {v.label}
        </div>
      ) : null}
    </div>
  );
};

// ── 条形对比 ───────────────────────────────────────────────
const Bars: React.FC<Props> = ({v, s, local}) => {
  if (v.type !== 'bars') return null;
  const p = s.palette;
  const items = v.items || [];
  const max = v.max || Math.max(...items.map((i) => Math.abs(i.value)), 1);
  return (
    <div
      style={{
        width: '100%',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        gap: fs(38),
        padding: `0 ${fs(V ? 58 : 110)}px`,
        boxSizing: 'border-box',
      }}
    >
      {items.map((it, i) => {
        const pr = pop(local, i * 6 + 2, 16, 90);
        const w = (Math.abs(it.value) / max) * 100 * pr;
        const hot = i === items.length - 1;
        return (
          <div key={i} style={{opacity: pr}}>
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'baseline',
                marginBottom: fs(12),
              }}
            >
              <span style={{fontFamily: s.font.body, fontSize: fs(52), color: p.ink, fontWeight: 700}}>
                {it.label}
              </span>
              <span
                style={{
                  fontFamily: s.font.mono,
                  fontSize: fs(54),
                  color: hot ? p.accent : p.ink,
                  fontWeight: 700,
                  fontVariantNumeric: 'tabular-nums',
                }}
              >
                {it.value}
                {v.unit || ''}
              </span>
            </div>
            <div
              style={{
                height: fs(44),
                background: alpha(p.ink, 0.08),
                borderRadius: 99,
                overflow: 'hidden',
              }}
            >
              <div
                style={{
                  width: `${w}%`,
                  height: '100%',
                  borderRadius: 99,
                  background: hot ? p.accent : s.caption === 'bracket' ? p.accent2 : alpha(p.ink, 0.45),
                }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
};

// ── 流程步骤 ───────────────────────────────────────────────
const Steps: React.FC<Props> = ({v, s, local}) => {
  if (v.type !== 'steps') return null;
  const p = s.palette;
  const items = v.items || [];
  return (
    <div
      style={{
        width: '100%',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        padding: `0 ${fs(V ? 66 : 150)}px`,
        boxSizing: 'border-box',
      }}
    >
      {v.title ? (
        <div
          style={{
            ...rise(local, 0),
            fontFamily: s.font.body,
            fontSize: fs(40),
            color: p.muted,
            letterSpacing: fs(3),
            marginBottom: fs(V ? 56 : 40),
          }}
        >
          {v.title}
        </div>
      ) : null}
      {items.map((it, i) => {
        const pr = pop(local, i * 7 + 3, 16, 130);
        const last = i === items.length - 1;
        return (
          <div
            key={i}
            style={{
              display: 'flex',
              gap: fs(28),
              opacity: pr,
              transform: `translateX(${(1 - pr) * -20}px)`,
            }}
          >
            <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
              <div
                style={{
                  width: fs(V ? 92 : 84),
                  height: fs(V ? 92 : 84),
                  flex: '0 0 auto',
                  borderRadius: '50%',
                  border: `${Math.max(2, s.look.borderW * 1.5)}px solid ${i === 0 ? p.accent : p.line}`,
                  background: i === 0 ? p.accent : 'transparent',
                  color: i === 0 ? p.paper : p.ink,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontFamily: s.font.mono,
                  fontSize: fs(38),
                  fontWeight: 800,
                }}
              >
                {i + 1}
              </div>
              {!last ? (
                <div
                  style={{
                    width: Math.max(2, s.look.borderW),
                    flex: 1,
                    minHeight: fs(V ? 46 : 32),
                    background: p.line,
                    marginTop: fs(8),
                  }}
                />
              ) : null}
            </div>
            <div
              style={{
                fontFamily: s.font.body,
                fontSize: fs(V ? 62 : 56),
                lineHeight: 1.42,
                color: p.ink,
                fontWeight: i === 0 ? 700 : s.look.bodyWeight,
                paddingBottom: last ? 0 : fs(V ? 56 : 38),
                paddingTop: fs(10),
              }}
            >
              {it}
            </div>
          </div>
        );
      })}
    </div>
  );
};

// ── 左右对比（竖屏改为上下） ───────────────────────────────
const Compare: React.FC<Props> = ({v, s, local}) => {
  if (v.type !== 'compare') return null;
  const p = s.palette;
  const col = (side: {title: string; points: string[]}, i: number, color: string) => {
    const pr = pop(local, i * 8 + 2, 16, 110);
    return (
      <div
        style={{
          flex: V ? '0 1 auto' : 1,
          opacity: pr,
          transform: `translateY(${(1 - pr) * 26}px)`,
          background: alpha(color, s.caption === 'bracket' ? 0.08 : 0.07),
          border: `${Math.max(1, s.look.borderW)}px solid ${alpha(color, 0.5)}`,
          borderRadius: s.look.radius,
          padding: fs(34),
          display: 'flex',
          flexDirection: 'column',
          gap: fs(16),
          boxSizing: 'border-box',
        }}
      >
        <div
          style={{
            fontFamily: s.font.display,
            fontWeight: s.look.headWeight,
            fontSize: fs(54),
            color,
            lineHeight: 1.2,
          }}
        >
          {side.title}
        </div>
        {side.points.map((pt, j) => (
          <div key={j} style={{display: 'flex', gap: fs(12), alignItems: 'flex-start'}}>
            <div
              style={{
                width: fs(12),
                height: fs(12),
                borderRadius: 99,
                background: color,
                marginTop: fs(18),
                flex: '0 0 auto',
              }}
            />
            <div
              style={{
                fontFamily: s.font.body,
                fontSize: fs(44),
                lineHeight: 1.45,
                color: p.ink,
                opacity: 0.9,
              }}
            >
              {pt}
            </div>
          </div>
        ))}
      </div>
    );
  };
  return (
    <div
      style={{
        width: '100%',
        height: '100%',
        display: 'flex',
        flexDirection: V ? 'column' : 'row',
        alignItems: 'stretch',
        justifyContent: 'center',
        gap: fs(26),
        padding: `0 ${fs(V ? 56 : 110)}px`,
        boxSizing: 'border-box',
      }}
    >
      {col(v.left, 0, p.muted)}
      {col(v.right, 1, p.accent)}
    </div>
  );
};

// ── 金句 ───────────────────────────────────────────────────
const Quote: React.FC<Props> = ({v, s, local}) => {
  if (v.type !== 'quote') return null;
  const p = s.palette;
  const pr = pop(local, 4, 15, 100);
  // 目标两行内排完，超长自动收字号，避免出现孤字一行
  const len = Math.max(charLen(v.text || ''), 1);
  const maxW = TL.width - fs(170);
  const lines = len > 9 ? 2 : 1;
  const size = Math.min(fs(84), (maxW * 0.97) / Math.ceil(len / lines));
  return (
    <div
      style={{
        width: '100%',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        padding: `0 ${fs(84)}px`,
        boxSizing: 'border-box',
        textAlign: 'center',
      }}
    >
      <div
        style={{
          width: fs(86),
          height: fs(7),
          background: p.accent,
          borderRadius: 99,
          marginBottom: fs(50),
          transform: `scaleX(${interpolate(ease(local, 0, 14), [0, 1], [0.2, 1])})`,
        }}
      />
      <div
        style={{
          fontFamily: s.font.display,
          fontWeight: s.look.headWeight,
          fontSize: size,
          lineHeight: 1.46,
          color: p.ink,
          letterSpacing: s.look.tracking,
          opacity: pr,
          transform: `scale(${0.96 + 0.04 * pr})`,
        }}
      >
        {v.text}
      </div>
      {v.by ? (
        <div
          style={{
            ...rise(local, 18),
            fontFamily: s.font.body,
            fontSize: fs(40),
            color: p.muted,
            marginTop: fs(40),
            letterSpacing: fs(2),
          }}
        >
          — {v.by}
        </div>
      ) : null}
    </div>
  );
};

export const Figure: React.FC<Props> = (props) => {
  switch (props.v.type) {
    case 'keywords':
      return <Keywords {...props} />;
    case 'stat':
      return <Stat {...props} />;
    case 'bars':
      return <Bars {...props} />;
    case 'steps':
      return <Steps {...props} />;
    case 'compare':
      return <Compare {...props} />;
    case 'quote':
      return <Quote {...props} />;
    default:
      return null;
  }
};
