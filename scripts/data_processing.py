from tatsoft_api import Translate
import pandas as pd

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


