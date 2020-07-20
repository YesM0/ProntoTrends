import * as React from 'react';
import {SubStateComponentProps} from "../pages/FinalCsvGeneration";
import {eel} from '../App'
import {ChangeEvent, Component} from "react";

interface ChartDataProps extends SubStateComponentProps {
    country_short_code: string
}

interface Tag_Item {
    tag_name: string,
    count: number,
    chosen: boolean
}

interface ChartData_State {
    data: Tag_Item[],
    min_region_count: number,
    select_all: boolean
}

class ChartDataSection extends Component<ChartDataProps, ChartData_State> {
    constructor(props: ChartDataProps) {
        super(props);
        this.state = {
            data: [],
            min_region_count: 0,
            select_all: false
        }
        this.handleCheck = this.handleCheck.bind(this)
        this.handleSubmit = this.handleSubmit.bind(this)
        this.handleAllCheck = this.handleAllCheck.bind(this)
    }

    async componentDidMount() {
        this.setState({data: await this.getTags(this.props.country_short_code)})
    }

    async getTags(country_short_code: string)
        :
        Promise<Tag_Item[]> {
        return await eel.get_tags(country_short_code)();
    }

    handleCheck(e: React.FormEvent<HTMLInputElement>) {
        let name = e.currentTarget.name
        let checked = e.currentTarget.checked
        let new_data = this.state.data.map(item => {
            if (item.tag_name === name) {
                return {
                    tag_name: item.tag_name,
                    count: item.count,
                    chosen: checked
                }
            } else {
                return item
            }
        })
        this.setState({
            data: new_data
        })
    }

    handleSubmit() {
        let choices = this.state.data.filter(item => (item.chosen)).map(item => item.tag_name)
        this.props.globalStateSetter({
            chart_settings: {
                tags_selected: choices,
                min_region_count: this.state.min_region_count
            }
        }, 'create Chart Data')
    }

    handleAllCheck(e: React.FormEvent<HTMLInputElement>) {
        this.setState({
            data: this.state.data.map(item => {
                let curr = {...item}
                curr['chosen'] = e.currentTarget.checked
                return curr
            }),
            select_all: e.currentTarget.checked
        })
    }

    render() {
        return (
            <>
                <label className={'label'}>
                        Min Region Count
                        <input className={'input'} type={'number'} value={this.state.min_region_count} min={0} max={30}
                               onChange={(e: ChangeEvent<HTMLInputElement>) => {
                                   this.setState({min_region_count: parseInt(e.target.value)})
                               }}/>
                    </label>
                <table>
                    <thead>
                    <td>
                        Tag
                    </td>
                    <td>
                        # Regions
                    </td>
                    <td>
                        Choose?
                    </td>
                    </thead>
                    {this.state.data.map(dpack => {
                        return (
                            <tr key={dpack.tag_name}>
                                <td>{dpack.tag_name}</td>
                                <td>{dpack.count}</td>
                                <td><input name={dpack.tag_name} type={'checkbox'} checked={dpack.chosen}
                                           onChange={this.handleCheck}/></td>
                            </tr>
                        )
                    })}
                </table>
                <label>
                    Select All
                    <input type={'checkbox'} checked={this.state.select_all} onChange={this.handleAllCheck}/>
                </label>
                <button onClick={this.handleSubmit} className={'button'} style={{
                    fontSize: '0.9rem', marginBottom: '1rem'
                }}>
                    Add Chart Creation with the chosen Tags to Task-List
                </button>
            </>
        );
    }
}

export default ChartDataSection