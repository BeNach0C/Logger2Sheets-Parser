import re
import os
import glob
import pandas as pd
from datetime import datetime

# ==============================================================================
# CONFIGURACIÓN DEL PROYECTO
# ==============================================================================

# Definición de las categorías de acción y las carpetas de log que les corresponden.
# La clave es el nombre base del archivo Excel, y el valor es una lista de carpetas
# que contienen los archivos .log a analizar para ese Excel.
CATEGORIAS = {
    "Bloques_puestos_y_rotos": ["Block Break", "Block Place"],
    "Fluidos": ["Bucket Empty", "Bucket Fill"],
    "Cofres_y_Mesas": ["Chest Interaction", "Enchanting", "Anvil", "Furnace", "Crafting"],
    "Letreros": ["Sign Change"],
}

# Nombre de la carpeta de salida para los archivos Excel
OUTPUT_FOLDER = "Filtered Sheet"
# Encabezados de las columnas para las hojas de Excel
COLUMNAS = ['Fecha', 'Hora', 'Dimensión', 'Coordenadas', 'Acción Completa']

# ==============================================================================
# FUNCIÓN DE EXTRACCIÓN Y PARSEO DE DATOS
# ==============================================================================

def parse_log_data(log_file_path):
    """
    Analiza un archivo de log y extrae la información relevante.

    Args:
        log_file_path (str): Ruta completa al archivo .log.

    Returns:
        list: Lista de diccionarios, donde cada diccionario es una fila de datos.
    """
    data = []
    # Expresión regular para capturar:
    # 1. Fecha (YYYY-MM-DD) y Hora (HH:MM:SS)
    # 2. Dimensión (entre corchetes, ej: [world], [%world%] o [Anark])
    # 3. Nombre del jugador (entre < >)
    # 4. El resto de la acción y coordenadas (capturadas de forma más flexible)
    log_pattern = re.compile(
        r'^\[(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2}:\d{2})\]\s+\[(.*?)\]\s+.*<\s*(\w+)\s*>\s+(.*)'
    )
    # Patrón más específico para coordenadas (X=123, Y=45, Z=-67)
    coord_pattern = re.compile(r'X=\s*(-?\d+),\s*Y=\s*(-?\d+),\s*Z=\s*(-?\d+)')


    try:
        with open(log_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                match = log_pattern.match(line.strip())

                if match:
                    log_date_raw, log_time_raw, dimension_raw, player_name, action_raw = match.groups()

                    # Limpiar la dimensión si tiene caracteres extraños (como %uuid% o %)
                    dimension = dimension_raw.strip('[]%').split('] ')[0].replace('%', '')

                    # 1. Fecha y Hora en formato requerido
                    # Formato deseado: DD/MM/YYYY y HH:MM:SS
                    try:
                        # Convertir y formatear la fecha
                        date_obj = datetime.strptime(log_date_raw, '%Y-%m-%d')
                        formatted_date = date_obj.strftime('%d/%m/%Y')
                        formatted_time = log_time_raw # La hora ya está en el formato HH:MM:SS
                    except ValueError:
                        print(f"Advertencia: No se pudo parsear la fecha/hora en la línea: {line.strip()}")
                        continue 

                    # 2. Extraer Coordenadas
                    coord_match = coord_pattern.search(action_raw)
                    coords = ""
                    if coord_match:
                        X, Y, Z = coord_match.groups()
                        coords = f"X={X}, Y={Y}, Z={Z}"

                    # 3. Guardar los datos
                    data.append({
                        'Fecha': formatted_date,
                        'Hora': formatted_time,
                        'Dimensión': dimension,
                        'Coordenadas': coords,
                        'Jugador': player_name,
                        'Acción Completa': action_raw.strip()
                    })

    except Exception as e:
        print(f"Error procesando el archivo {log_file_path}: {e}")

    return data

# ==============================================================================
# FUNCIÓN DE GENERACIÓN DE EXCEL
# ==============================================================================

def create_excel_report(action_name, log_data):
    """
    Genera un archivo Excel con múltiples hojas, una por jugador,
    utilizando solo el nombre de la acción para sobrescribir el archivo.

    Args:
        action_name (str): Nombre base de la acción para el archivo.
        log_data (list): Lista de todos los diccionarios de datos.
    """
    if not log_data:
        print(f"No hay datos para la acción '{action_name.replace('_', ' ')}'. Omitiendo la creación del archivo.")
        return

    # Convertir todos los datos a un DataFrame de pandas
    df_all = pd.DataFrame(log_data)
    
    # Asegurarse de que el DataFrame solo contenga las columnas requeridas (más la columna 'Jugador')
    columnas_df = ['Fecha', 'Hora', 'Dimensión', 'Coordenadas', 'Acción Completa', 'Jugador']
    df_all = df_all[columnas_df]

    # Modificación aquí: el nombre del archivo es solo el nombre de la acción.
    # Reemplazamos los guiones bajos por espacios para el nombre del archivo, 
    # y luego volvemos a poner guiones bajos para que el nombre de archivo sea seguro.
    safe_action_name = action_name.replace('_', ' ').replace(' ', '_')
    excel_filename = f"{safe_action_name}.xlsx"
    excel_path = os.path.join(OUTPUT_FOLDER, excel_filename)

    # El modo 'w' o la creación directa con pd.ExcelWriter sobrescribe archivos existentes.
    writer = pd.ExcelWriter(excel_path, engine='openpyxl')
    
    # Obtener la lista única de jugadores
    players = df_all['Jugador'].unique()
    
    # Crear una hoja para cada jugador
    for player in players:
        # Filtrar los datos para el jugador actual
        df_player = df_all[df_all['Jugador'] == player].copy()
        
        # Eliminar la columna 'Jugador' del contenido de la hoja
        df_player.drop(columns=['Jugador'], inplace=True)
        
        # Sanitizar el nombre del jugador para usarlo como nombre de la hoja (máx 31 chars)
        sheet_name = player.replace('[', '').replace(']', '').replace(':', '').replace('/', '').replace('\\', '').replace('?', '*').replace('*', ' ').replace('<', '').replace('>', '').replace(' ', '_').replace('.', '').replace(',', '')
        sheet_name = sheet_name[:31] 
        
        # Renombrar las columnas de la hoja de salida
        df_player.columns = COLUMNAS
        
        try:
            df_player.to_excel(writer, sheet_name=sheet_name, index=False)
        except Exception as e:
            print(f"Error escribiendo la hoja para el jugador '{player}' en el archivo '{excel_filename}': {e}")
            print(f"Intentando con un nombre de hoja genérico para '{player}'.")
            
            safe_sheet_name = f"Jugador_{len(df_all[df_all['Jugador'] == player])}_Regs"
            df_player.to_excel(writer, sheet_name=safe_sheet_name, index=False)

    try:
        writer.close()
        print(f"Éxito: Archivo de Excel creado/sobrescrito en: {excel_path}")
    except Exception as e:
        print(f"Error al guardar el archivo Excel en {excel_path}: {e}")

# ==============================================================================
# FUNCIÓN PRINCIPAL
# ==============================================================================

def main():
    """
    Función principal que orquesta la lectura de logs y la generación de reportes.
    """
    print("Iniciando el análisis de logs...")

    # 1. Crear la carpeta de salida si no existe
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
        print(f"Carpeta de salida creada: '{OUTPUT_FOLDER}'")
    else:
        print(f"Carpeta de salida encontrada: '{OUTPUT_FOLDER}'")


    # 2. Iterar sobre cada categoría y sus carpetas asociadas
    for action_name, folders in CATEGORIAS.items():
        all_logs_data = []
        print(f"\n--- Procesando acción: {action_name.replace('_', ' ')} ---")

        for folder in folders:
            # Construir el patrón de búsqueda: Carpeta/NombreDelArchivo.log
            search_pattern = os.path.join(os.getcwd(), folder, "*.log")
            
            # Usar glob para encontrar todos los archivos .log dentro de la carpeta
            log_files = glob.glob(search_pattern)

            if log_files:
                print(f"Encontrados {len(log_files)} archivos .log en la carpeta: '{folder}'")
                for log_file in log_files:
                    # Parsear los datos y añadirlos a la lista maestra
                    parsed_data = parse_log_data(log_file)
                    all_logs_data.extend(parsed_data)
            else:
                print(f"Advertencia: No se encontraron archivos .log en la carpeta: '{folder}'")

        # 3. Generar el reporte de Excel con los datos combinados (sobrescribe el anterior)
        create_excel_report(action_name, all_logs_data)
        
    print("\nAnálisis de logs finalizado.")

if __name__ == "__main__":
    main()