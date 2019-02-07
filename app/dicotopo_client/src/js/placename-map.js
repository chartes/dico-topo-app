import React from "react";

import L from 'leaflet';

import  '../css/GpPluginLeaflet.css';
import * as Gp from '../js/lib/GpPluginLeaflet';

import 'leaflet/dist/leaflet.css';
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

import 'leaflet.markercluster/dist/MarkerCluster.css';
import 'leaflet.markercluster/dist/MarkerCluster.Default.css';
import 'leaflet.markercluster/dist/leaflet.markercluster.js';


/*
function get_related_resource_from_included_list(data, resource_identifiers) {
    if (!Array.isArray(resource_identifiers)) {
        resource_identifiers = [resource_identifiers];
    }
    let resources = [];
    for (let resource_identifier of resource_identifiers) {
        for (let resource of data) {
            if (resource.type === resource_identifier.type && resource.id === resource_identifier.id) {
                resources.push(resource);
                break;
            }
        }
    }
    return resources;
}
*/

class PlacenameMap extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            loaded : false
        };

        if (document.getElementById("debug-mode")){
           this.api_base_url = "http://localhost:5003/dico-topo/api/1.0";
        } else {
           this.api_base_url = "/dico-topo/api/1.0";
        }


    }

    initMap() {
        L.Marker.prototype.options.icon= L.icon({
            iconUrl: icon,
            shadowUrl: iconShadow
        });

        this.map = L.map(
            "map", {
                 preferCanvas : true
             }
        ).setView([48.845, 2.424], 5);

        const lyrOSM = L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png?') ;
        this.map.addLayer(lyrOSM);
        /*
        const lyrOrtho = L.geoportalLayer.WMTS({
            layer: "ORTHOIMAGERY.ORTHOPHOTOS",
        });
        const lyrCassini = L.geoportalLayer.WMTS({
            layer: "GEOGRAPHICALGRIDSYSTEMS.CASSINI",
        });

        this.map.addLayer(lyrCassini);
        this.map.addLayer(lyrOrtho);


        */
        const layerSwitcher = L.geoportalControl.LayerSwitcher({
            layers: [{
                layer: lyrOSM,
                config: {
                    title: "OSM",
                    description: "Couche Open Street Maps"
                }
            }]
        });
        this.map.addControl(layerSwitcher);
        this.markerLayer = L.markerClusterGroup().addTo(this.map);
        this.updateMarkers(this.props.markersData);

        this.setState({loaded: true});
    }

    componentDidMount() {
        this.initMap();

        function addIGNServices()
        {
            this.setState({loaded: false});

            const lyrOrtho = L.geoportalLayer.WMTS({
                layer: "ORTHOIMAGERY.ORTHOPHOTOS",
            });
            const lyrCassini = L.geoportalLayer.WMTS({
                layer: "GEOGRAPHICALGRIDSYSTEMS.CASSINI",
            });

            this.map.addLayer(lyrCassini);
            this.map.addLayer(lyrOrtho);

            this.setState({loaded: true});
        }

        const p = new Promise(function(resolve, reject) {
            resolve(Gp.Services.getConfig({
                apiKey: "4bgxfnc1ufj44pmxpsloxq6j",
                onSuccess: addIGNServices.bind(this)
            }));
        });

    }

    componentDidUpdate({ markersData }) {
      // check if data has changed
      if (this.props.markersData !== markersData) {
        this.updateMarkers(this.props.markersData);
      }
    }

    updateMarkers(markersData) {
        if (this.state.loaded && markersData) {
            const onMarkerClick =  this.props.onMarkerClick;
            const api_url = this.api_base_url;

            this.markerLayer.clearLayers();
            let markers = [];
            for (let m of markersData) {
                let newMarker = L.marker(
                    m.latLng,
                   // { title: m.title }
                );
                newMarker.on('click',function(ev) {

                    fetch(`${api_url}/communes/${m.commune_id}/placename`)
                    .then(res => {
                        if (!res.ok) {
                            throw res;
                        }
                        return res.json();
                    })
                    .then((result) => {
                        onMarkerClick(result.data.id);
                    })
                    .catch(error => {
                        console.log("error while fetching commune:", error);
                        this.setState({error: error.statusText});
                    });

                });
                markers.push(newMarker);
            }
            this.markerLayer.addLayers(markers);
        }
    }

    render() {
        return <div id="map"></div>
    }
}

export default PlacenameMap;