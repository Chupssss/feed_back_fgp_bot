echo "Restarting bot..."

pid=`ps -ef | grep main_bot.py | grep -v grep | awk '{print $2}'`

if [ -z $pid ]; then
    echo "Bot is not running"
else
    echo "Bot has been terminated"
    kill -9 $pid
fi

echo "Starting bot..."
nohup python3 mian_bot.py >/dev/null 2>&1 &
echo "Bot has been restarted successfully"