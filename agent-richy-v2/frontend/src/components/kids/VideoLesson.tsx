'use client';

import React from 'react';
import { motion } from 'framer-motion';

interface Props {
  videoUrl?: string;
  videoType?: string;
  title: string;
  description?: string;
  thumbnailEmoji?: string;
  onPlay?: () => void;
}

export default function VideoLesson({ videoUrl, videoType, title, description, thumbnailEmoji = '🎬', onPlay }: Props) {
  const [playing, setPlaying] = React.useState(false);
  const isYouTube = videoType === 'youtube' || videoUrl?.includes('youtube.com');

  const handlePlay = () => {
    setPlaying(true);
    onPlay?.();
  };

  return (
    <div className="rounded-xl border border-navy-700
                    bg-navy-800 overflow-hidden shadow-sm">
      {/* Video area */}
      <div className="relative aspect-video bg-gradient-to-br from-navy-800 to-navy-900
                      flex items-center justify-center">
        {playing && videoUrl && isYouTube ? (
          <iframe
            src={`${videoUrl}?autoplay=1`}
            title={title}
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
            className="w-full h-full"
          />
        ) : playing && videoUrl ? (
          <video
            src={videoUrl}
            controls
            autoPlay
            className="w-full h-full object-cover"
          />
        ) : (
          <motion.button
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
            onClick={handlePlay}
            className="flex flex-col items-center gap-2"
          >
            <div className="w-16 h-16 rounded-full bg-gold-500/90 flex items-center justify-center
                            shadow-lg backdrop-blur-sm">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="white">
                <path d="M8 5v14l11-7z" />
              </svg>
            </div>
            <span className="text-4xl">{thumbnailEmoji}</span>
          </motion.button>
        )}
      </div>

      {/* Info */}
      <div className="p-4">
        <h3 className="text-sm font-semibold text-white">{title}</h3>
        {description && (
          <p className="text-xs text-gray-400 mt-1 line-clamp-2">
            {description}
          </p>
        )}
      </div>
    </div>
  );
}
