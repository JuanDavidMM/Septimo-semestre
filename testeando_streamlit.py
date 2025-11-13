import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("Extracto de Ventas")

# Subida del archivo
uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")

if uploaded_file is None:
    st.info("Necesitas ingresar el archivo")
    st.stop()
else:
    # Leer Excel
    df = pd.read_excel(uploaded_file)


    # Vista previa
    st.subheader("Data Preview")
    st.write(df.head())

    # Menú para elegir región
    opciones = df["REGION"].unique()
    filtro = st.selectbox("Selecciona una Región", opciones)

    # Filtra los datos
    datos_filtrados = df[df["REGION"] == filtro]
    st.write(datos_filtrados)

    # Métricas resumidas
    st.subheader("Resumen de la Región seleccionada")
    col1, col2, col3 = st.columns(3)
    col1.metric("Ventas Totales", datos_filtrados["VENTAS TOTALES"].astype(float).sum())
    col2.metric("Unidades Vendidas", datos_filtrados["UNIDADES VENDIDAS"].astype(float).sum())
    col3.metric("Promedio de % Ventas", round(datos_filtrados["PORCENTAJE DE VENTAS"].astype(float).mean(), 4))


    #Gráficas por Región
    #Haciendo agrupaciones por región y con datos sumados y para porcentaje con promedio
    resumen_region = df.groupby("REGION")[["UNIDADES VENDIDAS", "VENTAS TOTALES"]].sum().reset_index()
    resumen_region_porc = df.groupby("REGION")[["PORCENTAJE DE VENTAS"]].mean().reset_index()

    st.subheader("Unidades Vendidas por Región")
    st.bar_chart(resumen_region.set_index("REGION")["UNIDADES VENDIDAS"])

    st.subheader("Ventas Totales por Región")
    st.bar_chart(resumen_region.set_index("REGION")["VENTAS TOTALES"])

    st.subheader("Porcentaje Promedio de Ventas por Región")
    st.bar_chart(resumen_region_porc.set_index("REGION")["PORCENTAJE DE VENTAS"])

    # Selección de vendedor pero concatenamos primero y al desplegarlo usamos el ID para desplegar la info
    df["Vendedor"] = df["ID"].astype(str) + " - " + df["NOMBRE"] + " " + df["APELLIDO"]

    vendedor_sel = st.selectbox("Elige un vendedor", df["Vendedor"].unique())
    id_vendedor = vendedor_sel.split(" - ")[0]
    st.write(df[df["ID"].astype(str) == id_vendedor])

    



    
