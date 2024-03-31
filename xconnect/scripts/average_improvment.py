# find all combinations that sum to a given value
import math
import matplotlib.pyplot as plt

def combinationSum(arr, sum):
	ans = []
	temp = []

	# first do nothing but set{}
	# since set does not always sort
	# removing the duplicates using Set and
	# Sorting the List
	arr = sorted(list(set(arr)))
	findNumbers(ans, arr, temp, sum, 0)
	return ans

def findNumbers(ans, arr, temp, sum, index):
	
	if(sum == 0):
		# Add copy of the list to ans
		ans.append(list(temp))
		return
	
	# Iterate from index to len(arr) - 1
	for i in range(index, len(arr)):

		if(sum - arr[i]) >= 0:
			# adding element which can contribute to sum
			temp.append(arr[i])
			findNumbers(ans, arr, temp, sum-arr[i], i)
			# removing element from list
			temp.remove(arr[i])


def find_avg_cycles_improve(nof_pes):
	# Driver Code
	arr = []
	for i in range (int(math.log(nof_pes, 2))+1):
		print (i)
		arr.append(2**i)
	print("Groups: {}".format(arr))
	sum = nof_pes
	ans = combinationSum(arr, sum)

	if len(ans) <= 0:
		print("empty")
		
	# print all combinations
	avg_clk_improve = 0
	for i in range(len(ans)):
		clk_improve = 0
		print("[", end=' ')
		for j in range(len(ans[i])):
			print(str(ans[i][j])+" ", end=' ')
			clk_improve += nof_pes/ans[i][j]
		clk_improve = clk_improve/len(ans[i])
		print("]")
		print("clk_improve =", clk_improve)
		avg_clk_improve += clk_improve
	avg_clk_improve = avg_clk_improve/(len(ans))
	print ("avg_clk_improve =", avg_clk_improve)
	avg_improve_func_nof_pes.append(avg_clk_improve)


avg_improve_func_nof_pes = []
nof_pes = []

for i in range(7):
	nof_pes_i = 2**i
	nof_pes.append(nof_pes_i)
	find_avg_cycles_improve(nof_pes_i)

print(avg_improve_func_nof_pes)
print(nof_pes)

plt.plot(nof_pes, avg_improve_func_nof_pes)
plt.xlabel('nof_pes')
plt.ylabel('avg_improvement(clock cycles)')
plt.title('Average Improvement (clock cycles) vs Number of PEs')
plt.show()