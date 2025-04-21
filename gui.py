import tkinter as tk
from tkinter import messagebox

def start_gui(camera_data):
    #camera_data = get_cameras_with_resolutions()

    root = tk.Tk()
    root.title("Kamera & Auflösung wählen")
    root.geometry("550x700")

    selections = []
    result = []

    tk.Label(root, text="Wähle Kamera(s) & Auflösung:", font=("Arial", 14, "bold")).pack(pady=10)

    canvas_frame = tk.Frame(root)
    canvas_frame.pack(fill="both", expand=True)

    canvas = tk.Canvas(canvas_frame)
    scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    for cam in camera_data:
        cam_frame = tk.Frame(scrollable_frame, bd=1, relief="solid", padx=10, pady=5)
        cam_frame.pack(padx=10, pady=10, fill="x")

        cam_enabled = tk.BooleanVar()
        selected_res = tk.StringVar()
        selected_res.set("")  # Keine Vorauswahl

        res_frame = tk.Frame(cam_frame)

        # Kamera Checkbox
        cam_check = tk.Checkbutton(
            cam_frame,
            text=f"[{cam['index']}] {cam['name']}",
            variable=cam_enabled,
            font=("Arial", 12)
        )
        cam_check.pack(anchor="w")
        res_frame.pack(anchor="w", padx=20, pady=(5, 0))  # DIREKT ANZEIGEN

        # Auflösungsliste (Radiobuttons)
        if cam["resolutions"]:
            tk.Label(res_frame, text="Auflösung wählen:", font=("Arial", 10, "italic")).pack(anchor="w")
            for res in sorted(cam["resolutions"], key=lambda r: (r[0], r[1])):
                w, h = res
                res_str = f"{w}x{h}"
                rb = tk.Radiobutton(
                    res_frame,
                    text=res_str,
                    variable=selected_res,
                    value=res_str,
                    font=("Arial", 10)
                )
                rb.pack(anchor="w")

        # Auswahl speichern
        selections.append({
            "index": cam["index"],
            "name": cam["name"],
            "enabled": cam_enabled,
            "resolution": selected_res
        })

    def on_start():
        configs = []
        for sel in selections:
            if sel["enabled"].get():
                l_res = sel["resolution"].get()
                if not l_res:
                    messagebox.showwarning("Fehlende Auflösung", f"Bitte Auflösung für Kamera '{sel['name']}' wählen.")
                    return
                width, height = map(int, l_res.split("x"))
                configs.append({
                    "index": sel["index"],
                    "name": sel["name"],
                    "width": width,
                    "height": height
                })

        if not configs:
            messagebox.showwarning("Keine Kamera ausgewählt", "Bitte mindestens eine Kamera auswählen.")
            return

        root.destroy()
        result.extend(configs)

    tk.Button(
        root,
        text="Start",
        command=on_start,
        font=("Arial", 13),
        bg="#4CAF50",
        fg="white",
        padx=20,
        pady=5
    ).pack(pady=20)

    root.mainloop()
    return result