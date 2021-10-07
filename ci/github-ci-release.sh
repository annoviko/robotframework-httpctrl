PATH_ROOT=`readlink -f ..`
PATH_REPO_CURRENT=`readlink -f .`
PATH_SOURCE=`readlink -f src`

HTTPCTRL_USERNAME=${{ secrets.HTTPCTRL_USERNAME }}
HTTPCTRL_PASSWORD=${{ secrets.HTTPCTRL_PASSWORD }}
TWINE_USERNAME=${{ secrets.TWINE_USERNAME }}
TWINE_PASSWORD=${{ secrets.TWINE_PASSWORD }}

# packages to generate documentation
echo "Install packages for release."
pip3 install robotframework docutils pygments twine

# Release to PyPi
python3 setup.py sdist
twine upload dist/* -r testpypi
if [ $? -ne 0 ]; then
    echo "Impossible to release the library to PyPi."
    return -1
fi

# Create folder for the documentation
echo "Clone repository to update documentation."

mkdir $PATH_ROOT/httpctrl-gh-pages
cd $PATH_ROOT/httpctrl-gh-pages

git clone https://github.com/annoviko/robotframework-httpctrl.git .
git checkout gh-pages

PATH_REPO_GH_PAGES=`readlink -f .`

# Generate documentation
echo "Generate documentation."

cd $PATH_REPO_CURRENT
version=`cat config.txt`

cd $PATH_SOURCE

python3 -m robot.libdoc -v $version -F reST HttpCtrl.Client $PATH_REPO_GH_PAGES/client.html
python3 -m robot.libdoc -v $version -F reST HttpCtrl.Server $PATH_REPO_GH_PAGES/server.html
python3 -m robot.libdoc -v $version -F reST HttpCtrl.Json $PATH_REPO_GH_PAGES/json.html

# Commit and push documentation changes
echo "Upload the documentation."

cd $PATH_REPO_GH_PAGES

git push https://$HTTPCTRL_USERNAME:$HTTPCTRL_PASSWORD@github.com/annoviko/robotframework-httpctrl.git --all

