import * as React from 'react';
import {eel} from '../App'
import {Component} from 'react';

interface LoggingState {
    messages: string[]
}

function receiveLog(msg: string) {
    //console.log("got message " + msg)
    window.LoggingComponent.receiveLog(msg)
}

// Separating
window.eel.expose(receiveLog, 'receiveLog')

class LoggingTest extends Component<{}, LoggingState> {
    constructor(props: {}) {
        super(props);
        this.state = {
            messages: []
        }
        window.LoggingComponent = this;
        this.receiveLog = this.receiveLog.bind(this)
    }

    receiveLog(msg: string) {
        let keptMsgs = this.state.messages.splice(-10, 10)
        this.setState({
            messages: [...keptMsgs, msg]
        })
    }

    render() {
        return (
            <div>
                <button onClick={() => eel.sendLogs()}>Start receiving</button>
            <p>
                {this.state.messages.map(msg =>  <p>{msg}<br/></p>)}
            </p>
            </div>
        )
    }
}

export default LoggingTest