import folium

from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
from django.urls import reverse
from django.views.generic import View, DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from .models import Map, Project

from folium import plugins
# from .forms import MapForm

import ee

class MapView(View):
    model = Map
    fields = ('title', 'latitude', 'longitude', 'zoom', 
        'project', 'layer', 'start_date', 'end_date')

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

        for layer_instance in map.layer.all():
            #select the Dataset Here's used the MODIS data
            dataset = (ee.ImageCollection(layer_instance.code).filter(
                ee.Filter.date(
                    map.start_date.strftime('%Y-%m-%d'),
                    map.end_date.strftime('%Y-%m-%d')
                )).first())
            layer = dataset.select(layer_instance.band)

            #Styling 
            vis_params = {
                'min': float(layer_instance.min),
                'max': float(layer_instance.max),
                'palette': layer_instance.get_palette_list(),
                'opacity': float(layer_instance.opacity)
                }
            
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
       
        #figure 
        figure.render()
        context['folium_map'] = figure
        # image = ee.Image('LANDSAT/LC08/C01/T1_TOA/LC08_044034_20140318')
        # # Get image URL
        # context['url'] = image.getThumbURL({'min': 0, 'max': 3000, 'scale': 300})
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
    pass

class MapDelete(MapView, DeleteView):
    def get_map(self):
        return Map.objects.get(id=self.kwargs['pk'])
    
    def get_success_url(self):
        map = self.get_map()
        return reverse('project_detail', kwargs={'pk':map.project.id})

class ProjectCreate(CreateView):
    model = Project
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

class ProjectDetail(DetailView):
    model = Project

class ProjectUpdate(ProjectCreate, UpdateView):
    pass

class ProjectList(ListView):
    model = Project

class ProjectDelete(DeleteView):
    model = Project;
    def get_success_url(self):
        return reverse('project_list')

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