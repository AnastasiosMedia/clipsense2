import React from 'react';

interface Clip {
  path: string;
  score: number;
  scene: string;
  emotional_tone: string;
  story_importance: number;
  selection_reason: string;
  thumbnail_path?: string;
  ai_analysis?: string;
  object_detection?: {
    wedding_rings: number;
    wedding_cake: number;
    dancing: number;
    bouquet: number;
    ceremony_moments: number;
    toast_moments: number;
    people: number;
  };
  key_moments?: number[];
}

interface StoryboardGalleryProps {
  clips: Clip[];
  onClipClick?: (clip: Clip, index: number) => void;
}

export const StoryboardGallery: React.FC<StoryboardGalleryProps> = ({
  clips,
  onClipClick
}) => {
  const getSceneTypeIcon = (scene: string) => {
    const icons: { [key: string]: string } = {
      'ceremony': '💒',
      'reception': '🎉',
      'preparation': '💄',
      'dancing': '💃',
      'speeches': '🎤',
      'cake': '🍰'
    };
    return icons[scene] || '🎬';
  };

  if (!clips || clips.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-[#888888] text-lg mb-2">No clips available</div>
        <div className="text-[#666666] text-sm">Upload videos to see your storyboard</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h3 className="text-2xl font-bold text-white mb-2">Storyboard Gallery</h3>
        <p className="text-[#888888]">Visual flow of your highlight video</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {clips.map((clip, index) => (
          <div
            key={index}
            className="group cursor-pointer"
            onClick={() => onClipClick?.(clip, index)}
          >
            <div className="bg-[#0d0d0d] border border-[#1a1a1a] rounded-lg overflow-hidden transition-all duration-200 hover:border-[#333333]">
              {/* Thumbnail */}
              <div className="relative aspect-video bg-[#0f0f0f]">
                {clip.thumbnail_path ? (
                  <img
                    src={`http://127.0.0.1:8123${clip.thumbnail_path}`}
                    alt={clip.path?.split('/').pop() || 'Clip'}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center">
                    <div className="text-center">
                      <div className="text-4xl mb-2">{getSceneTypeIcon(clip.scene || 'ceremony')}</div>
                      <div className="text-[#666666] text-sm">No Preview</div>
                    </div>
                  </div>
                )}
                
                {/* Clip number overlay */}
                <div className="absolute top-2 left-2 bg-black/80 text-white text-sm px-2 py-1 rounded font-medium">
                  {index + 1}
                </div>
              </div>
              
              {/* No content - just the thumbnail with number overlay */}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
