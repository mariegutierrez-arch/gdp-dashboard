import streamlit as st
import math
import pandas as pd
from datetime import date
import io

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Sistema 3D Archery Org", page_icon="🎯", layout="wide")

# --- MEMORIA DE LA SESIÓN ---
if "dianas_guardadas" not in st.session_state:
    st.session_state.dianas_guardadas = []

if "tiros_arqueros" not in st.session_state:
    st.session_state.tiros_arqueros = []

if "info_torneos" not in st.session_state:
    st.session_state.info_torneos = {}

# --- FUNCIÓN AUXILIAR PARA CREAR ARCHIVO EXCEL ---
def convertir_a_excel(df: pd.DataFrame) -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Reporte')
    return output.getvalue()

# --- BASE DE DATOS DE ANIMALES 3D ---
FAUNA_3D = {
    "Ciervo Rojo / Wapití": {
        "area_vital": 300.0, "area_total": 1200.0, "grupo": 1,
        "imagen": "https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/1f98c.png"
    },
    "Oso Negro / Pardo": {
        "area_vital": 250.0, "area_total": 1000.0, "grupo": 1,
        "imagen": "https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/1f43b.png"
    },
    "Jabalí / Pecarí": {
        "area_vital": 180.0, "area_total": 700.0, "grupo": 2,
        "imagen": "https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/1f417.png"
    },
    "Lobo Gris": {
        "area_vital": 150.0, "area_total": 550.0, "grupo": 2,
        "imagen": "https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/1f43a.png"
    },
    "Puma / Cougar": {
        "area_vital": 140.0, "area_total": 500.0, "grupo": 2,
        "imagen": "https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/1f406.png"
    },
    "Conejo de Campo": {
        "area_vital": 40.0, "area_total": 150.0, "grupo": 4,
        "imagen": "https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/1f407.png"
    },
    "Liebre": {
        "area_vital": 45.0, "area_total": 180.0, "grupo": 4,
        "imagen": "https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/1f407.png"
    },
    "Pavo Salvaje": {
        "area_vital": 50.0, "area_total": 200.0, "grupo": 4,
        "imagen": "https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/1f883.png"
    },
    "Halcón": {
        "area_vital": 30.0, "area_total": 110.0, "grupo": 4,
        "imagen": "https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/1f985.png"
    },
    "Perdiz / Codorniz": {
        "area_vital": 25.0, "area_total": 90.0, "grupo": 4,
        "imagen": "https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/1f424.png"
    }
}

# --- LÓGICA DE CÁLCULO DIFICULTAD ---
def calcular_dificultad(distancia, angulo, area_vital, area_total, categoria):
    coeficientes = {'compuesto': 0.70, 'recurvo': 1.00, 'barebow': 1.30, 'tradicional': 1.60}
    k_cat = coeficientes.get(categoria.lower(), 1.00)
    
    rad_tiro = math.radians(angulo)
    cos_tiro = math.cos(rad_tiro) if math.cos(math.radians(angulo)) != 0 else 0.0001

    factor_distancia = ((distancia / 10) ** 2) * (1 / cos_tiro)
    factor_blanco = 1000 / (area_vital + math.sqrt(area_total))
    
    return factor_distancia * factor_blanco * k_cat

# --- ENCABEZADO ---
st.title("🎯 Control de Torneos 3D y Ranking de Arqueros")
st.caption("Puntuación oficial Archery Org, cálculo de dianas y desempeño de tiradores.")

# --- ESTRUCTURA DE PESTAÑAS ---
tab1, tab2, tab3 = st.tabs([
    "⚙️ Dificultad de Dianas", 
    "🎯 Puntuación Archery Org", 
    "🏆 Ranking de Arqueros"
])

