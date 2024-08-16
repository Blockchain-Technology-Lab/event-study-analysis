'''
Hi! 

Here is the code to run the event study analysis. The functions for the different models exist in the additional files. 
For more complete context on the project, visit the Notion page which details the proof of concept. 

That said, we have one main problem that we could use help addressing by whomever takes this on next: 
1. We ended up just visualizing the percentage change in the event window. However, the proper way to perform this analysis is to use a permutation test.
The test_significance function relies on a permutation test. We are not sure that this package accomplishes really what we are looking for. 
Ideally, we would follow this algorithm: https://link.springer.com/article/10.1007/s00181-023-02530-7 .... or something similar. 
In short, we need a way to test the significance of the abnormal returns differing from zero which does not rely on the assumption of normality (that a t-test does).
A permutation test is a way to do this. It is important to find single-firm permutation tests, as many tests assume testing an event across multiple firms.
'''
