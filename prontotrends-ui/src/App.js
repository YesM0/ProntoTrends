import React, {Component} from 'react';
import Header from './components/header'
import {
    Route,
    Switch,
    NavLink,
    HashRouter
} from 'react-router-dom'
import { ToastContainer, toast } from "react-toastify";
import 'react-toastify/dist/ReactToastify.css'
import './App.css';
import Home from './pages/Home'
import DatapipelineStart from "./pages/DatapipelineStart";
import InspectionStart from "./pages/InspectionStart";
import ValidationStart from "./pages/ValidationStart";
import ValidationSetup from "./pages/ValidationSetup";
import NavSideBar from "./components/NavBar";


export const eel = window.eel
eel.set_host('ws://localhost:8080')

window.eel.expose(show_log)
function show_log(msg) {
    console.log("got message " + msg)
    window.AppComponent.showLog(msg)
}

const navItems = [
    {
        title: 'Data Pipeline',
        link: '/DataPipeline',
        children: [
            {
                title: 'Input Setup',
                link: '/DataPipeline-InputSetup'
            },
            {
                title: 'Scraping',
                link: '/DataPipeline-Scraping'
            },
            {
                title: 'Aggregation',
                link: '/DataPipeline-Aggregate'
            },
            {
                title: 'Final CSV Generation',
                link: '/DataPipeline-FinalCsvGeneration',
                children: [
                    {
                        title: 'Test'
                    }
                ]
            },
            {
                title: 'Validation',
                link: '/DataPipeline-Validation',
                children: [
                    {
                        title: 'Set up Validation',
                        link: '/DataPipeline-Validation-SetUp'
                    },
                    {
                        title: 'Run Validation',
                        link: '/DataPipeline-Validation-Run'
                    }
                ]
            },
            {
                title: 'Special Tools',
                link: '/DataPipeline-SpecialTools',
                children: [
                    {
                        title: 'Database Requests',
                        link: '/DataPipeline-SpecialTools-DataBaseRequest'
                    }
                ]
            }
        ]
    },
    {
        title: 'Inspection',
        link: '/Inspect',
        children: [
            {
                title: 'Tag Inspection',
                link: '/Inspect-Individual'
            },
            {
                title: 'Comparison Inspection',
                link: '/Inspect-Comparison'
            }
        ]
    }
]


export class App extends Component {
    constructor(props) {
        super(props);
        this.showLog = this.showLog.bind(this)
        window.AppComponent = this;
    }

    showLog(msg) {
        toast(msg, {
            position: toast.POSITION.BOTTOM_RIGHT,
        });
    }

    render() {
        return (
            <div className="App">
                <Header/>
                <HashRouter>
                    <div style={{display: 'flex', alignItems: 'stretch', height: '100%'}}>
                        <div style={{flex: 1, minWidth: '10%', maxWidth: '18%', height: '100%'}}>
                            <NavSideBar items={navItems}/>
                            <button onClick={() => eel.getLog()}>Get Log from Python</button>
                        </div>
                        <div style={{flex: 1, backgroundColor: '#315c80'}}>
                            <Switch >
                                <Route exact path="/">
                                    <Home/>
                                </Route>
                                <Route exact path={'/DataPipeline'}>
                                    <DatapipelineStart/>
                                </Route>
                                <Route exact path={'/Inspect'}>
                                    <InspectionStart/>
                                </Route>
                                <Route exact path={'/DataPipeline-Validation'}>
                                    <ValidationStart/>
                                </Route>
                                <Route exact path={'/DataPipeline-Validation-SetUp'}>
                                    <ValidationSetup/>
                                </Route>
                                <Route>
                                    <h1>NO MATCH</h1>
                                </Route>
                            </Switch>
                            <ToastContainer/>
                        </div>
                    </div>
                </HashRouter>
            </div>
        )
            ;
    }
}


export default App;
