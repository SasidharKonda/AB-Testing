# importing required packages

import pyodbc
import textwrap
from numpy import nansum
from numpy import nanmean
import pandas as pd
import statsmodels.stats.api as sms
from scipy import stats as st

#Establish connection with Teradata 
cnx_tera = ('DRIVER={<Driver Name>};'
 	    'DBCNAME=<DBCNAME>;'
	    'DATABASE=<DATABASE NAME>;'
	    'AUTHENTICATION=LDAP;'
	    'UID=<Username>;'
	    'PWD=<Password>')

#Write the SQL query and import data into a dataframe
sql = textwrap.dedent("""select * from tablename""")
cnx = pyodbc.connect(cnx_tera) #Opening connection
df = pd.read_sql(sql, cnx) #Reading a table into dataframe
cnx.close() #Closing connection

#Read into another Dataframe
test_data = df
test_data.head(5) # Output look like below

#Add necessary metrics to data frame
test_data['cust_accept_rate']=(test_data.Accepted_Qty/test_data.TOT_QTY);

#Splitting data into TestA and TestB groups
test_data_A = test_data[test_data.TestGroup == 'TestA']
test_data_B = test_data[test_data.TestGroup == 'TestB']

#Clean the data by removing orders with 0 items or having more items than 99.5th percentile orders
print(test_data_A.TOT_QTY.quantile(.995))
test_data_A_clean = test_data_A[(test_data_A.TOT_QTY>0) & (test_data_A.TOT_QTY<test_data_A.TOT_QTY.quantile(.995))]

#Combine the cleaned data sets as one
test_data_clean = test_data_A_clean.append(test_data_B_clean)
test_data_clean.head(100)

#Summarize the metrics:- Calculating totals
test_summary1 = test_data_clean.groupby('TestGroup').agg(
{
    ,'TOT_QTY':'sum'
    ,'Accepted_Qty':'sum'
}
)

#Summarize the metrics:- Calculating means
test_summary2 = test_data_clean.groupby('TestGroup').agg(
{
          'TOT_QTY':'mean'
          ,'Accepted_Qty':'mean'
          ,'cust_accept_rate':'mean'
}
)

#Transposing the summaries
test_summary1 = test_summary1.T
test_summary2 = test_summary2.T

#Initialize a dataframe with test stats
test_stats = pd.DataFrame(columns = ['pct_lft','conf_int_lb','conf_int_rb','p-value'])
    
#Concatenate the test stats with both the summaries
test_summary1 = pd.concat([test_summary1,test_stats],axis=1,ignore_index=False,sort=False)

#Calculate pct_lift for all the metrics
test_summary1['pct_lft'] = (test_summary1['TestB']/test_summary1['TestA'])-1
test_summary2 = pd.concat([test_summary2,test_stats],axis=1,ignore_index=False,sort=False)

#Calculate pct_lift for all the metrics
test_summary2['pct_lft'] = (test_summary2['TestB']/test_summary2['TestA'])-1

#Calculate the test stats
for i in test_summary2.index:
    #Comparing means
    cm = sms.CompareMeans(sms.DescrStatsW(test_data_A_clean[i][test_data_A_clean[i].notnull()]),
			sms.DescrStatsW(test_data_B_clean[i][test_data_B_clean[i].notnull()]))
    #Extracting left boundary and right boundary
    lb,rb = cm.tconfint_diff(usevar='unequal',alternative='two-sided',alpha = 0.10)
    
    #Convert the lb and rb to lb lift and rb lift         
    test_summary2.at[i,'conf_int_lb'] = (rb*-1)/test_data_A_clean[i].mean()
    test_summary2.at[i,'conf_int_rb']=  (lb*-1)/test_data_A_clean[i].mean()
    
    #p-value
    t_stat,test_summary2.at[i,'p-value'] = st.ttest_ind(test_data_A_clean[i][test_data_A_clean[i].notnull()],
               				test_data_B_clean[i][test_data_B_clean[i].notnull()],equal_var = False)

print(test_summary2)
