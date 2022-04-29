import * as React from 'react';
import {useEffect} from 'react';
import {Assignment} from '../../../model/assignment';
import {Lecture} from '../../../model/lecture';
import {
  generateAssignment,
  pullAssignment,
  pushAssignment,
  updateAssignment
} from '../../../services/assignments.service';
import GetAppRoundedIcon from '@mui/icons-material/GetAppRounded';
import {AgreeDialog, CommitDialog} from '../../util/dialog';
import {
  Box,
  Button,
  Card,
  CardActions,
  CardContent,
  CardHeader,
  Grid,
  IconButton,
  Tab,
  Tabs,
  Tooltip,
  Typography
} from '@mui/material';
import ReplayIcon from '@mui/icons-material/Replay';
import OpenInBrowserIcon from '@mui/icons-material/OpenInBrowser';
import TerminalIcon from '@mui/icons-material/Terminal';
import {FilesList} from '../../util/file-list';
import {GlobalObjects} from '../../../index';
import {Contents} from '@jupyterlab/services';
import moment from 'moment';
import {openBrowser, openTerminal} from "./util";
import {PageConfig} from "@jupyterlab/coreutils";
import PublishRoundedIcon from "@mui/icons-material/PublishRounded";
import {getRemoteStatus} from "../../../services/file.service";
import {RepoType} from "../../util/repo-type";

export interface IFilesProps {
  lecture: Lecture;
  assignment: Assignment;
  onAssignmentChange: (assignment: Assignment) => void;
  showAlert: (severity: string, msg: string) => void;
}

