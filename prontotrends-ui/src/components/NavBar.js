import React, {useState} from "react";
import {NavLink} from "react-router-dom";


const NavSideBar = ({items}) => {
    return (
        <div style={{flex: 1, minWidth: '100%', backgroundColor: '#274964', color: 'white', borderRight: '10px white'}}>
            <ul style={{
                listStyle: 'none',
                textAlign: 'left',
                margin: 0,
                marginBlockStart: 0,
                paddingInlineStart: 0,
                lineHeight: '2rem',
                padding: '1rem'
            }}>
                {items.map((item, ind) => <NavItem
                    key={ind} item={item}/>)}
            </ul>
        </div>
    )
}

export default NavSideBar;

const NavItem = ({item}) => {
    let [open, setOpen] = useState(false);
    let hasChildren = (item.children);
    let children = (hasChildren) ? (<ul style={styles.ul}>{item.children.map((child, ind) => <NavItem
        key={ind} item={child}/>)}</ul>) : null;
    return (
        <li>
            <NavLink
                to={item.link}>{item.title}</NavLink><p onClick={() => setOpen(!open)}>{hasChildren && '🔽'}</p>
            {open && children}
        </li>
    )
}

const styles = {
    ul: {
        margin: 0,
        listStyle: 'none',
        paddingInlineStart: '10%',
        fontSize: '90%',
        lineHeight: '1.7'
    }
}