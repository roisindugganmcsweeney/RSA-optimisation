import pandas as pd
from pulp import LpMinimize, LpProblem, LpStatus, lpSum, LpVariable, LpAffineExpression
from math import ceil
import re


########################################################################################################################################################################################################################
# works in isolation - unsure how it works in connection with the rest of the code
# further refactoring to be done


def str_to_bool(df):
    """Convert 'enabled' and 'flex' columns to boolean columns
    due to Dash DataTable inability to display booleans"""
    for col, dtype in df.dtypes.items():
        if col == 'enabled' or col == 'flex':
            df[col] = df[col].astype('bool')
    return df


def DataFrame_to_dict(df: pd.DataFrame) -> dict: # converts a pandas DataFrame into a dictionary
    my_dict={}
    for column in df.columns:
        my_dict[column]=list(df[column])
    return my_dict


def filter_data_by_column(dataframe: pd.DataFrame, column: str) -> pd.DataFrame: # initial data cleaning
    return dataframe[(dataframe[column] == True)] # we will want to filter for only open centres


# This isn't a fully documented commenting of what its doing
def definitions_dictionary(centre_vals: dict) -> dict: # input the centre dictionary; this returns a dictionary of important information
    information_dict={}
    information_dict['weekDays'] = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    
    # This adds a built in adjustment value to the B variable below.  No idea what that is yet
    adjustment_list = [0 for i in range(len(centre_vals['maxBooths']))] # creates a list the length of the centre_vals DataFrame
    information_dict['adjustments'] = pd.DataFrame(adjustment_list, columns=['Adjustment']) # turns the above list into a DataFrame
    
    information_dict['flex'] = centre_vals['flex']+[0 for i in range(len(centre_vals['maxBooths']))] # this line makes no logical sense
    
    return information_dict


def create_LP_variables(centre_vals: dict) -> dict: # creates a dictionary of lists of LP Variables from the centre dictionary centre_vals
    # There are built classes for this, this should be automatic and functionalised
    
    var_dict =  {'Booths':[], 'Vax_TL':[], 'Circ_Vacc': [], 'Obs': [], 'Pharm': [],  'Reg_Adm': [], 'MaxVax': [], 'maxBooths': [], 'AbsBVar': [], 'BVar': []}
    # TODO This should just be outright functionalised - is this functionalised enough?
    # populate_lp_variables(variable_rules: addict.Dict, dataset: pd.DataFrame)
    
    centre_df: pd.DataFrame = pd.DataFrame.from_dict(centre_vals)    # Dict to Pandas DataFrame
    iteration_range=range(len(centre_df)) # originally had an iterrows but was edited out on recommendation of Nick
    for i in iteration_range:
        row=centre_df.iloc[i,:]
        max10 = round((row['maxBooths']+4.9)*.1)
        max5 = max10*2
        minBooths = row['minBooths']
        maxBooths = row['maxBooths']
        # Because of the naming scheme this is almost unreadable # hopefully this is better now
        var_dict['Booths'].append(LpVariable('Booths'+str(i),minBooths, maxBooths, 'Integer')) # number of booths open at centre i
        var_dict['Vax_TL'].append(LpVariable('Vax_TL'+str(i),minBooths, max10, 'Integer')) # number of vaccination team leads at centre i
        var_dict['Circ_Vacc'].append(LpVariable('Circ_Vacc'+str(i),minBooths, max10, 'Integer'))  # number of circulating vaccinators at centre i which????
        var_dict['Obs'].append(LpVariable('Obs'+str(i),minBooths, max10, 'Integer'))  # number of observers at centre i
        var_dict['Pharm'].append(LpVariable('Pharm'+str(i),minBooths, max10, 'Integer'))  # number of pharmacists at centre i
        var_dict['Reg_Adm'].append(LpVariable('Reg_Adm'+str(i),minBooths, max5, 'Integer'))  # number of registration admins at centre i
        var_dict['MaxVax'].append(row['maxDays']*row['vaxHours']*row['vph']) # maximum possible number of vaccines per booth per day at centre i
        var_dict['maxBooths'].append(LpVariable('maxBooths'+str(i),maxBooths, cat='Integer')) # the maximum number of booths open at centre i
        var_dict['AbsBVar'].append(LpVariable('AbsBVar'+str(i),0))
        var_dict['BVar'].append(LpVariable('BVar'+str(i)))
    return var_dict


