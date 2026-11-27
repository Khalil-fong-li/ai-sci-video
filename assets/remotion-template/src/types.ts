/** 时间轴数据结构：由 scripts/timeline.py 生成，不要手改。 */
export type Chunk = {from: number; dur: number; text: string};

export type Visual =
  | {type: 'image'; src: string; motion: string; fit?: 'cover' | 'contain'; label?: string}
  | {type: 'keywords'; words: string[]; note?: string}
  | {type: 'stat'; value: string; unit?: string; label?: string}
  | {type: 'bars'; items: {label: string; value: number}[]; unit?: string; max?: number}
  | {type: 'steps'; items: string[]; title?: string}
  | {
      type: 'compare';
      left: {title: string; points: string[]};
      right: {title: string; points: string[]};
    }
  | {type: 'quote'; text: string; by?: string}
  | {type: 'blank'};

export type Scene = {
  id: string;
  index: number;
  from: number;
  dur: number;
  visual: Visual;
  chunks: Chunk[];
};

export type Timeline = {
  fps: number;
  width: number;
  height: number;
  total: number;
  ratio: string;
  style: string;
  themeOverride: Record<string, string>;
  intro: {from: number; dur: number; kicker: string; line: string};
  scenes: Scene[];
  end: {from: number; dur: number; line1: string; line2: string; qr?: string};
};
