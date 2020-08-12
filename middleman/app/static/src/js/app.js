import { HashRouter as Router, Route, Switch, Redirect } from 'react-router-dom'
import React from 'react'

class App extends React.Component {
    componentDidMount = () => {
        console.log("Mounted")
    }
    
    landing = (props) => {
        console.log(props)
        return <span>Hi there</span>
    }

    render = () => (
        <Router>
            <Switch>
                <Route
                    path={'/'}
                    exact
                    component={this.landing}
                />
            </Switch>
        </Router>
    )
}

export default App