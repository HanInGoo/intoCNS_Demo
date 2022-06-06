import flask
import os
from flask import send_from_directory, request
import pandas as pd
#import numpy as np

app = flask.Flask(__name__)

input_data=[]
columns_next=[]

save=[]
row_del=[]

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/favicon.png')


@app.route('/')
@app.route('/home')
def home():
    return "Hello World"


@app.route('/webhook', methods=['POST'])
def webhook():
    IntoCNS_finish_1count_data_movement = ''
    IntoCNS_finish_data_movement_visualization = ''
    IntoCNS_finish_for_recovering = ''
    IntoCNS_finish_restart = ''
    IntoCNS_finish = ''
    IintoCNS_user_for_recovering = ''
    IntoCNS_user_restart = ''
    IntoCNS_user = ''

    req = request.get_json(force=True)
    #print(req)
    bot = ""
    global input_data

    user = req['queryResult']['queryText'] # 유저가 입력한 값을 가져오는 코드

    if req['queryResult']['parameters'].get("Symptom"):  # 질병이 입력되는 경우 질병의 명칭을 가져오기 위한 조건문
        symptom = []
        for i in range(0, len(req['queryResult']['parameters']['Symptom']), 1):
            symptom.append(req['queryResult']['parameters']['Symptom'][i])

    bot_intent = req['queryResult']['intent']['displayName']  # intent 입력

    print(req['queryResult'])
    print()
    print(" => user : ",user)
    print(" => intent : ",bot_intent)


    user_file = pd.read_csv(IntoCNS_user)  # IntoCNS-user.csv를 불러온다.
    user_pd = pd.DataFrame(user_file)  # pandas를 이용하여 데이터 프레임 형태로 변경


    if bot_intent=='001_search_disease':

        save.clear()

        ##################################################
        if req['queryResult']['parameters'].get("Symptom"):
            user_pd_check = list(user_pd.columns.values)  # 모든 증상들을 리스트에 저장한다.
            disease = []
            for i in range(0, len(symptom), 1):
                for j in range(0, len(user_pd_check), 1):
                    if symptom[i] == user_pd_check[j]:  # 리스트에 있는 요소가 증상에 포함되지 않는다면
                        disease.append(symptom[i])  # 해당 위치에 0을 넣는다.

            print(" => entity : ", end="")
            for i in range(0, len(disease), 1):
                if len(disease) == i + 1:
                    print(disease[i])
                else:
                    print(disease[i], end="")
                    print(", ", end="")

            print("")

        ##################################################

        for i in range(0, len(disease), 1):
            if bot_intent != 'no':
                 input_data.append(disease[i])



    if bot_intent=='999_restart': # 처음부터 다시 시작

        restoration_user = pd.read_csv(IntoCNS_user_for_recovering)
        restoration_user.to_csv(IntoCNS_user, index=False, encoding='utf-8-sig')

        restoration_intocns = pd.read_csv(IntoCNS_finish_for_recovering)
        restoration_intocns.to_csv(IntoCNS_finish, index=False, encoding='utf-8-sig')

        input_data.clear()
        row_del.clear()
        save.clear()
        columns_next.clear()

        print("===========================================")
        bot = "다시 시작합니다. 증상을 입력해 주세요."
        print("===========================================")

        return {
            'fulfillmentText':bot
        }

    if bot_intent=='000_yes':  # 예를 누르면 input 새로운 증상이 추가된다.
        input_data.append(save[0]) # 추천되었던 증상 input_data에 입력
        save.clear()



    if bot_intent == '000_do not know':
        columns_next.append(save[0])

        save.clear() # 현재 save 증상 존재하는 지 모른다고 하였기 때문에 save증상을 삭제하여 input_data에 추가하지를 않는다.

    if bot_intent=='000_no':
        row_del.append(save[0])


        save.clear()  # 현재 save 증상 존재하지 않는다고 하였기 때문에 save 증상을 삭제하여 input_data에 추가하지를 않는다.


    ################################### 리스트 입력 중에 중복 되는 증상 삭제 ###################################

    overlap_del = set(input_data)  # 집합set으로 변환
    input_data = list(overlap_del)  # list로 변환


    ################################### 리스트 입력 값에 해당하는 곳에 1 값 넣기 ################################

    for i in range (0,len(input_data),1): # 리스트에 들어있는 값의 길이 만큼 반복해준다.
        user_pd.loc[len(user_pd)-1, input_data[i]] = 1 # 리스트에서 나온 증상과 같은 증상을 user_pd에서 찾아 해당 위치에 1을 입력해준다.
    user_pd.to_csv(IntoCNS_user, index=False, encoding='utf-8-sig')
    # user_pd.to_csv('C:/Users/dlsrn/Desktop/intoCNS_folder/IntoCNS-user(시각화).csv', index=False, encoding='utf-8-sig')


    ################################### 해당 증상 열에 1이 없을 경우 질병 삭제 #####################################################

    intocns_file = pd.read_csv(IntoCNS_finish) # intoCNS 데이터 파일을 불러온다.
    intocns_pd=pd.DataFrame(intocns_file) # pandas를 이용하여 데이터 프레임 형태로 변경

    for i in range(0, len(input_data), 1):
        dele = intocns_pd[intocns_pd[input_data[i]] != 1].index # 리스트에서 나온 증상과 같은 intocns 에서의 증상의 위치에서
                                                                # 1이 포함되지 않는다면 행의 위치를 가져온다.
        intocns_pd = intocns_pd.drop(dele) # 가져온 1일 포함되지 않는 행의 위치를 이용하여 해당 행을 삭제한다.


    intocns_pd2 = intocns_pd.reset_index() # 행의 위치를 삭제하면 index의 순서가 0,1,2,3... 순서가 아닌 기존의 인덱스의 위치를 가져온다. 그래서 그것을 다시 0,1,2,3,4 순서로 재배치 해준다.
                                           # ex) 0,1,2,3,4,5,6 -> (인덱스 3, 4 삭제) -> 0,1,5,6,7 -> (인덱스 재배치) -> 0,1,2,3,4  ( O )
                                           #                                       -> 0,1,2,3,4 ( X )
                                           # 이렇게 해야지 인덱스 순서를 적용할 수 있음

    intocns_pd.to_csv(IntoCNS_finish, index=False, encoding='utf-8-sig') # 수정된 데이터를 다시 저장한다.
    intocns_pd.to_csv(IntoCNS_finish_data_movement_visualization, index=False, encoding='utf-8-sig') # 실질적으로 사용되는 csv파일은 나중에 초기화 된다. 그래서
                                                                                                                         # 이전 작업에서 마지막 결과가 어떻게 도출되었는지 보여주기 위한 csv파일잉다.


    ################################### 최종 출력 리스트에 담기 #####################################################

    result_list = [] # 최종적으로 도출된 질병의 이름을 저장하기 위한 리스트들이다.

    for i in range(0, len(intocns_pd2.index), 1):
        result_list.append(intocns_pd2.loc[i, '쿼리']) # 삭제하고 남은 질병들을 리스트에 담아 넣는다.

    print("=============================================================================================================================================================================")
    print("                                                                       ***** 남은 질병 리스트 ***** ")
    print("")

    count=0
    count2=0
    for i in range(0,len(result_list),1):
        print("[",result_list[i],"]",end=" ")
        count=count+1
        count2=count2+1

        if count==10:
            print("\n")
            count=0

    print("")
    print("=============================================================================================================================================================================")
    print("")
    print("=> 남은 질병의 수 : ", count2 )


    ################################### 최종 질병 리스트에 존재하는 요소가 없는 경우 ##########################################

    if len(result_list)==0: # 해당 증상으로 발생하는 질병이 존재하지 않는 경우
        bot='해당 증상과 관련된 질병은 존재하지 않습니다. 다시 입력해 주세요'

        # 다시시작하기 위해서 IntoCNS-user 파일 초기화
        restoration_user = pd.read_csv(IntoCNS_user_for_recovering)
        restoration_user.to_csv(IntoCNS_user, index=False, encoding='utf-8-sig')

        # 다시시작하기 위해서 IntoCNS-finish 파일 초기화
        restoration_intocns = pd.read_csv(IntoCNS_finish_for_recovering)
        restoration_intocns.to_csv(IntoCNS_finish, index=False, encoding='utf-8-sig')

        input_data.clear()
        row_del.clear()

        return {
            'fulfillmentText': bot
        }


    ################################### 최종 질병 리스트에 존재하는 요소가 10이하로 좁여지는 경우 ###############################

    if len(result_list)<=10:
        print("=============================================================================================================================================================================")
        print("                                                                  ***** [최종] 출력 되는 질병 리스트 ***** ")

        print("")
        print(result_list)

        print("=============================================================================================================================================================================")

        print("")
        bot="===== [ 질 병 ] ====="

        for i in range(0,len(result_list),1):
            bot=bot+"\n"+"- "+result_list[i] # 각 출력할 질병 text들을 변수에 저장

        ############################################# 다음 user를 입력받기 위한 준비
        number = len(user_pd) + 1  # user_pd에서의 마지막 행의 index에서 추가로 늘어날 index의 값을 넣어준다.

        user_name = 'user' + str(number) # 행 이름을 user1, user2 user3, user4... 같이 늘려준다.



        user_pd.loc[len(user_pd), '쿼리']= user_name


        user_pd = user_pd.fillna(0)  # 데이터 프레임에서 NaN값을 0으로 대처한다.

        #############################################

        # 다시시작하기 위해서 IntoCNS-user 파일 초기화
        restoration_user=user_pd
        restoration_user.to_csv(IntoCNS_user_for_recovering, index=False, encoding='utf-8-sig')
        restoration_user.to_csv(IntoCNS_user, index=False, encoding='utf-8-sig')

        # 다시시작하기 위해서 IntoCNS-finish 파일 초기화
        restoration_intocns = pd.read_csv(IntoCNS_finish_for_recovering)
        restoration_intocns.to_csv(IntoCNS_finish, index=False, encoding='utf-8-sig')


        result_list.clear()
        input_data.clear()
        row_del.clear()

        return {
            'fulfillmentText': bot
        }


    ################################# 정보가 부족하여 10 이하로 질병리스트가 좁혀지지 않는 경우 추천을 해주는 코드 ##############################
    else:
        restoration_intocns = pd.read_csv(IntoCNS_finish_for_recovering)
        intocns_pd3 = restoration_intocns # intocns_pd3는 가상 데이터프레임




        for i in range(0, len(input_data), 1):
            intocns_pd3 = intocns_pd3.drop(columns=[input_data[i]]) # 이전에 사용하였던 input_data에 존재 하는 증상들을
                                                                    # 가상데이터 데이터프레임의 열에서 삭제하였다.

        for i in range(0, len(columns_next), 1):
            intocns_pd3 = intocns_pd3.drop(columns=[columns_next[i]]) # 추천 하려고 했지만 yse가 아니여서 열에서 삭제하는 것들


        for i in range(0, len(row_del), 1):
            dele2 = intocns_pd3[intocns_pd3[row_del[i]] == 1].index  # 열에 1이 포함된 행의 위치를 가져온다.

            intocns_pd3 = intocns_pd3.drop(dele2)  # 1일 포함된 행의 위치를 이용하여 해당 행을 삭제한다.



        ################################# 빈도를 이용하여 다음으로 주천해 줄 값을 찾는다.

        #input_data에 존잰하는 증상들을 열에서 모두 삭제한 후의 데이터프레임을 다시 IntoCNS-finish(1카운트 데이터 움직임).csv에 저장한다.
        intocns_pd3.to_csv(IntoCNS_finish_1count_data_movement, index=False, encoding='utf-8-sig')

        sum = intocns_pd3.sum()  # 모든 각 열의 값을 더한다.
        sum_pd = pd.DataFrame(sum[1:])  # 각 열의 합들을 가져와서 이 각 열들의 합으로 이루어진 sum_pd 데이터 프레임을 만든다.

        sum_pd[0] = pd.to_numeric(sum_pd[0])  # ex) '0', '1' 텍스트 -> 0, 1 정수로 변경 / 텍스트를 사용하면 대소비교가 불가능 하다.



        save.append(sum_pd[0].idxmax()) # surm_pd에서 가장 큰값을 가져온다.
                                        # 여기서 가장 큰 값은 각 열에 존재하는 1들을 모두 합하여 비교하였을 때 가장 큰 값을 가지는 것을 말한다.


        bot = save[0]  # 가장 많이 발생하는 증상을 가져온다.

        bot ="혹시 [" + bot + "] 증상도 있나요"  # ex) "혹시 설사 증상도 있나요"

        return {
                'fulfillmentText': bot
            }

    ##########################################################

if __name__ == "__main__":
    app.secret_key = 'ItIsASecret'
    app.debug = True
    app.run()
