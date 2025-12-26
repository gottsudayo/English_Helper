print("システム準備中...")
import pygame
from tkinter import *
from tkinter import messagebox
import random
from time import sleep
import json
import os
import sys

# currentdirは必要に応じてスクリプトフォルダの絶対パスに変更してください。
currentdir = ""
# AI-ModeはTrueで有効、Falseで無効化です。
# 使用できるAIはGeminiのみです。
# Trueに設定した場合はトークン等も設定してください。
aimode = False
# Gemini APIトークンを""の中に記述してください。
ai_token = ""
# モデルに関しては、基本的に変更しないでください。一番長く使えるプランで十分です。
# Gemini 2.0 Flash-Liteは無料枠にて、1分間に30回、1日に1500回使えます。
# つまり、単純計算で連続50分使用すると制限されます。
ai_model = "gemini-2.0-flash-lite-preview-02-05"
# デフォルトのセリフを設定します。基本的にいじらない方がいいです。
ai_talk_a = "問題「"
ai_talk_b = "」の答えは「"
ai_talk_c = "」で合っているか、YesかNoで答えてください。余計な解説は一切要りません。YesかNoだけでいいです。"

class Same():
  def __init__(self):
    print("変数初期化中...")
    self.keys_list = []
    self.keys_list_dic = []
    self.words = {}
    self.wrong = []
    self.stopsound = pygame.mixer.stop
    self.ai = None
    
    if aimode:
      print("AIモードが有効になっています。")
      from google import genai
      try:
        self.ai = genai.Client(api_key=ai_token)
      except Exception as e:
        print(str(e))
        messagebox.showerror("error",f"Geminiの呼び出し中にエラーが出ました。\n{e}")
        exit()
    else:
      print("AIモードが無効になっています。")
        
      
    print("オーディオシステム初期化中...")
    pygame.init()
    pygame.mixer.init()

    print("単語データ読み込み中...")
    try:
        with open((currentdir + "words.json"), "r", encoding="utf-8") as f:
            self.words = json.load(f)
    except FileNotFoundError:
      print("words.jsonを生成中...")
      with open((currentdir + "words.json"), "w", encoding="utf-8") as f:
        json.dump(self.words, f, ensure_ascii=False, indent=4)
      messagebox.showinfo("info","words.jsonが見つからなかったため、新規作成しました。\n単語データを追加するには、editを実行してください。")
      exit()
    except json.JSONDecodeError:
      messagebox.showerror("error","words.jsonの読み込み中にエラーが発生しました。プログラムを終了します。")
      exit()
    except Exception as e:
      messagebox.showerror("error",f"予期せぬエラーが発生しました: {e}. プログラムを終了します。")
      exit()


    print("間違い直しデータ読み込み中...")
    try:
        with open((currentdir + "wrong.json"), "r", encoding="utf-8") as f:
            self.wrong = json.load(f)
    except FileNotFoundError:
        print("wrong.jsonを生成中...")
        with open((currentdir + "wrong.json"), "w", encoding="utf-8") as f:
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