export const Files = (props: IFilesProps) => {
  const [assignment, setAssignment] = React.useState(props.assignment);
  const [lecture, setLecture] = React.useState(props.lecture);
  const [selectedDir, setSelectedDir] = React.useState('source');
  const [showDialog, setShowDialog] = React.useState(false);
  const [dialogContent, setDialogContent] = React.useState({
    title: '',
    message: '',
    handleAgree: null,
    handleDisagree: null
  });
  const [reloadFilesToggle, setReloadFiles] = React.useState(false);

  const [repoStatus, setRepoStatus] = React.useState(null as "up_to_date" | "pull_needed" | "push_needed" | "divergent");

  const [srcChangedTimestamp, setSrcChangeTimestamp] = React.useState(moment().valueOf()); // now
  const [generateTimestamp, setGenerateTimestamp] = React.useState(null);

  const serverRoot = PageConfig.getOption('serverRoot');

  useEffect(() => {
    const srcPath = `source/${lecture.code}/${assignment.id}`;
    GlobalObjects.docManager.services.contents.fileChanged.connect(
      (sender: Contents.IManager, change: Contents.IChangedArgs) => {
        const {oldValue, newValue} = change;
        if (!newValue.path.includes(srcPath)) {
          return;
        }

        const modified = moment(newValue.last_modified).valueOf();
        if (srcChangedTimestamp === null || srcChangedTimestamp < modified) {
          setSrcChangeTimestamp(modified);
          console.log('New source file changed timestamp: ' + modified);
        }
      },
      this
    );

    getRemoteStatus(lecture, assignment, RepoType.SOURCE).then(status => {
      setRepoStatus(status as "up_to_date" | "pull_needed" | "push_needed" | "divergent");
    });
  }, [props]);

  const reloadFiles = () => {
    setReloadFiles(!reloadFilesToggle);
    getRemoteStatus(lecture, assignment, RepoType.SOURCE).then(status => {
      setRepoStatus(status as "up_to_date" | "pull_needed" | "push_needed" | "divergent");
    });
  }

  const handleSwitchDir = async (dir: 'source' | 'release') => {
    if (dir === 'release') {
      if (
        generateTimestamp === null ||
        generateTimestamp < srcChangedTimestamp
      ) {
        try {
          await generateAssignment(lecture.id, assignment);
        } catch (err) {
          props.showAlert('error', 'Error Generating Assignment');
          return;
        }
        setGenerateTimestamp(moment().valueOf());
      }
    }
    setSelectedDir(dir);
  };

  const closeDialog = () => setShowDialog(false);

  const handlePushAssignment = async (commitMessage: string) => {
    setDialogContent({
      title: 'Push Assignment',
      message: `Do you want to push ${assignment.name}? This updates the state of the assignment on the server with your local state.`,
      handleAgree: async () => {
        try {
          // Note: has to be in this order (release -> source)
          await pushAssignment(lecture.id, assignment.id, 'release');
          await pushAssignment(
            lecture.id,
            assignment.id,
            'source',
            commitMessage
          );
        } catch (err) {
          props.showAlert('error', 'Error Pushing Assignment');
          closeDialog();
          return;
        }
        const a = assignment;
        a.status = 'pushed';
        updateAssignment(lecture.id, a).then(
          assignment => {
            setAssignment(assignment);
            props.showAlert('success', 'Successfully Pushed Assignment');
            props.onAssignmentChange(assignment);
          },
          error => props.showAlert('error', 'Error Updating Assignment')
        );
        closeDialog();
      },
      handleDisagree: () => closeDialog()
    });
    setShowDialog(true);
  };

  const getRemoteStatusText = (status: "up_to_date" | "pull_needed" | "push_needed" | "divergent") => {
    if (status == "up_to_date") {
      return "The local files are up to date with the remote repository."
    } else if (status == "pull_needed") {
      return "The remote repository has new changes. Pull now to load them."
    } else if (status == "push_needed") {
      return "You have made changes to your local repository which you can push."
    } else {
      return "The local and remote files are divergent."
    }
  }

  const handlePullAssignment = async () => {
    setDialogContent({
      title: 'Pull Assignment',
      message: `Do you want to pull ${assignment.name}? This updates your assignment with the state of the server and overwrites all changes.`,
      handleAgree: async () => {
        try {
          await pullAssignment(lecture.id, assignment.id, 'source');
          props.showAlert('success', 'Successfully Pulled Assignment');
        } catch (err) {
          props.showAlert('error', 'Error Pulling Assignment');
        }
        reloadFiles();
        closeDialog();
      },
      handleDisagree: () => closeDialog()
    });
    setShowDialog(true);
  };

  return (
    <Card elevation={3}>
      <CardHeader
        title="Files"
        action={
          <Grid container>
            <Grid item>
              <Tooltip title="Reload">
                <IconButton
                  aria-label="reload"
                  onClick={() => reloadFiles()}
                >
                  <ReplayIcon/>
                </IconButton>
              </Tooltip>
            </Grid>
          </Grid>
        }
      />

      <CardContent sx={{height: '270px', overflowY: 'auto'}}>
        <Typography>{getRemoteStatusText(repoStatus)}</Typography>
        <Tabs
          variant="fullWidth"
          value={selectedDir}
          onChange={(e, dir) => handleSwitchDir(dir)}
        >
          <Tab label="Source" value="source"/>
          <Tab label="Release" value="release"/>
        </Tabs>
        <Box height={214} sx={{overflowY: 'auto'}}>
          <FilesList
            path={`${selectedDir}/${props.lecture.code}/${props.assignment.id}`}
            reloadFiles={reloadFilesToggle}
            showAlert={props.showAlert}
          />
        </Box>
      </CardContent>
      <CardActions>
        <CommitDialog handleCommit={msg => handlePushAssignment(msg)}>
          <Button sx={{mt: -1}} variant="outlined" size="small"
                  color={repoStatus === "pull_needed" || repoStatus === "divergent" ? "error" : "primary"}>
            <PublishRoundedIcon fontSize="small" sx={{mr: 1}}/>
            Commit
          </Button>
        </CommitDialog>
        <Button
          color={repoStatus === "push_needed" || repoStatus === "divergent" ? "error" : "primary"}
          sx={{mt: -1, ml: 2}}
          onClick={() => handlePullAssignment()}
          variant="outlined"
          size="small"
        >
          <GetAppRoundedIcon fontSize="small" sx={{mr: 1}}/>
          Pull
        </Button>
        <Tooltip title={"Show in File-Browser"}>
          <IconButton
            sx={{mt: -1, pt: 0, pb: 0}}
            color={"primary"}
            onClick={() => openBrowser(`${selectedDir}/${lecture.code}/${assignment.id}`, props.showAlert)}>
            <OpenInBrowserIcon/>
          </IconButton>
        </Tooltip>
        <Tooltip title={"Open in Terminal"}>
          <IconButton
            sx={{mt: -1, pt: 0, pb: 0}}
            color={"primary"}
            onClick={() => openTerminal(`${serverRoot}/${selectedDir}/${lecture.code}/${assignment.id}`, props.showAlert)}>
            <TerminalIcon/>
          </IconButton>
        </Tooltip>
      </CardActions>
      <AgreeDialog open={showDialog} {...dialogContent} />
    </Card>
  );
};
