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

Quick Start
-----------

To get started we simply launch leakhunter with the following command:

`python3 main.py`

For this, please make sure that you're in the cloned repo (leakhunter dir). 

Usage Instructions
------------------

Here's a quick breakdown of how to use this tool.  First, you need to get a few things together.

The first thing that you need is a docx file you intend to use as bait for the leaker.  What you put in this document is up to you, but you probably want to make it something enticing to them so that they'll want to actually leak it.  Edit that docx file as you see fit, and when it's ready please move it into the templates folder templates/ (the folder named 'templates' in this project's directory structure).

Now, you should be able to see your new template file in leak hunter, to confirm, launch leakhunter like the above:

`python3 main.py`

Then run the following command, looking at the output for your file's name:

`show_template_files`

You should be able to see your template file there as long as you moved it into the templates/ folder.

**Registering a Campaign**
The next thing we want you to do, is to register a campaign name with LeakHunter.  This enables you to keep all your work separate from other campaigns - and to run multiple campaigns at once from one codebase!

Just pick a descriptive name such as "hr_leaker" and set it as follows:

`set_campaign hr_leaker`

Assuming this is the first time you've used this campaign name, LeakHunter will create all the files you need quietly in the background.  If you've used this name before, LeakHunter will load the settings you had when you used it last.  This is great, because it means you can step away - close down LeakHunter, then come back and pickup on your campaign from where you left off.  

Note: We try to save all your changes periodically (on state change), there is no save button... but you shouldn't lose your work unless something unexpected happens.

**Listing Targets**
Now, if you're on a hunt for a leaker, you should have a list of targets you want to analyze.  You will be sending the bait file to each person on this list, so hopefully it's not too big.  Add a new target to the list like so (using the example of a target named Mr. Targetson):

`add_target Mr. Targetson`

You can show all the targets you've loaded with the command `show_targets`.

**Setting Listener Options**
You'll be running a 'listener' using LeakHunter, to listen for callbacks from your document whenever someone opens it.  This just means that LeakHunter will sit and wait to see network requests coming from the webbug we hide in the document.  

You need to tell the webbugs what the IP address will be that they should call home to.. This is probably one of the trickier parts to explain, because the IP might change depending on your environment.  If you're in a cloud instance, then you should know how to get your IP address for your instance.  But if you're running LeakHunter somewhere on a corporate network, you might need to get a complex NAT solution setup to enable the webbugs to phone home.  Probably your best bet is to run LeakHunter somewhere directly connected to the internet (without NAT) such as in a cloud environment.  But your setup is your responsibility.  Either way, you should set the IP and port options like so (example: 127.0.0.1:7777):

`set_listen_address 127.0.0.1`

`set_listen_port 7777`

**Selecting Template**
Finally, you need to select your template.  The document that you placed in the templates/ folder earlier presumably.  You can show templates with:

`show_template_files`

And then type out the name from that list which you wish to use for your campaign (example, confidential_memo.docx):

`set_target_file confidential_memo.docx`

**Injection**

With all those variables set, you're ready to inject the webbugs into the template document.  This process will create a copy of the template for each person on your target list.  That copy of the document will have a unique webbug embedded in it.  This webbug will contain a code which is unique to that specific target person.  This way, when the webbug calls home, we know who had the document that called home.

You'll be able to tell which document belongs to which target, because the document will have a new name of target_person.docx.

You will find all these documents in the following folder: campaign/<your_campaign_name>/injected/

Use this command:

`launch_injection`

If you have any errors, please first double check you've set all the variables correctly.  You need to have a listen_port, listen_address, at least one target, and a campaign as well as a target_file.

**Launch the Listener**

Now that you've completed injection, you should first start the listener before you do anything else.  We do this as follows:

`launch_listener`

You'll see that your console has now paused and is listening for requests.  You can hit ctrl-c to exit this, but do note that this closes the listener.  If the listener isn't running when the leaker opens the document, you won't see it.

Note: Also do check that there aren't any firewall rules in the way of the requests coming from the internet to your listener.  Remember you can see which port it's listening on with `show_listen_port`.

When someone connects, you'll see something like:

```
Connection from: ('127.0.0.1', 52738) -> Attributed to sula
Connection from: ('127.0.0.1', 52739) -> Attributed to sula
Connection from: ('127.0.0.1', 52740) -> Attributed to sula
Connection from: ('127.0.0.1', 52741) -> Attributed to sula
Connection from: ('127.0.0.1', 52742) -> Attributed to sula
Connection from: ('127.0.0.1', 52743) -> Attributed to sula
Connection from: ('127.0.0.1', 52744) -> Attributed to sula
Connection from: ('127.0.0.1', 52745) -> Attributed to sula
Connection from: ('127.0.0.1', 52746) -> Attributed to sula
Connection from: ('127.0.0.1', 52747) -> Attributed to sula
Connection from: ('127.0.0.1', 52748) -> Attributed to sula
Connection from: ('127.0.0.1', 52749) -> Attributed to sula
```

Note: The reason we see multiple requests in a row like this, is because Microsoft Word - and other processors - will often try multiple times to request the resource indicated by the webbug.  This is WAI!

You could try opening one of the injected documents to make sure your setup is working.  Or use a test campaign to just to get things right before starting a real launch.

**Distributing the Docs**
You're fully set!  Now you simply need to distribute the documents to the targets.  How you do this is up to you.  Perhaps sending out an email to each user individually, with their unique doc as an attachment.  Maybe indicate to them that you've placed everyone in the email thread on "BCC" (to explain why they only see you emailing them directly) because of the sensitive nature of the conversation.

Make sure that you change the name of the document back from <target_name>.docx to something like "confidential_memo.docx" before sending it out.  We changed it to 'target_name' out of a desire to keep the docs from getting mixed up.  It's really important that the right person get the right doc.  If you give the wrong doc to someone, it could invalidate the campaign - since each webbug is unique!

**Watch the Listener**
Now you just sit back and watch the listener.  You should see requests come in each time someone opens the document.  What you're looking for in particular, is one document that's far more active than any other.  If someone leaked a document out of your network - or shared it with others - then that one document will get read by many more than just one person.  So keep an eye out for the number of requests coming in (keeping in mind that it's normal to see a few requests back to back in the logs - but when one doc is far more active than others - it should be obvious).

The other thing you're looking for is IPs that don't correspond to your corporate network.  If you see that the document is calling back to your listener from IP addresses all over the world, it's a sure bet this document has been leaked!  

Happy Leak Hunting!

Development
-----------

For an example of how to add a new command, please see: 

[https://github.com/soheicyber/leakhunter/commit/c605186eed567afdd9ecb0cef5116d6601fd90b1](https://github.com/soheicyber/leakhunter/commit/c605186eed567afdd9ecb0cef5116d6601fd90b1)

Bug Fixes & Reports
-------------------

Please send bug reports to ben (at) soheicyber.com.  If you have a bug fix, you can simply submit a pull request here.  If nobody has responded to your pull request in a timely manner, then please feel free to reach out!

If you have any additional questions you can contact me on Twitter [@zaeyx](https://twitter.com/zaeyx)