class Game(Same):
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
      self.playsound((currentdir + "gui/bgm/opening.wav"))
      return
    syn = False
    if len(self.wrong) > 0:
        syn = messagebox.askyesno("確認", "このモードを開始すると、現在の間違い直しデータが上書きされます。\n本当に開始しますか？")
    else:
        syn = True
    if syn:
        self.playbgm((currentdir + "gui/bgm/bgm.wav"))
        self.wrong = []
        self.aqncanvas.pack_forget()
        self.aq_canvas.pack()
        collect = 0
        self.playsound((currentdir + "gui/se/question.wav"))
        for i in range(question_n):
          if i > 0:
            answer = self.aq_entry.get()
            if aimode:
              try:
                ai_content = ai_talk_a + self.words[current_key] + ai_talk_b + answer + ai_talk_c
                ai_answer = self.ai.models.generate_content(model=ai_model,contents=ai_content)
                if ai_answer.text == "Yes":
                  self.playsound((currentdir + "gui/se/collect.wav"))
                  self.aq_res_label["text"] = "正解！！"
                  self.aq_res_label.update()
                  collect += 1
                else:
                  self.playsound((currentdir + "gui/se/wrong.wav"))
                  self.aq_res_label["text"] = "不正解（正答：" + self.words[current_key] + "）"
                  self.aq_res_label.update()
                  self.wrong.append(self.keys_list[question_index])
              except Exception as e:
                print(str(e))
                messagebox.showerror("error",f"Geminiの使用中にエラーが出ました。\n{e}")
                exit()
            else:
              if self.words[current_key] == answer:
                self.playsound((currentdir + "gui/se/collect.wav"))
                self.aq_res_label["text"] = "正解！！"
                self.aq_res_label.update()
                collect += 1
              else:
                self.playsound((currentdir + "gui/se/wrong.wav"))
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
            if aimode:
              try:
                ai_content = ai_talk_a + self.words[current_key] + ai_talk_b + answer + ai_talk_c
                ai_answer = self.ai.models.generate_content(model=ai_model,contents=ai_content)
                if ai_answer.text == "Yes":
                  self.playsound((currentdir + "gui/se/collect.wav"))
                  self.aq_res_label["text"] = "正解！！"
                  self.aq_res_label.update()
                  collect += 1
                else:
                  self.playsound((currentdir + "gui/se/wrong.wav"))
                  self.aq_res_label["text"] = "不正解（正答：" + self.words[current_key] + "）"
                  self.aq_res_label.update()
                  self.wrong.append(self.keys_list[question_index])
              except Exception as e:
                print(str(e))
                messagebox.showerror("error",f"Geminiの使用中にエラーが出ました。\n{e}")
                exit()
            else:
              if self.words[current_key] == answer:
                self.playsound((currentdir + "gui/se/collect.wav"))
                self.aq_res_label["text"] = "正解！！"
                self.aq_res_label.update()
                collect += 1
              else:
                self.playsound((currentdir + "gui/se/wrong.wav"))
                self.aq_res_label["text"] = "不正解（正答：" + self.words[current_key] + "）"
                self.aq_res_label.update()
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
            umeru = round(45 - len(i) - (len(self.words[i]) * 0.5))
            self.wrong_disp.append(i + self.words[i].rjust(umeru))
          self.res_label["text"] = "苦手な単語"
          self.res_label.pack(pady=10)
          self.res_list_var.set(self.wrong_disp)
          self.res_list.pack(pady=10)
        else:
          self.res_label["text"] = "★間違いなし★"
          self.res_label.pack(pady=10)

        with open("wrong.json", "w", encoding="utf-8") as f:
            json.dump(self.wrong, f, ensure_ascii=False, indent=4)
        if len(self.wrong) > 0:
          self.home_wro_button["state"] = 'normal'
        else:
          self.home_wro_button["state"] = 'disabled'
        self.res_bac_button.pack(pady=10)

  def wrongm(self):
    self.stopsound()
    self.playbgm((currentdir + "gui/bgm/bgm.wav"))
    self.home_canvas.pack_forget()
    self.aq_canvas.pack()
    self.wrong_wrong = []
    collect = 0
    question_n = len(self.wrong)
    self.playsound((currentdir + "gui/se/question.wav"))
    for i in range(question_n):
      if i > 0:
        answer = self.aq_entry.get()
        if aimode:
          try:
            ai_content = ai_talk_a + self.words[current_key] + ai_talk_b + answer + ai_talk_c
            ai_answer = self.ai.generate_content(model=ai_model,contents=ai_content)
            if ai_answer.text == "Yes":
              self.playsound((currentdir + "gui/se/collect.wav"))
              self.aq_res_label["text"] = "正解！！"
              self.aq_res_label.update()
              collect += 1
            else:
              self.playsound((currentdir + "gui/se/wrong.wav"))
              self.aq_res_label["text"] = "不正解（正答：" + self.words[current_key] + "）"
              self.aq_res_label.update()
              self.wrong_wrong.append(self.wrong[i])
          except Exception as e:
            print(str(e))
            messagebox.showerror("error",f"Geminiの使用中にエラーが出ました。\n{e}")
            exit()
        else:    
          if self.words[current_key] == answer:
            self.playsound((currentdir + "gui/se/collect.wav"))
            self.aq_res_label["text"] = "正解！！"
            self.aq_res_label.update()
            collect += 1
          else:
            self.playsound((currentdir + "gui/se/wrong.wav"))
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
        self.stopsound()
        answer = self.aq_entry.get()
        if aimode:
          try:
            ai_content = ai_talk_a + self.words[current_key] + ai_talk_b + answer + ai_talk_c
            ai_answer = self.ai.generate_content(model=ai_model,contents=ai_content)
            if ai_answer.text == "Yes":
              self.playsound((currentdir + "gui/se/collect.wav"))
              self.aq_res_label["text"] = "正解！！"
              self.aq_res_label.update()
              collect += 1
            else:
              self.playsound((currentdir + "gui/se/wrong.wav"))
              self.aq_res_label["text"] = "不正解（正答：" + self.words[current_key] + "）"
              self.aq_res_label.update()
              self.wrong_wrong.append(self.wrong[i])
          except Exception as e:
            print(str(e))
            messagebox.showerror("error",f"Geminiの使用中にエラーが出ました。\n{e}")
            exit()
        else:    
          if self.words[current_key] == answer:
            self.playsound((currentdir + "gui/se/collect.wav"))
            self.aq_res_label["text"] = "正解！！"
            self.aq_res_label.update()
            collect += 1
          else:
            self.playsound((currentdir + "gui/se/wrong.wav"))
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
        umeru = round(45 - len(i) - (len(self.words[i]) * 0.5))
        self.wrong_disp.append(i + self.words[i].rjust(umeru))
      self.res_label["text"] = "復習不足な単語"
      self.res_label.pack(pady=10)
      self.res_list_var.set(self.wrong_disp)
      self.res_list.pack(pady=10)
    else:
      self.res_label["text"] = "★復習完了★"
      self.res_label.pack(pady=10)
    
    with open((currentdir + "wrong.json"), "w", encoding="utf-8") as f:
        json.dump(self.wrong_wrong, f, ensure_ascii=False, indent=4)
    self.wrong = self.wrong_wrong
    if len(self.wrong) > 0:
        self.home_wro_button["state"] = 'normal'
    else:
        self.home_wro_button["state"] = 'disabled'
    self.res_bac_button.pack(pady=10)
    
  def __init__(self):
    super().__init__()
    print("gui起動中...")
    
    self.gui = Tk()
    self.gui.title("単語特訓ヘルパー 1.1.0")
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
    self.home_bg = PhotoImage(file=(currentdir + "gui/bg/home_back.png"))
    self.home_canvas.create_image(0,0,image=self.home_bg)

    self.dic_canvas = Canvas(self.gui, width=400, height=400)
    self.dic_var = StringVar(self.dic_canvas,value=self.keys_list_dic)
    self.dic_list = Listbox(self.dic_canvas, font=("MS Gothic", 12),width=50,listvariable=self.dic_var)
    self.dic_clo_button = Button(self.dic_canvas, text="閉じる", font=("MS Gothic", 15), command=lambda: [self.dic_canvas.pack_forget(), self.home_canvas.pack(fill="both",expand=True),self.playsound((currentdir + "gui/bgm/opening.wav"))])
    self.dic_list.pack(pady=20)
    self.dic_clo_button.pack(pady=10)

    self.aqncanvas = Canvas(self.gui, width=400, height=400)
    self.aqnlabel_text = "問題数を入力してください\n（最大：" + str(len(self.keys_list)) + "）"
    self.aqnlabel = Label(self.aqncanvas, text=self.aqnlabel_text, font=("MS Gothic", 15))
    self.aqnnum = Entry(self.aqncanvas, font=("MS Gothic", 15))
    self.aqnnum.bind("<KeyPress-Return>", lambda event: self.ansm())
    self.aqnenter = Button(self.aqncanvas, text="開始", font=("MS Gothic", 15),command=self.ansm)
    self.aqncancel = Button(self.aqncanvas, text="キャンセル", font=("MS Gothic", 15), command=lambda: [self.aqncanvas.pack_forget(), self.home_canvas.pack(fill="both",expand=True),self.playsound((currentdir + "gui/bgm/opening.wav"))])
    self.aqnlabel.pack(pady=20)
    self.aqnnum.pack(pady=10)
    self.aqnenter.pack(pady=10)
    self.aqncancel.pack(pady=10)

    self.aq_canvas = Canvas(self.gui, width=400, height=400)
    self.aq_label = Label(self.aq_canvas, text="問題文", font=("MS Gothic", 20),wraplength=380)
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
    self.res_bac_button = Button(self.res_canvas, text="戻る", font=("MS Gothic", 15), command=lambda: [self.res_canvas.pack_forget(), self.home_canvas.pack(fill="both",expand=True),self.playsound((currentdir + "gui/bgm/opening.wav"))])
    self.res_title.pack(pady=20)
    
    self.playsound((currentdir + "gui/bgm/opening.wav"))
    if len(self.wrong) > 0:
      self.home_wro_button["state"] = 'normal'
    else:
      self.home_wro_button["state"] = 'disabled'
    
    self.gui.mainloop()

