import * as React from 'react'
import {ChangeEvent, Component} from 'react'
import CountrySelector from "../components/CountrySelector";
import Collapsible from "react-collapsible";
// import {eel} from '../App';
// import {toast} from "react-toastify";
import {CountryLU} from "./FinalCsvGeneration";

export const eel = window.eel
eel.set_host('ws://localhost:8080')

interface ScrapingItem {
    title: string,
    timestamp: number
}

interface StatusUpdate {
    scraping_results?: {
        files_expected?: number,
        files_generated?: number
    },
    scraping_progress?: {
        done?: number,
        to_do?: number,
        progress_rate_per_minute?: number
    },
    scraping_item?: ScrapingItem
}

interface ScraperSettingsState {
    sourceFile: string,
    scraping_type: string,
    scraping_results: {
        files_expected: number,
        files_generated: number
    },
    scraping_progress: {
        done: number,
        to_do: number | undefined,
        progress_rate_per_minute: number
    },
    scraping_items: Array<ScrapingItem>,
    campaign_shortcode: string,
    country_short_name: string,
    country_full_name: string,
    deduplicate_keywords: boolean,
    log: Array<string>
}

const defaultState: ScraperSettingsState = {
    sourceFile: "",
    scraping_type: "Individual - All Regions",
    scraping_results: {
        files_expected: 0,
        files_generated: 0
    },
    scraping_progress: {
        done: 0,
        to_do: undefined,
        progress_rate_per_minute: 4
    },
    scraping_items: [],
    campaign_shortcode: "",
    country_short_name: "DE",
    country_full_name: "Germany",
    deduplicate_keywords: false,
    log: []
}

function ScraperReceiveLog(msg: string) {
    window.ScraperComponent.receiveFrontEndLog(msg)
}

function ScraperReceiveStatus(update: StatusUpdate) {
    window.ScraperComponent.receiveStatusUpdates(update)
}

eel.expose(ScraperReceiveLog, 'ScraperReceiveLog')
eel.expose(ScraperReceiveStatus, 'ScraperReceiveStatus')

class Scraper extends Component<{}, ScraperSettingsState> {
    private fileInput: React.RefObject<HTMLInputElement>;

    constructor(props: {}) {
        super(props);
        this.state = defaultState
        this.fileInput = React.createRef();

        window.ScraperComponent = this;

        this.handleCountryChange = this.handleCountryChange.bind(this)
        this.handleRadioChange = this.handleRadioChange.bind(this)
        this.useDefaultFileHandler = this.useDefaultFileHandler.bind(this)
        this.receiveFrontEndLog = this.receiveFrontEndLog.bind(this)
        this.receiveStatusUpdates = this.receiveStatusUpdates.bind(this)
    }

    handleCountryChange(e: ChangeEvent<HTMLSelectElement>) {
        let ccs: CountryLU = {
            'Germany': 'DE',
            'France': 'FR',
            'Spain': 'ES',
            'Italy': 'IT',
            'Austria': 'AT',
            'Switzerland': 'CH'
        }
        console.log(e)
        this.setState({
            country_full_name: e.target.value,
            country_short_name: ccs[e.target.value] || 'IT'
        })
    }

    handleRadioChange(e: ChangeEvent<HTMLInputElement>) {
        this.setState({
            scraping_type: e.target.value
        })
    }

    useDefaultFileHandler(e: unknown) {
        eel.get_scraping_file(this.state.country_short_name, this.state.campaign_shortcode, this.state.scraping_type)((filepath: string) => this.setState({sourceFile: filepath}))
    }

    receiveFrontEndLog(msg: string) {
        let curr_messages = this.state.log.splice(-10, 10)
        this.setState({log: [...curr_messages, msg]})
    }

