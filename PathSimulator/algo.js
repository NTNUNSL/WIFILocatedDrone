path.algorithm.push("RamdomWalk");

var token = 0;
var last_rssi;
var last_move;



function RandomWalk() {

    token += 1;
    token = token % 30;
    if (token === 0) {
    
        if (drone.rssi > 0) {
            drone.acc = 100;
	    if (Math.random() > 0.5)
                drone.turn_left(5);
	    else
                drone.turn_right(5);
        }

        else {
            drone.acc = 200;
                if (Math.random() > 0.5)
                    drone.turn_left(Math.random()*30);
	        else
                    drone.turn_right(Math.random()*30);
        }
    
    }
    else {
        drone.acc = 0;
    }
}
