"""
modern_photo_editor_with_undo.py
Requirements:
    pip install customtkinter pillow

Features:
- Upload / Save image
- Resize, Rotate, Flip
- Grayscale, Blur, Sharpen
- Brightness / Contrast / Color (saturation) sliders
- Undo (revert to previous state) using a history stack
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageEnhance, ImageFilter
import os

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class ModernPhotoEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Modern Photo Editor — with Undo")
        self.root.geometry("1100x700")
        self.root.minsize(900, 600)

        self.image = None        
        self.preview = None
        self.file_path = None

        self.history = []

        self._brightness_started = False
        self._contrast_started = False
        self._color_started = False

        self.preview_frame = ctk.CTkFrame(self.root, corner_radius=8)
        self.preview_frame.pack(side="left", expand=True, fill="both", padx=12, pady=12)

        self.controls_frame = ctk.CTkFrame(self.root, width=320, corner_radius=8)
        self.controls_frame.pack(side="right", fill="y", padx=12, pady=12)

        self.preview_label = ctk.CTkLabel(self.preview_frame, text="Upload an image to begin",
                                          anchor="center", fg_color=("#d6d6d6", "#3a3a3a"))
        self.preview_label.pack(expand=True, fill="both", padx=20, pady=20)

        self._build_controls()

    def _build_controls(self):
        top_row = ctk.CTkFrame(self.controls_frame, fg_color="transparent")
        top_row.pack(fill="x", pady=(10, 6))

        ctk.CTkButton(top_row, text="Upload", command=self.upload_image, width=14).pack(side="left", padx=6)
        ctk.CTkButton(top_row, text="Save", command=self.save_image, width=14).pack(side="left", padx=6)
        ctk.CTkButton(top_row, text="Undo", fg_color="#ff7b7b", hover_color="#ff5a5a",
                       command=self.undo, width=14).pack(side="left", padx=6)

        btns = [
            ("Resize", self.resize_dialog),
            ("Rotate", self.rotate_dialog),
            ("Flip H", lambda: self.apply_and_push(lambda img: img.transpose(Image.FLIP_LEFT_RIGHT))),
            ("Flip V", lambda: self.apply_and_push(lambda img: img.transpose(Image.FLIP_TOP_BOTTOM))),
            ("Grayscale", lambda: self.apply_and_push(lambda img: img.convert("L").convert("RGB"))),
            ("Blur", lambda: self.apply_and_push(lambda img: img.filter(ImageFilter.BLUR))),
            ("Sharpen", lambda: self.apply_and_push(lambda img: img.filter(ImageFilter.SHARPEN))),
        ]
        for (text, cmd) in btns:
            ctk.CTkButton(self.controls_frame, text=text, command=cmd).pack(fill="x", padx=12, pady=6)

        ctk.CTkLabel(self.controls_frame, text="Adjustments", anchor="w", font=ctk.CTkFont(size=14, weight="bold")).pack(fill="x", padx=12, pady=(12, 6))

        self.brightness_var = ctk.DoubleVar(value=1.0)
        ctk.CTkLabel(self.controls_frame, text="Brightness").pack(fill="x", padx=12)
        self.brightness_slider = ctk.CTkSlider(self.controls_frame, from_=0.2, to=3.0, number_of_steps=200,
                                               command=self._brightness_moved, variable=self.brightness_var)
        self.brightness_slider.pack(fill="x", padx=12, pady=(0, 8))
        ctk.CTkButton(self.controls_frame, text="Apply Brightness", command=self.apply_brightness).pack(fill="x", padx=12, pady=(0,8))

        self.contrast_var = ctk.DoubleVar(value=1.0)
        ctk.CTkLabel(self.controls_frame, text="Contrast").pack(fill="x", padx=12)
        self.contrast_slider = ctk.CTkSlider(self.controls_frame, from_=0.2, to=3.0, number_of_steps=200,
                                             command=self._contrast_moved, variable=self.contrast_var)
        self.contrast_slider.pack(fill="x", padx=12, pady=(0, 8))
        ctk.CTkButton(self.controls_frame, text="Apply Contrast", command=self.apply_contrast).pack(fill="x", padx=12, pady=(0,8))

        self.color_var = ctk.DoubleVar(value=1.0)
        ctk.CTkLabel(self.controls_frame, text="Color (Saturation)").pack(fill="x", padx=12)
        self.color_slider = ctk.CTkSlider(self.controls_frame, from_=0.0, to=2.0, number_of_steps=200,
                                          command=self._color_moved, variable=self.color_var)
        self.color_slider.pack(fill="x", padx=12, pady=(0, 8))
        ctk.CTkButton(self.controls_frame, text="Apply Color", command=self.apply_color).pack(fill="x", padx=12, pady=(0,8))

        self.history_label = ctk.CTkLabel(self.controls_frame, text="History: 0", anchor="w")
        self.history_label.pack(fill="x", padx=12, pady=(10, 4))
    
        ctk.CTkButton(self.controls_frame, text="Reset All (to original file)", fg_color="#9b59b6", hover_color="#8845a6",
                       command=self.reset_all).pack(fill="x", padx=12, pady=6)

    def upload_image(self):
        path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")])
        if not path:
            return
        try:
            img = Image.open(path).convert("RGB")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open image:\n{e}")
            return

        self.file_path = path
        self.image = img
        self.history.clear()
        self._reset_sliders()
        self._update_history_label()
        self.display_image()

    def save_image(self):
        if not self.image:
            messagebox.showwarning("No image", "Please upload and edit an image first.")
            return
        save_path = filedialog.asksaveasfilename(defaultextension=".jpg",
                                                 filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png"), ("BMP", "*.bmp")])
        if not save_path:
            return
        try:
            os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
            self.image.save(save_path)
            messagebox.showinfo("Saved", f"Image saved to:\n{save_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save image:\n{e}")

    def display_image(self):
        if not self.image:
            self.preview_label.configure(text="Upload an image to begin", image=None)
            return
        preview_img = self.image.copy()
        preview_img.thumbnail((820, 640))
        self.preview = ImageTk.PhotoImage(preview_img)
        self.preview_label.configure(image=self.preview, text="")

    def push_history(self):
        if self.image:
            self.history.append(self.image.copy())
        self._update_history_label()

    def undo(self):
        if not self.history:
            messagebox.showinfo("Undo", "No more states to undo.")
            return
        prev = self.history.pop()
        self.image = prev
        self._reset_sliders()
        self.display_image()
        self._update_history_label()

    def _update_history_label(self):
        self.history_label.configure(text=f"History: {len(self.history)}")

    def apply_and_push(self, func):
    
        if not self.image:
            messagebox.showwarning("No image", "Upload an image first.")
            return
        try:
            self.push_history()
            new_img = func(self.image.copy())
            if new_img.mode != "RGB":
                new_img = new_img.convert("RGB")
            self.image = new_img
            self.display_image()
        except Exception as e:
            messagebox.showerror("Error", f"Operation failed: {e}")

    def resize_dialog(self):
        if not self.image:
            messagebox.showwarning("No image", "Upload an image first.")
            return

        dlg = ctk.CTkInputDialog(text="Enter width,height (e.g. 800,600)", title="Resize")
        val = dlg.get_input()
        if not val:
            return
        parts = val.replace(" ", "").split(",")
        if len(parts) != 2:
            messagebox.showerror("Invalid", "Please enter width and height separated by a comma.")
            return
        try:
            w = int(parts[0]); h = int(parts[1])
        except:
            messagebox.showerror("Invalid", "Width and height must be integers.")
            return

        def op(img):
            return img.resize((w, h))
        self.apply_and_push(op)

    def rotate_dialog(self):
        if not self.image:
            messagebox.showwarning("No image", "Upload an image first.")
            return
        dlg = ctk.CTkInputDialog(text="Enter rotation angle (degrees, clockwise)", title="Rotate")
        val = dlg.get_input()
        if not val:
            return
        try:
            angle = float(val)
        except:
            messagebox.showerror("Invalid", "Angle must be a number.")
            return
        self.apply_and_push(lambda img: img.rotate(-angle, expand=True))

    def _brightness_moved(self, value):
        
        if not self._brightness_started and self.image:
            self.push_history()
            self._brightness_started = True
        
        if self.image:
            val = float(value)
            try:
                enhanced = ImageEnhance.Brightness(self.history[-1] if self._brightness_started and self.history else self.image).enhance(val)
                
                tmp = enhanced.copy()
                tmp.thumbnail((820, 640))
                self.preview = ImageTk.PhotoImage(tmp)
                self.preview_label.configure(image=self.preview, text="")
            except Exception:
                pass

    def apply_brightness(self):
        if not self.image:
            messagebox.showwarning("No image", "Upload an image first.")
            return
        val = float(self.brightness_var.get())

        if not self._brightness_started:
            self.push_history()
        base = self.history[-1] if self.history else self.image
        new_img = ImageEnhance.Brightness(base).enhance(val)
        self.image = new_img.convert("RGB")
        self._brightness_started = False
        self._reset_sliders()
        self.display_image()

    def _contrast_moved(self, value):
        if not self._contrast_started and self.image:
            self.push_history()
            self._contrast_started = True
        if self.image:
            val = float(value)
            try:
                base = self.history[-1] if self._contrast_started and self.history else self.image
                tmp_img = ImageEnhance.Contrast(base).enhance(val)
                tmp = tmp_img.copy()
                tmp.thumbnail((820, 640))
                self.preview = ImageTk.PhotoImage(tmp)
                self.preview_label.configure(image=self.preview, text="")
            except Exception:
                pass

    def apply_contrast(self):
        if not self.image:
            messagebox.showwarning("No image", "Upload an image first.")
            return
        val = float(self.contrast_var.get())
        if not self._contrast_started:
            self.push_history()
        base = self.history[-1] if self.history else self.image
        new_img = ImageEnhance.Contrast(base).enhance(val)
        self.image = new_img.convert("RGB")
        self._contrast_started = False
        self._reset_sliders()
        self.display_image()

    def _color_moved(self, value):
        if not self._color_started and self.image:
            self.push_history()
            self._color_started = True
        if self.image:
            val = float(value)
            try:
                base = self.history[-1] if self._color_started and self.history else self.image
                tmp_img = ImageEnhance.Color(base).enhance(val)
                tmp = tmp_img.copy()
                tmp.thumbnail((820, 640))
                self.preview = ImageTk.PhotoImage(tmp)
                self.preview_label.configure(image=self.preview, text="")
            except Exception:
                pass

    def apply_color(self):
        if not self.image:
            messagebox.showwarning("No image", "Upload an image first.")
            return
        val = float(self.color_var.get())
        if not self._color_started:
            self.push_history()
        base = self.history[-1] if self.history else self.image
        new_img = ImageEnhance.Color(base).enhance(val)
        self.image = new_img.convert("RGB")
        self._color_started = False
        self._reset_sliders()
        self.display_image()

    def _reset_sliders(self):
        self.brightness_var.set(1.0)
        self.contrast_var.set(1.0)
        self.color_var.set(1.0)
        self._brightness_started = False
        self._contrast_started = False
        self._color_started = False

   
    def reset_all(self):
        if not self.file_path:
            messagebox.showwarning("Nothing", "No original file to reset to. Upload an image first.")
            return
        try:
            orig = Image.open(self.file_path).convert("RGB")
            self.push_history()
            self.image = orig
            self._reset_sliders()
            self.display_image()
        except Exception as e:
            messagebox.showerror("Error", f"Cannot reset to original file:\n{e}")


if __name__ == "__main__":
    root = ctk.CTk()
    app = ModernPhotoEditor(root)
    root.mainloop()
