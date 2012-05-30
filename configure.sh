#/bin/bash

rm calibration.grid
reacTIVision &
sleep 0.5
REACTIVISION_WID=`xdotool search "reacTIVision" | head -1`
#xdotool windowactivate $REACTIVISION_WID

#xdotool key s		# switch to source image
#xdotool key space	# enable frame equalizer
#xdotool key i		# goto inversion options
#xdotool key Left	# disable x inversion
#sleep 0.1
#xdotool key Up
#xdotool key Left	# disable y inversion
#sleep 0.1
#xdotool key Up
#xdotool key Left	# disable angle inversion
#sleep 0.1
#xdotool key i		# exit inversion options
#xdotool key n		# switch to no source image

xdotool key --window $REACTIVISION_WID n
python main.py -f --size=1280x1024
xdotool key --window $REACTIVISION_WID $ Escape	# close reacTIVision
sleep 1
reacTIVision
