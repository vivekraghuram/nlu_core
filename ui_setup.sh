#sh starter.sh &
export ECG_FED=FED2
export JYTHONPATH=build/compling.core.jar:src/main/nluas
jython -m analyzer ../ecg-grammars/compRobots.prefs &
export PID=$!
echo "Analyzer" $PID
python3 src/main/robots_ui.py AgentUI 
