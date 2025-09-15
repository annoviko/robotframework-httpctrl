PATH_ROOT=`readlink -f ..`
PATH_REPO_CURRENT=`readlink -f .`
PATH_SOURCE=`readlink -f src`


# Configure git to push changes
echo "[INFO] Configure git to commit and push changes."

git config --global user.email $HTTPCTRL_EMAIL
git config --global user.name $HTTPCTRL_USERNAME


# Read version
version=`cat VERSION`


# Create folder for the documentation
echo "[INFO] Clone repository to update documentation."

mkdir $PATH_ROOT/httpctrl-gh-pages
cd $PATH_ROOT/httpctrl-gh-pages

git clone https://github.com/annoviko/robotframework-httpctrl.git .
git checkout gh-pages

PATH_REPO_GH_PAGES=`readlink -f .`


# Generate documentation
echo "[INFO] Generate documentation."

cd $PATH_SOURCE

python3 -m robot.libdoc -v $version -F reST HttpCtrl.Client $PATH_REPO_GH_PAGES/client.html
python3 -m robot.libdoc -v $version -F reST HttpCtrl.Server $PATH_REPO_GH_PAGES/server.html
python3 -m robot.libdoc -v $version -F reST HttpCtrl.Json $PATH_REPO_GH_PAGES/json.html
python3 -m robot.libdoc -v $version -F reST HttpCtrl.Logging $PATH_REPO_GH_PAGES/logging.html


# Commit and push documentation changes
echo "[INFO] Upload the documentation."

cd $PATH_REPO_GH_PAGES

echo "[INFO] Update version on the main page."
sed -i -e "s/<b>Version:<\/b> [0-9]*\.[0-9]*\.[0-9]*/<b>Version:<\/b> $version/g" index.html

git commit . -m "[ci][release] Upload documentation."
if [ $? -ne 0 ]; then
    echo "[ERROR] Impossible to release the documentation (reason: commit new documentation failed)."
    exit -1
fi

git push https://$HTTPCTRL_USERNAME:$HTTPCTRL_PASSWORD@github.com/annoviko/robotframework-httpctrl.git --all

if [ $? -ne 0 ]; then
    echo "[ERROR] Impossible to release the documentation (reason: pushing new documentation failed)."
    exit -1
fi