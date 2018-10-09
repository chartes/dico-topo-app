import React from "react";

class PlacenameSearchForm extends React.Component {

    constructor(props) {
        super(props);

        this.handlePlacenameChange = this.handlePlacenameChange.bind(this);
        this.handleOldLabelsChange = this.handleOldLabelsChange.bind(this);
        this.handleLabelChange = this.handleLabelChange.bind(this);
        this.handleDescChange = this.handleDescChange.bind(this);

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

            const api_base_url = "http://localhost:5003/dico-topo/api/1.0";
            let url = "";
            let searched_indexes = "";

            if (params.label) {
                let fields = "label";
                if (params.desc) {
                    fields += ",desc";
                }
                // search on multiple indexes
                if (params["old-labels"]) {
                    searched_indexes = "&search-indexes=placename,placename_old_label";
                    fields += ",text_label_node"
                }
                url = `${api_base_url}/placenames?search[${fields}]=${params.searchedPlacename}${searched_indexes}`;
            } else if (params["old-labels"]) {
                let fields = "text_label_node";
                url = `${api_base_url}/placename-old-labels?search[${fields}]=${params.searchedPlacename}`;
            }

            console.log("search url: ", url);
            if (url) {
                fetch(url)
                .then(res => {
                    if (!res.ok) {
                        throw res;
                    }
                    return res.json();
                })
                .then((result) => {
                    this.setState({
                        ...params,
                        searchResult: result,
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
                                <div className="field">
                                    <p className="control is-expanded has-icons-left">
                                        <input className="input" type="text" placeholder="ex: Abbécourt"
                                               onChange={this.handlePlacenameChange}/>
                                        <span className="icon is-small is-left">
                                          <i className="fas fa-map-marker-alt"></i>
                                        </span>
                                    </p>
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
                                            <input type="checkbox" name="member" value="label" onChange={this.handleLabelChange} defaultChecked={this.state.searchParameters.label}/>
                                               Vedette
                                        </label>
                                        <label className="checkbox">
                                            <input type="checkbox" name="member" value="old-labels" onChange={this.handleOldLabelsChange} defaultChecked={this.state.searchParameters["old-labels"]}/>
                                                Formes anciennes
                                        </label>
                                        <label className="checkbox">
                                            <input type="checkbox" name="member" value="desc" onChange={this.handleDescChange} defaultChecked={this.state.searchParameters.desc}/>
                                                description
                                        </label>
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