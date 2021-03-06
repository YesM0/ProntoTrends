import React, {Component} from 'react'
import MaterialTable, {Column} from "material-table";
import {forwardRef} from 'react';

import AddBox from '@material-ui/icons/AddBox';
import ArrowDownward from '@material-ui/icons/ArrowDownward';
import Check from '@material-ui/icons/Check';
import ChevronLeft from '@material-ui/icons/ChevronLeft';
import ChevronRight from '@material-ui/icons/ChevronRight';
import Clear from '@material-ui/icons/Clear';
import DeleteOutline from '@material-ui/icons/DeleteOutline';
import Edit from '@material-ui/icons/Edit';
import FilterList from '@material-ui/icons/FilterList';
import FirstPage from '@material-ui/icons/FirstPage';
import LastPage from '@material-ui/icons/LastPage';
import Remove from '@material-ui/icons/Remove';
import SaveAlt from '@material-ui/icons/SaveAlt';
import Search from '@material-ui/icons/Search';
import ViewColumn from '@material-ui/icons/ViewColumn';

// icon types
import {Icons} from "material-table";

const tableIcons: Icons = {
    Add: forwardRef((props, ref) => <AddBox {...props} ref={ref}/>),
    Check: forwardRef((props, ref) => <Check {...props} ref={ref}/>),
    Clear: forwardRef((props, ref) => <Clear {...props} ref={ref}/>),
    Delete: forwardRef((props, ref) => <DeleteOutline {...props} ref={ref}/>),
    DetailPanel: forwardRef((props, ref) => <ChevronRight {...props} ref={ref}/>),
    Edit: forwardRef((props, ref) => <Edit {...props} ref={ref}/>),
    Export: forwardRef((props, ref) => <SaveAlt {...props} ref={ref}/>),
    Filter: forwardRef((props, ref) => <FilterList {...props} ref={ref}/>),
    FirstPage: forwardRef((props, ref) => <FirstPage {...props} ref={ref}/>),
    LastPage: forwardRef((props, ref) => <LastPage {...props} ref={ref}/>),
    NextPage: forwardRef((props, ref) => <ChevronRight {...props} ref={ref}/>),
    PreviousPage: forwardRef((props, ref) => <ChevronLeft {...props} ref={ref}/>),
    ResetSearch: forwardRef((props, ref) => <Clear {...props} ref={ref}/>),
    Search: forwardRef((props, ref) => <Search {...props} ref={ref}/>),
    SortArrow: forwardRef((props, ref) => <ArrowDownward {...props} ref={ref}/>),
    ThirdStateCheck: forwardRef((props, ref) => <Remove {...props} ref={ref}/>),
    ViewColumn: forwardRef((props, ref) => <ViewColumn {...props} ref={ref}/>)
};


interface EditableTableProps<RowData extends object> {
    initial_columns: Array<Column<RowData>>,
    title: string,
    data: Array<RowData>,
    handleDataChange: (data: RowData[]) => void
}

const timeoutDuration = 10;

class EditableTableClass extends Component<EditableTableProps<any>, Readonly<any>> {

    render() {
        return (
        <>
            <MaterialTable
                style={{fontSize: '1rem', fontFamily: 'inherit'}}
                title={this.props.title}
                columns={this.props.initial_columns}
                data={this.props.data}
                icons={tableIcons}
                options={{
                    search: false,
                    sorting: false,
                    draggable: false,
                    pageSize: 10
                }}
                editable={{
                    onRowAdd: newData =>
                        new Promise((resolve, reject) => {
                            setTimeout(() => {
                                this.props.handleDataChange([...this.props.data, newData]);

                                resolve();
                            }, timeoutDuration)
                        }),
                    onRowUpdate: (newData, oldData) =>
                        new Promise((resolve, reject) => {
                            setTimeout(() => {
                                const dataUpdate = [...this.props.data];
                                const index = oldData.tableData.id;
                                dataUpdate[index] = newData;
                                this.props.handleDataChange([...dataUpdate]);

                                resolve();
                            }, timeoutDuration)
                        }),
                    onRowDelete: oldData =>
                        new Promise((resolve, reject) => {
                            setTimeout(() => {
                                const dataDelete = [...this.props.data];
                                const index = oldData.tableData.id;
                                dataDelete.splice(index, 1);
                                this.props.handleDataChange([...dataDelete]);

                                resolve()
                            }, timeoutDuration)
                        }),
                }}
            />
        </>
    );
    }
}

export default EditableTableClass
