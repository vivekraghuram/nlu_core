# NLU CORE

This module contains "core" code for our agent-based full-path NLU system. 
The core code is all located in src/main/nluas, and the setup/config files
are located in the top directory.   

"Agents", in our system, are capable of building, sending, receiving, and 
using n-tuples, a custom communication tool.  An n-tuple contains action protocols
and application-specific content.    
  
Application Engineers wishing to use the "core" code for providing a NLU-interface
to their application can add their code to the "main" directory, importing the 
code from the "nluas" directory. A basic configuration requires at least:

* AgentUI: Communicates with the user. Analyzes text into a SemSpec, and specializes
this into an "n-tuple".

* ProblemSolver: Receives an n-tuple from the AgentUI, which it uses to solve a problem
in the application domain (e.g., robotics).  

Developers can add other modules/Agents by subclassing the CoreAgent module, or by making
more refined AgentUI/ProblemSolver modules, which already subclass CoreAgent. This will inherit
the Transport mechanism (see api.txt), as well as the configuration/setup parser (ArgParser).

# Running the System with Robots

The repository includes several setup scripts. To run with a language parser, you'll also need to have
downloaded the ecg-grammars repository found here: https://github.com/icsi-berkeley/ecg-grammars

You can just run setup.sh as is, and it'll run a text-based demo of the whole system. If you'd prefer to 
run with Morse, you should first run:

sh morse.sh

Then change the command in setup.sh from "python3 src/main/robots/robot_solver.py ProblemSolver &" to
"python3 src/main/robots/morse_solver.py ProblemSolver &" (commented out below it currently). Then run setup.sh as usual.
