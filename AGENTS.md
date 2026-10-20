# Protocolo de Orquestación y Reglas de Desarrollo — Market POS & Gestión de Inventario

Este documento rige la arquitectura, el flujo de trabajo de los agentes de IA y las directrices técnicas del proyecto **Market POS**. Todos los agentes y subagentes que participen en este espacio de trabajo deben adherirse estrictamente a estas reglas.

---

## 1. Visión y Dominio del Negocio

El sistema reemplaza una aplicación POS gratuita y no auditable por un ecosistema propio, relacional e inmutable para el control de inventario, punto de venta y resguardo de la caja chica.

### Principios de Negocio Obligatorios:
1. **Inmutabilidad y Auditoría**:
   - Cero borrado físico (`DELETE`) en productos, precios, movimientos o ventas. Uso exclusivo de *soft-deletes* (`is_active`).
   - Todo cambio de costo/precio genera un registro histórico (`price_history`).
   - Toda transacción se asocia de forma estricta a un `usuario_id` y a un `turno_id`.
2. **Conversión de Embalajes y Costo Real**:
   - El sistema debe procesar automáticamente bultos/cajas mayoristas a unidades base (con control estricto de decimales/redondeos).
3. **Protección de Margen y Alertas**:
   - Si una factura trae una variación de costo (alza o promoción/descuento de proveedor), el sistema debe alertar para sugerir o ajustar el precio de venta al público y evitar descalces o apropiaciones de margen.
4. **Cierre de Turno Ciego**:
   - El arqueo de caja chica al final del turno se realiza a ciegas: el trabajador declara el efectivo físico sin conocer el total calculado por el sistema, emitiendo de inmediato el reporte de descuadre.
5. **Recepción Omnicanal vía WhatsApp Bot**:
   - La captura de facturas se realiza prioritariamente desde el móvil mediante un **Bot de WhatsApp** (chat directo o grupo de recepción), vinculado por tenant/empresa (número de teléfono o ID de grupo).

---

## 2. Roles y Agentes Especializados (Orquestación)

Para garantizar calidad de código, robustez y separación de responsabilidades, el desarrollo y mantenimiento se dividirá entre los siguientes roles:

| Agente / Rol | Enfoque Principal | Habilidades y Responsabilidades |
| :--- | :--- | :--- |
| **`WhatsApp Receptionist Agent`** | Canal de Entrada Móvil & Webhook | - Recepción de fotos y PDFs desde WhatsApp (directo o grupo).<br>- Identificación de la empresa/sucursal por número de origen o grupo.<br>- Respuesta automatizada con confirmación y desglose preliminar al chat. |
| **`Core Business Engine Agent`** | Reglas de Negocio, Visión y Desglose | - Extracción multimodal (Visión/OCR) de facturas.<br>- Conversión de cajas/embalajes a unidades base individuales.<br>- Motor de detección de variaciones de costo y márgenes.<br>- Cálculo de puntos de reorden. |
| **`Architect & Data Agent`** | Arquitectura y Persistencia Multi-Tenant | - Esquema relacional con soporte multi-empresa/sucursal.<br>- Tablas append-only, transacciones ACID y logs de auditoría.<br>- Sincronización entre el Bot de WhatsApp y el motor transaccional. |
| **`POS & Shift Operations Agent`** | Operación Diaria y Punto de Venta | - Interfaz y API del Punto de Venta (rápido, lectura de códigos de barra).<br>- Apertura, control y cierre ciego de turno.<br>- Conciliación de caja chica en tiempo real. |
| **`Analytics & Reporting Agent`** | Inteligencia y Reportabilidad | - Reporte de arqueos, faltantes de stock y rotación ABC.<br>- Matriz de fluctuación de costos de proveedores. |
| **`QA & Integrity Agent`** | Pruebas y Validación Adversaria | - Pruebas de estrés, decimales y consistencia transaccional.<br>- Control de calidad independiente (`QA_APPROVED` / `REJECTED`). |

---

## 3. Protocolo de Comunicación Inter-Agente y Bus de Mensajes (`AGENT_BUS.md`)

1. **Unidireccionalidad de Validación**: Todo entregable debe registrarse en `AGENT_BUS.md` como `PENDING_REVIEW` para el `QA & Integrity Agent`.
2. **Veredicto Exclusivo de QA**: Solo QA puede emitir `QA_APPROVED` tras probar escenarios adversos.
3. **Persistencia Cronológica**: Todo cambio de estado y resultado de auditoría se documenta en el bus.

---

## 4. Catálogo de Habilidades Requeridas (`.agents/skills/`)

1. **`skill-extractor-facturas`**: Extracción multimodal de datos desde fotos de facturas recibidas por WhatsApp o web.
2. **`skill-conversion-embalaje`**: Conversión matemática de cajas/bultos a unidades base y costo unitario exacto.
3. **`skill-alertas-margen`**: Comparación de costos en factura vs. catálogo para protección de margen.
4. **`skill-auditoria-arqueo-ciego`**: Protocolo de cierre ciego de turno y control de caja chica.
5. **`skill-reorden-sugerido`**: Cálculo de inventario mínimo y pedidos planificados.
