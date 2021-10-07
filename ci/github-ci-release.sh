PATH_ROOT=`readlink -f ..`
PATH_REPO_CURRENT=`readlink -f .`
PATH_SOURCE=`readlink -f src`


# increment release
version=`cat VERSION`
pattern="([0-9]+).([0-9]+).([0-9]+)"
if [[ $version =~ $pattern ]]
then
    major="${BASH_REMATCH[1]}"
    minor="${BASH_REMATCH[2]}"
    micro="${BASH_REMATCH[3]}"

    micro=$((micro + 1))
else
    echo "Impossible to extract version to make release"
    return -1
fi

echo "$major.$minor.$micro" > VERSION


# push version change to the repository
git push https://$HTTPCTRL_USERNAME:$HTTPCTRL_PASSWORD@github.com/annoviko/robotframework-httpctrl.git --all


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
version=`cat VERSION`

cd $PATH_SOURCE

python3 -m robot.libdoc -v $version -F reST HttpCtrl.Client $PATH_REPO_GH_PAGES/client.html
python3 -m robot.libdoc -v $version -F reST HttpCtrl.Server $PATH_REPO_GH_PAGES/server.html
python3 -m robot.libdoc -v $version -F reST HttpCtrl.Json $PATH_REPO_GH_PAGES/json.html


# Commit and push documentation changes
echo "Upload the documentation."

cd $PATH_REPO_GH_PAGES

commit_message="[ci][release] Release documentation for $major.$minor.$micro."
git commit . -m $commit_message

git push https://$HTTPCTRL_USERNAME:$HTTPCTRL_PASSWORD@github.com/annoviko/robotframework-httpctrl.git --all

