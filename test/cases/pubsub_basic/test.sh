port=$(../../common/find-free-port)
printf "Using port $port\n"

rm -rf artifacts
mkdir -p artifacts

printf "Starting server\n"
SPOKEPORT=$port spoke &
PID=$!
sleep 0.2
printf "Starting echo client\n"
SPOKEPORT=$port spoke-echo foo | tee artifacts/output.txt &
sleep 0.2
printf "Publishing message\n"
SPOKEPORT=$port spoke-publish foo 5 &
sleep 0.2

kill -15 $PID
wait

printf "Diffing output - <exp >got\n"
diff expected.txt artifacts/output.txt
exitcode=$?

exit $exitcode
