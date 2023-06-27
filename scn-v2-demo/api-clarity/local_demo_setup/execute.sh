#!/usr/bin/env bash

# load config
source ../config.sh

usage() {
    cat <<EOF
usage: $PROGNAME [-h|--help] [-u|--uninstall]
    -h:                 Print this helps and exits
EOF
}

# Process args and set variables
shopt -s nocasematch
PROGNAME=$(basename "$0")
while [[ $# -ge 1 ]]; do
	opt="$1"
	case $opt in
        -h|--help)
            usage;
            exit 0; shift;
            ;;
        --force-repo-deletion)
            delete_repo="TRUE"; shift ;
            ;;
        --no-build)
            no_build="TRUE"; shift ;
            ;;
        *)
            break;
	esac
done


./clean.sh

repo_folder="apiclarity-${API_CLARITY_REPO_BRANCH}"

if [[ ${delete_repo} == "TRUE" ]]; then
  read -p "Are you sure to delete apiclarity repo [y/N]?" yn
  if [[ ${yn} != "y" ]]; then
      echo "Remove --force-repo-deletion flag and run again. Bye!"
      exit 0
  fi
  rm -rf ${repo_folder}
fi

if [[ ! -d ${repo_folder} ]]; then
  git clone --single-branch --branch ${API_CLARITY_REPO_BRANCH} ${API_CLARITY_REPO} ${repo_folder}
fi

if [[ ${no_build} != "TRUE" ]]; then
  make -C ${repo_folder} backend ui
  rm -rf ${repo_folder}/site
  ln -s ui/build/  ${repo_folder}/site
fi

cp -r ../tools/assets  ${repo_folder}/
#cp ../tools/assets/fuzzer_fake_data.txt ${repo_folder}/data.txt

cd ${repo_folder};

DATABASE_DRIVER=LOCAL \
 NO_K8S_MONITOR=true \
 STATS_MAX_SAMPLES=100 \
 DEPLOYMENT_TYPE=fake \
 MODULES_ASSETS=./assets \
 ENABLE_DB_INFO_LOGS=true \
 ./backend/bin/backend run &> /tmp/logs &

pid=$!
echo "API clarity pid=${pid}"

read -p "Press Enter to push trace #1 "
UPSTREAM_TELEMETRY_HOST_NAME=localhost \
 UPSTREAM_TELEMETRY_HOST_NAME=localhost \
  ../../tools/feed.sh 1

read -p "Press Enter to push trace #2 "
APICLARITY_BASE=http://localhost python3 ../../tools/generate_traces_stats.py 2 ../../tools/provided_spec.json


read -p "Press Enter to stop apiclarity"
kill -9 ${pid}
