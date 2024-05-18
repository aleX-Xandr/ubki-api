import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

__ALL__ = ["FormLabel", "FormInput", "FormButton", "FormText"]

class FormLabel(ttk.Label):
    def __init__(self, frame, text):
        super().__init__(frame, text=text)
        self.pack()

class FormInput(ttk.Entry):
    def __init__(self, frame, text, width):
        input_frame = ttk.Frame(frame)
        input_frame.pack(fill='x', padx=10, pady=5)
        self.form_label = ttk.Label(input_frame, text=text)
        self.form_label.pack()
        super().__init__(input_frame, width=width)
        self.pack(pady=10)

class FormButton(ttk.Button):
    def __init__(self, frame, text, callback):
        super().__init__(frame, text=text, command=callback)
        self.pack(pady=10)

class FormProgressBar(ttk.Progressbar):
    def __init__(self, frame, progress: int = 0, max: int = 100, **kwargs: dict):
        super().__init__(frame, **kwargs)
        self.pack(fill='x', pady=10)
        self.progress = progress
        self.max = max
    
    @property
    def progress(self) -> int:
        return self['value']
    
    @progress.setter
    def progress(self, new_value: int):
        self['value'] = new_value

    @property
    def max(self) -> int:
        return self["maximum"]
    
    @max.setter
    def max(self, new_value: int) -> None:
        self['maximum'] = new_value
        self['value'] = 0

class FormText(ScrolledText):
    def __init__(self, frame, **kwargs: dict):
        super().__init__(frame, wrap=tk.WORD)
        self.pack(**kwargs)
