Staged Stan Python package
===========================

This package runs the Stan_ Hamiltonean Monte Carlo sampler.

Staged Stan Python works in a deterministic fashion: Given 

  - Stan code,
  - data (python dictionary) and 
  - a seed

it computes the best fit once, and runs the sampling from the best fit once.
When the code is called again, the results are loaded from the cache.

Unlike PyStan_, the outputs (best fit, samples) are stored directly. 

Furthermore, the stan executable can be compiled and run on a different machine,
and the outputs copied over. Staged Stan will pick up the results.

Staged Stan requires Stan. Let the STANDIR environment variable point to the Stan directory (where makefile lives).

.. _Stan: http://mc-stan.org/
.. _PyStan: http://mc-stan.org/pystan.html

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

Output (parts are omitted)::
	
	[...] building executable [...]
	Running code: ('./code-92682818b5cf62a059c86189cc8ede9daa6f06ff/code.exe', 'output', 'file=./code-92682818b5cf62a059c86189cc8ede9daa6f06ff/data-2fbafe7c1993572a57131ef2a800f4072a088f3b/bestfit1.out', 'data', 'file=./code-92682818b5cf62a059c86189cc8ede9daa6f06ff/data-2fbafe7c1993572a57131ef2a800f4072a088f3b/data.R', 'random', 'seed=1', 'optimize')

	Best fit:
	  mymean               : [ 2.07380232 -0.9599354 ] 

	Running code: ('./code-92682818b5cf62a059c86189cc8ede9daa6f06ff/code.exe', 'output', 'file=./code-92682818b5cf62a059c86189cc8ede9daa6f06ff/data-2fbafe7c1993572a57131ef2a800f4072a088f3b/samples1.out', 'data', 'file=./code-92682818b5cf62a059c86189cc8ede9daa6f06ff/data-2fbafe7c1993572a57131ef2a800f4072a088f3b/data.R', 'init=./code-92682818b5cf62a059c86189cc8ede9daa6f06ff/data-2fbafe7c1993572a57131ef2a800f4072a088f3b/bestfit1.R', 'random', 'seed=1', 'sample')

	Gradient evaluation took 0 seconds
	1000 transitions using 10 leapfrog steps per transition would take 0 seconds.
	Adjust your expectations accordingly!


	Iteration:    1 / 2000 [  0%]  (Warmup)
	Iteration:  100 / 2000 [  5%]  (Warmup)
	Iteration:  200 / 2000 [ 10%]  (Warmup)
	Iteration:  300 / 2000 [ 15%]  (Warmup)
	Iteration:  400 / 2000 [ 20%]  (Warmup)
	Iteration:  500 / 2000 [ 25%]  (Warmup)
	Iteration:  600 / 2000 [ 30%]  (Warmup)
	Iteration:  700 / 2000 [ 35%]  (Warmup)
	Iteration:  800 / 2000 [ 40%]  (Warmup)
	Iteration:  900 / 2000 [ 45%]  (Warmup)
	Iteration: 1000 / 2000 [ 50%]  (Warmup)
	Iteration: 1001 / 2000 [ 50%]  (Sampling)
	Iteration: 1100 / 2000 [ 55%]  (Sampling)
	Iteration: 1200 / 2000 [ 60%]  (Sampling)
	Iteration: 1300 / 2000 [ 65%]  (Sampling)
	Iteration: 1400 / 2000 [ 70%]  (Sampling)
	Iteration: 1500 / 2000 [ 75%]  (Sampling)
	Iteration: 1600 / 2000 [ 80%]  (Sampling)
	Iteration: 1700 / 2000 [ 85%]  (Sampling)
	Iteration: 1800 / 2000 [ 90%]  (Sampling)
	Iteration: 1900 / 2000 [ 95%]  (Sampling)
	Iteration: 2000 / 2000 [100%]  (Sampling)

	  Elapsed Time: 0.01 seconds (Warm-up)
		        0.02 seconds (Sampling)
		        0.03 seconds (Total)

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

Read `the code <https://github.com/JohannesBuchner/stagedstan/blob/master/stagedstan.py>`_ (only ~160 lines) for API documentation.



