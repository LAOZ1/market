import unittest
from extractor_engine import ExtractorFacturasEngine

class TestExtractorFacturasEngine(unittest.TestCase):

    def test_deteccion_embalaje_cajas(self):
        desc = "HELADO SAVORY CHOCOLATE CJ X 24"
        es_emb, tipo, unidades = ExtractorFacturasEngine.detectar_embalaje(desc)
        self.assertTrue(es_emb)
        self.assertEqual(tipo, "caja")
        self.assertEqual(unidades, 24)

    def test_deteccion_embalaje_pack(self):
        desc = "COCA COLA ZERO 350ML PACK X 12"
        es_emb, tipo, unidades = ExtractorFacturasEngine.detectar_embalaje(desc)
        self.assertTrue(es_emb)
        self.assertEqual(tipo, "pack")
        self.assertEqual(unidades, 12)

    def test_producto_unitario_sin_embalaje(self):
        desc = "CHOCOLATE TREN 150G"
        es_emb, tipo, unidades = ExtractorFacturasEngine.detectar_embalaje(desc)
        self.assertFalse(es_emb)
        self.assertEqual(tipo, "unidad")
        self.assertEqual(unidades, 1)

    def test_desglose_costos_y_cantidades(self):
        # 3 cajas a $28.800 cada caja, vienen 24 por caja
        item = ExtractorFacturasEngine.procesar_item(
            descripcion="ACEITE VEGETAL 900ML CJ X 24",
            cantidad=3.0,
            precio_unitario=28800.0,
            codigo_proveedor="AC-900-24"
        )
        self.assertEqual(item.unidades_totales, 72)
        self.assertEqual(item.costo_unitario_base, 1200.0)

    def test_procesar_payload_completo(self):
        payload_simulado = {
            "proveedor_rut": "76.123.456-7",
            "proveedor_nombre": "DISTRIBUIDORA CENTRAL S.A.",
            "numero_factura": "98421",
            "fecha_emision": "2026-10-20",
            "monto_neto": 80000.0,
            "monto_iva": 15200.0,
            "monto_total": 95200.0,
            "items": [
                {
                    "codigo_proveedor": "PR-01",
                    "descripcion": "HELADOS PALETA FRUTAL CAJA X 30",
                    "cantidad": 2,
                    "precio_unitario": 15000.0,
                    "codigo_barra": "7801234567890"
                },
                {
                    "codigo_proveedor": "PR-02",
                    "descripcion": "BEBIDA LATA 350ML DISPLAY X 24",
                    "cantidad": 2,
                    "precio_unitario": 25000.0,
                    "codigo_barra": "7809876543210"
                }
            ]
        }
        factura = ExtractorFacturasEngine.procesar_payload_vision(payload_simulado)
        self.assertEqual(len(factura.items), 2)
        
        # Helados: 2 cajas de 30 = 60 unidades. $15.000 / 30 = $500 unitario
        self.assertEqual(factura.items[0].unidades_totales, 60)
        self.assertEqual(factura.items[0].costo_unitario_base, 500.0)
        self.assertEqual(factura.items[0].codigo_barra, "7801234567890")

        # Bebidas: 2 display de 24 = 48 unidades. $25.000 / 24 = $1041.6667
        self.assertEqual(factura.items[1].unidades_totales, 48)
        self.assertEqual(factura.items[1].costo_unitario_base, 1041.6667)

if __name__ == '__main__':
    unittest.main()
