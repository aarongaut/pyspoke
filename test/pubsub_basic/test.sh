port=9253
mkdir -p artifacts

SPOKEPORT=$port spoke &
PID=$!
sleep 0.2
SPOKEPORT=$port spoke-echo foo | tee artifacts/output.txt &
sleep 0.2
SPOKEPORT=$port spoke-publish foo 5 &
sleep 0.2

kill -15 $PID
wait

printf "Diffing output - <exp >got\n"
diff expected.txt artifacts/output.txt
exitcode=$?

exit $exitcode
