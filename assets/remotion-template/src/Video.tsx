import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {Captions} from './Captions';
import {Progress} from './Chrome';
import {EndCard} from './EndCard';
import {Intro} from './Intro';
import {SceneCard} from './SceneCard';
import {resolveStyle} from './style';
import {TL} from './timeline';

/**
 * 主合成：片头 → 正片各场 → 片尾，字幕与进度条独立分层。
 * 全部时序来自 src/data/timeline.json（由 scripts/timeline.py 生成）。
 */
export const SciVideo: React.FC = () => {
  const frame = useCurrentFrame();
  const s = resolveStyle();
  const introEnd = TL.intro.from + TL.intro.dur;
  const inIntro = frame >= TL.intro.from && frame < introEnd;
  const inEnd = frame >= TL.end.from;

  return (
    <AbsoluteFill style={{background: s.palette.bg}}>
      {inIntro ? <Intro s={s} /> : null}

      {TL.scenes.map((sc) =>
        frame >= sc.from && frame < sc.from + sc.dur ? <SceneCard key={sc.id} scene={sc} s={s} /> : null,
      )}

      {!inIntro && !inEnd && TL.scenes.length > 0 ? <Captions s={s} /> : null}

      {inEnd ? <EndCard s={s} /> : null}

      <Progress s={s} />
    </AbsoluteFill>
  );
};
