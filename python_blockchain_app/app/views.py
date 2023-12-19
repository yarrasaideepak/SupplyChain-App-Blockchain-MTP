import datetime
import json
import requests
from flask import render_template, redirect, request
from app.Sentiment.SentimentalAnalysis import *
from app import app
from datetime import date

# The node with which our application interacts, there can be multiple
# such nodes as well.
CONNECTED_NODE_ADDRESS = "http://127.0.0.1:8000"

posts = []
RegUsers = []
FeedbackList = []

Capacity_of_Centre = []
RegUsers_Cap = []
tempered = []


def fetch_posts():
    get_chain_address = "{}/chain".format(CONNECTED_NODE_ADDRESS)
    response = requests.get(get_chain_address)
    if response.status_code == 200:
        content = []
        chain = json.loads(response.content)
        for block in chain["chain"]:
            for tx in block["transactions"]:
                tx["index"] = block["index"]
                tx["hash"] = block["previous_hash"]
                content.append(tx)

        global posts
        posts = sorted(content, key=lambda k: k['timestamp'],
                       reverse=True)
    
@app.route('/CheckSchedule')
def CheckSchedule():
    return render_template('CheckSchedule.html')


@app.route('/SceduledVacc', methods=['POST'])
def SceduledVacc():
    Sche_State = request.form["state"]
    Sche_Dist = request.form["district"]
    Sche_Mand = request.form["mandal"]
    Fin_Cap = 9999
    for i in range(0,len(Capacity_of_Centre)):
        if(Sche_State==Capacity_of_Centre[i][0] and Sche_Dist==Capacity_of_Centre[i][1] and Sche_Mand==Capacity_of_Centre[i][2] ):
            Fin_Cap = int(Capacity_of_Centre[i][3])
    
    data_users = []

    RegUsers_Cap.sort(key=lambda x: x[5], reverse=True)
    
    for i in range(0,len(RegUsers_Cap)):
        if(RegUsers_Cap[i][0]==Sche_State and RegUsers_Cap[i][1]==Sche_Dist and RegUsers_Cap[i][2]== Sche_Mand):
            yu=[];yu.append(RegUsers_Cap[i][3]);yu.append(RegUsers_Cap[i][4]);data_users.append(yu);
    
    
    return render_template('SceduledVacc.html',cap = Fin_Cap,data1 = data_users, pop = RegUsers_Cap)


@app.route('/SetCapacity')
def SetCapacity():
    return render_template('SetCapacity.html')

    
@app.route('/CapacitySetSuccessfully', methods=['POST'])
def CapacitySetSuccessfully():
    Cap_State = request.form["state"]
    Cap_Dist = request.form["district"]
    Cap_Mandal = request.form["mandal"]
    Cap_Capacity = request.form["capacity"]
    temp = []
    temp.append(Cap_State);temp.append(Cap_Dist);temp.append(Cap_Mandal);
    temp.append(Cap_Capacity);
    Capacity_of_Centre.append(temp);
    return render_template('CapacitySetSuccessfully.html')


@app.route('/')
def index():
    fetch_posts()
    return render_template('Index.html',
                           title='Add Vaccine Details '
                                 'to Blockchain',
                           posts=posts,
                           node_address=CONNECTED_NODE_ADDRESS,
                           readable_time=timestamp_to_string)

@app.route('/GetTheFeedback', methods=['POST'])
def GetTheFeedback():
    DrugName = request.form["ProdtName"]
    pos = []
    neg = []
    found = 0;
    for i in range(0,len(FeedbackList)):
        if(DrugName==FeedbackList[i][0]):
            for j in range(1,len(FeedbackList[i])):
                res = TheClassifier(FeedbackList[i][j])
                if(res=="Positive"):
                    pos.append(FeedbackList[i][j])
                else:
                    neg.append(FeedbackList[i][j])
            found = 1
        if(found==1):
            break;
    if(found==0):
        return render_template('NoFeedbackFound.html')
    else:            
        return render_template('GetTheFeedback.html',pos = pos,neg = neg)

@app.route('/CheckFeedback')
def CheckFeedback():
    return render_template('CheckFeedback.html')

@app.route('/Feedback')
def Feedback():
    return render_template('Feedback.html')

