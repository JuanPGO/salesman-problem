# presentado por Juan Camilo Garcia y Juan Pablo Gómez

"""
Script principal para ejecutar TSP con OR-Tools (diferentes metaheurísticas).
"""

import time
import os
import sys
import matplotlib.pyplot as plt
from typing import Dict

# Agregar la carpeta padre al path para importar desde shared
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar módulos compartidos
from shared.leerInformacion import cargarCaso
from tsp_ortools import ejecutar_tsp_ortools

def validar_archivo_tsp(ruta_archivo: str) -> bool:
    """
    Valida que el archivo TSP existe y es accesible.
    
    Args:
        ruta_archivo: Ruta al archivo TSP
        
    Returns:
        bool: True si el archivo es válido, False caso contrario
    """
    # Verificar si el archivo existe
    if not os.path.exists(ruta_archivo):
        print(f"Error: El archivo '{ruta_archivo}' no existe.")
        return False
    
    # Verificar si es un archivo (no un directorio)
    if not os.path.isfile(ruta_archivo):
        print(f"Error: '{ruta_archivo}' no es un archivo válido.")
        return False
    
    # Verificar si tiene extensión .tsp
    if not ruta_archivo.lower().endswith('.tsp'):
        print(f"Advertencia: El archivo '{ruta_archivo}' no tiene extensión .tsp")
        respuesta = input("¿Desea continuar de todas formas? [s/N]: ")
        if respuesta.lower() != 's':
            return False
    
    # Verificar si se puede leer el archivo
    try:
        with open(ruta_archivo, 'r') as f:
            f.read(1)  # Intentar leer al menos un carácter
    except Exception as e:
        print(f"Error: No se puede leer el archivo '{ruta_archivo}'. {e}")
        return False
    
    return True

def mostrar_ayuda():
    """
    Muestra la información de ayuda sobre cómo usar el programa OR-Tools.
    """
    print("=== AYUDA DEL TSP CON OR-TOOLS ===")
    print("\nUso:")
    print("  python main_ortools.py <ruta_archivo>     - Ejecuta OR-Tools con el archivo especificado")
    print("  python main_ortools.py --help            - Muestra esta ayuda")
    print("\nEjemplos:")
    print("  python main_ortools.py ../data/wi29.tsp")
    print("  python main_ortools.py \"C:\\ruta\\archivo\\tsp\\wi29.tsp\"")
    print("\nNota: Es OBLIGATORIO especificar la ruta del archivo TSP como argumento.")

def ejecutar_algoritmo_ortools(archivo_instancia: str) -> Dict:
    """
    Ejecuta el algoritmo TSP usando OR-Tools con diferentes metaheurísticas.
    
    Args:
        archivo_instancia: Ruta al archivo de la instancia TSP
        
    Returns:
        Diccionario con los resultados
    """
    # Obtener el nombre de la instancia del nombre de archivo
    nombre_instancia = os.path.basename(archivo_instancia).split('.')[0]
    
    print(f"\n=== TSP CON OR-TOOLS ===")
    print(f"Instancia: {nombre_instancia}")
    print("="*50)
    
    # Ejecutar directamente TSP con OR-Tools
    resultado = ejecutar_tsp_ortools(archivo_instancia)
    
    # Preguntar si se desean generar gráficas
    if resultado and resultado.get('exito', False):
        generar_graficas = input("\n¿Desea generar gráficas comparativas con otros algoritmos? [s/N]: ")
        if generar_graficas.lower() == 's':
            print("\nGenerando comparativa con otros algoritmos...")
            generar_comparativa_ortools_vs_otros(archivo_instancia, resultado, nombre_instancia)
    
    return resultado

