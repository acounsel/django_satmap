import folium

from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
from django.urls import reverse
from django.views.generic import View, DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView

from .models import Map, Project

from folium import plugins
# from .forms import MapForm

import ee

class MapView(View):
    model = Map

class MapList(MapView, ListView):
    pass

class MapDetail(MapView, DetailView):
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Define an image.
        map = self.get_object()
        service_account = 'satmap@ee-samer.iam.gserviceaccount.com'
        credentials = ee.ServiceAccountCredentials(service_account, 'ee-samer-1cb0ce0fa0a0.json')
        ee.Initialize(credentials)
        figure = folium.Figure()
        
        #create Folium Object
        m = folium.Map(
            location=[map.latitude, map.longitude],
            zoom_start=map.zoom
        )

        #add map to figure
        m.add_to(figure)

        
        #select the Dataset Here's used the MODIS data
        dataset = (ee.ImageCollection(map.layer.code).filter(
            ee.Filter.date(
                map.start_date.strftime('%Y-%m-%d'),
                map.end_date.strftime('%Y-%m-%d')
            )).first())
        modisndvi = dataset.select(map.layer.band)

        #Styling 
        vis_paramsNDVI = {
            'min': map.layer.min,
            'max': map.layer.max,
            'palette': [ 'FE8374', 'C0E5DE', '3A837C','034B48',]}

        
        #add the map to the the folium map
        map_id_dict = ee.Image(modisndvi).getMapId(vis_paramsNDVI)
       
        #GEE raster data to TileLayer
        folium.raster_layers.TileLayer(
                    tiles = map_id_dict['tile_fetcher'].url_format,
                    attr = 'Google Earth Engine',
                    name = map.layer.band,
                    overlay = True,
                    control = True
                    ).add_to(m)

        
        #add Layer control
        m.add_child(folium.LayerControl())
       
        #figure 
        figure.render()
        context['folium_map'] = figure
        # image = ee.Image('LANDSAT/LC08/C01/T1_TOA/LC08_044034_20140318')
        # # Get image URL
        # context['url'] = image.getThumbURL({'min': 0, 'max': 3000, 'scale': 300})
        return context

class MapCreate(MapView, CreateView):
    fields = ('title', 'latitude', 'longitude', 'zoom', 
        'project', 'layer', 'start_date', 'end_date')
    
    def get_project(self):
        return Project.objects.get(id=self.request.GET['project'])

    def get_initial(self):
        initial = super().get_initial()
        project = self.get_project()
        initial['project'] = project
        initial['latitude'] = project.latitude
        initial['longitude'] = project.longitude
        return initial.copy()

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        return response

    def get_success_url(self):
        project = self.get_project()
        return reverse('project_detail', kwargs={'pk':project.id})

class ProjectCreate(CreateView):
    model = Project
    fields = ('name', 'description',
        'latitude', 'longitude', 'start_date', 'end_date', 'datasets')

class ProjectDetail(DetailView):
    model = Project

class ProjectList(ListView):
    model = Project

# def map_list(request):
#     maps = Map.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
#     return render(request, 'blog/map_list.html', {'maps': maps})

# def map_detail(request, pk):
#     map = get_object_or_404(Map, pk=pk)
#     return render(request, 'blog/map_detail.html', {'map': map})

# def map_edit(request, pk):
#     map = get_object_or_404(Map, pk=pk)
#     if request.method == "POST":
#         form = MapForm(request.POST, instance=map)
#         if form.is_valid():
#             map = form.save(commit=False)
#             map.author = request.user
#             map.published_date = timezone.now()
#             map.save()
#             return redirect('map_detail', pk=map.pk)