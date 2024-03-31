

import os,sys,random
import veri
import random
import math

WORD_SIZE = 8
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
run_cycles=0
transfers_complete = 0
GIVEUP_TIMEOUT = 10000    # how many cycles to run before retirment. 

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
    # print("all group sizes combinations:")
    # for i in range (len(ans)):
    #     print(ans[i])
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

class driverMonitor(logs.driverClass):
    def __init__(self,Path,Monitors):
        logs.driverClass.__init__(self,Path,Monitors)
        groups_sizes = []
        self.group_sizes_by_pe = []
        groups_sizes = get_random_groups_sizes(NOF_PES).copy()
        groups_sizes = [1, 1, 2, 4, 8]
        print("chosen combination:", groups_sizes)
        self.pe_group_sizes = crate_group_size_list(groups_sizes)
        print("self.pe_group_sizes:", self.pe_group_sizes)
        self.init_out_mem_data = []
        self.expected_in_mem_data =[]

        for pe_idx in range(NOF_PES):
            self.init_out_mem_data.append(random.sample(range(0, 2**WORD_SIZE), NOF_PES)) #create random initial memory

        for pe_idx_in_mem in range(NOF_PES):
            expected_in_mem = []
            for pe_idx_out_mem in range(NOF_PES):
                expected_in_mem.append(self.init_out_mem_data[pe_idx_out_mem][pe_idx_in_mem])
            self.expected_in_mem_data.append(expected_in_mem)


    def run(self):
        global run_cycles
        run_cycles += 1
        if (run_cycles == 1):
            for pe_idx in range(NOF_PES):
                out_mem_data_path = f"tb.dut.pe_memory_i[{pe_idx}].pe_memory_i.out_mem_data"
                pe_group_size_path = f"tb.dut.pe_memory_i[{pe_idx}].pe_memory_i.pe_group_size"
                veri.force_mem(pe_group_size_path, str(0), str(self.pe_group_sizes[pe_idx]))
                step_size = NOF_PES/self.pe_group_sizes[pe_idx]
                for i in range(self.pe_group_sizes[pe_idx]):
                    mem_idx = int((pe_idx+(i*step_size))%NOF_PES)
                    # veri.force_mem(out_mem_data_path, str(mem_idx), str(self.init_out_mem_data[pe_idx][mem_idx])) #mem can also be initialized from pe_memory.v
        elif (run_cycles == NOF_PES*2):
            for pe_idx in range(NOF_PES):
                in_mem_data = []
                expected_in_mem_data = []
                in_mem_data_path = f"tb.dut.pe_memory_i[{pe_idx}].pe_memory_i.in_mem_data"
                step_size = NOF_PES/self.pe_group_sizes[pe_idx]
                for i in range(self.pe_group_sizes[pe_idx]):
                    mem_idx = int((pe_idx+(i*step_size))%NOF_PES)
                    in_mem_data.append(int(veri.peek_mem(in_mem_data_path,str(mem_idx)),2))
                    expected_in_mem_data.append(self.expected_in_mem_data[pe_idx][mem_idx])
                in_mem_data.sort()
                expected_in_mem_data.sort()
                # print(f"pe: {pe_idx}\nin_data:  {in_mem_data}\nexpected: {expected_in_mem_data}",)
                for mem_idx in range(self.pe_group_sizes[pe_idx]):
                    if in_mem_data[mem_idx] != expected_in_mem_data[mem_idx]: 
                        print("ERROR!! in_mem_data[mem_idx]:", in_mem_data[mem_idx])
                    print(f"pe:{pe_idx}, in_mem_data[{mem_idx}]:{in_mem_data[mem_idx]}")
                    if in_mem_data[mem_idx] != pe_idx+10:
                        print("ERROR!! in_mem_data[mem_idx]:", in_mem_data[mem_idx])
        else:
            return

driverMonitor('tb',Monitors)

def negedge():
    global cycles
    cycles += 1
    veri.force('tb.cycles',str(cycles))
    if (cycles>GIVEUP_TIMEOUT):
        logs.log_info('finishing on default guard of %d'%GIVEUP_TIMEOUT)
        veri.finish()
    rst = veri.peek('tb.rst')
    if (rst=='1'):
        return

    if (cycles==30):
        veri.listing('tb','100','deep.list')
    if (cycles>30):
        for Mon in Monitors: Mon.run()