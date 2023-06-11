import pandas as pd
import numpy as np

class SimpleChatBot:
    def __init__(self, filepath):
        self.questions, self.answers = self.load_data(filepath)


    def load_data(self, filepath):
        data = pd.read_csv(filepath)
        questions = data['Q'].tolist()  # 질문열만 뽑아 파이썬 리스트로 저장
        answers = data['A'].tolist()   # 답변열만 뽑아 파이썬 리스트로 저장
        return questions, answers


    def initiate_table_from_input_and_question(self, input_sent, quest_sent):
        '''
        입력 문장과 질문 리스트 내 문장에 대한 레벤슈타인 거리를 계산하기 전 이에 대한 초기 table을 작성한다.
        테이블은 각  시작값인 공백을 포힘해야 하므로 각 문장의 길이보다 +1만큼 더하여 생성한다.
        또한 서로의 공백에 대한 레벤슈타인 거리는 삽입 비용으로 즉시 계산할 수 있으므로 이를 미리 계산하여 할당한다.

        예시)
        intput_sent = abcd, quest_sent = acd 이면 table을 다음과 같이 출력된다.
        [0][1][2][3]
        [1][0][0][0]
        [2][0][0][0]
        [3][0][0][0]
        [4][0][0][0]
        '''
        table = np.zeros((len(input_sent)+1, len(quest_sent)+1))
        for i in range(len(input_sent)+1):
            table[i][0] = i
        for j in range(len(quest_sent)+1):
            table[0][j] = j
        return table

    
    def calculate_reven_distance(self, df):
        '''
        apply method용 함수로서 레벤슈타인 거리를 계산하고 이를 반환한다.
        입력으로 입력 문장과 질문 문장이 포함된 df의 한 행을 받으며,
        여기서 입력 문장과 질문 문장을 가지고 initiate_table_From_input_and_question method를 이용하여
        최초 테이블을 작성한 후 이로부터 입력 문장과 질문 문장을 각각 interate하면서 레벤슈타인 거리를 계산해서
        table의 각 요소에 할당한다.
        레벤슈타인 거리를 계산하는 알고리즘은 다음과 같다
         1. 만약 입력 문장에서 추출한 문자와 질문 문장에서 추출한 문자가 같다면 대각선 값을 가져온다
         2. 만약 문자가 다르다면 변형 비용과 삭제 비용, 삽입 비용을 계산하고 그 중 최소값을 가져온다.
         모든 interation이 종료되면 table의 우측최하단 값을 final cost로 지정하고, 반환한다.
        '''
        #print(df)
        input_sent = df['input_sent']
        quest_sent = df['question']
        table = self.initiate_table_from_input_and_question(input_sent, quest_sent)
        for i in range(len(input_sent)):
            for j in range(len(quest_sent)):
                #print(f'{i},{j}')
                if input_sent[i] == quest_sent[j]:
                    cost = table[i][j]
                else:
                    transform_cost = table[i][j] + 1
                    delete_cost = table[i+1][j] + 1
                    insert_cost = table[i][j+1] + 1
                    cost = min(transform_cost, delete_cost, insert_cost)
                    
                table[i+1][j+1] = cost
        final_cost = table[-1][-1]
        return final_cost


    def find_best_answer(self, input_sentence):
        '''
        ChatbostData.csv로부터 질문리스트와 대답리스트를 읽어와서 이를 setence_set이라는 dataframe을 생성한다.
        여기에 입력 문장을 input_sent 컬럼에 일괄로 적용한다.
        apply함수를 통해 calculate_reven_distance를 각 행별로 적용하여, 이로부터 계산된 레벤슈타인 거리를 
        reven_distance 컬럼에 할당한다.
        argmin을 통해 비용이 가장 낮은 헹의 index를 가져와서 answer 컬럼에서 best_answer를 추출하고 이를 반환한다.
        '''
        sentence_set = pd.DataFrame(data=[set for set in zip(self.questions, self.answers)], columns=['question','answer'])
        sentence_set['input_sent'] = input_sentence
        sentence_set['reven_distance'] = sentence_set.apply(self.calculate_reven_distance, axis=1)
        best_answer_idx = sentence_set['reven_distance'].argmin()
        best_answer = sentence_set['answer'][best_answer_idx]
        return best_answer

# CSV 파일 경로를 지정하세요.
filepath = 'ChatbotData.csv'

# 간단한 챗봇 인스턴스를 생성합니다.
chatbot = SimpleChatBot(filepath)

# '종료'라는 단어가 입력될 때까지 챗봇과의 대화를 반복합니다.
while True:
    input_sentence = input('You: ')
    if input_sentence.lower() == '종료':
        break
    response = chatbot.find_best_answer(input_sentence)
    print('Chatbot:', response)
    
