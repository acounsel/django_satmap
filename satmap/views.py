import folium
from .utils import initialize_gee
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
from django.urls import reverse
from django.views.generic import View, DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from .forms import MapForm
from .models import Map, Project

from folium import plugins
# from .forms import MapForm

from datetime import datetime

import ee

class MapView(LoginRequiredMixin, View):
    model = Map
    form_class = MapForm
   
class MapList(MapView, ListView):
    pass

class MapDetail(MapView, DetailView):
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        initialize_gee()
        # Define an image.
        map = self.get_object()
        figure = folium.Figure()
        
        # mapbox_satellite_url = "https://api.mapbox.com/styles/v1/mapbox/satellite-v9/tiles/256/{z}/{x}/{y}@2x?access_token={}".format(settings.MAPBOX_KEY)
        mapbox_satellite_url = 'https://api.mapbox.com/styles/v1/mapbox/satellite-v9/tiles/256/{z}/{x}/{y}@2x?access_token=pk.eyJ1Ijoic2FyYWFiaSIsImEiOiJjbGxvYmpxYWMwNzR4M2luM2FhMTBtMDFwIn0.dtam9tTkw1w0b88z-c_BDA'

        #create Folium Object
        m = folium.Map(
            location=[map.latitude, map.longitude], 
            tiles=mapbox_satellite_url, 
            attr='Mapbox',
            zoom_start=map.zoom
        )

        #add map to figure
        m.add_to(figure)

        dates = []

        for layer_instance in map.layer.all():
            #select the Dataset Here's used the MODIS data
            if layer_instance.is_collection:
                datasets = (ee.ImageCollection(layer_instance.code).filter(
                    ee.Filter.date(
                        map.start_date.strftime('%Y-%m-%d'),
                        map.end_date.strftime('%Y-%m-%d')
                    )).sort('system:time_start', False))
                dataset = datasets.first()
                dates += datasets.aggregate_array('system:time_start').getInfo()
            else:
                dataset = (ee.Image(layer_instance.code))
                dates.append(dataset.get('system:time_start').getInfo())
            
            layer = dataset.select(layer_instance.band)

            vis_params = layer_instance.get_vis_params()
            
            #add the map to the the folium map
            map_id_dict = ee.Image(layer).getMapId(vis_params)
        
            #GEE raster data to TileLayer
            folium.raster_layers.TileLayer(
                        tiles = map_id_dict['tile_fetcher'].url_format,
                        attr = 'Google Earth Engine',
                        name = layer_instance.name,
                        overlay = True,
                        control = True
                        ).add_to(m)
        
        #add Layer control
        m.add_child(folium.LayerControl())

        python_dates = []
        print(dates)
        for date in dates:
            python_date = datetime.utcfromtimestamp(date / 1000.0).strftime('%Y-%m-%d')
            python_dates.append(python_date)
        
        context['folium_map'] = figure.render()
        context['dates'] = python_dates
        return context

class MapSplit(MapView, DetailView):
    template_name = 'satmap/map_split.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Define an image.
        map = self.get_object()
        initialize_gee()
        figure = folium.Figure()
        
        #create Folium Object
        m = plugins.DualMap(
            location=[map.latitude, map.longitude], 
            zoom_start=map.zoom
        )

        layer_one = map.layer.first()
            #select the Dataset Here's used the MODIS data
        dataset = (ee.ImageCollection(layer_one.code).filter(
            ee.Filter.date(
                map.start_date.strftime('%Y-%m-%d'),
                map.end_date.strftime('%Y-%m-%d')
            )).first())
        layer = dataset.select(layer_one.band)
        
        vis_params = layer_one.get_vis_params()
        
        #add the map to the the folium map
        map_id_dict = ee.Image(layer).getMapId(vis_params)
    
        #GEE raster data to TileLayer
        folium.raster_layers.TileLayer(
                    tiles = map_id_dict['tile_fetcher'].url_format,
                    attr = 'Google Earth Engine',
                    name = layer_one.name,
                    overlay = True,
                    control = True
                    ).add_to(m.m1)
        
        layer_two = map.layer.first()
            #select the Dataset Here's used the MODIS data
        collection = ee.ImageCollection(layer_two.code).filter(
            ee.Filter.date(
                map.start_date.strftime('%Y-%m-%d'),
                map.end_date.strftime('%Y-%m-%d')
            ))
        latest = collection.sort('system:time_start', False).first()
        layer = latest.select(layer_two.band)

        vis_params = layer_two.get_vis_params()
        
        #add the map to the the folium map
        map_id_dict = ee.Image(layer).getMapId(vis_params)
    
        #GEE raster data to TileLayer
        folium.raster_layers.TileLayer(
                    tiles = map_id_dict['tile_fetcher'].url_format,
                    attr = 'Google Earth Engine',
                    name = layer_two.name,
                    overlay = True,
                    control = True
                    ).add_to(m.m2)

        # m = m._repr_html_()
        # m.add_to(figure)
        # figure.render()
        # figure_html = figure._repr_html_()
        m.add_child(folium.LayerControl())
        context['folium_map'] = m._repr_html_()
        return context
    
