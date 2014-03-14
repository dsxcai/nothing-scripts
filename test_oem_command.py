#!/usr/bin/env python

import sys, os
import optparse
import re
import shlex, subprocess

FASTBOOT = '~/bin/fastboot'
REDIRECT_ARGS = '2>&1 |'

TEST_CASES = {
	'1_cid'   : {'read' : 'oem readcid', 'write' : 'oem writecid', 'value' : '99999999', 'help' : 'customer ID', 'patt' : 'grep \'cid:\' | awk \'{ printf $3; }\''},
	'0_bcid'  : {'read' : 'oem readbcid', 'write' : 'oem writebcid', 'erase' : 'oem erasebcid', 'value' : '1213aacc', 'help' : 'backup CID',
	             'patt' : 'grep \'Backup CID\' | awk \'{ printf $5; }\' | sed -r \"s/\\[(.+)\\]/\\1/g\" | sed -r \"s/<Empty>//g\"'},
	'colorid' : {'read' : 'oem readColorID', 'write' : 'oem writeColorID', 'erase' : 'oem eraseColorID', 'value' : '7', 'help' : 'color ID',
	             'patt' : 'grep \'color_ID\' | awk \'{ printf $4; }\' | sed -r \"s/\\[(.+)\\]/\\1/g\" | sed -r \"s/<Empty>//g\"'},
	'cfg'     : {'read' : 'oem readconfig', 'write' : 'oem writeconfig', 'erase' : 'oem eraseconfig', 'value' : {'6' : '0x2', '7' : '0x200A'}, 'help' : 'bootloader config',
	             'patt' : 'grep \'index\' | tr \",\" \" \" | sed -r \"s/index:|value://g\" | awk \'{ printf $3; }\'', 'multi' : [ '%X' % x for x in range(12) ]},
	'imei'    : {'read' : 'oem readimei', 'write' : 'oem writeimei', 'value' : '355195099999999', 'help' : 'device IMEI', 'patt' : 'grep \'imei:\' | awk \'{ printf $3; }\''},
	'mbsn'    : {'read' : 'oem readmbserialno', 'help' : 'mainboard serial no.', 'patt' : 'grep \'MB Serial No\' | awk \'{ printf $6; }\''},
	'meid'    : {'read' : 'oem readmeid', 'write' : 'oem writemeid', 'value' : '1357DEAD2468FF', 'help' : 'device MEID', 'patt' : 'grep \'meid:\' | awk \'{ printf $3; }\''},
	'mid'     : {'read' : 'oem readrawmid', 'write' : 'oem writemid', 'value' : '0P6B1XXX', 'help' : 'device model ID', 'patt' : 'grep \'readrawmid:\' | awk \'{ printf $3; }\''},
	'pid'     : {'read' : 'oem readpid', 'write' : 'oem writepid', 'value' : '272', 'help' : 'device project ID', 'patt' : 'grep \'pid:\' | awk \'{ printf $3; }\''},
	'sn'      : {'read' : 'oem readserialno', 'write' : 'oem writeserialno', 'value' : 'iloveyouforever', 'help' : 'device serial no.',
	             'patt' : 'grep \'Device Serial No. is\' | awk \'{ printf $6; }\''},
	'sku'     : {'read' : 'oem readsku', 'write' : 'oem writesku', 'value' : {'0' : '0xAABBCCDD', '9' : '0xDEADDEAD'}, 'help' : 'device sku config',
	             'patt' : 'grep \'index\' | tr \",\" \" \" | sed -r \"s/index:|value://g\" | awk \'{ printf $5; }\'', 'multi' : [ '%X' % x for x in range(12) ]},
}

DEVICE_DATA = {
}

TEST_RESULT = {
}

parser = optparse.OptionParser(usage="Usage: %prog [options]")

for i in TEST_CASES:
	help = TEST_CASES[i]['help'];
	metavar = re.sub('^[0-9]+_', '', i);
	if TEST_CASES[i].has_key('multi'):
		parser.add_option('--%s' % metavar, action = 'append', type = 'string', nargs = 2, metavar = '<index> <value>', dest = i, help = help);	
	else:
		parser.add_option('--%s' % metavar, action = 'store', type = 'string', dest = i, metavar = '<%s>' % (metavar), help = help);

