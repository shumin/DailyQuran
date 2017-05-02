import io
import json
import os


class QuranBanglaGenerator:
    def __init__(self):
        self.aya_mapping_file = os.path.join(os.path.dirname(__file__), 'data/aya-365day-map.json')
        self.bangla_quran_file = os.path.join(os.path.dirname(__file__), 'data/bangla-taisirul-quran.json')
        self.english_quran_file = os.path.join(os.path.dirname(__file__), 'data/english-sahih-international.json')
        self.sura_name_file = os.path.join(os.path.dirname(__file__), 'data/sura_name_map.json')
        self.output_file = os.path.join(os.path.dirname(__file__), 'data/output/result.json')

        self.aya_mapping_json = None
        self.bangla_quran_json = None
        self.english_quran_json = None
        self.sura_name_json = None

    def process(self):

        with open(self.aya_mapping_file) as aya_mapping_file:
            self.aya_mapping_json = json.load(aya_mapping_file)

        with open(self.bangla_quran_file) as bangla_quran_file:
            self.bangla_quran_json = json.load(bangla_quran_file)

        with open(self.english_quran_file) as english_quran_file:
            self.english_quran_json = json.load(english_quran_file)

        with open(self.sura_name_file) as sura_name_file:
            self.sura_name_json = json.load(sura_name_file)

        final_data = {}
        data = []
        for day in self.aya_mapping_json['daily-quran']:
            data_for_day = {}
            index = day['sura'] - 1
            aya_str = str(day['aya'])  # somehow single aya comes as int rather than str

            data_for_day['day'] = day['day']
            data_for_day['sura'] = day['sura']
            data_for_day['sura_name_en'] = self.sura_name_json[index]['sura_en']
            data_for_day['sura_name_bn'] = self.sura_name_json[index]['sura_bn']
            data_for_day['aya'] = aya_str

            bn_sura = self.bangla_quran_json['quran']['sura'][index]
            en_sura = self.english_quran_json['quran']['sura'][index]

            data_for_day['sura_name_ar'] = bn_sura['@name']
            data_for_day['translation_bn'] = self.get_translation_from(bn_sura, aya_str)
            data_for_day['translation_en'] = self.get_translation_from(en_sura, aya_str)

            data.append(data_for_day)
            print('Processed day: ' + str(day['day']))

        final_data['days'] = data
        final_data['translation_ref_bn'] = '<a href="https://github.com/SadaqaWorks/IslamicDatabase">Taisirul Quran</a>'
        final_data['translation_ref_en'] = '<a href="http://tanzil.net/#trans/en.sahih/1:1">Saheeh International</a>'

        self.write_to_file(final_data, self.output_file)
        self.generate_html(final_data)
        print('Completed data generation.')

    def get_translation_from(self, sura, aya):
        aya_list = aya.split(',')
        all_aya = ''

        for aya_num in aya_list:
            aya_index = int(aya_num) - 1
            all_aya += sura['aya'][aya_index]['@text'] + '\n'

        return all_aya

    def generate_html(self, final_data):
        print('Generating html files...')

        html_template = '<!DOCTYPE html> <html><head><meta charset="utf-8"></head> <body style="margin:30px auto; max-width: 90%"> {{body}} </body> </html>'
        index_html = ''

        for day in final_data['days']:
            day_str = str(day['day'])
            aya_str = str(day['aya'])
            index_html += ('<tr> <td><a href=%s>%s</a></td> </tr>' % (day_str + '.html', 'day ' + day_str))

            day_data = '<div><a href="index.html">index</a> </div>' \
                       + ('<h2>Day %s</h2>' % day_str)\
                       + '<div>' \
                       + day['translation_bn'] \
                       + '<div>' + day['sura_name_bn'] + ': ' + aya_str + '</div>' \
                       + '</div>' \
                       + '<div> <br/>' \
                       + day['translation_en'] \
                       + '<div>' + day['sura_name_en'] + ': ' + aya_str + '</div>' \
                       + '</div> <br/> <br/>' \
                       + '<h5>Translation reference:</h5>' \
                       + ('<span style="font-size:10pt">%s</span><br/>' % final_data['translation_ref_bn']) \
                       + ('<span style="font-size:10pt">%s</span><br/>' % final_data['translation_ref_en'])
            day_html = html_template.replace('{{body}}', day_data)
            day_file_name = os.path.join(os.path.dirname(__file__), ('data/output/%s.html' % day_str))
            self.write_to_file(day_html, day_file_name)
            print('Generated html for day %s' % day_str)

        index_html = '<table>' + index_html + '</table>'
        data = html_template.replace('{{body}}', index_html)
        file_name = os.path.join(os.path.dirname(__file__), 'data/output/index.html')
        self.write_to_file(data, file_name)

    def write_to_file(self, data, file_name):
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        with io.open(file_name, 'w', encoding='utf-8') as f:
            if type(data) is not str:
                data = json.dumps(data, ensure_ascii=False)
            f.write(data)

