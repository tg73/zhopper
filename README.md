Quick&dirty stuff to test z inaccuracies. Do not judge the code, this is more like scratchpad

#terminal 1:
#create probe test gcode

#start collecting the responses
% ./gcode_response_spy.py --host ratos2.local>> ~/tmp/r4.out

#follow the gcode

terminal 2:
tail -f ~/tmp/r4.out

#select lines & convert & send to influxdb
# use a custom writer to avoid buffering

terminal 3:
% tail -f  ~/tmp/r4.out|./convert_to_influx.py --measurement probe --result-header "// Result is" --tag "printer=vc4-400" |./influx_write_by_line.py --bucket r3

#start test print for probe accuracy, for example upload with mainsail

