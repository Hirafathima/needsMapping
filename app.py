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

app = Flask(__name__)
CORS(app, resources={r"/get_dept/*": {"origins": "*"}})


data= pd.read_csv('./CitizenNeeds.csv')
map_data = pd.DataFrame(data['District'].value_counts().reset_index())
map_data.columns=['District','count']
districts = data['District']
m = {}
for i in map_data['District']:
    n = {}
    k = {}
    val = districts.str.contains(i)
    n = data[val]['Basic Need'].value_counts()
    k['basic'] = n.to_dict()
    n = data[val]['Standard Need'].value_counts()
    k['Standard'] = n.to_dict()
    n = data[val]['Premium Need'].value_counts()
    k['Premium'] = n.to_dict()
    m[i] = k


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




@app.route('/map.html')
def show_map():
    data= pd.read_csv('./CitizenNeeds.csv')
    Rest_locations= pd.read_csv('./Rest_locations.csv')
    data = pd.DataFrame({
    'lat':Rest_locations['lat'],
    'lon':Rest_locations['lon'],
    'name':Rest_locations['Name'],
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
    chains=data['Basic Need'].value_counts()
    sns.barplot(x=chains,y=chains.index,palette='rocket')
    plt.title("Density plot of Basic Need in Kerala")
    plt.xlabel("Number of citizens opted")
    plt.savefig('./plot-basic.png')
    return send_file('./plot-basic.png', mimetype='image/png')

@app.route('/barplot-standard')
def get_image2():
    plt.figure(figsize=(15,8))
    chains=data['Standard Need'].value_counts()
    sns.barplot(x=chains,y=chains.index,palette='rocket')
    plt.title("Density plot of Standard Need in Kerala")
    plt.xlabel("Number of citizens opted")
    plt.savefig('./plot-standard.png')
    return send_file('./plot-standard.png', mimetype='image/png')

@app.route('/barplot-premium')
def get_image3():
    plt.figure(figsize=(15,8))
    chains=data['Premium Need'].value_counts()
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

