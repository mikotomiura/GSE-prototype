import json,urllib.parse,urllib.request,time
def tf(g): return '('+' OR '.join(f'TITLE_ABS:{t}' for t in g)+')'
F=['fatigue','exhaustion','exhausted','burnout','"burn-out"','depletion','depleted','tiredness','weariness']
A=['"artificial intelligence"','"generative AI"','GenAI','ChatGPT','"large language model"','"large language models"','LLM','chatbot','"AI tool"','"AI tools"','"AI assistant"','"AI-assisted"','"AI use"']
X=['"fatigue life"','"fatigue crack"','"fatigue strength"','"fatigue damage"','"driver fatigue"','"driver drowsiness"','"fatigue detection"','"muscle fatigue"','battery','alloy','welded']
P=['survey','questionnaire','scale','participants','respondents','interview','interviews','"self-report"','students','employees','users']
def c(q):
    u='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode({'query':q,'format':'json','pageSize':1})
    return json.load(urllib.request.urlopen(u,timeout=60))['hitCount']
q6=tf(F)+' AND '+tf(A)+' NOT '+tf(X)
q7=tf(F)+' AND '+tf(A)+' AND '+tf(P)+' NOT '+tf(X)
for n,q in [('test TITLE_ABS:fatigue',tf(['fatigue'])),('Q6',q6),('Q7',q7),('Q7 from 2022-11-30',q7+' AND FIRST_PDATE:[2022-11-30 TO 2026-12-31]')]:
    print(n,c(q)); time.sleep(1)
