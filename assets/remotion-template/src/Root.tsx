import React from 'react';
import {Composition} from 'remotion';
import {TL} from './timeline';
import {SciVideo} from './Video';

export const RemotionRoot: React.FC = () => (
  <Composition
    id="SciVideo"
    component={SciVideo}
    durationInFrames={TL.total}
    fps={TL.fps}
    width={TL.width}
    height={TL.height}
  />
);
