import React from "react";


import "../../css/dicotopo-app.css"
import CapabilityCard from './capability-card'


const COLLECTIONS_PARAMETERS = {
    "filter": "filter[field_name]=searched_value",
    "sort": "sort=field1,field2. Le tri respecte l'ordre des champs. Utiliser - pour effectuer un tri descendant",
    "page": "page[number]=3&page[size]=10. La pagination nécessite page[number], page[size] ou les deux paramètres en même temps. La taille ne peut pas excéder la limite inscrite dans la facade correspondante. La pagination produit des liens de navigation prev,next,self,first,last dans tous les cas où cela a du sens.",
    "include": "include=relation1,relation2. Le document retourné incluera les ressources liées à la présente ressource. Il n'est pas possible d'inclure une relation indirecte (ex: model.relation1.relation2)",
    "without-relationships": "Ce paramètre n'a pas de valeur. Sa seule présence dans l'URL permet d'obtenir une version allégée du document (les relations ne sont pas incluses dans la réponse)."
};

const RES_PARAMETERS = {
    "include": "include=relation1,relation2. Le document retourné incluera les ressources liées à la présente ressource. Il n'est pas possible d'inclure une relation indirecte (ex: model.relation1.relation2)",
    "without-relationships": "Ce paramètre n'a pas de valeur. Sa seule présence dans l'URL permet d'obtenir une version allégée du document (les relations ne sont pas incluses dans la réponse)."
};


class DicotopoDocsApp extends React.Component {
    constructor(props) {
        super(props);

        if (document.getElementById("debug-mode")){
           this.api_base_url = "http://localhost:5003/dico-topo/api/1.0";
        } else {
           this.api_base_url = "/dico-topo/api/1.0";
        }

        this.state = {
            capabilities : []
        }
    }

    componentDidMount() {
         const api_url = this.api_base_url;
         fetch(`${api_url}?capabilities`)
              .then(res => {
                  if (!res.ok) {
                      throw res;
                  }
                  return res.json();
              })
              .then((result) => {
                  this.setState(prevState => ({
                      ...prevState,
                      capabilities: result.data
                  }));
              })
              .catch(error => {
                  console.log("error while fetching capabilites:", error);
                  this.setState({error: error.statusText});
              });
    }


    render() {
        return  <div>
            <aside id="docs-aside">
                <div id="docs-services">
                    <header>
                        <h1 className="title">Services</h1>
                    </header>
                    <ul>{
                        this.state.capabilities.filter(c => c.type === "feature").map(capability => (
                            <li key={capability.id}><a href={"#" + capability.id}>{capability.id}</a></li>
                        ))
                    }
                    </ul>
                </div>
                <div id="docs-endpoints">
                    <header>
                        <h1 className="title">Resources</h1>
                    </header>
                    <ul>{
                    this.state.capabilities.filter(c => c.type === "resource").map(capability => (
                        <li key={capability.id}><a href={"#"+capability.id}>{capability.id}</a></li>
                    ))
                    }
                    </ul>
                </div>
            </aside>
            <div id="docs-main">
                <h1 className="title">Documentation de l'API Dicotopo (en cours de rédaction)</h1>
                <img src={"/dico-topo/static/images/json-api-logo-300x113.png"}/>
                <p>
                    La présente API a été conçue conformément à la spécification <a href="https://jsonapi.org/format/" target="_blank">json:api 1.0</a>.
                </p>
                <p> Les resources sont disponibles en HTTPS via la méthode GET
                </p>
                <h2 className="title">Services</h2>{
                    this.state.capabilities.filter(c => c.type === "feature").map(feat => (
                        <section id={feat.id} key={feat.id} className="capabilities">
                            <article className="card capability-card">
                                <header className="card-header">
                                    <h1 className="title is-size-4">{feat.attributes.title}</h1>
                                </header>
                                <div className="card-content">
                                    <p>{feat.attributes.content}</p>
                                    <table className="table is-narrow is-stripped">
                                        <thead>
                                        <tr>
                                            <th>description</th>
                                            <th>URL</th>
                                        </tr>
                                        </thead>
                                        <tbody>
                                        {feat.attributes.examples.map(ex => (<tr key={ex.content}>
                                            <td>{ex.description}</td>
                                            <td><a href={ex.content}>{ex.content}</a></td>
                                        </tr>))}
                                        </tbody>
                                    </table>
                                </div>
                            </article>
                        </section>
                    ))
                }
                <h2 className="title">Ressources</h2>
                <article className="card capability-card">
                <div className="card-content parameters">
                    <span className="tag">Paramètres GET disponibles pour les collections</span>
                    <table className="table is-narrow is-stripped">
                        <thead>
                        <tr>
                            <th style={{"width": "200px"}}>nom</th>
                            <th>description</th>
                        </tr>
                        </thead>
                        <tbody>
                        {Object.keys(COLLECTIONS_PARAMETERS).map(k => (<tr key={k}>
                            <td>{k}</td>
                            <td>{COLLECTIONS_PARAMETERS[k]}</td>
                        </tr>))}
                        </tbody>
                    </table>
                    <span className="tag">Paramètres GET disponibles pour les resources</span>
                    <table className="table is-narrow is-stripped">
                        <thead>
                        <tr>
                            <th style={{"width": "200px"}}>nom</th>
                            <th>description</th>
                        </tr>
                        </thead>
                        <tbody>
                        {Object.keys(RES_PARAMETERS).map(k => (<tr key={k}>
                            <td>{k}</td>
                            <td>{RES_PARAMETERS[k]}</td>
                        </tr>))}
                        </tbody>
                    </table>
                </div>
                </article>

                <div className="">{
                   this.state.capabilities.filter(c => c.type === "resource").map(capability => (
                       <div id={capability.id} key={capability.id}><CapabilityCard data={capability}/></div>
                   ))
                }
                </div>
           </div>
       </div>
    }
}

export default DicotopoDocsApp;