xterm -e "roscore" &
sleep 5
xterm -e "rosparam load $1" &
sleep 2
xterm -e "rosrun mrpp_sumo sumo_wrapper.py" &
sleep 3
# xterm -e "rosrun mrpp_sumo tpbp_basic.py" &
xterm -e "rosrun mrpp_sumo tpbp_v1_thread.py" &
sleep 2
xterm -e "rosrun mrpp_sumo record_data.py" &
sleep 2
xterm -e "rosrun mrpp_sumo command_center.py" 
sleep 5
killall xterm & sleep 10
