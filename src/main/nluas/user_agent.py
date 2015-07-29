from nluas.core_specializer import *
from nluas.core_agent import *
from nluas.analyzer_proxy import *
from nluas.core_specializer import *
from nluas.ntuple_decoder import NtupleDecoder
from nluas.spell_checker import *
import sys
import time

class UserAgent(CoreAgent):
    def __init__(self, args):
        CoreAgent.__init__(self, args)
        self.ui_parser = self.setup_ui_parser()
        #self.analyzer_port = self.unknown[0]
        self.initialize_UI()
        self.solve_destination = "{}_{}".format(self.federation, "ProblemSolver")


    def setup_ui_parser(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-port", type=str, help="indicate host to connect to",
                            default="http://localhost:8090")
        return parser

    def initialize_UI(self):
        args = self.ui_parser.parse_known_args(self.unknown)
        self.analyzer_port = args[0].port
        try:
            self.analyzer = Analyzer(self.analyzer_port)
            self.specializer=CoreSpecializer(self.analyzer)
        except ConnectionRefusedError as e:
            print(e)
            print("The analyzer_port address provided refused a connection: {}".format(self.analyzer_port))
            sys.exit()
        self.decoder = NtupleDecoder()
        self.spell_checker = SpellChecker(self.analyzer.get_lexicon())

    def process_input(self, msg):
        try:
            semspecs = self.analyzer.parse(msg)
            for fs in semspecs:
                try:
                    ntuple = self.specializer.specialize(fs)
                    json_ntuple = self.decoder.convert_to_JSON(ntuple)
                    #if self.specializer.debug_mode:
                    #   self.write_file(json_ntuple, msg)
                    self.transport.send(self.solve_destination, json_ntuple)
                    break
                except Exception as e:
                    print(e)
        except Exception as e:
            print(e)

    def callback(self, ntuple):
        print("Clarification requested.")
        #print(ntuple)
        decoded = self.decoder.convert_JSON_to_ntuple(ntuple)
        #print(decoded)

    def write_file(self, json_ntuple, msg):
        sentence = msg.replace(" ", "_").replace(",", "").replace("!", "").replace("?", "")
        t = str(time.time())
        generated = "src/main/json_tuples/" + sentence
        f = open(generated, "w")
        f.write(json_ntuple)

    def prompt(self):
        while True:
            specialize = True
            msg = input("> ")
            if msg == "q":
                self.close()
            elif msg == None or msg == "":
                specialize = False
            elif msg.lower()[0] == 'd':
                self.specializer.set_debug()
                specialize = False
            elif specialize:
                if self.check_spelling(msg):
                    self.process_input(msg)
            elif msg == None or msg == "":
                specialize = False
            elif msg.lower()[0] == 'd':
                self.specializer.set_debugging()
                specialize = False
            elif specialize:
                self.process_spelling(msg)

    
    def check_spelling(self, msg):
        table = self.spell_checker.spell_check(msg)
        if table:
            checked =self.spell_checker.join_checked(table['checked'])
            if checked != msg:
                print(self.spell_checker.print_modified(table['checked'], table['modified']))
                affirm = input("Is this what you meant? (y/n) > ")
                if affirm[0].lower() == "y":
                    self.process_input(checked)
                else:
                    return
            else:
                self.process_input(msg)



