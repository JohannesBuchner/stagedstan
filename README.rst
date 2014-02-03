Staged Stan Python package
===========================

This package runs the Stan Hamiltonean Monte Carlo sampler.

Staged Stan Python works in a deterministic fashion: Given 

  - stan code,
  - data (python dictionary) and 
  - a seed

it computes the best fit once, and runs the sampling from the best fit once.
When the code is called again, the results are loaded from the cache.

Unlike pystan, the outputs (best fit, samples) are stored directly. 

Furthermore, the stan executable can be compiled and run on a different machine,
and the outputs copied over. Staged Stan will pick up the results.

Staged Stan requires Stan. Let the STANDIR environment variable point to the Stan directory (where makefile lives).

Example::

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
	for k,v in get_samples(stancode, data, shuffle=True).iteritems():
		if '__' not in k:
			print '  %-20s : %s ' % (k, v)
	print

Output::
	
	Best fit:
	  mymean               : [ 2.07380232 -0.9599354 ] 

	Samples:
	  mymean               : [[ 2.10492  -0.897088]
	 [ 2.04165  -0.946299]
	 [ 2.11458  -0.894294]
	 ..., 
	 [ 2.09594  -0.895492]
	 [ 2.06744  -0.939044]
	 [ 2.07893  -0.956279]] 

The following files are created:

  * test/code-f2808a/code.exe -- compiled executable
  * test/code-f2808a/data-2fbaf/bestfit1.out -- results of the optimization
  * test/code-f2808a/data-2fbaf/samples1.out -- results of the sampling