def objective_function(centre_vals: dict, var_dict: dict) -> LpProblem: # returns the objective function
    # the objective function is (total number of booths open) + (total number of vaccine Team Leads) + (total number of circulating vaccinators) + (total number of pharmacists) + (total number of registration admins) +
    # it looks like the aim is to minimise total staff and booth usage (why is it that opening/closing an additional booth is considered the same as recruiting/dismissing a member of staff?); then using minimising the total absolute BVariance as a tie-breaker  ###TBQ
    # inputs required are the centre_vals dictionary, followed by the variable dictionary, then the number of vaccines required per week 
    
    inf_dict=definitions_dictionary(centre_vals) # gets the information
    
    # TODO To clean this up, use addict Dict()
    # Should be possible to link automatically and make this reusable key types
    sumBooths = sum(var_dict['Booths']) # LP variable: total number of open booths
    maxBooths = sum(centre_vals['maxBooths']) # LP variable: maximum total booths
    sumVax_TL = sum(var_dict['Vax_TL']) # LP variable: total Vaccination Team Leads across all centres
    sumObs = sum(var_dict['Obs']) # LP variable: total Observers across all centres
    sumPharm = sum(var_dict['Pharm']) # LP variable: total Pharmacists across all centres
    sumCirc_Vacc = sum(var_dict['Circ_Vacc']) # LP variable: total Circulating Vaccinators across all centres
    sumReg_Adm = sum(var_dict['Reg_Adm']) # LP variable: total Registration Admins across all centres

    # Custom rule for constraints: Feeds into the model I think
    #Calculate the avaialble vaccine split variance

    catchment_populations = centre_vals['catchment'] # the targeted population for the vaccine from centre
    total_catchment = sum(catchment_populations) # the total catchment population across all centres
    
    for i, catchmentPopulation in enumerate(catchment_populations): # More rules based allocation stuff
        var_dict['BVar'][i] = ((catchmentPopulation/total_catchment)*sumBooths-var_dict['Booths'][i]) # defines the BVar at centre i to be the difference between (the number of booths expected to be at centre i, given the total number of booths open and the proprtion of the total catchment population at centre i) and the number of booths actually open at centre i
   
    return (sumBooths+sumVax_TL+sumCirc_Vacc+sumObs+sumPharm+sumReg_Adm+(lpSum(var_dict['AbsBVar'])*.000001))


def add_constraints(centre_vals: dict, var_dict: dict, vaccines_required: int) -> list:
    # takes in the dictionary of variables and the centre_vals dictionary and returns the list of constraints
    
    sumBooths = sum(var_dict['Booths']) # LP variable: total number of open booths
    # The following line needs queried ###TBQ
    max_vax_booths = sum([a*b for a,b in zip(var_dict['MaxVax'],sumBooths)]) # the maximum possible number of vaccinations per week; summing the maximum_booths*
    inf_dict=definitions_dictionary(centre_vals) # gets the definition dictionary information
    
    constraints=[]
    constraints.append(max_vax_booths >= int(vaccines_required) + sum(centre_vals['reqDose'])) # the total number of possible vaccinations must be no less than the number of vaccines required + the total second dose requirements
    
    # Lots of hard coded values here that need to go
    for i, val in enumerate(var_dict['Booths']): # iterates through the booths

        constraints.append(var_dict['Vax_TL'][i] * 20 - val <= 19) # the number of vaccination Team Leads at centre i must be less than 1+(the number of booths open at centre i)/20
        constraints.append(var_dict['Vax_TL'][i] * 20 - val + inf_dict['flex'][i] >= 0) # and no less than ((the number of booths open at centre i) - (the flex at centre i))/20

        constraints.append(var_dict['Circ_Vacc'][i] * 10 - val <= 9) # the number of circulating vaccinators at centre i must be less than 1+(the number of booths open at centre i)/10
        constraints.append(var_dict['Circ_Vacc'][i] * 10 - val + inf_dict['flex'][i] >= 0) # and no less than ((the number of booths open at centre i) - (the flex at centre i))/10

        constraints.append(var_dict['Reg_Adm'][i] * 5 - val <= 4)  # the number of registration admins at centre i must be less than 1+(the number of booths open at centre i)/5
        constraints.append(var_dict['Reg_Adm'][i] * 5 - val + inf_dict['flex'][i] >= 0) # and no less than ((the number of booths open at centre i) - (the flex at centre i))/5

        constraints.append(var_dict['Circ_Vacc'][i] == var_dict['Obs'][i]) # the number of circulationg vaccinators at centre i must be equal to the number of observers at centre i

        constraints.append(var_dict['Vax_TL'][i] == var_dict['Pharm'][i]) # the Vaccinaion Team Leads at centre i must be equal to the number of Pharmacists at centre i 
        
        # AbsBVar[i] is a variable which is only constrained by the two constraints below i.e AbsBVar[i]>=|BVar[i]| - because AbsBVar contributes positively to the objective function, when the model is solved, the resultant value of AbsBVar[i] will be the lowest it possibly can be given the constraints i.e. in the optimal solution AbsBVar[i] is the absolute value of BVar[i]
        constraints.append(var_dict['AbsBVar'][i] >= var_dict['BVar'][i]) # the AbsBVar at centre i must be no less than BVar at centre i
        constraints.append(var_dict['AbsBVar'][i] >= -var_dict['BVar'][i]) # the AbsBVar at centre i must be no less than -BVar at centre i
        
        # reqDose is the list of second dose requirements for the centres
        constraints.append(val*var_dict['MaxVax'][i] >= centre_vals['reqDose'][i]) # (the number of vaccination booths open at centre i)*(the maximum number of vaccinations per booth at centre i) must be at least as great as the number of second dose requirements for centre i
    return constraints


