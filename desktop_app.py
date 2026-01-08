import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import sounddevice as sd
import soundfile as sf
import numpy as np
import noisereduce as nr
import tempfile
import os
from groq import Groq

# Groq API anahtarı


# Kalite seçenekleri
QUALITY_OPTIONS = {
    "Hızlı": {"model": "whisper-large-v3-turbo", "description": "Hızlı işlem, iyi kalite"},
    "Dengeli": {"model": "whisper-large-v3-turbo", "description": "Dengeli hız ve kalite"},
    "Yüksek Kalite": {"model": "whisper-large-v3", "description": "En iyi kalite, daha yavaş"}
}

class MetinAsistani:
    def __init__(self, root):
        self.root = root
        self.root.title("Metin Asistanı - Profesyonel Ses Tanıma")
        self.root.geometry("750x700")
        self.root.configure(bg="#1a1a2e")
        self.root.resizable(True, True)
        
        # Değişkenler
        self.is_recording = False
        self.audio_data = []
        self.sample_rate = 16000
        self.groq_client = Groq(api_key=GROQ_API_KEY)
        self.stream = None
        
        # Stil ayarları
        self.setup_styles()
        self.create_widgets()
    
    def setup_styles(self):
        """Kurumsal stil ayarları"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Renk paleti
        self.colors = {
            'primary': '#0f3460',
            'secondary': '#16213e',
            'accent': '#e94560',
            'bg': '#1a1a2e',
            'text': '#ffffff',
            'text_secondary': '#a0a0a0',
            'success': '#00d26a',
            'card_bg': '#16213e'
        }
        
        self.style.configure('TFrame', background=self.colors['bg'])
        self.style.configure('Card.TFrame', background=self.colors['card_bg'])
        self.style.configure('TLabel', font=('Segoe UI', 10), background=self.colors['bg'], foreground=self.colors['text'])
        self.style.configure('Title.TLabel', font=('Segoe UI', 11, 'bold'), background=self.colors['card_bg'], foreground=self.colors['text'])
        self.style.configure('TButton', font=('Segoe UI', 10, 'bold'), padding=12)
        self.style.configure('Accent.TButton', font=('Segoe UI', 11, 'bold'), padding=14)
        self.style.configure('TCombobox', font=('Segoe UI', 10))
        self.style.configure('TLabelframe', background=self.colors['card_bg'], foreground=self.colors['text'])
        self.style.configure('TLabelframe.Label', background=self.colors['card_bg'], foreground=self.colors['text'], font=('Segoe UI', 10, 'bold'))
        
    def create_widgets(self):
        # Başlık çerçevesi
        header_frame = tk.Frame(self.root, bg=self.colors['primary'], height=100)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame, 
            text="METİN ASİSTANI", 
            font=('Segoe UI', 24, 'bold'),
            bg=self.colors['primary'], 
            fg='white'
        )
        title_label.pack(pady=(20, 5))
        
        subtitle_label = tk.Label(
            header_frame,
            text="Profesyonel Ses Tanıma Sistemi",
            font=('Segoe UI', 11),
            bg=self.colors['primary'],
            fg='#a0c4ff'
        )
        subtitle_label.pack()
        
        # Ana içerik çerçevesi
        main_frame = tk.Frame(self.root, bg=self.colors['bg'], padx=25, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # Ayarlar çerçevesi
        settings_frame = tk.LabelFrame(
            main_frame, 
            text="  ⚙️ AYARLAR  ", 
            font=('Segoe UI', 10, 'bold'),
            bg=self.colors['card_bg'], 
            fg=self.colors['text'],
            padx=15,
            pady=10
        )
        settings_frame.pack(fill='x', pady=(0, 15))
        
        # Kalite seçimi
        quality_frame = tk.Frame(settings_frame, bg=self.colors['card_bg'])
        quality_frame.pack(fill='x', pady=5)
        
        tk.Label(
            quality_frame, 
            text="Kalite:", 
            font=('Segoe UI', 10, 'bold'),
            bg=self.colors['card_bg'], 
            fg=self.colors['text']
        ).pack(side='left', padx=(0, 10))
        
        self.quality_var = tk.StringVar(value="Dengeli")
        quality_combo = ttk.Combobox(
            quality_frame, 
            textvariable=self.quality_var,
            values=list(QUALITY_OPTIONS.keys()),
            state='readonly',
            width=15,
            font=('Segoe UI', 10)
        )
        quality_combo.pack(side='left')
        quality_combo.bind('<<ComboboxSelected>>', self.on_quality_change)
        
        self.quality_desc = tk.Label(
            quality_frame,
            text="Dengeli hız ve kalite",
            font=('Segoe UI', 9),
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary']
        )
        self.quality_desc.pack(side='left', padx=15)
        
        # Butonlar çerçevesi
        buttons_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        buttons_frame.pack(fill='x', pady=15)
        
        # Kayıt başlat butonu
        self.record_btn = ttk.Button(
            buttons_frame,
            text="🎙️ Kayıt Başlat",
            command=self.toggle_recording,
            style='Record.TButton'
        )
        self.record_btn.pack(side='left', expand=True, fill='x', padx=(0, 5))
        
        # Dosya yükle butonu
        self.file_btn = ttk.Button(
            buttons_frame,
            text="📁 Dosya Yükle",
            command=self.load_file
        )
        self.file_btn.pack(side='left', expand=True, fill='x', padx=5)
        
        # Temizle butonu
        self.clear_btn = ttk.Button(
            buttons_frame,
            text="🗑️ Temizle",
            command=self.clear_text
        )
        self.clear_btn.pack(side='left', expand=True, fill='x', padx=(5, 0))
        
        # Durum etiketi
        self.status_var = tk.StringVar(value="✅ Hazır")
        self.status_label = tk.Label(
            main_frame, 
            textvariable=self.status_var, 
            font=('Segoe UI', 10),
            bg=self.colors['bg'],
            fg=self.colors['success']
        )
        self.status_label.pack(pady=8)
        
        # İlerleme çubuğu
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate', length=300)
        self.progress.pack(fill='x', pady=5)
        
        # Sonuç çerçevesi
        result_frame = tk.LabelFrame(
            main_frame, 
            text="  📄 DÖNÜŞTÜRÜLEN METİN  ", 
            font=('Segoe UI', 10, 'bold'),
            bg=self.colors['card_bg'],
            fg=self.colors['text'],
            padx=10,
            pady=10
        )
        result_frame.pack(fill='both', expand=True, pady=(15, 0))
        
        # Metin alanı
        text_frame = tk.Frame(result_frame, bg=self.colors['card_bg'])
        text_frame.pack(fill='both', expand=True)
        
        self.result_text = tk.Text(
            text_frame,
            wrap='word',
            font=('Consolas', 11),
            bg='#0d1117',
            fg='#e6edf3',
            relief='flat',
            padx=15,
            pady=15,
            state='disabled',
            insertbackground='white'
        )
        self.result_text.pack(side='left', fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame, orient='vertical', command=self.result_text.yview)
        scrollbar.pack(side='right', fill='y')
        self.result_text.configure(yscrollcommand=scrollbar.set)
        
        # Alt butonlar
        bottom_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        bottom_frame.pack(fill='x', pady=(15, 0))
        
        self.copy_btn = ttk.Button(
            bottom_frame,
            text="📋 Kopyala",
            command=self.copy_text
        )
        self.copy_btn.pack(side='left', padx=(0, 10))
        
        self.save_btn = ttk.Button(
            bottom_frame,
            text="💾 Kaydet",
            command=self.save_text
        )
        self.save_btn.pack(side='left')
        
        # Footer - Geliştirici bilgisi
        footer_frame = tk.Frame(self.root, bg=self.colors['secondary'], height=40)
        footer_frame.pack(fill='x', side='bottom')
        footer_frame.pack_propagate(False)
        
        footer_label = tk.Label(
            footer_frame,
            text="Bu uygulamayı Ahmet Birhat Okumuş geliştirdi.",
            font=('Segoe UI', 9),
            bg=self.colors['secondary'],
            fg=self.colors['text_secondary']
        )
        footer_label.pack(expand=True)
        
    def on_quality_change(self, event=None):
        """Kalite seçimi değiştiğinde"""
        quality = self.quality_var.get()
        desc = QUALITY_OPTIONS[quality]["description"]
        self.quality_desc.configure(text=desc)
    
    def transcribe_with_groq(self, audio_path):
        """Groq Whisper API ile ses tanıma"""
        quality = self.quality_var.get()
        model = QUALITY_OPTIONS[quality]["model"]
        
        with open(audio_path, "rb") as audio_file:
            transcription = self.groq_client.audio.transcriptions.create(
                file=(os.path.basename(audio_path), audio_file.read()),
                model=model,
                language="tr",
                response_format="text",
                prompt="Bu bir Türkçe konuşmadır. Türkçe teknik terimler, inşaat, mühendislik, günlük konuşma içerir. Logar kapağı, rögar, beton, demir, kalıp, şantiye, inşaat, yapı, bina gibi terimler olabilir."
            )
        return transcription
    
    def reduce_noise(self, audio, sample_rate):
        """Gürültü azaltma"""
        try:
            reduced_audio = nr.reduce_noise(y=audio, sr=sample_rate, prop_decrease=0.8)
            return reduced_audio
        except Exception as e:
            print(f"Gürültü azaltma hatası: {e}")
            return audio
    
    def audio_callback(self, indata, frames, time, status):
        """Ses verisi geldiğinde çağrılır"""
        if status:
            print(f"Ses hatası: {status}")
        self.audio_data.append(indata.copy())
    
    def toggle_recording(self):
        """Kayıt başlat/durdur"""
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self):
        """Kayıt başlat"""
        self.is_recording = True
        self.audio_data = []
        self.record_btn.configure(text="⏹️ Kayıt Durdur")
        self.file_btn.configure(state='disabled')
        self.clear_btn.configure(state='disabled')
        self.status_var.set("🎙️ Kayıt yapılıyor... Durdurmak için butona tıklayın")
        self.progress.start()
        
        # Ses akışını başlat
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype='float32',
            callback=self.audio_callback
        )
        self.stream.start()
    
    def stop_recording(self):
        """Kayıt durdur ve işle"""
        self.is_recording = False
        self.record_btn.configure(text="🎙️ Kayıt Başlat", state='disabled')
        
        # Ses akışını durdur
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        
        # Ayrı thread'de işle
        thread = threading.Thread(target=self.process_recording)
        thread.start()
    
    def process_recording(self):
        """Kaydedilen sesi işle"""
        try:
            # Ses verisini birleştir
            if not self.audio_data:
                self.status_var.set("❌ Ses kaydı boş!")
                self.progress.stop()
                return
            
            audio = np.concatenate(self.audio_data, axis=0).flatten()
            
            # Gürültü azaltma
            self.status_var.set("🔇 Gürültü temizleniyor...")
            self.root.update()
            audio = self.reduce_noise(audio, self.sample_rate)
            
            # Geçici dosyaya kaydet
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                sf.write(tmp_file.name, audio, self.sample_rate)
                tmp_path = tmp_file.name
            
            # Groq Whisper API ile yazıya çevir
            self.status_var.set("📝 Ses yazıya dönüştürülüyor (Groq Whisper)...")
            self.root.update()
            transcription = self.transcribe_with_groq(tmp_path)
            
            # Geçici dosyayı sil
            os.unlink(tmp_path)
            
            # Groq LLM ile düzelt
            self.status_var.set("🔧 Metin düzeltiliyor...")
            self.root.update()
            transcription = self.correct_with_groq(transcription)
            
            # Sonucu göster
            self.result_text.configure(state='normal')
            self.result_text.delete('1.0', tk.END)
            self.result_text.insert('1.0', transcription)
            self.result_text.configure(state='disabled')
            
            self.status_var.set("✅ Dönüştürme tamamlandı!")
            self.progress.stop()
            
        except Exception as e:
            self.status_var.set(f"❌ Hata: {str(e)}")
            self.progress.stop()
            messagebox.showerror("Hata", str(e))
        
        finally:
            self.record_btn.configure(state='normal')
            self.file_btn.configure(state='normal')
            self.clear_btn.configure(state='normal')
    
    def load_file(self):
        """Ses dosyası yükle"""
        file_path = filedialog.askopenfilename(
            title="Ses Dosyası Seç",
            filetypes=[
                ("Ses Dosyaları", "*.wav *.mp3 *.m4a *.ogg *.flac"),
                ("WAV", "*.wav"),
                ("MP3", "*.mp3"),
                ("M4A", "*.m4a"),
                ("OGG", "*.ogg"),
                ("FLAC", "*.flac"),
                ("Tüm Dosyalar", "*.*")
            ]
        )
        
        if file_path:
            self.record_btn.configure(state='disabled')
            self.file_btn.configure(state='disabled')
            
            thread = threading.Thread(target=self.transcribe_file, args=(file_path,))
            thread.start()
    
    def transcribe_file(self, file_path):
        """Dosyayı yazıya çevir"""
        try:
            self.progress.start()
            
            # Groq Whisper API ile yazıya çevir (dosyayı direkt gönder)
            self.status_var.set("📝 Ses yazıya dönüştürülüyor...")
            self.root.update()
            transcription = self.transcribe_with_groq(file_path)
            
            # Groq LLM ile düzelt
            self.status_var.set("🔧 Metin düzeltiliyor...")
            self.root.update()
            transcription = self.correct_with_groq(transcription)
            
            # Sonucu göster
            self.result_text.configure(state='normal')
            self.result_text.delete('1.0', tk.END)
            self.result_text.insert('1.0', transcription)
            self.result_text.configure(state='disabled')
            
            self.status_var.set("✅ Dönüştürme tamamlandı!")
            self.progress.stop()
            
        except Exception as e:
            self.status_var.set(f"❌ Hata: {str(e)}")
            self.progress.stop()
            messagebox.showerror("Hata", str(e))
        
        finally:
            self.record_btn.configure(state='normal')
            self.file_btn.configure(state='normal')
    
    def copy_text(self):
        """Metni panoya kopyala"""
        text = self.result_text.get('1.0', tk.END).strip()
        if text:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.status_var.set("📋 Metin panoya kopyalandı!")
        else:
            messagebox.showwarning("Uyarı", "Kopyalanacak metin yok!")
    
    def save_text(self):
        """Metni dosyaya kaydet"""
        text = self.result_text.get('1.0', tk.END).strip()
        if not text:
            messagebox.showwarning("Uyarı", "Kaydedilecek metin yok!")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Metni Kaydet",
            defaultextension=".txt",
            filetypes=[("Metin Dosyası", "*.txt"), ("Tüm Dosyalar", "*.*")]
        )
        
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(text)
            self.status_var.set(f"💾 Dosya kaydedildi: {os.path.basename(file_path)}")
    
    def clear_text(self):
        """Metin alanını temizle"""
        self.result_text.configure(state='normal')
        self.result_text.delete('1.0', tk.END)
        self.result_text.configure(state='disabled')
        self.status_var.set("Hazır")
    
    def correct_with_groq(self, text):
        """Groq API ile metni düzelt"""
        try:
            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": """Sen bir Türkçe ses tanıma düzeltme uzmanısın. Görevin:

