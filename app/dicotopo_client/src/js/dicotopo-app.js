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
                 commune_id: commune.attributes["insee-code"],
                 title: commune.attributes["NCCENR"],
            }
        }
        return null;
    }

    updateMarkersOnMap(searchResult){
        let mapMarkers = [];
        //console.log("=====");
        if (searchResult && searchResult.included) {

            for (let commune of searchResult.included) {
                if ((commune.type === "commune" || commune.type === "localization-commune") && commune.attributes.longlat) {
                    /* add a new marker */
                    //console.log("make marker: ",  commune.type, newMarker);
                    const newMarker = this.makeMapMarker(commune);
                    if (newMarker){
                        let alreadyMarked = false;
                        // based on commune.insee_code, try to not add duplicate markers
                        for (let m of mapMarkers) {
                            //console.log(newMarker);
                            if (m.commune_id === newMarker.commune_id){
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
                            <th style={{minWidth: "200px"}}>Forme</th>
                            <th>Description</th>
                            <th>Département</th>
                            <th style={{minWidth: "100px"}}>Code INSEE</th>
                            <th style={{minWidth: "120px"}}>Permalien</th>
                        </tr>
                        </thead>
                        <tbody>
                            {
                                this.state.searchResult.data.map(placename  => (
                                    <tr key={placename.id}>
                                        <td>{placename.attributes.label}</td>
                                        <td dangerouslySetInnerHTML={{__html: placename.attributes.desc}}></td>
                                        <td>{placename.attributes.dpt}</td>
                                        <td>{placename.attributes["localization-insee-code"]}</td>
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
                    <PlacenameMap markersData={this.state.mapMarkers} onMarkerClick={this.setPlacenameCard.bind(this)}/>
                    <div className={"columns"}>
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