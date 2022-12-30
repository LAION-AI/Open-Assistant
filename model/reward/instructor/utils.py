import re

re_reference_remove = re.compile(r'\[([0-9])+\]|\[([0-9])+,([0-9])+\]')

def webgpt_return_format(row):
    if row['score_0'] >= row['score_1']:
        # remove this to prevent information leak, since we are not using reference
        return {
                'question': row['question']['full_text'],
                     'pos': re_reference_remove.sub('', row['answer_0']),
                     'neg': re_reference_remove.sub('', row['answer_1'])
                }

    return {
            'question': row['question']['full_text'],
                 'pos': re_reference_remove.sub('', row['answer_1']),
                 'neg': re_reference_remove.sub('', row['answer_0'])
            }
