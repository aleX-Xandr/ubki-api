from typing import Optional
from tkinter import filedialog
import tkinter as tk
import pandas as pd
import io
import json
import threading

from api import BaseApi
from config import DEBUG_MODE
from frames import LoginFrame, FileFrame
from models.builder import DataBuilder 

class LoginApp(tk.Tk):
    token: Optional[str] = None

    def __init__(self) -> None:
        super().__init__()
        # Allow the window to be resized horizontally and vertically
        self.geometry("800x600")  # Set initial size
        self.minsize(400, 300)  # Set minimum size
        self.file_frame = FileFrame(self)
        self.login_frame = LoginFrame(self)

        if self.has_session():
            self.show_file_frame()
        else:
            self.show_login_frame()

    def show_file_frame(self):
        self.file_frame.pack(fill="both", expand=True, pady=10, padx=10)
        self.login_frame.pack_forget()
        self.title("Upload File")

    def show_login_frame(self):
        self.login_frame.pack(fill="both", expand=True, pady=10, padx=10)
        self.file_frame.pack_forget()
        self.title("Login Interface")

    def has_session(self) -> bool:
        try:
            with open("session.json", "r") as file:
                data = json.load(file)
            if self.login(**data):
                self.file_frame.output(data)
                return True
        except FileNotFoundError:
            pass
        except json.JSONDecodeError:
            self.login_frame.output("Перевірте файл session.json: Некоректний формат JSON")
        except Exception as e:
            self.login_frame.output(f"Сталася помилка: {e}")
        return False
        
    def login(self, username, password) -> bool:
        api = BaseApi(api_path="b2_api_xml/ubki/auth")
        resp_data = api.authorize(username, password)
        if not resp_data:
            return False
        
        auth_data = resp_data["doc"]["auth"]
        if "errcode" in auth_data:
            self.login_frame.output(f"Сталася помилка: {auth_data.get('errtext')}")
            return False
        
        with open("session.json", "w") as file:
            json.dump({"username": username, "password": password}, file)

        self.token = auth_data["sessid"]
        self.login_frame.pack_forget()
        self.file_frame.pack(fill="both", expand=True, pady=100, padx=100)
        return True
        
    def build_task(self, csv_dict: dict) -> dict:
        builder = DataBuilder(csv_dict)
        builder.build()
        return builder.as_dict

    def exit_fullscreen(self, event):
        self.attributes('-fullscreen', False)
        self.quit()

    def bind_escape(self):
        self.bind("<Escape>", self.exit_fullscreen)

    # form endpoints

    def authorize(self):
        username = self.login_frame.entry_username.get()
        password = self.login_frame.entry_password.get()
        return self.login(username, password)

    def file_task(self) -> None:
        file_path = filedialog.askopenfilename(title="Виберіть файл")
        self.file_frame.output_field.delete(1.0, tk.END)
        if not file_path:
            self.file_frame.output("Файл не був обраний.")
            return
    
        with open(file_path, 'rb') as file:
            content = file.read()
        buffer = io.BytesIO(content)
        csv_data = pd.read_csv(buffer, encoding="Windows-1251", sep=";")
        csv_dicts = csv_data.to_dict(orient='records')
        csv_len = len(csv_dicts)
        success_users = 0
        for i, csv_dict in enumerate(csv_dicts):
            person_object = self.build_task(csv_dict)
            api = BaseApi(api_path="upload/data")
            api.headers["SessId"] = self.token
            resp_code, resp_data = api.send_data(person_object)
            errors = resp_data['sentdatainfo']["items"]
            errors.sort(key=lambda error: error["errtype"])
            if resp_code < 300:
                status = "БЕЗ ПОМИЛОК"
                success_users += 1
            else:
                status = "НАЯВНI ПОМИЛКИ"
            if DEBUG_MODE:
                separator = f"\n({i+1}/{csv_len}), STATUS:{status}, INN:{person_object['data']['fo_cki']['inn']}\nВідправлені дані: {json.dumps(person_object, indent=4, ensure_ascii=False)}\nПомилки сервера: {json.dumps(errors, indent=4, ensure_ascii=False)}"
            else:
                error_text = errors[0]["msg"] # json.dumps(error, indent=4, ensure_ascii=False)
                separator = f"\n({i+1}/{csv_len}) STATUS:{status}, INN:{person_object['data']['fo_cki']['inn']}\n{error_text}" # remove "{}" symbols from json dump
            self.file_frame.output(f"{separator}") #\nВідправлені дані: {json.dumps(person_object, indent=4, ensure_ascii=False)}\nПомилки сервера: {json.dumps(errors, indent=4, ensure_ascii=False)}")
        self.file_frame.output(f"\n\nВідправлення даних завершено. Успішно: {success_users} з {csv_len}")

    def open_file(self):
        task = threading.Thread(target=self.file_task)
        task.start()

if __name__ == "__main__":
    app = LoginApp()
    app.bind_escape()
    app.mainloop()