class MapTimeSeries(MapView, DetailView):
    template_name = 'satmap/map_split.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Define an image.
        map = self.get_object()
        initialize_gee()

        figure = folium.Figure()
        
        #create Folium Object
        m = folium.Map(
            location=[map.latitude, map.longitude],
            zoom_start=map.zoom
        )
        for layer_instance in map.layer.all():
            #select the Dataset Here's used the MODIS data
            dataset = (ee.ImageCollection(layer_instance.code).filter(
                ee.Filter.date(
                    map.start_date.strftime('%Y-%m-%d'),
                    map.end_date.strftime('%Y-%m-%d')
                )).first())
            layer = dataset.select(layer_instance.band)

            vis_params = layer_instance.get_vis_params()
            
            #add the map to the the folium map
            map_id_dict = ee.Image(layer).getMapId(vis_params)
            #GEE raster data to TileLayer
            folium.raster_layers.TileLayer(
                        tiles = map_id_dict['tile_fetcher'].url_format,
                        attr = 'Google Earth Engine',
                        name = layer_instance.name,
                        overlay = True,
                        control = True
                        ).add_to(m)
        
        geojson_data = {
            "type": "FeatureCollection",
            "features": [
                {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [float(map.latitude), float(map.longitude)]
                },
                "properties": {
                    "times": [map.start_date.strftime('%Y-%m-%d'),
                        map.end_date.strftime('%Y-%m-%d')]
                }
                }
            ]
        }
        print(geojson_data)

        plugins.TimestampedGeoJson(
            geojson_data,
            period='P1D',  # Defines the granularity of the time slider (1 day in this case)
            add_last_point=True
        ).add_to(m)

        m.add_child(folium.LayerControl())
        context['folium_map'] = m._repr_html_()
        return context

class MapCreate(MapView, CreateView):
    def get_project(self):
        return Project.objects.get(id=self.request.GET['project'])

    def get_initial(self):
        initial = super().get_initial()
        project = self.get_project()
        initial['project'] = project
        initial['start_date'] = project.start_date
        initial['end_date'] = project.end_date
        initial['latitude'] = project.latitude
        initial['longitude'] = project.longitude
        initial['layer'] = project.datasets.all()
        return initial.copy()

    def get_success_url(self):
        project = self.get_project()
        return reverse('project_detail', kwargs={'pk':project.id})
    
class MapDuplicate(MapCreate):
    def get_map(self):
        return Map.objects.get(id=self.kwargs['pk'])

    def get_initial(self):
        initial = super().get_initial()
        map = self.get_map()
        initial['project'] = map.project
        initial['title'] = map.title + ' Copy'
        initial['zoom'] = map.zoom
        initial['start_date'] = map.start_date
        initial['end_date'] = map.end_date
        initial['latitude'] = map.latitude
        initial['longitude'] = map.longitude
        initial['layer'] = map.layer.all()
        return initial.copy()

class MapUpdate(MapView, UpdateView):
    def get_map(self):
        return Map.objects.get(id=self.kwargs['pk'])
    
    def get_success_url(self):
        map = self.get_map()
        return reverse('map_detail', kwargs={'pk': map.id})

class MapDelete(MapView, DeleteView):
    def get_map(self):
        return Map.objects.get(id=self.kwargs['pk'])
    
    def get_success_url(self):
        map = self.get_map()
        return reverse('project_detail', kwargs={'pk':map.project.id})

class ProjectView(LoginRequiredMixin, View):
    model = Project

class ProjectCreate(ProjectView, CreateView):
    fields = ('name', 'description',
        'latitude', 'longitude', 'start_date', 'end_date', 'datasets')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        return response
    
class ProjectDuplicate(ProjectCreate, CreateView):
    def get_project(self):
        return Project.objects.get(id=self.kwargs['pk'])
    
    def get_initial(self):
        initial = super().get_initial()
        project = self.get_project()
        initial['name'] = project.name + ' Copy'
        initial['description'] = project.description
        initial['start_date'] = project.start_date
        initial['end_date'] = project.end_date
        initial['latitude'] = project.latitude
        initial['longitude'] = project.longitude
        initial['datasets'] = project.datasets.all()
        return initial.copy()
    
    def form_valid(self, form):
        response = super().form_valid(form)
        newproject = form.instance
        project = self.get_project()
        maps = Map.objects.filter(project=project)
        for map in maps:
            map.duplicate(project=newproject)
        return response
        
    def get_success_url(self):
        return reverse('project_list')

class ProjectDetail(ProjectView, DetailView):
    pass

class ProjectUpdate(ProjectCreate, UpdateView):
    pass

class ProjectList(ProjectView, ListView):
    model = Project

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)
    
class ProjectDelete(ProjectView, DeleteView):

    def get_success_url(self):
        return reverse('project_list')
