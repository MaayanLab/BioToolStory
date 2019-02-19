import React from 'react'
import IconButton from '../../components/IconButton';
import { ShowMeta } from '../../components/ShowMeta';
import { fetch_meta_post } from '../../util/fetch/meta';
import { Label } from '../../components/Label';
import M from "materialize-css";
import { call } from '../../util/call';

export const primary_resources = [
  'CREEDS',
  'ARCHS4',
  'KEGG',
  'GTEx',
  'ENCODE',
  'HPO',
  'CCLE',
  'Allen Brain Atlas',
  'Achilles',
]

export const primary_two_tailed_resources = [
  'CMAP'
]

export const renamed = {
  'Human Phenotype Ontology': 'HPO',
  'MGI Mammalian Phenotype': 'MGI-MP',
  'Cancer Cell Line Encyclopedia': 'CCLE',
  'NCI': 'NCI Pathways',
  'Disease Signatures': 'CREEDS',
  'Single Drug Perturbations': 'CREEDS',
  'Single Gene Perturbations': 'CREEDS',
  'clueio': 'CMAP',
  'GEO': 'CREEDS',
  'TRANSFAC AND JASPAR': 'TRANSFAC & JASPAR',
  'ENCODE/ChEA': 'ENCODE',
  'Gene Ontology Consortium': 'Gene Ontology',
  'PubMed': 'Enrichr',
}

export const iconOf = {
  'CREEDS': 'static/images/creeds.png',
  'CMAP': 'static/images/clueio.ico',
}

export default class Resources extends React.PureComponent {
  constructor(props) {
    super(props)

    this.state = {
      resources: [],
      selected: null,
    }

    this.download = this.download.bind(this)
    this.addToCart = this.addToCart.bind(this)
    this.removeFromCart = this.removeFromCart.bind(this)
    this.redirectLink = this.redirectLink.bind(this)
  }

  async componentDidMount() {
    const response = await fetch("/resources/all.json").then((res)=>res.json())
    const p = "1234"
    const res_meta = response.reduce((group, data)=>{
      group[data.Resource_Name] = data
      return group
    }, {})
    const {response: libraries} = await fetch_meta_post('/libraries/find', {})
    const resources = libraries.reduce((groups, lib) => {
      let resource = renamed[lib.meta['Primary_Resource'] || lib.meta['name']] || lib.meta['Primary_Resource'] || lib.meta['name']
      if ((lib.meta['Library_name'] || '').indexOf('ARCHS4') !== -1)
        resource = 'ARCHS4'

      if (groups[resource] === undefined) {
        groups[resource] = {
          name: resource,
          icon: iconOf[resource] || lib.meta['Icon'],
          description: res_meta[resource].Description,
          PMID: res_meta[resource].PMID,
          URL: res_meta[resource].URL,
          libraries: []
        }
      }
      groups[resource].libraries.push(lib)
      return groups
    }, {})
    // .map((group)=>{
    //   fetch("/resources/"+resource+".json").then((res)=>res.json).then((data)=>{
    //     console.log(data)
    //   })
    //   return
    // })

    this.setState({
      resources: Object.values(resources),
    })
  }

  async download(library_id) {
    alert('coming soon')
  }

  addToCart(id) {
    this.props.updateCart(
      this.props.cart.add(id)
    )
  }

  removeFromCart(id) {
    this.props.updateCart(
      this.props.cart.delete(id)
    )
  }

  redirectLink(e){
    window.location = "https://portals.broadinstitute.org/achilles";
  }

  render() {
    const sorted_resources = [...this.state.resources].sort((r1, r2) => r1.name.localeCompare(r2.name))
    return this.state.selected ? (
      <div className="row">
        <div className="col s12">
          
          <div className="row">
            <div class="col s12">
              <div class="card">
                <div className="row">
                  <div class="col s12">
                    <div class="card-image col s1">
                      <IconButton
                      img={this.state.selected.icon}
                      onClick={this.redirectLink}
                      />
                    </div>
                    <div class="card-content col s11">
                      <div>
                        <span className="card-title">{this.state.selected.name}</span>
                      </div>
                      <div>
                        <span>
                          <b>PMID:</b>&nbsp;
                          <a 
                            href={"https://www.ncbi.nlm.nih.gov/pubmed/" + this.state.selected.PMID}
                          >
                            {this.state.selected.PMID}
                          </a>
                        </span>
                      </div>
                      <div>
                        <span>
                          <b>URL:</b>&nbsp;
                          <a
                            href={this.state.selected.URL}
                          >
                            {this.state.selected.URL}
                          </a>
                        </span>
                      </div>
                      <div>
                        <p>{this.state.selected.description}</p>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="card-action">
                  <a
                    className="waves-effect waves-teal btn-flat" 
                    onClick={() => this.setState({ selected: null })}
                  >
                    BACK
                  </a>
                </div>
              </div>
            </div>
          </div>

          <div className="row">
            <div className="col s12">
              <ul
                className="collapsible popout"
              >
                {this.state.selected.libraries.map((library) => (
                  <li
                    key={library.id}
                  >
                    <div
                      className="page-header"
                      style={{
                        padding: 10,
                        display: 'flex',
                        flexDirection: "column",
                        backgroundColor: 'rgba(255,255,255,1)',
                      }}
                    >
                      <div
                        style={{
                          display: 'flex',
                          flexDirection: 'row',
                      }}>
                        <Label
                          item={library}
                          visibility={1}
                        />
                      </div>
                      <div style={{
                        display: 'flex',
                        flexDirection: "row",
                      }}>
                        <IconButton
                          alt="Signature Commons"
                          img="favicon.ico"
                        />
                        &nbsp;
                        <IconButton
                          alt="Download"
                          icon="file_download"
                          onClick={call(this.download, library.id)}
                        />
                        &nbsp;
                        {this.props.cart.has(library.id) ? (
                          <IconButton
                            alt="Remove from Cart"
                            icon="remove_shopping_cart"
                            onClick={call(this.removeFromCart, library.id)}
                          />
                        ) : (
                          <IconButton
                            alt="Add to Cart"
                            icon="add_shopping_cart"
                            onClick={call(this.addToCart, library.id)}
                          />
                        )}
                        <div style={{ flex: '1 0 auto' }}>&nbsp;</div>
                        <a
                          href="javascript:void(0);"
                          className="collapsible-header"
                          style={{ border: 0 }}
                        >
                          <i className="material-icons">expand_more</i>
                        </a>
                      </div>
                    </div>
                    <div
                      className="collapsible-body"
                    >
                      <ShowMeta
                        value={{
                          '@id': library.id,
                          '@type': 'Library',
                          'meta': library.meta,
                        }}
                      />
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </div>
    ) : (
      <div className="row">
        <div className="col offset-s2 s8">
          {sorted_resources.map((resource) => (
            <IconButton
              key={resource.name}
              alt={resource.name}
              img={resource.icon}
              onClick={() => this.setState({ selected: resource }, () => M.AutoInit())}
            />
          ))}
        </div>
      </div>
    )
  }
}