import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os


class FileMenu:
    def __init__(self, parent):
        """Initialize FileMenu with reference to parent CSERCodeEditor"""
        self.parent = parent
        self.file_menu_frame = None
        self.file_menu_visible = False
        
    def show_file_menu(self):
        """Show the file menu dropdown"""
        if self.file_menu_visible:
            self.close_menu()
            return
            
        # Create menu frame
        self.file_menu_frame = ctk.CTkFrame(
            self.parent.main_frame,
            fg_color="#2b2b2b",
            border_width=1,
            border_color="#404040",
            corner_radius=8
        )
        
        # Position menu below file button
        button_x = self.parent.file_button.winfo_x()
        button_y = self.parent.file_button.winfo_y() + self.parent.file_button.winfo_height()
        
        self.file_menu_frame.place(x=button_x, y=button_y, width=200, height=300)
        
        # Menu items
        menu_items = [
            ("📄 New File", self._new_file),
            ("📂 Open File", self._open_file),
            ("💾 Save", self._save_file),
            ("💾 Save As", self._save_as_file),
            ("📋 Copy All", self._copy_all),
            ("📋 Paste", self._paste),
            ("🔍 Find", self._find),
            ("🔄 Replace", self._replace),
            ("❌ Exit", self._exit_app)
        ]
        
        # Create menu buttons
        for i, (text, command) in enumerate(menu_items):
            btn = ctk.CTkButton(
                self.file_menu_frame,
                text=text,
                command=command,
                fg_color="transparent",
                text_color="#ffffff",
                hover_color="#404040",
                anchor="w",
                height=30,
                font=("Consolas", 12)
            )
            btn.pack(fill="x", padx=5, pady=2)
            
        # Update file button icon
        self.parent.update_file_button_icon(True)
        self.file_menu_visible = True
        
        # Bind click outside to close menu
        self.parent.bind_all("<Button-1>", self._on_click_outside)
        
        # Update menu position after a short delay
        self.parent.after(10, self.update_menu_position)
        
    def update_menu_position(self):
        """Update menu position to stay aligned with file button"""
        if self.file_menu_frame and self.file_menu_visible:
            try:
                # Get current button position
                button_x = self.parent.file_button.winfo_x()
                button_y = self.parent.file_button.winfo_y() + self.parent.file_button.winfo_height()
                
                # Update menu position
                self.file_menu_frame.place(x=button_x, y=button_y)
                
                # Schedule next update
                self.parent.after(50, self.update_menu_position)
            except:
                # If there's an error, close the menu
                self.close_menu()
                
    def close_menu(self):
        """Close the file menu"""
        if self.file_menu_frame:
            self.file_menu_frame.destroy()
            self.file_menu_frame = None
            
        self.file_menu_visible = False
        
        # Update file button icon
        self.parent.update_file_button_icon(False)
        
        # Unbind click outside event
        self.parent.unbind_all("<Button-1>")
        
    def _on_click_outside(self, event):
        """Handle clicks outside the menu to close it"""
        if self.file_menu_frame and self.file_menu_visible:
            # Check if click is outside menu
            menu_x = self.file_menu_frame.winfo_x()
            menu_y = self.file_menu_frame.winfo_y()
            menu_width = self.file_menu_frame.winfo_width()
            menu_height = self.file_menu_frame.winfo_height()
            
            click_x = event.x_root - self.parent.winfo_rootx()
            click_y = event.y_root - self.parent.winfo_rooty()
            
            # Also check if click is on file button
            button_x = self.parent.file_button.winfo_x()
            button_y = self.parent.file_button.winfo_y()
            button_width = self.parent.file_button.winfo_width()
            button_height = self.parent.file_button.winfo_height()
            
            if not (menu_x <= click_x <= menu_x + menu_width and 
                   menu_y <= click_y <= menu_y + menu_height) and \
               not (button_x <= click_x <= button_x + button_width and 
                   button_y <= click_y <= button_y + button_height):
                self.close_menu()
                
    def _new_file(self):
        """Create a new file"""
        self.close_menu()
        if self.parent.text_editor.get("1.0", "end-1c").strip():
            result = messagebox.askyesnocancel("New File", "Do you want to save the current file?")
            if result is True:  # Yes
                self._save_file()
            elif result is None:  # Cancel
                return
        
        self.parent.text_editor.delete("1.0", "end")
        self.parent.current_file = None
        self.parent.title("CSER Code Editor - Untitled")
        
    def _open_file(self):
        """Open a file"""
        self.close_menu()
        file_path = filedialog.askopenfilename(
            title="Open File",
            filetypes=[
                ("SourceMod files", "*.sp"),
                ("AMX Mod X files", "*.sma"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.parent.text_editor.delete("1.0", "end")
                    self.parent.text_editor.insert("1.0", content)
                    self.parent.current_file = file_path
                    filename = os.path.basename(file_path)
                    self.parent.title(f"CSER Code Editor - {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {str(e)}")
                
    def _save_file(self):
        """Save the current file"""
        self.close_menu()
        if self.parent.current_file:
            try:
                content = self.parent.text_editor.get("1.0", "end-1c")
                with open(self.parent.current_file, 'w', encoding='utf-8') as file:
                    file.write(content)
                messagebox.showinfo("Success", "File saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {str(e)}")
        else:
            self._save_as_file()
            
    def _save_as_file(self):
        """Save the file with a new name"""
        self.close_menu()
        file_path = filedialog.asksaveasfilename(
            title="Save As",
            defaultextension=".sma",
            filetypes=[
                ("SourceMod files", "*.sp"),
                ("AMX Mod X files", "*.sma"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                content = self.parent.text_editor.get("1.0", "end-1c")
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                self.parent.current_file = file_path
                filename = os.path.basename(file_path)
                self.parent.title(f"CSER Code Editor - {filename}")
                messagebox.showinfo("Success", "File saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {str(e)}")
                
    def _copy_all(self):
        """Copy all text to clipboard"""
        self.close_menu()
        content = self.parent.text_editor.get("1.0", "end-1c")
        self.parent.clipboard_clear()
        self.parent.clipboard_append(content)
        messagebox.showinfo("Success", "All text copied to clipboard!")
        
    def _paste(self):
        """Paste from clipboard"""
        self.close_menu()
        try:
            clipboard_content = self.parent.clipboard_get()
            self.parent.text_editor.insert("insert", clipboard_content)
        except:
            messagebox.showwarning("Warning", "Nothing to paste!")
            
    def _find(self):
        """Find text (placeholder)"""
        self.close_menu()
        messagebox.showinfo("Find", "Find functionality will be implemented soon!")
        
    def _replace(self):
        """Replace text (placeholder)"""
        self.close_menu()
        messagebox.showinfo("Replace", "Replace functionality will be implemented soon!")
        
    def _exit_app(self):
        """Exit the application"""
        self.close_menu()
        if self.parent.text_editor.get("1.0", "end-1c").strip():
            result = messagebox.askyesnocancel("Exit", "Do you want to save before exiting?")
            if result is True:  # Yes
                self._save_file()
            elif result is None:  # Cancel
                return
        self.parent.quit()