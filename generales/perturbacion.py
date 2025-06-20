"""
Implementación de mecanismos de perturbación para el problema TSP.
Estas funciones permiten escapar de óptimos locales en la búsqueda.
"""

import random

def perturbacion_double_bridge(tour: list) -> list:
    """
    Implementación de la perturbación "double-bridge" o "4-opt move".
    Esta perturbación corta el tour en 4 segmentos y los reordena.
    
    Args:
        tour: Lista de índices que representa el tour actual
        
    Returns:
        Una nueva solución obtenida tras aplicar la perturbación
    """
    n = len(tour)
    if n < 8:  # Necesitamos al menos 8 ciudades para hacer 4 cortes significativos
        return tour.copy()
    
    # Obtener 4 puntos de corte aleatorios (ordenados)
    puntos_corte = sorted(random.sample(range(1, n), 3))
    i, j, k = puntos_corte
    
    # Crear el nuevo tour reorganizando los 4 segmentos
    # A-B-C-D -> A-D-C-B (donde A,B,C,D son segmentos)
    nuevo_tour = tour[:i] + tour[k:] + tour[j:k] + tour[i:j]
    
    return nuevo_tour

def perturbacion_multi_swap(tour: list, num_swaps: int = 3) -> list:
    """
    Realiza múltiples intercambios aleatorios en el tour.
    
    Args:
        tour: Lista de índices que representa el tour actual
        num_swaps: Número de intercambios a realizar
        
    Returns:
        Una nueva solución obtenida tras aplicar la perturbación
    """
    nuevo_tour = tour.copy()
    n = len(nuevo_tour)
    
    for _ in range(num_swaps):
        # Seleccionar dos posiciones aleatorias diferentes
        i, j = random.sample(range(n), 2)
        
        # Intercambiar las ciudades en esas posiciones
        nuevo_tour[i], nuevo_tour[j] = nuevo_tour[j], nuevo_tour[i]
    
    return nuevo_tour

def perturbacion_3opt(tour: list, max_intentos: int = 5) -> list:
    """
    Implementación eficiente de la perturbación 3-opt.
    Elimina 3 aristas del tour y las reconecta de una manera diferente.
    
    Args:
        tour: Lista de índices que representa el tour actual
        max_intentos: Número máximo de intentos para encontrar una perturbación válida
        
    Returns:
        Una nueva solución obtenida tras aplicar la perturbación
    """
    n = len(tour)
    if n < 6:  # Necesitamos al menos 6 ciudades para hacer perturbación 3-opt
        return tour.copy()
    
    # Copia del tour original
    mejor_tour = tour.copy()
    
    # Realizar varios intentos para encontrar una buena perturbación
    for _ in range(max_intentos):
        # Seleccionar 3 posiciones aleatorias distintas (ordenadas)
        i, j, k = sorted(random.sample(range(n), 3))
        
        # Asegurar que no sean posiciones adyacentes
        if (j == i + 1 or j == (i - 1) % n) and (k == j + 1 or k == (j - 1) % n):
            continue
        
        # Crear el nuevo tour aplicando 3-opt
        # Hay varias formas de reconectar un tour después de eliminar 3 aristas
        # Elegimos una al azar para mayor diversificación
        tipo_reconexion = random.randint(0, 3)
        
        if tipo_reconexion == 0:
            # Opción 1: A-B-C-D-E-F -> A-C-B-E-D-F
            nuevo_tour = tour[:i+1] + tour[j:i:-1] + tour[k:j:-1] + tour[k+1:]
        elif tipo_reconexion == 1:
            # Opción 2: A-B-C-D-E-F -> A-D-C-B-E-F
            nuevo_tour = tour[:i+1] + tour[j+1:k+1] + tour[i+1:j+1][::-1] + tour[k+1:]
        elif tipo_reconexion == 2:
            # Opción 3: A-B-C-D-E-F -> A-E-D-C-B-F
            nuevo_tour = tour[:i+1] + tour[k:j:-1] + tour[i+1:j+1][::-1] + tour[k+1:]
        else:
            # Opción 4: A-B-C-D-E-F -> A-D-E-B-C-F
            nuevo_tour = tour[:i+1] + tour[j+1:k+1] + tour[i+1:j+1] + tour[k+1:]
        
        # Si el tour es válido, lo guardamos
        if len(nuevo_tour) == n:
            return nuevo_tour
    
    # Si no se encontró una perturbación válida, mantener el tour original
    return mejor_tour

def perturbacion_parcial(tour: list, porcentaje: float = 0.6) -> list:
    """
    Perturba solo un porcentaje de las ciudades del tour, dejando el resto fijo.
    
    Args:
        tour: Lista de índices que representa el tour actual
        porcentaje: Porcentaje de ciudades a perturbar (entre 0 y 1)
        
    Returns:
        Una nueva solución obtenida tras aplicar la perturbación
    """
    n = len(tour)
    nuevo_tour = tour.copy()
    
    # Determinar número de ciudades a perturbar
    num_ciudades = int(n * porcentaje)
    
    # Seleccionar posiciones a perturbar
    posiciones_perturbacion = random.sample(range(n), num_ciudades)
    
    # Aplicar perturbación (utilizando swap aleatorio)
    for _ in range(num_ciudades // 2):
        i, j = random.sample(posiciones_perturbacion, 2)
        nuevo_tour[i], nuevo_tour[j] = nuevo_tour[j], nuevo_tour[i]
    
    return nuevo_tour
