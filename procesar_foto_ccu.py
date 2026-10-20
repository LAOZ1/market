import json
from extractor_engine import ExtractorFacturasEngine

# Datos extraídos directamente de la imagen "63662 (1).jpg" (Comercial CCU S.A.)
# Se detectan dos Facturas Electrónicas independientes: N° 177409636 y N° 177409637

factura_1_raw = {
    "proveedor_rut": "99.554.560-8",
    "proveedor_nombre": "COMERCIAL CCU S.A.",
    "numero_factura": "177409636",
    "fecha_emision": "2026-04-29",
    "monto_neto": 57736.0,
    "monto_iva": 10970.0,
    "monto_iaba_10": 4250.0,
    "monto_total": 72956.0,
    "items": [
        {
            "codigo_proveedor": "1284",
            "descripcion": "CRUSH ZERO PET2000X6-TR",
            "cantidad": 1.0,
            "precio_unitario": 5313.0, # Valor neto post descuento (con flete prorrateado o neto directo)
            "unidades_por_empaque": 6
        },
        {
            "codigo_proveedor": "1621",
            "descripcion": "7UP ZERO PET2000X6-TR",
            "cantidad": 1.0,
            "precio_unitario": 5313.0,
            "unidades_por_empaque": 6
        },
        {
            "codigo_proveedor": "870375",
            "descripcion": "BILI ZERO PET2000CCX6-TR",
            "cantidad": 1.0,
            "precio_unitario": 5313.0,
            "unidades_por_empaque": 6
        },
        {
            "codigo_proveedor": "870376",
            "descripcion": "PAP ZERO PET2000CCX6-TR",
            "cantidad": 1.0,
            "precio_unitario": 5313.0,
            "unidades_por_empaque": 6
        },
        {
            "codigo_proveedor": "870690",
            "descripcion": "PEPSI ZERO PET2000X6-TR",
            "cantidad": 1.0,
            "precio_unitario": 5313.0,
            "unidades_por_empaque": 6
        },
        {
            "codigo_proveedor": "870831",
            "descripcion": "LIMON SODA ZERO PET2000X6-TR",
            "cantidad": 1.0,
            "precio_unitario": 5313.0,
            "unidades_por_empaque": 6
        },
        {
            "codigo_proveedor": "870852",
            "descripcion": "GINGER ALE ZERO PET2000X6-TR",
            "cantidad": 1.0,
            "precio_unitario": 5313.0,
            "unidades_por_empaque": 6
        },
        {
            "codigo_proveedor": "870855",
            "descripcion": "KEM ZERO PET2000CCX6-TR",
            "cantidad": 1.0,
            "precio_unitario": 5313.0,
            "unidades_por_empaque": 6
        }
    ]
}

factura_2_raw = {
    "proveedor_rut": "99.554.560-8",
    "proveedor_nombre": "COMERCIAL CCU S.A.",
    "numero_factura": "177409637",
    "fecha_emision": "2026-04-29",
    "monto_neto": 65482.0,
    "monto_iva": 12442.0,
    "monto_iaba_10": 2853.0,
    "monto_iaba_18": 3224.0,
    "monto_total": 84001.0,
    "items": [
        {
            "codigo_proveedor": "1325",
            "descripcion": "PEPSI PET2000X6-TR",
            "cantidad": 4.0,
            "precio_unitario": 4477.75, # $17.911 / 4 cajas
            "unidades_por_empaque": 6
        },
        {
            "codigo_proveedor": "870690",
            "descripcion": "PEPSI ZERO PET2000X6-TR",
            "cantidad": 6.0,
            "precio_unitario": 4755.17, # $28.531 / 6 cajas
            "unidades_por_empaque": 6
        }
    ]
}

def procesar_lote_facturas():
    resultados = []
    for raw in [factura_1_raw, factura_2_raw]:
        factura = ExtractorFacturasEngine.procesar_payload_vision(raw)
        data = {
            "proveedor_rut": factura.proveedor_rut,
            "proveedor_nombre": factura.proveedor_nombre,
            "numero_factura": factura.numero_factura,
            "fecha_emision": factura.fecha_emision,
            "monto_total": factura.monto_total,
            "items": []
        }
        for item in factura.items:
            data["items"].append({
                "codigo_ccu": item.codigo_proveedor,
                "descripcion": item.descripcion,
                "embalaje": f"{item.tipo_empaque.upper()} X {item.unidades_por_empaque}",
                "cajas_recibidas": item.cantidad_empaques,
                "unidades_base_ingresadas": item.unidades_totales,
                "precio_caja": item.precio_empaque,
                "costo_unitario_botella": item.costo_unitario_base
            })
        resultados.append(data)
    
    with open("facturas_procesadas_63662.json", "w", encoding="utf-8") as f:
        json.dump(resultados, f, indent=2, ensure_ascii=False)
    print("PROCESAMIENTO_EXITOSO: 2 facturas procesadas.")

if __name__ == "__main__":
    procesar_lote_facturas()
