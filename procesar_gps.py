### Libraries
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import geopandas as gpd
import numpy as np
### Parameters

def open_file (project, gpsFile, shpFile):
    ''' Takes project name and file names and open the respective files from the project folder
    Args:
        project (str): name of the project folder
        gpsFile (str): name of the gps file (including.gpx)
        shpFile (str): name of the shp zones file (including .shp)
    Returns:
        gpsPoints: geodataframe containing gps points data
        shpPolygons: geodataframe containing shapefile polygons data
        
    '''
    gpsName = project+"/"+gpsFile
    shpName = project+"/"+shpFile
    
    gpsPoints = gpd.read_file(gpsName, layer = 'track_points')
    shpPolygons = gpd.read_file(shpName)
    
    return gpsPoints, shpPolygons   

def project_epsg_batch(filelist, crs):
    ''' Takes geodataframes contained in a vector and project o a specified crs
    Args:
        filelist (vector): vector containing n geodataframes
        crs (str): name of the crs to be projected (ex: EPSG:3116)
    Returns:
        filelist: vector containing n transformed geodataframes
        
    '''
    elements = len(filelist)
    for i in range(elements):
        filelist[i]=filelist[i].to_crs(crs)
    return(filelist)

def filter_zones(polygons, zone_type, check_entities):
    ''' Filter zones based on zone-_type, and then check if they have at least 2 zones
    Args:
        polygons(gdf): geodataframe containing desired polygons to be filtered
        zone_type(str):Word to be used in the filter of Tipo column
        check_entities(bool): Check if there are more than 2 entities, this is necessary because in border, we need at least 2 zones
    Returns: Filtered GeodataFrame
    '''
    filteredGPD = polygons[polygons['Tipo']== zone_type]
    
    ## Check minimum errors
    if check_entities == True:
        print('Checking minimun units for {}'.format(zone_type))
        no_entities = filteredGPD['geometry'].count()
        if (no_entities < 2):
            print('Warning, theres not enough zones tagged as Borde, only {}'.format(no_entities))
        else:
            print('Notice, there are {} polygons'.format(no_entities))
    return(filteredGPD)

def direction_identificator(geoTrackPoints, noTrack):
    '''Detect direction for a specific track based on a name change in the
    border zones
    Args:
        geoTrackPoints(gdf)= geodataframe containing gpx point data
        noTrack(int) = no of track
    Returns Points where direction changes
    '''
    # Filter points of specific track
    track_segment = geoTrackPoints[geoTrackPoints['track_fid'] == noTrack]
    # Eliminate intermediate points    
    trackBorderPoints = track_segment[track_segment[['Nombre']].notnull().all(1)]
    # When name changes, is a direction change
    trackBorderPoints.loc[:, 'track_seg_point_id_destino'] = trackBorderPoints['track_seg_point_id'].shift(-1)
    trackBorderPoints.loc[:, 'Nombre_destino'] = trackBorderPoints['Nombre'].shift(-1)  
    changingPoint = trackBorderPoints[trackBorderPoints['Nombre'] != trackBorderPoints['Nombre_destino']]
    changingPoint.loc[:, 'Sentido'] = ('De '+ changingPoint['Nombre'] + ' a ' +  changingPoint['Nombre_destino'])
    changePoints = changingPoint[changingPoint['Nombre_destino'].notnull()]    
    return changePoints

def calculateSpeed(geodataframe, segments, row, tripCount, mode, minSpeed):
    ## Define facts from row
    track = row[1][0]
    direction = row[1][2]
    staRow = row[1][4]
    endRow = row[1][5]
    
    #Filter geodataframe trip and assign direction
    trip = geodataframe[(geodataframe['track_seg_point_id']>=staRow) & (geodataframe['track_seg_point_id']<=endRow) &(geodataframe['track_fid']== track)]
    trip['Sentido'] = direction
    tripTagged = gpd.sjoin(trip, segments, how = 'left', op ='intersects' )
    tripTagged['No_Recorrido'] = tripCount
    
    # Process position and distance
    tripTagged['Xi'] = tripTagged.geometry.x
    tripTagged['Yi'] = tripTagged.geometry.y
    tripTagged['Xi_1'] = tripTagged.Xi.shift()
    tripTagged['Yi_1'] = tripTagged.Yi.shift()
    tripTagged['Dist_m'] = np.sqrt(pow((tripTagged['Xi']-tripTagged['Xi_1']),2)+pow((tripTagged['Yi']-tripTagged['Yi_1']),2))
    tripTagged['Distance_meters_original'] = tripTagged['Distance_m_right']
    # Time
    tripTagged['Time_s'] = tripTagged['tiempo_segundos']-tripTagged['tiempo_segundos'].shift()
    tripTagged['Time_s_prev'] = tripTagged.tiempo_segundos.shift()
    tripTagged['Vel_Km_h'] = (tripTagged['Dist_m']/tripTagged['Time_s'])*3.6
    
    ## Filter based on a min speed valule
    tripTagged['Modo'] = mode
    #if speedBool == True:
    #    print("Filtering min speed")
    filteredSpeedTrip = tripTagged[tripTagged['Vel_Km_h'] >= minSpeed]        
    tripShort = filteredSpeedTrip[['track_fid','track_seg_point_id','time','tiempo_segundos','Time_s_prev','Sentido','Nombre_right','Desde_right','Hasta_right','Dist_m','Vel_Km_h','No_Recorrido','Modo','Time_s','Distance_meters_original','geometry','Xi','Yi']]
    return tripShort
