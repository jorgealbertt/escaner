# scripts/convert_excel.py
import pandas as pd
import json
import os

def clean_code(val):
    if pd.isna(val): return ""
    val_str = str(val).strip()
    if 'E+' in val_str or 'e+' in val_str:
        try:
            return str(int(float(val_str.replace(',', '.'))))
        except:
            pass
    if val_str.endswith('.0'):
        val_str = val_str[:-2]
    return val_str

def clean_price(val):
    if pd.isna(val): return "0"
    try:
        num = float(val)
        return f"{num:.2f}".rstrip('0').rstrip('.') if num % 1 != 0 else f"{int(num)}"
    except:
        return str(val).strip()

def main():
    # Busca cualquier archivo .xls o .xlsx en la raíz
    excel_file = None
    for file in os.listdir('.'):
        if file.endswith(('.xlsx', '.xls', '.csv')) and 'listado' in file.lower():
            excel_file = file
            break
            
    if not excel_file:
        print("No se encontró ningún archivo de listado Excel.")
        return

    print(f"Procesando: {excel_file}")
    if excel_file.endswith('.csv'):
        df = pd.read_csv(excel_file)
    else:
        df = pd.read_excel(excel_file)
        
    df.columns = [c.lower().strip() for c in df.columns]
    
    # Identificar columnas dinámicamente
    col_codigo = 'código' if 'código' in df.columns else ('cod.' if 'cod.' in df.columns else 'codigo')
    col_nombre = 'nombre'
    col_depto = 'departamento'
    col_existencia = 'existencia'
    col_mayor = 'mayor'
    col_detal = 'detal'

    inventory_data = []
    for _, row in df.iterrows():
        codigo = clean_code(row.get(col_codigo, ''))
        if not codigo: continue
        
        existencia = str(row.get(col_existencia, '0'))
        if existencia.endswith('.0'): existencia = existencia[:-2]
        
        item = {
            "codigo": codigo,
            "departamento": str(row.get(col_depto, '')).strip(),
            "nombre": str(row.get(col_nombre, '')).strip(),
            "mayor": clean_price(row.get(col_mayor, 0)),
            "detal": clean_price(row.get(col_detal, 0)),
            "existencia": existencia
        }
        inventory_data.append(item)

    js_content = f"const inventoryData = {json.dumps(inventory_data, ensure_ascii=False)};"
    
    with open('data_precios_v2.js', 'w', encoding='utf-8') as f:
        f.write(js_content)
        
    print(f"¡Éxito! Generado data_precios_v2.js con {len(inventory_data)} productos.")

if __name__ == "__main__":
    main()
