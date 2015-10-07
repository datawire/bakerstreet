clean:
	rm -rf kubernetes/

k8s_download:
	rm -rf kubernetes/
	curl -OL https://github.com/kubernetes/kubernetes/releases/download/v1.0.6/kubernetes.tar.gz
	tar -xf kubernetes.tar.gz

k8s_up:
	cd kubernetes/cluster/; ./kube-up.sh

k8s_down:
	cd kubernetes/cluster/; ./kube-down.sh

k8s_pods:
	kubectl get pods

bs_directory_up:
	kubectl create -f ./directory_pod.yml

bs_directory_down:
	kubectl delete pod directory

bs_directory_logs:
	kubectl logs directory

bs_watson_up:
	kubectl create -f ./watson_pod.yml

bs_watson_down:
	kubectl delete pod watson

bs_sherlock_up:
	kubectl create -f ./sherlock_pod.yml

bs_sherlock_down:
	kubectl delete pod sherlock