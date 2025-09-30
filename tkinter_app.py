import customtkinter as ctk
import tkinter as tk
import tkinter.font as tkfont
from tkinter import filedialog, messagebox
import re
import sys
import os
import threading
import time
from tkinter import font as tkFont
from PIL import Image, ImageTk
import ctypes
from path_validator import PathValidator

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

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
                self.logo_label.pack(pady=(40, 20))
        except Exception as e:
            print(f"Splash logo yükleme hatası: {e}")
        
        # Title - using Consolas font to match code editor
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="cser()",
            font=ctk.CTkFont(family="Consolas", size=28, weight="bold"),
            text_color='#ffffff'
        )
        self.title_label.pack(pady=(0, 5))
        
        # Subtitle
        self.subtitle_label = ctk.CTkLabel(
            self.main_frame,
            text="AMX Mod X Code Editor",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color='#888888'
        )
        self.subtitle_label.pack(pady=(0, 30))
        
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

class CSERCodeEditor:
    def __init__(self):
        # CRITICAL: Set process-level icon BEFORE creating window
        self._set_process_icon()
        
        self.root = ctk.CTk()
        self.root.title("CSER - AMX Mod X Editor")
        self.root.geometry("1200x800")
        
        # CRITICAL: Set window icon IMMEDIATELY after creation
        self._set_early_icon()
        
        # Prevent the window from forcing itself to the front
        self.root.withdraw()  # Hide initially
        self.root.after(100, self._show_window_gently)  # Show after a brief delay
        

        
        # Load custom font
        self.load_custom_font()
        
        # Load application logo
        self.load_logo()
        
        # Create main layout
        self.create_main_layout()
        
        # Create editor section first
        self.create_editor_section()
        
        # Setup syntax highlighting after editor is created
        self.setup_syntax_highlighting()
        
        # Create compiler/counter section
        self.create_compiler_section()
        
        # Create button section
        self.create_button_section()
        
        # Initialize content
        self.on_content_changed()
        
        # Initialize path validator
        self.path_validator = PathValidator()
        
        # Color scheme for syntax highlighting
        self.colors = {
            'keyword': '#569cd6',      # Blue for keywords
            'string': '#ce9178',       # Orange for strings
            'comment': '#6a9955',      # Green for comments
            'number': '#b5cea8',       # Light green for numbers
            'function': '#dcdcaa',     # Yellow for functions
            'preprocessor': '#c586c0', # Purple for preprocessor
            'operator': '#d4d4d4',     # White for operators
            'bracket': '#ffd700',      # Gold for brackets
            'type': '#4ec9b0'          # Cyan for types
        }
    
    def _set_process_icon(self):
        """Set process-level icon before window creation"""
        try:
            import ctypes
            from ctypes import wintypes
            
            # Get the icon file path
            icon_path = os.path.join(os.path.dirname(__file__), "images", "cser-icon.ico")
            if not os.path.exists(icon_path):
                print(f"Icon file not found: {icon_path}")
                return
            
            # Load the icon using Windows API
            user32 = ctypes.windll.user32
            kernel32 = ctypes.windll.kernel32
            shell32 = ctypes.windll.shell32
            
            # Set App User Model ID FIRST (critical for taskbar recognition)
            try:
                shell32.SetCurrentProcessExplicitAppUserModelID("CSER.AMXModXEditor.1.0")
                print("Process App User Model ID set")
            except Exception as e:
                print(f"Process App User Model ID failed: {e}")
            
            # Load multiple icon sizes for better compatibility
            icon_sizes = [16, 32, 48]
            loaded_icons = []
            
            for size in icon_sizes:
                try:
                    hicon = user32.LoadImageW(
                        None,  # hInst
                        icon_path,  # name
                        1,  # IMAGE_ICON
                        size,  # cx
                        size,  # cy
                        0x00000010 | 0x00008000  # LR_LOADFROMFILE | LR_DEFAULTSIZE
                    )
                    if hicon:
                        loaded_icons.append(hicon)
                        print(f"Process icon loaded ({size}x{size}): {icon_path}")
                except Exception as e:
                    print(f"Failed to load {size}x{size} icon: {e}")
            
            if loaded_icons:
                print(f"Process-level icons loaded successfully: {len(loaded_icons)} sizes")
            else:
                print("Failed to load any process-level icons")
                
        except Exception as e:
            print(f"Error setting process icon: {e}")
    
    def _set_early_icon(self):
        """Set window icon immediately after window creation"""
        try:
            # Get the icon file path
            icon_path = os.path.join(os.path.dirname(__file__), "images", "cser-icon.ico")
            if not os.path.exists(icon_path):
                print(f"Icon file not found: {icon_path}")
                return
            
            # Use Tkinter's iconbitmap method first
            try:
                self.root.iconbitmap(icon_path)
                print(f"Early iconbitmap set: {icon_path}")
            except Exception as e:
                print(f"Early iconbitmap failed: {e}")
            
            # Force immediate update
            self.root.update_idletasks()
            
            # Set App User Model ID immediately
            try:
                import ctypes
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("CSER.AMXModXEditor.1.0")
                print("Early App User Model ID set")
            except Exception as e:
                print(f"Early App User Model ID failed: {e}")
                
        except Exception as e:
            print(f"Error in early icon setting: {e}")
    
    def _show_window_gently(self):
        """Show the window without forcing it to the front"""
        self.root.deiconify()  # Show the window
        # Don't use lift(), focus_force(), or tkraise() to avoid minimizing other windows
    
    def load_custom_font(self):
        """Load Windows default monospace fonts suitable for code editing"""
        try:
            # Windows varsayılan monospace fontları - kod editörü için ideal
            # Öncelik sırası: Consolas > Courier New > Lucida Console > Courier
            font_candidates = [
                "Consolas",        # Modern, çok okunabilir (VS Code varsayılanı)
                "Courier New",     # Klasik, her Windows'ta var
                "Lucida Console",  # Terminal tarzı, net
                "Courier"          # En temel fallback
            ]
            
            # En uygun fontu bul
            selected_font = None
            for font_name in font_candidates:
                try:
                    # Test font oluştur
                    test_font = tkFont.Font(family=font_name, size=12)
                    # Eğer font gerçekten yüklendiyse, actual() metodu doğru family döner
                    if test_font.actual()['family'].lower() == font_name.lower():
                        selected_font = font_name
                        print(f"✓ {font_name} fontu bulundu ve seçildi")
                        break
                except:
                    continue
            
            if not selected_font:
                selected_font = "Courier New"  # Güvenli fallback
                print("⚠ Varsayılan font olarak Courier New kullanılıyor")
            
            # Font objelerini oluştur - daha büyük boyutlar
            self.custom_font = tkFont.Font(family=selected_font, size=14)  # 12'den 14'e
            self.line_font = tkFont.Font(family=selected_font, size=14)     # 12'den 14'e
            
            print(f"🎯 Kod editörü fontu: {selected_font} (14pt) - Büyütüldü")
            
        except Exception as e:
            # Son çare fallback
            print(f"Font yükleme hatası: {e}, sistem varsayılanı kullanılıyor")
            available_fonts = tkFont.families()
            
            if "Consolas" in available_fonts:
                self.custom_font = tkFont.Font(family="Consolas", size=12)
                self.line_font = tkFont.Font(family="Consolas", size=12)
                print("Using Consolas as fallback font")
            elif "Courier New" in available_fonts:
                self.custom_font = tkFont.Font(family="Courier New", size=12)
                self.line_font = tkFont.Font(family="Courier New", size=12)
                print("Using Courier New as fallback font")
            else:
                self.custom_font = tkFont.Font(family="monospace", size=12)
                self.line_font = tkFont.Font(family="monospace", size=12)
                print("Using default monospace font")
    
    def load_logo(self):
        """Load CSER application logo as window icon using ICO file"""
        try:
            # Use ICO file directly for both window and taskbar icons
            ico_path = os.path.join(os.path.dirname(__file__), "images", "cser-icon.ico")
            png_path = os.path.join(os.path.dirname(__file__), "images", "cser-icon.png")
            
            print(f"🔍 ICO dosyası aranıyor: {ico_path}")
            
            if os.path.exists(ico_path):
                print("✓ ICO dosyası bulundu")
                
                # Set Windows icon using ICO file directly
                try:
                    self.root.wm_iconbitmap(ico_path)
                    print("✓ Windows ICO dosyası pencere ikonu olarak ayarlandı")
                except Exception as ico_error:
                    print(f"⚠ ICO dosyası ayarlama hatası: {ico_error}")
                
                # Also create PhotoImage versions for iconphoto (fallback)
                if os.path.exists(png_path):
                    try:
                        logo_image = Image.open(png_path)
                        print(f"📏 PNG boyut: {logo_image.size}")
                        
                        # Create multiple sizes for iconphoto fallback
                        sizes = [(16, 16), (32, 32), (48, 48), (64, 64)]
                        self.logo_photos = []
                        
                        for size in sizes:
                            resized_image = logo_image.resize(size, Image.Resampling.LANCZOS)
                            photo = ImageTk.PhotoImage(resized_image)
                            self.logo_photos.append(photo)
                        
                        # Set as fallback using iconphoto
                        self.root.iconphoto(True, *self.logo_photos)
                        print("✓ PNG fallback ikonu da ayarlandı")
                        
                    except Exception as png_error:
                        print(f"⚠ PNG fallback hatası: {png_error}")
                
                # Set taskbar icon for Windows using ICO file
                self.set_taskbar_icon()
                
            else:
                print("⚠ ICO dosyası bulunamadı, PNG kullanılacak")
                # Fallback to PNG if ICO doesn't exist
                if os.path.exists(png_path):
                    logo_image = Image.open(png_path)
                    sizes = [(16, 16), (32, 32), (48, 48), (64, 64)]
                    self.logo_photos = []
                    
                    for size in sizes:
                        resized_image = logo_image.resize(size, Image.Resampling.LANCZOS)
                        photo = ImageTk.PhotoImage(resized_image)
                        self.logo_photos.append(photo)
                    
                    self.root.iconphoto(True, *self.logo_photos)
                    print("✓ PNG dosyası pencere ikonu olarak ayarlandı")
                    self.set_taskbar_icon()
                else:
                    print("⚠ Hiçbir ikon dosyası bulunamadı")
                    
        except Exception as e:
            print(f"⚠ Logo yükleme hatası: {e}")
    
    def set_taskbar_icon(self):
        """Set the taskbar icon for Windows using comprehensive approach"""
        try:
            if sys.platform == "win32":
                # Wait for window to be fully created and mapped
                self.root.update_idletasks()
                self.root.after(100, self._apply_taskbar_icon)  # Delay to ensure window is fully ready
                
        except Exception as e:
            print(f"⚠ Taskbar ikon ayarlama hatası: {e}")
    
    def _apply_taskbar_icon(self):
        """Apply taskbar icon using comprehensive Windows approach"""
        try:
            ico_path = os.path.join(os.path.dirname(__file__), "images", "cser-icon.ico")
            if os.path.exists(ico_path):
                print(f"🔍 ICO dosyası taskbar için kullanılıyor: {ico_path}")
                
                # STEP 1: Use Tkinter's built-in iconbitmap method first
                try:
                    self.root.iconbitmap(ico_path)
                    print("✓ Tkinter iconbitmap ayarlandı")
                except Exception as e:
                    print(f"⚠ Tkinter iconbitmap hatası: {e}")
                
                # STEP 2: Set Application User Model ID to separate from Python
                try:
                    app_id = "CSER.CodeEditor.2024"
                    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
                    print("✓ App User Model ID ayarlandı")
                except Exception as e:
                    print(f"⚠ App User Model ID hatası: {e}")
                
                # STEP 3: Set window properties
                self.root.title("CSER - AMX Mod X Editor")
                self.root.wm_iconname("CSER")
                
                # STEP 4: Additional Windows API calls for taskbar
                try:
                    hwnd = self.root.winfo_id()
                    
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
                        
                        print("✓ Windows API ikonları ayarlandı")
                        
                        # Force window update
                        ctypes.windll.user32.UpdateWindow(hwnd)
                        ctypes.windll.user32.RedrawWindow(hwnd, None, None, 0x0001 | 0x0004)
                        
                        # Notify shell of icon change
                        ctypes.windll.shell32.SHChangeNotify(0x08000000, 0x0000, None, None)
                        
                        print("✓ Taskbar ikonu başarıyla ayarlandı")
                        
                    else:
                        print("⚠ İkon yüklenemedi")
                        
                except Exception as e:
                    print(f"⚠ Windows API ikon hatası: {e}")
                    
            else:
                print("⚠ ICO dosyası bulunamadı")
                
        except Exception as e:
            print(f"⚠ Taskbar ikon hatası: {e}")
    
    def create_main_layout(self):
        """Create the main application layout"""
        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Create main container
        self.main_container = ctk.CTkFrame(self.root, corner_radius=0)
        self.main_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Configure main container grid (3 sections now)
        self.main_container.grid_rowconfigure(0, weight=1)  # Code editor section
        self.main_container.grid_rowconfigure(1, weight=0)  # Compiler/Counter section
        self.main_container.grid_rowconfigure(2, weight=0)  # Button section
        self.main_container.grid_columnconfigure(0, weight=1)
    
    def create_editor_section(self):
        """Create the modern code editor section with line numbers"""
        # Editor frame
        self.editor_frame = ctk.CTkFrame(self.main_container, corner_radius=10)
        self.editor_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 5))
        
        # Configure editor frame grid
        self.editor_frame.grid_rowconfigure(1, weight=1)
        self.editor_frame.grid_columnconfigure(0, weight=1)
        
        # File name section
        self.filename_frame = ctk.CTkFrame(self.editor_frame, height=50, corner_radius=8)
        self.filename_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 10))
        self.filename_frame.grid_propagate(False)
        
        # Configure filename frame
        self.filename_frame.grid_rowconfigure(0, weight=1)
        self.filename_frame.grid_columnconfigure(0, weight=0)  # File label
        self.filename_frame.grid_columnconfigure(1, weight=1)  # Filename container
        
        # File name label
        self.filename_label = ctk.CTkLabel(
            self.filename_frame, 
            text="File Name:", 
            font=ctk.CTkFont(size=15, weight="bold")
        )
        self.filename_label.grid(row=0, column=0, padx=(15, 10), pady=10, sticky="w")
        
        # Filename container
        self.name_container = ctk.CTkFrame(self.filename_frame, corner_radius=6)
        self.name_container.grid(row=0, column=1, sticky="ew", padx=(0, 15), pady=8)
        self.name_container.grid_columnconfigure(0, weight=1)
        
        # Filename entry
        self.filename_entry = ctk.CTkEntry(
            self.name_container,
            placeholder_text="Enter filename...",
            font=ctk.CTkFont(size=13),
            height=35,
            corner_radius=6,
            border_width=0
        )
        self.filename_entry.grid(row=0, column=0, sticky="ew", padx=(8, 2), pady=4)
        self.filename_entry.insert(0, "untitled")
        
        # Extension label
        self.extension_label = ctk.CTkLabel(
            self.name_container,
            text=".sma",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=("#7C7C7C", "#A0A0A0")
        )
        self.extension_label.grid(row=0, column=1, padx=(2, 8), pady=4, sticky="e")
        
        # Code editor container with line numbers
        self.editor_container = ctk.CTkFrame(self.editor_frame, corner_radius=8)
        self.editor_container.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        self.editor_container.grid_rowconfigure(0, weight=1)
        self.editor_container.grid_columnconfigure(0, weight=0)  # Line numbers
        self.editor_container.grid_columnconfigure(1, weight=1)  # Code editor
        self.editor_container.grid_columnconfigure(2, weight=0)  # Scrollbar
        
        # Line numbers text widget
        self.line_numbers = tk.Text(
            self.editor_container,
            width=4,
            padx=3,
            pady=15,  # Kod editörü ile aynı pady değeri
            takefocus=0,
            border=0,
            state='disabled',
            wrap='none',
            font=self.line_font,
            bg='#2d2d2d',
            fg='#858585',
            relief='flat',
            spacing1=0,  # Satır öncesi boşluk
            spacing2=0,  # Satır arası boşluk
            spacing3=0   # Satır sonrası boşluk
        )
        self.line_numbers.grid(row=0, column=0, sticky="ns", padx=(10, 0), pady=10)
        
        # Create text widget with modern styling
        self.code_editor = tk.Text(
            self.editor_container,
            wrap=tk.NONE,
            font=self.custom_font,
            bg='#1e1e1e',
            fg='#d4d4d4',
            insertbackground='#00d4ff',
            selectbackground='#264f78',
            selectforeground='#ffffff',
            relief='flat',
            borderwidth=0,
            padx=8,
            pady=15,
            undo=True,
            maxundo=50,
            spacing1=0,  # Satır öncesi boşluk
            spacing2=0,  # Satır arası boşluk
            spacing3=0   # Satır sonrası boşluk
        )
        

        
        # Add scrollbars
        self.v_scrollbar = ctk.CTkScrollbar(self.editor_container, command=self.on_scrollbar)
        self.h_scrollbar = ctk.CTkScrollbar(self.editor_container, orientation="horizontal", command=self.code_editor.xview)
        
        # Configure scrollbars with proper callbacks
        def on_vertical_scroll(*args):
            self.v_scrollbar.set(*args)
            self.on_textscroll(*args)
        
        self.code_editor.configure(yscrollcommand=on_vertical_scroll, xscrollcommand=self.h_scrollbar.set)
        
        # Grid the text widget and scrollbars
        self.code_editor.grid(row=0, column=1, sticky="nsew", padx=(2, 0), pady=10)
        self.v_scrollbar.grid(row=0, column=2, sticky="ns", padx=(5, 10), pady=10)
        self.h_scrollbar.grid(row=1, column=1, sticky="ew", padx=5, pady=(0, 10))
        

        
        # Bind events for line numbers and syntax highlighting
        self.code_editor.bind('<KeyRelease>', self.on_content_changed)
        self.code_editor.bind('<Button-1>', self.on_content_changed)
        self.code_editor.bind('<MouseWheel>', self.on_mouse_wheel)
        
        # Bind auto-indent events
        self.code_editor.bind('<Tab>', self.on_tab_key)
        self.code_editor.bind('<Return>', self.on_enter_key)
        
        # Bind smart deletion events
        self.code_editor.bind('<BackSpace>', self.on_backspace_key)
        self.code_editor.bind('<Control-BackSpace>', self.on_ctrl_backspace)
        
        # Bind save shortcut
        self.code_editor.bind('<Control-s>', self.on_ctrl_s)
        
        # Also bind mouse wheel to line numbers for consistent behavior
        self.line_numbers.bind('<MouseWheel>', self.on_mouse_wheel)
        
        # Add sample AMX Mod X code
        sample_code = """#include <amxmodx>

#define PLUGIN "CSER Default Plugin"
#define VERSION "1.0"
#define AUTHOR "CSER Team"

public plugin_init() {
    register_plugin(PLUGIN, VERSION, AUTHOR);
    register_event("HLTV", "event_round_start", "a", "1=0", "2=0");
}

public event_round_start() {
    client_print(0, print_center, "This plugin was created with CSER - AMX Mod X Editor");
}"""
        self.code_editor.insert("1.0", sample_code)
        self.update_line_numbers()


    
    def create_compiler_section(self):
        """Create the compiler and counter path section"""
        self.compiler_frame = ctk.CTkFrame(self.main_container, height=100, corner_radius=10)
        self.compiler_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(5, 5))
        self.compiler_frame.grid_propagate(False)
        
        # Configure compiler frame grid
        self.compiler_frame.grid_columnconfigure(1, weight=1)  # Path entries expand
        
        # Compiler path section
        compiler_label = ctk.CTkLabel(
            self.compiler_frame,
            text="Compiler Path:",
            font=("Segoe UI", 12, "bold"),
            text_color="#ffffff"
        )
        compiler_label.grid(row=0, column=0, sticky="w", padx=(15, 10), pady=(15, 5))
        
        self.compiler_path_entry = ctk.CTkEntry(
            self.compiler_frame,
            placeholder_text="Select compile.exe from addons/amxmodx/scripting folder",
            height=32,
            font=("Consolas", 11)
        )
        self.compiler_path_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=(15, 5))
        
        self.compiler_browse_btn = ctk.CTkButton(
            self.compiler_frame,
            text="Browse",
            width=80,
            height=32,
            command=self.browse_compiler_path
        )
        self.compiler_browse_btn.grid(row=0, column=2, sticky="e", padx=(0, 15), pady=(15, 5))
        
        # Game path section
        game_label = ctk.CTkLabel(
            self.compiler_frame,
            text="Game Path:",
            font=("Segoe UI", 12, "bold"),
            text_color="#ffffff"
        )
        game_label.grid(row=1, column=0, sticky="w", padx=(15, 10), pady=(5, 15))
        
        self.counter_path_entry = ctk.CTkEntry(
            self.compiler_frame,
            placeholder_text="Select Counter Strike 1.6 executable",
            height=32,
            font=("Consolas", 11)
        )
        self.counter_path_entry.grid(row=1, column=1, sticky="ew", padx=(0, 10), pady=(5, 15))
        
        self.counter_browse_btn = ctk.CTkButton(
            self.compiler_frame,
            text="Browse",
            width=80,
            height=32,
            command=self.browse_counter_path
        )
        self.counter_browse_btn.grid(row=1, column=2, sticky="e", padx=(0, 15), pady=(5, 15))
    
    def browse_compiler_path(self):
        """Browse for compiler executable"""
        from tkinter import filedialog
        filename = filedialog.askopenfilename(
            title="Select Compiler Executable",
            filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
        )
        if filename:
            self.compiler_path_entry.delete(0, 'end')
            self.compiler_path_entry.insert(0, filename)
            # Update path validator
            self.path_validator.set_paths(
                compiler_path=filename,
                game_path=self.counter_path_entry.get()
            )
    
    def browse_counter_path(self):
        """Browse for counter executable"""
        from tkinter import filedialog
        filename = filedialog.askopenfilename(
            title="Select Counter Executable",
            filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
        )
        if filename:
            self.counter_path_entry.delete(0, 'end')
            self.counter_path_entry.insert(0, filename)
            # Update path validator
            self.path_validator.set_paths(
                compiler_path=self.compiler_path_entry.get(),
                game_path=filename
            )
    
    def create_button_section(self):
        """Create the modern button section"""
        self.button_frame = ctk.CTkFrame(self.main_container, height=90, corner_radius=10)
        self.button_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(5, 10))
        self.button_frame.grid_propagate(False)
        
        # Configure button frame
        self.button_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(1, weight=0)
        self.button_frame.grid_columnconfigure(2, weight=0)
        self.button_frame.grid_columnconfigure(3, weight=0)
        self.button_frame.grid_columnconfigure(4, weight=1)
        
        # File button with dynamic arrow icon
        self.file_button = ctk.CTkButton(
            self.button_frame,
            text="▼ File",
            font=ctk.CTkFont(size=16, weight="bold"),
            width=130,
            height=45,
            corner_radius=8,
            fg_color=("#FF8C00", "#FF7F00"),
            hover_color=("#FFA500", "#FF8C00"),
            command=self.show_file_menu
        )
        self.file_button.grid(row=0, column=1, padx=10, pady=20)
        
        # Compile button
        self.compile_button = ctk.CTkButton(
            self.button_frame,
            text="⚙️ Compile",
            font=ctk.CTkFont(size=16, weight="bold"),
            width=130,
            height=45,
            corner_radius=8,
            fg_color=("#2E8B57", "#228B22"),
            hover_color=("#32CD32", "#90EE90"),
            command=self.compile_code
        )
        self.compile_button.grid(row=0, column=2, padx=10, pady=20)
        
        # Run button
        self.run_button = ctk.CTkButton(
            self.button_frame,
            text="▶ Run",
            font=ctk.CTkFont(size=16, weight="bold"),
            width=130,
            height=45,
            corner_radius=8,
            fg_color=("#1E90FF", "#4169E1"),
            hover_color=("#00BFFF", "#87CEEB"),
            command=self.run_code
        )
        self.run_button.grid(row=0, column=3, padx=10, pady=20)
    
    def setup_syntax_highlighting(self):
        """Setup syntax highlighting tags and definitions"""
        # C/SourceMod syntax highlighting colors
        self.syntax_colors = {
            'keyword': '#569cd6',      # Blue for keywords
            'string': '#ce9178',       # Orange for strings
            'comment': '#6a9955',      # Green for comments
            'number': '#b5cea8',       # Light green for numbers
            'preprocessor': '#c586c0', # Purple for preprocessor
            'function': '#dcdcaa',     # Yellow for functions
            'type': '#4ec9b0',         # Cyan for types
        }
        
        # C/SourceMod keywords
        self.keywords = [
            'auto', 'break', 'case', 'char', 'const', 'continue', 'default', 'do',
            'double', 'else', 'enum', 'extern', 'float', 'for', 'goto', 'if',
            'int', 'long', 'register', 'return', 'short', 'signed', 'sizeof', 'static',
            'struct', 'switch', 'typedef', 'union', 'unsigned', 'void', 'volatile', 'while',
            'public', 'stock', 'native', 'forward', 'new', 'decl', 'funcenum', 'functag',
            'Action', 'Plugin', 'Handle', 'bool', 'true', 'false', 'null', 'INVALID_HANDLE'
        ]
        
        # Configure tags
        for tag, color in self.syntax_colors.items():
            self.code_editor.tag_configure(tag, foreground=color)
    
    def highlight_syntax(self):
        """Apply C/SourceMod syntax highlighting"""
        # Clear existing tags
        for tag in self.syntax_colors.keys():
            self.code_editor.tag_remove(tag, "1.0", "end")
        
        content = self.code_editor.get("1.0", "end-1c")
        
        # Highlight keywords
        for keyword in self.keywords:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            for match in re.finditer(pattern, content):
                start = f"1.0+{match.start()}c"
                end = f"1.0+{match.end()}c"
                self.code_editor.tag_add("keyword", start, end)
        
        # Highlight strings
        string_pattern = r'"[^"]*"'
        for match in re.finditer(string_pattern, content):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.code_editor.tag_add("string", start, end)
        
        # Highlight single-line comments
        comment_pattern = r'//.*$'
        for match in re.finditer(comment_pattern, content, re.MULTILINE):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.code_editor.tag_add("comment", start, end)
        
        # Highlight multi-line comments
        multiline_comment_pattern = r'/\*.*?\*/'
        for match in re.finditer(multiline_comment_pattern, content, re.DOTALL):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.code_editor.tag_add("comment", start, end)
        
        # Highlight numbers
        number_pattern = r'\b\d+\.?\d*\b'
        for match in re.finditer(number_pattern, content):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.code_editor.tag_add("number", start, end)
        
        # Highlight preprocessor directives
        preprocessor_pattern = r'#\w+'
        for match in re.finditer(preprocessor_pattern, content):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.code_editor.tag_add("preprocessor", start, end)
        
        # Highlight function names
        function_pattern = r'\b\w+(?=\s*\()'
        for match in re.finditer(function_pattern, content):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.code_editor.tag_add("function", start, end)
    
    def update_line_numbers(self):
        """Update line numbers with center alignment and bounds checking"""
        try:
            self.line_numbers.config(state='normal')
            self.line_numbers.delete('1.0', 'end')
            
            # Get the number of lines in the code editor with bounds checking
            end_index = self.code_editor.index('end-1c')
            line_count = int(end_index.split('.')[0])
            
            # Ensure line count is valid
            if line_count < 1:
                line_count = 1
            
            # Generate line numbers with center alignment
            line_numbers_text = '\n'.join(f"{i:>3}" for i in range(1, line_count + 1))
            self.line_numbers.insert('1.0', line_numbers_text)
            
            # Configure center alignment
            self.line_numbers.tag_configure("center", justify='center')
            self.line_numbers.tag_add("center", "1.0", "end")
            
            self.line_numbers.config(state='disabled')
            
            # Synchronize scroll position immediately
            self.sync_line_numbers_scroll()
            
        except Exception as e:
            # Fallback: ensure line numbers widget is in disabled state
            try:
                self.line_numbers.config(state='disabled')
            except:
                 pass
    
    def sync_line_numbers_scroll(self):
        """Synchronize line numbers scroll position with code editor"""
        try:
            # Get current scroll position from code editor
            top, bottom = self.code_editor.yview()
            
            # Validate scroll position
            if top is not None and 0.0 <= top <= 1.0:
                # Apply the same scroll position to line numbers
                self.line_numbers.yview_moveto(top)
                
                # Force immediate update
                self.line_numbers.update_idletasks()
            
        except Exception as e:
            pass  # Ignore sync errors
    
    def on_content_changed(self, event=None):
        """Handle content changes for line numbers and syntax highlighting"""
        self.update_line_numbers()
        # Update horizontal scrollbar
        self.update_horizontal_scrollbar()
        # Schedule syntax highlighting to avoid performance issues
        self.root.after_idle(self.highlight_syntax)
    
    def update_horizontal_scrollbar(self):
        """Update horizontal scrollbar based on content width"""
        try:
            # Force update of the text widget
            self.code_editor.update_idletasks()
            
            # Get current horizontal scroll position
            current_view = self.code_editor.xview()
            
            # Update horizontal scrollbar
            self.h_scrollbar.set(*current_view)
            
        except Exception as e:
            pass  # Ignore horizontal scroll errors
    
    def on_textscroll(self, *args):
        """Synchronize line numbers with code editor scroll"""
        try:
            # Synchronize line numbers with code editor
            if len(args) >= 2:
                top_fraction = float(args[0])
                top_fraction = max(0.0, min(1.0, top_fraction))  # Clamp between 0 and 1
                self.line_numbers.yview_moveto(top_fraction)
                
        except Exception as e:
            pass  # Ignore scroll sync errors
    
    def on_scrollbar(self, *args):
        """Handle scrollbar events with improved synchronization"""
        try:
            # Apply scroll to code editor
            self.code_editor.yview(*args)
            
            # Synchronize line numbers
            self.line_numbers.yview(*args)
            
        except Exception as e:
            pass  # Ignore scroll errors
    
    def on_tab_key(self, event):
        """Handle Tab key to insert 4 spaces instead of tab character"""
        try:
            # Insert 4 spaces at cursor position
            self.code_editor.insert(tk.INSERT, "    ")
            
            # Auto-scroll to keep cursor visible
            self.code_editor.see(tk.INSERT)
            
            # Update line numbers and syntax highlighting
            self.root.after_idle(self.on_content_changed)
            
            # Prevent default tab behavior
            return "break"
            
        except Exception as e:
            pass  # Ignore tab errors
    
    def on_enter_key(self, event):
        """Handle Enter key for auto-indentation"""
        try:
            # Get current cursor position
            current_line = self.code_editor.index(tk.INSERT).split('.')[0]
            current_line_text = self.code_editor.get(f"{current_line}.0", f"{current_line}.end")
            
            # Calculate current indentation
            indent_level = 0
            for char in current_line_text:
                if char == ' ':
                    indent_level += 1
                elif char == '\t':
                    indent_level += 4  # Convert tab to 4 spaces
                else:
                    break
            
            # Check if current line ends with opening brace or colon (for auto-indent)
            stripped_line = current_line_text.strip()
            should_increase_indent = (
                stripped_line.endswith('{') or 
                stripped_line.endswith(':') or
                stripped_line.startswith('if ') or
                stripped_line.startswith('for ') or
                stripped_line.startswith('while ') or
                stripped_line.startswith('else') or
                stripped_line.startswith('switch ') or
                stripped_line.startswith('case ')
            )
            
            # Calculate new indentation
            new_indent_level = indent_level
            if should_increase_indent:
                new_indent_level += 4
            
            # Insert newline with proper indentation
            indent_spaces = " " * new_indent_level
            self.code_editor.insert(tk.INSERT, f"\n{indent_spaces}")
            
            # Auto-scroll to keep cursor visible
            self.code_editor.see(tk.INSERT)
            
            # Update line numbers and syntax highlighting
            self.root.after_idle(self.on_content_changed)
            
            # Prevent default enter behavior
            return "break"
            
        except Exception as e:
            pass  # Ignore enter errors
    
    def on_backspace_key(self, event):
        """Handle Backspace key for smart deletion of indentation"""
        try:
            # Get current cursor position
            cursor_pos = self.code_editor.index(tk.INSERT)
            line_num, col_num = cursor_pos.split('.')
            line_num, col_num = int(line_num), int(col_num)
            
            # Get current line text up to cursor
            line_start = f"{line_num}.0"
            line_text_before_cursor = self.code_editor.get(line_start, cursor_pos)
            
            # Check if we're at the beginning of spaces that could be a tab (4 spaces)
            if col_num >= 4 and line_text_before_cursor.endswith("    "):
                # Check if the last 4 characters are all spaces
                last_4_chars = line_text_before_cursor[-4:]
                if last_4_chars == "    ":
                    # Delete 4 spaces at once (simulating tab deletion)
                    start_pos = f"{line_num}.{col_num-4}"
                    self.code_editor.delete(start_pos, cursor_pos)
                    
                    # Update line numbers and syntax highlighting
                    self.root.after_idle(self.on_content_changed)
                    
                    # Prevent default backspace behavior
                    return "break"
            
            # If not a tab-like deletion, allow normal backspace
            return None
            
        except Exception as e:
            pass  # Ignore backspace errors
    
    def on_ctrl_backspace(self, event):
        """Handle Ctrl+Backspace for word deletion"""
        try:
            # Get current cursor position
            cursor_pos = self.code_editor.index(tk.INSERT)
            line_num, col_num = cursor_pos.split('.')
            line_num, col_num = int(line_num), int(col_num)
            
            # Get current line text up to cursor
            line_start = f"{line_num}.0"
            line_text_before_cursor = self.code_editor.get(line_start, cursor_pos)
            
            if not line_text_before_cursor:
                # If at beginning of line, delete previous line's newline
                if line_num > 1:
                    prev_line_end = f"{line_num-1}.end"
                    self.code_editor.delete(prev_line_end, cursor_pos)
            else:
                # Find word boundary to delete
                import re
                
                # Remove trailing whitespace first
                text_stripped = line_text_before_cursor.rstrip()
                if len(text_stripped) < len(line_text_before_cursor):
                    # Delete trailing whitespace
                    start_pos = f"{line_num}.{len(text_stripped)}"
                    self.code_editor.delete(start_pos, cursor_pos)
                else:
                    # Find start of current word
                    # Word can be alphanumeric, underscore, or other non-whitespace
                    word_pattern = r'\w+|[^\w\s]+|\s+'
                    words = list(re.finditer(word_pattern, line_text_before_cursor))
                    
                    if words:
                        # Get the last word/token
                        last_word = words[-1]
                        start_pos = f"{line_num}.{last_word.start()}"
                        self.code_editor.delete(start_pos, cursor_pos)
            
            # Update line numbers and syntax highlighting
            self.root.after_idle(self.on_content_changed)
            
            # Prevent default behavior
            return "break"
            
        except Exception as e:
            pass  # Ignore ctrl+backspace errors
    
    def on_ctrl_s(self, event):
        """Handle Ctrl+S key combination for saving"""
        self.save_code()
        return "break"  # Prevent default behavior
    
    def on_mouse_wheel(self, event):
        """Handle mouse wheel scroll with real-time synchronization"""
        try:
            # Calculate scroll delta (Windows uses event.delta, Linux uses event.num)
            if hasattr(event, 'delta'):
                delta = -1 * (event.delta / 120)  # Windows
            else:
                delta = -1 if event.num == 4 else 1  # Linux
            
            # Apply scroll to code editor
            self.code_editor.yview_scroll(int(delta), "units")
            
            # Immediately synchronize line numbers
            self.sync_line_numbers_scroll()
            
            # Update line numbers and syntax highlighting after scroll
            self.root.after_idle(self.on_content_changed)
            
            # Prevent default scroll behavior
            return "break"
            
        except Exception as e:
            pass  # Ignore scroll errors
    

    


    def get_full_filename(self):
        """Get the full filename with .sma extension"""
        filename = self.filename_entry.get().strip()
        if not filename:
            filename = "untitled"
        return f"{filename}.sma"
    
    def save_code(self):
        """Save the current code to a file with path validation"""
        # Update path validator with current paths
        self.path_validator.set_paths(
            compiler_path=self.compiler_path_entry.get(),
            game_path=self.counter_path_entry.get()
        )
        
        # Check if paths are missing
        missing_paths = self.path_validator.validate_for_compile_and_run()
        
        if missing_paths:
            # Show warning dialog for missing paths
            self.show_save_warning_dialog(missing_paths)
            return
        
        # Proceed with saving if paths are valid
        filename = self.get_full_filename()
        content = self.code_editor.get("1.0", "end-1c")
        
        try:
            with open(filename, 'w', encoding='utf-8') as file:
                file.write(content)
            print(f"File saved: {filename}")
            messagebox.showinfo("Success", f"File saved: {filename}")
        except Exception as e:
            print(f"Error saving file: {e}")
            messagebox.showerror("Error", f"Error saving file: {e}")
    
    def show_save_warning_dialog(self, missing_paths):
        """Show custom warning dialog when paths are missing during save"""
        # Use the custom PathValidatorDialog instead of Windows messagebox
        from path_validator import PathValidatorDialog
        
        dialog = PathValidatorDialog(self.root)
        result = dialog.show_path_missing_dialog(missing_paths)
        
        # Focus on the first missing path entry if user wants to set paths
        if result == "settings":
            if "compiler" in missing_paths:
                self.compiler_path_entry.focus_set()
            elif "game" in missing_paths:
                self.counter_path_entry.focus_set()
    
    def show_file_menu(self):
        """Show dropdown menu for file operations"""
        # Check if menu already exists and close it
        if hasattr(self, 'menu_window') and self.menu_window is not None:
            try:
                if self.menu_window.winfo_exists():
                    self.close_menu()
                    return
            except (tk.TclError, AttributeError):
                self.menu_window = None
        
        try:
            # Create a toplevel window for the dropdown menu
            self.menu_window = ctk.CTkToplevel(self.root)
            self.menu_window.title("")
            self.menu_window.geometry("150x120")
            self.menu_window.resizable(False, False)
            
            # Position the menu near the File button with smart positioning
            try:
                button_x = self.file_button.winfo_rootx()
                button_y = self.file_button.winfo_rooty()
                button_height = self.file_button.winfo_height()
                
                # Get screen dimensions
                screen_width = self.root.winfo_screenwidth()
                screen_height = self.root.winfo_screenheight()
                
                # Menu dimensions
                menu_width = 150
                menu_height = 120
                
                # Calculate default position (below button)
                default_x = button_x
                default_y = button_y + button_height + 5
                
                # Check if menu fits below the button
                if default_y + menu_height > screen_height:
                    # Not enough space below, position above the button
                    menu_y = button_y - menu_height - 5
                    # Make sure it doesn't go above screen
                    if menu_y < 0:
                        menu_y = 5
                else:
                    menu_y = default_y
                
                # Check horizontal positioning
                if default_x + menu_width > screen_width:
                    # Adjust to fit within screen width
                    menu_x = screen_width - menu_width - 5
                else:
                    menu_x = default_x
                
                # Ensure minimum margins
                menu_x = max(5, menu_x)
                menu_y = max(5, menu_y)
                
                self.menu_window.geometry(f"+{menu_x}+{menu_y}")
            except (tk.TclError, AttributeError):
                self.menu_window.geometry("+100+100")
            
            # Remove window decorations
            self.menu_window.overrideredirect(True)
            self.menu_window.attributes('-topmost', True)
            
            # Create menu frame
            menu_frame = ctk.CTkFrame(
                self.menu_window, 
                corner_radius=8,
                fg_color=("#2B2B2B", "#1E1E1E")
            )
            menu_frame.pack(fill="both", expand=True, padx=2, pady=2)
            
            # Open button
            open_btn = ctk.CTkButton(
                menu_frame,
                text="📁  Open",
                font=ctk.CTkFont(size=14),
                height=35,
                corner_radius=6,
                fg_color="transparent",
                hover_color=("#404040", "#353535"),
                anchor="w",
                command=self.handle_open_file
            )
            open_btn.pack(fill="x", padx=5, pady=2)
            
            # Save button
            save_btn = ctk.CTkButton(
                menu_frame,
                text="💾  Save",
                font=ctk.CTkFont(size=14),
                height=35,
                corner_radius=6,
                fg_color="transparent",
                hover_color=("#404040", "#353535"),
                anchor="w",
                command=self.handle_save_file
            )
            save_btn.pack(fill="x", padx=5, pady=2)
            
            # Save As button
            save_as_btn = ctk.CTkButton(
                menu_frame,
                text="📄  Save As",
                font=ctk.CTkFont(size=14),
                height=35,
                corner_radius=6,
                fg_color="transparent",
                hover_color=("#404040", "#353535"),
                anchor="w",
                command=self.handle_save_as_file
            )
            save_as_btn.pack(fill="x", padx=5, pady=2)
            
            # Store references for event handling
            self.menu_widgets = [self.menu_window, menu_frame, open_btn, save_btn, save_as_btn]
            
            # Bind click outside to close menu
            def on_click_outside(event):
                try:
                    if hasattr(self, 'menu_widgets') and event.widget not in self.menu_widgets:
                        self.close_menu()
                except (tk.TclError, AttributeError):
                    self.close_menu()
            
            # Store the event handler reference
            self.click_handler = on_click_outside
            
            # Schedule the binding after a short delay
            self.root.after(100, lambda: self.root.bind("<Button-1>", self.click_handler, add="+"))
            
            # Bind escape key to close menu
            self.menu_window.bind("<Escape>", lambda e: self.close_menu())
            
            # Add window movement tracking
            def on_window_move(event=None):
                try:
                    if hasattr(self, 'menu_window') and self.menu_window is not None:
                        if self.menu_window.winfo_exists():
                            self.update_menu_position()
                except (tk.TclError, AttributeError):
                    pass
            
            # Store the movement handler reference
            self.move_handler = on_window_move
            
            # Bind window movement events
            self.root.bind("<Configure>", self.move_handler, add="+")
            
            # Focus on menu window
            self.menu_window.focus_set()
            
            # Update button icon to show up arrow (menu is open)
            self.update_file_button_icon(is_menu_open=True)
            
        except Exception as e:
            print(f"Error creating menu: {e}")
            self.menu_window = None
    
    def update_menu_position(self):
        """Update dropdown menu position when main window moves"""
        try:
            if hasattr(self, 'menu_window') and self.menu_window is not None:
                if self.menu_window.winfo_exists():
                    # Get current button position
                    button_x = self.file_button.winfo_rootx()
                    button_y = self.file_button.winfo_rooty()
                    button_height = self.file_button.winfo_height()
                    
                    # Get screen dimensions
                    screen_width = self.root.winfo_screenwidth()
                    screen_height = self.root.winfo_screenheight()
                    
                    # Menu dimensions
                    menu_width = 150
                    menu_height = 120
                    
                    # Calculate new position (below button)
                    default_x = button_x
                    default_y = button_y + button_height + 5
                    
                    # Check if menu fits below the button
                    if default_y + menu_height > screen_height:
                        # Not enough space below, position above the button
                        menu_y = button_y - menu_height - 5
                        # Make sure it doesn't go above screen
                        if menu_y < 0:
                            menu_y = 5
                    else:
                        menu_y = default_y
                    
                    # Check horizontal positioning
                    if default_x + menu_width > screen_width:
                        # Adjust to fit within screen width
                        menu_x = screen_width - menu_width - 5
                    else:
                        menu_x = default_x
                    
                    # Ensure minimum margins
                    menu_x = max(5, menu_x)
                    menu_y = max(5, menu_y)
                    
                    # Update menu position
                    self.menu_window.geometry(f"+{menu_x}+{menu_y}")
                    
        except (tk.TclError, AttributeError):
            pass

    def close_menu(self):
        """Close the dropdown menu"""
        try:
            # Unbind the click event first
            if hasattr(self, 'click_handler'):
                try:
                    self.root.unbind("<Button-1>")
                except (tk.TclError, AttributeError):
                    pass
                delattr(self, 'click_handler')
            
            # Unbind window movement events
            if hasattr(self, 'move_handler'):
                try:
                    self.root.unbind("<Configure>")
                except (tk.TclError, AttributeError):
                    pass
                delattr(self, 'move_handler')
            
            # Clear widget references
            if hasattr(self, 'menu_widgets'):
                delattr(self, 'menu_widgets')
            
            # Destroy the menu window
            if hasattr(self, 'menu_window') and self.menu_window is not None:
                try:
                    if self.menu_window.winfo_exists():
                        self.menu_window.destroy()
                except (tk.TclError, AttributeError):
                    pass
                finally:
                    self.menu_window = None
                    
        except Exception as e:
            print(f"Error closing menu: {e}")
            self.menu_window = None
        
        # Update button icon to show down arrow (menu is closed)
        self.update_file_button_icon(is_menu_open=False)
    
    def update_file_button_icon(self, is_menu_open=False):
        """Update File button icon based on menu state"""
        try:
            if is_menu_open:
                # Menu is open, show up arrow
                self.file_button.configure(text="▲ File")
            else:
                # Menu is closed, show down arrow
                self.file_button.configure(text="▼ File")
        except Exception as e:
            print(f"Error updating file button icon: {e}")
    
    def handle_open_file(self):
        """Handle open file action"""
        self.close_menu()
        self.open_file()
    
    def handle_save_file(self):
        """Handle save file action"""
        self.close_menu()
        self.save_code()
    
    def handle_save_as_file(self):
        """Handle save as file action"""
        self.close_menu()
        self.save_as_file()
    
    def open_file(self):
        """Open a file dialog and load the selected file"""
        file_path = filedialog.askopenfilename(
            title="Open File",
            filetypes=[("SMA files", "*.sma"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.code_editor.delete("1.0", "end")
                    self.code_editor.insert("1.0", content)
                    
                    # Update filename entry
                    filename = os.path.splitext(os.path.basename(file_path))[0]
                    self.filename_entry.delete(0, "end")
                    self.filename_entry.insert(0, filename)
                    
                print(f"File opened: {file_path}")
                messagebox.showinfo("Success", f"File opened: {os.path.basename(file_path)}")
            except Exception as e:
                print(f"Error opening file: {e}")
                messagebox.showerror("Error", f"Error opening file: {e}")
    
    def save_as_file(self):
        """Save the current code with a new filename"""
        file_path = filedialog.asksaveasfilename(
            title="Save As",
            defaultextension=".sma",
            filetypes=[("SMA files", "*.sma"), ("All files", "*.*")]
        )
        
        if file_path:
            content = self.code_editor.get("1.0", "end-1c")
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                    
                # Update filename entry
                filename = os.path.splitext(os.path.basename(file_path))[0]
                self.filename_entry.delete(0, "end")
                self.filename_entry.insert(0, filename)
                
                print(f"File saved as: {file_path}")
                messagebox.showinfo("Success", f"File saved as: {os.path.basename(file_path)}")
            except Exception as e:
                print(f"Error saving file: {e}")
                messagebox.showerror("Error", f"Error saving file: {e}")
    
    def compile_code(self):
        """Compile button functionality - opens CMD window"""
        # Update path validator with current paths
        self.path_validator.set_paths(
            compiler_path=self.compiler_path_entry.get(),
            game_path=self.counter_path_entry.get()
        )
        
        # Check if compiler path is set
        result = self.path_validator.show_missing_paths_dialog(self.root, "compile")
        
        if result == "settings":
            # Focus on compiler path entry
            self.compiler_path_entry.focus()
            return
        
        # If we get here, all paths are valid
        filename = self.get_full_filename()
        print(f"Compiling {filename}...")
        # Here you would implement actual compilation logic
        # This will open a CMD window as mentioned by the user
    
    def run_code(self):
        """Run button functionality"""
        # Update path validator with current paths
        self.path_validator.set_paths(
            compiler_path=self.compiler_path_entry.get(),
            game_path=self.counter_path_entry.get()
        )
        
        # Check if game path is set
        result = self.path_validator.show_missing_paths_dialog(self.root, "run")
        
        if result == "settings":
            # Focus on game path entry
            self.counter_path_entry.focus()
            return
        
        # If we get here, all paths are valid
        filename = self.get_full_filename()
        print(f"Running {filename}...")
        # Here you would implement actual run logic
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

def start_main_app():
    """Start the main application after splash screen"""
    # Create new Tk instance for main app to avoid PhotoImage conflicts
    app = CSERCodeEditor()
    app.run()

def main():
    """Main entry point with splash screen"""
    # Show splash screen first
    splash = SplashScreen(start_main_app)
    
    # Start the splash event loop
    splash.splash_root.mainloop()

if __name__ == "__main__":
    main()