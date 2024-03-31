

import os,sys,random
import veri
import math
WORD_SIZE = 8 # FIXME
NOF_PES = 16
NOF_LEVELS = int(math.log(NOF_PES,2))
GROUP_SIZE_WIDTH = NOF_LEVELS +1


NewName = os.path.expanduser('~')
if os.path.exists('%s/vlsistuff' % NewName):
    sys.path.append('%s/vlsistuff/verification_libs3'%NewName)
elif 'VLSISTUFF' in os.environ:
    sys.path.append('%s/verification_libs3'%os.environ['VLSISTUFF'])
else:
    print("please set VLSISTUFF to where You cloned vlsistuff repository. like:  /home/cucu/softs/vlsistuff")
    sys.exit()

import logs
Monitors=[]
cycles=0
GIVEUP_TIMEOUT = 20    # how many cycles to run before retirment. 

import sequenceClass
seq = sequenceClass.sequenceClass('tb',Monitors,'',[])


def pymonname(Name):
    logs.pymonname(Name)

def sequence(TestName):
    Seq = logs.bin2string(TestName)
    seq.readfile(Seq)
    logs.setVar('sequence',Seq)
    Dir = os.path.dirname(Seq)
    logs.setVar('testsdir',Dir)
    logs.log_info('SEQUENCE %d'%len(seq.Sequence))

def cannot_find_sig(Sig):
    logs.log_error('cannot find "%s" signal in the design'%Sig)

def list_to_int(list, shift_size):
    list_as_int = 0
    for i in list:
        list_as_int = (list_as_int << shift_size) + i
    return list_as_int

def int_to_list(int, shift_size):
    list = []
    for i in range(NOF_PES):
        list.append(int >> (shift_size * i)) & ((2**shift_size) - 1)
    return list

def parse_output(output, word_size):
    output_as_list = []
    output_as_int = int(output,base=2)
    for i in range(NOF_PES):
        output_as_list.append((output_as_int >> (word_size * i)) & ((2**word_size) - 1))
    output_as_list.reverse()
    return output_as_list

class driverMonitor(logs.driverClass):
    def __init__(self,Path,Monitors):
        logs.driverClass.__init__(self,Path,Monitors)
        # self.input = [0] * NOF_PES
        self.input = list(range(NOF_PES)) #for sanity check
        self.counter = 0
        self.expected_output = list(range(NOF_PES))

    def run(self):
        global cycles
        cycles += 1
        if (cycles>2):
            output = veri.peek('tb.out')
            output_as_list = parse_output(output, WORD_SIZE)
            for pe_idx in range(NOF_PES):
                self.expected_output[pe_idx] = (self.expected_output[pe_idx] + 1) % NOF_PES
                if (self.expected_output[pe_idx] != output_as_list[pe_idx]):
                    print("ERROR! expected_output[{}][{}] = {}, output[{}][{}] = {}".format(self.counter, pe_idx, self.expected_output[pe_idx], self.counter, pe_idx, output_as_list[pe_idx]))
            print(f"expected_output:        {self.expected_output}")
            print(f"output:                 {output_as_list}")

            #update counter
            if (self.counter < 15):
                self.counter = self.counter + 1
            else:
                self.counter = 0

            #generate input
            self.input = random.sample(range(0, 2**WORD_SIZE), NOF_PES) #create random list if inputs
            print("counter:", self.counter)
            print("input:                 ", self.input)
            input_as_int = list_to_int(self.input, WORD_SIZE)
            veri.force('tb.in',str(input_as_int))
            return 



driverMonitor('tb',Monitors)

def negedge():
    veri.force('tb.cycles',str(cycles))
    if (cycles>GIVEUP_TIMEOUT):
        logs.log_info('finishing on default guard of %d'%GIVEUP_TIMEOUT)
        veri.finish()
    rst= veri.peek('tb.rst')
    if (rst!='0'):
        return
    for Mon in Monitors: Mon.run()
