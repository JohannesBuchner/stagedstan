import hashlib
import os
import numpy
import re
import shutil
import subprocess

cachedir = "."
standir = os.environ['STANDIR']

def hash_without_whitespaces(text):
	text = text.strip()
	text = text.replace('\t', '  ')
	text = re.sub(' * ', ' ', text)
	return hashlib.sha1(text).hexdigest()

"""
Cached and lazy initialisation of stan models.
Allows running stan externally.

Store code by sha1 sum
Store data by sha1 sum
Store best fit and samples:

codehash/
 |- code.stan
 |- code.exe
 |- datahash/
    |- data.R
    |- bestfit.R
    |- samples.txt
"""
def get_codeinfo(code):
	codehash = hash_without_whitespaces(code)
	codepath = os.path.join(cachedir, 'code-%s' % codehash)
	if not os.path.exists(codepath):
		os.mkdir(codepath)
	codefile = os.path.join(codepath, "code.stan")
	if not os.path.exists(codefile):
		print 'writing code file to %s ...' % codefile
		f = file(codefile, 'w')
		f.write(code)
		f.close()
	return dict(codepath=codepath, codefile=codefile, codehash=codehash)

def build_executable(codeinfo):
	# compile code: throw it into stan directory, and call make
	print 'building executable in %s ...' % standir
	shutil.copy(codeinfo['codefile'], os.path.join(standir, 'staged.stan'))
	subprocess.check_call(('make', '-C', standir, 'staged'))
	shutil.copy(os.path.join(standir, 'staged.cpp'), os.path.join(codeinfo['codepath'], 'code.cpp'))
	exe = os.path.join(codeinfo['codepath'], 'code.exe')
	shutil.copy(os.path.join(standir, 'staged'), exe)
	print 'build successful'
	return exe

def run_executable(exe, command, codeinfo, datainfo, outputfile, *otherargs):
	# compile code: throw it into stan directory, and call make
	args = tuple([exe, 
		'output', 'file=%s' % outputfile,
		'data', 'file=%s' % datainfo['datafile'],
		] + list(otherargs) + [command])
	print 'Running code:', args
	subprocess.check_call(args)

def get_executable(codeinfo):
	exe = os.path.join(codeinfo['codepath'], "code.exe")
	if not os.path.exists(exe):
		exe = build_executable(codeinfo)
	return exe

def convertdict(data):
	# convert into R data dump format
	items = []
	for k, v in data.iteritems():
		v = numpy.asarray(v)
		if len(v.shape) == 0:
			items.append("%s <- %s" % (k, v))
		elif len(v.shape) == 1:
			# sequence
			items.append("%s <- c(%s)" % (k, ','.join([str(vi) for vi in v])))
		else:
			# an array
			n = len(v)
			items.append("%s <- structure(c(%s), .Dim = c(%s))" % (k, 
				','.join([str(vi) for vi in v.ravel(order='F')]),
				','.join(['%d' % l for l in list(v.shape)])
				))
	text = '\n'.join(items) + "\n"
	return text

def makelist(shape):
	if len(shape) == 1:
		return [None]*shape[0]
	else:
		return [makelist(shape[1:]) for s in range(shape[0])]
def set_list_value(array, index, value):
	if len(index) == 1:
		array[index[0]] = value
	else:
		set_list_value(array[index[0]], index[1:], value)
