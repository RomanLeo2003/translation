from tatsoft_api import Translate
import pandas as pd
import jsonlines
import tqdm
from translatepy.translators.yandex import YandexTranslate

yandex = YandexTranslate()

tatsoft_translator = Translate()  # tatsoft translation

def perform_tatsoft_backtranslation(text, source='rus'):
    '''
    :param text: text to back translate
    :param soucre:
    :return: back translated text
    '''
    if source == 'rus':
        translated_text = tatsoft_translator.rus2tat(text)
        back_translated_text = tatsoft_translator.tat2rus(translated_text)
        return back_translated_text
    elif source == 'tat':
        translated_text = tatsoft_translator.tat2rus(text)
        back_translated_text = tatsoft_translator.rus2tat(translated_text)
        return back_translated_text
    else:
        print('Unavailible option')
        return None

def perform_yandex_backtranslation(text, target='Russian'):
    if target == 'Russian':
        translated_text = yandex.translate(text, target)
        backtranslated_text = yandex.translate(translated_text.result, 'Tatar')
    else:
        translated_text = yandex.translate(text, target)
        backtranslated_text = yandex.translate(translated_text.result, 'Russian')
    return backtranslated_text.result


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

    for r, t in tqdm.tqdm(zip(rus, tat)):
        backtranslated_rus.append(perform_yandex_backtranslation(r, 'Tatar'))
        backtranslated_tat.append(perform_yandex_backtranslation(t, 'Russian'))

    result_df = pd.DataFrame({'rus': rus + backtranslated_rus, 'tat': tat + backtranslated_tat})
    result_df.to_excel(path_to_result_excel)


def form_duplicated_df(path_to_source_excel, path_to_result_excel, duplicate_scale):
    source_df = pd.read_excel(path_to_source_excel)
    rus = source_df['rus'].to_list()
    tat = source_df['tat'].to_list()

    result_df = pd.DataFrame({'rus': rus * duplicate_scale, 'tat': tat * duplicate_scale})
    result_df.to_excel(path_to_result_excel)

def excel2json(excel_path, train_json_file, val_json_file, test_json_file, train_val_test_split):
    df = pd.read_excel(excel_path).sample(frac=1)
    df.columns = ['rus', 'tat']
    df.dropna()
    train_json_list = []
    val_json_list = []
    test_json_list = []
    for i, row in tqdm.tqdm(enumerate(df.iterrows())):
        if i < len(df) * train_val_test_split[0]:
            train_json_list.append({'translation': {'ru': str(row[1]['rus']), 'tat': str(row[1]['tat'])}})
        elif train_val_test_split[0] * len(df) <= i < train_val_test_split[1] * len(df):
            val_json_list.append({'translation': {'ru': str(row[1]['rus']), 'tat': str(row[1]['tat'])}})
        else:
            test_json_list.append({'translation': {'ru': str(row[1]['rus']), 'tat': str(row[1]['tat'])}})


    with jsonlines.open(train_json_file, 'w') as writer:
        writer.write_all(train_json_list)

    with jsonlines.open(val_json_file, 'w') as writer:
        writer.write_all(val_json_list)

    with jsonlines.open(test_json_file, 'w') as writer:
        writer.write_all(test_json_list)


form_backtranslated_df(r"C:\Users\user\Downloads\Telegram Desktop\RU-TT_2018_50000.xlsx", 'backtranslated.xlsx')
form_duplicated_df('backtranslated.xlsx', 'duplicated.xlsx', 2)
form_rus2tat_plus_tat2rus('duplicated.xlsx', 'result.xlsx')

excel2json('result.xlsx', 'train.json', 'val.json', 'test.json', (0.8, 0.9))



from optimum.onnxruntime import ORTModelForSeq2SeqLM
from transformers import AutoTokenizer

ort_model = ORTModelForSeq2SeqLM.from_pretrained(
    "nllb-model-name",
    export=True,
    provider="TensorrtExecutionProvider",
)

tokenizer = AutoTokenizer.from_pretrained("nllb-model-name")
inp = tokenizer("expectations were low, actual enjoyment was high", return_tensors="pt", padding=True)

result = ort_model(**inp)
assert ort_model.providers == ["TensorrtExecutionProvider", "CUDAExecutionProvider", "CPUExecutionProvider"]