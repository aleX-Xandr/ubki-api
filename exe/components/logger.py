


class Logger:

    def refresh(self):
        with open("full-log.txt", "w", encoding="utf-8") as file:
            file.write("")
            
        with open("log.txt", "w", encoding="utf-8") as file:
            file.write("")

    def save(self, text:str):
        with open("log.txt", 'a', encoding="utf-8") as file:
            file.write(text)

    def save_full(self, text:str):
        with open("full-log.txt", 'a', encoding="utf-8") as file:
            file.write(text)