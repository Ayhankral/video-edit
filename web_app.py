import os
import streamlit as st
from moviepy.editor import AudioFileClip, CompositeAudioClip, concatenate_audioclips, VideoFileClip, concatenate_videoclips, afx, vfx, ColorClip

# 1. TASARIM VE SAYFA AYARLARI (Gelişmiş Arka Plan ve Cam Efekti)
st.set_page_config(page_title="Pro Kurgu Stüdyosu", page_icon="🎬", layout="wide")

st.markdown("""
<style>
    /* Arka Plan Degradesi (Stüdyo Hissiyatı) */
    [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at top right, #1e1b4b 0%, #0f172a 50%, #000000 100%);
        color: #e2e8f0;
    }
    
    /* Üst Barı Gizleme */
    [data-testid="stHeader"] {
        background-color: transparent;
    }
    
    /* Cam Efekti (Glassmorphism) - Kolonlar İçin */
    [data-testid="column"] {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 20px;
        padding: 25px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(12px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    }

    /* Başlık Stilleri */
    .main-header { font-size: 3.5rem; color: #f8fafc; text-align: center; font-weight: 900; margin-bottom: 0px; padding-top: 10px; letter-spacing: -1.5px;}
    .main-header span { color: #FF4B4B; text-shadow: 0px 4px 25px rgba(255, 75, 75, 0.6); }
    .sub-header { text-align: center; color: #94a3b8; margin-bottom: 50px; font-size: 1.15rem; font-weight: 300;}
    
    /* İkonlar ve Butonlar */
    div.stButton > button { 
        width: 100%; 
        border-radius: 12px; 
        height: 65px; 
        font-size: 20px; 
        font-weight: 800; 
        background: linear-gradient(90deg, #FF4B4B 0%, #ff2a2a 100%);
        color: white; 
        border: none; 
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 20px;
    }
    div.stButton > button:hover { 
        transform: translateY(-4px); 
        box-shadow: 0px 12px 25px rgba(255, 75, 75, 0.5);
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">🎬 <span>Pro</span> Kurgu Stüdyosu</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Videolarınızı ve seslerinizi yapay zeka pürüzsüzlüğüyle harmanlayın. Gerçek bir radyo ve TV stüdyosu deneyimi.</p>', unsafe_allow_html=True)

# 2. SABİT FON MÜZİĞİ/VİDEOSU KONTROLÜ
olasi_uzantilar = [".mp4", ".mp3", ".wav", ".m4a", ".mov"]
aktif_fon = None
for uzanti in olasi_uzantilar:
    if os.path.exists(f"fon{uzanti}"):
        aktif_fon = f"fon{uzanti}"
        break

# 3. KULLANICI ARAYÜZÜ
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("### 🎬 1. Adım: Ana Medya")
    sarki_dosyasi = st.file_uploader("Ortadan kesilecek Video (.mp4) veya Ses (.mp3) dosyasını seçin.", type=["mp3", "wav", "m4a", "mp4", "mov"])

with col2:
    st.markdown("### 🎤 2. Adım: Araya Girecek Anons")
    ses_dosyasi = st.file_uploader("Araya girecek olan anons kaydını seçin.", type=["mp3", "wav", "m4a", "mp4", "mov"])

if not aktif_fon:
    st.error("❌ Sistemde sabit fon dosyası eksik! Lütfen 'fon.mp4' veya 'fon.mp3' yükleyin.")

# 4. YENİ NESİL VİDEO & SES İŞLEME MOTORU
if st.button("🚀 Kurguyu Başlat") and sarki_dosyasi and aktif_fon:
    with st.spinner("🎧 Stüdyo motoru devrede... Görüntü ve sesler işleniyor. Dosya boyutuna göre birkaç dakika sürebilir."):
        temp_sarki_path = None
        temp_ses_path = None
        try:
            # 1. Dosyaların Geçici Kaydı ve Tip Analizi
            sarki_ext = sarki_dosyasi.name.split('.')[-1].lower()
            is_main_video = sarki_ext in ['mp4', 'mov', 'avi', 'mkv']
            temp_sarki_path = f"temp_sarki.{sarki_ext}"
            
            with open(temp_sarki_path, "wb") as f:
                f.write(sarki_dosyasi.read())
            
            # 2. Ana Medyanın Parçalanması ve Sinematik Geçişler
            if is_main_video:
                sarki = VideoFileClip(temp_sarki_path)
                orta_nokta = sarki.duration / 2.0
                # Videolarda hem görüntüyü karart(fadeout) hem sesi kıs(audio_fadeout)
                sarki_1 = sarki.subclip(0, orta_nokta).fadeout(3.0).audio_fadeout(3.0)
                sarki_2 = sarki.subclip(orta_nokta, sarki.duration).fadein(3.0).audio_fadein(3.0)
            else:
                sarki = AudioFileClip(temp_sarki_path)
                orta_nokta = sarki.duration / 2.0
                sarki_1 = sarki.subclip(0, orta_nokta).audio_fadeout(3.0)
                sarki_2 = sarki.subclip(orta_nokta, sarki.duration).audio_fadein(3.0)

            # 3. Fon (Arka Plan) Dosyasının Analizi
            is_fon_video = aktif_fon.lower().endswith(('.mp4', '.mov', '.avi', '.mkv'))
            if is_fon_video:
                fon_medya = VideoFileClip(aktif_fon)
                fon_audio = fon_medya.audio
            else:
                fon_audio = AudioFileClip(aktif_fon)
                fon_medya = None

            # 4. Araya Girecek Anons Sesinin Ayarlanması
            if ses_dosyasi:
                ses_ext = ses_dosyasi.name.split('.')[-1].lower()
                temp_ses_path = f"temp_ses.{ses_ext}"
                with open(temp_ses_path, "wb") as f:
                    f.write(ses_dosyasi.read())
                
                # Anons olarak video yüklenirse bile sadece içindeki sesi alırız
                if ses_ext in ['mp4', 'mov']:
                    gecici_vid = VideoFileClip(temp_ses_path)
                    ses_kaydi = gecici_vid.audio
                else:
                    ses_kaydi = AudioFileClip(temp_ses_path)
                    
                jenerik_giris = 1.5
                jenerik_cikis = 1.5
                ara_sure = ses_kaydi.duration + jenerik_giris + jenerik_cikis
                
                if fon_audio.duration < ara_sure:
                    fon_audio_loop = afx.audio_loop(fon_audio, duration=ara_sure)
                else:
                    fon_audio_loop = fon_audio
                    
                fon_kisik = fon_audio_loop.subclip(0, ara_sure).volumex(0.25).audio_fadein(1.5).audio_fadeout(1.5)
                ses_yuksek = ses_kaydi.volumex(1.50).set_start(jenerik_giris)
                ara_ses = CompositeAudioClip([fon_kisik, ses_yuksek]).set_duration(ara_sure)
            else:
                ara_sure = min(fon_audio.duration, 10.0)
                ara_ses = fon_audio.subclip(0, ara_sure).volumex(0.25).audio_fadein(2.0).audio_fadeout(2.0)

            # 5. GÖRSEL VE İŞİTSEL BİRLEŞTİRME (VURUCU KISIM)
            if is_main_video:
                # Aradaki anons sırasında ekranda ne gözükecek?
                if is_fon_video and fon_medya:
                    # Fonumuz videoyla anons süresi kadar o fon videosunu döngüye al
                    ara_gorsel = fon_medya.fx(vfx.loop, duration=ara_sure).resize(sarki.size)
                else:
                    # Fon videolu değilse şık bir stüdyo siyahı ekran koy
                    ara_gorsel = ColorClip(size=sarki.size, color=(15, 23, 42), duration=ara_sure)
                
                # Aradaki görsele mikslenmiş sesleri göm
                ara_video_clip = ara_gorsel.set_audio(ara_ses)
                final_clip = concatenate_videoclips([sarki_1, ara_video_clip, sarki_2])
                
                cikti_yolu = "Studyo_Master.mp4"
                mime_type = "video/mp4"
                # Videoyu web uyumlu ses formatıyla (aac) dışarı aktar
                final_clip.write_videofile(cikti_yolu, fps=24, logger=None, audio_codec="aac")
            else:
                # Sadece ses varsa basit birleştirme yap
                final_clip = concatenate_audioclips([sarki_1, ara_ses, sarki_2])
                cikti_yolu = "Studyo_Master.mp3"
                mime_type = "audio/mpeg"
                final_clip.write_audiofile(cikti_yolu, fps=44100, logger=None, bitrate="192k")

            # Sunucuyu Rahatlat
            try: final_clip.close(); sarki.close(); 
            except: pass

            with open(cikti_yolu, "rb") as file:
                medya_bytes = file.read()

            st.success("✅ Kusursuz Kurgu Hazır!")
            
            st.download_button(
                label=f"📥 Hazırlanan Kurguyu İndir ({'Video' if is_main_video else 'Ses'})",
                data=medya_bytes,
                file_name=cikti_yolu,
                mime=mime_type
            )

            # Çöpleri temizle
            os.remove(cikti_yolu)
            if os.path.exists(temp_sarki_path): os.remove(temp_sarki_path)
            if temp_ses_path and os.path.exists(temp_ses_path): os.remove(temp_ses_path)

        except Exception as e:
            st.error(f"Sistem Hatası: {str(e)}")
            st.info("İpucu: Yüklenen dosyanın desteklenen bir mp4 veya mp3 olduğundan emin olun.")
