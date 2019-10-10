==========
Change Log
==========

------------
Contributers
------------

* Carl Waldbieser (https://github.com/cwaldbieser)
* Mark Liffiton (https://github.com/liffiton)

------
v1.0.1
------

* CASLocalAuthenticator did not create system users at login-time.  Users were
  only created on Jupyterhub restart.
* Thanks to the following individuals for raising this issue and/or testing!
    * Prebagarane Louvois
    * Gary Molenkamp
    * miguelmarco

------
v1.0.0
------

* Newer Jupyterhub uses Python native coroutines.

------
v0.3.0
------

* Added whitelist feature.

------
v0.2.0
------

* Added CAS logout feature. 

------
v0.1.0
------

* Corrected title in README.
* Include `lxml` in dependencies; resolves issue #1.
* BUGFIX: Attribute requirements produced error; resolves issue #3.
* Added `CASLocalAuthenticator` for Just-in-time account creation; see issue #4.


