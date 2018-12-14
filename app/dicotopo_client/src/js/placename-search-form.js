import React from "react";


function getUrlParameter(url, paramName) {
    paramName = paramName.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
    var regex = new RegExp('[\\?&]' + paramName + '=([^&#]*)');
    var results = regex.exec(url);
    return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
}

class PlacenameSearchForm extends React.Component {

    constructor(props) {
        super(props);

        this.handlePlacenameChange = this.handlePlacenameChange.bind(this);
        this.handleOldLabelsChange = this.handleOldLabelsChange.bind(this);
        this.handleLabelChange = this.handleLabelChange.bind(this);
        this.handleDescChange = this.handleDescChange.bind(this);
        this.handleOnKeyPress = this.handleOnKeyPress.bind(this);
        this.handleOnSearchClick = this.handleOnSearchClick.bind(this);

        if (document.getElementById("debug-mode")){
           this.api_base_url = "http://localhost:5003/dico-topo/api/1.0";
        } else {
           this.api_base_url = "/dico-topo/api/1.0";
        }

        this.state = {
            searchParameters: {
                searchedPlacename: null,

                // checkboxes
                label: true,
                "old-labels": true,
                desc: false
            },
            searchTableResult: {
                data: [],
                meta: {
                    "total-count": 0,
                    "nb-pages": 0
                }
            },
            searchMapResult: {
                data: []
            },

            error: null
        };

    }

    componentDidMount() {

    }

    performTableSearch(params, placename) {
        let urls = [];
        urls.push(`${this.api_base_url}/search?index=placename_old_label&query=${placename}&facade=search&page[size]=10`);
        urls.push(`${this.api_base_url}/search?index=placename&query=${placename}&facade=search&page[size]=10`);
        //clear results
        this.setState({
            ...params,
            searchTableResult: {
                data: [],
                meta: {
                    "total-count": 0,
                    "nb-pages": 0
                }
            },
            error: null
        });
        this.props.onSearchTable(this.state.searchTableResult);

        for (let url of urls) {
            //fetch new results
            console.log("search url: ", url);
            if (url) {
                document.getElementById("search-button").classList.add("is-loading");
                fetch(url)
                .then(res => {
                    if (!res.ok) {
                        throw res;
                    }
                    return res.json();
                })
                .then((result) => {
                    // extend the list
                    let newData = result.data;
                    Array.prototype.push.apply(newData, this.state.searchTableResult.data);

                    // compute the number of page for the pagination
                    let nbPages = getUrlParameter(result.links.last, "page%5Bnumber%5D");
                    console.log(nbPages);

                    this.setState({
                        ...params,
                        searchTableResult: {
                            data: newData,
                            meta: {
                                "total-count":   this.state.searchTableResult.meta["total-count"] + result.meta["total-count"],
                                "nb-pages": Math.max(this.state.searchTableResult.meta["nb-pages"], nbPages)
                            }
                        },
                        error: null
                    });

                    this.props.onSearchTable(this.state.searchTableResult);
                    document.getElementById("search-button").classList.remove("is-loading");
                })
                .catch(error => {
                    console.log("error while searching placename:", error);
                    document.getElementById("search-button").classList.remove("is-loading");
                    this.setState({error: error.statusText});
                });
            }
        }
    }


    performMapSearch(params, placename) {
        let urls = [];
        urls.push(`${this.api_base_url}/search?index=placename_old_label&query=${placename}&facade=map&page[size]=2000`);
        urls.push(`${this.api_base_url}/search?index=placename&query=${placename}&facade=map&page[size]=2000`);
        //clear results
        this.setState({
            ...params,
            searchMapResult: {
                data: [],
            },
            error: null
        });
        this.props.onSearchMap(this.state.searchMapResult);

        const process = (url) => {
            if (url) {
                fetch(url)
                .then(res => {
                    if (!res.ok) {
                        throw res;
                    }
                    return res.json();
                })
                .then((result) => {
                    // extend the list
                    let newData = result.data;
                    Array.prototype.push.apply(newData, this.state.searchMapResult.data);

                    this.setState({
                        ...params,
                        searchMapResult: {
                            data: newData,
                        },
                        error: null
                    });
                    this.props.onSearchMap(this.state.searchMapResult);
                    return process(result.links.next);
                })
                .catch(error => {
                    console.log("error while searching placename:", error);
                    document.getElementById("search-button").classList.remove("is-loading");
                    this.setState({error: error.statusText});
                });
            } else {
                document.getElementById("search-button").classList.remove("is-loading");
            }
        };

        for (let url of urls) {
            //fetch new results
            console.log("search map url: ", url);
            if (url) {
                document.getElementById("search-button").classList.add("is-loading");
                process(url);
            }
        }
    }

