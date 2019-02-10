import requests
import json
import time
import folium

#%% I - ECRITURE DE REQUETES GENERIQUES

#liens vers les differents datasets
arbres_name = 'arbresremarquablesparis'
velib_name = 'velib-disponibilite-en-temps-reel'


# En cas de bug du serveur 
class ServerError(BaseException):
    pass

# Classe qui contient les objets stations velib, arbres...etc
class Dataset():
        REQUEST = 'https://opendata.paris.fr/api/records/1.0/search/?dataset='
        def __init__(self, dataset_name): #le lien menant vers le dataset voulu sera indiqué en paramètre par l'utilisateur lors de l'instanciation de la classe
            """
            dataset_name is the name of the dataset as found on the API. e.g.:
            velib-disponibilite-en-temps-reel
            """
            self.dataset_name = dataset_name
            self.res = requests.get(self.REQUEST + self.dataset_name + "&rows=-1") #récupère les données chiffrées depuis parisdata
            self.obj = json.loads(self.res.text) #décode les données au format json
            self.records = self.obj['records'] #renvoie la valeur associée à la clé 'records' du dictionnaire 'obj', cette valeur est une liste qui contient autant de dictionnaires que de rows
            self.nhits=self.obj['nhits'] #nombre total de rows
            self.fields1 = self.records[1]['fields'] #renvoie la valeur associée à la clé 'fields' du premier dictionnaire de la liste 'records', cette valeur est elle-même un dictionnaire
            self.fields = list(self.fields1.keys()) #renvoie la liste des clés du dictionnaire 'fields'
      
        def request(self, nrows=-1, sortby=None):
            '''
            performs a request on the website and returns the first nrows items
            if sortby is provided, the result is sorted by the relevant criterion
            (sortby must be one of the items among self.fields)
            '''
            self.res1 = requests.get('https://opendata.paris.fr/api/records/1.0/search/?dataset=velib-disponibilite-en-temps-reel&rows={0}&sort={1}'.format(nrows,sortby)) #récupère les données chiffrées depuis parisdata
            self.obj1 = json.loads(self.res1.text) #décode les données au format json
            
            if "error" in self.obj1:
                raise ServerError(self.obj1["error"])
                
            self.records1 = self.obj1['records']
            return self.records1
            
    
        def find(self,critere='',valeur=None): 
            '''
            finds the corresponding object to the criteria value
            '''
            result= []
            for i in range(len(self.records)) :
                if self.records[i]['fields'][critere]==valeur :
                    result.append(self.records[i])
            if result!=[] :
                return result
            else:
                print ('No matches')
            
        def find_name(self, my_id): 
            '''
            (specfific to the bikes data) returns the name of a station of given ID number
            '''
            for dico in self.records :
                if dico['fields']['station_id'] == my_id :
                    return dico['fields']['name']
                

#%%  On instancie la classe Dataset en créant les objets station velib et arbres par exemple 
station=Dataset(velib_name)
arbres=Dataset(arbres_name)


#%% Boucle de récupération de données 

SLEEP_TIME = 60 # les requetes sont effectuees toutes les 60 secondes

times = []     #liste vide qui va contenir les temps

base = station.request(nrows=-1,sortby='station_id') #on fait une premiere requete pour acceder a tous les stations_id
data = {} 
for dico in base :
    station_id = dico['fields']['station_id']
    data[str(station_id)]=[]            #on cree un dictionnaire dont les cles sont les station_id et les valeurs sont des listes vides

for i in range(1440):
    try:
        val = station.request(nrows=-1,sortby='station_id') #on effectue une requete regulierement dans le temps
    except BaseException as e:
        print(e)
        continue
    times.append(time.time())  #on remplit la liste times avec l'instant t ou a ete effectuee la requete
    time.sleep(SLEEP_TIME)
    print("performing request number " + str(i))
    
    try:
        for dicobis in val :    #on remplit les listes du dictionnaire data avec les numbikes available a l'instant t 
            data[str(dicobis['fields']['station_id'])].append(dicobis['fields']['numbikesavailable'])
    
        with open('datas.json', 'w') as f:
            json.dump(data,f,indent=4)
    except BaseException as e:
        print(e)
        continue

    
#%% II - Disponibilite des velib de Paris en temps reel\
        
emplacement_name = 'velib-emplacement-des-stations'
emplacement = Dataset(emplacement_name)

# On cree un dictionnaire dont les cles sont les stations ID et les valeurs sont les coordonnees GPS correspondantes
idvsgps = {}
for dico in emplacement.obj['records'] :
    station_id = str(dico['fields']['station_id'])
    gps = dico['fields']['xy']
    idvsgps[station_id] = gps

def timeconvert(hours,minutes) :
    '''
    find the corresponding index to time format 'hours:min'  in the time list
    '''
    index = minutes + hours*60
    return index
    
def bikesnow(hours,minutes) :
    '''
    draws a map of the stations with circle markers whom size depends on the number of bikes available
    '''
    m = folium.Map(location = [48.864716, 2.349014], zoom_start=13)
    with open('datas.json') as f:
        datas = json.load(f)
    for station_id in idvsgps.keys():
        numbikes = datas[str(station_id)][timeconvert(hours,minutes)]
        if numbikes == 0 :      # the color of the marker shows how empty the station is
            col = '#ff0000'
        elif numbikes <= 5 :
            col = '#ffa500'
        else :
            col = '#32cd32'
        folium.CircleMarker(location = idvsgps[station_id], 
                            radius = 5 + 2*numbikes, #radisu proportional to the number of bikes available
                            color = col, 
                            popup = str(emplacement.find_name(float(station_id))) + '\n : ' + str(numbikes) + ' bike(s) available',
                            fill = True, 
                            fill_color = col).add_to(m)
    m.save('map.html')      #save map as html interactive page

#%% EXECUTION

hours, minutes = 6, 15
bikesnow(hours,minutes)

    
    
    
    
    
    
    