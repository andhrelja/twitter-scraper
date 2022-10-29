#-*-coding:utf-8-*-
#
#	Simple stemmer for Croatian v0.1
#	Copyright 2012 Nikola Ljubešić and Ivan Pandžić
#
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU Lesser General Public License as published
#	by the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#	GNU Lesser General Public License for more details.
#
#	You should have received a copy of the GNU Lesser General Public License
#	along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import re

from twitter_scraper.utils import fileio
from twitter_scraper import settings

RULES_TXT = os.path.join(settings.ROOT_DIR, 'twitter_scraper/text/stemmer/rules.txt')
TRANSFORMATIONS_TXT = os.path.join(settings.ROOT_DIR, 'twitter_scraper/text/stemmer/transformations.txt')

# stop = set(['biti','jesam','budem','sam','jesi','budeš','si','jesmo','budemo','smo','jeste','budete','ste','jesu','budu','su','bih','bijah','bjeh','bijaše','bi','bje','bješe','bijasmo','bismo','bjesmo','bijaste','biste','bjeste','bijahu','biste','bjeste','bijahu','bi','biše','bjehu','bješe','bio','bili','budimo','budite','bila','bilo','bile','ću','ćeš','će','ćemo','ćete','želim','želiš','želi','želimo','želite','žele','moram','moraš','mora','moramo','morate','moraju','trebam','trebaš','treba','trebamo','trebate','trebaju','mogu','možeš','može','možemo','možete'])
stop = fileio.read_content(settings.STOP_WORDS_HRV, 'json')
pravila = [re.compile(r'^('+osnova+')('+nastavak+r')$') for osnova, nastavak in [e.strip().split(' ') for e in open(RULES_TXT, encoding='utf-8')]]
transformacije=[e.strip().split('\t') for e in open(TRANSFORMATIONS_TXT, encoding='utf-8')]

def istakniSlogotvornoR(niz):
	return re.sub(r'(^|[^aeiou])r($|[^aeiou])',r'\1R\2',niz)

def imaSamoglasnik(niz):
	if re.search(r'[aeiouR]',istakniSlogotvornoR(niz)) is None:
		return False
	else:
		return True

def transformiraj(pojavnica):
	for trazi,zamijeni in transformacije:
		if pojavnica.endswith(trazi):
			return pojavnica[:-len(trazi)]+zamijeni
	return pojavnica

def korjenuj(pojavnica):
	for pravilo in pravila:
		dioba=pravilo.match(pojavnica)
		if dioba is not None:
			if imaSamoglasnik(dioba.group()) and len(dioba.group())>1:
				return dioba.group()
	return pojavnica

def croatian_stemmer(word):
	output = {}
	if not isinstance(word, str):
		raise TypeError('Expected `string`, got `{}`'.format(type(word)))
	if re.search(r"\s", word):
		raise ValueError('Expected a word without spaces, got `{}`'.format(word))
	return korjenuj(transformiraj(word.lower()))

if __name__=='__main__':
	print(croatian_stemmer('Ujak Ivo je krenuo u selo trčeći u bijelim tenisicama'))

