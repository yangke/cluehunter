.. ClueHunter documentation master file, created by
   sphinx-quickstart on Wed Jan 13 17:06:55 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to ClueHunter's documentation!
======================================
This document is for `ClueHunter <http://github.com/yangke/chucky-ng/>`_ , an auxiliary tool for crash point reverse data flow analysis. It generate data flow graph according to the gdb debug log(C program source code level). It receives manually specified sink variables that cause the last line crash and perform interprocedural analysis on the log trace. For obtaining the auto-debug trace, the tool `robot_dbg.exp` in ClueHunter requires the program under debug to be compiled with profiled code information (gcc **-g -save-temp** operation).

Target Problem: Where is the bad data come from?
------------------
A common question for program debugging is "where is the bad data come from?" In this case we need to analysis reversely from the crash or wrongly executed statement, trace the relative calculation, then infer and locate the wrong code logic. Slicing is a effective technique to prune away irrelative calculation help analyst r to focus on the error relative code snipet. Visulizing the complex code logic as a colorful property graph is also preferable. Actually, we always use IDE or gdb to view the code snipets and call stacks to keep in mind the whole picture of the data flow. ClueHunter is then designed to relax our mind and help us to infer the executed data transform logic.
 
Contents:

.. toctree::
   :maxdepth: 2



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

