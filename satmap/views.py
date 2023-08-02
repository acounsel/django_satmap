from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views.generic import View, DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView
from .models import Map, Project
# from .forms import MapForm
from django.shortcuts import redirect

class MapView(View):
    model = Map

class MapList(MapView, ListView):
    pass

class MapDetail(MapView, DetailView):
    pass

class MapCreate(MapView, CreateView):
    pass

class ProjectCreate(CreateView):
    model = Project
    fields = ('name', 'description', 
        'latitude', 'longitude', 'start_date', 'end_date', 'datasets')
    success_url = '/'

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