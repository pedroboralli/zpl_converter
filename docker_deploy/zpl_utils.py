import os
from PIL import Image
import fitz  # PyMuPDF
import re
import zlib
import base64

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
    """Converte ZPL com ~DGR ou ^GFA para PNG."""
    with open(zpl_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Tenta ~DGR (RAM)
    m = re.search(r"~DGR:[^,]+,(\d+),(\d+),([0-9A-F]+)", content)
    if m:
        total_bytes = int(m.group(1))
        width_bytes = int(m.group(2))
        hexdata = m.group(3)
        raw = bytes.fromhex(hexdata)
        height = total_bytes // width_bytes
        width = width_bytes * 8
    else:
        # Tenta ^GFA (Field Graphics)
        m = re.search(r"\^GFA,(\d+),(\d+),(\d+),([A-Za-z0-9,]+)", content)
        if not m:
            raise ValueError("ZPL inválido ou ~DGR/^GFA não encontrado.")
        total_bytes = int(m.group(1))
        bytes_used = int(m.group(2))
        bytes_per_row = int(m.group(3))
        data = m.group(4).replace('\n', '').replace('\r', '')
        # Decodifica o formato ASCII-Hex compactado do ZPL
        raw = decode_zpl_ascii_hex(data, bytes_used)
        width_bytes = bytes_per_row
        height = bytes_used // bytes_per_row
        width = width_bytes * 8

    img = Image.new("1", (width, height))
    pixels = img.load()
    idx = 0
    for y in range(height):
        for b in range(width_bytes):
            if idx >= len(raw):
                break
            byte = raw[idx]
            idx += 1
            for bit in range(8):
                x = b*8 + (7-bit)
                if x < width:
                    pixels[x, y] = 0 if (byte & (1 << bit)) else 1
    img.save(output_path)
    return output_path

def decode_zpl_ascii_hex(data, bytes_expected):
    """Decodifica o formato ASCII-Hex compactado do ^GFA."""
    # O ZPL usa um esquema de compressão simples para ^GFA (run-length encoding)
    # Veja: https://www.zebra.com/content/dam/zebra/manuals/en-us/software/zpl-zbi2-pm-en.pdf (procure por ^GF)
    result = bytearray()
    i = 0
    while i < len(data):
        c = data[i]
        if c in ' \n\r\t,':
            i += 1
            continue
        if c == ':':  # : repete 0x00 20 vezes
            result.extend([0x00] * 20)
            i += 1
        elif c == ';':  # ; repete 0xFF 20 vezes
            result.extend([0xFF] * 20)
            i += 1
        elif c == '!':  # ! repete o próximo caractere 400 vezes
            i += 1
            if i < len(data):
                v = int(data[i], 16)
                result.extend([v] * 400)
            i += 1
        elif c.isalnum():
            v = int(c, 16)
            result.append(v)
            i += 1
        else:
            i += 1
    return bytes(result[:bytes_expected])
