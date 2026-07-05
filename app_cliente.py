import streamlit as st
import sqlite3
from datetime import datetime, timedelta

def conectar_db():
    # Se conecta a la base de datos centralizada
    return sqlite3.connect('tickets.db', check_same_thread=False)

st.set_page_config(page_title="Portal de Tickets TI", layout="centered")

# Encabezado limpio para el cliente
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
            
            # Asegurar la creación de la tabla
            cursor.execute('''CREATE TABLE IF NOT EXISTS tickets 
                (id INTEGER PRIMARY KEY AUTOINCREMENT, cliente TEXT, descripcion TEXT, tipo_poliza TEXT, fecha_creacion TEXT, fecha_limite TEXT, estado TEXT, foto BLOB, comentarios_cierre TEXT)''')
            
            ahora = datetime.now()
            # Cálculo base de SLA inicial
            horas_sla = 4 if "Sí" in poliza else 24
            limite = ahora + timedelta(hours=horas_sla)
            
            foto_bytes = foto.read() if foto is not None else None
            
            cursor.execute('''INSERT INTO tickets (cliente, descripcion, tipo_poliza, fecha_creacion, fecha_limite, estado, foto, comentarios_cierre)
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
                           (cliente, descripcion, "Con Póliza" if "Sí" in poliza else "Estándar", ahora.strftime("%Y-%m-%d %H:%M"), limite.strftime("%Y-%m-%d %H:%M"), "Pendiente", foto_bytes, ""))
            conn.commit()
            conn.close()
            st.success("¡Tu reporte ha sido recibido con éxito! Un ingeniero de soporte tomará el caso.")
        else:
            st.error("Por favor completa los campos obligatorios (*).")