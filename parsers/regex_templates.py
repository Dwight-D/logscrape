'''Contains basic regex templates for use in text parsing etc'''

DATE_FULL = '[0-9]{4}-[0-9]{2}-[0-9]{2}'

HH_MM_SS = '[0-2][0-9]:[0-6][0-9]:[0-6][0-9]'

HH_MM_SS_MMM = HH_MM_SS + ',[0-9]{3}'

CLASS_NAME = '\[.*\]'

LOGBACK_BASIC_START = '^' + DATE_FULL + ' ' + HH_MM_SS_MMM + ' ' + CLASS_NAME
