#関数：ツイート履歴を形態素に分解する
import MeCab

#分かち書き、品詞分類、原型の抽出
def mecab_list(text):
    tagger = MeCab.Tagger("-Ochasen")
    tagger.parse('')
    node = tagger.parseToNode(text)
    mecab_output = []
    while node:
        word = node.surface
        wclass = node.feature.split(',')
        if wclass[0] != u'BOS/EOS':
            if wclass[6] == None:
                mecab_output.append([word,wclass[0],wclass[1],wclass[2],""])
            else:
                mecab_output.append([word,wclass[0],wclass[1],wclass[2],wclass[6]])
        node = node.next
    return mecab_output



#フォルダ内のファイルの一覧を取得（うつ群）
import glob

dep_file_names=[]

dep_files = glob.glob("./うつ群のタイムラインを格納したフォルダ/*")
for file in dep_files:
    dep_file_names.append(file)
    
    
ctrl_file_names=[]

ctrl_files = glob.glob("./非うつ群のタイムラインを格納したフォルダ/*")
for file in ctrl_files:
    ctrl_file_names.append(file)
    
print(len(dep_file_names))#940
print(len(ctrl_file_names))#947




#testデータをランダムに800ずつ選ぶ
import random

dep_training_set=random.sample(dep_file_names, 800)
dep_test_set=[i for i in dep_file_names if i not in dep_training_set]

ctrl_training_set=random.sample(ctrl_file_names, 800)
ctrl_test_set=[i for i in ctrl_file_names if i not in ctrl_training_set]
ctrl_test_set=ctrl_test_set[:140]


import copy
def timeline2stemDict(timeline):
    timeline_d={}
    for twt in timeline:
        twtML=copy.deepcopy(mecab_list(twt))
        for i in range(len(twtML)):
            if twtML[i][4] in timeline_d:
                timeline_d[twtML[i][4]][1]+=1
            elif twtML[i][4] not in timeline_d:
                timeline_d[twtML[i][4]]=[twtML[i][1],1]
    return timeline_d
    
    
    
def total_word_count(timelines1):
    global total_word_dict
    total_word_dict={}
    total_word_count_l=[]
    
    for TL in timelines1:
        TL2SL=timeline2stemDict(TL)
        total_word_count_l.append(TL2SL)
        for word in TL2SL:
            if word not in total_word_dict:
                total_word_dict[word]=[TL2SL[word][0],0]
    
    total_word_dict_list=[]
    for i in range(len(total_word_count_l)):
        total_word_dict_list.append(copy.deepcopy(total_word_dict))
    
    for i in range(len(total_word_count_l)):
        total_word_dict_list[i].update(total_word_count_l[i])

    return total_word_dict_list
    
    
    
def tf(TOTAL_WORD_COUNT_LIST1):
    tfs=[]
    for WORD_COUNT1 in TOTAL_WORD_COUNT_LIST1:
        sigma=sum([i[1] for i in WORD_COUNT1.values()])
        if sigma!=0:
            tfs_dict={}
            for WORD1 in WORD_COUNT1:
                tfs_dict[WORD1]=[WORD_COUNT1[WORD1][0],WORD_COUNT1[WORD1][1]/sigma]
            tfs.append(tfs_dict)
    return tfs





import math
def idf(TOTAL_WORD_COUNT_LIST2):
    idf_dict=copy.deepcopy(total_word_dict)
    n=len(TOTAL_WORD_COUNT_LIST2)
    for WORD_COUNT2 in TOTAL_WORD_COUNT_LIST2:
        for WORD2 in WORD_COUNT2:
            if WORD_COUNT2[WORD2][1]!=0:
                idf_dict[WORD2][1]+=1
    
    idf={}
    for _idf_dict in idf_dict:
        idf[_idf_dict]=[idf_dict[_idf_dict][0], math.log(n/idf_dict[_idf_dict][1])+1]

    return idf
    



#各語のtf*idfを計算
def tfidf(tf_list,idf_dict):
    tfidf_list=[]
    for _tf_list in tf_list:
        tfidf_dict={}
        for _idf_dict in idf_dict:
            tfidf_dict[_idf_dict]=[idf_dict[_idf_dict][0], idf_dict[_idf_dict][1]*_tf_list[_idf_dict][1]]
        tfidf_list.append(tfidf_dict)
    return tfidf_list
    
    
    
    
