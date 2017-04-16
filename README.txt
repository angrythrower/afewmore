Problems:

1. Newly created instances may not have the same directory as source instnace, so we need to 
create the same direcotry before copying the content.

2. Since we need the permission to copy and paste content, we need to use superuser command to change
file owner and file mod. 

3. We don't have login username when we created a new instance, we found out that we can just login as root user,
and ec2 will give us the right username if we can't just use root username.

4. We were planning to use rsync(1) at beginning, but it seems like not all instance have this command. 
And if we use rsync, we may need to upload our private key or create a new key pair on source instance. This
may couse security problems. So we choose scp(1) to copy directory content between instances.

5. After ran command 'aws ec2 run-instances', there could be a delay(about 30-70 seconds) before we can actually 
run command on the newly created instance. So we need to make sure the instance is ready before we copy the files. 
The offical way aws cli provided us is to use 'aws ec2 describe-instance-status --instance-id' to check if the 
instance if available for use, but this request only update every 60 seconds, and for some instance, they only need 
about 30 seconds to be ready. Then we found out that command ssh-keyscan(1) will return the host public key when the
host is ready, that is why we have a isReady() function in Instance class.
