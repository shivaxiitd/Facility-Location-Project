import sys
import math
import numpy
import openpyxl
import random
import matplotlib.pyplot

numpy.set_printoptions(threshold=sys.maxsize, suppress = True)

num_cust = 100

r = 4.0  # input r as the threshold distance

# taking num_cust+1 and 830, then ignoring the first row and column, for easy correlation of indices with given problem statement.

x = numpy.zeros((830,1))  # x array representing the 829 collection centers, each entry will be 1 if the center will open and 0 otherwise

d = numpy.zeros((num_cust+1,830))  # distance matrix for distance between demand node i and potential facility site j

wb = openpyxl.load_workbook("data_test.xlsx")
sheet = wb.active

num_eligible_facilities = numpy.zeros((num_cust+1,1))
eligible_facility_repository = numpy.zeros((num_cust+1,51))
num_eligible_cust = numpy.zeros((830,1))
eligible_cust_repository = numpy.zeros((830, 51))

for i in range(2, num_cust+2):
    for j in range(2, 831):
        if (sheet.cell(row=i, column=j).value) <= r:
            d[i-1][j-1] = 1
            eligible_facility_repository[i - 1][math.floor(num_eligible_facilities[i - 1][0])+1] = j - 1
            num_eligible_facilities[i - 1] += 1
            eligible_cust_repository[j-1][math.floor(num_eligible_cust[j-1][0])+1] = i-1
            num_eligible_cust[j - 1] += 1

N = 200 #the number of food sources/emp bees/onlooker bees/scout bees in each iteration

sols = numpy.zeros((N, 829))
sols_fitness = numpy.zeros((N,1))
sols_limits = numpy.zeros((N,1))
selection_probabilities = [0]*N

#initializing solutions

sol_gen_token = 0

while sol_gen_token<N:
    cust_assign_array = numpy.zeros((num_cust+1, 1))
    cust_assign_array[0][0]=1
    while 0 in cust_assign_array:
        temp_facility = random.randint(1,829)
        if temp_facility not in sols[sol_gen_token] and num_eligible_cust[temp_facility][0]!=0:
            sols[sol_gen_token][math.floor(sols_fitness[sol_gen_token][0])]=temp_facility
            sols_fitness[sol_gen_token]+=1
            cust_assign_token = 1
            while cust_assign_token<=num_eligible_cust[temp_facility][0]:
                cust_assign_array[math.floor(eligible_cust_repository[temp_facility][cust_assign_token])]=1
                cust_assign_token+=1
    sol_gen_token+=1

max_iter = 300 #maximum number of iterations to be done
iter_count = 1
limit_max= 4000 #A solution is replaced by a new one if it does not improve for this much time
max_col_add = 4
max_col_remove = 10
fitness_improvement_array = numpy.zeros(max_iter)
iteration_count = numpy.zeros(max_iter)
minimum_ever_fitness=10000

