import React from "react";

import PlacenameMap from './placename-map'

import "../css/dicotopo-app.css"
import PlacenameCard from "./placename-card";



function get_endpoint_url(endpoint_id, id) {
  const url = document.getElementById(endpoint_id).value;
  return url.replace("ID_PLACEHOLDER", id);
}


class DicotopoApp extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            enablePlacenameMap : document.getElementById('enable-placename-map'),
            enablePlacenameCard : document.getElementById('enable-placename-card'),

            mapMarkers : [],
            placenameUrl : document.getElementById('placename-endpoint').value
        };

    }

    componentDidMount() {

       if (this.state.enablePlacenameMap) {
           const url = get_endpoint_url("placename-collection-endpoint") + "?include=commune&page[number]=1&page[size]=500";
           fetch(url)
               .then(res => res.json())
               .then((result) => {
                   let mapMarkers = [];
                   for (let commune of result.included) {
                      if (commune.attributes.longlat) {
                          /* unbox the longlat field */
                          let longlat = commune.attributes.longlat.replace("(", "");
                          longlat = longlat.replace(")", "");
                          longlat = longlat.split(",");
                          let lat = parseFloat(longlat[0].trim());
                          let long = parseFloat(longlat[1].trim());

                          /* add a new marker */
                          mapMarkers.push({
                              latLng: [long, lat],
                              title: commune.attributes.insee_code,
                              placenameId: commune.relationships.placename.data.id
                          });
                      }
                  }

                  this.setState({
                      mapMarkers: mapMarkers
                  })
               },
                   (error) => {

               });
       }

    }

    setPlacenameCard(placenameId) {
        this.setState({
            placenameUrl: get_endpoint_url("placename-endpoint", placenameId)
        })
    }

    renderPlacenameCard() {
      if (this.state.placenameUrl && this.state.placenameUrl.indexOf("ID_PLACEHOLDER") === -1) {
        return <PlacenameCard url={this.state.placenameUrl}/>
      } else {
        return null;
      }
    }


    render() {
        if (this.state.enablePlacenameMap) {
            return (
                <div className={"container is-fluid"}>
                    <div className={"columns"}>
                        <div className={"column"}>
                            <PlacenameMap markersData={this.state.mapMarkers} onMarkerClick={this.setPlacenameCard.bind(this)}/>
                        </div>
                        <div className={"column"}>
                            {this.renderPlacenameCard()}
                        </div>
                    </div>
                </div>
            );
        } else {
            return (
                <div className={"container is-fluid"}>
                         {this.renderPlacenameCard()}
                </div>
            );
        }
    }
}

export default DicotopoApp;