    receiveStatusUpdates(update: StatusUpdate) {
        console.log(update)
        //const {scraping_item, scraping_progress, scraping_results} = update
        const {scraping_results: {files_generated, files_expected} = {}, scraping_progress: {to_do, progress_rate_per_minute, done} = {}, scraping_item} = update
        let num_todos = (to_do) ? to_do : this.state.scraping_progress.to_do;
        let num_done = (done) ? this.state.scraping_progress.done + done : this.state.scraping_progress.done;
        let num_files_gen = (files_generated) ? this.state.scraping_results.files_generated + files_generated : this.state.scraping_results.files_generated;
        let num_files_exp = (files_expected) ? this.state.scraping_results.files_expected + files_expected : this.state.scraping_results.files_expected;
        let cur_progress_rate = (progress_rate_per_minute) ? (progress_rate_per_minute / 4) + (this.state.scraping_progress.progress_rate_per_minute * 3 / 4) : this.state.scraping_progress.progress_rate_per_minute;
        let scraping_items = (scraping_item) ? [...this.state.scraping_items, scraping_item] : this.state.scraping_items;
        this.setState({
            scraping_results: {
                files_expected: num_files_exp,
                files_generated: num_files_gen
            },
            scraping_progress: {
                progress_rate_per_minute: cur_progress_rate,
                done: num_done,
                to_do: num_todos
            },
            scraping_items: scraping_items
        })
    }

