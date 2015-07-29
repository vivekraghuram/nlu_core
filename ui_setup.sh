#sh starter.sh &
export ECG_FED=FED2
export JYTHONPATH=build/compling.core.jar:src/main/nluas
jython -m analyzer ../ecg-grammars/starter.prefs localhost 8090 &
export PID=$!
echo $PID
wait $PID
python3 src/main/prog2.py AgentUI -port=http://localhost:8090