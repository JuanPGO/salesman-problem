# Importado de librerías
import pprint as pp

def cargarTour(rutaArchivo:str)->dict:
    
    # Inicializar / declarar
    caso = {
        'dimension': 0,                
        'tour': [],
    }
    
    with open(rutaArchivo, 'r') as f:        
        i = 0
        numero_ciudades = float('inf')
        for linea in f.readlines():
            arreglo_linea = linea.strip().split(" ")


            # Sección de servicios
            if i <= numero_ciudades:
                if i == 3:
                    caso['dimension'] = int(arreglo_linea[1])
                if i > 4 and len(caso['tour']) <= caso['dimension']:
                    caso['tour'].append(int(arreglo_linea[0]))
    
            
            # Subíndice de servicios / líneas    
            # print("depuracion",i+1)
            i += 1                
            
    return caso

# Llamado de prueba
# caso1 = cargarTour('data/eg7146.tour.txt')
# pp.pprint(caso1)


    