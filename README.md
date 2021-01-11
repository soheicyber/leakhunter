Leakhunter
==========

Author(s): Ben [@zaeyx](https://twitter.com/zaeyx)
Contributors(s):

Objective
---------

Leakhunter enables you to find evidence of data being leaked from your organization by an insider.  Leakhunter can help you identify when something has leaked, and also can help you determine who it was who leaked it.

The Method
----------

Leakhunter works by hiding a small line of code inside your word documents (docx format specifically) which will enable those documents to call home to Leakhunter.  When a document calls home from outside your organizations networks without permission, we know something is up.  

We also hide a unique token value in each callback.  This means that we know specifically which document is calling back to the server.  We can use this trick, to assign different documents with different token values to different people.  These documents may even look identical, but as long as the hidden token is different, we will then know which person's document was leaked.  This can help us track down the source of a leak much faster than through traditional means.

Setup
-----

To get started, you'll need to ensure you've installed python3, pip3, and the python requirements from requirements.txt.

You can do this with the following commands on Ubuntu:

*Install python3, pip3, and git*

`apt install python3 python3-pip git`

*Clone this repo*

`git clone https://github.com/soheicyber/leakhunter`

*cd into the cloned repo*

`cd leakhunter`

*Install the python requirements*

`pip3 install -r requirements.txt`

Launching
---------

To get started we simply launch leakhunter with the following command:

`python3 main.py`

For this, please make sure that you're in the cloned repo (leakhunter dir). 

Bug Fixes & Reports
-------------------

Please send bug reports to ben (at) soheicyber.com.  If you have a bug fix, you can simply submit a pull request here.  If nobody has responded to your pull request in a timely manner, then please feel free to reach out!

If you have any additional questions you can contact me on Twitter [@zaeyx](https://twitter.com/zaeyx)
