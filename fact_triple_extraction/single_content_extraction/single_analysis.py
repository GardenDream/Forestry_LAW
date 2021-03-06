#!/usr/bin/env python
# coding=utf-8
from fact_triple_extraction.xf_ltp_api import *
from data_resource import pool
from fact_triple_extraction.single_content_extraction.get_single_content import *
import threading


# 改名
def xunfei_single_analysis_and_save(contents, dp_tags, sdp_tags, lock):
    # dp_tags, sdp_tags = get_tags()
    for content_tuple in contents:
        law_id = content_tuple[0]
        article_class = content_tuple[1]
        chapter_id = content_tuple[2]
        sentence_id = content_tuple[3]
        content_list = content_tuple[4]
        is_complex = content_tuple[5]
        for content in content_list:
            if '：' not in content and len(content) < 100:
                words_list = time_control_method(word_segment, content, 'word')  # 分词结果
                postags_list = time_control_method(word_postag, content, 'pos')  # 词性标注结果
                dp_info = time_control_method(dependency_parse, content, 'dp')  # 依存句法分析
                # # [{'beg': 0, 'end': 1, 'id': 3, 'type': 'A0'}, {'beg': 4, 'end': 5, 'id': 3, 'type': 'A1'}]
                srl_info = time_control_method(semantic_role_labeller, content, 'srl')  # 语义角色标注分析
                # sdgp_info = time_control_method(semantic_dependency_parse, content, 'sdgp')  # 语义依存分析
                if words_list is None or postags_list is None or dp_info is None or srl_info is None:
                    continue

                dp_result_list = []
                for index in range(len(dp_info)):
                    parent_index = dp_info[index]['parent']
                    if parent_index == -1:
                        parent_word = 'Root'
                    else:
                        parent_word = words_list[parent_index]
                    child_index = index
                    child_word = words_list[child_index]
                    if dp_info[index]['relate'] in dp_tags:
                        reletion_name = dp_tags[dp_info[index]['relate']] + '-' + dp_info[index]['relate']
                    else:
                        reletion_name = dp_info[index]['relate'] + '-' + dp_info[index]['relate']
                    # TODO: 存入对应数据库操作
                    dp_result = [law_id,  # 0-法律id
                                 article_class,  # 1-文章类型（1或2）
                                 chapter_id,  # 章id
                                 sentence_id,  # sentence_id
                                 "".join(content_list),  # 完整句子
                                 content,  # 分析子句
                                 parent_word,  # 头词
                                 reletion_name,  # 关系
                                 child_word,  # 尾词
                                 is_complex]  # 是否是复杂句
                    dp_result_list.append(dp_result)
                    # save_to_dependency_parsing_result(dp_result)
                    # print("%s -----(%s)---- %s" % (parent_word, reletion_name, child_word))

                # sdp_result_list = []
                # for sdp_index in range(len(sdgp_info)):
                #     sdp_parent_index = sdgp_info[sdp_index]['parent']
                #     if sdp_parent_index == -1:
                #         sdp_parent_word = 'Root'
                #     else:
                #         sdp_parent_word = words_list[sdp_parent_index]
                #     sdp_child_index = sdgp_info[sdp_index]['id']
                #     sdp_child_word = words_list[sdp_child_index]
                #     if sdgp_info[sdp_index]['relate'] in sdp_tags:
                #         semantic_dp_name = sdp_tags[sdgp_info[sdp_index]['relate']] + '-' + sdgp_info[index]['relate']
                #     elif str(sdgp_info[sdp_index]['relate']).startswith('r') \
                #             and str(sdgp_info[sdp_index]['relate'])[1:] in sdp_tags:
                #         main_relate = '' + str(sdgp_info[sdp_index]['relate'])[1:]
                #         semantic_dp_name = sdp_tags[main_relate] + '--反角色' + '-' + sdgp_info[index]['relate']
                #     elif str(sdgp_info[sdp_index]['relate']).startswith('d') \
                #             and str(sdgp_info[sdp_index]['relate'])[1:] in sdp_tags:
                #         main_relate = '' + str(sdgp_info[sdp_index]['relate'])[1:]
                #         semantic_dp_name = sdp_tags[main_relate] + '--嵌套角色' + '-' + sdgp_info[index]['relate']
                #     else:
                #         semantic_dp_name = sdgp_info[sdp_index]['relate'] + '-' + sdgp_info[index]['relate']
                #     # TODO: 将语义依存分析结果存入数据库
                #     sdp_result = [law_id,
                #                   article_class,
                #                   chapter_id,
                #                   sentence_id,
                #                   "".join(content_list),
                #                   content,
                #                   sdp_parent_word,
                #                   semantic_dp_name,
                #                   sdp_child_word,
                #                   is_complex]  # 是否是复杂句
                #     sdp_result_list.append(sdp_result)
                    # save_to_semantic_dependency_result(sdp_result)
                    # print("%s(%s)-----%s-----%s(%s)" % (
                    #     sdp_parent_word, postags_list[sdp_parent_index], semantic_dp_name, sdp_child_word,
                    #     postags_list[sdp_child_index]))

                print('-------------------------语义角色标注结果打印----------------------------')
                role_lable_dict = dict()
                for role_label in srl_info:
                    verb = words_list[role_label['id']]
                    begin = role_label['beg']
                    end = role_label['end']
                    if verb in role_lable_dict:
                        role_lable_dict[verb].append(
                            tuple((role_label['type'], "".join(words_list[begin: end + 1]))))
                    else:
                        role_lable_dict.update({verb: []})
                        role_lable_dict[verb].append(
                            tuple((role_label['type'], "".join(words_list[begin: end + 1]))))
                # print(role_lable_dict)
                # TODO: 将语义角色标注信息存入数据库
                role_label_result = [law_id,
                                     article_class,
                                     chapter_id,
                                     sentence_id,
                                     "".join(content_list),
                                     content,
                                     role_lable_dict,
                                     is_complex]  # 是否是复杂句
                # save_to_semantic_role_label_result(role_label_result)
                print('=========================================================================================')
                lock.acquire()
                save_to_dependency_parsing_result(dp_result_list)
                # save_to_semantic_dependency_result(sdp_result_list)
                save_to_semantic_role_label_result(role_label_result)
                lock.release()


