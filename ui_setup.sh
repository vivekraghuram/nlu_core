#sh starter.sh &
export ECG_FED=FED2

export JYTHONPATH=build/compling.core.jar:src/main/nluas
alias jython=/Users/aurelienappriou/jython2.5.3/jython
jython -m analyzer ../ecg-grammars/starter.prefs &
export PID=$!
echo $PID
#wait $PID
python3 src/main/prog2.py AgentUI 