while iter_count<=max_iter:
    #emp bee phase
    emp_bee_token = 0

    print("empbee start")
    while emp_bee_token<N:
        neighbor_index = random.randint(0,N-1)
        while neighbor_index == emp_bee_token:
            neighbor_index=random.randint(0,N-1)


        difference_array = numpy.setdiff1d(sols[neighbor_index], sols[emp_bee_token])
        if len(difference_array)==0:
            #generate new sol for emp_bee_token, reset fitness and limit
            sols_fitness[emp_bee_token]=0
            sols_limits[emp_bee_token]=0
            cust = 0
            while cust < 829:
                sols[emp_bee_token][cust] = 0
                cust += 1
            cust_assign_array = numpy.zeros((num_cust + 1, 1))
            cust_assign_array[0][0] = 1
            while 0 in cust_assign_array:
                temp_facility = random.randint(1, 829)
                if temp_facility not in sols[emp_bee_token]  and num_eligible_cust[temp_facility][0]!=0:
                    sols[emp_bee_token][math.floor(sols_fitness[emp_bee_token][0])] = temp_facility
                    sols_fitness[emp_bee_token] += 1
                    cust_assign_token = 1
                    while cust_assign_token <= num_eligible_cust[temp_facility][0]:
                        cust_assign_array[math.floor(eligible_cust_repository[temp_facility][cust_assign_token])] = 1
                        cust_assign_token += 1

        if len(difference_array)>0:
            temp_sol_array = numpy.zeros((1,829))
            temp_copy_token = 0
            while temp_copy_token < 829:
                temp_sol_array[0][temp_copy_token]=sols[emp_bee_token][temp_copy_token]
                temp_copy_token+=1
            temp_fitness=sols_fitness[emp_bee_token][0]
            #column adding
            num_col_add = random.randint(1,min(len(difference_array),max_col_add))
            token_col_add = 0
            while token_col_add<num_col_add:
                temp_sol_array[0][math.floor(temp_fitness)]=difference_array[token_col_add]
                temp_fitness+=1
                token_col_add+=1

            #column removing
            num_col_remove = random.randint(1, max_col_remove)
            token_col_remove=0
            while token_col_remove<num_col_remove:
                temp_sol_array[0][random.randint(0,temp_fitness-1)]=0
                token_col_remove+=1
            temp_sol_array=numpy.unique(temp_sol_array[0])
            temp_fitness=len(numpy.unique(temp_sol_array))-1

            #solution checking
            facility_sol_check_array = numpy.zeros((830,1))
            sol_check_popul_token =0
            while sol_check_popul_token<=temp_fitness:
                facility_sol_check_array[math.floor(temp_sol_array[sol_check_popul_token])]=1
                sol_check_popul_token+=1

            cust_check_array = numpy.dot(d,facility_sol_check_array)
            cust_check_array[0]=1
            cust_check_array=cust_check_array[0:num_cust+1]
            if 0 in cust_check_array:
                #repair
                repair_these_cust = numpy.where(cust_check_array == 0)
                facility_repair_strength_array = numpy.zeros((830,1))
                cust_repair_token = 0
                while cust_repair_token<len(repair_these_cust[0]):
                    temp_cust = repair_these_cust[0][cust_repair_token]
                    cust_facil_token = 1
                    while cust_facil_token<=num_eligible_facilities[temp_cust][0]:
                        facility_repair_strength_array[math.floor(eligible_facility_repository[temp_cust][cust_facil_token])][0]+=1
                        cust_facil_token+=1
                    cust_repair_token+=1

                while 0 in cust_check_array:
                    rep_facil_index = numpy.where(facility_repair_strength_array==numpy.max(facility_repair_strength_array))[0][0]
                    facility_sol_check_array[rep_facil_index]=1
                    temp_sol_array = numpy.append(temp_sol_array, rep_facil_index)
                    facility_repair_strength_array[rep_facil_index]=0
                    cust_check_array = numpy.dot(d, facility_sol_check_array)
                    cust_check_array[0] = 1
                    cust_check_array = cust_check_array[0:num_cust + 1]

            temp_sol_array=numpy.unique(temp_sol_array)
            temp_fitness=len(temp_sol_array)-1
            #check fitness

            if temp_fitness < sols_fitness[emp_bee_token]:
                #replace solution

                replace_token = 0
                while replace_token<829:
                    if replace_token<temp_fitness:
                        sols[emp_bee_token][replace_token]=temp_sol_array[replace_token+1]
                    if replace_token>=temp_fitness:
                        sols[emp_bee_token][replace_token]=0
                    replace_token+=1
                sols_fitness[emp_bee_token]=temp_fitness
                sols_limits[emp_bee_token]=0
            if temp_fitness > sols_fitness[emp_bee_token]:
                sols_limits[emp_bee_token]+=1

        emp_bee_token+=1
    #generate selection probabilities for the N solutions
    indi_fitness_array = numpy.zeros((N,1))
    fitness_calc_token = 0
    while fitness_calc_token<N:
        indi_fitness_array[fitness_calc_token][0]=1/sols_fitness[fitness_calc_token][0]
        fitness_calc_token+=1

    selection_probabilities_token=0
    while selection_probabilities_token<N:
        selection_probabilities[selection_probabilities_token]=indi_fitness_array[selection_probabilities_token][0]/numpy.sum(indi_fitness_array)
        selection_probabilities_token+=1

    print("onloooker bee start")
    #onlooker bee phase
    onlooker_bee_token = 0
    while onlooker_bee_token<N:
        #pick hybrid_index by selection probabilities
        neighbor_index = numpy.random.choice(N,1,selection_probabilities)
        while neighbor_index == onlooker_bee_token:
            neighbor_index = numpy.random.choice(N,1,selection_probabilities)


        difference_array = numpy.setdiff1d(sols[neighbor_index], sols[onlooker_bee_token])
        if len(difference_array) == 0:
            # generate new sol for emp_bee_token, reset fitness and limit
            sols_fitness[onlooker_bee_token] = 0
            sols_limits[onlooker_bee_token] = 0
            cust = 0
            while cust < 829:
                sols[onlooker_bee_token][cust] = 0
                cust += 1
            cust_assign_array = numpy.zeros((num_cust + 1, 1))
            cust_assign_array[0][0] = 1
            while 0 in cust_assign_array:
                temp_facility = random.randint(1, 829)
                if temp_facility not in sols[onlooker_bee_token]  and num_eligible_cust[temp_facility][0]!=0:
                    sols[onlooker_bee_token][math.floor(sols_fitness[onlooker_bee_token][0])] = temp_facility
                    sols_fitness[onlooker_bee_token] += 1
                    cust_assign_token = 1
                    while cust_assign_token <= num_eligible_cust[temp_facility][0]:
                        cust_assign_array[math.floor(eligible_cust_repository[temp_facility][cust_assign_token])] = 1
                        cust_assign_token += 1

        if len(difference_array) > 0:
            temp_sol_array = numpy.zeros((1, 829))
            temp_copy_token = 0
            while temp_copy_token < 829:
                temp_sol_array[0][temp_copy_token] = sols[onlooker_bee_token][temp_copy_token]
                temp_copy_token += 1
            temp_fitness = sols_fitness[onlooker_bee_token][0]
            # column adding
            num_col_add = random.randint(1, min(len(difference_array), max_col_add))
            token_col_add = 0

            while token_col_add < num_col_add:
                temp_sol_array[0][math.floor(temp_fitness)] = difference_array[token_col_add]
                temp_fitness += 1
                token_col_add += 1

            # column removing
            num_col_remove = random.randint(1, max_col_remove)
            token_col_remove = 0
            while token_col_remove < num_col_remove:
                temp_sol_array[0][random.randint(0, temp_fitness - 1)] = 0
                token_col_remove += 1
            temp_sol_array = numpy.unique(temp_sol_array[0])
            temp_fitness = len(numpy.unique(temp_sol_array)) - 1
            # solution checking
            facility_sol_check_array = numpy.zeros((830, 1))
            sol_check_popul_token = 0
            while sol_check_popul_token <= temp_fitness:
                facility_sol_check_array[math.floor(temp_sol_array[sol_check_popul_token])] = 1
                sol_check_popul_token += 1
            cust_check_array = numpy.dot(d, facility_sol_check_array)
            cust_check_array[0] = 1
            cust_check_array = cust_check_array[0:num_cust + 1]

            if 0 in cust_check_array:
                # repair
                repair_these_cust = numpy.where(cust_check_array == 0)
                facility_repair_strength_array = numpy.zeros((830, 1))
                cust_repair_token = 0
                while cust_repair_token < len(repair_these_cust[0]):
                    temp_cust = repair_these_cust[0][cust_repair_token]
                    cust_facil_token = 1
                    while cust_facil_token <= num_eligible_facilities[temp_cust][0]:
                        facility_repair_strength_array[math.floor(eligible_facility_repository[temp_cust][cust_facil_token])][0] += 1
                        cust_facil_token += 1
                    cust_repair_token+=1

                while 0 in cust_check_array:
                    rep_facil_index = \
                    numpy.where(facility_repair_strength_array == numpy.max(facility_repair_strength_array))[0][0]
                    facility_sol_check_array[rep_facil_index] = 1
                    temp_sol_array = numpy.append(temp_sol_array, rep_facil_index)
                    facility_repair_strength_array[rep_facil_index] = 0
                    cust_check_array = numpy.dot(d, facility_sol_check_array)
                    cust_check_array[0] = 1
                    cust_check_array = cust_check_array[0:num_cust + 1]

            temp_sol_array = numpy.unique(temp_sol_array)
            temp_fitness = len(temp_sol_array) - 1


            # check fitness
            if temp_fitness < sols_fitness[onlooker_bee_token]:
                # replace solution

                replace_token = 0
                while replace_token < 829:
                    if replace_token < temp_fitness:
                        sols[onlooker_bee_token][replace_token] = temp_sol_array[replace_token + 1]
                    if replace_token >= temp_fitness:
                        sols[onlooker_bee_token][replace_token] = 0
                    replace_token += 1
                sols_fitness[onlooker_bee_token] = temp_fitness
                sols_limits[onlooker_bee_token] = 0
            if temp_fitness > sols_fitness[onlooker_bee_token]:

                sols_limits[onlooker_bee_token] += 1

        onlooker_bee_token+=1

    print("scout bee start")
    #scout bee phase
    scout_bee_token = 0
    while scout_bee_token<N:

        if sols_limits[scout_bee_token]>limit_max:

            #generate new solution
            sols_fitness[scout_bee_token] = 0
            sols_limits[scout_bee_token] = 0
            cust = 0
            while cust < 829:
                sols[scout_bee_token][cust] = 0
                cust += 1
            cust_assign_array = numpy.zeros((num_cust + 1, 1))
            cust_assign_array[0][0] = 1
            while 0 in cust_assign_array:
                temp_facility = random.randint(1, 829)
                if temp_facility not in sols[scout_bee_token]  and num_eligible_cust[temp_facility][0]!=0:
                    sols[scout_bee_token][math.floor(sols_fitness[scout_bee_token][0])] = temp_facility
                    sols_fitness[scout_bee_token] += 1
                    cust_assign_token = 1
                    while cust_assign_token <= num_eligible_cust[temp_facility][0]:
                        cust_assign_array[math.floor(eligible_cust_repository[temp_facility][cust_assign_token])] = 1
                        cust_assign_token += 1
        scout_bee_token+=1

    if numpy.min(sols_fitness)<minimum_ever_fitness:
        minimum_ever_fitness = numpy.min(sols_fitness)
        best_solution_ever = sols[numpy.where(sols_fitness==numpy.min(sols_fitness))[0][0]]
    print("best solution in current iteration is", numpy.min(sols_fitness)) #best solution in current iteration
    print("overall best solution ever achieved is", minimum_ever_fitness) #best solution ever
    print("Iteration Number - ", iter_count)
    fitness_improvement_array[iter_count-1]= minimum_ever_fitness
    iteration_count[iter_count-1]=iter_count
    iter_count=iter_count+1

matplotlib.pyplot.plot(iteration_count, fitness_improvement_array)
matplotlib.pyplot.xlabel("No. of iterations")
matplotlib.pyplot.ylabel("No. of facilities required in the best solution of ith iteration")
matplotlib.pyplot.show()

#The following will print the best solution ever
print(best_solution_ever)