    render() {
        let time_left = (this.state.scraping_progress.to_do || 0 - this.state.scraping_progress.done) / this.state.scraping_progress.progress_rate_per_minute
        if (time_left !== time_left) {
            time_left = 0
        }
        let time_left_str = (time_left / 60 >= 1) ? `${Math.round((time_left / 60) * 100) / 100} h` : `${Math.round(time_left)} min`
        return (
            <div className={'internal-component'} style={{textAlign: 'left'}}>
                <div style={{
                    height: '30%',
                    color: 'white',
                    padding: '2.5rem 4rem',
                    textAlign: 'left'
                }}>
                    <h1 style={{fontWeight: 'lighter', fontSize: '2.66rem'}}>
                        Scraping
                    </h1>
                    <Collapsible trigger={'Click for description'}
                                 triggerStyle={{fontStyle: 'italic', color: '#A7A8AA'}}>
                        <p style={{fontWeight: 'lighter', fontSize: '0.9rem'}}>
                            Use this page to set up the scraper and start it
                        </p>
                        <ul>
                            <li style={styles.li}>
                                <b>Comparisons</b> - Gets you information on the relative strength of different options.<br/>Uses
                                the ProntoPro_Trends_Questions_{this.state.country_short_name}.json files for input.
                                <br/>Per default, the scraper will select the keyword with the highest search volume to
                                represent the option
                                <br/><br/><b>Used for: Top5, Comparison Overviews</b>
                            </li>
                            <li style={styles.li}>
                                <b>Individual <a
                                    href={'https://sites.google.com/prontopro.fr/in-house-prontowiki/info/glossary'}
                                    target={'_blank'} rel={'noopener noreferrer'}>Tags</a></b> - Aims to get information
                                on the geographic popularity and the
                                over-time popularity of an individual tag.<br/>The values obtained are relative to the
                                peak of the tag's popularity. Thus a 100 for a given tag is not the same absolute value
                                as a 100 of another.<br/>Requires a file
                                like {(this.state.campaign_shortcode.length > 0) && this.state.campaign_shortcode + "_"}Keywords_{this.state.country_short_name}.csv
                                <br/><br/><b>Used for: Chart, Table, Map, (backup for Top5, when the script is run by
                                itself)</b><br/><br/>
                                <b>Variations</b>
                                <ul>
                                    <li>
                                        All Regions - to scrape for all subregions of a country
                                    </li>
                                    <li>
                                        Country-level only - scrape only for the country level (e.g. useful for quick
                                        scouting scrapes, saves up to 20x of scraping time)
                                    </li>
                                </ul>
                            </li>
                        </ul>
                    </Collapsible>
                </div>
                <Collapsible trigger={"Set-Up    ▶️"} triggerStyle={styles.subsection_headers} transitionTime={200}
                             triggerTagName={'div'} open={true} triggerWhenOpen={'Set-Up   🔽'}>
                    <div style={{
                        display: 'flex',
                        flexDirection: 'column',
                        padding: '1.5rem',
                        lineHeight: '2rem',
                        justifyContent: 'space-between',
                        alignContent: 'space-between'
                    }}>
                        <div>
                            <label className={'label'}>
                                Country
                                <CountrySelector value={this.state.country_full_name}
                                                 handleCountryChange={this.handleCountryChange}/>
                            </label>
                            <label className={'label'}>
                                Campaign shortcode
                                <input className={'input'} type={'text'} value={this.state.campaign_shortcode}
                                       onChange={(e: ChangeEvent<HTMLInputElement>) => {
                                           this.setState({campaign_shortcode: e.target.value})
                                       }} required={true}/>
                            </label>
                            <div style={{display: 'flex', justifyContent: 'space-between', padding: '0rem 2rem'}}>
                                <label>
                                    <input
                                        type="radio"
                                        value="Individual - All Regions"
                                        checked={this.state.scraping_type === 'Individual - All Regions'}
                                        onChange={this.handleRadioChange}
                                        style={{marginRight: '0.5rem'}}
                                    />
                                    Individual Tags - All Regions
                                </label>
                                <label>
                                    <input
                                        type={"radio"}
                                        value={'Comparison'}
                                        checked={this.state.scraping_type === 'Comparison'}
                                        onChange={this.handleRadioChange}
                                        style={{marginRight: '0.5rem'}}
                                    />
                                    Comparison
                                </label>
                                <label>
                                    <input
                                        type="radio"
                                        value="Individual - CC only"
                                        checked={this.state.scraping_type === 'Individual - CC only'}
                                        onChange={this.handleRadioChange}
                                        style={{marginRight: '0.5rem'}}
                                    />
                                    Individual - CC only
                                </label>
                            </div>
                            <div style={{padding: '1rem'}}><label>
                                Source file:
                                <input type={'file'} ref={this.fileInput}
                                       accept={`${(this.state.scraping_type === 'Comparison') ? '.json' : '.csv'}`}
                                       multiple={false}
                                       onChange={(event) => {
                                           let file = (event.target.files) ? event.target.files[0].name : ""
                                           this.setState({
                                               sourceFile: file
                                           })
                                       }}
                                       style={{paddingLeft: '1rem'}}
                                />
                            </label>
                                <button onClick={this.useDefaultFileHandler}>Use default</button>
                            </div>
                            <p><b>Chosen File file:</b> {this.state.sourceFile}</p>
                            <div style={{display: 'flex', flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center'}}>
                                <label>
                                    Deduplicate Keywords
                                    <input type={'checkbox'} checked={this.state.deduplicate_keywords}
                                           onChange={(e) => this.setState({deduplicate_keywords: e.currentTarget.checked})}
                                           disabled={(this.state.scraping_type.indexOf('Individual') === -1)}/>
                                </label>
                                <button className={'button'} style={{
                                    fontSize: '0.9rem', marginBottom: '1rem', width: '30%'
                                }}
                                        onClick={() => eel.scrape(this.state)}
                                >
                                    Run Scraper
                                </button>
                            </div>

                            <hr/>
                        </div>
                    </div>
                </Collapsible>
                <StatusDisplay progress_done={this.state.scraping_progress.done}
                               progress_to_do={this.state.scraping_progress.to_do} time_left_str={time_left_str}
                               log={this.state.log}/>
            </div>
        )
    }
}

const styles = {
    li: {
        paddingTop: '0.4rem',
        paddingBottom: '0.4rem'
    },
    subsection_headers: {
        fontStyle: 'bold',
        fontSize: '1.2rem',
        backgroundColor: '#48bfcc',
        width: '95%',
        padding: '0.3rem 1.5rem',
        borderBottom: '1px solid white',
        align: 'center'
    }
}

export default Scraper

const StatusDisplay = ({progress_done, progress_to_do, time_left_str, log}: { progress_done: number, progress_to_do: number | undefined, time_left_str: string, log: Array<string> }) => {
    if (log.length > 0) {
        return (<>
            <div style={{justifyContent: 'center', alignItems: 'center', display: 'flex', flexDirection: 'column', marginTop: '1.5rem'}}>
                <h1>Running...</h1>
                <br/>
                <progress value={progress_done} max={progress_to_do}
                          title={'Loading'} style={{width: '60%'}}/>
                <p>Expected duration: {time_left_str}</p>
            </div>
            <div style={{
                margin: '3rem',
                backgroundColor: '#1d364b',
                borderRadius: '10px',
                padding: '1.5rem',
                lineHeight: '0.8rem'
            }}>
                <b>Log</b>
                {log.map(item => (<p>{item}</p>))}
            </div>
        </>)
    } else {
        return null
    }
}