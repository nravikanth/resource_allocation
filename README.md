# resource_allocation
# Resource allocation script 
The Resource Allocator is responsible for assigning servers for users based on their needs.  
Each server has X number of CPUs.  
The available servers types are: 
● large     ­ 1 CPU 
● xlarge    ­ 2 CPU 
● 2xlarge   ­ 4 CPU 
● 4xlarge   ­ 8 CPU 
● 8xlarge   ­ 16 CPU 
● 10xlarge  ­ 32 CPU 
 
The cost per hour for each server would vary based on the data centre region. 
 
Users will be able to request for  
● minimum N CPUs for H hours 
● maximum price they are willing to pay for H hours  
● or a combination of both. 
 
Examples: 
1. Alice would like to request for servers with minimum 135 CPUs for 24 hours. 
2. Bob would like to request as many possible servers for $38 for 10 hours. 
3. Charlie would like to request for minimum 180 CPUs and wouldn't want to pay for more 
than $65 for 6 hours.

This code give result for first two case, but not for third, as its yet to implement



