import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import time

st.title("Mapa de Sucursales (Versión Gratis Mejorada)")

uploaded_file = st.file_uploader("Sube el archivo con las sucursales", type=["csv", "xlsx"])

if not uploaded_file:
    st.stop()

# Leer archivo
df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith(".xlsx") else pd.read_csv(uploaded_file)

st.write("### Columnas detectadas:")
st.write(df.columns)

# Verificar columna
col_sucursal = None
for c in df.columns:
    if "sucursal" in c.lower():
        col_sucursal = c
        break

if col_sucursal is None:
    st.error("No encuentro una columna con el nombre 'Sucursal'.")
    st.stop()

# Geocodificador
geolocator = Nominatim(user_agent="tiendas_app")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

df["lat"] = None
df["lon"] = None

progress = st.progress(0)
total = len(df)

st.write("### Geocodificando...")

for i, row in df.iterrows():
    nombre = row[col_sucursal]

    query = f"Tienda {nombre}, Mexico"   # IMPORTANTE: mejora los resultados

    try:
        location = geocode(query)
        if location:
            df.at[i, "lat"] = location.latitude
            df.at[i, "lon"] = location.longitude
    except:
        pass

    progress.progress((i+1)/total)

st.write("### Resultado de geocodificación:")
st.dataframe(df[[col_sucursal, "lat", "lon"]])

df_mapa = df.dropna(subset=["lat", "lon"])

if df_mapa.empty:
    st.error("Ninguna sucursal obtuvo coordenadas. Necesito ver un ejemplo real.")
else:
    st.write("### Mapa")
    st.map(df_mapa, latitude="lat", longitude="lon")
