set -e
rm -rf artifacts
mkdir -p artifacts

printf "Starting test script\n"
python test.py >& artifacts/output.txt &
PID=$!
sleep 0.2

printf "Sending SIGTERM to test script\n"
kill -15 $PID

printf "Waiting for test script to shut down\n"
wait

printf "Diffing output - <got >exp\n"
diff -r artifacts expected
exitcode=$?

exit $exitcode

