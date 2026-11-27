/**
 * 风格预设：同一套时间轴，换 style 就换视觉体系。
 * storyboard.json 里写 "style": "editorial"，也可以在 timeline.json 的 themeOverride 里微调色板。
 */
import timelineJson from './data/timeline.json';

export type Palette = {
  bg: string;
  paper: string;
  ink: string;
  muted: string;
  accent: string;
  accent2: string;
  pop: string;
  line: string;
};

export type CaptionKind = 'sticker' | 'herald' | 'bracket' | 'marker';

export type StyleDef = {
  name: string;
  label: string;
  palette: Palette;
  font: {display: string; body: string; mono: string};
  look: {
    radius: number;
    borderW: number;
    shadow: string;
    texture: 'none' | 'paper' | 'grid' | 'dots';
    tracking: number;
    headWeight: number;
    bodyWeight: number;
  };
  caption: CaptionKind;
  /** 每场的入场转场 */
  transition: 'fade' | 'wipe' | 'push';
};

const SANS =
  '"Noto Sans SC","Source Han Sans SC","Microsoft YaHei","PingFang SC",system-ui,sans-serif';
const SERIF =
  '"Noto Serif SC","Source Han Serif SC","Songti SC","SimSun","Times New Roman",serif';
const MONO = '"JetBrains Mono","Cascadia Mono","SF Mono",Consolas,"Courier New",monospace';
const KAI = '"Kaiti SC","KaiTi","STKaiti","Noto Serif SC",serif';

export const PRESETS: Record<string, StyleDef> = {
  /** 扁平贴纸：儿童科普、生活常识，最活泼 */
  'flat-kids': {
    name: 'flat-kids',
    label: '扁平贴纸',
    palette: {
      bg: '#FFF3E0', paper: '#FFFCF4', ink: '#241C15', muted: '#8A7461',
      accent: '#F0562D', accent2: '#1E8E7E', pop: '#FFC94D', line: '#241C15',
    },
    font: {display: SANS, body: SANS, mono: MONO},
    look: {radius: 28, borderW: 4, shadow: '10px 10px 0 rgba(36,28,21,0.9)',
      texture: 'none', tracking: 1, headWeight: 900, bodyWeight: 700},
    caption: 'sticker',
    transition: 'fade',
  },

  /** 杂志信息图：机构解读、政策/科研说明，克制成稳 */
  editorial: {
    name: 'editorial',
    label: '杂志信息图',
    palette: {
      bg: '#F6F4EF', paper: '#FFFFFF', ink: '#16181D', muted: '#6B6F76',
      accent: '#C0432B', accent2: '#1F4E5F', pop: '#E2BE6B', line: '#D8D4CA',
    },
    font: {display: SERIF, body: SANS, mono: MONO},
    look: {radius: 3, borderW: 1.5, shadow: '0 18px 50px rgba(22,24,29,0.10)',
      texture: 'paper', tracking: 0.5, headWeight: 700, bodyWeight: 400},
    caption: 'herald',
    transition: 'wipe',
  },

  /** 深色科技：AI / 芯片 / 数据，屏幕感强 */
  'dark-tech': {
    name: 'dark-tech',
    label: '深色科技',
    palette: {
      bg: '#0B0E13', paper: '#141922', ink: '#E8ECF2', muted: '#8A94A6',
      accent: '#35E0C0', accent2: '#6C8CFF', pop: '#FFD166', line: '#242C3A',
    },
    font: {display: SANS, body: SANS, mono: MONO},
    look: {radius: 12, borderW: 1, shadow: '0 0 60px rgba(53,224,192,0.18)',
      texture: 'grid', tracking: 1.5, headWeight: 800, bodyWeight: 400},
    caption: 'bracket',
    transition: 'push',
  },

  /** 手账笔记：人文/生物/医学，温和亲近 */
  paper: {
    name: 'paper',
    label: '手账笔记',
    palette: {
      bg: '#FBF7EC', paper: '#FFFDF7', ink: '#2A2620', muted: '#7A7264',
      accent: '#B4553C', accent2: '#4A6B4F', pop: '#E8C75A', line: '#B9AE99',
    },
    font: {display: KAI, body: KAI, mono: MONO},
    look: {radius: 8, borderW: 2, shadow: '4px 5px 0 rgba(42,38,32,0.14)',
      texture: 'paper', tracking: 1, headWeight: 700, bodyWeight: 400},
    caption: 'marker',
    transition: 'fade',
  },
};

export const STYLE_NAMES = Object.keys(PRESETS);

type RawTimeline = {
  style?: string;
  themeOverride?: Partial<Palette>;
  [k: string]: unknown;
};

const raw = timelineJson as unknown as RawTimeline;

/** 解析当前风格：未知名字回落到 editorial，色板允许逐项覆盖 */
export const resolveStyle = (): StyleDef => {
  const base = PRESETS[raw.style || ''] || PRESETS.editorial;
  const override = raw.themeOverride || {};
  const palette = {...base.palette};
  (Object.keys(override) as (keyof Palette)[]).forEach((k) => {
    if (override[k]) palette[k] = override[k] as string;
  });
  return {...base, palette};
};

/** 把 #RRGGBB 转成 rgba()，用于半透明叠色 */
export const alpha = (hex: string, a: number): string => {
  const h = hex.replace('#', '');
  const full = h.length === 3 ? h.split('').map((c) => c + c).join('') : h;
  const n = parseInt(full, 16);
  return `rgba(${(n >> 16) & 255},${(n >> 8) & 255},${n & 255},${a})`;
};

/** 混色：t=0 取 a，t=1 取 b */
export const mix = (a: string, b: string, t: number): string => {
  const pa = parseInt(a.replace('#', ''), 16);
  const pb = parseInt(b.replace('#', ''), 16);
  const ch = (x: number) => Math.round(x);
  const r = ch(((pa >> 16) & 255) * (1 - t) + ((pb >> 16) & 255) * t);
  const g = ch(((pa >> 8) & 255) * (1 - t) + ((pb >> 8) & 255) * t);
  const bl = ch((pa & 255) * (1 - t) + (pb & 255) * t);
  return `rgb(${r},${g},${bl})`;
};
