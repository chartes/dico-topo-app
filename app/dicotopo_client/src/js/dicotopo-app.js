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
            searchTableResult: null,
            searchMapResult: null
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

    setSearchPlacenameTableResult(searchTableResult){
        this.setState(prevState => ({
            ...prevState,
            searchTableResult: searchTableResult,
            placenameCardVisibility: false,
            searchResultVisibility: true
        }))
    }

    setSearchPlacenameMapResult(searchMapResult){

        this.updateMarkersOnMap(searchMapResult);

        this.setState(prevState => ({
            ...prevState,
            searchMapResult: searchMapResult,
        }))
    }

    makeMapMarker(resource) {
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

    updateMarkersOnMap(searchMapResult){
        let mapMarkers = [];
        //console.log("=====");
        if (searchMapResult) {
            let commune_ids = [];
            for (let resource of searchMapResult.data) {
                if (resource.attributes.longlat && resource.attributes["localization-insee-code"]) {
                    if (commune_ids.indexOf(resource.attributes["localization-insee-code"]) === -1) {
                        /* add a new marker */
                       mapMarkers.push(this.makeMapMarker(resource));
                       commune_ids.push(resource.attributes["localization-insee-code"]);
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
            <PlacenameSearchForm onSearchTable={this.setSearchPlacenameTableResult.bind(this)}
                                 onSearchMap={this.setSearchPlacenameMapResult.bind(this)}
                                 />
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
        if (!this.state.searchTableResult) {
            return null;
        }
        else {
            return (
                <div style={{display: (this.state.searchResultVisibility ? "block" : "none")}}>
                    <p>{this.state.searchTableResult.meta["total-count"]} résultat(s) - <span style={{color: "#EE8E4A"}}>debug: nbpages {this.state.searchTableResult.meta["nb-pages"]}</span></p>
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
                                this.state.searchTableResult.data.map(res  => (
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