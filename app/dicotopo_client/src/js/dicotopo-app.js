import React from "react";

import PlacenameMap from './placename-map'

import "../css/dicotopo-app.css"
import PlacenameCard from "./placename-card";
import PlacenameSearchForm from "./placename-search-form";


class DicotopoApp extends React.Component {
    constructor(props) {
        super(props);

        if (document.getElementById("debug-mode")){
           this.api_base_url = "http://localhost:5003/dico-topo/api/1.0";
        } else {
           this.api_base_url = "/dico-topo/api/1.0";
        }

        this.state = {
            enablePlacenameMap : document.getElementById('enable-placename-map'),
            enablePlacenameCard : document.getElementById('enable-placename-card'),

            mapMarkers : [],
            placenameUrl : null,
            placenameCardVisibility: false,
            searchResultVisibility: false,
            searchResult: null
        };
    }

    componentDidMount() {
        if (!this.state.enablePlacenameMap && !this.state.placenameUrl) {
            this.setPlacenameCard(window.location.href.split("/").pop());
        }
    }

    setPlacenameCard(placenameId) {
        this.setState(prevState => ({
            ...prevState,
            placenameUrl: `${this.api_base_url}/placenames/${placenameId}`,
            placenameCardVisibility : true
        }));
        console.log("set placenamecard to:", this.state.placenameUrl);
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

    makeMapMarker(resource) {
        if (resource) {
            /* unbox the longlat field */
            let longlat = resource.attributes.longlat.replace("(", "");
            longlat = longlat.replace(")", "");
            longlat = longlat.split(",");
            let lat = parseFloat(longlat[0].trim());
            let long = parseFloat(longlat[1].trim());
            //console.log(commune);
            return {
                 latLng: [long, lat],
                 commune_id: resource.attributes["localization-insee-code"],
                // title: commune.attributes["NCCENR"],
            }
        }
        return null;
    }

    updateMarkersOnMap(searchResult){
        let mapMarkers = [];
        //console.log("=====");
        if (searchResult) {
            for (let resource of searchResult.data) {
                if (resource.attributes.longlat) {
                    /* add a new marker */
                    //console.log("make marker: ",  commune.type, newMarker);
                    const newMarker = this.makeMapMarker(resource);
                    if (newMarker){
                        let alreadyMarked = false;
                        // based on commune.insee_code, try to not add duplicate markers
                        for (let m of mapMarkers) {
                            //console.log(newMarker);
                            if (m.commune_id === resource.commune_id){
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
        }

        this.setState(prevState => ({
            ...prevState,
            mapMarkers: mapMarkers
        }));
    }

    renderPlacenameCard() {
        if (this.state.placenameUrl === null) {
            return null
        }
        else {
            return <PlacenameCard url={this.state.placenameUrl} visible={this.state.placenameCardVisibility}/>
        }

    }

    renderSearchForm() {
        return (
            <PlacenameSearchForm onSearch={this.setSearchPlacenameResult.bind(this)}/>
        );
    }

    renderPlacenameResult(placename) {
        return   <tr key={placename.id} className={"placename-result-row"}>
                     <td>{placename.attributes["placename-label"]}</td>
                     <td dangerouslySetInnerHTML={{__html: placename.attributes.desc}}></td>
                     <td>{placename.attributes.dpt}</td>
                     <td>{placename.attributes.region}</td>
                     <td><a href={"/dico-topo/placenames/"+placename.id} target="_blank">{placename.id}</a></td>
                 </tr>
    }

    renderOldLabelResult(oldLabel) {
        return   <tr key={oldLabel.id} className={"old-label-result-row"}>
                     <td dangerouslySetInnerHTML={{__html: oldLabel.attributes["rich-label"]}}></td>
                     <td>Forme ancienne de <a href={"/dico-topo/placenames/"+oldLabel.attributes["placename-id"]} target="_blank" dangerouslySetInnerHTML={{__html: oldLabel.attributes["placename-label"]}}></a></td>
                     <td>{oldLabel.attributes.dpt}</td>
                     <td>{oldLabel.attributes.region}</td>
                     <td><a href={"/dico-topo/placenames/"+oldLabel.attributes["placename-id"]} target="_blank">{oldLabel.attributes["placename-id"]}</a></td>
                 </tr>
    }

    renderSearchResult() {
        if (!this.state.searchResult) {
            return null;
        }
        else {
            return (
                <div style={{display: (this.state.searchResultVisibility ? "block" : "none")}}>
                    <p>{this.state.searchResult.meta["total-count"]} résultat(s)</p>
                    <table className="table is-fullwidth is-hoverable is-stripped" >
                        <thead>
                        <tr>
                            <th style={{width: "260px"}}>Forme</th>
                            <th style={{minWidth: "480px"}}>Description</th>
                            <th>Département</th>
                            <th style={{minWidth: "160px"}}>Région</th>
                            <th style={{minWidth: "140px"}}>Permalien</th>
                        </tr>
                        </thead>
                        <tbody>
                            {
                                this.state.searchResult.data.map(res  => (
                                    res.type === "placename" ? this.renderPlacenameResult(res) : this.renderOldLabelResult(res)
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
                <div >
                    <PlacenameMap markersData={this.state.mapMarkers} onMarkerClick={this.setPlacenameCard.bind(this)}/>
                    <div id="data-container" className={"columns"}>
                        <div className={"column"}>
                            {this.renderSearchForm()}
                            {this.renderSearchResult()}
                        </div>
                        <div className={"column is-two-fifths"} style={{display: (this.state.placenameCardVisibility ? "block" : "none")}}>
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