def run_the_model(centre_vals: dict, vaccines_required: int): # runs the model
    model = LpProblem(name="vax-problem", sense=LpMinimize) # creates an LPMinimise model
    var_dict=create_LP_variables(centre_vals) # creates the variables dictionary
    
    of=objective_function(centre_vals, var_dict) # defines objective function
    model += of # adds objective function
    
    constraints=add_constraints(centre_vals, var_dict, vaccines_required) # creates the constraints
    for constraint in constraints: # adds the constraints
        model += constraint
    
    status = model.solve() # Solve the model
    return model # return solved model

def status_explainer(status: int) -> str: # translates the model.status into Plain English
    dic={-1: 'FAILURE', 0: 'NOT RAN YET', 1: 'SUCCESS'}
    if status in dic:
        return dic[status]
    else:
        return str(status)

def model_parse(model: LpProblem) -> pd.DataFrame: # converts from the solved model into an appropriate DataFrame
    # Probably needs _SUCCESS or _FAILURE if we really care how well it worked
    pattern = r'[a-zA-Z]+' # Why are we just searching for alphabetic characters here?
    pd_vals = {}
    # Not entirely sure why we can't just use model.variables but we can check that later
    # All this does is parse through the model variables and generate a dictionary to dump into a dataframe
    for var in model.variables():
        var_name = str(var.name)
        var_value = var.varValue
        # Pattern's defined above but needs to be compiled for it to be meaningful
        var_name_clean = re.match(r"[a-zA-z]+", str(var_name))[0]
        if var_name_clean in pd_vals:
            pd_vals[var_name_clean].append(int(var_value))
        else:
            pd_vals[var_name_clean] = [int(var_value)]

    parsed_model = pd.DataFrame.from_dict(pd_vals) # all model variables are put into a dataframe data
    
    parsed_model.drop(["AbsBVar"],axis=1,inplace=True) # the column AbsBVar is removed (presumably because it is no longer relevant)
    parsed_model['Status'] = status_explainer(model.status) # adds the model status as a column to the data DataFrame
    return parsed_model


