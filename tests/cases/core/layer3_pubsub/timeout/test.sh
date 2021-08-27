set -e
rm -rf artifacts
mkdir -p artifacts

port=$(../../../../common/find-free-port)

printf "Starting client on $port and waiting for timeout\n"
SPOKEPORT=$port python publish.py > artifacts/output.txt

printf "Diffing output - <got >exp\n"
diff -r artifacts expected
exitcode=$?

exit $exitcode
