paper.install(window)
let canvas = document.getElementById("canvas")

// console.log(levelData)
let moves = 0;

$(document).ready(() => {
    paper.setup(canvas)
    reset()
})

let timer = null;

function getproject(){
    return paper.project;
}

function reset(){
    project.clear();

    if (timer != null)
        clearInterval(timer);

    let GRID = new Size(levelData.width, levelData.height)
    let BORDER = 5
    let GAP = 5

    let BORDER_SIZE = new Size(BORDER)

    let ctx = canvas.getContext("2d")

    let height = view.size.height
    let width = view.size.width

    let SQUARE = new Size((width - 2*BORDER), (height - 2*BORDER)).divide(GRID)
    let SQUARE_WIDTH = new Size(SQUARE.width, 0)
    let SQUARE_HEIGHT = new Size(0, SQUARE.height)

    let GAP_SIZE = new Size(GAP);

    let logData = [];
    let won = false;
    let uploaded = false;
    moves = 0;

    drawGrid()
    
    let borderPath = drawBorder()

    let cars = levelData.cars.map(car => drawCar(car.id, car.x, car.y, car.w, car.h, car.color))    

    
    let goalStart = new Point(width - BORDER * 0.5, BORDER + (levelData.goal == 0 ? 0 : 1)).add(SQUARE_HEIGHT.multiply(levelData.goal))
    let goal = new Path.Line(goalStart, goalStart.add(SQUARE_HEIGHT).add(new Point(0, ((levelData.goal == 0 || levelData.goal == GRID.height) ? -1 : -2))))
    goal.style = {
        strokeColor: "rgb(255, 255, 255)",
        strokeWidth: BORDER, 
    }

    let start = Date.now();

    if(!loggedIn || won) {
        goInactive();
    }

    function drawBorder(){
        let borderPath = new Path.Rectangle(new Point(BORDER_SIZE.divide(2)), view.size.subtract(BORDER_SIZE))

        borderPath.strokeColor = "black"

        borderPath.style = {
            strokeColor: "black",
            strokeWidth: BORDER
        }

        return borderPath
    }

    function drawGrid(){
        let gridPaths = [];

        let low = new Point(BORDER, 0);
        let high = new Point(BORDER, height);

        for (let i = 1; i < GRID.width; i++){
            low = low.add(SQUARE_WIDTH)
            high = high.add(SQUARE_WIDTH)

            gridPaths.push(new Path.Line(low, high))
        }


        let left = new Point(0, BORDER)
        let right = new Point(width, BORDER)

        for (let i = 1; i < GRID.height; i++){
            left = left.add(SQUARE_HEIGHT)
            right = right.add(SQUARE_HEIGHT)

            gridPaths.push(new Path.Line(left, right))
        }


        for (let path of gridPaths){
            path.strokeColor = "#777"
        }
    }

    function drawCar(gameId, x, y, w, h, color) {
        let corner = SQUARE_WIDTH.multiply(x).add(SQUARE_HEIGHT.multiply(y)).add(BORDER_SIZE).add(GAP_SIZE);
        let width = new Size(SQUARE_WIDTH.multiply(w).add(SQUARE_HEIGHT.multiply(h)).subtract(GAP_SIZE.multiply(2)));

        let car = new Path.Rectangle(corner, width);

        car.vertical = h > w;

        car.gameId = gameId;

        car.strokeColor = "#000";
        car.fillColor = color;
        car.color = color;

        car.onMouseDown = event => {
            if(!loggedIn || won) return 

            car.fillColor = "rgba(0, 0, 0, 0.7)";
            car.dragedBy = event.point.subtract(car.position)
            car.draged = true;

            car.downTime = Date.now() - start

            car.minDrag = undefined
            car.maxDrag = undefined

        }

        car.onMouseDrag = event => {
            if (!car.draged || !loggedIn || won) return
                
            let delta = event.point.subtract(car.position).subtract(car.dragedBy)
            let max = new Point(10)

            if (car.vertical) {
                delta.x = 0
                max.x = 0
                if (delta.y < 0) max.y = -max.y
            } else {
                delta.y = 0;
                max.y = 0;            
                if (delta.x < 0) max.x = -max.x
            }

            while (delta.length > 0) {
                let now = delta.clone()

                if (delta.length > max.length){
                    now = max.clone()
                    delta = delta.subtract(max)
                } else {
                    delta = delta.subtract(delta)
                }

                car.position = car.position.add(now)

                let intersectsCar = false;

                for (let other of cars){
                    if (car.gameId == other.gameId) continue;
                    intersectsCar |= car.intersects(other);
                }

                if (car.intersects(goal)){
                    won = true;
                }

                if (intersectsCar || car.intersects(borderPath)) {
                    car.position = car.position.subtract(now)

                    break
                }
            }

            let pos = 0;

            if (car.vertical){
                pos = Math.round((car.bounds.topLeft.y - BORDER) / SQUARE.width)
                // console.log((car.bounds.topLeft.y - BORDER) / SQUARE.width)
            } else {
                pos = Math.round((car.bounds.topLeft.x - BORDER) / SQUARE.height)
                // console.log((car.bounds.topLeft.x - BORDER) / SQUARE.height)
            }

            if (car.minDrag != undefined) {
                car.minDrag = Math.min(pos, car.minDrag)
            } else {
                car.minDrag = pos;
            }

            if (car.maxDrag != undefined) {
                car.maxDrag = Math.max(pos, car.maxDrag)
            } else {
                car.maxDrag = pos;
            }

            // console.log("Dragging:", car.minDrag, "-", car.maxDrag)

            if (!loggedIn || won){
                if (car.minDrag != car.maxDrag)
                    moves += 1;

                logData.push({car: car.gameId, start: car.downTime, end: Date.now() - start, pos: pos, min: car.minDrag, max: car.maxDrag})
                goInactive();
                win();
                // console.log("WIN")
            }
        }

        car.onMouseUp = event => {
            if(!loggedIn || won) return 
            
            if (car.draged){
                let points = [];

                let max = car.vertical ? GRID.height : GRID.width;

                for(let i = 0; i < max; i++){
                    let point = new Point(SQUARE_WIDTH.multiply(i).add(SQUARE_HEIGHT.multiply(i)).add(BORDER_SIZE).add(GAP_SIZE));

                    if (car.vertical)
                        point.x = car.bounds.topLeft.x
                    else 
                        point.y = car.bounds.topLeft.y

                    point.pos = i;
                    points.push(point);
                }

                let minDistance = 99999999;
                let minPoint = car.bounds.topLeft;

                for (let point of points){
                    let distance = car.bounds.topLeft.subtract(point).length;

                    if (distance <= minDistance){
                        minDistance = distance;
                        minPoint = point;
                    }
                }

                car.bounds.topLeft = minPoint;
                
                if (car.minDrag != car.maxDrag)
                    moves += 1;
                
                if (car.minDrag == undefined)
                    car.minDrag = minPoint.pos 

                if (car.maxDrag == undefined)
                    car.maxDrag = minPoint.pos 


                logData.push({car: car.gameId, start: car.downTime, end: Date.now() - start, pos: minPoint.pos, min: car.minDrag, max: car.maxDrag})
                updateUI();
            }

            car.fillColor = car.color;
            car.draged = false;
        }

        return car;
    }


    function goInactive() {
        let inactive = new Path.Rectangle(new Point(0, 0), view.size)
        inactive.fillColor = "rgba(220, 220, 220, 0.7)"
    }

    function win(){
        let text = new paper.PointText(view.size.divide(2))
        text.content = "You won !"
        text.justification = "center"
        text.fontSize = 20

        if (timer != null)
            clearInterval(timer);
        
        updateUI();

        upload(true)
    }

    function upload(sync) {
        console.log(logData)
        
        $.ajax({
            type:"POST",
            url: window.location.href, 
            async: sync,
            data: {"data": JSON.stringify(logData), "time": Date.now() - start, "won": won, "csrfmiddlewaretoken": csfr}
        })

        uploaded = true;
    }

    timer = setInterval(updateUI, 1000)
    updateUI();

    function updateUI(){
        $(".level-moves").html(moves)

        let time = (Date.now() - start) / 1000;
        $(".level-time.minutes").html(Math.floor(time / 60))

        let seconds = "" + Math.floor(time % 60);
        if (seconds.length < 2) seconds = "0" + seconds;

        $(".level-time.seconds").html(seconds)
    }

    window.onbeforeunload = function(){
        if (uploaded == false) {
            upload(false);
        }
    };
}