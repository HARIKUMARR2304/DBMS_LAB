import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import time

# --- DATABASE CONFIGURATION ---
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "Hari@2304"  # 👈 Replace with your MySQL Root Password
DB_NAME = "quiz_db"

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        return conn
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Failed to connect to MySQL:\n{err}")
        return None

class ModernQuizApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("⚡ CyberQuiz Master - SQL & Python Data History")
        self.geometry("950x720")
        self.minsize(900, 650)
        self.configure(bg="#0b0f19")

        # State Variables
        self.questions = []
        self.user_answers = []
        self.current_idx = 0
        self.score = 0
        self.selected_opt = tk.StringVar()
        self.timer_seconds = 15
        self.timer_running = False

        self.setup_styles()

        # Top Navigation Bar
        header = tk.Frame(self, bg="#111827", height=65)
        header.pack(fill="x", side="top")
        
        lbl_brand = tk.Label(header, text="⚡ CYBERQUIZ", font=("Segoe UI", 18, "bold"), fg="#38bdf8", bg="#111827")
        lbl_brand.pack(side="left", padx=25, pady=15)

        btn_leaderboard = tk.Button(
            header, text="📊 Full Data History", font=("Segoe UI", 10, "bold"),
            bg="#1e293b", fg="#f8fafc", activebackground="#334155", activeforeground="#ffffff",
            bd=0, padx=14, pady=6, cursor="hand2", command=self.show_leaderboard
        )
        btn_leaderboard.pack(side="right", padx=25)

        # Main Container Panel
        self.container = tk.Frame(self, bg="#0b0f19")
        self.container.pack(fill="both", expand=True, padx=30, pady=20)

        # Direct Launch
        self.load_questions_and_start()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        self.style.configure(
            "Cyan.Horizontal.TProgressbar",
            thickness=10,
            troughcolor="#1e293b",
            background="#06b6d4"
        )
        
        self.style.configure(
            "Treeview",
            rowheight=30,
            font=("Segoe UI", 10),
            fieldbackground="#1e293b",
            background="#1e293b",
            foreground="#f8fafc"
        )
        self.style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 10, "bold"),
            background="#334155",
            foreground="#38bdf8"
        )
        self.style.map("Treeview", background=[("selected", "#0284c7")])

    def load_questions_and_start(self):
        conn = get_db_connection()
        if not conn:
            return

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM questions ORDER BY RAND()")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        if not rows:
            messagebox.showerror("Error", "No questions found in database table 'questions'.")
            return

        self.questions = [{
            "id": r["question_id"],
            "text": r["question_text"],
            "opts": [r["option_a"], r["option_b"], r["option_c"], r["option_d"]],
            "correct": r["correct_option"]
        } for r in rows]

        self.current_idx = 0
        self.score = 0
        self.user_answers = []
        self.render_quiz_screen()

    # --- QUIZ DISPLAY ---
    def render_quiz_screen(self):
        self.clear_container()

        stats_frame = tk.Frame(self.container, bg="#0b0f19")
        stats_frame.pack(fill="x", pady=(0, 10))

        self.lbl_progress = tk.Label(stats_frame, text=f"QUESTION {self.current_idx + 1} OF {len(self.questions)}", font=("Segoe UI", 10, "bold"), fg="#64748b", bg="#0b0f19")
        self.lbl_progress.pack(side="left")

        self.lbl_timer = tk.Label(stats_frame, text="⏳ 15s", font=("Segoe UI", 11, "bold"), fg="#f59e0b", bg="#0b0f19")
        self.lbl_timer.pack(side="right")

        self.progress_bar = ttk.Progressbar(self.container, style="Cyan.Horizontal.TProgressbar", maximum=100)
        self.progress_bar.pack(fill="x", pady=(0, 20))

        self.card = tk.Frame(self.container, bg="#1e293b", bd=0, highlightbackground="#3b82f6", highlightthickness=1)
        self.card.pack(fill="both", expand=True, ipadx=25, ipady=20)

        self.lbl_question = tk.Label(
            self.card, text="", font=("Segoe UI", 14, "bold"), fg="#f8fafc", bg="#1e293b",
            wraplength=750, justify="left"
        )
        self.lbl_question.pack(anchor="w", pady=(10, 25), padx=15)

        self.option_cards = []
        labels = ["A", "B", "C", "D"]
        for i in range(4):
            opt_frame = tk.Frame(self.card, bg="#0f172a", highlightbackground="#334155", highlightthickness=1, cursor="hand2")
            opt_frame.pack(fill="x", pady=6, padx=15)

            rb = tk.Radiobutton(
                opt_frame, text="", value=labels[i], variable=self.selected_opt,
                font=("Segoe UI", 11), fg="#cbd5e1", bg="#0f172a", activebackground="#0f172a",
                activeforeground="#67e8f9", selectcolor="#0f172a", bd=0, anchor="w", padx=10, pady=8
            )
            rb.pack(fill="x")
            
            opt_frame.bind("<Enter>", lambda e, f=opt_frame: f.config(highlightbackground="#38bdf8"))
            opt_frame.bind("<Leave>", lambda e, f=opt_frame: f.config(highlightbackground="#334155"))
            rb.bind("<Button-1>", lambda e, val=labels[i]: self.selected_opt.set(val))

            self.option_cards.append((opt_frame, rb))

        btn_next = tk.Button(
            self.container, text="Submit Answer ➔", font=("Segoe UI", 11, "bold"),
            bg="#2563eb", fg="#ffffff", activebackground="#1d4ed8", activeforeground="#ffffff",
            bd=0, padx=25, pady=10, cursor="hand2", command=self.handle_answer_submit
        )
        btn_next.pack(side="right", pady=(15, 0))

        self.display_question()

    def display_question(self):
        self.selected_opt.set("")
        q = self.questions[self.current_idx]

        self.lbl_progress.config(text=f"QUESTION {self.current_idx + 1} OF {len(self.questions)}")
        self.lbl_question.config(text=f"{self.current_idx + 1}. {q['text']}")

        labels = ["A", "B", "C", "D"]
        for idx, (frame, rb) in enumerate(self.option_cards):
            rb.config(text=f" {labels[idx]} .   {q['opts'][idx]}")

        target_pct = ((self.current_idx) / len(self.questions)) * 100
        self.animate_progress(target_pct)

        self.timer_seconds = 15
        self.timer_running = True
        self.update_timer()

    def update_timer(self):
        if self.timer_running and self.timer_seconds > 0:
            self.lbl_timer.config(text=f"⏳ {self.timer_seconds}s")
            self.timer_seconds -= 1
            self.after(1000, self.update_timer)
        elif self.timer_running and self.timer_seconds == 0:
            self.timer_running = False
            self.lbl_timer.config(text="⏰ Time's Up!")
            self.handle_answer_submit(auto_timeout=True)

    def handle_answer_submit(self, auto_timeout=False):
        self.timer_running = False
        user_choice = self.selected_opt.get()

        if not user_choice and not auto_timeout:
            messagebox.showwarning("Select Answer", "Please choose an option before submitting!")
            return

        if not user_choice:
            user_choice = "-"

        q_item = self.questions[self.current_idx]
        correct = q_item["correct"]
        is_corr = (user_choice == correct)

        if is_corr:
            self.score += 1
            self.flash_card("#16a34a")
        else:
            self.flash_card("#dc2626")

        self.user_answers.append({
            "text": q_item["text"],
            "user_choice": user_choice,
            "correct": correct,
            "is_correct": is_corr
        })

        self.current_idx += 1
        if self.current_idx < len(self.questions):
            self.display_question()
        else:
            self.animate_progress(100)
            self.save_full_history_to_db()
            self.show_results_screen()

    # --- RESULTS SCREEN ---
    def show_results_screen(self):
        self.clear_container()

        total = len(self.questions)
        pct = (self.score / total) * 100
        status = "Passed" if pct >= 50 else "Failed"

        result_card = tk.Frame(self.container, bg="#1e293b", highlightbackground="#38bdf8", highlightthickness=1)
        result_card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.65, relheight=0.7)

        badge_color = "#10b981" if pct >= 70 else ("#f59e0b" if pct >= 50 else "#ef4444")
        title_text = "🎉 Quiz Completed!" if pct >= 50 else "📚 Try Again!"

        tk.Label(result_card, text=title_text, font=("Segoe UI", 20, "bold"), fg=badge_color, bg="#1e293b").pack(pady=(20, 5))

        score_badge = tk.Label(
            result_card, text=f" Score: {self.score} / {total} ", font=("Segoe UI", 28, "bold"),
            bg=badge_color, fg="#ffffff", padx=20, pady=5
        )
        score_badge.pack(pady=10)

        tk.Label(result_card, text=f"Percentage: {pct:.1f}%  |  Status: {status}", font=("Segoe UI", 12, "bold"), fg="#cbd5e1", bg="#1e293b").pack(pady=5)
        tk.Label(result_card, text="✅ Detailed data breakdown stored in MySQL!", font=("Segoe UI", 10, "italic"), fg="#4ade80", bg="#1e293b").pack(pady=(0, 20))

        btn_box = tk.Frame(result_card, bg="#1e293b")
        btn_box.pack(pady=10)

        btn_retry = tk.Button(
            btn_box, text="🔄 Retake Quiz", font=("Segoe UI", 10, "bold"),
            bg="#2563eb", fg="#ffffff", activebackground="#1d4ed8", activeforeground="#ffffff",
            bd=0, padx=18, pady=8, cursor="hand2", command=self.load_questions_and_start
        )
        btn_retry.pack(side="left", padx=5)

        btn_view_lb = tk.Button(
            btn_box, text="📊 View Data History", font=("Segoe UI", 10, "bold"),
            bg="#059669", fg="#ffffff", activebackground="#047857", activeforeground="#ffffff",
            bd=0, padx=18, pady=8, cursor="hand2", command=self.show_leaderboard
        )
        btn_view_lb.pack(side="left", padx=5)

    # --- SQL DATA HISTORY SCREEN ---
    def show_leaderboard(self):
        self.timer_running = False
        self.clear_container()

        title_frame = tk.Frame(self.container, bg="#0b0f19")
        title_frame.pack(fill="x", pady=(0, 15))

        tk.Label(title_frame, text="📊 Attempt History & Breakdown", font=("Segoe UI", 16, "bold"), fg="#f8fafc", bg="#0b0f19").pack(side="left")

        btn_actions = tk.Frame(title_frame, bg="#0b0f19")
        btn_actions.pack(side="right")

        btn_clear = tk.Button(
            btn_actions, text="🗑️ Clear DB History", font=("Segoe UI", 9, "bold"),
            bg="#dc2626", fg="#ffffff", activebackground="#b91c1c", bd=0, padx=10, pady=5, cursor="hand2", command=self.clear_history_db
        )
        btn_clear.pack(side="left", padx=(0, 10))

        btn_back = tk.Button(
            btn_actions, text="⬅ Back to Quiz", font=("Segoe UI", 9, "bold"),
            bg="#334155", fg="#ffffff", activebackground="#475569", bd=0, padx=12, pady=5, cursor="hand2", command=self.load_questions_and_start
        )
        btn_back.pack(side="left")

        tk.Label(self.container, text="Summary Sessions (SQL Table: quiz_results)", font=("Segoe UI", 10, "bold"), fg="#38bdf8", bg="#0b0f19").pack(anchor="w", pady=(0, 5))

        cols = ("id", "score", "total", "pct", "status", "date")
        self.tree = ttk.Treeview(self.container, columns=cols, show="headings", height=5)

        self.tree.heading("id", text="Attempt ID")
        self.tree.heading("score", text="Score")
        self.tree.heading("total", text="Total Qs")
        self.tree.heading("pct", text="Percentage")
        self.tree.heading("status", text="Status")
        self.tree.heading("date", text="Date & Time")

        self.tree.column("id", width=80, anchor="center")
        self.tree.column("score", width=80, anchor="center")
        self.tree.column("total", width=80, anchor="center")
        self.tree.column("pct", width=100, anchor="center")
        self.tree.column("status", width=100, anchor="center")
        self.tree.column("date", width=200, anchor="center")
        self.tree.pack(fill="x", pady=(0, 15))

        self.tree.bind("<<TreeviewSelect>>", self.on_session_select)

        tk.Label(self.container, text="Detailed Breakdown (SQL Table: quiz_history_details)", font=("Segoe UI", 10, "bold"), fg="#38bdf8", bg="#0b0f19").pack(anchor="w", pady=(0, 5))

        detail_cols = ("q_text", "u_ans", "c_ans", "res")
        self.detail_tree = ttk.Treeview(self.container, columns=detail_cols, show="headings", height=6)
        
        self.detail_tree.heading("q_text", text="Question Text")
        self.detail_tree.heading("u_ans", text="Your Option")
        self.detail_tree.heading("c_ans", text="Correct Option")
        self.detail_tree.heading("res", text="Result")

        self.detail_tree.column("q_text", width=450)
        self.detail_tree.column("u_ans", width=100, anchor="center")
        self.detail_tree.column("c_ans", width=100, anchor="center")
        self.detail_tree.column("res", width=100, anchor="center")
        self.detail_tree.pack(fill="both", expand=True)

        self.fetch_history_summary()

    def fetch_history_summary(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT result_id, score, total_questions, percentage, status, submitted_at FROM quiz_results ORDER BY result_id DESC")
            rows = cursor.fetchall()
            for r in rows:
                self.tree.insert("", "end", values=(r[0], r[1], r[2], f"{r[3]}%", r[4], str(r[5])))
            cursor.close()
            conn.close()

    def on_session_select(self, event):
        selected_item = self.tree.selection()
        if not selected_item:
            return

        for item in self.detail_tree.get_children():
            self.detail_tree.delete(item)

        result_id = self.tree.item(selected_item)["values"][0]

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT question_text, user_choice, correct_choice, is_correct FROM quiz_history_details WHERE result_id = %s", (result_id,))
            rows = cursor.fetchall()
            for r in rows:
                outcome = "✅ Correct" if r[3] else "❌ Incorrect"
                self.detail_tree.insert("", "end", values=(r[0], r[1], r[2], outcome))
            cursor.close()
            conn.close()

    def save_full_history_to_db(self):
        total = len(self.questions)
        pct = (self.score / total) * 100
        status = "Passed" if pct >= 50 else "Failed"

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            query1 = "INSERT INTO quiz_results (score, total_questions, percentage, status) VALUES (%s, %s, %s, %s)"
            cursor.execute(query1, (self.score, total, pct, status))
            result_id = cursor.lastrowid

            query2 = "INSERT INTO quiz_history_details (result_id, question_text, user_choice, correct_choice, is_correct) VALUES (%s, %s, %s, %s, %s)"
            for item in self.user_answers:
                cursor.execute(query2, (result_id, item["text"], item["user_choice"], item["correct"], item["is_correct"]))

            conn.commit()
            cursor.close()
            conn.close()

    def clear_history_db(self):
        confirm = messagebox.askyesno("Confirm Clear", "Delete all saved records and history details from MySQL?")
        if confirm:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM quiz_results")
                conn.commit()
                cursor.close()
                conn.close()

                messagebox.showinfo("Success", "All history cleared from MySQL!")
                self.fetch_history_summary()
                for item in self.detail_tree.get_children():
                    self.detail_tree.delete(item)

    # --- UI ANIMATIONS & HELPERS ---
    def flash_card(self, color):
        orig_bg = "#1e293b"
        self.card.config(bg=color)
        self.lbl_question.config(bg=color)
        self.update()
        time.sleep(0.15)
        self.card.config(bg=orig_bg)
        self.lbl_question.config(bg=orig_bg)
        self.update()

    def animate_progress(self, target_val):
        start_val = self.progress_bar["value"]
        step = 1 if target_val > start_val else -1
        if start_val != target_val:
            for val in range(int(start_val), int(target_val) + step, step):
                self.progress_bar["value"] = val
                self.update()
                time.sleep(0.004)

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    app = ModernQuizApp()
    app.mainloop()
