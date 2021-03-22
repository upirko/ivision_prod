import React, { useState, useEffect } from 'react';
import { makeStyles } from '@material-ui/core/styles';
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import Button from '@material-ui/core/Button';
import Container from '@material-ui/core/Container';
import CircularProgress from '@material-ui/core/CircularProgress';
import Grid from '@material-ui/core/Grid';
import Paper from '@material-ui/core/Paper';

import VideoPlayer from './VideoPlayer';
import DataLayer from './DataLayer';
import useWebSocket from 'react-use-websocket';

const useStyles = makeStyles((theme) => ({
  loader: {
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)'
  },
  root: {
    display: 'flex',
  },
  appBar: {
    width: '100%',
  },
  appBarSpacer: theme.mixins.toolbar,
  title: {
    flexGrow: 1,
  },
  content: {
    flexGrow: 1,
    height: '100vh',
    overflow: 'auto',
  },
  container: {
    paddingTop: theme.spacing(4),
    paddingBottom: theme.spacing(4),
  },
  menuButton: {
    marginRight: theme.spacing(2)
  },
  paper: {
    padding: theme.spacing(2)
  },
  videoContainer: {
    position: 'relative'
  }
}));
const WS_URL = `ws://${window.location.hostname}:5000`;

export default function Dashboard() {
  const classes = useStyles();
  const [activeStream, setActiveStream] = useState();
  const [streams, setStreams] = useState([]);
  const [objects, setObjects] = useState([]);
  const [showArea, setShowArea] = useState();

  const {
    sendJsonMessage,
    lastJsonMessage,
  } = useWebSocket(WS_URL);

  const onClick = (e) => {
    if (!window.debugMode) {
      return;
    }
    const rect = e.target.getBoundingClientRect();
    const point = [
      (e.clientX - rect.left) / rect.width,
      (e.clientY - rect.top) / rect.height,
    ];
    console.log(point);
  }

  useEffect(() => {
    if (!lastJsonMessage) {
      return;
    }
    switch (lastJsonMessage.event) {
      case 'init':
        setStreams(lastJsonMessage.payload);
        break;
      case 'update':
        setObjects(lastJsonMessage.payload);
        break;
      default:
    }
  }, [lastJsonMessage]);

  useEffect(() => {
    if (!streams.length) {
      return 
    }
    setActiveStream(streams[0]);
  }, [streams]);

  useEffect(() => {
    if (!activeStream) {
      return;
    }
    const i = streams.findIndex(s => s === activeStream);
    if (i === -1) {
      return;
    }
    sendJsonMessage({
      event: 'changeStream',
      payload: streams.findIndex(s => s === activeStream)
    });
    setObjects([]);
  }, [activeStream, sendJsonMessage])

  return (
    <React.Fragment>
    { !activeStream ? 
      <div className={classes.loader}>
        <CircularProgress />
      </div> :
      <div className={classes.root}>
        <AppBar className={classes.appBar}>
          <Toolbar className={classes.toolbar}>
            {streams.map((s, i) => (
              <Button
                key={i}
                className={classes.menuButton}
                variant="contained"
                color={activeStream === s ? 'secondary' : 'default'}
                onClick={() => setActiveStream(s)}
              >{s.title}</Button>
            ))}
          </Toolbar>
        </AppBar>
        <main className={classes.content}>
          <div className={classes.appBarSpacer} />
          <Container maxWidth="lg" className={classes.container}>
            <Grid container spacing={3}>
              <Grid item xs={8}>
                <div className={classes.videoContainer}>
                  <VideoPlayer videoSrc={activeStream.source}/>
                  <DataLayer area={showArea ? activeStream.roi : []} objects={objects} onClick={onClick}/>
                </div>
              </Grid>
              <Grid item xs={4}>
                <Paper className={classes.paper}>
                  <h3>
                    <a href={activeStream.link} target="_blank" rel="noreferrer">Страница камеры</a>
                  </h3>
                  <p>
                    <label>Кол-во автомобилей на парковке:</label> <b>{objects.length}</b>
                  </p>
                  <p>
                    <label>Кол-во свободных мест на парковке:</label> <b>{Math.max(activeStream.max_count - objects.length, 0)}</b>
                  </p>
                  <button onClick={() => setShowArea(!showArea)}>
                    {showArea ? 'Скрыть' : 'Показать'} область парковки
                  </button>
                </Paper>
              </Grid>
            </Grid>
          </Container>
        </main>
      </div>
    }
    </React.Fragment>
  );
}