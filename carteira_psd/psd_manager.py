from psd_tools import PSDImage
from PIL import Image, ImageDraw
import os

def ler_campos_psd(arquivo):
    psd = PSDImage.open(arquivo)
    campos = []

    for layer in psd.descendants():
        if layer.is_visible():
            bbox = layer.bbox
            left, top, right, bottom = bbox

            campos.append({
                "nome": layer.name,
                "tipo": layer.kind,
                "posicao": [left, top, right, bottom]
            })

    return campos

def gerar_png(psd_path, dados, foto_path, area_foto, saida):
    psd = PSDImage.open(psd_path)
    imagem = psd.composite()
    img = imagem.convert("RGB")
    draw = ImageDraw.Draw(img)

    for campo in dados:
        texto = dados[campo]
        x, y, _, _ = area_foto
        draw.text((x, y), texto, fill=(0,0,0))

    if foto_path:
        foto = Image.open(foto_path)
        foto = foto.resize((area_foto[2]-area_foto[0], area_foto[3]-area_foto[1]))
        img.paste(foto, (area_foto[0], area_foto[1]))

    img.save(saida)
    return saida
