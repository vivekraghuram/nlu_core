#sh starter.sh &
export ECG_FED=FED1
export JYTHONPATH=build/compling.core.jar:src/main/nluas
jython -m analyzer ../ecg-grammars/compRobots.prefs &
export PID=$!
echo $PID
python3 src/main/robots_ui.py AgentUI 
