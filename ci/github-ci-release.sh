PATH_ROOT=`readlink -f ..`
PATH_REPO_CURRENT=`readlink -f .`
PATH_SOURCE=`readlink -f src`


# packages to generate documentation
echo "Install packages for release."
pip3 install docutils pygments twine

# Release to PyPi
python3 setup.py sdist
twine upload dist/* -r testpypi

# Create folder for the documentation
mkdir $PATH_ROOT/httpctrl-gh-pages
cd $PATH_ROOT/httpctrl-gh-pages

git clone https://github.com/annoviko/robotframework-httpctrl.git .
git checkout hg-pages

PATH_REPO_GH_PAGES=`readlink -f .`

# Generate documentation
cd $PATH_REPO_CURRENT
version=`cat config.txt`

cd $PATH_SOURCE

python3 -m robot.libdoc -v $version -F reST HttpCtrl.Client $PATH_REPO_GH_PAGES/client.html
python3 -m robot.libdoc -v $version -F reST HttpCtrl.Server $PATH_REPO_GH_PAGES/server.html
python3 -m robot.libdoc -v $version -F reST HttpCtrl.Json $PATH_REPO_GH_PAGES/json.html

# Commit and push documentation changes
cd $PATH_REPO_GH_PAGES

git push https://$HTTPCTRL_USERNAME:$HTTPCTRL_PASSWORD@github.com/annoviko/robotframework-httpctrl.git --all

