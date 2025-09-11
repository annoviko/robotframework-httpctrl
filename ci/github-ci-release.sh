PATH_ROOT=`readlink -f ..`
PATH_REPO_CURRENT=`readlink -f .`
PATH_SOURCE=`readlink -f src`


# configure git to push changes
echo "[INFO] Configure git to commit and push changes."

git config --global user.email $HTTPCTRL_EMAIL
git config --global user.name $HTTPCTRL_USERNAME


# assign new version to the library
echo "[INFO] Assign new version to the library (user provided value '$REQUESTED_VERSION')."

if [ -z "$REQUESTED_VERSION" ]
then
    # generate new version by increment
    echo "[INFO] Read current version of the library and increment it."

    version=`cat VERSION`
    pattern="([0-9]+).([0-9]+).([0-9]+)"
    if [[ $version =~ $pattern ]]
    then
        major="${BASH_REMATCH[1]}"
        minor="${BASH_REMATCH[2]}"
        micro="${BASH_REMATCH[3]}"

        micro=$((micro + 1))
    else
        echo "[ERROR] Impossible to extract version to make release."
        exit -1
    fi
    
    echo "$major.$minor.$micro" > VERSION
else
    # use user-provided version of the library
    echo "[INFO] Use user-provided version of the library '$REQUESTED_VERSION'."
    
    pattern="([0-9]+).([0-9]+).([0-9]+)"
    
    if [[ $REQUESTED_VERSION =~ $pattern ]]
    then
        echo "[INFO] Version has correct format."
    else
        echo "[ERROR] Incorrect format of the version."
        exit -1
    fi

    echo $REQUESTED_VERSION > VERSION
fi

version=`cat VERSION`


# push version change to the repository
echo "[INFO] Update version file in the repository."

git commit . -m "[ci][release] Update library version."
if [ $? -ne 0 ]; then
    echo "[ERROR] Impossible to release the library to PyPi (reason: commit new version to the repository failed)."
    exit -1
fi

git push https://$HTTPCTRL_USERNAME:$HTTPCTRL_PASSWORD@github.com/annoviko/robotframework-httpctrl.git --all
if [ $? -ne 0 ]; then
    echo "[ERROR] Impossible to release the library to PyPi (reason: pushing new version to the repository failed)."
    exit -1
fi


# packages to generate documentation
echo "[INFO] Install packages that are need to release the library and documentation."

pip3 install robotframework docutils pygments twine


# Release to PyPi
python3 -m build
twine upload dist/* -r pypi
if [ $? -ne 0 ]; then
    echo "[ERROR] Impossible to release the library to PyPi (reason: uploading to pypi failed)."
    exit -1
fi


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
