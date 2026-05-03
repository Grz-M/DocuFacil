import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
import fitz  # PyMuPDF para renderizado
from PyPDF2 import PdfMerger, PdfReader, PdfWriter # Para manipular archivos
import os
import json


# -CLASES DEL BACKEND

class UsuarioSesion:
    # Administra el historial de archivos recientes y su persistencia en JSON
    def __init__(self):
        self.archivo_config = "config_docufacil.json"
        self.recientes = []
        self.cargar_historial()

    def cargar_historial(self):
        # Carga la lista de recientes desde el disco
        if os.path.exists(self.archivo_config):
            try:
                with open(self.archivo_config, 'r', encoding='utf-8') as f: 
                    self.recientes = json.load(f).get("recientes", [])
            except: self.recientes = []

    def guardar_historial(self):
        # Guarda la lista actual de recientes en el archivo JSON
        with open(self.archivo_config, 'w', encoding='utf-8') as f: 
            json.dump({"recientes": self.recientes}, f, indent=4)

    def agregar_reciente(self, ruta):
        # Añade una ruta al inicio, evita duplicados y limita a 5 elementos
        if ruta in self.recientes: self.recientes.remove(ruta)
        self.recientes.insert(0, ruta)
        if len(self.recientes) > 5: self.recientes.pop()
        self.guardar_historial()

class VisualizadorLogica:
    # Maneja la lógica de apertura y renderizado de páginas de PDF
    def __init__(self):
        self.doc = None
        self.pagina_actual = 0
        self.zoom = 1.0

    def cargar_documento(self, ruta):
        # Abre un PDF y resetea la vista a la página inicial
        if self.doc: self.doc.close()
        self.doc = fitz.open(ruta)
        self.pagina_actual = 0
        self.zoom = 1.0

    def obtener_imagen_pagina(self):
        # Convierte la página actual del PDF en una imagen para la UI
        if not self.doc: return None
        # Genera el mapa de píxeles con el zoom actual
        pix = self.doc.load_page(self.pagina_actual).get_pixmap(matrix=fitz.Matrix(self.zoom, self.zoom))
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        return ctk.CTkImage(light_image=img, dark_image=img, size=(pix.width, pix.height))

class GestorHerramientas:
    # Conjunto de herramientas estáticas para procesamiento de archivos

    @staticmethod
    def unir_pdfs(lista, salida):
        # Combina múltiples archivos PDF en una sola ruta de salida
        try:
            merger = PdfMerger()
            for pdf in lista: merger.append(pdf)
            merger.write(salida)
            merger.close()
            return True, "Unión exitosa."
        except Exception as e: return False, str(e)

    @staticmethod
    def dividir_pdf(ruta, pag_inicio, pag_fin, salida):
        # Corta un rango de páginas de un PDF y crea un nuevo archivo
        try:
            reader = PdfReader(ruta)
            writer = PdfWriter()
            # Itera en el rango de páginas (ajustando a índice base 0)
            for i in range(max(0, int(pag_inicio)-1), min(len(reader.pages), int(pag_fin))): 
                writer.add_page(reader.pages[i])
            with open(salida, "wb") as f: writer.write(f)
            return True, "División exitosa."
        except Exception as e: return False, str(e)

    @staticmethod
    def imagenes_a_pdf(lista_img, salida):
        # Convierte y empaqueta una lista de imágenes en un archivo PDF
        try:
            if not lista_img: return False, "No hay imágenes."
            imgs = [Image.open(img).convert('RGB') for img in lista_img]
            imgs[0].save(salida, save_all=True, append_images=imgs[1:])
            return True, "Conversión exitosa."
        except Exception as e: return False, str(e)

    @staticmethod
    def pdf_a_imagenes(ruta, carpeta_salida):
        # Exporta cada página de un PDF como una imagen PNG independiente
        try:
            doc = fitz.open(ruta)
            base = os.path.splitext(os.path.basename(ruta))[0]
            for i in range(len(doc)): 
                # Renderizado de alta calidad (2.0) para la exportación
                doc.load_page(i).get_pixmap(matrix=fitz.Matrix(2.0, 2.0)).save(
                    os.path.join(carpeta_salida, f"{base}_{i+1}.png"))
            doc.close()
            return True, "Extracción exitosa."
        except Exception as e: return False, str(e)