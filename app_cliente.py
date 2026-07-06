import streamlit as st
import sqlite3
import os
from datetime import datetime, timedelta

def conectar_db():
    ruta_carpeta = os.path.join(os.path.expanduser("~"), "Documents", "AppTickets")
    if not os.path.exists(ruta_carpeta):
        os.makedirs(ruta_carpeta)
    ruta_db = os.path.join(ruta_carpeta, "tickets.db")
    # isolation_level=None fuerza a SQLite a guardar los datos inmediatamente (Autocommit)
    return sqlite3.connect(ruta_db, check_same_thread=False, isolation_level=None)

st.set_page_config(page_title="Portal de Tickets TI", layout="centered")

st.title("🛠️ Portal de Servicio Técnico TI")
st.subheader("Escanea y reporta tu falla de inmediato")

with st.form("form_cliente", clear_on_submit=True):
    cliente = st.text_input("Nombre de tu Empresa / Cliente *")
    descripcion = st.text_area("Describe detalladamente el problema de TI *")
    poliza = st.selectbox("¿Cuenta con Póliza de Servicio contratada?", ["No (Soporte Estándar)", "Sí (Prioridad SLA)"])
    foto = st.file_uploader("Subir foto de evidencia (Opcional)", type=["png", "jpg", "jpeg"])
    
    boton_enviar = st.form_submit_button("Enviar Orden de Servicio")
    
    if boton_enviar:
        if cliente and descripcion:
            conn = conectar_db()
            cursor = conn.cursor()
            
            cursor.execute('''CREATE TABLE IF NOT EXISTS tickets 
                (id INTEGER PRIMARY KEY AUTOINCREMENT, cliente TEXT, descripcion TEXT, tipo_poliza TEXT, 
                 fecha_creacion TEXT, fecha_limite TEXT, estado TEXT, foto BLOB, comentarios_cierre TEXT)''')
            
            ahora = datetime.now()
            horas_sla = 4 if "Sí" in poliza else 24
            limite = ahora + timedelta(hours=horas_sla)
            foto_bytes = foto.read() if foto is not None else None
            
            cursor.execute('''INSERT INTO tickets (cliente, descripcion, tipo_poliza, fecha_creacion, fecha_limite, estado, foto, comentarios_cierre)
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
                           (cliente, descripcion, "Con Póliza" if "Sí" in poliza else "Estándar", ahora.strftime("%Y-%m-%d %H:%M"), limite.strftime("%Y-%m-%d %H:%M"), "Pendiente", foto_bytes, ""))
            
            conn.close() # Cierre absoluto para liberar el archivo
            st.success("¡Tu reporte ha sido enviado! Abre el panel de administración y presiona Actualizar.")
        else:
            st.error("Por favor completa los campos obligatorios (*).")