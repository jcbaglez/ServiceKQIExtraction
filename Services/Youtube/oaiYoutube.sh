
#sudo ip netns exec ueSpace5 python3 main.py --duration 60 --niter 20 --output "testOAI/ue1.json"
screen -dm -S youtube1 sudo ip netns exec ueSpace5 python3 main.py --duration 60 --niter 12 --output "testOAI/test25PRBs_2ue_3videos_5.json"
screen -dm -S youtube2 sudo ip netns exec ueSpace3 python3 main.py --duration 60 --niter 12 --output "testOAI/test25PRBs_2ue_3videos_3.json"
#screen -dm -S youtube3 sudo ip netns exec ueSpace3 python3 main.py --duration 60 --niter 10 --output "testOAI/test50PRBs_3ue_3_auto.json"