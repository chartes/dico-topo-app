import React from "react";

import  "../css/placename.css"


class PlacenameCard extends React.Component {

  constructor(props) {
      super(props);
      this.state = {
          title: null,
          placenameId: null,
          url: null,
          description: null,
          comment: null,
          numStartPage: null,

          oldLabels: [],
          linkedPlacenames: [],

          isLoaded: false,
          error: null
      };

  }

  componentDidMount() {
      this.updateCard(this.props.url);
  }

  componentDidUpdate({ url }) {
      // check if data has changed
      if (this.props.url !== url) {
        this.updateCard(this.props.url);
      }
  }

  updateCard(placename_url) {
      fetch(placename_url + "?include=old-labels,linked-placenames")
          .then(res => {
              if (!res.ok) {
                  throw res;
              }
              return res.json();
          })
          .then((result) =>
              this.setState({
                  title: result.data.attributes.label,
                  placenameId: result.data.attributes.placename_id,
                  url: result.links.self,
                  numStartPage: result.data.attributes["num-start-page"],
                  description: result.data.attributes.desc,
                  comment: result.data.attributes.comment,

                  oldLabels: result.included.filter((res) => res.type === "placename-old-label"),
                  linkedPlacenames: result.included.filter((res) => res.type === "placename"),

                  error: null,
                  isLoaded: true
              })
          )
          .catch(error => {
              console.log("error while fetching placename:", error);
              this.setState({isLoaded : true, error: error.statusText});
          });
  }

  renderTitle() {
      return(
          <div id="placename-card-header-title" className="card-header-title is-size-5 has-text-grey-dark"
             dangerouslySetInnerHTML={{__html:`${this.state.title}`}}>
          </div>
      )
  }

  renderDescription() {
      if (!this.state.description)
          return null;
      else {
          return  (
              <div id="placename-description" className="content">
                  <u className="has-text-grey-light">Description :</u>
                  <p dangerouslySetInnerHTML={{__html: this.state.description}}></p>
              </div>
          )
      }
  }

  renderComment() {
      if (!this.state.comment)
          return null;
      else {
          return (
              <div id="placename-commentaire" className="content">
                  <u className="has-text-grey-light">Commentaire :</u>
                  <p dangerouslySetInnerHTML={{__html: this.state.comment}}></p>
              </div>
          )
      }
  }

  renderOldLabels() {
      if (this.state.oldLabels.length === 0) {
          return null;
      }
      else {
          let encapsulate_ref = (ref) => ref ? `(${ref})` : "";

          return (
              <div id="placename-old-labels" className="content">
                  <u className="has-text-grey-light">Noms anciens :</u>
                  <ul>
                    {this.state.oldLabels.map(oldLabel => (
                      <li key={oldLabel.id}
                          dangerouslySetInnerHTML={{
                        __html: `
                          ${oldLabel.attributes["rich-label"]}, ${oldLabel.attributes["rich-date"]}
                          ${encapsulate_ref(oldLabel.attributes["rich-reference"])}
                        `
                      }}>
                      </li>
                    ))}
                  </ul>
              </div>
          )
      }
  }
  renderLinkedPlacenames() {
      if (this.state.linkedPlacenames.length === 0) {
          return null;
      } else {
          return this.state.linkedPlacenames.map(placename => (
              <div key={placename.id} className="placename-compact-card">
                  <div className="card">
                      <div className="card-header">
                          <p className="card-header-title">
                              <span className="has-text-grey-dark">{placename.attributes.label},</span>
                              <span style={{fontWeight: "normal"}} dangerouslySetInnerHTML={{
                                  __html: placename.attributes.desc
                              }}></span>
                          </p>
                      </div>
                  </div>
              </div>)
          )
      }
  }

  render () {

      if(this.state.error) {
          return <div className={"message is-danger"}>{this.state.error}</div>
      }

      let invisible_classname = "";
      if(!this.state.isLoaded) {
        invisible_classname = "is-invisible"
      }

      return (
          <div>
              <div id="placename-card" className={"card " + invisible_classname}>
                  <div className="card-header">
                      {this.renderTitle()}
                      <a className={"is-pulled-right"} href={"/dico-topo/placenames/"+this.state.placenameId}>{this.state.placenameId}</a>
                  </div>
                  <div className="card-content">
                      {this.state.numStartPage}
                      {this.renderDescription()}
                      {this.renderComment()}
                      {this.renderOldLabels()}
                  </div>
                  <div className="card-footer"></div>
              </div>
              <div>
                  {this.renderLinkedPlacenames()}
              </div>
          </div>
      );
  }
}

export default PlacenameCard;