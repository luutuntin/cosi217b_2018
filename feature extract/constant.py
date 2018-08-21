nonCoreLabels = ['accompanier','age','benericiary','compared-to','concession','condition','consist','degree','destination','direction','domian','duration','example','extent','frequency','instrument','location','cause','manner','medium','mod','mode','name','ord','part','path','polarity','poss','purpose','quant','scale','source','subevent','time','topic','unit','value']
dateEntityLabels = ['calender','century','day','dayperiod','decade','era','month','quarter','season','timezone','weekday','year','year2']

prepLabelsPart = ['against','along-with','amid','among','as','at','by','concerning','considering','despite','except','excluding','following','for','from','in','in-addition-to','in-spite-of','into','like','on','on-behalf-of','opposite','per','regarding','save','such-as','through','to','toward','under','unlike','versus','with','within','without']
prepLabels = ['prep-'+ e for e in prepLabelsPart]

inverseLabels = [e + '-of' for e in Labels]

#following are entity type
person = []
#...

#followinf are mathematical operators

all_labels = labels.extends(inverseLabels)