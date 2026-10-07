import os
import streamlit as st
from moviepy.editor import AudioFileClip, CompositeAudioClip, concatenate_audioclips, VideoFileClip, afx

# Streamlit web arayüzü ayarları
st.title("Gelişmiş Ses Kurgu Stüdyosu")
st.write("Ana şarkınızı ve sesli mesajınızı yükleyerek profesyonel kurguyu başlatın.")

# Web üzerinden dosya yükleme alanları
sarki_dosyasi = st.file_uploader("🎵 Ana Şarkı (Ortadan Kesilecek):", type=["mp3", "wav", "m4a", "mp4"])
ses_dosyasi = st.file_uploader("🎤 Sesli Mesajın (Konuşma Kaydı):", type=["mp3", "wav", "m4a", "mp4"])

# Fon dosyasını mevcut dizinde arama mantığı
olasi_uzantilar = [".mp4", ".mp3", ".wav", ".m4a", ".mov"]
aktif_fon = None
for uzanti in olasi_uzantilar:
    if os.path.exists(f"fon{uzanti}"):
        aktif_fon = f"fon{uzanti}"
        break

if aktif_fon:
    st.success(f"✅ Sabit Fon Algılandı ({aktif_fon})")
else:
    st.error("❌ Sabit Fon Bulunamadı! Lütfen kodun bulunduğu klasöre 'fon.mp4' veya 'fon.mp3' koyun.")

if st.button("🚀 Profesyonel Olarak Birleştir") and sarki_dosyasi and aktif_fon:
    with st.spinner("Ses profesyonelce işleniyor, lütfen bekleyin..."):
        try:
            # Yüklenen dosyaları geçici olarak kaydet (moviepy'nin okuyabilmesi için)
            with open("temp_sarki.mp3", "wb") as f:
                f.write(sarki_dosyasi.read())
            
            sarki = AudioFileClip("temp_sarki.mp3")
            orta_nokta = sarki.duration / 2.0

            sarki_1 = sarki.subclip(0, orta_nokta).audio_fadeout(3.0)
            sarki_2 = sarki.subclip(orta_nokta, sarki.duration).audio_fadein(3.0)

            if aktif_fon.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
                fon_video = VideoFileClip(aktif_fon)
                fon = fon_video.audio
            else:
                fon = AudioFileClip(aktif_fon)

            if ses_dosyasi:
                with open("temp_ses.mp3", "wb") as f:
                    f.write(ses_dosyasi.read())
                
                ses_kaydi = AudioFileClip("temp_ses.mp3")
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
            
            cikti_yolu = "gelismis_kurgu_web.mp3"
            final_audio.write_audiofile(cikti_yolu, fps=44100)
            
            st.success("İşlem Tamamlandı!")
            
            # Web sitesi üzerinden indirme butonu
            with open(cikti_yolu, "rb") as file:
                st.download_button(
                    label="Oluşturulan Ses Dosyasını İndir",
                    data=file,
                    file_name="gelişmis_kurgu.mp3",
                    mime="audio/mpeg"
                )

        except Exception as e:
            st.error(f"Hata oluştu: {str(e)}")