@app.route('/SubmitFeedback', methods=['POST'])
def SubmitFeedback():
    t1 = request.form["Customer Name"]
    t2 = request.form["Product Name"]
    t3 = request.form["Feedback"]
    found = 0;
    for i in range(0,len(FeedbackList)):
        if(t2==FeedbackList[i][0]):
            FeedbackList[i].append(t3);
            found=1;break;
    if(found==0):
        tr = []
        tr.append(t2);tr.append(t3);
        FeedbackList.append(tr);
        
    return render_template('FeedbackSent.html')
    
@app.route('/RegisteredPeople')
def RegisteredPeople():
    return render_template('RegisteredPeople.html',data=RegUsers)

def calculateAge(birthDate):
    today = date.today()
    age = today.year - birthDate.year - ((today.month, today.day) <(birthDate.month, birthDate.day))
    return age

@app.route('/SuccesfullyRegistered', methods=['POST'])
def SuccesfullyRegistered():
    o1 = request.form["FSTNAME"]
    o2 = request.form["LSTNAME"]
    o3 = request.form["DOB"]
    o4 = request.form["MARTSTAT"]
    o5 = request.form["GENDER"]
    o6 = request.form["ADDRNO"]
    o7 = request.form["EMLADDR"]
    o8 = request.form["PHNO"]
    o9 = request.form["ADDR"]
    o10 = request.form["PSTCODE"]
    temp_list = []
    temp_list.append(o1);
    temp_list.append(o2);
    temp_list.append(o3);
    temp_list.append(o4);
    temp_list.append(o5);
    temp_list.append(o6);
    temp_list.append(o7);
    temp_list.append(o8);
    temp_list.append(o9);
    temp_list.append(o10);
    
    DOB_Y = o3[0]+o3[1]+o3[2]+o3[3]
    DOB_M = o3[5]+o3[6]
    DOB_D = o3[8]+o3[9]
    
    age = calculateAge(date(int(DOB_Y),int(DOB_M),int(DOB_D)))
    
    if(age>45):
        RegUsers.append(temp_list);
        pz = []; pz.append(xx1);pz.append(xx2);pz.append(xx3);pz.append(o1+" "+o2);pz.append(o6);
        

        rating = 0;
        if(request.form["GENDER"]=="male"):
            rating = rating + 1;
        if(request.form["GENDER"]=="female" and request.form["pregnant"]=="YesPregnant"):
            rating = rating + 5;
        if(request.form["FrontWarrior"]=="FrontYes"):
            rating = rating + 5;
        if(request.form["PubInter"]=="HighInter"):
            rating = rating + 5;
        elif(request.form["PubInter"]=="MidInter"):
            rating = rating + 2;
        elif(request.form["PubInter"]=="LowInter"):
            rating = rating + 0;
        if(age>=80):
            rating = rating + 5;
        elif(age>=70 and age<80):
            rating = rating + 4;
        elif(age>=60 and age<70):
            rating = rating + 3;
        elif(age>=50 and age<60):
            rating = rating + 2;
        elif(age>=45 and age<50):
            rating = rating + 0;
            
        listed = request.form.getlist("SeleDise");

        if(listed[0]!="0Dis"):
            rating = rating + (len(listed)*5);
        pz.append(rating);
        RegUsers_Cap.append(pz);
        return render_template('SuccesfullyRegistered.html',rat = rating,p1 = request.form["FrontWarrior"],p2 = request.form["SeleDise"])

    else:
        return render_template('FailedDueToAge.html')

@app.route('/Enterprise')
def Enterprise():
    return render_template('Enterprise.html',posts=posts)

@app.route('/FirstPage')
def FirstPage():
    return render_template('FirstPage.html',posts=posts)

@app.route('/CandidateData', methods=['POST'])
def CandidateData():
    z1 = request.form["StateName"]
    z2 = request.form["DistrictName"]
    z3 = request.form["MandalName"]
    global xx1; xx1 = z1;
    global xx2; xx2 = z2;
    global xx3; xx3 = z3;
    return render_template('RegisterForVaccine.html',SName=z1,DName=z2,MName=z3,Quanti=1,posts=posts)
    
@app.route('/submit2', methods=['POST'])
def submit2():
    q1 = request.form["PdtSearchName"]
    q2 = request.form["PdtBatchNumber"]
    q3 = request.form["division"]
    return render_template('results.html',SearchName=q1,SearchBatch=q2,divison=q3,finding=True,posts=posts)


