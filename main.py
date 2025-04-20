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
            # parâmetros de Imagem → ZPL
            larg_cm = float(entry_largura.get())
            alt_cm = float(entry_altura.get())
            qtd = int(entry_quantidade.get())

            # cm → dots (1cm = 0.3937in * 203 dpi)
            larg_pts = int(larg_cm * 0.3937 * 203)
            alt_pts = int(alt_cm * 0.3937 * 203)

            zpl = convert_image_to_zpl(path, larg_pts, alt_pts, qtd)
            out_txt = os.path.join(OUTPUT_DIR, f"{base}.txt")
            with open(out_txt, "w") as f:
                f.write(zpl)
            messagebox.showinfo("Sucesso", f"ZPL salvo em:\n{out_txt}")

        else:  # from_zpl
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

# --- GUI ---
root = tk.Tk()
root.title("PNG/JPG/PDF ↔ ZPL Converter")
root.geometry("450x380")

mode_var = tk.StringVar(value="to_zpl")
mode_var.trace_add("write", atualizar_campos)  # Chama ao trocar modo

frame_mode = tk.Frame(root)
tk.Radiobutton(frame_mode, text="Imagem (tipos) → ZPL", variable=mode_var, value="to_zpl").pack(side="left", padx=10)
tk.Radiobutton(frame_mode, text="ZPL → Imagem", variable=mode_var, value="from_zpl").pack(side="left", padx=10)
frame_mode.pack(pady=10)

entrada_arquivo = tk.StringVar()
tk.Label(root, text="Arquivo:").pack(anchor="w", padx=20)
tk.Entry(root, textvariable=entrada_arquivo, width=55).pack(padx=20)
tk.Button(root, text="Selecionar Arquivo", command=selecionar_arquivo).pack(pady=5)

# Parâmetros para Imagem → ZPL
frame_param = tk.Frame(root)
tk.Label(frame_param, text="Largura (cm):").grid(row=0, column=0, sticky="e")
entry_largura = tk.Entry(frame_param, width=8)
entry_largura.grid(row=0, column=1, padx=5)
tk.Label(frame_param, text="Altura (cm):").grid(row=0, column=2, sticky="e")
entry_altura = tk.Entry(frame_param, width=8)
entry_altura.grid(row=0, column=3, padx=5)
tk.Label(frame_param, text="Quantidade:").grid(row=0, column=4, sticky="e")
entry_quantidade = tk.Entry(frame_param, width=8)
entry_quantidade.grid(row=0, column=5, padx=5)
frame_param.pack(pady=10)

# Inicializa os campos corretamente
atualizar_campos()

tk.Button(root, text="Processar", command=processar).pack(pady=30)

root.mainloop()
