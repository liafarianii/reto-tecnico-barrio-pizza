# 🍕 Barrio Pizza — Control Inteligente de Órdenes de Compra

Herramienta de auditoría automática desarrollada en Python y Streamlit para evaluar y optimizar las órdenes de compra semanales en las sucursales de Barrio Pizza.

## 🚀 Funcionalidades Principales
* **Auditoría Automática de Pedidos:** Compara la demanda proyectada de cada sucursal contra la orden realizada.
* **Detección de Alertas:** Identifica omisiones críticas, riesgo de quiebre de stock y sobre-pedidos.
* **Consolidación por Proveedor:** Agrupa automáticamente la orden corregida por distribuidor (Bella Italia, Molinos Central, etc.).

## 💡 Supuestos de Negocio
1. **Proyección de Demanda:** Se calcula utilizando el promedio del consumo histórico de las últimas 6 semanas.
2. **Necesidad Real:** `Necesidad = Proyección - Inventario Actual`.
3. **Redondeo:** Las compras se hacen en empaques cerrados, aplicando redondeo hacia arriba (`ceil`).
4. **Tolerancia:** Se marca sobre-pedido cuando compran 2 o más empaques por encima de lo necesario.

## 🔄 Integración Futura con Odoo
1. **Conexión API:** Conectar la app vía XML-RPC con Odoo para leer inventario en tiempo real.
2. **Órdenes Automáticas:** Generar borradores de Órdenes de Compra (`purchase.order`) en Odoo con un clic.

## 🤖 Uso de IA
Se utilizó IA para acelerar el desarrollo del código en Python, estructurar las reglas de redondeo y diseñar la interfaz en Streamlit.
