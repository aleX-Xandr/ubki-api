from typing import Optional
from tkinter import filedialog
import tkinter as tk
import pandas as pd
import io
import json
import threading

from api import BaseApi
from frames import LoginFrame, FileFrame
from models.builder import DataBuilder 

class LoginApp(tk.Tk):
    token: Optional[str] = None

    def __init__(self) -> None:
        super().__init__()
        self.title("Login Interface")
        self.attributes('-fullscreen', True)
        self.file_frame = FileFrame(self)
        self.login_frame = LoginFrame(self) # init login frame

        if self.has_session():
            self.file_frame.pack(fill="both", expand=True, pady=100, padx=100)
            self.login_frame.pack_forget()
        else:
            self.file_frame.pack_forget()
            self.login_frame.pack(fill="both", expand=True, pady=100, padx=100)

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
        if file_path:
            with open(file_path, 'rb') as file:
                content = file.read()
                buffer = io.BytesIO(content)
                csv_data = pd.read_csv(buffer, encoding="Windows-1251", sep=";")
                csv_dicts = csv_data.to_dict(orient='records')
                csv_len = len(csv_dicts)
                for i, csv_dict in enumerate(csv_dicts):
                    person_object = self.build_task(csv_dict)
                    api = BaseApi(api_path="upload/data")
                    api.headers["SessId"] = self.token
                    resp_code, resp_data = api.send_data(person_object)
                    errors = resp_data['sentdatainfo']["items"]
                    separator = f"\n{'#'*20}\n({i+1}/{csv_len}) \nSTATUS:{resp_code} \nINN:{resp_data['sentdatainfo']['inn']}\n"
                    self.file_frame.output(f"\n\n{separator}\nВідправлені дані: {json.dumps(person_object, indent=4, ensure_ascii=False)}\nПомилки сервера: {json.dumps(errors, indent=4, ensure_ascii=False)}")
            self.file_frame.output("Відправлення даних завершено.")
        else:
            self.file_frame.output("Файл не був обраний.")

    def open_file(self):
        task = threading.Thread(target=self.file_task)
        task.start()

if __name__ == "__main__":
    app = LoginApp()
    app.bind_escape()
    app.mainloop()
