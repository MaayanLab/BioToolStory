import React from 'react'
import { Switch, Route, Redirect } from 'react-router-dom'
import GenesetSearchBox from './GenesetSearchBox'
import ResourceFilters from './ResourceFilters'
import LibraryResults from './LibraryResults'
import { connect } from "react-redux";
import { findSignature } from "../../util/redux/actions";
import { findMatchedSchema } from '../../util/objectMatch'
import { makeTemplate } from '../../util/makeTemplate'

const mapStateToProps = state => {
  return { 
    ...state.signature_result,
    ...state.serverSideProps,
    resources: Object.values(state.serverSideProps.resources),
    input: state.signature_input,
  }
};

function mapDispatchToProps(dispatch) {
  return {
    search : (params) => 
      dispatch(findSignature(input)),
  }
}

class SignatureSearch extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      input: {},
      controller: null,
    }
  }

  async componentDidMount() {
    window.scrollTo(0, 0)
    const schema = await findMatchedSchema(this.props.resources[0], this.props.schemas)
    const name_props = Object.values(schema.properties).filter(prop=>prop.name)
    const name_prop = name_props.length > 0 ? name_props[0].text : "${id}"
    const icon_props = Object.values(schema.properties).filter(prop=>prop.icon)
    const icon_prop = icon_props.length > 0 ? icon_props[0].src : "${id}"
    const description_props = Object.values(schema.properties).filter(prop=>prop.description)
    const description_prop = description_props.length > 0 ? description_props[0].text : "${id}"
    const sorted_resources = [...this.props.resources].sort((r1, r2) => {
      const r1_name = makeTemplate(name_prop, r1)
      const r2_name = makeTemplate(name_prop, r2)
      return (r1_name.localeCompare(r2_name))
    })
    this.setState({
      schema,
      sorted_resources,
      icon_prop,
      name_prop,
      description_prop,
    })
  }


  resource_filters = (props) => (
    <ResourceFilters
      resources={this.props.resources||[]}
      resource_signatures={this.props.resource_signatures || {}}
      ui_values={this.props.ui_values}
      input={this.props.input}
      submit={this.props.submit}
      signature_type={this.props.signature_type}
      {...props}
      {...this.state}
    />
  )

  library_results = (props) => (
    <LibraryResults
      results={
        (((this.props.resource_signatures || {})[props.match.params.resource.replace('_', ' ')] || {}).libraries || []).map(
            (lib) => this.props.library_signatures[lib]
        )
      }
      signature_keys={this.props.signature_keys}
      schemas={this.props.schemas}
      {...this.props}
      {...props}
      {...this.state}
    />
  )

  render_signature_search = () => {
    this.props.handleChange({}, 'signature', true)
    return <Redirect to="/" />
  }

  render_signature_search_type = (props) => {
    const type = props.match.params.type
    this.props.changeSignatureType(type)
    this.props.handleChange({}, 'signature', true)
    return <Redirect to="/" />
  }

  render = () => {
    return (
      <div className="row">
        <Switch>
          <Route exact path="/SignatureSearch" render={this.render_signature_search} />
          <Route path="/SignatureSearch/:type/:input_signature/:resource" component={this.library_results} />
          <Route path="/SignatureSearch/:type/:input_signature" component={this.resource_filters} />
          <Route path="/SignatureSearch/:type" render={this.render_signature_search_type} />
        </Switch>
      </div>
    )
  }
}

export default connect(mapStateToProps, mapDispatchToProps)(SignatureSearch)