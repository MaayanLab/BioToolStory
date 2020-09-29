import React from 'react'
import { withRouter, Link } from 'react-router-dom'
import AppBar from '@material-ui/core/AppBar'
import Toolbar from '@material-ui/core/Toolbar'
import Typography from '@material-ui/core/Typography'
import Button from '@material-ui/core/Button'
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import Hidden from '@material-ui/core/Hidden';
import SwipeableDrawer from '@material-ui/core/SwipeableDrawer';
import MenuIcon from '@material-ui/icons/Menu';

export const ListItemLink = (props) => {
  return <ListItem button component="a" {...props} />;
}

export function Nav(props) {
    const { location } = props
    return (
      <React.Fragment>
        <ListItemLink
            selected={location.pathname === '/'}
            style={{color: "inherit"}}
            href={"#/"}
        >
            {"Tools"}
        </ListItemLink>
        {/* <ListItemLink
          selected={location.pathname === '/API'}
          style={{color: "inherit"}}
          href={"#/API"}
        >
          {"API"}
        </ListItemLink> */}
      </React.Fragment>
    )
  }


class Header extends React.Component {
    constructor(props){
        super(props)
        this.state = {
            open: false,
        }
    }

    toggleDrawer = () => {
        this.setState(prevState =>({
            open: !prevState.open,
        }));
    };

    render = () => {
        return(
          <header>
            <AppBar position="static" color="primary" style={{boxShadow: "none"}}>
                <Toolbar>
                    <Hidden smDown>
                    <Typography variant="h4" color="inherit" style={{flexGrow: 1}}>
                        <Link
                        to="/"
                        style={{whiteSpace: 'nowrap', color: "inherit"}}
                        >
                        <img {...this.props.ui.header_info.icon}/> {this.props.title}
                        </Link>
                    </Typography>
                    <List
                    style={{display: "flex"}}
                    {...this.props.ui.header_info.menu_props}
                    >
                        <Nav {...this.props}/>
                    </List>
                </Hidden>
                <Hidden mdUp>
                    <Button edge="start" style={{margin: 0}} onClick={this.toggleDrawer} color="inherit" aria-label="menu">
                        <MenuIcon />
                    </Button>
                    <Typography variant="h4" color="inherit" style={{flexGrow: 1}}>
                        <Link
                        to="/"
                        style={{whiteSpace: 'nowrap', color: "inherit"}}
                        >
                        <img {...this.props.ui.header_info.icon}/> {this.props.title}
                        </Link>
                    </Typography>
                    <SwipeableDrawer
                        open={this.state.open}
                        onClose={this.toggleDrawer}
                        onOpen={this.toggleDrawer}
                    >
                        <div
                        tabIndex={0}
                        role="button"
                        onClick={this.toggleDrawer}
                        onKeyDown={this.toggleDrawer}
                        >
                        <List {...this.props.ui.header_info.menu_props}>
                            <Nav {...this.props}/>
                        </List>
                        </div>
                    </SwipeableDrawer>
                    </Hidden>
                </Toolbar>
            </AppBar>
          </header>
        )
    }
}

export default withRouter(Header)