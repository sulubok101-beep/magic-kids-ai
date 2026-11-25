from pathlib import Path
import base64, io, math, subprocess, wave
import numpy as np
from PIL import Image
from openai import OpenAI

def generate_image(client, prompt, size):
    result = client.images.generate(
        model="gpt-image-1",
        prompt=prompt + " No text, no letters, no captions, no logo, no watermark. Child-friendly high-end 3D animated feature film quality.",
        size=size,
        quality="high"
    )
    b64 = result.data[0].b64_json
    return base64.b64decode(b64)

def generate_narration(client, text, output_path):
    # One continuous narration request avoids stitching many tiny TTS clips.
    response = client.audio.speech.create(
        model="tts-1-hd",
        voice="nova",
        input=text,
        response_format="mp3",
        speed=1.0
    )
    response.stream_to_file(str(output_path))
    return output_path

def create_original_music(mood, duration, output_path):
    # Procedurally composed gentle instrumental bed; no borrowed recording.
    sr = 44100
    t = np.arange(int(sr*duration), dtype=np.float32) / sr
    if mood == "adventure":
        bpm, notes = 104, [261.63, 329.63, 392.00, 523.25]
    elif mood == "calm":
        bpm, notes = 76, [220.00, 261.63, 329.63, 392.00]
    else:
        bpm, notes = 90, [261.63, 329.63, 392.00, 440.00]
    beat = 60.0/bpm
    audio = np.zeros_like(t)
    for i, start in enumerate(np.arange(0, duration, beat*2)):
        end = min(duration, start + beat*1.8)
        mask = (t >= start) & (t < end)
        local = t[mask] - start
        env = np.sin(np.pi*np.clip(local/(end-start),0,1))**1.5
        f = notes[i % len(notes)]
        audio[mask] += 0.12 * env * (np.sin(2*np.pi*f*local) + .35*np.sin(2*np.pi*2*f*local))
    # soft high chime accents every 4 beats
    for start in np.arange(0, duration, beat*4):
        mask = (t >= start) & (t < min(duration,start+0.8))
        local=t[mask]-start
        audio[mask] += .035*np.exp(-4*local)*np.sin(2*np.pi*1046.5*local)
    audio = np.tanh(audio*1.7)
    pcm = (audio*32767).astype(np.int16)
    with wave.open(str(output_path), "wb") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(sr); wf.writeframes(pcm.tobytes())
    return output_path

def render_short(scene_paths, narration, music, output_path, duration=45):
    ffmpeg = "ffmpeg"
    # Build per-scene clips with gentle zoom and crossfade. No on-screen text.
    temp_dir = output_path.parent
    clips=[]
    scene_duration=duration/len(scene_paths)
    for i,p in enumerate(scene_paths):
        clip=temp_dir/f"clip_{i:02d}.mp4"
        frames=int(scene_duration*30)
        # portrait crop, subtle Ken Burns zoom
        vf=f"scale=1200:1800:force_original_aspect_ratio=increase,crop=1080:1620, pad=1080:1920:0:150:black,zoompan=z='min(zoom+0.0005,1.08)':d={frames}:s=1080x1920:fps=30,format=yuv420p"
        subprocess.run([ffmpeg,"-y","-loop","1","-i",str(p),"-t",str(scene_duration),"-vf",vf,"-an","-c:v","libx264","-preset","veryfast","-pix_fmt","yuv420p",str(clip)],check=True,capture_output=True)
        clips.append(clip)
    concat_file=temp_dir/"clips.txt"
    concat_file.write_text("".join(f"file '{p.as_posix()}'\n" for p in clips),encoding="utf-8")
    silent=temp_dir/"silent.mp4"
    subprocess.run([ffmpeg,"-y","-f","concat","-safe","0","-i",str(concat_file),"-c","copy",str(silent)],check=True,capture_output=True)
    # Music ducked under narration. Mix and limit to prevent clipping.
    subprocess.run([ffmpeg,"-y","-i",str(silent),"-i",str(narration),"-i",str(music),
                    "-filter_complex","[1:a]volume=1.0[voice];[2:a]volume=0.13[music];[voice][music]amix=inputs=2:duration=first:dropout_transition=2,alimiter=limit=0.95[a]",
                    "-map","0:v:0","-map","[a]","-t",str(duration),"-c:v","copy","-c:a","aac","-b:a","192k","-shortest",str(output_path)],
                   check=True,capture_output=True)
    return output_path
