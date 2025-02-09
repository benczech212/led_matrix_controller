HOSTNAME=192.168.4.99
USERNAME=ben
SOURCE_PATHS=( "../led_matrix_controller")
REMOTE_PATH=/home/ben/dev
RESTART_SERVICE=false
if [ "$1" == "--restart" ]; then
    RESTART_SERVICE=true
fi
# until ping -c 1 $HOSTNAME &>/dev/null; do
#     echo "Waiting for $HOSTNAME to be reachable..."
#     sleep 5
# done


# until ping -c 1 $HOSTNAME &>/dev/null; do
#     echo "Waiting for $HOSTNAME to be reachable..."
#     sleep 2
# done
for SOURCE_PATH in "${SOURCE_PATHS[@]}"
do
    echo "Copying $SOURCE_PATH to $HOSTNAME:$REMOTE_PATH"
    sudo mkdir -p $REMOTE_PATH
    scp -r $SOURCE_PATH $USERNAME@$HOSTNAME:$REMOTE_PATH
done
# if [ "$RESTART_SERVICE" = true ]; then
    # echo "Restarting service on $HOSTNAME"
    # ssh $USERNAME@$HOSTNAME 'sudo systemctl restart staff_of_observability'
# fi