def parse_output(outputfile):
	f = file(outputfile, 'r')
	lines = [l[:-1].split(',') for l in f.readlines() if not l.startswith('#') and l.strip() != '' ]
	header = lines[0]
	
	dimensions = {}
	assign = []
	for h in header:
		parts = h.split('.')
		name = parts[0]
		shape = tuple(map(int, parts[1:]))
		index = tuple([i - 1 for i in shape])
		assign.append((name, index))
		if name in dimensions:
			shape = [max(s, ns) for s, ns in zip(shape, dimensions[name])]
		dimensions[name] = tuple(shape)
	# mymean.1.2 has to end up in values[0][1]
	nrows = len(lines) - 1
	content = {}
	# the reason why we do it with lists (potentially memory inefficient)
	# is that numpy can detect the array data type for us
	for k, shape in dimensions.iteritems():
		content[k] = makelist([nrows] + list(shape))
	
	for i, row in enumerate(lines[1:]):
		for value, (name, index) in zip(row, assign):
			newindex = tuple([i] + list(index))
			if '.' in value:
				value = float(value)
			else:
				value = int(value)
			set_list_value(content[name], newindex, value)
	for name in content.keys():
		content[name] = numpy.array(content[name])
	return content

def get_datainfo(codeinfo, data):
	codepath = codeinfo['codepath']
	datacontent = convertdict(data)
	
	datahash = hash_without_whitespaces(datacontent)
	datapath = os.path.join(codepath, 'data-%s' % datahash)
	if not os.path.exists(datapath):
		os.mkdir(datapath)

	datafile = os.path.join(datapath, "data.R")
	if not os.path.exists(datafile):
		f = file(datafile, 'w')
		f.write(datacontent)
		f.close()
	return dict(datapath=datapath, datafile=datafile, datahash=datahash)

def get_best_fit(code, data, seed=1):
	codeinfo = get_codeinfo(code)
	exe = get_executable(codeinfo)
	datainfo = get_datainfo(codeinfo, data)
	outputfile = os.path.join(datainfo['datapath'], 'bestfit%d.out' % seed)
	if not os.path.exists(outputfile):
		run_executable(exe, 'optimize', codeinfo, datainfo, outputfile, "random", "seed=%d" % seed)
	best_fit = parse_output(outputfile)
	return dict([(k, v[0]) for k,v in best_fit.iteritems()])
	return best_fit


def get_samples(code, data, seed=1):
	codeinfo = get_codeinfo(code)
	exe = get_executable(codeinfo)
	datainfo = get_datainfo(codeinfo, data)
	outputfile = os.path.join(datainfo['datapath'], 'samples%d.out' % seed)
	initial = get_best_fit(code, data)
	
	initialfile = os.path.join(datainfo['datapath'], 'bestfit%d.R' % seed)
	f = file(initialfile, 'w')
	f.write(convertdict(initial))
	f.close()
	if not os.path.exists(outputfile):
		run_executable(exe, 'sample', codeinfo, datainfo, outputfile,
			"init=%s" % initialfile, "random", "seed=%d" % seed)
	return parse_output(outputfile)

def test_code(stancode):
	numpy.random.seed(0)
	obs = numpy.transpose([
		numpy.random.normal(2, 0.1, size=10),
		numpy.random.normal(-1, 0.1, size=10)
	])
	data = dict(N=10, stdev = 0.1, obs = obs)
	print 'Best fit:'
	for k,v in get_best_fit(stancode, data).iteritems():
		if '__' not in k:
			print '  %-20s : %s ' % (k, v)
	print
	print 'Samples:'
	for k,v in get_samples(stancode, data).iteritems():
		if '__' not in k:
			print '  %-20s : %s ' % (k, v)
	print
def test1():
	# test it with simple code
	stancode = """
data {
  int N;
  real stdev;
  real obs[N,2];
}
parameters {
  real mean1;
  real mean2;
}
model {
  for (i in 1:N) {
    obs[i,1] ~ normal(mean1, stdev);
    obs[i,2] ~ normal(mean2, stdev);
  }
}
"""
	test_code(stancode)
def test2():
	# test it with simple code
	stancode = """
data {
  int N;
  real stdev;
  real obs[N,2];
}
parameters {
  real mymean[2];
}
model {
  for (i in 1:N) {
    obs[i,1] ~ normal(mymean[1], stdev);
    obs[i,2] ~ normal(mymean[2], stdev);
  }
}
"""
	test_code(stancode)

if __name__ == '__main__':
	test2()

