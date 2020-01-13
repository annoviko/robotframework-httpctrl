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

# upload artifats
echo "Upload artifats to cloud."
cd ../

PROJECT_NAME=robotframework-httpctrl
python3 ci/cloud $CLOUD_TOKEN mkdir /$PROJECT_NAME
python3 ci/cloud $CLOUD_TOKEN mkdir /$PROJECT_NAME/$TRAVIS_BRANCH
python3 ci/cloud $CLOUD_TOKEN mkdir /$PROJECT_NAME/$TRAVIS_BRANCH/$TRAVIS_BUILD_NUMBER

ARTIFACT_FILEPATH=/$PROJECT_NAME/$TRAVIS_BRANCH/$TRAVIS_BUILD_NUMBER

python3 ci/cloud $CLOUD_TOKEN upload tst/report.html $ARTIFACT_FILEPATH/report.html
python3 ci/cloud $CLOUD_TOKEN upload tst/output.xml $ARTIFACT_FILEPATH/output.xml
python3 ci/cloud $CLOUD_TOKEN upload tst/log.html $ARTIFACT_FILEPATH/log.html

# check testing results
result=$?
if [ $result -ne 0 ]
then
    echo "Testing results contain errors - mark build as a failure."
    exit $EXIT_CODE_FAILED_TESTING
fi

# generate documentation
echo "Generate documentation for HttpCtrl."
cd src || exit $EXIT_CODE_INCORRECT_PATH
python3 -m robot.libdoc -v 0.1.5 -F reST HttpCtrl.Client client.html
python3 -m robot.libdoc -v 0.1.5 -F reST HttpCtrl.Server server.html
python3 -m robot.libdoc -v 0.1.5 -F reST HttpCtrl.Json json.html
