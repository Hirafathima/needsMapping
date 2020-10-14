from flask import Flask, render_template, request, Response, jsonify, send_file, Response, json
import requests

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from geopy.geocoders import Nominatim
import folium
import webbrowser
import io
import random
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import json
from flask_cors import CORS
with open("objects.py","r") as outfile:
    example = __import__('objects')
app = Flask(__name__)
CORS(app, resources={r"/get_dept/*": {"origins": "*"}})

url = "https://jsonbox.io/box_de8dc85dd983aa1882e2"
r = requests.get(url)
data = r.json()
print(data)
import csv

data_file = open('data_file.csv', 'w')
csv_writer = csv.writer(data_file)
count = 0

for emp in data:
    if count == 0:
        # Writing headers of CSV file
        header = emp.keys()
        csv_writer.writerow(header)
        count += 1

    # Writing data of CSV file
    csv_writer.writerow(emp.values())

data_file.close()
pd.pandas.set_option('display.max_columns', None)
data= pd.read_csv('./data_file.csv')
locations=pd.DataFrame({"District":data['district'].unique()})
locations['District']=locations['District'].apply(lambda x: "" + str(x))
lat_lon=[]
basic=[]
count_basic=[]
std=[]
count_std=[]
prm=[]
count_prm=[]
basic_link=[]
std_link=[]
prm_link=[]
geolocator=Nominatim(user_agent="app")
for location in locations['District']:
    location = geolocator.geocode(location)
    if location is None:
        lat_lon.append(np.nan)
    else:
        geo=(location.latitude,location.longitude)
        lat_lon.append(geo)

locations['geo_loc']=lat_lon
locations.to_csv('locations.csv',index=False)

map_data = pd.DataFrame(data['district'].value_counts().reset_index())
map_data.columns=['District','count']
map_data=map_data.merge(locations,on='District',how="left").dropna()
lat,lon=zip(*np.array(map_data['geo_loc']))
map_data['lat'], map_data['lon'] =lat, lon



districts = data['district']
m = {}
p={}

for i in map_data['District']:
    n = {}
    k = {}
    q = {}
    r = {}
    val = districts.str.contains(i)
    n = data[val]['basic'].value_counts()
    k['basic'] = n.to_dict()
    n = data[val]['standard'].value_counts()
    k['Standard'] = n.to_dict()
    n = data[val]['premium'].value_counts()
    k['Premium'] = n.to_dict()
    m[i] = k
    # l[i]={'erkm':{'basic':{'health clinic':[]},'std':{'h':[]},'p':{'u':[]}}}



    y=list(m[i]['basic'].keys())
    basic.append(y[0])
    basic_link.append(example.link[0]['basic'][y[0]])
    count_basic.append(m[i]['basic'][y[0]])
    r[y[0]] = example.link[0]['basic'][y[0]]
    q['basic'] = r
    r={}



    y = list(m[i]['Standard'].keys())
    std.append(y[0])
    std_link.append(example.link[1]['standard'][y[0]])
    count_std.append(m[i]['Standard'][y[0]])
    r[y[0]] = example.link[1]['standard'][y[0]]
    q['standard'] = r
    r={}


    y = list(m[i]['Premium'].keys())
    prm.append(y[0])
    prm_link.append(example.link[2]['premium'][y[0]])
    count_prm.append(m[i]['Premium'][y[0]])
    r[y[0]] = example.link[2]['premium'][y[0]]
    q['premium'] = r

    p[i] = q

# print(p)
map_data['basic'], map_data['count_basic'], map_data['std'], map_data['count_std'], map_data['prm'], map_data['count_prm'] =basic, count_basic, std, count_std, prm, count_prm
map_data['basic_link'], map_data['std_link'], map_data['prm_link'] = basic_link, std_link, prm_link
map_data.to_csv('rest_locations.csv')



# @app.route('/<name>')
# def hello(name):
#     return "Hello {}!".format(name)

@app.route('/post_survey', methods=['POST'])
def get_data():
    data = request.get_json()
    return "Survey updated", 201

@app.route('/get_dept')
def send_data():

    app_json = json.dumps(m)
    return app_json

@app.route('/get_links')
def send_link():
    app_link_json = json.dumps(p)
    return app_link_json






@app.route('/map.html')
def show_map():
    data= pd.read_csv('./data_file.csv')
    Rest_locations= pd.read_csv('./rest_locations.csv')
    data = pd.DataFrame({
    'lat':Rest_locations['lat'],
    'lon':Rest_locations['lon'],
    'name':Rest_locations['District'],
    'value_b':Rest_locations['count_basic'],
    'value_s':Rest_locations['count_std'],
    'value_p':Rest_locations['count_prm'],
    'basic':Rest_locations['basic'],
    'std':Rest_locations['std'],
    'prm':Rest_locations['prm']
    })
    m = folium.Map(location=[10.8505, 76.2711], tiles="OpenStreetMap", zoom_start=6)
    for i in range(0,len(data)):
        folium.Circle(
            location=[data.iloc[i]['lat'], data.iloc[i]['lon']],
            popup=data.iloc[i]['name'] + ' : ' + data.iloc[i]['basic'],
            radius=data.iloc[i]['value_b']*1000,
            color='crimson',
            fill=True,
            fill_color='crimson'
        ).add_to(m)
        folium.Circle(
            location=[data.iloc[i]['lat']+0.2, data.iloc[i]['lon']+0.2],
            popup=data.iloc[i]['name'] + ' : ' + data.iloc[i]['std'],
            radius=data.iloc[i]['value_s']*500,
            color='blue',
            fill=True,
            fill_color='blue'
        ).add_to(m)
        folium.Circle(
            location=[data.iloc[i]['lat'], data.iloc[i]['lon']+0.2],
            popup=data.iloc[i]['name'] + ' : ' + data.iloc[i]['prm'],
            radius=data.iloc[i]['value_p']*300,
            color='green',
            fill=True,
            fill_color='green'
        ).add_to(m)
    m.save('mymap.html')
    return m._repr_html_()



@app.route('/barplot-basic')
def get_image1():
    plt.figure(figsize=(15,8))
    chains=data['basic'].value_counts()
    sns.barplot(x=chains,y=chains.index,palette='rocket')
    plt.title("Density plot of Basic Need in Kerala")
    plt.xlabel("Number of citizens opted")
    plt.savefig('./plot-basic.png')
    return send_file('./plot-basic.png', mimetype='image/png')

@app.route('/barplot-standard')
def get_image2():
    plt.figure(figsize=(15,8))
    chains=data['standard'].value_counts()
    sns.barplot(x=chains,y=chains.index,palette='rocket')
    plt.title("Density plot of Standard Need in Kerala")
    plt.xlabel("Number of citizens opted")
    plt.savefig('./plot-standard.png')
    return send_file('./plot-standard.png', mimetype='image/png')

@app.route('/barplot-premium')
def get_image3():
    plt.figure(figsize=(15,8))
    chains=data['premium'].value_counts()
    sns.barplot(x=chains,y=chains.index,palette='rocket')
    plt.title("Density plot of Premium Need in Kerala")
    plt.xlabel("Number of citizens opted")
    plt.savefig('./plot-premium.png')
    return send_file('./plot-premium.png', mimetype='image/png')

@app.route('/weather')
def index():
    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid=f2eed327f2863e731aa1d68dd550548a'
    city = 'London'
    r = requests.get(url.format(city)).json()
    print(r)


if __name__ == '__main__':
    app.run(debug=True)
