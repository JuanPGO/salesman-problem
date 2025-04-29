# Importado de librerías
import pprint as pp

def cargarCaso(rutaArchivo:str)->dict:
    
    # Inicializar / declarar
    caso = {
        'pais': "",
        'dimension': 0,                
        'coordenadas': [],
    }
    
    with open(rutaArchivo, 'r') as f:        
        i = 0
        numero_ciudades = float('inf')
        for linea in f.readlines():
            arreglo_linea = linea.strip().split(" ")


            # Sección de servicios
            if i <= numero_ciudades:
                if i == 1:
                    caso['pais'] = arreglo_linea[5:]
                elif i == 4:
                    caso['dimension'] = int(arreglo_linea[2])
                elif i > 6 and len(caso['coordenadas']) < caso['dimension']:
                    caso['coordenadas'].append({
                            'latitud': float(arreglo_linea[1]),
                            'longitud':float(arreglo_linea[2])
                            })
            
            # Subíndice de servicios / líneas    
            # print("depuracion",i+1)
            i += 1                
            
    return caso

# # Llamado de prueba
caso1 = cargarCaso('data/wi29.tsp')
pp.pprint(caso1)


    