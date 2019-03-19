import React from 'react'
import { Link } from 'react-router-dom'
import IconButton from '../../components/IconButton'
import config from '../../ui-schemas/SignatureSearch.json'

export default class extends React.Component {
  constructor(props) {
    super(props)

    this.state = {
      show_all: false
    }
  }

  toggle_show_all = () => this.setState({ show_all: !this.state.show_all })

  sort_resources() {
    return [...this.props.resources].sort(
      (r1, r2) => {
        const diff = (((this.props.resource_signatures || {})[r2.name] || {}).count || 0) - (((this.props.resource_signatures || {})[r1.name] || {}).count || 0)
        if (diff === 0)
          return r1.name.localeCompare(r2.name)
        else
          return diff
      }
    )
  }

  render() {
    const sorted_resources = this.sort_resources()

    return (
      <div ref={(ref) => {
        if (!this.state.resourceAnchor)
          this.setState({ resourceAnchor: ref })
      }} className="col s12 center">
        {sorted_resources.map((resource, ind) => (
          <div key={resource.name}>
            {this.state.show_all || ind < config.maxResourcesToShow || sorted_resources.length < config.maxResourcesBeforeCollapse ? (
              <div>
                <Link
                  to={`${this.props.match.url}/${resource.name.replace(/ /g, '_')}`}
                >
                  <IconButton
                    alt={resource.name}
                    img={resource.icon}
                    counter={((this.props.resource_signatures || {})[resource.name] || {}).count}
                  />
                </Link>
              </div>
            ) : null}
          </div>
        ))}
        {sorted_resources.length >= config.maxResourcesBeforeCollapse ? (
          <IconButton
            alt={this.state.show_all ? "Less": "More"}
            icon="more_horiz"
            onClick={this.toggle_show_all}
          />
        ) : null}
      </div>
    )
  }
}
