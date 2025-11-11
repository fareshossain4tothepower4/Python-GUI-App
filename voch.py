import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
from datetime import datetime

try:
    import sounddevice as sd
    import soundfile as sf
    import numpy as np
    from scipy import signal
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False

class VoiceEffectsStudio:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice Effects Studio - 50+ Voices")
        self.root.geometry("1100x800")
        self.root.configure(bg="#1a1a2e")
        
        if not AUDIO_AVAILABLE:
            self.show_installation_guide()
            return
        
        self.audio_data = None
        self.sample_rate = None
        self.output_path = os.path.join(os.path.expanduser("~"), "Downloads", "VoiceEffects")
        self.is_recording = False
        self.is_playing = False
        self.recording_data = []
        
        os.makedirs(self.output_path, exist_ok=True)
        
        # Define voice presets
        self.voice_presets = {
            "Masculine Deep Voices": [
                ("Smooth Baritone", {"pitch": 0.75, "bass": 1.5, "reverb": 0.2}),
                ("Heavy Bass", {"pitch": 0.7, "bass": 2.0, "reverb": 0.1}),
                ("Radio Announcer", {"pitch": 0.85, "bass": 1.3, "bandpass": (300, 3000)}),
                ("News Anchor", {"pitch": 0.9, "bass": 1.2, "clarity": 1.5}),
                ("Documentary Narrator", {"pitch": 0.8, "bass": 1.4, "reverb": 0.3}),
                ("Movie Trailer", {"pitch": 0.65, "bass": 2.5, "reverb": 0.4, "dramatic": True}),
                ("Motivational Speaker", {"pitch": 0.85, "bass": 1.6, "energy": 1.2}),
                ("Jazz Singer", {"pitch": 0.8, "bass": 1.3, "warmth": 1.4}),
            ],
            "Character Archetypes": [
                ("Wise Elder", {"pitch": 0.75, "raspy": 0.3, "reverb": 0.25}),
                ("Military Commander", {"pitch": 0.8, "bass": 1.5, "authority": 1.3}),
                ("Action Hero", {"pitch": 0.85, "bass": 1.4, "grit": 1.2}),
                ("Detective Noir", {"pitch": 0.78, "bass": 1.3, "smoky": 1.4}),
                ("Space Captain", {"pitch": 0.82, "bass": 1.2, "reverb": 0.3}),
                ("Medieval Knight", {"pitch": 0.77, "bass": 1.6, "echo": 0.4}),
                ("Pirate Captain", {"pitch": 0.8, "raspy": 0.4, "grit": 1.3}),
                ("Wild West Sheriff", {"pitch": 0.83, "bass": 1.3, "drawl": 1.2}),
            ],
            "Professional Voices": [
                ("Corporate CEO", {"pitch": 0.88, "bass": 1.2, "authority": 1.4}),
                ("Sports Commentator", {"pitch": 0.95, "energy": 1.5, "clarity": 1.3}),
                ("Game Show Host", {"pitch": 1.0, "energy": 1.6, "brightness": 1.2}),
                ("Podcast Host", {"pitch": 0.9, "bass": 1.1, "warmth": 1.3}),
                ("Audio Book Narrator", {"pitch": 0.85, "bass": 1.2, "clarity": 1.5}),
                ("Voice Actor", {"pitch": 0.9, "versatile": 1.0}),
                ("Radio DJ", {"pitch": 0.88, "bass": 1.4, "energy": 1.3}),
                ("Meditation Guide", {"pitch": 0.75, "bass": 1.1, "soothing": 1.5}),
            ],
            "Dramatic Styles": [
                ("Shakespearean", {"pitch": 0.82, "bass": 1.3, "theatrical": 1.4}),
                ("Opera Singer", {"pitch": 0.8, "bass": 1.5, "reverb": 0.5}),
                ("Stage Actor", {"pitch": 0.88, "projection": 1.4, "clarity": 1.3}),
                ("Poetry Reader", {"pitch": 0.85, "bass": 1.2, "lyrical": 1.3}),
                ("Orator", {"pitch": 0.87, "bass": 1.3, "authority": 1.5}),
            ],
            "Modern Styles": [
                ("Hip Hop Vocal", {"pitch": 0.85, "bass": 1.8, "punch": 1.4}),
                ("Rock Vocalist", {"pitch": 0.9, "grit": 1.5, "power": 1.4}),
                ("Blues Singer", {"pitch": 0.78, "raspy": 0.4, "soulful": 1.4}),
                ("Country Singer", {"pitch": 0.88, "warmth": 1.3, "twang": 1.2}),
                ("R&B Smooth", {"pitch": 0.82, "bass": 1.4, "silky": 1.3}),
            ],
            "Fun & Creative": [
                ("Robot", {"pitch": 1.0, "robotic": True}),
                ("Chipmunk", {"pitch": 1.6, "speed": 1.2}),
                ("Monster", {"pitch": 0.5, "bass": 3.0, "distortion": 1.5}),
                ("Alien", {"pitch": 1.2, "weird": True, "reverb": 0.3}),
                ("Cave Troll", {"pitch": 0.55, "bass": 2.5, "echo": 0.6}),
                ("Telephone", {"pitch": 1.0, "bandpass": (300, 3400)}),
                ("Underwater", {"pitch": 0.8, "muffled": True}),
                ("Stadium Announcer", {"pitch": 0.9, "echo": 0.4, "large_space": True}),
                ("Whisper", {"pitch": 0.9, "volume": 0.3, "intimate": True}),
                ("Megaphone", {"pitch": 1.0, "bandpass": (400, 4000), "distortion": 0.5}),
            ],
            "Atmospheric": [
                ("Haunted House", {"pitch": 0.7, "reverb": 0.6, "spooky": True}),
                ("Cathedral", {"pitch": 0.85, "reverb": 0.7, "holy": True}),
                ("Small Room", {"pitch": 1.0, "reverb": 0.1}),
                ("Concert Hall", {"pitch": 0.9, "reverb": 0.5, "spacious": True}),
                ("Forest Echo", {"pitch": 0.88, "echo": 0.5, "nature": True}),
            ]
        }
        
        self.create_widgets()
    
    def show_installation_guide(self):
        frame = tk.Frame(self.root, bg="#1a1a2e")
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(frame, text="⚠️ Required Packages Not Installed", 
                font=("Papyrus", 16, "bold"), bg="#1a1a2e", fg="#ff6b6b").pack(pady=20)
        
        tk.Label(frame, text="Please run these commands:", 
                font=("Papyrus", 11), bg="#1a1a2e", fg="#feca57").pack(pady=10)
        
        cmd_frame = tk.Frame(frame, bg="#0f3460", relief=tk.RIDGE, bd=2)
        cmd_frame.pack(pady=10, padx=20, fill=tk.X)
        
        cmd_text = tk.Text(cmd_frame, height=2, font=("Courier", 10), bg="#0f3460", 
                          fg="#00ff00", bd=0, wrap=tk.WORD)
        cmd_text.pack(padx=10, pady=10, fill=tk.X)
        cmd_text.insert("1.0", "pip install sounddevice soundfile numpy scipy")
        cmd_text.config(state=tk.DISABLED)
        
        tk.Button(frame, text="Close", command=self.root.quit,
                 bg="#ff6b6b", fg="white", font=("Papyrus", 11, "bold"),
                 padx=30, pady=10, relief=tk.FLAT).pack(pady=20)
    
    def create_widgets(self):
        # Header
        header = tk.Frame(self.root, bg="#16213e", height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="🎤 Voice Effects Studio - 50+ Character Voices", 
                font=("Papyrus", 20, "bold"), bg="#16213e", fg="#00d9ff").pack(pady=8)
        tk.Label(header, text="Transform your voice into any character style", 
                font=("Papyrus", 9), bg="#16213e", fg="#95afc0").pack()
        
        # Main container
        main_container = tk.Frame(self.root, bg="#1a1a2e")
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Left panel - Input controls
        left_panel = tk.Frame(main_container, bg="#0f3460", relief=tk.RAISED, bd=2, width=280)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Recording section
        record_frame = tk.LabelFrame(left_panel, text="  Audio Input  ", 
                                     font=("Papyrus", 11, "bold"), bg="#0f3460", 
                                     fg="#00d9ff", relief=tk.FLAT)
        record_frame.pack(fill=tk.X, padx=10, pady=10)
        
        rec_inner = tk.Frame(record_frame, bg="#0f3460")
        rec_inner.pack(fill=tk.X, padx=8, pady=8)
        
        self.record_btn = tk.Button(rec_inner, text="🎙️ Record", 
                                    command=self.toggle_recording,
                                    bg="#ff6b6b", fg="white", 
                                    font=("Papyrus", 10, "bold"),
                                    relief=tk.FLAT, padx=15, pady=8)
        self.record_btn.pack(fill=tk.X, pady=3)
        
        tk.Button(rec_inner, text="📁 Load File", 
                 command=self.load_audio,
                 bg="#48dbfb", fg="white", 
                 font=("Papyrus", 10, "bold"),
                 relief=tk.FLAT, padx=15, pady=8).pack(fill=tk.X, pady=3)
        
        self.record_status = tk.Label(rec_inner, text="Ready", 
                                      font=("Papyrus", 8), bg="#0f3460", 
                                      fg="#feca57")
        self.record_status.pack(pady=3)
        
        # Playback controls
        play_frame = tk.LabelFrame(left_panel, text="  Playback  ", 
                                  font=("Papyrus", 11, "bold"), bg="#0f3460", 
                                  fg="#00d9ff", relief=tk.FLAT)
        play_frame.pack(fill=tk.X, padx=10, pady=10)
        
        play_inner = tk.Frame(play_frame, bg="#0f3460")
        play_inner.pack(fill=tk.X, padx=8, pady=8)
        
        self.play_btn = tk.Button(play_inner, text="▶️ Original", 
                                  command=lambda: self.play_audio("original"),
                                  bg="#00d9ff", fg="#1a1a2e", 
                                  font=("Papyrus", 9, "bold"),
                                  relief=tk.FLAT, padx=12, pady=6,
                                  state=tk.DISABLED)
        self.play_btn.pack(fill=tk.X, pady=2)
        
        self.play_effect_btn = tk.Button(play_inner, text="▶️ With Effect", 
                                        command=lambda: self.play_audio("effect"),
                                        bg="#00d9ff", fg="#1a1a2e", 
                                        font=("Papyrus", 9, "bold"),
                                        relief=tk.FLAT, padx=12, pady=6,
                                        state=tk.DISABLED)
        self.play_effect_btn.pack(fill=tk.X, pady=2)
        
        self.stop_btn = tk.Button(play_inner, text="⏹️ Stop", 
                                 command=self.stop_audio,
                                 bg="#ff6b6b", fg="white", 
                                 font=("Papyrus", 9, "bold"),
                                 relief=tk.FLAT, padx=12, pady=6,
                                 state=tk.DISABLED)
        self.stop_btn.pack(fill=tk.X, pady=2)
        
        # Export section
        export_frame = tk.LabelFrame(left_panel, text="  Export  ", 
                                    font=("Papyrus", 11, "bold"), bg="#0f3460", 
                                    fg="#00d9ff", relief=tk.FLAT)
        export_frame.pack(fill=tk.X, padx=10, pady=10)
        
        export_inner = tk.Frame(export_frame, bg="#0f3460")
        export_inner.pack(fill=tk.X, padx=8, pady=8)
        
        self.export_btn = tk.Button(export_inner, text="💾 Save WAV", 
                                    command=self.export_audio,
                                    bg="#4CAF50", fg="white", 
                                    font=("Papyrus", 9, "bold"),
                                    relief=tk.FLAT, padx=12, pady=6,
                                    state=tk.DISABLED)
        self.export_btn.pack(fill=tk.X)
        
        # Audio info
        info_frame = tk.Frame(left_panel, bg="#1a1a2e", relief=tk.RIDGE, bd=2)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.info_label = tk.Label(info_frame, text="No audio loaded\n\nRecord or load\nan audio file", 
                                   font=("Papyrus", 9), bg="#1a1a2e", 
                                   fg="#feca57", justify=tk.CENTER)
        self.info_label.pack(expand=True, pady=20)
        
        # Center panel - Voice presets in scrollable area
        center_panel = tk.Frame(main_container, bg="#0f3460", relief=tk.RAISED, bd=2)
        center_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Header
        preset_header = tk.Frame(center_panel, bg="#0f3460")
        preset_header.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(preset_header, text="🎭 Voice Presets", 
                font=("Papyrus", 12, "bold"), bg="#0f3460", fg="#00d9ff").pack(side=tk.LEFT)
        
        tk.Label(preset_header, text="Click any voice style to apply", 
                font=("Papyrus", 8), bg="#0f3460", fg="#95afc0").pack(side=tk.RIGHT)
        
        # Scrollable canvas
        canvas_frame = tk.Frame(center_panel, bg="#0f3460")
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        canvas = tk.Canvas(canvas_frame, bg="#1a1a2e", highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#1a1a2e")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add voice preset buttons
        for category, voices in self.voice_presets.items():
            cat_frame = tk.LabelFrame(scrollable_frame, text=f"  {category}  ", 
                                     font=("Papyrus", 10, "bold"), bg="#1a1a2e", 
                                     fg="#00d9ff", relief=tk.FLAT)
            cat_frame.pack(fill=tk.X, padx=10, pady=8)
            
            btn_container = tk.Frame(cat_frame, bg="#1a1a2e")
            btn_container.pack(fill=tk.X, padx=8, pady=8)
            
            for voice_name, params in voices:
                btn = tk.Button(btn_container, text=voice_name,
                               command=lambda n=voice_name, p=params: self.apply_preset(n, p),
                               bg="#2d3561", fg="white", 
                               font=("Papyrus", 9),
                               relief=tk.FLAT, padx=15, pady=6,
                               cursor="hand2", anchor=tk.W)
                btn.pack(fill=tk.X, pady=2)
                btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#00d9ff", fg="#1a1a2e"))
                btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#2d3561", fg="white"))
        
        # Right panel - Custom controls
        right_panel = tk.Frame(main_container, bg="#0f3460", relief=tk.RAISED, bd=2, width=260)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y)
        right_panel.pack_propagate(False)
        
        tk.Label(right_panel, text="⚙️ Custom Adjustments", 
                font=("Papyrus", 11, "bold"), bg="#0f3460", fg="#00d9ff").pack(pady=10)
        
        custom_frame = tk.Frame(right_panel, bg="#0f3460")
        custom_frame.pack(fill=tk.BOTH, expand=True, padx=10)
        
        # Pitch
        self.add_slider(custom_frame, "Pitch:", 0.5, 2.0, 1.0, "pitch_var")
        tk.Label(custom_frame, text="(Lower = Deeper)", font=("Papyrus", 7), 
                bg="#0f3460", fg="#95afc0").pack(pady=(0, 10))
        
        # Bass
        self.add_slider(custom_frame, "Bass Boost:", 0.5, 3.0, 1.0, "bass_var")
        tk.Label(custom_frame, text="(Higher = More Bass)", font=("Papyrus", 7), 
                bg="#0f3460", fg="#95afc0").pack(pady=(0, 10))
        
        # Reverb
        self.add_slider(custom_frame, "Reverb:", 0.0, 1.0, 0.0, "reverb_var")
        tk.Label(custom_frame, text="(Space/Echo Effect)", font=("Papyrus", 7), 
                bg="#0f3460", fg="#95afc0").pack(pady=(0, 10))
        
        # Speed
        self.add_slider(custom_frame, "Speed:", 0.5, 2.0, 1.0, "speed_var")
        tk.Label(custom_frame, text="(Playback Speed)", font=("Papyrus", 7), 
                bg="#0f3460", fg="#95afc0").pack(pady=(0, 10))
        
        # Distortion
        self.add_slider(custom_frame, "Grit/Rasp:", 0.0, 2.0, 0.0, "grit_var")
        tk.Label(custom_frame, text="(Voice Roughness)", font=("Papyrus", 7), 
                bg="#0f3460", fg="#95afc0").pack(pady=(0, 20))
        
        tk.Button(custom_frame, text="Apply Custom Settings", 
                 command=self.apply_custom,
                 bg="#e17055", fg="white", font=("Papyrus", 10, "bold"),
                 relief=tk.FLAT, padx=15, pady=10).pack(fill=tk.X)
        
        tk.Button(custom_frame, text="Reset to Default", 
                 command=self.reset_sliders,
                 bg="#636e72", fg="white", font=("Papyrus", 9),
                 relief=tk.FLAT, padx=15, pady=8).pack(fill=tk.X, pady=(5, 0))
        
        # Status bar
        status_bar = tk.Frame(self.root, bg="#16213e", height=28)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        status_bar.pack_propagate(False)
        
        self.status_label = tk.Label(status_bar, text="Ready - Load or record audio to begin", 
                                     font=("Papyrus", 9), bg="#16213e", 
                                     fg="#95afc0", anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        self.current_effect_label = tk.Label(status_bar, text="Effect: None", 
                                            font=("Papyrus", 9), bg="#16213e", 
                                            fg="#feca57", anchor=tk.E)
        self.current_effect_label.pack(side=tk.RIGHT, padx=10)
    
    def add_slider(self, parent, label, from_, to, default, var_name):
        tk.Label(parent, text=label, font=("Papyrus", 9, "bold"), 
                bg="#0f3460", fg="white").pack(anchor=tk.W, pady=(5, 2))
        
        var = tk.DoubleVar(value=default)
        setattr(self, var_name, var)
        
        slider = tk.Scale(parent, from_=from_, to=to, resolution=0.1,
                         variable=var, orient=tk.HORIZONTAL,
                         bg="#0f3460", fg="white", font=("Papyrus", 8),
                         highlightthickness=0, troughcolor="#1a1a2e",
                         showvalue=True)
        slider.pack(fill=tk.X, padx=5)
    
    def reset_sliders(self):
        self.pitch_var.set(1.0)
        self.bass_var.set(1.0)
        self.reverb_var.set(0.0)
        self.speed_var.set(1.0)
        self.grit_var.set(0.0)
        self.status_label.config(text="Sliders reset to default")
    
    def toggle_recording(self):
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self):
        self.is_recording = True
        self.recording_data = []
        self.record_btn.config(text="⏹️ Stop", bg="#4CAF50")
        self.record_status.config(text="Recording...")
        self.status_label.config(text="Recording... Speak now!")
        
        def record_callback(indata, frames, time, status):
            if self.is_recording:
                self.recording_data.append(indata.copy())
        
        self.stream = sd.InputStream(callback=record_callback, channels=1, 
                                     samplerate=44100, dtype='float32')
        self.stream.start()
    
    def stop_recording(self):
        if self.is_recording:
            self.is_recording = False
            self.stream.stop()
            self.stream.close()
            
            if self.recording_data:
                self.audio_data = np.concatenate(self.recording_data, axis=0).flatten()
                self.sample_rate = 44100
                self.on_audio_loaded()
            
            self.record_btn.config(text="🎙️ Record", bg="#ff6b6b")
            self.record_status.config(text="Recording stopped")
    
    def load_audio(self):
        filename = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=[("Audio Files", "*.wav *.mp3 *.flac *.ogg"), ("All Files", "*.*")]
        )
        
        if filename:
            try:
                self.audio_data, self.sample_rate = sf.read(filename)
                if len(self.audio_data.shape) > 1:
                    self.audio_data = self.audio_data.mean(axis=1)
                self.on_audio_loaded()
                self.status_label.config(text=f"Loaded: {os.path.basename(filename)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load audio:\n{str(e)}")
    
    def on_audio_loaded(self):
        duration = len(self.audio_data) / self.sample_rate
        self.info_label.config(text=f"✓ Audio Loaded\n\nDuration:\n{duration:.2f}s\n\nSample Rate:\n{self.sample_rate} Hz")
        self.play_btn.config(state=tk.NORMAL)
        self.export_btn.config(state=tk.NORMAL)
        self.record_status.config(text="Ready!")
        
        self.original_audio = self.audio_data.copy()
        self.processed_audio = None
    
    def apply_preset(self, name, params):
        if self.audio_data is None:
            messagebox.showwarning("No Audio", "Please load or record audio first")
            return
        
        try:
            audio = self.original_audio.copy()
            
            # Apply effects based on parameters
            pitch = params.get("pitch", 1.0)
            bass = params.get("bass", 1.0)
            reverb = params.get("reverb", 0.0)
            
            if pitch != 1.0:
                audio = self.change_pitch(audio, pitch)
            
            if bass > 1.0:
                audio = self.bass_boost(audio, bass)
            
            if "bandpass" in params:
                low, high = params["bandpass"]
                audio = self.bandpass_filter(audio, low, high)
            
            if reverb > 0:
                audio = self.add_reverb(audio, reverb)
            
            if params.get("robotic"):
                audio = self.robot_effect(audio)
            
            if params.get("raspy", 0) > 0:
                audio = self.add_rasp(audio, params["raspy"])
            
            if params.get("distortion", 0) > 0:
                audio = self.add_distortion(audio, params["distortion"])
            
            # Normalize
            audio = audio / (np.max(np.abs(audio)) + 0.0001)
            
            self.processed_audio = audio
            self.play_effect_btn.config(state=tk.NORMAL)
            self.current_effect_label.config(text=f"Effect: {name}")
            self.status_label.config(text=f"Applied: {name}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply effect:\n{str(e)}")
    
    def apply_custom(self):
        if self.audio_data is None:
            messagebox.showwarning("No Audio", "Please load or record audio first")
            return
        
        try:
            audio = self.original_audio.copy()
            
            pitch = self.pitch_var.get()
            bass = self.bass_var.get()
            reverb = self.reverb_var.get()
            speed = self.speed_var.get()
            grit = self.grit_var.get()
            
            if pitch != 1.0:
                audio = self.change_pitch(audio, pitch)
            
            if bass > 1.0:
                audio = self.bass_boost(audio, bass)
            
            if reverb > 0:
                audio = self.add_reverb(audio, reverb)
            
            if speed != 1.0:
                audio = self.change_speed(audio, speed)
            
            if grit > 0:
                audio = self.add_rasp(audio, grit)
            
            audio = audio / (np.max(np.abs(audio)) + 0.0001)
            
            self.processed_audio = audio
            self.play_effect_btn.config(state=tk.NORMAL)
            self.current_effect_label.config(text=f"Effect: Custom")
            self.status_label.config(text="Applied custom settings")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply effect:\n{str(e)}")
    
    def change_pitch(self, audio, factor):
        indices = np.round(np.arange(0, len(audio), factor))
        indices = indices[indices < len(audio)].astype(int)
        return audio[indices]
    
    def change_speed(self, audio, factor):
        indices = np.round(np.arange(0, len(audio), factor))
        indices = indices[indices < len(audio)].astype(int)
        return audio[indices]
    
    def bass_boost(self, audio, factor):
        nyquist = self.sample_rate / 2
        cutoff = 200 / nyquist
        b, a = signal.butter(4, cutoff, btype='low')
        bass = signal.filtfilt(b, a, audio)
        return audio + bass * (factor - 1)
    
    def bandpass_filter(self, audio, lowcut, highcut):
        nyquist = self.sample_rate / 2
        low = lowcut / nyquist
        high = highcut / nyquist
        b, a = signal.butter(4, [low, high], btype='band')
        return signal.filtfilt(b, a, audio)
    
    def robot_effect(self, audio):
        carrier_freq = 30
        t = np.arange(len(audio)) / self.sample_rate
        carrier = np.sin(2 * np.pi * carrier_freq * t)
        return audio * carrier
    
    def add_reverb(self, audio, amount):
        delay_samples = int(0.05 * self.sample_rate)
        reverb = np.zeros(len(audio) + delay_samples)
        reverb[:len(audio)] = audio
        
        for i in range(3):
            delay = int((0.05 + i * 0.03) * self.sample_rate)
            decay = amount * (0.6 ** i)
            if len(audio) + delay <= len(reverb):
                reverb[delay:delay+len(audio)] += audio * decay
        
        return reverb[:len(audio)]
    
    def add_rasp(self, audio, amount):
        noise = np.random.normal(0, 0.05 * amount, len(audio))
        distorted = np.tanh(audio * (1 + amount))
        return audio * (1 - amount * 0.3) + distorted * amount * 0.3 + noise
    
    def add_distortion(self, audio, amount):
        return np.tanh(audio * (1 + amount * 2))
    
    def play_audio(self, audio_type):
        if self.is_playing:
            return
        
        if audio_type == "original":
            audio = self.original_audio
        elif audio_type == "effect" and self.processed_audio is not None:
            audio = self.processed_audio
        else:
            messagebox.showwarning("No Effect", "Apply an effect first")
            return
        
        self.is_playing = True
        self.stop_btn.config(state=tk.NORMAL)
        self.status_label.config(text="Playing audio...")
        
        def play():
            sd.play(audio, self.sample_rate)
            sd.wait()
            self.is_playing = False
            self.stop_btn.config(state=tk.DISABLED)
            self.status_label.config(text="Playback finished")
        
        import threading
        threading.Thread(target=play, daemon=True).start()
    
    def stop_audio(self):
        sd.stop()
        self.is_playing = False
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Playback stopped")
    
    def export_audio(self):
        if self.processed_audio is None:
            messagebox.showwarning("No Effect", "Apply an effect first before exporting")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"voice_effect_{timestamp}.wav"
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".wav",
            filetypes=[("WAV files", "*.wav")],
            initialfile=default_name,
            initialdir=self.output_path
        )
        
        if filename:
            try:
                sf.write(filename, self.processed_audio, self.sample_rate)
                messagebox.showinfo("Success", f"Audio saved to:\n{filename}")
                self.status_label.config(text=f"Exported: {os.path.basename(filename)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save audio:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = VoiceEffectsStudio(root)
    root.mainloop()