import osmnx as ox
import networkx as nx
import folium
from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from utils import get_localisation, render_map, get_graph

GRAPH = get_graph()
# GRAPH = None
print("Graph loaded")

app = FastAPI()


class Itineraire_coo(BaseModel):
    depart: list[float]
    destination: list[float]


class Itineraire_address(BaseModel):
    depart: str
    destination: str


def calculate_route(itineraire: Itineraire_coo):
    node_depart = ox.nearest_nodes(GRAPH, itineraire.depart[1], itineraire.depart[0])
    node_arrivee = ox.nearest_nodes(
        GRAPH, itineraire.destination[1], itineraire.destination[0]
    )
    m = folium.Map(location=[44.841225, -0.580036], zoom_start=12)
    route_length = nx.shortest_path(GRAPH, node_depart, node_arrivee, weight="length")
    route_security = nx.shortest_path(
        GRAPH, node_depart, node_arrivee, weight="security"
    )
    route_score = nx.shortest_path(GRAPH, node_depart, node_arrivee, weight="score")

    for i in range(len(route_length) - 1):
        edge = []
        graph_edge = GRAPH.edges[route_length[i], route_length[i + 1], 0]
        for x, y in graph_edge["geometry"].coords:
            edge.append([y, x])
        tooltip_data = {
            "cycleway": graph_edge["cycleway"],
            "surface": graph_edge["surface"],
            "bicycle": graph_edge["bicycle"],
            "length": graph_edge["length"],
            "oneway": graph_edge["oneway"],
            "security_highway": graph_edge["security_highway"],
            "security_cycleway": graph_edge["security_cycleway"],
            "score": graph_edge["score"],
            "highway": graph_edge["highway"],
        }
        tooltip = folium.Tooltip(tooltip_data)
        folium.PolyLine(
            locations=edge, color="blue", tooltip=tooltip, opacity=0.7
        ).add_to(m)

    for i in range(len(route_security) - 1):
        edge = []
        graph_edge = GRAPH.edges[route_security[i], route_security[i + 1], 0]
        for x, y in graph_edge["geometry"].coords:
            edge.append([y, x])
        tooltip_data = {
            "cycleway": graph_edge["cycleway"],
            "surface": graph_edge["surface"],
            "bicycle": graph_edge["bicycle"],
            "length": graph_edge["length"],
            "oneway": graph_edge["oneway"],
            "security_highway": graph_edge["security_highway"],
            "security_cycleway": graph_edge["security_cycleway"],
            "score": graph_edge["score"],
            "highway": graph_edge["highway"],
        }
        tooltip = folium.Tooltip(tooltip_data)
        folium.PolyLine(
            locations=edge, color="yellow", tooltip=tooltip, opacity=0.7
        ).add_to(m)

    for i in range(len(route_score) - 1):
        edge = []
        graph_edge = GRAPH.edges[route_score[i], route_score[i + 1], 0]
        for x, y in graph_edge["geometry"].coords:
            edge.append([y, x])
        tooltip_data = {
            "cycleway": graph_edge["cycleway"],
            "surface": graph_edge["surface"],
            "bicycle": graph_edge["bicycle"],
            "length": graph_edge["length"],
            "oneway": graph_edge["oneway"],
            "security_highway": graph_edge["security_highway"],
            "security_cycleway": graph_edge["security_cycleway"],
            "score": graph_edge["score"],
            "highway": graph_edge["highway"],
        }
        tooltip = folium.Tooltip(tooltip_data)
        folium.PolyLine(
            locations=edge, color="green", tooltip=tooltip, opacity=0.7
        ).add_to(m)

    source_node = GRAPH.nodes[node_depart]
    target_node = GRAPH.nodes[node_arrivee]
    folium.Marker(
        location=[source_node["geometry"].y, source_node["geometry"].x],
        popup="source",
    ).add_to(m)
    folium.Marker(
        location=[target_node["geometry"].y, target_node["geometry"].x],
        popup="target",
    ).add_to(m)
    print(len(route_length), len(route_security), len(route_score))
    return {"map": render_map(m)}


app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/templates", StaticFiles(directory="templates"), name="templates")
app.mount("/js", StaticFiles(directory="js"), name="js")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    m = folium.Map(location=[44.841225, -0.580036], zoom_start=12)
    folium_html = render_map(m)
    return templates.TemplateResponse(
        request=request,
        name="map.html",
        context={"map": folium_html},
    )


@app.post("/iti_coordinate")
async def map(request: Request, itineraire_coo: Itineraire_coo):
    print(itineraire_coo)
    return calculate_route(itineraire_coo)


@app.post("/iti_address")
def itineraire(request: Request, itineraire_address: Itineraire_address):
    try:
        coo_depart = get_localisation(itineraire_address.depart)
        coo_arrivee = get_localisation(itineraire_address.destination)
    except ValueError as e:
        return e
    coo_depart = [coo_depart[1], coo_depart[0]]
    coo_arrivee = [coo_arrivee[1], coo_arrivee[0]]
    itineraire_coo = Itineraire_coo(depart=coo_depart, destination=coo_arrivee)
    print(itineraire_coo)
    return calculate_route(itineraire_coo)
