def procesarGPS(proyecto, gpsFilename, geoZonesFilename, modo, velMin):
    ## Paquetes
    import pandas as pd
    import geopandas as gpd
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    import numpy as np
    from datetime import datetime
    ## Preparación de archivos
    
    gpsFilenameP = proyecto +"/"+gpsFilename
    geoZonesFilenameP = proyecto +"/"+geoZonesFilename

    ## Abrir GPS y zonas
    gpsPoints = gpd.read_file(gpsFilenameP, layer = 'track_points')
    geoZones = gpd.read_file(geoZonesFilenameP)
    print(geoZones)
    ## Proyectar puntos de GPS en planas (aptas para Colombia en general)
    
    crs = "EPSG:3116"
    gpsPoints = gpsPoints.to_crs(crs)
    
    ## Seleccionar columnas relevantes

    gpsPoints = gpsPoints[['track_fid','track_seg_point_id','ele','time','geometry']]
    
    #### Etapa A: Identificar bordes y direccion de los recorridos
    
    ## Filtrar polígonos de borde 
    
    borders = geoZones[geoZones['Tipo']== 'Borde']
    
    ## 2. Spatial Join de bordes con puntos GPS

    gpsPoints = gpd.sjoin(gpsPoints, borders, how = "left", op='intersects')
    gpsPoints = gpsPoints.drop(columns=['index_right'])
    
    ## 3. Listado de tracks del GPS

    tracks = gpsPoints.track_fid.unique()
    
    ## 4. Base de datos colectora de bordes
    
    collectorDB = pd.DataFrame({'track_fid': pd.Series([],dtype = 'int'),
                           'rec_orige': pd.Series([],dtype = 'int'),
                           'Sentido': pd.Series([],dtype = 'str'),
                           'rec_destino': pd.Series([],dtype = 'int')})
    
    ## 5. Iterar cada track
    
    for track in tracks:

        ## Filtrar puntos del track seleccionado
        
        track_segment = gpsPoints[gpsPoints['track_fid']== track]
        tracktext = 'base'+track.astype(str)
    
        ### Eliminar puntos intermedios, (fuera de los polígonos de los bordes)
        
        trackBorderPoints = track_segment[track_segment[['Nombre']].notnull().all(1)]
        print("Check trackBorderPoints")
        print(trackBorderPoints)
    
        ### Cuando el nombre no sea igual entre celdas, se marca como cambio de dirección
    
        trackBorderPoints['track_seg_point_id_destino'] = trackBorderPoints.track_seg_point_id.shift(-1)
        trackBorderPoints['Nombre_destino'] = trackBorderPoints.Nombre.shift(-1)
        
        trackBorderPoints = trackBorderPoints[trackBorderPoints['Nombre'] != trackBorderPoints['Nombre_destino']]
        trackBorderPoints['Sentido'] = 'De '+ trackBorderPoints['Nombre'] + ' a ' +  trackBorderPoints['Nombre_destino']
        trackBorderPoints = trackBorderPoints[trackBorderPoints['Nombre_destino'].notnull()]
        
        ## Juntar el procesamiento de cambio de sentido de todos los tracks
        
        collectorDB = collectorDB.append(trackBorderPoints[['track_fid','track_seg_point_id','Sentido','track_seg_point_id_destino']])
        #print(trackBorderPoints[['track_fid','track_seg_point_id','Sentido','track_seg_point_id_destino']])
    
    ### Etapa B: Filtrar basado en los puntos de cambio de sentido
    
    ## Filtrar zonas que representan los segmentos
    
    segmentos = geoZones[geoZones ['Tipo']=='Segmento']
    segmentos
    
    minSpeed = velMin
    #minSpeed = 3
    #modo = "Auto"

    ## Procesar timestamp, convertir a un valor en segundos basados en el mes
 
    #gpsPoints['time']=gpsPoints['time'].astype('string')
    #gpsPoints['ano']= gpsPoints['time'].str.slice(0,4,1).astype(float)
    #gpsPoints['mes']= gpsPoints['time'].str.slice(5,7,1).astype(float)
    #gpsPoints['dia']= gpsPoints['time'].str.slice(8,10,1).astype(float)
    #gpsPoints['hora']= gpsPoints['time'].str.slice(11,13,1).astype(float)
    #gpsPoints['minuto']= gpsPoints['time'].str.slice(14,16,1).astype(float)
    #gpsPoints['segundo']= gpsPoints['time'].str.slice(17,19,1).astype(float)
    ## Actualizar cálculo del timestamp en segundos
    gpsPoints['time']=pd.to_datetime(gpsPoints['time'], infer_datetime_format=True)    
    
    #gpsPoints['tiempos_segundos'] = gpsPoints['time'].datetime.values.astype(np.int64) // 10 ** 9
    #gpsPoints['tiempo_segundos'] = pd.Timestamp(gpsPoints['time'], unit = 's')
    gpsPoints['tiempo_segundos'] = gpsPoints[['time']].apply(lambda x: x[0].timestamp(), axis=1).astype(int)
    #print(gpsPoints['tiempo_segundos'])
    ## Calcular en segundos, código puede fallar si se toman datos entre cambio de mes a medianoche

    #gpsPoints['tiempo_segundos'] = gpsPoints['dia']*(24*3600)+gpsPoints['hora']*3600+gpsPoints['minuto']*60+gpsPoints['segundo']
    #print(gpsPoints['tiempo_segundos'])

    ## Crear base para compilar los recorridos

