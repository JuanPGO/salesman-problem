# TSP - Traveling Salesman Problem

Proyecto de implementación y comparación de diferentes algoritmos para resolver el Problema del Vendedor Viajero (TSP).

**Presentado por:** Juan Camilo García y Juan Pablo Gómez

## 📁 Nueva Estructura del Proyecto

```
salesman-problem/
├── data/                           # Archivos de instancias TSP
│   ├── wi29.tsp
│   ├── dj38.tsp
│   ├── qa194.tsp
│   ├── uy734.tsp
│   └── ...
├── graficas/                       # Gráficas generadas por los algoritmos
├── shared/                         # Archivos transversales (compartidos)
│   ├── __init__.py
│   ├── leerInformacion.py         # Lectura de archivos TSP
│   ├── matrizDistancias.py        # Cálculo de distancias
│   ├── heuristicas.py             # Heurísticas constructivas
│   ├── codificacionVecindarios.py # Vecindarios (2-opt, etc.)
│   ├── busquedaLocal.py           # Búsqueda local
│   ├── perturbacion.py            # Operadores de perturbación
│   ├── leerTour.py                # Lectura de tours
│   └── cargaCalculoProfe.py       # Utilidades adicionales
├── ils/                           # Algoritmo ILS
│   ├── main_ils.py               # Ejecutable principal ILS
│   └── ils.py                    # Implementación ILS
├── genetico/                      # Algoritmo Genético
│   ├── main_genetico.py          # Ejecutable principal AG
│   └── geneticos.py              # Implementación AG Chu-Beasley
├── ortools/                       # Algoritmo OR-Tools
│   ├── main_ortools.py           # Ejecutable principal OR-Tools
│   └── tsp_ortools.py            # Implementación OR-Tools
├── main.py                        # ARCHIVO ORIGINAL (obsoleto)
├── esqueletoConcurrencia.py       # Esqueleto para concurrencia
├── README.md                      # README original
├── README_nueva_estructura.md     # Este archivo
└── LICENSE
```

## 🚀 Cómo Usar los Algoritmos

### Requisitos Previos

Asegúrate de tener instalados los paquetes necesarios:

```bash
pip install matplotlib numpy networkx ortools
```

### 1. Algoritmo ILS (Iterated Local Search)

```bash
# Navegar a la carpeta ILS
cd ils

# Ejecutar con un archivo TSP específico
python main_ils.py ../data/wi29.tsp

# Ver ayuda
python main_ils.py --help
```

**Características:**

- Implementa búsqueda local iterada
- Utiliza heurísticas constructivas (VCN, IMC)
- Aplica perturbación 3-opt
- Genera gráficas de convergencia y comparativas

### 2. Algoritmo Genético (Chu-Beasley)

```bash
# Navegar a la carpeta genetico
cd genetico

# Ejecutar con un archivo TSP específico
python main_genetico.py ../data/wi29.tsp

# Ver ayuda
python main_genetico.py --help
```

**Características:**

- Implementación del algoritmo genético Chu-Beasley
- Compara con heurísticas constructivas
- Muestra evolución de la población
- Genera gráficas de convergencia y comparativas

### 3. Algoritmo OR-Tools

```bash
# Navegar a la carpeta ortools
cd ortools

# Ejecutar con un archivo TSP específico
python main_ortools.py ../data/wi29.tsp

# Ver ayuda
python main_ortools.py --help
```

**Características:**

- Utiliza diferentes metaheurísticas de Google OR-Tools
- Compara múltiples estrategias de búsqueda
- Genera ranking de metaheurísticas
- Optimización de alto rendimiento

## 📊 Generación de Gráficas

Cada algoritmo puede generar gráficas automáticamente:

- **ILS:** Convergencia, comparativas de calidad y tiempos
- **Genético:** Evolución generacional, comparativas con heurísticas
- **OR-Tools:** Ranking de metaheurísticas, tiempos de ejecución

Las gráficas se guardan en la carpeta `graficas/` en el directorio raíz.

## 🔧 Archivos Transversales

La carpeta `shared/` contiene todos los módulos compartidos:

- **leerInformacion.py:** Parseo de archivos TSP
- **matrizDistancias.py:** Cálculo de matrices de distancia
- **heuristicas.py:** Heurísticas constructivas (VCN, IMC, Savings, Christofides)
- **busquedaLocal.py:** Implementaciones de búsqueda local
- **codificacionVecindarios.py:** Operadores de vecindario (2-opt)
- **perturbacion.py:** Operadores de perturbación

## 📝 Ejemplos de Uso

### Ejemplo 1: Ejecutar ILS con wi29.tsp

```bash
cd ils
python main_ils.py ../data/wi29.tsp
```

### Ejemplo 2: Ejecutar Algoritmo Genético con dj38.tsp

```bash
cd genetico
python main_genetico.py ../data/dj38.tsp
```

### Ejemplo 3: Ejecutar OR-Tools con qa194.tsp

```bash
cd ortools
python main_ortools.py ../data/qa194.tsp
```

## 🏗️ Ventajas de la Nueva Estructura

1. **Modularidad:** Cada algoritmo es independiente
2. **Mantenibilidad:** Fácil modificación y mejora de algoritmos individuales
3. **Escalabilidad:** Fácil adición de nuevos algoritmos
4. **Claridad:** Separación clara de responsabilidades
5. **Reutilización:** Archivos compartidos en `shared/`

## 📋 Migración desde la Estructura Anterior

Si venías usando el `main.py` original:

**Antes:**

```bash
python main.py data/wi29.tsp
# Luego seleccionar opción 1, 2 o 3 del menú
```

**Ahora:**

```bash
# Para ILS (opción 1)
cd ils && python main_ils.py ../data/wi29.tsp

# Para Genético (opción 2)
cd genetico && python main_genetico.py ../data/wi29.tsp

# Para OR-Tools (opción 3)
cd ortools && python main_ortools.py ../data/wi29.tsp
```

## 🚦 Estado del Proyecto

- ✅ Fragmentación completada
- ✅ Archivos transversales organizados
- ✅ Mains individuales funcionales
- ✅ Documentación actualizada
- ✅ Compatibilidad con estructura anterior mantenida

---

Para cualquier duda o problema con la nueva estructura, revisa este README o contacta a los desarrolladores.
