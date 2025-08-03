import tkinter as tk
from main import run_pipeline, run_single_site
import threading
from core.selenium.browser_opener import open_site
import itertools

# Globals
task_labels = {}
row_input = None
run_btn = None
row_btn = None
total_label = None
result_output = None
window = None
stop_btn = None

disabled_widgets = []
spinner_cycle = itertools.cycle(["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"])
spinner_running = False
stop_requested = False


def animate_spinner():
    if spinner_running:
        frame = next(spinner_cycle)
        run_btn.config(text=f"{frame} Running...")
        window.after(100, animate_spinner)


def log_progress(task, started=False, finished=False, duration=None, error_msg=None):
    if started:
        task_labels[task].config(text=f"✗  {task}", fg="#ffaa00")
    if finished:
        task_labels[task].config(text=f"✓  {task}", fg="#66ff66")
    if task == "ALL_DONE":
        total_label.config(text=f"✅ Done in {duration:.2f} seconds", fg="#00ffcc")
    if task == "ERROR":
        message = "❌ Pipeline failed"
        if error_msg:
            message += f" - {error_msg}"
        total_label.config(text=message, fg="red")


def show_site_result(site):
    def yes(flag): return "✅" if flag else "❌"

    def val_or_x(value): return value if value else "❌"

    results = [
        f"Ping Camera: {yes(site.flags.get('is_camera_ping'))}",
        f"Ping NVR: {yes(site.flags.get('is_nvr_ping'))}",
        f"Captures: {val_or_x(site.captures.get('num_captures'))}",
        f"Camera Time: {site.times.get('current_camera_time')}",
        f"Camera Time is synchronized: {yes(site.times.get('is_camera_synchronized'))}",
        f"Nvr Time: {site.times.get('current_nvr_time')}",
        f"Nvr Time is synchronized: {yes(site.times.get('is_nvr_synchronized'))}",
        f"Playback: {yes(site.captures.get('playback'))}"
    ]

    result_output.config(state="normal")
    result_output.delete(1.0, tk.END)
    for line in results:
        result_output.insert(tk.END, line + "\n")
    result_output.config(state="disabled")


def clear_results_area():
    for lbl in task_labels.values():
        lbl.config(text="", fg="#121212")
    result_output.config(state="normal")
    result_output.delete(1.0, tk.END)
    result_output.config(state="disabled")
    total_label.config(text="")


def run_full_script():
    global spinner_running, stop_requested
    stop_requested = False

    def task():
        global spinner_running
        try:
            run_pipeline(status_callback=log_progress, stop_flag=lambda: stop_requested)
        except Exception as e:
            log_progress("ERROR", error_msg=str(e))
        finally:
            spinner_running = False
            run_btn.config(text="▶ Run Full Sheet")
            for w in disabled_widgets:
                w.config(state="normal")

    for w in disabled_widgets:
        w.config(state="disabled")

    clear_results_area()

    for task_name in task_labels:
        task_labels[task_name].config(text=f"✗  {task_name}", fg="#ff4d4d")
        task_labels[task_name].pack(anchor="w")

    spinner_running = True
    animate_spinner()
    threading.Thread(target=task).start()


def run_row_script():
    global stop_requested
    stop_requested = False

    row_number = row_input.get()
    if row_number.isdigit():
        clear_results_area()

        for w in disabled_widgets:
            w.config(state="disabled")

        row_btn.config(text="⏳ Running...")
        window.update_idletasks()

        def task():
            try:
                site = run_single_site(int(row_number), stop_flag=lambda: stop_requested)
                if not stop_requested:
                    show_site_result(site)
                    total_label.config(text="✅ Site completed successfully", fg="#00ffcc")
                else:
                    total_label.config(text="🛑 Task stopped", fg="orange")
            except Exception as e:
                total_label.config(text=f"❌ Error - {str(e)}", fg="red")

            row_btn.config(text="🎯 Run Row Only")
            for w in disabled_widgets:
                w.config(state="normal")

        threading.Thread(target=task).start()
    else:
        total_label.config(text="❌ Invalid row number", fg="red")


