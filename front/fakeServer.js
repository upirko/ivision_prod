const WebSocket = require('ws');

const wss = new WebSocket.Server({ port: 5000 });

const STREAMS = [
  {
    title: 'Парковка у ЖД вокзала',
    link: 'https://moidom.citylink.pro/pub/10493',
    source: 'https://s2.moidom-stream.ru/s/public/0000010493.m3u8',
  },
  {
    title: 'Парковка на просп. Ленина',
    link: 'https://moidom.citylink.pro/pub/10491',
    source: 'https://s2.moidom-stream.ru/s/public/0000010491.m3u8',
  },
  {
    title: 'Парковка на ул. Анохина',
    link: 'https://moidom.citylink.pro/pub/10495',
    source: 'https://s2.moidom-stream.ru/s/public/0000010495.m3u8',
  },
];

wss.on('connection', function connection(ws) {
  ws.on('message', function incoming(message) {
    console.log('received: %s', message);
  });

  ws.send(JSON.stringify({
    event: 'init',
    payload: STREAMS
  }));

  const timer = setInterval(() => {
    const c = Math.round(Math.random() * 10);
    const obj = Array(c).fill(0).map(() => ({
      x: Math.random(),
      y: Math.random(),
      width: Math.random() * 0.1,
      height: Math.random() * 0.1
    }));
    ws.send(JSON.stringify({
      event: 'update',
      payload: obj
    }));
  }, 2000);

  ws.on('close', function incoming() {
    clearInterval(timer);
  });
});