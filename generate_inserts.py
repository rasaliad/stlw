#!/usr/bin/env python3
"""
Script para generar INSERTs SQL desde JSON de pedidos SAP
Lee pedido.json y genera pedido.sql con los INSERTs para STL_DISPATCHES y STL_DISPATCH_LINES
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List

def parse_iso_date_to_firebird(iso_date_str: str) -> str:
    """Convierte fecha ISO 8601 a formato Firebird DATE (solo fecha sin hora)"""
    if not iso_date_str:
        return "NULL"
    
    try:
        # Tomar solo los primeros 10 caracteres: 'YYYY-MM-DD'
        date_only = iso_date_str[:10]
        return f"'{date_only}'"
    except:
        return "NULL"

def escape_sql_string(value: str) -> str:
    """Escapa comillas simples en strings SQL"""
    if value is None:
        return "NULL"
    return f"'{str(value).replace(chr(39), chr(39)+chr(39))}'"

def generate_dispatch_insert(data: Dict[str, Any]) -> str:
    """Genera INSERT para tabla STL_DISPATCHES"""
    
    # Usar parse_iso_date_to_firebird para todas las fechas
    fecha_creacion = parse_iso_date_to_firebird(data.get('fechaCreacion'))
    fecha_picking = parse_iso_date_to_firebird(data.get('fechaPicking'))
    fecha_carga = parse_iso_date_to_firebird(data.get('fechaCarga')) if data.get('fechaCarga') else "NULL"
    
    sql = f"""INSERT INTO STL_DISPATCHES (
    NUMERO_DESPACHO,
    NUMERO_BUSQUEDA,
    FECHA_CREACION,
    FECHA_PICKING,
    FECHA_CARGA,
    CODIGO_CLIENTE,
    NOMBRE_CLIENTE,
    TIPO_DESPACHO,
    SYNC_STATUS,
    LAST_SYNC_AT
) VALUES (
    {data.get('numeroDespacho')},
    {data.get('numeroBusqueda')},
    {fecha_creacion},
    {fecha_picking},
    {fecha_carga},
    {escape_sql_string(data.get('codigoCliente'))},
    {escape_sql_string(data.get('nombreCliente'))},
    {data.get('tipoDespacho')},
    'SYNCED',
    CURRENT_TIMESTAMP
);"""

    return sql

def generate_dispatch_lines_inserts(data: Dict[str, Any]) -> List[str]:
    """Genera INSERTs para tabla STL_DISPATCH_LINES"""
    
    lines = data.get('lines', [])
    inserts = []
    
    numero_despacho = data.get('numeroDespacho')
    tipo_despacho = data.get('tipoDespacho')
    
    for line in lines:
        sql = f"""INSERT INTO STL_DISPATCH_LINES (
    DISPATCH_ID,
    CODIGO_PRODUCTO,
    NOMBRE_PRODUCTO,
    ALMACEN,
    CANTIDAD_UMB,
    LINE_NUM,
    UOM_CODE,
    UOM_ENTRY
) VALUES (
    (SELECT ID FROM STL_DISPATCHES WHERE NUMERO_DESPACHO = {numero_despacho} AND TIPO_DESPACHO = {tipo_despacho}),
    {escape_sql_string(line.get('codigoProducto'))},
    {escape_sql_string(line.get('nombreProducto'))},
    {escape_sql_string(line.get('almacen'))},
    {line.get('cantidadUMB', 0)},
    {line.get('lineNum', 0)},
    {escape_sql_string(line.get('uoMCode'))},
    {line.get('uoMEntry', 0)}
);"""
        inserts.append(sql)
    
    return inserts

def main():
    """Función principal"""
    input_file = 'pedido.json'
    output_file = 'pedido.sql'
    
    # Verificar que existe el archivo de entrada
    if not os.path.exists(input_file):
        print(f"❌ Error: No se encontró el archivo '{input_file}'")
        print(f"Crea un archivo '{input_file}' con el JSON del pedido de SAP")
        return
    
    try:
        # Leer archivo JSON
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"📖 Leyendo archivo '{input_file}'...")
        print(f"📝 Pedido: {data.get('numeroDespacho')} - Tipo: {data.get('tipoDespacho')}")
        
        # Generar SQLs
        dispatch_insert = generate_dispatch_insert(data)
        lines_inserts = generate_dispatch_lines_inserts(data)
        
        # Escribir archivo SQL
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("-- Archivo generado automáticamente desde pedido.json\n")
            f.write(f"-- Pedido: {data.get('numeroDespacho')} - Tipo: {data.get('tipoDespacho')}\n")
            f.write(f"-- Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("-- INSERT para STL_DISPATCHES\n")
            f.write(dispatch_insert)
            f.write("\n\n")
            
            f.write("-- INSERTs para STL_DISPATCH_LINES\n")
            for i, line_insert in enumerate(lines_inserts, 1):
                f.write(f"-- Línea {i}\n")
                f.write(line_insert)
                f.write("\n\n")
            
            f.write("-- FIN\n")
        
        print(f"✅ Archivo '{output_file}' generado exitosamente!")
        print(f"📊 Generados: 1 INSERT cabecera + {len(lines_inserts)} INSERTs líneas")
        print(f"🔍 Cliente: {data.get('nombreCliente')}")
        print(f"📦 Total líneas: {len(data.get('lines', []))}")
        
    except json.JSONDecodeError as e:
        print(f"❌ Error: El archivo '{input_file}' no es un JSON válido")
        print(f"Detalle: {e}")
    except Exception as e:
        print(f"❌ Error procesando archivo: {e}")

if __name__ == "__main__":
    main()