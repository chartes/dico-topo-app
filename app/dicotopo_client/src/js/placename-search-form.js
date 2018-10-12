import React from "react";

class PlacenameSearchForm extends React.Component {

    constructor(props) {
        super(props);

        this.handlePlacenameChange = this.handlePlacenameChange.bind(this);
        this.handleOldLabelsChange = this.handleOldLabelsChange.bind(this);
        this.handleLabelChange = this.handleLabelChange.bind(this);
        this.handleDescChange = this.handleDescChange.bind(this);
        this.handleOnKeyPress = this.handleOnKeyPress.bind(this);

        this.state = {
            searchParameters: {
                searchedPlacename: null,

                // checkboxes
                label: true,
                "old-labels": false,
                desc: false
            },
            searchResult: null,

            error: null
        };

    }

    componentDidMount() {

    }

    performSearch() {
        const params = this.state.searchParameters;
        if (params.searchedPlacename && params.searchedPlacename.length >= 2) {

            const api_base_url = "/dico-topo/api/1.0";
            //const api_base_url = "http://localhost:5003/dico-topo/api/1.0";

            let urls = [];


            if (params.label || params.desc) {
                let fields = "";
                if (params.label && params.desc) {
                    fields = "label,desc";
                } else if (params.label && !params.desc) {
                    fields = "label";
                } else {
                    fields ="desc";
                }
                urls.push(`${api_base_url}/placenames?search[${fields}]=${params.searchedPlacename}`);
            }
            if (params["old-labels"]) {
                let fields = "text_label_node";
                urls.push(`${api_base_url}/placename-old-labels?search[${fields}]=${params.searchedPlacename}`);
            }

            //clear results
            this.setState({
                ...params,
                searchResult: null,
                error: null
            });
            this.props.onSearch(this.state.searchResult);

            //fetch new results
            let results = [];
            console.log("search urls: ", urls);
            for(let url of urls) {

                if (url) {
                    fetch(url)
                    .then(res => {
                        if (!res.ok) {
                            throw res;
                        }
                        return res.json();
                    })
                    .then((result) => {
                        const oldResult = this.state.searchResult ? this.state.searchResult : [];
                        let newResult = result;
                        //console.log("old result:", oldResult);
                        Array.prototype.push.apply(result, oldResult);
                        //console.log("new result:", newResult);
                        this.setState({
                            ...params,
                            searchResult: newResult,
                            error: null
                        });
                        this.props.onSearch(this.state.searchResult);
                    })
                    .catch(error => {
                        console.log("error while searching placename:", error);
                        this.setState({error: error.statusText});
                    });
                }

            }

        }
    }


    handleLabelChange(e){
        this.setState({
            ...this.state,
            searchParameters : {
                ...this.state.searchParameters,
                label: e.target.checked
            }
        });
    }


    handleOldLabelsChange(e){
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

    handlePlacenameChange(e){
        this.setState({
             ...this.state,
            searchParameters : {
                ...this.state.searchParameters,
                searchedPlacename: e.target.value
            }
        });
    }

    handleOnKeyPress(e) {
        if (e.key === 'Enter'){
            this.handlePlacenameChange(e);
        }
    }

    componentDidUpdate(prevProps, prevState, snapshot) {
        // check if data has changed

        if (this.state.searchParameters !== prevState.searchParameters) {
            this.performSearch();
        }
    }

    render() {
        return (
            <div id="search-form-container">
                <h1 className="is-size-4">Recherche :</h1>
                <div className="columns">
                    <div className="column">
                        <div className="field is-horizontal">
                            <div className="field-label is-normal">
                                <label className="label">Nom de lieu</label>
                            </div>
                            <div className="field-body">
                                <div className="field has-addons">
                                    <div className="control">
                                        <button className="button is-info" onClick={this.performSearch.bind(this)}>
                                           <i className="fas fa-search"></i>
                                        </button>
                                    </div>
                                    <div className="control">
                                        <input className="input" type="text" placeholder="ex: Abbécourt"
                                               onChange={this.handlePlacenameChange}
                                               onKeyPress={this.handleOnKeyPress}/>
                                    </div>
                                </div>
                            </div>
                        </div>

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
                                         {/*
                                        <label className="checkbox">
                                            <input type="checkbox" name="member" value="old-labels" onChange={this.handleOldLabelsChange} defaultChecked={this.state.searchParameters["old-labels"]}/>
                                                Formes anciennes
                                        </label>

                                        <label className="checkbox">
                                            <input type="checkbox" name="member" value="desc" onChange={this.handleDescChange} defaultChecked={this.state.searchParameters.desc}/>
                                                description
                                        </label>
                                        */}
                                    </div>
                                </div>
                            </div>
                        </div>

                    </div>

                    <div className="column"></div>
                </div>
            </div>
        );
    }

}

export default PlacenameSearchForm;