import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk
import os
import sys
import threading
import time
import ctypes


class SplashScreen:
    def __init__(self, main_app_callback):
        self.main_app_callback = main_app_callback
        self.splash_root = ctk.CTk()
        self.splash_root.title("CSER")
        
        # Configure splash window
        self.splash_root.overrideredirect(True)  # Remove window decorations
        
        # Get screen dimensions and center the splash
        screen_width = self.splash_root.winfo_screenwidth()
        screen_height = self.splash_root.winfo_screenheight()
        splash_width = 400
        splash_height = 300
        x = (screen_width - splash_width) // 2
        y = (screen_height - splash_height) // 2
        self.splash_root.geometry(f"{splash_width}x{splash_height}+{x}+{y}")
        
        # Don't force splash to be always on top to avoid minimizing other windows
        # self.splash_root.attributes('-topmost', True)
        
        # Set taskbar icon for splash screen
        self.set_splash_taskbar_icon()
        
        # Animation variables
        self.alpha = 0.0
        self.fade_step = 0.05
        self.loading_dots = 0
        
        self.create_splash_content()
        self.start_animations()
        
    def create_splash_content(self):
        """Create the splash screen content"""
        # Main container
        self.main_frame = ctk.CTkFrame(
            self.splash_root, 
            corner_radius=0,  # Dikdörtgen köşeler
            fg_color='#1a1a1a'
        )
        self.main_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Logo section
        self.logo_frame = ctk.CTkFrame(
            self.main_frame, 
            corner_radius=0,
            fg_color='transparent'
        )
        self.logo_frame.pack(expand=True, fill='both', padx=15, pady=15)
        
        try:
            # Load and display logo
            logo_path = os.path.join(os.path.dirname(__file__), "images", "cser-icon.png")
            if os.path.exists(logo_path):
                logo_image = Image.open(logo_path)
                
                # Set window icon with multiple sizes for better compatibility
                sizes = [(16, 16), (32, 32), (48, 48), (64, 64)]
                self.icon_photos = []
                
                for size in sizes:
                    resized_image = logo_image.resize(size, Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(resized_image)
                    self.icon_photos.append(photo)
                
                # Set as window icon
                self.splash_root.iconphoto(True, *self.icon_photos)
                
                # Also try Windows-specific icon setting
                try:
                    import tempfile
                    with tempfile.NamedTemporaryFile(suffix='.ico', delete=False) as temp_ico:
                        logo_image.save(temp_ico.name, format='ICO', sizes=[(16,16), (32,32), (48,48), (64,64)])
                        self.splash_root.wm_iconbitmap(temp_ico.name)
                        
                        # Clean up temp file after a delay
                        def cleanup_temp_file():
                            try:
                                import time
                                time.sleep(1)
                                os.unlink(temp_ico.name)
                            except:
                                pass
                        
                        import threading
                        threading.Thread(target=cleanup_temp_file, daemon=True).start()
                except:
                    pass  # Ignore ICO errors for splash screen
                
                # Display logo in splash screen
                logo_display = logo_image.resize((120, 120), Image.Resampling.LANCZOS)
                self.logo_photo = ImageTk.PhotoImage(logo_display)
                
                self.logo_label = ctk.CTkLabel(
                    self.logo_frame, 
                    image=self.logo_photo,
                    text=""
                )
                self.logo_label.pack(pady=(40, 10))
        except Exception as e:
            print(f"Splash logo yükleme hatası: {e}")
        
        # Title - using Consolas font to match code editor
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="cser()",
            font=ctk.CTkFont(family="Consolas", size=28, weight="bold"),
            text_color='#ffffff'
        )
        self.title_label.pack(pady=(0, 2))
        
        # Subtitle
        self.subtitle_label = ctk.CTkLabel(
            self.main_frame,
            text="AMX Mod X Code Editor",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color='#888888'
        )
        self.subtitle_label.pack(pady=(0, 20))
        
        # Loading section
        self.loading_frame = ctk.CTkFrame(
            self.main_frame, 
            corner_radius=0,
            fg_color='transparent'
        )
        self.loading_frame.pack(side='bottom', pady=(0, 20))
        
        # Loading text
        self.loading_label = ctk.CTkLabel(
            self.loading_frame,
            text="Yükleniyor",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color='#666666'
        )
        self.loading_label.pack()
        
        # Progress bar - using CustomTkinter progress bar
        self.progress_bar = ctk.CTkProgressBar(
            self.loading_frame,
            width=200,
            height=6,
            corner_radius=0,
            progress_color='#0078d4',
            fg_color='#333333'
        )
        self.progress_bar.pack(pady=(10, 0))
        self.progress_bar.set(0)  # Start at 0%
        
    def start_animations(self):
        """Start fade-in animation and loading sequence"""
        self.fade_in()
        self.animate_loading()
        
        # Start main app after 3 seconds
        threading.Timer(3.0, self.close_splash).start()
        
    def fade_in(self):
        """Fade in animation"""
        if self.alpha < 1.0:
            self.alpha += self.fade_step
            try:
                self.splash_root.attributes('-alpha', self.alpha)
            except:
                pass
            self.splash_root.after(50, self.fade_in)
            
    def animate_loading(self):
        """Animate loading text and progress bar"""
        # Animate loading dots
        self.loading_dots = (self.loading_dots + 1) % 4
        dots = "." * self.loading_dots
        self.loading_label.configure(text=f"Yükleniyor{dots}")
        
        # Animate progress bar
        current_time = time.time()
        if not hasattr(self, 'start_time'):
            self.start_time = current_time
        
        elapsed = current_time - self.start_time
        progress = min(elapsed / 3.0, 1.0)  # 3 seconds total
        self.progress_bar.set(progress)  # CustomTkinter progress bar uses 0.0 to 1.0
        
        if progress < 1.0:
            self.splash_root.after(100, self.animate_loading)
            
    def close_splash(self):
        """Close splash screen and start main app"""
        def fade_out():
            if self.alpha > 0:
                self.alpha -= self.fade_step * 2  # Faster fade out
                try:
                    self.splash_root.attributes('-alpha', self.alpha)
                    self.splash_root.after(30, fade_out)
                except:
                    self.splash_root.destroy()
                    self.main_app_callback()
            else:
                self.splash_root.destroy()
                self.main_app_callback()
        
        fade_out()
    
    def set_splash_taskbar_icon(self):
        """Set taskbar icon for splash screen using comprehensive approach"""
        try:
            if sys.platform == "win32":
                # Wait for window to be fully created and mapped
                self.splash_root.update_idletasks()
                self.splash_root.after(100, self._apply_splash_taskbar_icon)  # Delay to ensure window is fully ready
                
        except Exception as e:
            print(f"⚠ Splash taskbar ikon ayarlama hatası: {e}")
    
    def _apply_splash_taskbar_icon(self):
        """Apply taskbar icon for splash using comprehensive Windows approach"""
        try:
            ico_path = os.path.join(os.path.dirname(__file__), "images", "cser-icon.ico")
            if os.path.exists(ico_path):
                print(f"🔍 Splash ICO dosyası taskbar için kullanılıyor: {ico_path}")
                
                # STEP 1: Use Tkinter's built-in iconbitmap method first
                try:
                    self.splash_root.iconbitmap(ico_path)
                    print("✓ Splash Tkinter iconbitmap ayarlandı")
                except Exception as e:
                    print(f"⚠ Splash Tkinter iconbitmap hatası: {e}")
                
                # STEP 2: Set Application User Model ID to separate from Python
                try:
                    app_id = "CSER.SplashScreen.2024"
                    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
                    print("✓ Splash App User Model ID ayarlandı")
                except Exception as e:
                    print(f"⚠ Splash App User Model ID hatası: {e}")
                
                # STEP 3: Set window properties
                self.splash_root.title("CSER - Loading...")
                self.splash_root.wm_iconname("CSER")
                
                # STEP 4: Additional Windows API calls for taskbar
                try:
                    hwnd = self.splash_root.winfo_id()
                    
                    # Load multiple icon sizes for better compatibility
                    hicon_small = ctypes.windll.user32.LoadImageW(0, ico_path, 1, 16, 16, 0x00000010)
                    hicon_large = ctypes.windll.user32.LoadImageW(0, ico_path, 1, 32, 32, 0x00000010)
                    
                    if hicon_small and hicon_large:
                        # Set window icons
                        ctypes.windll.user32.SendMessageW(hwnd, 0x0080, 0, hicon_small)  # WM_SETICON, ICON_SMALL
                        ctypes.windll.user32.SendMessageW(hwnd, 0x0080, 1, hicon_large)  # WM_SETICON, ICON_BIG
                        
                        # Set class icons for taskbar persistence
                        try:
                            ctypes.windll.user32.SetClassLongPtrW(hwnd, -14, hicon_small)  # GCL_HICONSM
                            ctypes.windll.user32.SetClassLongPtrW(hwnd, -34, hicon_large)  # GCL_HICON
                        except:
                            # Fallback for 32-bit systems
                            ctypes.windll.user32.SetClassLongW(hwnd, -14, hicon_small)
                            ctypes.windll.user32.SetClassLongW(hwnd, -34, hicon_large)
                        
                        print("✓ Splash Windows API ikonları ayarlandı")
                        
                        # Force window update
                        ctypes.windll.user32.UpdateWindow(hwnd)
                        ctypes.windll.user32.RedrawWindow(hwnd, None, None, 0x0001 | 0x0004)
                        
                        # Notify shell of icon change
                        ctypes.windll.shell32.SHChangeNotify(0x08000000, 0x0000, None, None)
                        
                        print("✓ Splash taskbar ikonu başarıyla ayarlandı")
                        
                    else:
                        print("⚠ Splash ikon yüklenemedi")
                        
                except Exception as e:
                    print(f"⚠ Splash Windows API ikon hatası: {e}")
                    
            else:
                print("⚠ Splash ICO dosyası bulunamadı")
                
        except Exception as e:
            print(f"⚠ Splash taskbar ikon hatası: {e}")