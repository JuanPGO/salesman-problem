# Problema del Vendedor Viajero (TSP)

Este proyecto implementa diferentes algoritmos para resolver el Problema del Vendedor Viajero (TSP), utilizando estrategias constructivas, de búsqueda local y metaheurísticas.

## Descripción del Problema

El TSP consiste en encontrar la ruta más corta que recorre todas las ciudades de un conjunto dado exactamente una vez, regresando a la ciudad de origen. Es un problema NP-difícil clásico en optimización combinatoria.

## Componentes Implementados

### 1. Codificación

- Representación del tour mediante lista de índices de ciudades
- Cálculo de distancias en formato EUC2D (distancia euclidiana 2D)

### 2. Heurísticas Constructivas

- **Vecino Más Cercano**: Construye el tour seleccionando iterativamente la ciudad no visitada más cercana
- **Inserción Más Cercana**: Construye el tour insertando ciudades en la posición que genere el menor incremento de distancia

### 3. Vecindarios

- **Swap2**: Intercambia dos ciudades cualesquiera del tour
- **Insert Izquierda**: Mueve una ciudad a una posición a la izquierda en el tour
- **Insert Derecha**: Mueve una ciudad a una posición a la derecha en el tour
- **2-opt**: Invierte un segmento del tour para eliminar cruces

### 4. Búsqueda Local

- **Mejor Mejora**: Evalúa todos los vecinos y selecciona el mejor
- **Primera Mejora**: Selecciona el primer vecino que mejore la solución actual

### 5. Perturbación

- **Double Bridge**: Divide el tour en 4 segmentos y los reorganiza
- **Multi Swap**: Realiza múltiples intercambios aleatorios
- **Sección Inversa**: Invierte una sección aleatoria del tour
- **Perturbación Múltiple**: Combina diferentes tipos de perturbaciones

### 6. Metaheurística ILS

- **Iterated Local Search**: Integra búsqueda local (explotación) y perturbación (exploración)
- Diferentes criterios de aceptación y configuraciones

## Estructura del Proyecto

```
├── busquedaLocal.py     # Implementación de algoritmos de búsqueda local
├── codificacionVecindarios.py   # Definición de operadores de vecindario
├── data/                # Instancias de problemas en formato TSP
├── esqueletoConcurrencia.py     # Esqueleto para implementación concurrente
├── heuristicas.py       # Implementación de heurísticas constructivas
├── ils.py               # Implementación del algoritmo ILS
├── leerInformacion.py   # Funciones para cargar instancias TSP
├── leerTour.py          # Funciones para cargar tours de referencia
├── main.py              # Script principal para ejecutar y comparar algoritmos
├── matrizDistancias.py  # Implementación de cálculo de distancias
├── perturbacion.py      # Mecanismos de perturbación
└── README.md            # Este archivo
```

## Ejecución

Para ejecutar el programa principal y comparar todos los algoritmos:

```bash
python main.py
```

Este script permite:

1. Seleccionar una instancia TSP
2. Ejecutar y comparar todos los algoritmos implementados
3. Visualizar y analizar resultados
4. Opcionalmente, generar gráficas comparativas

## Algoritmos Disponibles

### Heurísticas Constructivas

```python
# Vecino más cercano
resultado_vcn = heuristicaVecinoMasCercano(caso, matriz)

# Inserción más cercana
resultado_imc = heuristicaInsercionMasCercana(caso, matriz)
```

### Búsqueda Local

```python
# Búsqueda local con mejor mejora
resultado_bl = busqueda_local_mejor_mejora(tour_inicial, matriz, vecindarios)

# Búsqueda local con primera mejora
resultado_bl = busqueda_local_primera_mejora(tour_inicial, matriz, vecindarios)
```

### ILS

```python
# Algoritmo ILS básico
resultado_ils = ils_algorithm(caso, matriz, heuristica, busqueda_local, perturbacion)

# Análisis completo de ILS con múltiples configuraciones
mejor_resultado = ejecutar_ils_completo(caso, matriz)
```

## Características Adicionales

- **Comparativa de Rendimiento**: Análisis y comparación de diferentes algoritmos
- **Visualización**: Generación de gráficas para analizar calidad, tiempo y convergencia
- **Flexibilidad**: Fácil integración de nuevos operadores y estrategias

## Extensiones Posibles

- Implementación de otras metaheurísticas (Simulated Annealing, GRASP, VNS)
- Paralelización de algoritmos
- Hibridación de métodos
- Adaptación para variantes del TSP (TSP con ventanas de tiempo, múltiples vendedores, etc.)

---

## Descripción de los Módulos Principales

### codificacionVecindarios.py

Contiene la implementación de diferentes operadores de vecindario que generan soluciones cercanas a una dada, esenciales para los algoritmos de búsqueda local:

- swap2: Intercambia dos ciudades del tour
- insert_izquierda/derecha: Mueve una ciudad a otra posición
- two_opt: Operador de inversión para eliminar cruces

### busquedaLocal.py

Implementa algoritmos de búsqueda local para encontrar óptimos locales a partir de una solución inicial:

- busqueda_local_mejor_mejora: Explora todo el vecindario y selecciona la mejor solución
- busqueda_local_primera_mejora: Acepta la primera solución que mejore la actual

### perturbacion.py

Contiene mecanismos para realizar modificaciones más severas a las soluciones, permitiendo escapar de óptimos locales:

- perturbacion_double_bridge: Operación de cortar y reconectar 4 segmentos
- Múltiples estrategias de perturbación con diferentes grados de intensidad

### ils.py

Implementa el algoritmo Iterated Local Search, que alterna entre fases de intensificación (búsqueda local) y diversificación (perturbación):

- ils_algorithm: Implementación configurable del algoritmo
- ejecutar_ils_completo: Función para analizar múltiples configuraciones
