import pygame
from tkinter import *
from tkinter import messagebox
import random
from time import sleep
import json
import os

class Game():
  def playsound(self, path):
    pygame.mixer.Sound(path).play()

  def playbgm(self, path):
    pygame.mixer.Sound(path).play(loops=-1)

  def ansm(self):
    try:
      question_n = int(self.aqnnum.get())
      self.aqnnum.delete(0, END)
    except ValueError:
      messagebox.showerror("error","問題数には数字を入力してください。")
      self.aqnnum.delete(0, END)
      self.aqncanvas.pack_forget()
      self.home_canvas.pack(fill="both",expand=True)
      self.playsound((self.currentdir + "gui/bgm/opening.wav"))
      return
    syn = False
    if len(self.wrong) > 0:
        syn = messagebox.askyesno("確認", "このモードを開始すると、現在の間違い直しデータが上書きされます。\n本当に開始しますか？")
    else:
        syn = True
    if syn:
        self.playbgm((self.currentdir + "gui/bgm/bgm.wav"))
        self.wrong = []
        self.aqncanvas.pack_forget()
        self.aq_canvas.pack()
        collect = 0
        self.playsound((self.currentdir + "gui/se/question.wav"))
        for i in range(question_n):
          if i > 0:
            answer = self.aq_entry.get()
            if self.words[current_key] == answer:
                self.playsound((self.currentdir + "gui/se/collect.wav"))
                self.aq_res_label["text"] = "正解！！"
                self.aq_res_label.update()
                collect += 1
            else:
                self.playsound((self.currentdir + "gui/se/wrong.wav"))
                self.aq_res_label["text"] = "不正解（正答：" + self.words[current_key] + "）"
                self.aq_res_label.update()
                self.wrong.append(self.keys_list[question_index])
          self.aq_entry.delete(0, END)
          question_index = random.randint(0,len(self.keys_list) - 1) # Generate a random index for the self.keys_list
          current_key = self.keys_list[question_index] # Get the key using the random index
          self.aq_label["text"] = current_key + "  （" + str(question_n - i) + "）" # Print the Japanese word (key)
          self.aq_label.update()
          self.aq_canvas.wait_variable(self.aq_sub_var)
          self.aq_sub_var.set(False)
          if i == question_n - 1:
            self.stopsound()
            answer = self.aq_entry.get()
            if self.words[current_key] == answer:
                self.playsound((self.currentdir + "gui/se/collect.wav"))
                collect += 1
            else:
                self.playsound((self.currentdir + "gui/se/wrong.wav"))
                self.wrong.append(self.keys_list[question_index])
        self.aq_canvas.pack_forget()
        self.res_canvas.pack()
        self.res_per["text"] = "正答率：" + str(collect) + "/" + str(question_n) + ", " + str(round((collect / question_n) * 100)) + "%"
        self.res_per.pack(pady=10)
        a = 0
        if len(self.wrong) > 0:
          while a == len(self.wrong):
            if self.wrong.count(self.wrong[a]) > 1:
              for j in range(self.wrong.count(self.wrong[a]) - 1):
                self.wrong.remove(self.wrong[a])
                a -= 1
            a += 1
          self.wrong_disp = []
          for i in self.wrong:
            umeru = 50 - len(i) - round(len(self.words[i]) * 0.8)
            self.wrong_disp.append(i + self.words[i].rjust(umeru))
          self.res_label["text"] = "苦手な単語"
          self.res_label.pack(pady=10)
          self.res_list_var.set(self.wrong_disp)
          self.res_list.pack(pady=10)
        else:
          self.res_label["text"] = "★間違いなし★"
          self.res_label.pack(pady=10)

        with open("self.wrong.json", "w", encoding="utf-8") as f:
            json.dump(self.wrong, f, ensure_ascii=False, indent=4)
        if len(self.wrong) > 0:
          self.home_wro_button["state"] = 'normal'
        else:
          self.home_wro_button["state"] = 'disabled'
        self.res_bac_button.pack(pady=10)

  def wrongm(self):
    self.playbgm((self.currentdir + "gui/bgm/bgm.wav"))
    self.home_canvas.pack_forget()
    self.aq_canvas.pack()
    self.wrong_wrong = []
    collect = 0
    question_n = len(self.wrong)
    self.playsound((self.currentdir + "gui/se/question.wav"))
    for i in range(question_n):
      if i > 0:
        answer = self.aq_entry.get()
        if self.words[current_key] == answer:
            self.playsound((self.currentdir + "gui/se/collect.wav"))
            self.aq_res_label["text"] = "正解！！"
            self.aq_res_label.update()
            collect += 1
        else:
            self.playsound((self.currentdir + "gui/se/wrong.wav"))
            self.aq_res_label["text"] = "不正解（正答：" + self.words[current_key] + "）"
            self.aq_res_label.update()
            self.wrong_wrong.append(self.wrong[i])
      self.aq_entry.delete(0, END)
      current_key = self.wrong[i] # Get the key using the random index
      self.aq_label["text"] = current_key + "  （" + str(question_n - i) + "）" # Print the Japanese word (key)
      self.aq_label.update()
      self.aq_canvas.wait_variable(self.aq_sub_var)
      self.aq_sub_var.set(False)
      if i == question_n - 1:
        answer = self.aq_entry.get()
        if self.words[current_key] == answer:
            self.playsound((self.currentdir + "gui/se/collect.wav"))
            self.aq_res_label["text"] = "正解！！"
            self.aq_res_label.update()
            collect += 1
        else:
            self.playsound((self.currentdir + "gui/se/wrong.wav"))
            self.aq_res_label["text"] = "不正解（正答：" + self.words[current_key] + "）"
            self.aq_res_label.update()
            self.wrong_wrong.append(self.wrong[i])
    self.aq_canvas.pack_forget()
    self.stopsound()
    self.res_canvas.pack()
    self.res_per["text"] = "正答率：" + str(collect) + "/" + str(question_n) + ", " + str(round((collect / question_n) * 100)) + "%"
    self.res_per.pack(pady=10)
    a = 0
    if len(self.wrong_wrong) > 0:
      self.wrong_disp = []
      for i in self.wrong_wrong:
        umeru = 50 - len(i) - len(self.words[i])
        self.wrong_disp.append(i + self.words[i].rjust(umeru))
      self.res_label["text"] = "復習不足な単語"
      self.res_label.pack(pady=10)
      self.res_list_var.set(self.wrong_disp)
      self.res_list.pack(pady=10)
    else:
      self.res_label["text"] = "★復習完了★"
      self.res_label.pack(pady=10)
    
    with open("self.wrong.json", "w", encoding="utf-8") as f:
        json.dump(self.wrong_wrong, f, ensure_ascii=False, indent=4)
    if len(self.wrong) > 0:
        self.home_wro_button["state"] = 'normal'
    else:
        self.home_wro_button["state"] = 'disabled'
    self.res_bac_button.pack(pady=10)
    
  def __init__(self):
    # self.currentdirは必要に応じてスクリプトフォルダの絶対パスに変更してください。
    self.currentdir = ""
    print("システム準備中...")
    print("変数初期化中...")
    self.keys_list = []
    self.keys_list_dic = []
    self.stopsound = pygame.mixer.stop
    
    print("オーディオシステム初期化中...")
    pygame.init()
    pygame.mixer.init()

    print("単語データ読み込み中...")
    try:
        with open((self.currentdir + "words.json"), "r", encoding="utf-8") as f:
            self.words = json.load(f)
    except FileNotFoundError:
        messagebox.showerror("error","words.jsonが見つかりません。プログラムを終了します。")
        exit()
    except json.JSONDecodeError:
        messagebox.showerror("error","words.jsonの読み込み中にエラーが発生しました。プログラムを終了します。")
        exit()
    except Exception as e:
        messagebox.showerror("error",f"予期せぬエラーが発生しました: {e}. プログラムを終了します。")
        exit()


    print("間違い直しデータ読み込み中...")
    try:
        with open("wrong.json", "r", encoding="utf-8") as f:
            self.wrong = json.load(f)
    except FileNotFoundError:
        self.wrong = []
        with open((self.currentdir + "wrong.json"), "w", encoding="utf-8") as f:
            json.dump(self.wrong, f, ensure_ascii=False, indent=4)
    except json.JSONDecodeError:
        messagebox.showerror("error","wrong.jsonの読み込み中にエラーが発生しました。プログラムを終了します。")
        exit()
    except Exception as e:
        messagebox.showerror("error",f"予期せぬエラーが発生しました: {e}. プログラムを終了します。")
        exit()

    self.wrong_wrong = []
    self.keys_list = list(self.words.keys()) # Convert dict_keys to a list once
    for i in self.keys_list:
        umeru = 50 - len(i) - len(self.words[i])
        self.keys_list_dic.append(i + self.words[i].rjust(umeru))
    
    print("gui起動中...")
    
    self.gui = Tk()
    self.gui.title("単語特訓ヘルパー")
    self.gui.geometry("400x400")
    self.gui.resizable(False, False)
    self.gui.protocol("WM_DELETE_WINDOW", lambda: os._exit(0))

    self.home_canvas = Canvas(self.gui, width=400, height=400)
    self.home_title = Label(self.home_canvas, text="単語特訓ヘルパー", font=("MS Gothic", 20, 'bold'),bg="aqua")
    self.home_dic_button = Button(self.home_canvas, text="単語記憶", font=("MS Gothic", 15),command=lambda: [self.home_canvas.pack_forget(), self.dic_canvas.pack(),self.stopsound()])
    self.home_ans_button = Button(self.home_canvas, text="単語回答", font=("MS Gothic", 15),command=lambda: [self.home_canvas.pack_forget(), self.aqncanvas.pack(),self.stopsound()])
    self.home_wro_button = Button(self.home_canvas, text="間違い直し", font=("MS Gothic", 15),command=lambda: [self.wrongm(),self.stopsound()])
    self.home_title.pack(pady=20)
    self.home_dic_button.pack(pady=10)
    self.home_ans_button.pack(pady=10)
    self.home_wro_button.pack(pady=10)
    self.home_canvas.pack(fill="both",expand=True)
    self.home_bg = PhotoImage(file=(self.currentdir + "gui/bg/home_back.png"))
    self.home_canvas.create_image(0,0,image=self.home_bg)

    self.dic_canvas = Canvas(self.gui, width=400, height=400)
    self.dic_var = StringVar(self.dic_canvas,value=self.keys_list_dic)
    self.dic_list = Listbox(self.dic_canvas, font=("MS Gothic", 12),width=50,listvariable=self.dic_var)
    self.dic_clo_button = Button(self.dic_canvas, text="閉じる", font=("MS Gothic", 15), command=lambda: [self.dic_canvas.pack_forget(), self.home_canvas.pack(fill="both",expand=True),self.playsound((self.currentdir + "gui/bgm/opening.wav"))])
    self.dic_list.pack(pady=20)
    self.dic_clo_button.pack(pady=10)

    self.aqncanvas = Canvas(self.gui, width=400, height=400)
    self.aqnlabel_text = "問題数を入力してください\n（最大：" + str(len(self.keys_list)) + "）"
    self.aqnlabel = Label(self.aqncanvas, text=self.aqnlabel_text, font=("MS Gothic", 15))
    self.aqnnum = Entry(self.aqncanvas, font=("MS Gothic", 15))
    self.aqnnum.bind("<KeyPress-Return>", lambda event: self.ansm())
    self.aqnenter = Button(self.aqncanvas, text="開始", font=("MS Gothic", 15),command=self.ansm)
    self.aqncancel = Button(self.aqncanvas, text="キャンセル", font=("MS Gothic", 15), command=lambda: [self.aqncanvas.pack_forget(), self.home_canvas.pack(fill="both",expand=True),self.playsound((self.currentdir + "gui/bgm/opening.wav"))])
    self.aqnlabel.pack(pady=20)
    self.aqnnum.pack(pady=10)
    self.aqnenter.pack(pady=10)
    self.aqncancel.pack(pady=10)

    self.aq_canvas = Canvas(self.gui, width=400, height=400)
    self.aq_label = Label(self.aq_canvas, text="問題文", font=("MS Gothic", 20))
    self.aq_entry = Entry(self.aq_canvas, font=("MS Gothic", 15))
    self.aq_entry.bind("<KeyPress-Return>", lambda event: self.aq_sub_var.set(True))
    self.aq_sub_var = BooleanVar(self.aq_canvas,value=False)
    self.aq_submit = Button(self.aq_canvas, text="解答", font=("MS Gothic", 15),command=lambda: self.aq_sub_var.set(True))
    self.aq_res_label = Label(self.aq_canvas, text="ここには前の問題の正誤が入ります", font=("MS Gothic", 10))
    self.aq_label.pack(pady=20)
    self.aq_entry.pack(pady=10)
    self.aq_submit.pack(pady=10)
    self.aq_res_label.pack(pady=10)

    self.res_canvas = Canvas(self.gui, width=400, height=400)
    self.res_title = Label(self.res_canvas, text="結果", font=("MS Gothic", 20))
    self.res_per = Label(self.res_canvas, text="正答率： ", font=("MS Gothic", 15))
    self.res_label = Label(self.res_canvas, text="苦手な単語", font=("MS Gothic", 15))
    self.res_list_var = StringVar(self.res_canvas)
    self.res_list = Listbox(self.res_canvas, font=("MS Gothic", 12),width=50,listvariable=self.res_list_var,height=7)
    self.res_bac_button = Button(self.res_canvas, text="戻る", font=("MS Gothic", 15), command=lambda: [self.res_canvas.pack_forget(), self.home_canvas.pack(fill="both",expand=True),self.playsound((self.currentdir + "gui/bgm/opening.wav"))])
    self.res_title.pack(pady=20)
    
    self.playsound((self.currentdir + "gui/bgm/opening.wav"))
    if len(self.wrong) > 0:
      self.home_wro_button["state"] = 'normal'
    else:
      self.home_wro_button["state"] = 'disabled'
    
    self.gui.mainloop()

if __name__ == "__main__":
  Game()
  