import os,sys,random
import veri
import math
import random
WORD_SIZE = 8 # FIXME
NOF_PES = 8
NOF_LEVELS = int(math.log(NOF_PES,2))
GROUP_SIZE_WIDTH = NOF_LEVELS +1

class pe:
  def __init__(self, pe_idx, group_size):
    self.pe_idx    = pe_idx
    self.group_size = group_size

NewName = os.path.expanduser('~')
if os.path.exists('%s/vlsistuff' % NewName):
    sys.path.append('%s/vlsistuff/verification_libs3'%NewName)
elif 'VLSISTUFF' in os.environ:
    sys.path.append('%s/verification_libs3'%os.environ['VLSISTUFF'])
else:
    print("please set VLSISTUFF to where You cloned vlsistuff repository.")
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

def get_random_groups_sizes(nof_pes):
    alowed_sizes = []
    ans = []
    temp = []
    for i in range (int(math.log(nof_pes, 2))+1):
        alowed_sizes.append(2**i)
    print("alowed_sizes: {}".format(alowed_sizes))
    # find all group sizes combinations (combinational sum)
    findNumbers(ans, alowed_sizes, temp, nof_pes, 0)
    if len(ans) <= 0:
        print("all_group_sizes_comb is empty")
    print("all group sizes combinations:")
    for i in range (len(ans)):
        print(ans[i])
    # choose one random comination
    index = random.randint(0, len(ans)-1)
    return ans[index]

def findNumbers(ans, alowed_sizes, temp, sum, index):
	if(sum == 0):
		# Adding deep copy of list to ans
		ans.append(list(temp))
		return
	# Iterate from index to len(arr) - 1
	for i in range(index, len(alowed_sizes)):
		# checking that sum does not become negative
		if(sum - alowed_sizes[i]) >= 0:
			# adding element which can contribute to sum
			temp.append(alowed_sizes[i])
			findNumbers(ans, alowed_sizes, temp, sum-alowed_sizes[i], i)
			# removing element from list (backtracking)
			temp.remove(alowed_sizes[i])

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
        
def crate_group_size_list(groups_sizes):
    group_sizes_by_pe = []
    for i in range(NOF_PES):
        group_sizes_by_pe.append(-1)  # Initial group size is -1.
    # Allocate PEs to groups
    groups_sizes.sort(reverse=1)
    # Check that the sum of all the allocated groups equals to number of PEs.
    pes_groups_sum = 0
    for i in range(len(groups_sizes)):
        pes_groups_sum = pes_groups_sum + groups_sizes[i]
    if pes_groups_sum != NOF_PES:
        print("ERROR!!! number of PEs ({}) differs from the total number of PEs groups ({}). Exit!!!".format(NOF_PES,pes_groups_sum) )
        exit()
    for i in range(len(groups_sizes)):
        group_size = groups_sizes[i]
        pes_step = int(NOF_PES / group_size)
        # find start PE for this group
        start_pe_idx = -1
        for i in range(NOF_PES):
            if group_sizes_by_pe[i] == -1:
                start_pe_idx = i
                break
        pe_idx = start_pe_idx
        for i in range(group_size):
            group_sizes_by_pe[pe_idx] = group_size
            pe_idx = pe_idx + pes_step
    return group_sizes_by_pe

def get_expected_output(group_sizes_by_pe, input, counter):
    # print("input [get_expected_output]:", input)
    level_input = input
    for level_idx in range(NOF_LEVELS):   # Iterate over levels.
        level_output = []
        for pe_idx in range(NOF_PES):   # Iterate over level MUXes.
            group_size = group_sizes_by_pe[pe_idx]
            b = '{:0{width}b}'.format(counter, width=NOF_LEVELS)
            reverse_counter = int(b[::-1], 2)
            levels_mask = ~((int(NOF_PES/group_size))-1)
            if (((reverse_counter & levels_mask)>>level_idx) & 0x1) == 0:
                level_output.append(level_input[pe_idx])
            else:
                swap_size = 1 << level_idx
                if (pe_idx % (1 << (level_idx + 1))) < swap_size:
                    level_output.append(level_input[pe_idx + swap_size])
                else:
                    level_output.append(level_input[pe_idx - swap_size])
        level_input = level_output
    return level_output

class driverMonitor(logs.driverClass):
    def __init__(self,Path,Monitors):
        groups_sizes = []
        self.group_sizes_by_pe = []
        groups_sizes = get_random_groups_sizes(NOF_PES).copy()
        print("chosen combination:", groups_sizes)
        self.group_sizes_by_pe = crate_group_size_list(groups_sizes)
        print("group_sizes_by_pe:", self.group_sizes_by_pe)
        self.groups_sizes_by_pe_int = list_to_int(self.group_sizes_by_pe, GROUP_SIZE_WIDTH)
        self.counter = NOF_PES-2
        self.valid_output = 0
        self.output_peek = 0
        self.input = [0] * NOF_PES

        logs.driverClass.__init__(self,Path,Monitors)
        
    def run(self):
        global cycles
        cycles += 1
        if (cycles>2):
            #compare current output to expected output
            self.expected_output = []
            self.expected_connectivity = []
            self.expected_output = get_expected_output(self.group_sizes_by_pe, self.input, self.counter)
            self.expected_connectivity = get_expected_output(self.group_sizes_by_pe, list(range(NOF_PES)), self.counter)

            output = veri.peek('tb.output_pes_data')
            output_as_list = parse_output(output, WORD_SIZE)
            src_connectivity = veri.peek('tb.src_connectivity')
            src_connectivity_as_list = parse_output(src_connectivity, NOF_LEVELS)

            for pe_idx in range(NOF_PES):
                if (self.expected_output[pe_idx] != output_as_list[pe_idx]):
                    print("ERROR! self.expected_output[{}][{}] = {}, output[{}][{}] = {}".format(self.counter, pe_idx, self.expected_output[pe_idx], self.counter, pe_idx, output_as_list[pe_idx]))
                if (self.expected_connectivity[pe_idx] != src_connectivity_as_list[pe_idx]):
                    print("ERROR! self.expected_connectivity[{}][{}] = {}, src_connectivity[{}][{}] = {}".format(self.counter, pe_idx, self.expected_connectivity[pe_idx], self.counter, pe_idx, src_connectivity_as_list[pe_idx]))
            
            print(f"expected_output:        {self.expected_output}")
            print(f"output:                 {output_as_list}")
            print(f"expected_connectivity:  {self.expected_connectivity}")
            print(f"src_connectivity:       {src_connectivity_as_list}")

        #update counter
        if (self.counter < NOF_PES-1):
            self.counter = self.counter + 1
        else:
            self.counter = 0

        #generate new input
        self.input = random.sample(range(0, 2**WORD_SIZE), NOF_PES) #create random list if inputs ##FIXME - does it need to be 2**WORD_SIZE-1?
        # self.input = list(range(NOF_PES)) #for sanity check
        print("counter:", self.counter)
        print("input:                 ", self.input)
        input_as_int = list_to_int(self.input, WORD_SIZE)
        veri.force('tb.input_pes_data',str(input_as_int))
        veri.force('tb.groups_sizes',str(self.groups_sizes_by_pe_int))
        return   
    
# example of driver class usage
driverMonitor('tb',Monitors)

def negedge():
    veri.force('tb.cycles',str(cycles))
    if (cycles>GIVEUP_TIMEOUT):
        logs.log_info('finishing on default guard of %d'%GIVEUP_TIMEOUT)
        veri.finish()
    rst = veri.peek('tb.rst')
    if (rst!='0'):
        return
    for Mon in Monitors: Mon.run()

