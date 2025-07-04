import base64
import io
import os
from socket import socket, AF_INET, SOCK_STREAM
from customtkinter import *
import threading
from tkinter import filedialog
from PIL import Image


class MainWindow(CTk):
    def __init__(self):
        super().__init__()
        self.geometry("400x300")
        self.label = None
        self.username = "No name"
        self.menu_frame = CTkFrame(self, width=30, height=300, fg_color="blue")
        self.menu_frame.pack_propagate(False)
        self.menu_frame.place(x=0, y=0)
        self.is_show_menu = False
        self.speed_animate_menu = -5

        self.btn = CTkButton(self, text="▶️", command=self.toggle_show_menu, width=30)
        self.btn.place(x=0, y=0)


        self.chat_field = CTkScrollableFrame(self, fg_color="#87CEFA")
        self.chat_field.place(x=0, y=0)

        self.message_entry = CTkEntry(
            self, placeholder_text="Введіть повідомлення:", height=40
        )
        self.message_entry.place(x=0, y=0)

        self.send_button = CTkButton(self, text=">", width=50, height=40, command=self.send_message)
        self.send_button.place(x=0, y=0)

        self.open_img_button = CTkButton(self, text="3", width=50, height=40, command=self.open_image)
        self.open_img_button.place(x=0, y=0)

        EMOJI
        self.emoji_button = CTkButton(self, text="😊", width=40, height=40, command=self.toggle_emoji_menu)
        self.emoji_button.place(x=0, y=0)

        self.emoji_menu = CTkFrame(self, fg_color="#ADD8E6", corner_radius=10, border_width=1, border_color="grey")
        self.emoji_menu.place_forget()

        self.emojis = [
            ("😀", "#FFD700"),
            ("😂", "#FFA500"),
            ("😍", "#FF69B4"),
            ("😎", "#00BFFF"),
            ("🤔", "#9370DB"),
            ("😭", "#1E90FF"),
        ]
        for i, (emoji, color) in enumerate(self.emojis):
            btn = CTkButton(self.emoji_menu, text=emoji, fg_color=color, width=40, height=40,
                            command=lambda e=emoji: self.insert_emoji(e))
            btn.grid(row=0, column=i, padx=3, pady=3)

        self.is_emoji_menu_shown = False

        self.adaptive_ui()
        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect(("localhost", 8080))
            hello = f"TEXT@{self.username}@[SYSTEM] {self.username} приєднався до чату!\n"
            self.sock.send(hello.encode('utf-8'))
            threading.Thread(target=self.recv_message, daemon=True).start()
        except Exception as e:
            self.add_message(f"помилка: {e}")

    def add_message(self, message, img=None):
        message_frame = CTkFrame(self.chat_field, fg_color="grey")
        message_frame.pack(pady=5, anchor="w")
        wrapleng_size = self.winfo_width() - self.menu_frame.winfo_width() - 40

        if not img:
            CTkLabel(message_frame, text=message, wraplength=wrapleng_size, text_color='white', justify='left').pack(
                padx=10, pady=5)
        else:
            CTkLabel(message_frame, text=message, wraplength=wrapleng_size, text_color="white", justify="left",
                     image=img, compound="top").pack(padx=10, pady=5)

    def send_message(self):
        message = self.message_entry.get()
        if message:
            self.add_message(f"{self.username}: {message}")
            data = f"TEXT@{self.username}@{message}\n"
            try:
                self.sock.sendall(data.encode())
            except:
                pass
        self.message_entry.delete(0, END)

    def recv_message(self):
        buffer = ""
        while True:
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                buffer += chunk.decode(errors='ignore')

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.handle_line(line.strip())
            except:
                break
        self.sock.close()

    def handle_line(self, line):
        if not line:
            return
        parts = line.split("@", 3)  # parts = ["тип смс", "имя", "смс"]
        msg_type = parts[0]
        if msg_type == "TEXT":
            author = parts[1]
            message = parts[2]
            self.add_message(f"{author}: {message}")
        elif msg_type == "IMAGE":
            author = parts[1]
            filename = parts[2]
            b64_img = parts[3]
            try:
                img_data = base64.b64decode(b64_img)
                pil_img = Image.open(io.BytesIO(img_data))
                ctk_img = CTkImage(pil_img, size=(300, 300))
                self.add_message(f"{author}, надіслав зображення: {filename}", img=ctk_img)
            except:
                self.add_message(f"Помилка відображення картинки")

    def open_image(self):
        file_name = filedialog.askopenfilename()
        if not file_name:
            return

        with open(file_name, "rb") as f:
            raw = f.read()
        b64_data = base64.b64encode(raw).decode()
        short_name = os.path.basename(file_name)
        data = f"IMAGE@{self.username}@{short_name}@{b64_data}\n"

        self.sock.sendall(data.encode())

        self.add_message('', CTkImage(light_image=Image.open(file_name), size=(300, 300)))

    def toggle_show_menu(self):
        if self.is_show_menu:
            self.is_show_menu = False
            self.speed_animate_menu *= -1
            self.btn.configure(text="▶️")
            self.show_menu()
        else:
            self.is_show_menu = True
            self.speed_animate_menu *= -1
            self.btn.configure(text="◀️")
            self.show_menu()
            # setting menu widgets
            self.label = CTkLabel(self.menu_frame, text="Імʼя")
            self.label.pack(pady=30)
            self.entry = CTkEntry(self.menu_frame, placeholder_text="Ваш нік...")
            self.entry.pack()
            self.save_name_button = CTkButton(self.menu_frame, text="Зберегти", command=self.save_name)
            self.save_name_button.pack()

    def save_name(self):
        new_name = self.entry.get().strip()
        if new_name:
            self.username = new_name
            self.add_message(f"Ваш новий нік: {self.username}")

    def show_menu(self):
        self.menu_frame.configure(
            width=self.menu_frame.winfo_width() + self.speed_animate_menu
        )
        if not self.menu_frame.winfo_width() >= 200 and self.is_show_menu:
            self.after(10, self.show_menu)
        elif self.menu_frame.winfo_width() >= 40 and not self.is_show_menu:
            self.after(10, self.show_menu)
            if self.label and self.entry:
                self.label.destroy()
                self.entry.destroy()
                self.save_name_button.destroy()

    def adaptive_ui(self):
        self.menu_frame.configure(height=self.winfo_height())
        self.chat_field.place(x=self.menu_frame.winfo_width())
        self.chat_field.configure(
            width=self.winfo_width() - self.menu_frame.winfo_width() - 20,
            height=self.winfo_height() - 40,
        )
        self.send_button.place(x=self.winfo_width() - 50, y=self.winfo_height() - 40)
        self.message_entry.place(
            x=self.menu_frame.winfo_width() - 5, y=self.send_button.winfo_y()
        )
        self.message_entry.configure(
            width=self.winfo_width()
                  - 195
        )
        self.open_img_button.place(x=self.winfo_width() - 105, y=self.send_button.winfo_y())
        self.emoji_button.place(x=self.winfo_width() - 145, y=self.send_button.winfo_y())
        self.after(50, self.adaptive_ui)

    def toggle_emoji_menu(self):
        if self.is_emoji_menu_shown:
            self.emoji_menu.place_forget()
            self.is_emoji_menu_shown = False
        else:
            x = self.emoji_button.winfo_x()
            y = self.emoji_button.winfo_y() - 50
            self.emoji_menu.place(x=x, y=y)
            self.is_emoji_menu_shown = True

    def insert_emoji(self, emoji):
        current = self.message_entry.get()
        self.message_entry.delete(0, END)
        self.message_entry.insert(0, current + emoji)
        self.toggle_emoji_menu()


if __name__ == "__main__":
    win = MainWindow()
    win.mainloop()
