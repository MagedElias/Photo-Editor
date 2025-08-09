# Summarized Code + GUI
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageEnhance, ImageFilter

class PhotoEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Photo Editor - Pillow")
        self.root.geometry("900x600")
        self.image = None
        self.tk_image = None
        self.file_path = None

        # GUI layout
        self.canvas = tk.Label(root, bg="gray")
        self.canvas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        button_frame = tk.Frame(root, bg="lightgray")
        button_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # Upload & Save
        tk.Button(button_frame, text="Upload Image", command=self.upload_image, width=20).pack(pady=5)
        tk.Button(button_frame, text="Save Image", command=self.save_image, width=20).pack(pady=5)

        # Editing Buttons
        tk.Button(button_frame, text="Resize", command=self.resize_image, width=20).pack(pady=5)
        tk.Button(button_frame, text="Rotate", command=self.rotate_image, width=20).pack(pady=5)
        tk.Button(button_frame, text="Flip Horizontal", command=lambda: self.flip_image("horizontal"), width=20).pack(pady=5)
        tk.Button(button_frame, text="Flip Vertical", command=lambda: self.flip_image("vertical"), width=20).pack(pady=5)
        tk.Button(button_frame, text="Grayscale", command=self.grayscale_image, width=20).pack(pady=5)
        tk.Button(button_frame, text="Add Blur", command=lambda: self.apply_filter(ImageFilter.BLUR), width=20).pack(pady=5)
        tk.Button(button_frame, text="Increase Brightness", command=lambda: self.adjust_brightness(1.2), width=20).pack(pady=5)
        tk.Button(button_frame, text="Increase Contrast", command=lambda: self.adjust_contrast(1.2), width=20).pack(pady=5)

    def upload_image(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png *.jpeg *.bmp")])
        if self.file_path:
            self.image = Image.open(self.file_path)
            self.display_image()

    def display_image(self):
        if self.image:
            img_resized = self.image.copy()
            img_resized.thumbnail((600, 500))
            self.tk_image = ImageTk.PhotoImage(img_resized)
            self.canvas.config(image=self.tk_image)

    def save_image(self):
        if self.image:
            save_path = filedialog.asksaveasfilename(defaultextension=".jpg",
                                                     filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png")])
            if save_path:
                self.image.save(save_path)
                messagebox.showinfo("Saved", "Image saved successfully!")
        else:
            messagebox.showerror("Error", "No image to save!")

    def resize_image(self):
        if self.image:
            try:
                w = int(self.simple_input("Width"))
                h = int(self.simple_input("Height"))
                self.image = self.image.resize((w, h))
                self.display_image()
            except:
                messagebox.showerror("Error", "Invalid width/height!")

    def rotate_image(self):
        if self.image:
            try:
                angle = int(self.simple_input("Rotate Angle"))
                self.image = self.image.rotate(angle)
                self.display_image()
            except:
                messagebox.showerror("Error", "Invalid angle!")

    def flip_image(self, direction):
        if self.image:
            if direction == "horizontal":
                self.image = self.image.transpose(Image.FLIP_LEFT_RIGHT)
            elif direction == "vertical":
                self.image = self.image.transpose(Image.FLIP_TOP_BOTTOM)
            self.display_image()

    def grayscale_image(self):
        if self.image:
            self.image = self.image.convert("L")
            self.display_image()

    def apply_filter(self, filter_type):
        if self.image:
            self.image = self.image.filter(filter_type)
            self.display_image()

    def adjust_brightness(self, level):
        if self.image:
            enhancer = ImageEnhance.Brightness(self.image)
            self.image = enhancer.enhance(level)
            self.display_image()

    def adjust_contrast(self, level):
        if self.image:
            enhancer = ImageEnhance.Contrast(self.image)
            self.image = enhancer.enhance(level)
            self.display_image()

    def simple_input(self, prompt):
        """Simple input dialog for numbers."""
        popup = tk.Toplevel(self.root)
        popup.title(prompt)
        popup.geometry("200x100")
        entry = tk.Entry(popup)
        entry.pack(pady=10)
        value = {"val": None}

        def submit():
            value["val"] = entry.get()
            popup.destroy()

        tk.Button(popup, text="OK", command=submit).pack()
        popup.wait_window()
        return value["val"]

if __name__ == "__main__":
    root = tk.Tk()
    app = PhotoEditor(root)
    root.mainloop()
