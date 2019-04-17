import React from "react";


import  "../../css/capabilities.css"
import "../../css/xcode.css"
import hljs from "highlight.js"

class CapabilityCard extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            examples: {},
            isReady: false
        }
    }

    componentDidMount() {
        if (this.props.data.attributes.examples) {
            var exPromises = [];
            const examples = this.props.data.attributes.examples;

            for (var url in examples){
                exPromises.push(
                    fetch(examples[url]).then(r => {
                        return r.json()
                    })
                    .then(r => {
                        return {url: examples[url], data: r}
                    })
                );
            }
            console.warn(exPromises);

            Promise.all(exPromises).then( r => {
                this.setState({
                    examples: r,
                    isReady: true
                });
                console.warn(this.state);
                document.querySelectorAll('pre code').forEach((block) => {
                    hljs.highlightBlock(block);
                });
            })
        } else {
            this.setState({
                isReady: true
            });
        }
    }

    renderCapability(attributes) {

        const res_attributes = attributes.endpoints.resource.attributes;
        const res_relationships = attributes.endpoints.resource.relationships;

        return <section className="capabilities">
            <header><p>{attributes.description}</p></header>
            <article className="endpoints">

                <div className="resource">
                    <h2 className={"h2 title is-size-5"}>Collection</h2>
                    <div className="url">
                        <span className="tag" style={{"width": "40px", "marginRight": "12px"}}>Url</span>
                        <span><a href={attributes.endpoints.collection.url}
                                 target={"_blank"}>{attributes.endpoints.collection.url}</a></span>
                    </div>
                </div>
                <div className="columns">
                    <div className="column is-two-fifths">
                        <div className="resource">
                            <h2 className={"h2 title is-size-5"}>Resource</h2>
                            <div className="url">
                                <span className="tag" style={{"width": "40px", "marginRight": "12px"}}>Url</span>
                                <span>{attributes.endpoints.resource.url}</span>
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
                                    {res_attributes.map(att => (<tr key={att.name}>
                                        <td>{att.name}</td>
                                        <td>{att.description}</td>
                                    </tr>))}
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
                                    {res_relationships.map(rel => (<tr key={rel.name}>
                                        <td>{rel.name}</td>
                                        <td>{rel.description}</td>
                                        <td>
                                            <a href={"#" + rel.ref}>{rel.type} de type '{rel.ref}'</a></td>
                                    </tr>))}
                                    </tbody>
                                </table>
                            </div>

                        </div>
                    </div>
                    <div className="column">
                        {attributes.examples && this.state.isReady &&
                        <div>
                            <pre>CURL -X {attributes.examples.url}</pre>
                            <pre><code>{this.renderCurlRequest()}</code></pre>
                        </div>
                        }
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

    renderCurlRequest() {
        return JSON.stringify(this.state.examples[0]["data"], null, 2)
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