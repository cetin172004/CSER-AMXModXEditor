import customtkinter as ctk
import tkinter as tk
import tkinter.font as tkfont
from tkinter import filedialog, messagebox
import re
import sys
import os
import threading
import time
import subprocess
from tkinter import font as tkFont
from PIL import Image, ImageTk
import ctypes

# Import our custom modules
from splash_screen import SplashScreen
from syntax_highlighter import SyntaxHighlighter
from file_menu import FileMenu



# Set appearance mode and color theme
ctk.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"



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
        
        # Initialize modules after editor is created
        self.syntax_highlighter = SyntaxHighlighter(self.code_editor)
        self.file_menu = FileMenu(self)
        
        # Setup syntax highlighting after editor is created
        self.syntax_highlighter.setup_syntax_highlighting()
        
        # Create compiler/counter section
        self.create_compiler_section()
        
        # Create button section
        self.create_button_section()
        
        # Initialize content
        self.on_content_changed()
    
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
        """Create the paths section for cstrike folder and game executable"""
        self.compiler_frame = ctk.CTkFrame(self.main_container, height=120, corner_radius=10)
        self.compiler_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(5, 5))
        self.compiler_frame.grid_propagate(False)
        
        # Configure compiler frame grid
        self.compiler_frame.grid_columnconfigure(1, weight=1)  # Path entries expand
        
        # CS1.6 cstrike folder section
        cstrike_label = ctk.CTkLabel(
            self.compiler_frame,
            text="CS1.6 cstrike Folder:",
            font=("Segoe UI", 12, "bold"),
            text_color="#ffffff"
        )
        cstrike_label.grid(row=0, column=0, sticky="w", padx=(15, 10), pady=(15, 5))
        
        self.cstrike_path_entry = ctk.CTkEntry(
            self.compiler_frame,
            placeholder_text="Select Counter-Strike 1.6 cstrike folder",
            height=32,
            font=("Consolas", 11)
        )
        self.cstrike_path_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=(15, 5))
        
        self.cstrike_browse_btn = ctk.CTkButton(
            self.compiler_frame,
            text="Browse",
            width=80,
            height=32,
            command=self.browse_cstrike_path
        )
        self.cstrike_browse_btn.grid(row=0, column=2, sticky="e", padx=(0, 15), pady=(15, 5))
        
        # Game executable section
        game_label = ctk.CTkLabel(
            self.compiler_frame,
            text="Game Executable:",
            font=("Segoe UI", 12, "bold"),
            text_color="#ffffff"
        )
        game_label.grid(row=1, column=0, sticky="w", padx=(15, 10), pady=(5, 15))
        
        self.game_path_entry = ctk.CTkEntry(
            self.compiler_frame,
            placeholder_text="Select Counter-Strike 1.6 executable (hl.exe)",
            height=32,
            font=("Consolas", 11)
        )
        self.game_path_entry.grid(row=1, column=1, sticky="ew", padx=(0, 10), pady=(5, 15))
        
        self.game_browse_btn = ctk.CTkButton(
            self.compiler_frame,
            text="Browse",
            width=80,
            height=32,
            command=self.browse_game_path
        )
        self.game_browse_btn.grid(row=1, column=2, sticky="e", padx=(0, 15), pady=(5, 15))
    
    def browse_cstrike_path(self):
        """Browse for cstrike folder"""
        from tkinter import filedialog
        folder_path = filedialog.askdirectory(
            title="Select Counter-Strike 1.6 cstrike folder"
        )
        if folder_path:
            self.cstrike_path_entry.delete(0, 'end')
            self.cstrike_path_entry.insert(0, folder_path)
    
    def browse_game_path(self):
        """Browse for game executable file"""
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="Select Counter-Strike 1.6 executable",
            filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
        )
        if file_path:
            self.game_path_entry.delete(0, 'end')
            self.game_path_entry.insert(0, file_path)
    
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
            command=self.file_menu.show_file_menu
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
        self.root.after_idle(self.syntax_highlighter.highlight_syntax)
    
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
    

    

    

    

    

    

    

    
    def update_plugins_ini(self, configs_path, plugin_name):
        """Update plugins.ini file with new plugin"""
        try:
            plugins_ini_path = os.path.join(configs_path, "plugins.ini")
            plugin_line = f"{plugin_name}.amxx"
            
            # Dosya varsa oku, yoksa boş liste oluştur
            existing_lines = []
            if os.path.exists(plugins_ini_path):
                with open(plugins_ini_path, 'r', encoding='utf-8') as file:
                    existing_lines = [line.strip() for line in file.readlines()]
            
            # Plugin zaten varsa ekleme
            if plugin_line in existing_lines:
                print(f"✅ Plugin zaten mevcut: {plugin_line}")
                return True
            
            # Plugin'i ekle
            existing_lines.append(plugin_line)
            
            # Dosyayı güncelle
            with open(plugins_ini_path, 'w', encoding='utf-8') as file:
                for line in existing_lines:
                    if line.strip():  # Boş satırları atla
                        file.write(line + '\n')
            
            print(f"✅ Plugin eklendi: {plugin_line} -> {plugins_ini_path}")
            return True
            
        except Exception as e:
            print(f"❌ plugins.ini güncellenirken hata: {e}")
            return False





    def find_amxx_file_in_compiled(self, compiled_path, filename):
        """Find .amxx file in compiled folder"""
        try:
            # .sma uzantısını .amxx ile değiştir
            amxx_filename = filename.replace('.sma', '.amxx') if filename.endswith('.sma') else f"{filename}.amxx"
            amxx_file_path = os.path.join(compiled_path, amxx_filename)
            
            if os.path.exists(amxx_file_path):
                print(f"✅ .amxx dosyası bulundu: {amxx_file_path}")
                return amxx_file_path
            else:
                print(f"❌ .amxx dosyası bulunamadı: {amxx_file_path}")
                return None
        except Exception as e:
            print(f"❌ .amxx dosyası aranırken hata: {e}")
            return None

    def copy_amxx_to_plugins(self, source_path, plugins_path):
        """Copy .amxx file from compiled to plugins folder"""
        try:
            import shutil
            
            # Hedef klasör yoksa oluştur
            if not os.path.exists(plugins_path):
                os.makedirs(plugins_path)
                print(f"📁 Plugins klasörü oluşturuldu: {plugins_path}")
            
            # Dosya adını al
            filename = os.path.basename(source_path)
            destination_path = os.path.join(plugins_path, filename)
            
            # Dosyayı kopyala
            shutil.copy2(source_path, destination_path)
            print(f"✅ Dosya kopyalandı: {source_path} -> {destination_path}")
            return True
            
        except Exception as e:
            print(f"❌ Dosya kopyalanırken hata: {e}")
            return False



    def compile_code(self):
        """Compile button functionality - opens CMD window"""
        filename = self.get_full_filename()
        cstrike_path = self.cstrike_path_entry.get().strip()
        compiler_path = os.path.join(cstrike_path, "addons", "amxmodx", "scripting", "compile.exe")
        
        print(f"Compiling {filename}...")
        print(f"🔨 Compiler başlatılıyor: {compiler_path}")
        
        try:
            startup_info = subprocess.STARTUPINFO()
            startup_info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startup_info.wShowWindow = 1  # SW_NORMAL = 1
            
            # Launcher dosyaları için özel kontrol
            compiler_filename = os.path.basename(compiler_path).lower()
            if "launcher" in compiler_filename:
                # Launcher dosyaları parametresiz çalıştır
                print("🚀 Compiler Launcher dosyası tespit edildi - parametresiz çalıştırılıyor")
                process = subprocess.Popen(
                    [compiler_path],
                    startupinfo=startup_info,
                    cwd=os.path.dirname(compiler_path) if os.path.dirname(compiler_path) else None
                )
                print(f"✅ Compiler Launcher başarıyla başlatıldı (PID: {process.pid})")
                
                # Launcher işlemi başarılı olduğunda plugins.ini'yi güncelle
                self.update_plugins_ini_after_compile(cstrike_path, filename)
            else:
                # Normal compiler dosyaları için parametreli çalıştır
                print("🔨 Normal compiler dosyası - parametreli çalıştırılıyor")
                process = subprocess.Popen(
                    [compiler_path, filename],
                    startupinfo=startup_info,
                    cwd=os.path.dirname(compiler_path) if os.path.dirname(compiler_path) else None
                )
                print(f"✅ Compiler başarıyla başlatıldı (PID: {process.pid})")
                
                # Compile işlemi başarılı olduğunda plugins.ini'yi güncelle
                self.update_plugins_ini_after_compile(cstrike_path, filename)
                
        except FileNotFoundError:
            print(f"❌ Compiler dosyası çalıştırılamadı: {compiler_path}")
        except Exception as e:
            print(f"❌ Compiler başlatılırken hata oluştu: {str(e)}")
    
    def update_plugins_ini_after_compile(self, cstrike_path, filename):
        """Update plugins.ini and copy .amxx file after successful compile"""
        try:
            # 1. Configs klasörü yolunu oluştur
            configs_path = os.path.join(cstrike_path, "addons", "amxmodx", "configs")
            if not os.path.exists(configs_path):
                print(f"❌ Configs klasörü bulunamadı: {configs_path}")
                return
                return
            
            # 2. Compiled klasörü yolunu oluştur
            compiled_path = os.path.join(cstrike_path, "addons", "amxmodx", "scripting", "compiled")
            if not os.path.exists(compiled_path):
                print(f"❌ Compiled klasörü bulunamadı: {compiled_path}")
                return
            
            # 3. Plugins klasörü yolunu oluştur
            plugins_path = os.path.join(cstrike_path, "addons", "amxmodx", "plugins")
            if not os.path.exists(plugins_path):
                print(f"❌ Plugins klasörü bulunamadı: {plugins_path}")
                return
            
            # Dosya adından .sma uzantısını çıkar
            plugin_name = filename.replace('.sma', '') if filename.endswith('.sma') else filename
            
            print(f"📁 Configs klasörü: {configs_path}")
            print(f"📁 Compiled klasörü: {compiled_path}")
            print(f"📁 Plugins klasörü: {plugins_path}")
            print(f"🔌 Plugin adı: {plugin_name}")
            
            # 4. plugins.ini'yi güncelle
            plugins_ini_success = self.update_plugins_ini(configs_path, plugin_name)
            if plugins_ini_success:
                print(f"✅ plugins.ini başarıyla güncellendi!")
            else:
                print(f"❌ plugins.ini güncellenemedi!")
            
            # 5. .amxx dosyasını compiled klasöründe ara
            amxx_file_path = self.find_amxx_file_in_compiled(compiled_path, filename)
            if not amxx_file_path:
                print(f"❌ .amxx dosyası compiled klasöründe bulunamadı")
                return
            
            # 6. .amxx dosyasını plugins klasörüne kopyala
            copy_success = self.copy_amxx_to_plugins(amxx_file_path, plugins_path)
            if copy_success:
                print(f"✅ .amxx dosyası plugins klasörüne kopyalandı!")
            else:
                print(f"❌ .amxx dosyası kopyalanamadı!")
                
        except Exception as e:
            print(f"❌ Compile sonrası işlemlerinde hata: {e}")
    
    def run_code(self):
        """Run button functionality - Execute the game/exe file"""
        game_path = self.game_path_entry.get().strip()
        
        if not game_path:
            return
            
        if not os.path.exists(game_path):
            # Game executable bulunamadı
            return
            
        if not game_path.lower().endswith('.exe'):
            messagebox.showerror("Hata", "Sadece .exe dosyaları çalıştırılabilir!")
            return
        
        try:
            print(f"🎮 Oyun başlatılıyor: {game_path}")
            
            startup_info = subprocess.STARTUPINFO()
            startup_info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startup_info.wShowWindow = 1  # SW_NORMAL = 1
            
            # Launcher dosyaları için özel kontrol
            game_filename = os.path.basename(game_path).lower()
            if "launcher" in game_filename:
                # Launcher dosyaları parametresiz çalıştır
                print("🚀 Launcher dosyası tespit edildi - parametresiz çalıştırılıyor")
                process = subprocess.Popen(
                    [game_path],
                    startupinfo=startup_info,
                    cwd=os.path.dirname(game_path) if os.path.dirname(game_path) else None
                )
                print(f"✅ Launcher başarıyla başlatıldı (PID: {process.pid})")
            else:
                # Normal oyun dosyaları için parametreli çalıştır
                print("🎮 Normal oyun dosyası - parametreli çalıştırılıyor")
                process = subprocess.Popen(
                    [game_path, "-windowed", "-width", "800", "-height", "600"],
                    startupinfo=startup_info,
                    cwd=os.path.dirname(game_path) if os.path.dirname(game_path) else None
                )
                print(f"✅ Oyun başarıyla başlatıldı (PID: {process.pid})")
                print("📏 Çözünürlük: 800x600 (windowed mode)")
            
        except FileNotFoundError:
            messagebox.showerror("Hata", f"Dosya çalıştırılamadı: {game_path}")
        except Exception as e:
            messagebox.showerror("Hata", f"Oyun başlatılırken hata oluştu:\n{str(e)}")
            print(f"❌ Hata: {str(e)}")
    
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