import json

sequence_onset = 2000
numEvents = 8
onset_distance = 150000

dic = {'sequence0':{}}
for i in range(0,numEvents):
	dic['sequence0']['event' + str(i)] = {"onset":sequence_onset+i*onset_distance,
					      "duration":20000,
					      "pulsewidth":5,
					      "frequency":20,
					      "amplitude":100,
					      "OUTchannel":"D"}

with open('gensequences.json','w') as fp:
	json.dump(dic,fp,sort_keys=True,indent=4,separators=(',',':'))
