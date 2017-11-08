#!/bin/bash
#
# 1. Make sure java, java devel and git packages are installed
# 2. 'git clone https://github.com/tmcallaghan/sysbench-mongodb'
# 3. Download mongodb java driver to root of sysbench-mongodb git checkout
# 4. Edit config.bash for your situation
# 5. Copy and run this script in root of sysbench-mongodb git checkout

set -e

basedir=$1
lockfile=/tmp/sysbench-mongodb-loop.lock
driver=$basedir/mongo-java-driver-2.13.0.jar
config=$basedir/config.bash
sysbench_mongodb_log=/var/log/sysbench-mongodb/sysbench-mongodb.log
mongo_flags="--quiet"
keep_output=0
delete_database=1
shard_database=1
iter_sleep=60
up_set=0

# Load vars from sysbench-mongodbs config
if [ ! -f "$config" ]; then
  echo "Cannot load sysbench-mongodb config: $config!"
  exit 1
fi
source $config

# Loop sysbench-mongodb forever
(
  flock -n 200
  cd $basedir
  while true; do
    if [ $keep_output -lt 1 ]; then
      rm -f mongoSysbenchExecute*.txt* *.log 2>/dev/null || true
    fi
  
    if [ "$A_USERNAME" != "none" ] && [ "$A_PASSWORD" != "none" ]; then
      if [ "$up_set" -eq 0 ]; then
	 mongo_flags="$mongo_flags --username=$A_USERNAME --password=$A_PASSWORD --authenticationDatabase=admin"
         up_set=1
      fi
    fi 
    if [ $delete_database -gt 0 ]; then
      mongo $mongo_flags --eval 'db.getSiblingDB("'$DB_NAME'").runCommand({dropDatabase:1})' >/dev/null
    fi

    if [ $shard_database -gt 0 ]; then
      js=/tmp/sbtest.js
      echo 'sh.stopBalancer()' >$js
      for num in $(seq 1 ${NUM_COLLECTIONS}); do
         coll="${DB_NAME}${num}"
         echo 'db.getSiblingDB("'$DB_NAME'").'$coll'.drop()' >>$js
      done
      echo 'db.getSiblingDB("'$DB_NAME'").dropDatabase()' >>$js
      echo 'sh.enableSharding("'$DB_NAME'")' >>$js
      for num in $(seq 1 ${NUM_COLLECTIONS}); do
         coll="${DB_NAME}${num}"
         echo 'sh.shardCollection("'$DB_NAME'.'$coll'", {_id:"hashed"})' >>$js
      done
      echo 'sh.startBalancer()' >>$js
      mongo $mongo_flags $js
      rm -f $js
    fi
  
    export CLASSPATH=$driver:$CLASSPATH
    ./run.simple.bash $config >$sysbench_mongodb_log 2>&1
    
    sleep $iter_sleep
  done
) 200>$lockfile
