import React, {Component} from "react";
import NavigationPage from "../components/NavigationPage";

class DatapipelineStart extends Component {

    items = [
        {
            id: 0,
            link: '/Datapipeline-InputSetup',
            title: 'Prepare Inputs for Scraping',
            description: 'You can do a lot of stuff here'
        },
        {
            id: 1,
            link: '/Datapipeline-Scraping',
            title: 'Prepare Inputs for Scraping',
            description: 'You can do a lot of stuff here'
        },
        {
            id: 3,
            link: '/Datapipeline-FinalCsvGeneration',
            title: 'Generate final CSVs',
            description: 'You can do a lot of stuff here'
        },
        {
            id: 4,
            link: '/Datapipeline-Validation',
            title: 'Validate created files pre-upload',
            description: 'You can do a lot of stuff here'
        },

    ]

    render() {
        return (
            <NavigationPage items={this.items}/>
        );
    }
}

export default DatapipelineStart;
