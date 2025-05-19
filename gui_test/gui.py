import tkinter as tk
from tkinter import scrolledtext
from chatbot import load_history, save_history, generate_response

class CubeBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CubeBot 챗봇")

        self.messages = load_history()

        # 대화 출력 영역
        self.chat_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=25, state='disabled')
        self.chat_area.pack(padx=10, pady=10)

        # 입력창
        self.entry = tk.Entry(root, width=80)
        self.entry.pack(padx=10, pady=(0, 10))
        self.entry.bind("<Return>", self.send_message)

        # 인사말 표시
        self.insert_message("🤖 CubeBot", "CubeBot 챗봇에 오신 것을 환영합니다!\n(종료하려면 창을 닫으세요)\n")

    def insert_message(self, sender, message):
        self.chat_area.configure(state='normal')
        self.chat_area.insert(tk.END, f"{sender}: {message}\n")
        self.chat_area.configure(state='disabled')
        self.chat_area.see(tk.END)

    def send_message(self, event=None):
        user_input = self.entry.get().strip()
        if not user_input:
            return

        self.entry.delete(0, tk.END)
        self.insert_message("🙋 사용자", user_input)

        self.messages.append({"role": "user", "content": user_input})
        self.insert_message("🤖 CubeBot", "...답변 생성 중...")

        self.root.after(100, self.generate_response_async)

    def generate_response_async(self):
        self.chat_area.configure(state='normal')
        self.chat_area.delete("end-2l", tk.END)  # "답변 생성 중..." 제거
        self.chat_area.insert(tk.END, "\n🤖 CubeBot: ")

        full_reply = ""
        for chunk in generate_response(self.messages):
            token = chunk
            full_reply += token
            self.chat_area.insert(tk.END, token)
            self.chat_area.see(tk.END)
            self.root.update()

        self.chat_area.insert(tk.END, "\n")
        self.chat_area.configure(state='disabled')

        self.messages.append({"role": "assistant", "content": full_reply})
        save_history(self.messages)


if __name__ == "__main__":
    root = tk.Tk()
    app = CubeBotGUI(root)
    root.mainloop()
