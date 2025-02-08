#!/bin/sh

count=$1
address=$2
port=$3
bot=$4
room=$5

cleanup() {
    # kill all processes whose parent is this process
    pkill -P $$
}

for sig in INT QUIT HUP TERM; do
  trap "
    cleanup
    trap - $sig EXIT
    kill -s $sig "'"$$"' "$sig"
done
trap cleanup EXIT

for i in `seq 1 $count`
do
    echo "Joining bot $i"
    $4 --host $address --port $port --room $room &
done

for job in `jobs -p`
do
    wait $job
done

echo "All bots joined"
