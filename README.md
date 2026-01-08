# METİN ASİSTANI

Profesyonel Ses Tanıma Sistemi - Mikrofonla alınan sesi veya yüklenen ses dosyalarını yazıya çeviren Türkçe destekli masaüstü uygulaması.

**Geliştirici:** Ahmet Birhat Okumuş

---

## 🚀 Kullanım

**MetinAsistani.exe** dosyasına çift tıklayın. Uygulama açılacaktır.

> Not: İlk açılışta birkaç saniye bekleyebilir.

---

## 📋 Gereksinimler

- Windows 10/11
- İnternet bağlantısı (Groq API için gerekli)

---

## ✨ Özellikler

- 🎙️ **Canlı Mikrofon Kaydı**: Başlat/Durdur ile istediğiniz kadar kayıt
- 📁 **Dosya Yükleme**: WAV, MP3, M4A, OGG, FLAC formatları
- 🇹🇷 **Türkçe Desteği**: Groq Whisper ile yüksek doğruluk
- � **Gürültü Temizleme**: Arka plan sesleri otomatik filtreleme
- 🤖 **Yapay Zeka Düzeltme**: Groq LLM ile metin iyileştirme
- ⚙️ **Kalite Seçenekleri**: Hızlı, Dengeli, Yüksek Kalite

---

## 🎯 Kalite Seçenekleri

| Seçenek | Açıklama |
|---------|----------|
| **Hızlı** | Hızlı işlem, iyi kalite |
| **Dengeli** | Dengeli hız ve kalite (önerilen) |
| **Yüksek Kalite** | En iyi kalite, daha yavaş |

---

## 🛠️ Teknolojiler

- **Groq Whisper API**: Ses tanıma (whisper-large-v3-turbo)
- **Groq LLM**: Metin düzeltme (llama-3.3-70b)
- **Noisereduce**: Gürültü azaltma
- **Tkinter**: Masaüstü arayüzü
- **SoundDevice**: Mikrofon erişimi

---

## 📁 Dosyalar

| Dosya | Açıklama |
|-------|----------|
| `kurulum.bat` | Kurulum dosyası - ilk çalıştırmada kullanın |
| `baslat.bat` | Başlatma dosyası - uygulamayı açar |
| `desktop_app.py` | Ana uygulama kodu |
| `requirements.txt` | Python bağımlılıkları |

---

## 📞 Destek

Herhangi bir sorun yaşarsanız:
1. Python'un yüklü olduğundan emin olun
2. `kurulum.bat` dosyasını yönetici olarak çalıştırın
3. İnternet bağlantınızı kontrol edin (Groq API için gerekli)

---

**© 2024 Ahmet Birhat Okumuş - Tüm hakları saklıdır.**
