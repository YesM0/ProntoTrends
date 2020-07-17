import * as React from 'react'
import {ChangeEvent, Component} from 'react'
import CountrySelector from "../components/CountrySelector";
import EditableTableClass from "../components/EditableTable-Class";
import Collapsible from "react-collapsible";
import {eel} from '../App'
import CategoryOverviewSection from '../components/CategoryOverviewSection'
import Top5Section from '../components/Top5Section'
import ChartDataSection from "../components/ChartDataSection";

export interface CategoryOverviewsSettings {
    category_names: Array<string>,
    category_column_names: Array<string>
}

interface ChartDataSettings {
    min_region_count: number,
    tags_selected: Array<string>
}

interface Top5Settings {
    folders_to_use: Array<string>
}

interface MapDataSettings {
    use_chart_data: boolean
}

interface MainSectionSettings {
    categories_to_include: Array<string> // can be sourced from settings for the Category Overviews
}

interface ColumnRemap {
    [key: string]: Array<string>
}

interface UserSettings {
    country_short_name?: string,
    country_full_name?: string,
    campaign_shortcode?: string,
    chosenActions?: Array<string>,
    category_overview_settings?: Partial<CategoryOverviewsSettings>,
    chart_settings?: Partial<ChartDataSettings>,
    top5_settings?: Partial<Top5Settings>,
    map_settings?: Partial<MapDataSettings>,
    main_section_settings?: Partial<MainSectionSettings>,
    column_remap?: Partial<ColumnRemap>
}

interface CountryLU {
    [key: string]: string
}

export interface SubStateComponentProps {
    globalStateSetter: (stateUpdate: Partial<UserSettings>, emitter: string) => void,
}


class FinalCsvGenerationSetup extends Component<{}, UserSettings> {
    constructor(props: {}) {
        super(props);
        this.state = {
            country_short_name: 'DE',
            country_full_name: 'Germany',
            campaign_shortcode: '',
            chosenActions: [],
            category_overview_settings: {
                category_column_names: [],
                category_names: []
            },
            chart_settings: {
                min_region_count: 0,
                tags_selected: []
            },
            column_remap: {},
            main_section_settings: {
                categories_to_include: []
            },
            map_settings: {
                use_chart_data: true
            },
            top5_settings: {
                folders_to_use: []
            }
        }
        this.handleComponentSubmit = this.handleComponentSubmit.bind(this)
        this.handleCountryChange = this.handleCountryChange.bind(this)
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
            country_short_name: ccs[e.target.value] || 'it'
        })
    }

    handleComponentSubmit(stateUpdate: Partial<UserSettings>, emitter: string) {
        let current_chosen_actions = this.state.chosenActions || []
        this.setState({...stateUpdate, chosenActions: [...current_chosen_actions, emitter] })
    }

    render() {

        return (<div className={'internal-component'} style={{textAlign: 'left'}}>
            <div style={{
                height: '30%',
                color: 'white',
                padding: '2.5rem 4rem',
                textAlign: 'left'
            }}>
                <h1 style={{fontWeight: 'lighter', fontSize: '2.66rem'}}>
                    Final CSV generation
                </h1>
                <Collapsible trigger={'Click for description'} triggerStyle={{fontStyle: 'italic', color: '#A7A8AA'}}>
                    <p style={{fontWeight: 'lighter', fontSize: '0.8rem'}}>
                        Use this page to generate the final CSVs. You can create files for all different styles.
                        <br/><br/>
                        The Final CSV Genenerator offers the following types of files:
                    </p>
                    <ul>
                        <li style={styles.li}>
                            <b>Comparison Overviews</b> - sources data from the comparisons folder and creates a summary
                            file which lists the percentage popularity of the different options over the course of the
                            year.
                        </li>
                        <li style={styles.li}>
                            <b>Main Section</b> - takes the results from Comparison Overviews and finds the top choices
                            for each category per year and region
                        </li>
                        <li style={styles.li}>
                            <b>Top 5</b> - Uses a comparison dataset to determine the most popular choice in a given
                            year at a national level. Determines most popular month and least popular month, as well as
                            the seasonality inbetween.
                        </li>
                        <li style={styles.li}>
                            <b>Chart</b> - takes results from Aggregated (have to be adjusted) and collates them into a
                            yearly overview of single tags against each other
                        </li>
                        <li style={styles.li}>
                            <b>Table</b> - takes the results from Chart and converts them into the table format where
                            the within tag popularity over a year is broken down in percent. E.g. 10% of requests for X
                            happen in January
                        </li>
                        <li style={styles.li}>
                            <b>Map</b> - uses Data from the Chart to create a yearly map overview on how the interest in
                            topic X is distributed across regions.
                        </li>
                    </ul>
                </Collapsible>
            </div>
            <div style={{
                display: 'flex',
                flexDirection: 'column',
                padding: '1.5rem',
                lineHeight: '2rem',
                justifyContent: 'space-between',
                alignContent: 'space-between'
            }}>
                <div>
                    <h2>Set-Up</h2>
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
                               }}/>
                    </label>
                    <br/>
                    <Collapsible trigger={'Category overviews'} triggerStyle={styles.subsection_headers}
                                 transitionTime={200} triggerTagName={'div'}>
                        <CategoryOverviewSection country_short_code={this.state.country_short_name || 'DE'}
                                                 globalStateSetter={this.handleComponentSubmit}/>
                    </Collapsible>
                    <Collapsible trigger={'Top 5'} triggerStyle={styles.subsection_headers} transitionTime={200}
                                 triggerTagName={'div'}>
                        <Top5Section country_short_code={this.state.country_short_name || 'DE'} globalStateSetter={this.handleComponentSubmit} key={this.state.country_short_name}/>
                    </Collapsible>
                    <Collapsible trigger={'chart-data'} triggerStyle={styles.subsection_headers} transitionTime={200}
                                 triggerTagName={'div'}>
                        <ChartDataSection globalStateSetter={this.handleComponentSubmit} country_short_code={this.state.country_short_name || 'DE'} key={this.state.country_short_name}/>
                    </Collapsible>
                    <Collapsible trigger={'Table'} triggerStyle={styles.subsection_headers} transitionTime={200}
                                 triggerTagName={'div'}>
                        <div>Selection</div>
                    </Collapsible>
                    <Collapsible trigger={'Main Section'} triggerStyle={styles.subsection_headers} transitionTime={200}
                                 triggerTagName={'div'}>
                        <div>Folders/ Cats to use</div>
                    </Collapsible>
                    <Collapsible trigger={'Map'} triggerStyle={styles.subsection_headers} transitionTime={200}
                                 triggerTagName={'div'}>
                        <div>Use chart Data toggle</div>
                    </Collapsible>

                </div>
            </div>
            {/*<button onClick={this.handleSubmit} className={'button'} style={{marginBottom: '2rem'}}>*/}
            {/*    Finish and Create File*/}
            {/*</button>*/}
        </div>)
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
        width: '100%'
    }
}

export default FinalCsvGenerationSetup

