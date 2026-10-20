# Bus de Comunicación y Registro de Pasamanos (AGENT_BUS)

Este archivo actúa como el bus de mensajes, control de estados y canal de entrega formal entre los agentes especializados del proyecto **Market POS**.

---

## 1. Estado Actual del Sistema

| Parámetro | Valor |
| :--- | :--- |
| **Fase Activa** | Fase 2: Arquitectura del WhatsApp Receptionist Bot & Multi-Tenant |
| **Turno Activo (Agente)** | `WhatsApp Receptionist Agent` / `Architect & Data Agent` |
| **Estado de la Entrega** | `IN_PROGRESS` |
| **Siguiente Agente en Cola** | `QA & Integrity Agent` |

---

## 2. Registro de Mensajes y Pasamanos (Handoff Log)

### [2026-10-20] Entrada #001 a #007 — (Resumen de Fases Previas Aprobadas)
- Extracción de facturas y conversión de embalajes formalizada y probada (`QA_APPROVED`).
- Mapeo de códigos de barra EAN-13 para facturas de CCU completado y aprobado (`QA_APPROVED`).

---

### [2026-10-20] Entrada #008 — Especificación y Adición del Agente Recepcionista de WhatsApp
- **De**: `System Orchestrator`
- **Para**: Todos los agentes
- **Estado**: `INITIALIZED`
- **Mensaje**: El canal primario de captura de facturas pasa a ser un **Bot de WhatsApp**. El bot operará tanto en chats directos como en grupos de recepción, asociando el origen al tenant/empresa correspondiente (multi-empresa) mediante número de teléfono o ID de grupo.
- **Acción Siguiente**: Detallar los costos operativos de WhatsApp para Chile y diseñar el Webhook receptor de medios.
