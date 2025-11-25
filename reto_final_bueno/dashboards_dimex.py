import streamlit as st
import pandas as pd

from data_dimex import build_filters
from metrics_dimex import compute_kpis
from components_dimex import (
    render_kpi_cards,
    render_risk_chart,
    render_metrics_tab,
    admin_chart_bubble,
    admin_chart_heatmap,
    admin_chart_rankings,
    admin_chart_clusters,
    admin_chart_growth_vs_risk,
)
from ml_clusters_dimex import render_cluster_tab
from chatbot_dimex import render_chatbot_tab  # <-- agregado

def render_admin_dashboard():
    # Filtros (sidebar) y datos filtrados
    df_filtered, region_sel, zona_sel, sucursal_sel = build_filters()

    if df_filtered is None or df_filtered.empty:
        st.info("Carga una base y/o ajusta los filtros para ver información.")
        return

    # Tabs principales del dashboard (agregado Chatbot como tab 4)
    tab_resumen, tab_ml, tab_table, tab_chatbot = st.tabs(
        [
            "📊 Resumen cartera",
            "🧠 Clusters ML por sucursal",
            "📑 Tabla detallada",
            "🤖 Chatbot IA"
        ]
    )

    # TAB 1: Resumen cartera
    with tab_resumen:
        with st.container():
            # KPIs generales
            kpis = compute_kpis(df_filtered)
            render_kpi_cards(kpis)

            region_txt = region_sel if region_sel != "Todas" else "todas las regiones"
            zona_txt = zona_sel if zona_sel != "Todas" else "todas las zonas"
            suc_txt = (
                sucursal_sel if sucursal_sel != "Todas" else "todas las sucursales"
            )

            st.caption(
                f"Vista actual: **{region_txt}** · **{zona_txt}** · **{suc_txt}** "
                f"— datos agregados directamente de la base de sucursales."
            )

            # Gráfica que ya tenías (riesgo top sucursales)
            render_risk_chart(df_filtered)

            # 🆕 NUEVO BLOQUE: gráficas avanzadas para admin
            st.markdown("### 🔍 Vista ejecutiva de riesgo por sucursal")
            admin_chart_bubble(df_filtered)
            admin_chart_heatmap(df_filtered)
            admin_chart_rankings(df_filtered)
            admin_chart_clusters(df_filtered)
            admin_chart_growth_vs_risk(df_filtered)

    # TAB 2: Clusters ML
    with tab_ml:
        render_cluster_tab(df_filtered)

    # TAB 3: Tabla detallada
    with tab_table:
        render_metrics_tab(df_filtered)

    # TAB 4: Chatbot
    with tab_chatbot:
        render_chatbot_tab(role="admin")


def render_employee_dashboard():
    """
    Vista para empleados: cada usuario sólo ve el detalle de SU sucursal.
    1) El empleado sube el archivo
    2) Selecciona sucursal
    3) Ingresa contraseña de sucursal
    4) Ve KPIs, cluster, gráficas y recomendaciones
    """
    from auth_dimex import BRANCH_PASSWORDS
    from ml_clusters_dimex import compute_cluster_scores
    from metrics_dimex import compute_kpis
    from components_dimex import (
        render_kpi_cards,
        render_cluster_badge,
        render_employee_risk_charts,
        render_branch_recommendations,
    )

    st.markdown("## 👷 Panel de empleado por sucursal")

    # 1. Subida de archivo específica para el empleado
    st.markdown("### 📂 Sube el archivo de sucursales")
    uploaded_file = st.file_uploader(
        "Carga el archivo con la información de sucursales (.xlsx o .csv)",
        type=["xlsx", "csv"],
        key="emp_file_uploader",
    )

    if uploaded_file is None:
        st.info("Por favor sube el archivo para poder ver la información de tu sucursal.")
        return

    # 2. Leer el archivo subido
    try:
        if uploaded_file.name.lower().endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"No se pudo leer el archivo. Revisa el formato. Detalle técnico: {e}")
        return

    if df is None or df.empty:
        st.warning("El archivo se leyó pero no contiene registros.")
        return

    # Validar que exista la columna Sucursal
    if "Sucursal" not in df.columns:
        st.error(
            "El archivo no tiene la columna 'Sucursal'. "
            "Verifica que el archivo tenga esa columna con ese nombre exacto."
        )
        return

    # 3. Calcular clusters si todavía no existen en el DataFrame
    if "Cluster_ML" not in df.columns:
        df = compute_cluster_scores(df)

    if "Cluster_ML" not in df.columns:
        st.warning(
            "No se encontró la columna 'Cluster_ML' después del cálculo. "
            "Revisa el módulo ml_clusters_dimex.py."
        )
        return

    # 4. Selección de sucursal
    sucursales = sorted(df["Sucursal"].dropna().unique())
    sucursal_sel = st.selectbox(
        "Selecciona tu sucursal",
        options=sucursales,
        key="emp_sucursal_select",
    )

    # 5. Validación de contraseña por sucursal
    st.markdown("### 🔑 Verificación de sucursal")
    st.caption(
        "Ingresa la contraseña asignada a tu sucursal. "
        "Si no la conoces, solicítala al administrador del sistema."
    )

    branch_pwd_conf = BRANCH_PASSWORDS.get(sucursal_sel)

    if branch_pwd_conf is None:
        st.error(
            "Esta sucursal todavía no tiene una contraseña configurada en "
            "`BRANCH_PASSWORDS` (archivo auth_dimex.py). "
            "Pídele al administrador que la registre."
        )
        return

    input_pwd = st.text_input(
        "Contraseña de la sucursal",
        type="password",
        key="emp_branch_pwd",
    )

    # Hasta que no escriba algo, no seguimos
    if input_pwd == "":
        st.stop()

    if input_pwd != branch_pwd_conf:
        st.error("Contraseña incorrecta. Verifica los datos e inténtalo nuevamente.")
        st.stop()

    # 6. Filtrar DataFrame a la sucursal validada
    df_suc = df[df["Sucursal"] == sucursal_sel].copy()

    if df_suc.empty:
        st.warning(
            "No se encontró información para la sucursal seleccionada "
            "después del filtrado."
        )
        return

    # 7. Cluster de la sucursal
    cluster_label = str(df_suc["Cluster_ML"].iloc[0])
    render_cluster_badge(cluster_label)

    # 8. KPIs específicos de la sucursal (reusamos compute_kpis)
    kpis_suc = compute_kpis(df_suc)
    render_kpi_cards(kpis_suc)

    # 9. Gráficas específicas para el empleado
    render_employee_risk_charts(df_suc)

    # 10. Recomendaciones según cluster
    render_branch_recommendations(cluster_label)

    # 11. 🆕 Chatbot (opcional, solo mostrar espacio para empleados)
    st.markdown("---")
    st.subheader("Chatbot Dimex")
    render_chatbot_tab(role="employee")  # puedes cambiar lógica de rol si quieres