def generar_comparativa_ortools_vs_otros(archivo_instancia: str, resultado_ortools: Dict, nombre_instancia: str):
    """
    Genera una comparativa entre las diferentes metaheurísticas de OR-Tools.
    
    Args:
        archivo_instancia: Ruta al archivo de la instancia TSP
        resultado_ortools: Resultado del algoritmo OR-Tools con todos los resultados
        nombre_instancia: Nombre de la instancia para los títulos
    """
    try:
        print("Generando gráficas comparativas de metaheurísticas OR-Tools...")
        
        # Obtener todos los resultados de las metaheurísticas
        todos_resultados = resultado_ortools.get('todos_resultados', {})
        
        if not todos_resultados:
            print("No se encontraron resultados de metaheurísticas para generar gráficas.")
            return
        
        # Filtrar solo resultados exitosos
        resultados_exitosos = {k: v for k, v in todos_resultados.items() if v.get('exito', False)}
        
        if not resultados_exitosos:
            print("No hay resultados exitosos para generar gráficas.")
            return
        
        # Crear gráficas
        graficas_dir = os.path.join('..', 'graficas')
        if not os.path.exists(graficas_dir):
            os.makedirs(graficas_dir)
        
        # Preparar datos para las gráficas
        metaheuristicas = list(resultados_exitosos.keys())
        distancias = [resultados_exitosos[meta]['distancia'] for meta in metaheuristicas]
        tiempos = [resultados_exitosos[meta]['tiempo'] for meta in metaheuristicas]
        
        # Gráfica de calidad (distancias)
        plt.figure(figsize=(12, 8))
        colores = ['lightblue', 'lightgreen', 'orange', 'lightcoral', 'gold', 'lightpink']
        
        plt.barh(metaheuristicas, distancias, color=colores[:len(metaheuristicas)])
        plt.xlabel('Distancia (menor es mejor)')
        plt.title(f'Comparativa de Metaheurísticas OR-Tools - Calidad - {nombre_instancia}')
        plt.grid(axis='x', linestyle='--', alpha=0.7)
        
        # Anotar valores
        for i, v in enumerate(distancias):
            plt.text(v + max(distancias)*0.01, i, str(v), va='center', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(os.path.join(graficas_dir, f'{nombre_instancia}_ortools_comparativa.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
        # Gráfica de tiempos
        plt.figure(figsize=(12, 8))
        colores_tiempo = ['salmon', 'lightcoral', 'gold', 'lightsteelblue', 'lightseagreen', 'plum']
        
        plt.barh(metaheuristicas, tiempos, color=colores_tiempo[:len(metaheuristicas)])
        plt.xlabel('Tiempo (segundos)')
        plt.title(f'Comparativa de Metaheurísticas OR-Tools - Tiempos - {nombre_instancia}')
        plt.grid(axis='x', linestyle='--', alpha=0.7)
        
        # Anotar valores
        for i, v in enumerate(tiempos):
            plt.text(v + max(tiempos)*0.05, i, f"{v:.4f}s", va='center', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(os.path.join(graficas_dir, f'{nombre_instancia}_ortools_tiempos.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
        # Gráfica combinada (ranking de calidad vs tiempo)
        plt.figure(figsize=(14, 10))
        
        # Crear subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
        
        # Ordenar por calidad (distancia)
        datos_ordenados = sorted(resultados_exitosos.items(), key=lambda x: x[1]['distancia'])
        metas_ord, datos_ord = zip(*datos_ordenados)
        distancias_ord = [d['distancia'] for _, d in datos_ordenados]
        tiempos_ord = [d['tiempo'] for _, d in datos_ordenados]
        
        # Subplot 1: Ranking por calidad
        ax1.barh(range(len(metas_ord)), distancias_ord, color=colores[:len(metas_ord)])
        ax1.set_yticks(range(len(metas_ord)))
        ax1.set_yticklabels(metas_ord)
        ax1.set_xlabel('Distancia (menor es mejor)')
        ax1.set_title(f'Ranking por Calidad - {nombre_instancia}')
        ax1.grid(axis='x', linestyle='--', alpha=0.7)
        
        # Anotar valores en subplot 1
        for i, v in enumerate(distancias_ord):
            ax1.text(v + max(distancias_ord)*0.01, i, str(v), va='center', fontweight='bold')
        
        # Subplot 2: Tiempos correspondientes
        ax2.barh(range(len(metas_ord)), tiempos_ord, color=colores_tiempo[:len(metas_ord)])
        ax2.set_yticks(range(len(metas_ord)))
        ax2.set_yticklabels(metas_ord)
        ax2.set_xlabel('Tiempo (segundos)')
        ax2.set_title(f'Tiempos de Ejecución - {nombre_instancia}')
        ax2.grid(axis='x', linestyle='--', alpha=0.7)
        
        # Anotar valores en subplot 2
        for i, v in enumerate(tiempos_ord):
            ax2.text(v + max(tiempos_ord)*0.05, i, f"{v:.4f}s", va='center', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(os.path.join(graficas_dir, f'{nombre_instancia}_ortools_ranking.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Gráficas comparativas guardadas en directorio '../graficas/':")
        print(f"  - {nombre_instancia}_ortools_comparativa.png (Comparativa de calidad)")
        print(f"  - {nombre_instancia}_ortools_tiempos.png (Comparativa de tiempos)")
        print(f"  - {nombre_instancia}_ortools_ranking.png (Ranking combinado)")
        
        # Mostrar resumen
        print(f"\n{'='*70}")
        print(f"RESUMEN COMPARATIVO METAHEURÍSTICAS OR-TOOLS - {nombre_instancia}")
        print(f"{'='*70}")
        print(f"{'Rank':<4} {'Metaheurística':<20} {'Distancia':<12} {'Tiempo':<10}")
        print("-" * 50)
        
        for i, (meta, datos) in enumerate(datos_ordenados, 1):
            print(f"{i:<4} {meta:<20} {datos['distancia']:<12} {datos['tiempo']:<10.4f}")
        
    except Exception as e:
        print(f"Error generando comparativa: {e}")

if __name__ == "__main__":
    print("=== TSP CON OR-TOOLS ===")
    
    # Verificar si se pasaron argumentos de línea de comandos
    if len(sys.argv) > 1:
        # Si el primer argumento es --help, mostrar ayuda
        if sys.argv[1] in ["--help", "-h", "help"]:
            mostrar_ayuda()
        else:
            # Validar y usar el archivo especificado
            archivo_especificado = sys.argv[1]
            if validar_archivo_tsp(archivo_especificado):
                ejecutar_algoritmo_ortools(archivo_especificado)
            else:
                print("\nError: No se pudo cargar el archivo especificado.")
                print("Use 'python main_ortools.py --help' para ver la ayuda.")
    else:
        # No se especificó archivo, mostrar error y ayuda
        print("Error: Debe especificar la ruta del archivo TSP como argumento.")
        print("\nUso: python main_ortools.py <ruta_archivo>")
        print("Ejemplo: python main_ortools.py ../data/wi29.tsp")
        print("\nPara más información, use: python main_ortools.py --help") 