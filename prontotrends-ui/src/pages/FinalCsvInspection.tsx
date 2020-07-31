import * as React from 'react';
import {Pie, Doughnut} from "react-chartjs-2";
import {ChangeEvent, Component} from 'react';
import {eel} from '../App';
// import Collapsible from "react-collapsible";
import CountrySelector from "../components/CountrySelector";
import {CountryLU} from "./FinalCsvGeneration";
import Select from 'react-select'
import {ValueType} from 'react-select'

interface ChartData {
    labels: string[],
    datasets: Array<{data: number[], backgroundColor: string[], hoverBackgroundColor: string[]}>
}

interface FinalCsvInspection_State {
    chartType: 'pie' | 'bar' | 'line',
    sourceFile: string,
    settings: {
        year?: number,
        region?: string
    },
    country_short_name: string,
    country_full_name: string,
    campaign_shortcode: string,
    available_campaigns: Array<SelectionItem>,
    available_files: Array<SelectionItem>,
    available_options: {
        year: Array<SelectionItem>,
        regions: Array<SelectionItem>
    },
    data: ChartData
}

type SelectionItem = {
    value: string | number,
    label: string
}

const data = {
    labels: [
        'Red',
        'Blue',
        'Yellow'
    ],
    datasets: [{
        data: [200, 50, 100],
        backgroundColor: [
            '#FF6384',
            '#36A2EB',
            '#FFCE56'
        ],
        hoverBackgroundColor: [
            '#FF6384',
            '#36A2EB',
            '#FFCE56'
        ]
    }]
};

const defaultState: FinalCsvInspection_State = {
    chartType: 'pie',
    sourceFile: '',
    settings: {
        year: 2020,
        region: ""
    },
    country_full_name: 'Germany',
    country_short_name: 'DE',
    campaign_shortcode: '',
    available_campaigns: [],
    available_files: [],
    available_options: {
        year: [],
        regions: []
    },
    data: data
}


class FinalCsvInspection extends Component<{}, FinalCsvInspection_State> {
    constructor(props: {}) {
        super(props);
        this.state = defaultState;
        this.handleCountryChange = this.handleCountryChange.bind(this);
        this.updateFileOptions = this.updateFileOptions.bind(this);
        this.updateCampaignOptions = this.updateCampaignOptions.bind(this);
        this.getSelectionOptions = this.getSelectionOptions.bind(this);
        this.getData = this.getData.bind(this)
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
        }, this.updateCampaignOptions)
    }

    updateCampaignOptions() {
        eel.get_available_campaigns(this.state.country_short_name)((campaigns: Array<string>) => {
            let available_campaigns = campaigns.map(x => {
                return {value: x, label: x}
            })
            this.setState({available_campaigns: available_campaigns})
        })
    }

    componentDidMount() {
        this.updateCampaignOptions()
    }

    updateFileOptions() {
        eel.get_final_category_overviews(this.state.country_short_name, this.state.campaign_shortcode)((files: Array<string>) => {
            let available_files = files.map(x => {
                return {
                    value: x,
                    label: x
                }
            })
            this.setState({available_files: available_files})
        })
    }

    getSelectionOptions() {
        eel.get_available_options_from_file(this.state.sourceFile)((dict: { Year: SelectionItem[], ticket_geo_region_name: SelectionItem[], full_csv_path: string }) => {
            console.log(dict)
            this.setState({
                available_options: {
                    regions: dict.ticket_geo_region_name,
                    year: dict.Year
                },
                sourceFile: dict.full_csv_path
            })
        })
    }

    getData() {
        console.log("In getData")
        if (this.state.settings.year && this.state.settings.region) {
            console.log("Getting data from file: " + this.state.sourceFile)
            eel.get_data_for_chosen_options(this.state.sourceFile, this.state.settings.year, this.state.settings.region)((data: ChartData) => {
               console.log(data)
                this.setState({
                   data: data
               })
            })
        }
    }

    render() {
        return (
            <div>
                <div id={'settings'} style={{textAlign: 'left'}}>
                    <label className={'label'}>
                        Country
                        <CountrySelector value={this.state.country_full_name}
                                         handleCountryChange={this.handleCountryChange}/>
                    </label>
                    <br/>
                    <label className={'label'}>Select Campaign
                        <Select options={this.state.available_campaigns}
                                onChange={(selected: ValueType<SelectionItem> | SelectionItem) => {
                                    if (selected) {
                                        let campaign_shortcode = '' + (selected as SelectionItem).value
                                        this.setState({
                                            campaign_shortcode: campaign_shortcode
                                        }, this.updateFileOptions)
                                    }
                                }} styles={{
                            option: (provided) => ({
                                ...provided,
                                color: 'black'
                            }),
                            container: (provided) => ({
                                ...provided,
                                width: 200,
                                display: 'inline-block',
                                marginLeft: '1rem'
                            })
                        }
                        }/></label>
                    <br/>
                    <label className={'label'}>Select File
                        <Select options={this.state.available_files}
                                onChange={(selected: ValueType<SelectionItem> | SelectionItem) => {
                                    if (selected) {
                                        let sourceFile = '' + (selected as SelectionItem).value
                                        this.setState({
                                            sourceFile: sourceFile
                                        }, this.getSelectionOptions)
                                    }
                                }} styles={{
                            option: (provided) => ({
                                ...provided,
                                color: 'black'
                            }),
                            container: (provided) => ({
                                ...provided,
                                width: 200,
                                display: 'inline-block',
                                marginLeft: '1rem'
                            })
                        }
                        }/>
                    </label>
                    <br/>
                    <label className={'label'}>Select Year
                        <Select options={this.state.available_options.year}
                                onChange={(selected: ValueType<SelectionItem> | SelectionItem) => {
                                    if (selected) {
                                        let year = (selected as SelectionItem).value
                                        if (typeof year === 'string') {
                                            year = parseInt(year)
                                        }
                                        let region = this.state.settings.region
                                        this.setState({
                                            settings: {
                                                year: year,
                                                region: region
                                            }
                                        }, this.getData)
                                    }
                                }} styles={{
                            option: (provided) => ({
                                ...provided,
                                color: 'black'
                            }),
                            container: (provided) => ({
                                ...provided,
                                width: 200,
                                display: 'inline-block',
                                marginLeft: '1rem'
                            })
                        }
                        }/>
                    </label>
                    <br/>
                    <label className={'label'}>Select Region
                        <Select options={this.state.available_options.regions}
                                onChange={(selected: ValueType<SelectionItem> | SelectionItem) => {
                                    if (selected) {
                                        let val = '' + (selected as SelectionItem).value
                                        let year = this.state.settings.year;
                                        this.setState({
                                            settings: {
                                                region: val,
                                                year: year
                                            }
                                        }, this.getData)
                                    }
                                }} styles={{
                            option: (provided) => ({
                                ...provided,
                                color: 'black'
                            }),
                            container: (provided) => ({
                                ...provided,
                                width: 200,
                                display: 'inline-block',
                                marginLeft: '1rem'
                            })
                        }
                        }/>
                    </label>
                </div>
                <div style={{textAlign: 'left'}}>
                </div>
                {(this.state.chartType === 'pie') && <Pie data={this.state.data} legend={{labels: {fontColor: 'white'}}}/>}
            </div>

        )
    }
}

export default FinalCsvInspection