def cumsumFilter(speedTracks):
    compilaRecorridos = speedTracks.sort_values(['No_Recorrido','Nombre_right','Vel_Km_h'], ascending = (True, True, False))  
    compilaRecorridos['CumDistance']=compilaRecorridos.groupby(['No_Recorrido','Nombre_right'])['Dist_m'].transform(pd.Series.cumsum)
    #CompilaRecorridos.to_csv(archivo1)
    filteredTracks = compilaRecorridos[compilaRecorridos['CumDistance'] <= compilaRecorridos['Distance_meters_original']]
    return compilaRecorridos, filteredTracks
### Main function
    
def procesarGPS(proyecto, gpsFilename, geoZonesFilename, modo, velMin):
    ## Paquetes
    import pandas as pd
    import geopandas as gpd
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    import numpy as np
    from datetime import datetime
    
    ## Open files 
    print('Open File')
    gpsPointsR, geoZonesR = open_file(proyecto, gpsFilename, geoZonesFilename)

    ## Project files
    
    crs = "EPSG:3116"
    print('Project coordinates')
    gpdVector = project_epsg_batch([gpsPointsR, geoZonesR], crs)
    
    gpsPointsA = gpdVector[0]
    geoZones =  gpdVector[1]
    
    ## Select relevant columns
        
    gpsPoints = gpsPointsA[['track_fid','track_seg_point_id','ele','time','geometry']]
    
    #### Etapa A: Borders and track direction
    
    ## Filter border zones
    print('Filter border zones')
    borders = filter_zones(geoZones, 'Borde', True)
 
    ## 2. Spatial Join between borders and gps points
    print("Loop in tracks")
    gpsPoints = gpd.sjoin(gpsPoints, borders, how = "left", op='intersects')
    gpsPointsNoIndex = gpsPoints.drop(columns=['index_right'])
    
    ## 3. List of GPS tracks

    tracks = gpsPointsNoIndex.track_fid.unique()

    ## 4. Definition of dataframe that collects borders
    
    collectorDB = pd.DataFrame({'track_fid': pd.Series([],dtype = 'int'),
                           'rec_orige': pd.Series([],dtype = 'int'),
                           'Sentido': pd.Series([],dtype = 'str'),
                           'rec_destino': pd.Series([],dtype = 'int')})
    ## 5. Iterate over tracks 
    countTrack = 0
    
    for track in tracks:           
        ## Filter points in the chosen track     
        trackBorderPoints = direction_identificator(gpsPointsNoIndex, track)
        ## Can we reduce columns in the function??
        collectorDB = pd.concat([collectorDB, trackBorderPoints[['track_fid','track_seg_point_id','Sentido','track_seg_point_id_destino']]])
        countTrack =countTrack + 1   
    print('{} tracks found in gpx file'.format(countTrack) )    
    ## 6. Filter dataframe based on changing points
    ## Filter zone type segments
    segmentos = geoZones[geoZones ['Tipo']=='Segmento']
    minSpeed = velMin
    ## Convert time to datetime format
    gpsPointsNoIndex['time']=pd.to_datetime(gpsPointsNoIndex['time'], infer_datetime_format=True)    
    #Calculate time as a second timestamp (int type)
    gpsPointsNoIndex['tiempo_segundos'] = gpsPointsNoIndex[['time']].apply(lambda x: x[0].timestamp(), axis=1).astype(int)

    ## Database to compile trips

    CompilaRecorridos = pd.DataFrame({'track_fid': pd.Series([], dtype = 'int'),
                                  'track_seg_point_id': pd.Series([], dtype = 'int'),
                                  'time': pd.Series([], dtype = 'str'),
                                  'Sentido': pd.Series([], dtype = 'str'),
                                  'Segmento': pd.Series([], dtype = 'str'),
                                  'Modo':pd.Series([], dtype = 'str'),
    })

    ## Process each trip 
    viaje = 1
    print("Loop per each trip to compute speed")

    for row in collectorDB.iterrows():   
        processedSpeed = calculateSpeed(gpsPointsNoIndex, segmentos, row, viaje, modo, velMin)       
        CompilaRecorridos = pd.concat([CompilaRecorridos, processedSpeed])
        viaje = viaje+1
        
    print("{} trips has been processed".format(viaje))
    
    ### Save first result (In csv and geojson)    
    
    archivo1 = proyecto +"/"+ "01_Resultado_"+gpsFilename+"_base_cruda.csv"
    archivo1gjson = proyecto +"/"+ "01_Resultado_"+gpsFilename+"_base_cruda.geojson"
    CompilaRecorridos.to_csv(archivo1)
    GeoTrack = gpd.GeoDataFrame(CompilaRecorridos, geometry=gpd.points_from_xy(CompilaRecorridos.Xi,CompilaRecorridos.Yi)).set_crs(crs)
    GeoTrack.to_file(archivo1gjson, driver='GeoJSON')
    print("El archivo 1 se guarda como ")
    print(archivo1)    
    
    ### Sort speeds and calculate cumsum
    
    cumsumDatabase, filteredDatabase = cumsumFilter(CompilaRecorridos)
    
    archivo2 = proyecto +"/"+ "02_Resultado_"+gpsFilename+"_base_cruda_cumsum.csv"
    cumsumDatabase.to_csv(archivo2)
    archivo3 = proyecto +"/"+ "03_Resultado_"+gpsFilename+"_base_cruda_cumsum_filtered.csv"
    filteredDatabase.to_csv(archivo3)
    print("Results of cumsum")
    print("Original file has {} rows".format(len(cumsumDatabase.index)))
    print("Results of filtered cumsum")
    print("Filtered file has {} rows".format(len(filteredDatabase.index)))
    
    
    ## Speed calculations, times and output format
        
    
    ## Revisar este bloque, quitar tiempo max - minimo, computar con dtiempo
    base = CompilaRecorridos
    base['Vel_x_tiem'] = base['Vel_Km_h']*base['Time_s']
    statistics = base.groupby(['No_Recorrido','Sentido','Desde_right','Hasta_right']).agg({'No_Recorrido':['count'],
                                                                                           'Vel_Km_h':['min','max','std'],
                                                                                           'Vel_x_tiem':['sum'],
                                                                                           'Time_s':['sum'],
                                                                                           'Distance_meters_original':['max'],
                                                                                           'Dist_m':['sum']})
    
    archivo4 = proyecto+"/"+"04_Resultado_"+gpsFilename+"_estadisticos.csv"
    statistics.to_csv(archivo4)
    result = base.groupby(['No_Recorrido','Sentido','Desde_right','Hasta_right']).agg({'Dist_m':['sum'],
                                                                                   'Time_s_prev':['min'],
                                                                                   'tiempo_segundos': ['min','max'],
                                                                                   'Vel_x_tiem':['sum'],
                                                                                   'Time_s':['sum']})
    print("Resultado group By")
    print(result)
    
    ## Temporal de revisión de indicadores
    archivo5 = proyecto +"/"+"05_Resultado_"+ gpsFilename + "groupBy.csv"
    result.to_csv(archivo5)
    
    ## Fin temporal
    
    result = result.reset_index()
    result.columns=['Recorrido','Sentido','Desde','Hasta','Distancia','Tiempo_prev_min','Tiempo_min','Tiempo_max','VelT','Ttot']
    result['VelPonderada'] = result['VelT']/result['Ttot']
    result['Tiempo_en_tramo'] = (result['Tiempo_max']-result['Tiempo_min'])/3600
    result['Velocidad'] = (result['Distancia']/1000)/result['Tiempo_en_tramo']
    
    #Print results second stage
    archivo5 = proyecto +"/"+ "05_Resultado_"+gpsFilename+"_velocidad_calculada.csv"
    result.to_csv(archivo5)

    ## Corrección de los tiempos de distancias

    ## Pivot table para simular formato de entrega

    tabla = pd.pivot_table(result, values = 'Tiempo_en_tramo', index = ['Desde','Hasta'], columns = ['Sentido','Recorrido'])
    archivo6 = proyecto +"/"+"06_Resultado"+gpsFilename+"formato_reporte.csv"
    tabla.to_csv(archivo6)
    
    #tabla
    print("Finalizado correctamente")

#procesarGPS("G3_Test","AT_G4_GPS12_08012022_LCR.gpx", "G4_CRS.shp", "Livianos calzada rapida",3)
