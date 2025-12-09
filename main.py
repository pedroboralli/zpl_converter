import os
import tkinter as tk
from tkinter import filedialog, messagebox
from zpl_utils import (
    convert_image_to_zpl,
    convert_zpl_to_image
)

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def selecionar_arquivo():
    mode = mode_var.get()
    if mode == "to_zpl":
        tipos = [("Imagens/PDF", "*.png;*.jpg;*.jpeg;*.pdf")]
    else:
        tipos = [("ZPL TXT", "*.txt")]
    path = filedialog.askopenfilename(filetypes=tipos)
    if path:
        entrada_arquivo.set(path)

def processar():
    path = entrada_arquivo.get()
    if not path or not os.path.exists(path):
        messagebox.showerror("Erro", "Selecione um arquivo válido.")
        return

    mode = mode_var.get()
    base = os.path.basename(path).split(".")[0]

    try:
        if mode == "to_zpl":
            larg_cm = float(entry_largura.get())
            alt_cm = float(entry_altura.get())
            qtd = int(entry_quantidade.get())
            larg_pts = int(larg_cm * 0.3937 * 203)
            alt_pts = int(alt_cm * 0.3937 * 203)
            zpl = convert_image_to_zpl(path, larg_pts, alt_pts, qtd)
            out_txt = os.path.join(OUTPUT_DIR, f"{base}.txt")
            with open(out_txt, "w") as f:
                f.write(zpl)
            messagebox.showinfo("Sucesso", f"ZPL salvo em:\n{out_txt}")
        else:
            out_png = os.path.join(OUTPUT_DIR, f"{base}.png")
            convert_zpl_to_image(path, out_png)
            messagebox.showinfo("Sucesso", f"Imagem PNG salva em:\n{out_png}")
    except Exception as e:
        messagebox.showerror("Erro", str(e))

def atualizar_campos(*args):
    modo = mode_var.get()
    state = "normal" if modo == "to_zpl" else "disabled"
    entry_largura.config(state=state)
    entry_altura.config(state=state)
    entry_quantidade.config(state=state)

root = tk.Tk()
root.title("ZPL Converter Offline")
root.geometry("600x320")
root.configure(bg="#fafbfc")

container = tk.Frame(root, bg="#fff", bd=0, relief="flat")
container.place(relx=0.5, rely=0.5, anchor="center", width=540, height=260)

# Upload area
frame_upload = tk.Frame(container, bg="#f6f8fa", bd=2, relief="groove", highlightbackground="#d0d7de", highlightcolor="#d0d7de", highlightthickness=2)
frame_upload.place(x=18, y=18, width=220, height=120)
icon = tk.Label(frame_upload, text="+", font=("Arial", 36), fg="#b6bfc9", bg="#f6f8fa")
icon.pack(pady=(18, 0))
drop_label = tk.Label(frame_upload, text="Selecione o arquivo", bg="#f6f8fa", fg="#555")
drop_label.pack()
entrada_arquivo = tk.StringVar()
entry_file = tk.Entry(container, textvariable=entrada_arquivo, width=28, state="readonly", relief="flat", bg="#f6f8fa")
entry_file.place(x=18, y=145)
btn_upload = tk.Button(container, text="Procurar...", command=selecionar_arquivo, bg="#2563eb", fg="#fff", relief="flat")
btn_upload.place(x=170, y=142, width=65)

# Mode selection
mode_var = tk.StringVar(value="to_zpl")
mode_var.trace_add("write", atualizar_campos)
frame_mode = tk.Frame(container, bg="#fff")
frame_mode.place(x=260, y=18)
tk.Radiobutton(frame_mode, text="Image to ZPL", variable=mode_var, value="to_zpl", bg="#fff").grid(row=0, column=0, sticky="w")
tk.Radiobutton(frame_mode, text="ZPL to Image", variable=mode_var, value="from_zpl", bg="#fff").grid(row=1, column=0, sticky="w")

# Parameters
frame_param = tk.Frame(container, bg="#fff")
frame_param.place(x=260, y=60)
tk.Label(frame_param, text="Label Width (cm)", bg="#fff").grid(row=0, column=0, sticky="e")
entry_largura = tk.Entry(frame_param, width=7)
entry_largura.grid(row=0, column=1, padx=6)
entry_largura.insert(0, "10")
tk.Label(frame_param, text="Label Height (cm)", bg="#fff").grid(row=1, column=0, sticky="e")
entry_altura = tk.Entry(frame_param, width=7)
entry_altura.grid(row=1, column=1, padx=6)
entry_altura.insert(0, "7.5")
tk.Label(frame_param, text="Quantity", bg="#fff").grid(row=2, column=0, sticky="e")
entry_quantidade = tk.Entry(frame_param, width=7)
entry_quantidade.grid(row=2, column=1, padx=6)
entry_quantidade.insert(0, "1")

# Process button
btn_process = tk.Button(container, text="Generate and Download", command=processar, bg="#2563eb", fg="#fff", font=("Arial", 12, "bold"), relief="flat")
btn_process.place(x=260, y=150, width=220, height=40)

# Inicializa os campos corretamente
atualizar_campos()

root.mainloop()
