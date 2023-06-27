#!/bin/bash 
i=1
file=$1
file_=$1
file1=$1
echo "$#"
if [ $# -eq 3 ]
	then 
	kubectl exec -it -n kong-istio  $2 -c tcpdump-sidecar -- tcpdump -w /tcpdump/$file -C 30k  >  /dev/null 2>&1 &
 
	while true 
	do
	
		while  kubectl exec -it -n kong-istio $2 -- test ! -f /tcpdump/$file_$i	
		#while true
		do
		
			echo "waiting for $file.."
			read -t 30 -n 1 k
                	[[ "$k" == 's' ]] && break
                	
		done
                [[ "$k" == 's' ]] && break
		echo "$file1 was copied"
		kubectl cp -n kong-istio $2:tcpdump/$file  -c tcpdump-sidecar ~/Documents/Dataset/$3/$file1 
		file=$file_$i
		file1="${file_%%.*}"$i.pcap
		let i++
	done
	
	kubectl exec -it -n kong-istio kong-istio-kong-84c984887f-vksct   -c tcpdump-sidecar -- kill %1
else
	echo "need to add three command line aguments <file name> <pod name> <folder>"
fi
