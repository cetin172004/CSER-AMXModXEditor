import customtkinter as ctk
import os
import tkinter as tk
import ctypes
from tkinter import messagebox, filedialog

class PathValidatorDialog:
    """
    Estetik pop-up dialog sınıfı - Compiler ve Game path kontrolü için
    """
    
    def __init__(self, parent=None):
        self.parent = parent
        self.result = None
        self.dialog = None
        
    def show_path_missing_dialog(self, missing_paths):
        """
        Show aesthetic pop-up for missing paths
        
        Args:
            missing_paths (list): List of missing paths ['compiler', 'game']
        """
        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.title("Missing Paths")
        self.dialog.geometry("400x250")
        self.dialog.resizable(False, False)
        
        # Set window icon to CSER icon using Windows API
        self._set_dialog_icon()
        
        # Center dialog
        self.center_dialog()
    
    def _set_dialog_icon(self):
        """Set dialog icon using multiple methods for maximum compatibility"""
        try:
            icon_path = os.path.join(os.path.dirname(__file__), "images", "cser-icon.ico")
            if not os.path.exists(icon_path):
                print(f"Dialog icon file not found: {icon_path}")
                return
            
            # Method 1: Immediate iconbitmap setting
            try:
                self.dialog.iconbitmap(icon_path)
                print("Dialog iconbitmap set immediately")
            except Exception as e:
                print(f"Immediate iconbitmap failed: {e}")
            
            # Method 2: Force window to be visible first, then set icon
            def force_icon_setting():
                try:
                    # Make sure window is visible and mapped
                    self.dialog.deiconify()
                    self.dialog.lift()
                    self.dialog.focus_force()
                    self.dialog.update()
                    
                    # Try iconbitmap again
                    self.dialog.iconbitmap(icon_path)
                    self.dialog.wm_iconbitmap(icon_path)
                    
                    # Get window handle for Windows API
                    hwnd = self.dialog.winfo_id()
                    if hwnd:
                        user32 = ctypes.windll.user32
                        
                        # Load and set multiple icon sizes
                        for size in [16, 32, 48]:
                            try:
                                hicon = user32.LoadImageW(
                                    None,  # hInst
                                    icon_path,  # name
                                    1,  # IMAGE_ICON
                                    size,  # cx
                                    size,  # cy
                                    0x00000010  # LR_LOADFROMFILE
                                )
                                
                                if hicon:
                                    # Set as both small and large icon
                                    user32.SendMessageW(hwnd, 0x0080, 0, hicon)  # WM_SETICON, ICON_SMALL
                                    user32.SendMessageW(hwnd, 0x0080, 1, hicon)  # WM_SETICON, ICON_BIG
                                    print(f"Dialog Windows API icon set ({size}x{size})")
                            except Exception as e:
                                print(f"Windows API icon setting failed for {size}x{size}: {e}")
                    
                    # Force window update
                    self.dialog.update_idletasks()
                    self.dialog.update()
                    
                except Exception as e:
                    print(f"Force icon setting failed: {e}")
            
            # Schedule multiple attempts
            self.dialog.after(10, force_icon_setting)
            self.dialog.after(100, force_icon_setting)
            self.dialog.after(200, force_icon_setting)
            
        except Exception as e:
            print(f"Error in _set_dialog_icon: {e}")
        
        # Make dialog modal
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Main frame
        main_frame = ctk.CTkFrame(self.dialog, corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Warning icon
        icon_label = ctk.CTkLabel(
            main_frame,
            text="⚠️",
            font=ctk.CTkFont(size=48),
            text_color="#FF6B6B"
        )
        icon_label.pack(pady=(30, 20))
        
        # Professional message
        message_label = ctk.CTkLabel(
            main_frame,
            text="Please configure the required compiler and game paths before\nproceeding.",
            font=ctk.CTkFont(size=16),
            text_color="#E0E0E0",
            wraplength=300,
            justify="center"
        )
        message_label.pack(pady=(0, 30))
        
        # Button frame
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(pady=(0, 20))
        
        # OK button
        ok_btn = ctk.CTkButton(
            button_frame,
            text="OK",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#4CAF50",
            hover_color="#45A049",
            corner_radius=8,
            height=40,
            width=120,
            command=self.open_settings
        )
        ok_btn.pack(pady=(0, 20))
        
        # Wait for dialog
        self.dialog.wait_window()
        return self.result
    

    
    def center_dialog(self):
        """Center dialog on screen"""
        self.dialog.update_idletasks()
        
        # Screen dimensions
        screen_width = self.dialog.winfo_screenwidth()
        screen_height = self.dialog.winfo_screenheight()
        
        # Dialog dimensions
        dialog_width = 400
        dialog_height = 250
        
        # Center coordinates
        x = (screen_width - dialog_width) // 2
        y = (screen_height - dialog_height) // 2
        
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
    
    def open_settings(self):
        """Open settings menu"""
        self.result = "settings"
        self.dialog.destroy()
    
    def cancel_dialog(self):
        """Cancel dialog without opening settings"""
        self.result = "cancel"
        self.dialog.destroy()


class PathValidator:
    """
    Path kontrolü yapan ana sınıf
    """
    
    def __init__(self):
        self.compiler_path = ""
        self.game_path = ""
    
    def set_paths(self, compiler_path="", game_path=""):
        """Path'leri ayarla"""
        self.compiler_path = compiler_path
        self.game_path = game_path
    
    def validate_for_compile(self):
        """Check if compiler path is set"""
        missing_paths = []
        
        if not self.compiler_path or self.compiler_path.strip() == "":
            missing_paths.append("compiler")
            
        return missing_paths
    
    def validate_for_run(self):
        """Check if game path is set"""
        missing_paths = []
        
        if not self.game_path or self.game_path.strip() == "":
            missing_paths.append("game")
            
        return missing_paths
    
    def validate_for_compile_and_run(self):
        """Check if both compiler and game paths are set"""
        missing_paths = []
        
        if not self.compiler_path or self.compiler_path.strip() == "":
            missing_paths.append("compiler")
            
        if not self.game_path or self.game_path.strip() == "":
            missing_paths.append("game")
            
        return missing_paths
    
    def show_missing_paths_dialog(self, parent, action_type="compile"):
        """
        Eksik path'ler için dialog göster
        
        Args:
            parent: Ana pencere
            action_type: "compile", "run" veya "both"
        
        Returns:
            str: "settings", "cancel" veya None
        """
        if action_type == "compile":
            missing_paths = self.validate_for_compile()
        elif action_type == "run":
            missing_paths = self.validate_for_run()
        else:  # both
            missing_paths = self.validate_for_compile_and_run()
        
        if missing_paths:
            dialog = PathValidatorDialog(parent)
            return dialog.show_path_missing_dialog(missing_paths)
        
        return None  # Tüm path'ler mevcut


# Test fonksiyonu
def test_path_validator():
    """Path validator'ı test et"""
    root = ctk.CTk()
    root.title("Path Validator Test")
    root.geometry("300x200")
    
    validator = PathValidator()
    
    def test_compile():
        result = validator.show_missing_paths_dialog(root, "compile")
        print(f"Compile test result: {result}")
    
    def test_run():
        result = validator.show_missing_paths_dialog(root, "run")
        print(f"Run test result: {result}")
    
    def test_both():
        result = validator.show_missing_paths_dialog(root, "both")
        print(f"Both test result: {result}")
    
    # Test butonları
    ctk.CTkButton(root, text="Test Compile", command=test_compile).pack(pady=10)
    ctk.CTkButton(root, text="Test Run", command=test_run).pack(pady=10)
    ctk.CTkButton(root, text="Test Both", command=test_both).pack(pady=10)
    
    root.mainloop()


if __name__ == "__main__":
    test_path_validator()