## Revisar este bloque, para seleccionar puntos

    CompilaRecorridos = pd.DataFrame({'track_fid': pd.Series([], dtype = 'int'),
                                  'track_seg_point_id': pd.Series([], dtype = 'int'),
                                  'time': pd.Series([], dtype = 'str'),
                                  'ano': pd.Series([], dtype = 'int'),
                                  'mes': pd.Series([], dtype = 'int'),
                                  'dia': pd.Series([], dtype = 'int'),
                                  'hora': pd.Series([], dtype = 'int'),
                                  'minuto': pd.Series([], dtype = 'int'),
                                  'segundo': pd.Series([], dtype = 'int'),
#                                  'tiempo_seg': pd.Series([], dtype = 'int'),
#                                  'tiempo_seg_previo' : pd.Series([], dtype ='int'),
                                  'Sentido': pd.Series([], dtype = 'str'),
                                  'Segmento': pd.Series([], dtype = 'str'),
#                                  'Desde': pd.Series([], dtype = 'str'),
#                                  'Hasta': pd.Series([], dtype = 'str'),
#                                  'Distancia_metros': pd.Series([], dtype = 'float'),
#                                  'Velocidad_Km_h': pd.Series([], dtype = 'float'),
#                                  'Track_no':pd.Series([], dtype = 'int'),
                                  'Modo':pd.Series([], dtype = 'str'),
    })


    ## Procesar para cada track los recorridos
    viaje = 1
    for row in collectorDB.iterrows():
    
        Track = row[1][0]
        Sentido = row[1][2]
        reg_inicio =row[1][4]
        reg_fin = row[1][5]
        #print(row)
        #print(Track)
        #print(Sentido)
        #print(reg_inicio)
        #print(reg_fin)
    
        trip = gpsPoints[(gpsPoints['track_seg_point_id']>=reg_inicio) & (gpsPoints['track_seg_point_id']<=reg_fin) &(gpsPoints['track_fid']== Track)]
        trip['Sentido'] = Sentido
    
        tripTagged = gpd.sjoin(trip, segmentos, how = 'left', op ='intersects' )
                
        
        # Cálculo de tiempo en cada timestep (el tiempo del timestep i es calculado con el registro anterior)
        tripTagged['Xi'] = tripTagged.geometry.x
        tripTagged['Yi'] = tripTagged.geometry.y
        tripTagged['Xi_1'] = tripTagged.Xi.shift()
        tripTagged['Yi_1'] = tripTagged.Yi.shift()
        tripTagged['Time_s'] = tripTagged['tiempo_segundos']-tripTagged.tiempo_segundos.shift()
        tripTagged['Time_s_prev'] = tripTagged.tiempo_segundos.shift()
        tripTagged['Dist_m'] = np.sqrt(pow((tripTagged['Xi']-tripTagged['Xi_1']),2)+pow((tripTagged['Yi']-tripTagged['Yi_1']),2))
        tripTagged['Vel_Km_h'] = (tripTagged['Dist_m']/tripTagged['Time_s'])*3.6
        ## Filter based on a min speed valule
        tripTagged['No_Recorrido'] = viaje
        tripTagged['Modo'] = modo
        tripTagged = tripTagged[tripTagged['Vel_Km_h'] >= minSpeed]
        #fileName = 'Viaje_'+str(viaje)+'.csv'
        #tripTagged.to_csv(fileName)
    
        tripShort = tripTagged[['track_fid','track_seg_point_id','time','tiempo_segundos','Time_s_prev','Sentido','Nombre_right','Desde_right','Hasta_right','Dist_m','Vel_Km_h','No_Recorrido','Modo','Time_s']]
    
        CompilaRecorridos = CompilaRecorridos.append(tripShort)
        #print(trip)
        viaje = viaje+1
        #print(row['track_seg_point_id'])

    #print(CompilaRecorridos)
    
    archivo1 = proyecto +"/"+ "01_Resultado_"+gpsFilename+"_base_cruda.csv"
    print("El archivo 1 se guarda como ")
    print(archivo1)
    CompilaRecorridos.to_csv(archivo1)
    
    # Parte 2, cálculo de velocidades, tiempos y organizar resultados
    
    base = CompilaRecorridos
    
    base['Vel_x_tiem'] = base['Vel_Km_h']*base['Time_s']
    result = base.groupby(['No_Recorrido','Sentido','Desde_right','Hasta_right']).agg({'Dist_m':['sum'],
                                                                                   'Time_s_prev':['min'],
                                                                                   'tiempo_segundos': ['min','max'],
                                                                                   'Vel_x_tiem':['sum'],
                                                                                   'Time_s':['sum']})
    result = result.reset_index()
    result.columns=['Recorrido','Sentido','Desde','Hasta','Distancia','Tiempo_prev_min','Tiempo_min','Tiempo_max','VelT','Ttot']
    result['VelPonderada'] = result['VelT']/result['Ttot']
    result['Tiempo_en_tramo'] = (result['Tiempo_max']-result['Tiempo_min'])/3600
    result['Velocidad'] = (result['Distancia']/1000)/result['Tiempo_en_tramo']
    #result
    archivo2 = proyecto +"/"+ "02_Resultado_"+gpsFilename+"_velocidad_calculada.csv"
    
    result.to_csv(archivo2)

    ## Corrección de los tiempos de distancias

    ## Pivot table para simular formato de entrega

    tabla = pd.pivot_table(result, values = 'Tiempo_en_tramo', index = ['Desde','Hasta'], columns = ['Sentido','Recorrido'])
    archivo3 = proyecto +"/"+"03_Resultado"+gpsFilename+"formato_reporte.csv"
    tabla.to_csv(archivo3)
    
    #tabla
    print("Finalizado correctamente")

procesarGPS("T9_Noviembre","G9_Sergio_Oct9_AT_AC100_entre_KR48_y_KR7_LCL_BCL.gpx", "G9_No1_proyectado.shp", "Livianos Calzada lenta",1)
