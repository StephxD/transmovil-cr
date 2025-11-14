import streamlit as st
import pandas as pd
import plotly.express as px

import folium
from streamlit_folium import folium_static

# ------------------------------------------------------------
# ----- Fuentes de datos -----
# ------------------------------------------------------------

# Archivo de datos de rutas de transporte
# Debe estar en: datos/rutas.xlsx
URL_DATOS_RUTAS = "tarea_3/datos/rutas.xlsx"



# ------------------------------------------------------------
# ----- Funciones para recuperar los datos -----
# ------------------------------------------------------------

@st.cache_data
def cargar_datos_rutas():
    """
    Carga los datos de rutas desde un archivo Excel y los devuelve
    como un DataFrame de pandas.
    Se almacena en caché para mejorar el rendimiento.
    """
    datos = pd.read_excel(URL_DATOS_RUTAS)
    # Aseguramos que las columnas clave existan:
    # ruta, tipo, region, lat, lon, velocidad_promedio, demora_minutos
    return datos


# ------------------------------------------------------------
# ----- Título de la aplicación -----
# ------------------------------------------------------------

st.title("🚍 TransMovil CR - Rutas de transporte")
st.caption("Aplicación interactiva para visualizar rutas, velocidades y congestión.")


# ------------------------------------------------------------
# ----- Carga de datos -----
# ------------------------------------------------------------

estado_carga = st.text("Cargando datos de rutas...")
rutas = cargar_datos_rutas()
estado_carga.text("Los datos de rutas fueron cargados correctamente")


# ------------------------------------------------------------
# ----- Preparación de datos -----
# ------------------------------------------------------------

# Renombrar columnas a algo más legible 
rutas = rutas.rename(columns={
    "ruta": "Ruta",
    "tipo": "Tipo de transporte",
    "region": "Región",
    "lat": "Latitud",
    "lon": "Longitud",
    "velocidad_promedio": "Velocidad promedio (km/h)",
    "demora_minutos": "Demora (min)"
})

# ------------------------------------------------------------
# ----- Lista de selección en la barra lateral -----
# ------------------------------------------------------------

st.sidebar.header("⚙️ Filtros de visualización")

# Listas de opciones
lista_tipos = rutas["Tipo de transporte"].unique().tolist()
lista_tipos.sort()

lista_regiones = rutas["Región"].unique().tolist()
lista_regiones.sort()

# Selectbox / multiselect
tipo_seleccionado = st.sidebar.multiselect(
    "Tipo de transporte",
    options=lista_tipos,
    default=lista_tipos
)

region_seleccionada = st.sidebar.multiselect(
    "Región",
    options=lista_regiones,
    default=lista_regiones
)

# ----- Filtrar datos según la selección -----

rutas_filtradas = rutas[
    (rutas["Tipo de transporte"].isin(tipo_seleccionado)) &
    (rutas["Región"].isin(region_seleccionada))
].copy()


# ------------------------------------------------------------
# ----- Tabla interactiva -----
# ------------------------------------------------------------

st.subheader("📋 Rutas de transporte")
st.dataframe(rutas_filtradas, hide_index=True, use_container_width=True)


# ------------------------------------------------------------
# ----- Gráfico estadístico interactivo -----
# ------------------------------------------------------------

st.subheader("📈 Velocidad promedio por tipo de transporte")

# Agrupar por tipo de transporte
velocidad_por_tipo = (
    rutas_filtradas
    .groupby("Tipo de transporte")["Velocidad promedio (km/h)"]
    .mean()
    .reset_index()
)

fig_vel = px.bar(
    velocidad_por_tipo,
    x="Tipo de transporte",
    y="Velocidad promedio (km/h)",
    color="Tipo de transporte",
    title="Velocidad promedio por tipo de transporte",
    text_auto=True,
    labels={
        "Tipo de transporte": "Tipo de transporte",
        "Velocidad promedio (km/h)": "Velocidad promedio (km/h)"
    }
)

fig_vel.update_layout(
    xaxis_title="Tipo de transporte",
    yaxis_title="Velocidad promedio (km/h)",
    template="plotly_white"
)

st.plotly_chart(fig_vel, use_container_width=True)


# ------------------------------------------------------------
# ----- Mapa interactivo con Folium -----
# ------------------------------------------------------------

st.subheader("🗺️ Mapa interactivo de rutas y puntos de congestión")

# Si no hay datos filtrados, evitamos error
if rutas_filtradas.empty:
    st.warning("No hay rutas que coincidan con los filtros seleccionados.")
else:
    # Coordenadas iniciales: promedio de latitud y longitud
    centro_lat = rutas_filtradas["Latitud"].mean()
    centro_lon = rutas_filtradas["Longitud"].mean()

    mapa = folium.Map(location=[centro_lat, centro_lon], zoom_start=10)

    # Paleta sencilla de colores por tipo de transporte
    colores_tipo = {
        "Autobús": "blue",
        "Bus": "blue",
        "Tren": "red",
        "Taxi": "orange"
    }

    for _, fila in rutas_filtradas.iterrows():
        tipo = fila["Tipo de transporte"]
        color = colores_tipo.get(tipo, "green")

        popup_text = (
            f"<b>Ruta:</b> {fila['Ruta']}<br>"
            f"<b>Tipo:</b> {fila['Tipo de transporte']}<br>"
            f"<b>Región:</b> {fila['Región']}<br>"
            f"<b>Velocidad:</b> {fila['Velocidad promedio (km/h)']} km/h<br>"
            f"<b>Demora:</b> {fila['Demora (min)']} min"
        )

        folium.CircleMarker(
            location=[fila["Latitud"], fila["Longitud"]],
            radius=6,
            color=color,
            fill=True,
            fill_opacity=0.8,
            popup=folium.Popup(popup_text, max_width=250),
            tooltip=fila["Ruta"]
        ).add_to(mapa)

    # Mostrar el mapa en Streamlit
    folium_static(mapa)


# ------------------------------------------------------------
# ----- Pie de página -----
# ------------------------------------------------------------

st.markdown("---")
st.caption("Tarea 03 · Stephanie Oviedo")
