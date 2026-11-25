from __future__ import annotations
import os, json, tempfile, traceback
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv

from story import generate_gift_boxes, generate_story_choices, generate_storyboard
from media import generate_image, generate_narration, create_original_music, render_short

load_dotenv()

st.set_page_config(page_title="Magic Kids AI", page_icon="🎁", layout="wide")

st.title("🎁 Magic Kids AI")
st.caption("Üç kutu seç. İçinden üç macera çıksın.")
def get_key():
    try:
        return st.secrets.get("OPENAI_API_KEY", "") or os.getenv("OPENAI_API_KEY", "")
    except Exception:
        return os.getenv("OPENAI_API_KEY", "")

api_key = get_key()
if not api_key:
    st.warning("Üretim için OpenAI API anahtarı gerekli. Streamlit → App settings → Secrets bölümüne OPENAI_API_KEY = \"...\" ekle.")
    st.stop()

client = __import__("openai").OpenAI(api_key=api_key)

with st.sidebar:
    st.header("🎬 Stüdyo ayarları")
    age = st.selectbox("Hedef yaş grubu", ["2–4 yaş", "3–6 yaş", "6–9 yaş", "9–12 yaş", "Yaşa göre karma içerik"], index=4)
    duration = st.selectbox("Video süresi", ["45 saniye"], index=0)
    language = st.selectbox("Dil", ["Türkçe"])
    visual_style = st.selectbox("Görsel tarzı", ["Yüksek kaliteli, sevimli sinematik 3D animasyon"], index=0)
    st.markdown("---")
    st.write("**Sabit tercihler**")
    st.write("🎁 Sinematik kutu açılışı")
    st.write("🎙️ Sıcak, sevecen Türkçe anlatıcı")
    st.write("✨ Hikâyeye göre otomatik ses efektleri")
    st.write("🎵 Özgün otomatik arka plan müziği")
    st.write("🌟 Şaşırtıcı ve mutlu son")
    st.write("🔤 Videoda yazı ve altyazı yok")

if "stage" not in st.session_state:
    st.session_state.stage = "boxes"
if "box_choices" not in st.session_state:
    st.session_state.box_choices = None
if "story_choices" not in st.session_state:
    st.session_state.story_choices = None
if "selected_story" not in st.session_state:
    st.session_state.selected_story = None

def reset_all():
    for k in ["stage","box_choices","story_choices","selected_story","box_images","story_images","storyboard","final_video","audio_bytes"]:
        st.session_state.pop(k, None)
    st.session_state.stage = "boxes"

st.button("↻ Yeni oturum / yeni kutular", on_click=reset_all)

if st.session_state.stage == "boxes":
    st.subheader("Bugün hangi sihirli kutuyu açıyoruz?")
    if st.button("🎁 Üç yeni kutu oluştur", type="primary"):
        with st.spinner("Üç farklı sihirli dünya tasarlanıyor..."):
            st.session_state.box_choices = generate_gift_boxes(client, age, visual_style)
            st.session_state.box_images = []
            for item in st.session_state.box_choices:
                st.session_state.box_images.append(generate_image(client, item["image_prompt"], "1024x1024"))
        st.rerun()
    if st.session_state.box_choices:
        cols = st.columns(3)
        for i,(col,item,img) in enumerate(zip(cols, st.session_state.box_choices, st.session_state.box_images)):
            with col:
                st.image(img, use_container_width=True)
                st.subheader(item["name"])
                st.write(item["teaser"])
                if st.button(f"Bu kutuyu aç 🎁", key=f"box_{i}"):
                    with st.spinner("Kutu açılıyor... ✨ Üç yeni macera hazırlanıyor."):
                        st.session_state.story_choices = generate_story_choices(client, item, age, visual_style)
                        st.session_state.story_images = [generate_image(client, x["poster_prompt"], "1024x1024") for x in st.session_state.story_choices]
                        st.session_state.stage = "stories"
                    st.rerun()

elif st.session_state.stage == "stories":
    st.subheader("🎉 Kutunun içinden üç macera çıktı!")
    cols = st.columns(3)
    for i,(col,item,img) in enumerate(zip(cols, st.session_state.story_choices, st.session_state.story_images)):
        with col:
            st.image(img, use_container_width=True)
            st.subheader(item["title"])
            st.write(item["description"])
            st.caption(f"Değer: {item['lesson']}")
            if st.button("Bu hikâyeyi seç", key=f"story_{i}", type="primary"):
                st.session_state.selected_story = item
                st.session_state.stage = "production"
                st.rerun()
    if st.button("← Kutulara dön"):
        st.session_state.stage = "boxes"
        st.rerun()

elif st.session_state.stage == "production":
    story = st.session_state.selected_story
    st.subheader(f"🎬 Seçilen macera: {story['title']}")
    st.write(story["description"])
    if st.button("Hikâyeyi ve videoyu üret", type="primary"):
        with st.status("Animasyon stüdyosu çalışıyor...", expanded=True) as status:
            st.write("Hikâye sahnelere ayrılıyor...")
            board = generate_storyboard(client, story, age, visual_style, 5)
            st.session_state.storyboard = board
            work = Path(tempfile.mkdtemp(prefix="magic_kids_"))
            scene_paths = []
            for i,scene in enumerate(board["scenes"], 1):
                st.write(f"{i}/5: Sahne görseli oluşturuluyor...")
                img = generate_image(client, scene["image_prompt"], "1024x1536")
                p = work / f"scene_{i:02d}.png"
                p.write_bytes(img)
                scene_paths.append(p)
            st.write("Sıcak Türkçe anlatım hazırlanıyor...")
            audio = generate_narration(client, board["narration"], work/"narration.mp3")
            st.write("Hikâyeye uygun özgün müzik ve efektler hazırlanıyor...")
            music = create_original_music(board.get("mood","wonder"), 45, work/"music.wav")
            st.write("Dikey video birleştiriliyor...")
            video = render_short(scene_paths, audio, music, work/"magic_kids_shorts.mp4", 45)
            st.session_state.final_video = video.read_bytes()
            st.session_state.final_title = story["title"]
            status.update(label="Macera hazır! 🎉", state="complete", expanded=False)
    if st.session_state.get("final_video"):
        st.video(st.session_state.final_video)
        st.download_button("⬇️ MP4 videoyu indir", st.session_state.final_video, file_name="magic_kids_shorts.mp4", mime="video/mp4", type="primary")
        with st.expander("Hikâye metni"):
            st.write(st.session_state.storyboard["narration"])
        if st.button("Yeni kutular oluştur"):
            reset_all()
            st.rerun()
