from typing import Optional
from tkinter import filedialog

import concurrent.futures
import io
import json
import pandas as pd
import threading
import tkinter as tk

from components.api import Client
from components.builder import DataBuilder
from components.frames import FileFrame, LoginFrame
from components.logger import Logger
from config import DEBUG_MODE, MAX_THREADS, MESSAGE_TEMPLATE

logger = Logger()

class LoginApp(tk.Tk):
    token: Optional[str] = None
    success_users: int = 0
    log_dump: str = ""

    def __init__(self) -> None:
        super().__init__()
        self.geometry("800x600") # встановлюємо початковий розмір
        self.minsize(400, 300) # встановлюємо мінімальний розмір
        self.file_frame = FileFrame(self)
        self.login_frame = LoginFrame(self)

        if self.has_session(): # Пропуск авторизації
            self.show_file_frame()  
        else:
            self.show_login_frame()

    def show_file_frame(self) -> None:
        self.file_frame.pack(fill="both", expand=True, pady=10, padx=10)
        self.login_frame.pack_forget()
        self.title("Upload File")

    def show_login_frame(self) -> None:
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
        api = Client(api_path="b2_api_xml/ubki/auth")
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
        self.file_frame.pack(fill="both", expand=True, pady=10, padx=10)
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

    def send_build(self, csv_dict: dict) -> bool:
        person_object = self.build_task(csv_dict)
        api = Client(api_path="upload/data")
        api.headers["SessId"] = self.token
        resp_code, resp_data = api.send_data(person_object)
        errors = resp_data['sentdatainfo']["items"]
        errors.sort(key=lambda error: error["errtype"])
        resp_status = resp_code > 300
        if resp_status:
            status = "БЕЗ ПОМИЛОК"
        else:
            status = "НАЯВНI ПОМИЛКИ"
        self.log_dump += f"\nSTATUS:{status} {resp_code}, INN:{person_object['data']['fo_cki']['inn']}\nВідправлені дані: {json.dumps(person_object, indent=4, ensure_ascii=False)}\nПомилки сервера: {json.dumps(errors, indent=4, ensure_ascii=False)}"
        error_text = errors[0]["msg"] # json.dumps(error, indent=4, ensure_ascii=False)
        result = MESSAGE_TEMPLATE.format(
            status=status, 
            data=json.dumps(person_object, indent=4, ensure_ascii=False),
            error=error_text, 
            all_errors=json.dumps(errors, indent=4, ensure_ascii=False),
            inn=person_object['data']['fo_cki']['inn'], 
            response_code=resp_code,
        )
        self.file_frame.progress_bar.progress += 1
        self.file_frame.output(f"\n{result}")
        print("PROGRESS: ", self.file_frame.progress_bar.progress)
        if self.file_frame.progress_bar.progress % 100 == 0:
            logger.save(self.file_frame.output_field.get("1.0", tk.END).strip())
            logger.save_full(self.log_dump)
            self.log_dump = ""
            self.file_frame.output_field.delete(1.0, tk.END)
        self.file_frame.result_label.config(
            text=f"Всього/Відправлено/Успішно: {self.file_frame.progress_bar.max}/{self.file_frame.progress_bar.progress}/{self.success_users}"
        ) 
        self.update_idletasks()
        return resp_status


    def file_task(self) -> None:
        file_path = filedialog.askopenfilename(title="Виберіть файл")
        logger.refresh()
        self.log_dump = ""
        self.file_frame.output_field.delete(1.0, tk.END)
        self.success_users = 0
        if not file_path:
            self.file_frame.output("Файл не був вибраний.")
            return
    
        with open(file_path, 'rb') as file:
            content = file.read()
        buffer = io.BytesIO(content)
        csv_data = pd.read_csv(buffer, encoding="Windows-1251", sep=";")
        csv_dicts = csv_data.to_dict(orient='records')
        self.file_frame.progress_bar.max = len(csv_dicts)

        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
            futures = [executor.submit(self.send_build, csv_dict) for csv_dict in csv_dicts]

        for future in concurrent.futures.as_completed(futures):
            if future.result():
                self.success_users += 1

        self.file_frame.output(f"\n\nВідправлення даних завершено. Успішно: {self.success_users} з {self.file_frame.progress_bar.max}")
        logger.save(self.file_frame.output_field.get("1.0", tk.END).strip())
        logger.save_full(self.log_dump)

    def open_file(self):
        task = threading.Thread(target=self.file_task)
        task.start()

if __name__ == "__main__":
    app = LoginApp()
    app.bind_escape()
    app.mainloop()