#複数のtxtファイルからタイムラインのリストを作成する関数
def timelines(file_list):
    timelines=[]
    for file in file_list:
        text=open(file).read()
        open(file).close()

        timelines.append([text])
    return timelines
    
    
def get_tfidf(file_list):
    the_timelines=timelines(file_list)#入力のtxtファイル名から全てのタイムラインのリストを作成する,
    #the_timelines=[[],[],[]]
    print(len(the_timelines))
    
    the_total_word_count=total_word_count(the_timelines)
    #the_total_word_count=[{:[],:[],:[]},..,{:[],:[],:[]}]
    print(len(the_total_word_count))
    
    the_tf=tf(the_total_word_count)
    #the_tf=[{:[],:[],:[]},..,{:[],:[],:[]}]
    print(len(the_tf))
    
    the_idf=idf(the_total_word_count)
    #the_idf={:[],:[],:[]}
    print(len(the_idf))
    
    the_tfidf=tfidf(the_tf,the_idf)
    return the_tfidf
    


both_tfidf=get_tfidf(ctrl_training_set+dep_training_set)



ctrl_counter={}
for the_tfidf_dict in both_tfidf[:len(ctrl_training_set)]:
    for word1 in the_tfidf_dict:
        if word1 not in ctrl_counter:
            ctrl_counter[word1]=[the_tfidf_dict[word1][0],the_tfidf_dict[word1][1]]
        else:
            ctrl_counter[word1][1]+=the_tfidf_dict[word1][1]

#ctrl群のw            
for _ctrl_counter in ctrl_counter:
    ctrl_counter[_ctrl_counter][1]/=len(ctrl_training_set)
ctrl_sigma_w=ctrl_counter



#全ての語の値を0に初期化
init_terms_0=copy.deepcopy(ctrl_counter)
for _init_terms_0 in init_terms_0:
    init_terms_0[_init_terms_0][1]=0



#うつ群の各語の重み
dep_init_terms_0=copy.deepcopy(init_terms_0)
for dep_the_tfidf_dict in both_tfidf[len(ctrl_training_set):]:
    for _dep_the_tfidf_dict in dep_the_tfidf_dict:
        dep_init_terms_0[_dep_the_tfidf_dict][1]+=dep_the_tfidf_dict[_dep_the_tfidf_dict][1]
dep_sigma_w=dep_init_terms_0



for _dep_sigma_w in dep_sigma_w:
    n_d=_dep_sigma_w
    dep_sigma_w[n_d][1]/=len(dep_training_set)



dj={}
for _dep_sigma_w in dep_sigma_w:
    the_term=_dep_sigma_w 
    dj[the_term]=[dep_sigma_w[the_term][0],dep_sigma_w[the_term][1]-ctrl_sigma_w[the_term][1]]
    
    
    
    
dj=sorted(dj.items(), reverse=True, key=lambda x: x[1][1])




#三品詞を格納するリストの名前をverbs_djにしてしまう。
verbs_dj=[]
for _i in range(len(dj)):
    if dj[_i][1][0]=='動詞' or '形容詞' or '副詞':
        verbs_dj.append(dj[_i])

verbs_dj=verbs_dj[:500]+verbs_dj[-500:]
print(len(verbs_dj))





#1000語のtfidfを格納したリストの作成（＝training dataの作成）
#1行目のラベルの作成
word_columns=[]
word_columns.append('num')
for _verbs_dj in verbs_dj:
    word_columns.append(_verbs_dj[0])
word_columns.append('group')

#要素を0に初期化した辞書の作成
training_verbs=word_columns[1:-1]
training_verbs_row_0={}
for _training_verbs in training_verbs:
    training_verbs_row_0[_training_verbs]=0

#要素（数字）の整列
training_3category_1000=[]

#ctrl分修正
for _i in range(len(both_tfidf[:len(ctrl_training_set)])):
    training_3category_1000_ctrl=copy.deepcopy(training_verbs_row_0)
    training_3category_1000_list=[_i]
    for __both_tfidf in both_tfidf[_i]:
        if __both_tfidf in training_3category_1000_ctrl:
            training_3category_1000_ctrl[__both_tfidf]=both_tfidf[_i][__both_tfidf][1]
    training_3category_1000_list+=list(training_3category_1000_ctrl.values())
    training_3category_1000_list.append('crtl')
    training_3category_1000.append(training_3category_1000_list)

    
