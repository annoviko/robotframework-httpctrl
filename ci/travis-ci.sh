# package to test
pip3 install -q robotframework

# packages to generate documention
pip3 install -q docutils pugments

# run tests
cd tst
python3 -m robot *.robot

# generate documention
cd ../src
python3 -m robot.libdoc -F reST HttpCtrl.Client client.html
python3 -m robot.libdoc -F reST HttpCtrl.Server server.html
python3 -m robot.libdoc -F reST HttpCtrl.Json json.html
