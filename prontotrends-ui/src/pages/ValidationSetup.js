import React, {Component} from "react";
import EditableTable from "../components/EditableTable";
import CountrySelector from "../components/CountrySelector";

// TODO: Combine Finished and Save button -> requires rewriting the Table Component to a class component or use this: https://stackoverflow.com/questions/27864951/how-to-access-childs-state-in-react

export const eel = window.eel
eel.set_host('ws://localhost:8080')

class ValidationSetup extends Component {
    constructor(props) {
        super(props);

        this.state = {
            country: 'Germany',
            title: '',
            colNames: [],
            separators: ',',
            separators_visible: ',',
            labels: {},
            variableTypes: {},
            labelCounts: {},
            table_submitted: false
        }

        this.handleSubmit = this.handleSubmit.bind(this)
        this.handleSeparatorChange = this.handleSeparatorChange.bind(this)
        this.handleTitleInput = this.handleTitleInput.bind(this)
        this.handleTableDataSubmit = this.handleTableDataSubmit.bind(this)
        this.handleCountryChange = this.handleCountryChange.bind(this)
        this.submittable = this.submittable.bind(this)
    }

    submittable(state) {
        // check: hasCountry, hasTitle, hasColumnNames
        return (state.country.length > 0 && state.title.length > 0 && state.colNames.length > 0)
    }

    handleSubmit(event) {
        event.preventDefault();
        if (!this.state.table_submitted) {
            alert('Please save the column data in the table first')
        } else {
            if (!this.submittable(this.state)) {
                alert("The data you filled is insufficient. Make sure that you added a Filename and Column Names")
            } else {
                eel.receive_data({destination: 'ValidationSetUp', data: this.state})((res) => console.log(res))
            }
        }
    }

    handleSeparatorChange(event) {
        let val = event.target.value;
        if (val === ',' || val === ';' || val === '\t' || val === 'TAB') {
            let val_translated = (val === '\t') ? "TAB" : val;
            val = (val === 'TAB') ? '\t' : val
            this.setState({separators: val, separators_visible: val_translated})
        }
    }

    handleCountryChange(event) {
        this.setState({country: event.target.value})
    }

    handleTitleInput(event) {
        let filename = event.target.value.trim();
        this.setState({title: filename})
    }


    handleTableDataSubmit(data) {
        console.log(data)
        let columnNames = [];
        let dataTypes = {};
        let labels = {};
        let distribution = {};
        data.forEach(item => {
            columnNames.push(item.colName);
            dataTypes[item.colName] = item.dataType;
            labels[item.colName] = (item.labels) ? item.labels.split(",").map(x => x.trim()) : null;
            distribution[item.colName] = item.labelFrequencyType
        })
        this.setState({
            colNames: columnNames,
            labels: labels,
            variableTypes: dataTypes,
            labelCounts: distribution,
            table_submitted: true,
        }, () => console.log(this.state))
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
                    <h1 style={{fontWeight: '100', fontSize: '2.66rem'}}>Validation Setup</h1>
                    <p style={{fontWeight: '100'}}>
                        Validation is the last step before the upload of data to the Website. It checks all files for
                        errors or inconsistencies and proposes solutions.
                        <br/><br/>
                        In the setup stage you want to program the rules to be applied to new files. Often previous
                        patterns can be reused but here you can edit everything necessary to work for your specific file
                    </p>
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
                        <h2>Let's set up some new validation rules.</h2>
                        <label className={'label'}>
                            Country
                            <CountrySelector value={this.state.country} handleCountryChange={this.handleCountryChange}/>
                        </label>
                        <label className={'label'}>
                            Filename
                            <input className={'input'} type={'text'} onChange={this.handleTitleInput}
                                   value={this.state.title}/>
                        </label>
                        <br/>
                        <label className={'label'}>
                            Column Separator to use:
                            <select style={{margin: '1rem'}} onChange={this.handleSeparatorChange}
                                    value={this.state.separators_visible}>
                                <option value=",">,</option>
                                <option value=";">;</option>
                                <option value="TAB">TAB</option>
                            </select>
                        </label>
                        <br/>
                        <small style={{lineHeight: '0.2rem', fontWeight: '100', fontStyle: 'italic'}}>
                            Use the following table to set up rules for the columns. Please ensure that the order of the
                            rows in the table corresponds to the order of the columns in the final file.
                            <br/>
                            For the labels you can use the following constants to avoid having to type too much:
                            REGIONS_SPAIN, REGIONS_GERMANY, REGIONS_ITALY, REGIONS_FRANCE. Ensure proper spelling!
                        </small>
                        <EditableTable initial_columns={[
                            {
                                title: 'Column Name (capitalization is important)',
                                field: 'colName'
                            },
                            {
                                title: 'Data-Type (e.g. "dec|0-1")',
                                field: 'dataType'
                            },
                            {
                                title: 'Labels in Col (separate using ",")',
                                field: 'labels'
                            },
                            {
                                title: 'Label frequency distribution',
                                field: 'labelFrequencyType',
                                lookup: {
                                    'equal': 'Equal',
                                    'unequal': 'Unequal'
                                }
                            }
                        ]} title={'Columns Setup'} dataHandler={this.handleTableDataSubmit}
                        />
                    </div>
                </div>
                <button onClick={this.handleSubmit} className={'button'} style={{marginBottom: '2rem'}}>
                    Finish and Create File
                </button>

            </div>
        )
    }
}

export default ValidationSetup;
