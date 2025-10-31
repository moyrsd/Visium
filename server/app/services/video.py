from moviepy import (
    VideoFileClip,
    AudioFileClip,
    concatenate_videoclips,
    CompositeAudioClip,
    afx,
    vfx,
)
import random


def final_video(video_paths, audio_paths, music_paths):
    clips = []
    for v, a in zip(video_paths, audio_paths):
        vc, ac = VideoFileClip(v), AudioFileClip(a)
        video_clip = vc.with_audio(ac)
        clips.append(video_clip.with_effects([vfx.FadeIn(1), vfx.FadeOut(1)]))

    final = concatenate_videoclips(clips, method="compose")
    music_path = random.choice(music_paths)
    music = AudioFileClip(music_path)
    music = music.with_effects(
        [
            afx.MultiplyVolume(0.05),
            afx.AudioFadeIn(2),
            afx.AudioLoop(duration=final.duration),
        ]
    )
    mixed_audio = CompositeAudioClip([final.audio, music])
    final = final.with_audio(mixed_audio)
    final.write_videofile(
        "output.mp4",
        codec="libx264",
        audio_codec="aac",
        temp_audiofile="temp-audio.m4a",
        remove_temp=True,
    )

    print("Final Video rendered succesfully")


# if __name__ == "__main__":
#     video_paths = [
#         "media/videos/92c3c4a8-c9da-4143-b64e-ae781ac86984/videos/slide_1/480p15/slide_1.mp4",
#         "media/videos/92c3c4a8-c9da-4143-b64e-ae781ac86984/videos/slide_2/480p15/slide_2.mp4",
#         "media/videos/92c3c4a8-c9da-4143-b64e-ae781ac86984/videos/slide_3/480p15/slide_3.mp4",
#         "media/videos/92c3c4a8-c9da-4143-b64e-ae781ac86984/videos/slide_4/480p15/slide_4.mp4",
#         "media/videos/92c3c4a8-c9da-4143-b64e-ae781ac86984/videos/slide_5/480p15/slide_5.mp4",
#         "media/videos/92c3c4a8-c9da-4143-b64e-ae781ac86984/videos/slide_6/480p15/slide_6.mp4",
#         "media/videos/92c3c4a8-c9da-4143-b64e-ae781ac86984/videos/slide_7/480p15/slide_7.mp4",
#     ]
#     audio_paths = [
#         "media/audio/92c3c4a8-c9da-4143-b64e-ae781ac86984/slide_1.mp3",
#         "media/audio/92c3c4a8-c9da-4143-b64e-ae781ac86984/slide_2.mp3",
#         "media/audio/92c3c4a8-c9da-4143-b64e-ae781ac86984/slide_3.mp3",
#         "media/audio/92c3c4a8-c9da-4143-b64e-ae781ac86984/slide_4.mp3",
#         "media/audio/92c3c4a8-c9da-4143-b64e-ae781ac86984/slide_5.mp3",
#         "media/audio/92c3c4a8-c9da-4143-b64e-ae781ac86984/slide_6.mp3",
#         "media/audio/92c3c4a8-c9da-4143-b64e-ae781ac86984/slide_7.mp3",
#     ]
#     music_paths = [
#         "1.mp3",
#         "2.mp3",
#         "3.mp3",
#         "4.mp3",
#         "5.mp3",
#         "6.mp3",
#         "7.mp3",
#         "8.mp3",
#         "9.mp3",
#         "10.mp3",
#     ]
#     relative_music_paths = ["3b1b_music_library/" + s for s in music_paths]
#     final_video(video_paths, audio_paths, relative_music_paths)