#dep分修正
for _i in range(len(ctrl_training_set),len(ctrl_training_set)+len(dep_training_set)):
    training_3category_1000_dep=copy.deepcopy(training_verbs_row_0)
    training_3category_1000_list=[_i]
    for __both_tfidf in both_tfidf[_i]:
        if __both_tfidf in training_3category_1000_dep:
            training_3category_1000_dep[__both_tfidf]=both_tfidf[_i][__both_tfidf][1]
    training_3category_1000_list+=list(training_3category_1000_dep.values())
    training_3category_1000_list.append('dep')
    training_3category_1000.append(training_3category_1000_list)
    
    
    
    

print(len(word_columns))#1002
print(len(training_3category_1000[0]))#1002




verb_df=pd.DataFrame(training_3category_1000, columns=word_columns)
verb_df.to_csv('20200108three950training.csv', index=False ,encoding='utf-8')
#ここまででtrainデータの完成



#testデータの作成
test_both_tfidf=get_tfidf(ctrl_test_set+dep_test_set)


#リストtraining_verbs作成

training_verbs_row={}
for _training_verbs in training_verbs:
    training_verbs_row[_training_verbs]=0
#print(training_verbs_row)

verb_dicts_list=[]

for _test_both_tfidf in test_both_tfidf:
    verb_dict=copy.deepcopy(training_verbs_row)
    for verb in _test_both_tfidf:
        if verb in verb_dict:
            verb_dict[verb]=list(_test_both_tfidf[verb])
    verb_dicts_list.append(verb_dict)
    
    


#素性ベクトルcsvの作成（動詞・形容詞・副詞、test）
test_data_contents=[]

for __i in range(len(ctrl_test_set)):
    test_data_content_row_ctrl=[]
    test_data_content_row_ctrl.append(__i)
    the_verb_dict1=copy.deepcopy(verb_dicts_list[__i])
    for __word in the_verb_dict1:
        if the_verb_dict1[__word]!=0:
            test_data_content_row_ctrl.append(the_verb_dict1[__word][1])#[1]
        else:
            test_data_content_row_ctrl.append(0.0)
    test_data_content_row_ctrl.append('ctrl')
    test_data_contents.append(test_data_content_row_ctrl)
    
print(len(test_data_contents))
    
for __i in range(len(ctrl_test_set),len(ctrl_test_set)+len(dep_test_set)):
    test_data_content_row_dep=[]
    test_data_content_row_dep.append(__i)
    the_verb_dict2=copy.deepcopy(verb_dicts_list[__i])
    for __word in the_verb_dict2:
        if the_verb_dict2[__word]!=0:
            test_data_content_row_dep.append(the_verb_dict2[__word][1])#[1]
        else:
            test_data_content_row_dep.append(0.0)
    test_data_content_row_dep.append('dep')
    test_data_contents.append(test_data_content_row_dep)





test_verb_df=pd.DataFrame(test_data_contents, columns=word_columns)
test_verb_df.to_csv('20200108three950test.csv', index=False ,encoding='utf-8')
#ここまででtestデータが完成




#動詞上位30語、下位30語の可視化
verb_dj=[]

for _i in range(len(verbs_dj)):
    if verbs_dj[_i][1][0]=='動詞':
        verb_dj.append(verbs_dj[_i])
print(' '.join([i[0] for i in verb_dj[:30]]))
print()
print(' '.join(reversed([i[0] for i in verb_dj[-30:]])))




#形容詞上位30語、下位30語
ad_dj=[]

for _i in range(len(dj)):
    if dj[_i][1][0]=='形容詞':
        ad_dj.append(dj[_i])
print(' '.join([i[0] for i in ad_dj[:30]]))
print()
print(' '.join(reversed([i[0] for i in ad_dj[-30:]])))





#副詞上位30語、下位30語
adverb_dj=[]

for _i in range(len(dj)):
    if dj[_i][1][0]=='副詞':
        adverb_dj.append(dj[_i])
print(' '.join([i[0] for i in adverb_dj[:30]]))
print()
print(' '.join(reversed([i[0] for i in adverb_dj[-30:]])))
