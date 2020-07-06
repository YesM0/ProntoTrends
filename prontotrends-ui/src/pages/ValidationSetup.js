import React, {Component} from "react";
import EditableTable from "../components/EditableTable";


export const eel = window.eel
eel.set_host('ws://localhost:8080')

class ValidationSetup extends Component {
    constructor(props) {
        super(props);

        this.state = {
            title: '',
            colNames: ["year", "month"],
            separators: ',',
            separators_visible: ',',
            labels: {},
            variableTypes: {},
            labelCounts: {}
        }

        this.handleSubmit = this.handleSubmit.bind(this)
        this.handleSeparatorChange = this.handleSeparatorChange.bind(this)
        this.handleTitleInput = this.handleTitleInput.bind(this)
        this.handleTableDataSubmit = this.handleTableDataSubmit.bind(this)
    }

    handleSubmit(event) {
        event.preventDefault();
        console.log(this.state)
        console.log("submission is not implemented yet")
        eel.receive_data(this.state)
    }

    handleSeparatorChange(event) {
        let val = event.target.value;
        if (val === ',' || val === ';' || val === '\t' || val === 'TAB') {
            let val_translated = (val === '\t') ? "TAB" : val;
            val = (val === 'TAB') ? '\t' : val
            this.setState({separators: val, separators_visible: val_translated})
        }
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
            labelCounts: distribution
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
                <button onClick={this.handleSubmit}>
                    Finish
                </button>
            </div>
        )
    }
}

export default ValidationSetup;