1. Ses tanıma hatalarını düzelt (yanlış duyulan kelimeler)
2. Fonetik benzerliklerden DOĞRU kelimeyi tahmin et:
   - "roket" -> "rögar" veya "logar" (inşaat terimi)
   - "logar kapağı" -> "logar kapağı" (doğru)
   - "rögar" -> "rögar" (kanalizasyon kapağı)
3. Türkçe teknik terimleri tanı:
   - İnşaat: logar, rögar, beton, demir, kalıp, şantiye, temel, kolon, kiriş
   - Araç: motor, şanzıman, fren, debriyaj, rot, balans
4. Cümle bağlamına göre mantıklı düzeltme yap
5. Anlamsız kelimeler varsa bağlama uygun Türkçe kelimeyle değiştir

SADECE düzeltilmiş metni döndür. Açıklama ekleme. Orijinal anlamı koru."""
                    },
                    {
                        "role": "user",
                        "content": f"Bu ses tanıma çıktısını düzelt:\n\n{text}"
                    }
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.1,
                max_tokens=2048
            )
            return chat_completion.choices[0].message.content.strip()
        except Exception as e:
            print(f"Groq hatası: {e}")
            return text


if __name__ == "__main__":
    root = tk.Tk()
    app = MetinAsistani(root)
    root.mainloop()
