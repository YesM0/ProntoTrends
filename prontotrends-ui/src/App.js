import React, {Component} from 'react';
import Header from './components/header'
import {
    Route,
    Switch,
    HashRouter
} from 'react-router-dom'
import { ToastContainer, toast } from "react-toastify";
import 'react-toastify/dist/ReactToastify.css'
import './App.css';
import "@pathofdev/react-tag-input/build/index.css";
import Home from './pages/Home'
import DatapipelineStart from "./pages/DatapipelineStart";
import InspectionStart from "./pages/InspectionStart";
import ValidationStart from "./pages/ValidationStart";
import ValidationSetup from "./pages/ValidationSetup";
import NavSideBar from "./components/NavBar";
import FinalCsvGeneration from './pages/FinalCsvGeneration';
import InputSetup from "./pages/InputSetup";
import DatabaseCredsSetup from "./pages/DatabaseCredsSetup";


export const eel = window.eel
eel.set_host('ws://localhost:8080')

function show_log(msg, options) {
    //console.log("got message " + msg)
    window.AppComponent.showLog(msg, options)
}

// Separating
window.eel.expose(show_log, 'show_log')

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
    },
    {
        title: 'Settings',
        link: '/Settings',
        children: [
            {
                title: 'Database Credentials',
                link: '/Settings-DatabaseCredentials'
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

    showLog(msg, options) {
        toast(msg, {...options,
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
                        </div>
                        <div style={{flex: 1, backgroundColor: '#315c80'}}>
                            <Switch >
                                <Route exact path="/">
                                    <Home/>
                                </Route>
                                <Route exact path={'/DataPipeline'}>
                                    <DatapipelineStart/>
                                </Route>
                                <Route
                                    exact path={'/DataPipeline-FinalCsvGeneration'}>
                                    <FinalCsvGeneration/>
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
                                <Route exact path={'/DataPipeline-InputSetup'}>
                                    <InputSetup/>
                                </Route>
                                <Route exact path={'/Settings-DatabaseCredentials'}>
                                    <DatabaseCredsSetup/>
                                </Route>
                                <Route>
                                    <div>
                                        <h1 style={ { padding: '2rem' }}>
                                            No Match
                                        </h1>
                                        <h2 style={ { padding: '2rem' }}>
                                            It may be that this section has not yet been implemented
                                        </h2>
                                    </div>
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
