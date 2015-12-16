path.algorithm.push("RamdomWalk");

var token = 0;
var last_rssi;
var last_move; // 0 for left, 1 for right
var in_region = 0;


function RandomWalk() {

    token += 1;
    token = token % 15;
    if (token === 0) {
    
        if (drone.rssi > 0) {
            drone.acc = 100;
            if (in_region === 0) {
	        if (Math.random() > 0.5) {
                    drone.turn_left(5);
                    last_move = 0;
                }
	        else {
                    drone.turn_right(5);
                    last_move = 1;
                }
                in_region = 1;
            }
            else {
                if (drone.rssi > last_rssi) {
                    // do nothing, keep going
                }
                else {
                    if (last_move === 0) drone.turn_left(180-10*Math.random());
                    else drone.turn_right(180-10*Math.random());
                }
            }
            last_rssi = drone.rssi;
        }

        else {
            in_region = 0;
            drone.acc = 200;
                if (Math.random() > 0.5)
                    drone.turn_left(Math.random()*50);
	        else
                    drone.turn_right(Math.random()*50);
        }
    
    }
    else {
        drone.acc = 0;
    }
}
