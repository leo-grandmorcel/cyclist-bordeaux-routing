from pyrosm import OSM, get_data
import requests
import folium

SECURITY_BY_CYCLEWAY = {
    "lane": 1,
    "track": 1,
    "separate": 1,
    "opposite": 0.9,
    "opposite_lane": 0.9,
    "opposite_track": 0.9,
    "left": 0.8,
    "share_busway": 0.7,
    "opposite_share_busway": 0.6,
    "shared_lane": 0.5,
    "yes": 0.6,
    "crossing": 0.5,
    "none": 0,
    "no": 0,
    None: 0,
}
SECURITY_BY_HIGHWAY = {
    "cycleway": 1,
    "pedestrian": 0.9,
    "residential": 0.6,
    "living_street": 0.6,
    "tertiary": 0.7,
    "tertiary_link": 0.7,
    "bus_stop": 0.7,
    "track": 0.6,
    "services": 0.7,
    "service": 0.7,
    "path": 0.6,
    "secondary": 0.6,
    "secondary_link": 0.6,
    "unclassified": 0.5,
    "road": 0.5,
    "primary": 0.4,
    "primary_link": 0.4,
}


def get_graph():
    data = OSM(get_data("Bordeaux", directory="data"))
    cycling_nodes, cycling_edges = data.get_network(network_type="cycling", nodes=True)
    cycling_nodes = cycling_nodes[["id", "geometry", "lat", "lon"]]
    cycling_edges = cycling_edges[
        [
            "id",
            "u",
            "v",
            "geometry",
            "highway",
            "cycleway",
            "surface",
            "bicycle",
            "length",
            "oneway",
        ]
    ]
    cycling_edges = cycling_edges[
        ~cycling_edges["highway"].isin(
            ["construction", "trunk_link", "trunk", "footway", "steps", "bridleway"]
        )
    ]
    cycling_edges["security_highway"] = 1 - cycling_edges["highway"].map(
        SECURITY_BY_HIGHWAY
    )
    cycling_edges["security_highway"] = cycling_edges["security_highway"].fillna(0.5)
    cycling_edges["security_cycleway"] = 1 - cycling_edges["cycleway"].map(
        SECURITY_BY_CYCLEWAY
    )
    cycling_edges["security_cycleway"] = cycling_edges["security_cycleway"].fillna(0.1)
    cycling_edges["score"] = cycling_edges["length"] / (
        cycling_edges["security_highway"] + cycling_edges["security_cycleway"]
    )
    graph = data.to_graph(cycling_nodes, cycling_edges, graph_type="networkx")
    return graph


def get_localisation(address):
    response = (
        requests.get(
            f"https://api-adresse.data.gouv.fr/search/?q={address.replace(' ','+')}&lat=44.841225&lon=-0.580036&limit=5"
        )
        .json()
        .get("features")
    )
    try:
        response = response[0].get("geometry").get("coordinates")
    except:
        raise ValueError("Address not found")
    return response


def find_popup_slice(html):
    """
    Find the starting and edning index of popup function
    """

    pattern = "function latLngPop(e)"

    starting_index = html.find(pattern)

    tmp_html = html[starting_index:]

    found = 0
    index = 0
    opening_found = False
    while not opening_found or found > 0:
        if tmp_html[index] == "{":
            found += 1
            opening_found = True
        elif tmp_html[index] == "}":
            found -= 1

        index += 1

    ending_index = starting_index + index

    return starting_index, ending_index


def find_map_variable_name(html):
    pattern = "var map_"

    starting_index = html.find(pattern) + 4
    tmp_html = html[starting_index:]
    ending_index = tmp_html.find(" =") + starting_index

    return html[starting_index:ending_index]


def find_popup_variable_name(html):
    pattern = "var lat_lng"

    starting_index = html.find(pattern) + 4
    tmp_html = html[starting_index:]
    ending_index = tmp_html.find(" =") + starting_index

    return html[starting_index:ending_index]


def custom_code(map_variable_name):
    return """
            // custom code
            var marqueurs = [];
            function latLngPop(e) {
                if (marqueurs.length >= 2){
                    var marqueurASupprimer = marqueurs.shift();
                    marqueurASupprimer.remove();
                }
                var marqueur = L.marker([e.latlng.lat, e.latlng.lng],{}).addTo(%s);
                marqueurs.push(marqueur);
                var boutonItineraire = document.getElementById('boutonItineraire');
                if (!boutonItineraire && marqueurs.length == 2) {
                    boutonItineraire = document.createElement('button');
                    boutonItineraire.id = 'boutonItineraire';
                    boutonItineraire.innerHTML = 'Calculate the route';
                    boutonItineraire.addEventListener('click', function() {
                        getitineraire_coo(marqueurs);
                    });
                    var map_base = document.getElementById('map_base');
                    map_base.appendChild(boutonItineraire);
                }
            }
            // end custom code
    """ % (map_variable_name)


def render_map(m):
    legend_html = """
    <div style="position: absolute;
        left: 8rem;
        margin-top: 1rem;
        padding: 0.5rem;
        border:2px solid grey; 
        z-index:500; 
        font-size:14px;
        border-radius: 1.5rem;
        background-color:white;
        ">&nbsp; <b>Legend :</b><br>
        &nbsp;<i class="fa fa-map-marker fa-2x" style="color:blue"></i> Length &nbsp; <br>
        &nbsp;<i class="fa fa-map-marker fa-2x" style="color:yellow"></i> Security &nbsp; <br>
        &nbsp;<i class="fa fa-map-marker fa-2x" style="color:green"></i> Score &nbsp; 
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))
    folium.LatLngPopup().add_to(m)

    folium_html = m.get_root().render()
    map_variable_name = find_map_variable_name(folium_html)
    pstart, pend = find_popup_slice(folium_html)
    folium_html = (
        folium_html[:pstart] + custom_code(map_variable_name) + folium_html[pend:]
    )

    return folium_html