def munge_info(data: pd.DataFrame, centre_vals: dict) -> dict:
    # extracts important information for data munging
    output={'booths':[], 'days':[], 'hour_flex':[], 'hours_worked_per_day':[], 'empl_week_hours':[], 'staff_flex':[], 'hours_available':[], 'hours_remaining':[], 'rounded':[]}
    inf_dic=definitions_dictionary(centre_vals) # gets the definition dictionary information
    iteration_range=range(len(data))
    
    for i in iteration_range:
        temp={} # a temparary dictionary of information for a given record
        temp['booths'] = data.Booths[i]
        temp['days'] = centre_vals['maxDays'][i] # number of days that the centre can be open
        # flex is a boolean value indicating whether or not a centre has flexibility with its hours and staff
        # I have yet to read through in detail and understand the flex stuff and this section 
        temp['hour_flex'] = inf_dic['flex'][i] # if there is flex at centre i
        temp['hours_worked_per_day'] = centre_vals['workingHours'][i] # variable for working hours
        temp['empl_week_hours'] = temp['days'] * temp['hours_worked_per_day'] # the total employee working hours at the centre
        temp['staff_flex'] = inf_dic['flex'][i] # if there is flex at centre i
        temp['hours_available'] = (temp['empl_week_hours'] + temp['hour_flex']) # (total hours are the standard employee hours) + (the flex at the centre)
        temp['hours_remaining'] = temp['hours_available'] 
        temp['rounded'] = ceil((temp['booths'] - temp['staff_flex'])) # the number of booths available, when taking into account staff_flex ###TBQ??
        if temp['rounded'] == 0: temp['rounded'] = 1 ###TBQ??
        
        keys=temp.keys()
        for key in keys:# appending the temporary information into a dictionary of lists for output
            output[key].append(temp[key])
        
    return output

def data_munge_1(data: pd.DataFrame, centre_vals: dict) -> pd.DataFrame:
     # takes the DataFrame from a parsed model and the centre_vals dictionary used to solve the model, outputs a modified version of the data DataFrame in preparation for making suitable dataframe for use by the front end 
    
    inf_dic=definitions_dictionary(centre_vals) # gets the definition dictionary information
    munge_dic=munge_info(data, centre_vals) # gathers information for the munging
    
    # This is some jupyterlabbery to avoid apparent losses of data - random jupyter lab cell execution orders sometimes mess things up
    # Really, this should be done externally to this script post modelling and defined by the user interface if you want this as a tool
    # See the last TODO in the file re file names
    
    data_intermed=data.copy()
    #adds in new columns
    data_intermed['Vacc'] = data_intermed['Booths'] # ???
    data_intermed['Vax/Day'] = 0 # the number of vaccines per day, at each centre - initially set at 0 - to be filled in later
    data_intermed['Vax/Week'] = 0 # the number of vaccines per week - initially set at 0 - to be filled in later
    data_intermed['Booth %'] = 0.0 # the percentage of booths which are open, at each centre - initially set at 0 - to be filled in later
    
    ######### THESE LINES COULD POTENTIALLY BE FUNCTIONALISED
    iteration_range=range(len(data_intermed))
    for i in iteration_range:      
        # Booths values in data are adjusted by adding in the adjustments (currently the adjustments are 0, but I am keeping it in case there is some use for it)
        data_intermed['Booths'][i] = data_intermed.Booths[i] + inf_dic['adjustments'].Adjustment[i]
        row=data_intermed.iloc[i,:]
        # See line 273.  Also, no more uses of i as an index variable unless it 100% requires it.  If this can be functionalised, do it
        data_intermed['Vacc'][i] = ceil(data_intermed.Vacc[i]*centre_vals['workingHours'][i]*centre_vals['maxDays'][i]/munge_dic['empl_week_hours'][i]) # sets the Vacc variable, which is, for each centre i, the proportion of employee weekly hours for which centre i is open (the maximum number of hours of vaccination per week)
        data_intermed['Circ_Vacc'][i] = ceil((ceil((munge_dic['rounded'][i])/10)*(centre_vals['workingHours'][i]*centre_vals['maxDays'][i]/munge_dic['empl_week_hours'][i]))) # the number of circulating vaccinators at centre i - adjusted for the number of hours they work per week
        data_intermed['Reg_Adm'][i] = ceil((ceil((munge_dic['rounded'][i])/3)*(centre_vals['workingHours'][i]*centre_vals['maxDays'][i]/munge_dic['empl_week_hours'][i]))) # the number of registration admins at centre i - adjusted for the number of hours they work per week
        data_intermed['Obs'][i] = ceil((ceil((munge_dic['rounded'][i])/10)*(centre_vals['workingHours'][i]*centre_vals['maxDays'][i]/munge_dic['empl_week_hours'][i])))  # the number of observers at centre i - adjusted for the number of hours they work per week
        data_intermed['Pharm'][i] = ceil((ceil((munge_dic['rounded'][i])/20)*(centre_vals['workingHours'][i]*centre_vals['maxDays'][i]/munge_dic['empl_week_hours'][i]))) # the number of pharmacists at centre i - adjusted for the number of hours they work per week
        data_intermed['Vax_TL'][i] = ceil((ceil((munge_dic['rounded'][i])/20)*(centre_vals['workingHours'][i]*centre_vals['maxDays'][i]/munge_dic['empl_week_hours'][i]))) # the number of pharmacists at centre i - adjusted for the number of hours they work per week
        data_intermed['Vax/Day'][i] = data_intermed['Booths'][i]*centre_vals['vaxHours'][i]*centre_vals['vph'][i] # the total number of vaccinations per day at centre i; calculated by multiplying (number of booths)*(hours per day)*(vaccines per booth-hour)
        data_intermed['Vax/Week'][i] = data_intermed['Booths'][i]*centre_vals['vaxHours'][i]*centre_vals['maxDays'][i]*centre_vals['vph'][i] # the total number of vaccinations per week at centre i; calculated by multiplying (number of booths)*(hours per day)*(days per week)*(vaccines per booth-hour)
        data_intermed['Booth %'][i] = (100*data_intermed['Booths'][i]/sum(data_intermed.Booths)) # the proportion of open booths which are at centre i

    data_intermed = data_intermed[['Booths', 'Booth %', 'Vacc', 'Circ_Vacc', 'Obs', 'Pharm', 'Reg_Adm', 'Vax_TL', 'Vax/Day', 'Vax/Week','Status']] # restricts the dataFrame data to these columns - eliminating the other columns
    data_intermed['Centre'] = centre_vals['centre']
    data_intermed['Booth Capacity %'] = (100*data_intermed.Booths/centre_vals['maxBooths']).fillna(0) # the percentage of booths at centre i which are open
    data_intermed['Index'] = centre_vals['index'] # adds an index column
    
    data_intermed = data_intermed.round(2)
    
    return data_intermed
    
