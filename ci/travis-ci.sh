# package to test
echo "Install Robot Framework."
sudo pip3 install -q robotframework

# packages to generate documentation
echo "Install packages to generate documentation."
sudo pip3 install -q docutils pygments

# export path to the library
echo "Export path to the HttpCtrl library."
cd src
PYTHONPATH=`pwd`
export PYTHONPATH=${PYTHONPATH}

echo "Path '$PYTHONPATH' is exported."

# run tests
echo "Run tests for HttpCtrl."
cd ../tst
python3 -m robot server_methods.robot

# generate documentation
echo "Generate documentation for HttpCtrl."
cd ../src
python3 -m robot.libdoc -v 0.1.0 -F reST HttpCtrl.Client client.html
python3 -m robot.libdoc -v 0.1.0 -F reST HttpCtrl.Server server.html
python3 -m robot.libdoc -v 0.1.0 -F reST HttpCtrl.Json json.html