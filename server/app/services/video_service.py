import os
import random
import uuid

from moviepy import AudioFileClip, CompositeAudioClip, VideoFileClip, afx, concatenate_videoclips, vfx

from app.services.logging_service import logger


def render_video(video_paths, music_paths, output_path, music_multiply=0.05, user_music=None) -> None:
    clips = []
    for v in video_paths:
        vc = VideoFileClip(v)
        clips.append(vc)

    final = concatenate_videoclips(clips, method="compose")

    if not user_music:
        music_path = random.choice(music_paths)
        music = AudioFileClip(music_path)
    else:
        music = AudioFileClip(user_music)

    logger.info(f"Using music track: {music_path if not user_music else 'user provided music'}")
    music = music.with_effects(
        [afx.MultiplyVolume(music_multiply), afx.AudioFadeIn(2), afx.AudioLoop(duration=final.duration)]
    )
    logger.info(f"Music duration after loop: {music.duration}, Video duration: {final.duration}")
    mixed_audio = CompositeAudioClip([final.audio, music])
    final = final.with_audio(mixed_audio)
    write_output(final, output_path)
    logger.info(f"Final Video rendered at {output_path}")


def mix_audio(video_path: str, audio_path: str, output_path: str, fade_duration: int = 1) -> None:
    vc = VideoFileClip(video_path)
    ac = AudioFileClip(audio_path)
    video_clip = vc.with_audio(ac)
    fade_video = video_clip.with_effects([vfx.FadeIn(fade_duration), vfx.FadeOut(fade_duration)])
    write_output(fade_video, output_path)
    logger.info(f"Audio mixed and video saved at {output_path}")
    return output_path


def write_output(clip, output_path: str) -> None:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    clip.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        temp_audiofile=f"{output_path}.temp_audio_{uuid.uuid4().hex}.m4a",
        remove_temp=True,
    )


