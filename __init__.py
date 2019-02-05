import requests
import json


#%% LIENS VERS LES DIFFERENTS DATASETS

arbres_name = 'arbresremarquablesparis'
velib_name = 'velib-disponibilite-en-temps-reel'

#%%

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
        self.records1 = self.obj1['records']
        return self.records1
        
        

    def find(self,critere='',valeur=1): #critère de tri à définir lors de l'application de la fonction sortby
        result= []
        for i in range(len(self.records)) :
            if self.records[i]['fields'][critere]==valeur :
                result.append(self.records[i])
        if result!=[] :
            return result
        else:
            print ('No matches')
        
#%%
station=Dataset(velib_name)
arbres=Dataset(arbres_name)

#%%


import time
times = []     #liste vide qui va contenir les temps
base = station.request(nrows=10,sortby='station_id') #on fait une premiere requete pour acceder a tous les stations_id
data = {} 
for dico in base :
    station_id = dico['fields']['station_id']
    data[str(station_id)]=[]            #on cree un dictionnaire dont les cles sont les station_id et les valeurs sont des listes vides

for i in range(10):
    val = station.request(nrows=10,sortby='station_id') #on effectue une requete regulierement dans le temps
    times.append(time.time())  #on remplit la liste times avec l'instant t ou a ete effectuee la requete
    time.sleep(1)
    print("performing request number " + str(i))
    
    for dicobis in val :    #on remplit les listes du dictionnaire data avec les numbikes available a l'instant t 
        data[str(dicobis['fields']['station_id'])].append(dicobis['fields']['numbikesavailable'])
    
    with open('datas.json', 'w') as f:
        json.dump(data,f,indent=4)


    

    