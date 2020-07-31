import React, {Component} from "react";
import NavigationPage from "../components/NavigationPage";

class InspectionStart extends Component {

    items = [
        {
            id: 0,
            link: '/IndividualInspection',
            title: 'Inspect data on individual Tags',
            description: 'You can do a lot of stuff here'
        },
        {
            id: 1,
            link: '/ComparisonInspection',
            title: 'Inspect comparisons',
            description: 'You can do a lot of stuff here'
        },
    ]

    render() {
        return (
            <NavigationPage items={this.items}/>
        );
    }
}

export default InspectionStart;
