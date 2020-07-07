import React, {Component} from "react";
import NavigationPage from "../components/NavigationPage";

class ValidationStart extends Component {
    constructor(props) {
        super(props);
    }

    items = [
        {
            id: 0,
            link: '/ValidationSetup',
            title: 'Prepare the rules for Validation',
            description: 'You can do a lot of stuff here'
        },
        {
            id: 1,
            link: '/Validation',
            title: 'Validate files for upload',
            description: 'You can do a lot of stuff here'
        },
    ]

    render() {
        return (
            <NavigationPage items={this.items}/>
        );
    }
}

export default ValidationStart;
