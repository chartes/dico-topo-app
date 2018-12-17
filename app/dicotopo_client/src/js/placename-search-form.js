import React from "react";

import getUrlParameter from "./lib/utils";


class PlacenameSearchForm extends React.Component {

    constructor(props) {
        super(props);

        this.handlePlacenameChange = this.handlePlacenameChange.bind(this);
        this.handleOldLabelsChange = this.handleOldLabelsChange.bind(this);
        this.handleLabelChange = this.handleLabelChange.bind(this);
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
                pageSize: 25,
                currentPageNumber: 1,
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
        console.log("search form did mount")
    }

    componentDidUpdate(prevProps, prevState) {
        // check if data has changed
        if (this.state.searchParameters.currentPageNumber !== prevState.searchParameters.currentPageNumber ||
            this.state.searchParameters.searchedPlacename !== prevState.searchParameters.searchedPlacename) {
            console.log(this.state, prevState);
            console.log("search !")

            // do not search map if the placename didnt change
            const searchMap = this.state.searchParameters.searchedPlacename !== prevState.searchParameters.searchedPlacename;

            this.performSearch(true, searchMap);
        }
    }

    performTableSearch() {
        let urls = [];
        const pm = this.state.searchParameters;

        const pageNumber = pm.currentPageNumber;

        urls.push(`${this.api_base_url}/search?index=placename_old_label&query=${pm.searchedPlacename}&facade=search&page[size]=${pm.pageSize}&page[number]=${pageNumber}`);
        urls.push(`${this.api_base_url}/search?index=placename&query=${pm.searchedPlacename}&facade=search&page[size]=${pm.pageSize}&page[number]=${pageNumber}`);

        const nb_urls = urls.length;

        //clear results
        this.setState({
            ...this.state.searchParameters,
            searchTableResult: {
                data: [],
                meta: {
                    "total-count": 0,
                    "nb-pages": 0
                },
                showPagination: false
            },
            error: null
        });

        this.props.onSearchTable(this.state.searchTableResult);

        let url_idx = 0;
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
                    console.log("nbPages:", nbPages);

                    this.setState({
                        ...this.state.searchParameters,
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
                    url_idx += 1;
                    if (url_idx === nb_urls) {
                        this.setState({
                            ...this.state.searchParameters,
                            showPagination: true
                        });
                    }
                })
                .catch(error => {
                    console.log("error while searching placename:", error);
                    document.getElementById("search-button").classList.remove("is-loading");
                    this.setState({error: error.statusText});
                });
            }
        }
    }

    performMapSearch() {
        let urls = [];
        const pm = this.state.searchParameters;
        urls.push(`${this.api_base_url}/search?index=placename_old_label&query=${pm.searchedPlacename}&facade=map&page[size]=2000`);
        urls.push(`${this.api_base_url}/search?index=placename&query=${pm.searchedPlacename}&facade=map&page[size]=2000`);
        //clear results
        this.setState({
            ...pm,
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
                        ...pm,
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

    performSearch(searchTable=true, searchMap=true) {
        const params = this.state.searchParameters;
        if (params.searchedPlacename && params.searchedPlacename.length >= 3) {

            document.getElementById("search-button").classList.remove("is-loading");
            if (searchTable) {
                this.performTableSearch();
            }
            if (searchMap) {
               this.performMapSearch();
            }
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

    handlePlacenameChange(){
        this.setState({
            ...this.state,
            searchParameters : {
                ...this.state.searchParameters,
                searchedPlacename: document.getElementById("placenameInput").value,
                currentPageNumber: 1
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

    goToTablePage(num) {
        this.setState({
            ...this.state,
            searchParameters : {
                ...this.state.searchParameters,
                currentPageNumber: num
            }
        });
    }

    renderSearchPagination() {
        if (!this.state.showPagination){
            return <div></div>
        }
        const result = this.state.searchTableResult;
        const nbPages = result.meta["nb-pages"];

        let prevPage = this.state.currentPageNumber - 1;
        let currPage = this.state.currentPageNumber;
        let nextPage = this.state.currentPageNumber +1;

        const stylePageLink = num => num === this.state.currentPageNumber ? "is-medium" : " is-outlined";

        const makeLink = (num, lbl) => <span className={"button is-link " + stylePageLink(num)} onClick={() => this.goToTablePage(num)}>{lbl}</span>;

        if (currPage === 1 || currPage === nbPages) {
            currPage = Math.max(1, Math.ceil(nbPages * 0.5));
            prevPage = currPage - 1;
            nextPage = currPage + 1;
        }

        return <div className="buttons are-normal pagination-links">
            {makeLink(1, 1)}
            <span className={"dotdot"}>...</span>
            {prevPage > 1 ? makeLink(prevPage, prevPage) : ""}
            {currPage > 1 && currPage < nbPages ? makeLink(currPage, currPage) : ""}
            {nextPage < nbPages ? makeLink(nextPage, nextPage): ""}
            <span className={"dotdot"}>...</span>
            {makeLink(nbPages, nbPages)}
        </div>

    }


    render() {
        return (
            <div>
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
                                        </div>
                                    </div>
                                </div>
                            </div>
                            */}

                        </div>
                        <div className="column"></div>
                    </div>
                </div>
                <div id="pagination">
                    {this.renderSearchPagination()}
                </div>
            </div>
        );
    }

}

export default PlacenameSearchForm;