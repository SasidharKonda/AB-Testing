# Binomial Metric - Order Conversion

p_cntrl = length(df$orders)/length(df$visitors)         #Baseline conversion in Control -> 7.8%
p_trt = (0.0125+1)*p_cntrl                              #Conversion rate if increased by 1.25% to 7.9%

#Power analysis
pwr_Conv = power.prop.test(p1= p_cntrl,p2 = p_trt,
                           sig.level = 0.05,power = 0.80,alternative = "two.sided")

/*
  Two-sample comparison of proportions power calculation 

n = 1135539
p1 = 0.078
p2 = 0.079
sig.level = 0.05
power = 0.8
alternative = two.sided

NOTE: n is number in *each* group
*/
Orders_per_day =  length(df$order_id)/length(unique(df$ord_date))  #225000
days_req = ceiling(pwr_Conv$n*2/Orders_per_day)                    #11 days

#Non-binomial Metric - Avg. Units per Order
arms = 2                               #Number of arms in the experiment control & Treatment
Avg_upo_ctrl = mean(df$units)          #Mean of Control
Avg_upo_trt = (0.005+1)*Avg_upo_ctrl   #0.5% Change you want to see in treatment

Std_Dev_units = sd(df$units)           #Standard Deviation in units

# Power Analysis
power.t.test(delta = abs(Avg_upo_ctrl - Avg_upo_trt) ,sd = Std_Dev_units,
            sig.level = 0.05,power = 0.80,alternative = 'two.sided')   

/*
      Two-sample t test power calculation 

              n = 1673735
          delta = 0.006446556
             sd = 2.105
      sig.level = 0.05
          power = 0.8
    alternative = two.sided

NOTE: n is number in *each* group
*/

Orders_per_day =  length(df$order_id)/length(unique(df$ord_date))  #225000
Days_req = arms * Pwr_upo$n/Orders_per_day                         #15
