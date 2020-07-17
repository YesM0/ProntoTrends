import {Component} from "react";
import {eel} from "../App";
import EditableTableClass from "./EditableTable-Class";
import * as React from "react";
import { SubStateComponentProps } from '../pages/FinalCsvGeneration'

interface CatOverviewProps extends SubStateComponentProps {
    country_short_code: string
}

interface TableRow {
    category_name: string,
    chosen: boolean,
    column_name: string
}

interface CatOverviewState {
    data: TableRow[]
}

class CategoryOverviewSection extends Component<CatOverviewProps, CatOverviewState> {
    constructor(props: CatOverviewProps) {
        super(props);
        this.state = {
            data: []
        }
        //console.log(this.state)
        this.handleTableSubmit = this.handleTableSubmit.bind(this)
        this.handleDataChange = this.handleDataChange.bind(this)
    }

    handleTableSubmit() {
        // reformat
        let data = this.state.data
        let filtered = data.filter(item => (item.chosen))
        let categories = filtered.map(cat => cat.category_name)
        let column_names = filtered.map(cat => cat.column_name)
        this.props.globalStateSetter({
            category_overview_settings: {
                category_names: categories,
                category_column_names: column_names
            }
        }, 'Create Category Overviews')
    }

    handleDataChange(new_data: Array<TableRow>) {
        this.setState({data: new_data})
    }

    async getComparisons(country_short_code: string)
        :
        Promise<TableRow[]> {
        let data = await eel.get_comparisons(country_short_code)();
        // console.log("get comparisons result:")
        // console.log(availableCategories)
        return data.map((cat: string) => {
            return {
                category_name: cat,
                chosen: false,
                column_name: ''
            }
        })
    }

    async componentDidMount() {
        this.setState({data: await this.getComparisons(this.props.country_short_code)})
    }

    async componentDidUpdate(prevProps: Readonly<CatOverviewProps>, prevState: Readonly<CatOverviewState>, snapshot?: any) {
        console.log("Updated CategoryOverviewSection State")
        console.log(this.state, this.props)
        if (prevProps.country_short_code !== this.props.country_short_code) {
            console.log("Country changed")
            this.setState({data: await this.getComparisons(this.props.country_short_code)})
        }
    }

    render() {
        return (
            <div style={{
                padding: '1rem 0rem'
            }}>
                <EditableTableClass initial_columns={[
                    {
                        field: 'category_name',
                        title: 'Category',
                        cellStyle: {
                            fontSize: '0.8rem'
                        },
                        editable: 'never'
                    },
                    {
                        field: 'chosen',
                        title: 'Choose?',
                        type: "boolean"
                    },
                    {
                        field: 'column_name',
                        title: 'Column Name (has to end on _type)',
                        type: 'string'
                    }
                ]} title={'Category Overview Settings'} data={this.state.data}
                                    handleDataChange={this.handleDataChange}/>

                <button onClick={this.handleTableSubmit} className={'button'} style={{
                    fontSize: '0.9rem', marginBottom: '1rem'
                }}>
                    Add the selected Category Overviews to the Task-List
                </button>
            </div>
        )
    }
}

export default CategoryOverviewSection
