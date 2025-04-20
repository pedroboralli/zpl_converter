import os
from PIL import Image
import fitz  # PyMuPDF

def load_image(path):
    """Carrega PNG, JPG ou PDF (primeira página)."""
    ext = os.path.splitext(path)[1].lower()
    if ext == '.pdf':
        doc = fitz.open(path)
        page = doc.load_page(0)
        pix = page.get_pixmap()
        mode = "RGB" if pix.alpha == 0 else "RGBA"
        return Image.frombytes(mode, [pix.width, pix.height], pix.samples)
    else:
        return Image.open(path)

def convert_pil_image_to_zpl(image, quantidade):
    """Gera string ZPL a partir de PIL.Image (1-bit) e comando ^PQ."""
    image_bw = image.convert("1")
    width_bytes = (image_bw.width + 7) // 8
    total_bytes = width_bytes * image_bw.height

    hex_data = ""
    pixels = image_bw.load()
    for y in range(image_bw.height):
        byte = 0
        bits = 0
        for x in range(image_bw.width):
            bit = 0 if pixels[x, y] else 1
            byte = (byte << 1) | bit
            bits += 1
            if bits == 8:
                hex_data += f"{byte:02X}"
                byte = 0
                bits = 0
        if bits > 0:
            byte <<= (8 - bits)
            hex_data += f"{byte:02X}"

    return (
        "^XA\n"
        f"~DGR:IMAGE.GRF,{total_bytes},{width_bytes},{hex_data}\n"
        "^FO0,0^XGIMAGE.GRF,1,1^FS\n"
        f"^PQ{quantidade}\n"
        "^XZ"
    )

def convert_image_to_zpl(path, largura, altura, quantidade):
    """Carrega imagem (PNG/JPG/PDF), redimensiona e converte para ZPL."""
    img = load_image(path)
    img = img.resize((largura, altura))
    return convert_pil_image_to_zpl(img, quantidade)

def convert_zpl_to_image(zpl_path, output_path):
    """Lê arquivo .txt com ZPL (~DGR) e reconstrói PNG, suportando HEX e Z64."""
    import re
    import zlib
    import base64

    with open(zpl_path, "r") as f:
        content = f.read()

    # HEX padrão
    m = re.search(r"~DGR:[^,]+,(\d+),(\d+),([0-9A-F]+)", content)
    if m:
        total_bytes = int(m.group(1))
        width_bytes = int(m.group(2))
        hexdata = m.group(3)
        raw = bytes.fromhex(hexdata)
    else:
        # Z64 compactado
        m = re.search(r"~DGR:[^,]+,(\d+),(\d+),:Z64:([A-Za-z0-9+/=]+)", content)
        if not m:
            raise ValueError("ZPL inválido ou ~DGR não encontrado.")
        total_bytes = int(m.group(1))
        width_bytes = int(m.group(2))
        z64data = m.group(3)
        # decode base64, then zlib decompress
        compressed = base64.b64decode(z64data)
        raw = zlib.decompress(compressed)

    height = total_bytes // width_bytes
    width = width_bytes * 8

    from PIL import Image
    img = Image.new("1", (width, height))
    pixels = img.load()
    idx = 0
    for y in range(height):
        for b in range(width_bytes):
            byte = raw[idx]
            idx += 1
            for bit in range(8):
                x = b*8 + (7-bit)
                if x < width:
                    pixels[x, y] = 0 if (byte & (1 << bit)) else 1

    img.save(output_path)
    return output_path
