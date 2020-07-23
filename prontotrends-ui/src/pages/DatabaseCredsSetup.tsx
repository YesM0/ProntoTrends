import * as React from "react";
import {eel} from '../App';
import {Component} from 'react'
import Collapsible from "react-collapsible";
import {toast} from "react-toastify";

interface DBSettings {
    host: string,
    user: string,
    password: string
}

interface DBCredsState {
    details: Partial<DBSettings>
}

class DatabaseCredsSetup extends Component<{}, DBCredsState> {
    constructor(props: {}) {
        super(props)
        this.state = {
            details: {}
        }
    }

    componentDidMount() {
        eel.get_db_access_data()((d: {}) => this.setState({
            details: d
        }))
    }

    render() {
        return (
            <div className={'internal-component'} style={{textAlign: 'left'}}>
                <div style={{
                    height: '30%',
                    color: 'white',
                    padding: '2.5rem 4rem',
                    textAlign: 'left'
                }}>
                    <h1 style={{fontWeight: 'lighter', fontSize: '2.66rem'}}>
                        Database Credentials Setup
                    </h1>
                    <Collapsible trigger={'Click for description'}
                                 triggerStyle={{fontStyle: 'italic', color: '#A7A8AA'}}>
                        <p style={{fontWeight: 'lighter', fontSize: '0.9rem'}}>
                            Use this page to set up your database credentials
                        </p>
                    </Collapsible>
                </div>
                <div style={{
                    padding: '3rem',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center'
                }}>
                    <div>
                        <label>
                            Host
                            <input className={'input'} type={'text'} onChange={event => this.setState({
                                details: {
                                    ...this.state.details,
                                    host: event.target.value
                                }
                            })} value={this.state.details.host}/>
                        </label>
                    </div>
                    <div>
                        <label>
                            Username
                            <input className={'input'} type={'text'} onChange={event => this.setState({
                                details: {
                                    ...this.state.details,
                                    user: event.target.value
                                }
                            })} value={this.state.details.user}/>
                        </label>
                    </div>
                    <div>
                        <label>
                            Password
                            <input className={'input'} type={'password'} onChange={event => this.setState({
                                details: {
                                    ...this.state.details,
                                    password: event.target.value
                                }
                            })}
                            value={this.state.details.password} />
                        </label>
                    </div>
                    <button className={'button'} style={{
                                fontSize: '0.9rem', marginBottom: '1rem'
                            }}
                                    onClick={() => eel.save_db_access_data(this.state.details)}
                            >
                                Save Credentials
                            </button>
                </div>
            </div>
        );
    }

}


export default DatabaseCredsSetup