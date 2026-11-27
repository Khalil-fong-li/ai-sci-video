import React from 'react';
import {AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame} from 'remotion';
import {Figure} from './Figure';
import {alpha, StyleDef} from './style';
import {clamp, TL, V} from './timeline';
import type {Scene} from './types';

const {width: W, height: H} = TL;

/** 运镜：返回缩放与百分比位移 */
const motionOf = (m: string, p: number) => {
  switch (m) {
    case 'push-in':
      return {scale: 1 + 0.09 * p, x: 0, y: -1.5 * p};
    case 'pull-out':
      return {scale: 1.09 - 0.09 * p, x: 0, y: 0.8 * p};
    case 'pan-right':
      return {scale: 1.07, x: -2.2 + 4.4 * p, y: 0};
    case 'pan-left':
      return {scale: 1.07, x: 2.2 - 4.4 * p, y: 0};
    case 'tilt-up':
      return {scale: 1.07, x: 0, y: 2 - 4 * p};
    case 'tilt-down':
      return {scale: 1.07, x: 0, y: -2 + 4 * p};
    default:
      return {scale: 1.02, x: 0, y: 0};
  }
};

/** 背景纹理：纸纹 / 网格 / 圆点，纯 CSS 平铺，无外部资源 */
const Texture: React.FC<{s: StyleDef}> = ({s}) => {
  const p = s.palette;
  if (s.look.texture === 'none') return null;
  const common: React.CSSProperties = {position: 'absolute', inset: 0, pointerEvents: 'none'};
  if (s.look.texture === 'grid') {
    return (
      <div
        style={{
          ...common,
          backgroundImage: `linear-gradient(${alpha(p.line, 0.55)} 1px, transparent 1px),
            linear-gradient(90deg, ${alpha(p.line, 0.55)} 1px, transparent 1px)`,
          backgroundSize: '44px 44px',
          opacity: 0.55,
        }}
      />
    );
  }
  if (s.look.texture === 'dots') {
    return (
      <div
        style={{
          ...common,
          backgroundImage: `radial-gradient(${alpha(p.ink, 0.16)} 1.2px, transparent 1.2px)`,
          backgroundSize: '18px 18px',
          opacity: 0.6,
        }}
      />
    );
  }
  // paper：细横线 + 极淡噪点
  return (
    <div
      style={{
        ...common,
        backgroundImage: `repeating-linear-gradient(0deg, ${alpha(p.line, 0.14)} 0 1px, transparent 1px 5px),
          radial-gradient(${alpha(p.ink, 0.06)} 1px, transparent 1px)`,
        backgroundSize: 'auto, 7px 7px',
        opacity: 0.75,
      }}
    />
  );
};

/** 装饰：不同风格的边角元素，让静止画面也有"设计感" */
const Garnish: React.FC<{s: StyleDef; index: number}> = ({s, index}) => {
  const p = s.palette;
  if (s.name === 'editorial') {
    return (
      <>
        <div style={{position: 'absolute', left: 54, top: 54, width: 60, height: 6, background: p.accent}} />
        <div
          style={{
            position: 'absolute',
            right: 54,
            bottom: 40,
            fontFamily: s.font.mono,
            fontSize: 26,
            letterSpacing: 3,
            color: alpha(p.ink, 0.32),
          }}
        >
          {String(index).padStart(2, '0')} / {String(TL.scenes.length).padStart(2, '0')}
        </div>
      </>
    );
  }
  if (s.name === 'dark-tech') {
    return (
      <>
        {[
          {x: 0.08, y: 0.12, c: p.accent},
          {x: 0.9, y: 0.28, c: p.accent2},
        ].map((g, i) => (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: `${g.x * 100}%`,
              top: `${g.y * 100}%`,
              width: 460,
              height: 460,
              marginLeft: -230,
              marginTop: -230,
              borderRadius: '50%',
              background: `radial-gradient(circle, ${alpha(g.c, 0.2)} 0%, transparent 68%)`,
            }}
          />
        ))}
      </>
    );
  }
  return null;
};

export const SceneCard: React.FC<{scene: Scene; s: StyleDef}> = ({scene, s}) => {
  const f = useCurrentFrame();
  const local = f - scene.from;
  const p = s.palette;
  const progress = interpolate(local, [0, scene.dur], [0, 1], clamp);

  // 入场转场
  const tIn = Math.min(1, local / 9);
  let enterStyle: React.CSSProperties = {};
  if (s.transition === 'wipe') {
    enterStyle = {clipPath: `inset(0 ${(1 - tIn) * 100}% 0 0)`};
  } else if (s.transition === 'push') {
    enterStyle = {transform: `translateX(${(1 - tIn) * 6}%)`, opacity: 0.2 + 0.8 * tIn};
  } else {
    enterStyle = {opacity: tIn};
  }

  const v = scene.visual;
  const isImage = v.type === 'image';
  const imgTop = V ? 110 : 0;
  const imgH = V ? H * 0.735 : H;

  return (
    <AbsoluteFill style={{background: p.bg, overflow: 'hidden', ...enterStyle}}>
      <Texture s={s} />
      <Garnish s={s} index={scene.index} />

      {isImage && v.type === 'image' ? (
        <>
          <div
            style={{
              position: 'absolute',
              left: V ? (s.name === 'editorial' ? 46 : 0) : 0,
              top: imgTop,
              width: V ? (s.name === 'editorial' ? W - 92 : W) : W,
              height: imgH,
              borderRadius: V ? s.look.radius : 0,
              overflow: 'hidden',
              border: s.look.borderW ? `${s.look.borderW}px solid ${p.line}` : undefined,
              boxShadow: s.look.shadow,
              background: p.paper,
              transform: s.name === 'paper' ? 'rotate(-0.6deg)' : undefined,
            }}
          >
            <Img
              src={staticFile(v.src)}
              style={{
                width: '100%',
                height: '100%',
                objectFit: v.fit || 'cover',
                transform: `scale(${motionOf(v.motion, progress).scale})
                  translate(${motionOf(v.motion, progress).x}%, ${motionOf(v.motion, progress).y}%)`,
              }}
            />
            {s.name === 'dark-tech' ? (
              <div
                style={{
                  position: 'absolute',
                  inset: 0,
                  background: `linear-gradient(180deg, transparent 55%, ${alpha(p.bg, 0.85)} 100%)`,
                }}
              />
            ) : null}
          </div>
          {V && v.label ? (
            <div
              style={{
                position: 'absolute',
                left: s.name === 'editorial' ? 52 : 40,
                top: imgTop + imgH + 18,
                fontFamily: s.font.mono,
                fontSize: 26,
                letterSpacing: 1,
                color: alpha(p.ink, 0.45),
              }}
            >
              {v.label}
            </div>
          ) : null}
        </>
      ) : null}

      {!isImage ? (
        <div
          style={{
            position: 'absolute',
            left: 0,
            top: V ? 70 : 0,
            width: W,
            height: V ? H * 0.8 : H,
            paddingBottom: V ? 0 : 210,
            boxSizing: 'border-box',
            display: 'flex',
          }}
        >
          <Figure v={v} s={s} local={local} dur={scene.dur} />
        </div>
      ) : null}
    </AbsoluteFill>
  );
};
