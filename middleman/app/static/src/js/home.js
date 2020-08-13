import React from 'react'
import { HashRouter as Router, Route, Switch, Redirect } from 'react-router-dom'
import Header from './header'


export default class Home extends React.Component {
    render = () => {
        return (
            <div>
                <Header {...this.props} />
            </div>
        )
    }
}
