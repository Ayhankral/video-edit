import os
import streamlit as st
from moviepy.editor import AudioFileClip, CompositeAudioClip, concatenate_audioclips, VideoFileClip, afx

# 1. SAYFA VE TASARIM AYARLARI
st.set_page_config(page_title="Radyo & Jenerik Kurgu", page_icon="🎙️", layout="wide")

st.markdown("""
<style>
    .main-header { font-size: 2.8rem; color: #FF4B4B; text-align: center; font-weight: 800; margin-bottom: 0px; padding-top: 20px;}
    .sub-header { text-align: center; color: #a1a1aa; margin-bottom: 40px; font-size: 1.1rem;}
    div.stButton > button { width: 100%; border-radius: 10px; height: 55px; font-size: 18px; font-weight: bold; background-color: #FF4B4B; color: white; border: none; transition: 0.3s;}
    div.stButton > button:hover { background-color: #ff3333; transform: scale(1.02); box-shadow: 0px 4px 15px rgba(255, 75, 75, 0.4);}
    .upload-box { border: 2px dashed #4b5563; padding: 20px; border-radius: 10px; background-color: #1f2937; text-align: center;}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">🎙️ Profesyonel Jenerik Kurgu Stüdyosu</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Ana şarkınızı (veya videonuzu) ve anonsunuzu yükleyin, sistem saniyeler içinde radyo kalitesinde miksajı yapsın.</p>', unsafe_allow_html=True)

# 2. SABİT FON MÜZİĞİ KONTROLÜ
olasi_uzantilar = [".mp4", ".mp3", ".wav", ".m4a", ".mov"]
aktif_fon = None
for uzanti in olasi_uzantilar:
    if os.path.exists(f"fon{uzanti}"):
        aktif_fon = f"fon{uzanti}"
        break

# 3. KULLANICI ARAYÜZÜ (mp4 desteği eklendi)
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("### 🎵 1. Adım: Ana Şarkı / Video")
    sarki_dosyasi = st.file_uploader("Ortadan kesilecek ses veya VİDEO dosyasını seçin.", type=["mp3", "wav", "m4a", "mp4"])

with col2:
    st.markdown("### 🎤 2. Adım: Anons / Ses Kaydı")
    ses_dosyasi = st.file_uploader("Araya girecek olan anonsu veya VİDEO kaydını seçin.", type=["mp3", "wav", "m4a", "mp4"])

st.markdown("---")

if not aktif_fon:
    st.error("❌ Sistemde sabit fon dosyası eksik! Lütfen GitHub'a 'fon.mp4' veya 'fon.mp3' dosyanızı yükleyin.")

# 4. İŞLEM BAŞLATMA VE GELİŞMİŞ UZANTI TANIMA MOTORU
if st.button("🚀 Kurguyu Başlat ve Birleştir") and sarki_dosyasi and aktif_fon:
    with st.spinner("🎧 Stüdyo motoru çalışıyor, sesler harmanlanıyor... Lütfen bekleyin."):
        temp_sarki_path = None
        temp_ses_path = None
        try:
            # Şarkının orijinal uzantısını al (mp4 vb. hatalarını engeller)
            sarki_ext = sarki_dosyasi.name.split('.')[-1]
            temp_sarki_path = f"temp_sarki.{sarki_ext}"
            
            with open(temp_sarki_path, "wb") as f:
                f.write(sarki_dosyasi.read())
            
            # AudioFileClip video yüklense bile içindeki sesi otomatik çeker alır
            sarki = AudioFileClip(temp_sarki_path)
            orta_nokta = sarki.duration / 2.0

            sarki_1 = sarki.subclip(0, orta_nokta).audio_fadeout(3.0)
            sarki_2 = sarki.subclip(orta_nokta, sarki.duration).audio_fadein(3.0)

            if aktif_fon.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
                fon_video = VideoFileClip(aktif_fon)
                fon = fon_video.audio
            else:
                fon = AudioFileClip(aktif_fon)

            if ses_dosyasi:
                ses_ext = ses_dosyasi.name.split('.')[-1]
                temp_ses_path = f"temp_ses.{ses_ext}"
                
                with open(temp_ses_path, "wb") as f:
                    f.write(ses_dosyasi.read())
                
                ses_kaydi = AudioFileClip(temp_ses_path)
                jenerik_giris = 1.5
                jenerik_cikis = 1.5
                ara_sure = ses_kaydi.duration + jenerik_giris + jenerik_cikis
                
                if fon.duration < ara_sure:
                    fon = afx.audio_loop(fon, duration=ara_sure)
                    
                fon_kisik = fon.subclip(0, ara_sure).volumex(0.25).audio_fadein(1.5).audio_fadeout(1.5)
                ses_yuksek = ses_kaydi.volumex(1.50).set_start(jenerik_giris)
                ara_ses = CompositeAudioClip([fon_kisik, ses_yuksek]).set_duration(ara_sure)
            else:
                ara_sure = min(fon.duration, 10.0)
                ara_ses = fon.subclip(0, ara_sure).volumex(0.25).audio_fadein(2.0).audio_fadeout(2.0)

            final_audio = concatenate_audioclips([sarki_1, ara_ses, sarki_2])
            
            cikti_yolu = "kurgu_hazir.mp3"
            final_audio.write_audiofile(cikti_yolu, fps=44100, logger=None, bitrate="192k")
            
            # Bellek Temizliği
            sarki.close()
            fon.close()
            if ses_dosyasi: ses_kaydi.close()
            final_audio.close()
            
            with open(cikti_yolu, "rb") as file:
                audio_bytes = file.read()

            st.success("✅ İşlem Kusursuz Şekilde Tamamlandı!")
            
            st.download_button(
                label="📥 Hazırlanan Kurguyu İndir",
                data=audio_bytes,
                file_name="Stüdyo_Kurgu_Master.mp3",
                mime="audio/mpeg"
            )

            # Dosya Temizliği (Sunucu çökmesini önler)
            os.remove(cikti_yolu)
            if temp_sarki_path and os.path.exists(temp_sarki_path):
                os.remove(temp_sarki_path)
            if temp_ses_path and os.path.exists(temp_ses_path):
                os.remove(temp_ses_path)

        except Exception as e:
            st.error(f"Sistem Hatası: {str(e)}")
            st.info("İpucu: Yüklediğiniz dosyaların bozuk olmadığından emin olun.")