class Editor(Same):
  # 単語追加処理
  def addword_submit(self):
    jp_word = self.add_jp_entry.get()
    en_word = self.add_en_entry.get()
    if jp_word == "" or en_word == "":
      messagebox.showerror("error","単語が入力されていません。")
      return
    if jp_word in self.words:
      messagebox.showerror("error","その意味は既に存在します。")
      return
    self.words[jp_word] = en_word
    umeru = 50 - len(jp_word) - len(en_word)
    self.keys_list_dic.append(jp_word + en_word.rjust(umeru))
    self.main_wordlist_var.set(self.keys_list_dic)
    self.add_window.destroy()
  # 単語編集ウィンドウ
  def editword(self):
    selected_indices = self.main_wordlist.curselection()
    if not selected_indices:
      messagebox.showerror("error","編集する単語が選択されていません。")
      return
    index = selected_indices[0]
    key_to_edit = self.keys_list[index]
    self.edit_window = Toplevel(self.gui)
    self.edit_window.title("単語編集")
    self.edit_window.geometry("300x200")
    self.edit_window.resizable(False, False)
    self.edit_jp_label = Label(self.edit_window, text="意味", font=("MS Gothic", 12))
    self.edit_jp_entry = Entry(self.edit_window, font=("MS Gothic", 12))
    self.edit_jp_entry.insert(0, key_to_edit)
    self.edit_en_label = Label(self.edit_window, text="答え", font=("MS Gothic", 12))
    self.edit_en_entry = Entry(self.edit_window, font=("MS Gothic", 12))
    self.edit_en_entry.insert(0, self.words[key_to_edit])
    self.edit_submit_button = Button(self.edit_window, text="保存", font=("MS Gothic", 12), command=lambda: self.editword_submit(index, key_to_edit))
    self.edit_cancel_button = Button(self.edit_window, text="キャンセル", font=("MS Gothic", 12), command=self.edit_window.destroy)
    self.edit_jp_label.pack(pady=5)
    self.edit_jp_entry.pack(pady=5)
    self.edit_en_label.pack(pady=5)
    self.edit_en_entry.pack(pady=5)
    self.edit_submit_button.pack(pady=5)
    self.edit_cancel_button.pack(pady=5)
  # 単語追加ウィンドウ
  def addword(self):
    self.add_window = Toplevel(self.gui)
    self.add_window.title("単語追加")
    self.add_window.geometry("300x200")
    self.add_window.resizable(False, False)
    self.add_jp_label = Label(self.add_window, text="意味", font=("MS Gothic", 12))
    self.add_jp_entry = Entry(self.add_window, font=("MS Gothic", 12))
    self.add_en_label = Label(self.add_window, text="答え", font=("MS Gothic", 12))
    self.add_en_entry = Entry(self.add_window, font=("MS Gothic", 12))
    self.add_submit_button = Button(self.add_window, text="追加", font=("MS Gothic", 12), command=self.addword_submit)
    self.add_cancel_button = Button(self.add_window, text="キャンセル", font=("MS Gothic", 12), command=self.add_window.destroy)
    self.add_jp_label.pack(pady=5)
    self.add_jp_entry.pack(pady=5)
    self.add_en_label.pack(pady=5)
    self.add_en_entry.pack(pady=5)
    self.add_submit_button.pack(pady=5)
    self.add_cancel_button.pack(pady=5)
  # 単語削除処理
  def delword(self):
    selected_indices = self.main_wordlist.curselection()
    if not selected_indices:
      messagebox.showerror("error","削除する単語が選択されていません。")
      return
    for index in reversed(selected_indices):
      key_to_delete = self.keys_list[index]
      del self.words[key_to_delete]
      del self.keys_list_dic[index]
    self.main_wordlist_var.set(self.keys_list_dic)
  # 単語保存処理
  def saveword(self):
    with open((currentdir + "words.json"), "w", encoding="utf-8") as f:
      json.dump(self.words, f, ensure_ascii=False, indent=4)
    messagebox.showinfo("保存完了","単語データを保存しました。")
  def __init__(self):
    super().__init__()
    # GUI初期化
    print("設定gui起動中...")
    # 定義
    self.gui = Tk()
    self.gui.title("単語データEditor")
    self.gui.geometry("400x400")
    self.gui.resizable(False, False)
    self.main_wordlist_var = StringVar(self.gui,value=self.keys_list_dic)
    self.main_wordlist = Listbox(self.gui, font=("MS Gothic", 12),width=50)
    self.main_add_button = Button(self.gui, text="追加", font=("MS Gothic", 15), command=self.addword)
    self.main_edit_button = Button(self.gui, text="編集", font=("MS Gothic", 15),command=self.editword)
    self.main_del_button = Button(self.gui, text="削除", font=("MS Gothic", 15), command=self.delword)
    self.main_quit_button = Button(self.gui, text="保存", font=("MS Gothic", 15), command=self.saveword)
    self.main_wordlist.configure(listvariable=self.main_wordlist_var)
    
    # ウィジェット配置
    self.main_wordlist.pack(pady=20)
    self.main_add_button.pack(pady=5,side=LEFT)
    self.main_edit_button.pack(pady=5,side=LEFT)
    self.main_del_button.pack(pady=5,side=LEFT)
    self.main_quit_button.pack(pady=5,side=RIGHT)
    
    # メインループ
    self.gui.mainloop()

if __name__ == "__main__":
  if len(sys.argv) > 1 and sys.argv[1] == "edit":
    Editor()
  else:
    Game()
  