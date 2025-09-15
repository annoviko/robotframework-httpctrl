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

pip3 install robotframework docutils pygments twine build


# Release to PyPi
python3 -m build
twine upload dist/* -r pypi
if [ $? -ne 0 ]; then
    echo "[ERROR] Impossible to release the library to PyPi (reason: uploading to pypi failed)."
    exit -1
fi
