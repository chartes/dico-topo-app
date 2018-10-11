import React from "react";

import PlacenameMap from './placename-map'

import "../css/dicotopo-app.css"
import PlacenameCard from "./placename-card";
import PlacenameSearchForm from "./placename-search-form";



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
            placenameUrl : document.getElementById('placename-endpoint').value,
            placenameCardVisibility: false,
            searchResultVisibility: false,
            searchResult: null
        };

    }

    componentDidMount() {

       if (this.state.enablePlacenameMap) {
           //this.updateMarkersOnMap();
       } else {
           this.setState({
               ...this.state,
               placenameCardVisibility: true
           })
       }

    }

    setPlacenameCard(placenameId) {
        this.setState(prevState => ({
            ...prevState,
            placenameUrl: get_endpoint_url("placename-endpoint", placenameId),
            placenameCardVisibility : true,
            searchResultVisibility: false
        }))
    }

    setSearchPlacenameResult(searchResult){

        this.updateMarkersOnMap(searchResult);

        this.setState(prevState => ({
            ...prevState,
            searchResult: searchResult,
            placenameCardVisibility: false,
            searchResultVisibility: true
        }))
    }

    makeMapMarker(commune) {
        if (commune) {
            /* unbox the longlat field */
            let longlat = commune.attributes.longlat.replace("(", "");
            longlat = longlat.replace(")", "");
            longlat = longlat.split(",");
            let lat = parseFloat(longlat[0].trim());
            let long = parseFloat(longlat[1].trim());
            //console.log(commune);
            return {
                 latLng: [long, lat],
                 title: commune.attributes["insee-code"],
                 label: commune.attributes["NCCENR"],
                 placenameId: commune.relationships.placename.data.id
            }
        }
        return null;
    }

    updateMarkersOnMap(searchResult){
        //const url = get_endpoint_url("placename-collection-endpoint") + "?include=commune&page[number]=1&page[size]=500";
        let promises = [];
        let mapMarkers = [];
        //console.log("=====");
        if (searchResult && searchResult.data) {
           for(let p_res of searchResult.data) {
                let url = `${p_res.links.self}?include=commune,linked-commune`;
                //console.log("purl:", url);
                promises.push(
                     fetch(url)
                       .then(res => res.json())
                       .then((result) => {
                           // get the corresponding commune
                           for (let commune of result.included) {
                               if ((commune.type === "commune" || commune.type === "linked-commune") && commune.attributes.longlat) {
                                   /* add a new marker */
                                   //console.log("make marker: ",  commune.type, newMarker);
                                   const newMarker = this.makeMapMarker(commune);
                                   if (newMarker){
                                       let alreadyMarked = false;
                                       // based on commune.insee_code, try to not add duplicate markers
                                       for (let m of mapMarkers) {
                                           //console.log(newMarker);
                                           if (m.title === newMarker.title){
                                               alreadyMarked = true;
                                               break;
                                           }
                                       }
                                       // add the marker
                                       if (!alreadyMarked) {
                                           mapMarkers.push(newMarker);
                                       }
                                   }
                               }
                           }
                       },
                       (error) => {

                       })
                );

            }
        }


        Promise.all(promises).then(values => {
            //console.log("markers", mapMarkers);
            this.setState(prevState => ({
                ...prevState,
                mapMarkers: mapMarkers
            }))
        });

    }

    renderPlacenameCard() {
      if (this.state.placenameUrl && this.state.placenameUrl.indexOf("ID_PLACEHOLDER") === -1) {
        return <PlacenameCard url={this.state.placenameUrl} visible={this.state.placenameCardVisibility}/>
      } else {
        return null;
      }
    }

    renderSearchForm() {
        return (
            <PlacenameSearchForm onSearch={this.setSearchPlacenameResult.bind(this)}/>
        );
    }

    renderSearchResult() {
        if (!this.state.searchResult) {
            return null;
        }
        else {
            return (
                <div style={{display: (this.state.searchResultVisibility ? "block" : "none")}}>
                    <div>{this.state.searchResult.data.length} résultat(s)</div>
                    <table className="table is-fullwidth is-hoverable is-stripped" >
                        <thead>
                        <tr>
                            <th><abbr title="Position">Nom</abbr></th>
                            <th>Description</th>
                            <th><abbr title="Won">Permalien</abbr></th>
                        </tr>
                        </thead>
                        <tbody>
                            {
                                this.state.searchResult.data.map(placename  => (
                                    <tr key={placename.id}>
                                        <td>{placename.attributes.label}</td>
                                        <td dangerouslySetInnerHTML={{__html: placename.attributes.desc}}></td>
                                        <td><a href={"/dico-topo/placenames/"+placename.id} target="_blank">{placename.id}</a></td>
                                    </tr>
                                ))
                            }
                        </tbody>
                    </table>
                </div>
            );
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
                        <div className={"column is-half"}>
                            {this.renderSearchForm()}
                            {this.renderSearchResult()}
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