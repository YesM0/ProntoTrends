import React, {Component} from "react";
import {NavLink} from "react-router-dom";

class Home extends Component {
    constructor(props) {
        super(props);
    }

    render() {
        return (
            <div>
                <div style={{
                    padding: '6rem',
                    backgroundColor: '#274964',
                    color: 'white',
                    textAlign: 'left',
                    backgroundImage: `url($)`
                }}>
                    <h1 style={{fontWeight: '100', fontSize: '2.66rem'}}>Welcome to ProntoTrends</h1>
                    <h3 style={{fontWeight: '100'}}>How can we help you today?</h3>
                    <div style={{
                        display: 'flex',
                        flexDirection: 'row',
                        width: '100%',
                        justifyContent: 'center',
                        marginTop: '2rem'
                    }}>
                        <NavLink to="/DataPipeline" className={'button'}>Enter Datapipeline</NavLink>
                        <NavLink to="/Inspection" className={'button'}>Enter Inspection</NavLink>
                    </div>
                </div>
                <div style={ {padding: '2rem 3rem', textAlign: 'left' }}>
                    <h2>What is ProntoTrends?</h2>
                    <p>
                        ProntoTrends is the place where consumers and journalists can find all information around
                        services
                        offered on ProntoPro
                    </p>
                    <h2>
                        What is this tool for?
                    </h2>
                    <p>
                        The ProntoTrends software suite supports you in creating the content to be presented on the
                        website.
                        From Scraping over final data generation to inspection everything is included.
                    </p>
                </div>
            </div>
        );
    }
}

const styles = {
    button: {
        padding: '1rem',
        backgroundColor: '#48bfcc',
        borderRadius: '0px',
        marginTop: '2rem',
        marginLeft: '2rem',
        marginRight: '2rem',
        color: '#274964',
        fontWeight: '700',
        textDecoration: 'none',
    }
}

export default Home;