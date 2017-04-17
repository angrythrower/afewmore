CS 615 Homework #6
Author: Tianxiao Yang and Josh-Erik Dolisca

Contents
**********************************

1. Introduction/Summary
2. Script Development
3. Challenges
4. Unix Philosophy and the Zen of Python

**********************************

-------------------------------

1. Introduction/Summary

-------------------------------

This document is meant to provide commentary to the assignment regarding the tool "afewmore(1)". Afewmore is a tool that will duplicate an EC2 instance. It will also copy data from the original EC2 instance to the copied instances. You can specify the amount of new instances to be created from the original and the directory to copy from the original as well. The tool will simply give you the list of instance IDs for the newly created instances. If more information is required, you can use the "-v" option to output the log of each step of the instance creation for each instance. If you need assistance on how to use the tool, you can use the "-h" option.

We built the tool using python as it was the best tool for us to use as a group and it works well with the concepts in "The Zen of Python", by Tim Peters. We tested afewmore(1) in an Ubuntu instance with an image ami-6de0dd04. In order to set up the environment with the awscli package, we needed to run 'sudo apt-get update' to resynchronize the package index files from the source. We then installed awscli with 'sudo apt-get install awscli'. It was apparent that we could use HW#1 to set up this instance with our aws configurations. As we already have account information, we simply needed to get the public, access, and secret access keys onto the aws config on this Ubuntu instance. Our security groups are already created and our private key name is available to us. After configuring the profile and putting the public key location in `/.ssh/config we have the basic environment setup for the tool.

-------------------------------

2. Script Development Results

-------------------------------

As stated before, we decided to use python to build out this tool. There were a number of reasons that we chose python. In regards to the group, it was the best tool to use regarding our knowledge of programming languages. It is a scripting language meant for ease of use. It was the simplest option as there was no need to compile code, like C/C++. The learning curve is also a factor, as there are more rules and regulations for syntax and use. This also plays a role in scalability. Expanding on this tool is simple whether you want to write directly in the file or import it and all its functions and definitions into another tool. 

For this script, we decided to create classes to group instance data together for ease of access and functions to implement the actions taken in the script. Our classes are: SecurityGroup and Instance. SecurityGroup is meant to hold all the information regarding the security groups of an instance. Since there can be multiple security groups, we decided to make a class to properly group the information. The instance class is the main class that groups all the information about the instance: instance id, availability zone, image id, public ip, public DNS name, user name of the instance, and the key name. This makes an object that we can store and retrieve information from with ease. We split our functions based on the action required of the tool: execute a command in bash, analyze the original and created instances, duplicate an original instance, verify the duplicate is up, SCP the data from the original instance to the copied instance, and start the tool based on script arguments. These functions allowed us to run the main script that would take in the user input as per the manual page and perform the function that the tool afewmore was meant to perform; create multiple of one instance. 

-------------------------------

3. Challenges

-------------------------------

There were a number of challenges we faced while developing the script. 

One issue that we ran into was waiting for the new instance to come up. After the script runs command 'aws ec2 run-instances', there could be a delay(about 30-70 seconds) before we can actually run commands on the newly created instance. We need to make sure the instance is ready before we can access the instance to copy the files. The official way aws cli provided us is to use 'aws ec2 describe-instance-status --instance-id' to check if the instance is available for use, but this request only update every 60 seconds. This would waste a lot of time for a large number of duplicate instances as instances only need about 30 seconds to come up. We realized that command ssh-keyscan(1) will return the host public key when the host is ready, so we decided to base our uptime check on whether we can retrieve the host public key from the newly created instance. This concept is utilized in the isReady() function in the Instance class.

Another part of the assignment that was challenging was copying the data from the source instance to the new instances. Newly created instances may not have the same directory as the source instance, so we need to create the same directory before copying the content. In order to do so, we need the proper permissions to copy and paste content. To accomplish this, we have to use superuser command to change the file owner and file mod in the source and target instances. The final step in transferring the data is the actual connection between hosts and transfer. We were planning to use rsync(1) at beginning, but it seems like not all instances have this command. Also, if we use rsync, we may need to upload our private key or create a new key pair on source instance. This may become a security concern to have a source instance configured with aws. We also run into the issue of how to transfer the public key since we need it to start the transfer. We choose scp(1) to copy directory content between instances directly.

The biggest hurdle for the scalability of the tool is that we don't have login username when we create a new instance as the instance could be any OS. Instead of hard coding in the user names of most popular operating systems, we found out that we can just login as root user and ec2 will give us an output with the right username if we can't just use root username for that image. 

------------------------------------------

4. Unix Philosophy and the Zen of Python

------------------------------------------

On top of the functionality of our script, we tried to ensure to follow most of the principles discussed in class regarding coding. As far as the Unix Philosophy goes, our script will only duplicate instances as per the manual page. It will do no more and no less and it does it repeatedly with the same result. It can work with other programs as it just needs to be executed. IT can also be imported to another python script to help perform other tasks. All of its input data is from the command line, so it handles text streams well. Any other script can call the tool with its own specific options for its purpose.

As for the Zen of Python, we feel that we've complied with many of the principles. There are some that are apparent and some that are not. There are also some that correlate.

-Beautiful is better than ugly/Readability Counts
The source code for the script is formatted to be read by human eyes. Proper indentation for classes, functions, and control statements make it easy to see what parts of the code belong to a specific part. The variables and function names have also been written out as names or words that humans can understand, not random jargon created on the fly. Being able to read the code is part of its scalability to grow and become part of another tool. 

-Explicit is better than implicit/In the face of ambiguity, refuse the temptation to guess
The python script that we developed, there were certain aspects that we had to know for sure. In regards to the public key for the duplication and copying of data, we had to be explicitly aware of the aws configuration and the host setup to know that the system would run the ssh command a specific way. We also couldn't assume that we could log in with root. Due to the ambiguity of the user name options for a wide range of hosts, we needed to develop a sure way to get the right user. We cannot assume that an instance will always be SuSE or Solaris or FreeBSD. Our code goes out and finds exactly what the login user is. Using "self" to be explicit in which object the functions are getting the information from is also a factor.

-Simple is better than complex/Complex is better than complicated
All our code is clear and concise. The control and conditional statements are clear defined and explained in the notes of the script. While it took multiple lines to write some of the functions, it was done simply without round about methods. Instead of going out of our way to create special keys for the source instance to use rsync to transfer the contents of the copy directory, we found the simpler way of looking for the host key, which tells us what we're looking for. 

-Sparse is better than dense
We attempted to use as few lines of code to perform these functions as possible. Proper grouping of variables and control statements helped make it less dense overall

-Errors should never pass silently/Unless explicitly silenced.
All of the errors handled by the script have explicit messages that tell us what went wrong and why. Assistance is given in the form of the help option of the tool and you can be verbose to see exactly where something failed in the script.

-In the face of ambiguity, refuse the temptation to guess
Verifying the instances were up and running through the isReady() function was one way that we ensured that we can continue and run the program. Most of the conditions that the program checks makes sure that there is no room for error. It is either up or down, the directory is either there or it isn't. 

-If the implementation is hard to explain, it's a bad idea/If the implementation is easy to explain, it may be a good idea
The implementation is explained throughout the script with comments on the major pieces of the code. 

The principle that we could work on in the future the most is "Flat is better than nested." We wanted to limit the amount of separate functions and options that the code went through, so we nested some conditional statements that we may have been able to flatten, however as far as our knowledge goes, this was the best option. 