def stop_task():
    global stop_requested
    stop_requested = True
    total_label.config(text="🛑 Stop requested...", fg="orange")


def build_gui():
    global row_input, task_labels, total_label, run_btn, row_btn, result_output, window, stop_btn

    window = tk.Tk()
    window.title("Netikot Sheet Runner")
    window.state("zoomed")
    window.configure(bg="#121212")

    title = tk.Label(window, text="📊 Google Sheet Runner", font=("Segoe UI", 30, "bold"),
                     bg="#121212", fg="#00FF88")
    title.pack(pady=30)

    main_frame = tk.Frame(window, bg="#121212")
    main_frame.pack(fill="both", expand=True)

    left = tk.Frame(main_frame, bg="#121212", width=500)
    left.pack(side="left", expand=True, fill="both")

    divider = tk.Frame(main_frame, bg="#333", width=4)
    divider.pack(side="left", fill="y")

    right = tk.Frame(main_frame, bg="#121212", width=500)
    right.pack(side="left", expand=True, fill="both")

    run_btn = tk.Button(left, text="▶ Run Full Sheet", font=("Segoe UI", 14, "bold"),
                        bg="#00ADB5", fg="white", relief="flat", width=20,
                        command=run_full_script, cursor="hand2")
    run_btn.pack(pady=20)
    disabled_widgets.append(run_btn)

    checklist_frame = tk.Frame(left, bg="#121212")
    checklist_frame.pack(pady=10)

    steps = ["Fetching data", "Ping", "Login", "Fetching Captures", "Unknowns"]
    for step in steps:
        lbl = tk.Label(checklist_frame, text=f"✗  {step}", font=("Segoe UI", 14),
                       bg="#121212", fg="#ff4d4d", anchor="w")
        lbl.pack(anchor="w")
        task_labels[step] = lbl

    total_label = tk.Label(left, text="", font=("Segoe UI", 13),
                           bg="#121212", fg="white")
    total_label.pack(pady=20)

    stop_btn = tk.Button(left, text="🛑 Stop Task", font=("Segoe UI", 12),
                         bg="red", fg="white", relief="flat", width=20,
                         command=stop_task, cursor="hand2")
    stop_btn.pack(pady=10)

    tk.Label(right, text="Row Number:", font=("Segoe UI", 14),
             bg="#121212", fg="#eeeeee").pack(pady=30)

    row_input = tk.Entry(right, font=("Segoe UI", 14), width=20,
                         bg="#1F1F1F", fg="white", insertbackground="white", relief="flat")
    row_input.pack(pady=10)

    row_btn = tk.Button(right, text="🎯 Run Row Only", font=("Segoe UI", 14, "bold"),
                        bg="#FF5722", fg="white", relief="flat", width=20,
                        command=run_row_script, cursor="hand2")

    open_btn_cam = tk.Button(right, text="🌐 Open Camera Site", font=("Segoe UI", 14, "bold"),
                         bg="#3F51B5", fg="white", relief="flat", width=20,
                         command=lambda: threading.Thread(target=lambda: open_site(row_input.get(),"camera")).start(),
                         cursor="hand2")

    open_btn_nvr = tk.Button(right, text="🌐 Open NVR Site", font=("Segoe UI", 14, "bold"),
                           bg="#3949AB", fg="white", relief="flat", width=20,
                           command=lambda: threading.Thread(target=lambda: open_site(row_input.get(),"nvr")).start(),
                           cursor="hand2")
    open_btn_cam.pack(pady=10)

    open_btn_nvr.pack(pady=10)

    row_btn.pack(pady=20)
    disabled_widgets.append(row_btn)

    result_output = tk.Text(right, height=15, font=("Segoe UI", 12),
                            bg="#1F1F1F", fg="white", relief="flat", state="disabled")
    result_output.pack(padx=10, pady=10, fill="x")

    tk.Label(window, text="Made with 💻 by Mador Data Pakmaz", font=("Segoe UI", 10),
             bg="#121212", fg="#555").pack(side="bottom", pady=10)

    window.mainloop()


if __name__ == "__main__":
    build_gui()
