# package to test
echo "Install Robot Framework."
sudo pip install -q robotframework-python3

# packages to generate documentation
echo "Install packages to generate documentation."
sudo pip install -q docutils pygments

# export path to the library
echo "Export path to the HttpCtrl library."
cd src
PYTHONPATH=`pwd`
export PYTHONPATH=${PYTHONPATH}

echo "Path '$PYTHONPATH' is exported."

# run tests
echo "Run tests for HttpCtrl."
cd ../tst
python -m robot *.robot

# generate documentation
echo "Generate documentation for HttpCtrl."
cd ../src
python3 -m robot.libdoc -v 0.1.0 -F reST HttpCtrl.Client client.html
python3 -m robot.libdoc -v 0.1.0 -F reST HttpCtrl.Server server.html
python3 -m robot.libdoc -v 0.1.0 -F reST HttpCtrl.Json json.html
