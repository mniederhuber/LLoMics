# functions to check logic of llm output and generate samplesheets
# logic for llm check:
# - disagreements between bool and character variables, ie. time_series is False but time_point has a value
#   this case should raise a flag for human review
# - disagreement within a set of experiments, ie. one experiment is marked as gene_mutation but none of the rest are
# - regular expression check, look for keys like WT, wild type etc. and flag if they are marked incorrectly
# - disagreement between general perturb and wt variables, and speicific sub variables
import pandas as pd

def bool_check(df):
    """
    Check for inconsistencies between boolean and character variables
    """
    var_dict = {'mutation':'gene_mutation',
                'deletion':'gene_deletion',
                'depletion':'protein_depletion',
                'stress':'stress_condition',
                'time_point':'time_series'}

    # loop through the rows and check for inconsistencies
    check = []
    # for each row in the df, check if any of the bool and char variables disagree
    for i in range(len(df)):
        mismatch = False 
        for var in var_dict:

            if df.loc[i, var_dict[var]] == False and pd.isnull(df.loc[i, var]) == False:
                mismatch = True 
            elif df.loc[i, var_dict[var]] == True and pd.isnull(df.loc[i, var]) == True:
                mismatch = True

        if mismatch:
            check.append(True)
        else:
            check.append(False)
    df['warning'] = check

    return df

def balance_check(df, balance = 0.3):
    """
    Check if true false counts are dramatically imbalanced for each variable.
    ie. if there are only one or two rows that are marked as gene_mutation, this could be an error
    """
    vars = ['gene_mutation','gene_deletion','protein_depletion','stress_condition','time_series']
    check_dict = {} 
    for var in vars:
        true_count = df[var].count(True)
        false_count = df[var].count(False)
        ratio = true_count / false_count
        if ratio <= balance or 1/ratio <= balance:
            check_dict[var] = True
        else:
            check_dict[var] = False

    balance_df = pd.dataframfrom_dict(check_dict, index = [0]) 
    return balance_df    

#def title_check(df):
    """
    Check for regular expression matches in the variables
    """
