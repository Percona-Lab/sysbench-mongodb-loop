#!/bin/bash

set -e

# Load global vars from sysbench-mongodb-loop config
if [ ! -f "$(dirname $0)/config.sh" ]; then
  echo "Cannot load sysbench-mongodb-loop config: $(dirname $0)/config.sh!"
  exit 1
fi
source $(dirname $0)/config.sh

TMP_DIR=$BASE_DIR/tmp
LOCK_FILE=$TMP_DIR/sysbench-mongodb-loop.lock
INIT_JS=$TMP_DIR/init.js
MONGO_FLAGS="--quiet"

# Load vars from sysbench-mongodbs config
if [ ! -f "$SYSBENCH_MONGODB_CONFIG" ]; then
  echo "Cannot load sysbench-mongodb config: $SYSBENCH_MONGODB_CONFIG!"
  exit 1
fi
source $SYSBENCH_MONGODB_CONFIG

if [ "$ADMIN_USERNAME" != "none" ] && [ "$ADMIN_PASSWORD" != "none" ]; then
  MONGO_FLAGS="$MONGO_FLAGS --username=$ADMIN_USERNAME --password=$ADMIN_PASSWORD --authenticationDatabase=admin"
fi

if [ -z "$BASE_DIR" ]; then
  BASE_DIR=$(readlink -f $(dirname $0))
fi

# Loop sysbench-mongodb forever
(
  flock -n 200

  cd $BASE_DIR

  while true; do
    if [ $KEEP_OUTPUT = "false" ]; then
      rm -f $BASE_DIR/mongoSysbenchExecute*.txt* *.log 2>/dev/null || true
    fi

    echo 'db.getSiblingDB("'$DB_NAME'").runCommand({dropDatabase:1})' >$INIT_JS

    if [ $SHARD_DATABASE = "true" ]; then
      echo 'sh.stopBalancer()' >>$INIT_JS
      for num in $(seq 1 ${NUM_COLLECTIONS}); do
         coll="${DB_NAME}${num}"
         echo 'db.getSiblingDB("'$DB_NAME'").'$coll'.drop()' >>$INIT_JS
      done
      echo 'db.getSiblingDB("'$DB_NAME'").dropDatabase()' >>$INIT_JS
      echo 'sh.enableSharding("'$DB_NAME'")' >>$INIT_JS
      for num in $(seq 1 ${NUM_COLLECTIONS}); do
         coll="${DB_NAME}${num}"
         echo 'sh.shardCollection("'$DB_NAME'.'$coll'", {_id:"hashed"})' >>$INIT_JS
      done
      echo 'sh.startBalancer()' >>$INIT_JS
    fi
    
    mongo $MONGO_FLAGS $INIT_JS
    rm -f $INIT_JS
  
    cd $SYSBENCH_MONGODB_DIR
    export CLASSPATH=$SYSBENCH_MONOGDB_JAVA_DRIVER:$CLASSPATH
    ./run.simple.bash $SYSBENCH_MONGODB_CONFIG >>$SYSBENCH_MONGODB_LOG 2>&1
    
    sleep $ITER_SLEEP
  done
) 200>$LOCK_FILE
