from tkinter import ttk

from components.ui_components import *

class LoginFrame(ttk.Frame):
    def __init__(self, app):
        super().__init__(app)
        
        self.entry_username = FormInput(
            self, text="Логін:", width=30
        )
        self.entry_password = FormInput(
            self, text="Пароль:", width=30
        )
        self.auth_button = FormButton(
            self, text="Авторизуватися", callback=app.authorize
        )
        self.output_field = FormText(self, pady=10, padx=10)
        self.output_field.pack_forget()
        
        self.pack_propagate(False)
        self.pack(fill="both", expand=True)
        
    def output(self, content):
        self.output_field.insert(tk.END, f"\n{content}")
        self.output_field.pack()

class FileFrame(ttk.Frame):
    def __init__(self, app):
        super().__init__(app)
        
        self.choose_file_button = FormButton(
            self, text="Вибрати файл", callback=app.open_file
        )
        self.output_field = FormText(
            self, fill="both", expand=True, pady=10, padx=10
        )
        self.progress_bar = FormProgressBar(
            self, orient="horizontal", mode="determinate"
        )
        self.result_label = FormLabel(
            self, text="Всього/Відправлено/Успішно:"
        )
        
        self.pack_propagate(False)
        self.pack(fill="both", expand=True)

    def output(self, content):
        self.output_field.insert(tk.END, content)
