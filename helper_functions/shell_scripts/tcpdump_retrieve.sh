#!/bin/bash 
i=1
file=$@
file_=$@
file1=$@

kubectl exec -it -n kong-istio  kong-istio-kong-84c984887f-7jt6x -c tcpdump-sidecar -- tcpdump -w /tcpdump/$file -C 30k  >  /dev/null 2>&1 &
 
while true 
do
	
	while  kubectl exec -it -n kong-istio kong-istio-kong-84c984887f-7jt6x -- test ! -f /tcpdump/$file_$i	
	#while true
	do
		
		echo "waiting for $file.."
		sleep 30
	done
	
	echo "$file1 was copied"
	kubectl cp -n kong-istio kong-istio-kong-84c984887f-7jt6x:tcpdump/$file  -c tcpdump-sidecar ~/Documents/Dataset/Anomalies/$file1 
	file=$file_$i
	file1="${file_%%.*}"$i.pcap
	let i++
done
	
kubectl exec -it -n kong-istio  kong-istio-kong-84c984887f-7jt6x -c tcpdump-sidecar --kill %-
