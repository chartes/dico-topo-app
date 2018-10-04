import React from "react";

import L from 'leaflet';

import  '../css/GpPluginLeaflet.css';
import  '../js/lib/GpPluginLeaflet';

import 'leaflet/dist/leaflet.css';

import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

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

        };

    }

    componentDidMount() {
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

       this.markerLayer = L.layerGroup().addTo(this.map);
       this.updateMarkers(this.props.markersData);
    }

    componentDidUpdate({ markersData }) {
      // check if data has changed
      if (this.props.markersData !== markersData) {
        this.updateMarkers(this.props.markersData);
      }
    }

    updateMarkers(markersData) {
        const onMarkerClick =  this.props.onMarkerClick;
        if (markersData) {
            this.markerLayer.clearLayers();
            for (let m of markersData) {
                let newMarker = L.marker(
                    m.latLng,
                    { title: m.title }
                );
                newMarker.on('click',function(ev) {
                   onMarkerClick(m.placenameId);
                });
                newMarker.addTo(this.markerLayer);
            }
        }
    }

    render() {
        return <div id="map"></div>
    }
}

export default PlacenameMap;