import json
diacritics = {
    'č': 'c', 
    'ć': 'c', 
    'đ': 'd', 
    'š': 's', 
    'ž': 'z'
}

kwrds = [
    'alemka', 'antigensk', 'antimaskeri', 'antivakseri', 'astra zeneca', 'astrazeneca', 'berosmarkoti',
    'beroš', 'viliberos', 'biontech', 'bolnic', 'booster doza', 'brazilski', 'britanski', 'capak', 'cijep', 
    'cijepljen', 'cjep', 'cjepiv', 'cjepljen', 'coron', 'corona', 'covid', 'covid-19', 'delta', 
    'dezinf', 'dijagnost', 'distanc', 'doktor', 'druga doza', 'epide', 'epidemij', 'festivala slobode', 
    'hzjz', 'indijski', 'infekc', 'inkubacij', 'izolac', 'južnoafrički', 'karant', 'koron', 'korona', 
    'kovid', 'lambda', 'ljekov', 'lockd', 'lockdown', 'mask', 'medicin', 'moderna', 'mutirani', 'n95', 
    'ncov', 'njujorški', 'novi soj', 'novozaražen', 'nuspoj', 'obolje', 'omikorn', 'ostanidoma', 
    'ostanimodoma', 'ostanimoodgovorni', 'pandem', 'pandemij', 'patoge', 'pfizer', 'stozer', 'stožer',
    'propusnic', 'prva doza', 'respir', 'samoizola', 'samoizolacij', 'stožer civilne zaštite', 'terapij',
    'sars-cov-2', 'sarscov2', 'simpto', 'slusajstruku', 'slušajstruku', 'sojevi koronavirusa', 'sputnik',
    'testira', 'treća doza', 'treca doza', 'viro', 'virus', 'vizir', 'zaraz', 'zaraž', 'češki soj', 'ceski soj'
] + [
    'koron',
    'covid',
    'zaraže',
    'zaraze',
    'zaraza',
    'pcr',
    'rt pcr',
    'maska',
    'maske',
    'masku',
    'maskom',
    'dezinfekcij',
    'beroš',
    'vili beroš',
    'markotić',
    'alemka markotić',
    'cjepiv',
    'cijepiv',
    'cijeplj',
    'respirator',
    'stožera civilne',
    'stožer civilne',
    'stožeru civilne',
    'stožeri civilne',
    'pfizer',
    'biontech',
    'curevac',
    'astrazeneca',
    'sanofi',
    'janssen',
    'johnson',
    'moderna',
    'inovio',
    'gilead',
    'glaxosmithkline',
    'novavax',
    'regeneron',
    'takeda',
    'vaxart',
]

new_kwrds = set()

for kw in kwrds:
    new_kw = kw
    replaced = False
    for diacritic, replacement in diacritics.items():
        new_kw = new_kw.replace(diacritic, replacement)
        replaced = True
    new_kwrds.add(kw)
    if replaced:
        new_kwrds.add(new_kw)

print(json.dumps(list(new_kwrds), indent=2, ensure_ascii=False))