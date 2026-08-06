import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Barrio Pizza - Control de Compras", layout="wide")

st.title(" Barrio Pizza — Control Inteligente de Órdenes de Compra")
st.markdown("Herramienta de auditoría automática de pedidos e inventario para sucursales.")

# 1. Cargar Datos
@st.cache_data
def load_data():
    df_ing = pd.read_csv('ingredientes.csv')
    df_cons = pd.read_csv('consumo_historico.csv')
    df_inv = pd.read_csv('inventario_actual.csv')
    df_ord = pd.read_csv('orden_compra_semana.csv')
    return df_ing, df_cons, df_inv, df_ord

df_ing, df_cons, df_inv, df_ord = load_data()

# 2. Procesamiento de Proyección y Alertas
df_proj = df_cons.groupby(['sucursal', 'ingrediente_id'])['consumo_unidad_base'].mean().reset_index()
df_proj.rename(columns={'consumo_unidad_base': 'consumo_proyectado'}, inplace=True)

df_merged = pd.merge(df_proj, df_ing, on='ingrediente_id', how='left')
df_merged = pd.merge(df_merged, df_inv, on=['sucursal', 'ingrediente_id'], how='left')
df_merged['stock_actual_unidad_base'] = df_merged['stock_actual_unidad_base'].fillna(0)

# Necesidad real en unidades base
df_merged['necesidad_base'] = np.maximum(0, df_merged['consumo_proyectado'] - df_merged['stock_actual_unidad_base'])

# Conversión a formatos enteros
df_merged['formatos_sugeridos'] = np.ceil(df_merged['necesidad_base'] / df_merged['unidad_base_por_formato'])

# Unión con Orden de Compra
df_final = pd.merge(df_merged, df_ord, on=['sucursal', 'ingrediente_id'], how='left')
df_final['cantidad_formatos'] = df_final['cantidad_formatos'].fillna(0)

# Clasificación de Alertas
def clasificar_orden(row):
    ped = row['cantidad_formatos']
    sug = row['formatos_sugeridos']
    ing = row['nombre']
    
    if sug > 0 and ped == 0:
        return 'CRÍTICO: Olvido / Faltante', f"⚠️ Se omitió {ing}. Necesidad proyectada: {sug:.0f} {row['formato_compra']}(s)."
    elif ped < sug:
        dif = sug - ped
        return 'ALERTA: Pedido Insuficiente', f"🔻 {ing}: Se pidieron {ped:.0f} y se necesitan {sug:.0f} {row['formato_compra']}(s) (Faltan {dif:.0f}). Riesgo de quiebre."
    elif ped > sug + 1:
        dif = ped - sug
        return 'ADVERTENCIA: Sobre-pedido', f"🔺 {ing}: Se pidieron {ped:.0f} cuando la necesidad es {sug:.0f} {row['formato_compra']}(s) (Exceso de {dif:.0f})."
    else:
        return 'OK: Correcto', "✅ Orden alineada con necesidad real y redondeo."

df_final[['estado_alerta', 'mensaje_alerta']] = df_final.apply(clasificar_orden, axis=1, result_type='expand')

# 3. Métricas Principales (KPIs)
col1, col2, col3, col4 = st.columns(4)
col1.metric("Sucursales Evaluadas", df_final['sucursal'].nunique())
col2.metric("Alertas Críticas / Faltantes", len(df_final[df_final['estado_alerta'].str.contains('CRÍTICO|ALERTA')]))
col3.metric("Sobre-pedidos", len(df_final[df_final['estado_alerta'].str.contains('ADVERTENCIA')]))
col4.metric("Órdenes Correctas", len(df_final[df_final['estado_alerta'].str.contains('OK')]))

# 4. Filtros
st.sidebar.header("Filtros")
sucursal_sel = st.sidebar.selectbox("Seleccionar Sucursal", ["Todas"] + list(df_final['sucursal'].unique()))

if sucursal_sel != "Todas":
    df_view = df_final[df_final['sucursal'] == sucursal_sel]
else:
    df_view = df_final

# 5. Visualización de Alertas
st.subheader("Alertas de Compra Detectadas")
df_alertas = df_view[df_view['estado_alerta'] != 'OK: Correcto']

if len(df_alertas) == 0:
    st.success("No hay alertas detectadas para esta selección.")
else:
    for idx, row in df_alertas.iterrows():
        if "CRÍTICO" in row['estado_alerta'] or "ALERTA" in row['estado_alerta']:
            st.error(f"**[{row['sucursal']}]** {row['mensaje_alerta']}")
        else:
            st.warning(f"**[{row['sucursal']}]** {row['mensaje_alerta']}")

# 6. Gráfico Comparativo
st.subheader("Comparativo: Cantidad Pedida vs. Cantidad Sugerida (Formatos)")
fig = px.bar(
    df_view, 
    x='nombre', 
    y=['cantidad_formatos', 'formatos_sugeridos'],
    barmode='group',
    title=f"Evaluación de Pedidos - {sucursal_sel}",
    labels={'value': 'Formatos', 'variable': 'Leyenda', 'nombre': 'Ingrediente'}
)
st.plotly_chart(fig, use_container_width=True)

# 7. Pedido Sugerido Consolidado por Proveedor
st.subheader("📦 Orden de Compra Corregida por Proveedor")
df_proveedor = df_view.groupby(['proveedor', 'nombre', 'formato_compra'])['formatos_sugeridos'].sum().reset_index()
df_proveedor = df_proveedor[df_proveedor['formatos_sugeridos'] > 0]
st.dataframe(df_proveedor, use_container_width=True)