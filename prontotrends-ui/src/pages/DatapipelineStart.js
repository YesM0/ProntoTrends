import React, {Component} from "react";
import NavigationPage from "../components/NavigationPage";

class DatapipelineStart extends Component {

    items = [
        {
            id: 0,
            link: '/InputSetup',
            title: 'Prepare Inputs for Scraping',
            description: 'You can do a lot of stuff here'
        },
        {
            id: 1,
            link: '/Scraping',
            title: 'Prepare Inputs for Scraping',
            description: 'You can do a lot of stuff here'
        },
        {
            id: 2,
            link: '/Summarize',
            title: 'Scrape new Data',
            description: 'You can do a lot of stuff here'
        },
        {
            id: 3,
            link: '/FinalCSVs',
            title: 'Generate final CSVs',
            description: 'You can do a lot of stuff here'
        },
        {
            id: 4,
            link: '/ValidationStart',
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
