
#sh starter.sh
#screen -dmS "analyzer" sh starter.sh
#screen -dmS "test2" python3 src/main/prog2.py AgentUI
#screen -dmS "test3" python3 src/main/prog.py ProblemSolver -logfile=test
#sh ui_setup.sh &
#sh starter.sh && python3 src/main/prog2.py AgentUI &
export ECG_FED=FED1
python3 src/main/prog.py ProblemSolver
#sh ui_setup.sh
#python3 src/main/prog2.py AgentUI

