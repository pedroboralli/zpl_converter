import os
import time
from flask import Flask, render_template, request, send_file, after_this_request
from zpl_utils import convert_image_to_zpl, convert_zpl_to_image

app = Flask(__name__)

# Configuração da pasta de saída
OUTPUT_DIR = "convertidos"
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/convert/to_zpl", methods=["POST"])
def to_zpl():
    try:
        if "file" not in request.files:
            return "Nenhum arquivo enviado", 400
        
        file = request.files["file"]
        if file.filename == "":
            return "Nenhum arquivo selecionado", 400

        # Parâmetros
        try:
            larg_cm = float(request.form.get("width", 10))
            alt_cm = float(request.form.get("height", 7.5))
            qtd = int(request.form.get("quantity", 1))
        except ValueError:
            return "Parâmetros inválidos", 400

        # Salva arquivo temporariamente
        temp_path = os.path.join(OUTPUT_DIR, f"temp_upload_{int(time.time())}_{file.filename}")
        file.save(temp_path)

        # Converte
        larg_pts = int(larg_cm * 0.3937 * 203)
        alt_pts = int(alt_cm * 0.3937 * 203)
        
        zpl_content = convert_image_to_zpl(temp_path, larg_pts, alt_pts, qtd)
        
        # Limpa upload temporário
        os.remove(temp_path)

        # Salva resultado
        base_name = os.path.splitext(file.filename)[0]
        output_filename = f"{base_name}.txt"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        
        with open(output_path, "w") as f:
            f.write(zpl_content)

        @after_this_request
        def remove_file(response):
             # Opcional: remover arquivo após download se desejar manter a pasta limpa. 
             # O usuário pediu para salvar na pasta "convertidos", então vou MANTER o arquivo lá.
             return response

        return send_file(output_path, as_attachment=True, download_name=output_filename)

    except Exception as e:
        return f"Erro na conversão: {str(e)}", 500

@app.route("/convert/to_image", methods=["POST"])
def to_image():
    try:
        if "file" not in request.files:
            return "Nenhum arquivo enviado", 400
        
        file = request.files["file"]
        if file.filename == "":
            return "Nenhum arquivo selecionado", 400

        # Salva arquivo temporariamente
        temp_path = os.path.join(OUTPUT_DIR, f"temp_zpl_{int(time.time())}.txt")
        file.save(temp_path)

        # Converte
        base_name = os.path.splitext(file.filename)[0]
        output_filename = f"{base_name}.png"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        
        convert_zpl_to_image(temp_path, output_path)
        
        # Limpa upload temporário
        os.remove(temp_path)

        return send_file(output_path, as_attachment=True, download_name=output_filename)

    except Exception as e:
        return f"Erro na conversão: {str(e)}", 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
