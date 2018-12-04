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
      this.updateCard(this.props.url, this.props.data);
  }

  componentDidUpdate({ url, data }) {
      // check if data has changed
      if (this.props.url !== url || this.props.data !== data) {
        this.updateCard(this.props.url, this.props.data);
      }
  }

  updateCard(placename_url, data=null) {
      this.setState({
          ...this.state,
          isLoaded: false
      });

      if (data !== null) {
          this.setState({
              title: data.attributes.label,
              placenameId: data.attributes.id,
              url: data.links.self,
              numStartPage: data.attributes["num-start-page"],
              description: data.attributes.desc,
              comment: data.attributes.comment,
              oldLabels: data.included ? data.included.filter((res) => res.type === "placename-old-label") : [],
              linkedPlacenames:  data.included ? data.included.filter((res) => res.type === "placename") : [],
              error: null,
              isLoaded: true
          });
      }
      else {
          fetch(placename_url + "?include=old-labels,linked-placenames&without-relationships")
            .then(res => {
                if (!res.ok) {
                    throw res;
                }
                return res.json();
            })
            .then((result) => {
                this.setState({
                    title: result.data.attributes.label,
                    placenameId: result.data.id,
                    url: result.links.self,
                    numStartPage: result.data.attributes["num-start-page"],
                    description: result.data.attributes.desc,
                    comment: result.data.attributes.comment,

                    oldLabels: result.included.filter((res) => res.type === "placename-old-label"),
                    linkedPlacenames: result.included.filter((res) => res.type === "placename"),

                    error: null,
                    isLoaded: true
                });
            })
            .catch(error => {
                console.log("error while fetching placename:", error);
                this.setState({isLoaded : true, error: error.statusText, ...this.state});
            });
      }
  }

  renderTitle() {
      return(
          <div id="placename-card-header-title" className="card-header-title has-text-grey-dark is-size-4"
             dangerouslySetInnerHTML={{__html:`${this.state.title}`}}>
          </div>
      )
  }

  renderDescription(compact=false) {
      if (!this.state.description)
          return null;
      else {
          if (compact) {
              return <div dangerouslySetInnerHTML={{__html: this.state.description}}></div>;
          }
          else {
              return  (
                  <div id="placename-description" className="content">
                      <u className="has-text-grey-light">Description :</u>
                      <p dangerouslySetInnerHTML={{__html: this.state.description}}></p>
                  </div>
              )
          }
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

  renderAttribute(obj, key) {
    return  obj.attributes[key] ? obj.attributes[key] : "" ;
  }


  renderOldLabels() {
      if (this.state.oldLabels.length === 0) {
          return null;
      }
      else {
          let encapsulate_ref = (ref) => ref ? `(${ref})` : "";
          const comma = (oldLabel) => oldLabel.length > 0 ? "," : "";

          return (
              <div id="placename-old-labels" className="content">
                  <u className="has-text-grey-light">Formes anciennes :</u>
                  <ul>
                    {this.state.oldLabels.map(oldLabel => (
                      <li key={oldLabel.id}
                          dangerouslySetInnerHTML={{
                        __html: `
                          ${this.renderAttribute(oldLabel, "rich-label")}${comma(oldLabel)} ${this.renderAttribute(oldLabel, "rich-date")}
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
              <PlacenameCard key={placename.id} url={placename.links.self} data={placename} compact={true} visible={this.props.visible}/>
          ))
      }
  }

  renderFullCard() {
      if (this.state.isLoaded) {
          return (
              <article className={this.props.visible ? "" : "is-invisible"}>
                  <div id="placename-card"
                       className="card">
                      <header className="card-header">
                          {this.renderTitle()}
                          <div className={"placename-permalink is-pulled-right"}>
                              <div className="placename-permalink-label">permalien :</div>
                              <a href={"/dico-topo/placenames/" + this.state.placenameId}
                                 target="_blank">{this.state.placenameId}</a>
                          </div>
                      </header>
                      <div className="card-content">
                          {this.renderDescription()}
                          {this.renderComment()}
                          {this.renderOldLabels()}
                      </div>
                  </div>
                  <div>
                      {this.renderLinkedPlacenames()}
                  </div>
              </article>
          );
      } else {
          return <div className="is-disabled">Chargement <div className="button is-loading is-white" style={{width: "20px", height: "20px"}}></div></div>
      }
  }

  renderCompactCard() {
      return (
          <article>
              <div id="placename-card" className={"card " + (this.state.isLoaded && this.props.visible ? "" : "is-invisible")}>
                  <div className="card-header" style={{paddingTop: "0.5em", paddingBottom: "0.5em"}}>
                      <div id="placename-card-header-title" className="card-header-title has-text-grey-dark is-size-6"
                            dangerouslySetInnerHTML={{
                                __html:`${this.state.title}, <span style="font-weight: normal; padding-left: 0.5em">${this.state.description}</span>`
                            }}>
                      </div>
                      <div className={"placename-permalink is-pulled-right"}>
                          <a  href={"/dico-topo/placenames/"+this.state.placenameId} target="_blank">{this.state.placenameId}</a>
                      </div>
                  </div>

              </div>
          </article>
      );
  }

  render () {

      if (this.state.error) {
          return <div className={"message is-danger"}>{this.state.error}</div>
      }
      if (this.props.compact) {
          return this.renderCompactCard();
      }
      else {
          return this.renderFullCard();
      }
  }
}

export default PlacenameCard;