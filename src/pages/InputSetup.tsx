import * as React from 'react'
import {ChangeEvent, Component} from 'react'
import CountrySelector from "../components/CountrySelector";
import Collapsible from "react-collapsible";
import {eel} from '../App';
import ReactTagInput from "@pathofdev/react-tag-input";
import EditableTableClass from "../components/EditableTable-Class";
import {toast} from "react-toastify";
//import CountryLU from '../pages/FinalCsvGeneration'

type InputType = 'Individual' | 'Comparison' | string

interface CountryLU {
    [key: string]: string
}

interface InputSetupSettings {
    country_short_name: string,
    country_full_name: string,
    campaign_shortcode: string,
    tags_selected: Array<string>,
    input_type: InputType,
    tag_settings: object[]
}

interface TagSettings {
    category: string,
    option: string,
    keywords: string[],
    tag_id?: number
}

const defaultState: InputSetupSettings = {
    country_short_name: "DE",
    country_full_name: "Germany",
    campaign_shortcode: '',
    tags_selected: [],
    input_type: 'Comparison',
    tag_settings: []
}

class InputSetup extends Component<{}, InputSetupSettings> {
    constructor(props: {}) {
        super(props);
        this.state = defaultState

        this.handleCountryChange = this.handleCountryChange.bind(this)
        this.handleRadioChange = this.handleRadioChange.bind(this)
        this.handleTagInput = this.handleTagInput.bind(this)
        this.handleDBDataGathering = this.handleDBDataGathering.bind(this)
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
            input_type: e.target.value
        })
    }

    handleTagInput(items: Array<string>) {
        this.setState({
            tags_selected: items
        })
    }

    handleDBDataGathering() {
        if (this.state.tags_selected.length > 0) {
            toast("Loading data from DB", {
                position: toast.POSITION.BOTTOM_RIGHT
            });
            eel.get_keywords_for_tags(this.state.country_short_name, this.state.tags_selected)((res: Array<TagSettings>) => {
                console.log(res)
                this.setState({
                    tag_settings: [...this.state.tag_settings, ...res]
                })
            })
        }
    }

    handleCreationSubmit() {
        if (this.state.tag_settings.length === 0) {
            toast("Cannot create file for empty data", {
                type: "warning"
            })
        } else {
            eel.receive_data({data: this.state, destination: 'InputSetup'})
        }
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
                        Scraping Input Setup
                    </h1>
                    <Collapsible trigger={'Click for description'}
                                 triggerStyle={{fontStyle: 'italic', color: '#A7A8AA'}}>
                        <p style={{fontWeight: 'lighter', fontSize: '0.9rem'}}>
                            Use this page to generate the inputs for Scraping. You can choose between two modes:
                            "Individual Tag" or "Comparison" mode
                        </p>
                        <ul>
                            <li style={styles.li}>
                                <b>Comparisons</b> - Gets you information on the relative strength of different options.<br/>Requires
                                you to define the categories you want to look at (e.g. Garden services) and then the
                                options within that category to look at. For each of these options you then have to
                                define Keywords the script will use to represent the option.
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
                                as a 100 of another.<br/>Uses multiple keywords averaged together as a proxy to
                                represent the Tag level popularity. This is due to the fact that a Tag is a bigger
                                concept than just a given keyword, meaning people requesting the same tag may look for
                                it using multiple keywords.<br/><i>It is essentially like you're a supermarket and want
                                to
                                know how many people look for "Vegetables". You don't only want to count people that
                                have
                                literally asked for "Vegetables" but also people that looked for "Zucchini" or
                                "Cucumber"</i>
                                <br/><br/><b>Used for: Chart, Table, Map, (backup for Top5, when the script is run by
                                itself)</b>
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
                    <h2>Set-Up</h2>
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
                        <label>
                            <input
                                type="radio"
                                value="Individual"
                                checked={this.state.input_type === 'Individual'}
                                onChange={this.handleRadioChange}
                            />
                            Individual Tags
                        </label>
                        <label>
                            <input
                                type={"radio"}
                                value={'Comparison'}
                                checked={this.state.input_type === 'Comparison'}
                                onChange={this.handleRadioChange}
                            />
                            Comparison
                        </label>
                        <label>
                            <input
                                type={"radio"}
                                value={'Both'}
                                checked={this.state.input_type === 'Both'}
                                onChange={this.handleRadioChange}
                            />
                            Both
                        </label>
                        <Collapsible
                            trigger={`Get Tag Data from DB ${(this.state.tags_selected.length || -1 > 0) ? ' ✅' : ""}`}
                            triggerStyle={styles.subsection_headers}
                            transitionTime={200} triggerTagName={'div'}>
                            <div style={{
                                width: '100%',
                                padding: '1rem',
                                display: "flex",
                                flexDirection: "column",
                                justifyContent: "center"
                            }}>
                                <ReactTagInput
                                    tags={this.state.tags_selected || []}
                                    onChange={this.handleTagInput}
                                    placeholder="Type and press enter to input Keywords or Tag Ids"
                                    removeOnBackspace={true}
                                />
                                <button className={'button'} style={{
                                    fontSize: '0.9rem', marginBottom: '1rem'
                                }}
                                        onClick={this.handleDBDataGathering}
                                >
                                    Gather Keywords from DB
                                </button>
                            </div>
                        </Collapsible>
                        <hr/>
                        <EditableTableClass initial_columns={[
                            {
                                field: 'category',
                                title: 'Category',
                                cellStyle: {
                                    fontSize: '0.8rem'
                                }
                            },
                            {
                                field: 'option',
                                title: 'Option'
                            },
                            {
                                field: 'keywords',
                                title: 'Keywords',
                                editComponent: TagField,
                                render: (rowData) => rowData.keywords.join(", ")
                            }
                        ]} title={"Set-up"} data={this.state.tag_settings} handleDataChange={(data => this.setState({
                            tag_settings: data
                        }))}/>
                        <div style={{display: "flex", flexDirection: 'row', alignItems: 'center', justifyContent: 'center'}}>
                            <button className={'button'} style={{
                                fontSize: '0.9rem', marginBottom: '1rem'
                            }}
                                    onClick={() => eel.receive_data({data: this.state, destination: 'InputSetup'})}
                            >
                                Submit & Create Input File
                            </button>
                            <button className={'button'} style={{
                                fontSize: '0.9rem', marginBottom: '1rem'
                            }}
                                    onClick={() => this.setState(defaultState)}
                            >
                                Reset All
                            </button>
                        </div>
                    </div>
                </div>
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

export default InputSetup


const TagField = (props: { value: Array<string>, onChange: (tags: Array<string>) => void }) => {
    return <ReactTagInput tags={props.value || []} onChange={tags => props.onChange(tags)} removeOnBackspace={true}/>
}