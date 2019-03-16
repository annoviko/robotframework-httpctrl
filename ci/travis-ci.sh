# package to test
sudo pip3 install -q robotframework

# packages to generate documentation
sudo pip3 install -q docutils pygments

# export path to the library
cd src
PYTHONPATH=`pwd`
export PYTHONPATH=${PYTHONPATH}

# run tests
cd ../tst
python3 -m robot *.robot

# generate documentation
cd ../src
python3 -m robot.libdoc -v 0.1.0 -F reST HttpCtrl.Client client.html
python3 -m robot.libdoc -v 0.1.0 -F reST HttpCtrl.Server server.html
python3 -m robot.libdoc -v 0.1.0 -F reST HttpCtrl.Json json.html