@app.route('/submit', methods=['POST'])
def submit_textarea():
    
    #post_content = request.form["content"]
    #author = request.form["author"]
    #author2 = request.form["author2"]

    p1   = request.form["content"]
    p2   = request.form["author"]
    p3   = request.form["BatchNo"]
    p4   = request.form["PdtDate"]
    p5   = request.form["ValPrd"]
    p6   = request.form["PkgDate"]
    p7   = request.form["PkgTime"]
    p8   = request.form["PkgInchargeName"]
    p9   = request.form["PkgOpr"]
    p10  = request.form["PkgMtrlName"]
    p11  = request.form["PkgMtrlNo"]
    p12  = request.form["InspRec"]
    p13  = request.form["PkgOpsDetails"]
    p14  = request.form["AbnormalReport"]
    p15  = request.form["InvestigatorName"]
    p16  = request.form["FinCheckRep"]
    p17  = request.form["IPdtName"]
    p18  = request.form["IDosageForm"]
    p19  = request.form["ISpec"]
    p20  = request.form["IBatchNo"]
    p21  = request.form["IQualStd"]
    p22  = request.form["IInspProc"]
    p23  = request.form["IInspEquip"]
    p24  = request.form["IBtchNoOfSol"]
    p25  = request.form["IBtchNoOfMed"]
    p26  = request.form["IBtchNoOfSrc"]
    p27  = request.form["IBtchNoOfStdPdt"]
    p28  = request.form["IInfAnimals"]
    p29  = request.form["IInspProcess"]
    p30  = request.form["IInspRes"]
    p31  = request.form["IDateOfInsp"]
    p32  = request.form["IInspDetails"]
    p33  = request.form["IRevName"]
    p34  = request.form["IDateOfRev"]
    p35  = request.form["CIdOfRecp"]
    p36  = request.form["CGenderOfRecp"]
    p37  = request.form["CAgeOfRecp"]
    p38  = request.form["CPdtName"]
    p39  = request.form["CBatchNo"]
    p40  = request.form["CInocAdd"]
    p41  = request.form["CInocTime"]
    p42  = request.form["CInocDate"]
    p43  = request.form["CInocDose"]
    p44  = request.form["CInocDept"]
    p45  = request.form["CInocDoc"]
    p46  = request.form["CState"]
    p47  = request.form["CDist"]
    p48  = request.form["CMandal"]
    p49  = request.form["CQuantity"]

    post_object = {
        
        #'content': post_content,
        #'author':  author,
        #'author2': author2,
        'content': p1,
        'author' : p2,
        'BatchNo': p3,
        'PdtDate' : p4,
        'ValPrd' : p5,
        'PkgDate' : p6,
        'PkgTime' : p7,
        'PkgInchargeName' : p8,
        'PkgOpr' : p9,
        'PkgMtrlName' : p10,
        'PkgMtrlNo' : p11,
        'InspRec' : p12,
        'PkgOpsDetails' : p13,
        'AbnormalReport' : p14,
        'InvestigatorName' : p15,
        'FinCheckRep' : p16,
        'IPdtName' : p17,
        'IDosageForm' : p18,
        'ISpec' : p19,
        'IBatchNo' : p20,
        'IQualStd' : p21,
        'IInspProc' : p22,
        'IInspEquip' : p23,
        'IBtchNoOfSol' : p24,
        'IBtchNoOfMed' : p25,
        'IBtchNoOfSrc' : p26,
        'IBtchNoOfStdPdt' : p27,
        'IInfAnimals' : p28,
        'IInspProcess' : p29,
        'IInspRes' : p30,
        'IDateOfInsp' : p31,
        'IInspDetails' : p32,
        'IRevName' : p33,
        'IDateOfRev' : p34,
        'CIdOfRecp' : p35,
        'CGenderOfRecp' : p36,
        'CAgeOfRecp' : p37,
        'CPdtName' : p38,
        'CBatchNo' : p39,
        'CInocAdd' : p40,
        'CInocTime' : p41,
        'CInocDate' : p42,
        'CInocDose' : p43,
        'CInocDept' : p44,
        'CInocDoc' : p45,
        'CState': p46,
        'CDist': p47,
        'CMandal': p48,
        'CQuantity': p49,
    }

    # Submit a transaction
    new_tx_address = "{}/new_transaction".format(CONNECTED_NODE_ADDRESS)

    requests.post(new_tx_address,
                  json=post_object,
                  headers={'Content-type': 'application/json'})
    return redirect('/')


def timestamp_to_string(epoch_time):
    return datetime.datetime.fromtimestamp(epoch_time).strftime('%H:%M')
