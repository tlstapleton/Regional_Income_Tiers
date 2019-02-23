# Regional Income Tiers

This code will assign households to relative regional income tiers based on the household size, household income, and the Metropolitan
Statistical Area in which the household resides.

# Background

Household income can vary widely across the United States.  Particularly when comparing income levels across regions, certain regions have a significantly higher or significantly lower median household income than the U.S. median household income.  To truly get a sense of a household’s economic status, a household’s income must be measured against cost of living in the region and household size.

# Inputs

Households are pulled from the Experian household dataset.  The household counts by Metropolitan Statistical Area, household size, and household income were pulled using Alteryx initially.  These counts are in the file Inputs/HHFile_Counts_By_CBSAMET.csv.  This file is the input for the Python code, which uses the household variables to assign each household into an income tier of lower, middle, or upper.
The other file in the Inputs folder, Inputs/Regional_Price_Parity.csv, contains the regional price parities for every Metropolitan Statistical Area in the United States according to the U.S. Bureau of Economic Analysis.  These are used as measurements of geographical cost of living.

#Methodology

The full methodology is outlined in the file Regional_Income_Tiers_Documentation.docx.

The code that executes this methodology is Assign_Income_Tiers_Final.py.  The final lookup table output by the code is income_tier_lookup_table.csv.