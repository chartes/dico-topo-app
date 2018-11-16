import React from "react";


import  "../../css/capabilities.css"


class CapabilityCard extends React.Component {

    constructor(props) {
        super(props);
    }

    componentDidMount() {
    }

    renderCapability(attributes) {

        const res_attributes = attributes.endpoints.resource.attributes;
        const res_relationships = attributes.endpoints.resource.relationships;

        const parameters = attributes.endpoints.collection.parameters;

        return <section className="capabilities">
            <header><p>{attributes.description}</p></header>
            <article className="endpoints">
                <div className="resource">
                    <h2 className={"h2 title is-size-5"}>Resource</h2>
                    <div className="url">
                        <span className="tag">Url</span>
                        <span>{attributes.endpoints.resource.url}</span>
                    </div>
                    <div className="parameters">
                        <span className="tag">Parameters</span>
                    </div>

                    <div className="attributes">
                        <h3 className={"title is-size-6"}>Attributs</h3>
                        <table className="table is-narrow is-stripped">
                            <thead>
                                <tr>
                                    <th>nom</th>
                                    <th>description</th>
                                </tr>
                            </thead>
                            <tbody>
                            {res_attributes.map(att => (<tr key={att.name}><td>{att.name}</td><td>{att.description}</td></tr>))}
                            </tbody>
                        </table>
                    </div>

                     <div className="relations">
                         <h3 className={"title is-size-6"}>Relations</h3>
                         <table className="table is-narrow is-stripped">
                             <thead>
                                 <tr>
                                     <th>nom</th>
                                     <th>description</th>
                                     <th>type</th>
                                 </tr>
                             </thead>
                             <tbody>
                             {res_relationships.map(rel => (<tr key={rel.name}><td>{rel.name}</td><td>{rel.description}</td><td>{rel.type}</td></tr>))}
                             </tbody>
                         </table>
                    </div>

                </div>

                <div className="collection">
                    <h2  className={"h2 title is-size-5"}>Collection</h2>
                    <div className="url">
                        <span className="tag">Url</span>
                        <span><a href={attributes.endpoints.collection.url} target={"_blank"}>{attributes.endpoints.collection.url}</a></span>
                    </div>
                    <div className="parameters">
                        <span className="tag">Parameters</span>
                            <table className="table is-narrow is-stripped">
                            <thead>
                                <tr>
                                    <th>nom</th>
                                    <th>description</th>
                                </tr>
                            </thead>
                            <tbody>
                            {Object.keys(parameters).map(k => (<tr key={k}><td>{k}</td><td>{parameters[k]}</td></tr>))}
                            </tbody>
                        </table>
                    </div>
                </div>

            </article>
        </section>
    }

    renderRelationship(rel) {

    }

    renderMeta() {
        <div></div>
    }

    renderCurlRequest(url) {

    }

    renderUsages(usages) {
        <div></div>
    }

    render() {
        return <article className="">
            <div className="card capability-card">
                <header className="card-header">
                    <h1 className={"title is-size-4"}>{this.props.data.id}</h1>
                </header>
                <div className="card-content">
                    {this.renderCapability(this.props.data.attributes)}
                    {this.renderMeta(this.props.data.meta)}
                    {this.renderUsages(this.props.data.usage)}
                </div>
            </div>
            <div>
            </div>
        </article>

    }
}

export default CapabilityCard;