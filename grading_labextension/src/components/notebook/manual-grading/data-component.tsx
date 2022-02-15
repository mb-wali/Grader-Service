import * as React from 'react';
import { Cell } from '@jupyterlab/cells';
import { Box, Divider, Grid, Typography } from '@mui/material';
import { CellModel } from '../model';
import { GradeBook } from '../../../services/gradebook';


export interface DataComponentProps {
    cell: Cell;
    gradebook: GradeBook;
    nbname: string;

}

export const DataComponent = (props: DataComponentProps) => {
    const nbgraderData = CellModel.getNbgraderData(props.cell.model.metadata);
    const toolData = CellModel.newToolData(nbgraderData, props.cell.model.type);

    const gradableCell = (toolData.type !== "readonly" && toolData.type !== "solution" && toolData.type !== "");

    return (
        <Box>
            <Divider />
            <Box sx={{ mt: 2, mb: 1, ml: 3 }}>
                <Grid container spacing={2}>
                    <Grid item>
                        <Typography>Type: {toolData.type}</Typography>
                    </Grid>

                    <Grid item>
                        <Typography>ID: {toolData.id}</Typography>
                    </Grid>

                    {toolData.type === "tests" &&
                        <Grid item>
                            <Typography>Autograded Points: {props.gradebook.getAutoGradeScore(props.nbname, toolData.id)}</Typography>
                        </Grid>
                    }

                    {gradableCell &&
                        <Grid item>
                            <Typography>Max Points: {toolData.points}</Typography>
                        </Grid>
                    }
                </Grid>
            </Box>
        </Box>
    );
}
