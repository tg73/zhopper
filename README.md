Quick&dirty stuff to test z inaccuracies. 
Provides tools to create a test file that the user will print, and the tools to collect the gcode output, convert to influxdb line format and send to influxdb.

terminal 1:
Create probe test gcode file, z.gcode

`./genprobeaccuracy.py --count 100`

Start collecting the responses:

`./gcode_response_spy.py --host ratos2.local>> ~/tmp/r4.out`

Follow the gcode
terminal 2:

`tail -f ~/tmp/r4.out`

Select lines & convert & send to influxdb
Use a custom writer to avoid buffering
terminal 3:

`tail -f  ~/tmp/r4.out|./convert_to_influx.py --measurement probe --result-header "// Result is" --tag "printer=vc4-400" |./influx_write_by_line.py --bucket r3`

Start test print for probe accuracy, for example upload with mainsail
Check results in influxdb

