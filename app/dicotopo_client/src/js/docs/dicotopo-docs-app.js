import React from "react";


import "../../css/dicotopo-app.css"


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
       return <div>Hello, I'm the Dicotopo App doc !
           <div>{
               this.state.capabilities.map(capability => (
                   <div key={capability.id}>{capability.id}</div>
               ))
           }
           </div>
       </div>
    }
}

export default DicotopoDocsApp;