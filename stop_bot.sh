pid=$(ps -ef | grep "main_bot.py" | grep -v grep | awk '{print $2}')

if [ -z "$pid" ]; then
  echo "Bot is not running"
else
  # Terminate the process
  kill $pid
  echo "Bot has been terminated"
fi