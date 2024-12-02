HELP_QUEUE_OPTIONS = """b( context^exten^priority ) - Before initiating an outgoing call, Gosub to the specified location using the newly created channel. The Gosub will be executed for each destination channel.

B( context^exten^priority ) - Before initiating the outgoing call(s), Gosub to the specified location using the current channel.
C - Mark all calls as "answered elsewhere" when cancelled.
c - Continue in the dialplan if the callee hangs up.
d - data-quality (modem) call (minimum delay).
F( context^exten^priority ) - When the caller hangs up, transfer the called member to the specified destination and start execution at that location.
NOTE: Any channel variables you want the called channel to inherit from the caller channel must be prefixed with one or two underbars ('_').
F - When the caller hangs up, transfer the called member to the next priority of the current extension and start execution at that location.
NOTE: Any channel variables you want the called channel to inherit from the caller channel must be prefixed with one or two underbars ('_').
NOTE: Using this option from a Macro() or GoSub() might not make sense as there would be no return points.
h - Allow callee to hang up by pressing *.
H - Allow caller to hang up by pressing *.
n - No retries on the timeout; will exit this application and go to the next step.
i - Ignore call forward requests from queue members and do nothing when they are requested.
I - Asterisk will ignore any connected line update requests or any redirecting party update requests it may receive on this dial attempt.
r - Ring instead of playing MOH. Periodic Announcements are still made, if applicable.
R - Ring instead of playing MOH when a member channel is actually ringing.
t - Allow the called user to transfer the calling user.
T - Allow the calling user to transfer the call.
w - Allow the called user to write the conversation to disk via Monitor.
W - Allow the calling user to write the conversation to disk via Monitor.
k - Allow the called party to enable parking of the call by sending the DTMF sequence defined for call parking in features.conf.
K - Allow the calling party to enable parking of the call by sending the DTMF sequence defined for call parking in features.conf.
x - Allow the called user to write the conversation to disk via MixMonitor.
X - Allow the calling user to write the conversation to disk via MixMonitor.        
        """

