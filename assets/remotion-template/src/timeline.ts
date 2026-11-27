import timelineJson from './data/timeline.json';
import type {Timeline} from './types';

/** 全局时间轴单例 */
export const TL = timelineJson as unknown as Timeline;
export const V = TL.height > TL.width;
/** 版式基准：竖屏/横屏都按短边算，字号在两向都稳定 */
export const BASE = Math.min(TL.width, TL.height);
export const U = BASE / 1080;
export const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
/** 场景内时间轴的通用缓入 */
export const ease = (local: number, from: number, dur: number): number =>
  Math.max(0, Math.min(1, (local - from) / Math.max(dur, 1)));
