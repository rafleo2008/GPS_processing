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
    gpsPointsR = gpd.read_file(gpsFilenameP, layer = 'track_points')
    geoZonesR = gpd.read_file(geoZonesFilenameP)
    ## Proyectar puntos de GPS en planas (aptas para Colombia en general)
    
    crs = "EPSG:3116"
    gpsPoints = gpsPointsR.to_crs(crs)
    geoZones = geoZonesR.to_crs(crs)
    
    ## Seleccionar columnas relevantes

    gpsPoints = gpsPoints[['track_fid','track_seg_point_id','ele','time','geometry']]
    
    #### Etapa A: Identificar bordes y direccion de los recorridos
    
    ## Filtrar polígonos de borde 
    
    borders = geoZones[geoZones['Tipo']== 'Borde']
    #borders.to_csv('bordes.csv')
    ## 2. Spatial Join de bordes con puntos GPS

    gpsPoints = gpd.sjoin(gpsPoints, borders, how = "left", op='intersects')
    #gpsPoints.to_csv('test.csv')
    gpsPoints = gpsPoints.drop(columns=['index_right'])
    
    
    ## 3. Listado de tracks del GPS
    #print("GPSPoints")
    #print(gpsPoints)

    tracks = gpsPoints.track_fid.unique()
    #print("Tracks")
    #print(tracks)
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
#    print(segmentos)
    
    minSpeed = velMin

    ## Actualizar cálculo del timestamp en segundos
    gpsPoints['time']=pd.to_datetime(gpsPoints['time'], infer_datetime_format=True)    
    

    gpsPoints['tiempo_segundos'] = gpsPoints[['time']].apply(lambda x: x[0].timestamp(), axis=1).astype(int)

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
                                  'Sentido': pd.Series([], dtype = 'str'),
                                  'Segmento': pd.Series([], dtype = 'str'),
                                  'Modo':pd.Series([], dtype = 'str'),
    })


    ## Procesar para cada track los recorridos
    viaje = 1
    for row in collectorDB.iterrows():
    
        Track = row[1][0]
        Sentido = row[1][2]
        reg_inicio =row[1][4]
        reg_fin = row[1][5]
    
        trip = gpsPoints[(gpsPoints['track_seg_point_id']>=reg_inicio) & (gpsPoints['track_seg_point_id']<=reg_fin) &(gpsPoints['track_fid']== Track)]
        trip['Sentido'] = Sentido
    
        tripTagged = gpd.sjoin(trip, segmentos, how = 'left', op ='intersects' )
#        print("Print tagged")        
#        print(tripTagged)
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
    
        tripShort = tripTagged[['track_fid','track_seg_point_id','time','tiempo_segundos','Time_s_prev','Sentido','Nombre_right','Desde_right','Hasta_right','Dist_m','Vel_Km_h','No_Recorrido','Modo','Time_s']]
    
        CompilaRecorridos = CompilaRecorridos.append(tripShort)
        viaje = viaje+1
    
    archivo1 = proyecto +"/"+ "01_Resultado_"+gpsFilename+"_base_cruda.csv"
    print("El archivo 1 se guarda como ")
    print(archivo1)
    CompilaRecorridos.to_csv(archivo1)
    
    # Parte 2, cálculo de velocidades, tiempos y organizar resultados
    
    ## Revisar este bloque, quitar tiempo max - minimo, computar con dtiempo 
    base = CompilaRecorridos
    
    base['Vel_x_tiem'] = base['Vel_Km_h']*base['Time_s']
    result = base.groupby(['No_Recorrido','Sentido','Desde_right','Hasta_right']).agg({'Dist_m':['sum'],
                                                                                   'Time_s_prev':['min'],
                                                                                   'tiempo_segundos': ['min','max'],
                                                                                   'Vel_x_tiem':['sum'],
                                                                                   'Time_s':['sum']})
    print("Resultado group By")
    print(result)
    
    ## Temporal de revisión de indicadores
    
    archivo1_5 = proyecto +"/"+ gpsFilename + "groupBy.csv"
    result.to_csv(archivo1_5)
    
    ## Fin temporal
    
    result = result.reset_index()
    result.columns=['Recorrido','Sentido','Desde','Hasta','Distancia','Tiempo_prev_min','Tiempo_min','Tiempo_max','VelT','Ttot']
    result['VelPonderada'] = result['VelT']/result['Ttot']
    result['Tiempo_en_tramo'] = (result['Tiempo_max']-result['Tiempo_min'])/3600
    result['Velocidad'] = (result['Distancia']/1000)/result['Tiempo_en_tramo']
    
    #Print results second stage
    archivo2 = proyecto +"/"+ "02_Resultado_"+gpsFilename+"_velocidad_calculada.csv"
    result.to_csv(archivo2)

    ## Corrección de los tiempos de distancias

    ## Pivot table para simular formato de entrega

    tabla = pd.pivot_table(result, values = 'Tiempo_en_tramo', index = ['Desde','Hasta'], columns = ['Sentido','Recorrido'])
    archivo3 = proyecto +"/"+"03_Resultado"+gpsFilename+"formato_reporte.csv"
    tabla.to_csv(archivo3)
    
    #tabla
    print("Finalizado correctamente")

procesarGPS("T9_Noviembre","G9_Sergio_Oct9_AT_AC100_entre_KR48_y_KR7_LCL_BCL.gpx", "G9_No1_proyectado.shp", "Autos",3)
