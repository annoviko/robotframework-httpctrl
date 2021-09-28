# error codes
EXIT_CODE_INCORRECT_PATH=1
EXIT_CODE_FAILED_TESTING=2

# package to test
echo "Install Robot Framework."
pip3 install robotframework

# packages to generate documentation
echo "Install packages to generate documentation."
pip3 install docutils pygments

# export path to the library
echo "Export path to the HttpCtrl library."
cd src || exit $EXIT_CODE_INCORRECT_PATH
PYTHONPATH=`pwd`
export PYTHONPATH=${PYTHONPATH}

echo "Path '$PYTHONPATH' is exported."

# run tests
echo "Run tests for HttpCtrl."
cd ../tst || exit $EXIT_CODE_INCORRECT_PATH
python3 -m robot.run *.robot
result=$?

# check testing results
if [ $result -ne 0 ]
then
    echo "Testing results contain errors - mark build as a failure."
    exit $EXIT_CODE_FAILED_TESTING
fi

# generate documentation
echo "Generate documentation for HttpCtrl."
cd ../src || exit $EXIT_CODE_INCORRECT_PATH
python3 -m robot.libdoc -v 0.1.8 -F reST HttpCtrl.Client client.html
python3 -m robot.libdoc -v 0.1.8 -F reST HttpCtrl.Server server.html
python3 -m robot.libdoc -v 0.1.8 -F reST HttpCtrl.Json json.html
