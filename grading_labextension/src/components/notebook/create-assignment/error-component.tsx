import { Notebook } from "@jupyterlab/notebook";
import { Button } from '@blueprintjs/core';
import { Cell } from '@jupyterlab/cells';
import * as React from "react";

import { Alert } from "@mui/material";


export interface ErrorComponentProps {
    err: string;
}



export const ErrorComponent = (props : ErrorComponentProps) => {
    //const alertStyle = { width: 250 };

    return (
        <Alert variant="filled" severity='error'>
        {props.err}
    </Alert>
    );
}