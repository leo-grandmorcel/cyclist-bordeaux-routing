from django.http import HttpResponse
import folium


def index(request):
    figure = folium.Figure()

    # Make the map
    map = folium.Map(
        location=[44.841225, -0.580036], zoom_start=13, tiles="OpenStreetMap"
    )

    map.add_to(figure)

    # Render and send to template
    figure.render()
    return HttpResponse(figure._repr_html_())
