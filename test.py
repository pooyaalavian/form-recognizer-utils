import dotenv
dotenv.load_dotenv()
import logging
from pathlib import Path
from src import process_document, clean_key_vals, translate_keys_to_preset_terms
from src.table.simple_table import SimpleTable

logging.basicConfig(
    #  filename='log_file_name.log',
    level=logging.INFO,
    format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)


def main(file: str):
    doc = process_document(file)
    tbls = [SimpleTable(t) for t in doc.tables]
    kvs = clean_key_vals(doc)
    numeric_kvs = [kv for kv in kvs if kv.is_numeric]
    for kv in numeric_kvs:
        print(kv)
    matched_kvs = translate_keys_to_preset_terms([x.key for x in numeric_kvs])
    print('\n\n',matched_kvs,'\n\n')
    for standard_key, form_key in matched_kvs.items():
        if form_key is None:
            print(f'- No match found for {standard_key}. Skipping...' )
            continue
        value = [x for x in numeric_kvs if x.key==form_key]
        if len(value)==0:
            raise Exception(f'No value found for {standard_key}/{form_key}. OpenAI made a mistake...')
        print(standard_key, value[0])
    print('a')


if __name__ == '__main__':
    # update with address of your input file.
    f='data.private/input/....pdf'
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', type=str, help='path to file', default=f)
    args = parser.parse_args()
    # main(Path(args.file).resolve())
    main(args.file)
