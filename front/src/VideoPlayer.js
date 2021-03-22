import React, { useEffect, useRef, useState } from 'react';
import videojs from 'video.js';
import 'video.js/dist/video-js.min.css';

export default function VideoPlayer(props) {
  const playerRef = useRef();
  const [player, setPlayer] = useState(null);

  useEffect(() => {
    const p = videojs(playerRef.current, { autoplay: true, muted: true });
    setPlayer(p);
    return () => {
      p.dispose();
    };
  }, []);

  useEffect(() => {
    if (player) {
      player.src(props.videoSrc);
    }
  }, [player, props.videoSrc]);

  return (
    <div data-vjs-player>
      <video ref={playerRef} className="video-js vjs-16-9" playsInline />
    </div>
  );
}