def data_munge_2(data_intermed: pd.DataFrame, centre_vals: dict) -> pd.DataFrame: # takes the intermediate dataframe and converts it into format suitable for the front end 
    # More data munging
    
    output=data_intermed.copy()
    output = output.append(output.sum(numeric_only=True), ignore_index=True)
    
    # renames the columns to the appriate heading names and reorders them into an approptriate order
    col_dict={'Centre': 'Centre Name', 'Obs': 'Observers', 'Circ_Vacc': 'Circulating Vaccinators', 'Pharm': 'Pharmacists', 'Reg_Adm': 'Registration Admins', 'Vax_TL': 'Team Leads', 'Vax/Day': 'Vaccines Per Day', 'Vax/Week': 'Total Vaccines', 'Booth %': 'Percent Allocated', 'Vacc': 'Vaccinators', 'Booths': 'Booths Open'}
    output=output.rename(columns=col_dict)
    
    for key in ['Booths Open','Vaccinators','Circulating Vaccinators','Observers','Pharmacists','Registration Admins','Team Leads','Vaccines Per Day','Total Vaccines']:
        output[key]=output[key].astype(int) # sets certain columns to integer format
    
    output=output[['Centre Name', 'Percent Allocated', 'Booths Open', 'Vaccinators', 'Circulating Vaccinators', 'Observers', 'Pharmacists', 'Registration Admins', 'Team Leads', 'Vaccines Per Day', 'Total Vaccines']]
    
    output.iloc[-1, output.columns.get_loc('Centre Name')] = 'Totals' # renames the Centre Name in the totals record to 'Totals'
    output = output.round(2)

    output.index.name='ID' # relabels the heading of the index column
    output.index=output.index[:-1].to_list()+['#'] # relabels index of optimised_df to '#'
    
    return output # shows the optimised solution

    
def build(df: pd.DataFrame, vaccines_required: int) -> pd.DataFrame: # takes a csv file address of centres and returns DataFrame of the optimised solution
    df = str_to_bool(df)  # Convert 'enabled' and 'flex' columns to boolean columns due to Dash DataTable inability to display booleans
    centre_vals=DataFrame_to_dict(filter_data_by_column(df,'enabled')) # creates the cenre_vals dictionary for the rest of the functions to use
    model=run_the_model(centre_vals,vaccines_required) # cretes and runs the model
    parsed_model=model_parse(model) # parses the model into a table
    return data_munge_2(data_munge_1(parsed_model,centre_vals),centre_vals) # munges the data into a suitable format for the front end
########################################################################################################################################################################################################################
