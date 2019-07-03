import React from 'react'
import { withRouter, Link } from 'react-router-dom'
import { base_scheme as meta_base_scheme, base_url as meta_base_url } from '../../util/fetch/meta'

export function Nav(props) {
  return (
    <ul {...props}>
      { props.ui_content.content.signature_search ?
        <li
          className={props.location.pathname === '/SignatureSearch' ? 'active' : ''}
        >
          <Link to="/SignatureSearch">
            Signature Search
          </Link>
        </li> : null
      }
      { props.ui_content.content.metadata_search ?
        <li
          className={props.location.pathname === '/MetadataSearch' ? 'active' : ''}
        >
          <Link to="/MetadataSearch">
            Metadata Search
          </Link>
        </li> : null
      }
      { props.ui_content.content.resources ?
        <li
          className={props.location.pathname === `/${props.ui_content.content.change_resource || 'Resources'}` ? 'active' : ''}
        >
          <Link to={`/${props.ui_content.content.change_resource || 'Resources'}`}>
            {props.ui_content.content.change_resource || 'Resources'}
          </Link>
        </li> : null
      }
      <li>
        <a
          target="_blank"
          rel="noopener noreferrer"
          href={`${meta_base_scheme}://petstore.swagger.io/?url=${meta_base_url}/openapi.json`}
        >
          API
        </a>
      </li>
    </ul>
  )
}


export default withRouter((props) => {
  const paths = props.location.pathname.split('/')
  return (
    <header>
      <nav className="nav-extended">
        <div className="nav-wrapper">
          <Link
            to="/"
            className="brand-logo left hide-on-med-and-down"
            style={{
              whiteSpace: 'nowrap',
            }}
          >
            &nbsp;&nbsp; <img src={`${process.env.PREFIX}/static/favicon.ico`} width={22} />&nbsp; {props.ui_content.content.header || 'Signature Commons'}
          </Link>
          <Link
            to="/"
            className={`brand-logo ${location} hide-on-large-only`}
            style={{
              whiteSpace: 'nowrap',
            }}
          >
            &nbsp;&nbsp; <img src={`${process.env.PREFIX}/static/favicon.ico`} width={22} />&nbsp; Signature Commons
          </Link>
          <a href="#" data-target="mobile-menu" className="sidenav-trigger"><i className="material-icons">menu</i></a>
          <Nav id="nav-mobile" className="right hide-on-med-and-down" location={props.location} ui_content={props.ui_content} />
        </div>
        <Nav className="sidenav" id="mobile-menu" location={props.location} ui_content={props.ui_content}/>

        {paths.length <= 2 ? null : (
          <div className="nav-wrapper grey">
            <div className="row">
              <div className="col s12">
                {paths.slice(1).map((path, i) => {
                  const href = paths.slice(0, i + 2).join('/')
                  return (
                    <Link
                      key={href}
                      to={href}
                      className="breadcrumb"
                    >
                      {path.replace(/_/g, ' ')}
                    </Link>
                  )
                })}
              </div>
            </div>
          </div>
        )}
      </nav>
    </header>
  )
})
