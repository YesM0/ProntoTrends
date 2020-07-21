import React, {Component} from "react";
import {NavLink} from "react-router-dom";

class NavigationPage extends Component {

    styles = {
    row: {
        display: 'flex',
        flexDirection: 'row',
        justifyContent: 'center'
    },
    item_title: {
        flex: 2.5,
        padding: '1rem',
        margin: '1rem',
        textDecoration: 'none'
    },
    item_description: {
        flex: 1,
        padding: '1rem',
        margin: '1rem',
        textDecoration: 'none',
        color: 'grey'
    }
}

    render() {
        return (
            <div>
                <div style={{
                    height: '30%',
                    backgroundColor: "#274964",
                    color: 'white',
                    padding: '2.5rem 4rem',
                    textAlign: 'left'
                }}>
                    <h1 style={{fontWeight: '100', fontSize: '2.66rem', position: 'sticky', top: '10px'}}>{this.props.title || "Datapipeline"}</h1>
                    <h3 style={{fontWeight: '100'}}>What step do you want to take next?</h3>
                </div>
                <div>
                    {this.props.items.map(item => (<NavLink to={item.link} style={this.styles.row}>
                        <div style={this.styles.item_title}>{item.title}</div>
                        <div style={this.styles.item_description}>{item.description}</div>
                    </NavLink>))}
                </div>
                {this.props.children}
            </div>
        );
    }
}

export default NavigationPage;