    performSearch() {
        const params = this.state.searchParameters;
        if (params.searchedPlacename && params.searchedPlacename.length >= 3) {

            document.getElementById("search-button").classList.remove("is-loading");

            this.performTableSearch(params, params.searchedPlacename);
            this.performMapSearch(params, params.searchedPlacename);
        }
    }


    handleLabelChange(e){
        /*
            when the state of the Label checkbox changes
        */
        this.setState({
            ...this.state,
            searchParameters : {
                ...this.state.searchParameters,
                label: e.target.checked
            }
        });
    }


    handleOldLabelsChange(e){
        /*
            when the state of the OldLabel checkbox changes
        */
        this.setState({
            ...this.state,
            searchParameters : {
                ...this.state.searchParameters,
                "old-labels": e.target.checked
            }
        });
    }

    handleDescChange(e){
        this.setState({
            ...this.state,
            searchParameters : {
                ...this.state.searchParameters,
                desc: e.target.checked
            }
        });
    }

    handlePlacenameChange(){
        this.setState({
            ...this.state,
            searchParameters : {
                ...this.state.searchParameters,
                searchedPlacename: document.getElementById("placenameInput").value
            }
        });
    }

    handleOnKeyPress(e) {
        /*
            When the user press Enter in the placename search box
        */
        if (e.key === 'Enter'){
            this.handlePlacenameChange();
        }
    }

    handleOnSearchClick() {
        this.handlePlacenameChange();
    }

    componentDidUpdate(prevProps, prevState) {
        // check if data has changed
        if (this.state.searchParameters !== prevState.searchParameters) {
            this.performSearch();
        }
    }

    render() {
        return (
            <div id="search-form-container">

                <div className="columns">
                    <div className="column">
                        <div className="field is-horizontal">
                            <div className="field-body">
                                <div className="field has-addons">
                                    <div className="control">
                                        <button id="search-button" className="button is-info" onClick={this.handleOnSearchClick}>
                                           <i className="fas fa-search"></i>
                                        </button>
                                    </div>
                                    <div className="control">
                                        <input id="placenameInput" className="input" type="text" placeholder="ex: Abancourt"
                                               onKeyPress={this.handleOnKeyPress}/>
                                    </div>
                                </div>
                            </div>
                        </div>
                         {/*
                        <div className="field is-horizontal">
                            <div className="field-label">
                                <label className="label">Inclure</label>
                            </div>
                            <div className="field-body">
                                <div className="field">
                                    <div className="control">

                                        <label className="checkbox">
                                            <input type="checkbox" name="member" value="label"
                                                   onChange={this.handleLabelChange}
                                                   defaultChecked={this.state.searchParameters.label}/>
                                               Vedette
                                        </label>

                                        <label className="checkbox">
                                            <input type="checkbox" name="member" value="old-labels" onChange={this.handleOldLabelsChange} defaultChecked={this.state.searchParameters["old-labels"]}/>
                                                Formes anciennes
                                            <span id="old-label-legend"></span>
                                        </label>

                                        <label className="checkbox">
                                            <input type="checkbox" name="member" value="desc" onChange={this.handleDescChange} defaultChecked={this.state.searchParameters.desc}/>
                                                description
                                        </label>

                                    </div>
                                </div>
                            </div>
                        </div>
                        */}

                    </div>

                    <div className="column"></div>
                </div>
            </div>
        );
    }

}

export default PlacenameSearchForm;