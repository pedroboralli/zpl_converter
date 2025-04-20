import os
from flask import Flask, request, render_template, send_file, redirect, url_for
from zpl_utils import convert_image_to_zpl, convert_zpl_to_image

app = Flask(__name__)
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    result_file = None
    if request.method == "POST":
        mode = request.form.get("mode")
        file = request.files.get("file")
        if not file:
            return render_template("index.html", error="Selecione um arquivo.")
        filename = file.filename
        base = os.path.splitext(filename)[0]
        path = os.path.join(OUTPUT_DIR, filename)
        file.save(path)

        try:
            if mode == "to_zpl":
                larg_cm = float(request.form.get("largura"))
                alt_cm = float(request.form.get("altura"))
                qtd = int(request.form.get("quantidade"))
                larg_pts = int(larg_cm * 0.3937 * 203)
                alt_pts = int(alt_cm * 0.3937 * 203)
                zpl = convert_image_to_zpl(path, larg_pts, alt_pts, qtd)
                out_txt = os.path.join(OUTPUT_DIR, f"{base}.txt")
                with open(out_txt, "w") as f:
                    f.write(zpl)
                result_file = url_for('download_file', filename=f"{base}.txt")
            else:
                out_png = os.path.join(OUTPUT_DIR, f"{base}.png")
                convert_zpl_to_image(path, out_png)
                result_file = url_for('download_file', filename=f"{base}.png")
        except Exception as e:
            return render_template("index.html", error=str(e))
        return render_template("index.html", result_file=result_file)
    return render_template("index.html")

@app.route('/output/<filename>')
def download_file(filename):
    return send_file(os.path.join(OUTPUT_DIR, filename), as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)