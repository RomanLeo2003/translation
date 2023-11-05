from tatsoft_api import Translate
import pandas as pd
import jsonlines
import tqdm

tatsoft_translator = Translate()  # tatsoft translation

def perform_tatsoft_backtranslation(text, source='rus'):
    '''
    :param text: text to back translate
    :param soucre:
    :return: back translated text
    '''
    if source == 'rus':
        translated_text = tatsoft_translator.rus2tat(text)
        back_translated_text = tatsoft_translator.tat2rus(text)
        return back_translated_text
    elif source == 'tat':
        translated_text = tatsoft_translator.tat2rus(text)
        back_translated_text = tatsoft_translator.rus2tat(text)
        return back_translated_text
    else:
        print('Unavailible option')
        return None


def form_rus2tat_plus_tat2rus(path_to_source_excel, path_to_result_excel):
    source_df = pd.read_excel(path_to_source_excel)
    result_df = pd.DataFrame({'source': source_df['rus'].to_list() + source_df['tat'].to_list(), \
                              'target': source_df['tat'].to_list() + source_df['rus'].to_list()})
    result_df.to_excel(path_to_result_excel)

def form_backtranslated_df(path_to_source_excel, path_to_result_excel):
    source_df = pd.read_excel(path_to_source_excel)
    backtranslated_rus = []
    backtranslated_tat = []
    rus = source_df['rus'].to_list()
    tat = source_df['tat'].to_list()

    for r, t in zip(rus, tat):
        backtranslated_rus.append(perform_tatsoft_backtranslation(r, 'rus'))
        backtranslated_tat.append(perform_tatsoft_backtranslation(t, 'tat'))

    result_df = pd.DataFrame({'rus': rus + backtranslated_rus, 'tat': tat + backtranslated_tat})
    result_df.to_excel(path_to_result_excel)


def form_duplicated_df(path_to_source_excel, path_to_result_excel, duplicate_scale):
    source_df = pd.read_excel(path_to_source_excel)
    rus = source_df['rus'].to_list()
    tat = source_df['tat'].to_list()

    result_df = pd.DataFrame({'rus': rus * duplicate_scale, 'tat': tat * duplicate_scale})
    result_df.to_excel(path_to_result_excel)

def excel2json(excel_path, train_json_file, val_json_file, test_json_file, train_val_test_split):
    df = pd.read_excel(excel_path)
    df.columns = ['rus', 'tat']
    df.dropna()
    train_json_list = []
    val_json_list = []
    test_json_list = []
    for i, row in enumerate(df.iterrows()):
        if i < train_val_test_split[0]:
            train_json_list.append({'translation': {'ru': str(row[1]['rus']), 'tat': str(row[1]['tat'])}})
        elif train_val_test_split[0] <= i < train_val_test_split[1]:
            val_json_list.append({'translation': {'ru': str(row[1]['rus']), 'tat': str(row[1]['tat'])}})
        else:
            test_json_list.append({'translation': {'ru': str(row[1]['rus']), 'tat': str(row[1]['tat'])}})


    with jsonlines.open(train_json_file, 'w') as writer:
        writer.write_all(train_json_list)

    with jsonlines.open(val_json_file, 'w') as writer:
        writer.write_all(val_json_list)

    with jsonlines.open(test_json_file, 'w') as writer:
        writer.write_all(test_json_list)