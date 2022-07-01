# Companionship-Network
This is a repository for a closer inspection of the renowned network for accompaniment.

### Install  
The code relies mostly on python native packages, it only needs ```pandas``` to create the network and ```networkx``` to execute everything. We **recommend using Anaconda**, as everything necessary is already installed in there, otherwise these packages can be manually installed by executing the following command:  
```$ pip install pandas networkx```  
Note: Pip has to be Version ```pip>=19.3``` to be able to install pandas from pip.

### Usage
To execute the code navigate into the ```src``` folder and execute the following command:  
```$ python run.py```  
  
For more output, verbose mode can be switched on like so:  
```$ python run.py -v```


### Results
We rank each seller according to the rankings they got. But in a further step we weight the reviews from the buyers, as some buyer give a lot of the same feedback as they always seem to have the same experience. This is not informative for the ranking, so we weight their input based on the reviews they give. After that we rank the sellers again, including the weighting of the buyers and analyze the rate of change between the two rankings. This change can be seen in the following plot, where changes are accumulated in bins of size 100.  
![The rate of change between the unweighted and the weighted rankings binned into bins of size 100.](/plots/100bag_rank_change_of_sellers_after_weighting_buyers.png)  
Negative numbers indicate a drop in ranks, whereas a positive number indicates a climb in the ranking.  
  