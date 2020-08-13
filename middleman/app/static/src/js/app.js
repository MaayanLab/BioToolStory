import React from 'react'
import { HashRouter as Router, Route, Switch, Redirect } from 'react-router-dom'
import Home from './home'
import { defaultUI } from './defaultUI'
import { defaultTheme } from './defaultTheme'
import merge from 'deepmerge'
import { createMuiTheme, MuiThemeProvider } from '@material-ui/core'

// from deepmerge
const overwriteMerge = (destinationArray, sourceArray, options) => sourceArray

class App extends React.Component {
    constructor(props){
        super(props)
        this.state = {
            ui: defaultUI,
            theme: createMuiTheme(defaultTheme)
        }
    }

    componentDidMount = () => {
        this.setState({
            ui:  merge(defaultUI, this.props.ui,  { arrayMerge: overwriteMerge }),
            theme: createMuiTheme(merge(defaultTheme, this.props.ui.theme))
        })
    }
    
    landing = (props) => {
        return <Home {...props} {...this.props} ui={this.state.ui} />
    }

    render = () => (
        <MuiThemeProvider theme={this.state.theme}>
            <Router>
                <Switch>
                    <Route
                        path={'/'}
                        exact
                        component={(this.landing)}
                    />
                </Switch>
            </Router>
        </MuiThemeProvider>
    )
}

export default App