def save_to_dependency_parsing_result(result):
    insert_sql = '''insert into dependency_parsing_result (law_id, class, chapter_id, sentence_id, complete_sentence, 
                    parse_sentence, front_word, dependency_parsing_relation, tail_word, is_complex) 
                    value (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
    pool_conn = pool.connection()
    cursor = pool_conn.cursor()
    for res in result:
        law_id = res[0]
        article_class = res[1]
        chapter_id = res[2]
        sentence_id = res[3]
        complete_sentence = res[4]
        parse_sentence = res[5]
        front_word = res[6]
        dependency_parsing_relation = res[7]
        tail_word = res[8]
        is_complex = res[9]
        try:
            cursor.execute(insert_sql, (law_id, article_class, chapter_id, sentence_id, complete_sentence,
                                        parse_sentence, front_word, dependency_parsing_relation, tail_word, is_complex))
            conn.commit()
            print(sentence_id, parse_sentence, '----DEPENDENCY PARSING SUCCESS----')
        except Exception as e:
            conn.rollback()
            print('\033[1;32;41m' + sentence_id + ': ' + parse_sentence + 'DP FAILED' + e + '\033[0m')


def save_to_semantic_dependency_result(result):
    insert_sql = '''insert into semantic_dependency_result (law_id, class, chapter_id, sentence_id, complete_sentence, 
                    parse_sentence, front_word, semantic_dependency_relation, tail_word, is_complex) 
                    value (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
    pool_conn = pool.connection()
    cursor = pool_conn.cursor()
    for res in result:
        law_id = res[0]
        article_class = res[1]
        chapter_id = res[2]
        sentence_id = res[3]
        complete_sentence = res[4]
        parse_sentence = res[5]
        front_word = res[6]
        semantic_dependency_relation = res[7]
        tail_word = res[8]
        is_complex = res[9]
        try:
            cursor.execute(insert_sql, (law_id, article_class, chapter_id, sentence_id, complete_sentence,
                                        parse_sentence, front_word, semantic_dependency_relation, tail_word, is_complex))
            conn.commit()
            print(sentence_id, parse_sentence, '----SEMANTIC DEPENDENCY PARSING SUCCESS----')
        except Exception as e:
            conn.rollback()
            print('\033[1;32;41m' + sentence_id + ': ' + parse_sentence + 'SDP FAILED' + e + '\033[0m')
        pass


def save_to_semantic_role_label_result(result):
    insert_sql = '''insert into semantic_role_label_result (law_id, class, chapter_id, sentence_id, 
                    complete_sentence, parse_sentence, verb, role_label, content, is_complex) 
                    value (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
    pool_conn = pool.connection()
    cursor = pool_conn.cursor()
    law_id = result[0]
    article_class = result[1]
    chapter_id = result[2]
    sentence_id = result[3]
    complete_sentence = result[4]
    parse_sentence = result[5]
    role_label_dict = result[6]
    is_complex = result[7]
    for verb in role_label_dict:
        for role_info in role_label_dict[verb]:
            role = role_info[0]
            content = role_info[1]
            try:
                cursor.execute(insert_sql, (law_id, article_class, chapter_id, sentence_id, complete_sentence, parse_sentence, verb, role, content, is_complex))
                conn.commit()
                print(sentence_id, parse_sentence, '----SEMANTIC ROLE LABELLING SUCCESS----')
            except Exception as e:
                conn.rollback()
                print('\033[1;32;41m' + sentence_id + ': ' + parse_sentence + 'SRL FAILED' + e + '\033[0m')


# 将抽取任务的不同组开启不同的线程
def start_multiple_thread_to_analysis(func_name, thread_num, contents_group, dp_tags, sdp_tags, lock):
    thread_pool = []
    for index in range(thread_num):
        thread_pool.append(threading.Thread(target=func_name, args=(contents_group[index], dp_tags, sdp_tags, lock)))
    for i in range(len(thread_pool)):
        thread_pool[i].start()


if __name__ == '__main__':
    thread_num = 4
    dp_tags, sdp_tags = get_tags()
    sql_control_lock = threading.Lock()
    # article_1_single_contents = get_article_1_single_content()
    article_2_single_contents = get_article_2_single_content(30000, 35000)
    contents_group = single_content_group(article_2_single_contents, thread_num)
    start_multiple_thread_to_analysis(xunfei_single_analysis_and_save,
                                      thread_num,
                                      contents_group,
                                      dp_tags,
                                      sdp_tags,
                                      sql_control_lock)