parser.add_option('--fastboot', '-f', action = 'store', type = 'string', dest = 'fastboot', metavar = '<fastboot>', help = 'full path of the fastboot tool');
parser.add_option('--list', '-l', action = 'store_true', default = False, dest = 'list', help = 'print out the test cases and exit');

def set_default_options(opt, case):
	for key, value in opt.__dict__.items():
		if key == 'fastboot':
			if value:
				FASTBOOT = value;
		elif key != 'list':
			if value:
				if case[key].has_key('multi'):
					case[key]['value'] = {value[0][0] : value[0][1]};
				else:
					case[key]['value'] = value;
			if case[key].has_key('multi'):
				for i in case[key]['multi']:
					if not case[key]['value'].has_key(i):
						case[key]['value'][i] = '0x0';

def verifty_test_result(case, test):
	for i in case:
		if case[i].has_key('value'):
			print "%s: " % (i),
			if test[i] != case[i]['value']:
				print "Failed."
			else:
				print "Passed."

def do_test(opt, case):
	# Save device data
	for i in case:
		if case[i].has_key('multi'):
			DEVICE_DATA[i] = {};
			for j in case[i]['multi']:
				DEVICE_DATA[i][j] = subprocess.check_output('%s %s %s %s %s' % (FASTBOOT, case[i]['read'], j, REDIRECT_ARGS, case[i]['patt']), shell=True);
		else:
			res = subprocess.check_output('%s %s %s %s' % (FASTBOOT, case[i]['read'], REDIRECT_ARGS, case[i]['patt']), shell=True);
			if len(res) > 0:
				DEVICE_DATA[i] = res;
	# Do tests
	for i in case:
		# call erasing command
		if case[i].has_key('erase'):
			subprocess.check_call('%s %s' % (FASTBOOT, case[i]['erase']), shell=True);
		if case[i].has_key('write'):
			if case[i].has_key('multi'):
				for j in case[i]['value']:
					subprocess.check_call('%s %s %s %s' % (FASTBOOT, case[i]['write'], j, case[i]['value'][j]), shell=True);
			else:
				subprocess.check_call('%s %s %s' % (FASTBOOT, case[i]['write'], case[i]['value']), shell=True);
	# Save test results
	for i in case:
		if case[i].has_key('multi'):
			TEST_RESULT[i] = {};
			for j in case[i]['multi']:
				TEST_RESULT[i][j] = subprocess.check_output('%s %s %s %s %s' % (FASTBOOT, case[i]['read'], j, REDIRECT_ARGS, case[i]['patt']), shell=True);
		else:
			res = subprocess.check_output('%s %s %s %s' % (FASTBOOT, case[i]['read'], REDIRECT_ARGS, case[i]['patt']), shell=True);
			if len(res) > 0:
				TEST_RESULT[i] = res;
	# Restore device data
	for i in case:
		# call erasing command
		if case[i].has_key('erase'):
			subprocess.check_call('%s %s' % (FASTBOOT, case[i]['erase']), shell=True);
		if case[i].has_key('write'):
			if case[i].has_key('multi'):
				for j in DEVICE_DATA[i]:
					subprocess.check_call('%s %s %s %s' % (FASTBOOT, case[i]['write'], j, DEVICE_DATA[i][j]), shell=True);
			else:
				if DEVICE_DATA.has_key(i):
					subprocess.check_call('%s %s %s' % (FASTBOOT, case[i]['write'], DEVICE_DATA[i]), shell=True);

def main(args):
	(options, args) = parser.parse_args(args);
	set_default_options(options, TEST_CASES);
	if options.list:
		for i in TEST_CASES:
			if TEST_CASES[i].has_key('value'):
				test_name = re.sub('^[0-9]+_', '', i);
				if TEST_CASES[i].has_key('multi'):
					print "%s: " % (test_name),
					for j in TEST_CASES[i]['value']:
						print "\tindex: %s, value: %s" % (j, TEST_CASES[i]['value'][j])
				else:
					print "%s: %s" % (test_name, TEST_CASES[i]['value'])
	else:
		do_test(options, TEST_CASES);
		verifty_test_result(TEST_CASES, TEST_RESULT);

if __name__ == "__main__":
	main(sys.argv)