# ==========================================
# PESTAÑA 1: DIFICULTAD Y CARACTERÍSTICAS
# ==========================================
with tab1:
    with st.expander("📍 Información General del Torneo y Clima", expanded=True):
        col_t1, col_t2, col_t3 = st.columns(3)
        with col_t1:
            nombre_torneo = st.text_input("Nombre del Torneo", value="Torneo Oficial 2026")
            lugar_torneo = st.text_input("Lugar / Sede", value="Campo de Tiro 3D")
        with col_t2:
            fecha_torneo = st.date_input("Fecha del Evento", value=date.today())
            condicion_clima = st.selectbox("🌤️ Estado del Clima", ["Soleado", "Nublado", "Lluvia Ligera", "Viento Fuerte", "Niebla"])
        with col_t3:
            temperatura = st.number_input("🌡️ Temperatura (°C)", value=20)
            viento_velocidad = st.number_input("💨 Vel. del Viento (km/h)", value=10)
        
        st.session_state.info_torneos[nombre_torneo] = {
            "Lugar": lugar_torneo,
            "Fecha": str(fecha_torneo),
            "Clima": f"{condicion_clima}, {temperatura}°C, Viento: {viento_velocidad} km/h"
        }

    st.divider()

    col_a, col_b = st.columns([1, 1])
    
    with col_a:
        st.subheader("Configuración de Estación")
        num_estacion = st.number_input("Número de Estación / Diana", min_value=1, value=1)
        cat_seleccionada = st.selectbox("🏹 Categoría", ["Compuesto", "Recurvo", "Barebow", "Tradicional"])
        
        animal_sel = st.selectbox("🦌 Especie de Animal 3D", list(FAUNA_3D.keys()))
        datos_animal = FAUNA_3D[animal_sel]
        
        col_img, col_txt = st.columns([1, 2])
        with col_img:
            st.image(datos_animal["imagen"], width=100)
        with col_txt:
            st.markdown(f"**Especie:** {animal_sel}")
            st.caption(f"**Grupo:** {datos_animal['grupo']}")
            st.caption(f"**Zona Vital:** {datos_animal['area_vital']} cm² | **Área Total:** {datos_animal['area_total']} cm²")
        
        distancia = st.number_input("📏 Distancia real (m)", value=25, min_value=1)
        angulo = st.number_input("📐 Ángulo (°)", value=0)

        if st.button("➕ Guardar Diana", type="primary", use_container_width=True):
            id_calc = calcular_dificultad(distancia, angulo, datos_animal['area_vital'], datos_animal['area_total'], cat_seleccionada)
            info_clima_actual = st.session_state.info_torneos[nombre_torneo]["Clima"]
            
            st.session_state.dianas_guardadas.append({
                "Torneo": nombre_torneo,
                "Lugar": lugar_torneo,
                "Fecha": str(fecha_torneo),
                "Clima": info_clima_actual,
                "Estación": f"#{num_estacion}",
                "Animal": animal_sel,
                "Categoría": cat_seleccionada,
                "Distancia (m)": distancia,
                "Índice Dificultad": round(id_calc, 2)
            })
            st.success("¡Diana registrada en el historial!")

    with col_b:
        st.subheader("📋 Registro de la Sesión")
        if st.session_state.dianas_guardadas:
            df_dianas = pd.DataFrame(st.session_state.dianas_guardadas)
            st.dataframe(df_dianas, use_container_width=True)
            
            # Botón de Descarga Excel de Dianas
            excel_dianas = convertir_a_excel(df_dianas)
            st.download_button(
                label="📊 Descargar Dianas en Excel (.xlsx)",
                data=excel_dianas,
                file_name=f"dianas_{nombre_torneo.lower().replace(' ', '_')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
            
            if st.button("🗑️ Limpiar Dianas"):
                st.session_state.dianas_guardadas = []
                st.rerun()
        else:
            st.info("Sin dianas guardadas.")

# ==========================================
# PESTAÑA 2: PUNTUACIÓN ARCHERY ORG
# ==========================================
with tab2:
    st.subheader("🎯 Cómputo de Flechas (Reglamento 3D Archery Org)")
    st.markdown("""
    **Tabla de Puntos:**
    * **11 Puntos:** Centro Vital Interno (*Spider/11 ring*)
    * **10 Puntos:** Zona Vital (*10 ring*)
    * **8 Puntos:** Zona de Vital Extendida / Cuerpo (*8 ring*)
    * **5 Puntos:** Zona de Diana / Pezuña o Cuerno (*Line/Body*)
    * **0 Puntos:** Miss / Fallo
    """)
    st.divider()

    col_p1, col_p2 = st.columns([1, 1])
    
    with col_p1:
        arquero_nombre = st.text_input("Nombre del Arquero", value="Arquero 1")
        torneo_tiro = st.selectbox("Torneo Actual", list(st.session_state.info_torneos.keys()) if st.session_state.info_torneos else [nombre_torneo])
        num_diana_tiro = st.number_input("Estación / Diana Número", min_value=1, value=1, key="diana_tiro")
        
        zona_impacto = st.radio(
            "Impacto de la Flecha:",
            options=[11, 10, 8, 5, 0],
            format_func=lambda x: f"{x} Puntos - " + (
                "Centro Vital (11)" if x == 11 else
                "Zona Vital (10)" if x == 10 else
                "Zona Vital Extendida (8)" if x == 8 else
                "Cuerpo / Diana (5)" if x == 5 else "Fallo / Miss (0)"
            )
        )

        if st.button("📝 Registrar Flecha", use_container_width=True):
            st.session_state.tiros_arqueros.append({
                "Arquero": arquero_nombre,
                "Torneo": torneo_tiro,
                "Diana": f"#{num_diana_tiro}",
                "Puntos": zona_impacto,
                "Es_Vital": 1 if zona_impacto in [11, 10] else 0
            })
            st.success(f"¡{zona_impacto} puntos registrados para {arquero_nombre}!")

    with col_p2:
        st.subheader("Historial de Flechas")
        if st.session_state.tiros_arqueros:
            st.dataframe(pd.DataFrame(st.session_state.tiros_arqueros), use_container_width=True)
            if st.button("🗑️ Borrar Historial de Tiros"):
                st.session_state.tiros_arqueros = []
                st.rerun()

# ==========================================
# PESTAÑA 3: RANKING Y DESEMPEÑO
# ==========================================
with tab3:
    st.subheader("🏆 Tabla de Posiciones y Rendimiento")
    
    if st.session_state.tiros_arqueros:
        df_tiros = pd.DataFrame(st.session_state.tiros_arqueros)
        
        ranking = df_tiros.groupby("Arquero").agg(
            Flechas_Tiradas=("Puntos", "count"),
            Puntaje_Total=("Puntos", "sum"),
            Promedio_por_Flecha=("Puntos", "mean"),
            Impactos_Vitales=("Es_Vital", "sum"),
            Puntaje_Máximo=("Puntos", "max")
        ).reset_index()

        ranking["% Efectividad Vital"] = (ranking["Impactos_Vitales"] / ranking["Flechas_Tiradas"]) * 100
        ranking = ranking.sort_values(by="Puntaje_Total", ascending=False).reset_index(drop=True)
        ranking.index += 1

        st.dataframe(
            ranking.style.format({
                "Promedio_por_Flecha": "{:.2f}",
                "% Efectividad Vital": "{:.1f}%"
            }),
            use_container_width=True
        )

        # Botón de Descarga Excel para el Ranking
        excel_ranking = convertir_a_excel(ranking)
        st.download_button(
            label="📥 Descargar Ranking General en Excel (.xlsx)",
            data=excel_ranking,
            file_name=f"ranking_{nombre_torneo.lower().replace(' ', '_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
            use_container_width=True
        )

        st.divider()
        st.markdown("**Comparativa Visual de Puntuaciones Totales**")
        st.bar_chart(ranking, x="Arquero", y="Puntaje_Total")
    else:
        st.info("Registra flechas en la pestaña 'Puntuación Archery Org' para visualizar el ranking.")