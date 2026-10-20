import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

@dataclass
class ItemFactura:
    codigo_proveedor: Optional[str]
    descripcion: str
    es_embalaje: bool
    tipo_empaque: str  # caja, pack, bulto, unidad
    unidades_por_empaque: int
    cantidad_empaques: float
    precio_empaque: float
    unidades_totales: int
    costo_unitario_base: float
    codigo_barra: Optional[str] = None

@dataclass
class FacturaExtraida:
    proveedor_rut: str
    proveedor_nombre: str
    numero_factura: str
    fecha_emision: str
    items: List[ItemFactura]
    monto_neto: float
    monto_iva: float
    monto_total: float

class ExtractorFacturasEngine:
    """
    Motor extractor y parseador de facturas físicas/digitales.
    Permite procesar texto extraído por OCR / Modelos de Visión
    y convertirlo en entidades estructuradas con cálculo de embalaje.
    """

    PATRONES_EMBALAJE = [
        (r'caja\s*x?\s*(\d+)', 'caja'),
        (r'cj\s*x?\s*(\d+)', 'caja'),
        (r'pack\s*x?\s*(\d+)', 'pack'),
        (r'pk\s*x?\s*(\d+)', 'pack'),
        (r'bulto\s*x?\s*(\d+)', 'bulto'),
        (r'display\s*x?\s*(\d+)', 'display'),
        (r'(\d+)\s*unid', 'caja'),
        (r'(\d+)\s*u\b', 'caja'),
    ]

    @classmethod
    def detectar_embalaje(cls, descripcion: str) -> tuple[bool, str, int]:
        """
        Analiza la descripción del ítem en busca de patrones de empaque mayorista.
        Ej: 'HELLMANNS MAYO 120G CJ X 24' -> (True, 'caja', 24)
        """
        desc_lower = descripcion.lower()
        for patron, tipo in cls.PATRONES_EMBALAJE:
            match = re.search(patron, desc_lower)
            if match:
                try:
                    unidades = int(match.group(1))
                    if unidades > 1:
                        return True, tipo, unidades
                except (ValueError, IndexError):
                    pass
        return False, 'unidad', 1

    @classmethod
    def calcular_desglose(
        cls,
        cantidad_empaques: float,
        precio_empaque: float,
        unidades_por_empaque: int
    ) -> tuple[int, float]:
        """
        Calcula las unidades reales totales y el costo unitario base con precisión.
        """
        if unidades_por_empaque <= 0:
            unidades_por_empaque = 1
        
        unidades_totales = int(cantidad_empaques * unidades_por_empaque)
        costo_unitario = round(precio_empaque / unidades_por_empaque, 4)
        return unidades_totales, costo_unitario

    @classmethod
    def procesar_item(
        cls,
        descripcion: str,
        cantidad: float,
        precio_unitario: float,
        codigo_proveedor: Optional[str] = None,
        unidades_override: Optional[int] = None,
        codigo_barra: Optional[str] = None
    ) -> ItemFactura:
        """
        Procesa una línea de la factura y genera la descomposición matemática exacta.
        """
        if unidades_override and unidades_override > 1:
            es_embalaje = True
            tipo_empaque = 'caja'
            unidades_por_pack = unidades_override
        else:
            es_embalaje, tipo_empaque, unidades_por_pack = cls.detectar_embalaje(descripcion)

        totales, costo_base = cls.calcular_desglose(
            cantidad_empaques=cantidad,
            precio_empaque=precio_unitario,
            unidades_por_empaque=unidades_por_pack
        )

        return ItemFactura(
            codigo_proveedor=codigo_proveedor,
            descripcion=descripcion.strip().upper(),
            es_embalaje=es_embalaje,
            tipo_empaque=tipo_empaque,
            unidades_por_empaque=unidades_por_pack,
            cantidad_empaques=cantidad,
            precio_empaque=precio_unitario,
            unidades_totales=totales,
            costo_unitario_base=costo_base,
            codigo_barra=codigo_barra
        )

    @classmethod
    def procesar_payload_vision(cls, payload: Dict[str, Any]) -> FacturaExtraida:
        """
        Transforma el resultado devuelto por un modelo de visión/OCR a formato validado.
        """
        items_procesados: List[ItemFactura] = []
        for raw_item in payload.get('items', []):
            item = cls.procesar_item(
                descripcion=raw_item.get('descripcion', ''),
                cantidad=float(raw_item.get('cantidad', 1)),
                precio_unitario=float(raw_item.get('precio_unitario', 0.0)),
                codigo_proveedor=raw_item.get('codigo_proveedor'),
                unidades_override=raw_item.get('unidades_por_empaque'),
                codigo_barra=raw_item.get('codigo_barra')
            )
            items_procesados.append(item)

        return FacturaExtraida(
            proveedor_rut=payload.get('proveedor_rut', 'S/R'),
            proveedor_nombre=payload.get('proveedor_nombre', 'PROVEEDOR DESCONOCIDO'),
            numero_factura=str(payload.get('numero_factura', '0')),
            fecha_emision=payload.get('fecha_emision', ''),
            items=items_procesados,
            monto_neto=float(payload.get('monto_neto', 0.0)),
            monto_iva=float(payload.get('monto_iva', 0.0)),
            monto_total=float(payload.get('monto_total', 0.0))
        )
