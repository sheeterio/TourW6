import os
import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk


class PanoramaRecenter:
    def __init__(self, root):
        self.root = root
        self.root.title("Panorama Recenter")

        # Folder zdjęć wejsciowych
        self.input_folder = filedialog.askdirectory(title="Wybierz folder wejsciowy")
        if not self.input_folder:
            return

        # Folder zdjęć wyjściowych
        self.output_folder = filedialog.askdirectory(title="Wybierz folder wyjsciowy")
        if not self.output_folder:
            return

        self.image_files = sorted(
            [f for f in os.listdir(self.input_folder) if f.lower().endswith(('jpg', 'jpeg', 'png'))])
        self.current_index = 0
        self.yaw_offset = 0

        if not self.image_files:
            print("Nie znaleziono właściwych zdjęć w folderze.")
            return
        
        self.canvas = tk.Canvas(root, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        control_frame = tk.Frame(root)
        control_frame.pack(fill=tk.X)
        #14716 -> 7358 (180), 40.88 (1), 1246 (30.49)
        self.yaw_slider = tk.Scale(control_frame, from_=-7500, to=7500, orient=tk.HORIZONTAL, label="Przesunięcie", #Yaw, do zmiany zakres w zależności od szerokości panoram
                                   command=self.update_offsets)
        self.yaw_slider.pack(fill=tk.X)

        self.save_button = tk.Button(control_frame, text="Zapisz & Dalej", command=self.save_and_next)
        self.save_button.pack()

        self.info_label = tk.Label(control_frame, text="", font=("Arial", 12))
        self.info_label.pack()

        self.load_image()

    def load_image(self):
        # Ładowanie i wyświetlanie panoramy
        file_path = os.path.join(self.input_folder, self.image_files[self.current_index])
        self.image = cv2.imread(file_path)
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        self.display_image()
        self.update_info_label()

    def display_image(self):
        # Wyświetla przesunięcie panoramy oraz linie pomocnicze
        shifted = np.roll(self.image, self.yaw_offset, axis=1)
        canvas_width = self.root.winfo_width()
        #print(len(self.image[1,:]))
        canvas_height = self.root.winfo_height() - 100
        resized = cv2.resize(shifted, (canvas_width, canvas_height), interpolation=cv2.INTER_LINEAR)

        self.pil_image = Image.fromarray(resized)
        self.tk_image = ImageTk.PhotoImage(self.pil_image)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

        # Pomocniczy czerwony znacznik środka X
        mid_x = canvas_width // 2
        mid_y = canvas_height // 2
        self.canvas.create_line(mid_x - 10, mid_y - 10, mid_x + 10, mid_y + 10, fill="red", width=2)
        self.canvas.create_line(mid_x + 10, mid_y - 10, mid_x - 10, mid_y + 10, fill="red", width=2)
        # Pomocnicza żółta pionowa linia 
        self.canvas.create_line(mid_x, 0, mid_x, canvas_height, fill="yellow", width=2)

    def update_offsets(self, value):
        # Aktualizuje widok panoramy o wybrane przesunięcie
        self.yaw_offset = int(self.yaw_slider.get())
        self.display_image()

    def save_and_next(self):
        # Zapisuje panoramę z przesunięciem i poprawką azymutu, przechodzi do kolejnej panoramy
        save_path = os.path.join(self.output_folder, self.image_files[self.current_index])
        curwi=len(self.image[1,:])
        curone=curwi/360
        cur30=int(curone*30.49)
        #print("Correction of",cur30,"for",self.image_files[self.current_index])

        if self.yaw_offset == 0:
            # Wersja bez poprawki azymutalnej
            #original_path = os.path.join(self.input_folder, self.image_files[self.current_index])
            #cv2.imwrite(save_path, cv2.imread(original_path))
            shifted = np.roll(self.image, self.yaw_offset+cur30, axis=1)
            cv2.imwrite(save_path, cv2.cvtColor(shifted, cv2.COLOR_RGB2BGR))
            print("Korekcja +", cur30, "dla", self.image_files[self.current_index])
        elif self.yaw_offset > 0:
            shifted = np.roll(self.image, self.yaw_offset+cur30, axis=1)
            cv2.imwrite(save_path, cv2.cvtColor(shifted, cv2.COLOR_RGB2BGR))
            print("Korekcja +", cur30, "dla", self.image_files[self.current_index])
        elif self.yaw_offset < 0:
            shifted = np.roll(self.image, self.yaw_offset+cur30, axis=1)
            cv2.imwrite(save_path, cv2.cvtColor(shifted, cv2.COLOR_RGB2BGR))
            print("Korekcja +", cur30, "dla", self.image_files[self.current_index])

        self.current_index += 1
        if self.current_index < len(self.image_files):
            self.load_image()
            self.yaw_slider.set(0)
        else:
            messagebox.showinfo("Zrobione", "Wszystkie panoramy zostały skorygowane!")
            self.root.quit()

    def update_info_label(self):
        # Aktualizuje pasek postępu i nazwy obecnej panoramy
        info_text = f"Zdjęcie {self.current_index + 1}/{len(self.image_files)}: {self.image_files[self.current_index]}"
        self.info_label.config(text=info_text)

# Główny program
if __name__ == "__main__":
    root = tk.Tk()
    root.state("zoomed")
    app = PanoramaRecenter(root)
    root.mainloop()
