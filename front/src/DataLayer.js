import { useRef, useEffect } from 'react';
import { makeStyles } from '@material-ui/core/styles';

const useStyles = makeStyles((theme) => ({
    canvas: {
        position: 'absolute',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%'
    }
}));

export default function DataLayer({ area, objects, onClick }) {
    const canvasRef = useRef();
    const classes = useStyles();
    const areaColor = 'rgba(0, 255, 0, 0.3)';
    const strokeColor = 'rgba(0, 255, 0, 1)';
    const pointSize = 10;

    function drawArea(ctx, area) {
        ctx.beginPath();
        area.forEach(([x, y], i) => {
            const fn = i ? 'lineTo' : 'moveTo';
            ctx[fn](x, y);
        });
        ctx.closePath();
    
        ctx.fillStyle = areaColor;
        ctx.fill();
        ctx.strokeStyle = strokeColor;
        ctx.stroke();
    
        ctx.fillStyle = strokeColor;
        area.forEach(([x, y]) => {
            ctx.fillRect(x - pointSize / 2, y - pointSize / 2, pointSize, pointSize);
        });
    }

    function drawObject(ctx, obj) {
        ctx.strokeStyle = strokeColor;
        ctx.strokeRect(obj.x, obj.y, obj.width, obj.height);
    }

    useEffect(() => {
        const canvas = canvasRef.current;
        const { width, height } = canvas.getBoundingClientRect();

        canvas.width = width;
        canvas.height = height;
        
        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, width, height);

        drawArea(ctx, area.map(point => [point[0] * width, point[1] * height]));
        objects.forEach(obj => {
            obj.x *= width;
            obj.y *= height;
            obj.width *= width;
            obj.height *= height;
            drawObject(ctx, obj);
        });
        
    }, [ area, objects ]);
    

    return <canvas ref={canvasRef} className={classes.canvas} onClick={onClick}/>;
}