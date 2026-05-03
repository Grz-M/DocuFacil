from docufacil_backend import *


# -CONFIGURACIÓN VISUAL

ctk.set_appearance_mode("Dark") 
ctk.set_default_color_theme("blue")

class Aplicacion(ctk.CTk):
    # Interfaz principal de DocuFácil que conecta la lógica con el diseño visual

    def __init__(self):
        super().__init__()
        self.title("DocuFácil - Gestión de Documentos")
        self.geometry("1000x700")
        
        # Inicialización de módulos lógicos y variables de estado
        self.sesion = UsuarioSesion()
        self.motor_lector = VisualizadorLogica()
        self.archivos_unir, self.archivos_img = [], []
        self.archivo_dividir = self.archivo_pdf2img = None

        # Configuración del grid principal (Lateral y Principal)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # -PANEL LATERAL DE NAVEGACIÓN
        self.panel_lateral = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.panel_lateral.grid(row=0, column=0, sticky="nsew")
        self.panel_lateral.grid_rowconfigure(8, weight=1)

        self.lbl_logo = ctk.CTkLabel(self.panel_lateral, text="DocuFácil", font=ctk.CTkFont(size=22, weight="bold"))
        self.lbl_logo.grid(row=0, column=0, padx=20, pady=30)

        # Botones del menú lateral
        self.crear_btn_nav("🏠 Inicio", self.mostrar_pantalla_inicio, 1)
        self.crear_btn_nav("👁️ Lector PDF", self.mostrar_pantalla_lector, 2)
        self.crear_btn_nav("🔗 Unir PDFs", self.mostrar_pantalla_unir, 3)
        self.crear_btn_nav("✂️ Dividir PDF", self.mostrar_pantalla_dividir, 4)
        self.crear_btn_nav("🖼️ Img a PDF", self.mostrar_pantalla_img_a_pdf, 5)
        self.crear_btn_nav("📸 PDF a Img", self.mostrar_pantalla_pdf_a_img, 6)

        self.tema_opcion = ctk.CTkOptionMenu(self.panel_lateral, values=["Dark", "Light", "System"], command=ctk.set_appearance_mode)
        self.tema_opcion.grid(row=9, column=0, padx=20, pady=20)

        # - ÁREA DE CONTENIDO
        self.area_principal = ctk.CTkFrame(self, fg_color="transparent")
        self.area_principal.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.area_principal.grid_rowconfigure(0, weight=1)
        self.area_principal.grid_columnconfigure(0, weight=1)
        
        # Creación de frames para cada vista
        self.frame_inicio = ctk.CTkFrame(self.area_principal, fg_color="transparent")
        self.frame_lector = ctk.CTkFrame(self.area_principal, fg_color="transparent")
        self.frame_unir = ctk.CTkFrame(self.area_principal, fg_color="transparent")
        self.frame_dividir = ctk.CTkFrame(self.area_principal, fg_color="transparent")
        self.frame_img_a_pdf = ctk.CTkFrame(self.area_principal, fg_color="transparent")
        self.frame_pdf_a_img = ctk.CTkFrame(self.area_principal, fg_color="transparent")

        # Dibujar elementos en cada vista e iniciar en 'Inicio'
        self.crear_vista_inicio()
        self.crear_vista_lector()
        self.crear_vista_unir()
        self.crear_vista_dividir()
        self.crear_vista_img_a_pdf()
        self.crear_vista_pdf_a_img()
        self.mostrar_pantalla_inicio()

    def crear_btn_nav(self, texto, comando, fila):
        # Helper para crear botones de navegación consistentes
        btn = ctk.CTkButton(self.panel_lateral, text=texto, corner_radius=0, height=45, 
                            fg_color="transparent", text_color=("black", "white"), 
                            hover_color=("gray75", "gray30"), anchor="w", command=comando)
        btn.grid(row=fila, column=0, sticky="ew")


    # -DISEÑO DE VISTAS

    def crear_vista_inicio(self):
        # Vista de bienvenida y archivos recientes
        self.frame_inicio.grid_rowconfigure(3, weight=1)
        self.frame_inicio.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(self.frame_inicio, text="Bienvenido a DocuFácil", font=ctk.CTkFont(size=28, weight="bold")).grid(row=0, column=0, pady=(40, 20))
        ctk.CTkButton(self.frame_inicio, text="Abrir Nuevo Documento", command=self.accion_abrir_desde_inicio, height=40).grid(row=1, column=0, pady=10)
        ctk.CTkLabel(self.frame_inicio, text="Archivos Recientes", font=ctk.CTkFont(size=16)).grid(row=2, column=0, sticky="w", padx=40, pady=(20,5))
        self.lista_recientes = ctk.CTkScrollableFrame(self.frame_inicio, width=600, height=350)
        self.lista_recientes.grid(row=3, column=0, padx=40, pady=10, sticky="nsew")

    def crear_vista_lector(self):
        # Vista para leer y navegar por el PDF
        self.frame_lector.grid_rowconfigure(1, weight=1)
        self.frame_lector.grid_columnconfigure(0, weight=1)
        barra = ctk.CTkFrame(self.frame_lector, height=50)
        barra.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        ctk.CTkButton(barra, text="-", width=40, command=self.lector_zoom_out).pack(side="left", padx=5)
        ctk.CTkButton(barra, text="+", width=40, command=self.lector_zoom_in).pack(side="left", padx=5)
        ctk.CTkButton(barra, text="<", width=40, command=self.lector_pag_ant).pack(side="left", padx=(20,5))
        self.lbl_paginacion = ctk.CTkLabel(barra, text="Página 0 / 0")
        self.lbl_paginacion.pack(side="left", padx=10)
        ctk.CTkButton(barra, text=">", width=40, command=self.lector_pag_sig).pack(side="left", padx=5)
        
        area_doc = ctk.CTkScrollableFrame(self.frame_lector, fg_color=("gray85", "gray25"))
        area_doc.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.lbl_render = ctk.CTkLabel(area_doc, text="Ningún archivo cargado")
        self.lbl_render.pack(expand=True, pady=50)

    def crear_vista_unir(self):
        # Panel para combinar PDFs
        self.frame_unir.grid_rowconfigure(1, weight=1)
        self.frame_unir.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(self.frame_unir, text="Unir Múltiples PDFs", font=ctk.CTkFont(size=22, weight="bold")).grid(row=0, column=0, pady=20)
        self.lista_unir = ctk.CTkScrollableFrame(self.frame_unir, width=600, height=300)
        self.lista_unir.grid(row=1, column=0, padx=50, sticky="nsew")
        ctk.CTkButton(self.frame_unir, text="Agregar Archivos", command=self.accion_explorar_unir).grid(row=2, column=0, pady=10)
        ctk.CTkButton(self.frame_unir, text="Procesar y Guardar", fg_color="#28a745", hover_color="#218838", text_color="white", command=self.accion_procesar_unir).grid(row=3, column=0, pady=20)

    def crear_vista_dividir(self):
        # Panel para extraer rangos de páginas
        ctk.CTkLabel(self.frame_dividir, text="Extraer Páginas", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=20)
        self.lbl_archivo_dividir = ctk.CTkLabel(self.frame_dividir, text="Ningún archivo seleccionado")
        self.lbl_archivo_dividir.pack(pady=10)
        ctk.CTkButton(self.frame_dividir, text="Seleccionar PDF", command=self.accion_explorar_dividir).pack(pady=10)
        f_r = ctk.CTkFrame(self.frame_dividir, fg_color="transparent")
        f_r.pack(pady=20)
        self.ent_desde = ctk.CTkEntry(f_r, placeholder_text="Desde", width=80); self.ent_desde.grid(row=0, column=0, padx=10)
        self.ent_hasta = ctk.CTkEntry(f_r, placeholder_text="Hasta", width=80); self.ent_hasta.grid(row=0, column=1, padx=10)
        ctk.CTkButton(self.frame_dividir, text="Extraer Rango", fg_color="#28a745", hover_color="#218838", text_color="white", command=self.accion_procesar_dividir).pack(pady=10)

    def crear_vista_img_a_pdf(self):
        # Panel para convertir fotos a PDF
        self.frame_img_a_pdf.grid_rowconfigure(1, weight=1)
        self.frame_img_a_pdf.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(self.frame_img_a_pdf, text="Imágenes a PDF", font=ctk.CTkFont(size=22, weight="bold")).grid(row=0, column=0, pady=20)
        self.lista_img2pdf = ctk.CTkScrollableFrame(self.frame_img_a_pdf, width=600, height=300)
        self.lista_img2pdf.grid(row=1, column=0, padx=50, sticky="nsew")
        ctk.CTkButton(self.frame_img_a_pdf, text="Agregar Imágenes", command=self.accion_explorar_img2pdf).grid(row=2, column=0, pady=10)
        ctk.CTkButton(self.frame_img_a_pdf, text="Convertir", fg_color="#28a745", hover_color="#218838", text_color="white", command=self.accion_procesar_img2pdf).grid(row=3, column=0, pady=20)

    def crear_vista_pdf_a_img(self):
        # Panel para exportar páginas como imágenes
        ctk.CTkLabel(self.frame_pdf_a_img, text="PDF a Imágenes", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=20)
        self.lbl_archivo_pdf2img = ctk.CTkLabel(self.frame_pdf_a_img, text="Ningún archivo seleccionado")
        self.lbl_archivo_pdf2img.pack(pady=10)
        ctk.CTkButton(self.frame_pdf_a_img, text="Seleccionar PDF", command=self.accion_explorar_pdf2img).pack(pady=10)
        ctk.CTkButton(self.frame_pdf_a_img, text="Extraer Imágenes", fg_color="#28a745", hover_color="#218838", text_color="white", command=self.accion_procesar_pdf2img).pack(pady=20)


    # -CONTROLADORES Y LÓGICA DE EVENTOS
    
    def refrescar_lista_recientes(self):
        # Actualiza visualmente la lista de historial desde la sesión
        for widget in self.lista_recientes.winfo_children(): widget.destroy()
        for ruta in self.sesion.recientes:
            if os.path.exists(ruta):
                ctk.CTkButton(self.lista_recientes, text=f"📄 {os.path.basename(ruta)}", 
                              fg_color="transparent", text_color=("black", "white"), hover_color=("gray75", "gray30"),
                              anchor="w", command=lambda r=ruta: self.abrir_en_lector(r)).pack(fill="x", pady=2)

    def accion_abrir_desde_inicio(self):
        # Carga un archivo PDF seleccionado por el usuario
        ruta = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")]); 
        if ruta: self.abrir_en_lector(ruta)

    def abrir_en_lector(self, ruta):
        # Inicia el motor de renderizado y cambia a la pantalla del lector
        self.sesion.agregar_reciente(ruta); 
        self.refrescar_lista_recientes()
        self.motor_lector.cargar_documento(ruta); 
        self.lector_actualizar_pantalla(); 
        self.mostrar_pantalla_lector()

    def lector_actualizar_pantalla(self):
        # Renderiza la página actual del documento en el Label principal
        if not self.motor_lector.doc: return
        img = self.motor_lector.obtener_imagen_pagina()
        if img:
            self.lbl_render.configure(image=img, text="")
            self.lbl_paginacion.configure(text=f"Página {self.motor_lector.pagina_actual + 1} / {len(self.motor_lector.doc)}")

    # Controles del Lector (Páginas y Zoom)
    def lector_pag_sig(self):
        if self.motor_lector.doc and self.motor_lector.pagina_actual < len(self.motor_lector.doc) - 1:
            self.motor_lector.pagina_actual += 1; self.lector_actualizar_pantalla()
    def lector_pag_ant(self):
        if self.motor_lector.doc and self.motor_lector.pagina_actual > 0:
            self.motor_lector.pagina_actual -= 1; self.lector_actualizar_pantalla()
    def lector_zoom_in(self):
        self.motor_lector.zoom += 0.2; self.lector_actualizar_pantalla()
    def lector_zoom_out(self):
        if self.motor_lector.zoom > 0.4: self.motor_lector.zoom -= 0.2; self.lector_actualizar_pantalla()

    # Lógica para Herramientas (Unir, Dividir, Conversión)
    def accion_explorar_unir(self):
        rutas = filedialog.askopenfilenames(filetypes=[("PDF", "*.pdf")])
        for r in rutas:
            self.archivos_unir.append(r)
            ctk.CTkLabel(self.lista_unir, text=f"• {os.path.basename(r)}").pack(anchor="w", padx=10)

    def accion_procesar_unir(self):
        if len(self.archivos_unir) < 2: 
            return messagebox.showwarning("Unión pdfs", "[!] Se requieren al menos 2 PDFs.")    
        salida = filedialog.asksaveasfilename(defaultextension=".pdf")
        if salida:
            ok, msj = GestorHerramientas.unir_pdfs(self.archivos_unir, salida)
            messagebox.showinfo("Unión pdfs", msj)
            if ok:
                self.archivos_unir.clear()
                for w in self.lista_unir.winfo_children(): w.destroy()

    def accion_explorar_dividir(self):
        r = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
        if r:
            self.archivo_dividir = r
            self.lbl_archivo_dividir.configure(text=f"Archivo: {os.path.basename(r)}")

    def accion_procesar_dividir(self):
        ini, fin = self.ent_desde.get(), self.ent_hasta.get()
        if self.archivo_dividir and ini.isdigit() and fin.isdigit():
            salida = filedialog.asksaveasfilename(defaultextension=".pdf")
            if salida:
                ok, msj = GestorHerramientas.dividir_pdf(self.archivo_dividir, ini, fin, salida)
                messagebox.showinfo("División pdfs", msj)
        else:
            messagebox.showerror("División pdfs", "[!] Revisa el archivo y los campos de texto.")

    def accion_explorar_img2pdf(self):
        rutas = filedialog.askopenfilenames(filetypes=[("Imágenes", "*.png;*.jpg")])
        for r in rutas:
            self.archivos_img.append(r)
            ctk.CTkLabel(self.lista_img2pdf, text=f"• {os.path.basename(r)}").pack(anchor="w", padx=10)

    def accion_procesar_img2pdf(self):
        if not self.archivos_img: 
            return messagebox.showwarning("Imagen a pdf", "[!] Agrega imágenes primero.")
        salida = filedialog.asksaveasfilename(defaultextension=".pdf")
        if salida:
            ok, msj = GestorHerramientas.imagenes_a_pdf(self.archivos_img, salida)
            messagebox.showinfo("Imagen a pdf", msj)
            if ok:
                self.archivos_img.clear()
                for w in self.lista_img2pdf.winfo_children(): w.destroy()

    def accion_explorar_pdf2img(self):
        r = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
        if r:
            self.archivo_pdf2img = r
            self.lbl_archivo_pdf2img.configure(text=f"Archivo: {os.path.basename(r)}")

    def accion_procesar_pdf2img(self):
        if not self.archivo_pdf2img: 
            return messagebox.showwarning("Pdf a imagen", "[!] Selecciona un PDF.")
        
        carpeta = filedialog.askdirectory(title="Selecciona dónde guardar las imágenes")
        if carpeta:
            ok, msj = GestorHerramientas.pdf_a_imagenes(self.archivo_pdf2img, carpeta)
            messagebox.showinfo("Pdf a imagen", msj)
            if ok:
                self.archivo_pdf2img = None
                self.lbl_archivo_pdf2img.configure(text="Ningún archivo seleccionado")


    # -NAVEGACIÓN ENTRE PANTALLAS
    def ocultar_todos_los_frames(self):
        for f in [self.frame_inicio, self.frame_lector, self.frame_unir, self.frame_dividir, self.frame_img_a_pdf, self.frame_pdf_a_img]:
            f.grid_forget()

    def mostrar_pantalla_inicio(self): self.ocultar_todos_los_frames(); self.refrescar_lista_recientes(); self.frame_inicio.grid(row=0, column=0, sticky="nsew")
    def mostrar_pantalla_lector(self): self.ocultar_todos_los_frames(); self.frame_lector.grid(row=0, column=0, sticky="nsew")
    def mostrar_pantalla_unir(self): self.ocultar_todos_los_frames(); self.frame_unir.grid(row=0, column=0, sticky="nsew")
    def mostrar_pantalla_dividir(self): self.ocultar_todos_los_frames(); self.frame_dividir.grid(row=0, column=0, sticky="nsew")
    def mostrar_pantalla_img_a_pdf(self): self.ocultar_todos_los_frames(); self.frame_img_a_pdf.grid(row=0, column=0, sticky="nsew")
    def mostrar_pantalla_pdf_a_img(self): self.ocultar_todos_los_frames(); self.frame_pdf_a_img.grid(row=0, column=0, sticky="nsew")

if __name__ == "__main__":
    app = Aplicacion()
    app.mainloop()