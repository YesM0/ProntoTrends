import * as React from 'react';
import {SubStateComponentProps} from "../pages/FinalCsvGeneration";
import {eel} from '../App'
import {Component} from "react";

interface MainSection_Props extends SubStateComponentProps {
    country_short_code: string
}

interface FolderItem {
    folder_name: string,
    chosen: boolean
}

interface MainSection_State {
    data: FolderItem[]
}

class MainSection_Section extends Component<MainSection_Props, MainSection_State> {
    constructor(props: MainSection_Props) {
        super(props);
        this.state = {
            data: []
        }
        this.handleCheck = this.handleCheck.bind(this)
        this.handleSubmit = this.handleSubmit.bind(this)
    }

    async componentDidMount() {
        this.setState({data: await this.getFolders(this.props.country_short_code)})
    }

    async getFolders(country_short_code: string)
        :
        Promise<FolderItem[]> {
        let data = await eel.get_comparisons(country_short_code)();
        // console.log("get comparisons result:")
        // console.log(availableCategories)
        return data.map((cat: string) => {
            return {
                folder_name: cat,
                chosen: false
            }
        })
    }

    handleCheck(e: React.FormEvent<HTMLInputElement>) {
        let name = e.currentTarget.name
        let checked = e.currentTarget.checked
        let new_data = this.state.data.map(item => {
            if (item.folder_name === name) {
                return {
                    folder_name: item.folder_name,
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
        let choices = this.state.data.filter(item => (item.chosen)).map(item => item.folder_name)
        this.props.globalStateSetter({
            main_section_settings: {
                categories_to_include: choices
            }
        }, 'Create Main Section')
    }

    render() {
        return (
            <>
                <table>
                    <thead>
                    <td>
                        Category
                    </td>
                    <td>
                        Choose?
                    </td>
                    </thead>
                    {this.state.data.map(dpack => {
                        return (
                            <tr key={dpack.folder_name}>
                                <td>{dpack.folder_name}</td>
                                <td><input name={dpack.folder_name} type={'checkbox'} checked={dpack.chosen}
                                           onChange={this.handleCheck}/></td>
                            </tr>
                        )
                    })}
                </table>
                <button onClick={this.handleSubmit} className={'button'} style={{
                    fontSize: '0.9rem', marginBottom: '1rem'
                }}>
                    Add MainSection-creation with the chosen Folders to the task list
                </button>
                <small>Please ensure that the selected Categories have category overviews created.</small>
            </>
        );
    }
}

export default MainSection_Section